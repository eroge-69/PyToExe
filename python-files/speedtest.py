import requests
from bs4 import BeautifulSoup
import time

def measure_speed():
    # Инициируем тест скорости
    start_test_url = "https://2ip.ru/speedtest/"
    session = requests.Session()
    
    # Получаем уникальный ID теста
    response = session.get(start_test_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    test_id = soup.find('div', {'class': 'speedtest-process'})['data-test-id']
    
    # Запускаем тест
    start_url = f"https://2ip.ru/speedtest/start/?test_id={test_id}&_={int(time.time()*1000)}"
    session.get(start_url)
    
    # Ждем завершения теста (обычно 10-15 сек)
    print("Измерение скорости...")
    time.sleep(15)
    
    # Получаем результаты
    result_url = f"https://2ip.ru/speedtest/result/?test_id={test_id}&_={int(time.time()*1000)}"
    result = session.get(result_url).json()
    
    # Извлекаем данные
    download = result.get('download', {}).get('speed', {}).get('value', 0)
    upload = result.get('upload', {}).get('speed', {}).get('value', 0)
    ping = result.get('ping', {}).get('value', 0)
    
    # Конвертируем в Мбит/с
    download_mbps = round(download * 8 / 1024 / 1024, 2)
    upload_mbps = round(upload * 8 / 1024 / 1024, 2)
    
    return {
        "download": download_mbps,
        "upload": upload_mbps,
        "ping": ping
    }

if __name__ == "__main__":
    try:
        results = measure_speed()
        print("\nРезультаты теста скорости (2ip.ru):")
        print(f"Скачивание: {results['download']} Мбит/с")
        print(f"Загрузка:   {results['upload']} Мбит/с")
        print(f"Пинг:       {results['ping']} мс")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        print("Проверьте подключение к интернету или попробуйте позже")
input("\nНажмите Enter для выхода...")