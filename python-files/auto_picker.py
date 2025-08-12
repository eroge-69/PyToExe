import keyboard
import time
import threading
import ctypes
import sys

# Check if running as admin (required for some games)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Restarting as administrator...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Game-specific settings
PRESS_DURATION = 0.05  # How long to hold E key
PRESS_INTERVAL = 0.1   # Time between presses

# Control variables
auto_press_active = False
stop_event = threading.Event()

def press_e_loop():
    while not stop_event.is_set():
        keyboard.press('e')
        time.sleep(PRESS_DURATION)
        keyboard.release('e')
        time.sleep(PRESS_INTERVAL - PRESS_DURATION)

def toggle_auto_press():
    global auto_press_active, stop_event
    
    auto_press_active = not auto_press_active
    
    if auto_press_active:
        stop_event.clear()
        threading.Thread(target=press_e_loop, daemon=True).start()
        print("Auto E: ON (F1 to stop)")
    else:
        stop_event.set()
        print("Auto E: OFF (F1 to start)")

# Set up hotkey
keyboard.add_hotkey('f1', toggle_auto_press)

print("RYL2 Auto E Presser")
print("Press F1 to toggle auto-press E")
print("Press ESC to exit")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_event.set()
    print("\nExiting...")
finally:
    keyboard.unhook_all()