"""
Date Service
處理日期格式化、日期計算等業務邏輯
"""
import datetime
import logging

logger = logging.getLogger(__name__)


class DateService:
    """日期處理服務"""
    
    # 統一的日期格式
    DATE_FORMAT = "%Y/%m/%d"
    DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
    TIME_FORMAT = "%H:%M"
    
    @staticmethod
    def format_date(date_obj: datetime.datetime, format_str: str = None) -> str:
        """
        格式化日期對象為字串
        
        Args:
            date_obj: datetime 對象
            format_str: 格式字串，默認為 DATE_FORMAT
            
        Returns:
            str: 格式化後的日期字串
        """
        if format_str is None:
            format_str = DateService.DATE_FORMAT
        
        try:
            return date_obj.strftime(format_str)
        except Exception as e:
            logger.error(f"日期格式化失敗: {e}")
            return ""
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = None) -> datetime.datetime:
        """
        解析日期字串為 datetime 對象
        
        Args:
            date_str: 日期字串
            format_str: 格式字串，默認為 DATE_FORMAT
            
        Returns:
            datetime.datetime: 解析後的 datetime 對象，解析失敗返回 None
        """
        if format_str is None:
            format_str = DateService.DATE_FORMAT
        
        try:
            return datetime.datetime.strptime(date_str, format_str)
        except Exception as e:
            logger.error(f"日期解析失敗: {e}")
            return None
    
    @staticmethod
    def get_current_date_str(format_str: str = None) -> str:
        """
        獲取當前日期字串
        
        Args:
            format_str: 格式字串，默認為 DATE_FORMAT
            
        Returns:
            str: 當前日期字串
        """
        if format_str is None:
            format_str = DateService.DATE_FORMAT
        
        return datetime.datetime.now().strftime(format_str)
    
    @staticmethod
    def get_current_datetime() -> datetime.datetime:
        """
        獲取當前日期時間
        
        Returns:
            datetime.datetime: 當前日期時間
        """
        return datetime.datetime.now()
    
    @staticmethod
    def calculate_days_between(date1: datetime.datetime, date2: datetime.datetime) -> int:
        """
        計算兩個日期之間的天數
        
        Args:
            date1: 開始日期
            date2: 結束日期
            
        Returns:
            int: 天數差異
        """
        try:
            delta = date2 - date1
            return abs(delta.days)
        except Exception as e:
            logger.error(f"計算日期差異失敗: {e}")
            return 0
    
    @staticmethod
    def is_date_in_future(date_obj: datetime.datetime) -> bool:
        """
        檢查日期是否在未來
        
        Args:
            date_obj: 待檢查的日期
            
        Returns:
            bool: 是否在未來
        """
        return date_obj > datetime.datetime.now()
    
    @staticmethod
    def get_min_date_for_picker() -> datetime.datetime:
        """
        獲取日期選擇器的最小日期（今天）
        
        Returns:
            datetime.datetime: 今天的日期
        """
        return datetime.datetime.now()
    
    @staticmethod
    def validate_date_range(start_date: datetime.datetime, end_date: datetime.datetime) -> tuple[bool, str]:
        """
        驗證日期範圍是否有效
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        if not start_date or not end_date:
            return False, "日期不能為空"
        
        if end_date < start_date:
            return False, "結束日期不能早於開始日期"
        
        if start_date < datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            return False, "開始日期不能早於今天"
        
        return True, ""
