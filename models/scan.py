"""
Scan Model
處理掃描記錄相關的資料操作
"""
from typing import Dict, List, Optional, Any
from .base import BaseModel


class Scan(BaseModel):
    """掃描記錄 Model"""
    
    def __init__(
        self,
        scan_id: Optional[int] = None,
        user_email: str = "",
        role: str = "user",
        scan_result: str = "",
        timestamp: Optional[str] = None
    ):
        self.scan_id = scan_id
        self.user_email = user_email
        self.role = role
        self.scan_result = scan_result
        self.timestamp = timestamp or self.generate_timestamp()
    
    @classmethod
    def find_by_user(cls, user_email: str) -> List['Scan']:
        """查詢使用者的所有掃描記錄"""
        db = cls.get_db()
        scans = db.get("scans", [])
        
        user_scans = []
        for scan_data in scans:
            if scan_data.get("user_email") == user_email:
                user_scans.append(cls(
                    scan_id=scan_data.get("id"),
                    user_email=scan_data.get("user_email", ""),
                    role=scan_data.get("role", "user"),
                    scan_result=scan_data.get("scan_result", ""),
                    timestamp=scan_data.get("timestamp", "")
                ))
        
        return user_scans
    
    def save(self) -> bool:
        """儲存掃描記錄"""
        db = self.get_db()
        
        if "scans" not in db:
            db["scans"] = []
        
        # 如果是新記錄，生成 ID
        if self.scan_id is None:
            self.scan_id = len(db["scans"]) + 1
        
        scan_data = {
            "id": self.scan_id,
            "user_email": self.user_email,
            "role": self.role,
            "scan_result": self.scan_result,
            "timestamp": self.timestamp
        }
        
        db["scans"].append(scan_data)
        self.save_db(db)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "scan_id": self.scan_id,
            "user_email": self.user_email,
            "role": self.role,
            "scan_result": self.scan_result,
            "timestamp": self.timestamp
        }
