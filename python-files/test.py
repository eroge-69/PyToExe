import ctypes
from ctypes import wintypes
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulong),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

@HOOKPROC
def low_level_mouse_proc(nCode, wParam, lParam):
    if nCode >= 0:
        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        print(f"Mouse event at {ms.pt.x}, {ms.pt.y}, wParam={wParam}")
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

def install_hook():
    hook_id = user32.SetWindowsHookExW(14, low_level_mouse_proc, kernel32.GetModuleHandleW(None), 0)
    if not hook_id:
        print("Failed to install hook - run as administrator")
        return None

    def message_loop():
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    threading.Thread(target=message_loop, daemon=True).start()
    return hook_id

if __name__ == "__main__":
    hook = install_hook()
    if hook:
        print("Hook installed, move your mouse...")
        import time
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            user32.UnhookWindowsHookEx(hook)
            print("Hook removed, exiting")
