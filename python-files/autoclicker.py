# autoclicker_gui.py

import time
import threading
import ctypes
from ctypes import Structure, c_long, c_uint, c_void_p, byref
from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, DWORD
import tkinter as tk

# Win32 constants
WM_HOTKEY            = 0x0312
MOD_NONE             = 0x0000
VK_F1                = 0x70
VK_ESCAPE            = 0x1B
MOUSE_DOWN           = 0x0002
MOUSE_UP             = 0x0004

# Shared state
running     = False
exiting     = False
interval_us = 500   # default interval: 500 μs

# POINT and MSG structures for GetMessage
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class MSG(Structure):
    _fields_ = [
        ("hwnd",    HWND),
        ("message", UINT),
        ("wParam",  WPARAM),
        ("lParam",  LPARAM),
        ("time",    DWORD),
        ("pt",      POINT),
    ]

user32 = ctypes.windll.user32

def click_loop():
    """Tight-loop clicker using perf_counter for sub-ms timing."""
    global running, exiting, interval_us
    last = time.perf_counter()
    while not exiting:
        if running:
            now     = time.perf_counter()
            elapsed = (now - last) * 1_000_000  # seconds → μs
            if elapsed >= interval_us:
                user32.mouse_event(MOUSE_DOWN, 0, 0, 0, 0)
                user32.mouse_event(MOUSE_UP,   0, 0, 0, 0)
                last = now
        else:
            time.sleep(0.01)
            last = time.perf_counter()

def hotkey_listener():
    """Register F1/Esc and flip running or set exiting on WM_HOTKEY."""
    global running, exiting
    user32.RegisterHotKey(None, 1, MOD_NONE, VK_F1)
    user32.RegisterHotKey(None, 2, MOD_NONE, VK_ESCAPE)
    msg = MSG()
    while not exiting and user32.GetMessageW(byref(msg), None, 0, 0) != 0:
        if msg.message == WM_HOTKEY:
            if msg.wParam == 1:
                running = not running
            elif msg.wParam == 2:
                exiting = True
                break
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageW(byref(msg))
    user32.UnregisterHotKey(None, 1)
    user32.UnregisterHotKey(None, 2)

def run_gui():
    """Build and run the Tkinter interface."""
    global interval_us, exiting

    root = tk.Tk()
    root.title("Auto-Clicker")
    root.resizable(False, False)

    # Clean exit when window closes
    def on_close():
        nonlocal_exit()
        root.destroy()

    def nonlocal_exit():
        global exiting
        exiting = True

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Input fields
    tk.Label(root, text="Seconds:").grid(row=0, column=0, padx=5, pady=4, sticky="e")
    entry_s = tk.Entry(root, width=8); entry_s.grid(row=0, column=1)
    tk.Label(root, text="Milliseconds:").grid(row=1, column=0, sticky="e")
    entry_ms = tk.Entry(root, width=8); entry_ms.grid(row=1, column=1)
    tk.Label(root, text="Microseconds:").grid(row=2, column=0, sticky="e")
    entry_us = tk.Entry(root, width=8); entry_us.grid(row=2, column=1)

    entry_s.insert(0,  "0")
    entry_ms.insert(0, "0")
    entry_us.insert(0, str(interval_us))

    # Apply button
    def apply_interval():
        global interval_us
        try:
            s  = int(entry_s.get())
            ms = int(entry_ms.get())
            us = int(entry_us.get())
            total = max(1, s*1_000_000 + ms*1_000 + us)
            interval_us = total
        except ValueError:
            pass  # ignore invalid input

    tk.Button(root, text="Apply", command=apply_interval)\
      .grid(row=3, column=0, columnspan=2, pady=6)

    # Status label
    status_lbl = tk.Label(root, text="OFF", fg="red", font=("Arial", 16))
    status_lbl.grid(row=4, column=0, columnspan=2, pady=(0,10))

    # Periodically refresh ON/OFF display
    def refresh_status():
        if exiting:
            root.quit()
            return
        if running:
            status_lbl.config(text="ON", fg="green")
        else:
            status_lbl.config(text="OFF", fg="red")
        root.after(100, refresh_status)

    root.after(100, refresh_status)
    root.mainloop()

if __name__ == "__main__":
    # Daemon threads to allow process exit when GUI closes
    threading.Thread(target=click_loop,     daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    run_gui()
    print("Auto-clicker exited.")