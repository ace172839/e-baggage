#
# 檔案: views/user/user_supporting.py
# (修改)
#
import flet as ft
from typing import TYPE_CHECKING
from config import *
from constants import *
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab

if TYPE_CHECKING:
    from main import App

# 【修改】重新命名並使其返回 ft.View
def build_support_view(app_instance: 'App') -> ft.View:
    """
    建立「客服」頁面的完整 View
    """
    # ... (您原有的 build_support_content 邏輯) ...
    content_column = ft.Column(
        controls=[
            ft.Text("客服支援", size=30, color=COLOR_TEXT_DARK),
            ft.Text("這裡是客服頁面...", color=COLOR_TEXT_DARK)
        ],
        scroll=ft.ScrollMode.AUTO,
    )
    
    return ft.View(
        route="/app/user/support",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            # 內容區域
            ft.Container(
                content=content_column,
                padding=20,
                expand=True
            ),
            
            # 底部導航列
            build_bottom_nav_bar(app_instance, selected_index=4)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )