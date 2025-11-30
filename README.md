# e-baggage

電子行李托運系統 - 使用 Flet 框架開發的跨平台應用程式

## 專案架構

本專案採用 **MVC (Model-View-Controller)** 架構模式：

```
e-baggage/
├── models/                 # 資料層 (Model)
│   ├── __init__.py
│   ├── base.py            # 基礎 Model 類別
│   ├── user.py            # 使用者模型
│   ├── order.py           # 訂單模型
│   ├── driver.py          # 司機模型
│   ├── hotel.py           # 飯店模型
│   └── scan.py            # 掃描記錄模型
│
├── controllers/           # 控制層 (Controller)
│   ├── __init__.py
│   ├── base_controller.py # 基礎 Controller 類別
│   ├── user_controller.py # 使用者控制器
│   ├── order_controller.py # 訂單控制器
│   ├── driver_controller.py # 司機控制器
│   └── hotel_controller.py # 飯店控制器
│
├── views/                 # 視圖層 (View)
│   ├── login/            # 登入相關視圖
│   ├── user/             # 使用者相關視圖
│   └── common/           # 共用元件
│
├── services/             # 服務層 (可選)
│   ├── __init__.py
│   ├── map_service.py    # 地圖服務
│   └── animation_service.py # 動畫服務
│
├── app/                  # 應用程式邏輯
│   ├── router.py         # 路由處理
│   ├── user.py           # 使用者相關功能
│   ├── driver.py         # 司機相關功能
│   ├── hotel.py          # 飯店相關功能
│   └── ...
│
├── main.py               # 應用程式入口
├── config.py             # 配置文件
├── constants.py          # 常數定義
├── db_helpers.py         # 資料庫輔助函數 (即將淘汰)
└── demo_db.json          # JSON 資料庫
```

## MVC 架構說明

### Model（模型層）
- **職責**：處理資料邏輯、資料庫操作
- **位置**：`models/` 目錄
- **特點**：
  - 每個模型代表一個業務實體（User, Order, Driver, Hotel, Scan）
  - 提供 CRUD 操作方法
  - 獨立於 UI 和業務邏輯

### Controller（控制器層）
- **職責**：處理業務邏輯、協調 Model 和 View
- **位置**：`controllers/` 目錄
- **特點**：
  - 接收使用者輸入
  - 調用 Model 進行資料操作
  - 返回結果給 View
  - 不包含 UI 相關程式碼

### View（視圖層）
- **職責**：UI 渲染、顯示資料
- **位置**：`views/` 目錄
- **特點**：
  - 只負責 UI 元素的創建和顯示
  - 不包含業務邏輯
  - 通過 Controller 與 Model 互動

### Service（服務層）
- **職責**：共用的業務邏輯和服務
- **位置**：`services/` 目錄
- **特點**：
  - 提供可重用的功能（地圖、動畫等）
  - 可被多個 Controller 調用

## 如何運行

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行應用程式
```bash
flet run main.py
```

## 開發指南

### 添加新功能
1. **Model**：在 `models/` 中創建新的模型類別
2. **Controller**：在 `controllers/` 中創建對應的控制器
3. **View**：在 `views/` 中創建 UI 視圖
4. **Router**：在 `app/router.py` 中註冊新路由

### 程式碼結構範例

```python
# Model 範例 (models/user.py)
class User(BaseModel):
    def find_by_email(cls, email: str):
        # 資料查詢邏輯
        pass

# Controller 範例 (controllers/user_controller.py)
class UserController(BaseController):
    def login(self, email: str, password: str):
        # 業務邏輯
        user = User.find_by_email(email)
        # ...
        
# View 範例 (views/login/login_view.py)
def build_login_view(app_instance):
    # UI 渲染
    return ft.View(...)
```

## 資料庫

目前使用 JSON 檔案 (`demo_db.json`) 作為簡易資料庫。
未來可以輕鬆遷移到 SQLite、PostgreSQL 等關聯式資料庫。

## 技術棧

- **框架**：Flet (基於 Flutter)
- **語言**：Python 3.x
- **架構模式**：MVC
- **資料庫**：JSON (可擴展)

## 維護者

e-baggage 開發團隊

## 授權

[授權資訊]
