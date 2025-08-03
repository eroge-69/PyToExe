import requests
import time
import re
import pyperclip
from plyer import notification
from colorama import init, Fore, Style
import threading
import keyboard
import os

init(autoreset=True)

CONFIG_FILE = "config.txt"

def load_token():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_token(token):
    with open(CONFIG_FILE, "w") as f:
        f.write(token.strip())

TOKEN = load_token()
if not TOKEN or TOKEN.lower() == "your_token_here":
    print(Fore.YELLOW + "Please input your token:")
    TOKEN = input(">> ").strip()
    save_token(TOKEN)

CHANNELS = {
    "1": ("10 Million+", "1394958063341015081"),
    "2": ("1–10 Million", "1394958060828627064"),
}

JOB_ID_REGEX = re.compile(r"- (?:🆔 )?Job ID \(PC\): ```([^\s`]+)```", re.MULTILINE)
channel_id = None
base_url = None
paused = False
running = True
last_msg_id = None

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(Fore.MAGENTA + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + "         TRRST  A U T O  J O I N E R")
    print(Fore.MAGENTA + "=" * 50 + "\n")

def print_info(text): print(Fore.CYAN + "[INFO]" + Style.RESET_ALL + " " + text)
def print_success(text): print(Fore.GREEN + "[SUCCESS]" + Style.RESET_ALL + " " + text)
def print_warning(text): print(Fore.YELLOW + "[WARNING]" + Style.RESET_ALL + " " + text)
def print_error(text): print(Fore.RED + "[ERROR]" + Style.RESET_ALL + " " + text)

def pretty_print_message(content):
    skip_prefixes = ["- 🌐 Join Link:", "- Job ID (Mobile):"]
    for line in content.strip().splitlines():
        if any(line.startswith(prefix) for prefix in skip_prefixes): continue
        if line.startswith("- 🏷️ Name:"): print(Fore.MAGENTA + line)
        elif line.startswith("- 💰 Money per sec:"): print(Fore.YELLOW + line)
        elif line.startswith("- 👥 Players:"): print(Fore.CYAN + line)
        elif "Brainrot Notify" in line or "Chilli Hub" in line:
            print(Fore.GREEN + Style.BRIGHT + line)
        else: print(line)

def get_latest_message():
    global last_msg_id, paused, running
    while running:
        if paused:
            time.sleep(0.1)
            continue

        try:
            response = requests.get(base_url, headers={
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*",
                "Referer": f"https://discord.com/channels/@me/{channel_id}",
            })

            if response.status_code != 200:
                print_error(f"HTTP {response.status_code}: {response.text}")
                time.sleep(0.5)
                continue

            data = response.json()
            if not data:
                time.sleep(0.5)
                continue

            msg = data[0]
            msg_id = msg["id"]
            if msg_id == last_msg_id:
                time.sleep(0.1)
                continue
            last_msg_id = msg_id

            author = msg["author"]["username"]
            content = msg.get("content", "")

            for embed in msg.get("embeds", []):
                content += f"\n{embed.get('title', '')}\n{embed.get('description', '')}"
                for field in embed.get("fields", []):
                    content += f"\n- {field['name']}: {field['value']}"

            clear_terminal()
            print_header()
            print_success(f"New message from {author}:")
            pretty_print_message(content)

            lines = content.splitlines()
            brainrot_line = next((l for l in lines if "Brainrot Notify" in l or "Chilli Hub" in l), "")
            name_line = next((l for l in lines if l.startswith("- 🏷️ Name:")), "")
            money_line = next((l for l in lines if l.startswith("- 💰 Money per sec:")), "")
            players_line = next((l for l in lines if l.startswith("- 👥 Players:")), "")

            notif_text = "\n".join(filter(None, [brainrot_line, name_line, money_line, players_line]))

            match = JOB_ID_REGEX.search(content)
            if match and not paused:
                job_code = match.group(1).strip()
                pyperclip.copy(job_code)

                notification.notify(
                    title="Discord Job-ID Notification",
                    message=notif_text,
                    timeout=8
                )
                print_success(f"Copied Job-ID code: {job_code}")
            else:
                print_info("No Job-ID code found in the message.")

        except Exception as e:
            print_error(f"Exception occurred: {e}")
        time.sleep(0.1)

def listen_for_keys():
    global paused, running, channel_id, base_url, last_msg_id

    while running:
        if keyboard.is_pressed('['):
            paused = not paused
            state = "Paused" if paused else "Resumed"
            print_info(f"{state}. Press [ again to toggle, or ] to return to menu.")
            time.sleep(0.5)

        if keyboard.is_pressed(']'):
            paused = True
            print_info("Returning to menu...")
            time.sleep(0.5)
            select_channel()
            last_msg_id = None
            paused = False

        time.sleep(0.1)

def select_channel():
    global channel_id, base_url

    clear_terminal()
    print_header()

    print(Fore.BLUE + "=== Channel Selection Menu ===")
    for key, (label, _) in CHANNELS.items():
        print(f"{key}. {label}")
    print(Fore.BLUE + "===============================\n")

    while True:
        choice = input(Fore.CYAN + "Select a channel (1 or 2): ").strip()
        if choice in CHANNELS:
            name, channel_id = CHANNELS[choice]
            base_url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
            print_success(f"Monitoring channel: {name}")
            break
        else:
            print_error("Invalid selection. Please enter 1 or 2.")

if __name__ == "__main__":
    select_channel()
    threading.Thread(target=listen_for_keys, daemon=True).start()
    get_latest_message()
