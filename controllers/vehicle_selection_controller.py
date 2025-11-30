"""Vehicle Selection Controller
管理即時預約送出後的車型推薦與確認流程"""
import flet as ft
import logging
import random
from typing import TYPE_CHECKING, Dict, List, Optional

import requests

from models.trip import Trip
from services.location_service import LocationService
from services.map_util_service import MapUtilService

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


class VehicleSelectionController:
    """集中處理車型推薦、選擇與最終儲存邏輯"""

    OSRM_ENDPOINT = (
        "http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    )

    VEHICLE_LIBRARY: List[Dict[str, object]] = [
        {
            "type": "sedan",
            "label": "舒適轎車",
            "description": "最多 3 件 24 吋行李",
            "icon": ft.Icons.DIRECTIONS_CAR,
            "eta": f"約 {random.randint(2, 10)} 分鐘抵達",
            "multiplier": 1.0,
            "capacity_text": "3 件行李",
        },
        {
            "type": "suv",
            "label": "都會 SUV",
            "description": "最多 5 件 24 吋行李",
            "icon": ft.Icons.DIRECTIONS_CAR_FILLED,
            "eta": f"約 {random.randint(2, 10)} 分鐘抵達",
            "multiplier": 1.25,
            "capacity_text": "5 件行李",
        },
        {
            "type": "van",
            "label": "7 人座商旅",
            "description": "最多 7 件 24 吋行李",
            "icon": ft.Icons.AIRPORT_SHUTTLE,
            "eta": f"約 {random.randint(5, 20)} 分鐘抵達",
            "multiplier": 1.5,
            "capacity_text": "7 件行李",
        },
    ]

    def __init__(self, app_instance: "App") -> None:
        self.app = app_instance
        self.page = app_instance.page
        self.view = None

        self.trip: Optional[Trip] = None
        self.pickup_display = ""
        self.dropoff_display = ""
        self.luggage_note = ""
        self.luggage_count = 0
        self.base_price = 0.0

        self.distance_km = 0.0
        self.eta_min = 0
        self.polyline_points: List[List[float]] = []
        self.center_latlon = (0.0, 0.0)
        self.zoom = 14

        self.selected_vehicle_type = "sedan"
        self.recommended_vehicle_type = "sedan"

    # ------------------ 公開 API ------------------
    def bind_view(self, view) -> None:
        """綁定 View，讓控制器可以要求重繪"""
        logger.debug("綁定 VehicleSelection View")
        self.view = view

    def prepare_from_trip(
        self,
        trip: Trip,
        pickup_display: str,
        dropoff_display: str,
        luggage_count: int,
        luggage_note: str = "",
    ) -> None:
        """接收即時預約建立好的 Trip，準備顯示資料"""
        logger.info("準備 VehicleSelection 資料")
        self.trip = trip
        self.pickup_display = pickup_display
        self.dropoff_display = dropoff_display
        self.luggage_note = luggage_note
        self.luggage_count = max(luggage_count, 1)

        self.recommended_vehicle_type = self._recommend_vehicle(self.luggage_count)
        self.selected_vehicle_type = self.recommended_vehicle_type

        self.base_price = trip.price or self._estimate_price_fallback(trip)
        self.distance_km = round(
            LocationService.calculate_distance(
                trip.pickup_lat,
                trip.pickup_lon,
                trip.dropoff_lat,
                trip.dropoff_lon,
            ),
            1,
        )
        self.eta_min = int(self.distance_km * 2.2) or 5

        self.polyline_points = self._fetch_route_polyline(
            trip.pickup_lat,
            trip.pickup_lon,
            trip.dropoff_lat,
            trip.dropoff_lon,
        ) or [
            [trip.pickup_lon, trip.pickup_lat],
            [trip.dropoff_lon, trip.dropoff_lat],
        ]
        self.center_latlon = MapUtilService.calculate_center(
            trip.pickup_lat,
            trip.pickup_lon,
            trip.dropoff_lat,
            trip.dropoff_lon,
        )
        self.zoom = MapUtilService.calculate_zoom_level(
            trip.pickup_lat,
            trip.pickup_lon,
            trip.dropoff_lat,
            trip.dropoff_lon,
        )

        if self.view:
            self.view.update_view()

    def get_vehicle_options(self) -> List[Dict[str, object]]:
        """提供 View 使用的車型列表"""
        options = []
        for option in self.VEHICLE_LIBRARY:
            is_selected = option["type"] == self.selected_vehicle_type
            is_recommended = option["type"] == self.recommended_vehicle_type
            price = self._format_price(option)
            options.append(
                {
                    **option,
                    "price": price,
                    "is_selected": is_selected,
                    "is_recommended": is_recommended,
                }
            )
        return options

    def get_map_context(self) -> Dict[str, object]:
        """Map View 需要的基本座標資訊"""
        if not self.trip:
            return {}
        return {
            "center": self.center_latlon,
            "zoom": self.zoom,
            "polyline": self.polyline_points,
            "pickup": {
                "label": self.pickup_display,
                "lat": self.trip.pickup_lat,
                "lon": self.trip.pickup_lon,
            },
            "dropoff": {
                "label": self.dropoff_display,
                "lat": self.trip.dropoff_lat,
                "lon": self.trip.dropoff_lon,
            },
        }

    def get_trip_summary(self) -> Dict[str, object]:
        if not self.trip:
            return {}
        return {
            "pickup": self.pickup_display,
            "dropoff": self.dropoff_display,
            "luggage_count": self.luggage_count,
            "luggage_note": self.luggage_note,
            "distance_km": self.distance_km,
            "eta_min": self.eta_min,
        }

    def select_vehicle(self, vehicle_type: str) -> None:
        """使用者點選某個車型卡片"""
        if vehicle_type not in {opt["type"] for opt in self.VEHICLE_LIBRARY}:
            logger.warning("未知車型: %s", vehicle_type)
            return
        self.selected_vehicle_type = vehicle_type
        if self.view:
            self.view.update_view()

    def confirm_vehicle_choice(self, e=None) -> None:
        """確認車型並寫入行程"""
        if not self.trip:
            self._show_snack("尚未建立行程，請回到即時預約")
            self.page.go("/app/user/instant_booking")
            return

        selected_option = next(
            (opt for opt in self.VEHICLE_LIBRARY if opt["type"] == self.selected_vehicle_type),
            None,
        )
        if not selected_option:
            self._show_snack("請選擇車型")
            return

        ib_controller = getattr(self.app, "instant_booking_controller", None)
        if not ib_controller or not self.trip:
            logger.error("InstantBookingController 未就緒，無法進入確認步驟")
            self._show_snack("系統忙碌中，請稍後再試")
            return

        price_value = self._calculate_price(selected_option)
        self.trip.vehicle_type = selected_option["type"]
        self.trip.price = price_value

        ib_controller.present_vehicle_confirmation(
            vehicle_type=selected_option["type"],
            vehicle_label=selected_option["label"],
            vehicle_price=price_value,
        )
        self._show_snack("已套用推薦車型，請確認訂單", color=ft.Colors.GREEN_700)
        self.page.go("/app/user/instant_booking")

    def go_back_to_edit(self, e=None) -> None:
        """返回訂單確認步驟"""
        if self.app.instant_booking_controller:
            self.app.instant_booking_controller.current_step = 2
            if self.app.instant_booking_controller.view:
                self.app.instant_booking_controller.view.update_view()
        self.page.go("/app/user/instant_booking")

    def reset(self) -> None:
        """清除暫存狀態"""
        self.trip = None
        self.pickup_display = ""
        self.dropoff_display = ""
        self.luggage_note = ""
        self.luggage_count = 0
        self.base_price = 0.0
        self.distance_km = 0.0
        self.eta_min = 0
        self.polyline_points = []
        self.center_latlon = (0.0, 0.0)
        self.zoom = 14
        self.selected_vehicle_type = "sedan"
        self.recommended_vehicle_type = "sedan"

    # ------------------ 私有工具 ------------------
    def _recommend_vehicle(self, luggage_count: int) -> str:
        if luggage_count < 3:
            return "sedan"
        if luggage_count < 5:
            return "suv"
        return "van"

    def _estimate_price_fallback(self, trip: Trip) -> float:
        """缺少 price 時，根據距離與車型大致估算"""
        distance_km = LocationService.calculate_distance(
            trip.pickup_lat,
            trip.pickup_lon,
            trip.dropoff_lat,
            trip.dropoff_lon,
        )
        return max(350.0, distance_km * 80)

    def _calculate_price(self, option: Dict[str, object]) -> float:
        multiplier = float(option.get("multiplier", 1))
        return round(self.base_price * multiplier)

    def _format_price(self, option: Dict[str, object]) -> str:
        price = self._calculate_price(option)
        return f"NT$ {price:,.0f}"

    def _show_snack(self, message: str, color: str = ft.Colors.RED) -> None:
        snack = ft.SnackBar(ft.Text(message), bgcolor=color)
        snack.open = True
        self.page.snack_bar = snack
        self.page.update()

    def _fetch_route_polyline(
        self,
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
    ) -> Optional[List[List[float]]]:
        url = self.OSRM_ENDPOINT.format(
            start_lon=pickup_lon,
            start_lat=pickup_lat,
            end_lon=dropoff_lon,
            end_lat=dropoff_lat,
        )
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            routes = data.get("routes") or []
            if routes:
                coordinates = routes[0]["geometry"]["coordinates"]
                if coordinates:
                    return coordinates
        except Exception as exc:
            logger.warning("OSRM 路線取得失敗: %s", exc)
        return None
