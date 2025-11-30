"""
Order History Service
處理訂單歷史查詢
"""
import logging
import json
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

DEMO_DB_PATH = "demo_db.json"


class OrderHistoryService:
    """訂單歷史服務"""
    
    @staticmethod
    def get_all_orders() -> List[Dict[str, Any]]:
        """
        取得所有訂單
        
        Returns:
            訂單列表
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            orders = data.get('orders', [])
            logger.info(f"載入了 {len(orders)} 筆訂單")
            return orders
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入訂單時發生錯誤: {e}")
            return []
    
    @staticmethod
    def get_orders_sorted_by_date(reverse: bool = True) -> List[Dict[str, Any]]:
        """
        取得依日期排序的訂單
        
        Args:
            reverse: 是否倒序（最新的在前）
            
        Returns:
            排序後的訂單列表
        """
        orders = OrderHistoryService.get_all_orders()
        try:
            def get_order_date(order):
                # 嘗試獲取 date 欄位
                date_str = order.get('date')
                if date_str:
                    try:
                        return datetime.strptime(date_str, '%Y/%m/%d')
                    except ValueError:
                        pass
                
                # 嘗試獲取 created_at 欄位
                created_at = order.get('created_at')
                if created_at:
                    try:
                        return datetime.fromisoformat(created_at)
                    except ValueError:
                        pass
                
                return datetime.min

            orders.sort(key=get_order_date, reverse=reverse)
        except Exception as e:
            logger.error(f"排序訂單時發生錯誤: {e}")
        
        return orders
    
    @staticmethod
    def get_orders_by_user(user_email: str) -> List[Dict[str, Any]]:
        """
        取得特定使用者的訂單
        
        Args:
            user_email: 使用者 email
            
        Returns:
            該使用者的訂單列表
        """
        all_orders = OrderHistoryService.get_all_orders()
        user_orders = [
            order for order in all_orders
            if order.get('user_email') == user_email
        ]
        logger.info(f"使用者 {user_email} 有 {len(user_orders)} 筆訂單")
        return user_orders

    @staticmethod
    def update_order_status(order_id: str, new_status: str) -> bool:
        """
        更新指定訂單的狀態
        
        Args:
            order_id: 訂單編號 (支援 id 或 order_id 欄位)
            new_status: 新的狀態文字
        
        Returns:
            是否更新成功
        """
        try:
            with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"載入訂單資料時發生錯誤: {e}")
            return False

        orders = data.get('orders', [])
        updated = False
        timestamp = datetime.now().isoformat()

        for order in orders:
            identifier = order.get('id') or order.get('order_id')
            if identifier == order_id:
                order['status'] = new_status
                order['updated_at'] = timestamp
                if new_status == "cancelled":
                    order['cancelled_at'] = timestamp
                updated = True
                break

        if not updated:
            logger.warning(f"找不到訂單 {order_id}，無法更新狀態")
            return False

        try:
            with open(DEMO_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"訂單 {order_id} 狀態已更新為 {new_status}")
            return True
        except Exception as e:
            logger.error(f"寫入訂單狀態時發生錯誤: {e}")
            return False
