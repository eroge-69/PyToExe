import os
import re
import time
import json
import requests
from datetime import datetime
from platformdirs import user_documents_path

LOG_PATH = "sent_log.json"

# Автоматическое определение пути к папке Zoom
ZOOM_PATH = os.path.join(user_documents_path(), "Zoom")

CHAT_ID = "-4897594542"
BOT_TOKEN = "8126291058:AAGGddCgMjqGtpGvhZUgdKLwaDXFqJV3NkY"

# Загружаем лог отправленных файлов
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        sent_log = set(json.load(f))
else:
    sent_log = set()

def send_video(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    with open(file_path, "rb") as video:
        files = {"video": video}
        data = {
            "chat_id": CHAT_ID,
            "caption": caption,
            "supports_streaming": True
        }
        response = requests.post(url, files=files, data=data)
        if response.ok:
            print(f"✅ Отправлено: {os.path.basename(file_path)}")
        else:
            print(f"❌ Ошибка при отправке {os.path.basename(file_path)}: {response.text}")
        return response.ok

def extract_user_and_datetime_from_path(path):
    folder = os.path.basename(os.path.dirname(path))

    # Паттерн для поиска даты и времени (форматы с точками или двоеточиями в времени)
    dt_pattern = re.compile(r'(\d{4}[-/]\d{2}[-/]\d{2})[ ](\d{2}[.:]\d{2}[.:]\d{2})')
    match = dt_pattern.search(folder)

    if not match:
        print(f"⚠️ Не найден формат даты и времени в '{folder}'")
        return "Неизвестный пользователь", "Неизвестная дата"

    date_str = match.group(1).replace('/', '-')
    time_str = match.group(2).replace('.', ':')
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        date_formatted = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        date_formatted = "Неизвестная дата"

    # Всё, что идёт после даты и времени
    after_dt = folder[match.end():].strip()

    # Возможные варианты:
    # 1) "name's Zoom Meeting"
    # 2) "Zoom Meeting name"
    # Нужно убрать "Zoom Meeting" (в любом регистре и порядке) и "'s"

    # Убираем "'s"
    after_dt = after_dt.replace("'s", "").strip()

    # Ищем и удаляем "Zoom Meeting" (может быть в начале или в конце)
    zoom_meeting_pattern = re.compile(r'zoom meeting', re.IGNORECASE)
    parts = zoom_meeting_pattern.split(after_dt)

    # После разделения parts — остаются либо [имя], либо ['', имя]
    # Возьмём все части, соединяем и обрезаем пробелы
    user_name = " ".join(part.strip() for part in parts if part.strip())

    if not user_name:
        user_name = "Неизвестный пользователь"

    return user_name, date_formatted

def scan_and_send():
    for root, _, files in os.walk(ZOOM_PATH):
        for name in files:
            if name.endswith(".mp4"):
                full_path = os.path.join(root, name)
                if full_path not in sent_log:
                    user_name, date = extract_user_and_datetime_from_path(full_path)
                    caption = f"🎥 {user_name} · {date} · {name}"
                    print(f"📤 Отправка: {caption}")
                    if send_video(full_path, caption):
                        sent_log.add(full_path)
                        with open(LOG_PATH, "w", encoding="utf-8") as f:
                            json.dump(list(sent_log), f)

if __name__ == "__main__":
    print(f"📡 Агент запущен. Следит за: {ZOOM_PATH}")
    while True:
        scan_and_send()
        time.sleep(30)
