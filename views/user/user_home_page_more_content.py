import flet as ft
from typing import TYPE_CHECKING

from config import WINDOW_WIDTH
from config import USER_DASHBOARD_MORE_ITEMS as more_items

if TYPE_CHECKING:
    from main import App

def build_more_content(app_instance: 'App') -> ft.Column:
    """
    建立「更多」頁面的內容
    """
    controls_list = []
    for item in more_items:
        controls_list.append(
            ft.ListTile(
                title=ft.Text(item["label"], size=18),
                leading=ft.Icon(item["icon"]),
                on_click=lambda e: app_instance.page.go(item["route"]),
                trailing=ft.Icon(ft.Icons.NAVIGATE_NEXT),
            )
        )
        controls_list.append(ft.Divider(height=1))

    return ft.Column(
        controls=controls_list,
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )