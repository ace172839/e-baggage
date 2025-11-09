import logging
import flet as ft
from typing import TYPE_CHECKING

from config import WINDOW_HEIGHT, WINDOW_WIDTH, SCAN_RESULT_LSIT
from constants import *

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_scan_view(app_instance: 'App') -> ft.View:
    
    logger.info("Building Scan View")
    
    return ft.View(
        route="/app/user/scan",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("掃描行李", color=ft.Colors.BLACK), 
            bgcolor=COLOR_BRAND_YELLOW, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/user/booking_instant"), 
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
                            on_click=app_instance.handle_scan_start,
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
        route="/app/user/scan_results",
        bgcolor=ft.Colors.BLACK,
        appbar=ft.AppBar(
            title=ft.Text("掃描結果", color=ft.Colors.BLACK), 
            bgcolor=COLOR_BRAND_YELLOW, 
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, 
                on_click=lambda _: app_instance.page.go("/app/user/scan"), 
                icon_color=ft.Colors.WHITE
            )
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
                                ft.Text("請問是否正確？", size=16, color=COLOR_TEXT_DARK),
                                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="不正確",
                                            icon=ft.Icons.CANCEL,
                                            height=50,
                                            bgcolor=ft.Colors.RED_100,
                                            color=ft.Colors.RED_800,
                                            on_click=app_instance.handle_scan_reject,
                                            expand=True,
                                        ),
                                        ft.ElevatedButton(
                                            text="確認正確",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            height=50,
                                            bgcolor=ft.Colors.GREEN_100,
                                            color=ft.Colors.GREEN_800,
                                            on_click=app_instance.handle_scan_confirm,
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