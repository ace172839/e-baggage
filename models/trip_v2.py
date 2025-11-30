from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Optional

@dataclass
class HotelStaySegment:
    """代表一段連續的住宿"""
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    hotel_name: str = ""
    is_locked: bool = False  # 如果使用者確認了這一段，UI 上鎖定它

    @property
    def is_complete(self):
        return self.check_in_date and self.check_out_date and self.hotel_name

    def to_dict(self):
        """序列化用"""
        return {
            "check_in_date": self.check_in_date.isoformat() if self.check_in_date else None,
            "check_out_date": self.check_out_date.isoformat() if self.check_out_date else None,
            "hotel_name": self.hotel_name,
        }

@dataclass
class Trip:
    """即時叫車、或是事先預約的旅館間移動"""
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    pickup_location: str = ""
    dropoff_location: str = ""
    luggage_count: int = 0


    @property
    def is_complete(self):
        return self.check_in_date and self.check_out_date and self.hotel_name

    def to_dict(self):
        """序列化用"""
        return {
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "pickup_location": self.pickup_location,
            "dropoff_location": self.dropoff_location,
            "luggage_count": self.luggage_count,
        }

@dataclass
class Travel:
    """整個旅程的設定"""
    # 這些是 Landing Page 設定的大範圍
    total_start_date: Optional[datetime] = None
    total_end_date: Optional[datetime] = None
    
    # 接送設定
    need_arrival_transfer: bool = True
    need_departure_transfer: bool = True
    
    # 動態增加的住宿段落
    segments: List[HotelStaySegment] = field(default_factory=list)

    trips: List[Trip] = field(default_factory=list)

    def to_dict(self):
        return {
            "total_start_date": self.total_start_date.isoformat() if self.total_start_date else None,
            "total_end_date": self.total_end_date.isoformat() if self.total_end_date else None,
            "luggage_count": self.luggage_count,
            "need_arrival_transfer": self.need_arrival_transfer,
            "need_departure_transfer": self.need_departure_transfer,
            "trips": [t.to_dict() for t in self.trips],
        }