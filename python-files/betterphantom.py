import asyncio
import json
import os
from telethon import TelegramClient
from telethon.tl.types import User

# 🔑 Твои данные
api_id = 29887802        # ← замени
api_hash = '266162f6d82817bbe4bd08f61065d120'
session_name = 'my_session'

# 🧾 Список отслеживаемых пользователей
# Можно username или ID как строки
watched_users = ['ria_ssss', 'linaki_ss', 'vienny1', 'yo0o0ohohoh', 'saaskek', 'Natouto_real']  # можно смешивать

# 📁 Файл для сохранения фото-ID
DATA_FILE = 'profile_photos.json'

# 📨 Кому слать уведомление (можно 'me' или username)
notify_recipient = 'FuckTheCensorship'
message_template = "🔄 Пользователь {name} сменил фотографию профиля!"


def load_saved_photos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_photos(photo_data):
    with open(DATA_FILE, 'w') as f:
        json.dump(photo_data, f)


async def get_photo_id(user: User):
    return getattr(user.photo, 'photo_id', None)


async def monitor_profiles():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    # Загрузка сохранённых фото
    saved_photos = load_saved_photos()
    updated = False

    # Получатель уведомлений
    recipient = await client.get_entity(notify_recipient)

    print("🚀 Мониторинг профилей запущен...")

    while True:
        for username in watched_users:
            try:
                user = await client.get_entity(username)
                user_id = str(user.id)
                new_photo_id = await get_photo_id(user)

                # Проверка на смену
                old_photo_id = saved_photos.get(user_id)

                if new_photo_id != old_photo_id:
                    if old_photo_id is not None:
                        # Фото изменилось!
                        msg = message_template.format(name=user.username or user.first_name)
                        await client.send_message(recipient, msg)
                        print(f"📸 {user.username or user.id} сменил фото — уведомление отправлено.")
                    else:
                        print(f"🆕 Добавлен пользователь {user.username or user.id} в отслеживание.")

                    # Сохраняем новое фото
                    saved_photos[user_id] = new_photo_id
                    updated = True
                else:
                    print(f"✅ {user.username or user.id}: фото не изменилось.")

            except Exception as e:
                print(f"❌ Ошибка при обработке {username}: {e}")

        # Обновим файл, если что-то поменялось
        if updated:
            save_photos(saved_photos)
            updated = False

        await asyncio.sleep(30)  # проверка каждые 30 секунд


if __name__ == '__main__':
    asyncio.run(monitor_profiles())