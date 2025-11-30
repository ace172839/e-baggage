"""
History Controller
處理訂單歷史的業務邏輯
"""
import flet as ft
import logging
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any, Optional

from services import OrderHistoryService, DateService

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


class HistoryController:
    """訂單歷史控制器"""
    
    STATUS_LABELS = {
        "pending": "待確認",
        "confirmed": "已確認",
        "completed": "已完成",
        "cancelled": "已取消",
    }

    STATUS_COLORS = {
        "pending": ft.Colors.ORANGE_300,
        "confirmed": ft.Colors.BLUE_300,
        "completed": ft.Colors.GREEN_300,
        "cancelled": ft.Colors.RED_300,
    }

    def __init__(self, app_instance: 'App'):
        logger.info("初始化 HistoryController")
        self.app = app_instance
        self.page = app_instance.page
        self.view = None
        
        # 當前篩選條件
        self.filter_status = "all"  # all, pending, completed, cancelled
        self.orders: List[Dict[str, Any]] = []
        logger.debug("HistoryController 初始化完成")
        
    def bind_view(self, view):
        """綁定 View 實例"""
        logger.info("綁定 View 到 HistoryController")
        self.view = view
        
    def load_orders(self):
        """載入訂單列表"""
        try:
            # 從 Service 獲取訂單
            user_email = self.app.current_user_email if hasattr(self.app, 'current_user_email') else "user@example.com"
            
            # 獲取所有排序後的訂單，然後過濾當前用戶
            all_orders = OrderHistoryService.get_orders_sorted_by_date(reverse=True)
            self.orders = [
                order for order in all_orders 
                if order.get('user_email') == user_email
            ]
            
            logger.info(f"載入了 {len(self.orders)} 筆訂單 (用戶: {user_email})")
            
            # 根據篩選條件過濾
            self.apply_filter()
            
        except Exception as e:
            logger.error(f"載入訂單失敗: {e}")
            self.orders = []
            
    def apply_filter(self):
        """套用篩選條件"""
        if self.filter_status == "all":
            return
            
        # 篩選訂單
        self.orders = [
            order for order in self.orders 
            if order.get("status") == self.filter_status
        ]
        
        logger.info(f"篩選後剩餘 {len(self.orders)} 筆訂單")
        
    def set_filter(self, status: str, e=None):
        """設定篩選條件"""
        self.filter_status = status
        logger.info(f"設定篩選: {status}")
        
        # 重新載入訂單
        self.load_orders()
        
        # 更新 View
        if self.view:
            self.view.update_view()
            
    def _format_iso_datetime(self, iso_value: Optional[str]) -> str:
        if not iso_value:
            return ""
        try:
            dt = datetime.fromisoformat(iso_value)
            return DateService.format_date(dt, DateService.DATETIME_FORMAT)
        except ValueError:
            return iso_value

    def extract_order_fields(self, order: Dict[str, Any]) -> Dict[str, Any]:
        identifier = order.get("id") or order.get("order_id") or order.get("trip_id") or "N/A"
        raw_status = (order.get("status") or "pending").lower()
        status_key = raw_status if raw_status in self.STATUS_LABELS else raw_status
        status_label = self.STATUS_LABELS.get(status_key, raw_status.upper())
        status_color = self.STATUS_COLORS.get(status_key, ft.Colors.GREY_300)

        date_str = order.get("date", "")
        date_time_display = ""
        primary_datetime_field = order.get("start_time") or order.get("created_at") or order.get("timestamp")
        if primary_datetime_field:
            try:
                dt = datetime.fromisoformat(primary_datetime_field)
                date_str = DateService.format_date(dt)
                date_time_display = DateService.format_date(dt, DateService.DATETIME_FORMAT)
            except ValueError:
                date_time_display = primary_datetime_field
                if not date_str and "T" in primary_datetime_field:
                    date_str = primary_datetime_field.split("T")[0]

        pickup = (
            order.get("pickup_display")
            or order.get("pickup_location")
            or order.get("pickup")
            or order.get("start_address")
            or "未提供"
        )
        dropoff = (
            order.get("dropoff_display")
            or order.get("dropoff_location")
            or order.get("dropof")
            or order.get("end_address")
            or "未提供"
        )

        price = order.get("price") or order.get("amount")
        if isinstance(price, (int, float)):
            price_display = f"NT$ {price:,.0f}"
        elif price:
            price_display = f"NT$ {price}"
        else:
            price_display = "—"

        luggage_items = order.get("luggage_items") or []
        if luggage_items:
            luggage_count = sum(int(item.get("quantity", 1) or 1) for item in luggage_items)
        else:
            luggage_count = order.get("luggage_count") or order.get("luggages")

        return {
            "order_id": identifier,
            "status_key": status_key,
            "status_label": status_label,
            "status_color": status_color,
            "order_date": date_str,
            "order_datetime": date_time_display,
            "pickup": pickup,
            "dropoff": dropoff,
            "price_display": price_display,
            "raw_price": price,
            "order_type": order.get("order_type", "legacy"),
            "luggage_count": luggage_count,
            "luggage_note": order.get("luggage_note"),
            "start_time_str": self._format_iso_datetime(order.get("start_time")),
            "end_time_str": self._format_iso_datetime(order.get("end_time")),
            "parent_travel_id": order.get("parent_travel_id"),
        }

    def view_order_detail(self, order_id: str, e=None):
        """查看訂單詳情"""
        logger.info(f"查看訂單詳情: {order_id}")

        order = next(
            (o for o in self.orders if (o.get("id") or o.get("order_id")) == order_id),
            None,
        )
        if not order:
            self.page.snack_bar = ft.SnackBar(ft.Text("找不到訂單"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return

        info = self.extract_order_fields(order)

        def _text_row(label: str, value: str, icon: Optional[str] = None):
            leading = ft.Icon(icon, size=18, color=ft.Colors.BLACK87) if icon else None
            row_controls = []
            if leading:
                row_controls.append(leading)
            row_controls.append(
                ft.Column(
                    controls=[
                        ft.Text(label, size=11, color=ft.Colors.GREY_600),
                        ft.Text(value or "—", size=14, color=ft.Colors.BLACK87, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=2,
                )
            )
            return ft.Row(controls=row_controls, spacing=10)

        details_column = ft.Column(
            controls=[
                _text_row("狀態", info["status_label"]),
                _text_row("訂單編號", info["order_id"]),
                _text_row("建立時間", info["order_datetime"] or info["start_time_str"]),
                _text_row("行程開始", info["start_time_str"]),
                _text_row("行程結束", info["end_time_str"]),
                _text_row("起點", info["pickup"]),
                _text_row("終點", info["dropoff"]),
                _text_row("金額", info["price_display"]),
            ],
            spacing=8,
            tight=True,
            scroll=True,
            height=300,
        )

        if info["luggage_count"]:
            details_column.controls.append(
                _text_row("行李件數", str(info["luggage_count"]))
            )
        if info["luggage_note"]:
            details_column.controls.append(
                _text_row("行李備註", info["luggage_note"])
            )
        if info["parent_travel_id"]:
            details_column.controls.append(
                _text_row("所屬旅程", info["parent_travel_id"])
            )

        dialog = ft.AlertDialog(
            title=ft.Text(f"訂單詳情", weight=ft.FontWeight.BOLD),
            content=ft.Container(content=details_column, width=420),
            actions=[ft.TextButton("關閉", on_click=lambda e: self.page.close(dialog))],
        )

        self.page.open(dialog)
        self.page.update()
        
    def cancel_order(self, order_id: str, e=None):
        """取消訂單"""
        logger.info(f"取消訂單: {order_id}")
        
        # 顯示確認對話框
        def confirm_cancel(e):
            try:
                success = OrderHistoryService.update_order_status(order_id, "cancelled")
                if success:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text(f"訂單 {order_id} 已取消"),
                        bgcolor=ft.Colors.ORANGE
                    )
                    # 重新載入訂單
                    self.load_orders()
                    if self.view:
                        self.view.update_view()
                else:
                    self.page.snack_bar = ft.SnackBar(
                        ft.Text("找不到訂單，無法取消"),
                        bgcolor=ft.Colors.RED
                    )
                self.page.snack_bar.open = True
            except Exception as ex:
                logger.error(f"取消訂單失敗: {ex}")
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("取消訂單失敗"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
            finally:
                self.page.close(dialog)
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("確認取消訂單"),
            content=ft.Text(f"確定要取消訂單 {order_id} 嗎？"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("確認", on_click=confirm_cancel),
            ],
        )
        
        self.page.open(dialog)
        
    def refresh_orders(self, e=None):
        """刷新訂單列表"""
        logger.info("刷新訂單列表")
        self.load_orders()
        
        if self.view:
            self.view.update_view()
            
        self.page.snack_bar = ft.SnackBar(
            ft.Text("訂單列表已更新"),
            bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    def go_to_new_booking(self, e=None):
        """前往新預約頁面"""
        logger.info("前往新預約")
        self.page.go("/app/user/instant_booking")
