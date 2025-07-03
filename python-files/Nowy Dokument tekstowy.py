import time
import csv
import os
from datetime import datetime, timedelta
import win32gui
import win32process
import psutil
import ctypes

LOG_INTERVAL = 5  # seconds
USAGE_DIR = "pc_usage_logs"
os.makedirs(USAGE_DIR, exist_ok=True)

def get_active_window_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return "WALLPAPER"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        return proc.name()
    except:
        return "Unknown"

def is_screen_on():
    # Returns True if the screen is on (user not locked)
    return ctypes.windll.user32.GetForegroundWindow() != 0

def load_today_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(USAGE_DIR, f"{today}.csv")
    usage = {}
    screen_on_seconds = 0

    if os.path.exists(log_path):
        with open(log_path, "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "SCREEN_ON":
                    screen_on_seconds = int(row[1])
                else:
                    usage[row[0]] = int(row[1])
    return usage, screen_on_seconds

def save_today_log(usage, screen_on_seconds):
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(USAGE_DIR, f"{today}.csv")
    with open(log_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SCREEN_ON", screen_on_seconds])
        for app, secs in usage.items():
            writer.writerow([app, secs])

def format_time(seconds):
    return str(timedelta(seconds=seconds))

def print_usage_summary(usage, screen_on_seconds):
    print("\n--- Daily Usage Summary ---")
    print(f"Total screen-on time: {format_time(screen_on_seconds)}")
    for app, secs in sorted(usage.items(), key=lambda x: -x[1]):
        print(f"{app:<20} {format_time(secs)}")

def main():
    usage, screen_on_seconds = load_today_log()
    print("Tracking PC usage... Press Ctrl+C to stop.")

    while True:
        now = datetime.now()
        app_name = get_active_window_process_name()
        screen_active = is_screen_on()

        if screen_active:
            screen_on_seconds += LOG_INTERVAL
            if app_name not in usage:
                usage[app_name] = 0
            usage[app_name] += LOG_INTERVAL

        save_today_log(usage, screen_on_seconds)
        time.sleep(LOG_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_usage_summary(*load_today_log())
        print("\nStopped tracking.")
