import threading
import ctypes
import time
import random
from pynput import mouse, keyboard
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# ---------------- CONFIGURATION ----------------
DELAY = 0.05      # Time between recoil movements (in seconds)
RECOIL_X = 1      # Recoil movement along the X-axis
RECOIL_Y = 2      # Recoil movement along the Y-axis

PRIMARY_HOTKEY = '1'
SECONDARY_HOTKEY = '2'
PAUSE_HOTKEY = 'p'
CONFIG_HOTKEY = 'l'  # Press 'l' to update config live

# Hardcoded valid license keys (in practice, store securely or validate via server)
VALID_KEYS = {
    "ELIXER-1234-ABCD-5678",
    "ELIXER-9012-EFGH-3456",
    "ELIXER-7890-IJKL-1234"
}

# ---------------- INTERNAL STATE ----------------
holding = False
left_held = False
right_held = False
paused = False

config = {
    'delay': DELAY,
    'x': RECOIL_X,
    'y': RECOIL_Y
}

pause_lock = threading.Lock()

# ---------------- FUNCTIONS ----------------

def move_mouse(dx, dy):
    ctypes.windll.user32.mouse_event(0x0001, int(dx), int(dy), 0, 0)

def recoil_control():
    global paused, holding
    while True:
        with pause_lock:
            if holding and not paused:
                dx = config['x'] if random.random() < 0.5 else 0
                move_mouse(dx, config['y'])
        time.sleep(config['delay'])

def on_click(x, y, button, pressed):
    global left_held, right_held, holding
    if button == mouse.Button.left:
        left_held = pressed
    elif button == mouse.Button.right:
        right_held = pressed
    holding = left_held and right_held

def update_config():
    try:
        print(Fore.MAGENTA + "\n--- Update Recoil Settings ---" + Style.RESET_ALL)
        new_delay = float(input(Fore.MAGENTA + f"New delay (current {config['delay']}): " + Style.RESET_ALL) or config['delay'])
        new_x = float(input(Fore.MAGENTA + f"New X recoil (current {config['x']}): " + Style.RESET_ALL) or config['x'])
        new_y = float(input(Fore.MAGENTA + f"New Y recoil (current {config['y']}): " + Style.RESET_ALL) or config['y'])
        config['delay'] = new_delay
        config['x'] = new_x
        config['y'] = new_y
        print(Fore.MAGENTA + f"[Config Updated] Delay: {new_delay}, X: {new_x}, Y: {new_y}\n" + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "[ERROR] Invalid input. Config not updated.\n" + Style.RESET_ALL)

def on_release(key):
    global paused
    try:
        if key.char == PRIMARY_HOTKEY:
            print(Fore.MAGENTA + "[Hotkey] Primary pressed" + Style.RESET_ALL)
        elif key.char == SECONDARY_HOTKEY:
            print(Fore.MAGENTA + "[Hotkey] Secondary pressed" + Style.RESET_ALL)
        elif key.char == PAUSE_HOTKEY:
            with pause_lock:
                paused = not paused
                print(Fore.MAGENTA + "[System] Paused" if paused else "[System] Resumed" + Style.RESET_ALL)
        elif key.char.lower() == CONFIG_HOTKEY:
            update_config()
    except AttributeError:
        pass

# ---------------- KEY VERIFICATION ----------------

def verify_license_key():
    print(Fore.MAGENTA + "=== ELIXER License Verification ===" + Style.RESET_ALL)
    entered_key = input(Fore.MAGENTA + "Enter your license key: " + Style.RESET_ALL).strip()
    if entered_key in VALID_KEYS:
        print(Fore.MAGENTA + "[SUCCESS] License key verified!" + Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + "[ERROR] Invalid license key. Exiting ELIXER." + Style.RESET_ALL)
        return False

# ---------------- MAIN ----------------

def print_banner():
    ascii_art = r"""
 _______   ___       ___     ___    ___ _______   ________         
|\  ___ \ |\  \     |\  \   |\  \  /  /|\  ___ \ |\   __  \        
\ \   __/|\ \  \    \ \  \  \ \  \/  / | \   __/|\ \  \|\  \       
 \ \  \_|/_\ \  \    \ \  \  \ \    / / \ \  \_|/_\ \   _  _\      
  \ \  \_|\ \ \  \____\ \  \  /     \/   \ \  \_|\ \ \  \\  \|     
   \ \_______\ \_______\ \__\/  /\   \    \ \_______\ \__\\ _\     
    \|_______|\|_______|\|__/__/ /\ __\    \|_______|\|__|\|__|    
                            |__|/ \|__|                            
"""
    print(Fore.MAGENTA + ascii_art + Style.RESET_ALL)

def main():
    if not verify_license_key():
        return  # Exit if key is invalid

    print_banner()
    print(Fore.MAGENTA + "=== ELIXER (Live Config Enabled) ===" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Initial settings -> Delay: {config['delay']}s | X: {config['x']} | Y: {config['y']}" + Style.RESET_ALL)
    print(Fore.MAGENTA + "Hold RIGHT + LEFT mouse buttons to trigger recoil." + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Press '{PAUSE_HOTKEY}' to pause/resume. Press '{CONFIG_HOTKEY.upper()}' to change settings live." + Style.RESET_ALL)
    print(Fore.MAGENTA + "Press Ctrl+C to exit.\n" + Style.RESET_ALL)

    threading.Thread(target=recoil_control, daemon=True).start()
    mouse.Listener(on_click=on_click).start()

    def keyboard_thread():
        with keyboard.Listener(on_release=on_release) as listener:
            listener.join()

    threading.Thread(target=keyboard_thread, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n[System] Exiting ELIXER." + Style.RESET_ALL)

if __name__ == "__main__":
    main()