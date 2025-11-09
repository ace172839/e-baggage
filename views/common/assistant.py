import flet as ft
from typing import TYPE_CHECKING
from constants import *
import json
import random
import logging

if TYPE_CHECKING:
    from main import App

# 獲取 logger
logger = logging.getLogger(__name__)

DEMO_DB_PATH = "demo_db.json"

# --- 1. 資料處理輔助函式 ---

def load_recommendations() -> list:
    """ 從 demo_db.json 載入推薦資料 """
    try:
        with open(DEMO_DB_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        return db_data.get('recommendations', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def apply_filters(recommendations: list, filters: dict) -> list:
    """ 根據篩選器過濾景點 """
    filtered_list = []
    
    for item in recommendations:
        tags = item.get("tags", [])
        item_time = item.get("time") # 獲取景點的 time (e.g., 1.5, 3, 8)
        
        # 檢查 類型 (室內/室外)
        type_match = (filters["type"] == "any" or filters["type"] in tags)
        
        # 檢查 偏好
        pref_match = (filters["preference"] == "any" or filters["preference"] in tags)
        
        # 檢查 交通
        trans_match = (filters["transport"] == "any" or filters["transport"] in tags)
        
        # --- ↓↓↓ 新增的時間篩選邏輯 ↓↓↓ ---
        duration_filter = filters["duration"]
        duration_match = False
        if duration_filter == "any":
            duration_match = True
        elif item_time is not None:
            # 為了 Demo 效果，我們讓範圍稍微寬鬆一點
            if duration_filter == "1-2h":
                duration_match = (1 <= item_time <= 2.5) # 1-2.5 小時
            elif duration_filter == "3-4h":
                duration_match = (2.6 <= item_time <= 5) # 2.6-5 小時
            elif duration_filter == "6h+":
                duration_match = (item_time > 5) # 5 小時以上
        # --- ↑↑↑ 篩選邏輯結束 ↑↑↑ ---
        
        if type_match and pref_match and trans_match and duration_match:
            filtered_list.append(item)
            
    return filtered_list

# --- 2. 處理返回主選單 (我們修正過的) ---

def _go_to_main_options(e, bs: ft.BottomSheet, app_instance: 'App'):
    """
    輔助函式，用於「返回主選單」按鈕。
    它會先設定內容，然後再呼叫更新。
    """
    show_main_options(bs, app_instance)
    bs.update()

# --- 3. 助理介面的各種狀態 (View) ---

def show_filter_results_view(bs: ft.BottomSheet, app_instance: 'App'):
    """
    狀態 4: 顯示篩選後的行程結果
    """
    all_recs = load_recommendations()
    filters = app_instance.ai_filter_state
    
    logger.info(f"Applying filters: {filters}")
    filtered_recs = apply_filters(all_recs, filters)
    
    results_controls = []
    if not filtered_recs:
        results_controls.append(ft.Text(
            "喔喔... 找不到完全符合條件的景點。請放寬篩選再試一次。", 
            color=COLOR_TEXT_DARK
        ))
    else:
        results_controls.append(ft.Text(
            "為您推薦以下行程：", 
            size=16, 
            color=COLOR_TEXT_DARK
        ))
        random.shuffle(filtered_recs)
        # 最多顯示 3 個
        for item in filtered_recs[:3]:
            results_controls.append(
                ft.ListTile(
                    title=ft.Text(item['name'], color=COLOR_TEXT_DARK),
                    subtitle=ft.Text(item['description'], color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.PLACE, color=COLOR_TEXT_DARK)
                )
            )

    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("您的專屬行程", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.Divider(height=10),
                *results_controls, # 解包 List
                ft.Divider(height=20),
                ft.ElevatedButton(
                    "重新篩選",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: show_filter_view(bs, app_instance)
                ),
                ft.ElevatedButton(
                    "返回主選單",
                    icon=ft.Icons.MENU,
                    on_click=lambda e: _go_to_main_options(e, bs, app_instance)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    bs.update()

def on_filter_change(e: ft.ControlEvent, app_instance: 'App', filter_key: str):
    """
    當篩選器 (RadioGroup) 變動時，更新儲存的狀態
    """
    app_instance.ai_filter_state[filter_key] = e.data
    logger.info(f"Filter state changed: {app_instance.ai_filter_state}")

def show_filter_view(bs: ft.BottomSheet, app_instance: 'App'):
    """
    狀態 3: 顯示「規劃行程」的篩選器
    """
    filters = app_instance.ai_filter_state
    radio_text_style = ft.TextStyle(color=COLOR_TEXT_DARK) # 統一定義文字顏色

    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("請設定您的行程偏好", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                
                ft.Text("1. 活動地點？", color=COLOR_TEXT_DARK),
                ft.RadioGroup(
                    value=filters["type"], # 綁定儲存的狀態
                    on_change=lambda e: on_filter_change(e, app_instance, "type"),
                    content=ft.Row([
                        ft.Radio(value="indoor", label="室內", label_style=radio_text_style),
                        ft.Radio(value="outdoor", label="室外", label_style=radio_text_style),
                        ft.Radio(value="any", label="不限", label_style=radio_text_style),
                    ])
                ),
                
                ft.Text("2. 偏好類型？", color=COLOR_TEXT_DARK),
                ft.RadioGroup(
                    value=filters["preference"],
                    on_change=lambda e: on_filter_change(e, app_instance, "preference"),
                    content=ft.Column([
                        ft.Row([
                            ft.Radio(value="food", label="美食優先", label_style=radio_text_style),
                            ft.Radio(value="art", label="文藝展覽", label_style=radio_text_style),
                            ft.Radio(value="nature", label="親近自然", label_style=radio_text_style),
                        ]),
                        ft.Row([
                            ft.Radio(value="history", label="歷史人文", label_style=radio_text_style),
                            ft.Radio(value="urban_shopping", label="都市購物", label_style=radio_text_style),
                            ft.Radio(value="any", label="不限", label_style=radio_text_style),
                        ])
                    ])
                ),

                ft.Text("3. 交通方式？", color=COLOR_TEXT_DARK),
                ft.RadioGroup(
                    value=filters["transport"],
                    on_change=lambda e: on_filter_change(e, app_instance, "transport"),
                    content=ft.Row([
                        ft.Radio(value="car", label="開車/叫車", label_style=radio_text_style),
                        ft.Radio(value="public_transit", label="大眾運輸", label_style=radio_text_style),
                        ft.Radio(value="any", label="不限", label_style=radio_text_style),
                    ])
                ),
                
                # --- ↓↓↓ 新增的時間篩選器 ↓↓↓ ---
                ft.Text("4. 行程時間？", color=COLOR_TEXT_DARK),
                ft.RadioGroup(
                    value=filters["duration"],
                    on_change=lambda e: on_filter_change(e, app_instance, "duration"),
                    content=ft.Row(
                        controls=[
                            ft.Radio(value="1-2h", label="1-2 小時", label_style=radio_text_style),
                            ft.Radio(value="3-4h", label="3-4 小時", label_style=radio_text_style),
                            ft.Radio(value="6h+", label="6 小時+", label_style=radio_text_style),
                            ft.Radio(value="any", label="不限", label_style=radio_text_style),
                        ],
                        wrap=True # 允許換行
                    )
                ),
                # --- ↑↑↑ 新增結束 ↑↑↑ ---
                
                ft.Divider(height=20),
                
                ft.ElevatedButton(
                    "開始規劃",
                    icon=ft.Icons.CHECK,
                    on_click=lambda _: show_filter_results_view(bs, app_instance),
                    bgcolor=COLOR_BRAND_YELLOW
                ),
                ft.ElevatedButton(
                    "返回主選單",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: _go_to_main_options(e, bs, app_instance)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    bs.update()

def show_recommend_trip_options(bs: ft.BottomSheet, app_instance: 'App'):
    """
    狀態 2: 推薦特色行程 (舊功能)
    """
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("推薦您近期（2025年11月）的特色活動：", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.ListTile(
                    title=ft.Text("松山文創園區 2025 原創基地節", color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：即日起 ~ 11/16", color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.BRUSH),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=松山文創園區+2025原創基地節")
                ),
                ft.ListTile(
                    title=ft.Text("打開台北 (Open House Taipei)", color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：11/22 ~ 11/23", color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.HOUSE),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=打開台北+2025")
                ),
                ft.ListTile(
                    title=ft.Text("繽紛耶誕玩台北", color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：11/28 起", color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.SNOWING),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=繽紛耶誕玩台北+2025")
                ),
                ft.Divider(height=10),
                ft.ElevatedButton(
                    "返回主選單",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: _go_to_main_options(e, bs, app_instance)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    bs.update()

def on_chat_input_change(e: ft.ControlEvent, quick_answers_ref: ft.Ref[ft.Container]):
    """
    當使用者開始在 TextField 中打字時，隱藏快速問答按鈕
    """
    if e.data: # 如果 TextField 中有文字
        quick_answers_ref.current.visible = False
    else: # 如果 TextField 為空
        quick_answers_ref.current.visible = True
    
    quick_answers_ref.current.update()

def show_main_options(bs: ft.BottomSheet, app_instance: 'App'):
    """
    狀態 1: AI 助理主選單 (重構版)
    """
    
    # 建立一個 Ref 來控制快速問答按鈕的容器
    quick_answers_ref = ft.Ref[ft.Container]()
    
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                # 1. 快速問答 (可隱藏)
                ft.Container(
                    ref=quick_answers_ref,
                    content=ft.Column(
                        controls=[
                            ft.Text("您好！有什麼可以為您服務的嗎？", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                            
                            # --- 修正點 3: 使用 Container 包裹 ListTile ---
                            ft.Container(
                                content=ft.ListTile(
                                    title=ft.Text("幫我規劃附近的行程", color=COLOR_TEXT_DARK),
                                    leading=ft.Icon(ft.Icons.MAP),
                                    on_click=lambda _: show_filter_view(bs, app_instance),
                                    bgcolor=ft.Colors.TRANSPARENT # ListTile 本身透明
                                ),
                                bgcolor=ft.Colors.BLACK12, # Container 有背景色
                                border_radius=8            # Container 有圓角
                            ),
                            
                            ft.Container(
                                content=ft.ListTile(
                                    title=ft.Text("推薦當地特色行程", color=COLOR_TEXT_DARK),
                                    leading=ft.Icon(ft.Icons.STAR),
                                    on_click=lambda _: show_recommend_trip_options(bs, app_instance),
                                    bgcolor=ft.Colors.TRANSPARENT
                                ),
                                bgcolor=ft.Colors.BLACK12,
                                border_radius=8
                            ),

                            ft.Container(
                                content=ft.ListTile(
                                    title=ft.Text("線上 AI 客服支援", color=COLOR_TEXT_DARK),
                                    leading=ft.Icon(ft.Icons.SUPPORT_AGENT),
                                    bgcolor=ft.Colors.TRANSPARENT
                                ),
                                bgcolor=ft.Colors.BLACK12,
                                border_radius=8
                            )
                        ],
                        spacing=10
                    )
                ),
                
                ft.Divider(height=20),
                
                # 2. 聊天輸入框 (恆在)
                ft.TextField(
                    label="或是在這裡直接問我...",
                    prefix_icon=ft.Icons.CHAT_BUBBLE,
                    
                    # --- 修正點 4: 使用 ft.border_radius.all() ---
                    border_radius=ft.border_radius.all(10), 
                    # --- 修正結束 ---
                    
                    border_color=COLOR_BRAND_YELLOW,
                    focused_border_color=COLOR_BRAND_YELLOW,
                    on_change=lambda e: on_chat_input_change(e, quick_answers_ref),
                    color=COLOR_TEXT_DARK, # <-- 修正點 1: 補回文字顏色
                    label_style=ft.TextStyle(color=ft.Colors.GREY_700) # (讓 Label 顏色淺一點)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE
        ),
    )
    # (注意：這裡沒有 bs.update()，因為我們在 _go_to_main_options 和 open_ai_bottom_sheet 中處理)

# --- 4. 觸發點 (主函式) ---

def open_ai_bottom_sheet(app_instance: 'App'):
    """
    開啟或關閉 AI 助理的 BottomSheet
    """
    # 為了避免重複建立，我們將 BottomSheet 儲存在 app_instance 上
    if not hasattr(app_instance, "ai_bottom_sheet_ref"):
        app_instance.ai_bottom_sheet_ref = ft.BottomSheet(
            content=ft.Container(height=1), # 先給一個空的內容
            dismissible=True,
            # (您可以在這裡設定 BottomSheet 的背景色，例如)
            # bgcolor=COLOR_BG_LIGHT_TAN 
        )
        # 關鍵：將 BottomSheet 加入到 Page 的 overlay 中
        app_instance.page.overlay.append(app_instance.ai_bottom_sheet_ref)
        
    # 初始化 (或重設) 篩選器狀態
    if not hasattr(app_instance, "ai_filter_state"):
        app_instance.ai_filter_state = {}
        
    # --- ↓↓↓ 新增/重設所有篩選器 ↓↓↓ ---
    app_instance.ai_filter_state["type"] = "any"
    app_instance.ai_filter_state["preference"] = "any"
    app_instance.ai_filter_state["transport"] = "any"
    app_instance.ai_filter_state["duration"] = "any" # <-- 修正點
    # --- ↑↑↑ 新增/重設結束 ↑↑↑ ---
        
    bs = app_instance.ai_bottom_sheet_ref
    
    if bs.open:
        bs.open = False
    else:
        show_main_options(bs, app_instance) # 載入主選單
        bs.open = True
    
    app_instance.page.update() # (這是我們修正過的，使用 page.update())

# --- 5. 導出元件 (FAB) ---

def build_ai_fab(app_instance: 'App') -> ft.FloatingActionButton:
    """
    建立 AI 助理的懸浮按鈕
    """
    return ft.FloatingActionButton(
        icon=ft.Icons.WECHAT, # <-- 修正點 2: 修正大小写
        bgcolor=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        tooltip="AI 助理",
        on_click=lambda _: open_ai_bottom_sheet(app_instance)
    )