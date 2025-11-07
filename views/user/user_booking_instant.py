import flet as ft
import flet_map as map
from views.user.user_home_page_content import build_dashboard_content
from config import *
from constants import *
from config import MAP_ROUTING_RESULT
from typing import TYPE_CHECKING
import logging
import json
from datetime import datetime
import random

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

DEMO_DB_PATH = "demo_db.json"

def load_partner_hotels_from_db():
    try:
        with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
            db_date = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    hotels = db_date.get('partner_hotels', [])
    return hotels

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
    orders.sort(key=lambda order: datetime.strptime(order['date'], '%Y/%m/%d'), reverse=True)
    db_data['orders'] = orders

    with open(DEMO_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)
    logger.info(f"Order {order_data['id']} saved to {DEMO_DB_PATH}")

def calculate_zoom_level(lat1, lon1, lat2, lon2):
    # These values are highly empirical and might need adjustment based on actual map behavior
    # A common approach is to find the max span and then use a lookup table or a logarithmic scale.
    
    max_lat_diff = abs(lat1 - lat2)
    max_lon_diff = abs(lon1 - lon2)
    
    max_diff = max(max_lat_diff, max_lon_diff)

    if max_diff < 0.001: # Very close points, zoom in
        return 17
    elif max_diff < 0.005:
        return 16
    elif max_diff < 0.01:
        return 15
    elif max_diff < 0.05:
        return 14
    elif max_diff < 0.1:
        return 13
    elif max_diff < 0.5:
        return 12
    elif max_diff < 1:
        return 11
    else:
        return 8 # Fallback for very distant points

def build_instant_booking_view(app_instance: 'App') -> ft.View:
    """
    建立「即時預約」的主畫面 (View)
    包含地圖和下方的表單
    """
    logger.info("正在建立「即時預約」主畫面 (build_instant_booking_view)")

    def show_confirm_view(e):
        """
        建立「確認畫面」並將其顯示在主內容區域
        (這才是您缺少的邏輯)
        """
        logger.info("切換到「即時預約」確認畫面")
        app_instance.page.go("/app/user/confirm_order")

    # --- 1. 地圖控制項 ---
    # 地圖控制項被移到 App class (main.py) 的 Ref 中
    # 這樣才能在不同函式中 (例如 handle_select_location) 控制它
    # 我們在這裡初始化地圖
    
    # 檢查 App 實例上是否已經有 map_ref，沒有才建立
    logger.info("初始化地圖控制項")

    hotels_detail = load_partner_hotels_from_db()
    hotel_markers = []
    for hotel in hotels_detail:
        if hotel.get("is_partner", False):
            icon = ft.Icon(ft.Icons.HOTEL, color=ft.Colors.BLUE_600, size=25)
        else:
            icon = ft.Icon(ft.Icons.HOTEL, color=ft.Colors.GREY_400, size=25)
        marker = map.Marker(
            content=icon,
            coordinates=map.MapLatitudeLongitude(hotel["lat"], hotel["lon"]),
        )
        hotel_markers.append(marker)
    all_markers = hotel_markers
    all_markers.append(map.Marker(
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=35),
                        coordinates=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
                    ))

    app_instance.map_ref.current = map.Map(
        expand=True,
        initial_zoom=16,
        initial_center=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
        interaction_configuration=map.MapInteractionConfiguration(
            flags=map.MapInteractiveFlag.ALL
        ),
        layers=[
            map.TileLayer(
                url_template=USER_DASHBOARD_MAP_TEMPLATE,
            ),
            map.MarkerLayer(
                markers=all_markers,
            ),
        ],
    )

    # --- 3. 表單控制項 ---
    form_content = ft.Container(
        width=WINDOW_WIDTH,
        padding=20,
        bgcolor=COLOR_BG_LIGHT_TAN,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26),
        
        content=ft.Column(
            controls=[
                ft.TextField(
                    ref=app_instance.pickup_location_ref,
                    label="上車地點:",
                    prefix_icon=ft.Icons.MY_LOCATION,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    on_focus=app_instance.handle_select_location_pickup,
                    value=app_instance.pickup_location_ref.current.value if app_instance.pickup_location_ref.current else "",
                    color=COLOR_TEXT_DARK
                ),
                ft.TextField(
                    ref=app_instance.dropoff_location_ref,
                    label="下車地點:",
                    prefix_icon=ft.Icons.FLAG,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    on_focus=app_instance.handle_select_location_dropoff,
                    value=app_instance.dropoff_location_ref.current.value if app_instance.dropoff_location_ref.current else "",
                    color=COLOR_TEXT_DARK
                ),
                ft.Row(
                    controls=[
                        ft.TextField(
                            ref=app_instance.notes_ref,
                            label="行李件數:",
                            prefix_icon=ft.Icons.LUGGAGE_OUTLINED,
                            border_radius=8,
                            bgcolor=ft.Colors.WHITE,
                            expand=True,
                            value=str(app_instance.scan_results),
                            color=COLOR_TEXT_DARK
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CAMERA_ALT,
                            icon_size=30,
                            tooltip="掃描行李 (AI)",
                            on_click=app_instance.handle_scan_baggage, # 點擊掃描
                            bgcolor=ft.Colors.WHITE,
                            height=55,
                            width=55,
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.TextField(
                    ref=app_instance.notes_ref,
                    label="備註事項:",
                    prefix_icon=ft.Icons.EDIT_NOTE,
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    expand=True,
                    color=COLOR_TEXT_DARK
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="取消",
                            icon=ft.Icons.CANCEL,
                            height=50,
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_800,
                            on_click=lambda e: app_instance.page.go("/app/user"),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="確認",
                            icon=ft.Icons.CHECK_CIRCLE,
                            height=50,
                            bgcolor=ft.Colors.GREEN_100,
                            color=ft.Colors.GREEN_800,
                            on_click=show_confirm_view,
                            expand=True,
                        )
                    ]
                )
            ],
            spacing=10,
        )
    )

    # --- 4. 組合 View ---
    return ft.View(
        route="/app/user",
        padding=0,
        controls=[
            ft.Column(
                controls=[
                    ft.Container(
                        content=app_instance.map_ref.current,
                        expand=True,
                    ),
                    ft.Container(
                        content=form_content,
                    )
                ],
                expand=True,
                spacing=0 # 確保地圖和表單之間沒有空隙
            )
        ]
    )

def build_instant_booking_confirm_view(app_instance: 'App') -> ft.View:
    logger.info("Building Confirm Order View")
    
    def handle_submit(e):
        logger.info("「送出預約」按鈕被點擊，準備重設內容到儀表板")

        # Extract order details
        pickup = app_instance.pickup_location_ref.current.value if app_instance.pickup_location_ref.current else "未知上車地點"
        dropoff = app_instance.dropoff_location_ref.current.value if app_instance.dropoff_location_ref.current else "未知下車地點"
        # Assuming notes_ref is used for luggages count based on the label in build_instant_booking_view
        luggages = app_instance.notes_ref.current.value if app_instance.notes_ref.current else "0"
        amount = "250" # Hardcoded for now, needs to be dynamic if possible

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
            new_order_id = "O001" # If file doesn't exist or is empty

        new_order = {
            "id": new_order_id,
            "date": datetime.now().strftime("%Y/%m/%d"),
            "pickup": pickup if pickup else "台北101",
            "dropof": dropoff if dropoff else "板橋車站",
            "amount": amount if amount else "250",
            "luggages": luggages if luggages else "5"
        }

        save_order_to_db(new_order)
        app_instance.scan_results = 0
        app_instance.page.go("/app/user")

    pickup_name = "板橋車站"
    pickup_coords = LOCATION_BANQIAO_STATION
    dropoff_name = "台北 101"
    dropoff_coords = LOCATION_TAIPEI_101
    
    calculated_zoom = calculate_zoom_level(
        pickup_coords[0], pickup_coords[1],
        dropoff_coords[0], dropoff_coords[1]
    )

    confirm_map = map.Map(
        expand=True,
        initial_zoom=calculated_zoom,
        initial_center=map.MapLatitudeLongitude(
            (pickup_coords[0] + dropoff_coords[0]) / 2,
            (pickup_coords[1] + dropoff_coords[1]) / 2
        ),
        layers=[
            map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
            map.MarkerLayer(
                markers=[
                    map.Marker(
                        content=ft.Icon(ft.Icons.MY_LOCATION, color=ft.Colors.BLUE, size=30),
                        coordinates=map.MapLatitudeLongitude(*pickup_coords),
                    ),
                    map.Marker(
                        content=ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED, size=30),
                        coordinates=map.MapLatitudeLongitude(*dropoff_coords),
                    ),
                ]
            ),
            map.PolylineLayer(
                polylines=[
                    map.PolylineMarker(
                        coordinates=[map.MapLatitudeLongitude(coord[1], coord[0]) for coord in MAP_ROUTING_RESULT["routes"][0]["geometry"]["coordinates"]],
                        color=ft.Colors.BLACK38,
                        stroke_width=5
                    )
                ]
            )
        ]
    )

    if app_instance.notes_ref.current and app_instance.notes_ref.current.value != "":
        note = ft.Text(f"\n註記： {app_instance.notes_ref.current.value}", color=ft.Colors.RED)
    else:
        note = ft.Text("")


    info_card = ft.Container(
        padding=30,
        bgcolor=COLOR_BG_LIGHT_TAN,
        border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=10, bottom_right=10),
        content=ft.Column(
            controls=[
                ft.Text(f"上車地點：{pickup_name}", color=COLOR_TEXT_DARK),
                ft.Text(f"下車地點：{dropoff_name}", color=COLOR_TEXT_DARK),
                ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                ft.Text("根據您的行李數量及大小，", color=COLOR_TEXT_DARK),
                ft.Text("        推薦車款為: 休旅車", color=COLOR_TEXT_DARK),
                ft.Text("        預計費用為: 250 元", color=COLOR_TEXT_DARK),
                ft.Text("預計行李抵達旅館時間: 50 分鐘", color=COLOR_TEXT_DARK),
                note,
                ft.Divider(height=1, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="取消",
                            icon=ft.Icons.CANCEL,
                            height=50,
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_800,
                            on_click=lambda _: app_instance.page.go("/app/user/booking_instant"),
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            text="確認",
                            icon=ft.Icons.CHECK_CIRCLE,
                            height=50,
                            bgcolor=ft.Colors.GREEN_100,
                            color=ft.Colors.GREEN_800,
                            on_click=handle_submit,
                            expand=True,
                        )
                    ]
                )
            ],
            height=260,
            scroll=ft.ScrollMode.ADAPTIVE,
        )
    )

    return ft.View(
        route="/app/user/confirm_order",
        padding=0,
        appbar=ft.AppBar(
            title=ft.Text("確認您的行程"),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: app_instance.page.page.go("/app/user/booking_instant")),
        ),
        controls=[
            ft.Stack(
                controls=[
                    ft.Container(content=confirm_map, expand=True, margin=ft.margin.only(bottom=260)),
                    ft.Container(content=info_card, alignment=ft.alignment.bottom_center)
                ],
                expand=True
            )
        ]
    )