"""
Advance Booking View (重構版)
使用 Controller 模式，實現動態生成住宿欄位
"""
import flet as ft
from typing import TYPE_CHECKING
import logging

from config import WINDOW_WIDTH
from constants import *
from views.common.navigator import build_bottom_nav_bar
from views.common.assistant import build_ai_fab
from services import DateService, OrderDisplayService
from controllers import PreviousBookingController

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)


def build_previous_booking_view(app_instance: 'App') -> ft.View:
    """
    建立事先預約的主 View
    使用 Controller 模式
    """
    logger.info("建立事先預約 View")
    
    # 使用 App 中已初始化的 Controller (保持狀態)
    controller = app_instance.previous_booking_controller
    logger.debug(f"使用現有 PreviousBookingController，current_step={controller.current_step}")
    
    # 載入飯店資料
    from services import BookingService
    all_hotels = BookingService.load_hotels()
    # 建立飯店字典 {"飯店名稱": {"地址", "is_partner", ...}}
    hotel_dict = {}
    for hotel in all_hotels:
        name = hotel.get('name', '')
        address = hotel.get('address', '')
        hotel_dict[name] = {
            'address': address,
            'is_partner': hotel.get('is_partner', False),
            'full_text': f"{name} ({address})"
        }
    
    # 主容器
    main_content = ft.Container(expand=True)
    
    # 日期選擇器
    arrival_date_picker = ft.DatePicker(
        on_change=lambda e: _on_arrival_date_change(e),
        first_date=DateService.get_min_date_for_picker(),
        help_text="請選擇您的抵達日期"
    )
    
    return_date_picker = ft.DatePicker(
        on_change=lambda e: _on_return_date_change(e),
        first_date=DateService.get_min_date_for_picker(),
        help_text="請選擇您的回程日期"
    )
    
    # 添加到 overlay
    if arrival_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(arrival_date_picker)
    if return_date_picker not in app_instance.page.overlay:
        app_instance.page.overlay.append(return_date_picker)
    
    # 為住宿規劃的 DatePicker 引用字典
    booking_check_in_pickers = {}
    booking_check_out_pickers = {}
    
    def _on_booking_check_in_change(e, idx):
        """入住日期變更"""
        controller.update_booking_check_in(idx, e.control.value)
        if idx in booking_check_in_pickers:
            app_instance.page.close(booking_check_in_pickers[idx])
    
    def _on_booking_check_out_change(e, idx):
        """退房日期變更"""
        controller.update_booking_check_out(idx, e.control.value)
        if idx in booking_check_out_pickers:
            app_instance.page.close(booking_check_out_pickers[idx])
    
    def _on_arrival_date_change(e):
        """抵達日期變更"""
        selected_date = DateService.format_date(arrival_date_picker.value)
        if app_instance.prev_arrival_date_ref.current:
            app_instance.prev_arrival_date_ref.current.value = selected_date
            app_instance.prev_arrival_date_ref.current.blur()
        controller.set_start_date(arrival_date_picker.value)
        app_instance.page.close(arrival_date_picker)
        app_instance.page.update()
    
    def _on_return_date_change(e):
        """回程日期變更"""
        selected_date = DateService.format_date(return_date_picker.value)
        if app_instance.prev_return_date_ref.current:
            app_instance.prev_return_date_ref.current.value = selected_date
            app_instance.prev_return_date_ref.current.blur()
        controller.set_end_date(return_date_picker.value)
        app_instance.page.close(return_date_picker)
        app_instance.page.update()
    
    def _build_step1_landing():
        """步驟 1: 日期選擇與設定"""
        
        return ft.Container(
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            expand=True,
            content=ft.Column(
                controls=[
                    # 標題
                    ft.Text("規劃您的旅程", size=28, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    ft.Text("請填寫行程基本資訊", size=14, color=COLOR_TEXT_DARK),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # 日期選擇卡片
                    ft.Container(
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column(
                            controls=[
                                ft.Text("選擇日期", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                ft.Divider(),
                                
                                # 抵達日期
                                ft.TextField(
                                    ref=app_instance.prev_arrival_date_ref,
                                    label="抵達日期",
                                    prefix_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                                    border_radius=8,
                                    bgcolor=ft.Colors.WHITE,
                                    color=COLOR_TEXT_DARK,
                                    read_only=True,
                                    on_focus=lambda _: app_instance.page.open(arrival_date_picker),
                                    value=app_instance.prev_arrival_date_val if hasattr(app_instance, 'prev_arrival_date_val') else ""
                                ),
                                
                                # 回程日期
                                ft.TextField(
                                    ref=app_instance.prev_return_date_ref,
                                    label="回程日期",
                                    prefix_icon=ft.Icons.CALENDAR_MONTH,
                                    border_radius=8,
                                    bgcolor=ft.Colors.WHITE,
                                    color=COLOR_TEXT_DARK,
                                    read_only=True,
                                    on_focus=lambda _: app_instance.page.open(return_date_picker),
                                    value=app_instance.prev_return_date_val if hasattr(app_instance, 'prev_return_date_val') else ""
                                ),
                            ],
                            spacing=10
                        )
                    ),
                    
                    # ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # # 運送選項卡片
                    # ft.Container(
                    #     padding=20,
                    #     bgcolor=ft.Colors.WHITE,
                    #     border_radius=10,
                    #     shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                    #     content=ft.Column(
                    #         controls=[
                    #             ft.Text("運送選項", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    #             ft.Divider(),
                                
                    #             # 接機服務
                    #             ft.Switch(
                    #                 label="需要機場接機服務",
                    #                 label_style=ft.TextStyle(color=COLOR_TEXT_DARK),
                    #                 value=True,
                    #                 active_color=COLOR_BRAND_YELLOW,
                    #                 on_change=controller.toggle_arrival_transfer  # 委派給 Controller
                    #             ),
                                
                    #             # 送機服務
                    #             ft.Switch(
                    #                 label="需要機場送機服務",
                    #                 label_style=ft.TextStyle(color=COLOR_TEXT_DARK),
                    #                 value=True,
                    #                 active_color=COLOR_BRAND_YELLOW,
                    #                 on_change=controller.toggle_departure_transfer  # 委派給 Controller
                    #             ),
                                
                    #             # 行李數量
                    #             ft.TextField(
                    #                 label="行李數量",
                    #                 prefix_icon=ft.Icons.LUGGAGE,
                    #                 border_radius=8,
                    #                 bgcolor=ft.Colors.WHITE,
                    #                 color=COLOR_TEXT_DARK,
                    #                 value="1",
                    #                 keyboard_type=ft.KeyboardType.NUMBER,
                    #                 on_change=controller.update_luggage_count  # 委派給 Controller
                    #             ),
                    #         ],
                    #         spacing=10
                    #     )
                    # ),
                    
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    
                    # 下一步按鈕
                    ft.ElevatedButton(
                        text="下一步：規劃住宿",
                        icon=ft.Icons.ARROW_FORWARD,
                        height=50,
                        bgcolor=COLOR_BRAND_YELLOW,
                        color=COLOR_TEXT_DARK,
                        on_click=controller.go_to_planning,  # 委派給 Controller
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
    
    def _build_step2_planning():
        
        segments_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=300)
        
        for idx, seg in enumerate(controller.trip_config.segments):
            is_last = (idx == len(controller.trip_config.segments) - 1)
            
            # --- 樣式設定 ---
            card_bg = "white" if not seg.is_locked else "#E0E0E0"
            border_color = COLOR_TEXT_DARK if is_last else "grey"
            
            # --- 內容元件 ---
            # 1. 入住日期 (如果是第二段以上，通常鎖定為上一段退房日)
            in_date_str = seg.check_in_date.strftime("%Y-%m-%d") if seg.check_in_date else "選擇日期"
            in_btn = ft.OutlinedButton(in_date_str, 
                                     icon=ft.Icons.DATE_RANGE,
                                     disabled=(idx > 0 or seg.is_locked), # 只有第一段且未鎖定可改入住日
                                     on_click=lambda e, i=idx: controller.open_date_picker(i, True))
            
            # 2. 退房日期
            out_date_str = seg.check_out_date.strftime("%Y-%m-%d") if seg.check_out_date else "選擇日期"
            out_btn = ft.OutlinedButton(out_date_str, 
                                      icon=ft.Icons.DATE_RANGE, 
                                      disabled=seg.is_locked,
                                      on_click=lambda e, i=idx: controller.open_date_picker(i, False))
            
            # 3. 飯店搜尋框 (使用 AutoComplete)
            def on_hotel_select(e, index=idx):
                """ 當使用者選擇飯店時 """
                if e.selection:
                    selected_hotel = e.selection.key  # key 是飯店名稱
                    controller.update_hotel_name(index, selected_hotel)
                    logger.info(f"第 {index} 筆預訂選擇飯店: {selected_hotel}")
                    # 更新視圖以顯示選擇的飯店
                    # controller.view.update_view()
            
            # 顯示當前選擇的飯店或搜尋框
            if seg.is_locked:
                # 已鎖定：只顯示飯店名稱（不顯示搜尋框）
                hotel_field = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("住宿地點 / 飯店名稱", size=12, color=ft.Colors.GREY_700),
                            ft.Text(seg.hotel_name, size=14, color=COLOR_TEXT_DARK, weight=ft.FontWeight.BOLD)
                        ],
                        spacing=2
                    ),
                    expand=True
                )
            else:
                # 未鎖定：顯示搜尋框（無論是否已選擇飯店）
                hotel_field = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("住宿地點 / 飯店名稱", size=12, color=ft.Colors.GREY_700),
                            ft.AutoComplete(
                                suggestions=[
                                    ft.AutoCompleteSuggestion(
                                        key=name,
                                        value=hotel_info['full_text']
                                    )
                                    for name, hotel_info in hotel_dict.items()
                                ],
                                suggestions_max_height=100,
                                visible=True,
                                on_select=on_hotel_select,
                            )
                        ],
                        spacing=2
                    ),
                    expand=True
                )

            # 4. 操作按鈕 (只有最後一段且未鎖定時顯示)
            action_row = ft.Row()
            if is_last and not seg.is_locked:
                action_row = ft.Row([
                    ft.ElevatedButton("確認並填寫下一段", 
                                      bgcolor="green", color="white", 
                                      on_click=lambda e, i=idx: controller.add_next_segment(i)),
                    ft.IconButton(ft.Icons.DELETE, icon_color="red", 
                                  visible=(idx>0), # 第一段不能刪
                                  on_click=controller.remove_last_segment)
                ], alignment=ft.MainAxisAlignment.END)

            # 組裝卡片
            card = ft.Container(
                content=ft.Column([
                    ft.Text(f"住宿 #{idx + 1}", weight="bold", color="black"),
                    ft.Row([
                        ft.Text("入住:", color=COLOR_TEXT_DARK),
                        in_btn
                    ]),
                    ft.Row([
                        ft.Text("退房:", color=COLOR_TEXT_DARK),
                        out_btn
                    ]),
                    hotel_field,
                    action_row
                ]),
                padding=15,
                bgcolor=card_bg,
                border=ft.border.all(2 if is_last else 1, border_color),
                border_radius=10
            )
            segments_column.controls.append(card)

        return ft.Container(
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            expand=True,
            content=ft.Column([
                ft.Text("Step 2: 住宿規劃", size=24, weight="bold", color=COLOR_TEXT_DARK),
                ft.Text(f"旅程區間: {controller.trip_config.total_start_date} ~ {controller.trip_config.total_end_date}", color=COLOR_TEXT_DARK),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                segments_column,
                ft.Row([
                    ft.OutlinedButton("上一步", on_click=controller.go_back),
                    ft.ElevatedButton("完成規劃 (Submit)", 
                                    bgcolor=COLOR_TEXT_DARK, color="white",
                                    # 只有當最後一段且已經覆蓋到結束日期才 enable，或在 controller 裡擋
                                    on_click=controller.go_to_confirm)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        )
    
    def _build_step3_confirm():
        """步驟 3: 確認訂單"""
        
        # 建立住宿摘要列表
        hotel_summary = []
        non_partner_hotels = []
        
        # 按入住日期排序
        sorted_segments = sorted(controller.trip_config.segments, key=lambda x: x.check_in_date)
        
        for idx, seg in enumerate(sorted_segments, 1):
            date_range = f"{DateService.format_date(seg.check_in_date)} ~ {DateService.format_date(seg.check_out_date)}"
            nights = (seg.check_out_date - seg.check_in_date).days
            
            hotel_row = ft.Container(
                padding=10,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.HOTEL,
                            color=ft.Colors.GREY_600,
                            size=24
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(f"住宿 {idx}", size=12, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                                ft.Text(seg.hotel_name, size=16, color=COLOR_TEXT_DARK, weight=ft.FontWeight.BOLD),
                                ft.Text(date_range, size=13, color=ft.Colors.GREY_700),
                                ft.Text(f"{nights} 晚", size=12, color=ft.Colors.BLUE_700)
                            ],
                            spacing=2,
                            expand=True
                        )
                    ],
                    spacing=10
                )
            )
            hotel_summary.append(hotel_row)
        
        return ft.Container(
            padding=20,
            bgcolor=COLOR_BG_LIGHT_TAN,
            expand=True,
            content=ft.Column(
                controls=[
                    # 標題
                    ft.Text("確認您的預約", size=28, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # 行程概要卡片
                    ft.Container(
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column(
                            controls=[
                                ft.Text("行程概要", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                ft.Divider(),
                                
                                # 日期範圍
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.DATE_RANGE, color=ft.Colors.BLUE_700),
                                        ft.Text(
                                            f"{DateService.format_date(controller.trip_config.total_start_date)} ~ {DateService.format_date(controller.trip_config.total_end_date)}",
                                            size=16,
                                            color=COLOR_TEXT_DARK
                                        )
                                    ],
                                    spacing=10
                                ),
                                
                                # 行李數量
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.LUGGAGE, color=ft.Colors.BROWN),
                                        ft.Text(
                                            f"行李運送: {len(controller.trip_config.segments)} 趟",
                                            size=16,
                                            color=COLOR_TEXT_DARK
                                        )
                                    ],
                                    spacing=10
                                ),
                            ],
                            spacing=10
                        )
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 住宿明細卡片
                    ft.Container(
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column(
                            controls=[
                                ft.Text("住宿明細", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                ft.Divider(),
                                ft.Column(controls=hotel_summary, spacing=10),
                            ],
                            spacing=10
                        )
                    ),
                    
                    # 非特約飯店警告
                    ft.Container(
                        padding=15,
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=8,
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ORANGE_700),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "*非特約旅館提醒*",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.ORANGE_700
                                        ),
                                        ft.Text(
                                            f"您有 {len(non_partner_hotels)} 晚住宿為非特約旅館，請自行與旅館溝通行李接待事項",
                                            size=12,
                                            color=ft.Colors.ORANGE_700
                                        )
                                    ],
                                    spacing=5,
                                    expand=True
                                )
                            ],
                            spacing=10
                        ),
                        visible=False
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # 預估費用
                    ft.Container(
                        padding=20,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("預估總費用:", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                        ft.Text(
                                            f"NT$ {sum((seg.check_out_date - seg.check_in_date).days * 300 for seg in controller.trip_config.segments) + 500}",
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.GREEN_700
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Text(
                                    f"共 {sum((seg.check_out_date - seg.check_in_date).days for seg in controller.trip_config.segments)} 晚 × NT$300/晚 + 基本費用 NT$500",
                                    size=12,
                                    color=ft.Colors.GREY_700
                                )
                            ],
                            spacing=5
                        )
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # 按鈕組
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                text="返回",
                                icon=ft.Icons.ARROW_BACK,
                                height=50,
                                expand=1,
                                on_click=controller.go_back  # 委派給 Controller
                            ),
                            ft.ElevatedButton(
                                text="送出訂單",
                                icon=ft.Icons.SEND,
                                height=50,
                                expand=2,
                                bgcolor=ft.Colors.GREEN_600,
                                color=ft.Colors.WHITE,
                                on_click=controller.submit_order  # 委派給 Controller
                            ),
                        ],
                        spacing=10
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
    
    def update_view(self=None):
        """更新 View 內容（由 Controller 調用）"""
        logger.info(f"更新事先預約 View - 當前步驟: {controller.current_step}")
        main_content.content = {
            1: _build_step1_landing,
            2: _build_step2_planning,
            3: _build_step3_confirm
        }.get(controller.current_step, _build_step1_landing)()
        
        main_content.update()
        logger.debug("事先預約 View 更新完成")
    
    # 綁定 update_view 到 controller
    controller.bind_view(type('ViewUpdater', (), {'update_view': update_view})())
    logger.info("Controller 綁定完成")
    
    # 設置初始內容（不調用 update）
    main_content.content = _build_step1_landing()
    logger.info("初始內容設置完成")
    
    # 返回 View
    return ft.View(
        route="/app/user/previous_booking",
        padding=0,
        floating_action_button=build_ai_fab(app_instance),
        controls=[
            main_content,
            build_bottom_nav_bar(app_instance, selected_index=3)
        ],
        bgcolor=COLOR_BG_LIGHT_TAN
    )