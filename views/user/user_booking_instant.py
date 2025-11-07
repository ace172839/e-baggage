import flet as ft
import flet_map as map
from config import *
from constants import *
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_instant_booking_view(app_instance: 'App') -> ft.View:
    """
    建立「即時預約」的主畫面 (View)
    包含地圖和下方的表單
    """
    logger.info("正在建立「即時預約」主畫面 (build_instant_booking_view)")

    # --- 1. 地圖控制項 ---
    # 地圖控制項被移到 App class (main.py) 的 Ref 中
    # 這樣才能在不同函式中 (例如 handle_select_location) 控制它
    # 我們在這裡初始化地圖
    
    # 檢查 App 實例上是否已經有 map_ref，沒有才建立
    logger.info("初始化地圖控制項")
    app_instance.map_ref.current = map.Map(
        expand=True,
        initial_zoom=16,
        initial_center=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
        interaction_configuration=map.MapInteractionConfiguration(
            flags=map.MapInteractiveFlag.ALL
        ),
        layers=[
            map.TileLayer(
                url_template=USER_DASHBOARD_MAP_TEMPLATE,
            ),
            map.MarkerLayer(
                ref=app_instance.marker_layer_ref,
                markers=[
                    # 預設標記 (台北 101)
                    map.Marker(
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=35),
                        coordinates=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
                    ),
                ],
            ),
        ],
    )
    
    # --- 2. 搜尋框 (預設隱藏) ---
    # 我們將這個搜尋框放在 App 實例中，以便在點擊時顯示
    if not app_instance.search_bar_ref.current:
        app_instance.search_bar_ref.current = ft.Container(
            content=ft.TextField(
                ref=app_instance.search_text_ref,
                label="搜尋地點...",
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                on_submit=app_instance.handle_search_location, # 按下 Enter 時觸發
            ),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
            visible=False # 預設隱藏
        )

    # --- 3. 表單控制項 ---
    form_content = ft.Container(
        width=WINDOW_WIDTH,
        padding=20,
        bgcolor=COLOR_BG_LIGHT_TAN,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26),
        
        content=ft.Column(
            controls=[
                ft.TextField(
                    ref=app_instance.pickup_location_ref,
                    label="上車地點:",
                    prefix_icon=ft.Icons.MY_LOCATION,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    on_focus=app_instance.handle_select_location_pickup, # 點擊時觸發
                    value="台北 101", # Demo 預設值
                ),
                ft.TextField(
                    ref=app_instance.dropoff_location_ref,
                    label="下車地點:",
                    prefix_icon=ft.Icons.FLAG,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    on_focus=app_instance.handle_select_location_dropoff, # 點擊時觸發
                ),
                ft.Row(
                    controls=[
                        ft.TextField(
                            ref=app_instance.notes_ref,
                            label="備註事項:",
                            prefix_icon=ft.Icons.EDIT_NOTE,
                            border_radius=8,
                            bgcolor=ft.Colors.WHITE,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CAMERA_ALT,
                            icon_size=30,
                            tooltip="掃描行李 (AI)",
                            on_click=app_instance.handle_scan_baggage, # 點擊掃描
                            bgcolor=ft.Colors.WHITE,
                            height=55,
                            width=55,
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="取消",
                            icon=ft.Icons.CANCEL,
                            height=50,
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_800,
                            on_click=lambda e: app_instance.page.go("/app/user"),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="確認",
                            icon=ft.Icons.CHECK_CIRCLE,
                            height=50,
                            bgcolor=ft.Colors.GREEN_100,
                            color=ft.Colors.GREEN_800,
                            on_click=app_instance.handle_confirm_instant_booking,
                            expand=True,
                        )
                    ]
                )
            ],
            spacing=10,
        )
    )

    # --- 4. 組合 View ---
    return ft.View(
        route="/app/user",
        padding=0,
        controls=[
            ft.Stack(
                controls=[
                    # 底層：地圖
                    ft.Container(
                        content=app_instance.map_ref.current,
                        expand=True,
                        margin=ft.margin.only(bottom=260) # 預留底部表單空間
                    ),
                    # 中層：搜尋框 (浮動在最上面)
                    app_instance.search_bar_ref.current,
                    
                    # 上層：表單 (浮動在最下面)
                    ft.Container(
                        content=form_content,
                        alignment=ft.alignment.bottom_center
                    )
                ],
                expand=True
            )
        ]
    )