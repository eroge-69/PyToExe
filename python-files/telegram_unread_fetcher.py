import os
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.errors import UserPrivacyRestrictedError

def get_api_credentials(txt_file):
    try:
        with open(txt_file, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                return int(lines[0].strip()), lines[1].strip()
    except Exception as e:
        print(f"[Ошибка] Не удалось прочитать {txt_file}: {e}")
    return None, None

def format_message(session_name, entity_name, sender_id, phone, message, date):
    date_str = date.strftime('%Y-%m-%d %H:%M')
    phone_str = f"+{phone}" if phone else "unknown"
    return f"[{date_str}] [{session_name}] [{entity_name}] {sender_id} (phone: {phone_str}): {message}"

def fetch_unread_messages(session_name, api_id, api_hash):
    messages = []
    try:
        with TelegramClient(session_name, api_id, api_hash) as client:
            for dialog in client.iter_dialogs():
                entity = dialog.entity
                entity_name = getattr(entity, 'title', getattr(entity, 'username', 'Unknown'))

                if dialog.unread_count > 0:
                    for msg in client.iter_messages(entity, limit=dialog.unread_count):
                        if msg and not msg.out and msg.text and isinstance(msg.peer_id, (PeerUser, PeerChat, PeerChannel)):
                            try:
                                sender = client.get_entity(msg.sender_id)
                                phone = getattr(sender, 'phone', None)
                            except UserPrivacyRestrictedError:
                                phone = None
                            except Exception:
                                phone = None

                            formatted = format_message(
                                session_name,
                                entity_name,
                                msg.sender_id,
                                phone,
                                msg.text.replace('\n', ' '),
                                msg.date
                            )
                            messages.append(formatted)
    except Exception as e:
        print(f"[Ошибка] Сессия {session_name}: {e}")
    return messages

def main():
    result_file = "unread_messages.txt"
    all_messages = []

    for file in os.listdir():
        if file.endswith(".session"):
            base_name = file[:-8]
            txt_file = f"{base_name}.txt"

            if os.path.exists(txt_file):
                api_id, api_hash = get_api_credentials(txt_file)
                if api_id and api_hash:
                    print(f"[✓] Обработка сессии: {base_name}")
                    messages = fetch_unread_messages(base_name, api_id, api_hash)
                    all_messages.extend(messages)
                else:
                    print(f"[!] Неверные данные в {txt_file}")
            else:
                print(f"[!] Файл {txt_file} не найден")

    all_messages.sort()

    with open(result_file, "w", encoding="utf-8") as f:
        for msg in all_messages:
            f.write(msg + "\n")

    print(f"\nГотово! Найдено {len(all_messages)} сообщений.\nСохранено в {result_file}")

if __name__ == "__main__":
    main()
