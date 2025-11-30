"""
Hotel Controller
處理飯店相關的業務邏輯
"""
import logging
from typing import Optional
from .base_controller import BaseController
from models.hotel import Hotel
from models.scan import Scan

logger = logging.getLogger(__name__)


class HotelController(BaseController):
    """飯店控制器"""
    
    def get_current_hotel(self) -> Optional[Hotel]:
        """
        取得當前飯店資訊
        
        Returns:
            Hotel 物件
        """
        # 在 demo 中，我們使用固定的飯店 ID
        hotel = Hotel.find_by_id(1)
        
        # 如果不存在，創建預設飯店
        if not hotel:
            hotel = Hotel(
                hotel_id=1,
                name="圓山大飯店",
                baggage_count=63,
                baggage_capacity=180,
                not_arrived_customers=27
            )
            hotel.save()
        
        return hotel
    
    def add_baggage(self, count: int = 1) -> bool:
        """
        增加行李數量
        
        Args:
            count: 數量
            
        Returns:
            是否成功
        """
        try:
            hotel = self.get_current_hotel()
            if hotel:
                result = hotel.add_baggage(count)
                if result:
                    # 更新 app 狀態
                    self.app.hotel_baggages = hotel.baggage_count
                    logger.info(f"行李數量已增加 {count}，目前: {hotel.baggage_count}")
                    return True
                else:
                    logger.warning("行李容量已滿")
                    return False
            return False
        except Exception as e:
            logger.error(f"增加行李數量時發生錯誤: {e}")
            return False
    
    def remove_baggage(self, count: int = 1) -> bool:
        """
        減少行李數量
        
        Args:
            count: 數量
            
        Returns:
            是否成功
        """
        try:
            hotel = self.get_current_hotel()
            if hotel:
                result = hotel.remove_baggage(count)
                if result:
                    # 更新 app 狀態
                    self.app.hotel_baggages = hotel.baggage_count
                    logger.info(f"行李數量已減少 {count}，目前: {hotel.baggage_count}")
                    return True
                else:
                    logger.warning("行李數量不足")
                    return False
            return False
        except Exception as e:
            logger.error(f"減少行李數量時發生錯誤: {e}")
            return False
    
    def update_not_arrived(self, count: int) -> bool:
        """
        更新未抵達旅客數
        
        Args:
            count: 數量
            
        Returns:
            是否成功
        """
        try:
            hotel = self.get_current_hotel()
            if hotel:
                hotel.update_not_arrived(count)
                # 更新 app 狀態
                self.app.hotel_not_arrived_customer = count
                logger.info(f"未抵達旅客數已更新: {count}")
                return True
            return False
        except Exception as e:
            logger.error(f"更新未抵達旅客數時發生錯誤: {e}")
            return False
    
    def save_scan_result(self, scan_result: str) -> bool:
        """
        儲存掃描結果
        
        Args:
            scan_result: 掃描結果文字
            
        Returns:
            是否成功
        """
        try:
            user_email = self.page.session.get("email") or "hotel@demo.com"
            
            scan = Scan(
                user_email=user_email,
                role="hotel",
                scan_result=scan_result
            )
            
            if scan.save():
                logger.info("掃描結果已儲存")
                return True
            return False
        except Exception as e:
            logger.error(f"儲存掃描結果時發生錯誤: {e}")
            return False
    
    def handle_navigation(self, selected_index: int) -> str:
        """
        處理飯店導航
        
        Args:
            selected_index: 選擇的索引
            
        Returns:
            要導航的路由
        """
        navigation_map = {
            0: "/app/hotel",
            1: "/app/hotel/scan",
            2: "/app/hotel",
            3: "/app/hotel",
            4: "/app/hotel"
        }
        
        route = navigation_map.get(selected_index, "/app/hotel")
        logger.info(f"飯店導航到: {route}")
        return route
