import os
import asyncio
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel

# 🔐 Замените на свои значения от my.telegram.org
api_id = 123456  # <-- сюда ваш API ID
api_hash = 'your_api_hash_here'  # <-- сюда ваш API HASH

# 📂 Папка со сессиями (текущая)
session_folder = '.'

# 📄 Файл для записи результатов
output_file = 'unread_chats.txt'

async def check_sessions():
    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')]
    result_lines = []

    for session in session_files:
        session_name = os.path.splitext(session)[0]
        print(f"🔄 Проверка сессии: {session_name}")

        client = TelegramClient(session_name, api_id, api_hash)
        try:
            await client.start()
            me = await client.get_me()
            print(f"✅ Успешный вход: {me.first_name} ({me.phone})")

            dialogs = await client.get_dialogs()

            for dialog in dialogs:
                if dialog.unread_count > 0:
                    entity = dialog.entity
                    name = entity.title if hasattr(entity, 'title') else (entity.first_name or '')
                    if isinstance(entity, User):
                        phone = entity.phone or 'номер не найден'
                        result_lines.append(f"[{session_name}] Личка: {name} | Тел: {phone}")
                    elif isinstance(entity, Chat):
                        result_lines.append(f"[{session_name}] Группа: {name}")
                    elif isinstance(entity, Channel):
                        result_lines.append(f"[{session_name}] Канал: {name}")

        except Exception as e:
            print(f"❌ Ошибка в {session_name}: {e}")
        finally:
            await client.disconnect()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_lines))

    print(f"\n📄 Готово! Результаты записаны в {output_file}")

if __name__ == '__main__':
    asyncio.run(check_sessions())
