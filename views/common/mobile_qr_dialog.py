# app/views/common/mobile_qr_dialog.py (或放在您方便的地方)
import flet as ft
import qrcode
import socket
import io
import base64

def get_local_ip():
    """自動取得本機在區網內的 IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 這裡不需要真的連線，只是用來測試路由
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def show_mobile_simulation_dialog(page: ft.Page, port=8550):
    """顯示手機模擬用的 QR Code"""
    
    # 1. 取得網址
    ip = get_local_ip()
    url = f"http://{ip}:{port}"
    print(f"Mobile URL: {url}") # 在 Terminal 印出方便除錯

    # 2. 生成 QR Code 圖片 (Base64)
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 轉成 Flet 可以讀取的 Base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 3. 建立 Dialog
    dlg = ft.AlertDialog(
        title=ft.Text("手機模擬體驗"),
        content=ft.Column([
            ft.Text("請確保手機與電腦連線至同一個 Wi-Fi", color="red", size=12),
            ft.Container(height=10),
            ft.Image(src_base64=img_str, width=250, height=250),
            ft.Container(height=10),
            ft.Text(f"或手動輸入網址:"),
            ft.Text(url, weight="bold", size=20, selectable=True),
        ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[
            ft.TextButton("關閉", on_click=lambda e: page.close(dlg))
        ],
    )
    
    page.open(dlg)