import flet as ft
import threading
import time
import random
from views.common.assistant import build_ai_fab

class CurrentOrderView():
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.running = False
        
        # 汽車圖示
        self.car_icon = ft.Icon(
            name=ft.Icons.DIRECTIONS_CAR,
            color=ft.Colors.BLUE_700,
            size=40,
            left=50,
            top=50,
            animate_position=ft.Animation.curve(1000, ft.AnimationCurve.LINEAR)
        )
        
        # 導航地圖
        self.map_view = ft.Stack(
            [
                ft.Image(
                    src="https://placehold.co/800x600/c0f0c0/333?text=從台北101到板橋",
                    width=page.width,
                    fit=ft.ImageFit.COVER
                ),
                self.car_icon,
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.BLACK,
                    bgcolor=ft.Colors.WHITE70,
                    on_click=lambda _: self.page.go("/splash/hotel"),
                    top=10,
                    left=10
                )
            ],
            height=page.height * 0.6
        )
        
        # 司機資訊
        self.driver_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text("司機姓名：王小明", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("車牌號碼：ABC-1234", size=16),
                    ft.Text("司機手機：0912345678", size=16),
                    ft.Text("預估抵達：50分鐘", size=16, color=ft.Colors.BLUE_600),
                ],
                spacing=10
            ),
            padding=20,
            expand=True,
            bgcolor=ft.Colors.WHITE
        )

    def build(self):
        return ft.Column(
            [
                self.map_view,
                self.driver_info
            ],
            spacing=0,
            expand=True
        )

    def did_mount(self):
        self.running = True
        self.thread = threading.Thread(target=self.simulate_movement, args=(), daemon=True)
        self.thread.start()

    def will_unmount(self):
        self.running = False

    def simulate_movement(self):
        max_left = self.page.width - 80 if self.page.width else 300
        max_top = (self.page.height * 0.6) - 80 if self.page.height else 400
        
        while self.running:
            time.sleep(2)
            if not self.running:
                break
            
            # 隨機往前移動
            new_left = (self.car_icon.left or 50) + random.randint(10, 30)
            new_top = (self.car_icon.top or 50) + random.randint(5, 15)
            
            if new_left > max_left:
                new_left = 50
            if new_top > max_top:
                new_top = 50
                
            self.car_icon.left = new_left
            self.car_icon.top = new_top
            
            try:
                self.update()
            except Exception as e:
                # 視圖可能已卸載
                print(f"Error updating car position: {e}")
                break