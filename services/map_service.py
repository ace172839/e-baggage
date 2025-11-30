"""
Map Service
處理地圖相關的服務
"""
import logging
from typing import Tuple, List, Dict, Any
import flet_map as map

logger = logging.getLogger(__name__)


class MapService:
    """地圖服務"""
    
    @staticmethod
    def create_marker(
        icon: str,
        color: str,
        coordinates: Tuple[float, float],
        size: int = 35,
        ref = None
    ) -> map.Marker:
        """
        創建地圖標記
        
        Args:
            icon: 圖標
            color: 顏色
            coordinates: 座標 (緯度, 經度)
            size: 大小
            ref: 引用
            
        Returns:
            Marker 物件
        """
        import flet as ft
        
        marker_kwargs = {
            "content": ft.Icon(icon, color=color, size=size),
            "coordinates": map.MapLatitudeLongitude(*coordinates)
        }
        
        if ref is not None:
            marker_kwargs["ref"] = ref
        
        return map.Marker(**marker_kwargs)
    
    @staticmethod
    def create_polyline(
        coordinates: List[List[float]],
        color: str,
        width: int = 5
    ) -> map.PolylineMarker:
        """
        創建路線
        
        Args:
            coordinates: 座標列表 [[經度, 緯度], ...]
            color: 顏色
            width: 寬度
            
        Returns:
            PolylineMarker 物件
        """
        return map.PolylineMarker(
            coordinates=[
                map.MapLatitudeLongitude(coord[1], coord[0])
                for coord in coordinates
            ],
            color=color,
            border_stroke_width=width
        )
    
    @staticmethod
    def create_polyline_from_routing(
        routing_data: Dict[str, Any],
        color: str,
        width: int = 5
    ) -> map.PolylineMarker:
        """
        從路由資料創建路線
        
        Args:
            routing_data: 路由資料（包含 routes[0].geometry.coordinates）
            color: 顏色
            width: 寬度
            
        Returns:
            PolylineMarker 物件
        """
        coordinates = routing_data["routes"][0]["geometry"]["coordinates"]
        return MapService.create_polyline(coordinates, color, width)
    
    @staticmethod
    def calculate_center(
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        計算兩點的中心座標
        
        Args:
            coord1: 座標1 (緯度, 經度)
            coord2: 座標2 (緯度, 經度)
            
        Returns:
            中心座標 (緯度, 經度)
        """
        return (
            (coord1[0] + coord2[0]) / 2,
            (coord1[1] + coord2[1]) / 2
        )
