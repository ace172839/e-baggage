import flet as ft
import flet_map as map
from typing import TYPE_CHECKING
from geopy.geocoders import Nominatim
import logging

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
        if target_key not in ["arrival_location", "return_location"]:
            raise ValueError(f"無效的 target_key: {target_key}")
    except (IndexError, ValueError) as e:
        logger.error(f"從路由 '{view.route}' 解析 target_key 失敗: {e}")
        # 返回一個錯誤頁面或導航回上一頁
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
    
    selected_coords = ft.Ref[map.MapLatitudeLongitude]()
    selected_display_name = ft.Ref[str]()

    # --- 3. 輔助函式 ---
    def create_marker(coords: map.MapLatitudeLongitude) -> map.Marker:
        return map.Marker(
            content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_700, size=40),
            coordinates=coords,
        )

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

    # --- 4. 事件處理 ---
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

    def on_search_click(e):
        query = search_bar_ref.current.value
        if not query or not geolocator: return
        
        logger.info(f"正在搜尋: {query}")
        try:
            location = geolocator.geocode(query, country_codes="TW")
            if location:
                coords = map.MapLatitudeLongitude(location.latitude, location.longitude)
                update_selection(coords, location.address, update_map_center=True)
            else:
                app_instance.page.snack_bar = ft.SnackBar(ft.Text(f"找不到地點: {query}"), open=True)
                app_instance.page.update()
        except Exception as ex:
            logger.error(f"地理編碼時發生錯誤: {ex}")
            app_instance.page.snack_bar = ft.SnackBar(ft.Text("搜尋時發生錯誤"), open=True)
            app_instance.page.update()

    def on_confirm_click(e):
        if selected_display_name.current:
            logger.info(f"確認選擇 for '{target_key}': {selected_display_name.current}")
            app_instance.booking_data[target_key] = selected_display_name.current
        else:
            logger.warning("未選擇任何地點，但按下了確認。")
        
        app_instance.page.go("/app/user/booking_previous")

    def on_cancel_click(e):
        app_instance.page.go("/app/user/booking_previous")

    # --- 5. 建立控制項 ---
    initial_center = USER_DASHBOARD_DEFAULT_LOCATION
    initial_marker = []
    
    # 檢查 booking_data 中是否有此 target_key 的現有值
    existing_location = app_instance.booking_data.get(target_key)
    if existing_location and geolocator:
        try:
            location = geolocator.geocode(existing_location, country_codes="TW")
            if location:
                initial_center = (location.latitude, location.longitude)
                coords = map.MapLatitudeLongitude(location.latitude, location.longitude)
                initial_marker = [create_marker(coords)]
                # 同時預先填入選擇狀態
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

    # --- 6. 組合 View ---
    view.padding = 0
    view.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=on_cancel_click),
        title=ft.TextField(
            ref=search_bar_ref,
            label="搜尋地點...",
            on_submit=on_search_click,
            border=ft.InputBorder.NONE,
        ),
        actions=[ft.IconButton(icon=ft.Icons.SEARCH, on_click=on_search_click)],
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
