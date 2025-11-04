# views/user/user_booking_instant.py
import flet as ft
import flet_map as map
from constants import *
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_instant_booking_content(app_instance: 'App'):
    def handle_tap(e: map.MapTapEvent):
        logger.info(f"地圖被點擊 at 經度: {e.longitude}, 緯度: {e.latitude}")
    
    return ft.Column(
        [
            ft.Text(
                "Click anywhere to add a Marker, right-click to add a CircleMarker."
            ),
            map.Map(
                expand=True,
                on_init=lambda e: logger.info("地圖初始化完成"),
                initial_zoom=4.2,
                initial_center=map.MapLatitudeLongitude(15, 10),
                interaction_configuration=map.MapInteractionConfiguration(
                    flags=map.MapInteractiveFlag.ALL
                ),
                on_tap=handle_tap,
                on_secondary_tap=handle_tap,
                on_long_press=handle_tap,
                on_event=lambda e: logger.info(f"Map event: {e.event_type}"),
                layers=[
                    map.TileLayer(
                        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        on_image_error=lambda e: print("TileLayer Error"),
                    ),
                    map.RichAttribution(
                        attributions=[
                            map.TextSourceAttribution(
                                text="OpenStreetMap Contributors",
                                on_click=lambda e: e.page.launch_url(
                                    "https://openstreetmap.org/copyright"
                                ),
                            ),
                            map.TextSourceAttribution(
                                text="Flet",
                                on_click=lambda e: e.page.launch_url(
                                    "https://flet.dev"
                                ),
                            ),
                        ]
                    ),
                    map.SimpleAttribution(
                        text="Flet",
                        alignment=ft.alignment.top_right,
                        on_click=lambda e: print("Clicked SimpleAttribution"),
                    ),
                    # map.MarkerLayer(
                    #     ref=marker_layer_ref,
                    #     markers=[
                    #         map.Marker(
                    #             content=ft.Icon(ft.Icons.LOCATION_ON),
                    #             coordinates=map.MapLatitudeLongitude(30, 15),
                    #         ),
                    #         map.Marker(
                    #             content=ft.Icon(ft.Icons.LOCATION_ON),
                    #             coordinates=map.MapLatitudeLongitude(10, 10),
                    #         ),
                    #         map.Marker(
                    #             content=ft.Icon(ft.Icons.LOCATION_ON),
                    #             coordinates=map.MapLatitudeLongitude(25, 45),
                    #         ),
                    #     ],
                    # ),
                    # map.CircleLayer(
                    #     ref=circle_layer_ref,
                    #     circles=[
                    #         map.CircleMarker(
                    #             radius=10,
                    #             coordinates=map.MapLatitudeLongitude(16, 24),
                    #             color=ft.Colors.RED,
                    #             border_color=ft.Colors.BLUE,
                    #             border_stroke_width=4,
                    #         ),
                    #     ],
                    # ),
                    map.PolygonLayer(
                        polygons=[
                            map.PolygonMarker(
                                label="Popular Touristic Area",
                                label_text_style=ft.TextStyle(
                                    color=ft.Colors.BLACK,
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE),
                                coordinates=[
                                    map.MapLatitudeLongitude(10, 10),
                                    map.MapLatitudeLongitude(30, 15),
                                    map.MapLatitudeLongitude(25, 45),
                                ],
                            ),
                        ],
                    ),
                    map.PolylineLayer(
                        polylines=[
                            map.PolylineMarker(
                                border_stroke_width=3,
                                border_color=ft.Colors.RED,
                                gradient_colors=[ft.Colors.BLACK, ft.Colors.BLACK],
                                color=ft.Colors.with_opacity(0.6, ft.Colors.GREEN),
                                coordinates=[
                                    map.MapLatitudeLongitude(10, 10),
                                    map.MapLatitudeLongitude(30, 15),
                                    map.MapLatitudeLongitude(25, 45),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        height=400,
        expand=True,
    )


# def build_instant_booking_content(app_instance: 'App') -> ft.Stack:
#     """
#     建立「即時預約」的內容 (地圖 + 浮動表單)
#     """
#     logger.info("正在建立「即時預約」內容 (build_instant_booking_content)")

#     map_control = map.Map(
#         expand=True,
#         on_init=lambda e: logger.info("地圖初始化完成"),
#         layers=[
#             map.TileLayer(
#                 url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
#             ),
#         ],
#     )

#     # --- 2. 定義表單元件 (浮動) ---
#     form_container = ft.Container(
#         alignment=ft.alignment.bottom_center,
#         content=ft.Container(
#             width=375,
#             padding=20,
#             bgcolor=COLOR_BG_LIGHT_TAN,
#             border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
#             shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26),
            
#             content=ft.Column(
#                 controls=[
#                     ft.Text("即時預約", size=24, weight=ft.FontWeight.BOLD),
#                     ft.TextField(
#                         label="取件地址:",
#                         prefix_icon=ft.Icons.MY_LOCATION,
#                         border_radius=8,
#                         bgcolor=ft.Colors.WHITE,
#                     ),
#                     ft.TextField(
#                         label="目的地:",
#                         prefix_icon=ft.Icons.FLAG,
#                         border_radius=8,
#                         bgcolor=ft.Colors.WHITE,
#                     ),
#                     ft.Row(
#                         controls=[
#                             ft.TextField(
#                                 label="預約件數:",
#                                 prefix_icon=ft.Icons.WORK_HISTORY,
#                                 border_radius=8,
#                                 bgcolor=ft.Colors.WHITE,
#                                 expand=True,
#                             ),
#                             ft.IconButton(
#                                 icon=ft.Icons.CAMERA_ALT,
#                                 icon_size=30,
#                                 tooltip="掃描行李 (AI)",
#                                 on_click=lambda _: app_instance.handle_scan_baggage(),
#                                 bgcolor=ft.Colors.WHITE,
#                                 height=55,
#                                 width=55,
#                             )
#                         ],
#                         vertical_alignment=ft.CrossAxisAlignment.START,
#                     ),
#                     ft.TextField(
#                         label="附註項目:",
#                         prefix_icon=ft.Icons.EDIT_NOTE,
#                         border_radius=8,
#                         bgcolor=ft.Colors.WHITE,
#                     ),
#                     ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
#                     ft.ElevatedButton(
#                         text="確認預約",
#                         icon=ft.Icons.CHECK_CIRCLE,
#                         height=50,
#                         bgcolor=COLOR_BRAND_YELLOW,
#                         color=COLOR_TEXT_DARK,
#                         on_click=lambda _: print("確認預約按鈕被點擊"),
#                     )
#                 ],
#                 spacing=10,
#             )
#         )
#     )

#     # --- 3. 建立並回傳 Stack ---
#     return ft.Stack(
#         controls=[
#             map_control,    # 地圖在最底層
#             form_container, # 表單浮動在上面
#         ],
#         expand=True
#     )