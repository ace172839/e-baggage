"""
Driver Controller
處理司機相關的業務邏輯
"""
import logging
from typing import Tuple, Optional
from .base_controller import BaseController
from models.driver import Driver

logger = logging.getLogger(__name__)


class DriverController(BaseController):
    """司機控制器"""
    
    def get_current_driver(self) -> Optional[Driver]:
        """
        取得當前登入的司機資訊
        
        Returns:
            Driver 物件
        """
        # 在 demo 中，我們使用固定的司機 ID
        driver = Driver.find_by_id(1)
        
        # 如果不存在，創建預設司機
        if not driver:
            driver = Driver(
                driver_id=1,
                name="王小明",
                phone="0912345678",
                license_plate="ABC-6666",
                current_location=(25.0374, 121.5635),  # 台北市政府
                status="available"
            )
            driver.save()
        
        return driver
    
    def update_location(self, location: Tuple[float, float]) -> bool:
        """
        更新司機位置
        
        Args:
            location: (緯度, 經度)
            
        Returns:
            是否成功
        """
        try:
            driver = self.get_current_driver()
            if driver:
                driver.update_location(location)
                logger.info(f"司機位置已更新: {location}")
                return True
            return False
        except Exception as e:
            logger.error(f"更新司機位置時發生錯誤: {e}")
            return False
    
    def update_status(self, status: str) -> bool:
        """
        更新司機狀態
        
        Args:
            status: 狀態 (available/busy/offline)
            
        Returns:
            是否成功
        """
        try:
            driver = self.get_current_driver()
            if driver:
                driver.update_status(status)
                logger.info(f"司機狀態已更新: {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"更新司機狀態時發生錯誤: {e}")
            return False
    
    def get_available_drivers(self) -> list:
        """
        取得所有可用的司機
        
        Returns:
            司機列表
        """
        drivers = Driver.get_available_drivers()
        return [driver.to_dict() for driver in drivers]
    
    def handle_navigation(self, route: str) -> str:
        """
        處理司機導航
        
        Args:
            route: 目標路由
            
        Returns:
            路由
        """
        logger.info(f"司機導航到: {route}")
        return route
