import os
import subprocess
import ctypes
import string
import requests
import datetime
import psutil
import pyautogui
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from plyer import notification
import cv2  # Для веб-камеры, pip install opencv-python
from PIL import Image  # Для скриншотов, pip install pillow

# Твой токен от BotFather
BOT_TOKEN = '8379452459:AAHLbcbWlt3ZPuJ8Pcf17vFEVoffLnkYhd0'

# Твой Telegram ID (только ты можешь управлять, чтобы никто не шутил над тобой 😂)
ALLOWED_USER_ID = 5186874712

# Папка для скачивания медиа
DOWNLOAD_FOLDER = os.path.expanduser('~/Downloads')

# Переменные для отслеживания режимов
waiting_for_wallpaper = False
waiting_for_file = False
waiting_for_music = False

# Диски для навигации
drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

def get_drives_text():
    if not drives:
        return 'Диски не найдены? Проверь ПК! 😅'
    return '\n'.join(f"{i+1}. 📁 {d}" for i, d in enumerate(drives))

def get_items(path):
    items = []
    try:
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            isdir = os.path.isdir(full)
            items.append((name, full, isdir))
    except PermissionError:
        items = [('Доступ запрещён! 🔒', '', False)]
    except Exception:
        items = [('Ошибка чтения! 😱', '', False)]
    return items

def get_list_text(items, path=''):
    if not items or items[0][0] in ['Доступ запрещён!', 'Ошибка чтения!']:
        return f"📂 {path}\n{items[0][0]} 😅\n\n🔙 Напиши 'back' для возврата"

    def get_icon(name, isdir):
        if isdir:
            return "📁"
        ext = name.lower().split('.')[-1]

        mapping = {
            # 📂 Системные / исполняемые
            "exe": "💾", "msi": "💾", "bat": "⚙️", "sh": "🐚", "dll": "🧩", "sys": "🖥️",
            
            # 📝 Тексты и коды
            "txt": "📝", "log": "📜", "md": "📘", "ini": "⚙️", "cfg": "⚙️",
            "py": "🐍", "js": "⚡", "ts": "⚡", "html": "🌐", "htm": "🌐", "css": "🎨",
            "json": "📑", "xml": "🧾", "yml": "📑", "yaml": "📑", "c": "💻", "cpp": "💻",
            "cs": "🖥️", "java": "☕", "php": "🐘", "rb": "💎", "go": "🐹", "rs": "🦀",

            # 🎶 Музыка
            "mp3": "🎵", "wav": "🎶", "flac": "🎼", "ogg": "🎧", "midi": "🎹",

            # 🎥 Видео
            "mp4": "🎥", "avi": "📼", "mkv": "🎬", "mov": "🎞️", "webm": "📽️",

            # 📷 Картинки
            "png": "🖼️", "jpg": "📷", "jpeg": "📷", "gif": "🤣", "bmp": "🖼️",
            "svg": "🔲", "ico": "🔘", "tiff": "🖼️", "psd": "🎨", "xcf": "🎨",

            # 📚 Документы
            "pdf": "📚", "doc": "📘", "docx": "📘", "odt": "📘",
            "xls": "📊", "xlsx": "📊", "ods": "📊",
            "ppt": "📈", "pptx": "📈", "odp": "📈",
            "rtf": "📑",

            # 📦 Архивы
            "zip": "📦", "rar": "📦", "7z": "📦", "tar": "📦", "gz": "📦", "bz2": "📦",

            # 🎮 Игры и образы
            "iso": "💿", "bin": "💿", "cue": "💿", "img": "💿", "vhd": "💽", "vhdx": "💽",
            "rom": "🎮", "sav": "💾",

            # 📡 Интернет
            "torrent": "🌀", "apk": "🤖", "ipa": "🍏", "xap": "📱",
            "batman": "🦇",  # чисто для прикола, вдруг найдёшь такой файл 😂
        }

        return mapping.get(ext, "📄")

    header = f"📂 {path}\n" if path else ''
    lines = []

    for i, (name, _, isdir) in enumerate(items):
        # диски
        if len(name) == 2 and name[1] == ":":
            icon = "💽" if name[0].lower() in ["c", "d"] else "💿"
        else:
            icon = get_icon(name, isdir)
        lines.append(f"{i+1}. {icon} {name}")

    return header + "\n".join(lines) + "\n\n👉 Напиши номер элемента или 'back' для возврата 😂🔥"

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return file_path
    # Если файл существует, добавляем дату и время
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    new_filename = f"{base}-{timestamp}{ext}"
    return os.path.join(DOWNLOAD_FOLDER, new_filename)

def check_user(update: Update) -> bool:
    return update.message.from_user.id == ALLOWED_USER_ID

async def start(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        await update.message.reply_text('Эй, чужак! Отказоно в доступе! 🚫')
        return
    await update.message.reply_text('Привет, босс! Я твой ПК-слуга !\n  Новые команды: \n /screenshot (скрин экрана!)\n /lock_screen (блок экрана)\n /restart (перезагрузка)\n /hibernate (спячка) \n/list_processes (список процесов),\n /kill_all (закрыть всё!)\n /set_brightness <0-100> (Яркасть экрана)\n /open_url <url> (Открыте URL)\n /take_photo (фото с вебки)\n /record_screen <сек> (Запись экрана)\n /system_info (Системная информация)\n /clean_temp (Очистка Temp)\n /random_wallpaper (Случайные обои)\n /mute (Тишина)\n /unmute (выключить тишину)\n /volume_up (Поднять громкость)\n /volume_down (Понизить громкость)\n/search_file <имя> (Поиск файла)\n/create_folder <путь> (Создать папку)\n/rename_file <старое> <новое> (Переименовать файл)\n/mouse_dance (танец мыши!) \nСтарые: \n/shutdown \n/open_app (любой файл!)\n /open_media\n/delete_file \n/close_app (Закрыть Приложение) \n/change_wallpaper (Изменить обои) \n/set_volume (Устоновить громкость) \n/show_message (Отправить сообщение) \n/sendfile (Отправить файл) \n/playmusic (Играть музыку). ')

async def shutdown(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Выключаю ПК! Спокойной ночи, хозяин! 😴😂')
    os.system('shutdown /s /t 1')

async def restart(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Перезагружаю ПК! Держись, будет тряска! 🔄😂')
    os.system('shutdown /r /t 1')

async def hibernate(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Укладываю ПК в спячку! Сладких снов, железяка! 🛌😂')
    os.system('shutdown /h')

async def lock_screen(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Блокирую экран! Никто не увидит твои секреты! 🔒😂')
    ctypes.windll.user32.LockWorkStation()


async def file_manager(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    context.user_data['mode'] = 'file_manager'
    context.user_data['page'] = 0  # Начинаем с первой страницы
    if 'current_path' not in context.user_data:
        context.user_data['current_path'] = os.path.expanduser('~')  # Старт в домашней папке 😂
    items = get_items(context.user_data['current_path'])
    await update.message.reply_text(get_list_text(items, context.user_data['current_path'], context.user_data['page']))

async def download_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Включи /file_manager и используй "download <num>" для скачивания файла! 😂')

async def upload_file(update: Update, context: CallbackContext) -> None:
    global waiting_for_upload
    if not check_user(update):
        return
    if 'current_path' not in context.user_data:
        await update.message.reply_text('Сначала войди в /file_manager и выбери папку! 😂')
        return
    waiting_for_upload = True
    await update.message.reply_text(f'Пришли файл для загрузки в {context.user_data["current_path"]}! 📤😂')

async def move_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    context.user_data['submode'] = 'move_source'
    await update.message.reply_text('Включи /file_manager, выбери источник и напиши "select <num>" для перемещения! Потом выбери цель и "paste"! 😂')

async def copy_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    context.user_data['submode'] = 'copy_source'
    await update.message.reply_text('Включи /file_manager, выбери источник и напиши "select <num>" для копирования! Потом выбери цель и "paste"! 😂')

async def wifi_list(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'networks']).decode('cp866')
        await update.message.reply_text(f'WiFi-сети вокруг тебя:\n{output}\nПопробуй угадать пароль соседа! 😜😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу найти сети: {str(e)} 😢')

async def battery(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged
            status = 'Заряжается 🔌' if plugged else 'На батарейке 🔋'
            await update.message.reply_text(f'Батарея: {percent}% {status}! Не дай ПК уснуть! 😴😂')
        else:
            await update.message.reply_text('Батарея? Это настольный ПК, бро! ⚡😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😢')

async def clipboard_get(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        await update.message.reply_text(f'В буфере: {data[:100]}... 😜😂' if len(data) > 100 else f'В буфере: {data} 😜😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу достать буфер: {str(e)} 😢')

async def clipboard_set(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Что записать в буфер? /clipboard_set lol 😂')
        return
    text = ' '.join(context.args)
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        await update.message.reply_text(f'Записал в буфер: {text}! Вставляй и ржи! 😜😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😢')

async def tell_joke(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    jokes = [
        "Почему программист предпочитает тёмную тему? Потому что светлый режим напоминает ему о счёте за электричество! 😜😂",
        "Какой язык программирования самый смешной? Python, потому что он шипит как змейка! 🐍😂",
        "Почему компьютер пошёл в арт-школу? Потому что он хотел научиться рисовать байты! 🎨😂",
    ]
    await update.message.reply_text(random.choice(jokes))

async def press_key(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Какую клавишу нажать? /press_key enter 😂')
        return
    key = context.args[0].lower()
    try:
        pyautogui.press(key)
        await update.message.reply_text(f'Нажал {key}! Как будто привидение за клавой! 👻😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу нажать: {str(e)} 😢')

async def type_text(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Что напечатать? /type_text Привет, мир! 😂')
        return
    text = ' '.join(context.args)
    try:
        pyautogui.write(text)
        await update.message.reply_text(f'Напечатал: {text}! Как хакер из 90-х! 💾😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😢')

async def open_app(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if context.args:
        path = ' '.join(context.args)
        try:
            os.startfile(path)
            await update.message.reply_text(f'Открываю {path}! Волшебство! ✨😂')
        except Exception as e:
            await update.message.reply_text(f'Ой-ой, не могу открыть {path}: {str(e)} 😅')
    else:
        context.user_data['mode'] = 'open'
        context.user_data['current_path'] = ''
        await update.message.reply_text('Ищем файл или папку для открытия! Выбери диск:\n' + get_drives_text() + '\n😂')

async def handle_media(update: Update, context: CallbackContext) -> None:
    global waiting_for_wallpaper, waiting_for_file, waiting_for_music
    if not check_user(update):
        return
    user_data = context.user_data
    if 'mode' in user_data:
        await update.message.reply_text('Эй, сейчас в режиме файлов! Закончи навигацию, потом шлёй медиа! 😜')
        return
    if waiting_for_music and update.message.audio:
        file = await update.message.audio.get_file()
        filename = update.message.audio.file_name or 'audio.mp3'
        file_path = get_unique_filename(filename)
        try:
            await file.download_to_drive(file_path)
            os.startfile(file_path)
            await update.message.reply_text(f'Включаю твою музыку: {os.path.basename(file_path)}! Качай головой! 🎵😂')
        except Exception as e:
            await update.message.reply_text(f'Ой, не могу воспроизвести: {str(e)} 😢')
        waiting_for_music = False
    elif waiting_for_file and (update.message.document or update.message.photo or update.message.video):
        if update.message.document:
            file = await update.message.document.get_file()
            filename = update.message.document.file_name
        elif update.message.photo:
            file = await update.message.photo[-1].get_file()
            filename = 'photo.jpg'
        elif update.message.video:
            file = await update.message.video.get_file()
            filename = 'video.mp4'
        file_path = get_unique_filename(filename)
        try:
            await file.download_to_drive(file_path)
            await update.message.reply_text(f'Сохранил {os.path.basename(file_path)} в Downloads! 📁😂')
        except Exception as e:
            await update.message.reply_text(f'Не могу сохранить: {str(e)} 😢')
        waiting_for_file = False
    elif update.message.photo and waiting_for_wallpaper:
        file = await update.message.photo[-1].get_file()
        file_path = os.path.join(DOWNLOAD_FOLDER, 'photo_wallpaper.jpg')
        await file.download_to_drive(file_path)
        try:
            abs_path = os.path.abspath(file_path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0)
            await update.message.reply_text(f'Сменил обои! ПК стильный! 🖼️😂')
        except Exception as e:
            await update.message.reply_text(f'Не могу сменить обои: {str(e)} 😭')
        waiting_for_wallpaper = False
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_path = os.path.join(DOWNLOAD_FOLDER, 'photo.jpg')
        await file.download_to_drive(file_path)
        os.startfile(file_path)
        await update.message.reply_text('Открываю фото! 📸😂')
    elif update.message.video:
        file = await update.message.video.get_file()
        file_path = os.path.join(DOWNLOAD_FOLDER, 'video.mp4')
        await file.download_to_drive(file_path)
        os.startfile(file_path)
        await update.message.reply_text('Открываю видео! 🍿😂')
    else:
        await update.message.reply_text('Пришли медиа после команды! 😜')

async def delete_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if context.args:
        file_path = ' '.join(context.args)
        try:
            os.remove(file_path)
            await update.message.reply_text(f'Удалил {file_path}! 🗑️😂')
        except Exception as e:
            await update.message.reply_text(f'Не могу удалить: {str(e)} 😢')
    else:
        context.user_data['mode'] = 'delete'
        context.user_data['current_path'] = ''
        await update.message.reply_text('Готов к удалению! Выбери диск:\n' + get_drives_text() + ' 😂')

async def close_app(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Какую прогу закрыть? /close_app chrome.exe 😂')
        return
    app_name = ' '.join(context.args)
    try:
        os.system(f'taskkill /IM {app_name} /F')
        await update.message.reply_text(f'Закрыл {app_name}! 🚪😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу закрыть: {str(e)} 😅')

async def kill_all(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Закрываю ВСЁ! ПК в шоке! 💥😂')
    os.system('taskkill /f /im *')

async def list_processes(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
    text = 'Запущенные процессы:\n' + '\n'.join([f"{p['pid']}: {p['name']}" for p in processes[:20]])  # Первые 20
    await update.message.reply_text(text + '\n...и ещё куча! 😂')

async def change_wallpaper(update: Update, context: CallbackContext) -> None:
    global waiting_for_wallpaper
    if not check_user(update):
        return
    if context.args:
        wallpaper_path = ' '.join(context.args)
        try:
            abs_path = os.path.abspath(wallpaper_path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0)
            await update.message.reply_text(f'Сменил обои на {wallpaper_path}! 🖼️😂')
        except Exception as e:
            await update.message.reply_text(f'Не могу: {str(e)} 😭')
    else:
        waiting_for_wallpaper = True
        await update.message.reply_text('Пришли фото! 📸😎')

async def random_wallpaper(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    images = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.lower().endswith(('.jpg', '.png'))]
    if images:
        import random
        img = random.choice(images)
        path = os.path.join(DOWNLOAD_FOLDER, img)
        try:
            abs_path = os.path.abspath(path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 0)
            await update.message.reply_text(f'Случайные обои: {img}! Сюрприз! 🎲😂')
        except Exception as e:
            await update.message.reply_text(f'Не могу: {str(e)} 😭')
    else:
        await update.message.reply_text('Нет картинок в Downloads! Добавь! 😜')

async def set_volume(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Уровень громкости? /set_volume 50 😂')
        return
    try:
        level = float(' '.join(context.args))
        if not 0 <= level <= 100:
            raise ValueError('0-100! 😆')
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        await update.message.reply_text(f'Громкость {level}%! 🎵😂')
    except ValueError as e:
        await update.message.reply_text(f'Неверно: {str(e)} 😜')
    except Exception as e:
        await update.message.reply_text(f'Проблема: {str(e)} 😭')

async def volume_up(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new = min(1.0, current + 0.1)
        volume.SetMasterVolumeLevelScalar(new, None)
        await update.message.reply_text('Громче! +10%! 🔊😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😅')

async def volume_down(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new = max(0.0, current - 0.1)
        volume.SetMasterVolumeLevelScalar(new, None)
        await update.message.reply_text('Тише! -10%! 🤫😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😅')

async def mute(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
        await update.message.reply_text('Звук выключен! Тишина! 🤐😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😭')

async def unmute(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)
        await update.message.reply_text('Звук включен! Громко! 🔊😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😭')

async def set_brightness(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Яркость 0-100? /set_brightness 50 😂')
        return
    try:
        level = int(' '.join(context.args))
        if not 0 <= level <= 100:
            raise ValueError('0-100! 😆')
        # Для Windows, используем WMI (нужен pywin32)
        import wmi
        c = wmi.WMI(namespace="wmi")
        brightness_methods = c.WmiMonitorBrightnessMethods()[0]
        brightness_methods.WmiSetBrightness(1, level)
        await update.message.reply_text(f'Яркость {level}%! Светло! 💡😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу изменить яркость: {str(e)} (Установи pywin32!) 😭')

async def open_url(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Какой URL? /open_url https://google.com 😂')
        return
    url = ' '.join(context.args)
    try:
        os.startfile(url)
        await update.message.reply_text(f'Открываю {url}! Сёрфинг! 🌊😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу открыть URL: {str(e)} 😅')

async def screenshot(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        screenshot = pyautogui.screenshot()
        file_path = os.path.join(DOWNLOAD_FOLDER, f'screenshot-{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.png')
        screenshot.save(file_path)
        with open(file_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption='Скриншот твоего ПК! 📸😂')
        os.remove(file_path)  # Удаляем после отправки
    except Exception as e:
        await update.message.reply_text(f'Не могу сделать скрин: {str(e)} (Установи pyautogui!) 😭')

async def take_photo(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    try:
        cap = cv2.VideoCapture(0)  # Веб-камера
        ret, frame = cap.read()
        if ret:
            file_path = os.path.join(DOWNLOAD_FOLDER, f'photo-{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.jpg')
            cv2.imwrite(file_path, frame)
            cap.release()
            with open(file_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption='Фото с вебки! 😎📷😂')
            os.remove(file_path)
        else:
            await update.message.reply_text('Камера не работает! 😢')
    except Exception as e:
        await update.message.reply_text(f'Ошибка фото: {str(e)} (Установи opencv-python!) 😭')

async def record_screen(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Сколько секунд записывать? /record_screen 10 😂')
        return
    try:
        duration = int(' '.join(context.args))
        file_path = os.path.join(DOWNLOAD_FOLDER, f'record-{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.mp4')
        # Простая запись через ffmpeg (предполагаем, что установлен)
        cmd = f'ffmpeg -f gdigrab -framerate 10 -t {duration} -i desktop {file_path}'
        subprocess.run(cmd, shell=True)
        await update.message.reply_video(open(file_path, 'rb'), caption=f'Запись экрана {duration} сек! 🎥😂')
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f'Не могу записать: {str(e)} (Установи ffmpeg!) 😭')

async def system_info(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    info = f'ОС: {os.name}\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%\nДиски: {len(drives)}'
    await update.message.reply_text(info + '\nТвой ПК в форме! 💪😂')

async def clean_temp(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    temp_path = os.environ.get('TEMP', '')
    try:
        for file in os.listdir(temp_path):
            os.remove(os.path.join(temp_path, file))
        await update.message.reply_text('Очистил temp! Чисто, как слеза! 🧼😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу очистить: {str(e)} 😢')

async def search_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Что искать? /search_file meme.jpg 😂')
        return
    search_name = ' '.join(context.args)
    results = []
    for root, dirs, files in os.walk('C:\\'):  # Поиск по C:
        if search_name in files:
            results.append(os.path.join(root, search_name))
        if len(results) > 5:  # Ограничим
            break
    text = 'Нашёл: ' + '\n'.join(results) if results else 'Ничего! 😢'
    await update.message.reply_text(text + ' 😂')

async def create_folder(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Путь для папки? /create_folder C:\\NewFolder 😂')
        return
    path = ' '.join(context.args)
    try:
        os.makedirs(path, exist_ok=True)
        await update.message.reply_text(f'Создал папку {path}! Дом готов! 🏠😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу создать: {str(e)} 😢')

async def rename_file(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if len(context.args) < 2:
        await update.message.reply_text('Старое и новое имя? /rename_file old.txt new.txt 😂')
        return
    old = context.args[0]
    new = ' '.join(context.args[1:])
    try:
        os.rename(old, new)
        await update.message.reply_text(f'Переименовал {old} в {new}! Круто! 🔄😂')
    except Exception as e:
        await update.message.reply_text(f'Не могу: {str(e)} 😢')

async def mouse_dance(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    await update.message.reply_text('Мышь танцует! 💃🖱️😂')
    for _ in range(10):
        pyautogui.moveRel(100, 100, duration=0.5)
        pyautogui.moveRel(-100, -100, duration=0.5)

async def show_message(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    if not context.args:
        await update.message.reply_text('Текст? /show_message Hello --title Bot 😂')
        return
    args = ' '.join(context.args)
    title = 'PC Controller Bot'
    message = args
    if '--title' in args:
        parts = args.split('--title')
        message = parts[0].strip()
        if len(parts) > 1:
            title = parts[1].strip()
    if not message:
        await update.message.reply_text('Текст пустой! 😜')
        return
    try:
        notification.notify(title=title, message=message, timeout=10)
        await update.message.reply_text(f'Показал: "{message}"! 📢😂')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)} 😭')

async def send_file(update: Update, context: CallbackContext) -> None:
    global waiting_for_file
    if not check_user(update):
        return
    waiting_for_file = True
    await update.message.reply_text('Пришли файл! 📁😂')

async def play_music(update: Update, context: CallbackContext) -> None:
    global waiting_for_music
    if not check_user(update):
        return
    waiting_for_music = True
    await update.message.reply_text('Пришли аудио! 🎵😂')

async def handle_navigation(update: Update, context: CallbackContext) -> None:
    if not check_user(update):
        return
    user_data = context.user_data
    if 'mode' not in user_data:
        return
    mode = user_data['mode']
    text = update.message.text.strip()
    current_path = user_data.get('current_path', '')

    if text.lower() == 'back':
        if current_path == '':
            await update.message.reply_text('Уже на дисках! 😂')
            return
        if current_path.endswith(':'):
            user_data['current_path'] = ''
            await update.message.reply_text('Вернулся к дискам!\n' + get_drives_text())
        else:
            parent = os.path.dirname(current_path)
            user_data['current_path'] = parent
            items = get_items(parent)
            await update.message.reply_text(get_list_text(items, parent))
        return

    try:
        index = int(text) - 1
        if current_path == '':
            if 0 <= index < len(drives):
                selected = drives[index]
                user_data['current_path'] = selected
                items = get_items(selected)
                await update.message.reply_text(get_list_text(items, selected))
            else:
                await update.message.reply_text('Нет такого диска! 😅')
        else:
            items = get_items(current_path)
            if 0 <= index < len(items):
                name, full, isdir = items[index]
                if items[0][0] in ['Доступ запрещён!', 'Ошибка чтения!']:
                    await update.message.reply_text('Доступ запрещён! 🔒😂')
                    return
                if isdir:
                    user_data['current_path'] = full
                    new_items = get_items(full)
                    await update.message.reply_text(get_list_text(new_items, full))
                else:
                    if mode == 'open':
                        try:
                            os.startfile(full)
                            await update.message.reply_text(f'Открыл {name}! 🚀😂')
                        except Exception as e:
                            await update.message.reply_text(f'Не могу открыть: {str(e)} 😢')
                    elif mode == 'delete':
                        try:
                            os.remove(full)
                            await update.message.reply_text(f'Удалил {name}! 🗑️😂')
                        except Exception as e:
                            await update.message.reply_text(f'Не удалил: {str(e)} 😢')
                    del user_data['mode']
                    del user_data['current_path']
            else:
                await update.message.reply_text('Номер неверный! 🤦😂')
    except ValueError:
        await update.message.reply_text("Пиши число или 'back'! 😆")
    except Exception as e:
        await update.message.reply_text(f'Сломался: {str(e)} 😂')

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('shutdown', shutdown))
    application.add_handler(CommandHandler('restart', restart))
    application.add_handler(CommandHandler('hibernate', hibernate))
    application.add_handler(CommandHandler('lock_screen', lock_screen))
    application.add_handler(CommandHandler('file_manager', file_manager))
    application.add_handler(CommandHandler('download_file', download_file))
    application.add_handler(CommandHandler('upload_file', upload_file))
    application.add_handler(CommandHandler('move_file', move_file))
    application.add_handler(CommandHandler('copy_file', copy_file))
    application.add_handler(CommandHandler('wifi_list', wifi_list))
    application.add_handler(CommandHandler('battery', battery))
    application.add_handler(CommandHandler('clipboard_get', clipboard_get))
    application.add_handler(CommandHandler('clipboard_set', clipboard_set))
    application.add_handler(CommandHandler('tell_joke', tell_joke))
    application.add_handler(CommandHandler('press_key', press_key))
    application.add_handler(CommandHandler('type_text', type_text))
    application.add_handler(CommandHandler('close_app', close_app))
    application.add_handler(CommandHandler('kill_all', kill_all))
    application.add_handler(CommandHandler('list_processes', list_processes))
    application.add_handler(CommandHandler('change_wallpaper', change_wallpaper))
    application.add_handler(CommandHandler('random_wallpaper', random_wallpaper))
    application.add_handler(CommandHandler('set_volume', set_volume))
    application.add_handler(CommandHandler('volume_up', volume_up))
    application.add_handler(CommandHandler('volume_down', volume_down))
    application.add_handler(CommandHandler('mute', mute))
    application.add_handler(CommandHandler('unmute', unmute))
    application.add_handler(CommandHandler('set_brightness', set_brightness))
    application.add_handler(CommandHandler('open_url', open_url))
    application.add_handler(CommandHandler('screenshot', screenshot))
    application.add_handler(CommandHandler('take_photo', take_photo))
    application.add_handler(CommandHandler('record_screen', record_screen))
    application.add_handler(CommandHandler('system_info', system_info))
    application.add_handler(CommandHandler('clean_temp', clean_temp))
    application.add_handler(CommandHandler('search_file', search_file))
    application.add_handler(CommandHandler('mouse_dance', mouse_dance))
    application.add_handler(CommandHandler('show_message', show_message))
    application.add_handler(CommandHandler('sendfile', send_file))
    application.add_handler(CommandHandler('playmusic', play_music))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO, handle_media))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_navigation))

    application.run_polling()

if __name__ == '__main__':
    main()