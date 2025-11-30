"""
User Controller
處理使用者相關的業務邏輯
"""
import logging
from typing import Dict, Any
import flet as ft
from .base_controller import BaseController
from models.user import User
from models.order import Order

logger = logging.getLogger(__name__)


class UserController(BaseController):
    """使用者控制器"""
    
    def login(self, email: str, password: str, role: str) -> bool:
        """
        處理使用者登入
        
        Args:
            email: 使用者 email
            password: 密碼
            role: 角色 (user/driver/hotel)
            
        Returns:
            登入是否成功
        """
        # Debug 模式直接通過
        if self.app.mode == "debug":
            logger.warning("在偵錯模式下登入，已跳過驗證。")
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", email or "demo@user.com")
            return True
        
        # 正式模式驗證
        if User.authenticate(email, password):
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", email)
            logger.info(f"使用者 {email} 登入成功")
            return True
        else:
            logger.warning(f"使用者 {email} 登入失敗")
            return False
    
    def get_current_user(self) -> str:
        """取得當前登入的使用者 email"""
        return self.page.session.get("email") or ""
    
    def get_user_orders(self) -> list:
        """取得使用者的所有訂單"""
        user_email = self.get_current_user()
        if not user_email:
            return []
        
        orders = Order.find_by_user(user_email)
        return [order.to_dict() for order in orders]
    
    def handle_booking_instant(self, booking_data: Dict[str, Any]) -> bool:
        """
        處理即時預約
        
        Args:
            booking_data: 預約資料
            
        Returns:
            是否成功
        """
        try:
            # 儲存到 app 狀態
            self.app.booking_data = booking_data
            logger.info(f"即時預約資料已儲存: {booking_data}")
            return True
        except Exception as e:
            logger.error(f"處理即時預約時發生錯誤: {e}")
            return False
    
    def handle_booking_previous(self, booking_data: Dict[str, Any]) -> bool:
        """
        處理事先預約
        
        Args:
            booking_data: 預約資料
            
        Returns:
            是否成功
        """
        try:
            # 儲存到 app 狀態
            self.app.booking_data = booking_data
            logger.info(f"事先預約資料已儲存: {booking_data}")
            return True
        except Exception as e:
            logger.error(f"處理事先預約時發生錯誤: {e}")
            return False
    
    def handle_navigation(self, selected_index: int) -> str:
        """
        處理底部導航列的點擊
        
        Args:
            selected_index: 選擇的索引
            
        Returns:
            要導航的路由
        """
        # 隱藏搜尋欄
        if self.app.search_bar_ref.current:
            self.app.search_bar_ref.current.visible = False
        
        navigation_map = {
            0: "/app/user/more",
            1: "/app/user/instant_booking",
            2: "/app/user/dashboard",
            3: "/app/user/previous_booking",
            4: "/app/user/support"
        }
        
        route = navigation_map.get(selected_index, "/app/user/dashboard")
        logger.info(f"使用者導航到: {route}")
        return route
