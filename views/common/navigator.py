import flet as ft
from typing import TYPE_CHECKING
from constants import *

if TYPE_CHECKING:
    from main import App

def build_bottom_nav_bar(app_instance: 'App', selected_index: int) -> ft.NavigationBar:
    """
    建立一個共享的底部導航列 (Bottom Navigation Bar)
    
    :param app_instance: App 實例
    :param selected_index: 目前應被選中的
    """
    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=app_instance.handle_nav_bar_change,
        bgcolor=COLOR_BACKGROUD_YELLOW,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.MORE_HORIZ,
                label="更多",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE,
                label="即時預約",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME, 
                label="首頁"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_MONTH,
                label="事先預約"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SUPPORT_AGENT,
                label="客服"
            )
        ]
    )