import requests
import time
import os
import sys
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def animate_text(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def loading_bar(duration=3):
    print(f"{Color.OKCYAN}Yükleniyor", end='')
    for _ in range(duration * 4):
        print('.', end='', flush=True)
        time.sleep(0.25)
    print(Color.ENDC)

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer = f"{Color.WARNING}{mins:02d}:{secs:02d}{Color.ENDC}"
        print(f"\r⏳ Bekleme süresi: {timer}", end='', flush=True)
        time.sleep(1)
    print(f"\n{Color.OKGREEN}✅ Yeni işlem yapılabilir!{Color.ENDC}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    clear_screen()
    print(f"""{Color.HEADER}
┌──────────────────────────────────────┐
│   {Color.OKGREEN}Instagram & TikTok Beğeni Tool{Color.HEADER}   │
├──────────────────────────────────────┤
│   {Color.OKBLUE}1. Instagram Beğeni (75)                {Color.HEADER}│
│   {Color.OKBLUE}2. TikTok Beğeni (30)                   {Color.HEADER}│
│   {Color.OKBLUE}0. Çıkış                                {Color.HEADER}│
└──────────────────────────────────────┘    
""")

def send_request(platform, link):
    cookies = {
        'trsdb': '1',
        'token': '761991ff786b3aabeb9944728c8fa629',
        'ci_session': 'd23b9327b6ebdd6578b0709f8437d736dba475ce'
    }

    headers = {
        'authority': 'leofame.com',
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://leofame.com',
        'referer': '',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }

    params = {'api': '1'}

    if platform == '1':
        url = 'https://leofame.com/free-instagram-likes'
        headers['referer'] = url
        data = {
            'token': cookies['token'],
            'timezone_offset': 'Europe/Istanbul',
            'free_link': link,
            'quantity': '75',
            'speed': '5'
        }
        wait_seconds = 300

    elif platform == '2':
        url = 'https://leofame.com/free-tiktok-likes'
        headers['referer'] = url
        data = {
            'token': cookies['token'],
            'timezone_offset': 'Europe/Istanbul',
            'free_link': link,
            'quantity': '30'
        }
        wait_seconds = 80

    else:
        print(f"{Color.FAIL}🚫 Geçersiz seçim.{Color.ENDC}")
        return

    try:
        loading_bar()
        response = requests.post(url, params=params, cookies=cookies, headers=headers, data=data)
        if response.ok:
            print(f"{Color.OKGREEN}✅ Beğeniler gönderildi, lütfen bekleyin...{Color.ENDC}")
            countdown(wait_seconds)
        else:
            print(f"{Color.FAIL}⚠ Sunucu hatası: {response.status_code}{Color.ENDC}")
    except Exception as e:
        print(f"{Color.FAIL}❌ Hata oluştu: {e}{Color.ENDC}")
def main():
    while True:
        banner()
        choice = input(f"{Color.OKCYAN}👉 Seçiminizi yapın: {Color.ENDC}").strip()
        if choice.lower() == '0':
            print(f"{Color.WARNING}Çıkış yapılıyor...{Color.ENDC}")
            break
        link = input(f"{Color.OKBLUE}🔗 Linki girin: {Color.ENDC}").strip()
        send_request(choice, link)
        input(f"\n{Color.BOLD}🔁 Devam etmek için Enter'a basın...{Color.ENDC}")
if __name__ == '__main__':
    animate_text(f"{Color.BOLD} Tiktok ve İnstagram beğeni Tooluna Hoş geldiniz..!{Color.ENDC}", 0.05)
    main()
