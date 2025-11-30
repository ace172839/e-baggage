"""
Location Service
處理地理位置、地址搜索、地圖相關業務邏輯
"""
import logging
import time
from typing import Callable, Optional, Tuple

from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

try:
    from requests.exceptions import ConnectionError as RequestsConnectionError
    from requests.exceptions import ReadTimeout
except ImportError:  # 允許在未安裝 requests 時仍可載入模組
    RequestsConnectionError = ReadTimeout = Exception


RETRYABLE_EXCEPTIONS = (
    GeocoderTimedOut,
    GeocoderUnavailable,
    ReadTimeout,
    RequestsConnectionError,
    TimeoutError,
    ConnectionError,
)

logger = logging.getLogger(__name__)


class LocationService:
    """地理位置服務"""
    
    def __init__(
        self,
        user_agent: str = "e-baggage-app",
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        """
        初始化位置服務
        
        Args:
            user_agent: Nominatim 使用者代理字串
            timeout: 單次呼叫逾時秒數
            max_retries: 逾時時最多重試次數
            retry_delay: 每次重試前的延遲秒數基準
        """
        self.timeout = timeout
        self.max_retries = max(1, max_retries)
        self.retry_delay = max(0.1, retry_delay)
        
        try:
            self.geolocator = Nominatim(user_agent=user_agent, timeout=self.timeout)
            logger.info("LocationService 初始化成功")
        except Exception as e:
            logger.error(f"初始化 Nominatim 失敗: {e}")
            self.geolocator = None
    
    def geocode(self, address: str, country_code: str = "TW") -> Optional[Tuple[float, float, str]]:
        """
        地址轉換為經緯度（正向地理編碼）
        
        Args:
            address: 地址字串
            country_code: 國家代碼，默認為台灣 (TW)
            
        Returns:
            Optional[Tuple[float, float, str]]: (緯度, 經度, 完整地址) 或 None
        """
        if not self.geolocator:
            logger.error("Geolocator 未初始化")
            return None
        
        try:
            logger.info(f"正向地理編碼: {address}")
            location = self._with_retry(
                operation_name="正向地理編碼",
                func=lambda: self.geolocator.geocode(
                    address,
                    country_codes=country_code,
                    timeout=self.timeout,
                ),
            )
            
            if location:
                logger.info(f"找到位置: {location.address}")
                return (location.latitude, location.longitude, location.address)
            else:
                logger.warning(f"找不到位置: {address}")
                return None
                
        except RETRYABLE_EXCEPTIONS as e:
            logger.error(f"地理編碼多次逾時/失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"地理編碼失敗: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float, language: str = "zh-TW") -> Optional[str]:
        """
        經緯度轉換為地址（反向地理編碼）
        
        Args:
            latitude: 緯度
            longitude: 經度
            language: 語言代碼
            
        Returns:
            Optional[str]: 地址字串或 None
        """
        if not self.geolocator:
            logger.error("Geolocator 未初始化")
            return None
        
        try:
            logger.info(f"反向地理編碼: ({latitude}, {longitude})")
            location = self._with_retry(
                operation_name="反向地理編碼",
                func=lambda: self.geolocator.reverse(
                    (latitude, longitude),
                    exactly_one=True,
                    language=language,
                    timeout=self.timeout,
                ),
            )
            
            if location:
                full_address = location.address
                logger.info(f"找到地址: {full_address}")
                
                # 提取簡潔的中文地址（移除國家和郵遞區號）
                address_parts = full_address.split(', ')
                filtered_parts = []
                for part in address_parts:
                    # 跳過純數字（郵遞區號）和國家名稱
                    if not part.isdigit() and part not in ['Taiwan', '台灣', '臺灣', 'Republic of China']:
                        filtered_parts.append(part)
                
                # 取前3-4個最有意義的部分
                if filtered_parts:
                    simplified_address = ', '.join(filtered_parts[:4])
                    logger.info(f"簡化地址: {simplified_address}")
                    return simplified_address
                else:
                    return full_address
            else:
                logger.warning(f"找不到地址: ({latitude}, {longitude})")
                return None
                
        except RETRYABLE_EXCEPTIONS as e:
            logger.error(f"反向地理編碼多次逾時/失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"反向地理編碼失敗: {e}")
            return None

    def _with_retry(self, operation_name: str, func: Callable):
        """針對可恢復錯誤進行簡單重試"""
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return func()
            except RETRYABLE_EXCEPTIONS as exc:
                last_exception = exc
                logger.warning(
                    f"{operation_name} 第{attempt}/{self.max_retries}次失敗 (可重試): {exc}"
                )
                if attempt < self.max_retries:
                    sleep_time = self.retry_delay * attempt
                    time.sleep(sleep_time)
            except Exception:
                raise
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{operation_name} 重試機制未能取得結果")
    
    @staticmethod
    def format_coordinates(latitude: float, longitude: float, precision: int = 5) -> str:
        """
        格式化經緯度為字串
        
        Args:
            latitude: 緯度
            longitude: 經度
            precision: 小數位數
            
        Returns:
            str: 格式化的經緯度字串
        """
        return f"{latitude:.{precision}f}, {longitude:.{precision}f}"
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """
        驗證經緯度是否有效
        
        Args:
            latitude: 緯度
            longitude: 經度
            
        Returns:
            bool: 是否有效
        """
        try:
            if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
                return False
            
            if latitude < -90 or latitude > 90:
                return False
            
            if longitude < -180 or longitude > 180:
                return False
            
            return True
        except:
            return False
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        計算兩個經緯度之間的距離（使用 Haversine 公式）
        
        Args:
            lat1: 第一個點的緯度
            lon1: 第一個點的經度
            lat2: 第二個點的緯度
            lon2: 第二個點的經度
            
        Returns:
            float: 距離（公里）
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 地球半徑（公里）
        R = 6371.0
        
        # 轉換為弧度
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # 差異
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine 公式
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        logger.info(f"計算距離: {distance:.2f} km")
        
        return distance
