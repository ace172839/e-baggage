import flet as ft
import flet_map as map
from typing import TYPE_CHECKING
import logging
import threading

from config import WINDOW_WIDTH, USER_DASHBOARD_DEFAULT_LOCATION, USER_DASHBOARD_MAP_TEMPLATE
from constants import *
from services import LocationService

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_map_view(app_instance: 'App', view: ft.View) -> ft.View:
    """
    建立一個全螢幕的地圖 View，用於選擇地點。
    這個 View 會從 view.route 解析出要更新的目標 key。
    """
    logger.info(f"正在建立地圖選擇 View (build_map_view) for route: {view.route}")
    
    # --- 1. 從路由解析目標 ---
    try:
        target_key = view.route.split('/')[-1]
        
        # --- ↓↓↓ 修改點：加入新的 valid_keys ↓↓↓ ---
        valid_keys = [
            "arrival_location", 
            "return_location", 
            "instant_pickup", 
            "instant_dropoff",
            "prev_pickup", # 新增
            "prev_dropoff" # 新增
        ]
        
        # 檢查是否為住宿預訂路由 (hotel_booking_0, hotel_booking_1, etc.)
        is_hotel_booking = target_key.startswith("hotel_booking_")
        
        if target_key not in valid_keys and not is_hotel_booking:
            raise ValueError(f"無效的 target_key: {target_key}")
        
        # 解析住宿預訂索引
        booking_index = None
        if is_hotel_booking:
            try:
                booking_index = int(target_key.split("_")[-1])
                logger.info(f"地圖用於選擇第 {booking_index} 筆住宿地點")
            except (IndexError, ValueError) as ex:
                logger.error(f"無法解析住宿預訂索引: {ex}")
                raise ValueError(f"無效的住宿預訂索引: {target_key}")
            
    except (IndexError, ValueError) as e:
        logger.error(f"從路由 '{view.route}' 解析 target_key 失敗: {e}")
        return ft.View(
            route=view.route,
            controls=[ft.Text("錯誤：無效的地圖路由。")],
            appbar=ft.AppBar(title=ft.Text("錯誤"), leading=ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: app_instance.page.go_back()))
        )

    # --- 2. 初始化 & Refs ---
    location_service = LocationService() 

    map_control_ref = ft.Ref[map.Map]()
    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    search_bar_ref = ft.Ref[ft.TextField]()
    search_progress_ring_ref = ft.Ref[ft.ProgressRing]()
    selected_address_text_ref = ft.Ref[ft.Text]()  # 顯示當前選擇地址的文字
    address_loading_indicator_ref = ft.Ref[ft.ProgressRing]()  # 地址載入指示器
    
    selected_coords = ft.Ref[map.MapLatitudeLongitude]()
    selected_display_name = ft.Ref[str]()

    # --- 3. 輔助函式 (保持不變) ---
    def create_marker(coords: map.MapLatitudeLongitude) -> map.Marker:
        return map.Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_700, size=40),
            coordinates=coords,
        )

    def update_selection(coords: map.MapLatitudeLongitude, display_name: str, update_map_center: bool = False, zoom: float = 16.0, show_loading: bool = False):
        logger.info(f"更新地圖選擇: {display_name}")
        selected_coords.current = coords
        selected_display_name.current = display_name
        
        # 批量更新 UI 元素以減少重繪次數
        updates = []
        
        # 更新地址顯示文字
        if selected_address_text_ref.current:
            selected_address_text_ref.current.value = display_name
            updates.append(selected_address_text_ref.current)
        
        # 控制載入指示器顯示
        if address_loading_indicator_ref.current:
            address_loading_indicator_ref.current.visible = show_loading
            updates.append(address_loading_indicator_ref.current)
        
        # 更新標記
        if marker_layer_ref.current:
            marker_layer_ref.current.markers = [create_marker(coords)]
            updates.append(marker_layer_ref.current)
        
        # 批量更新所有 UI 元素（除了地圖中心）
        for control in updates:
            control.update()
            
        # 地圖中心移動放在最後，單獨更新
        if update_map_center and map_control_ref.current:
            map_control_ref.current.center_on(coords, zoom=zoom)
            map_control_ref.current.update()

    def on_map_tap(e: map.MapTapEvent):
        logger.debug(f"地圖點擊: Lat={e.coordinates.latitude}, Lon={e.coordinates.longitude}")
            
        coords = map.MapLatitudeLongitude(e.coordinates.latitude, e.coordinates.longitude)
        # 先顯示座標格式，立即更新 UI，並顯示載入指示器
        display_name = LocationService.format_coordinates(e.coordinates.latitude, e.coordinates.longitude)
        update_selection(coords, display_name, update_map_center=True, show_loading=True)
        
        # 在背景執行緒進行反向地理編碼，避免阻塞 UI
        def reverse_geocode_worker():
            try:
                # LocationService 已經處理地址簡化
                address = location_service.reverse_geocode(e.coordinates.latitude, e.coordinates.longitude)
                if address:
                    selected_display_name.current = address
                    logger.debug(f"反向地理編碼完成: {address}")
                    # 更新地址顯示文字並隱藏載入指示器
                    try:
                        if selected_address_text_ref.current and selected_address_text_ref.current.page:
                            selected_address_text_ref.current.value = address
                            selected_address_text_ref.current.update()
                        if address_loading_indicator_ref.current and address_loading_indicator_ref.current.page:
                            address_loading_indicator_ref.current.visible = False
                            address_loading_indicator_ref.current.update()
                    except Exception as update_ex:
                        logger.warning(f"UI 更新失敗 (控制項可能已離開頁面): {update_ex}")
            except Exception as ex:
                logger.error(f"反向地理編碼失敗: {ex}")
                # 失敗時也隱藏載入指示器
                try:
                    if address_loading_indicator_ref.current and address_loading_indicator_ref.current.page:
                        address_loading_indicator_ref.current.visible = False
                        address_loading_indicator_ref.current.update()
                except Exception as update_ex:
                    logger.warning(f"UI 更新失敗: {update_ex}")
        
        threading.Thread(target=reverse_geocode_worker, daemon=True).start()


    # --- 4. 事件處理 ---

    def search_worker_thread(query_str: str):
        """
        在背景執行緒中執行地理編碼，避免 UI 凍結。
        使用 LocationService 進行搜索
        """
        import time
        thread_start = time.time()
        logger.info(f"[Thread] 正在搜尋: {query_str}")

        try:
            # 使用 LocationService 進行地理編碼
            geocode_start = time.time()
            result = location_service.geocode(query_str, country_code="TW")
            geocode_time = time.time() - geocode_start
            logger.debug(f"[Thread] 地理編碼耗時: {geocode_time:.3f}秒")
            
            if result:
                latitude, longitude, address = result
                logger.info(f"[Thread] 找到地點: {address}")
                coords = map.MapLatitudeLongitude(latitude, longitude)
                
                # 更新狀態
                selected_coords.current = coords
                selected_display_name.current = address
                
                # 更新地址顯示文字（不顯示載入指示器）
                if selected_address_text_ref.current:
                    selected_address_text_ref.current.value = address
                    selected_address_text_ref.current.update()
                
                # 更新標記
                if marker_layer_ref.current:
                    marker_layer_ref.current.markers = [create_marker(coords)]
                    marker_layer_ref.current.update()
                
                # 移動地圖中心（一次性更新）
                map_update_start = time.time()
                if map_control_ref.current:
                    logger.debug(f"[Thread] 更新地圖中心: {coords}")
                    map_control_ref.current.center_on(coords, zoom=16)
                    map_control_ref.current.update()
                map_update_time = time.time() - map_update_start
                logger.debug(f"[Thread] 地圖更新耗時: {map_update_time:.3f}秒")
                
                # 隱藏搜尋載入指示器
                if search_progress_ring_ref.current:
                    search_progress_ring_ref.current.visible = False
                    search_progress_ring_ref.current.update()
                
                total_time = time.time() - thread_start
                logger.info(f"[Thread] 搜尋完成，總耗時: {total_time:.3f}秒")
                
            else:
                logger.warning(f"[Thread] 找不到地點: {query_str}")
                app_instance.page.snack_bar = ft.SnackBar(ft.Text(f"找不到地點: {query_str}"), open=True)
                if search_progress_ring_ref.current:
                    search_progress_ring_ref.current.visible = False
                    search_progress_ring_ref.current.update()
                else:
                    app_instance.page.update()
                
        except Exception as ex:
            logger.error(f"[Thread] 地理編碼時發生錯誤: {ex}")
            app_instance.page.snack_bar = ft.SnackBar(ft.Text("搜尋時發生錯誤"), open=True)
            if search_progress_ring_ref.current:
                search_progress_ring_ref.current.visible = False
                search_progress_ring_ref.current.update()
            else:
                app_instance.page.update()

    def on_search_click(e):
        """
        處理搜尋按鈕點擊事件
        """
        import time
        start_time = time.time()
        query = search_bar_ref.current.value
        if not query: 
            return
        
        logger.info(f"請求搜尋: {query} (開始時間: {start_time:.3f})")
        
        if search_progress_ring_ref.current:
            search_progress_ring_ref.current.visible = True
            search_progress_ring_ref.current.update()
        
        logger.debug(f"搜尋 UI 更新完成，耗時: {time.time() - start_time:.3f}秒")
        
        threading.Thread(
            target=search_worker_thread,
            args=(query,),
            daemon=True
        ).start()

    # --- ↓↓↓ 修改點：更新 on_confirm_click ↓↓↓ ---
    def on_confirm_click(e):
        
        # 處理未選擇地點就按確認
        if not selected_display_name.current:
            logger.warning("未選擇任何地點，但按下了確認。")
            if target_key in ["instant_pickup", "instant_dropoff"]:
                app_instance.page.go("/app/user/instant_booking")
            # (prev_pickup, prev_dropoff, arrival_location, return_location 都返回 previous_booking)
            else:
                app_instance.page.go("/app/user/previous_booking")
            return

        logger.info(f"確認選擇 for '{target_key}': {selected_display_name.current}")
        
        # 寫入 Instant Booking 的 Refs
        if target_key == "instant_pickup":
            if app_instance.pickup_location_ref.current:
                app_instance.pickup_location_ref.current.value = selected_display_name.current
            app_instance.page.go("/app/user/instant_booking")
        
        elif target_key == "instant_dropoff":
            if app_instance.dropoff_location_ref.current:
                app_instance.dropoff_location_ref.current.value = selected_display_name.current
            app_instance.page.go("/app/user/instant_booking")
        
        # --- ↓↓↓ 新增的邏輯 ↓↓↓ ---
        # 寫入 Previous Booking 的 Refs
        elif target_key == "prev_pickup":
            if app_instance.prev_pickup_location_ref.current:
                app_instance.prev_pickup_location_ref.current.value = selected_display_name.current
            # 也寫入 state_val
            app_instance.prev_pickup_location_val = selected_display_name.current
            app_instance.page.go("/app/user/previous_booking")
        
        elif target_key == "prev_dropoff":
            if app_instance.prev_dropoff_location_ref.current:
                app_instance.prev_dropoff_location_ref.current.value = selected_display_name.current
            # 也寫入 state_val
            app_instance.prev_dropoff_location_val = selected_display_name.current
            app_instance.page.go("/app/user/previous_booking")
        
        # 住宿預訂地點選擇
        elif is_hotel_booking and booking_index is not None:
            controller = app_instance.previous_booking_controller
            coords = (selected_coords.current.latitude, selected_coords.current.longitude) if selected_coords.current else None
            controller.update_booking_location(booking_index, selected_display_name.current, coords)
            logger.info(f"已更新第 {booking_index} 筆住宿地點: {selected_display_name.current}")
            app_instance.page.go("/app/user/previous_booking")
        # --- ↑↑↑ 新增結束 ↑↑↑ ---
        
        # (保留舊的 booking_data 邏輯，以防萬一)
        elif target_key in ["arrival_location", "return_location"]:
            app_instance.booking_data[target_key] = selected_display_name.current
            app_instance.page.go("/app/user/previous_booking")
        
        else:
            logger.error(f"on_confirm_click 遇到未處理的 target_key: {target_key}")
            app_instance.page.go("/app/user/previous_booking")
    # --- ↑↑↑ 修改結束 ↑↑↑ ---

    # --- ↓↓↓ 修改點：更新 on_cancel_click ↓↓↓ ---
    def on_cancel_click(e):
        logger.info("取消選擇地點")
        if target_key in ["instant_pickup", "instant_dropoff"]:
            app_instance.page.go("/app/user/instant_booking")
        # (明確處理所有返回 previous_booking 的情況)
        elif target_key in ["prev_pickup", "prev_dropoff", "arrival_location", "return_location"] or is_hotel_booking:
            app_instance.page.go("/app/user/previous_booking")
        else:
            app_instance.page.go("/app/user/previous_booking") # 預設返回
    # --- ↑↑↑ 修改結束 ↑↑↑ ---


    # --- 5. 建立控制項 ---
    initial_center = USER_DASHBOARD_DEFAULT_LOCATION
    initial_marker = []
    
    # --- ↓↓↓ 修改點：讀取現有值 ↓↓↓ ---
    existing_location = None
    if target_key == "instant_pickup":
        if app_instance.pickup_location_ref.current:
            existing_location = app_instance.pickup_location_ref.current.value
            
    elif target_key == "instant_dropoff":
        if app_instance.dropoff_location_ref.current:
            existing_location = app_instance.dropoff_location_ref.current.value
            
    # --- 新增的邏輯 ---
    elif target_key == "prev_pickup":
        # 優先從 state_val 讀取，因為 Ref 可能還沒建立
        existing_location = app_instance.prev_pickup_location_val
            
    elif target_key == "prev_dropoff":
        existing_location = app_instance.prev_dropoff_location_val
    # --- 新增結束 ---
            
    elif target_key in ["arrival_location", "return_location"]:
        existing_location = app_instance.booking_data.get(target_key)
    # --- ↑↑↑ 修改結束 ↑↑↑ ---


    # 使用 LocationService 處理現有位置（僅在有有效位置時才執行）
    if existing_location and location_service.geolocator:
        # 跳過經緯度格式的字串，避免不必要的地理編碼
        if not (',' in existing_location and all(c.replace('.', '').replace('-', '').replace(' ', '').isdigit() or c in '°NS,EW ' for c in existing_location)):
            try:
                logger.info(f"為現有位置進行地理編碼: {existing_location}")
                result = location_service.geocode(existing_location, country_code="TW")
                if result:
                    latitude, longitude, address = result
                    initial_center = (latitude, longitude)
                    coords = map.MapLatitudeLongitude(latitude, longitude)
                    initial_marker = [create_marker(coords)]
                    selected_coords.current = coords
                    selected_display_name.current = address
                    logger.info(f"現有位置定位成功: {address}")
            except Exception as e:
                logger.warning(f"無法為 '{existing_location}' 預先定位: {e}")

    map_control = map.Map(
        ref=map_control_ref,
        expand=True,
        initial_zoom=16,
        initial_center=map.MapLatitudeLongitude(*initial_center),
        on_tap=on_map_tap,
        layers=[
            map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
            map.MarkerLayer(ref=marker_layer_ref, markers=initial_marker),
        ],
    )

    # --- 6. 組合 View (保持不變) ---
    view.padding = 0
    view.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_cancel_click),
        title=ft.TextField(
            ref=search_bar_ref,
            label="搜尋地點...",
            on_submit=on_search_click,
            border=ft.InputBorder.NONE,
            color=COLOR_TEXT_DARK
        ),
        actions=[
            ft.Container(
                content=ft.ProgressRing(
                    ref=search_progress_ring_ref,
                    visible=False,
                    width=20,
                    height=20,
                    stroke_width=2.5,
                    color=COLOR_BRAND_YELLOW
                ),
                padding=ft.padding.only(right=15, top=12)
            ),
            ft.IconButton(icon=ft.Icons.SEARCH, on_click=on_search_click)
        ],
        bgcolor=ft.Colors.WHITE
    )
    view.controls = [
        ft.Stack(
            controls=[
                map_control,
                # 頂部地址顯示
                ft.Container(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    ref=selected_address_text_ref,
                                    value="請點擊地圖選擇地點",
                                    size=14,
                                    color=COLOR_TEXT_DARK,
                                    text_align=ft.TextAlign.CENTER,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True
                                ),
                                ft.ProgressRing(
                                    ref=address_loading_indicator_ref,
                                    visible=False,
                                    width=20,
                                    height=20,
                                    stroke_width=2,
                                    color=COLOR_BRAND_YELLOW
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                        padding=10,
                        border_radius=8,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.BLACK26)
                    ),
                    alignment=ft.alignment.top_center,
                    padding=ft.padding.only(top=20),
                    top=0,
                    left=20,
                    right=20
                ),
                # 底部確認按鈕
                ft.Container(
                    content=ft.ElevatedButton(
                        text="確認地點",
                        icon=ft.Icons.CHECK_CIRCLE,
                        on_click=on_confirm_click,
                        width=WINDOW_WIDTH * 0.9,
                        height=50,
                        bgcolor=COLOR_BRAND_YELLOW,
                        color=COLOR_TEXT_DARK
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=20),
                    bottom=0,
                    left=0,
                    right=0
                )
            ],
            expand=True
        )
    ]
    return view