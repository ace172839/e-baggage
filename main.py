import datetime
import flet as ft
import logging
import random
# from db_helpers import init_database


from constants import *
from config import WINDOW_HEIGHT, WINDOW_WIDTH

from views.login.splash_view import build_splash_view
from views.login.role_select_view import build_role_select_view
from views.login.login_view import build_login_view

from views.user.user_home_page import build_user_app_view
from views.user.user_home_page_content import build_dashboard_content
from views.user.user_home_page_more_content import build_more_content
from views.user.user_booking_instant import build_instant_booking_content
from views.user.user_booking_previous import build_roundtrip_content
from views.user.user_supporting import build_support_content


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
        只保留「狀態」和「Refs」，UI 邏輯已移出。
        """
        self.page = None

        # 登入表單的 Refs (用於讀取數值)
        self.login_username = ft.Ref[ft.TextField]()
        self.login_password = ft.Ref[ft.TextField]()
        self.login_captcha = ft.Ref[ft.TextField]()
        self.login_error_text = ft.Ref[ft.Text]()
        self.captcha_text = ft.Ref[ft.Text]() # 驗證碼文字
        self.mode = mode
        # self.mode = "production"

        self.main_content_ref = ft.Ref[ft.Container]()

    def main(self, page: ft.Page):
        """
        Flet App 的主入口點 (Entrypoint)
        """
        self.page = page
        self.page.title = "e-baggage"

        # --- 設定視窗為手機尺寸 ---
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.resizable = False
        self.page.window.always_on_top = True
        # -------------------------

        # --- 字體設定 ---
        self.page.fonts = {
            "Noto Sans TC": "NotoSansTC-Regular.ttf",
            "Noto Serif TC": "NotoSerifTC-Regular.ttf",
        }
        self.page.theme = ft.Theme(
            font_family="Noto Sans TC",
            color_scheme=ft.ColorScheme(
                #primary=COLOR_TEXT_DARK,
                secondary=COLOR_TEXT_DARK,
                surface=COLOR_TEXT_DARK,
                on_surface=COLOR_TEXT_DARK,
                surface_container=COLOR_TEXT_DARK,
            ),
            icon_theme=ft.IconTheme(
                color=COLOR_ICON_WHITE
            )
        )
        
        # --- 初始化 ---
        # 1. 初始化資料庫 (暫時註解)
        # try:
        #     init_database()
        # except Exception as e:
        #     print(f"資料庫初始化失敗: {e}")

        # 2. 設置 App 的路由系統
        self.page.on_route_change = self.on_route_change
        
        # 3. 啟動 App
        self.page.go("/splash")

    def on_route_change(self, route):
        """
        App 的主路由器 (Router)
        現在它呼叫外部的 view builders
        """        
        self.page.views.clear()
        
        # --- 路由 1: 啟動畫面 ---
        if self.page.route == "/splash":
            self.page.views.append(build_splash_view(self)) # 傳入 'self' (App 實例)

        # --- 路由 2: 角色選擇畫面 ---
        elif self.page.route == "/role_select":
            self.page.views.append(build_role_select_view(self)) # 傳入 'self'

        # --- 路由 3: 登入表單 ---
        elif self.page.route.startswith("/login/"):
            role_key = self.page.route.split("/")[-1]
            self.page.views.append(build_login_view(self, role_key)) # F傳入 'self' 和 'role'
        
        # --- 路由 4: 登入後的 App 主畫面 ---
        elif self.page.session.get("logged_in"):
            role = self.page.session.get("role")
            
            if role == "user" and self.page.route.startswith("/app/user"):
                # 如果是使用者，並且路由是 /app/user/...
                # 我們就顯示「App 主殼」
                self.page.views.append(build_user_app_view(self))
            
            elif role == "hotel":
                # (旅館介面)
                self.page.views.append(self.build_hotel_app_view())
            
            else:
                # 登入了，但路由不對，導回角色選擇
                self.page.views.append(build_role_select_view(self))
        
        # --- 預設 ---
        else:
            self.page.views.append(build_role_select_view(self)) # 傳入 'self'

        self.page.update()



    # --- 處理 (Handle) 邏輯 ---
    # 這些「控制器」邏輯保留在主類別中
    
    def login_view_handle_regenerate_captcha(self, e):
        """處理驗證碼重新產生事件"""
        new_code = str(random.randint(10000, 99999))
        self.captcha_text.current.value = new_code
        self.page.update()

    def _show_login_error(self, message: str):
        """輔助函式：在登入表單上顯示錯誤訊息"""
        if self.login_error_text.current:
            self.login_error_text.current.value = message
            self.login_error_text.current.visible = True
            self.page.update()

    def login_view_handle_login(self, e, role: str):
        """處理登入按鈕點擊事件，包含驗證邏輯"""
        
        # --- 模式 1: 偵錯模式 (跳過所有驗證) ---
        if self.mode == "debug":
            logger.warning("在偵錯模式下登入，已跳過驗證。")
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", self.login_username.current.value)
            self.page.go(f"/app/{role}")
            return
        
        # --- 模式 2: 正式模式 (執行完整驗證) ---
        
        # 提取表單數值
        user_email = self.login_username.current.value
        password = self.login_password.current.value
        captcha_input = self.login_captcha.current.value
        captcha_correct = self.captcha_text.current.value
        
        # 驗證 1: 驗證碼
        if captcha_input != captcha_correct:
            self._show_login_error("驗證碼錯誤，請重新輸入。")
            return
        
        # 驗證 2: 帳號
        if not user_email:
            self._show_login_error("請輸入您的帳號。")
            return
        
        # 驗證 3: 密碼
        if not password or not (8 <= len(password) <= 10):
            self._show_login_error("請輸入 8-10 位數的有效密碼。")
            return
        
        # --- 所有驗證通過 ---
        logger.info(f"使用者 {user_email} 成功登入，角色為 {role}")
        self.page.session.set("logged_in", True)
        self.page.session.set("role", role)
        self.page.session.set("email", user_email)
        self.page.go(f"/app/{role}")

    def handle_scan_baggage(self):
        """
        處理「掃描行李」按鈕點擊事件。
        """
        logger.info("AI 行李掃描功能啟動！")
        self.page.add(ft.SnackBar(ft.Text("AI 掃描功能 (下一步)"), open=True))
        
    def handle_nav_bar_change(self, e):
        """
        處理「底部導航列」的點擊事件
        """
        selected_index = int(e.data) 
        content = None

        if selected_index == 0:
            content = build_more_content(self)
            logger.info("切換到「更多」列表")
        elif selected_index == 1:
            content = build_instant_booking_content(self)
            logger.info("切換到「即時預約」")
        elif selected_index == 2:
            content = build_dashboard_content(self)
            logger.info("切換到「首頁」儀表板")
        elif selected_index == 3:
            content = build_roundtrip_content(self)
            logger.info("切換到「事先預約」")
        elif selected_index == 4:
            content = build_support_content(self)
            logger.info("切換到「客服」")
        else:
            logger.error(f"Unknown selected index: {selected_index}")
            return
        
        # 更新主內容區域
        if self.main_content_ref.current:
            self.main_content_ref.current.content = content
            self.main_content_ref.current.update()
        else:
            logger.error("main_content_ref 尚未綁定！")

    # --- App View Builders ---
    
    def build_user_app_view(self):
        return build_user_app_view(self)

    def build_hotel_app_view(self):
        # ... (旅館介面) ...
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