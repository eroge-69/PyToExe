import ctypes
import platform
import sys

def is_windows():
    return platform.system() == "Windows"

if not is_windows():
    print("? This script only works on Windows.")
    sys.exit()

def is_caps_lock_on():
    # 0x14 is virtual-key code for Caps Lock
    return ctypes.windll.user32.GetKeyState(0x14) & 1

def force_caps_lock_on():
    if not is_caps_lock_on():
        ctypes.windll.user32.keybd_event(0x14, 0, 0, 0)  # key down
        ctypes.windll.user32.keybd_event(0x14, 0, 2, 0)  # key up

force_caps_lock_on()
