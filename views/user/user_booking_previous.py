import flet as ft
import datetime
from typing import TYPE_CHECKING
import logging

from config import PREVIOUS_BOOKING_LIST
from constants import *
from views.common_components import build_bottom_nav_bar

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_previous_booking_view(app_instance: 'App') -> ft.Control:
    """
    建立「事先預約」的內容
    包含日期選擇器功能
    """
    logger.info("正在建立「事先預約」內容 (build_previous_booking_view)")

    arrival_date = "2026/01/01"
    return_date = "2026/01/10"
    arrival_location = "桃園機場"
    return_location = "嘉義火車站"

    def show_confirm_view(e):
        logger.info("切換到「事先預約」確認畫面")
        # 在切換前，確保 UI 上的任何手動輸入（如果有的話）被儲存
        # (目前都是 read_only，所以這一步是安全的)
        app_instance.page.go("/app/user/booking_previous_confirm")

    view = ft.View(
        route="/app/user/booking_previous",
        padding=0,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("事先預約", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                        ft.Text("請點擊下方欄位來選擇日期與地點。", color=COLOR_TEXT_DARK),
                        
                        ft.TextField(
                            label="抵達日期",
                            prefix_icon=ft.Icons.CALENDAR_TODAY,
                            read_only=True,
                            color=COLOR_TEXT_DARK,
                            value=arrival_date,
                        ),
                        ft.TextField(
                            label="抵達地點 (例如：桃園機場)",
                            prefix_icon=ft.Icons.FLIGHT_LAND,
                            color=COLOR_TEXT_DARK,
                            read_only=True,
                            value=arrival_location,
                        ),
                        
                        ft.TextField(
                            label="返程日期",
                            prefix_icon=ft.Icons.CALENDAR_TODAY,
                            read_only=True,
                            color=COLOR_TEXT_DARK,
                            value=return_date,
                        ),
                        ft.TextField(
                            label="返程地點 (例如：板橋車站)",
                            prefix_icon=ft.Icons.FLIGHT_TAKEOFF,
                            color=COLOR_TEXT_DARK,
                            read_only=True,
                            value=return_location,
                        ),
                        
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        ft.ElevatedButton(
                            text="下一步：確認預約",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            height=50,
                            width=300,
                            bgcolor=COLOR_BRAND_YELLOW,
                            color=COLOR_TEXT_DARK,
                            on_click=show_confirm_view,
                        )
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
                padding=20,
                expand=True,
                bgcolor=COLOR_BG_LIGHT_TAN
            ),
            build_bottom_nav_bar(app_instance, selected_index=3)
        ]
    )
    return view


def build_previous_booking_confirm_view(app_instance: 'App') -> ft.Control:
    """
    建立「事先預約」的確認訂單頁面
    """
    logger.info("正在建立「事先預約」的確認訂單頁面 (build_previous_booking_confirm_view)")

    order_list_rows = []
    for booking in PREVIOUS_BOOKING_LIST:
        second_field_text = booking["time"] if booking["time"] else "入住"
        order_list_rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(booking["start_date"])),
                ft.DataCell(ft.Text(second_field_text)),
                ft.DataCell(ft.Text(booking["location"]))
            ]
        ))
    
    uncontracted_list_rows = []
    for booking in PREVIOUS_BOOKING_LIST:
        if not booking["contracted"]:
            uncontracted_list_rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(booking["start_date"], color=ft.Colors.RED_700)),
                    ft.DataCell(ft.Text(booking["location"], color=ft.Colors.RED_700))
                ]
            ))
    
    def handle_submit(e):
        logger.info("「送出預約」按鈕被點擊，準備重設內容到儀表板")
        app_instance.page.go("/app/user/dashboard")


    page_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("預約確認", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                ft.Text("請確認以下預約資訊：", color=COLOR_TEXT_DARK),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("")),
                    ],
                    rows=order_list_rows
                ),
                ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                ft.Text(
                    "*以下住宿非特約旅館，請旅客自行與旅館溝通行李接待事項*",
                    color=ft.Colors.RED_700, # 增加紅色提示
                    size=12
                ),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("")),
                        ft.DataColumn(ft.Text("")),
                    ],
                    rows=uncontracted_list_rows
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton(
                    text="送出預約",
                    icon=ft.Icons.SEND,
                    height=50,
                    width=200,
                    bgcolor=COLOR_BRAND_YELLOW,
                    color=COLOR_TEXT_DARK,
                    on_click=handle_submit
                )            
            ],
            spacing=15,
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        padding=20,
        expand=True
    )

    return ft.View(
        route="/app/user/booking_previous_confirm",
        padding=0,
        controls=[
            page_content,
            build_bottom_nav_bar(app_instance, selected_index=3)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )