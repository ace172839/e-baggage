import flet as ft
import random
from typing import TYPE_CHECKING
from config import USER_DASHBOARD_IMAGE, USER_DASHBOARD_MARQUEE_MESSAGES
from constants import *

if TYPE_CHECKING:
    from main import App

def build_dashboard_content(app_instance: 'App') -> ft.Container:
    # 隨機跑馬燈文字
    selected_message = random.choice(USER_DASHBOARD_MARQUEE_MESSAGES)

    return ft.Container(
        expand=True,
        bgcolor=COLOR_BG_LIGHT_TAN,
        content=ft.Column(
            [
                # --- 顯示跑馬燈 ---
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ASSISTANT, color=ft.Colors.WHITE70, size=14),
                            ft.Text(selected_message, size=12, color=ft.Colors.WHITE)
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    height=36,
                    bgcolor=ft.Colors.BLACK54,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                ),

                # --- user home page 的圖片 ---
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                    content=ft.Image(
                        src=USER_DASHBOARD_IMAGE,
                        height=250,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(10),
                    ),
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=20,
    )