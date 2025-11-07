import flet as ft
import datetime
from typing import TYPE_CHECKING
from config import PREVIOUS_BOOKING_LIST
from constants import * # 用於按鈕樣式
from views.user.user_home_page_content import build_dashboard_content # ADDED
import logging
import json
import datetime
import random
from urllib.parse import quote_plus, parse_qs

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

DEMO_DB_PATH = "demo_db.json"

# Helper function to save order to demo_db.json
def save_order_to_db(order_data: dict):
    try:
        with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db_data = {"users": {}, "orders": [], "scans": [], "partner_hotels": []}

    orders = db_data.get('orders', [])
    orders.append(order_data)

    # Sort orders by date in descending order
    orders.sort(key=lambda order: datetime.datetime.strptime(order['date'], '%Y/%m/%d'), reverse=True)
    db_data['orders'] = orders

    with open(DEMO_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)
    logger.info(f"Order {order_data['id']} saved to {DEMO_DB_PATH}")

def build_previous_booking_view(app_instance: 'App') -> ft.Control:
    """
    建立「事先預約」的內容
    包含日期選擇器功能
    """
    logger.info("正在建立「事先預約」內容 (build_previous_booking_view)")

    # --- 1. Refs ---
    # 需要 Refs 來在選擇日期後更新 TextField 的值
    arrival_date_ref = ft.Ref[ft.TextField]()
    return_date_ref = ft.Ref[ft.TextField]()
    pickup_location_ref = ft.Ref[ft.TextField]()
    dropoff_location_ref = ft.Ref[ft.TextField]()

    # --- 2. DatePicker 事件處理 ---
    
    def on_arrival_date_selected(e):
        """當「抵達日期」被選中時呼叫"""
        selected_date = e.control.value.strftime("%Y-%m-%d") # 將日期格式化為字串
        logger.info(f"抵達日期已選擇: {selected_date}")
        if arrival_date_ref.current:
            arrival_date_ref.current.value = selected_date
            arrival_date_ref.current.update()
        arrival_date_picker.open = False
        app_instance.page.update()

    def on_return_date_selected(e):
        """當「返程日期」被選中時呼叫"""
        selected_date = e.control.value.strftime("%Y-%m-%d")
        logger.info(f"返程日期已選擇: {selected_date}")
        if return_date_ref.current:
            return_date_ref.current.value = selected_date
            return_date_ref.current.update()
        return_date_picker.open = False
        app_instance.page.update()


    # --- 3. 建立 DatePicker 控制項 ---
    # 這些是隱藏的控制項，會以彈窗形式出現
    
    arrival_date_picker = ft.DatePicker(
        on_change=on_arrival_date_selected,
        first_date=datetime.datetime.now(), # 只能選今天之後的日期
        help_text="請選擇您的抵達日期",
    )
    
    return_date_picker = ft.DatePicker(
        on_change=on_return_date_selected,
        first_date=datetime.datetime.now(),
        help_text="請選擇您的返程日期"
    )

    # --- 4. 將 DatePicker 加入 Page Overlay (關鍵步驟) ---
    # 檢查是否已存在，避免重複加入
    if arrival_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(arrival_date_picker)
    if return_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(return_date_picker)

    # --- 5. 觸發 DatePicker 的函式 ---
    
    def open_arrival_picker(e):
        """點擊「抵達」輸入框時，開啟日曆"""
        logger.debug("開啟抵達日期選擇器")
        arrival_date_picker.open = True
        app_instance.page.update()

    def open_return_picker(e):
        """點擊「返程」輸入框時，開啟日曆"""
        logger.debug("開啟返程日期選擇器")
        # 讓返程日期的起始日 = 抵達日期 (如果已選的話)
        if arrival_date_picker.value:
            return_date_picker.first_date = arrival_date_picker.value
        return_date_picker.open = True
        app_instance.page.update()

    def show_confirm_view(e):
        logger.info("切換到「事先預約」確認畫面")

        # Collect form data
        arrival_date = arrival_date_ref.current.value if arrival_date_ref.current else ""
        return_date = return_date_ref.current.value if return_date_ref.current else ""
        pickup_location = pickup_location_ref.current.value if pickup_location_ref.current else ""
        dropoff_location = dropoff_location_ref.current.value if dropoff_location_ref.current else ""

        # Construct URL with query parameters
        query_params = f"arrival_date={quote_plus(arrival_date)}&return_date={quote_plus(return_date)}&pickup_location={quote_plus(pickup_location)}&dropoff_location={quote_plus(dropoff_location)}"
        app_instance.page.go(f"/app/user/booking_previous_confirm?{query_params}")

    # --- 6. 建立頁面佈局 ---
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("事先預約", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.Text("此為「事先預約」功能頁面，您可以點擊下方欄位來選擇日期。", color=COLOR_TEXT_DARK),
                
                ft.TextField(
                    ref=arrival_date_ref,
                    label="抵達日期",
                    prefix_icon=ft.Icons.CALENDAR_TODAY,
                    read_only=True,
                    on_focus=open_arrival_picker,
                    # color=COLOR_TEXT_DARK
                ),
                ft.TextField(
                    ref=pickup_location_ref,
                    label="抵達地點 (例如：桃園機場)",
                    prefix_icon=ft.Icons.FLIGHT_LAND,
                    color=COLOR_TEXT_DARK
                ),
                
                ft.TextField(
                    ref=return_date_ref,
                    label="返程日期",
                    prefix_icon=ft.Icons.CALENDAR_TODAY,
                    read_only=True,
                    on_focus=open_return_picker,
                    # color=COLOR_TEXT_DARK
                ),
                ft.TextField(
                    ref=dropoff_location_ref,
                    label="返程地點 (例如：板橋車站)",
                    prefix_icon=ft.Icons.FLIGHT_TAKEOFF,
                    color=COLOR_TEXT_DARK
                ),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton(
                    text="確認",
                    icon=ft.Icons.CHECK_CIRCLE,
                    height=50,
                    width=200,
                    bgcolor=COLOR_BRAND_YELLOW,
                    color=COLOR_TEXT_DARK,
                    on_click=show_confirm_view,
                )
            ],
            spacing=15,
            scroll=ft.ScrollMode.ADAPTIVE
        ),
        padding=20,
        expand=True
    )

def build_previous_booking_confirm_view(app_instance: 'App') -> ft.Control:
    """
    建立「事先預約」的確認訂單頁面
    """
    logger.info("正在建立「事先預約」的確認訂單頁面 (build_previous_booking_confirm_view)")

    # Extract query parameters from the route
    query_string = app_instance.page.route.split('?')
    if len(query_string) > 1:
        query_params = parse_qs(query_string[1])
        arrival_date = query_params.get('arrival_date', [''])[0]
        return_date = query_params.get('return_date', [''])[0]
        pickup_location = query_params.get('pickup_location', [''])[0]
        dropoff_location = query_params.get('dropoff_location', [''])[0]
    else:
        arrival_date = "未知"
        return_date = "未知"
        pickup_location = "未知"
        dropoff_location = "未知"

    order_list_rows = []
    # For previous booking, we don't have a PREVIOUS_BOOKING_LIST to display here
    # Instead, we display the current booking details
    order_list_rows.append(ft.DataRow(
        cells=[
            ft.DataCell(ft.Text("抵達日期:")),
            ft.DataCell(ft.Text(arrival_date)),
            ft.DataCell(ft.Text("")),
        ]
    ))
    order_list_rows.append(ft.DataRow(
        cells=[
            ft.DataCell(ft.Text("抵達地點:")),
            ft.DataCell(ft.Text(pickup_location)),
            ft.DataCell(ft.Text("")),
        ]
    ))
    order_list_rows.append(ft.DataRow(
        cells=[
            ft.DataCell(ft.Text("返程日期:")),
            ft.DataCell(ft.Text(return_date)),
            ft.DataCell(ft.Text("")),
        ]
    ))
    order_list_rows.append(ft.DataRow(
        cells=[
            ft.DataCell(ft.Text("返程地點:")),
            ft.DataCell(ft.Text(dropoff_location)),
            ft.DataCell(ft.Text("")),
        ]
    ))

    # The uncontracted_list_rows logic seems to be for displaying existing bookings, not the current one.
    # I will keep it as is for now, but it might need review if it's not relevant to the current booking confirmation.
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

        # Use extracted values
        luggages = "1" # Still placeholder, needs to be dynamic if possible
        amount = "300" # Still placeholder, needs to be dynamic if possible

        # Generate a new order ID
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            existing_orders = db_data.get('orders', [])
            max_id = 0
            for order in existing_orders:
                if order['id'].startswith('O'):
                    try:
                        num = int(order['id'][1:])
                        if num > max_id:
                            max_id = num
                    except ValueError:
                        pass
            new_order_id = f"O{max_id + 1:03d}"
        except (FileNotFoundError, json.JSONDecodeError):
            new_order_id = "O001"

        new_order = {
            "id": new_order_id,
            "date": arrival_date, # Use arrival_date as the order date
            "pickup": pickup_location,
            "dropof": dropoff_location,
            "amount": amount,
            "luggages": luggages
        }

        save_order_to_db(new_order)

        app_instance.page.go("/app/user")

    return ft.Container(
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