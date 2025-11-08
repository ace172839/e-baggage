import flet as ft
from constants import *

def build_splash_to_hotel_view(app_instance: 'App') -> ft.View:
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
        route="/splash/hotel",
        controls=[
            ft.Container(
                expand=True,
                padding=10,
                content=ft.Image(
                    src="images/splash.png",
                    fit=ft.ImageFit.CONTAIN,
                ),
                on_click=lambda _: app_instance.page.go("/app/hotel")
            )
        ],
        bgcolor=COLOR_BG_DARK_GOLD,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )