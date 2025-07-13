# -*- coding: utf-8 -*-
import random
import string
import requests
import os
from pystyle import Colors, Colorate
import time

def ngl():
    def deviceId():
        chars = string.ascii_lowercase + string.digits
        return f"{''.join(random.choices(chars, k=8))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=12))}"

    def UserAgent():
        with open('user-agents.txt', 'r', encoding='utf-8') as file:
            agents = file.readlines()
            return random.choice(agents).strip()

    def Proxy():
        with open('proxies.txt', 'r', encoding='utf-8') as file:
            proxy_list = file.readlines()
            if not proxy_list:
                print(R + "[-]" + W + " Error: proxies.txt is empty.")
                exit(1)
            random_proxy = random.choice(proxy_list).strip()
            return {'http': random_proxy, 'https': random_proxy}

    R = '\033[31m'
    G = '\033[32m'
    W = '\033[0m'

    os.system('cls' if os.name == 'nt' else 'clear')

    # ✅ ASCII-safe banner
    print(Colorate.Vertical(Colors.blue_to_purple, """
  ______     __  __      
 |____  |   / _|/ _|     
     / /_ _| |_| |_ __ _ 
    / / _` |  _|  _/ _` |
   / / (_| | | | || (_| |
  /_/ \__,_|_| |_| \__,_|
                         
                         
    """))

    nglusername = input(Colorate.Vertical(Colors.blue_to_purple, "name: "))
    message = input(Colorate.Vertical(Colors.blue_to_purple, "msg: "))
    Count = int(input(Colorate.Vertical(Colors.blue_to_purple, "count: ")))
    delay = float(input(Colorate.Vertical(Colors.blue_to_purple, "sec?: ")))
    use_proxy = input(Colorate.Vertical(Colors.blue_to_purple, "Use proxy? (y/n): ")).lower()

    proxies = Proxy() if use_proxy == "y" else None

    print(Colorate.Vertical(Colors.green_to_blue, "Please wait..."))

    value = 0
    notsend = 0

    while value < Count:
        headers = {
            'Host': 'ngl.link',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': f'{UserAgent()}',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://ngl.link',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'https://ngl.link/{nglusername}',
            'accept-language': 'en-US,en;q=0.9',
        }

        data = {
            'username': nglusername,
            'question': message,
            'deviceId': deviceId(),
            'gameSlug': '',
            'referrer': '',
        }

        try:
            response = requests.post('https://ngl.link/api/submit', headers=headers, data=data, proxies=proxies)
            if response.status_code == 200:
                notsend = 0
                value += 1
                print(G + "[+]" + W + f" Sent => {value}")
            else:
                notsend += 1
                print(R + "[-]" + W + " Not Sent")

            if notsend == 4:
                print(R + "[!]" + W + " Changing proxy and headers...")
                if use_proxy == "y":
                    proxies = Proxy()
                notsend = 0

            time.sleep(delay)

        except requests.exceptions.ProxyError:
            print(R + "[-]" + W + " Proxy failed!")
            if use_proxy == "y":
                proxies = Proxy()

ngl()
