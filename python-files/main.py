import os
import sqlite3
import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils.exceptions import ChatNotFound
import openpyxl
from openpyxl import Workbook
import io

# Настройки
API_TOKEN = '8356738228:AAF4LdsnsSZRvWT_a-vbVs-46HhZde-f0gI'
ADMIN_IDS = [7615176654]  # ID администраторов
SCHOOL_NAME = "56"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Классы состояний
class AuthState(StatesGroup):
    waiting_for_school = State()

class TrackSubmission(StatesGroup):
    waiting_for_link = State()
    waiting_for_title = State()
    waiting_for_file = State()

class SupportState(StatesGroup):
    waiting_for_message = State()

class AdminState(StatesGroup):
    editing_message = State()
    adding_admin = State()
    removing_admin = State()

# Инициализация БД
def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        school_name TEXT,
        attempts INTEGER DEFAULT 0,
        is_banned BOOLEAN DEFAULT FALSE,
        full_name TEXT,
        username TEXT,
        UNIQUE(user_id)
    )
    ''')
    
    # Таблица треков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        data TEXT,
        type TEXT,
        status TEXT DEFAULT 'pending',
        moderator_comment TEXT,
        priority INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица поддержки
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS support_requests (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        message TEXT,
        attachment TEXT,
        status TEXT DEFAULT 'open',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица админов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        UNIQUE(user_id)
    )
    ''')
    
    # Таблица сообщений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        key TEXT UNIQUE,
        value TEXT
    )
    ''')
    
    # Добавляем стандартные сообщения
    default_messages = [
        ('rules', 'Правила отправки песен:\n1. Трек должен быть качественным\n2. Не допускается ненормативная лексика'),
        ('disco_info', 'Дискотека проходит каждую пятницу с 18:00 до 22:00'),
        ('about_bot', 'Этот бот создан для отправки песен на школьные дискотеки')
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO messages (key, value) VALUES (?, ?)', default_messages)
    
    # Добавляем админов по умолчанию
    for admin_id in ADMIN_IDS:
        cursor.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
    
    conn.commit()
    conn.close()

init_db()

# Вспомогательные функции
def is_admin(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

def get_message(key):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM messages WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Сообщение не найдено"

def get_tracks_count():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tracks WHERE status = 'approved'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Клавиатуры
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Отправить песню"))
    keyboard.add(KeyboardButton("Правила отправки"), KeyboardButton("Информация о дискотеке"))
    keyboard.add(KeyboardButton("О боте"), KeyboardButton("Техподдержка"))
    return keyboard

def admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Модерация треков"), KeyboardButton("Запросы в техподдержку"))
    keyboard.add(KeyboardButton("Изменить админов"), KeyboardButton("Изменить сообщения"))
    keyboard.add(KeyboardButton("Отмодерированные треки"), KeyboardButton("Логи"))
    keyboard.add(KeyboardButton("Главное меню"))
    return keyboard

def track_options_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Ссылка", callback_data="link"))
    keyboard.add(InlineKeyboardButton("Название", callback_data="title"))
    keyboard.add(InlineKeyboardButton("Файл", callback_data="file"))
    return keyboard

def moderation_keyboard(track_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Принять", callback_data=f"approve_{track_id}"))
    keyboard.add(InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{track_id}"))
    keyboard.add(InlineKeyboardButton("🔁 Уже был", callback_data=f"duplicate_{track_id}"))
    return keyboard

def support_keyboard(request_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Ответить", callback_data=f"reply_{request_id}"))
    keyboard.add(InlineKeyboardButton("Закрыть", callback_data=f"close_{request_id}"))
    return keyboard

def message_edit_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Правила", callback_data="edit_rules"))
    keyboard.add(InlineKeyboardButton("Инфо о дискотеке", callback_data="edit_disco"))
    keyboard.add(InlineKeyboardButton("О боте", callback_data="edit_about"))
    return keyboard

def admin_management_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Добавить админа", callback_data="add_admin"))
    keyboard.add(InlineKeyboardButton("Удалить админа", callback_data="remove_admin"))
    return keyboard

# Хэндлеры
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        await AuthState.waiting_for_school.set()
        await message.answer("Для доступа к боту введите название вашей школы:")
    else:
        if user[4]:  # is_banned
            await message.answer("Ваш аккаунт заблокирован. Обратитесь в поддержку.")
        else:
            if is_admin(user_id):
                await message.answer("Добро пожаловать в админ-панель!", reply_markup=admin_keyboard())
            else:
                tracks_count = get_tracks_count()
                await message.answer(f"Главное меню. Всего отправлено треков: {tracks_count}", reply_markup=main_keyboard())
    
    conn.close()

@dp.message_handler(state=AuthState.waiting_for_school)
async def process_school(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    school_name = message.text
    attempts = 1
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    if school_name == SCHOOL_NAME:
        cursor.execute("INSERT OR REPLACE INTO users (user_id, school_name, full_name, username) VALUES (?, ?, ?, ?)",
                      (user_id, school_name, message.from_user.full_name, message.from_user.username))
        await state.finish()
        
        tracks_count = get_tracks_count()
        await message.answer(f"Доступ разрешен! Всего отправлено треков: {tracks_count}", reply_markup=main_keyboard())
    else:
        cursor.execute("SELECT attempts FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            attempts = user[0] + 1
            if attempts >= 10:
                cursor.execute("UPDATE users SET is_banned = TRUE WHERE user_id = ?", (user_id,))
                await message.answer("Аккаунт заблокирован после 10 неудачных попыток.")
                await state.finish()
                return
            cursor.execute("UPDATE users SET attempts = ? WHERE user_id = ?", (attempts, user_id))
        else:
            cursor.execute("INSERT INTO users (user_id, school_name, attempts) VALUES (?, ?, ?)",
                          (user_id, school_name, attempts))
        await message.answer(f"Неверное название школы. Попытка {attempts}/10")
    
    conn.commit()
    conn.close()

@dp.message_handler(text="Главное меню")
async def main_menu(message: types.Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer("Админ-панель:", reply_markup=admin_keyboard())
    else:
        tracks_count = get_tracks_count()
        await message.answer(f"Главное меню. Всего отправлено треков: {tracks_count}", reply_markup=main_keyboard())

@dp.message_handler(text="Отправить песню")
async def submit_track(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user and user[0]:
        await message.answer("Ваш аккаунт заблокирован. Обратитесь в поддержку.")
    else:
        await message.answer("Выберите способ отправки:", reply_markup=track_options_keyboard())
    
    conn.close()

@dp.callback_query_handler(lambda c: c.data in ['link', 'title', 'file'])
async def process_track_option(callback_query: types.CallbackQuery, state: FSMContext):
    option = callback_query.data
    if option == 'link':
        await TrackSubmission.waiting_for_link.set()
        await bot.send_message(callback_query.from_user.id, "Отправьте ссылку на трек:")
    elif option == 'title':
        await TrackSubmission.waiting_for_title.set()
        await bot.send_message(callback_query.from_user.id, "Введите название трека и исполнителя:")
    elif option == 'file':
        await TrackSubmission.waiting_for_file.set()
        await bot.send_message(callback_query.from_user.id, "Загрузите файл в формате MP3/FLAC:")
    
    await callback_query.answer()

@dp.message_handler(state=TrackSubmission.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    link = message.text
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tracks (user_id, data, type) VALUES (?, ?, ?)", 
                  (user_id, link, 'link'))
    conn.commit()
    conn.close()
    
    await state.finish()
    await message.answer("Трек отправлен на модерацию!", reply_markup=main_keyboard())
    
    # Уведомление админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"Новый трек отправлен!\nОт: {message.from_user.full_name} (@{message.from_user.username})\nСсылка: {link}", 
                                 reply_markup=moderation_keyboard(cursor.lastrowid))
        except:
            pass

@dp.message_handler(state=TrackSubmission.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    title = message.text
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tracks (user_id, data, type) VALUES (?, ?, ?)", 
                  (user_id, title, 'title'))
    conn.commit()
    conn.close()
    
    await state.finish()
    await message.answer("Трек отправлен на модерацию!", reply_markup=main_keyboard())
    
    # Уведомление админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"Новый трек отправлен!\nОт: {message.from_user.full_name} (@{message.from_user.username})\nНазвание: {title}", 
                                 reply_markup=moderation_keyboard(cursor.lastrowid))
        except:
            pass

@dp.message_handler(content_types=['audio', 'document'], state=TrackSubmission.waiting_for_file)
async def process_file(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.audio:
        file_id = message.audio.file_id
    elif message.document:
        if message.document.mime_type not in ['audio/mpeg', 'audio/flac']:
            await message.answer("Пожалуйста, отправьте файл в формате MP3 или FLAC.")
            return
        file_id = message.document.file_id
    else:
        await message.answer("Пожалуйста, отправьте аудиофайл.")
        return
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tracks (user_id, data, type) VALUES (?, ?, ?)", 
                  (user_id, file_id, 'file'))
    conn.commit()
    conn.close()
    
    await state.finish()
    await message.answer("Трек отправлен на модерацию!", reply_markup=main_keyboard())
    
    # Уведомление админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"Новый трек отправлен!\nОт: {message.from_user.full_name} (@{message.from_user.username})")
            if message.audio:
                await bot.send_audio(admin_id, file_id, reply_markup=moderation_keyboard(cursor.lastrowid))
            else:
                await bot.send_document(admin_id, file_id, reply_markup=moderation_keyboard(cursor.lastrowid))
        except:
            pass

@dp.message_handler(text="Правила отправки")
async def show_rules(message: types.Message):
    rules = get_message('rules')
    await message.answer(rules)

@dp.message_handler(text="Информация о дискотеке")
async def show_disco_info(message: types.Message):
    disco_info = get_message('disco_info')
    await message.answer(disco_info)

@dp.message_handler(text="О боте")
async def show_about(message: types.Message):
    about = get_message('about_bot')
    await message.answer(about)

@dp.message_handler(text="Техподдержка")
async def support(message: types.Message):
    await SupportState.waiting_for_message.set()
    await message.answer("Опишите вашу проблему. Вы можете прикрепить скриншот.")

@dp.message_handler(state=SupportState.waiting_for_message, content_types=types.ContentType.ANY)
async def process_support_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    support_text = message.text or message.caption or "Без текста"
    attachment = None
    
    if message.photo:
        attachment = message.photo[-1].file_id
    elif message.document:
        attachment = message.document.file_id
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO support_requests (user_id, message, attachment) VALUES (?, ?, ?)", 
                  (user_id, support_text, attachment))
    conn.commit()
    conn.close()
    
    await state.finish()
    await message.answer("Ваше сообщение отправлено в поддержку!", reply_markup=main_keyboard())
    
    # Уведомление админам
    for admin_id in ADMIN_IDS:
        try:
            text = f"Новый запрос в поддержку!\nОт: {message.from_user.full_name} (@{message.from_user.username})\nID: {user_id}\n\n{support_text}"
            
            if attachment:
                if message.photo:
                    await bot.send_photo(admin_id, attachment, caption=text, reply_markup=support_keyboard(cursor.lastrowid))
                else:
                    await bot.send_document(admin_id, attachment, caption=text, reply_markup=support_keyboard(cursor.lastrowid))
            else:
                await bot.send_message(admin_id, text, reply_markup=support_keyboard(cursor.lastrowid))
        except:
            pass

# Админ-панель
@dp.message_handler(text="Модерация треков")
async def moderate_tracks(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks WHERE status = 'pending' ORDER BY created_at LIMIT 1")
    track = cursor.fetchone()
    conn.close()
    
    if not track:
        await message.answer("Нет треков для модерации.")
        return
    
    track_id, user_id, data, track_type, status, moderator_comment, priority, created_at = track
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, username FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    user_info = f"{user[0]} (@{user[1]})" if user else "Неизвестный пользователь"
    
    text = f"Трек для модерации:\nID: {track_id}\nОт: {user_info}\nТип: {track_type}\nДата: {created_at}\n\n"
    
    if track_type == 'link':
        text += f"Ссылка: {data}"
    elif track_type == 'title':
        text += f"Название: {data}"
    
    await message.answer(text, reply_markup=moderation_keyboard(track_id))

@dp.callback_query_handler(lambda c: c.data.startswith(('approve_', 'reject_', 'duplicate_')))
async def process_moderation(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ запрещен.")
        return
    
    action, track_id = callback_query.data.split('_')
    track_id = int(track_id)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    if action == 'approve':
        cursor.execute("UPDATE tracks SET status = 'approved' WHERE id = ?", (track_id,))
        await callback_query.answer("Трек одобрен.")
    elif action == 'reject':
        cursor.execute("UPDATE tracks SET status = 'rejected' WHERE id = ?", (track_id,))
        await callback_query.answer("Трек отклонен.")
    elif action == 'duplicate':
        cursor.execute("UPDATE tracks SET status = 'duplicate', priority = priority + 1 WHERE id = ?", (track_id,))
        await callback_query.answer("Трек отмечен как дубликат.")
    
    conn.commit()
    conn.close()
    
    # Удаляем сообщение с кнопками модерации
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    
    # Показываем следующий трек
    await moderate_tracks(callback_query.message)

@dp.message_handler(text="Запросы в техподдержку")
async def show_support_requests(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM support_requests WHERE status = 'open' ORDER BY created_at LIMIT 1")
    request = cursor.fetchone()
    conn.close()
    
    if not request:
        await message.answer("Нет открытых запросов в поддержку.")
        return
    
    request_id, user_id, request_message, attachment, status, created_at = request
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, username FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    user_info = f"{user[0]} (@{user[1]})" if user else "Неизвестный пользователь"
    
    text = f"Запрос в поддержку:\nID: {request_id}\nОт: {user_info}\nДата: {created_at}\n\n{request_message}"
    
    if attachment:
        try:
            await bot.send_document(message.from_user.id, attachment, caption=text, reply_markup=support_keyboard(request_id))
            return
        except:
            pass
    
    await message.answer(text, reply_markup=support_keyboard(request_id))

@dp.callback_query_handler(lambda c: c.data.startswith(('reply_', 'close_')))
async def process_support_request(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ запрещен.")
        return
    
    action, request_id = callback_query.data.split('_')
    request_id = int(request_id)
    
    if action == 'close':
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE support_requests SET status = 'closed' WHERE id = ?", (request_id,))
        conn.commit()
        conn.close()
        
        await callback_query.answer("Запрос закрыт.")
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        
        # Показываем следующий запрос
        await show_support_requests(callback_query.message)
    elif action == 'reply':
        # Здесь можно реализовать функционал ответа пользователю
        await callback_query.answer("Функция ответа пока не реализована.")

@dp.message_handler(text="Изменить админов")
async def change_admins(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    await message.answer("Управление администраторами:", reply_markup=admin_management_keyboard())

@dp.callback_query_handler(lambda c: c.data in ['add_admin', 'remove_admin'])
async def process_admin_management(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ запрещен.")
        return
    
    if callback_query.data == 'add_admin':
        await AdminState.adding_admin.set()
        await bot.send_message(callback_query.from_user.id, "Введите ID пользователя, которого хотите сделать администратором:")
    elif callback_query.data == 'remove_admin':
        await AdminState.removing_admin.set()
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username FROM admins")
        admins = cursor.fetchall()
        conn.close()
        
        if not admins:
            await bot.send_message(callback_query.from_user.id, "Нет администраторов для удаления.")
            return
        
        admin_list = "\n".join([f"{admin[0]} (@{admin[1]})" for admin in admins])
        await bot.send_message(callback_query.from_user.id, f"Текущие администраторы:\n{admin_list}\n\nВведите ID администратора, которого хотите удалить:")
    
    await callback_query.answer()

@dp.message_handler(state=AdminState.adding_admin)
async def process_add_admin(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO admins (user_id, username) VALUES (?, ?)", 
                      (new_admin_id, message.from_user.username))
        conn.commit()
        conn.close()
        
        await state.finish()
        await message.answer("Администратор добавлен!", reply_markup=admin_keyboard())
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID (число).")

@dp.message_handler(state=AdminState.removing_admin)
async def process_remove_admin(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE user_id = ?", (admin_id,))
        conn.commit()
        conn.close()
        
        await state.finish()
        await message.answer("Администратор удален!", reply_markup=admin_keyboard())
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID (число).")

@dp.message_handler(text="Изменить сообщения")
async def edit_messages(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    await message.answer("Выберите сообщение для редактирования:", reply_markup=message_edit_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('edit_'))
async def process_edit_message(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Доступ запрещен.")
        return
    
    message_type = callback_query.data.split('_')[1]
    
    if message_type == 'rules':
        key = 'rules'
        current = get_message('rules')
    elif message_type == 'disco':
        key = 'disco_info'
        current = get_message('disco_info')
    elif message_type == 'about':
        key = 'about_bot'
        current = get_message('about_bot')
    else:
        await callback_query.answer("Неизвестный тип сообщения.")
        return
    
    await AdminState.editing_message.set()
    await bot.send_message(callback_query.from_user.id, f"Текущее сообщение:\n{current}\n\nВведите новое сообщение:")
    
    # Сохраняем ключ в состоянии
    await dp.current_state().update_data(edit_key=key)
    await callback_query.answer()

@dp.message_handler(state=AdminState.editing_message)
async def process_message_edit(message: types.Message, state: FSMContext):
    new_text = message.text
    data = await state.get_data()
    key = data.get('edit_key')
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET value = ? WHERE key = ?", (new_text, key))
    conn.commit()
    conn.close()
    
    await state.finish()
    await message.answer("Сообщение обновлено!", reply_markup=admin_keyboard())

@dp.message_handler(text="Отмодерированные треки")
async def show_moderated_tracks(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracks WHERE status = 'approved' ORDER BY priority DESC, created_at")
    tracks = cursor.fetchall()
    conn.close()
    
    if not tracks:
        await message.answer("Нет отмодерированных треков.")
        return
    
    tracks_list = "\n\n".join([f"ID: {track[0]}\nТип: {track[3]}\nДанные: {track[2]}\nПриоритет: {track[6]}\nДата: {track[7]}" for track in tracks])
    
    # Разбиваем на части, если список слишком длинный
    if len(tracks_list) > 4000:
        parts = [tracks_list[i:i+4000] for i in range(0, len(tracks_list), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(f"Отмодерированные треки:\n\n{tracks_list}")

@dp.message_handler(text="Логи")
async def export_logs(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    
    # Создаем Excel файл с логами
    wb = Workbook()
    
    # Лист с пользователями
    ws_users = wb.active
    ws_users.title = "Пользователи"
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Данные пользователей
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    ws_users.append(["ID", "User ID", "School", "Attempts", "Banned", "Full Name", "Username"])
    for user in users:
        ws_users.append(user)
    
    # Лист с треками
    ws_tracks = wb.create_sheet("Треки")
    cursor.execute("SELECT * FROM tracks")
    tracks = cursor.fetchall()
    
    ws_tracks.append(["ID", "User ID", "Data", "Type", "Status", "Comment", "Priority", "Created At"])
    for track in tracks:
        ws_tracks.append(track)
    
    # Лист с поддержкой
    ws_support = wb.create_sheet("Поддержка")
    cursor.execute("SELECT * FROM support_requests")
    requests = cursor.fetchall()
    
    ws_support.append(["ID", "User ID", "Message", "Attachment", "Status", "Created At"])
    for request in requests:
        ws_support.append(request)
    
    conn.close()
    
    # Сохраняем файл
    filename = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    
    # Отправляем файл
    await message.answer_document(InputFile(filename), caption="Логи бота")
    
    # Удаляем временный файл
    os.remove(filename)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)