"""
Order Model
處理訂單相關的資料操作
"""
from typing import Dict, List, Optional, Any
from .base import BaseModel


class Order(BaseModel):
    """訂單 Model"""
    
    def __init__(
        self,
        order_id: Optional[int] = None,
        user_email: str = "",
        start_date: str = "",
        end_date: str = "",
        start_address: str = "",
        end_address: str = "",
        driver_email: str = "",
        status: str = "pending",
        order_time: Optional[str] = None
    ):
        self.order_id = order_id
        self.user_email = user_email
        self.start_date = start_date
        self.end_date = end_date
        self.start_address = start_address
        self.end_address = end_address
        self.driver_email = driver_email
        self.status = status
        self.order_time = order_time or self.generate_timestamp()
    
    @classmethod
    def find_by_id(cls, order_id: int) -> Optional['Order']:
        """根據 ID 查詢訂單"""
        db = cls.get_db()
        orders = db.get("orders", [])
        
        for order_data in orders:
            if order_data.get("id") == order_id:
                return cls(
                    order_id=order_data.get("id"),
                    user_email=order_data.get("user_email", ""),
                    start_date=order_data.get("start_date", ""),
                    end_date=order_data.get("end_date", ""),
                    start_address=order_data.get("start_address", ""),
                    end_address=order_data.get("end_address", ""),
                    driver_email=order_data.get("driver_email", ""),
                    status=order_data.get("status", "pending"),
                    order_time=order_data.get("order_time", "")
                )
        return None
    
    @classmethod
    def find_by_user(cls, user_email: str) -> List['Order']:
        """查詢使用者的所有訂單"""
        db = cls.get_db()
        orders = db.get("orders", [])
        
        user_orders = []
        for order_data in orders:
            if order_data.get("user_email") == user_email:
                user_orders.append(cls(
                    order_id=order_data.get("id"),
                    user_email=order_data.get("user_email", ""),
                    start_date=order_data.get("start_date", ""),
                    end_date=order_data.get("end_date", ""),
                    start_address=order_data.get("start_address", ""),
                    end_address=order_data.get("end_address", ""),
                    driver_email=order_data.get("driver_email", ""),
                    status=order_data.get("status", "pending"),
                    order_time=order_data.get("order_time", "")
                ))
        
        return user_orders
    
    def save(self) -> bool:
        """儲存訂單"""
        db = self.get_db()
        
        if "orders" not in db:
            db["orders"] = []
        
        # 如果是新訂單，生成 ID
        if self.order_id is None:
            self.order_id = len(db["orders"]) + 1
        
        order_data = {
            "id": self.order_id,
            "user_email": self.user_email,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_address": self.start_address,
            "end_address": self.end_address,
            "driver_email": self.driver_email,
            "status": self.status,
            "order_time": self.order_time
        }
        
        # 檢查是否已存在，如果存在則更新
        updated = False
        for i, order in enumerate(db["orders"]):
            if order.get("id") == self.order_id:
                db["orders"][i] = order_data
                updated = True
                break
        
        if not updated:
            db["orders"].append(order_data)
        
        self.save_db(db)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "id": self.order_id,
            "user_email": self.user_email,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_address": self.start_address,
            "end_address": self.end_address,
            "driver_email": self.driver_email,
            "status": self.status,
            "order_time": self.order_time
        }
