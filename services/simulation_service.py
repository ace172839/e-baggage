"""
Simulation Service
處理模擬數據生成、動畫模擬等業務邏輯
"""
import random
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class SimulationService:
    """模擬數據服務"""
    
    @staticmethod
    def calculate_next_position(current_left: float, current_top: float, 
                               max_left: float, max_top: float,
                               min_step: int = 10, max_step: int = 30) -> Tuple[float, float]:
        """
        計算下一個位置（模擬移動）
        
        Args:
            current_left: 當前水平位置
            current_top: 當前垂直位置
            max_left: 最大水平位置
            max_top: 最大垂直位置
            min_step: 最小移動步長
            max_step: 最大移動步長
            
        Returns:
            Tuple[float, float]: (新的水平位置, 新的垂直位置)
        """
        # 隨機往前移動
        new_left = current_left + random.randint(min_step, max_step)
        new_top = current_top + random.randint(5, 15)
        
        # 邊界檢查，超出範圍則重置
        if new_left > max_left:
            new_left = 50
        if new_top > max_top:
            new_top = 50
        
        logger.debug(f"計算新位置: ({new_left}, {new_top})")
        return new_left, new_top
    
    @staticmethod
    def generate_driver_info(driver_id: str = None) -> dict:
        """
        生成模擬的司機資訊
        
        Args:
            driver_id: 司機ID，如果為None則隨機生成
            
        Returns:
            dict: 司機資訊字典
        """
        driver_names = ["王小明", "李大華", "張志明", "陳美麗", "林建國"]
        
        if driver_id is None:
            driver_id = f"D{random.randint(1000, 9999)}"
        
        driver_info = {
            "id": driver_id,
            "name": random.choice(driver_names),
            "license_plate": f"{random.choice(['ABC', 'DEF', 'GHI', 'JKL'])}-{random.randint(1000, 9999)}",
            "phone": f"09{random.randint(10000000, 99999999)}",
            "estimated_arrival": f"{random.randint(10, 60)}分鐘",
            "rating": round(random.uniform(4.0, 5.0), 1)
        }
        
        logger.info(f"生成司機資訊: {driver_info['name']}")
        return driver_info
    
    @staticmethod
    def generate_order_id(prefix: str = "ORD") -> str:
        """
        生成訂單ID
        
        Args:
            prefix: ID前綴
            
        Returns:
            str: 訂單ID
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = random.randint(1000, 9999)
        order_id = f"{prefix}{timestamp}{random_suffix}"
        
        logger.info(f"生成訂單ID: {order_id}")
        return order_id
    
    @staticmethod
    def calculate_estimated_time(distance_km: float, speed_kmh: float = 40.0) -> int:
        """
        根據距離計算預估時間
        
        Args:
            distance_km: 距離（公里）
            speed_kmh: 平均速度（公里/小時）
            
        Returns:
            int: 預估時間（分鐘）
        """
        if distance_km <= 0:
            return 0
        
        time_hours = distance_km / speed_kmh
        time_minutes = int(time_hours * 60)
        
        # 添加一些隨機誤差（±10%）
        variance = random.uniform(0.9, 1.1)
        time_minutes = int(time_minutes * variance)
        
        logger.info(f"計算預估時間: {distance_km}km -> {time_minutes}分鐘")
        return max(5, time_minutes)  # 最少5分鐘
    
    @staticmethod
    def simulate_price(distance_km: float, base_price: float = 100.0, 
                      price_per_km: float = 15.0) -> int:
        """
        模擬計算價格
        
        Args:
            distance_km: 距離（公里）
            base_price: 基本價格
            price_per_km: 每公里價格
            
        Returns:
            int: 總價格（四捨五入到整數）
        """
        if distance_km <= 0:
            return int(base_price)
        
        total_price = base_price + (distance_km * price_per_km)
        
        # 添加一些隨機誤差（±5%）
        variance = random.uniform(0.95, 1.05)
        total_price = total_price * variance
        
        # 四捨五入到整數
        total_price = round(total_price)
        
        logger.info(f"計算價格: {distance_km}km -> NT${total_price}")
        return total_price
    
    @staticmethod
    def generate_mock_locations(count: int = 5) -> list:
        """
        生成模擬的地點列表
        
        Args:
            count: 要生成的地點數量
            
        Returns:
            list: 地點列表
        """
        mock_locations = [
            "台北101",
            "台北車站",
            "松山機場",
            "桃園機場",
            "板橋車站",
            "中正紀念堂",
            "西門町",
            "信義商圈",
            "士林夜市",
            "北投溫泉"
        ]
        
        selected = random.sample(mock_locations, min(count, len(mock_locations)))
        logger.info(f"生成 {len(selected)} 個模擬地點")
        return selected
