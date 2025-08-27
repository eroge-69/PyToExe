import curl_cffi.requests
import threading
from kasawa import console
from pystyle import Colors, Colorate, Center, Anime, Write
import websocket
import time
import json
import base64
import uuid
import random
import re
from module.discord.header import discord
from module.discord.websockets import fetch_sessionID
import asyncio
from concurrent.futures import ThreadPoolExecutor

session = curl_cffi.requests.Session(impersonate="chrome")

with open("./input/proxies.txt", "r", encoding="utf-8") as f:
    proxies = f.read().splitlines()

with open("./input/tokens.txt", "r", encoding="utf-8") as f:
    tokens = f.read().splitlines()

with open("./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def change_proxy():
    while True:
        selected_proxy = random.choice(proxies)
        session.proxies = {
            "http": f"http://{selected_proxy}", 
            "https": f"http://{selected_proxy}"
        }
        time.sleep(5)


if config['proxies']:
    proxy_thread = threading.Thread(target=change_proxy, daemon=True)
    proxy_thread.start()


def joiner(token, invite):
    sessionid = fetch_sessionID(token)
    payload = {
        'session_id': sessionid,
    }
    r = session.post(f'https://discord.com/api/v9/invites/{invite}', headers=discord.header(token, invite), json=payload)
    if r.status_code == 200:
        console.log.success(f"Token {token[:25]}***** Joined {invite} !")
    elif r.status_code == 429:
        console.log.warning(f" Token {token[:25]}***** Rate Limit !")
    elif r.status_code == 400:
        console.log.warning(f"Token {token[:25]}***** Captcha !")
    elif r.status_code == 403:
        console.log.error(f"Token {token[:25]}**** Cloudflare !")
    else:
        console.log.error(f"Token {token[:25]}**** Error {r.json()}")
        


async def main():
    console.clear()
    print(Colorate.Horizontal(Colors.blue_to_cyan, rf'''
 _____     _                      ___       _                 
|_   _|   | |                    |_  |     (_)                
  | | ___ | | _____ _ __  ___      | | ___  _ _ __   ___ _ __ 
  | |/ _ \| |/ / _ \ '_ \/ __|     | |/ _ \| | '_ \ / _ \ '__|
  | | (_) |   <  __/ | | \__ \ /\__/ / (_) | | | | |  __/ |   
  \_/\___/|_|\_\___|_| |_|___/ \____/ \___/|_|_| |_|\___|_|   
                                                              
                load {len(tokens)} Tokens, load {len(proxies)} proxies
'''))
    console.log.ask("Invite : ")
    invite = input("╰-➤ ")
    try:

        invite = discord.format_invite(invite)
        info = discord.invite_info(invite)
        print("")
        console.log.info("═════════════════════════════════════════════════")
        console.log.info(f"Guild Name : {info['profile']['name']} ({info['profile']['id']})")
        console.log.info(f"Member Count : {info['profile']['member_count']} Member Online : {info['profile']['online_count']}")
        console.log.info(f"Description : {info['profile']['description']}")
        console.log.info("═════════════════════════════════════════════════")
    except:
        console.log.error(f"Failed to Join this server !")

    if config['captcha']:
        for token in tokens:
            joiner(token, invite)
    else:
        threads = []
        for token in tokens:
            t = threading.Thread(target=joiner, args=(token, invite,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()




if __name__ == "__main__":
    asyncio.run(main())