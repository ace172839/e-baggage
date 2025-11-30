# 從舊架構遷移到 MVC 的指南

## 重構前後對比

### 舊架構問題
```
main.py (853 行)
├── App 類別包含所有邏輯
│   ├── UI 渲染
│   ├── 業務邏輯
│   ├── 資料操作
│   └── 事件處理
├── db_helpers.py (獨立的資料庫函數)
└── views/ (部分 UI)
```

**問題**：
- 程式碼耦合度高
- main.py 過於龐大
- 難以測試和維護
- 職責不清晰

### 新架構優勢
```
MVC 架構
├── models/ (資料層)
│   ├── User, Order, Driver, Hotel, Scan
│   └── 統一的資料庫操作
├── controllers/ (控制層)
│   ├── UserController
│   ├── OrderController
│   ├── DriverController
│   └── HotelController
├── views/ (視圖層)
│   └── 純 UI 渲染
├── services/ (服務層)
│   ├── MapService
│   └── AnimationService
└── main.py (入口，簡潔)
```

**優勢**：
- ✅ 關注點分離
- ✅ 程式碼清晰易懂
- ✅ 易於測試
- ✅ 易於擴展

## 具體遷移步驟

### 步驟 1: 保留舊檔案作為參考
```bash
# 建議先備份
cp main.py main.py.backup
cp db_helpers.py db_helpers.py.backup
```

### 步驟 2: 使用新的 Model

#### 舊程式碼 (db_helpers.py)
```python
def save_order_to_history(trip_data, user_email):
    db = get_db()
    new_order = {
        "id": len(db["orders"]) + 1,
        "user_email": user_email,
        "start_address": trip_data["start_address"],
        "end_address": trip_data["end_address"],
        # ...
    }
    db["orders"].append(new_order)
    save_db(db)
```

#### 新程式碼 (使用 Model)
```python
from models import Order

order = Order(
    user_email=user_email,
    start_address=trip_data["start_address"],
    end_address=trip_data["end_address"],
    driver_name=trip_data.get("driver_name", ""),
    license_plate=trip_data.get("license_plate", "")
)
order.save()
```

### 步驟 3: 使用 Controller 處理業務邏輯

#### 舊程式碼 (main.py)
```python
class App:
    def handle_order_confirm(self, e):
        logger.info("Order confirmed!")
        
        # 複雜的業務邏輯
        booking_data = self.booking_data
        user_email = self.page.session.get("email")
        
        # 儲存訂單
        trip_data = {
            "start_address": booking_data.get("start"),
            "end_address": booking_data.get("end"),
            # ...
        }
        save_order_to_history(trip_data, user_email)
        
        # 清空狀態
        self.booking_data = {}
        
        # 顯示彈窗
        success_dialog = ft.AlertDialog(...)
        self.page.open(success_dialog)
```

#### 新程式碼 (使用 Controller)
```python
# main.py
class App:
    def handle_order_confirm(self, e):
        # 調用 Controller
        if self.order_controller.confirm_order():
            # 顯示成功訊息
            success_dialog = ft.AlertDialog(
                title=ft.Text("預約成功！"),
                content=ft.Text("正在為您尋找司機..."),
                # ...
            )
            self.page.open(success_dialog)
        else:
            # 顯示錯誤訊息
            self.page.snack_bar = ft.SnackBar(
                ft.Text("訂單確認失敗"), 
                open=True
            )
            self.page.update()

# controllers/order_controller.py
class OrderController(BaseController):
    def confirm_order(self) -> bool:
        try:
            booking_data = self.app.booking_data
            user_email = self.page.session.get("email") or "demo@user.com"
            
            # 創建訂單
            order = Order(
                user_email=user_email,
                start_address=booking_data.get("start_address", ""),
                end_address=booking_data.get("end_address", ""),
                driver_name=booking_data.get("driver_name", "王小明"),
                license_plate=booking_data.get("license_plate", "ABC-6666")
            )
            
            if order.save():
                # 清空預約資料
                self.app.booking_data = {}
                logger.info(f"訂單確認成功: {order.order_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"確認訂單時發生錯誤: {e}")
            return False
```

### 步驟 4: 簡化 View

#### 舊程式碼 (可能混合業務邏輯)
```python
def build_dashboard_view(app_instance):
    def on_nav_change(e):
        selected_index = int(e.data)
        
        # 業務邏輯混在 View 中
        if app_instance.search_bar_ref.current:
            app_instance.search_bar_ref.current.visible = False
        
        if selected_index == 0:
            logger.info("導航到「更多」頁面")
            app_instance.page.go("/app/user/more")
        elif selected_index == 1:
            # ... 很多 if-elif
        # ...
    
    return ft.View(...)
```

#### 新程式碼 (純 UI)
```python
def build_dashboard_view(app_instance):
    def on_nav_change(e):
        # 調用 Controller
        route = app_instance.user_controller.handle_navigation(int(e.data))
        app_instance.page.go(route)
    
    return ft.View(
        route="/app/user/dashboard",
        controls=[
            ft.NavigationBar(on_change=on_nav_change, ...)
        ]
    )
```

## 常見遷移場景

### 場景 1: 登入驗證

#### 舊程式碼
```python
def login_view_handle_login(self, e, role: str):
    if self.mode == "debug":
        logger.warning("在偵錯模式下登入，已跳過驗證。")
        self.page.session.set("logged_in", True)
        self.page.session.set("role", role)
        self.page.session.set("email", self.login_username.current.value)
        self.page.go(f"/app/{role}")
        return
    
    # 複雜的驗證邏輯
    # ...
```

#### 新程式碼
```python
# main.py
def login_view_handle_login(self, e, role: str):
    email = self.login_username.current.value or "demo@user.com"
    password = self.login_password.current.value or ""
    
    if self.user_controller.login(email, password, role):
        self.page.go(f"/app/{role}")
    else:
        self._show_login_error("登入失敗")

# controllers/user_controller.py
class UserController(BaseController):
    def login(self, email: str, password: str, role: str) -> bool:
        if self.app.mode == "debug":
            # Debug 模式邏輯
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", email)
            return True
        
        # 正式模式驗證
        if User.authenticate(email, password):
            self.page.session.set("logged_in", True)
            self.page.session.set("role", role)
            self.page.session.set("email", email)
            return True
        return False
```

### 場景 2: 資料查詢

#### 舊程式碼
```python
def get_user_orders(self, user_email):
    db = get_db()
    user_orders = []
    for order in db.get("orders", []):
        if order.get("user_email") == user_email:
            user_orders.append(order)
    return user_orders
```

#### 新程式碼
```python
# 直接使用 Model
from models import Order

user_orders = Order.find_by_user(user_email)
order_dicts = [order.to_dict() for order in user_orders]
```

### 場景 3: 狀態更新

#### 舊程式碼
```python
def update_hotel_baggage(self, count):
    self.hotel_baggages += count
    # 需要手動同步到資料庫
    db = get_db()
    # ... 複雜的更新邏輯
```

#### 新程式碼
```python
# 使用 Controller
self.hotel_controller.add_baggage(count)

# Controller 內部
class HotelController(BaseController):
    def add_baggage(self, count: int = 1) -> bool:
        hotel = self.get_current_hotel()
        if hotel and hotel.add_baggage(count):
            # 自動更新 app 狀態
            self.app.hotel_baggages = hotel.baggage_count
            return True
        return False
```

## 檢查清單

遷移完成後，檢查以下項目：

### Model 層
- [ ] 所有資料操作都在 Model 中
- [ ] Model 不包含 UI 相關程式碼
- [ ] Model 提供清晰的 CRUD 方法
- [ ] 使用 `to_dict()` 方法返回資料

### Controller 層
- [ ] 業務邏輯都在 Controller 中
- [ ] Controller 不直接操作 UI 元素
- [ ] Controller 方法返回結果（bool, dict, list 等）
- [ ] Controller 調用 Model 進行資料操作

### View 層
- [ ] View 只包含 UI 渲染程式碼
- [ ] View 通過 Controller 處理事件
- [ ] View 不包含業務邏輯判斷
- [ ] View 函數簡潔清晰

### main.py
- [ ] main.py 簡化，只保留必要的初始化
- [ ] 初始化所有 Controller
- [ ] Handler 方法調用 Controller
- [ ] 沒有直接的資料庫操作

## 測試遷移結果

### 1. 功能測試
```bash
# 運行應用程式
flet run main.py

# 測試以下功能：
- [ ] 登入功能
- [ ] 使用者預約
- [ ] 訂單確認
- [ ] 司機接單
- [ ] 飯店掃描
```

### 2. 程式碼檢查
```python
# 檢查是否正確使用 Model
from models import User, Order

# 檢查是否正確使用 Controller
user_controller = UserController(app_instance)
result = user_controller.login("test@test.com", "password", "user")

# 檢查 View 是否純粹
# View 不應該有複雜的 if-elif 邏輯
# View 不應該直接操作資料庫
```

### 3. 日誌檢查
查看日誌檔案，確認：
- [ ] Model 的資料操作日誌
- [ ] Controller 的業務邏輯日誌
- [ ] 沒有錯誤或警告

## 常見問題 (FAQ)

### Q: 舊的 db_helpers.py 還需要嗎？
A: 不需要。所有資料操作已移到 Model 中。可以保留作為參考，但不再使用。

### Q: app/ 目錄下的檔案怎麼辦？
A: 可以逐步遷移：
- `app/user.py` → 視圖功能保留或移到 `views/`
- `app/driver.py` → 同上
- `app/hotel.py` → 同上
- `app/router.py` → 保留，但更新以使用新架構

### Q: 如何確保沒有破壞現有功能？
A: 
1. 保留舊檔案作為備份
2. 逐步遷移，每次遷移一個功能
3. 充分測試每個功能
4. 查看日誌確認正常運作

### Q: 可以只遷移部分功能嗎？
A: 可以。建議優先遷移：
1. 資料操作（Model）
2. 核心業務邏輯（Controller）
3. 複雜的 View

### Q: 效能會受影響嗎？
A: 不會。MVC 只是架構模式，不影響效能。反而因為程式碼更清晰，可能更容易優化。

## 總結

通過以上步驟，您的專案已經成功遷移到 MVC 架構：

✅ **更清晰**：每個檔案職責明確
✅ **更易維護**：修改某個功能不影響其他部分
✅ **更易測試**：每層可以獨立測試
✅ **更易擴展**：新增功能按照 MVC 模式添加

恭喜完成重構！
