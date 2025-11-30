"""
Booking Service
處理預約相關的業務邏輯
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

DEMO_DB_PATH = "demo_db.json"


class BookingService:
    """預約服務"""
    
    @staticmethod
    def load_hotels() -> List[Dict[str, Any]]:
        """
        從資料庫載入所有飯店資訊 (用於搜尋)
        
        Returns:
            所有飯店列表
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            hotels = db_data.get('hotels', [])
            logger.info(f"載入了 {len(hotels)} 間飯店")
            return hotels
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入飯店時發生錯誤: {e}")
            return []

    @staticmethod
    def load_partner_hotels() -> List[Dict[str, Any]]:
        """
        從資料庫載入合作飯店資訊 (用於地圖顯示)
        
        Returns:
            合作飯店列表
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            hotels = db_data.get('partner_hotels', [])
            logger.info(f"載入了 {len(hotels)} 間合作飯店")
            return hotels
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入合作飯店時發生錯誤: {e}")
            return []
    
    @staticmethod
    def save_order(order_data: Dict[str, Any]) -> bool:
        """
        儲存訂單到資料庫
        
        Args:
            order_data: 訂單資料
            
        Returns:
            是否成功
        """
        try:
            # 讀取現有資料
            try:
                with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                    db_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                db_data = {
                    "users": {},
                    "orders": [],
                    "scans": [],
                    "hotels": []
                }
            
            orders = db_data.get('orders', [])
            orders.append(order_data)
            
            # 按日期降序排序
            def get_order_date(order):
                # 嘗試獲取 date 欄位
                date_str = order.get('date')
                if date_str:
                    try:
                        return datetime.strptime(date_str, '%Y/%m/%d')
                    except ValueError:
                        pass
                
                # 嘗試獲取 created_at 欄位 (針對不同格式的訂單)
                created_at = order.get('created_at')
                if created_at:
                    try:
                        # 處理 ISO 格式
                        return datetime.fromisoformat(created_at)
                    except ValueError:
                        pass
                
                return datetime.min

            orders.sort(key=get_order_date, reverse=True)
            db_data['orders'] = orders
            
            # 寫入檔案
            with open(DEMO_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"訂單 {order_data.get('id', 'unknown')} 已儲存")
            return True
        except Exception as e:
            logger.error(f"儲存訂單時發生錯誤: {e}")
            return False
    
    @staticmethod
    def generate_order_id() -> str:
        """
        生成新的訂單 ID
        
        Returns:
            訂單 ID (格式: O001, O002, ...)
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            existing_orders = db_data.get('orders', [])
            max_id = 0
            
            for order in existing_orders:
                order_id = order.get('id', '')
                if order_id.startswith('O'):
                    try:
                        num = int(order_id[1:])
                        if num > max_id:
                            max_id = num
                    except ValueError:
                        continue
            
            new_order_id = f"O{max_id + 1:03d}"
            logger.info(f"生成新訂單 ID: {new_order_id}")
            return new_order_id
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("資料庫不存在，使用預設訂單 ID: O001")
            return "O001"
    
    @staticmethod
    def create_order_data(
        pickup: str,
        dropoff: str,
        luggages: str,
        amount: str = "250"
    ) -> Dict[str, Any]:
        """
        創建訂單資料
        
        Args:
            pickup: 上車地點
            dropoff: 下車地點
            luggages: 行李數量
            amount: 金額
            
        Returns:
            訂單資料字典
        """
        order_id = BookingService.generate_order_id()
        
        return {
            "id": order_id,
            "date": datetime.now().strftime("%Y/%m/%d"),
            "pickup": pickup or "台北101",
            "dropof": dropoff or "圓山大飯店",
            "amount": amount or "250",
            "luggages": luggages or "0"
        }
    
    @staticmethod
    def load_recommendations() -> List[Dict[str, Any]]:
        """
        載入推薦資訊（AI 助手使用）
        
        Returns:
            推薦列表
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            recommendations = db_data.get('recommendations', [])
            logger.info(f"載入了 {len(recommendations)} 條推薦")
            return recommendations
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入推薦時發生錯誤: {e}")
            return []
