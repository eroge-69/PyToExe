import tkinter as tk
import time
import threading
import keyboard
import win32gui
import win32con
import ctypes
from playsound import playsound

class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spike Timer")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.configure(bg='black')
        self.root.geometry("250x100+20+20")
        self.root.attributes("-alpha", 0.85)

        self.timer_label = tk.Label(self.root, text="00.0", font=("Segoe UI", 36, "bold"), fg="#FFFFFF", bg="black")
        self.timer_label.pack(pady=5)

        self.defuse_label = tk.Label(self.root, text="Warte auf Spike...", font=("Segoe UI", 14, "bold"), fg="#AAAAAA", bg="black")
        self.defuse_label.pack(pady=5)

        self.start_button = tk.Button(self.root, text="START", font=("Segoe UI", 10, "bold"), fg="white", bg="#28a745", command=self.start_timer, width=8)
        self.start_button.place(x=20, y=70)

        self.stop_button = tk.Button(self.root, text="RESET", font=("Segoe UI", 10, "bold"), fg="white", bg="#dc3545", command=self.reset_timer, width=8)
        self.stop_button.place(x=140, y=70)

        self.running = False
        self.start_time = 0
        self.played_10s = False
        self.played_defuse_deadline = False

        threading.Thread(target=self.hotkey_listener, daemon=True).start()
        self.make_click_through()

        self.root.mainloop()

    def hotkey_listener(self):
        keyboard.add_hotkey('F1', self.start_timer)
        keyboard.wait()

    def start_timer(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            self.played_10s = False
            self.played_defuse_deadline = False
            threading.Thread(target=self.update_timer, daemon=True).start()

    def reset_timer(self):
        self.running = False
        self.timer_label.config(text="00.0")
        self.defuse_label.config(text="Warte auf Spike...")

    def update_timer(self):
        while self.running:
            elapsed = time.time() - self.start_time
            remaining = 45 - elapsed

            if remaining <= 0:
                self.timer_label.config(text="💥")
                self.defuse_label.config(text="Explodiert!")
                self.running = False
                break

            self.timer_label.config(text=f"{remaining:04.1f}")

            if remaining >= 7:
                self.defuse_label.config(text="🟢 Full Defuse")
            elif remaining >= 3.5:
                self.defuse_label.config(text="🟡 Half Defuse")
            else:
                self.defuse_label.config(text="🔴 Kein Defuse")

            # Sounds
            if remaining <= 10 and not self.played_10s:
                self.played_10s = True
                threading.Thread(target=lambda: playsound("10sec.mp3"), daemon=True).start()

            if remaining <= 7 and not self.played_defuse_deadline:
                self.played_defuse_deadline = True
                threading.Thread(target=lambda: playsound("defuse_deadline.mp3"), daemon=True).start()

            time.sleep(0.1)

    def make_click_through(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        hwnd = win32gui.FindWindow(None, self.root.title())
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

if __name__ == "__main__":
    Overlay()
