"""
Order Controller
處理訂單相關的業務邏輯
"""
import logging
from typing import Dict, Any, Optional
from .base_controller import BaseController
from models.order import Order

logger = logging.getLogger(__name__)


class OrderController(BaseController):
    """訂單控制器"""
    
    def create_order(
        self,
        user_email: str,
        start_address: str,
        end_address: str,
        driver_name: str = "王小明",
        license_plate: str = "ABC-6666"
    ) -> Optional[Order]:
        """
        創建新訂單
        
        Args:
            user_email: 使用者 email
            start_address: 上車地點
            end_address: 下車地點
            driver_name: 司機名稱
            license_plate: 車牌號碼
            
        Returns:
            訂單物件，失敗則返回 None
        """
        try:
            order = Order(
                user_email=user_email,
                start_address=start_address,
                end_address=end_address,
                driver_name=driver_name,
                license_plate=license_plate,
                status="pending"
            )
            
            if order.save():
                logger.info(f"訂單已創建: {order.order_id}")
                return order
            else:
                logger.error("訂單儲存失敗")
                return None
        except Exception as e:
            logger.error(f"創建訂單時發生錯誤: {e}")
            return None
    
    def confirm_order(self) -> bool:
        """
        確認訂單
        從 app.booking_data 創建訂單
        
        Returns:
            是否成功
        """
        try:
            booking_data = self.app.booking_data
            
            if not booking_data:
                logger.warning("沒有預約資料可確認")
                return False
            
            user_email = self.page.session.get("email") or "demo@user.com"
            
            order = self.create_order(
                user_email=user_email,
                start_address=booking_data.get("start_address", ""),
                end_address=booking_data.get("end_address", ""),
                driver_name=booking_data.get("driver_name", "王小明"),
                license_plate=booking_data.get("license_plate", "ABC-6666")
            )
            
            if order:
                # 清空預約資料
                self.app.booking_data = {}
                logger.info(f"訂單確認成功: {order.order_id}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"確認訂單時發生錯誤: {e}")
            return False
    
    def cancel_order(self) -> bool:
        """
        取消訂單
        清空預約資料
        
        Returns:
            是否成功
        """
        try:
            self.app.booking_data = {}
            logger.info("訂單已取消")
            return True
        except Exception as e:
            logger.error(f"取消訂單時發生錯誤: {e}")
            return False
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        根據 ID 取得訂單
        
        Args:
            order_id: 訂單 ID
            
        Returns:
            訂單資料字典
        """
        order = Order.find_by_id(order_id)
        return order.to_dict() if order else None
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """
        更新訂單狀態
        
        Args:
            order_id: 訂單 ID
            status: 新狀態
            
        Returns:
            是否成功
        """
        try:
            order = Order.find_by_id(order_id)
            if order:
                order.status = status
                order.save()
                logger.info(f"訂單 {order_id} 狀態已更新為: {status}")
                return True
            else:
                logger.warning(f"找不到訂單: {order_id}")
                return False
        except Exception as e:
            logger.error(f"更新訂單狀態時發生錯誤: {e}")
            return False
