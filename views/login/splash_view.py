import flet as ft
from constants import *

def build_splash_view(app_instance: 'App') -> ft.View:
    """
    建立「啟動畫面」的 UI
    我們傳入 'app_instance' (主 App 類別) 來存取 page.go
    """

    # def navigate_to_roles():
    #     """計時器結束後，導航到角色選擇頁"""
    #     app_instance.page.go("/role_select")

    # # 啟動一個 2.5 秒的非阻塞計時器
    # timer = threading.Timer(2, navigate_to_roles)
    # timer.start()

    return ft.View(
        route="/splash",
        controls=[
            ft.Container(
                expand=True,
                padding=30,
                content=ft.Column(
                    [
                        # Logo (暫時替代)
                        ft.Icon(ft.Icons.LUGGAGE_OUTLINED, size=100, color=COLOR_BRAND_YELLOW),
                        ft.Text("e-baggage", size=40, color=COLOR_BRAND_YELLOW, font_family="Noto Sans TC"),
                        
                        ft.Divider(height=50, color=ft.Colors.TRANSPARENT),

                        # Slogan
                        ft.Text("# 托 你 的 福", width=330, size=20, color=ft.Colors.WHITE, font_family="Noto Serif TC", text_align=ft.TextAlign.LEFT),
                        ft.Text("讓 我 擁 有 無 負 擔 的 旅 途.", width=330, size=20, color=ft.Colors.WHITE, font_family="Noto Serif TC"),
                        ft.Text("#E-BAGGAGE.NO BURDEN JOURNEY.", width=330, size=12, color=ft.Colors.WHITE54),

                        # For design and testing purpose
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        ft.Container(
                            width=100,
                            height=60,
                            bgcolor=COLOR_BRAND_YELLOW,
                            alignment=ft.alignment.center,
                            on_click=lambda _: app_instance.page.go("/role_select"),
                            content=ft.Text("下一頁", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            )
        ],
        bgcolor=COLOR_BG_DARK_GOLD,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )