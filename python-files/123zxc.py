import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import logging
from urllib.parse import urlparse
import asyncio
from datetime import datetime, timezone, timedelta
import os
import sys
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

# Настройки
logging.basicConfig(level=logging.INFO)
TOKEN = "7223686049:AAE9MnTRG6uYMkAbV6-Md-c5np4FlpdBxXk"
OWNER_ID = 2119130131

SCAM_CHANNEL = "https://t.me/jddidodox"

# Telethon настройки
API_ID = 25018678
API_HASH = '932d4bf3dbc93dfb50e76d59530bc612'

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

telethon_client = TelegramClient('wtn_antiscam', API_ID, API_HASH)
MOSCOW_TZ = timezone(timedelta(hours=3))

# Вероятности скама
SCAM_PROBABILITY = {
    "owner": 0,
    "admin": 1,
    "garant": 1,
    "trainee": 23,
    "default": 50
}

# Клавиатура (только для личных сообщений)
def get_main_keyboard(is_private: bool):
    if not is_private:
        return None
        
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛡️ Список гарантов"),
                KeyboardButton(text="👤 Мой профиль")
            ],
            [
                KeyboardButton(text="🔍 Проверить пользователя"),
                KeyboardButton(text="⚠️ Слить скамера")
            ]
        ],
        resize_keyboard=True
    )

def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_PATH = get_app_path()
DB_FILE = os.path.join(APP_PATH, "scam_db.json")

async def get_user_id_by_username(username):
    try:
        if username.startswith('@'):
            username = username[1:]
        
        async with telethon_client:
            user = await telethon_client(GetFullUserRequest(username))
            return user.users[0].id
    except Exception as e:
        logging.error(f"Error getting user ID: {e}")
        return None

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def load_db():
    try:
        if not os.path.exists(DB_FILE):
            default_db = {
                "users": {},
                "guarantors": [],
                "admins": [OWNER_ID],
                "trainees": []
            }
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(default_db, f, ensure_ascii=False, indent=4)
            return default_db
        
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            # Конвертация старого формата
            if "trainees" not in db:
                db["trainees"] = []
            return db
    except Exception as e:
        logging.error(f"Error loading database: {e}")
        default_db = {
            "users": {},
            "guarantors": [],
            "admins": [OWNER_ID],
            "trainees": []
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=4)
        return default_db

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Error saving database: {e}")

def is_owner(user_id: int):
    return user_id == OWNER_ID

def is_admin(user_id: int):
    db = load_db()
    return str(user_id) in db["admins"]

def is_garantor(user_id: int):
    db = load_db()
    return str(user_id) in db["guarantors"]

def is_trainee(user_id: int):
    db = load_db()
    return str(user_id) in db["trainees"]

def get_scam_probability(user_id: int):
    if is_owner(user_id):
        return SCAM_PROBABILITY["owner"]
    elif is_admin(user_id):
        return SCAM_PROBABILITY["admin"]
    elif is_garantor(user_id):
        return SCAM_PROBABILITY["garant"]
    elif is_trainee(user_id):
        return SCAM_PROBABILITY["trainee"]
    else:
        return SCAM_PROBABILITY["default"]

def add_new_user(user_id: str):
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "checks": 0,
            "scams": []
        }
        save_db(db)
    return db["users"][user_id]

# ========== TEXT COMMANDS HANDLERS ==========

@dp.message(F.text.lower().startswith("чек "))
async def check_text_handler(message: Message):
    """Обработчик текстовой команды 'чек'"""
    target = message.text.split(maxsplit=1)[1].strip()
    await check_user(message, target)

@dp.message(F.text.lower() == "чек ми")
@dp.message(F.text.lower() == "чекми")
@dp.message(F.text.lower() == "ми")
async def me_text_handler(message: Message):
    """Обработчик текстовых вариантов команды /me"""
    await my_stats(message)

@dp.message(F.text.lower() == "гаранты")
async def garants_text_handler(message: Message):
    """Обработчик текстовой команды 'гаранты'"""
    await list_guarantors(message)

@dp.message(F.text.lower() == "админы")
async def admins_text_handler(message: Message):
    """Обработчик текстовой команды 'админы'"""
    await list_admins(message)

@dp.message(F.text.lower().startswith("чек "))
async def check_text_handler(message: Message):
    """Обработчик текстовой команды 'чек'"""
    target = message.text.split(maxsplit=1)[1].strip()
    await check_user(message, target)

# ========== BASIC COMMANDS ==========

@dp.message(Command("start"))
async def start(message: Message):
    add_new_user(str(message.from_user.id))
    await message.answer(
        "🔐 <b>WTN | AntiScamBase</b> - система проверки пользователей\n\n"
        "📌 <b>Основные функции:</b>\n"
        "▫️ Проверка пользователей по ID/юзернейму\n"
        "▫️ База данных скамеров с доказательствами\n\n"
        "⚙️ <b>Используйте кнопки ниже или команды:</b>\n"
        "▫️ /me - ваш профиль\n"
        "▫️ /check [ID/@юзернейм] - проверить пользователя\n"
        "▫️ /garants - список гарантов",
        reply_markup=get_main_keyboard(message.chat.type == "private"),
        disable_web_page_preview=True
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    if not (is_admin(message.from_user.id) or is_owner(message.from_user.id)):
        await message.answer("❌ Эта команда доступна только администраторам", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    help_text = """
<b>⚙️ Доступные команды:</b>

<b>👑 Владелец:</b>
<code>/add_admin ID</code> - Добавить администратора
<code>/remove_admin ID</code> - Удалить администратора
<code>/admins</code> - Список администраторов
<code>/add_garant ID</code> - Добавить гаранта
<code>/remove_garant ID</code> - Удалить гаранта
<code>/add_trainee ID</code> - Добавить стажера
<code>/remove_trainee ID</code> - Удалить стажера

<b>🛡️ Администратор:</b>
<code>/add ID Причина Доказательства</code> - Добавить скамера
<code>/remove ID Номер_скама</code> - Удалить запись о скаме
<code>/garants</code> - Список гарантов

<b>👤 Все пользователи:</b>
<code>/start</code> - Начать работу с ботом
<code>/me</code> - Мой профиль
<code>/check ID</code> - Проверить пользователя
<code>/garants</code> - Список гарантов
"""
    await message.answer(help_text, 
                       reply_markup=get_main_keyboard(message.chat.type == "private"))

# ========== PROFILE COMMANDS ==========

@dp.message(F.text == "👤 Мой профиль")
@dp.message(Command("me"))
async def my_stats(message: Message):
    try:
        user_id = str(message.from_user.id)
        db = load_db()
        
        # Добавляем пользователя если его нет
        if user_id not in db["users"]:
            add_new_user(user_id)
            db = load_db()
        
        user = db["users"][user_id]
        
        # Определяем статус
        if is_owner(int(user_id)):
            status_icon = "👑"
            status_text = "Владелец бота"
            scam_prob = SCAM_PROBABILITY["owner"]
        elif is_admin(int(user_id)):
            status_icon = "🛡️"
            status_text = "Администратор"
            scam_prob = SCAM_PROBABILITY["admin"]
        elif is_garantor(int(user_id)):
            status_icon = "🛡️"
            status_text = "Гарант"
            scam_prob = SCAM_PROBABILITY["garant"]
        elif is_trainee(int(user_id)):
            status_icon = "🔵"
            status_text = "Стажер"
            scam_prob = SCAM_PROBABILITY["trainee"]
        elif not user["scams"]:
            status_icon = "🟢"
            status_text = "Нейтрален"
            scam_prob = SCAM_PROBABILITY["default"]
        else:
            status_icon = "🔴"
            status_text = f"Скамер ({len(user['scams'])} случаев)"
            scam_prob = 100

        profile_message = (
            "╔═══════════════════════\n"
            f"║ [👤] <b>Профиль пользователя:</b>\n"
            "╠═══════════════════════\n"
            f"║\n"
            f"║ ┌ <b>ID:</b> <code>{user_id}</code>\n"
            f"║ ├\n"
            f"║ ├ <b>Проверок:</b> {user['checks']}\n"
            f"║ ├\n"
            f"║ ├ <b>Статус:</b> [{status_icon}] {status_text}\n"
            f"║ └ <b>Вероятность скама:</b> {scam_prob}%\n"
            f"║\n"
            "╠══════════════════════════════════\n"
            "║ Для безопасного проведения сделок\n"
            "║ всегда используйте гарантов WTN.\n"
            "╠══════════════════════════════════\n"
            f"║ Проверено: @WTN_antiscambot\n"
            "╚══════════════════════════════════"
        )

        scam_info = ""
        for i, scam in enumerate(user["scams"], 1):
            scam_info += (
                f"\n\n<b>⚠️ Скам #{i}</b>\n"
                f"├ <b>Причина:</b> {scam['reason']}\n"
                f"├ <b>Дата:</b> {scam['date']}\n"
                f"└ <b>Доказательства:</b> <a href='{scam['proof']}'>ссылка</a>"
            )

        reply_markup = None
        if message.chat.type == "private":
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Открыть профиль", url=f"tg://user?id={user_id}")]
            ])

        await message.answer(
            profile_message + scam_info,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

    except Exception as e:
        logging.error(f"Error in my_stats: {e}")
        error_msg = "❌ Произошла ошибка при получении профиля"
        if message.chat.type == "private":
            await message.answer(error_msg, reply_markup=get_main_keyboard(True))
        else:
            await message.answer(error_msg)

# ========== CHECK USER ==========

async def check_user(message: Message, target: str):
    db = load_db()
    
    if target.startswith('@'):
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    elif not target.isdigit():
        await message.answer("❌ Укажите ID (число) или @юзернейм", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    if target not in db["users"]:
        db["users"][target] = {
            "checks": 0,
            "scams": []
        }
    
    db["users"][target]["checks"] += 1
    save_db(db)
    
    user = db["users"][target]
    
    # Определяем статус и вероятность скама
    if is_owner(int(target)):
        status_icon = "👑"
        status_text = "Владелец бота"
        scam_prob = SCAM_PROBABILITY["owner"]
    elif is_admin(int(target)):
        status_icon = "🛡️"
        status_text = "Администратор"
        scam_prob = SCAM_PROBABILITY["admin"]
    elif is_garantor(int(target)):
        status_icon = "🛡️"
        status_text = "Гарант"
        scam_prob = SCAM_PROBABILITY["garant"]
    elif is_trainee(int(target)):
        status_icon = "🔵"
        status_text = "Стажер"
        scam_prob = SCAM_PROBABILITY["trainee"]
    elif not user["scams"]:
        status_icon = "🟢"
        status_text = "Нейтрален"
        scam_prob = SCAM_PROBABILITY["default"]
    else:
        status_icon = "🔴"
        status_text = f"Скамер ({len(user['scams'])} случаев)"
        scam_prob = 100

    result_message = (
        "╔═══════════════════════\n"
        f"║ [🔍] <b>Результат проверки:</b>\n"
        "╠═══════════════════════\n"
        f"║\n"
        f"║ ┌ <b>ID:</b> <code>{target}</code>\n"
        f"║ ├\n"
        f"║ ├ <b>Проверок:</b> {user['checks']}\n"
        f"║ ├\n"
        f"║ ├ <b>Статус:</b> [{status_icon}] {status_text}\n"
        f"║ └ <b>Вероятность скама:</b> {scam_prob}%\n"
        f"║\n"
        "╠══════════════════════════════════\n"
        "║ Для безопасного проведения сделок\n"
        "║ всегда используйте гарантов WTN.\n"
        "╠══════════════════════════════════\n"
        f"║ Проверено: @WTN_antiscambot\n"
        "╚══════════════════════════════════"
    )

    scam_info = ""
    for i, scam in enumerate(user["scams"], 1):
        scam_info += (
            f"\n\n<b>⚠️ Скам #{i}</b>\n"
            f"├ <b>Причина:</b> {scam['reason']}\n"
            f"├ <b>Дата:</b> {scam['date']}\n"
            f"└ <b>Доказательства:</b> <a href='{scam['proof']}'>ссылка</a>"
        )

    profile_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Перейти к профилю", url=f"tg://user?id={target}")]
    ])

    await message.answer(
        result_message + scam_info,
        reply_markup=profile_button,
        disable_web_page_preview=True
    )

@dp.message(Command("check"))
async def check_command_handler(message: Message):
    """Обработчик команды /check"""
    args = message.text.split()
    
    if len(args) < 2:
        # Если команда без параметров
        if message.chat.type == "private":
            await message.answer("📝 Введите ID или @юзернейм пользователя после команды /check\n"
                               "Пример: <code>/check 123456</code> или <code>/check @username</code>",
                               reply_markup=get_main_keyboard(True))
        else:
            await message.answer("ℹ️ Используйте: /check [ID/@username]")
        return
    
    target = args[1]
    await check_user(message, target)

@dp.message(F.text == "🔍 Проверить пользователя")
async def check_button_handler(message: Message):
    """Обработчик кнопки проверки (только в ЛС)"""
    if message.chat.type != "private":
        return
        
    await message.answer("📝 Введите команду /check с ID или @юзернеймом\n"
                       "Пример: <code>/check 123456</code> или <code>/check @username</code>",
                       reply_markup=get_main_keyboard(True))

# ========== ADMIN LIST COMMAND ==========

@dp.message(Command("admins"))
async def list_admins(message: Message):
    try:
        db = load_db()
        
        # Собираем информацию о всех категориях пользователей
        categories = {
            "👑 Владелец": [OWNER_ID],
            "🛡️ Администраторы": db.get("admins", []),
            "🛡️ Гаранты": db.get("guarantors", []),
            "🔵 Стажеры": db.get("trainees", [])
        }
        
        # Получаем информацию о пользователях
        text_lines = []
        button_lines = []
        
        for category, user_ids in categories.items():
            if not user_ids:
                continue
                
            category_users = []
            for user_id in user_ids:
                try:
                    async with telethon_client:
                        user = await telethon_client.get_entity(int(user_id))
                        name = user.first_name
                        if user.username:
                            name = f"@{user.username}"
                        elif user.last_name:
                            name = f"{user.first_name} {user.last_name}"
                        # Добавляем emoji в зависимости от категории
                        emoji = category.split()[0]
                        button_text = f"{emoji} {name}"
                except Exception as e:
                    logging.error(f"Error getting user info: {e}")
                    name = f"ID: {user_id}"
                    button_text = f"👤 {name}"
                
                category_users.append(f"▫️ {name}")
                button_lines.append((user_id, button_text))
            
            text_lines.append(f"\n<b>{category}:</b>\n" + "\n".join(category_users))
        
        if not text_lines:
            await message.answer("ℹ️ В системе нет администраторов", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        
        # Создаем интерактивные кнопки с именами
        keyboard = []
        row = []
        for user_id, button_text in button_lines:
            row.append(InlineKeyboardButton(
                text=button_text,
                url=f"tg://user?id={user_id}"
            ))
            # Размещаем по 2 кнопки в ряд
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:  # Добавляем оставшиеся кнопки
            keyboard.append(row)
        
        admins_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "👑 <b>Список администрации WTN</b>\n" + 
            "\n".join(text_lines) +
            "\n\nНажмите на имя для перехода в профиль",
            reply_markup=admins_markup,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logging.error(f"Error in list_admins: {e}")
        error_msg = "❌ Произошла ошибка при получении списка"
        if message.chat.type == "private":
            await message.answer(error_msg, reply_markup=get_main_keyboard(True))
        else:
            await message.answer(error_msg)

@dp.message(Command("add_admin"))
async def add_admin(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только для владельца!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "❌ Формат: <code>/add_admin ID/@юзернейм</code>\n\n"
            "Пример:\n"
            "<code>/add_admin 123456</code>\n"
            "<code>/add_admin @username</code>",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    db = load_db()
    if target in db["admins"]:
        await message.answer("ℹ️ Этот пользователь уже админ", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    db["admins"].append(target)
    save_db(db)
    
    await message.answer(
        f"✅ Пользователь <code>{target}</code> добавлен в список админов",
        reply_markup=get_main_keyboard(message.chat.type == "private")
    )

@dp.message(Command("remove_admin"))
async def remove_admin(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только для владельца!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "❌ Формат: <code>/remove_admin ID/@юзернейм</code>\n\n"
            "Пример:\n"
            "<code>/remove_admin 123456</code>\n"
            "<code>/remove_admin @username</code>",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    db = load_db()
    if target not in db["admins"]:
        await message.answer("ℹ️ Этот пользователь не является админом", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    db["admins"].remove(target)
    save_db(db)
    
    await message.answer(
        f"✅ Пользователь <code>{target}</code> удален из списка админов",
        reply_markup=get_main_keyboard(message.chat.type == "private")
    )

# ========== GARANT MANAGEMENT COMMANDS ==========

@dp.message(Command("add_garant"))
async def add_garant(message: Message):
    try:
        # Проверка прав доступа (только для владельца)
        if not is_owner(message.from_user.id):
            await message.answer("❌ Эта команда доступна только владельцу бота",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return

        # Разбираем аргументы команды
        args = message.text.split()
        if len(args) < 2:
            await message.answer(
                "❌ Неверный формат команды. Используйте:\n"
                "<code>/add_garant ID_пользователя</code>\n"
                "или\n"
                "<code>/add_garant @username</code>",
                reply_markup=get_main_keyboard(message.chat.type == "private"))
            return

        target = args[1].strip("@")
        
        # Преобразуем юзернейм в ID при необходимости
        if not target.isdigit():
            await message.answer("🔄 Определяю ID пользователя...",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            try:
                user_id = await get_user_id_by_username(target)
                if not user_id:
                    await message.answer("❌ Пользователь не найден",
                                       reply_markup=get_main_keyboard(message.chat.type == "private"))
                    return
                target = str(user_id)
            except Exception as e:
                logging.error(f"Error resolving username: {e}")
                await message.answer("❌ Ошибка при определении ID пользователя",
                                   reply_markup=get_main_keyboard(message.chat.type == "private"))
                return

        db = load_db()
        
        # Проверяем, не является ли пользователь уже гарантом
        if target in db["guarantors"]:
            await message.answer("ℹ️ Этот пользователь уже является гарантом",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
            
        # Проверяем, существует ли пользователь в базе
        if target not in db["users"]:
            db["users"][target] = {"checks": 0, "scams": []}

        # Добавляем в список гарантов
        db["guarantors"].append(target)
        save_db(db)

        # Получаем имя пользователя для сообщения
        try:
            async with telethon_client:
                user = await telethon_client.get_entity(int(target))
                name = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name if user.last_name else ''}"
        except:
            name = f"ID {target}"

        await message.answer(
            f"✅ Пользователь <b>{name}</b> (<code>{target}</code>) успешно добавлен в список гарантов",
            reply_markup=get_main_keyboard(message.chat.type == "private"))
            
    except Exception as e:
        logging.error(f"Error in add_garant: {e}")
        await message.answer("❌ Произошла ошибка при добавлении гаранта",
                           reply_markup=get_main_keyboard(message.chat.type == "private"))

@dp.message(Command("remove_garant"))
async def remove_garant(message: Message):
    try:
        # Проверка прав доступа (только для владельца)
        if not is_owner(message.from_user.id):
            await message.answer("❌ Эта команда доступна только владельцу бота",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return

        # Разбираем аргументы команды
        args = message.text.split()
        if len(args) < 2:
            await message.answer(
                "❌ Неверный формат команды. Используйте:\n"
                "<code>/remove_garant ID_пользователя</code>\n"
                "или\n"
                "<code>/remove_garant @username</code>",
                reply_markup=get_main_keyboard(message.chat.type == "private"))
            return

        target = args[1].strip("@")
        
        # Преобразуем юзернейм в ID при необходимости
        if not target.isdigit():
            await message.answer("🔄 Определяю ID пользователя...",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            try:
                user_id = await get_user_id_by_username(target)
                if not user_id:
                    await message.answer("❌ Пользователь не найден",
                                       reply_markup=get_main_keyboard(message.chat.type == "private"))
                    return
                target = str(user_id)
            except Exception as e:
                logging.error(f"Error resolving username: {e}")
                await message.answer("❌ Ошибка при определении ID пользователя",
                                   reply_markup=get_main_keyboard(message.chat.type == "private"))
                return

        db = load_db()
        
        # Проверяем, является ли пользователь гарантом
        if target not in db["guarantors"]:
            await message.answer("ℹ️ Этот пользователь не является гарантом",
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return

        # Удаляем из списка гарантов
        db["guarantors"].remove(target)
        save_db(db)

        # Получаем имя пользователя для сообщения
        try:
            async with telethon_client:
                user = await telethon_client.get_entity(int(target))
                name = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name if user.last_name else ''}"
        except:
            name = f"ID {target}"

        await message.answer(
            f"✅ Пользователь <b>{name}</b> (<code>{target}</code>) удален из списка гарантов",
            reply_markup=get_main_keyboard(message.chat.type == "private"))
            
    except Exception as e:
        logging.error(f"Error in remove_garant: {e}")
        await message.answer("❌ Произошла ошибка при удалении гаранта",
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        
# ========== GARANTS COMMANDS ==========

async def get_garants_list():
    """Получаем список гарантов с именами"""
    db = load_db()
    garants_list = []
    
    for user_id in db.get("guarantors", []):
        try:
            async with telethon_client:
                user = await telethon_client.get_entity(int(user_id))
                name = user.first_name
                if user.username:
                    name = f"@{user.username}"
                elif user.last_name:
                    name = f"{user.first_name} {user.last_name}"
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            name = f"ID: {user_id}"
        
        garants_list.append((user_id, name))
    
    return garants_list

@dp.message(F.text == "🛡️ Список гарантов")
@dp.message(Command("garants"))
async def list_guarantors(message: Message):
    try:
        garants = await get_garants_list()
        
        if not garants:
            await message.answer("ℹ️ Список гарантов пуст", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        
        # Создаем интерактивные кнопки
        keyboard = []
        for user_id, name in garants:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🛡️ {name}",
                    url=f"tg://user?id={user_id}"
                )
            ])
        
        # Добавляем кнопку обновления только в ЛС
        if message.chat.type == "private":
            keyboard.append([
                InlineKeyboardButton(
                    text="🔄 Обновить список",
                    callback_data="refresh_garants"
                )
            ])
        
        garants_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer(
            "🛡️ <b>Список гарантов WTN</b>\n\n"
            "Нажмите на имя гаранта, чтобы перейти в профиль:",
            reply_markup=garants_markup
        )
    except Exception as e:
        logging.error(f"Error in list_guarantors: {e}")
        await message.answer("❌ Произошла ошибка при получении списка гарантов",
                           reply_markup=get_main_keyboard(message.chat.type == "private"))

@dp.callback_query(F.data == "refresh_garants")
async def refresh_garants(callback: types.CallbackQuery):
    try:
        await callback.answer("Обновляем список...")
        garants = await get_garants_list()
        
        if not garants:
            await callback.message.edit_text("ℹ️ Список гарантов пуст")
            return
        
        keyboard = []
        for user_id, name in garants:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🛡️ {name}",
                    url=f"tg://user?id={user_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                text="🔄 Обновить список",
                callback_data="refresh_garants"
            )
        ])
        
        garants_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.edit_text(
            "🛡️ <b>Список гарантов WTN</b>\n\n"
            "Нажмите на имя гаранта, чтобы перейти в профиль:",
            reply_markup=garants_markup
        )
    except Exception as e:
        logging.error(f"Error refreshing garants list: {e}")
        await callback.answer("Ошибка при обновлении", show_alert=True)

# ========== TRAINEE MANAGEMENT ==========

@dp.message(Command("add_trainee"))
async def add_trainee(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только для владельца!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "❌ Формат: <code>/add_trainee ID/@юзернейм</code>\n\n"
            "Пример:\n"
            "<code>/add_trainee 123456</code>\n"
            "<code>/add_trainee @username</code>",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    db = load_db()
    if target in db["trainees"]:
        await message.answer("ℹ️ Этот пользователь уже стажер", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    db["trainees"].append(target)
    save_db(db)
    
    await message.answer(
        f"✅ Пользователь <code>{target}</code> добавлен в список стажеров",
        reply_markup=get_main_keyboard(message.chat.type == "private")
    )

@dp.message(Command("remove_trainee"))
async def remove_trainee(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Только для владельца!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "❌ Формат: <code>/remove_trainee ID/@юзернейм</code>\n\n"
            "Пример:\n"
            "<code>/remove_trainee 123456</code>\n"
            "<code>/remove_trainee @username</code>",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    db = load_db()
    if target not in db["trainees"]:
        await message.answer("ℹ️ Этот пользователь не является стажером", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    db["trainees"].remove(target)
    save_db(db)
    
    await message.answer(
        f"✅ Пользователь <code>{target}</code> удален из списка стажеров",
        reply_markup=get_main_keyboard(message.chat.type == "private")
    )

# ========== SCAM MANAGEMENT ==========

@dp.message(F.text == "⚠️ Слить скамера")
async def report_scammer(message: Message):
    if message.chat.type != "private":
        return
    
    await message.answer(
        f"⚠️ <b>Для добавления скамера в базу:</b>\n"
        f"1. Перейдите в наш канал: {SCAM_CHANNEL}\n"
        f"2. Опубликуйте доказательства\n"
        f"3. Ожидайте проверки модераторами\n\n"
        f"<i>Либо используйте команду /add (только для админов)</i>",
        reply_markup=get_main_keyboard(message.chat.type == "private"),
        disable_web_page_preview=True
    )

@dp.message(Command("add"))
async def add_scammer(message: Message):
    if message.chat.type != "private":
        return
        
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только для админов!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer(
            "❌ Формат: <code>/add ID/@юзернейм Причина Ссылка_на_доказательства</code>\n\n"
            "Пример:\n"
            "<code>/add 123456 Обман на продаже https://example.com/proof</code>",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    reason = args[2]
    proof = args[3]
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    if not is_valid_url(proof):
        await message.answer("❌ Укажите валидную ссылку (например: <code>https://example.com/proof</code>)", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    db = load_db()
    if target not in db["users"]:
        db["users"][target] = {
            "checks": 0,
            "scams": []
        }
    
    new_scam = {
        "reason": reason,
        "proof": proof,
        "date": datetime.now(MOSCOW_TZ).strftime("%d.%m.%Y %H:%M (МСК)")
    }
    
    db["users"][target]["scams"].append(new_scam)
    save_db(db)
    
    scam_count = len(db["users"][target]["scams"])
    await message.answer(
        f"✅ <b>{target}</b> добавлен в базу скамеров!\n"
        f"▫️ Всего скамов: <b>{scam_count}</b>\n"
        f"▫️ Причина: <b>{reason}</b>\n"
        f"▫️ Дата: <b>{new_scam['date']}</b>\n"
        f"▫️ Доказательства: <a href='{proof}'>ссылка</a>",
        reply_markup=get_main_keyboard(message.chat.type == "private"),
        disable_web_page_preview=True
    )

@dp.message(Command("remove"))
async def remove_scammer(message: Message):
    if message.chat.type != "private":
        return
        
    if not is_admin(message.from_user.id):
        await message.answer("❌ Только для админов!", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "❌ Формат: <code>/remove ID/@юзернейм Номер_скама</code>\n\n"
            "Пример:\n"
            "<code>/remove 123456 1</code> - удалит первый скам у пользователя 123456\n"
            "<code>/remove @username all</code> - удалит все скамы у пользователя",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    target = args[1].strip("@")
    scam_num = args[2].lower()
    
    if not target.isdigit():
        await message.answer("🔄 Получаю ID пользователя...")
        user_id = await get_user_id_by_username(target)
        if not user_id:
            await message.answer("❌ Пользователь не найден", 
                               reply_markup=get_main_keyboard(message.chat.type == "private"))
            return
        target = str(user_id)
    
    db = load_db()
    if target not in db["users"]:
        await message.answer("ℹ️ Пользователь не найден в базе", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    if not db["users"][target]["scams"]:
        await message.answer("ℹ️ У пользователя нет записей о скамах", 
                           reply_markup=get_main_keyboard(message.chat.type == "private"))
        return
    
    if scam_num == "all":
        db["users"][target]["scams"] = []
        save_db(db)
        await message.answer(
            f"✅ Все скамы пользователя <code>{target}</code> удалены",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    try:
        scam_num = int(scam_num)
        if scam_num < 1 or scam_num > len(db["users"][target]["scams"]):
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Укажите корректный номер скама (число) или 'all'",
            reply_markup=get_main_keyboard(message.chat.type == "private")
        )
        return
    
    removed_scam = db["users"][target]["scams"].pop(scam_num - 1)
    save_db(db)
    
    await message.answer(
        f"✅ Скам #{scam_num} удален у пользователя <code>{target}</code>\n"
        f"▫️ Причина: <b>{removed_scam['reason']}</b>\n"
        f"▫️ Дата: <b>{removed_scam['date']}</b>\n"
        f"▫️ Были доказательства: <a href='{removed_scam['proof']}'>ссылка</a>",
        reply_markup=get_main_keyboard(message.chat.type == "private"),
        disable_web_page_preview=True
    )

# ========== BOT STARTUP ==========

async def main():
    await telethon_client.start()
    logging.info("Telethon client started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        load_db()
        logging.info(f"Создана новая база данных: {DB_FILE}")
    
    logging.info("Бот запускается...")
    asyncio.run(main())