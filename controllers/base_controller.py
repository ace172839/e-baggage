"""
Base Controller 類別
提供控制器的基礎功能
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App


class BaseController:
    """基礎 Controller 類別"""
    
    def __init__(self, app_instance: 'App'):
        """
        初始化控制器
        
        Args:
            app_instance: App 實例，用於訪問頁面和狀態
        """
        self.app = app_instance
        self.page = app_instance.page
