# MVC 快速參考指南

## 🚀 快速開始

### 運行應用程式
```bash
flet run main.py
```

### 專案結構
```
models/      → 資料層（資料庫操作）
controllers/ → 控制層（業務邏輯）
views/       → 視圖層（UI 渲染）
services/    → 服務層（共用功能）
```

## 📖 常用操作

### Model 操作

#### 創建使用者
```python
from models import User

user = User(email="user@example.com", username="使用者", password="123456")
user.save()
```

#### 查詢使用者
```python
user = User.find_by_email("user@example.com")
if user:
    print(user.to_dict())
```

#### 創建訂單
```python
from models import Order

order = Order(
    user_email="user@example.com",
    start_address="台北 101",
    end_address="圓山大飯店",
    driver_name="王小明",
    license_plate="ABC-6666"
)
order.save()
```

#### 查詢訂單
```python
# 查詢單個訂單
order = Order.find_by_id(1)

# 查詢使用者的所有訂單
orders = Order.find_by_user("user@example.com")
```

### Controller 操作

#### 使用者登入
```python
# 在 main.py 中
def handle_login(self, e, role: str):
    email = self.login_username.current.value
    password = self.login_password.current.value
    
    if self.user_controller.login(email, password, role):
        self.page.go(f"/app/{role}")
    else:
        self._show_login_error("登入失敗")
```

#### 確認訂單
```python
# 在 main.py 中
def handle_order_confirm(self, e):
    if self.order_controller.confirm_order():
        # 顯示成功訊息
        pass
    else:
        # 顯示錯誤訊息
        pass
```

#### 更新司機位置
```python
# 在 Controller 中
self.driver_controller.update_location((25.0374, 121.5635))
```

#### 管理飯店行李
```python
# 增加行李
self.hotel_controller.add_baggage(5)

# 減少行李
self.hotel_controller.remove_baggage(3)
```

### Service 操作

#### 地圖服務
```python
from services import MapService

# 創建標記
marker = MapService.create_marker(
    icon=ft.Icons.LOCATION_ON,
    color=ft.Colors.RED,
    coordinates=(25.0329, 121.5644)
)

# 創建路線
polyline = MapService.create_polyline(
    coordinates=[[121.5644, 25.0329], [121.5263, 25.0783]],
    color=ft.Colors.BLUE
)

# 計算中心點
center = MapService.calculate_center(
    (25.0329, 121.5644),
    (25.0783, 121.5263)
)
```

#### 動畫服務
```python
from services import AnimationService

# 動畫標記
path = [(25.0329, 121.5644), (25.0783, 121.5263)]
AnimationService.animate_marker_along_path(
    app_instance,
    marker_ref,
    path,
    duration=0.5
)

# 停止動畫
AnimationService.stop_animation(app_instance)
```

## 🎯 設計模式

### 創建新功能

#### 1. 創建 Model
```python
# models/new_feature.py
from .base import BaseModel

class NewFeature(BaseModel):
    def __init__(self, ...):
        # 初始化屬性
        pass
    
    @classmethod
    def find_by_id(cls, feature_id):
        # 查詢邏輯
        pass
    
    def save(self):
        # 儲存邏輯
        pass
```

#### 2. 創建 Controller
```python
# controllers/new_feature_controller.py
from .base_controller import BaseController
from models import NewFeature

class NewFeatureController(BaseController):
    def create_feature(self, ...):
        # 業務邏輯
        feature = NewFeature(...)
        return feature.save()
    
    def get_feature(self, feature_id):
        return NewFeature.find_by_id(feature_id)
```

#### 3. 創建 View
```python
# views/new_feature/feature_view.py
import flet as ft

def build_feature_view(app_instance):
    def on_submit(e):
        # 調用 Controller
        app_instance.feature_controller.create_feature(...)
    
    return ft.View(
        route="/app/feature",
        controls=[
            ft.ElevatedButton("提交", on_click=on_submit)
        ]
    )
```

#### 4. 註冊路由
```python
# app/router.py
from views.new_feature.feature_view import build_feature_view

def create_route_handler(app_instance):
    def on_route_change(route_event):
        # ...
        elif page.route == "/app/feature":
            page.views.append(build_feature_view(app_instance))
```

## 🔍 程式碼檢查清單

### Model
- [ ] 繼承 `BaseModel`
- [ ] 提供 `save()` 方法
- [ ] 提供 `find_by_*()` 查詢方法
- [ ] 提供 `to_dict()` 方法
- [ ] 不包含 UI 相關程式碼
- [ ] 不包含業務邏輯

### Controller
- [ ] 繼承 `BaseController`
- [ ] 方法返回結果（bool, dict, list 等）
- [ ] 調用 Model 進行資料操作
- [ ] 不直接操作 UI 元素
- [ ] 包含業務邏輯判斷

### View
- [ ] 只包含 UI 渲染程式碼
- [ ] 通過 Controller 處理事件
- [ ] 不包含業務邏輯
- [ ] 不直接操作資料庫
- [ ] 函數簡潔清晰

## 🐛 常見問題

### Q: 如何訪問 page？
```python
# 在 Controller 中
self.page  # 訪問頁面

# 在 View 中
app_instance.page  # 通過 app_instance 訪問
```

### Q: 如何在 Controller 中更新 UI？
```python
# Controller 不應該直接更新 UI
# 應該返回結果，讓 main.py 中的 handler 更新 UI

# ❌ 錯誤
class OrderController:
    def confirm_order(self):
        # ...
        self.page.update()  # 不要這樣做

# ✅ 正確
class OrderController:
    def confirm_order(self) -> bool:
        # ...
        return True  # 返回結果

# 在 main.py 中
def handle_confirm(self, e):
    if self.order_controller.confirm_order():
        self.page.update()  # 在這裡更新 UI
```

### Q: 如何共用資料？
```python
# 通過 app_instance 共用狀態
app_instance.booking_data = {...}

# 通過 Session 共用
self.page.session.set("key", "value")
value = self.page.session.get("key")
```

### Q: 如何處理錯誤？
```python
class OrderController(BaseController):
    def confirm_order(self) -> bool:
        try:
            # 業務邏輯
            order = Order(...)
            order.save()
            return True
        except Exception as e:
            logger.error(f"錯誤: {e}")
            return False
```

## 📚 API 參考

### BaseModel
```python
class BaseModel:
    @staticmethod
    def get_db() -> Dict[str, Any]
    
    @staticmethod
    def save_db(data: Dict[str, Any]) -> None
    
    @staticmethod
    def generate_timestamp() -> str
```

### BaseController
```python
class BaseController:
    def __init__(self, app_instance: 'App')
    self.app      # App 實例
    self.page     # Page 實例
```

### UserController
```python
login(email, password, role) -> bool
get_current_user() -> str
get_user_orders() -> list
handle_booking_instant(data) -> bool
handle_booking_previous(data) -> bool
handle_navigation(index) -> str
```

### OrderController
```python
create_order(...) -> Optional[Order]
confirm_order() -> bool
cancel_order() -> bool
get_order_by_id(order_id) -> Optional[Dict]
update_order_status(order_id, status) -> bool
```

### DriverController
```python
get_current_driver() -> Optional[Driver]
update_location(location) -> bool
update_status(status) -> bool
get_available_drivers() -> list
```

### HotelController
```python
get_current_hotel() -> Optional[Hotel]
add_baggage(count) -> bool
remove_baggage(count) -> bool
update_not_arrived(count) -> bool
save_scan_result(result) -> bool
```

## 🎨 程式碼風格

### 命名規範
- **類別**: `PascalCase` (例: `UserController`)
- **函數/方法**: `snake_case` (例: `get_user_orders`)
- **常數**: `UPPER_CASE` (例: `WINDOW_WIDTH`)
- **私有方法**: `_method_name` (例: `_show_error`)

### 類型提示
```python
def create_order(
    self,
    user_email: str,
    start_address: str
) -> Optional[Order]:
    pass
```

### 文檔字串
```python
def confirm_order(self) -> bool:
    """
    確認訂單
    從 app.booking_data 創建訂單
    
    Returns:
        是否成功
    """
    pass
```

## 🔗 相關文檔

- **README.md** - 專案說明
- **MVC_ARCHITECTURE.md** - 詳細架構文檔
- **MIGRATION_GUIDE.md** - 遷移指南
- **REFACTORING_SUMMARY.md** - 重構總結

## 💡 提示

1. **先想後做**: 先思考功能屬於哪一層
2. **保持簡潔**: 每個方法只做一件事
3. **使用日誌**: 記錄重要操作
4. **錯誤處理**: 使用 try-except
5. **測試驅動**: 先寫測試再寫程式碼

---

**最後更新**: 2025-11-24
**版本**: MVC v1.0
