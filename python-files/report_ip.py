#!/usr/bin/env python3
# report_ip.py
# Скрипт берёт имя компа, LAN IP и время, и шлёт в телеграм-чат.

import socket
import datetime
import urllib.request
import urllib.parse

# Данные для бота
TOKEN = "bot366206628:AAGwzPPIh9VZP3n_fJ2IgyEPcRphWxjoPXw"
CHAT_ID = "261405852"

def get_local_ip():
    """Выцепить LAN IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # трюк: реального запроса не будет
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "неизвестен"

def get_hostname():
    return socket.gethostname()

def send_message(text):
    """Отправка текста в телеграм"""
    url = f"https://api.telegram.org/{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as r:
        r.read()  # ответ нам не особо нужен

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🖥️ Host: {get_hostname()}\n🌐 LAN IP: {get_local_ip()}\n⏰ {now}"
    send_message(msg)
