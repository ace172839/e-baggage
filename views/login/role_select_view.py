import flet as ft
from constants import *

def build_role_select_view(app_instance: 'App') -> ft.View:
    """
    建立「角色選擇畫面」的 UI
    """

    def create_role_button(text: str, icon_name: str, route_target: str):
        """一個輔助函式，用來建立漂亮的角色按鈕"""
        return ft.Container(
            width=300,
            height=120,
            bgcolor=COLOR_BRAND_YELLOW,
            border_radius=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
            on_click=lambda _: app_instance.page.go(route_target),
            padding=20,
            content=ft.Row(
                [
                    ft.Text(text, size=48, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK, expand=1),
                    # 暫時用 Icon 替代您的美術圖
                    ft.Icon(icon_name, size=60, color=ft.Colors.BLACK38)
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    return ft.View(
        route="/role_select",
        controls=[
            # 頂部 Logo
            ft.Container(
                padding=20,
                height=100,
                bgcolor=COLOR_BRAND_YELLOW,
                border_radius=ft.BorderRadius(0, 0, 15, 15),
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LUGGAGE_OUTLINED, size=40),
                        ft.Text("e-baggage", size=30, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ),

            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),

            # 按鈕區塊 (使用 Container 包裹 Column 來確保置中)
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        create_role_button("顧客端", ft.Icons.PERSON_ROUNDED, "/login/user"),
                        create_role_button("司機端", ft.Icons.SUPPORT_AGENT_ROUNDED, "/login/driver"),
                        create_role_button("旅店端", ft.Icons.HOTEL_ROUNDED, "/login/hotel"),
                    ],
                    spacing=25,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ],
        bgcolor=COLOR_BG_LIGHT_TAN,
        padding=0,
    )