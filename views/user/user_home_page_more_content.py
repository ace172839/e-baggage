import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

def build_more_content(app_instance: 'App') -> ft.Column:
    """
    建立「更多」頁面的內容
    """

    more_items = [
        {"icon": ft.Icons.PERSON_OUTLINE, "label": "帳號設定", "route": "/app/user/profile"},
        {"icon": ft.Icons.FAVORITE_BORDER, "label": "我的最愛", "route": "/app/user/favorites"},
        {"icon": ft.Icons.SHOPPING_CART_OUTLINED, "label": "購物車", "route": "/app/user/cart"},
        {"icon": ft.Icons.HISTORY, "label": "交易紀錄", "route": "/app/user/history"},
        {"icon": ft.Icons.CALL, "label": "客服聯繫", "route": "/app/user/support"},
        {"icon": ft.Icons.SETTINGS_OUTLINED, "label": "系統設定", "route": "/app/user/settings"},
        {"icon": ft.Icons.LOGOUT, "label": "登出", "route": "/logout"},
    ]

    def handle_item_click(e, route: str):
        if route == "/logout":
            print("處理登出...")
            app_instance.page.session.clear() # 清空 session
            app_instance.page.go("/role_select") # 導回角色選擇
        else:
            print(f"導航到: {route}")
            # 暫時只 print，之後我們可以實現真的頁面跳轉
            pass

    controls_list = []
    for item in more_items:
        controls_list.append(
            ft.ListTile(
                title=ft.Text(item["label"], size=18),
                leading=ft.Icon(item["icon"]),
                on_click=lambda e, r=item["route"]: handle_item_click(e, r),
                trailing=ft.Icon(ft.Icons.NAVIGATE_NEXT),
            )
        )
        controls_list.append(ft.Divider(height=1))

    return ft.Column(
        controls=controls_list,
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )