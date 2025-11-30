"""
Map Utility Service
地圖相關的工具函數
"""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class MapUtilService:
    """地圖工具服務"""
    
    @staticmethod
    def calculate_zoom_level(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> int:
        """
        根據兩點座標計算合適的縮放等級
        
        Args:
            lat1: 第一點緯度
            lon1: 第一點經度
            lat2: 第二點緯度
            lon2: 第二點經度
            
        Returns:
            縮放等級 (8-17)
        """
        max_lat_diff = abs(lat1 - lat2)
        max_lon_diff = abs(lon1 - lon2)
        
        max_diff = max(max_lat_diff, max_lon_diff)
        
        if max_diff < 0.001:  # 非常接近的點
            return 17
        elif max_diff < 0.005:
            return 16
        elif max_diff < 0.01:
            return 15
        elif max_diff < 0.05:
            return 14
        elif max_diff < 0.1:
            return 13
        elif max_diff < 0.2:
            return 12
        elif max_diff < 0.5:
            return 11
        elif max_diff < 1:
            return 10
        else:
            return 8  # 非常遙遠的點
    
    @staticmethod
    def calculate_center(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> Tuple[float, float]:
        """
        計算兩點的中心座標
        
        Args:
            lat1: 第一點緯度
            lon1: 第一點經度
            lat2: 第二點緯度
            lon2: 第二點經度
            
        Returns:
            中心座標 (緯度, 經度)
        """
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        
        logger.debug(f"計算中心點: ({center_lat}, {center_lon})")
        return (center_lat, center_lon)
