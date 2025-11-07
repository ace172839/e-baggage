import logging
from typing import TYPE_CHECKING

# --- View 匯入 ---
from views.login.splash_view import build_splash_view
from views.login.login_view import build_login_view
from views.user.user_home_page_content import build_dashboard_view
from views.user.user_home_page_more_content import build_more_view
from views.user.user_booking_instant import build_instant_booking_view, build_instant_booking_confirm_view
from views.user.user_booking_previous import build_previous_booking_view, build_previous_booking_confirm_view
from views.user.user_supporting import build_support_view
from views.user.map_view import build_map_view
from views.user.user_history import history_view

# --- 從 app/ 子模組匯入 ---
from app.scan import build_scan_view, build_scan_results_view
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
            page.views.append(build_login_view(app_instance, role_key))
        
        # --- 旅客流程 ---
        elif page.route == "/app/user":
            page.go("/app/user/dashboard")
        elif page.route == "/app/user/dashboard":
            page.views.append(build_dashboard_view(app_instance))
        elif page.route == "/app/user/more":
            page.views.append(build_more_view(app_instance))
        elif page.route == "/app/user/booking_instant":
            page.views.append(build_instant_booking_view(app_instance))
        elif page.route == "/app/user/confirm_order":
            page.views.append(build_instant_booking_confirm_view(app_instance))
        elif page.route == "/app/user/booking_previous":
            page.views.append(build_previous_booking_view(app_instance))
        elif page.route == "/app/user/booking_previous_confirm":
            page.views.append(build_previous_booking_confirm_view(app_instance))
        elif page.route == "/app/user/support":
            page.views.append(build_support_view(app_instance))
        elif page.route == "/app/user/scan":
            page.views.append(build_scan_view(app_instance))
        elif page.route == "/app/user/scan_results":
            page.views.append(build_scan_results_view(app_instance))
        elif page.route == "/app/user/history":
            page.views.append(history_view(app_instance.page))
        elif page.route == "/app/user/map":
            page.views.append(build_map_view(app_instance))
            
        # --- 司機流程 ---
        elif page.route == "/app/driver":
            page.views.append(build_driver_home_view(app_instance))
            app_instance.handle_show_driver_alert()
        elif page.route == "/app/driver/tracking":
            page.views.append(build_driver_tracking_view(app_instance))
            app_instance.start_driver_animation()

        # --- 旅館流程 ---
        # elif role == "hotel":
        #     page.views.append(app_instance.build_hotel_app_view())
        
        # --- 預設 (未登入) ---
        else:
            page.go("/splash")

        page.update()

    # *** 關鍵：返回「函式本身」，而不是呼叫它 ***
    return on_route_change