import logging
import flet as ft
import flet_map as map
from typing import TYPE_CHECKING

from config import LOCATION_GRAND_HOTEL, LOCATION_TAIPEI_101, LOCATION_TAIPEI_CITY_HALL, USER_DASHBOARD_MAP_TEMPLATE, MAP_ROUTING_CITYHALL_101, MAP_ROUTING_101_GRAND_HOTEL
from config import WINDOW_HEIGHT, WINDOW_WIDTH, SCAN_RESULT_LSIT
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
        initial_zoom=16,
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
        bgcolor=ft.Colors.GREY_600,
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

def build_driver_tracking_view_101(app_instance: 'App') -> ft.View:
    
    logger.info("Building Driver Tracking View")
    
    driver_coords = LOCATION_TAIPEI_CITY_HALL
    pickup_coords = LOCATION_TAIPEI_101
    
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
        coordinates=[map.MapLatitudeLongitude(coord[1], coord[0]) for coord in MAP_ROUTING_CITYHALL_101["routes"][0]["geometry"]["coordinates"]],
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
                ft.Text("正在前往：   台北101", color=ft.Colors.BLACK),
                ft.Text("車上行李數：  0件 / 8件", color=ft.Colors.BLACK),
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
        route="/app/driver/tracking_101",
        padding=0,
        appbar=ft.AppBar(title=ft.Text("前往乘客地點"), bgcolor=ft.Colors.AMBER),
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

def build_driver_tracking_view_hotel(app_instance: 'App') -> ft.View:
    
    logger.info("Building Driver Tracking View")
    
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
                ft.Text("正在前往：   圓山大飯店", color=ft.Colors.BLACK),
                ft.Text("車上行李數：  5件 / 8件", color=ft.Colors.BLACK),
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
        route="/app/driver/tracking_101",
        padding=0,
        appbar=ft.AppBar(title=ft.Text("前往旅館地點"), bgcolor=ft.Colors.AMBER),
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

def build_scan_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Scan View")
    
    return ft.View(
        route="/app/driver/scan",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("掃描行李", color=ft.Colors.WHITE), 
            bgcolor=ft.Colors.BLACK, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/driver"), 
                icon_color=ft.Colors.WHITE
            )
        ),
        controls=[
            ft.Stack(
                controls=[
                    ft.Image(
                        src=f"images/baggages.jpg", 
                        fit=ft.ImageFit.COVER,
                        width=WINDOW_WIDTH,
                        opacity=0.7
                    ),
                    ft.Container(
                        border=ft.border.all(4, ft.Colors.GREEN_ACCENT),
                        border_radius=10,
                        width=300,
                        height=300,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="掃描行李",
                            icon=ft.Icons.CAMERA,
                            height=60,
                            on_click=app_instance.handle_driver_scan_start,
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN,
                        ),
                        alignment=ft.alignment.bottom_center,
                        padding=50
                    ),
                    ft.ProgressRing(width=64, height=64, stroke_width=8, visible=False)
                ],
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    )

def build_scan_results_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Scan Results View")
    scan_result_text = ""
    for baggage in SCAN_RESULT_LSIT:
        scan_result_text += f"{baggage['size']}吋{baggage['color']}{baggage['type']} {baggage['quantity']} 件\n"
    app_instance.scan_results = len(SCAN_RESULT_LSIT)
    
    return ft.View(
        route="/app/driver/scan_results",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("掃描結果", color=ft.Colors.WHITE), 
            bgcolor=ft.Colors.BLACK
        ),
        controls=[
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src=f"images/baggages.jpg", 
                            fit=ft.ImageFit.CONTAIN,
                            width=WINDOW_WIDTH,
                            height=WINDOW_HEIGHT * 0.6,
                            opacity=0.5
                        ),
                        expand=2
                    ),
                    ft.Container(
                        padding=10,
                        bgcolor=COLOR_BG_LIGHT_TAN,
                        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
                        content=ft.Column(
                            controls=[
                                ft.Text("掃描結果", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                ft.Text(scan_result_text, size=14, color=ft.Colors.GREY_800),
                                ft.Text("已將照片上傳至雲端保存，下車時旅館端會再次核實", size=16, color=COLOR_TEXT_DARK),
                                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="返回",
                                            icon=ft.Icons.CANCEL,
                                            height=50,
                                            bgcolor=ft.Colors.RED_100,
                                            color=ft.Colors.RED_800,
                                            on_click=lambda _: app_instance.page.go("/app/driver"),
                                            expand=True,
                                        ),
                                        ft.ElevatedButton(
                                            text="啟程",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            height=50,
                                            bgcolor=ft.Colors.GREEN_100,
                                            color=ft.Colors.GREEN_800,
                                            on_click=lambda _: app_instance.page.go("/splash/user"),
                                            expand=True,
                                        )
                                    ]
                                )
                            ],
                            scroll=ft.ScrollMode.ADAPTIVE
                        ),
                        expand=3
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )