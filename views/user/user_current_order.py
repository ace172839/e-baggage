import flet as ft
import threading
import time
from views.common.assistant import build_ai_fab
from services import SimulationService

class CurrentOrderView():
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.running = False
        self.simulation_service = SimulationService()
        
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
        
        # 使用 SimulationService 生成司機資訊
        driver_data = self.simulation_service.generate_driver_info()
        
        # 司機資訊
        self.driver_info = ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"司機姓名：{driver_data['name']}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"車牌號碼：{driver_data['license_plate']}", size=16),
                    ft.Text(f"司機手機：{driver_data['phone']}", size=16),
                    ft.Text(f"預估抵達：{driver_data['estimated_arrival']}", size=16, color=ft.Colors.BLUE_600),
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
            
            # 使用 SimulationService 計算新位置
            current_left = self.car_icon.left or 50
            current_top = self.car_icon.top or 50
            new_left, new_top = self.simulation_service.calculate_next_position(
                current_left, current_top, max_left, max_top
            )
                
            self.car_icon.left = new_left
            self.car_icon.top = new_top
            
            try:
                self.update()
            except Exception as e:
                # 視圖可能已卸載
                print(f"Error updating car position: {e}")
                break