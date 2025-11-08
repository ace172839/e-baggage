import logging
import flet as ft
from typing import TYPE_CHECKING

from config import WINDOW_HEIGHT, WINDOW_WIDTH, SCAN_RESULT_LSIT
from constants import *

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_hotel_view(app_instance: 'App') -> ft.View:
    def hotel_navigator_handler(e: ft.ControlEvent):
        selected_index = int(e.data) 

        if selected_index == 0:
            logger.info("導航到「更多」頁面")
            app_instance.page.go("/app/hotel")
        elif selected_index == 1:
            logger.info("導航到「掃描行李」Demo 頁面")
            app_instance.page.go("/app/hotel/scan")
        elif selected_index == 2:
            logger.info("導航到「首頁」儀表板")
            app_instance.page.go("/app/hotel")
        elif selected_index == 3:
            logger.info("導航到「Check-in」頁面")
            app_instance.page.go("/app/hotel")
        elif selected_index == 4:
            logger.info("導航到「訂單列表」頁面")
            app_instance.page.go("/app/hotel")
        else:
            logger.error(f"未知的導航索引: {selected_index}")
            app_instance.page.go("/app/hotel")


    logger.info("Building Hotel View")
    


    return ft.View(
        route="/app/user/hotel",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("托李福酒店", color=ft.Colors.BLACK), 
            bgcolor=ft.Colors.INDIGO, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/user"),
                icon_color=ft.Colors.WHITE
            )
        ),
        controls=[
            ft.Image(
                src=f"images/hotel.jpg", 
                fit=ft.ImageFit.COVER,
                width=WINDOW_WIDTH,
                opacity=0.7
            ),
            ft.NavigationBar(
                selected_index=2,
                on_change=hotel_navigator_handler,
                bgcolor=COLOR_BACKGROUD_YELLOW,
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.Icons.MORE_HORIZ,
                        label="更多",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.CAMERA_ALT,
                        label="掃描行李",
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.HOME, 
                        label="首頁"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.EXIT_TO_APP,
                        label="Check-in"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.LIST_ALT,
                        label="訂單列表"
                    )
                ]
            )
        ]
    )

def build_scan_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Scan View")
    
    return ft.View(
        route="/app/hotel/scan",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("掃描行李", color=ft.Colors.WHITE), 
            bgcolor=ft.Colors.BLACK, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/hotel"), 
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
                            on_click=app_instance.handle_hotel_scan_start,
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
        route="/app/hotel/scan_results",
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
                                ft.Text("行李確認無誤。請協助自動化 check-in。", size=16, color=COLOR_TEXT_DARK),
                                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="返回",
                                            icon=ft.Icons.CANCEL,
                                            height=50,
                                            bgcolor=ft.Colors.RED_100,
                                            color=ft.Colors.RED_800,
                                            on_click=lambda _: app_instance.page.go("/app/hotel"),
                                            expand=True,
                                        ),
                                        ft.ElevatedButton(
                                            text="開始 Check-in",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            height=50,
                                            bgcolor=ft.Colors.GREEN_100,
                                            color=ft.Colors.GREEN_800,
                                            on_click=lambda _: app_instance.page.go("/splash/user2"),
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