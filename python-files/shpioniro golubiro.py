import os
import time
import subprocess
import psutil
import requests
import pyautogui
import telebot
from telebot import types
import win32gui
import win32process
import threading
import logging
import tempfile

# === Настройки ===
TOKEN = "7979263447:AAEFLa50EUCA7Df_Wbx04Z2idci10kJ61Ps"  # Токен бота
CHAT_ID = 1516697851  # ID пользователя
bot = telebot.TeleBot(TOKEN, threaded=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Глобальные переменные для гибернации ===
last_activity = time.time()
HIBERNATION_TIMEOUT = 300  # 5 минут бездействия
POLLING_TIMEOUT_NORMAL = 5  # Таймаут опроса в нормальном режиме (сек)
POLLING_TIMEOUT_HIBERNATE = 15  # Таймаут опроса в режиме гибернации (сек)
current_polling_timeout = POLLING_TIMEOUT_NORMAL
polling_active = True

# === Вспомогательные функции ===
def check_access(message):
    """Проверяет, имеет ли пользователь доступ."""
    return message.chat.id == CHAT_ID

def get_foreground_app():
    """Получает информацию об активном окне."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc_name = psutil.Process(pid).name()
        return title, proc_name, pid
    except Exception as e:
        logging.error(f"Ошибка в get_foreground_app: {e}")
        return "Неизвестно", "Неизвестно", 0

def kill_process(pid):
    """Завершает процесс по PID."""
    try:
        psutil.Process(pid).kill()
        return True
    except Exception as e:
        logging.error(f"Ошибка при завершении процесса {pid}: {e}")
        return False

def make_screenshot():
    """Делает скриншот и отправляет его."""
    try:
        # Сохраняем скриншот во временной папке
        temp_dir = tempfile.gettempdir()
        file = os.path.join(temp_dir, f"screen_{int(time.time())}.png")
        pyautogui.screenshot().save(file)
        with open(file, "rb") as f:
            bot.send_photo(CHAT_ID, f)
        os.remove(file)
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота: {e}")
        bot.send_message(CHAT_ID, "⚠️ Не удалось сделать скриншот")

def ensure_autorun():
    """Добавляет скрипт в автозагрузку Windows."""
    try:
        startup = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut = os.path.join(startup, "pc_bot.lnk")
        if not os.path.exists(shortcut):
            subprocess.run(
                f'powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut(\'{shortcut}\');'
                f'$s.TargetPath=\'{__file__}\';$s.Save()"',
                shell=True, check=True
            )
            logging.info("Скрипт добавлен в автозагрузку")
    except Exception as e:
        logging.error(f"Ошибка при настройке автозагрузки: {e}")

def wait_for_internet():
    """Ожидает подключения к интернету, проверяя несколько URL."""
    urls = ["https://www.google.com", "https://www.cloudflare.com", "https://www.amazon.com"]
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logging.info(f"Интернет-соединение установлено через {url}")
                    return True
            except requests.RequestException:
                logging.warning(f"Не удалось подключиться к {url}")
        attempt += 1
        logging.warning(f"Попытка {attempt}/{max_attempts}: Нет интернета, повтор через 10 сек")
        time.sleep(10)

    logging.error("Не удалось установить интернет-соединение после всех попыток")
    bot.send_message(CHAT_ID, "⚠️ Не удалось подключиться к интернету. Бот остановлен.")
    return False

# === Гибернация ===
def update_activity():
    """Обновляет время последней активности."""
    global last_activity, current_polling_timeout, polling_active
    last_activity = time.time()
    if current_polling_timeout != POLLING_TIMEOUT_NORMAL:
        current_polling_timeout = POLLING_TIMEOUT_NORMAL
        polling_active = True
        logging.info("Перешел в нормальный режим")

def hibernation_check():
    """Проверяет необходимость перехода в режим гибернации."""
    global last_activity, current_polling_timeout, polling_active
    while True:
        if time.time() - last_activity > HIBERNATION_TIMEOUT and current_polling_timeout != POLLING_TIMEOUT_HIBERNATE:
            current_polling_timeout = POLLING_TIMEOUT_HIBERNATE
            polling_active = True
            logging.info("Перешел в режим гибернации")
        time.sleep(60)

# === Главное меню ===
def main_menu():
    """Создает главное меню."""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔍 Активное окно", "📸 Скриншот")
    kb.add("🔄 Обновить библиотеки")
    return kb

# === Команды ===
@bot.message_handler(commands=["start"])
def start(message):
    """Обработчик команды /start."""
    if not check_access(message):
        return
    update_activity()
    bot.send_message(message.chat.id, "👋 Привет! Это бот для управления ПК", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Активное окно")
def fg(message):
    """Обработчик команды 'Активное окно'."""
    if not check_access(message):
        return
    update_activity()
    title, proc_name, pid = get_foreground_app()
    if pid == 0:
        bot.send_message(message.chat.id, "⚠️ Не удалось получить информацию об окне")
        return
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("❌ Закрыть", callback_data=f"kill_{pid}"))
    bot.send_message(
        message.chat.id,
        f"🪟 Активное окно:\n\nНазвание: {title}\nПроцесс: {proc_name}\nPID: {pid}",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("kill_"))
def cb_kill(call):
    """Обработчик кнопки закрытия процесса."""
    if call.message.chat.id != CHAT_ID:
        return
    update_activity()
    pid = int(call.data.split("_")[1])
    if kill_process(pid):
        bot.answer_callback_query(call.id, f"✅ Закрыл PID {pid}")
    else:
        bot.answer_callback_query(call.id, f"⚠️ Не удалось закрыть {pid}")

@bot.message_handler(func=lambda m: m.text == "📸 Скриншот")
def scr(message):
    """Обработчик команды 'Скриншот'."""
    if not check_access(message):
        return
    update_activity()
    make_screenshot()

@bot.message_handler(func=lambda m: m.text == "🔄 Обновить библиотеки")
def upd(message):
    """Обработчик команды 'Обновить библиотеки'."""
    if not check_access(message):
        return
    update_activity()
    bot.send_message(message.chat.id, "⏳ Обновляю пакеты...")
    try:
        subprocess.run("pip install --upgrade pip telebot psutil pyautogui pywin32 requests", shell=True, check=True)
        bot.send_message(message.chat.id, "✅ Обновление завершено")
    except Exception as e:
        logging.error(f"Ошибка при обновлении библиотек: {e}")
        bot.send_message(message.chat.id, "⚠️ Не удалось обновить библиотеки")

# === Запуск ===
if __name__ == "__main__":
    if wait_for_internet():
        ensure_autorun()
        threading.Thread(target=hibernation_check, daemon=True).start()
        while True:
            try:
                if polling_active:
                    bot.infinity_polling(timeout=current_polling_timeout)
            except Exception as e:
                logging.error(f"Ошибка в infinity_polling: {e}")
                time.sleep(10)