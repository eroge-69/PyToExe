#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fake Keyboard — F13 every minute
GUI app. Click Start to begin, Stop to pause. Close the window to exit.
Works without extra Python packages. Intended for Windows 10/11.
"""

import threading
import time
import ctypes
from ctypes import wintypes
import tkinter as tk

# --- Windows-only: send F13 via WinAPI ---
VK_F13 = 0x7C
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    )

class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),)
    _anonymous_ = ("ii",)
    _fields_ = (("type", wintypes.DWORD), ("ii", _I))

SendInput = ctypes.windll.user32.SendInput

def press_vk(vk_code: int):
    ki_down = KEYBDINPUT(wVk=vk_code, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)
    inp_down = INPUT(type=INPUT_KEYBOARD, ki=ki_down)
    ki_up = KEYBDINPUT(wVk=vk_code, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)
    inp_up = INPUT(type=INPUT_KEYBOARD, ki=ki_up)
    n = SendInput(2, ctypes.byref((INPUT * 2)(inp_down, inp_up)), ctypes.sizeof(INPUT))
    return n == 2

class F13Worker(threading.Thread):
    def __init__(self, interval_sec: int, stop_event: threading.Event, on_tick=None):
        super().__init__(daemon=True)
        self.interval = interval_sec
        self.stop_event = stop_event
        self.on_tick = on_tick

    def run(self):
        # fire immediately, then every interval
        while not self.stop_event.is_set():
            ok = press_vk(VK_F13)
            if self.on_tick:
                self.on_tick(ok)
            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fake Keyboard — F13")
        self.geometry("320x160")
        self.resizable(False, False)
        try:
            self.iconbitmap(default="")  # no icon; placeholder
        except Exception:
            pass

        self.status_var = tk.StringVar(value="Status: Inactive")
        self.last_send_var = tk.StringVar(value="Last send: —")

        tk.Label(self, text="Fake Keyboard", font=("Segoe UI", 14, "bold")).pack(pady=(12, 4))
        tk.Label(self, text="Sends F13 every minute while active.").pack(pady=(0, 8))

        self.status_label = tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 11))
        self.status_label.pack()

        self.last_label = tk.Label(self, textvariable=self.last_send_var, font=("Segoe UI", 9))
        self.last_label.pack(pady=(2, 12))

        buttons = tk.Frame(self)
        buttons.pack()
        self.toggle_btn = tk.Button(buttons, text="Start", width=12, command=self.toggle)
        self.toggle_btn.pack(side=tk.LEFT, padx=4)
        self.quit_btn = tk.Button(buttons, text="Quit", width=12, command=self.on_close)
        self.quit_btn.pack(side=tk.LEFT, padx=4)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.stop_event = threading.Event()
        self.worker = None

    def toggle(self):
        if self.worker and self.worker.is_alive():
            self.stop_event.set()
            self.worker = None
            self.status_var.set("Status: Inactive")
            self.toggle_btn.config(text="Start")
        else:
            self.stop_event = threading.Event()
            self.worker = F13Worker(60, self.stop_event, on_tick=self._on_tick)
            self.worker.start()
            self.status_var.set("Status: Active (F13 every 60s)")
            self.toggle_btn.config(text="Stop")

    def _on_tick(self, ok: bool):
        def update_label():
            ts = time.strftime("%H:%M:%S")
            if ok:
                self.last_send_var.set(f"Last send: {ts} (OK)")
            else:
                self.last_send_var.set(f"Last send: {ts} (FAILED)")
        self.after(0, update_label)

    def on_close(self):
        if self.worker and self.worker.is_alive():
            self.stop_event.set()
        self.destroy()

if __name__ == "__main__":
    App().mainloop()
