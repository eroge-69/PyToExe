import os
import sys
import time
import threading
import requests
import webbrowser
import base64
import subprocess
import platform
from colorama import Fore, init

init(autoreset=True)
os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def spinner(done_flag):
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while not done_flag[0]:
        print(f'\r{Fore.CYAN}{symbols[idx % len(symbols)]} Loading...', end='')
        idx += 1
        time.sleep(0.1)
    print('\r', end='')

def progress_bar(done_flag, duration=5):
    width = 40
    sys.stdout.write("[" + " " * width + "]")
    sys.stdout.flush()
    sys.stdout.write("\b" * (width + 1))
    for _ in range(width):
        if done_flag[0]:
            break
        time.sleep(duration / width)
        sys.stdout.write("-")
        sys.stdout.flush()
    sys.stdout.write("]\n")

def decrypt_key(encoded_key):
    return base64.b64decode(encoded_key.encode()).decode()

PHONE_API_KEY_ENC = "MDZiNmYyZDM1OTY3MjM5MjkyMTI1ZjJjYzlhNzZkMzU="
EMAIL_API_KEY_ENC = "YWIxNTNkY2Q0OWI1NTExYjVkYWI3YjE2YzdjMmE4YzA="
DNS_API_KEY = "fd2C3hFP53JrglsQFalzLg==p2qiqWdqaUVCNLno"

phone_api_key = decrypt_key(PHONE_API_KEY_ENC)
email_api_key = decrypt_key(EMAIL_API_KEY_ENC)

def ping_worker(command, ip):
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"{Fore.GREEN}Pinged IP = {ip} | {line.strip()}", flush=True)
        process.stdout.close()
        process.wait()
    except Exception as e:
        print(f"{Fore.RED}Ping error for {ip}: {e}")

def ping_ip(ip, threads=4):
    system = platform.system().lower()
    if system == 'windows':
        param_count = '-n'
        param_size = '-l'
        interval = []  # Windows ping doesn't support interval
        packet_size = '65500'
    else:
        param_count = '-c'
        param_size = '-s'
        interval = ['-i', '0.0000001']  # Faster interval
        packet_size = '65500'

    command = ['ping', param_count, '100000', param_size, packet_size] + interval + [ip]

    typewriter(f"\npinging {ip} with {threads} threads...\n")

    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=ping_worker, args=(command, ip))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

def print_menu(menu_num):
    os.system('cls' if os.name == 'nt' else 'clear')
    if menu_num == 1:
        content = f'''
{Fore.CYAN}██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░░█████╗░░█████╗░
{Fore.BLUE}██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔═══╝░██╔═══╝░██╔═══╝░
{Fore.MAGENTA}██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██████╗░██████╗░██████╗░
{Fore.RED}██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██╔══██╗██╔══██╗██╔══██╗
{Fore.YELLOW}██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝╚█████╔╝╚█████╔╝
{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░░╚════╝░░╚════╝░
{Fore.MAGENTA} Osint  0 MADE BY HANAKO 0

{Fore.CYAN} [0] Exit
{Fore.CYAN} [1] Enter Name Info    
{Fore.BLUE} [2] Enter Phone Number
{Fore.BLUE} [3] Enter Address Info  
{Fore.CYAN} [4] Enter IP Info
'''
    if menu_num == 2:
        content = f'''
{Fore.CYAN}██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░░█████╗░░█████╗░
{Fore.BLUE}██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔═══╝░██╔═══╝░██╔═══╝░
{Fore.MAGENTA}██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██████╗░██████╗░██████╗░
{Fore.RED}██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██╔══██╗██╔══██╗██╔══██╗
{Fore.YELLOW}██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝╚█████╔╝╚█████╔╝
{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░░╚════╝░░╚════╝░
{Fore.MAGENTA} Osint/Discord/Website Code  0 MADE BY HANAKO 0

{Fore.CYAN} [5] Enter Email Info
{Fore.CYAN} [6] DNS Lookup
{Fore.BLUE} [7] Ping IP
{Fore.BLUE} [8] See website code
{Fore.CYAN} [9] Join The Discord
'''
    if menu_num == 3:
        content = f'''
{Fore.CYAN}██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░░█████╗░░█████╗░
{Fore.BLUE}██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔═══╝░██╔═══╝░██╔═══╝░
{Fore.MAGENTA}██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██████╗░██████╗░██████╗░
{Fore.RED}██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██╔══██╗██╔══██╗██╔══██╗
{Fore.YELLOW}██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝╚█████╔╝╚█████╔╝
{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░░╚════╝░░╚════╝░
{Fore.MAGENTA} Swatting Methods/Secure emails  0 MADE BY HANAKO 0

{Fore.CYAN} [10] Globfone (Free)
{Fore.CYAN} [11] Set Up GV (Paid But Better)
{Fore.BLUE} [12] 988 suicide Hotline (Free + May get them sent to a mental hospital)
{Fore.BLUE} [13] @Mailum.com
{Fore.CYAN} [14] @Proton.me
'''
    if menu_num == 4:
        content = f'''
{Fore.CYAN}██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░░█████╗░░█████╗░
{Fore.BLUE}██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔═══╝░██╔═══╝░██╔═══╝░
{Fore.MAGENTA}██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██████╗░██████╗░██████╗░
{Fore.RED}██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██╔══██╗██╔══██╗██╔══██╗
{Fore.YELLOW}██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝╚█████╔╝╚█████╔╝
{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░░╚════╝░░╚════╝░
{Fore.MAGENTA} Telegram Links/Paste Bin links  0 MADE BY HANAKO 0

{Fore.CYAN} [15] My Personal telegram
{Fore.CYAN} [16] Group Telegram
{Fore.BLUE} [17] Group Announcements Telegram
{Fore.BLUE} [18] Doxbin
{Fore.CYAN} [19] Vilebin
'''
    if menu_num == 5:
        content = f'''
{Fore.CYAN}██████╗░██████╗░░█████╗░░░░░░██╗███████╗░█████╗░████████╗  ░█████╗░░█████╗░░█████╗░
{Fore.BLUE}██╔══██╗██╔══██╗██╔══██╗░░░░░██║██╔════╝██╔══██╗╚══██╔══╝  ██╔═══╝░██╔═══╝░██╔═══╝░
{Fore.MAGENTA}██████╔╝██████╔╝██║░░██║░░░░░██║█████╗░░██║░░╚═╝░░░██║░░░  ██████╗░██████╗░██████╗░
{Fore.RED}██╔═══╝░██╔══██╗██║░░██║██╗░░██║██╔══╝░░██║░░██╗░░░██║░░░  ██╔══██╗██╔══██╗██╔══██╗
{Fore.YELLOW}██║░░░░░██║░░██║╚█████╔╝╚█████╔╝███████╗╚█████╔╝░░░██║░░░  ╚█████╔╝╚█████╔╝╚█████╔╝
{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝░╚════╝░░╚════╝░╚══════╝░╚════╝░░░░╚═╝░░░  ░╚════╝░░╚════╝░░╚════╝░
{Fore.MAGENTA} Rarbin.com / website  0 MADE BY HANAKO 0

{Fore.CYAN} [20] user/Ae
{Fore.CYAN} [21] user/su
{Fore.BLUE} [22] user/jk
{Fore.BLUE} [23] user/67
{Fore.CYAN} [24] 2n9 Website
'''

    print(Fore.CYAN + content)

current_menu = 1

while True:
    print_menu(current_menu)
    menu = input(Fore.CYAN + "Select an option or type 'next or back': ").strip().lower()

    if menu == "next":
        if current_menu == 1:
            current_menu = 2
        elif current_menu == 2:
            current_menu = 3
        elif current_menu == 3:
            current_menu = 4
        elif current_menu == 4:
            current_menu = 5
        continue

    if menu == "back":
        if current_menu == 5:
            current_menu = 4
        elif current_menu == 4:
            current_menu = 3
        elif current_menu == 3:
            current_menu = 2
        elif current_menu == 2:
            current_menu = 1
        continue

    if menu == "0":
        break
    if current_menu == 1:
        if menu == "1":
            url = f"https://www.beenverified.com"
            print(f"\nOpening: {url}")
            webbrowser.open(url)

        elif menu == "2":
            phone = input("Enter phone number (with country code): ").strip()
            url = f"https://apilayer.net/api/validate?access_key={phone_api_key}&number={phone}"
            done_flag = [False]
            t_spinner = threading.Thread(target=spinner, args=(done_flag,))
            t_progress = threading.Thread(target=progress_bar, args=(done_flag, 5))
            t_spinner.start()
            t_progress.start()
            try:
                response = requests.get(url)
                done_flag[0] = True
                t_spinner.join()
                t_progress.join()
                data = response.json()
                if data.get("valid"):
                    output = (
                        f"\n--- Phone Info ---\n"
                        f"Country: {data.get('country_name')}\n"
                        f"Location: {data.get('location')}\n"
                        f"Carrier: {data.get('carrier')}\n"
                        f"Line Type: {data.get('line_type')}\n"
                    )
                    typewriter(output)
                else:
                    typewriter(f"{Fore.YELLOW}[!] Invalid phone number.")
            except Exception as e:
                done_flag[0] = True
                typewriter(f"{Fore.RED}Error retrieving phone info: {e}")

        elif menu == "3":
            url = f"https://www.whitepages.com/reverse-address"
            print(f"\nOpening: {url}")
            webbrowser.open(url)

        elif menu == "4":
            ip = input("Enter IP address (or leave blank for your IP): ").strip()
            url = f"https://ipinfo.io/{ip}/json" if ip else "https://ipinfo.io/json"
            done_flag = [False]
            t_spinner = threading.Thread(target=spinner, args=(done_flag,))
            t_progress = threading.Thread(target=progress_bar, args=(done_flag, 5))
            t_spinner.start()
            t_progress.start()
            try:
                response = requests.get(url)
                done_flag[0] = True
                t_spinner.join()
                t_progress.join()
                data = response.json()
                output = "\n--- IP Info ---\n"
                for key, value in data.items():
                    output += f"{key.title()}: {value}\n"
                typewriter(output)
            except Exception as e:
                done_flag[0] = True
                typewriter(f"{Fore.RED}Error retrieving IP info: {e}")

        else:
            typewriter(f"{Fore.RED}[!] Invalid selection.")

    else:  # menu 2 options 5-8
        if menu == "5":
            email = input("Enter email address: ").strip()
            url = f"https://apilayer.net/api/check?access_key={email_api_key}&email={email}&smtp=1&format=1"
            done_flag = [False]
            t_spinner = threading.Thread(target=spinner, args=(done_flag,))
            t_progress = threading.Thread(target=progress_bar, args=(done_flag, 5))
            t_spinner.start()
            t_progress.start()
            try:
                response = requests.get(url)
                done_flag[0] = True
                t_spinner.join()
                t_progress.join()
                data = response.json()
                output = (
                    f"\n--- Email Info ---\n"
                    f"Format Valid: {data.get('format_valid')}\n"
                    f"MX Found: {data.get('mx_found')}\n"
                    f"SMTP Check: {data.get('smtp_check')}\n"
                    f"Disposable: {data.get('disposable')}\n"
                    f"Domain: {data.get('domain')}\n"
                    f"Free Email: {data.get('free')}\n"
                    f"Score: {data.get('score')} (0 to 1, higher = more deliverable)\n"
                )
                if not data.get("format_valid"):
                    output += f"{Fore.YELLOW}[!] Invalid email format.\n"
                typewriter(output)
            except Exception as e:
                done_flag[0] = True
                typewriter(f"{Fore.RED}Error validating email: {e}")

        elif menu == "6":
            domain = input("Enter domain (e.g. example.com): ").strip()
            api_url = f'https://api.api-ninjas.com/v1/dnslookup?domain={domain}'
            headers = {'X-Api-Key': DNS_API_KEY}
            done_flag = [False]
            t_spinner = threading.Thread(target=spinner, args=(done_flag,))
            t_progress = threading.Thread(target=progress_bar, args=(done_flag, 5))
            t_spinner.start()
            t_progress.start()
            try:
                response = requests.get(api_url, headers=headers)
                done_flag[0] = True
                t_spinner.join()
                t_progress.join()
                if response.status_code == 200:
                    typewriter(f"\n--- DNS Records for {domain} ---\n{response.text}")
                else:
                    typewriter(f"{Fore.RED}Error {response.status_code}: {response.text}")
            except Exception as e:
                done_flag[0] = True
                typewriter(f"{Fore.RED}Exception during DNS lookup: {e}")

        elif menu == "7":
            ip = input("Enter IP address to ping: ").strip()
            if ip:
                ping_ip(ip)
            else:
                typewriter(f"{Fore.YELLOW}[!] No IP entered.")

        elif menu == "8":
            url = "https://www.view-page-source.com/"
            print(f"\nOpening: {url}")
            webbrowser.open(url)


        elif menu == "9":
            url = "https://discord.gg/tjdgK3pF"
            print(f"\nOpening: {url}")
            webbrowser.open(url)

        elif menu == "10":
            url = "https://globfone.com/"
            print(f"\nOpening: {url}")
            webbrowser.open(url)

        elif menu == "11":
            url = "https://voice.google.com/signup"
            print(f"nOpening: {url}")
            webbrowser.open(url)
       
        elif menu == "12":
            url = "https://988lifeline.org/"
            print(f"nOpening {url}")
            webbrowser.open(url)

        elif menu == "13":
            url = "hhttps://mailum.com/"
            print(f"nOpening: {url}")
            webbrowser.open(url)

        elif menu == "14":
            url = "https://account.proton.me/mail/signup?ref=mailhero"
            print(f"nOpening: {url}")
            webbrowser.open(url)
        
        elif menu == "15":
            url = "https://t.me/endextortion"
            print(f"nOpening: {url}")
            webbrowser.open(url)
       
        elif menu == "16":
            url = "https://t.me/+1plKawZsiDEwYmU0"
            print(f"nOpening: {url}")
            webbrowser.open(url)

        elif menu == "17":
            url = "https://t.me/i2n9Ann"
            print(f"nOpening: {url}")
            webbrowser.open(url)
            
        elif menu == "18":
            url = "https://doxbin.com/user/2n9"
            print(f"nOpening {url}")
            webbrowser.open(url)

        elif menu == "19":
            url = "https://vilebin.ch/user/@Hanako"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        elif menu == "20":
            url = "https://rarbin.com/user/AE"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        elif menu == "21":
            url = "https://rarbin.com/user/su"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        elif menu == "22":
            url = "https://rarbin.com/user/jk"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        elif menu == "23":
            url = "https://rarbin.com/user/67"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        elif menu == "24":
            url = "https://988ae.xyz"
            print(f"nOpening {url}")
            webbrowser.open(url)
        
        else:
            typewriter(f"{Fore.RED}[!] Invalid selection.")

    input(f"\n{Fore.CYAN}Press Enter to return to menu...")
