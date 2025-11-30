import flet as ft
import logging
from typing import TYPE_CHECKING

# --- View 匯入 ---
from views.login.splash_view import build_splash_view
from views.login.login_view import build_login_view
from views.login.splash_view_to_user import build_splash_to_user_view
from views.login.splash_view_to_user2 import build_splash_to_user_view2
from views.login.splash_view_to_driver import build_splash_to_driver_view
from views.login.splash_view_to_hotel import build_splash_to_hotel_view

from views.user.user_home_page_content import build_dashboard_view
from views.user.user_home_page_more_content import build_more_view
from views.user.user_instant_booking import build_instant_booking_view
from views.user.user_previous_booking import build_previous_booking_view
from views.user.user_supporting import build_support_view
from views.user.map_view import build_map_view
from views.user.user_history_refactored import build_history_view
from views.user.user_vehicle_selection import build_vehicle_selection_view

# --- 從 app/ 子模組匯入 ---
from app.user import build_user_tracking_view
from app.scan import build_scan_view, build_scan_results_view
from app.driver import build_driver_home_view, build_driver_tracking_view_101, build_driver_tracking_view_hotel, build_scan_view as build_driver_scan_view, build_scan_results_view as build_driver_scan_results_view
from app.hotel import build_hotel_view, build_scan_view as build_hotel_scan_view, build_scan_results_view as build_hotel_scan_results_view


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
        page = app_instance.page
        logger.info(f"Navigating to route: {page.route}")
        
        if page.route == "/app/user/map" or page.route == "/app/user/instant_booking":
            page.update()
        else:
            page.views.clear()
        
        # --- 路由 1: 啟動畫面 ---
        if page.route == "/splash":
            page.views.append(build_splash_view(app_instance))
        elif page.route == "/splash/user":
            page.views.append(build_splash_to_user_view(app_instance))
        elif page.route == "/splash/user2":
            page.views.append(build_splash_to_user_view2(app_instance))
        elif page.route == "/splash/dirver":
            page.views.append(build_splash_to_driver_view(app_instance))
        elif page.route == "/splash/hotel":
            page.views.append(build_splash_to_hotel_view(app_instance))
        
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
        elif page.route == "/app/user/instant_booking":
            page.views.append(build_instant_booking_view(app_instance))
        elif page.route == "/app/user/confirm_order":
            page.views.append(build_instant_booking_view(app_instance))
        elif page.route == "/app/user/previous_booking":
            page.views.append(build_previous_booking_view(app_instance))
        elif page.route == "/app/user/previous_booking_confirm":
            page.views.append(build_previous_booking_view(app_instance))
        elif page.route == "/app/user/support":
            page.views.append(build_support_view(app_instance))
        elif page.route == "/app/user/scan":
            page.views.append(build_scan_view(app_instance))
        elif page.route == "/app/user/scan_results":
            page.views.append(build_scan_results_view(app_instance))
        elif page.route == "/app/user/history":
            page.views.append(build_history_view(app_instance))
        elif page.route == "/app/user/vehicle_selection":
            page.views.append(build_vehicle_selection_view(app_instance))
        elif page.route.startswith("/app/user/map/"):
            map_target_view = ft.View(route=page.route)
            page.views.append(build_map_view(app_instance, map_target_view))
        elif page.route == "/app/user/current_order":
            page.views.append(build_user_tracking_view(app_instance))
            app_instance.start_user_animation()
            
        # --- 司機流程 ---
        elif page.route == "/app/driver":
            page.views.append(build_driver_home_view(app_instance))
            app_instance.handle_show_driver_alert()
        elif page.route == "/app/driver/tracking_101":
            page.views.append(build_driver_tracking_view_101(app_instance))
            app_instance.start_driver_animation_101()
        elif page.route == "/app/driver/tracking_hotel":
            page.views.append(build_driver_tracking_view_hotel(app_instance))
            app_instance.start_driver_animation_hotel()
        elif page.route == "/app/driver/scan":
            page.views.append(build_driver_scan_view(app_instance))
        elif page.route == "/app/driver/scan_results":
            page.views.append(build_driver_scan_results_view(app_instance))


        # --- 旅館流程 ---
        elif page.route == "/app/hotel":
            page.views.append(build_hotel_view(app_instance))
        elif page.route == "/app/hotel/scan":
            page.views.append(build_hotel_scan_view(app_instance))
        elif page.route == "/app/hotel/scan_results":
            page.views.append(build_hotel_scan_results_view(app_instance))
        
        # --- 預設 (未登入) ---
        else:
            page.go("/splash")

        page.update()

    # *** 關鍵：返回「函式本身」，而不是呼叫它 ***
    return on_route_change