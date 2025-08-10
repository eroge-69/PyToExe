import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
import time
import random
import os

# Функция для загрузки прокси из файла
def load_proxies(filepath='proxy.txt'):
    proxies = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    proxies.append(line)
        print(f"Загружено {len(proxies)} прокси.")
    else:
        print("Файл proxy.txt не найден, работа без прокси.")
    return proxies

# Функция для получения случайного прокси
def get_random_proxy(proxies):
    if not proxies:
        return None
    proxy = random.choice(proxies)
    ip, port, username, password = proxy.split(':')
    return {
        'http': f'http://{username}:{password}@{ip}:{port}',
        'https': f'https://{username}:{password}@{ip}:{port}'
    }

# Функция для поиска email на сайте
def find_email(url, session, proxies):
    try:
        proxy = get_random_proxy(proxies) if proxies else None
        response = session.get(url, proxies=proxy, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        emails = list(set(emails))  # Удаляем дубликаты
        return emails[0] if emails else "Email не найден"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# Основная функция парсинга
def parse_hotels(city):
    proxies = load_proxies()
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    output_file = f'hotels_output_{city}.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Результаты парсинга отелей в городе {city}\n\n")
    
    query = f"{city} hotels"
    hotel_count = 0
    max_hotels = 10  # Ограничение для примера

    for url in search(query, num_results=50):
        if hotel_count >= max_hotels:
            break
        
        try:
            proxy = get_random_proxy(proxies) if proxies else None
            response = session.get(url, proxies=proxy, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.text if soup.title else "Без названия"
            
            print(f"Обработка: {title} ({url})")
            email = find_email(url, session, proxies)
            
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"Отель: {title}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Email: {email}\n")
                f.write("-" * 50 + "\n")
            
            hotel_count += 1
            print(f"Обработана страница {hotel_count}")
            time.sleep(random.uniform(1, 3))  # Задержка для избежания блокировок
        
        except Exception as e:
            print(f"Ошибка обработки {url}: {str(e)}")
            continue
    
    print(f"Парсинг завершен. Результаты сохранены в {output_file}")

if __name__ == "__main__":
    city = input("Введите название города (например, Paris): ").strip()
    if city:
        parse_hotels(city)
    else:
        print("Название города не введено!")