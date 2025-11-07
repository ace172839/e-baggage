import flet as ft
from typing import TYPE_CHECKING

from config import WINDOW_WIDTH
from config import USER_DASHBOARD_MORE_ITEMS as more_items
from constants import *


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
                title=ft.Text(item["label"], size=24),
                leading=ft.Icon(item["icon"]),
                on_click=lambda e, route=item["route"]: app_instance.page.go(route),
                trailing=ft.Icon(ft.Icons.NAVIGATE_NEXT),
            )
        )
        controls_list.append(ft.Divider(height=1, visible=False))

    return ft.Column(
        controls=controls_list,
        scroll=ft.ScrollMode.AUTO,
    )