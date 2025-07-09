import random
import string
import tls_client
import threading
import os
import ctypes
import json
import requests
from colorama import init, Fore, Back
#Access Code Protection
access_code = "Mega6711"  # Set your access code here

user_input = input("Enter Your Key: ")

if user_input != access_code:
    print(" Incorrect Key")
    exit()
else:
    print(" Starting the tool...\n")

# CONFIG #
config_file = "config.json"
with open(config_file, "r") as f:
    config = json.load(f)

WEBHOOK_URL = config.get("webhook_url")
WEBHOOK_NAME = config.get("webhook_name")
WEBHOOK_AVATAR_URL = config.get("webhook_avatar_url")
RANDOM_METHOD_LENGTH = 4  # تم تحديث القيمة إلى 3
THREADS = config.get("Thread")  # تعديل هنا لاستخدام قيمة من ملف التكوين
# CONFIG #

init()
session = tls_client.Session(
    client_identifier="chrome_115", random_tls_extension_order=True)
with open('proxies.txt', 'r') as file:
    proxies = [line.strip() for line in file]
with open('tokens.txt', 'r') as file:
    tokens = [line.strip() for line in file]

class stats:
    checked = 0
    taken = 0
    sniped = 0


def updatetitle():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW(
            f"Discord Nickname Sniper - Checked: {stats.checked} | Taken: {stats.taken} | Sniped: {stats.sniped}")


threading.Thread(target=updatetitle).start()


def checkUsername():
    username = generateUsername()
    url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
    headers = {
        "authority": "discord.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": "__dcfduid=676e06b0565b11ed90f9d90136e0396b; __sdcfduid=676e06b1565b11ed90f9d90136e0396bc28dfd451bebab0345b0999e942886d8dfd7b90f193729042dd3b62e2b13812f; __cfruid=1cefec7e9c504b453c3f7111ebc4940c5a92dd08-1666918609; locale=en-US",
        "origin": "https://discord.com",
        "pragma": "no-cache",
        "referer": "https://discord.com/channels/@me",
        "sec-ch-ua": f'"Google Chrome";v="115", "Chromium";v="115", "Not=A?Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36",
        "x-debug-options": "bugReporterEnabled",
        "x-discord-locale": "en-US",
        "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwNy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTA3LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlcGVhc2VfY2hhbm5lcCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE1NDc1MCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
    }
    jsondata = {
        "username": username
    }
    try:
        req = session.post(url, headers=headers, json=jsondata, proxy={
            "http": "http://" + random.choice(proxies),
            "https": "http://" + random.choice(proxies),
        })
    except:
        return
    if req.status_code == 200:
        stats.checked += 1
        checktaken = req.json()['taken']
        if checktaken == True:
            print(
                f" {Back.LIGHTRED_EX}  ✕  {Back.RESET} {Fore.WHITE}Username Taken - {username}")
            stats.taken += 1
        else:
            stats.sniped += 1
            print(
                f" {Back.LIGHTGREEN_EX}  ✓  {Back.RESET} {Fore.WHITE}Username Sniped - {username}")
            sendToWebhook(username)


def sendToWebhook(username):

    embed = {
        "title": "Available !",
        "description": f"**Username :** ```{username} ```",
        "color": 0,  # Random color for fun!
        "thumbnail": {
            "url": "https://cdn.discordapp.com/avatars/759484523900567573/5a17ef9104d95f13b24ab421636dd8a8.png?size=1024"
        },
        "footer": {
            "text": "https://discord.gg/xZFeabab9R",
            "icon_url": "https://cdn.discordapp.com/avatars/759484523900567573/5a17ef9104d95f13b24ab421636dd8a8.png?size=1024"
        }
    }
    payload = {
        "content": "**<@414527355197849603>**",
        "username": WEBHOOK_NAME,
        "avatar_url": WEBHOOK_AVATAR_URL,
        "embeds": [embed]
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"Successfully sent username {username} to Discord Webhook!")
    except Exception as e:
        print(f"Error sending username {username} to Discord Webhook:", e)











import random
import string

def generateUsername():
    # اختيار نمط عشوائي: 0 للنمط الأول، 1 للنمط الثاني
    pattern = random.choice([0, 1])

    if pattern == 0:
        # النمط الأول: حرف مكرر + رمز + حرف عشوائي
        characters = string.ascii_lowercase + string.digits
        repeated_char = random.choice(characters)
        random_char = random.choice(characters)
        symbol = random.choice(["_", "."])
        username = [repeated_char, repeated_char, symbol, random_char]
        random.shuffle(username)
        return ''.join(username)

    else:
        # النمط الثاني: 3 أرقام + رمز في موقع عشوائي
        digits = random.choices("0123456789", k=3)
        symbol = random.choice(["_", "."])
        insert_pos = random.randint(0, 3)
        username = digits[:]
        username.insert(insert_pos, symbol)
        return ''.join(username)
















def loopThread():
    while True:
        checkUsername()


print("Mega")

print("Hello My Hunter - Mega:")
print("User 88_l")
USERNAME_GENERATION_METHOD = "RANDOM"

# بدء العملية
threadsstarted = []
for _ in range(THREADS):
    thread = threading.Thread(target=loopThread)
    threadsstarted.append(thread)
    thread.start()
for th in threadsstarted:
    th.join()

print(f"{Fore.WHITE}Press any key...")
os.system("pause > NUL")
exit(1)