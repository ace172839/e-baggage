# views/user_booking_roundtrip_content.py
import flet as ft
from constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App

def build_previous_booking_view(app_instance: 'App') -> ft.Container:
    """
    建立「事先預約 - 啟程返程」的 UI (精靈第 1 步)
    """

    def handle_next_step(e):
        # (下一步：邏輯)
        # 1. 在這裡驗證所有 TextField
        # 2. 將日期/時間/地點儲存到 page.session
        # 3. 呼叫一個函式，重新渲染這個 View，顯示「住宿」步驟
        print("點擊了「下一步」，準備進入「住宿」")
        app_instance.page.add(
            ft.SnackBar(ft.Text("下一步：住宿選擇 (未實作)"), open=True)
        )
        app_instance.page.update()

    def build_booking_row(title: str, date_val: str, time_val: str, location_val: str):
        """輔助函式：建立一個「預約」區塊"""
        return ft.Column(
            [
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.TextField(label="日期", value=date_val, read_only=True, prefix_icon=ft.Icons.CALENDAR_MONTH, expand=1),
                    ft.TextField(label="時間", value=time_val, read_only=True, prefix_icon=ft.Icons.ACCESS_TIME, width=120),
                ]),
                ft.TextField(label="地點", value=location_val, read_only=True, prefix_icon=ft.Icons.LOCATION_ON),
            ],
            spacing=10
        )

    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        padding=20,
        content=ft.Column(
            [
                # 1. 標題
                ft.Text("事先預約", size=32, weight=ft.FontWeight.BOLD),
                
                ft.Divider(height=10),

                # 2. 抵達
                build_booking_row(
                    "抵達",
                    "2026/01/01",
                    "12:04",
                    "桃園機場"
                ),
                
                ft.Divider(height=20),
                
                # 3. 返程
                build_booking_row(
                    "返程",
                    "2026/01/10",
                    "19:22",
                    "（請點擊地圖）"
                ),

                # (我們之後會在這裡放一個小地圖元件，用來點選「送達地點」)
                
                # 4. 底部按鈕 (使用 expander 來推到底部)
                ft.Container(expand=True), # 佔位符
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "返回",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: app_instance.handle_nav_bar_change(e=ft.ControlEvent(target=None, name="change", data="0")), # 模擬點擊 "更多"
                            height=50,
                            bgcolor=ft.Colors.RED_200,
                            color=ft.Colors.BLACK,
                            expand=True
                        ),
                        ft.ElevatedButton(
                            "下一步",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=handle_next_step,
                            height=50,
                            bgcolor=ft.Colors.GREEN_200,
                            color=ft.Colors.BLACK,
                            expand=True
                        ),
                    ]
                )
            ]
        )
    )