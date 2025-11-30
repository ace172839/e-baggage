import flet as ft
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional

from models.trip import Travel, HotelStay
from services.travel_service import TravelService
from services.location_service import LocationService
from services import BookingService

logger = logging.getLogger(__name__)


@dataclass
class HotelStaySegment:
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    hotel_name: str = ""
    is_locked: bool = False

    @property
    def is_complete(self) -> bool:
        return bool(self.check_in_date and self.check_out_date and self.hotel_name)


@dataclass
class TripConfiguration:
    total_start_date: Optional[date] = None
    total_end_date: Optional[date] = None
    segments: List[HotelStaySegment] = field(default_factory=list)
    luggage_count: int = 0
    need_arrival_transfer: bool = False
    need_departure_transfer: bool = False
    arrival_location: str = "桃園國際機場"
    departure_location: str = "桃園國際機場"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_start_date": self.total_start_date.isoformat() if self.total_start_date else None,
            "total_end_date": self.total_end_date.isoformat() if self.total_end_date else None,
            "luggage_count": self.luggage_count,
            "need_arrival_transfer": self.need_arrival_transfer,
            "need_departure_transfer": self.need_departure_transfer,
            "segments": [
                {
                    "check_in_date": seg.check_in_date.isoformat() if seg.check_in_date else None,
                    "check_out_date": seg.check_out_date.isoformat() if seg.check_out_date else None,
                    "hotel_name": seg.hotel_name,
                    "is_locked": seg.is_locked,
                }
                for seg in self.segments
            ],
        }
 

class PreviousBookingController:
    def __init__(self, app_instance):
        self.app = app_instance
        self.page = app_instance.page
        
        # 每次進入 previous_booking 都是一個新的 trip
        self.trip_config: TripConfiguration = TripConfiguration()
        self.preview_travel: Optional[Travel] = None
        self.location_service = LocationService()
        self.hotel_lookup = self._load_hotel_lookup()
        self._init_new_trip()
        
        self.current_step = 1
        self.view = None
        
        # 用於日期選擇器的暫存引用
        self._temp_date_target = None 
        self._temp_segment_index = None
        self._temp_is_start_date = True

        # 初始化 DatePicker
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_picked,
            date_picker_mode=ft.DatePickerMode.DAY
        )
    
    def _load_hotel_lookup(self) -> Dict[str, Dict[str, Any]]:
        lookup: Dict[str, Dict[str, Any]] = {}
        for hotel in BookingService.load_hotels():
            name = hotel.get("name")
            if name:
                lookup[name] = hotel
        return lookup

    def _init_new_trip(self):
        """創建一個新的 previous booking trip"""
        self.trip_config = TripConfiguration()
        self.trip_config.segments = []
        self.preview_travel = None
        logger.info("已創建新的 previous booking trip")

    @staticmethod
    def _coerce_date(value: Optional[date]) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None

    def _geocode_address(self, address: str):
        if not address:
            return None
        try:
            return self.location_service.geocode(address)
        except Exception as exc:
            logger.warning("地理編碼失敗 (%s): %s", address, exc)
            return None

    def _resolve_hotel_metadata(self, hotel_name: str) -> Dict[str, Any]:
        if not hotel_name:
            raise ValueError("請輸入飯店名稱")
        info = self.hotel_lookup.get(hotel_name)
        if info:
            return info
        coords = self._geocode_address(hotel_name)
        if coords:
            lat, lon, formatted = coords
            return {
                "name": hotel_name,
                "address": formatted or hotel_name,
                "lat": lat,
                "lon": lon,
                "is_partner": False,
            }
        return {
            "name": hotel_name,
            "address": hotel_name,
            "lat": 0.0,
            "lon": 0.0,
            "is_partner": False,
        }

    def _build_travel_from_config(self) -> Travel:
        config = self.trip_config
        if not config.total_start_date or not config.total_end_date:
            raise ValueError("請先設定旅程日期")
        if not config.segments:
            raise ValueError("請至少新增一段住宿")

        hotels: List[HotelStay] = []
        for seg in config.segments:
            if not seg.is_complete:
                raise ValueError("請完成所有住宿資訊")
            metadata = self._resolve_hotel_metadata(seg.hotel_name)
            hotels.append(
                HotelStay(
                    hotel_name=seg.hotel_name,
                    address=metadata.get("address", seg.hotel_name),
                    lat=float(metadata.get("lat", 0.0)),
                    lon=float(metadata.get("lon", 0.0)),
                    check_in_date=seg.check_in_date,
                    check_out_date=seg.check_out_date,
                    is_locked=True,
                )
            )

        travel = Travel(
            id=str(uuid.uuid4()),
            total_start_date=config.total_start_date,
            total_end_date=config.total_end_date,
            status="DRAFT",
            luggage_count=config.luggage_count,
            arrival_transfer=config.need_arrival_transfer,
            arrival_location=config.arrival_location,
            departure_transfer=config.need_departure_transfer,
            departure_location=config.departure_location,
            hotels=hotels,
        )

        arrival_coords = self._geocode_address(config.arrival_location) if config.need_arrival_transfer else None
        if arrival_coords:
            travel.arrival_lat, travel.arrival_lon = arrival_coords[0], arrival_coords[1]
        departure_coords = self._geocode_address(config.departure_location) if config.need_departure_transfer else None
        if departure_coords:
            travel.departure_lat, travel.departure_lon = departure_coords[0], departure_coords[1]
        return travel

    def _ensure_preview_travel(self) -> Travel:
        travel = self._build_travel_from_config()
        TravelService.generate_trips(travel)
        self.preview_travel = travel
        return travel

    def bind_view(self, view):
        self.view = view

    # --- Step 1: Landing Page Actions ---

    def set_start_date(self, start: date):
        logger.info(f"設定開始日期: {start}")
        new_start = self._coerce_date(start)
        if not new_start:
            return
        self.trip_config.total_start_date = new_start
        if self.trip_config.total_end_date and self.trip_config.total_end_date <= new_start:
            self.trip_config.total_end_date = new_start + timedelta(days=1)
        self.preview_travel = None

    def set_end_date(self, end: date):
        logger.info(f"設定結束日期: {end}")
        new_end = self._coerce_date(end)
        if not new_end:
            return
        self.trip_config.total_end_date = new_end
        self.preview_travel = None
    
    def _init_first_segment(self):
        """進入 Planning 時，自動建立第一段空白住宿"""
        self.trip_config.segments = []
        start_date = self.trip_config.total_start_date
        if not start_date:
            return
        first_seg = HotelStaySegment(
            check_in_date=start_date, # 預設第一天入住
            check_out_date=None,
            hotel_name=""
        )
        self.trip_config.segments.append(first_seg)

    def go_to_planning(self, e):
        if not self.trip_config.total_start_date or not self.trip_config.total_end_date:
            self.show_snack("請先選擇完整的旅程日期")
            return
        
        if self.trip_config.total_end_date <= self.trip_config.total_start_date:
            self.show_snack("結束日期必須晚於開始日期")
            return

        # 只在第一次進入或 segments 為空時初始化
        if not self.trip_config.segments:
            self._init_first_segment()
        self.current_step = 2
        self.view.update_view()

    # --- Step 2: Planning Actions (Dynamic Segments) ---

    def open_date_picker(self, segment_index, is_start_date):
        """開啟日期選擇器"""
        self._temp_segment_index = segment_index
        self._temp_is_start_date = is_start_date
        
        # 設定可選範圍（限制在旅程日期範圍內）
        current_seg = self.trip_config.segments[segment_index]
        
        # 設定日期選擇器的範圍
        self.date_picker.first_date = self.trip_config.total_start_date
        self.date_picker.last_date = self.trip_config.total_end_date
        
        if is_start_date and segment_index > 0:
            # 如果不是第一段，開始日期不能早於上一段的退房日期
            prev_seg = self.trip_config.segments[segment_index - 1]
            if prev_seg.check_out_date:
                self.date_picker.first_date = prev_seg.check_out_date
        
        self.page.open(self.date_picker)

    def _on_date_picked(self, e):
        """處理日期選擇回調"""
        if e.control.value:
            picked_date = e.control.value.date()
            idx = self._temp_segment_index
            seg = self.trip_config.segments[idx]

            if self._temp_is_start_date:
                seg.check_in_date = picked_date
            else:
                # 驗證：退房日必須晚於入住日
                if seg.check_in_date and picked_date <= seg.check_in_date:
                    self.show_snack("退房日期必須晚於入住日期")
                    return
                seg.check_out_date = picked_date
            
            self.preview_travel = None
            self.view.update_view()

    def update_hotel_name(self, index, name):
        self.trip_config.segments[index].hotel_name = name
        self.preview_travel = None
        # 這裡不需 update_view，因為 TextField 是輸入框

    def add_next_segment(self, current_index):
        """當使用者點擊「確認並新增下一段」"""
        logger.info(f"add_next_segment called for index {current_index}")
        current_seg = self.trip_config.segments[current_index]

        # 1. 驗證當前段落是否填寫完整
        if not current_seg.is_complete:
            missing_fields = []
            if not current_seg.check_in_date:
                missing_fields.append("入住日期")
            if not current_seg.check_out_date:
                missing_fields.append("退房日期")
            if not current_seg.hotel_name:
                missing_fields.append("飯店名稱")
            self.show_snack(f"請完整填寫當前住宿資訊：{', '.join(missing_fields)}")
            return

        # 2. 鎖定當前段落
        current_seg.is_locked = True
        logger.info(f"Segment {current_index} locked")

        # 3. 檢查是否已經覆蓋到總旅程結束日期
        if current_seg.check_out_date >= self.trip_config.total_end_date:
            self.show_snack("行程規劃已完成 (已達旅程結束日期)")
            self.view.update_view()
            return

        # 4. 創建下一段
        new_seg = HotelStaySegment(
            check_in_date=current_seg.check_out_date, # 自動銜接：上一段退房 = 這一段入住
            check_out_date=None,
            hotel_name=""
        )
        self.trip_config.segments.append(new_seg)
        logger.info(f"New segment created. Total segments: {len(self.trip_config.segments)}")
        self.preview_travel = None
        self.view.update_view()

    def remove_last_segment(self, e):
        """刪除最後一段 (如果想重填)"""
        if len(self.trip_config.segments) > 1:
            self.trip_config.segments.pop()
            # 解鎖前一段
            self.trip_config.segments[-1].is_locked = False
            self.preview_travel = None
            self.view.update_view()

    def go_to_confirm(self, e):
        logger.info("go_to_confirm called")
        # 最終驗證
        last_seg = self.trip_config.segments[-1]
        
        logger.info(f"Last segment: check_in={last_seg.check_in_date}, check_out={last_seg.check_out_date}, hotel={last_seg.hotel_name}")
        logger.info(f"Last segment is_complete: {last_seg.is_complete}")
        
        if not last_seg.is_complete:
            missing_fields = []
            if not last_seg.check_in_date:
                missing_fields.append("入住日期")
            if not last_seg.check_out_date:
                missing_fields.append("退房日期")
            if not last_seg.hotel_name:
                missing_fields.append("飯店名稱")
            self.show_snack(f"請完成最後一段住宿的填寫：{', '.join(missing_fields)}")
            logger.warning(f"Last segment validation failed. Missing: {missing_fields}")
            return
        
        # 鎖定最後一段
        last_seg.is_locked = True
        logger.info("Last segment locked")
            
        if last_seg.check_out_date < self.trip_config.total_end_date:
            self.show_snack(f"住宿安排尚未涵蓋至旅程結束 ({self.trip_config.total_end_date})")
            logger.warning(f"Coverage incomplete: {last_seg.check_out_date} < {self.trip_config.total_end_date}")
            return

        try:
            self._ensure_preview_travel()
        except ValueError as exc:
            logger.warning("旅程驗證失敗: %s", exc)
            self.show_snack(str(exc))
            last_seg.is_locked = False
            return
        except Exception as exc:
            logger.exception("建立旅程預覽時發生錯誤: %s", exc)
            self.show_snack("無法建立預覽，請稍後再試")
            last_seg.is_locked = False
            return

        logger.info("Moving to step 3: confirmation")
        self.current_step = 3
        self.view.update_view()

    # --- Step 3: Submission ---

    def submit_order(self, e):
        """儲存規劃完成的旅程"""
        try:
            travel = self.preview_travel or self._ensure_preview_travel()
        except ValueError as exc:
            logger.warning("旅程驗證失敗: %s", exc)
            self.show_snack(str(exc))
            return
        except Exception as exc:
            logger.exception("生成旅程失敗: %s", exc)
            self.show_snack("無法建立旅程，請稍後再試")
            return

        try:
            user_email = getattr(self.app, "current_user_email", "user@example.com")
            TravelService.save_travel_with_trips(travel, user_email)
        except Exception as exc:
            logger.exception("旅程儲存失敗: %s", exc)
            self.show_snack("儲存失敗，請稍後再試")
            return

        self.show_snack("旅程建立成功！", color=ft.Colors.GREEN)
        self.reset_form()
        self.page.go("/app/user/history")

    # --- Helper ---
    def reset_form(self):
        logger.info("重置事先預約表單")
        self._init_new_trip()
        self.current_step = 1
        for ref_attr in [
            "prev_arrival_date_ref",
            "prev_return_date_ref",
            "prev_pickup_location_ref",
            "prev_dropoff_location_ref",
        ]:
            ref = getattr(self.app, ref_attr, None)
            if ref and ref.current:
                ref.current.value = ""
        self.app.prev_arrival_date_val = None
        self.app.prev_return_date_val = None
        self.preview_travel = None
        if self.view:
            self.view.update_view()
        self.page.update()

    def show_snack(self, msg, color=ft.Colors.RED_400):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
    
    def go_back(self, e):
        if self.current_step > 1:
            self.current_step -= 1
            if self.current_step < 3:
                self.preview_travel = None
            if self.view:
                self.view.update_view()
            else:
                self.page.update()
        else:
            self.page.go("/app/user/dashboard")