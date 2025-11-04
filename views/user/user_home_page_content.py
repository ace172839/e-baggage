import flet as ft
from config import USER_DASHBOARD_IMAGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

def build_dashboard_content(app_instance: 'App') -> ft.Container:
    """
    建立旅客 App 的「主畫面」內容 (您的截圖 1)
    """
    return ft.Container(
        expand=True,
        content=ft.Column(
            [
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
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=20,
    )