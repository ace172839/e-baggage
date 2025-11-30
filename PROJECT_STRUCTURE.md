# e-baggage 專案結構樹狀圖

```
e-baggage/
│
├── 📁 models/                          # 🆕 資料層 (Model)
│   ├── __init__.py                     # Models 模組初始化
│   ├── base.py                         # 基礎 Model 類別
│   ├── user.py                         # 使用者模型
│   ├── order.py                        # 訂單模型
│   ├── driver.py                       # 司機模型
│   ├── hotel.py                        # 飯店模型
│   └── scan.py                         # 掃描記錄模型
│
├── 📁 controllers/                     # 🆕 控制層 (Controller)
│   ├── __init__.py                     # Controllers 模組初始化
│   ├── base_controller.py              # 基礎控制器
│   ├── user_controller.py              # 使用者控制器
│   ├── order_controller.py             # 訂單控制器
│   ├── driver_controller.py            # 司機控制器
│   └── hotel_controller.py             # 飯店控制器
│
├── 📁 services/                        # 🆕 服務層 (Service)
│   ├── __init__.py                     # Services 模組初始化
│   ├── map_service.py                  # 地圖服務
│   └── animation_service.py            # 動畫服務
│
├── 📁 views/                           # 視圖層 (View)
│   ├── __init__.py
│   │
│   ├── 📁 login/                       # 登入相關視圖
│   │   ├── __init__.py
│   │   ├── splash_view.py              # 啟動畫面
│   │   ├── splash_view_to_user.py      # 使用者啟動畫面
│   │   ├── splash_view_to_user2.py     # 使用者啟動畫面 2
│   │   ├── splash_view_to_driver.py    # 司機啟動畫面
│   │   ├── splash_view_to_hotel.py     # 飯店啟動畫面
│   │   ├── login_view.py               # 登入視圖
│   │   └── role_select_view.py         # 角色選擇視圖
│   │
│   ├── 📁 user/                        # 使用者相關視圖
│   │   ├── __init__.py
│   │   ├── user_home_page_content.py   # 首頁內容
│   │   ├── user_home_page_more_content.py # 更多內容
│   │   ├── user_booking_instant.py     # 即時預約
│   │   ├── user_booking_previous.py    # 事先預約
│   │   ├── user_current_order.py       # 當前訂單
│   │   ├── user_history.py             # 歷史記錄
│   │   ├── user_supporting.py          # 客服
│   │   └── map_view.py                 # 地圖視圖
│   │
│   └── 📁 common/                      # 共用元件
│       ├── __init__.py
│       ├── navigator.py                # 導航元件
│       └── assistant.py                # 助手元件
│
├── 📁 app/                             # 應用程式邏輯
│   ├── __init__.py
│   ├── router.py                       # 路由處理
│   ├── user.py                         # 使用者相關功能
│   ├── driver.py                       # 司機相關功能
│   ├── hotel.py                        # 飯店相關功能
│   ├── order.py                        # 訂單相關功能
│   └── scan.py                         # 掃描相關功能
│
├── 📁 assets/                          # 資源檔案
│   ├── 📁 fonts/                       # 字體
│   │   └── LXGWWenKaiTC-Regular.ttf
│   └── 📁 images/                      # 圖片
│       ├── hotel.jpg
│       ├── baggages_hotel.jpg
│       └── ...
│
├── 📁 .venv/                           # Python 虛擬環境
├── 📁 .vscode/                         # VS Code 配置
├── 📁 __pycache__/                     # Python 快取
│
├── 📄 main.py                          # 🔄 應用程式入口（已重構）
├── 📄 config.py                        # 配置文件
├── 📄 constants.py                     # 常數定義
├── 📄 db_helpers.py                    # ⚠️ 資料庫輔助（即將淘汰）
├── 📄 demo_db.json                     # JSON 資料庫
├── 📄 test.py                          # 測試檔案
├── 📄 keys.json                        # 密鑰配置
│
├── 📄 requirements.txt                 # Python 依賴
├── 📄 .gitignore                       # Git 忽略檔案
│
├── 📄 README.md                        # 📝 專案說明（已更新）
├── 📄 MVC_ARCHITECTURE.md              # 🆕 MVC 架構文檔
├── 📄 MIGRATION_GUIDE.md               # 🆕 遷移指南
├── 📄 REFACTORING_SUMMARY.md           # 🆕 重構總結
├── 📄 QUICK_REFERENCE.md               # 🆕 快速參考
└── 📄 PROJECT_STRUCTURE.md             # 🆕 專案結構（本檔案）
```

## 📊 檔案統計

### 總覽
- **總資料夾**: 11 個
- **總檔案**: 60+ 個
- **新增檔案**: 19 個（MVC 架構）
- **文檔檔案**: 5 個

### 按類型分類

#### 🆕 MVC 架構檔案
```
models/         7 個檔案  (~600 行)
controllers/    5 個檔案  (~500 行)
services/       3 個檔案  (~200 行)
─────────────────────────────────
總計           15 個檔案  (~1,300 行)
```

#### 📝 視圖層檔案
```
views/login/    7 個檔案
views/user/     8 個檔案
views/common/   2 個檔案
─────────────────────────────
總計           17 個檔案
```

#### 📋 應用邏輯檔案
```
app/            6 個檔案
```

#### 📄 文檔檔案
```
README.md                  專案說明
MVC_ARCHITECTURE.md        MVC 架構詳解
MIGRATION_GUIDE.md         遷移指南
REFACTORING_SUMMARY.md     重構總結
QUICK_REFERENCE.md         快速參考
PROJECT_STRUCTURE.md       專案結構（本檔案）
```

## 🗂️ 目錄說明

### `/models` - 資料層
**職責**: 資料模型和資料庫操作
**特點**:
- 每個檔案對應一個業務實體
- 提供 CRUD 操作
- 獨立於 UI 和業務邏輯

**檔案列表**:
- `base.py` - 基礎 Model，提供資料庫操作
- `user.py` - 使用者資料管理
- `order.py` - 訂單資料管理
- `driver.py` - 司機資料管理
- `hotel.py` - 飯店資料管理
- `scan.py` - 掃描記錄管理

### `/controllers` - 控制層
**職責**: 業務邏輯處理
**特點**:
- 協調 Model 和 View
- 處理使用者輸入
- 不包含 UI 程式碼

**檔案列表**:
- `base_controller.py` - 基礎 Controller
- `user_controller.py` - 使用者業務邏輯
- `order_controller.py` - 訂單業務邏輯
- `driver_controller.py` - 司機業務邏輯
- `hotel_controller.py` - 飯店業務邏輯

### `/services` - 服務層
**職責**: 可重用的服務功能
**特點**:
- 提供共用功能
- 無狀態設計
- 可被多個 Controller 使用

**檔案列表**:
- `map_service.py` - 地圖相關服務
- `animation_service.py` - 動畫相關服務

### `/views` - 視圖層
**職責**: UI 渲染
**特點**:
- 只負責顯示
- 通過 Controller 處理事件
- 不包含業務邏輯

**子目錄**:
- `login/` - 登入相關視圖
- `user/` - 使用者相關視圖
- `common/` - 共用元件

### `/app` - 應用邏輯
**職責**: 路由和應用級功能
**特點**:
- 路由處理
- 角色相關功能
- 與 MVC 層配合

**檔案列表**:
- `router.py` - 路由處理
- `user.py` - 使用者功能
- `driver.py` - 司機功能
- `hotel.py` - 飯店功能
- `order.py` - 訂單功能
- `scan.py` - 掃描功能

### `/assets` - 資源檔案
**職責**: 靜態資源
**內容**:
- 字體檔案
- 圖片資源

## 🔄 資料流圖

```
使用者 → View → Handler → Controller → Model → Database
  ↑                                              ↓
  └───────────────── Response ──────────────────┘
```

### 詳細流程

1. **使用者操作** → 點擊按鈕、輸入資料
2. **View** → 觸發事件
3. **Handler (main.py)** → 接收事件
4. **Controller** → 處理業務邏輯
5. **Model** → 資料庫操作
6. **Database** → 讀寫資料
7. **Response** → 返回結果
8. **UI 更新** → 顯示給使用者

## 📈 架構演進

### 重構前
```
main.py (853 行)
├── UI 渲染
├── 業務邏輯
├── 資料操作
└── 事件處理

db_helpers.py (60 行)
└── 資料庫函數
```

### 重構後
```
MVC 架構
├── models/ (7 檔案, ~600 行)
│   └── 資料層
├── controllers/ (5 檔案, ~500 行)
│   └── 控制層
├── services/ (3 檔案, ~200 行)
│   └── 服務層
├── views/ (17 檔案)
│   └── 視圖層
└── main.py (簡化)
    └── 應用入口
```

## 🎯 設計原則

### SOLID 原則
- ✅ **S**ingle Responsibility - 單一職責
- ✅ **O**pen/Closed - 開放封閉
- ✅ **L**iskov Substitution - 里氏替換
- ✅ **I**nterface Segregation - 介面隔離
- ✅ **D**ependency Inversion - 依賴倒置

### MVC 原則
- ✅ **關注點分離** - Model、View、Controller 各司其職
- ✅ **低耦合** - 各層獨立，減少相互依賴
- ✅ **高內聚** - 相關功能集中在一起

## 🔧 維護指南

### 添加新功能
1. 在 `models/` 創建 Model
2. 在 `controllers/` 創建 Controller
3. 在 `views/` 創建 View
4. 在 `app/router.py` 註冊路由

### 修改現有功能
1. 資料結構變更 → 修改 Model
2. 業務邏輯變更 → 修改 Controller
3. UI 變更 → 修改 View

### 程式碼審查
- [ ] 是否遵循 MVC 模式
- [ ] 是否有適當的錯誤處理
- [ ] 是否有清晰的註釋
- [ ] 是否有類型提示

## 📝 命名約定

### 檔案命名
- Model: `entity_name.py` (例: `user.py`)
- Controller: `entity_name_controller.py` (例: `user_controller.py`)
- View: `feature_name_view.py` (例: `login_view.py`)
- Service: `service_name_service.py` (例: `map_service.py`)

### 類別命名
- Model: `EntityName` (例: `User`)
- Controller: `EntityNameController` (例: `UserController`)
- Service: `ServiceNameService` (例: `MapService`)

## 🚀 下一步

### 短期目標
- [ ] 完成所有功能的 MVC 遷移
- [ ] 添加單元測試
- [ ] 優化效能

### 中期目標
- [ ] 資料庫遷移（JSON → SQLite）
- [ ] 添加 API 層
- [ ] 增強錯誤處理

### 長期目標
- [ ] 微服務架構
- [ ] 雲端部署
- [ ] 多平台支援

## 📚 參考資源

- [Flet 官方文檔](https://flet.dev)
- [MVC 設計模式](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [Python 最佳實踐](https://docs.python-guide.org/)

---

**建立日期**: 2025-11-24
**版本**: MVC v1.0
**維護者**: e-baggage 開發團隊
