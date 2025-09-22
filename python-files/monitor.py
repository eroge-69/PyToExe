import psutil
import win32gui
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import schedule
import threading
import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

# Configuration
LOG_INTERVAL = 30  # Seconds
IDLE_THRESHOLD = 300  # 5 min
SHEET_ID = "1KrcHjPM_PssF3PhrSOEcInhTEzUyS6DjwENPIElF8c0"  # Your Google Sheet ID
CREDENTIALS_FILE = "credentials.json"  # Must be in same folder as .exe
CONFIG_FILE = "config.json"  # For user/PC names

# Global variables
logs = []
last_activity = time.time()
user_name = ""
pc_name = ""

def setup_config():
    """Prompt for user and PC names if config doesn't exist."""
    global user_name, pc_name
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            user_name = config.get('user_name', '')
            pc_name = config.get('pc_name', '')
        if user_name and pc_name:
            return  # Config exists and is valid
    # Prompt via GUI
    root = tk.Tk()
    root.withdraw()  # Hide main window
    user_name = simpledialog.askstring("Setup", "Enter User Name (e.g., Alice_Sales):")
    if not user_name:
        messagebox.showerror("Error", "User Name required. Exiting.")
        exit(1)
    pc_name = simpledialog.askstring("Setup", "Enter PC Name (e.g., PC-Desk-05):")
    if not pc_name:
        messagebox.showerror("Error", "PC Name required. Exiting.")
        exit(1)
    config = {'user_name': user_name, 'pc_name': pc_name}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    messagebox.showinfo("Success", "Configuration saved. The app will now run in the background.")

def get_active_window():
    """Get current foreground window title."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        return title if title else "Unknown"
    except:
        return "Error"

def on_activity():
    """Update last activity time on mouse/keyboard input."""
    global last_activity
    last_activity = time.time()

def log_activity():
    """Log current activity and system stats."""
    activity = "Idle" if time.time() - last_activity > IDLE_THRESHOLD else get_active_window()
    timestamp = datetime.now().isoformat()
    cpu = psutil.cpu_percent()
    logs.append([timestamp, user_name, pc_name, activity, str(cpu)])
    print(f"Logged: {user_name} on {pc_name} - {activity} at {timestamp}")

def flush_logs():
    """Send logs to Google Sheets."""
    if logs:
        try:
            sheet.append_rows(logs)
            print("Logs sent to Google Sheets")
            logs.clear()
        except Exception as e:
            print(f"Failed to send logs: {e}")

# Idle detection (simplified, using polling)
def monitor_input():
    last_mouse = win32gui.GetCursorPos()
    while True:
        time.sleep(1)
        current_mouse = win32gui.GetCursorPos()
        if current_mouse != last_mouse:
            on_activity()
            last_mouse = current_mouse

# Main setup
setup_config()

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# Schedule tasks
schedule.every(LOG_INTERVAL).seconds.do(log_activity)
schedule.every(300).seconds.do(flush_logs)  # Every 5 min

# Start input monitoring in a separate thread
threading.Thread(target=monitor_input, daemon=True).start()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)