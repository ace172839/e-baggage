"""
Order Display Service
處理訂單顯示相關的業務邏輯
"""
import logging
from typing import List, Dict, Any
import flet as ft

logger = logging.getLogger(__name__)


class OrderDisplayService:
    """訂單顯示服務"""
    
    @staticmethod
    def create_order_table_rows(bookings: List[Dict[str, Any]], columns: List[str]) -> List[ft.DataRow]:
        """
        根據訂單列表創建表格行
        
        Args:
            bookings: 訂單列表
            columns: 要顯示的欄位名稱列表
            
        Returns:
            List[ft.DataRow]: Flet DataRow 列表
        """
        try:
            rows = []
            for booking in bookings:
                cells = []
                for col in columns:
                    value = booking.get(col, "")
                    
                    # 特殊處理：如果是時間欄位且為空，顯示「入住」
                    if col == "time" and not value:
                        value = "入住"
                    
                    cells.append(ft.DataCell(ft.Text(str(value))))
                
                rows.append(ft.DataRow(cells=cells))
            
            logger.info(f"創建了 {len(rows)} 行訂單表格")
            return rows
            
        except Exception as e:
            logger.error(f"創建訂單表格行失敗: {e}")
            return []
    
    @staticmethod
    def create_uncontracted_hotel_rows(bookings: List[Dict[str, Any]]) -> List[ft.DataRow]:
        """
        創建非特約旅館的表格行（帶紅色標記）
        
        Args:
            bookings: 訂單列表
            
        Returns:
            List[ft.DataRow]: Flet DataRow 列表
        """
        try:
            rows = []
            for booking in bookings:
                if not booking.get("contracted", True):  # 如果不是特約旅館
                    rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(
                                booking.get("start_date", ""),
                                color=ft.Colors.RED_700
                            )),
                            ft.DataCell(ft.Text(
                                booking.get("location", ""),
                                color=ft.Colors.RED_700
                            ))
                        ]
                    ))
            
            logger.info(f"創建了 {len(rows)} 行非特約旅館記錄")
            return rows
            
        except Exception as e:
            logger.error(f"創建非特約旅館表格行失敗: {e}")
            return []
    
    @staticmethod
    def filter_bookings_by_criteria(bookings: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根據條件篩選訂單
        
        Args:
            bookings: 訂單列表
            criteria: 篩選條件字典
            
        Returns:
            List[Dict[str, Any]]: 篩選後的訂單列表
        """
        try:
            filtered = bookings
            
            for key, value in criteria.items():
                filtered = [b for b in filtered if b.get(key) == value]
            
            logger.info(f"篩選後剩餘 {len(filtered)} 筆訂單")
            return filtered
            
        except Exception as e:
            logger.error(f"篩選訂單失敗: {e}")
            return bookings
    
    @staticmethod
    def format_order_summary(order: Dict[str, Any]) -> str:
        """
        格式化訂單摘要字串
        
        Args:
            order: 訂單字典
            
        Returns:
            str: 格式化的訂單摘要
        """
        try:
            summary_parts = []
            
            if "start_date" in order:
                summary_parts.append(f"日期: {order['start_date']}")
            
            if "location" in order:
                summary_parts.append(f"地點: {order['location']}")
            
            if "time" in order and order["time"]:
                summary_parts.append(f"時間: {order['time']}")
            
            summary = " | ".join(summary_parts)
            logger.info(f"格式化訂單摘要: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"格式化訂單摘要失敗: {e}")
            return "訂單資訊"
    
    @staticmethod
    def validate_booking_data(booking: Dict[str, Any], required_fields: List[str]) -> tuple[bool, str]:
        """
        驗證訂單資料是否完整
        
        Args:
            booking: 訂單字典
            required_fields: 必填欄位列表
            
        Returns:
            tuple[bool, str]: (是否有效, 錯誤訊息)
        """
        try:
            missing_fields = []
            
            for field in required_fields:
                if field not in booking or not booking[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"缺少必填欄位: {', '.join(missing_fields)}"
                logger.warning(error_msg)
                return False, error_msg
            
            logger.info("訂單資料驗證通過")
            return True, ""
            
        except Exception as e:
            logger.error(f"驗證訂單資料失敗: {e}")
            return False, "驗證失敗"
