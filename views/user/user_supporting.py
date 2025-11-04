import flet as ft
from constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

def build_support_content(app_instance: 'App') -> ft.Column:
    """
    建立「客服」頁面的佔位符
    """
    return ft.Column(
        [
            ft.Text("這裡是「客服聯繫」的內容", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("（下一步：實作聯絡表單）"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )