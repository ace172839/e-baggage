"""
Animation Service
處理動畫相關的服務
"""
import logging
import threading
import time
from typing import Tuple, List, TYPE_CHECKING
import flet_map as map

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


class AnimationService:
    """動畫服務"""
    
    @staticmethod
    def animate_marker_along_path(
        app_instance: 'App',
        marker_ref,
        path: List[Tuple[float, float]],
        duration: float = 0.5
    ) -> None:
        """
        沿路徑動畫標記
        
        Args:
            app_instance: App 實例
            marker_ref: 標記引用
            path: 路徑座標列表 [(緯度, 經度), ...]
            duration: 每步持續時間（秒）
        """
        app_instance.animation_running = True
        app_instance.animation_step = 0
        
        def animation_loop():
            while (app_instance.animation_running and 
                   app_instance.animation_step < len(path)):
                
                if marker_ref.current:
                    current_pos = path[app_instance.animation_step]
                    marker_ref.current.coordinates = map.MapLatitudeLongitude(
                        *current_pos
                    )
                    
                    if app_instance.page:
                        app_instance.page.update()
                
                app_instance.animation_step += 1
                time.sleep(duration)
            
            app_instance.animation_running = False
            logger.info("動畫已完成")
        
        animation_thread = threading.Thread(target=animation_loop, daemon=True)
        animation_thread.start()
        app_instance.animation_timer = animation_thread
    
    @staticmethod
    def stop_animation(app_instance: 'App') -> None:
        """
        停止動畫
        
        Args:
            app_instance: App 實例
        """
        app_instance.animation_running = False
        logger.info("動畫已停止")
    
    @staticmethod
    def interpolate_path(
        start: Tuple[float, float],
        end: Tuple[float, float],
        steps: int = 10
    ) -> List[Tuple[float, float]]:
        """
        在兩點之間插值生成路徑
        
        Args:
            start: 起點 (緯度, 經度)
            end: 終點 (緯度, 經度)
            steps: 步數
            
        Returns:
            路徑座標列表
        """
        path = []
        for i in range(steps + 1):
            t = i / steps
            lat = start[0] + (end[0] - start[0]) * t
            lon = start[1] + (end[1] - start[1]) * t
            path.append((lat, lon))
        
        return path
    
    @staticmethod
    def create_path_from_routing(
        routing_data: dict,
        sample_rate: int = 10
    ) -> List[Tuple[float, float]]:
        """
        從路由資料創建動畫路徑
        
        Args:
            routing_data: 路由資料
            sample_rate: 取樣率（每 N 個點取一個）
            
        Returns:
            路徑座標列表 [(緯度, 經度), ...]
        """
        coordinates = routing_data["routes"][0]["geometry"]["coordinates"]
        
        # 取樣以減少點數
        sampled = coordinates[::sample_rate]
        
        # 轉換為 (緯度, 經度) 格式
        path = [(coord[1], coord[0]) for coord in sampled]
        
        return path
