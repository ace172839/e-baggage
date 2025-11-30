"""
Hotel Model
處理飯店相關的資料操作
"""
from typing import Dict, Optional, Any
from .base import BaseModel


class Hotel(BaseModel):
    """飯店 Model"""
    
    def __init__(
        self,
        hotel_id: Optional[int] = None,
        name: str = "",
        baggage_count: int = 0,
        baggage_capacity: int = 180,
        not_arrived_customers: int = 0
    ):
        self.hotel_id = hotel_id
        self.name = name
        self.baggage_count = baggage_count
        self.baggage_capacity = baggage_capacity
        self.not_arrived_customers = not_arrived_customers
    
    @classmethod
    def find_by_id(cls, hotel_id: int) -> Optional['Hotel']:
        """根據 ID 查詢飯店"""
        db = cls.get_db()
        hotels = db.get("hotels", {})
        
        hotel_data = hotels.get(str(hotel_id))
        if hotel_data:
            return cls(
                hotel_id=hotel_id,
                name=hotel_data.get("name", ""),
                baggage_count=hotel_data.get("baggage_count", 0),
                baggage_capacity=hotel_data.get("baggage_capacity", 180),
                not_arrived_customers=hotel_data.get("not_arrived_customers", 0)
            )
        return None
    
    def save(self) -> bool:
        """儲存飯店資料"""
        db = self.get_db()
        
        if "hotels" not in db:
            db["hotels"] = {}
        
        # 如果是新飯店，生成 ID
        if self.hotel_id is None:
            self.hotel_id = len(db["hotels"]) + 1
        
        db["hotels"][str(self.hotel_id)] = {
            "name": self.name,
            "baggage_count": self.baggage_count,
            "baggage_capacity": self.baggage_capacity,
            "not_arrived_customers": self.not_arrived_customers
        }
        
        self.save_db(db)
        return True
    
    def add_baggage(self, count: int = 1) -> bool:
        """增加行李數量"""
        if self.baggage_count + count <= self.baggage_capacity:
            self.baggage_count += count
            return self.save()
        return False
    
    def remove_baggage(self, count: int = 1) -> bool:
        """減少行李數量"""
        if self.baggage_count - count >= 0:
            self.baggage_count -= count
            return self.save()
        return False
    
    def update_not_arrived(self, count: int) -> bool:
        """更新未抵達旅客數"""
        self.not_arrived_customers = count
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "baggage_count": self.baggage_count,
            "baggage_capacity": self.baggage_capacity,
            "not_arrived_customers": self.not_arrived_customers
        }
