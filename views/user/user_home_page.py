import flet as ft
from constants import *
from typing import TYPE_CHECKING
 
from views.user.user_home_page_content import build_dashboard_content
from views.user.user_booking_instant import build_instant_booking_content
from views.user.user_booking_previous import build_roundtrip_content
from views.user.user_supporting import build_support_content

if TYPE_CHECKING:
    from main import App

def build_user_app_view(app_instance: 'App') -> ft.View:
    """
    建立「旅客 App」的主殼 (Shell)
    這是一個「愚笨」的 UI 建立器
    """
    
    # --- 決定 App 啟動時的預設畫面 ---
    # 我們預設載入「即時預約」 (index 1)
    # (這對 Demo 您的新 UI 流程最有幫助)
    DEFAULT_CONTENT = build_instant_booking_content(app_instance)
    DEFAULT_INDEX = 1

    return ft.View(
        route="/app/user",
        padding=0,
        bgcolor=COLOR_BG_LIGHT_TAN, # App 的淺色背景

        # 頂部 AppBar (Logo)
        appbar=ft.AppBar(
            title=ft.Row([
                ft.Icon(ft.Icons.LUGGAGE_OUTLINED, size=30),
                ft.Text("e-baggage", size=24, weight=ft.FontWeight.BOLD)
            ]),
            center_title=True,
            bgcolor=COLOR_BRAND_YELLOW,
        ),

        # 底部導航列 (Bottom Nav Bar)
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MENU, label="更多"),
                ft.NavigationBarDestination(icon=ft.Icons.LOCATION_ON, label="即時預約"),
                ft.NavigationBarDestination(icon=ft.Icons.COMPARE_ARROWS, label="來回預約"),
                ft.NavigationBarDestination(icon=ft.Icons.CALL, label="客服"),
            ],
            selected_index=DEFAULT_INDEX,
            
            # 將 on_change 綁定到 App 類別的「控制器」方法
            on_change=app_instance.handle_nav_bar_change,
            
            bgcolor=ft.Colors.WHITE,
        ),

        # 主內容區域
        controls=[
            ft.Container(
                # 將 Ref 綁定到 App 類別的屬性
                ref=app_instance.main_content_ref,
                expand=True,
                bgcolor=ft.Colors.WHITE,
                content=DEFAULT_CONTENT
            )
        ]
    )