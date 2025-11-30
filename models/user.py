"""
User Model
處理使用者相關的資料操作
"""
from typing import Dict, Optional, Any
from .base import BaseModel


class User(BaseModel):
    """使用者 Model"""
    
    def __init__(self, email: str, username: str = "", password: str = ""):
        self.email = email
        self.username = username
        self.password = password
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """根據 email 查詢使用者"""
        db = cls.get_db() or {}
        user_data = db.get("users", {}).get(email)
        
        if user_data:
            return cls(
                email=email,
                username=user_data.get("username", ""),
                password=user_data.get("password", "")
            )
        return None
    
    @classmethod
    def authenticate(cls, email: str, password: str) -> bool:
        """驗證使用者登入"""
        user = cls.find_by_email(email)
        if user and user.password == password:
            return True
        return False
    
    def save(self) -> bool:
        """儲存使用者資料"""
        db = self.get_db()
        
        if "users" not in db:
            db["users"] = {}
        
        db["users"][self.email] = {
            "username": self.username,
            "password": self.password,
            "created_at": self.generate_timestamp()
        }
        
        self.save_db(db)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "email": self.email,
            "username": self.username
        }
