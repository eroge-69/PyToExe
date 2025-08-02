import json
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import MessageEntityType
from aiogram.utils import executor

# Токен бота (замените на свой или используйте переменную окружения)
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8493914531:AAFBWbiFVit4J-nj8vTruXaFV8l73BgC42Q')
USERS_FILE = 'users.json'

bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)

# === УТИЛИТА ЭКРАНИРОВАНИЯ ===

def escape_markdown(text: str) -> str:
    # Экранирование специальных символов MarkdownV2
    return re.sub(r'([_*[$]()>~`#+\-=|{}.!])', r'\\\1', text)

# === ХРАНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ===

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def register_user(user_id, username):
    users = load_users()
    users[str(user_id)] = {
        "username": username or "",
        "enabled": True
    }
    save_users(users)

def find_user_by_username(username):
    users = load_users()
    for user_id_str, data in users.items():
        if data.get("username", "").lower() == username.lower():
            return int(user_id_str)
    return None

# === /START команда ===

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    register_user(message.from_user.id, message.from_user.username)
    await message.reply(f"✅ Вы подписаны на упоминания, {escape_markdown(message.from_user.first_name)}\\!")
    print(f"[START] @{message.from_user.username} ({message.from_user.id})")

# === Обработчик для автоматического ответа в ЛС ===

@dp.message_handler(lambda message: message.chat.type == 'private', content_types=types.ContentType.TEXT)
async def reply_in_dm(message: types.Message):
    await message.answer(
        "Привет! Управление региональной информационной политики *не сможет прочитать ваше сообщение*.\n"
        "Правила работы в чате РЕДАКЦИИ — [здесь](https://t.me/c/2671747194/537/1299?single).\n\n"
        "Остались вопросы? Напишите в ветку ВОПРОСЫ.\n"
        "Готова отработка медийного ТЗ или ответ на запрос? Тогда в ОТРАБОТКА ВСЕХ ЗАДАЧ.\n\n"
        "Спасибо! 🙌",
        parse_mode="Markdown"
    )

# === Обработка упоминаний в группах ===

@dp.message_handler(content_types=types.ContentType.TEXT)
async def mention_handler(message: types.Message):
    if message.chat.type not in ['group', 'supergroup']:
        return

    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.MENTION:
                # Получение никнейма без '@'
                username = message.text[entity.offset + 1: entity.offset + entity.length]
                user_id = find_user_by_username(username)

                if user_id:
                    try:
                        chat_id_clean = str(message.chat.id).replace("-100", "")
                        message_link = f"https://t.me/c/{chat_id_clean}/{message.message_id}"

                        await bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"📣 *Вас упомянули в чате* {escape_markdown('«' + message.chat.title + '»')}\n"
                                f"[Открыть сообщение]({message_link})\n\n"
                                f"{escape_markdown(message.text)}"
                            ),
                            parse_mode="MarkdownV2",
                            disable_web_page_preview=True
                        )
                        print(f"[INFO] Упоминание @{username} → {user_id}")
                    except Exception as e:
                        print(f"⚠️ Ошибка отправки @{username} → {e}")
                else:
                    print(f"[WARN] Не найден пользователь @{username}")

# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот запущен и ожидает команд...")
    executor.start_polling(dp, skip_updates=True)