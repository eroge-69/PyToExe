import cv2
import numpy as np
import pyautogui
import time
import requests
import uuid
import hashlib
from datetime import datetime, timedelta
import keyboard  # Make sure to install this library using `pip install keyboard`

WEBHOOK_URL = "https://discord.com/api/webhooks/1385709782329069629/unU5rbuyUAflG1rA9itrn0JS0J-FO2nKLjs64qd7hx062KGY-JjVdAzSezl2EZCxkHE1"
VALID_KEYS = {
    "LIFETIME-53485thfg": "Have fun",
    "LIFETIME-432746res": "Have fun",
    "LIFETIME-35873gfdd": "Have fun",
    # Add more keys here
}

IPQUALITYSCORE_API_KEY = 'your_ipqualityscore_api_key'
IPQUALITYSCORE_URL = 'https://ipqualityscore.com/api/json/ip/'

def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        return ip
    except Exception as e:
        print(f"❌ IP address error: {e}")
        return None

def is_vpn(ip):
    url = f'{IPQUALITYSCORE_URL}{IPQUALITYSCORE_API_KEY}/{ip}'
    response = requests.get(url)
    data = response.json()
    return data.get('vpn', False)

def get_hwid():
    mac = uuid.getnode()
    hwid = hashlib.sha256(str(mac).encode()).hexdigest()
    return hwid

def send_webhook(content):
    data = {"content": content}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Failed to send webhook: {e}")

def load_bindings():
    try:
        response = requests.get(WEBHOOK_URL)
        if response.status_code == 200:
            data = response.json()
            if 'content' in data and data['content'].startswith('bindings:'):
                bindings_data = data['content'].split('bindings:', 1)[1].strip()
                return dict(item.split(':') for item in bindings_data.split(';') if item)
    except Exception as e:
        print(f"❌ Error loading bindings: {e}")
    return {}

def save_bindings(bindings):
    bindings_data = ';'.join(f"{key}:{ip}:{timestamp}" for key, (ip, timestamp) in bindings.items())
    content = f"bindings:{bindings_data}"
    send_webhook(content)

def check_key(key):
    hwid = get_hwid()
    ip = get_ip_address()
    if not ip:
        print("Unable to retrieve IP address. Access denied.")
        return False
    if is_vpn(ip):
        print("VPN detected. Access denied.")
        return False
    bindings = load_bindings()
    current_time = datetime.utcnow()
    if key in bindings:
        stored_ip, timestamp_str = bindings[key]
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        if stored_ip != ip:
            send_webhook(f"Key attempt: `{key}` - Status: WRONG IP BUD - HWID: `{hwid[:8]}...` - IP: `{ip}` - Stored IP: `{stored_ip}`")
            print("WRONG IP BUD. This key is already bound to another IP address. Access denied.")
            return False
        if current_time > timestamp + timedelta(minutes=1):
            send_webhook(f"Key attempt: `{key}` - Status: Key expired - HWID: `{hwid[:8]}...` - IP: `{ip}`")
            print("Key expired. Access denied.")
            return False
        send_webhook(f"Key attempt: `{key}` - Status: Access granted - HWID: `{hwid[:8]}...` - IP: `{ip}`")
        print(f"Access granted to {VALID_KEYS[key]}")
        return True
    if key not in VALID_KEYS:
        send_webhook(f"Key attempt: `{key}` - Status: Invalid key - HWID: `{hwid[:8]}...` - IP: `{ip}`")
        print("Invalid key. Access denied.")
        return False
    timestamp = current_time
    bindings[key] = (ip, timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'))
    save_bindings(bindings)
    send_webhook(f"Key attempt: `{key}` - Status: New binding created - HWID: `{hwid[:8]}...` - IP: `{ip}`")
    print(f"Access granted to {VALID_KEYS[key]}")
    return True

def is_red(pixel):
    b, g, r = pixel
    return r > 150 and g < 100 and b < 100

def wait_for_key_press():
    print("Press any key or mouse button to continue...")
    key = keyboard.read_key(suppress=True)
    print(f"Key pressed: {key}")
    return key

def on_press(event, panic_key):
    if event.name == panic_key:
        print("Panic key pressed. Exiting triggerbot.")
        exit()

def triggerbot(delay, keybind, panic_key):
    crosshair_x = 960  # Adjust as needed for your screen resolution
    crosshair_y = 540
    region_size = 10

    # Set up the key press handler
    keyboard.on_press(lambda e: on_press(e, panic_key))

    try:
        while True:
            screenshot = pyautogui.screenshot(region=(
                crosshair_x - region_size//2,
                crosshair_y - region_size//2,
                region_size,
                region_size
            ))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            red_detected = False
            for y in range(region_size):
                for x in range(region_size):
                    if is_red(frame[y, x]):
                        red_detected = True
                        break
                if red_detected:
                    break

            if red_detected:
                pyautogui.press(keybind)
                time.sleep(delay)

            time.sleep(0.01)
    except Exception as e:
        print(f"Error in triggerbot: {e}")

def main():
    key = input("Enter your access key: ").strip()
    if check_key(key):
        delay = float(input("Enter the delay (seconds): ").strip())
        panic_key = input("Enter the panic key: ").strip()
        print("Waiting for keybind input...")
        keybind = wait_for_key_press()
        print(f"Keybind set to: {keybind}")
        triggerbot(delay, keybind, panic_key)

if __name__ == "__main__":
    main()