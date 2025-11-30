import flet as ft
import json
import logging
from datetime import datetime, date
from models.trip import TripConfiguration, HotelStaySegment

logger = logging.getLogger(__name__)
 

class PreviousBookingController:
    def __init__(self, app_instance):
        self.app = app_instance
        self.page = app_instance.page
        
        # 每次進入 instant_booking, previous_booking 都是一個新的 trip
        self.trip_config = None
        self._init_new_trip()
        
        self.current_step = 1
        self.view = None
        
        # 用於日期選擇器的暫存引用
        self._temp_date_target = None 
        self._temp_segment_index = None
        self._temp_is_start_date = True

        # 初始化 DatePicker
        self.date_picker = ft.DatePicker(
            on_change=self._on_date_picked,
            date_picker_mode=ft.DatePickerMode.DAY
        )
    
    def _init_new_trip(self):
        """創建一個新的 previous booking trip"""
        self.trip_config = TripConfiguration()
        self.trip_config.segments = []
        logger.info("已創建新的 previous booking trip")

    def bind_view(self, view):
        self.view = view

    # --- Step 1: Landing Page Actions ---

    def set_start_date(self, start: date):
        logger.info(f"設定開始日期: {start}")
        self.trip_config.total_start_date = start.date() if hasattr(start, 'date') else start
    def set_end_date(self, end: date):
        logger.info(f"設定結束日期: {end}")
        self.trip_config.total_end_date = end.date() if hasattr(end, 'date') else end
    
    def _init_first_segment(self):
        """進入 Planning 時，自動建立第一段空白住宿"""
        self.trip_config.segments = []
        first_seg = HotelStaySegment(
            check_in_date=self.trip_config.total_start_date, # 預設第一天入住
            check_out_date=None,
            hotel_name=""
        )
        self.trip_config.segments.append(first_seg)

    def go_to_planning(self, e):
        if not self.trip_config.total_start_date or not self.trip_config.total_end_date:
            self.show_snack("請先選擇完整的旅程日期")
            return
        
        if self.trip_config.total_end_date <= self.trip_config.total_start_date:
            self.show_snack("結束日期必須晚於開始日期")
            return

        # 只在第一次進入或 segments 為空時初始化
        if not self.trip_config.segments:
            self._init_first_segment()
        self.current_step = 2
        self.view.update_view()

    # --- Step 2: Planning Actions (Dynamic Segments) ---

    def open_date_picker(self, segment_index, is_start_date):
        """開啟日期選擇器"""
        self._temp_segment_index = segment_index
        self._temp_is_start_date = is_start_date
        
        # 設定可選範圍（限制在旅程日期範圍內）
        current_seg = self.trip_config.segments[segment_index]
        
        # 設定日期選擇器的範圍
        self.date_picker.first_date = self.trip_config.total_start_date
        self.date_picker.last_date = self.trip_config.total_end_date
        
        if is_start_date and segment_index > 0:
            # 如果不是第一段，開始日期不能早於上一段的退房日期
            prev_seg = self.trip_config.segments[segment_index - 1]
            if prev_seg.check_out_date:
                self.date_picker.first_date = prev_seg.check_out_date
        
        self.page.open(self.date_picker)

    def _on_date_picked(self, e):
        """處理日期選擇回調"""
        if e.control.value:
            picked_date = e.control.value.date()
            idx = self._temp_segment_index
            seg = self.trip_config.segments[idx]

            if self._temp_is_start_date:
                seg.check_in_date = picked_date
            else:
                # 驗證：退房日必須晚於入住日
                if seg.check_in_date and picked_date <= seg.check_in_date:
                    self.show_snack("退房日期必須晚於入住日期")
                    return
                seg.check_out_date = picked_date
            
            self.view.update_view()

    def update_hotel_name(self, index, name):
        self.trip_config.segments[index].hotel_name = name
        # 這裡不需 update_view，因為 TextField 是輸入框

    def add_next_segment(self, current_index):
        """當使用者點擊「確認並新增下一段」"""
        logger.info(f"add_next_segment called for index {current_index}")
        current_seg = self.trip_config.segments[current_index]

        # 1. 驗證當前段落是否填寫完整
        if not current_seg.is_complete:
            missing_fields = []
            if not current_seg.check_in_date:
                missing_fields.append("入住日期")
            if not current_seg.check_out_date:
                missing_fields.append("退房日期")
            if not current_seg.hotel_name:
                missing_fields.append("飯店名稱")
            self.show_snack(f"請完整填寫當前住宿資訊：{', '.join(missing_fields)}")
            return

        # 2. 鎖定當前段落
        current_seg.is_locked = True
        logger.info(f"Segment {current_index} locked")

        # 3. 檢查是否已經覆蓋到總旅程結束日期
        if current_seg.check_out_date >= self.trip_config.total_end_date:
            self.show_snack("行程規劃已完成 (已達旅程結束日期)")
            self.view.update_view()
            return

        # 4. 創建下一段
        new_seg = HotelStaySegment(
            check_in_date=current_seg.check_out_date, # 自動銜接：上一段退房 = 這一段入住
            check_out_date=None,
            hotel_name=""
        )
        self.trip_config.segments.append(new_seg)
        logger.info(f"New segment created. Total segments: {len(self.trip_config.segments)}")
        self.view.update_view()

    def remove_last_segment(self, e):
        """刪除最後一段 (如果想重填)"""
        if len(self.trip_config.segments) > 1:
            self.trip_config.segments.pop()
            # 解鎖前一段
            self.trip_config.segments[-1].is_locked = False
            self.view.update_view()

    def go_to_confirm(self, e):
        logger.info("go_to_confirm called")
        # 最終驗證
        last_seg = self.trip_config.segments[-1]
        
        logger.info(f"Last segment: check_in={last_seg.check_in_date}, check_out={last_seg.check_out_date}, hotel={last_seg.hotel_name}")
        logger.info(f"Last segment is_complete: {last_seg.is_complete}")
        
        if not last_seg.is_complete:
            missing_fields = []
            if not last_seg.check_in_date:
                missing_fields.append("入住日期")
            if not last_seg.check_out_date:
                missing_fields.append("退房日期")
            if not last_seg.hotel_name:
                missing_fields.append("飯店名稱")
            self.show_snack(f"請完成最後一段住宿的填寫：{', '.join(missing_fields)}")
            logger.warning(f"Last segment validation failed. Missing: {missing_fields}")
            return
        
        # 鎖定最後一段
        last_seg.is_locked = True
        logger.info("Last segment locked")
            
        if last_seg.check_out_date < self.trip_config.total_end_date:
            self.show_snack(f"住宿安排尚未涵蓋至旅程結束 ({self.trip_config.total_end_date})")
            logger.warning(f"Coverage incomplete: {last_seg.check_out_date} < {self.trip_config.total_end_date}")
            return
        
        logger.info("Moving to step 3: confirmation")
        self.current_step = 3
        self.view.update_view()

    # --- Step 3: Submission ---

    def submit_order(self, e):
        """儲存到 JSON DB"""
        new_order = {
            "order_id": f"ORD-{int(datetime.now().timestamp())}",
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "trip_config": self.trip_config.to_dict()
        }

        try:
            # 讀取現有 DB
            try:
                with open("demo_db.json", "r", encoding="utf-8") as f:
                    db_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                db_data = {"orders": []}

            # 寫入
            if "orders" not in db_data:
                db_data["orders"] = []
            db_data["orders"].append(new_order)

            with open("demo_db.json", "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=4, ensure_ascii=False)
            
            self.show_snack("訂單建立成功！", color="green")
            self.page.go("/app/user/history") # 跳轉回歷史紀錄
            
        except Exception as ex:
            print(ex)
            self.show_snack(f"儲存失敗: {str(ex)}")

    # --- Helper ---
    def show_snack(self, msg, color="red"):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
    
    def go_back(self, e):
        if self.current_step > 1:
            self.current_step -= 1
            if self.current_step == 2:
                 # 回到 Planning 時可能需要重置狀態
                 pass
            self.view.update_view()
        else:
            self.page.go("/app/user/dashboard")