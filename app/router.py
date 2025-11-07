import logging
from typing import TYPE_CHECKING

# --- View 匯入 ---
from views.login.splash_view import build_splash_view
from views.login.login_view import build_login_view
from views.user.user_home_page import build_user_app_view
from views.user.user_booking_instant import build_instant_booking_view

# --- 從 app/ 子模組匯入 ---
from app.scan import build_scan_view, build_scan_results_view
from app.order import build_confirm_order_view
from app.driver import build_driver_home_view, build_driver_tracking_view

if TYPE_CHECKING:
    from main import App

logger = logging.getLogger(__name__)

def create_route_handler(app_instance: 'App'):
    """
    這是一個「工廠函式」。
    它接收 App 實例，並「返回」一個 Flet 可以使用的路由處理函式。
    """

    def on_route_change(route_event): # <--- 這才是 Flet 實際呼叫的函式
        """
        這是真正的路由處理常式。
        它可以透過「閉包」存取外層的 app_instance。
        """
        page = app_instance.page # 從 app_instance 取得 page
        
        page.views.clear()
        logger.info(f"Navigating to route: {page.route}")
        
        # --- 路由 1: 啟動畫面 ---
        if page.route == "/splash":
            page.views.append(build_splash_view(app_instance))

        # --- 路由 2: 登入表單 ---
        elif page.route.startswith("/login/"):
            role_key = page.route.split("/")[-1]
            if role_key != "user":
                role_key = "user"
            page.views.append(build_login_view(app_instance, role_key))
        
        # --- 路由 3: 登入後的 App ---
        elif page.session.get("logged_in"):
            role = page.session.get("role")
            
            # --- 使用者 (旅客) 流程 ---
            if role == "user":
                if page.route == "/app/user":
                    page.views.append(build_user_app_view(app_instance))
                elif page.route == "/app/user/booking_instant":
                    page.views.append(build_instant_booking_view(app_instance))
                elif page.route == "/app/user/scan":
                    page.views.append(build_scan_view(app_instance))
                elif page.route == "/app/user/scan_results":
                    page.views.append(build_scan_results_view(app_instance))
                elif page.route == "/app/user/confirm_order":
                    page.views.append(build_confirm_order_view(app_instance))
                else:
                    page.go("/app/user")
            
            # --- 司機流程 ---
            elif role == "driver":
                if page.route == "/app/driver":
                    page.views.append(build_driver_home_view(app_instance))
                    app_instance.handle_show_driver_alert()
                elif page.route == "/app/driver/tracking":
                    page.views.append(build_driver_tracking_view(app_instance))
                    app_instance.start_driver_animation()
                else:
                    page.go("/app/driver")

            # --- 旅館流程 ---
            elif role == "hotel":
                page.views.append(app_instance.build_hotel_app_view())
            
            else:
                page.go("/login/user")
        
        # --- 預設 (未登入) ---
        else:
            page.go("/splash")

        page.update()

    # *** 關鍵：返回「函式本身」，而不是呼叫它 ***
    return on_route_change