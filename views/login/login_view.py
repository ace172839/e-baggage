import flet as ft
import random
from constants import *

def build_login_view(app_instance: 'App', role: str) -> ft.View:
    """
    建立「登入表單」的 UI
    我們傳入 'app_instance' 來存取主類別中的 Refs 和 handle_login 方法
    """
    
    # 根據角色，決定顯示的中文
    role_map = {
        "user": ("顧客端", ft.Icons.PERSON_ROUNDED),
        "driver": ("司機端", ft.Icons.SUPPORT_AGENT_ROUNDED),
        "hotel": ("旅店端", ft.Icons.HOTEL_ROUNDED)
    }
    role_text, role_icon = role_map.get(role, ("登入", ft.Icons.LOCK))

    return ft.View(
        route=f"/login/{role}",
        controls=[
            ft.Container(
                width=350,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Image(
                                    src="images/logo.png",
                                    width=100,
                                    height=100,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        ft.Container(
                            width=350,
                            padding=30,
                            border_radius=20,
                            bgcolor=COLOR_BG_LIGHT_TAN,
                            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK26),
                            content=ft.Column(
                                controls=[
                                    # 頂部 Logo

                                    
                                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                                    # 角色標題
                                    ft.Row([
                                        ft.Icon(role_icon, size=40),
                                        ft.Text(role_text, size=36, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                                    ]),
                                    
                                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                                    
                                    # 表單
                                    ft.TextField(
                                        ref=app_instance.login_username,
                                        label="帳號:",
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=8,
                                    ),
                                    ft.TextField(
                                        ref=app_instance.login_password,
                                        label="密碼:",
                                        password=True,
                                        can_reveal_password=True,
                                        helper_text="請輸入8-10英文大小組合與數字",
                                        helper_style=ft.TextStyle(color=ft.Colors.RED_300),
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=8,
                                    ),
                                    ft.TextField(
                                        ref=app_instance.login_captcha,
                                        label="驗證碼:",
                                        bgcolor=ft.Colors.WHITE,
                                        border_radius=8,
                                    ),
                                    
                                    # 驗證碼圖片
                                    ft.Row([
                                        ft.ElevatedButton(
                                            text="重產識別碼",
                                            color=ft.Colors.WHITE,
                                            height=40,
                                            on_click=app_instance.login_view_handle_regenerate_captcha
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                ref=app_instance.captcha_text,
                                                value=str(random.randint(10000, 99999)),
                                                size=24, color=ft.Colors.BLACK38,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                            bgcolor=ft.Colors.GREY_300,
                                            padding=10,
                                            border_radius=6,
                                            expand=True,
                                            alignment=ft.alignment.center
                                        )
                                    ]),
                                    
                                    ft.Text(ref=app_instance.login_error_text, color=ft.Colors.RED_600, visible=False),
                                    
                                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            "登入", 
                                            on_click=lambda e: app_instance.login_view_handle_login(e, role),
                                            height=45,
                                            width=100,
                                            bgcolor=COLOR_BRAND_YELLOW,
                                            color=COLOR_TEXT_DARK,
                                            expand=True
                                        ),
                                        alignment=ft.alignment.center
                                    )
                                ],
                            ),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ],
        bgcolor=COLOR_BG_DARK_GOLD,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )