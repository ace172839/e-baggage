import flet as ft
import random
from typing import TYPE_CHECKING
from config import USER_DASHBOARD_IMAGE, USER_DASHBOARD_MARQUEE_MESSAGES
from constants import *
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab

if TYPE_CHECKING:
    from main import App

def build_dashboard_content(app_instance: 'App') -> ft.Column:
    # 隨機跑馬燈文字
    selected_message = random.choice(USER_DASHBOARD_MARQUEE_MESSAGES)

    return ft.Column(
        controls=[
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
    )

def build_dashboard_view(app_instance: 'App') -> ft.View:
    """
    建立「首頁儀表板」的完整 View
    """
    return ft.View(
        route="/app/user/dashboard",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            # 內容區域
            ft.Container(
                content=build_dashboard_content(app_instance),
                padding=20,
                expand=True,
            ),
            
            # 底部導航列
            build_bottom_nav_bar(app_instance, selected_index=2)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )