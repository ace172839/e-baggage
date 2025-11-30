# MVC 架構重構說明

## 重構目標

將原本混雜在 `main.py` 中的業務邏輯、資料操作和 UI 渲染分離，改為清晰的 MVC 架構。

## 架構優勢

### 1. 關注點分離 (Separation of Concerns)
- **Model**：專注資料和資料庫操作
- **View**：專注 UI 渲染
- **Controller**：專注業務邏輯

### 2. 可維護性提升
- 每個層次職責清晰
- 修改某一層不影響其他層
- 程式碼更容易理解和維護

### 3. 可測試性
- 各層可以獨立測試
- Controller 可以脫離 UI 進行單元測試
- Model 可以獨立測試資料邏輯

### 4. 可擴展性
- 新增功能只需按照 MVC 模式添加對應檔案
- 易於團隊協作開發

## 重構內容

### Models 層

#### BaseModel (models/base.py)
提供所有模型的基礎功能：
- `get_db()`: 讀取 JSON 資料庫
- `save_db()`: 儲存到 JSON 資料庫
- `generate_timestamp()`: 生成時間戳

#### 具體模型
- **User** (models/user.py): 使用者資料和驗證
- **Order** (models/order.py): 訂單管理
- **Driver** (models/driver.py): 司機資訊
- **Hotel** (models/hotel.py): 飯店資訊
- **Scan** (models/scan.py): 掃描記錄

### Controllers 層

#### BaseController (controllers/base_controller.py)
所有控制器的基礎類別，提供對 App 實例和 Page 的訪問。

#### 具體控制器
- **UserController**: 使用者相關業務邏輯（登入、導航、預約）
- **OrderController**: 訂單相關業務邏輯（創建、確認、取消）
- **DriverController**: 司機相關業務邏輯（位置更新、狀態管理）
- **HotelController**: 飯店相關業務邏輯（行李管理、掃描記錄）

### Services 層

提供可重用的服務：
- **MapService**: 地圖相關功能（標記、路線）
- **AnimationService**: 動畫相關功能（標記動畫）

### Views 層

保持原有結構，確保只負責 UI 渲染：
- `views/login/`: 登入相關視圖
- `views/user/`: 使用者相關視圖
- `views/common/`: 共用元件

## 使用範例

### 在 main.py 中使用 Controller

```python
class App:
    def __init__(self):
        # 控制器會在 main() 中初始化
        self.user_controller = None
        self.order_controller = None
        # ...
    
    def main(self, page: ft.Page):
        self.page = page
        
        # 初始化控制器
        self.user_controller = UserController(self)
        self.order_controller = OrderController(self)
        # ...
    
    def handle_login(self, e, role: str):
        # 使用 Controller 處理登入
        email = self.login_username.current.value
        password = self.login_password.current.value
        
        if self.user_controller.login(email, password, role):
            self.page.go(f"/app/{role}")
        else:
            self._show_login_error("登入失敗")
    
    def handle_order_confirm(self, e):
        # 使用 Controller 確認訂單
        if self.order_controller.confirm_order():
            # 顯示成功訊息
            pass
```

### 在 View 中使用 Controller

```python
def build_dashboard_view(app_instance: 'App') -> ft.View:
    # View 只負責 UI
    # 業務邏輯通過 Controller 處理
    
    def on_navigation_change(e):
        # 調用 Controller
        route = app_instance.user_controller.handle_navigation(int(e.data))
        app_instance.page.go(route)
    
    return ft.View(
        route="/app/user/dashboard",
        controls=[
            # UI 元素
            ft.NavigationBar(on_change=on_navigation_change)
        ]
    )
```

### 直接使用 Model

```python
from models import User, Order

# 查詢使用者
user = User.find_by_email("user@example.com")

# 創建訂單
order = Order(
    user_email="user@example.com",
    start_address="台北 101",
    end_address="圓山大飯店"
)
order.save()

# 查詢訂單
user_orders = Order.find_by_user("user@example.com")
```

## 遷移指南

### 從舊程式碼遷移到 MVC

#### 步驟 1: 識別功能所屬層次
- 資料查詢/儲存 → Model
- 業務判斷/流程控制 → Controller
- UI 渲染 → View

#### 步驟 2: 重構資料操作
將 `db_helpers.py` 中的函數移到對應的 Model：
```python
# 舊程式碼 (db_helpers.py)
def save_order_to_history(trip_data, user_email):
    db = get_db()
    # ...

# 新程式碼 (models/order.py)
class Order(BaseModel):
    def save(self):
        # ...
```

#### 步驟 3: 重構業務邏輯
將 `main.py` 中的 handler 方法移到 Controller：
```python
# 舊程式碼 (main.py)
def handle_order_confirm(self, e):
    # 複雜的業務邏輯
    pass

# 新程式碼 (controllers/order_controller.py)
class OrderController(BaseController):
    def confirm_order(self):
        # 業務邏輯
        pass
```

#### 步驟 4: 簡化 View
確保 View 只包含 UI 程式碼：
```python
# View 應該簡潔
def build_view(app_instance):
    def on_click(e):
        # 調用 Controller
        app_instance.order_controller.confirm_order()
    
    return ft.View(
        controls=[
            ft.ElevatedButton("確認", on_click=on_click)
        ]
    )
```

## 最佳實踐

### 1. Model 設計
- 一個 Model 對應一個業務實體
- 提供清晰的 CRUD 方法
- 不包含 UI 相關邏輯

### 2. Controller 設計
- 保持方法簡潔，單一職責
- 不直接操作 UI 元素
- 返回結果而非直接更新頁面

### 3. View 設計
- 只負責 UI 渲染
- 通過 Controller 處理事件
- 不包含業務邏輯判斷

### 4. Service 設計
- 提取可重用的功能
- 無狀態設計
- 可被多個 Controller 調用

## 未來擴展

### 資料庫遷移
目前使用 JSON，可輕鬆遷移到：
- SQLite（輕量級）
- PostgreSQL（生產環境）
- MongoDB（NoSQL）

只需修改 `BaseModel` 的 `get_db()` 和 `save_db()` 方法。

### API 整合
可以在 Service 層添加 API 服務：
```python
# services/api_service.py
class APIService:
    @staticmethod
    def call_external_api():
        # API 調用邏輯
        pass
```

### 測試
每層都可以獨立測試：
```python
# tests/test_models.py
def test_user_creation():
    user = User(email="test@test.com")
    assert user.save()

# tests/test_controllers.py
def test_order_confirmation():
    controller = OrderController(mock_app)
    assert controller.confirm_order()
```

## 總結

通過 MVC 重構，專案變得：
- ✅ 更易維護
- ✅ 更易測試
- ✅ 更易擴展
- ✅ 更易協作
- ✅ 程式碼更清晰

這是軟體工程的最佳實踐，適用於中大型專案開發。
