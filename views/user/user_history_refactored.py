"""
History View (重構版)
使用 Controller 模式，無業務邏輯判斷
"""
import flet as ft
from typing import TYPE_CHECKING
import logging

from constants import *
from config import WINDOW_WIDTH
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab
from services import DateService
from controllers import HistoryController

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_history_view(app_instance: 'App') -> ft.View:
    """
    建立訂單歷史 View
    使用 Controller 模式
    """
    logger.info("建立訂單歷史 View")
    
    # 使用 App 中已初始化的 Controller (保持狀態)
    controller = app_instance.history_controller
    logger.debug(f"使用現有 HistoryController，filter_status={controller.filter_status}")
    
    # 載入訂單
    controller.load_orders()
    
    # 主容器
    main_content = ft.Container(expand=True)
    
    def _create_order_card(order):
        """創建訂單卡片"""
        info = controller.extract_order_fields(order)
        order_id = info["order_id"]
        order_date = info["order_date"]
        pickup = info["pickup"]
        dropoff = info["dropoff"]
        status = info["status_key"]
        status_label = info["status_label"]
        status_color = info["status_color"]
        
        return ft.Container(
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.BLACK12),
            content=ft.Column(
                controls=[
                    # 訂單頭部
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(
                                    status_label,
                                    size=12,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD
                                ),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                bgcolor=status_color,
                                border_radius=5
                            ),
                            ft.Text(
                                order_date,
                                size=14,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                f"#{order_id}",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT_DARK
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 起點
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TRIP_ORIGIN, color=ft.Colors.GREEN_700, size=20),
                            ft.Column(
                                controls=[
                                    ft.Text("起點", size=11, color=ft.Colors.GREY_600),
                                    ft.Text(pickup, size=14, color=COLOR_TEXT_DARK)
                                ],
                                spacing=2,
                                expand=True
                            )
                        ],
                        spacing=10
                    ),
                    
                    # 箭頭
                    ft.Container(
                        content=ft.Icon(ft.Icons.ARROW_DOWNWARD, size=16, color=ft.Colors.GREY_400),
                        margin=ft.margin.only(left=10)
                    ),
                    
                    # 終點
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PLACE, color=ft.Colors.RED_700, size=20),
                            ft.Column(
                                controls=[
                                    ft.Text("終點", size=11, color=ft.Colors.GREY_600),
                                    ft.Text(dropoff, size=14, color=COLOR_TEXT_DARK)
                                ],
                                spacing=2,
                                expand=True
                            )
                        ],
                        spacing=10
                    ),
                    
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    
                    # 操作按鈕
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                text="查看詳情",
                                icon=ft.Icons.INFO_OUTLINE,
                                on_click=lambda e, oid=order_id: controller.view_order_detail(oid, e)  # 委派給 Controller
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                text="取消訂單",
                                icon=ft.Icons.CANCEL_OUTLINED,
                                style=ft.ButtonStyle(color=ft.Colors.RED_700),
                                on_click=lambda e, oid=order_id: controller.cancel_order(oid, e),  # 委派給 Controller
                                visible=status == "pending"
                            ) if status == "pending" else ft.Container()
                        ],
                        spacing=10
                    )
                ],
                spacing=5
            )
        )
    
    def _build_content():
        """建立內容區域"""
        
        # 篩選按鈕組
        filter_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    text="全部",
                    bgcolor=COLOR_BRAND_YELLOW if controller.filter_status == "all" else ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    on_click=lambda e: controller.set_filter("all", e)  # 委派給 Controller
                ),
                ft.ElevatedButton(
                    text="待確認",
                    bgcolor=COLOR_BRAND_YELLOW if controller.filter_status == "pending" else ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    on_click=lambda e: controller.set_filter("pending", e)  # 委派給 Controller
                ),
                ft.ElevatedButton(
                    text="已完成",
                    bgcolor=COLOR_BRAND_YELLOW if controller.filter_status == "completed" else ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    on_click=lambda e: controller.set_filter("completed", e)  # 委派給 Controller
                ),
                ft.ElevatedButton(
                    text="已取消",
                    bgcolor=COLOR_BRAND_YELLOW if controller.filter_status == "cancelled" else ft.Colors.WHITE,
                    color=COLOR_TEXT_DARK,
                    on_click=lambda e: controller.set_filter("cancelled", e)  # 委派給 Controller
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        # 訂單列表
        order_cards = []
        if controller.orders:
            for order in controller.orders:
                order_cards.append(_create_order_card(order))
        else:
            # 空狀態
            order_cards.append(
                ft.Container(
                    padding=40,
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.INBOX, size=80, color=ft.Colors.GREY_400),
                            ft.Text(
                                "暫無訂單記錄",
                                size=18,
                                color=ft.Colors.GREY_600,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                "開始您的第一筆預約吧！",
                                size=14,
                                color=ft.Colors.GREY_500
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                text="立即預約",
                                icon=ft.Icons.ADD,
                                bgcolor=COLOR_BRAND_YELLOW,
                                color=COLOR_TEXT_DARK,
                                on_click=controller.go_to_new_booking  # 委派給 Controller
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.alignment.center
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            expand=True,
            content=ft.Column(
                controls=[
                    # 標題列
                    ft.Row(
                        controls=[
                            ft.Text(
                                "訂單歷史",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TEXT_DARK
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                icon_color=COLOR_TEXT_DARK,
                                tooltip="刷新",
                                on_click=controller.refresh_orders  # 委派給 Controller
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 篩選按鈕
                    filter_buttons,
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 訂單列表
                    ft.Container(
                        content=ft.Column(
                            controls=order_cards,
                            spacing=15,
                            scroll=ft.ScrollMode.AUTO
                        ),
                        expand=True
                    )
                ],
                spacing=0
            )
        )
    
    def update_view(self=None):
        """更新 View 內容（由 Controller 調用）"""
        main_content.content = _build_content()
        main_content.update()
    
    # 綁定 update_view 到 controller
    controller.bind_view(type('ViewUpdater', (), {'update_view': update_view})())
    
    # 設置初始內容（不調用 update）
    main_content.content = _build_content()
    
    # 返回 View
    return ft.View(
        route="/app/user/history",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            main_content,
            build_bottom_nav_bar(app_instance, selected_index=2)  # 假設歷史在第2個位置
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )
