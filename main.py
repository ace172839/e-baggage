import datetime
import flet as ft
import flet_map as map
import logging
import random
import time
import json
import threading

from constants import *
# (注意：這假設您的 config.py 已經被更新)
from config import *

# --- 匯入新的 config 變數 ---
from config import (
    LOCATION_TAIPEI_101, 
    LOCATION_GRAND_HOTEL, 
    MAP_ROUTING_101_GRAND_HOTEL,
    MAP_ROUTING_CITYHALL_101, # (這個 driver 路線保持不變)
    USER_DASHBOARD_MAP_TEMPLATE,
)

# --- 恢復原始的 router 匯入 ---
from app.router import create_route_handler


DEBUG = True
if DEBUG:
    level = logging.DEBUG
    mode = "debug"
else:
    level = logging.INFO
    mode = "production"

# (設定 logging)
logging.basicConfig(
    filename=f"ebaggage_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=level
)
logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        """
        初始化 App。
        """
        self.page = None
        self.mode = mode

        # --- 登入 Refs ---
        self.login_username = ft.Ref[ft.TextField]()
        self.login_password = ft.Ref[ft.TextField]()
        self.login_captcha = ft.Ref[ft.TextField]()
        self.login_error_text = ft.Ref[ft.Text]()
        self.captcha_text = ft.Ref[ft.Text]()

        # --- 即時預約 Refs (Demo 狀態) ---
        self.current_location_ref = ft.Ref[ft.TextField]()
        self.arrival_date_ref = ft.Ref[ft.TextField]()
        self.return_date_ref = ft.Ref[ft.TextField]()
        self.pickup_location_ref = ft.Ref[ft.TextField]()
        self.dropoff_location_ref = ft.Ref[ft.TextField]()
        
        # --- 事先預約 Refs (從您上傳的程式碼恢復) ---
        self.prev_arrival_date_ref = ft.Ref[ft.TextField]()
        self.prev_return_date_ref = ft.Ref[ft.TextField]()
        self.prev_pickup_location_ref = ft.Ref[ft.TextField]()
        self.prev_dropoff_location_ref = ft.Ref[ft.TextField]()
        self.prev_arrival_date_val = None
        self.prev_return_date_val = None
        self.prev_pickup_location_val = None
        self.prev_dropoff_location_val = None
        
        self.notes_ref = ft.Ref[ft.TextField]()
        self.current_search_mode = "pickup"
        
        # --- 全域地圖 Refs ---
        self.map_ref = ft.Ref[map.Map]()
        self.marker_layer_ref = ft.Ref[map.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map.PolylineLayer]()
        self.driver_marker_ref = ft.Ref[map.Marker]()
        
        # --- 使用者追蹤頁面專用 Refs ---
        self.user_tracking_map_ref = ft.Ref[map.Map]()
        self.car_marker_ref = ft.Ref[map.Marker]()
        
        # --- 搜尋 Refs ---
        self.search_bar_ref = ft.Ref[ft.Container]()
        self.search_text_ref = ft.Ref[ft.TextField]()
        
        # --- 其他狀態 ---
        self.scan_results = 0
        self.scan_confirmed = False
        self.driver_alert_dialog = ft.Ref[ft.AlertDialog]()
        
        # (從您上傳的程式碼恢復 booking_data)
        self.booking_data = {} 

        # --- 動畫控制變數 ---
        self.animation_running = False # 用於 user_animation
        self.animation_timer = None # 用於 user_animation
        self.animation_step = 0 

        self.hotel_baggages = 63
        self.hotel_not_arrived_customer = 27


    def main(self, page: ft.Page):
        self.page = page
        self.page.title = "e-baggage"

        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.resizable = False
        self.page.window.always_on_top = True

        self.page.fonts = {
            "LXGWWenKaiTC-Regular": "fonts/LXGWWenKaiTC-Regular.ttf",
        }
        self.page.theme = ft.Theme(
            font_family="LXGWWenKaiTC-Regular",

            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLACK,
                on_primary=ft.Colors.WHITE,
                primary_container=ft.Colors.BLUE,
                on_primary_container=ft.Colors.LIGHT_BLUE,
                secondary_container=ft.Colors.BLUE_GREY_700,
                on_secondary_container=ft.Colors.WHITE,
                on_surface=ft.Colors.BLACK,
                on_surface_variant=ft.Colors.GREY_500,
                surface_container_low=COLOR_BG_LIGHT_TAN,
            ),
            
            date_picker_theme=ft.DatePickerTheme(
                bgcolor=ft.Colors.WHITE,
                header_bgcolor=COLOR_BG_LIGHT_TAN,
                locale=ft.Locale("zh", "TW")
            ),
            data_table_theme=ft.DataTableTheme(
                data_text_style=ft.TextStyle(
                    size=12,
                    color=COLOR_TEXT_DARK
                ),
                heading_row_height=0,
                divider_thickness=0
            )
        )
        
        self.page.on_route_change = create_route_handler(self)
        self.page.go("/splash")


    # --- 處理 (Handle) 邏輯 ---
    def login_view_handle_regenerate_captcha(self, e):
        
        new_code = str(random.randint(10000, 99999))
        self.captcha_text.current.value = new_code
        self.page.update()

    def _show_login_error(self, message: str):
        
        if self.login_error_text.current:
            self.login_error_text.current.value = message
            self.login_error_text.current.visible = True
            self.page.update()

    def login_view_handle_login(self, e, role: str):
        if self.mode == "debug":
            logger.warning("在偵錯模式下登入，已跳過驗證。")
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", self.login_username.current.value or "demo@user.com")
            
            self.page.go(f"/app/{role}")
            return
        
        logger.info("正式模式登入驗證 (未實作)")

        
    # === Demo 流程 Handlers ===
    
    def handle_nav_bar_change(self, e):
        """
        處理「底部導航列」的點擊事件
        """
        selected_index = int(e.data) 
        
        if self.search_bar_ref.current:
            self.search_bar_ref.current.visible = False

        if selected_index == 0:
            logger.info("導航到「更多」頁面")
            self.page.go("/app/user/more")
        elif selected_index == 1:
            logger.info("導航到「即時預約」Demo 頁面")
            self.page.go("/app/user/booking_instant") 
        elif selected_index == 2:
            logger.info("導航到「首頁」儀表板")
            self.page.go("/app/user/dashboard")
        elif selected_index == 3:
            logger.info("導航到「事先預約」頁面")
            self.page.go("/app/user/booking_previous")
        elif selected_index == 4:
            logger.info("導航到「客服」頁面")
            self.page.go("/app/user/support")
        else:
            logger.error(f"未知的導航索引: {selected_index}")
            self.page.go("/app/user/dashboard") 
    

    def _update_map_location(self, coords: tuple, location_name: str, mode: str):
        logger.info(f"Updating map for {mode} to {location_name} at {coords}")
        
        if not self.map_ref.current or not self.marker_layer_ref.current:
            logger.error("Map or MarkerLayer not initialized!")
            return

        self.map_ref.current.center = map.MapLatitudeLongitude(*coords)
        
        self.marker_layer_ref.current.markers = [
            map.Marker(
                content=ft.Icon(
                    ft.Icons.LOCATION_ON, 
                    color=ft.Colors.RED_700, 
                    size=40
                ),
                coordinates=map.MapLatitudeLongitude(*coords),
            )
        ]

        if mode == "pickup" and self.pickup_location_ref.current:
            self.pickup_location_ref.current.value = location_name
        elif mode == "dropoff" and self.dropoff_location_ref.current:
            self.dropoff_location_ref.current.value = location_name
            
        if self.search_bar_ref.current:
            self.search_bar_ref.current.visible = False

        self.page.update()

    def handle_select_location_pickup(self, e):
        logger.info("導航到地圖選擇 (即時預約 - 上車地點)")
        self.page.go("/app/user/map/instant_pickup")

    def handle_select_location_dropoff(self, e):
        logger.info("導航到地圖選擇 (即時預約 - 下車地點)")
        self.page.go("/app/user/map/instant_dropoff")

    def handle_select_location_prev_pickup(self, e):
        logger.info("導航到地圖選擇 (事先預約 - 上車地點)")
        self.page.go("/app/user/map/prev_pickup")

    def handle_select_location_prev_dropoff(self, e):
        logger.info("導航到地圖選擇 (事先預約 - 下車地點)")
        self.page.go("/app/user/map/prev_dropoff")

    def handle_search_location(self, e):
        
        search_query = self.search_text_ref.current.value
        logger.info(f"Handling search for: {search_query}")
        
        if "圓山" in search_query:
            self._update_map_location(LOCATION_GRAND_HOTEL, "圓山大飯店", self.current_search_mode)
        elif "101" in search_query:
            self._update_map_location(LOCATION_TAIPEI_101, "台北 101", self.current_search_mode)
        else:
            self._update_map_location(USER_DASHBOARD_DEFAULT_LOCATION, "台北 101 (預設)", self.current_search_mode)

    def handle_scan_baggage(self, e):
        logger.info("AI 行李掃描功能啟動！")
        self.page.go("/app/user/scan")
        
    def handle_cancel_instant_booking(self, e):
        logger.info("Booking cancelled")
        if self.pickup_location_ref.current:
            self.pickup_location_ref.current.value = "台北 101"
        if self.dropoff_location_ref.current:
            self.dropoff_location_ref.current.value = ""
        if self.notes_ref.current:
            self.notes_ref.current.value = ""
        self.scan_confirmed = False
        self._update_map_location(LOCATION_TAIPEI_101, "台北 101", "pickup")
        self.page.update()

    def handle_confirm_instant_booking(self, e):
        logger.info("Proceeding to order confirmation")
        if not self.scan_confirmed:
            self.page.snack_bar = ft.SnackBar(ft.Text("請先掃描行李！"), open=True)
            self.page.update()
            return
        self.page.go("/app/user/confirm_order")

    def handle_scan_start(self, e):
        
        logger.info("Starting scan...")
        
        if self.page.views:
            for ctrl in self.page.views[-1].controls:
                if isinstance(ctrl, ft.Stack):
                    for stack_item in ctrl.controls:
                        if isinstance(stack_item, ft.ProgressRing):
                            stack_item.visible = True
                            break
            self.page.update()

        def go_to_results():
            self.page.go("/app/user/scan_results")

        threading.Timer(2.0, go_to_results).start()

    def handle_hotel_scan_start(self, e):
        
        logger.info("Starting scan...")
        
        if self.page.views:
            for ctrl in self.page.views[-1].controls:
                if isinstance(ctrl, ft.Stack):
                    for stack_item in ctrl.controls:
                        if isinstance(stack_item, ft.ProgressRing):
                            stack_item.visible = True
                            break
            self.page.update()

        def go_to_results():
            self.page.go("/app/hotel/scan_results")

        threading.Timer(2.0, go_to_results).start()

    def handle_driver_scan_start(self, e):
        
        logger.info("Starting scan...")
        
        if self.page.views:
            for ctrl in self.page.views[-1].controls:
                if isinstance(ctrl, ft.Stack):
                    for stack_item in ctrl.controls:
                        if isinstance(stack_item, ft.ProgressRing):
                            stack_item.visible = True
                            break
            self.page.update()

        def go_to_results():
            self.page.go("/app/driver/scan_results")

        threading.Timer(2.0, go_to_results).start()

    def handle_scan_reject(self, e):
        
        logger.info("Scan rejected, going back")
        self.page.go("/app/user/scan")

    def handle_scan_confirm(self, e):
        
        logger.info("Scan confirmed")
        self.scan_confirmed = True
        self.page.go("/app/user/booking_instant")

    def handle_order_cancel(self, e):
        
        logger.info("Order confirmation cancelled")
        self.page.go("/app/user/booking_instant")

    def handle_order_confirm(self, e):
        
        logger.info("Order confirmed! Booking successful.")
        
        success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("預約成功！"),
            content=ft.Text("正在為您尋找司機..."),
            actions=[
                ft.TextButton(
                    "確認", 
                    on_click=lambda e: self.page.close(success_dialog), 
                    style=ft.ButtonStyle(color=ft.Colors.GREEN)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self._navigate_after_dialog_close("/app/driver", "driver")
        )
        
        self.page.open(success_dialog)

    def _navigate_after_dialog_close(self, route: str, role: str = None):
        """
        一個輔助函式，確保在彈窗關閉後才執行頁面導航
        """
        if role:
            self.page.session.set("role", role)
        self.page.go(route)

    def handle_show_driver_alert(self):
        def new_order_to_driver():
            if not self.driver_alert_dialog.current:
                self.driver_alert_dialog.current = ft.AlertDialog(
                    ref=self.driver_alert_dialog,
                    modal=True,
                    title=ft.Text("新的行李預約"),
                    content=ft.Text("您有新的行李預約，車資分潤為200元，預估行車時間 50 分鐘"),
                    actions=[
                        ft.TextButton("取消", on_click=self.handle_driver_reject, style=ft.ButtonStyle(color=ft.Colors.RED)),
                        ft.TextButton("接單", on_click=self.handle_driver_accept, style=ft.ButtonStyle(color=ft.Colors.GREEN)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            
            self.page.open(self.driver_alert_dialog.current)
            
        logger.info("Showing driver alert")
        timer = threading.Timer(2.5, new_order_to_driver)
        timer.start()

    def handle_driver_reject(self, e):
        logger.info("Driver rejected order")
        if self.driver_alert_dialog.current:
            self.driver_alert_dialog.current.on_dismiss = None
            self.page.close(self.driver_alert_dialog.current)

    def handle_driver_accept(self, e):
        logger.info("Driver accepted order")
        dialog_to_close = self.driver_alert_dialog.current
        
        if dialog_to_close:
            dialog_to_close.on_dismiss = lambda _: self._navigate_after_dialog_close("/app/driver/tracking_101")
            self.page.close(dialog_to_close)
        else:
            self._navigate_after_dialog_close("/app/driver/tracking_101")
        
    def _show_driver_scan_dialog(self, e=None):
        """
        顯示抵達旅客地點的彈窗，並導航至掃描頁面。
        """
        logger.info("準備顯示司機掃描彈窗...")
        
        def show_dialog():
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("抵達目的地"),
                content=ft.Text("抵達目的地。請掃描旅客的行李，並協助將行李上車"),
                actions=[
                    ft.TextButton(
                        "開始掃描", 
                        on_click=lambda e: self.page.close(dialog), 
                        style=ft.ButtonStyle(color=ft.Colors.GREEN)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: self._navigate_after_dialog_close("/app/driver/scan")
            )
            
            self.page.open(dialog) 
            logger.info("司機掃描彈窗已顯示。")

        if self.page:
            self.page.run_thread(show_dialog) 
        else:
            logger.error("Page 不存在，無法顯示司機掃描彈窗。")
    
    # --- ↓↓↓ 新增函式：顯示司機抵達旅館彈窗 ↓↓↓ ---
    def _show_driver_hotel_dialog(self, e=None):
        """
        顯示抵達旅館的彈窗，並導航回司機主頁。
        """
        logger.info("準備顯示司機抵達旅館彈窗...")
        
        def show_dialog():
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("抵達目的地"),
                content=ft.Text("抵達目的地。請提醒旅館掃描旅客的行李，並協助將行李下車進入旅館"),
                actions=[
                    ft.TextButton(
                        "確認", 
                        on_click=lambda e: self.page.close(dialog), # 點擊按鈕只關閉
                        style=ft.ButtonStyle(color=ft.Colors.GREEN)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: self._navigate_after_dialog_close("/app/driver") # 關閉後導航回司機主頁
            )
            
            self.page.open(dialog) 
            logger.info("司機抵達旅館彈窗已顯示。")

        if self.page:
            self.page.run_thread(show_dialog) 
        else:
            logger.error("Page 不存在，無法顯示司機抵達旅館彈窗。")
    # --- ↑↑↑ 新增函式結束 ↑↑↑ ---
        
    def start_driver_animation_101(self):
        
        logger.info("Scheduling driver tracking animation")

        def animation_logic():
            logger.info("Starting driver tracking animation after delay")
            
            if not self.driver_marker_ref.current or not self.map_ref.current:
                logger.error("Driver marker or map not ready for animation after delay.")
                return

            path_data = MAP_ROUTING_CITYHALL_101["routes"][0]["geometry"]["coordinates"]
            
            animation_points = [[lat, lon] for lon, lat in path_data]
            
            if not animation_points:
                logger.error("No coordinates found in path data")
                return

            num_points = len(animation_points)
            total_duration_sec = 8.0
            time_per_step = total_duration_sec / num_points
            
            final_lat_lon = animation_points[-1]
            final_map_coords = map.MapLatitudeLongitude(*final_lat_lon)

            def animate_step(i):
                if i >= num_points:
                    logger.info("Animation finished")
                    
                    if self.map_ref.current:
                        self.map_ref.current.center_on(final_map_coords, 16)
                    
                    if self.polyline_layer_ref.current:
                        self.polyline_layer_ref.current.polylines = [
                            map.PolylineMarker(
                                coordinates=[
                                    final_map_coords, 
                                    map.MapLatitudeLongitude(*LOCATION_TAIPEI_101), 
                                ],
                                color=ft.Colors.BLUE,
                                border_stroke_width=5
                            )
                        ]
                        
                    if self.driver_marker_ref.current:
                        self.driver_marker_ref.current.coordinates = final_map_coords
                    
                    self._show_driver_scan_dialog()
                        
                    self.page.update()
                    return
                
                current_lat, current_lon = animation_points[i]
                
                logger.debug(f"Animation step {i}: Lat={current_lat}, Lon={current_lon}")
                
                if self.driver_marker_ref.current:
                    self.driver_marker_ref.current.coordinates = map.MapLatitudeLongitude(current_lat, current_lon)
                self.map_ref.current.center_on(map.MapLatitudeLongitude(current_lat, current_lon), 16)
                self.page.update()

                threading.Timer(time_per_step, lambda: animate_step(i + 1)).start()

            animate_step(0)

        threading.Timer(0.5, animation_logic).start()

    def start_driver_animation_hotel(self):
        
        logger.info("Scheduling driver tracking animation")

        def animation_logic():
            logger.info("Starting driver tracking animation after delay")
            
            if not self.driver_marker_ref.current or not self.map_ref.current:
                logger.error("Driver marker or map not ready for animation after delay.")
                return

            path_data = MAP_ROUTING_101_GRAND_HOTEL["routes"][0]["geometry"]["coordinates"]
            
            animation_points = [[lat, lon] for lon, lat in path_data]
            
            if not animation_points:
                logger.error("No coordinates found in path data")
                return

            num_points = len(animation_points)
            total_duration_sec = 20.0 
            time_per_step = total_duration_sec / num_points
            
            final_lat_lon = animation_points[-1]
            final_map_coords = map.MapLatitudeLongitude(*final_lat_lon)

            def animate_step(i):
                if i >= num_points:
                    logger.info("Animation finished")
                    
                    if self.map_ref.current:
                        self.map_ref.current.center_on(final_map_coords, 16)
                    
                    if self.polyline_layer_ref.current:
                        self.polyline_layer_ref.current.polylines = [
                            map.PolylineMarker(
                                coordinates=[
                                    final_map_coords, 
                                    map.MapLatitudeLongitude(*LOCATION_GRAND_HOTEL), 
                                ],
                                color=ft.Colors.BLUE,
                                border_stroke_width=5
                            )
                        ]
                        
                    if self.driver_marker_ref.current:
                        self.driver_marker_ref.current.coordinates = final_map_coords

                    # --- ↓↓↓ 修改點：呼叫新的 _show_driver_hotel_dialog ↓↓↓ ---
                    self._show_driver_hotel_dialog()
                    # --- ↑↑↑ 修改結束 ↑↑↑ ---
                        
                    self.page.update()
                    return
                
                current_lat, current_lon = animation_points[i]
                
                logger.debug(f"Animation step {i}: Lat={current_lat}, Lon={current_lon}")
                
                if self.driver_marker_ref.current:
                    self.driver_marker_ref.current.coordinates = map.MapLatitudeLongitude(current_lat, current_lon)
                self.map_ref.current.center_on(map.MapLatitudeLongitude(current_lat, current_lon), 16)
                self.page.update()

                threading.Timer(time_per_step, lambda: animate_step(i + 1)).start()

            animate_step(0)

        threading.Timer(0.5, animation_logic).start()

    def _show_arrival_dialog_and_navigate(self, e=None):
        """
        顯示行李送達的彈窗，並在關閉時導航回儀表板。
        """
        logger.info("準備顯示抵達彈窗...")
        
        def show_dialog():
            scan_result_text = ""
            # (假設 SCAN_RESULT_LSIT 已經在 config.py 或 constants.py 中定義)
            try:
                for baggage in SCAN_RESULT_LSIT:
                    scan_result_text += f"{baggage['size']}吋{baggage['color']}{baggage['type']} {baggage['quantity']} 件\n"
                scan_result_amount = len(SCAN_RESULT_LSIT)
            except NameError:
                logger.error("SCAN_RESULT_LSIT 未定義")
                scan_result_text = "行李資訊讀取失敗"
                scan_result_amount = 0

            # --- ↓↓↓ 1. (重要) 先宣告 dialog 變數，以便內部函式可以存取 ---
            dialog = ft.AlertDialog() 

            # --- 2. 建立一個函式，用於顯示第二階段的 "Check-in" 彈窗 ---
            def show_checkin_confirmation(d: ft.AlertDialog):
                logger.info("顯示 Check-in 確認彈窗")
                d.title = ft.Text("Check-in 成功")
                d.content = ft.Column(
                    [
                        ft.Text("圓山大飯店 已為您自動 check-in"),
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=60)
                    ],
                    # (為 Column 設定固定高度，避免彈窗大小劇烈變化)
                    height=100, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
                d.actions = [
                    ft.TextButton(
                        "完成",
                        on_click=lambda e: self.page.close(d), # 點擊 "完成" 只關閉彈窗
                        style=ft.ButtonStyle(color=ft.Colors.GREEN)
                    )
                ]
                d.actions_alignment=ft.MainAxisAlignment.CENTER
                # (on_dismiss 事件保持不變，仍會導航回 dashboard)
                d.update() # 刷新同一個彈窗的內容

            # --- 3. 設定 dialog 變數的屬性 (第一階段) ---
            dialog.modal = True
            dialog.title = ft.Text("行程結束")
            dialog.content = ft.Column(
                controls=[
                    ft.Text("您的行李已被送達目的地。", color=ft.Colors.WHITE), # (使用恆量)
                    ft.Text(scan_result_text, color=ft.Colors.WHITE),
                    ft.Text(f"總共 {scan_result_amount} 件行李送達。", color=ft.Colors.WHITE),
                    ft.Image(
                        # (假設 'baggages_hotel.jpg' 拼字正確且存在於 assets/images/)
                        src="images/baggages_hotel.jpg", 
                        width=230,
                        fit=ft.ImageFit.CONTAIN
                    ),
                ],
                alignment=ft.alignment.center,
                scroll=ft.ScrollMode.ADAPTIVE, # (使用 scroll 替代 expand)
                height=350 # (設定一個固定高度)
            )
            dialog.actions = [
                ft.TextButton(
                    "聯繫客服", 
                    on_click=lambda e: self.page.close(dialog), # 點擊只關閉
                    style=ft.ButtonStyle(color=ft.Colors.RED)
                ),
                ft.TextButton(
                    "確認無誤", 
                    on_click=lambda e: show_checkin_confirmation(dialog), # <-- 呼叫切換函式
                    style=ft.ButtonStyle(color=ft.Colors.GREEN)
                )
            ]
            dialog.actions_alignment = ft.MainAxisAlignment.END
            dialog.on_dismiss = lambda e: self._navigate_after_dialog_close("/app/user/dashboard")
            
            # --- 4. 打開第一階段的彈窗 ---
            self.page.open(dialog) 
            logger.info("抵達彈窗已顯示。")

        if self.page:
            self.page.run_thread(show_dialog) 
        else:
            logger.error("Page 不存在，無法顯示抵達彈窗。")


    def _force_stop_animation_and_redirect(self):
        """
        由 10 秒計時器觸發，強制停止動畫並顯示彈窗。
        """
        if self.animation_running:
            logger.info("10-second timer fired. Stopping animation early.")
            self.animation_running = False 
            
            self._show_arrival_dialog_and_navigate()


    def start_user_animation(self):
        
        logger.info("Scheduling user tracking animation")

        self.animation_running = False

        def animation_logic():
            logger.info("Starting user tracking animation after delay")
            
            self.animation_running = True 
            
            if not self.driver_marker_ref.current or not self.map_ref.current:
                logger.error("Driver marker or map not ready for animation after delay.")
                self.animation_running = False
                return

            threading.Timer(10.0, self._force_stop_animation_and_redirect).start()

            try:
                path_data = MAP_ROUTING_101_GRAND_HOTEL["routes"][0]["geometry"]["coordinates"]
            except Exception as e:
                logger.error(f"Failed to get path data: {e}")
                self.animation_running = False
                return
                
            animation_points = [[lat, lon] for lon, lat in path_data]
            
            if not animation_points:
                logger.error("No coordinates found in path data")
                self.animation_running = False
                return

            num_points = len(animation_points)
            total_duration_sec = 100.0 
            time_per_step = total_duration_sec / num_points
            
            final_map_coords = map.MapLatitudeLongitude(*LOCATION_GRAND_HOTEL) 

            def animate_step(i):
                
                if not self.animation_running:
                    logger.debug(f"Animation stopped externally at step {i}.")
                    return

                if i >= num_points:
                    logger.info("Animation finished normally (100s complete)")
                    
                    self.animation_running = False 
                    
                    if self.map_ref.current:
                        self.map_ref.current.center_on(final_map_coords, 14)
                    
                    if self.polyline_layer_ref.current:
                        self.polyline_layer_ref.current.polylines = [
                            map.PolylineMarker(
                                coordinates=[
                                    final_map_coords,
                                    map.MapLatitudeLongitude(*LOCATION_GRAND_HOTEL), 
                                ],
                                color=ft.Colors.BLUE,
                                border_stroke_width=5
                            )
                        ]
                        
                    if self.driver_marker_ref.current:
                        self.driver_marker_ref.current.coordinates = final_map_coords
                        
                    self._show_arrival_dialog_and_navigate()
                    return
                
                current_lat, current_lon = animation_points[i]
                
                logger.debug(f"Animation step {i}: Lat={current_lat}, Lon={current_lon}")
                
                if self.driver_marker_ref.current:
                    self.driver_marker_ref.current.coordinates = map.MapLatitudeLongitude(current_lat, current_lon)
                self.map_ref.current.center_on(map.MapLatitudeLongitude(current_lat, current_lon), 16)
                self.page.update()

                if self.animation_running: 
                    threading.Timer(time_per_step, lambda: animate_step(i + 1)).start()

            animate_step(0)

        threading.Timer(0.5, animation_logic).start()

    def stop_user_animation(self):
        """
        從外部停止動畫 (例如當 View 被銷毀時)。
        """
        logger.info("從外部停止使用者動畫 (stop_user_animation)")
        if self.animation_timer:
            self.animation_timer.cancel()
            self.animation_timer = None


    # --- App View Builders ---
    def build_hotel_app_view(self):
        email = self.page.session.get("email")
        return ft.View(
            route="/app/hotel",
            controls=[
                ft.AppBar(title=ft.Text("旅館主畫面"), bgcolor=COLOR_BG_DARK_GOLD), # (使用 config.py 中的變數)
                ft.Column([
                    ft.Text(f"歡迎, 旅館 {email}!", size=30),
                    ft.Text("這裡是旅館 App 主畫面 (下一步)")
                ])
            ]
        )


# --- 啟動 App ---
if __name__ == "__main__":
    app_instance = App()
    ft.app(
        target=app_instance.main,
        assets_dir="assets"
    )
