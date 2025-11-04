import json
import os
from datetime import datetime

DB_FILE = "demo_db.json"

def get_db():
    """讀取本地 JSON 資料庫"""
    if not os.path.exists(DB_FILE):
        # 如果檔案不存在，創建一個空的結構
        save_db({"users": {}, "orders": [], "scans": []})
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 如果檔案損毀，回傳一個空的結構
        return {"users": {}, "orders": [], "scans": []}

def save_db(data):
    """儲存資料到本地 JSON 資料庫"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_order_to_history(trip_data, user_email):
    """
    專門用來儲存訂單的函式
    (在 order.py 抵達時呼叫)
    """
    db = get_db()
    
    new_order = {
        "id": len(db["orders"]) + 1,
        "user_email": user_email,
        "start_address": trip_data["start_address"],
        "end_address": trip_data["end_address"],
        "driver": trip_data["driver_name"],
        "license_plate": trip_data["license_plate"],
        "timestamp": datetime.now().isoformat() # 紀錄時間
    }
    
    db["orders"].append(new_order)
    save_db(db)

def save_scan_to_history(user_email, role, scan_result_text):
    """
    專門用來儲存 AI 掃描結果的函式
    """
    db = get_db()
    
    new_scan = {
        "id": len(db["scans"]) + 1,
        "user_email": user_email,
        "scanned_by": role, # "user" or "hotel"
        "result": scan_result_text,
        "timestamp": datetime.now().isoformat()
    }
    
    db["scans"].append(new_scan)
    save_db(db)