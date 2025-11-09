#
# 檔案: views/user/user_home_page_more_content.py
# (修改)
#
import flet as ft
from typing import TYPE_CHECKING
from config import *
from constants import *
from views.common.navigator import build_bottom_nav_bar # 【新增】 匯入

if TYPE_CHECKING:
    from main import App

# 【修改】重新命名並使其返回 ft.View
def build_more_view(app_instance: 'App') -> ft.View:
    """
    建立「更多」頁面的完整 View
    """
    controls_list = []
    for item in USER_DASHBOARD_MORE_ITEMS:
        controls_list.append(
            ft.ListTile(
                title=ft.Text(item["label"], size=24, color=COLOR_TEXT_DARK),
                leading=ft.Icon(item["icon"], color=COLOR_TEXT_DARK),
                on_click=lambda e, route=item["route"]: app_instance.page.go(route),
                trailing=ft.Icon(ft.Icons.NAVIGATE_NEXT, color=COLOR_TEXT_DARK),
            )
        )
        controls_list.append(ft.Divider(height=1))

    return ft.View(
        route="/app/user/more",
        padding=0,
        controls=[
            # 內容區域
            ft.Column(
                controls=controls_list,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0
            ),
            
            # 底部導航列
            build_bottom_nav_bar(app_instance, selected_index=0)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )