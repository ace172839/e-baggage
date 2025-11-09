import logging
import flet as ft
import flet_map as map
from typing import TYPE_CHECKING

from config import LOCATION_GRAND_HOTEL, LOCATION_TAIPEI_101, USER_DASHBOARD_MAP_TEMPLATE
from constants import *

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_confirm_order_view(app_instance: 'App') -> ft.View:
    logger.info("Building Confirm Order View")
    
    pickup_name = "圓山大飯店"
    pickup_coords = LOCATION_GRAND_HOTEL
    dropoff_name = "台北 101"
    dropoff_coords = LOCATION_TAIPEI_101
    
    if app_instance.pickup_location_ref.current and "板橋" in app_instance.pickup_location_ref.current.value:
        pickup_name, pickup_coords = "圓山大飯店", LOCATION_GRAND_HOTEL
        dropoff_name, dropoff_coords = "台北 101", LOCATION_TAIPEI_101
    elif app_instance.pickup_location_ref.current and "101" in app_instance.pickup_location_ref.current.value:
        pickup_name, pickup_coords = "台北 101", LOCATION_TAIPEI_101
        dropoff_name, dropoff_coords = "圓山大飯店", LOCATION_GRAND_HOTEL

    confirm_map = map.Map(
        expand=True,
        initial_zoom=13,
        initial_center=map.MapLatitudeLongitude(
            (pickup_coords[0] + dropoff_coords[0]) / 2,
            (pickup_coords[1] + dropoff_coords[1]) / 2
        ),
        layers=[
            map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
            map.MarkerLayer(
                markers=[
                    map.Marker(
                        content=ft.Icon(ft.Icons.MY_LOCATION, color=ft.Colors.BLUE, size=30),
                        coordinates=map.MapLatitudeLongitude(*pickup_coords),
                    ),
                    map.Marker(
                        content=ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED, size=30),
                        coordinates=map.MapLatitudeLongitude(*dropoff_coords),
                    ),
                ]
            ),
            map.PolylineLayer(
                polylines=[
                    map.PolylineMarker(
                        coordinates=[
                            map.MapLatitudeLongitude(*pickup_coords),
                            map.MapLatitudeLongitude(*dropoff_coords),
                        ],
                        color=ft.Colors.BLUE,
                        border_stroke_width=5
                    )
                ]
            )
        ]
    )

    info_card = ft.Container(
        padding=30,
        bgcolor=COLOR_BG_LIGHT_TAN,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        content=ft.Column(
            controls=[
                ft.Text("訂單確認", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"上車地點：{pickup_name}"),
                ft.Text(f"下車地點：{dropoff_name}"),
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Text("根據您的行李數量及大小，", color=COLOR_TEXT_DARK),
                ft.Text("        推薦車款為: 休旅車", color=COLOR_TEXT_DARK),
                ft.Text("        預計費用為: 250 元", color=COLOR_TEXT_DARK),
                ft.Text("預計行李抵達旅館時間: 50 分鐘", color=COLOR_TEXT_DARK),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="取消",
                            icon=ft.Icons.CANCEL,
                            height=50,
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_800,
                            on_click=app_instance.handle_order_cancel,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="確認",
                            icon=ft.Icons.CHECK_CIRCLE,
                            height=50,
                            bgcolor=ft.Colors.GREEN_100,
                            color=ft.Colors.GREEN_800,
                            on_click=app_instance.handle_order_confirm,
                            expand=True,
                        )
                    ]
                )
            ],
            height=260,
            scroll=ft.ScrollMode.ADAPTIVE,
        )
    )

    return ft.View(
        route="/app/user/confirm_order",
        padding=0,
        appbar=ft.AppBar(
            title=ft.Text("確認您的行程"),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app_instance.page.page.go("/app/user/booking_instant")),
        ),
        controls=[
            ft.Stack(
                controls=[
                    ft.Container(content=confirm_map, expand=True, margin=ft.margin.only(bottom=260)),
                    ft.Container(content=info_card, alignment=ft.alignment.bottom_center)
                ],
                expand=True
            )
        ]
    )