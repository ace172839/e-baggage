import flet as ft
from typing import TYPE_CHECKING
from constants import *


if TYPE_CHECKING:
    from main import App

# --- 狀態 3: 顯示行程規劃 (Demo 內容) ---
def show_trip_details(bs: ft.BottomSheet, trip_type: str):
    """
    顯示最終的行程規劃內容。
    (目前為 Demo 內容，之後可以替換)
    """
    
    # 之後您可以提供 trip_short, trip_half_day 等變數
    if trip_type == "short":
        content_text = "這裡是「1-2 小時短行程」的規劃：\n\n1. 台北101 觀景台\n2. 幾米月亮公車\n3. 國父紀念館水舞"
    elif trip_type == "half":
        content_text = "這裡是「3-4 小時半日行程」的規劃：\n\n1. 龍山寺\n2. 剝皮寮老街\n3. 華西街夜市"
    else: # all
        content_text = "這裡是「6 小時以上整日行程」的規劃：\n\n1. 故宮博物院\n2. 士林官邸\n3. 士林夜市"
        
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("為您規劃的行程如下：", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.Text(content_text, size=12, color=COLOR_TEXT_DARK),
                ft.Divider(height=10),
                ft.ElevatedButton(
                    "返回",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: show_plan_trip_options(bs) # 返回上一層 (狀態 2)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    bs.update()

def _go_to_main_options(e, bs: ft.BottomSheet):
    """
    一個輔助函式，用於「返回主選單」按鈕。
    它會先設定內容，然後再呼叫更新。
    """
    show_main_options(bs)
    bs.update()

# --- 狀態 2 (流程 1): 規劃行程的選項 ---
def show_plan_trip_options(bs: ft.BottomSheet):
    """
    顯示「規劃行程」的子選項
    """
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("請選擇您想要的行程長度：", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.ListTile(
                    title=ft.Text("1-2 小時短行程", size=12, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.TIMER_3_SELECT),
                    on_click=lambda _: show_trip_details(bs, "short")
                ),
                ft.ListTile(
                    title=ft.Text("3-4 小時半日行程", size=12, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.TIMER_10_SELECT),
                    on_click=lambda _: show_trip_details(bs, "half")
                ),
                ft.ListTile(
                    title=ft.Text("6 小時以上整日行程", size=12, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.TIMER_OFF),
                    on_click=lambda _: show_trip_details(bs, "all")
                ),
                ft.Divider(height=10),
                ft.ElevatedButton(
                    "返回主選單",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: _go_to_main_options(e, bs) # 返回主選單 (狀態 1)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )
    )
    bs.update()

# --- 狀態 2 (流程 2): 推薦特色行程 ---
def show_recommend_trip_options(bs: ft.BottomSheet):
    """
    顯示「推薦特色行程」的選項
    (這些是我根據 2025 年 11 月的時事所搜尋到的 Demo 內容)
    """
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("推薦您近期（2025年11月）的特色活動：", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.ListTile(
                    title=ft.Text("松山文創園區 2025 原創基地節", size=12, color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：即日起 ~ 11/16", size=10, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.BRUSH),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    # 點擊會嘗試打開瀏覽器搜尋
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=松山文創園區+2025原創基地節")
                ),
                ft.ListTile(
                    title=ft.Text("打開台北 (Open House Taipei)", size=12, color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：11/22 ~ 11/23", size=10, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.HOUSE),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=打開台北+2025")
                ),
                ft.ListTile(
                    title=ft.Text("繽紛耶誕玩台北", size=12, color=COLOR_TEXT_DARK),
                    subtitle=ft.Text("活動日期：11/28 起", size=10, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.SNOWING),
                    trailing=ft.Icon(ft.Icons.OPEN_IN_NEW),
                    on_click=lambda _: bs.page.launch_url("https://www.google.com/search?q=繽紛耶誕玩台北+2025")
                ),
                ft.Divider(height=10),
                ft.ElevatedButton(
                    "返回主選單",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: _go_to_main_options(e, bs) # 返回主選單 (狀態 1)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.ADAPTIVE
        )
    )
    bs.update()

# --- 狀態 1: AI 助理主選單 ---
def show_main_options(bs: ft.BottomSheet):
    """
    顯示 AI 助理的主選單 (第一層)
    """
    bs.content = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("您好！有什麼可以為您服務的嗎？", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_DARK),
                ft.ListTile(
                    title=ft.Text("幫我規劃附近的行程", size=14, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.MAP),
                    on_click=lambda _: show_plan_trip_options(bs), # 進入狀態 2 (流程 1)
                    bgcolor=ft.Colors.WHITE38
                ),
                ft.ListTile(
                    title=ft.Text("推薦當地特色行程", size=14, color=COLOR_TEXT_DARK),
                    leading=ft.Icon(ft.Icons.STAR),
                    on_click=lambda _: show_recommend_trip_options(bs), # 進入狀態 2 (流程 2)
                    bgcolor=ft.Colors.WHITE38
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
        ),
        bgcolor=ft.Colors.WHITE38
    )

# --- 觸發點: 開啟 AI 助理 ---
def open_ai_bottom_sheet(app_instance: 'App'):
    """
    開啟或關閉 AI 助理的 BottomSheet
    """
    # 為了避免重複建立，我們將 BottomSheet 儲存在 app_instance 上
    if not hasattr(app_instance, "ai_bottom_sheet_ref"):
        app_instance.ai_bottom_sheet_ref = ft.BottomSheet(
            content=ft.Container(height=1), # 先給一個空的內容
            dismissible=True
        )
        # 關鍵：將 BottomSheet 加入到 Page 的 overlay 中
        app_instance.page.overlay.append(app_instance.ai_bottom_sheet_ref)
    
    bs = app_instance.ai_bottom_sheet_ref
    
    # 如果已經打開，就關閉它
    if bs.open:
        bs.open = False
    # 如果是關閉的，就用「主選單」內容填充它，然後打開
    else:
        show_main_options(bs) # 載入主選單
        bs.open = True
    
    app_instance.page.update() # 執行打開或關閉

# --- 導出元件: 建立懸浮按鈕 (FAB) ---
def build_ai_fab(app_instance: 'App') -> ft.FloatingActionButton:
    """
    建立 AI 助理的懸浮按鈕
    """
    return ft.FloatingActionButton(
        icon=ft.Icons.WECHAT,
        shape=ft.CircleBorder(),
        bgcolor=ft.Colors.WHITE,
        tooltip="AI 助理",
        on_click=lambda _: open_ai_bottom_sheet(app_instance)
    )