import requests
import json
import re
import threading
import queue
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import asyncio

# Глобальные переменные
task_queue = queue.Queue()
processed_lines = set()
unique_phone_numbers = set()
base_url = "https://moskva.mts.ru"
num_threads = 10

# Инициализация параметров
def init_params():
    global base_url, num_threads
    
    base_url = input("Введите базовый URL (например, https://moskva.mts.ru): ").strip()
    if not base_url:
        print("Ошибка: URL не введен. Используется значение по умолчанию: https://moskva.mts.ru")
        base_url = "https://moskva.mts.ru"

    try:
        num_threads = int(input("Введите количество потоков (по умолчанию 10): ") or 10)
        print(f"Будет использовано {num_threads} потоков")
    except ValueError:
        print("Ошибка: введено не число. Используется значение по умолчанию: 10")
        num_threads = 10

# Асинхронная функция запроса
async def async_make_request(session, key, proxy, number, thread_name, base_url, max_retries=2):
    url = f"https://onlinesales.mts.ru/MTS/api/ep/get-personal-offer-assortiment?key={key}&numberCount=10&mask=79*{number}*&slot=nomer&salabilityCategoryCode=N"
    
    headers = {
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Host": "onlinesales.mts.ru",
        "Origin": base_url,
        "Referer": base_url + "/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "accept": "application/json",
        "cabinet-key": "sim98087648-0000-0120-ou5-00000010000012",
        "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    proxy_url = f"http://{proxy}"
    
    for attempt in range(max_retries):
        try:
            async with session.get(url, headers=headers, proxy=proxy_url, timeout=5) as response:
                status_code = response.status
                
                if status_code == 200:
                    data = await response.json()
                    phone_numbers = [item['msisdn'] for item in data.get('freePhoneList', [])]
                    if phone_numbers:
                        print(f"{thread_name}- {status_code} {phone_numbers}")
                        return phone_numbers
                    else:
                        print(f"{thread_name}- {status_code} (нет номеров)")
                        return []
                elif status_code == 500 and attempt < max_retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    print(f"{thread_name}- {status_code}")
                    return []
                    
        except Exception as e:
            print(f"{thread_name}- Ошибка: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
                continue
            return []
    
    return []

# Асинхронный обработчик задач
async def async_process_line(line, numbers, thread_name):
    key_match = re.search(r'key=([^\&]+)', line)
    proxy_match = re.search(r'\| ([^\s]+)$', line)
    
    if key_match and proxy_match:
        key = key_match.group(1)
        proxy = proxy_match.group(1)
        
        connector = aiohttp.TCPConnector(force_close=True)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for number in numbers:
                tasks.append(async_make_request(session, key, proxy, number, thread_name, base_url))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            with open('phone_numbers.txt', 'a', encoding='utf-8') as f:
                for phone_numbers in results:
                    if isinstance(phone_numbers, list):
                        for num in phone_numbers:
                            f.write(f"{num}\n")

# Обертка для запуска асинхронного кода в потоке
def process_line(line, numbers, thread_name):
    asyncio.run(async_process_line(line, numbers, thread_name))

# Чтение номеров из файла
def load_numbers():
    try:
        with open('numbers.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Ошибка: файл numbers.txt не найден")
        sys.exit(1)

# Основной цикл
def main():
    init_params()
    numbers = load_numbers()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        try:
            while True:
                if os.path.exists('keys.txt'):
                    with open('keys.txt', 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f if line.strip() and line not in processed_lines]
                    
                    if lines:
                        for line in lines:
                            processed_lines.add(line)
                            executor.submit(process_line, line, numbers, f"Поток-{threading.get_ident()}")
                        
                        with open('keys.txt', 'w', encoding='utf-8') as f:
                            f.write('')
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем. Завершаем работу.")
            sys.exit(0)

if __name__ == "__main__":
    main()
