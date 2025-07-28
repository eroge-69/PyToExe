import requests
import time
from threading import Thread
import sys
import random
from datetime import datetime

class PhoneLookupTool:
    API_URL = "https://chaos-api.lol/check"
    API_TOKENS = [
        "31349d8b-ff7d-4827-939e-22cc01f066ef",
        "5906edee-4abd-45d5-ada6-7df022766223"
    ]
    
    # Цвета
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }

    def __init__(self):
        self.current_token_index = 0
        self.stop_animation = False
        self.spinner_chars = '|/—\\'
        self.spinner_pos = 0

    def display_banner(self):       
        banner = f"""
        {self.colorize('red', '▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄')}
        {self.colorize('red', '		CHAOS SEARCH')}
        {self.colorize('red', '▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀')}
        
        {self.colorize('yellow', 'Версия: 1.0')}
        {self.colorize('yellow', 'Дата: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        {self.colorize('blue', 'Используется Chaos API')}"""
       
        print(banner)

    def colorize(self, color, text):
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def spinner(self):
        char = self.spinner_chars[self.spinner_pos]
        self.spinner_pos = (self.spinner_pos + 1) % len(self.spinner_chars)
        return char

    def show_progress(self):
        while not self.stop_animation:
            sys.stdout.write(f"\r{self.colorize('yellow', '┗ Поиск информации ' + self.spinner())}")
            sys.stdout.flush()
            time.sleep(0.1)

    def make_request(self, phone_number):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            params = {
                'number': phone_number,
                'token': self.API_TOKENS[self.current_token_index]
            }
            
            response = requests.get(
                self.API_URL,
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 403:
                self.rotate_token()
                return self.make_request(phone_number)
                
            return response.json() if response.status_code == 200 else None
            
        except requests.exceptions.RequestException:
            return None

    def rotate_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.API_TOKENS)
        print(self.colorize('yellow', f"\n⌧ Переключение на токен #{self.current_token_index + 1}"))

    def lookup_phone(self, phone_number):
        self.stop_animation = False
        progress_thread = Thread(target=self.show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        try:
            result = self.make_request(phone_number)
            return result
        finally:
            self.stop_animation = True
            time.sleep(0.2)
            print('\r' + ' '*50 + '\r', end='')

    def display_results(self, data):
        if not data:
            print(self.colorize('red', "\n⌧ Информация по данному номеру не найдена"))
            return
            
        print(self.colorize('green', f"\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓"))
        print(self.colorize('green', f"┃ ▣ Номер: {data.get('number', 'не указан')}"))
        print(self.colorize('green', f"┃ ▣ Найдено записей: {data.get('found', 0)}"))
        print(self.colorize('green', f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"))
        
        for db_index, database in enumerate(data.get('results', []), 1):
            print(self.colorize('blue', f"▦ База данных #{db_index}: {database.get('database', 'неизвестный источник')}"))
            
            for entry in database.get('data', []):
                print(self.colorize('yellow', f"  ├─ {entry}"))
            
            if db_index < len(data.get('results', [])):
                print(self.colorize('red', "  ┊"))

    def run(self):
        self.display_banner()
        
        while True:
            try:
                phone = input(self.colorize('green', "\n┗ Введите номер телефона (или 'q' для выхода): "))
                
                if phone.lower() == 'q':
                    print(self.colorize('red', "\n⌧ Выход из программы..."))
                    break
                    
                if not phone.isdigit():
                    print(self.colorize('red', "\n⌧ Ошибка: номер должен содержать только цифры"))
                    continue
                    
                result = self.lookup_phone(phone)
                self.display_results(result)
                
            except KeyboardInterrupt:
                print(self.colorize('red', "\n⌧ Прервано пользователем"))
                break

if __name__ == "__main__":
    tool = PhoneLookupTool()
    tool.run()