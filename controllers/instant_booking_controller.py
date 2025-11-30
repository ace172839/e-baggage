"""
Instant Booking Controller
處理即時預約的業務邏輯
"""
import flet as ft
import logging
import math
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Tuple

from services import BookingService
from services.location_service import LocationService
from services.travel_service import TravelService
from models.trip import Trip, LuggageItem
from config import USER_DASHBOARD_DEFAULT_LOCATION

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


class InstantBookingController:
    """即時預約控制器"""
    
    def __init__(self, app_instance: 'App'):
        logger.info("初始化 InstantBookingController")
        self.app = app_instance
        self.page = app_instance.page
        self.view = None
        
        # 當前步驟: 1=地圖選擇, 2=確認訂單
        self.current_step = 1

        self.pending_trip: Optional[Trip] = None
        self.pickup_location = ""
        self.dropoff_location = ""
        self.luggage_count = 1
        self.luggage_note = ""  # 行李備注
        self.scan_confirmed = False
        self.location_service = LocationService()
        self.selected_vehicle_type: str = ""
        self.selected_vehicle_label: str = ""
        self.selected_vehicle_price: float = 0.0
        
        # 飯店資料管理
        self.all_hotels = BookingService.load_partner_hotels()
        self.nearby_hotels = []
        self.current_map_center = USER_DASHBOARD_DEFAULT_LOCATION
        
        logger.debug("InstantBookingController 初始化完成")
        
    def update_nearby_hotels(self, lat, lon, radius_km=5.0, limit=50):
        """更新附近的飯店列表"""
        self.current_map_center = (lat, lon)
        
        # 簡單的距離計算 (歐幾里得距離近似)
        # 1度緯度約 111km
        # 1度經度約 111km * cos(lat)
        
        def calculate_distance(h_lat, h_lon):
            return math.sqrt((h_lat - lat)**2 + (h_lon - lon)**2)
            
        # 排序並取前 limit 個
        sorted_hotels = sorted(
            self.all_hotels,
            key=lambda h: calculate_distance(h['lat'], h['lon'])
        )
        
        self.nearby_hotels = sorted_hotels[:limit]
        logger.info(f"已更新附近飯店列表，中心: ({lat}, {lon})，數量: {len(self.nearby_hotels)}")
        
        # 如果 View 已經綁定，通知 View 更新地圖標記
        if self.view and hasattr(self.view, 'update_map_markers'):
            self.view.update_map_markers()
            
    def on_map_position_changed(self, e):
        """地圖位置改變時的回調"""
        # 注意：頻繁觸發，建議只更新座標，不立即搜尋
        if hasattr(e, 'center'):
            self.current_map_center = (e.center.latitude, e.center.longitude)
            
    def search_hotels_at_current_center(self, e=None):
        """在當前地圖中心搜尋飯店"""
        lat, lon = self.current_map_center
        self.update_nearby_hotels(lat, lon)
    
    def bind_view(self, view):
        """綁定 View 實例"""
        logger.info("綁定 View 到 InstantBookingController")
        self.view = view

    # --- Helper utilities ---

    def _init_new_trip(self):
        """清空暫存行程，確保每次操作都有全新計算"""
        self.pending_trip = None

    def refresh_user_location(self):
        """嘗試根據目前輸入的定位更新地圖中心"""
        candidate = None
        if self.app.current_location_ref.current and self.app.current_location_ref.current.value:
            candidate = self.app.current_location_ref.current.value
        elif self.app.pickup_location_ref.current and self.app.pickup_location_ref.current.value:
            candidate = self.app.pickup_location_ref.current.value

        if candidate:
            coords = self._geocode_address(candidate)
            if coords:
                self.current_map_center = coords
                logger.info("地圖中心更新為使用者位置 %s", coords)

    def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        if not address:
            return None
        try:
            result = self.location_service.geocode(address)
        except Exception as exc:
            logger.warning("地址 %s 地理編碼失敗: %s", address, exc)
            return None

        if result:
            lat, lon, _ = result
            return (lat, lon)
        return None

    def _build_luggage_items(self) -> List[LuggageItem]:
        details = getattr(self.app, "scan_baggage_details", None)
        items: List[LuggageItem] = []
        if details:
            for record in details:
                try:
                    size = int(record.get("size", 24))
                except (TypeError, ValueError):
                    size = 24
                quantity = int(record.get("quantity", 1) or 1)
                items.append(LuggageItem(size=size, quantity=max(quantity, 1)))
        if not items:
            items = [LuggageItem(size=24, quantity=max(self.luggage_count or 1, 1))]
        return items

    def _compute_pending_trip(self) -> None:
        pickup_ref = self.app.pickup_location_ref.current
        dropoff_ref = self.app.dropoff_location_ref.current
        pickup_value = pickup_ref.value if pickup_ref else ""
        dropoff_value = dropoff_ref.value if dropoff_ref else ""

        pickup_coords = self._geocode_address(pickup_value) or self.current_map_center
        dropoff_coords = self._geocode_address(dropoff_value)

        if not pickup_coords:
            raise ValueError("無法取得上車地點座標")
        if not dropoff_coords:
            raise ValueError("無法取得下車地點座標")

        luggage_items = self._build_luggage_items()
        start_time = datetime.now()
        pickup_payload = (pickup_value, pickup_coords[0], pickup_coords[1])
        dropoff_payload = (dropoff_value, dropoff_coords[0], dropoff_coords[1])

        self.pending_trip = TravelService.build_manual_trip(
            start_time=start_time,
            pickup=pickup_payload,
            dropoff=dropoff_payload,
            luggage_items=luggage_items,
            parent_id=None,
        )
        self.pending_trip.status = "PENDING"

    def _show_snack(self, message: str, color: str = ft.Colors.RED):
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
        
    def handle_pickup_location_select(self, e):
        """處理上車地點選擇"""
        logger.info("開始選擇上車地點")
        self.page.go("/app/user/map/instant_pickup")
        
    def handle_dropoff_location_select(self, e):
        """處理下車地點選擇"""
        logger.info("開始選擇下車地點")
        self.page.go("/app/user/map/instant_dropoff")
        
    def handle_scan_baggage(self, e):
        """處理掃描行李"""
        logger.info("AI 行李掃描功能啟動！")
        self.page.go("/app/user/scan")
        
    def update_luggage_count(self, e):
        """更新行李數量"""
        try:
            count = int(e.control.value)
            self.luggage_count = max(1, min(10, count))  # 限制 1-10 件
            logger.info(f"行李數量更新為: {self.luggage_count}")
        except ValueError:
            logger.warning(f"無效的行李數量: {e.control.value}")
            
    def update_luggage_note(self, e):
        """更新行李備注"""
        self.luggage_note = e.control.value or ""
        logger.info(f"行李備注更新為: {self.luggage_note}")
            
    def go_to_confirm(self, e):
        """前往確認頁面"""
        logger.info("處理前往確認頁面請求")
        # 驗證必填欄位
        if not self.app.pickup_location_ref.current or not self.app.pickup_location_ref.current.value:
            logger.warning("上車地點未選擇")
            self._show_snack("請選擇上車地點")
            return
            
        if not self.app.dropoff_location_ref.current or not self.app.dropoff_location_ref.current.value:
            logger.warning("下車地點未選擇")
            self._show_snack("請選擇下車地點")
            return
            
        # 驗證行李掃描
        if not self.scan_confirmed:
            logger.warning("行李尚未掃描")
            self._show_snack("請先掃描行李！")
            return
        
        # 儲存數據
        self.pickup_location = self.app.pickup_location_ref.current.value
        self.dropoff_location = self.app.dropoff_location_ref.current.value
        if self.app.luggage_note_ref.current:
            self.luggage_note = self.app.luggage_note_ref.current.value or ""
        try:
            self._compute_pending_trip()
        except ValueError as exc:
            logger.warning("計算行程失敗: %s", exc)
            self._show_snack(str(exc))
            return
        except Exception as exc:
            logger.error("計算行程時發生錯誤: %s", exc)
            self._show_snack("無法計算預估價格，請稍後重試")
            return

        logger.info(f"即時預約: {self.pickup_location} -> {self.dropoff_location}, 備注: {self.luggage_note}")

        self._clear_vehicle_selection()
        self.submit_order(e)
            
    def submit_order(self, e):
        """導向車型選擇畫面，延後最終儲存"""
        logger.info("提交即時預約訂單，準備車型選擇")

        if not self.pending_trip:
            try:
                self._compute_pending_trip()
            except ValueError as exc:
                logger.warning("缺少訂單資料: %s", exc)
                self._show_snack(str(exc))
                return
            except Exception as exc:
                logger.error("無法生成行程: %s", exc)
                self._show_snack("無法建立行程，請稍後再試")
                return

        vehicle_controller = getattr(self.app, "vehicle_selection_controller", None)
        if not vehicle_controller:
            logger.error("VehicleSelectionController 未就緒")
            self._show_snack("系統忙碌中，請稍後再嘗試")
            return

        vehicle_controller.prepare_from_trip(
            trip=self.pending_trip,
            pickup_display=self.pickup_location,
            dropoff_display=self.dropoff_location,
            luggage_count=self.luggage_count,
            luggage_note=self.luggage_note,
        )
        self.page.go("/app/user/vehicle_selection")

    def present_vehicle_confirmation(
        self,
        vehicle_type: str,
        vehicle_label: str,
        vehicle_price: float,
    ) -> None:
        """紀錄車型結果並切換到最終確認畫面"""
        if not self.pending_trip:
            logger.error("pending_trip 不存在，無法顯示確認頁")
            self._show_snack("系統忙碌中，請重新建立訂單")
            return

        self.selected_vehicle_type = vehicle_type
        self.selected_vehicle_label = vehicle_label
        self.selected_vehicle_price = vehicle_price
        self.pending_trip.vehicle_type = vehicle_type
        self.pending_trip.price = vehicle_price

        self.current_step = 2
        if self.view:
            self.view.update_view()
        else:
            self.page.go("/app/user/instant_booking")

    def finalize_booking(self, e):
        """最終確認訂單並儲存"""
        if not self.pending_trip:
            self._show_snack("訂單資訊不完整，請重新操作")
            return
        if not self.selected_vehicle_type:
            self._show_snack("請先選擇車型")
            return

        user_email = getattr(self.app, "current_user_email", "user@example.com")
        try:
            TravelService.save_single_trip(
                self.pending_trip,
                user_email=user_email,
                order_type="instant_trip",
                extra_fields={
                    "pickup_display": self.pickup_location,
                    "dropoff_display": self.dropoff_location,
                    "luggage_note": self.luggage_note,
                    "selected_vehicle": self.selected_vehicle_type,
                },
            )
        except Exception as exc:  # pragma: no cover - UI feedback path
            logger.exception("即時預約儲存失敗: %s", exc)
            self._show_snack("儲存失敗，請稍後再試")
            return

        self._show_snack("已為您派車，稍候即抵達！", color=ft.Colors.GREEN_600)

        vehicle_controller = getattr(self.app, "vehicle_selection_controller", None)
        if vehicle_controller:
            vehicle_controller.reset()

        self.reset_form()
        self.page.go("/app/user/history")
            
    def go_back(self, e):
        """返回上一步"""
        logger.info(f"返回上一步，當前步驟: {self.current_step}")
        if self.current_step > 1:
            self.current_step = 1
            if self.view:
                self.view.update_view()
            else:
                self.page.go("/app/user/instant_booking")
        else:
            self.page.go("/app/user/dashboard")
            
    def reset_form(self):
        """重置表單並創建新的 trip"""
        logger.info("重置即時預約表單")
        self.current_step = 1
        self.pickup_location = ""
        self.dropoff_location = ""
        self.luggage_count = 1
        self.luggage_note = ""
        self.scan_confirmed = False
        self._clear_vehicle_selection()
        
        # 創建新的 trip
        self._init_new_trip()
        
        if self.app.pickup_location_ref.current:
            self.app.pickup_location_ref.current.value = ""
        if self.app.dropoff_location_ref.current:
            self.app.dropoff_location_ref.current.value = ""
        if self.app.luggage_note_ref.current:
            self.app.luggage_note_ref.current.value = ""

    def _clear_vehicle_selection(self) -> None:
        self.selected_vehicle_type = ""
        self.selected_vehicle_label = ""
        self.selected_vehicle_price = 0.0
