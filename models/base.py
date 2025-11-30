"""
Base Model 類別
提供通用的資料庫操作功能
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

DB_FILE = "demo_db.json"


class BaseModel:
    """基礎 Model 類別"""
    
    @staticmethod
    def get_db() -> Dict[str, Any]:
        """讀取本地 JSON 資料庫"""
        if not os.path.exists(DB_FILE):
            # 如果檔案不存在，創建一個空的結構
            BaseModel.save_db({
                "users": {},
                "orders": [],
                "scans": [],
                "drivers": {},
                "hotels": {}
            })
        
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果檔案損毀，回傳一個空的結構
            return {
                "users": {},
                "orders": [],
                "scans": [],
                "drivers": {},
                "hotels": {}
            }
    
    @staticmethod
    def save_db(data: Dict[str, Any]) -> None:
        """儲存資料到本地 JSON 資料庫"""
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def generate_timestamp() -> str:
        """生成當前時間戳"""
        return datetime.now().isoformat()
