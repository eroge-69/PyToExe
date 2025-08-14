import time
import random
import threading
import ctypes
from ctypes import wintypes
import keyboard
import psutil
import win32gui
import win32process
import winsound

# ----------------------------
# Settings
# ----------------------------
TARGET_PROCESSES = {"gta5.exe", "gta5_enhanced.exe"}  # case-insensitive
PRESS_MIN_MS = 50
PRESS_MAX_MS = 120
INTERVAL_MIN_S = 0.5
INTERVAL_MAX_S = 2.0

# Volume (0.0 to 1.0)
TONE_VOLUME = 0.5

# ----------------------------
# State
# ----------------------------
active = False
stop_script = False

# ----------------------------
# WinAPI: SendInput definitions
# ----------------------------
user32 = ctypes.WinDLL('user32', use_last_error=True)

# INPUT types
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# KEYEVENTF flags
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_SCANCODE    = 0x0008

# Scan codes (Set 1) for WASD
SC_W = 0x11
SC_A = 0x1E
SC_S = 0x1F
SC_D = 0x20

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk",      wintypes.WORD),
        ("wScan",    wintypes.WORD),
        ("dwFlags",  wintypes.DWORD),
        ("time",     wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    )

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx",          wintypes.LONG),
        ("dy",          wintypes.LONG),
        ("mouseData",   wintypes.DWORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    )

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg",    wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )

class INPUT_union(ctypes.Union):
    _fields_ = (
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    )

class INPUT(ctypes.Structure):
    _fields_ = (
        ("type",   wintypes.DWORD),
        ("union",  INPUT_union),
    )

LPINPUT = ctypes.POINTER(INPUT)

user32.SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)
user32.SendInput.restype  = wintypes.UINT

# ----------------------------
# Volume control
# ----------------------------
winmm = ctypes.WinDLL('winmm')
def set_volume(vol: float):
    """Set system volume for beeps (0.0 to 1.0)."""
    vol = max(0.0, min(1.0, vol))
    vol_hex = int(vol * 0xFFFF)
    packed = (vol_hex << 16) | vol_hex
    winmm.waveOutSetVolume(0, packed)

# ----------------------------
# Beep helpers
# ----------------------------
def tone(freq, dur_ms):
    winsound.Beep(freq, dur_ms)

def tone_activate():
    tone(1000, 100)

def tone_deactivate():
    tone(500, 100)

def tone_exit():
    tone(300, 80)
    time.sleep(0.05)
    tone(300, 80)

# ----------------------------
# Input functions
# ----------------------------
def send_key_scancode(scancode: int, press_ms: int):
    """Press and release a key by scan code using SendInput."""
    # Key down
    down = INPUT()
    down.type = INPUT_KEYBOARD
    down.union.ki = KEYBDINPUT(
        wVk=0,
        wScan=scancode,
        dwFlags=KEYEVENTF_SCANCODE,
        time=0,
        dwExtraInfo=None
    )
    # Key up
    up = INPUT()
    up.type = INPUT_KEYBOARD
    up.union.ki = KEYBDINPUT(
        wVk=0,
        wScan=scancode,
        dwFlags=KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=None
    )

    n = user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    if n != 1:
        raise ctypes.WinError(ctypes.get_last_error())

    time.sleep(max(press_ms, 1) / 1000.0)

    n = user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))
    if n != 1:
        raise ctypes.WinError(ctypes.get_last_error())

def gta_is_focused() -> bool:
    """Return True if the foreground window belongs to GTA5/GTA5_Enhanced."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = psutil.Process(pid).name().lower()
        return name in TARGET_PROCESSES
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def spam_loop():
    global active, stop_script
    keys = [SC_W, SC_A, SC_S, SC_D]

    while not stop_script:
        if active and gta_is_focused():
            sc = random.choice(keys)
            press_ms = random.randint(PRESS_MIN_MS, PRESS_MAX_MS)
            try:
                send_key_scancode(sc, press_ms)
            except Exception as e:
                print(f"SendInput error: {e}")
                time.sleep(0.2)
            time.sleep(random.uniform(INTERVAL_MIN_S, INTERVAL_MAX_S))
        else:
            time.sleep(0.05)

# ----------------------------
# Hotkey actions
# ----------------------------
def on_scroll_lock(_event):
    global active
    active = not active
    if active:
        print("[ScrollLock] Bot ON")
        tone_activate()
    else:
        print("[ScrollLock] Bot OFF")
        tone_deactivate()

def on_pause(_event):
    global stop_script
    print("[Pause] Exiting...")
    tone_exit()
    stop_script = True

# ----------------------------
# Main
# ----------------------------
def main():
    global stop_script
    set_volume(TONE_VOLUME)

    print("GTA V SendInput bot")
    print("- Scroll Lock: toggle on/off")
    print("- Pause: exit")
    print("- Works only when GTA5 window is focused.")

    keyboard.on_press_key("scroll lock", on_scroll_lock)
    keyboard.on_press_key("pause", on_pause)

    t = threading.Thread(target=spam_loop, daemon=True)
    t.start()

    while not stop_script:
        time.sleep(0.1)

if __name__ == "__main__":
    main()
