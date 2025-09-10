import os
import time
import json
import uuid
import sys
import random
import pyperclip  # For clipboard operations
import requests  # For fetching auth, sending webhook, and getting IP
from colorama import Fore, Style, init  # For colored text

# Initialize colorama
init(autoreset=True)

title = "Space Hub | Keys , Gift Cards , Promocodes | Generator"

BOT_NAME = "Space Generator"
BOT_AVATAR = "https://r2.e-z.host/31420b89-b1f8-4bfd-b77f-1e16877fbeed/x6bnefkb.png"
EMBED_IMAGE_URL = "https://r2.e-z.host/31420b89-b1f8-4bfd-b77f-1e16877fbeed/ez37jlr2.png"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1415320561084665876/-751c71ecOfMIXxczAIESRN0zUVQS-oDmB6H6IN1l3sYnw03bZkOWu0LydzVufdwgyTt"

AUTH_URL = "https://gist.githubusercontent.com/ago106/a5562b8c14df8256529e37ab677b5175/raw/"

# Start Logo without animation
def starting_message():
    print("")
    print("")
    print("     → Welcome to Space Hub Generator")
    print("     → Discord: .gg/ktC6dNVxDC")
    print("")

# Load saved credentials
def load_credentials():
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as file:
            return json.load(file)
    return None

# Save credentials
def save_credentials(login, password):
    with open("credentials.json", "w") as file:
        json.dump({"login": login, "password": password}, file)

# Fetch auth data
def fetch_auth_data():
    try:
        response = requests.get(AUTH_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(Fore.RED + f"     → Failed to fetch authorization data: {e}")
        sys.exit(1)

# Get IP address
def get_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except:
        return "Unknown"

# Send to Discord webhook with improved embed using fields and code block
def send_webhook(login, uid, gen_type, key, ip):
    if not DISCORD_WEBHOOK_URL:
        return
    embed = {
        "title": "New Key Generated",
        "color": 0x00ff00,
        "author": {"name": BOT_NAME, "icon_url": BOT_AVATAR},
        "thumbnail": {"url": EMBED_IMAGE_URL},
        "fields": [
            {"name": "Login", "value": login, "inline": True},
            {"name": "UID", "value": uid, "inline": True},
            {"name": "IP", "value": ip, "inline": True},
            {"name": "Type", "value": gen_type, "inline": True},
            {"name": "Generated", "value": f"```\n{key}\n```", "inline": False}
        ]
    }
    data = {"embeds": [embed]}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except:
        pass

# Generate Key V1 (e.g., Gift Cards)
def generate_key_v1():
    chars = "1234567890"
    key = ''.join(random.choice(chars) for _ in range(10))
    return f"{key[:3]}-{key[3:6]}-{key[6:]}"

# Generate Key V2 (e.g., Wave)
def generate_key_v2():
    chars = "abcdef0123456789"
    key = ''.join(random.choice(chars) for _ in range(8))
    key += "-"
    for _ in range(3):
        key += ''.join(random.choice(chars) for _ in range(4))
        key += "-"
    key += ''.join(random.choice(chars) for _ in range(12))
    return key

# Generate Key V3 (e.g., Synapse Z)
def generate_key_v3():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    return ''.join(random.choice(chars) for _ in range(129))

# Copy to Clipboard
def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        print(Fore.GREEN + "     → Key copied to clipboard!")
    except Exception as e:
        print(Fore.RED + f"     → Failed to copy to clipboard: {e}")

# Clear terminal
def clear_terminal():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # POSIX (Linux, macOS и др.)
        os.system('clear')

# Display generated key screen
def display_generated_key(gen_type, key):
    clear_terminal()
    starting_message()
    print("")
    print(Fore.GREEN + f"     → Generated {gen_type} Key: {key}")
    copy_to_clipboard(key)
    time.sleep(3)

# Main Menu
def show_main_menu(login, uid, ip):
    while True:
        clear_terminal()
        starting_message()
        print(Fore.CYAN + "     ╔════════════════════════════════════════╗")
        print(Fore.CYAN + f"     ║ Welcome, {login}!")
        print(Fore.CYAN + f"     ║ UID: {uid}")
        print(Fore.CYAN + "     ║ Select Generator Type:")
        print(Fore.CYAN + "     ║ 1. Wave")
        print(Fore.CYAN + "     ║ 2. Synapse Z")
        print(Fore.CYAN + "     ║ 3. Gift Cards")
        print(Fore.CYAN + "     ║ 4. Exit")
        print(Fore.CYAN + "     ╚════════════════════════════════════════╝")

        choice = input(Fore.YELLOW + "     → Enter your choice (1-4): ")

        if choice == "1":
            key = generate_key_v2()
            send_webhook(login, uid, "Wave", key, ip)
            display_generated_key("Wave", key)
        elif choice == "2":
            key = generate_key_v3()
            send_webhook(login, uid, "Synapse Z", key, ip)
            display_generated_key("Synapse Z", key)
        elif choice == "3":
            key = generate_key_v1()
            send_webhook(login, uid, "Gift Cards", key, ip)
            display_generated_key("Gift Cards", key)
        elif choice == "4":
            print(Fore.RED + "     → Exiting...")
            break
        else:
            print(Fore.RED + "     → Invalid choice. Please try again.")
            time.sleep(2)

# Main Program
if __name__ == "__main__":
    clear_terminal()
    starting_message()
    time.sleep(random.uniform(1.2, 2.3))

    ip = get_ip()
    auth_data = fetch_auth_data()
    users = auth_data.get("users", [])
    credentials = load_credentials()

    if credentials:
        clear_terminal()
        starting_message()
        print(Fore.CYAN + "     → Authenticating with saved credentials...")
        time.sleep(random.uniform(0.9, 1.3))
        login = credentials["login"]
        password = credentials["password"]

        user_data = next((u for u in users if u.get("login") == login and u.get("password") == password), None)
        if user_data:
            uid = user_data.get("uid", "")
            show_main_menu(login, uid, ip)
        else:
            print(Fore.RED + "     → Invalid credentials. Closing in 3 seconds.")
            time.sleep(3)
            if os.path.exists("credentials.json"):
                os.remove("credentials.json")
    else:
        clear_terminal()
        starting_message()
        print(Fore.CYAN + "     → Authorization required...")
        time.sleep(random.uniform(1.5, 2.5))
        print(Fore.CYAN + "     → Please login to your account")
        print("")

        login = input(Fore.YELLOW + "     → Enter Login: ")
        password = input(Fore.YELLOW + "     → Enter Password: ")

        user_data = next((u for u in users if u.get("login") == login and u.get("password") == password), None)
        if user_data:
            save_credentials(login, password)
            uid = user_data.get("uid", "")
            show_main_menu(login, uid, ip)
        else:
            print(Fore.RED + "     → Invalid credentials. Closing in 3 seconds.")
            time.sleep(3)