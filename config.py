from flet import Icons as icons

WINDOW_WIDTH = 375
WINDOW_HEIGHT = 667

######################
### User Dashboard ###
######################
USER_DASHBOARD_IMAGE = "https://media.istockphoto.com/id/2198413055/photo/brazilian-couple-arriving-at-hotel.jpg?s=1024x1024&w=is&k=20&c=D5XFMhcnxpiaXRfA2a2VaybSkpPHx9SKRUP3jJ0tpeQ="
USER_DASHBOARD_NAVIGATOR_ITEMS = [
    {"icon": icons.MENU, "label": "更多"},
    {"icon": icons.LOCATION_ON, "label": "即時預約"},
    {"icon": icons.HOME_OUTLINED, "label": "首頁"},
    {"icon": icons.EDIT_CALENDAR, "label": "事先預約"},
    {"icon": icons.CALL, "label": "客服"},
]
USER_DASHBOARD_MARQUEE_MESSAGES = [
    "11/1 14:00-11/2 02:00 白晝之夜在信義區舉行",
    "【AI 助手】偵測到您在 W 飯店附近...",
    "週末行李托運 8 折優惠券已發送！",
    "e-baggage 提醒您：提早預約，旅途更輕鬆。",
]
USER_DASHBOARD_MORE_ITEMS = [
    {"icon": icons.PERSON_OUTLINE, "label": "帳號設定", "route": "/app/user/profile"},
    {"icon": icons.LOCATION_ON, "label": "即時預約", "route": "/app/user/user_booking_instant"},
    {"icon": icons.EDIT_CALENDAR, "label": "事先預約", "route": "/app/user/user_booking_previous"},
    {"icon": icons.FAVORITE_BORDER, "label": "我的最愛", "route": "/app/user/favorites"},
    {"icon": icons.HISTORY, "label": "行程紀錄", "route": "/app/user/history"},
    {"icon": icons.CALL, "label": "客服聯繫", "route": "/app/user/support"},
    {"icon": icons.SETTINGS_OUTLINED, "label": "系統設定", "route": "/app/user/settings"},
]

USER_DASHBOARD_DEFAULT_LOCATION = (25.01443, 121.4638)  # 板橋車站
# USER_DASHBOARD_DEFAULT_LOCATION = (25.03396, 121.5644)  # 台北 101
# USER_DASHBOARD_MAP_TEMPLATE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
USER_DASHBOARD_MAP_TEMPLATE = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
# USER_DASHBOARD_MAP_TEMPLATE = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"