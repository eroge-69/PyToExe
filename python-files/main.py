from colorama import Fore, Style
import os
import pystyle
from pystyle import Colorate, Colors
from pystyle import *
from colorama import Fore, init
import subprocess
import subprocess
import os
from colorama import init, Fore
from colorama import init, Fore, Style
import urllib
import json
import requests
import os
from colorama import init, Fore
import subprocess
from colorama import init, Fore, Style
import smtplib
import subprocess
from colorama import Fore, Style
from colorama import Fore
from pystyle import Colors, Colorate, Center, Box
import os
import datetime
import pystyle
from pystyle import *
import os
from colorama import init, Fore
from colorama import Fore, Style
from pystyle import Colorate, Colors
import subprocess

def base():
    init(autoreset=True)
    if not os.path.exists('databases'):
        print(f"системе неудается найти папку 'databases' ")
    else:
        count = len(os.listdir('databases'))
        print(f'имеется {count} базы.\n')
        data = input(f'введите информацию для поиска: ')
        print('\nпоиск начат\n')

        result = ''
        for label in os.listdir('databases'):
            file_path = os.path.join('databases', label)
            try:
                with open(file_path, 'r', encoding='UTF-8') as f:
                    for line in f:
                        if data in line:
                            result += f"[{label}] - {line}".replace('.', '').replace('[', '').replace(']', '').replace('"',
                                                                                                                   '').replace(
                            'NULL', '')
                            break
            except Exception as e:
                print(f"...")

        print(Fore.BLUE +'Поиск окончен!')
        if result:
            print(Fore.BLUE + '\nвот что мы нашли: \n')
            pystyle.Write.Print((result), pystyle.Colors.green_to_cyan, interval = 0.00000000001)
        else:
            print(Fore.BLUE + "ничего не найдено.")

def ip():
    getIP = input("\n[+] Введите IP адрес: ")
    url = "https://ipinfo.io/" + getIP + "/json"
    try:
        getInfo = urllib.request.urlopen(url)
    except:
        print('Ничего не найдено')
        f = input("нажмите enter... ': " + Style.RESET_ALL)
        if f == "":
            subprocess.run(["python", "main.py"])

    infoList = json.load(getInfo)
    def whoisIPinfo(ip):
        try:
            myComand = "whois " + getIP
            whoisInfo = os.popen(myComand).read()
            return whoisInfo
        except:
            return "Wrong"                          
    print("Айпи адрес: ", infoList["ip"])
    print("Город: ", infoList["city"])
    print("Регион: ", infoList["region"])
    print("Страна: ", infoList["country"])
    print("Часовой пояс: ", infoList["timezone"])
    print("Координаты города: ", infoList["loc"])
    f = input("нажмите enter... ': " + Style.RESET_ALL)
    if f == "":
        subprocess.run(["python", "main.py"])


def username():
    def check_website(url):
        response = requests.get(url)
        if response.status_code == 200:
            print(f"{url}")

    username = input("Введите никнейм: ")

    sites = [
        f"https://vk.com/{username}",
        f"https://github.com/{username}",
        f"https://t.me/{username}",
        f"https://www.tiktok.com/@{username}",
        f"https://github.com/{username}",
        f"https://www.youtube.com/{username}",
    ]

    for site in sites:
        check_website(site)
    return

def mega_ddos1():
    subprocess.run(['python', 'mega_ddos1.py'])
def mega_ddos2():
    subprocess.run(['python', 'mega_ddos2.py'])
def GOOSE_FREE():
    subprocess.run(['python', 'GOOSE_FREE.py'])

COLOR_CODE = {
    "RESET": "\033[0m",  
    "UNDERLINE": "\033[04m", 
    "GREEN": "\033[32m",     
    "YELLOW": "\033[93m",    
    "RED": "\033[31m",       
    "CYAN": "\033[36m",     
    "BOLD": "\033[01m",        
    "PINK": "\033[95m",
    "URL_L": "\033[36m",       
    "LI_G": "\033[92m",      
    "F_CL": "\033[0m",
    "DARK": "\033[90m",
    "WHITE": "\033[90m",
    "BLACK": "\033[90m",         
}

banner = '''


 ╭───────────────────────────────────────────────────────────────────────────────────────────────────╮  
 │   :::::::::::      ::::::::: ::::::::::: :::::::::   ::::::::  :::::::::      :::      ::::::::   │ 
 │       :+:          :+:    :+:    :+:     :+:    :+: :+:    :+: :+:    :+:   :+: :+:   :+:    :+:  │  
 │       +:+          +:+    +:+    +:+     +:+    +:+ +:+    +:+ +:+    +:+  +:+   +:+  +:+         │  
 │       +#+          +#++:++#+     +#+     +#+    +:+ +#+    +:+ +#++:++#:  +#++:++#++: +#++:++#++  │ 
 │       +#+          +#+           +#+     +#+    +#+ +#+    +#+ +#+    +#+ +#+     +#+        +#+  │ 
 │       #+#          #+#           #+#     #+#    #+# #+#    #+# #+#    #+# #+#     #+# #+#    #+#  │ 
 │   ###########      ###       ########### #########   ########  ###    ### ###     ###  ########   │  
 ╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
            ╭────────────────────────────────────────────────────────────────────────────╮                                              
            │   автор @q1tbertqutebov │ СОФТ ФРИ НЕ ПОКУПАЙ У ЕБЛАНОВ! канал @QUTEBteam  │         
      ╭────────────────────────╮     ╭────────────────────────╮     ╭────────────────────────╮
      │  1 • ПОИСК ПО НОМЕРУ   │     │  4 • ПОИСК ПО ПОЧТЕ    │     │  7 • ПОИСК ПО САЙТУ    │
      │  2 • ПОИСК ПО IP       │     │  5 • ПОИСК ПО ФИО      │     │  8 • ПОИСК ПО ИМЕНИ    │
      │  3 • ПОИСК ПО НИКУ     │     │  6 • ПОИСК ПО КАРТКЕ   │     │  9 • ПОИСК ПО ДС       │    
      ╰────────────────────────╯     ╰────────────────────────╯     ╰────────────────────────╯
      ╭────────────────────────╮     ╭────────────────────────╮     ╭────────────────────────╮
      │ 10 • ПОИСК ПО ТГ ЮЗУ   │     │ 13 • ПОИСК ПО БД       │     │ 16 • ПОИСК ПО ИНН      │
      │ 11 • ПОИСК ПО ТГ АЙДИ  │     │ 14 • ПОИСК ПО ШКОЛАМ   │     │ 17 • ПОИСК ПО СНИЛСУ   │
      │ 12 • ПОИСК ПО ПИДОРУ   │     │ 15 • ПОИСК ПО ВК       │     │ 18 • ПОИСК ПО ФССП     │    
      ╰────────────────────────╯     ╰────────────────────────╯     ╰────────────────────────╯
                     │  19 • О СОФТЕ ПИДОРАСА   │ │  20 • ВыЙТИ НАХУЙ        │ 
                     ╰──────────────────────────╯ ╰──────────────────────────╯ 
                            │ 2025 • МОИ ПОЗДРАВЛЕНИЕ С НОВЫМ ГОДОМ │
                            ╰───────────────────────────────────────╯


'''
print(Colorate.Vertical(Colors.white_to_green, Center.XCenter(banner)))
select = input(f'{COLOR_CODE["GREEN"]}[+]{COLOR_CODE["GREEN"]} Выбери хуйню какую нибудь-> {COLOR_CODE["WHITE"]}')


if select == '1':
   base()

elif select == '2':
   ip()

elif select == '3':
   username()

elif select == '4':
   base()

elif select == '5':
   base()

elif select == '6':
   ip()

elif select == '7':
   username()

elif select == '8':
   base()

elif select == '9':
   base()

elif select == '10':
   base()

elif select == '11':
   base()

elif select == '12':
   base()

elif select == '13':
   base()

elif select == '14':
   base()

elif select == '15':
   base()

elif select == '16':
   base()

elif select == '17':
   base()

elif select == '18':
   base()

elif select == '19':
    print("""

создатель софта: Китберт Кутебов

мой тг: @q1tbertqutebov

мой тгк: @QUTEBteam

ссылка на тгк: https://t.me/QUTEBteam

присоединяйся, сливаем много софтов, также пишем свои.

я не несу ответственности за ваши действия, софт создан исключительно в образовательных целях.


""")                                
    f = input("Нажмите enter': " + Style.RESET_ALL)
    if f == "":
        subprocess.run(["python", "main.py"])

elif select == '20':
    print("""

ну и иди нахуй.

""")    

elif select == '2025':
    print("""

крч пупсы мои любимые

желаю вам на новый год здоровье а также счастье

надеюсь у в 2025 будем все хорошо!

удачи епта! сабку на @QUTEBteam

""")                                
    f = input("Нажмите enter': " + Style.RESET_ALL)
    if f == "":
        subprocess.run(["python", "main.py"])

