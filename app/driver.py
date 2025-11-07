import logging
import flet as ft
import flet_map as map
from typing import TYPE_CHECKING

from config import LOCATION_BANQIAO_STATION, LOCATION_TAIPEI_101, LOCATION_TAIPEI_CITY_HALL, USER_DASHBOARD_MAP_TEMPLATE
from config import WINDOW_HEIGHT, WINDOW_WIDTH
from constants import *

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_driver_home_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Driver Home View")
    
    driver_coords = LOCATION_TAIPEI_CITY_HALL

    driver_map = map.Map(
        ref=app_instance.map_ref,
        expand=True,
        initial_zoom=15,
        initial_center=map.MapLatitudeLongitude(*driver_coords),
        layers=[
            map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
            map.MarkerLayer(
                ref=app_instance.marker_layer_ref,
                markers=[
                    map.Marker(
                        ref=app_instance.driver_marker_ref,
                        content=ft.Icon(ft.Icons.LOCAL_TAXI, color=ft.Colors.GREEN, size=35),
                        coordinates=map.MapLatitudeLongitude(*driver_coords),
                    ),
                ]
            ),
            map.PolylineLayer(
                ref=app_instance.polyline_layer_ref,
                polylines=[]
            )
        ]
    )

    button_bar = ft.Container(
        height=WINDOW_HEIGHT / 4,
        padding=20,
        bgcolor=COLOR_BG_LIGHT_TAN,
        content=ft.Row(
            controls=[
                ft.ElevatedButton("更多", icon=ft.Icons.MENU, height=60, expand=True),
                ft.ElevatedButton("導航", icon=ft.Icons.NAVIGATION, height=60, expand=True),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
    )

    return ft.View(
        route="/app/driver",
        padding=0,
        controls=[
            ft.Column(
                controls=[
                    ft.Container(content=driver_map, expand=True),
                    button_bar
                ],
                expand=True,
                spacing=0
            )
        ]
    )

def build_driver_tracking_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Driver Tracking View")
    
    driver_coords = LOCATION_TAIPEI_CITY_HALL
    pickup_coords = LOCATION_TAIPEI_101
    dropoff_coords = LOCATION_BANQIAO_STATION
    
    if app_instance.map_ref.current:
        app_instance.map_ref.current.center = map.MapLatitudeLongitude(*driver_coords)
        app_instance.map_ref.current.zoom = 14
    
    driver_marker = map.Marker(
        ref=app_instance.driver_marker_ref,
        content=ft.Icon(ft.Icons.LOCAL_TAXI, color=ft.Colors.GREEN, size=35),
        coordinates=map.MapLatitudeLongitude(*driver_coords),
    )
    pickup_marker = map.Marker(
        content=ft.Icon(ft.Icons.PERSON_PIN_CIRCLE, color=ft.Colors.BLUE, size=35),
        coordinates=map.MapLatitudeLongitude(*pickup_coords),
    )
    
    if app_instance.marker_layer_ref.current:
        app_instance.marker_layer_ref.current.markers = [driver_marker, pickup_marker]
        
    route_to_pickup = map.PolylineMarker(
        coordinates=[
            map.MapLatitudeLongitude(*driver_coords),
            map.MapLatitudeLongitude(*pickup_coords),
        ],
        color=ft.Colors.GREEN_700,
        border_stroke_width=5
    )
    if app_instance.polyline_layer_ref.current:
        app_instance.polyline_layer_ref.current.polylines = [route_to_pickup]

    info_panel = ft.Container(
        height=WINDOW_HEIGHT / 3,
        padding=20,
        bgcolor=COLOR_BG_LIGHT_TAN,
        content=ft.Column(
            controls=[
                ft.Text("當前動態", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("司機名稱：王小明"),
                ft.Text("司機車牌：ABC-6666"),
                ft.Text("司機電話：0912345678"),
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
        route="/app/driver/tracking",
        padding=0,
        appbar=ft.AppBar(title=ft.Text("前往乘客地點")),
        controls=[
            ft.Column(
                controls=[
                    ft.Container(content=app_instance.map_ref.current, expand=True),
                    info_panel
                ],
                expand=True,
                spacing=0
            )
        ]
    )