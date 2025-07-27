import os
import sys
import time
import requests
import phonenumbers
import re
import json
from phonenumbers import carrier, timezone, geocoder
from datetime import datetime
import pytz
from colorama import init, Fore, Style
from bs4 import BeautifulSoup
from urllib.parse import quote

init(autoreset=True)

# Цветовая схема
RED = Fore.LIGHTRED_EX
WHITE = Fore.LIGHTWHITE_EX
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.YELLOW
CYAN = Fore.LIGHTCYAN_EX

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(RED + r"""
    ██████╗ ███████╗██╗   ██╗██╗██╗     ███╗   ███╗ █████╗ ██████╗ ███████╗
    ██╔══██╗██╔════╝██║   ██║██║██║     ████╗ ████║██╔══██╗██╔══██╗██╔════╝
    ██║  ██║█████╗  ██║   ██║██║██║     ██╔████╔██║███████║██████╔╝█████╗  
    ██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║     ██║╚██╔╝██║██╔══██║██╔══██╗██╔══╝  
    ██████╔╝███████╗ ╚████╔╝ ██║███████╗██║ ╚═╝ ██║██║  ██║██║  ██║███████╗
    ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
    """)
    print(RED + "    DevilMare OSINT Tool")
    print(WHITE + "    v1 | by @koqqs")
    print(RED + "="*80 + Style.RESET_ALL)

def print_menu():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Главное меню:")
    print(f"{RED}[{WHITE}1{RED}] {WHITE}Полный анализ ВК профиля")
    print(f"{RED}[{WHITE}2{RED}] {WHITE}Поиск людей в ВК")
    print(f"{RED}[{WHITE}3{RED}] {WHITE}Поиск по номеру телефона")
    print(f"{RED}[{WHITE}4{RED}] {WHITE}Поиск по никнейму (Google Dorks)")
    print(f"{RED}[{WHITE}5{RED}] {WHITE}Проверка утечек данных")
    print(f"{RED}[{WHITE}6{RED}] {WHITE}Анализ IP")
    print(f"{RED}[{WHITE}0{RED}] {WHITE}Выход")
    print(RED + "="*80)

# ==================== VK Functions ====================
def get_vk_id(input_str):
    """Определяем ID по разным форматам ввода"""
    if input_str.isdigit():
        return input_str
    
    if input_str.startswith(('http', 'vk.com', '@')):
        if input_str.startswith('@'):
            username = input_str[1:]
        else:
            match = re.search(r'vk.com/([^/?]+)', input_str)
            username = match.group(1) if match else input_str
        
        if username.startswith('id'):
            return username[2:]
        
        # Получаем ID через мобильную версию
        mobile_url = f"https://m.vk.com/{username}"
        try:
            response = requests.get(mobile_url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
            }, timeout=10)
            if 'error.php?err=404' not in response.url:
                match = re.search(r'data-owner-id="(\d+)"', response.text)
                if match:
                    return match.group(1)
        except:
            pass
    return None

def get_vk_info(user_id):
    """Получаем полную информацию о профиле ВК"""
    result = {'id': user_id}
    
    # 1. Мобильная версия (основная информация)
    try:
        mobile_url = f"https://m.vk.com/id{user_id}"
        response = requests.get(mobile_url, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'
        }, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result['name'] = soup.find('h2', class_='op_header').get_text(strip=True) if soup.find('h2', class_='op_header') else None
        result['status'] = soup.find('div', class_='pp_status').get_text(strip=True) if soup.find('div', class_='pp_status') else None
        
        # Дополнительная информация
        info_items = soup.select('div.pi_item')
        for item in info_items:
            text = item.get_text(strip=True)
            if 'город' in text.lower():
                result['city'] = text.replace('Город', '').strip()
            elif 'родил' in text.lower():
                result['bdate'] = text.split(':')[1].strip()
    except Exception as e:
        result['mobile_error'] = str(e)
    
    # 2. Сервис vk.watch (статистика)
    try:
        watch_url = f"https://vk.watch/id{user_id}"
        response = requests.get(watch_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Подписчики
        subs = soup.find('div', string=re.compile('подписчиков'))
        if subs:
            result['followers'] = subs.get_text(strip=True)
        
        # Статистика
        stats = soup.select('div.stats div.item')
        for item in stats:
            key = item.find('div', class_='label').get_text(strip=True)
            value = item.find('div', class_='count').get_text(strip=True)
            result[key.lower()] = value
    except Exception as e:
        result['watch_error'] = str(e)
    
    # 3. Сервис vk.barkov.net (фото)
    try:
        barkov_url = f"https://vk.barkov.net/id{user_id}"
        response = requests.get(barkov_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        photos = [img['src'] for img in soup.select('div.photo-item img')[:3]]
        if photos:
            result['photos_sample'] = photos
    except:
        pass
    
    return result

def search_vk_people(name, city=None):
    """Поиск людей по имени и городу"""
    try:
        base_url = "https://vk.com/people"
        params = {'q': name}
        if city:
            params['city'] = city
        
        url = f"{base_url}/{quote(params['q'])}"
        if city:
            url += f"/city{quote(params['city'])}"
        
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'
        }, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for person in soup.select('div.peoples_item'):
            link = person.find('a', class_='search_item')['href']
            user_id = link.split('/')[-1]
            name = person.find('div', class_='search_item_name').get_text(strip=True)
            info = person.find('div', class_='search_item_info').get_text(strip=True)
            
            results.append({
                'id': user_id,
                'name': name,
                'info': info,
                'link': f"https://vk.com{link}"
            })
        
        return results
    except Exception as e:
        return {'error': str(e)}

def vk_analyze():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Анализ ВК профиля")
    print(f"{YELLOW}[!] Введите: ID (цифры), username (durov), или ссылку (vk.com/durov)")
    user_input = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите данные: ").strip()
    
    user_id = get_vk_id(user_input)
    if not user_id:
        print(f"{RED}[!] Не удалось определить ID пользователя")
        return
    
    print(f"{GREEN}[+] Получаем информацию для ID: {user_id}")
    info = get_vk_info(user_id)
    
    if not info:
        print(f"{RED}[!] Не удалось получить данные")
        return
    
    print(f"\n{WHITE}[+] Основная информация:")
    print(f"• ID: {info.get('id', 'N/A')}")
    print(f"• Имя: {info.get('name', 'N/A')}")
    print(f"• Статус: {info.get('status', 'N/A')}")
    print(f"• Город: {info.get('city', 'N/A')}")
    print(f"• Дата рождения: {info.get('bdate', 'N/A')}")
    
    if 'followers' in info:
        print(f"\n{WHITE}[+] Статистика:")
        print(f"• Подписчики: {info['followers']}")
    
    if 'photos_sample' in info:
        print(f"\n{WHITE}[+] Фотографии (первые 3):")
        for i, photo in enumerate(info['photos_sample'], 1):
            print(f"{i}. {photo}")
    
    print(f"\n{YELLOW}[!] Полная ссылка: https://vk.com/id{user_id}")

def vk_search_people():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Поиск людей в ВК")
    name = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите имя и фамилию: ").strip()
    city = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите город (необязательно): ").strip()
    
    print(f"{GREEN}[+] Ищем людей...")
    results = search_vk_people(name, city if city else None)
    
    if 'error' in results:
        print(f"{RED}[!] Ошибка: {results['error']}")
        return
    
    if not results:
        print(f"{RED}[!] Ничего не найдено")
        return
    
    print(f"\n{WHITE}[+] Найдено {len(results)} человек:")
    for i, person in enumerate(results[:5], 1):  # Показываем первые 5 результатов
        print(f"\n{CYAN}{i}. {person['name']}")
        print(f"{WHITE}• Инфо: {person.get('info', 'N/A')}")
        print(f"• Ссылка: {person['link']}")

# ==================== Other Functions ====================
def phone_search():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Поиск по номеру телефона")
    print(f"{YELLOW}[!] Введите номер в формате: +7XXXXXXXXXX (Россия) или +380XXXXXXXXX (Украина)")
    phone = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите номер: ")
    
    try:
        print(f"{GREEN}[+] Анализируем номер...")
        parsed = phonenumbers.parse(phone)
        
        print(f"\n{WHITE}[+] Основная информация:")
        print(f"• Полный номер: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"• Страна: {geocoder.description_for_number(parsed, 'ru')} (код: {parsed.country_code})")
        print(f"• Оператор: {carrier.name_for_number(parsed, 'ru')}")
        
        print(f"\n{WHITE}[+] Проверка:")
        print(f"• Валидный номер: {'Да' if phonenumbers.is_valid_number(parsed) else 'Нет'}")
        
        tz = timezone.time_zones_for_number(parsed)
        if tz:
            print(f"• Часовой пояс: {tz[0]}")
        
        print(f"\n{WHITE}[+] Поиск в сервисах:")
        print(f"1. VK: https://vk.com/people/{phone}")
        print(f"2. WhatsApp: https://wa.me/{phone}")
        print(f"3. Telegram: https://t.me/{phone[1:]}")
        print(f"4. Avito: https://www.avito.ru/items/phone/{phone[1:]}")
        
    except Exception as e:
        print(f"{RED}[!] Ошибка: {str(e)}")

def username_search():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Поиск по никнейму")
    print(f"{YELLOW}[!] Введите никнейм (например: john_doe)")
    username = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите никнейм: ")
    
    try:
        print(f"{GREEN}[+] Генерируем ссылки для поиска...")
        
        dorks = {
            "Все соцсети": f'intext:"{username}"',
            "VK": f'site:vk.com "{username}"',
            "Instagram": f'site:instagram.com "{username}"',
            "Twitter/X": f'site:twitter.com "{username}" OR site:x.com "{username}"',
            "Facebook": f'site:facebook.com "{username}"',
            "GitHub": f'site:github.com "{username}"'
        }
        
        print(f"\n{WHITE}[+] Google Dorks (скопируйте в браузер):")
        for service, dork in dorks.items():
            url = f"https://www.google.com/search?q={dork.replace(' ', '+')}"
            print(f"{WHITE}• {service}: {url}")
        
    except Exception as e:
        print(f"{RED}[!] Ошибка: {str(e)}")

def leak_check():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Проверка утечек данных")
    print(f"{YELLOW}[!] Введите email/номер/логин (например: example@mail.com)")
    data = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите данные: ")
    
    try:
        print(f"{GREEN}[+] Проверяем утечки...")
        
        print(f"\n{WHITE}[+] Основные сервисы:")
        print(f"1. Have I Been Pwned: https://haveibeenpwned.com/unifiedsearch/{data}")
        print(f"2. LeakCheck: https://leakcheck.io/search?query={data}")
        
        print(f"\n{WHITE}[+] Дополнительные проверки:")
        print(f"• Pastebin: https://www.google.com/search?q=site:pastebin.com+{data}")
        print(f"• GitHub: https://github.com/search?q={data}")
        
    except Exception as e:
        print(f"{RED}[!] Ошибка: {str(e)}")

def ip_analyze():
    print(f"\n{RED}[{WHITE}+{RED}] {WHITE}Анализ IP")
    print(f"{YELLOW}[!] Введите IP-адрес (например: 8.8.8.8)")
    ip = input(f"{RED}[{WHITE}?{RED}] {WHITE}Введите IP: ")
    
    try:
        print(f"{GREEN}[+] Получаем данные...")
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        data = response.json()
        
        if data['status'] == 'success':
            print(f"\n{WHITE}[+] Геоданные:")
            print(f"• IP: {data.get('query', 'N/A')}")
            print(f"• Страна: {data.get('country', 'N/A')}")
            print(f"• Город: {data.get('city', 'N/A')}")
            print(f"• Провайдер: {data.get('isp', 'N/A')}")
            print(f"• Координаты: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
            
            print(f"\n{WHITE}[+] Карты:")
            print(f"• Google Maps: https://maps.google.com/?q={data['lat']},{data['lon']}")
        else:
            print(f"{RED}[!] Ошибка: {data.get('message', 'Неизвестная ошибка')}")
        
    except Exception as e:
        print(f"{RED}[!] Ошибка: {str(e)}")

# ==================== Main ====================
def main():
    print_banner()
    while True:
        print_menu()
        choice = input(f"\n{RED}[{WHITE}?{RED}] {WHITE}Выберите опцию: ")
        
        if choice == "1":
            vk_analyze()
        elif choice == "2":
            vk_search_people()
        elif choice == "3":
            phone_search()
        elif choice == "4":
            username_search()
        elif choice == "5":
            leak_check()
        elif choice == "6":
            ip_analyze()
        elif choice == "0":
            print(f"\n{RED}[!] Выход...")
            time.sleep(1)
            sys.exit()
        else:
            print(f"{RED}[!] Неверный выбор")
            
        input(f"\n{RED}[{WHITE}?{RED}] {WHITE}Нажмите Enter чтобы продолжить...")
        print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Прервано")
        sys.exit()	