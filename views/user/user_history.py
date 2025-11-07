import flet as ft
import json
from datetime import datetime
from constants import *
from config import WINDOW_WIDTH


PAGE_SIZE = 5

def get_orders():
    with open('demo_db.json', 'r') as f:
        data = json.load(f)
    return data.get('orders', [])

def history_view(page: ft.Page) -> ft.View:
    orders = get_orders()
    orders.sort(key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d'), reverse=True)

    start_index = 0

    def create_order_entry(order):
        return ft.Container(
            ft.Column([
                ft.Text(f" {datetime.strptime(order['date'], '%Y/%m/%d').strftime('%Y-%m-%d')}", size=18, color=COLOR_TEXT_DARK),
                ft.Text(f"To:   {order['dropof']}", size=14, color=COLOR_TEXT_DARK),
                ft.Text(f"From: {order['pickup']}", size=12, color=COLOR_TEXT_DARK),
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            width=WINDOW_WIDTH*0.9
        )

    orders_list = ft.Column(spacing=5)
    
    prev_button = ft.ElevatedButton("Previous", on_click=lambda e: go_prev(e), disabled=True)
    next_button = ft.ElevatedButton("Next", on_click=lambda e: go_next(e))

    def update_orders_list():
        end_index = min(start_index + PAGE_SIZE, len(orders))
        order_items = [create_order_entry(orders[i]) for i in range(start_index, end_index)]
        
        can_go_back = start_index > 0
        can_go_forward = end_index < len(orders)
        
        prev_button.disabled = not can_go_back
        next_button.disabled = not can_go_forward
        
        orders_list.controls = order_items
        if page.route == "/app/user/history":
            page.update()

    def go_back(e):
        page.go("/app/user/dashboard")

    def go_prev(e):
        nonlocal start_index
        start_index = max(0, start_index - PAGE_SIZE)
        update_orders_list()

    def go_next(e):
        nonlocal start_index
        start_index += PAGE_SIZE
        update_orders_list()

    update_orders_list()

    back_button = ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back)

    return ft.View(
        route="/app/user/history",
        controls=[
            ft.Row([back_button, prev_button, next_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            orders_list,
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )

