import enum
from typing import Dict, Optional, Any, Tuple
from .base import BaseModel

class VehicleType(enum.Enum):
    CAR = "轎車"
    SUV = "休旅車"
    TRUCK = "小型貨車"
class VehicleCapacity(enum.Enum):
    CAR = 40
    SUV = 90
    TRUCK = 300

class Driver(BaseModel):
    def __init__(
        self,
        driver_id: Optional[int] = None,
        name: str = "",
        phone: str = "",
        vehicle_type: VehicleType = VehicleType.CAR,
        license_plate: str = "",
        current_location: Optional[Tuple[float, float]] = None,
        status: str = "available"
    ):
        self.driver_id = driver_id
        self.name = name
        self.phone = phone
        self.vehicle_type = vehicle_type
        self.license_plate = license_plate
        self.current_location = current_location
        self.status = status
    
    @classmethod
    def find_by_id(cls, driver_id: int) -> Optional['Driver']:
        """根據 ID 查詢司機"""
        db = cls.get_db()
        drivers = db.get("drivers", {})
        
        driver_data = drivers.get(str(driver_id))
        if driver_data:
            return cls(
                driver_id=driver_id,
                name=driver_data.get("name", ""),
                phone=driver_data.get("phone", ""),
                license_plate=driver_data.get("license_plate", ""),
                current_location=tuple(driver_data.get("current_location", [])) if driver_data.get("current_location") else None,
                status=driver_data.get("status", "available")
            )
        return None
    
    @classmethod
    def get_available_drivers(cls) -> list:
        """取得所有可用的司機"""
        db = cls.get_db()
        drivers = db.get("drivers", {})
        
        available = []
        for driver_id, driver_data in drivers.items():
            if driver_data.get("status") == "available":
                available.append(cls(
                    driver_id=int(driver_id),
                    name=driver_data.get("name", ""),
                    phone=driver_data.get("phone", ""),
                    license_plate=driver_data.get("license_plate", ""),
                    current_location=tuple(driver_data.get("current_location", [])) if driver_data.get("current_location") else None,
                    status=driver_data.get("status", "available")
                ))
        
        return available
    
    def save(self) -> bool:
        """儲存司機資料"""
        db = self.get_db()
        
        if "drivers" not in db:
            db["drivers"] = {}
        
        # 如果是新司機，生成 ID
        if self.driver_id is None:
            self.driver_id = len(db["drivers"]) + 1
        
        db["drivers"][str(self.driver_id)] = {
            "name": self.name,
            "phone": self.phone,
            "license_plate": self.license_plate,
            "current_location": list(self.current_location) if self.current_location else None,
            "status": self.status
        }
        
        self.save_db(db)
        return True
    
    def update_location(self, location: Tuple[float, float]) -> bool:
        """更新司機位置"""
        self.current_location = location
        return self.save()
    
    def update_status(self, status: str) -> bool:
        """更新司機狀態"""
        self.status = status
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "driver_id": self.driver_id,
            "name": self.name,
            "phone": self.phone,
            "license_plate": self.license_plate,
            "current_location": self.current_location,
            "status": self.status
        }
