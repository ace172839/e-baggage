import logging
import flet as ft
import flet_map as map
from typing import TYPE_CHECKING

from config import LOCATION_GRAND_HOTEL, LOCATION_TAIPEI_101, LOCATION_TAIPEI_CITY_HALL, USER_DASHBOARD_MAP_TEMPLATE, MAP_ROUTING_101_GRAND_HOTEL
from config import WINDOW_HEIGHT, WINDOW_WIDTH
from constants import *

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_user_tracking_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building User Tracking View")
    
    driver_coords = LOCATION_TAIPEI_101
    pickup_coords = LOCATION_GRAND_HOTEL
    
    driver_marker = map.Marker(
        ref=app_instance.driver_marker_ref,
        content=ft.Icon(ft.Icons.LOCAL_TAXI, color=ft.Colors.GREEN, size=35),
        coordinates=map.MapLatitudeLongitude(*driver_coords),
    )
    pickup_marker = map.Marker(
        content=ft.Icon(ft.Icons.PERSON_PIN_CIRCLE, color=ft.Colors.BLUE, size=35),
        coordinates=map.MapLatitudeLongitude(*pickup_coords),
    )
    
    marker_layer = map.MarkerLayer(
        ref=app_instance.marker_layer_ref,
        markers=[driver_marker, pickup_marker]
    )
        
    route_to_pickup = map.PolylineMarker(
        coordinates=[map.MapLatitudeLongitude(coord[1], coord[0]) for coord in MAP_ROUTING_101_GRAND_HOTEL["routes"][0]["geometry"]["coordinates"]],
        color=ft.Colors.GREEN_700,
        border_stroke_width=5
    )

    polyline_layer = map.PolylineLayer(
        ref=app_instance.polyline_layer_ref,
        polylines=[route_to_pickup]
    )

    tracking_map = map.Map(
        ref=app_instance.map_ref,
        expand=True,
        initial_zoom=16,
        initial_center=map.MapLatitudeLongitude(*driver_coords),
        layers=[
            map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
            marker_layer,
            polyline_layer
        ]
    )

    info_panel = ft.Container(
        height=WINDOW_HEIGHT / 3,
        padding=20,
        bgcolor=COLOR_BG_LIGHT_TAN,
        content=ft.Column(
            controls=[
                ft.Text("當前動態", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text("司機名稱：王小明", color=ft.Colors.BLACK),
                ft.Text("司機車牌：ABC-6666", color=ft.Colors.BLACK),
                ft.Text("司機電話：0912345678", color=ft.Colors.BLACK),
                ft.TextField(
                    label="傳送訊息...",
                    prefix_icon=ft.Icons.CHAT,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )

    return ft.View(
        route="/app/user/current_order",
        padding=0,
        appbar=ft.AppBar(
            title=ft.Text("訂單追蹤", color=ft.Colors.BLACK), 
            bgcolor=COLOR_BRAND_YELLOW, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/user/dashboard"), 
                icon_color=ft.Colors.WHITE
            )
        ),
        controls=[
            ft.Column(
                controls=[
                    ft.Container(content=tracking_map, expand=True),
                    info_panel
                ],
                expand=True,
                spacing=0
            )
        ]
    )