import flet as ft
from constants import *
from config import USER_DASHBOARD_NAVIGATOR_ITEMS
from typing import TYPE_CHECKING
 
# --- [修改] 導入所有 5 個內容頁面 ---
from views.user.user_home_page_content import build_dashboard_content
from views.user.user_booking_instant import build_instant_booking_view
from views.user.user_booking_previous import build_previous_booking_view
from views.user.user_supporting import build_support_content
from views.user.user_home_page_more_content import build_more_content


if TYPE_CHECKING:
    from main import App

def build_user_app_view(app_instance: 'App') -> ft.View:
    """
    建立「旅客 App」的主殼 (Shell)
    """
    DEFAULT_CONTENT = build_dashboard_content(app_instance)
    # 預設選中 "首頁"
    DEFAULT_INDEX = 2

    return ft.View(
        route="/app/user",
        padding=0,
        bgcolor=COLOR_BG_LIGHT_TAN,

        # --- 頂部 App Bar ---
        appbar=ft.AppBar(
            title=ft.Row(
                controls=[
                    ft.Image(
                        src="images/logo.png",
                        width=75,
                        height=75,
                        fit=ft.ImageFit.CONTAIN
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            center_title=True,
            bgcolor=COLOR_BG_DARK_GOLD,
        ),

        # --- 底部導航列 ---
        navigation_bar=ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                        icon=ft.Icon(item["icon"]),
                        label=item["label"],
                    ) for item in USER_DASHBOARD_NAVIGATOR_ITEMS
            ],
            selected_index=DEFAULT_INDEX, # 預設選中「首頁」
            
            # 將 on_change 綁定到 App 類別的「控制器」方法
            on_change=app_instance.handle_nav_bar_change,
            bgcolor=COLOR_BACKGROUD_YELLOW,
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