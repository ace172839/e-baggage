"""
Instant Booking View (重構版)
使用 Controller 模式，View 只負責 UI 渲染
"""
import flet as ft
import flet_map as map
from typing import TYPE_CHECKING
import logging

from config import USER_DASHBOARD_DEFAULT_LOCATION, USER_DASHBOARD_MAP_TEMPLATE, WINDOW_WIDTH
from constants import *
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab
from services import BookingService
from controllers import InstantBookingController

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_instant_booking_view(app_instance: 'App') -> ft.View:
    """
    建立即時預約的主 View
    使用 Controller 模式
    """
    logger.info("建立即時預約 View")
    
    # 使用 App 中已初始化的 Controller (保持狀態)
    controller = app_instance.instant_booking_controller
    logger.debug(f"使用現有 InstantBookingController，scan_confirmed={controller.scan_confirmed}")
    
    # 主容器 (用於動態切換內容)
    main_content = ft.Container(expand=True)
    
    # 用於持有當前的 MarkerLayer 引用，以便更新
    current_marker_layer = [None]

    def update_map_markers(self=None):
        """更新地圖上的標記 (由 Controller 調用)"""
        if not current_marker_layer[0]:
            return
            
        logger.info("正在更新地圖標記...")
        new_markers = []
        for hotel in controller.nearby_hotels:
            icon_color = ft.Colors.BLUE_600 if hotel.get("is_partner", False) else ft.Colors.GREY_400
            marker = map.Marker(
                content=ft.Icon(ft.Icons.HOTEL, color=icon_color, size=25),
                coordinates=map.MapLatitudeLongitude(hotel["lat"], hotel["lon"]),
            )
            new_markers.append(marker)
            
        # 添加用戶位置標記
        # 注意：這裡應該使用當前地圖中心或用戶實際位置，暫時使用默認位置或 controller 記錄的位置
        center_lat, center_lon = controller.current_map_center
        new_markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=35),
                coordinates=map.MapLatitudeLongitude(center_lat, center_lon),
            )
        )
        
        current_marker_layer[0].markers = new_markers
        current_marker_layer[0].update()
        logger.info(f"地圖標記已更新，共 {len(new_markers)} 個")

    def _build_step1_booking_form():
        """步驟 1: 地圖選擇與表單填寫"""
        
        # 確保有初始數據
        if not controller.nearby_hotels:
            controller.update_nearby_hotels(*USER_DASHBOARD_DEFAULT_LOCATION)

        # 載入合作飯店標記 (使用 controller.nearby_hotels)
        hotel_markers = []
        for hotel in controller.nearby_hotels:
            icon_color = ft.Colors.BLUE_600 if hotel.get("is_partner", False) else ft.Colors.GREY_400
            marker = map.Marker(
                content=ft.Icon(ft.Icons.HOTEL, color=icon_color, size=25),
                coordinates=map.MapLatitudeLongitude(hotel["lat"], hotel["lon"]),
            )
            hotel_markers.append(marker)
            
        # 添加用戶位置標記
        hotel_markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=35),
                coordinates=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
            )
        )
        
        marker_layer = map.MarkerLayer(markers=hotel_markers)
        current_marker_layer[0] = marker_layer
        
        # 地圖控制項
        map_control = map.Map(
            expand=True,
            initial_zoom=16,
            initial_center=map.MapLatitudeLongitude(*USER_DASHBOARD_DEFAULT_LOCATION),
            interaction_configuration=map.MapInteractionConfiguration(
                flags=map.MapInteractiveFlag.ALL
            ),
            on_position_change=controller.on_map_position_changed,
            layers=[
                map.TileLayer(url_template=USER_DASHBOARD_MAP_TEMPLATE),
                marker_layer,
            ],
        )
        
        # "在此區域搜尋" 按鈕
        search_btn = ft.Container(
            content=ft.ElevatedButton(
                "在此區域搜尋",
                icon=ft.Icons.SEARCH,
                on_click=controller.search_hotels_at_current_center,
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.BLACK,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                )
            ),
            alignment=ft.alignment.top_center,
            padding=ft.padding.only(top=10),
        )

        # 地圖堆疊層 (地圖 + 搜尋按鈕)
        map_stack = ft.Stack(
            controls=[
                map_control,
                search_btn
            ],
            expand=True
        )
        
        # 表單內容
        form_content = ft.Container(
            width=WINDOW_WIDTH,
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            border_radius=ft.BorderRadius(10, 10, 10, 10),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLACK26),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text("即時預約", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    ft.Text("請選擇上下車地點", size=14, color=COLOR_TEXT_DARK),
                    
                    # ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 上車地點
                    ft.TextField(
                        ref=app_instance.pickup_location_ref,
                        label="上車地點",
                        prefix_icon=ft.Icons.MY_LOCATION,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                        color=COLOR_TEXT_DARK,
                        read_only=True,
                        on_click=controller.handle_pickup_location_select,  # 改用 on_click 支持重新選擇
                        value=app_instance.pickup_location_ref.current.value if app_instance.pickup_location_ref.current else ""
                    ),
                    
                    # 下車地點
                    ft.TextField(
                        ref=app_instance.dropoff_location_ref,
                        label="下車地點",
                        prefix_icon=ft.Icons.FLAG,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                        color=COLOR_TEXT_DARK,
                        read_only=True,
                        on_click=controller.handle_dropoff_location_select,  # 改用 on_click 支持重新選擇
                        value=app_instance.dropoff_location_ref.current.value if app_instance.dropoff_location_ref.current else ""
                    ),
                    
                    ft.Row(
                        controls=[
                            # 行李數量
                            ft.TextField(
                                label="行李數量",
                                prefix_icon=ft.Icons.LUGGAGE,
                                border_radius=8,
                                bgcolor=ft.Colors.WHITE,
                                color=COLOR_TEXT_DARK,
                                value="1",
                                keyboard_type=ft.KeyboardType.NUMBER,
                                on_change=controller.update_luggage_count,  # 委派給 Controller
                                expand=5
                            ),
                            # 掃描行李按鈕
                            ft.OutlinedButton(
                                text="掃描行李",
                                icon=ft.Icons.QR_CODE_SCANNER,
                                height=45,
                                on_click=controller.handle_scan_baggage,  # 委派給 Controller
                                expand=1
                            ),
                        ],
                        spacing=10,
                        expand=True
                    ),

                    ft.TextField(
                        ref=app_instance.luggage_note_ref,
                        label="行李備注",
                        prefix_icon=ft.Icons.NOTE,
                        border_radius=8,
                        bgcolor=ft.Colors.WHITE,
                        color=COLOR_TEXT_DARK,
                        hint_text="例如：易碎物品、特殊尺寸等（選填）",
                        on_change=controller.update_luggage_note,  # 委派給 Controller
                    ),
                    
                    # ft.Divider(height=3, color=ft.Colors.TRANSPARENT),
                    
                    # 確認按鈕
                    ft.ElevatedButton(
                        text="下一步：選擇車型",
                        icon=ft.Icons.CHECK_CIRCLE,
                        height=40,
                        bgcolor=COLOR_BRAND_YELLOW,
                        color=COLOR_TEXT_DARK,
                        on_click=controller.go_to_confirm,  # 委派給 Controller
                    )
                ],
                spacing=10,
                expand=True
            ),
            expand=True
        )
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=map_control,
                    expand=2
                ),
                ft.Container(
                    content=form_content,
                    expand=3
                )
            ],
            spacing=0,
            expand=True
        )
    
    def _build_step2_confirm():
        """步驟 2: 確認訂單"""
        pending_trip = controller.pending_trip
        estimated_price = controller.selected_vehicle_price or (pending_trip.price if pending_trip else 0)
        price_text = f"NT$ {estimated_price:,.0f}" if estimated_price else "待選擇"
        vehicle_selected = bool(controller.selected_vehicle_type)

        vehicle_summary = ft.Container(
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DIRECTIONS_CAR_FILLED, color=ft.Colors.BLUE_600, size=28),
                            ft.Text("已選擇車型", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                            ft.TextButton(
                                "變更車型",
                                on_click=controller.submit_order,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        controller.selected_vehicle_label or "尚未選擇",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900 if vehicle_selected else ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        f"類型：{controller.selected_vehicle_type}" if vehicle_selected else "請返回上一頁選擇車型",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Text(
                        price_text,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_700 if vehicle_selected else ft.Colors.GREY_400,
                    ),
                ],
                spacing=10,
            ),
        )

        return ft.Container(
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text("確認您的預約", size=28, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # 訂單摘要卡片
                    ft.Container(
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column(
                            controls=[
                                ft.Text("訂單摘要", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                ft.Divider(),
                                
                                # 上車地點
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.MY_LOCATION, color=ft.Colors.GREEN_700),
                                        ft.Column(
                                            controls=[
                                                ft.Text("上車地點", size=12, color=ft.Colors.GREY_700),
                                                ft.Text(
                                                    controller.pickup_location or "未選擇",
                                                    size=16,
                                                    color=COLOR_TEXT_DARK,
                                                    width=WINDOW_WIDTH - 100,
                                                    max_lines=3,
                                                    overflow=ft.TextOverflow.VISIBLE
                                                )
                                            ],
                                            spacing=2,
                                            expand=True
                                        )
                                    ],
                                    spacing=10
                                ),
                                
                                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                                
                                # 下車地點
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED_700),
                                        ft.Column(
                                            controls=[
                                                ft.Text("下車地點", size=12, color=ft.Colors.GREY_700),
                                                ft.Text(
                                                    controller.dropoff_location or "未選擇",
                                                    size=16,
                                                    color=COLOR_TEXT_DARK,
                                                    width=WINDOW_WIDTH - 100,
                                                    max_lines=3,
                                                    overflow=ft.TextOverflow.VISIBLE
                                                )
                                            ],
                                            spacing=2,
                                            expand=True
                                        )
                                    ],
                                    spacing=10
                                ),
                                
                                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                                
                                # 行李數量
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.LUGGAGE, color=ft.Colors.BLUE_700),
                                        ft.Column(
                                            controls=[
                                                ft.Text("行李數量", size=12, color=ft.Colors.GREY_700),
                                                ft.Text(f"{controller.luggage_count} 件", size=16, color=COLOR_TEXT_DARK)
                                            ],
                                            spacing=2
                                        )
                                    ],
                                    spacing=10
                                ),
                                
                                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                                
                                # 行李備注
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.NOTE, color=ft.Colors.ORANGE_700),
                                        ft.Column(
                                            controls=[
                                                ft.Text("行李備注", size=12, color=ft.Colors.GREY_700),
                                                ft.Text(
                                                    controller.luggage_note if controller.luggage_note else "無",
                                                    size=16,
                                                    color=COLOR_TEXT_DARK if controller.luggage_note else ft.Colors.GREY_400
                                                )
                                            ],
                                            spacing=2,
                                            expand=True
                                        )
                                    ],
                                    spacing=10
                                ),
                                
                                ft.Divider(),
                                
                                # 預估費用
                                ft.Row(
                                    controls=[
                                        ft.Text("預估費用:", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                        ft.Text(price_text, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                            ],
                            spacing=10
                        )
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

                    vehicle_summary,

                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # 按鈕組
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                text="返回",
                                icon=ft.Icons.ARROW_BACK,
                                height=50,
                                expand=1,
                                on_click=controller.go_back,  # 委派給 Controller
                            ),
                            ft.ElevatedButton(
                                text="確認送出",
                                icon=ft.Icons.SEND,
                                height=50,
                                expand=2,
                                bgcolor=ft.Colors.GREEN_600,
                                color=ft.Colors.WHITE,
                                disabled=not vehicle_selected,
                                on_click=controller.finalize_booking,
                            ),
                        ],
                        spacing=10
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        )
    
    def update_view(self=None):
        """更新 View 內容（由 Controller 調用）"""
        logger.info(f"更新即時預約 View - 當前步驟: {controller.current_step}")
        main_content.content = {
            1: _build_step1_booking_form,
            2: _build_step2_confirm
        }.get(controller.current_step, _build_step1_booking_form)()

        if main_content.page:
            main_content.update()
        else:
            logger.debug("main_content 尚未掛載，略過 update()")
        logger.debug("即時預約 View 更新完成")
    
    # 綁定 update_view 到 controller
    controller.bind_view(type('ViewUpdater', (), {
        'update_view': update_view,
        'update_map_markers': update_map_markers
    })())
    logger.info("Controller 綁定完成")
    
    # 設置初始內容（不調用 update）
    initial_builder = {
        1: _build_step1_booking_form,
        2: _build_step2_confirm
    }.get(controller.current_step, _build_step1_booking_form)
    main_content.content = initial_builder()
    logger.info("初始內容設置完成")
    
    # 返回 View
    return ft.View(
        route="/app/user/instant_booking",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            main_content,
            build_bottom_nav_bar(app_instance, selected_index=1)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )
