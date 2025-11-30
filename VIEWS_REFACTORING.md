# Views 層重構說明

## 重構目標

將 `views/` 目錄下的檔案進行重構，確保 View 層只負責 UI 渲染，將業務邏輯和資料操作移到適當的層次。

## 重構原則

### View 層應該：
✅ 只包含 UI 元件的創建和佈局  
✅ 調用 Service 或 Controller 處理業務邏輯  
✅ 保持簡潔，易於理解  
✅ 不直接操作資料庫或檔案  

### View 層不應該：
❌ 包含資料庫操作（如 `json.load()`, `json.dump()`）  
❌ 包含複雜的業務邏輯判斷  
❌ 包含資料處理函數  
❌ 直接讀寫檔案  

## 重構內容

### 1. 創建新的 Service

#### `services/booking_service.py`
**職責**: 處理預約相關的業務邏輯

**方法**:
- `load_partner_hotels()` - 載入合作飯店
- `save_order()` - 儲存訂單
- `generate_order_id()` - 生成訂單 ID
- `create_order_data()` - 創建訂單資料
- `load_recommendations()` - 載入推薦資訊

**從哪裡移出**:
- `views/user/user_booking_instant.py` 的 `load_partner_hotels_from_db()`
- `views/user/user_booking_instant.py` 的 `save_order_to_db()`
- `views/common/assistant.py` 的 `load_recommendations()`

#### `services/map_util_service.py`
**職責**: 地圖相關的工具函數

**方法**:
- `calculate_zoom_level()` - 計算縮放等級
- `calculate_center()` - 計算中心點

**從哪裡移出**:
- `views/user/user_booking_instant.py` 的 `calculate_zoom_level()`

#### `services/order_history_service.py`
**職責**: 處理訂單歷史查詢

**方法**:
- `get_all_orders()` - 取得所有訂單
- `get_orders_sorted_by_date()` - 取得排序後的訂單
- `get_orders_by_user()` - 取得特定使用者的訂單

**從哪裡移出**:
- `views/user/user_history.py` 的 `get_orders()`

### 2. 重構的 View 檔案

#### `views/user/user_booking_instant.py`

**重構前**:
```python
# ❌ View 中包含資料操作
def load_partner_hotels_from_db():
    with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
        db_date = json.load(f)
    hotels = db_date.get('partner_hotels', [])
    return hotels

def save_order_to_db(order_data: dict):
    with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    # ... 複雜的儲存邏輯
```

**重構後**:
```python
# ✅ View 調用 Service
from services import BookingService

hotels_detail = BookingService.load_partner_hotels()

if BookingService.save_order(order_data):
    logger.info("訂單儲存成功")
```

**改進**:
- ✅ 移除了直接的檔案操作
- ✅ 使用 Service 封裝業務邏輯
- ✅ View 更簡潔，只專注於 UI

#### `views/common/assistant.py`

**重構前**:
```python
# ❌ View 中包含資料載入
def load_recommendations() -> list:
    try:
        with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        return db_data.get('recommendations', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []
```

**重構後**:
```python
# ✅ 使用 Service
from services import BookingService

all_recs = BookingService.load_recommendations()
```

**改進**:
- ✅ 移除了檔案讀取邏輯
- ✅ 複用 BookingService 的方法
- ✅ 更好的錯誤處理（在 Service 層）

#### `views/user/user_history.py`

**重構前**:
```python
# ❌ View 中包含資料查詢和排序
def get_orders():
    with open('demo_db.json', 'r') as f:
        data = json.load(f)
    return data.get('orders', [])

def history_view(app_instance):
    orders = get_orders()
    orders.sort(key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d'), reverse=True)
```

**重構後**:
```python
# ✅ 使用 Service
from services import OrderHistoryService

def history_view(app_instance):
    orders = OrderHistoryService.get_orders_sorted_by_date(reverse=True)
```

**改進**:
- ✅ 移除了檔案操作
- ✅ 移除了排序邏輯
- ✅ Service 提供已排序的資料

## 架構改進

### 重構前
```
views/user/user_booking_instant.py
├── UI 渲染
├── 資料庫操作 ❌
├── 檔案讀寫 ❌
└── 業務邏輯 ❌
```

### 重構後
```
views/user/user_booking_instant.py
└── UI 渲染 ✅
    └── 調用 Service

services/booking_service.py
├── 資料庫操作 ✅
├── 檔案讀寫 ✅
└── 業務邏輯 ✅
```

## 新增的 Service 統計

| Service | 檔案 | 方法數 | 程式碼行數 |
|---------|------|--------|-----------|
| BookingService | booking_service.py | 5 | ~170 |
| MapUtilService | map_util_service.py | 2 | ~60 |
| OrderHistoryService | order_history_service.py | 3 | ~70 |
| **總計** | **3 個檔案** | **10 個方法** | **~300 行** |

## 重構效益

### 1. 關注點分離 ✨
- View 只負責 UI
- Service 負責業務邏輯
- 職責更清晰

### 2. 程式碼重用 🔄
- Service 可被多個 View 使用
- 避免重複程式碼
- 統一的資料處理邏輯

### 3. 易於測試 🧪
- Service 可以獨立測試
- 不需要 UI 就能測試業務邏輯
- Mock 更容易

### 4. 易於維護 🔧
- 修改資料邏輯只需改 Service
- 不影響 View
- 錯誤處理集中管理

### 5. 可擴展性 📈
- 新增功能只需添加 Service 方法
- View 保持簡潔
- 符合開放封閉原則

## 使用範例

### 在 View 中使用 Service

```python
# views/user/some_view.py
from services import BookingService, OrderHistoryService

def build_some_view(app_instance):
    # 載入飯店
    hotels = BookingService.load_partner_hotels()
    
    # 儲存訂單
    order_data = BookingService.create_order_data(
        pickup="台北101",
        dropoff="圓山大飯店",
        luggages="5"
    )
    success = BookingService.save_order(order_data)
    
    # 載入訂單歷史
    orders = OrderHistoryService.get_orders_sorted_by_date()
    
    # ... UI 渲染
```

## 檢查清單

重構後的 View 檔案應該：

- [ ] 不包含 `import json`
- [ ] 不包含 `open()` 或 `with open()`
- [ ] 不包含 `json.load()` 或 `json.dump()`
- [ ] 不包含複雜的資料處理函數
- [ ] 只包含 UI 元件創建
- [ ] 使用 Service 處理資料
- [ ] 程式碼簡潔易讀

## 遷移指南

如果您要重構其他 View 檔案，請遵循以下步驟：

### 步驟 1: 識別需要移出的程式碼
```python
# 在 View 中找到這些模式：
- def load_xxx()
- def save_xxx()
- def calculate_xxx()
- with open(...)
- json.load(...)
```

### 步驟 2: 創建或使用現有 Service
```python
# 在 services/ 中創建或使用 Service
class XxxService:
    @staticmethod
    def load_xxx():
        # 資料操作邏輯
        pass
```

### 步驟 3: 更新 View
```python
# 重構前
def build_view():
    data = load_xxx()  # ❌ 本地函數
    
# 重構後
from services import XxxService

def build_view():
    data = XxxService.load_xxx()  # ✅ 使用 Service
```

### 步驟 4: 測試
- 確保功能正常運作
- 檢查日誌輸出
- 驗證資料正確性

## 後續改進

### 短期
- [ ] 重構剩餘的 View 檔案
- [ ] 添加單元測試
- [ ] 完善錯誤處理

### 中期
- [ ] Service 層添加快取機制
- [ ] 優化資料庫查詢
- [ ] 添加資料驗證

### 長期
- [ ] 遷移到關聯式資料庫
- [ ] 實作 Repository 模式
- [ ] 添加 API 層

## 總結

通過這次重構：

✅ **View 層更純粹** - 只負責 UI 渲染  
✅ **Service 層更完善** - 統一的業務邏輯  
✅ **程式碼更清晰** - 關注點分離  
✅ **易於維護** - 修改影響範圍小  
✅ **易於測試** - 可獨立測試各層  

這是向專業軟體架構邁進的重要一步！

---

**重構日期**: 2025-11-24  
**重構者**: MVC 架構團隊  
**版本**: v1.1
