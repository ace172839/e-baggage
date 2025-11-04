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