#!/usr/bin/env python3
import sys, subprocess, importlib, threading, time, ctypes
import tkinter as tk
from tkinter import ttk

# Auto-installazione
def install_and_import(pkg):
    try:
        return importlib.import_module(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return importlib.import_module(pkg)

pyautogui = install_and_import('pyautogui')

# WinAPI: evita la sospensione
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

def prevent_sleep():
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    )

class KeepAwakeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KeepAwake Controller")
        self.running = False

        self.interval = tk.DoubleVar(value=0.3)  # Minuti
        self.distance = tk.IntVar(value=20)      # Pixel
        self.status = tk.StringVar(value="OFF")

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Intervallo (min):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(frm, from_=0.1, to=60, increment=0.1, textvariable=self.interval).grid(row=0, column=1)

        ttk.Label(frm, text="Movimento (px):").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(frm, from_=1, to=100, textvariable=self.distance).grid(row=1, column=1)

        self.status_led = ttk.Label(frm, text="Stato: OFF", foreground="red")
        self.status_led.grid(row=2, columnspan=2, pady=5)

        ttk.Button(frm, text="Start / Stop", command=self.toggle).grid(row=3, column=0, sticky="we")
        ttk.Button(frm, text="Test", command=self.do_movement).grid(row=3, column=1, sticky="we")

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.status_led.config(text="Stato: ON", foreground="green")
            threading.Thread(target=self._worker, daemon=True).start()
        else:
            self.status_led.config(text="Stato: OFF", foreground="red")

    def _worker(self):
        while self.running:
            self.do_movement()
            prevent_sleep()
            time.sleep(self.interval.get() * 60)

    def do_movement(self):
        x, y = pyautogui.position()
        d = self.distance.get()

        # Croce: Su, Giù, Sx, Dx
        pyautogui.moveTo(x, y - d)
        pyautogui.moveTo(x, y + d)
        pyautogui.moveTo(x - d, y)
        pyautogui.moveTo(x + d, y)
        pyautogui.moveTo(x, y)

if __name__ == "__main__":
    KeepAwakeApp().mainloop()
