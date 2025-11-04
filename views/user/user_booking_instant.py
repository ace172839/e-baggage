# views/user/user_booking_instant.py
import flet as ft
import flet_map as map
from constants import *
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_instant_booking_content(app_instance: 'App') -> ft.Stack:
    """
    建立「即時預約」的內容 (地圖 + 浮動表單)
    """
    logger.info("正在建立「即時預約」內容 (build_instant_booking_content)")

    # --- 1. 定義地圖元件 ---
    map_control = map.Map(
        expand=True,
        initial_center=map.MapLatitudeLongitude(25.04, 121.56), # 台北
        initial_zoom=13,
        layers=[
            map.TileLayer(
                url_template="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                subdomains=["a", "b", "c"],
            ),
            map.MarkerLayer(
                markers=[
                    map.Marker(
                        coordinates=map.MapLatitudeLongitude(25.04, 121.56),
                        content=ft.Icon(ft.Icons.PERSON_PIN_CIRCLE, size=50, color=ft.Colors.RED_600)
                    ),
                ]
            ),
        ],
    )

    # --- 2. 定義表單元件 (浮動) ---
    form_container = ft.Container(
        alignment=ft.alignment.bottom_center,
        content=ft.Container(
            width=375,
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26),
            
            content=ft.Column(
                controls=[
                    ft.Text("即時預約", size=24, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="取件地址:",
                        prefix_icon=ft.Icons.MY_LOCATION,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                    ),
                    ft.TextField(
                        label="目的地:",
                        prefix_icon=ft.Icons.FLAG,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                    ),
                    ft.Row(
                        controls=[
                            ft.TextField(
                                label="預約件數:",
                                prefix_icon=ft.Icons.WORK_HISTORY,
                                border_radius=8,
                                bgcolor=ft.Colors.WHITE,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CAMERA_ALT,
                                icon_size=30,
                                tooltip="掃描行李 (AI)",
                                on_click=lambda _: app_instance.handle_scan_baggage(),
                                bgcolor=ft.Colors.WHITE,
                                height=55,
                                width=55,
                            )
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.TextField(
                        label="附註項目:",
                        prefix_icon=ft.Icons.EDIT_NOTE,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.ElevatedButton(
                        text="確認預約",
                        icon=ft.Icons.CHECK_CIRCLE,
                        height=50,
                        bgcolor=COLOR_BRAND_YELLOW,
                        color=COLOR_TEXT_DARK,
                        on_click=lambda _: print("確認預約按鈕被點擊"),
                    )
                ],
                spacing=10,
            )
        )
    )

    # --- 3. 建立並回傳 Stack ---
    return ft.Stack(
        controls=[
            map_control,    # 地圖在最底層
            form_container, # 表單浮動在上面
        ],
        expand=True
    )