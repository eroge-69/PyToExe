import os
import time
import requests

# 🛠️ Настройка
hosts = [
    "8.8.8.8",
    "1.1.1.1",
    "192.168.0.1"
]

TELEGRAM_TOKEN = "ВАШ_ТОКЕН"
TELEGRAM_CHAT_ID = "ВАШ_CHAT_ID"

def ping(host):
    param = "-n" if os.name == "nt" else "-c"
    command = f"ping {param} 1 {host}"
    return os.system(command) == 0

def send_alert(host):
    msg = f"❌ Потеря связи с {host}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

status = {host: True for host in hosts}

while True:
    print("\n🔄 Проверка связи...")
    for host in hosts:
        alive = ping(host)
        if alive:
            print(f"✅ {host} доступен")
        else:
            if status[host]:
                print(f"❌ {host} — СВЯЗЬ ПРОПАЛА!")
                send_alert(host)
        status[host] = alive
    time.sleep(5)