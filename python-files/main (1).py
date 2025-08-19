
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import xml.etree.ElementTree as ET
import re

# Конфигурация устройства
DEVICE_IP = "10.80.220.44"
USERNAME = "admin"
PASSWORD = "SuperPass2024"
BASE_URL = f"http://{DEVICE_IP}/ISAPI/System/time"

def get_current_time():
    """Получить текущее время с устройства"""
    try:
        response = requests.get(
            BASE_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=3
        )
        response.raise_for_status()
        
        # Парсим XML ответ
        root = ET.fromstring(response.content)
        ns = {'ns': 'http://www.hikvision.com/ver20/XMLSchema'}
        local_time = root.find('.//ns:localTime', ns).text
        time_zone = root.find('.//ns:timeZone', ns).text
        
        # Извлекаем понятное время
        match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', local_time)
        if match:
            return f"{match.group(0)} (Часовой пояс: {time_zone})"
        return local_time
    except Exception as e:
        return f"Ошибка: {str(e)}"

def sync_time():
    """Синхронизировать время через NTP"""
    ntp_config = """
    <Time version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
        <timeMode>NTP</timeMode>
        <timeZone>CST-3:00:00</timeZone>
        <ntpServer>
            <enabled>true</enabled>
            <host>pool.ntp.org</host>
            <port>123</port>
            <interval>60</interval>
        </ntpServer>
    </Time>
    """
    
    try:
        # Устанавливаем NTP конфигурацию
        response = requests.put(
            BASE_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            data=ntp_config,
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        response.raise_for_status()
        
        # Запускаем немедленную синхронизацию
        sync_resp = requests.put(
            f"http://{DEVICE_IP}/ISAPI/System/time/ntpSyncNow",
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=5
        )
        sync_resp.raise_for_status()
        
        return True
    except Exception as e:
        print(f"Ошибка синхронизации: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("Текущее время на устройстве:", get_current_time())
    
    print("\nИнициируем синхронизацию времени...")
    if sync_time():
        print("Синхронизация успешно запущена!")
        
        # Ждем 3 секунды для обновления времени
        print("\nОжидаем обновления времени...")
        import time
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("Обновленное время на устройстве:", get_current_time())
    else:
        print("Не удалось выполнить синхронизацию")

if __name__ == "__main__":
    main()