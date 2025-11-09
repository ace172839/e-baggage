import flet as ft
import datetime
from typing import TYPE_CHECKING
import logging

from config import PREVIOUS_BOOKING_LIST, WINDOW_WIDTH
from constants import *
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def build_previous_booking_view(app_instance: 'App') -> ft.View:
    """
    建立「事先預約」的主畫面 (View)
    """
    logger.info("正在建立「事先預約」畫面 (build_previous_booking_view)")

    # --- ↓↓↓ 1. 日期選擇器邏輯修改 ↓↓↓ ---
    
    def on_arrival_date_change(e):
        """當抵達日期選定後"""
        selected_date = arrival_date_picker.value.strftime("%Y/%m/%d")
        logger.info(f"選擇了抵達日期: {selected_date}")
        
        # 更新 TextField 的值
        if app_instance.prev_arrival_date_ref.current:
            app_instance.prev_arrival_date_ref.current.value = selected_date
            
        # 更新儲存在 App 實例中的狀態變數 (用於頁面重建時恢復)
        app_instance.prev_arrival_date_val = selected_date
        
        # (原 booking_data 邏輯可以保留或移除，但為了統一，我們使用 state_val)
        app_instance.booking_data["arrival_date"] = selected_date 
        app_instance.page.close(arrival_date_picker)
        app_instance.page.update()

    def on_return_date_change(e):
        """當回程日期選定後"""
        selected_date = return_date_picker.value.strftime("%Y/%m/%d")
        logger.info(f"選擇了回程日期: {selected_date}")

        # 更新 TextField 的值
        if app_instance.prev_return_date_ref.current:
            app_instance.prev_return_date_ref.current.value = selected_date
            
        # 更新儲存在 App 實例中的狀態變數
        app_instance.prev_return_date_val = selected_date
        
        app_instance.booking_data["return_date"] = selected_date
        app_instance.page.close(return_date_picker)
        app_instance.page.update()
        
    def on_dismissal(e):
        logger.info(f"日期選擇器已關閉")

    # 建立日期選擇器物件 (它們會被加入到 page.overlay)
    arrival_date_picker = ft.DatePicker(
        on_change=on_arrival_date_change,
        on_dismiss=on_dismissal,
        first_date=datetime.datetime.now(),
        help_text="請選擇您的抵達日期"
    )
    
    return_date_picker = ft.DatePicker(
        on_change=on_return_date_change,
        on_dismiss=on_dismissal,
        first_date=datetime.datetime.now(),
        help_text="請選擇您的回程日期"
    )

    # 首次建立 View 時，將 date pickers 加入到 page overlay
    # (Flet 會處理重複加入的問題)
    if arrival_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(arrival_date_picker)
    if return_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(return_date_picker)
        
    # --- ↑↑↑ 日期選擇器邏輯結束 ↑↑↑ ---


    # --- 2. 主要表單內容 ---
    form_content = ft.Container(
        width=WINDOW_WIDTH,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("事先預約", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.Text("請填寫您的航班與行李資訊", color=COLOR_TEXT_DARK),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                # --- ↓↓↓ 修改點：日期按鈕 -> TextField ↓↓↓ ---
                ft.TextField(
                    ref=app_instance.prev_arrival_date_ref,
                    label="抵達日期:",
                    prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    # 點擊時打開日期選擇器
                    on_focus=lambda _: app_instance.page.open(arrival_date_picker),
                    # 從 App 狀態變數恢復值
                    value=app_instance.prev_arrival_date_val,
                    read_only=True # (重要) 避免鍵盤彈出
                ),
                
                ft.TextField(
                    ref=app_instance.prev_return_date_ref,
                    label="回程日期:",
                    prefix_icon=ft.Icons.CALENDAR_MONTH,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    # 點擊時打開日期選擇器
                    on_focus=lambda _: app_instance.page.open(return_date_picker),
                    # 從 App 狀態變數恢復值
                    value=app_instance.prev_return_date_val,
                    read_only=True
                ),
                # --- ↑↑↑ 修改結束 ↑↑↑ ---
                
                # ft.TextField(
                #     label="航班編號:",
                #     prefix_icon=ft.Icons.FLIGHT,
                #     border_radius=8,
                #     bgcolor=ft.Colors.WHITE,
                #     color=COLOR_TEXT_DARK,
                #     value=app_instance.booking_data.get("flight_number", "")
                # ),

                # --- ↓↓↓ 修改點：地點 Dropdown -> TextField ↓↓↓ ---
                ft.TextField(
                    ref=app_instance.prev_pickup_location_ref,
                    label="抵達地點:",
                    prefix_icon=ft.Icons.MY_LOCATION,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    # 點擊時呼叫 main.py 中的新 handler
                    on_focus=app_instance.handle_select_location_prev_pickup,
                    # 從 App 狀態變數恢復值
                    value=app_instance.prev_pickup_location_val,
                    read_only=True
                ),
                
                ft.TextField(
                    ref=app_instance.prev_dropoff_location_ref,
                    label="返程地點:",
                    prefix_icon=ft.Icons.FLAG,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    # 點擊時呼叫 main.py 中的新 handler
                    on_focus=app_instance.handle_select_location_prev_dropoff,
                    # 從 App 狀態變數恢復值
                    value=app_instance.prev_dropoff_location_val,
                    read_only=True
                ),
                # --- ↑↑↑ 修改結束 ↑↑↑ ---

                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.ElevatedButton(
                    text="確認預約",
                    icon=ft.Icons.CHECK_CIRCLE,
                    height=50,
                    bgcolor=ft.Colors.GREEN_100,
                    color=ft.Colors.GREEN_800,
                    # (確認按鈕的邏輯暫時不變)
                    on_click=app_instance.handle_previous_booking_start
                )
            ],
            spacing=10,
        )
    )

    # --- 3. 組合 View ---
    return ft.View(
        route="/app/user/booking_previous",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            ft.Container(
                content=form_content,
                # (使用您在 constants.py 中定義的背景色)
                bgcolor=COLOR_BG_LIGHT_TAN, 
                expand=True,
                alignment=ft.alignment.top_center
            ),
            build_bottom_nav_bar(app_instance, selected_index=3)
        ]
    )


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
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            ft.AppBar(
                title=ft.Text("預約確認", color=ft.Colors.BLACK), 
                bgcolor=COLOR_BRAND_YELLOW, 
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK, 
                    on_click=lambda _: app_instance.page.go("/app/user/booking_previous"), 
                    icon_color=ft.Colors.WHITE
                )
            ),
            page_content,
            build_bottom_nav_bar(app_instance, selected_index=3)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )