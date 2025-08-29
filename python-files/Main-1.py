import os
import time
import psutil
import win32gui
import win32process 
import threading
from pynput import mouse, keyboard
from datetime import datetime
import logging
import configparser
from pynput.keyboard import Key,KeyCode

home_directory = os.path.expanduser("~")
directories = home_directory.split(os.sep)
formatted_directory = "_".join(directories[1:])

# Change server path to Documents folder
documents_path = os.path.join(home_directory, "Documents")
today_date = datetime.now().strftime("%d-%m-%Y")
log_directory = os.path.join(documents_path, "Logs Data", today_date)
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"activity_log_{formatted_directory}_{today_date}.txt")
print(log_file)

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s', 
    handlers=[logging.FileHandler(log_file, encoding='utf-8'), 
    logging.StreamHandler()
    ]
    )

config = configparser.ConfigParser()
config.read(os.path.join(home_directory, "config.ini"))

target_applications = config.get('Settings', 'target_applications', fallback="excel.exe,powerpnt.exe,chrome.exe,winword.exe,outlook.exe,chatgpt.exe").split(',')

user_active = False
key_active = False
last_key = None
last_key_time = None
key_start_time = None
passive_start_time = None
lock = threading.Lock()

KEY_ACTIVE_THRESHOLD = 2 * 60
PASSIVE_ACTIVE_THRESHOLD = 15 * 60

def on_move(x, y):
    global user_active, passive_start_time
    with lock:
        user_active = True
        passive_start_time = None

def on_click(x, y, button, pressed):
    global user_active, passive_start_time
    with lock:
        user_active = True
        passive_start_time = None

def on_scroll(x, y, dx, dy):
    global user_active, passive_start_time
    with lock:
        user_active = True
        passive_start_time = None

windows_key_pressed = False
l_key_pressed = False

def on_press(key):
    global user_active, key_active, last_key, last_key_time, key_start_time, passive_start_time, windows_key_pressed, l_key_pressed
    with lock:
        current_time = time.time()

        if key == Key.cmd:
            windows_key_pressed = True

            if l_key_pressed:
                logging.info("Another Activity - Windows + L press to lock the screen")
                user_active = True
                passive_start_time = None
                windows_key_pressed = False
                l_key_pressed = False
                return 
        elif key == KeyCode.from_char('l'):
            l_key_pressed = True
            if windows_key_pressed:
                logging.info("Another Activity - Windows + L press to lock the screen")
                user_active = True
                passive_start_time = None
                windows_key_pressed = False
                l_key_pressed = False
                return  

        if key == last_key:
            if not key_start_time:
                key_start_time = current_time
            elif (current_time - key_start_time) >= KEY_ACTIVE_THRESHOLD:
                logging.info(f"Continuous key press detected for more than 2 minutes and the key is {key}")
                key_start_time = None
        else:
            key_start_time = current_time

        user_active = True
        key_active = True
        last_key = key
        last_key_time = current_time
        passive_start_time = None

def on_release(key):
    global user_active, key_active, passive_start_time, windows_key_pressed, l_key_pressed
    with lock:
        if key == Key.cmd:
            windows_key_pressed = False
        elif key == KeyCode.from_char('l'):
            l_key_pressed = False

        user_active = True
        passive_start_time = None
        key_active = False

def is_target_application_active():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid > 0:
            active_process = psutil.Process(pid)
            process_name = active_process.name().lower()
            return any(app_name.lower() in process_name for app_name in target_applications)
        else:
            return False
    except psutil.NoSuchProcess:
        return False
    except Exception as e:
        logging.error(f"Error checking target application: {e}")
        return False

def check_user_activity():
    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as mouse_listener, keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
        mouse_listener.join()
        keyboard_listener.join()

def record_activity():
    global user_active, passive_start_time
    current_time = time.time()
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd) or "No Title"

    if is_target_application_active():
        with lock:
            activity = "User active" if user_active else "User passively active"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            active_process = psutil.Process(pid)
            app_name = active_process.name().upper()
            logging.info(f"{app_name} - {window_title} - {activity}")

            if user_active:
                passive_start_time = None
            elif not passive_start_time:
                passive_start_time = current_time

            if passive_start_time and (current_time - passive_start_time) >= PASSIVE_ACTIVE_THRESHOLD:  # Check if passive activity persists for 15 minutes
                logging.info(f'Continuous passive activity detected in {app_name} for more than 15 minutes. Shutting down the computer.')
                passive_start_time = None
        except psutil.NoSuchProcess:
            logging.error(f"Process not found for PID {pid}")
    else:
        logging.info(f"Another activity - {window_title}")

    with lock:
        user_active = False  

def main():
    user_activity_thread = threading.Thread(target=check_user_activity)
    user_activity_thread.daemon = True
    user_activity_thread.start()
    
    try:
        while True:
            record_activity()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        user_activity_thread.join()

if __name__ == "__main__":
    os.makedirs(log_directory, exist_ok=True)
    main()
