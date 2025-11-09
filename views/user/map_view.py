import flet as ft
import flet_map as map
from typing import TYPE_CHECKING
from geopy.geocoders import Nominatim
import logging
import threading  # <--- 1. 匯入 threading

from config import WINDOW_WIDTH, USER_DASHBOARD_DEFAULT_LOCATION, USER_DASHBOARD_MAP_TEMPLATE
from constants import *

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
        valid_keys = ["arrival_location", "return_location", "instant_pickup", "instant_dropoff"]
        if target_key not in valid_keys:
            raise ValueError(f"無效的 target_key: {target_key}")
    except (IndexError, ValueError) as e:
        logger.error(f"從路由 '{view.route}' 解析 target_key 失敗: {e}")
        return ft.View(
            route=view.route,
            controls=[ft.Text("錯誤：無效的地圖路由。")],
            appbar=ft.AppBar(title=ft.Text("錯誤"), leading=ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: app_instance.page.go_back()))
        )

    # --- 2. 初始化 & Refs ---
    try:
        geolocator = Nominatim(user_agent="e-baggage-app")
    except Exception as e:
        logger.error(f"初始化 Nominatim 失敗: {e}")
        geolocator = None 

    map_control_ref = ft.Ref[map.Map]()
    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    search_bar_ref = ft.Ref[ft.TextField]()
    search_progress_ring_ref = ft.Ref[ft.ProgressRing]() # <--- 2. 新增 Ref
    
    selected_coords = ft.Ref[map.MapLatitudeLongitude]()
    selected_display_name = ft.Ref[str]()

    # --- 3. 輔助函式 ---
    def create_marker(coords: map.MapLatitudeLongitude) -> map.Marker:
        return map.Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_700, size=40),
            coordinates=coords,
        )

    # update_selection 函式保持不變
    def update_selection(coords: map.MapLatitudeLongitude, display_name: str, update_map_center: bool = False, zoom: float = 16.0):
        logger.info(f"更新地圖選擇: {display_name}")
        selected_coords.current = coords
        selected_display_name.current = display_name
        
        if marker_layer_ref.current:
            marker_layer_ref.current.markers = [create_marker(coords)]
            marker_layer_ref.current.update()
            
        if update_map_center and map_control_ref.current:
            map_control_ref.current.center = coords
            map_control_ref.current.zoom = zoom
            map_control_ref.current.update()

    # on_map_tap 函式保持不變
    def on_map_tap(e: map.MapTapEvent):
        logger.debug(f"地圖點擊: Lat={e.coordinates.latitude}, Lon={e.coordinates.longitude}")
        if not geolocator: return
            
        coords = map.MapLatitudeLongitude(e.coordinates.latitude, e.coordinates.longitude)
        display_name = f"{e.coordinates.latitude:.5f}, {e.coordinates.longitude:.5f}"
        
        try:
            location = geolocator.reverse((e.coordinates.latitude, e.coordinates.longitude), exactly_one=True, language="zh-TW")
            if location: display_name = location.address
        except Exception as ex:
            logger.warning(f"反向地理編碼失敗: {ex}")
            
        update_selection(coords, display_name, update_map_center=True)


    # --- 4. 事件處理 (修改點) ---

    # --- 4a. 新增：背景執行緒函式 ---
    def search_worker_thread(query_str: str):
        """
        在背景執行緒中執行地理編碼，避免 UI 凍結。
        (這包含了您原本 on_search_click 的主要邏輯)
        """
        logger.info(f"[Thread] 正在搜尋: {query_str}")
        if not geolocator:
            logger.error("[Thread] Geolocator 未初始化")
            return

        try:
            # --- 這行是耗時的網路操作 ---
            location = geolocator.geocode(query_str, country_codes="TW")
            
            if location:
                logger.info(f"[Thread] 找到地點: {location.address}")
                lat = round(location.latitude, 4)
                lon = round(location.longitude, 4)
                coords = map.MapLatitudeLongitude(lat, lon)
                
                # --- 更新 Refs (就像您在 main.py 的動畫中所做的) ---
                selected_coords.current = coords
                selected_display_name.current = location.address
                
                if marker_layer_ref.current:
                    marker_layer_ref.current.markers = [create_marker(coords)]
                    marker_layer_ref.current.update()
                    
                if map_control_ref.current:
                    logger.debug(f"[Thread] 更新地圖中心: {coords}")
                    map_control_ref.current.center_on(coords, 16)
                    # map_control_ref.current.center = coords
                    # map_control_ref.current.zoom = 16
                    map_control_ref.current.update()
                
                # --- 隱藏載入中圓圈 ---
                if search_progress_ring_ref.current:
                    search_progress_ring_ref.current.visible = False
                    search_progress_ring_ref.current.update()
                
            else:
                logger.warning(f"[Thread] 找不到地點: {query_str}")
                app_instance.page.snack_bar = ft.SnackBar(ft.Text(f"找不到地點: {query_str}"), open=True)
                if search_progress_ring_ref.current:
                    search_progress_ring_ref.current.visible = False
                    search_progress_ring_ref.current.update()
                app_instance.page.update()
                
        except Exception as ex:
            logger.error(f"[Thread] 地理編碼時發生錯誤: {ex}")
            app_instance.page.snack_bar = ft.SnackBar(ft.Text("搜尋時發生錯誤"), open=True)
            if search_progress_ring_ref.current:
                search_progress_ring_ref.current.visible = False
                search_progress_ring_ref.current.update()
            app_instance.page.update()

    # --- 4b. 修改：原本的 on_search_click ---
    def on_search_click(e):
        query = search_bar_ref.current.value
        if not query or not geolocator: 
            return
        
        logger.info(f"請求搜尋: {query}")
        
        # 立即顯示載入指示器
        if search_progress_ring_ref.current:
            search_progress_ring_ref.current.visible = True
            search_progress_ring_ref.current.update()
        
        # 在新執行緒中啟動搜尋，避免凍結
        threading.Thread(
            target=search_worker_thread,
            args=(query,), # 將 query 作為參數傳遞
            daemon=True   # 確保 App 關閉時執行緒也會關閉
        ).start()

    # on_confirm_click 和 on_cancel_click 保持不變
    def on_confirm_click(e):
        if not selected_display_name.current:
            logger.warning("未選擇任何地點，但按下了確認。")
            if target_key in ["instant_pickup", "instant_dropoff"]:
                app_instance.page.go("/app/user/booking_instant")
            else:
                app_instance.page.go("/app/user/booking_previous")
            return

        logger.info(f"確認選擇 for '{target_key}': {selected_display_name.current}")
        
        if target_key == "instant_pickup":
            if app_instance.pickup_location_ref.current:
                app_instance.pickup_location_ref.current.value = selected_display_name.current
            app_instance.page.go("/app/user/booking_instant")
        
        elif target_key == "instant_dropoff":
            if app_instance.dropoff_location_ref.current:
                app_instance.dropoff_location_ref.current.value = selected_display_name.current
            app_instance.page.go("/app/user/booking_instant")
        
        elif target_key in ["arrival_location", "return_location"]:
            app_instance.booking_data[target_key] = selected_display_name.current
            app_instance.page.go("/app/user/booking_previous")
        
        else:
            logger.error(f"on_confirm_click 遇到未處理的 target_key: {target_key}")
            app_instance.page.go_back()

    def on_cancel_click(e):
        if target_key in ["instant_pickup", "instant_dropoff"]:
            app_instance.page.go("/app/user/booking_instant")
        else:
            app_instance.page.go("/app/user/booking_previous")

    # --- 5. 建立控制項 ---
    initial_center = USER_DASHBOARD_DEFAULT_LOCATION
    initial_marker = []
    
    existing_location = None
    if target_key == "instant_pickup":
        if app_instance.pickup_location_ref.current:
            existing_location = app_instance.pickup_location_ref.current.value
    elif target_key == "instant_dropoff":
        if app_instance.dropoff_location_ref.current:
            existing_location = app_instance.dropoff_location_ref.current.value
    elif target_key in ["arrival_location", "return_location"]:
        existing_location = app_instance.booking_data.get(target_key)

    if existing_location and geolocator:
        try:
            location = geolocator.geocode(existing_location, country_codes="TW")
            if location:
                initial_center = (location.latitude, location.longitude)
                coords = map.MapLatitudeLongitude(location.latitude, location.longitude)
                initial_marker = [create_marker(coords)]
                selected_coords.current = coords
                selected_display_name.current = location.address
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

    # --- 6. 組合 View (修改點) ---
    view.padding = 0
    view.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_cancel_click),
        title=ft.TextField(
            ref=search_bar_ref,
            label="搜尋地點...",
            on_submit=on_search_click, # 確保 on_submit 也綁定
            border=ft.InputBorder.NONE,
            color=COLOR_TEXT_DARK
        ),
        actions=[
            # --- 4. 新增：載入中圓圈 ---
            ft.Container(
                content=ft.ProgressRing(
                    ref=search_progress_ring_ref,
                    visible=False,
                    width=20,
                    height=20,
                    stroke_width=2.5,
                    color=COLOR_BRAND_YELLOW # 給它一個顏色
                ),
                padding=ft.padding.only(right=15, top=12) # 調整一下位置
            ),
            ft.IconButton(icon=ft.Icons.SEARCH, on_click=on_search_click)
        ],
        bgcolor=ft.Colors.WHITE
    )
    view.controls = [
        ft.Stack(
            controls=[
                map_control,
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