import datetime
import flet as ft
import flet_map as map
import logging
import random
import time
import threading

from constants import *
from config import *

# --- 恢復原始的 View 匯入 ---
from app.router import create_route_handler


DEBUG = True
if DEBUG:
    level = logging.DEBUG
    mode = "debug"
else:
    level = logging.INFO
    mode = "production"

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
        self.map_ref = ft.Ref[map.Map]()
        self.marker_layer_ref = ft.Ref[map.MarkerLayer]()
        self.polyline_layer_ref = ft.Ref[map.PolylineLayer]()
        self.driver_marker_ref = ft.Ref[map.Marker]()
        self.search_bar_ref = ft.Ref[ft.Container]()
        self.search_text_ref = ft.Ref[ft.TextField]()
        self.scan_results = 0
        self.scan_confirmed = False
        self.driver_alert_dialog = ft.Ref[ft.AlertDialog]()


    def main(self, page: ft.Page):
        # ... (main 函數保持不變) ...
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
                primary=ft.Colors.BLACK,                    # 登入畫面的 icon，被選中的文字
                on_primary=ft.Colors.WHITE,
                primary_container=ft.Colors.BLUE,
                on_primary_container=ft.Colors.GREEN,
                secondary_container=COLOR_BG_DARK_GOLD,        # selected_navigator_bar container
                on_secondary_container=ft.Colors.WHITE,     # selected_navigator_bar icon
                on_surface=ft.Colors.BLACK,                   # selected_navigator_bar的文字
                on_surface_variant=ft.Colors.GREY_500,      # 未被選中的 TextField, navigator_bar的文字
                surface_container_low=ft.Colors.ORANGE_300,     # 產生驗證碼bg
            ),
            
            # --- 其他 Theme (保持不變) ---
            date_picker_theme=ft.DatePickerTheme(
                bgcolor=ft.Colors.WHITE,                    # DatePicker 彈窗是 "Surface" (白色)
                range_picker_bgcolor=ft.Colors.PINK,       # RangePicker 彈窗是 "Surface" (白色)
                header_bgcolor=COLOR_BG_LIGHT_TAN,
                locale=ft.Locale("zh", "TW")
            ),

            # color_scheme=ft.ColorScheme(
            #     # --- 主要 (Primary) 色系 ---
            #     primary=ft.Colors.BLACK,                    # 登入畫面的 icon，被選中的文字
            #     on_primary=ft.Colors.BLACK,                   # (2) 在「主要顏色」上的文字/圖示
            #     primary_container=ft.Colors.BLACK,          # (3) "次要" 的主要顏色容器 (例如 FAB)
            #     on_primary_container=ft.Colors.BLACK,       # (4) 在 "Primary Container" 上的文字/圖示

            #     # --- 次要 (Secondary) 色系 ---
            #     secondary=ft.Colors.GREEN,                  # (5) 次要顏色 (例如選中的 FilterChip)
            #     on_secondary=ft.Colors.GREEN,                 # (6) 在「次要顏色」上的文字/圖示
            #     secondary_container=ft.Colors.GREEN,            # selected_navigator_bar container
            #     on_secondary_container=ft.Colors.GREEN,         # selected_navigator_bar icon

            #     # --- 第三 (Tertiary) 色系 ---
            #     tertiary=ft.Colors.BLUE,                    # (9) 第三顏色
            #     on_tertiary=ft.Colors.BLUE,                  # (10) 在「第三顏色」上的文字/圖示
            #     tertiary_container=ft.Colors.BLUE,          # (11)
            #     on_tertiary_container=ft.Colors.BLUE,     # (12)

            #     # --- 錯誤 (Error) 色系 ---
            #     error=ft.Colors.ORANGE,                # (13) 錯誤顏色
            #     on_error=ft.Colors.ORANGE,                     # (14) 在「錯誤顏色」上的文字/圖示
            #     error_container=ft.Colors.ORANGE,      # (15)
            #     on_error_container=ft.Colors.ORANGE, # (16)

            #     # --- 背景 (Background) ---
            #     background=ft.Colors.PURPLE,                # (17) 【Page 背景】(App 最底層)
            #     on_background=ft.Colors.PURPLE,             # (18) 在 "Background" 上的文字/圖示

            #     # --- 表面 (Surface) ---
            #     on_surface=ft.Colors.RED,                   # selected_navigator_bar的文字

            #     # --- 表面變體 (Surface Variant) ---
            #     surface_variant=ft.Colors.RED,             # (21) 表面變體 (例如 TextField 邊框, Chip 背景)
            #     on_surface_variant=ft.Colors.GREY_700,             # 未被選中的 TextField, navigator_bar的文字

            #     # --- 表面容器 (Surface Container) (Material 3 核心) ---
            #     surface_container_low=ft.Colors.YELLOW,     # 產生驗證碼bg
            # ),
            
            # # --- 其他 Theme (保持不變) ---
            # date_picker_theme=ft.DatePickerTheme(
            #     bgcolor=ft.Colors.WHITE, # DatePicker 彈窗是 "Surface" (白色)
            #     locale=ft.Locale("zh", "TW")
            # ),
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
        # --- 模式 1: 偵錯模式 ---
        if self.mode == "debug":
            logger.warning("在偵錯模式下登入，已跳過驗證。")
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", self.login_username.current.value or "demo@user.com")
            
            # *** 修改點：登入後去 /app/user (主外殼) ***
            self.page.go(f"/app/{role}")
            return
        
        # --- 模式 2: 正式模式 (省略) ---
        logger.info("正式模式登入驗證 (未實作)")

        
    # === Demo 流程 Handlers ===
    
    # --- 恢復 handle_nav_bar_change ---
    def handle_nav_bar_change(self, e):
        """
        處理「底部導航列」的點擊事件
        """
        selected_index = int(e.data) 
        content = None
        
        # 清除地圖搜尋框 (如果有的話)
        if self.search_bar_ref.current:
            self.search_bar_ref.current.visible = False

        if selected_index == 0:
            logger.info("導航到「更多」頁面")
            self.page.go("/app/user/more")
        elif selected_index == 1:
            logger.info("導航到「即時預約」Demo 頁面")
            self.page.go("/app/user/booking_instant") # 這是一個獨立的 View
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
            self.page.go("/app/user/dashboard") # 預設返回
    

    # --- 以下 Demo 相關的 Handlers 保持不變 ---

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
        logger.info("Navigating to map selection for pickup")
        self.page.go("/app/user/select_pickup")

    def handle_select_location_dropoff(self, e):
        logger.info("Navigating to map selection for dropoff")
        self.page.go("/app/user/select_dropoff")

    def handle_search_location(self, e):
        
        search_query = self.search_text_ref.current.value
        logger.info(f"Handling search for: {search_query}")
        
        if "板橋" in search_query:
            self._update_map_location(LOCATION_BANQIAO_STATION, "板橋車站", self.current_search_mode)
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
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.session.set("role", "driver")
            self.page.go("/app/driver")

        success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("預約成功！"),
            content=ft.Text("正在為您尋找司機..."),
            actions=[
                ft.TextButton("確認", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(success_dialog)
        self.page.update()

    def handle_show_driver_alert(self):
        
        logger.info("Showing driver alert")
        
        if not self.driver_alert_dialog.current:
            self.driver_alert_dialog.current = ft.AlertDialog(
                ref=self.driver_alert_dialog,
                modal=True,
                title=ft.Text("新的行李預約"),
                content=ft.Text("您有新的行李預約，車資分潤為100元，預估行車時間 50 分鐘"),
                actions=[
                    ft.TextButton("取消", on_click=self.handle_driver_reject, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ft.TextButton("接單", on_click=self.handle_driver_accept, style=ft.ButtonStyle(color=ft.Colors.GREEN)),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            self.page.open(self.driver_alert_dialog.current)
        self.page.update()

    def handle_driver_reject(self, e):
        
        logger.info("Driver rejected order")
        self.page.close(self.driver_alert_dialog.current)
        self.page.update()

    def handle_driver_accept(self, e):
        
        logger.info("Driver accepted order")
        self.page.close(self.driver_alert_dialog.current)
        self.page.update()
        self.page.go("/app/driver/tracking")
        
    def start_driver_animation(self):
        
        logger.info("Starting driver tracking animation")
        
        if not self.driver_marker_ref.current or not self.map_ref.current:
            logger.error("Driver marker or map not ready for animation")
            return

        start_lat, start_lon = LOCATION_TAIPEI_CITY_HALL
        end_lat, end_lon = LOCATION_TAIPEI_101
        steps = 5
        
        def animate_step(i):
            if i > steps:
                logger.info("Animation finished")
                if self.map_ref.current:
                    self.map_ref.current.center = map.MapLatitudeLongitude(*LOCATION_TAIPEI_101)
                    self.map_ref.current.zoom = 14
                if self.polyline_layer_ref.current:
                    self.polyline_layer_ref.current.polylines = [
                        map.PolylineMarker(
                            coordinates=[
                                map.MapLatitudeLongitude(*LOCATION_TAIPEI_101),
                                map.MapLatitudeLongitude(*LOCATION_BANQIAO_STATION),
                            ],
                            color=ft.Colors.BLUE,
                            border_stroke_width=5
                        )
                    ]
                if self.driver_marker_ref.current:
                    self.driver_marker_ref.current.coordinates = map.MapLatitudeLongitude(*LOCATION_TAIPEI_101)
                self.page.update()
                return

            t = i / steps
            current_lat = start_lat + (end_lat - start_lat) * t
            current_lon = start_lon + (end_lon - start_lon) * t
            
            logger.debug(f"Animation step {i}: Lat={current_lat}, Lon={current_lon}")
            
            if self.driver_marker_ref.current:
                self.driver_marker_ref.current.coordinates = map.MapLatitudeLongitude(current_lat, current_lon)
                self.page.update()

            threading.Timer(1.0, lambda: animate_step(i + 1)).start()

        animate_step(1)


    # --- App View Builders ---
    def build_hotel_app_view(self):
        # ... (旅館介面 - 未變) ...
        email = self.page.session.get("email")
        return ft.View(
            route="/app/hotel",
            controls=[
                ft.AppBar(title=ft.Text("旅館主畫面"), bgcolor=ft.Colors.AMBER),
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
