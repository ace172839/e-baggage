from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import List, Optional, Dict, Any


@dataclass
class LuggageItem:
    """單一尺寸的行李資訊"""

    size: int
    quantity: int = 1
    image_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "size": self.size,
            "quantity": self.quantity,
            "image_url": self.image_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LuggageItem":
        return cls(
            size=int(data.get("size", 24) or 24),
            quantity=int(data.get("quantity", 1) or 1),
            image_url=data.get("image_url"),
        )


@dataclass
class HotelStay:
    """Travel 中的一段住宿資訊"""

    hotel_name: str
    address: str
    lat: float
    lon: float
    check_in_date: date
    check_out_date: date
    is_locked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotel_name": self.hotel_name,
            "address": self.address,
            "lat": self.lat,
            "lon": self.lon,
            "check_in_date": self.check_in_date.isoformat(),
            "check_out_date": self.check_out_date.isoformat(),
            "is_locked": self.is_locked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HotelStay":
        return cls(
            hotel_name=data["hotel_name"],
            address=data["address"],
            lat=float(data["lat"]),
            lon=float(data["lon"]),
            check_in_date=date.fromisoformat(data["check_in_date"]),
            check_out_date=date.fromisoformat(data["check_out_date"]),
            is_locked=data.get("is_locked", False),
        )

    @property
    def nights(self) -> int:
        return max(0, (self.check_out_date - self.check_in_date).days)


@dataclass
class Trip:
    """司機端可見的最小運輸單位"""

    id: str
    start_time: datetime
    pickup_location: str
    pickup_lat: float
    pickup_lon: float
    dropoff_location: str
    dropoff_lat: float
    dropoff_lon: float
    status: str = "PENDING"
    vehicle_type: str = "sedan"
    price: float = 0.0
    parent_travel_id: Optional[str] = None
    end_time: Optional[datetime] = None
    luggage_items: List[LuggageItem] = field(default_factory=list)
    luggage_images: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "parent_travel_id": self.parent_travel_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "pickup_location": self.pickup_location,
            "pickup_lat": self.pickup_lat,
            "pickup_lon": self.pickup_lon,
            "dropoff_location": self.dropoff_location,
            "dropoff_lat": self.dropoff_lat,
            "dropoff_lon": self.dropoff_lon,
            "status": self.status,
            "vehicle_type": self.vehicle_type,
            "price": self.price,
            "luggage_items": [item.to_dict() for item in self.luggage_items],
            "luggage_images": list(self.luggage_images),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trip":
        return cls(
            id=data["id"],
            parent_travel_id=data.get("parent_travel_id"),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            pickup_location=data["pickup_location"],
            pickup_lat=float(data["pickup_lat"]),
            pickup_lon=float(data["pickup_lon"]),
            dropoff_location=data["dropoff_location"],
            dropoff_lat=float(data["dropoff_lat"]),
            dropoff_lon=float(data["dropoff_lon"]),
            status=data.get("status", "PENDING"),
            vehicle_type=data.get("vehicle_type", "sedan"),
            price=float(data.get("price", 0.0)),
            luggage_items=[LuggageItem.from_dict(item) for item in data.get("luggage_items", [])],
            luggage_images=data.get("luggage_images", []),
        )

    @property
    def luggage_count(self) -> int:
        return sum(item.quantity for item in self.luggage_items) or 0


@dataclass
class Travel:
    """Advance/預約旅程"""

    id: str
    total_start_date: date
    total_end_date: date
    status: str = "DRAFT"
    luggage_count: int = 0
    arrival_transfer: bool = False
    arrival_location: str = ""
    arrival_lat: Optional[float] = None
    arrival_lon: Optional[float] = None
    arrival_time: Optional[time] = None
    departure_transfer: bool = False
    departure_location: str = ""
    departure_lat: Optional[float] = None
    departure_lon: Optional[float] = None
    departure_time: Optional[time] = None
    default_checkout_time: Optional[time] = None
    luggage_items: List[LuggageItem] = field(default_factory=list)
    hotels: List[HotelStay] = field(default_factory=list)
    trips: List[Trip] = field(default_factory=list)
    total_price: float = 0.0
    user_email: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "total_start_date": self.total_start_date.isoformat(),
            "total_end_date": self.total_end_date.isoformat(),
            "status": self.status,
            "luggage_count": self.luggage_count,
            "arrival_transfer": self.arrival_transfer,
            "arrival_location": self.arrival_location,
            "arrival_lat": self.arrival_lat,
            "arrival_lon": self.arrival_lon,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "departure_transfer": self.departure_transfer,
            "departure_location": self.departure_location,
            "departure_lat": self.departure_lat,
            "departure_lon": self.departure_lon,
            "departure_time": self.departure_time.isoformat() if self.departure_time else None,
            "default_checkout_time": self.default_checkout_time.isoformat() if self.default_checkout_time else None,
            "luggage_items": [item.to_dict() for item in self.luggage_items],
            "hotels": [hotel.to_dict() for hotel in self.hotels],
            "trips": [trip.to_dict() for trip in self.trips],
            "total_price": self.total_price,
            "user_email": self.user_email,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Travel":
        return cls(
            id=data["id"],
            total_start_date=date.fromisoformat(data["total_start_date"]),
            total_end_date=date.fromisoformat(data["total_end_date"]),
            status=data.get("status", "DRAFT"),
            luggage_count=int(data.get("luggage_count", 0) or 0),
            arrival_transfer=data.get("arrival_transfer", False),
            arrival_location=data.get("arrival_location", ""),
            arrival_lat=data.get("arrival_lat"),
            arrival_lon=data.get("arrival_lon"),
            arrival_time=time.fromisoformat(data["arrival_time"]) if data.get("arrival_time") else None,
            departure_transfer=data.get("departure_transfer", False),
            departure_location=data.get("departure_location", ""),
            departure_lat=data.get("departure_lat"),
            departure_lon=data.get("departure_lon"),
            departure_time=time.fromisoformat(data["departure_time"]) if data.get("departure_time") else None,
            default_checkout_time=time.fromisoformat(data["default_checkout_time"]) if data.get("default_checkout_time") else None,
            luggage_items=[LuggageItem.from_dict(item) for item in data.get("luggage_items", [])],
            hotels=[HotelStay.from_dict(item) for item in data.get("hotels", [])],
            trips=[Trip.from_dict(item) for item in data.get("trips", [])],
            total_price=float(data.get("total_price", 0.0)),
            user_email=data.get("user_email"),
        )

    @property
    def title(self) -> str:
        start = self.total_start_date.strftime("%m/%d")
        end = self.total_end_date.strftime("%m/%d")
        primary_hotel = self.hotels[0].hotel_name if self.hotels else "旅程"
        return f"{start}-{end} {primary_hotel}"
