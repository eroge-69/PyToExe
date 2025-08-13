import ctypes
import threading
import time
import mouse

IsSpamming = False
PressesPerSecond = 700

# Windows API constants
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("WVk", ctypes.c_ushort),
                ("WScan", ctypes.c_ushort),
                ("DWFlags", ctypes.c_ulong),
                ("Time", ctypes.c_ulong),
                ("DwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("UMsg", ctypes.c_ulong),
                ("WParamL", ctypes.c_short),
                ("WParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("DX", ctypes.c_long),
                ("DY", ctypes.c_long),
                ("MouseData", ctypes.c_ulong),
                ("DWFlags", ctypes.c_ulong),
                ("Time", ctypes.c_ulong),
                ("DwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("Ki", KeyBdInput),
                ("Mi", MouseInput),
                ("Hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("Type", ctypes.c_ulong),
                ("II", Input_I)]

KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002

SCAN_A = 0x1E
SCAN_D = 0x20

def PressKey(ScanCode):
    Extra = ctypes.c_ulong(0)
    Ii_ = Input_I()
    Ii_.Ki = KeyBdInput(0, ScanCode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(Extra))
    X = Input(ctypes.c_ulong(1), Ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(X), ctypes.sizeof(X))

def ReleaseKey(ScanCode):
    Extra = ctypes.c_ulong(0)
    Ii_ = Input_I()
    Ii_.Ki = KeyBdInput(0, ScanCode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(Extra))
    X = Input(ctypes.c_ulong(1), Ii_)
    ctypes.windll.user32.SendInput(1, ctypes.byref(X), ctypes.sizeof(X))

def PressAndRelease(ScanCode):
    PressKey(ScanCode)
    ReleaseKey(ScanCode)

def SpamKeys():
    global IsSpamming
    delay = 1 / PressesPerSecond
    while IsSpamming:
        PressAndRelease(SCAN_A)
        PressAndRelease(SCAN_D)
        time.sleep(delay)

def OnMouseButton5Down():
    global IsSpamming
    if not IsSpamming:
        IsSpamming = True
        threading.Thread(target=SpamKeys, daemon=True).start()

def OnMouseButton5Up():
    global IsSpamming
    IsSpamming = False

mouse.on_button(OnMouseButton5Down, buttons=("x2",), types=("down",))
mouse.on_button(OnMouseButton5Up, buttons=("x2",), types=("up",))

print(f"Hold mouse button 5 to enable.")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
