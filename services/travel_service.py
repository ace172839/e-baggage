"""Travel / Trip services: validation, generation, pricing, persistence."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, time, timedelta
from typing import List, Tuple, Dict, Any, Optional

from db_helpers import get_db, save_db
from models.trip import Travel, Trip, HotelStay, LuggageItem
from services.location_service import LocationService

logger = logging.getLogger(__name__)


class TravelService:
    """Business logic for converting Travel plans into Trips."""

    DEFAULT_ARRIVAL_TIME = time(14, 0)
    DEFAULT_CHECKOUT_TIME = time(11, 0)
    DEFAULT_DEPARTURE_TIME = time(12, 0)
    BASE_FARE = 30.0
    DISTANCE_RATE = 30.0  # 每公里 30 元

    @staticmethod
    def _ensure_order_list(db: Dict[str, Any]) -> List[Dict[str, Any]]:
        orders = db.get("orders")
        if orders is None:
            orders = []
            db["orders"] = orders
        return orders

    @classmethod
    def validate_hotels(cls, travel: Travel) -> None:
        if not travel.hotels:
            raise ValueError("請至少新增一段住宿")

        sorted_hotels = sorted(travel.hotels, key=lambda h: h.check_in_date)
        travel.hotels = sorted_hotels

        if sorted_hotels[0].check_in_date != travel.total_start_date:
            raise ValueError("第一段住宿必須從旅程開始日入住")
        if sorted_hotels[-1].check_out_date != travel.total_end_date:
            raise ValueError("最後一段住宿必須涵蓋旅程結束日")

        for idx in range(len(sorted_hotels) - 1):
            if sorted_hotels[idx].check_out_date != sorted_hotels[idx + 1].check_in_date:
                raise ValueError("住宿日期必須無縫銜接 (前段退房 = 下一段入住)")

    @classmethod
    def _estimate_end_time(cls, start_time: datetime, distance_km: float) -> datetime:
        avg_speed_kmh = 35.0
        duration_hours = max(distance_km / avg_speed_kmh, 0.5)
        return start_time + timedelta(hours=duration_hours)

    @classmethod
    def _luggage_fee(cls, items: List[LuggageItem]) -> float:
        total = 0.0
        for item in items:
            size = int(item.size)
            if size <= 20:
                rate = 50
            elif size <= 24:
                rate = 80
            else:
                rate = 100
            total += rate * max(item.quantity, 1)
        return total

    @classmethod
    def _calculate_trip_price(
        cls,
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
        luggage_items: List[LuggageItem],
    ) -> Tuple[float, float]:
        distance_km = LocationService.calculate_distance(
            pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
        )
        fare = cls.BASE_FARE + distance_km * cls.DISTANCE_RATE + cls._luggage_fee(luggage_items)
        return round(fare, 2), distance_km

    @classmethod
    def _build_trip(
        cls,
        parent_id: Optional[str],
        start_time: datetime,
        pickup: Tuple[str, float, float],
        dropoff: Tuple[str, float, float],
        luggage_items: List[LuggageItem],
    ) -> Trip:
        pickup_location, pick_lat, pick_lon = pickup
        dropoff_location, drop_lat, drop_lon = dropoff
        price, distance_km = cls._calculate_trip_price(pick_lat, pick_lon, drop_lat, drop_lon, luggage_items)
        trip = Trip(
            id=str(uuid.uuid4()),
            parent_travel_id=parent_id,
            start_time=start_time,
            end_time=cls._estimate_end_time(start_time, distance_km),
            pickup_location=pickup_location,
            pickup_lat=pick_lat,
            pickup_lon=pick_lon,
            dropoff_location=dropoff_location,
            dropoff_lat=drop_lat,
            dropoff_lon=drop_lon,
            price=price,
            luggage_items=luggage_items,
        )
        return trip

    @classmethod
    def build_manual_trip(
        cls,
        start_time: datetime,
        pickup: Tuple[str, float, float],
        dropoff: Tuple[str, float, float],
        luggage_items: List[LuggageItem],
        parent_id: Optional[str] = None,
    ) -> Trip:
        """提供即時訂單等情境建立單一 Trip"""
        return cls._build_trip(parent_id, start_time, pickup, dropoff, luggage_items)

    @classmethod
    def generate_trips(cls, travel: Travel) -> List[Trip]:
        cls.validate_hotels(travel)
        trips: List[Trip] = []

        luggage_items = travel.luggage_items or [LuggageItem(size=24, quantity=max(travel.luggage_count, 1))]
        first_hotel = travel.hotels[0]
        last_hotel = travel.hotels[-1]

        if travel.arrival_transfer and travel.arrival_location and travel.arrival_lat and travel.arrival_lon:
            start_dt = datetime.combine(travel.total_start_date, travel.arrival_time or cls.DEFAULT_ARRIVAL_TIME)
            trips.append(
                cls._build_trip(
                    travel.id,
                    start_dt,
                    (travel.arrival_location, travel.arrival_lat, travel.arrival_lon),
                    (first_hotel.hotel_name, first_hotel.lat, first_hotel.lon),
                    luggage_items,
                )
            )

        default_checkout = travel.default_checkout_time or cls.DEFAULT_CHECKOUT_TIME
        for idx in range(len(travel.hotels) - 1):
            current_hotel = travel.hotels[idx]
            next_hotel = travel.hotels[idx + 1]
            start_dt = datetime.combine(current_hotel.check_out_date, default_checkout)
            trips.append(
                cls._build_trip(
                    travel.id,
                    start_dt,
                    (current_hotel.hotel_name, current_hotel.lat, current_hotel.lon),
                    (next_hotel.hotel_name, next_hotel.lat, next_hotel.lon),
                    luggage_items,
                )
            )

        if travel.departure_transfer and travel.departure_location and travel.departure_lat and travel.departure_lon:
            start_dt = datetime.combine(travel.total_end_date, travel.departure_time or cls.DEFAULT_DEPARTURE_TIME)
            trips.append(
                cls._build_trip(
                    travel.id,
                    start_dt,
                    (last_hotel.hotel_name, last_hotel.lat, last_hotel.lon),
                    (travel.departure_location, travel.departure_lat, travel.departure_lon),
                    luggage_items,
                )
            )

        travel.trips = trips
        travel.total_price = round(sum(trip.price for trip in trips), 2)
        return trips

    @classmethod
    def _serialize_trip(cls, trip: Trip, user_email: str, order_type: str = "trip") -> Dict[str, Any]:
        payload = trip.to_dict()
        payload.update(
            {
                "order_type": order_type,
                "user_email": user_email,
                "created_at": datetime.now().isoformat(),
            }
        )
        return payload

    @classmethod
    def _serialize_travel(cls, travel: Travel, user_email: str) -> Dict[str, Any]:
        payload = travel.to_dict()
        payload.update(
            {
                "order_type": "travel",
                "user_email": user_email,
                "created_at": datetime.now().isoformat(),
                "trip_ids": [trip.id for trip in travel.trips],
            }
        )
        return payload

    @classmethod
    def save_travel_with_trips(cls, travel: Travel, user_email: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        db = get_db()
        orders = cls._ensure_order_list(db)

        travel_entry = cls._serialize_travel(travel, user_email)
        trip_entries = [cls._serialize_trip(trip, user_email, "travel_trip") for trip in travel.trips]

        orders.append(travel_entry)
        orders.extend(trip_entries)

        orders.sort(key=lambda o: o.get("created_at", o.get("start_time", "")), reverse=True)
        save_db(db)
        logger.info("Travel %s 已儲存 (%d 個 trips)", travel.id, len(travel.trips))
        return travel_entry, trip_entries

    @classmethod
    def save_single_trip(
        cls,
        trip: Trip,
        user_email: str,
        order_type: str = "trip",
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        db = get_db()
        orders = cls._ensure_order_list(db)
        entry = cls._serialize_trip(trip, user_email, order_type)
        if extra_fields:
            entry.update(extra_fields)
        orders.append(entry)
        orders.sort(key=lambda o: o.get("start_time", o.get("created_at", "")), reverse=True)
        save_db(db)
        logger.info("Trip %s 已儲存", trip.id)
        return entry
