import tkinter as tk
import ctypes
import threading
import time
from datetime import datetime

# Prevent Sleep Constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001

class SleepShield:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SleepShield")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.active = False
        self.duration = tk.IntVar()
        self.duration.set(0)

        tk.Label(self.root, text="SleepShield", font=("Helvetica", 18, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)
        tk.Label(self.root, text="How long to keep PC awake? (Minutes)", font=("Helvetica", 10), bg="#1e1e1e", fg="white").pack()

        tk.Entry(self.root, textvariable=self.duration, width=10, font=("Helvetica", 12)).pack(pady=10)

        tk.Button(self.root, text="Start", command=self.start_awake, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold")).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit, width=15, bg="#f44336", fg="white", font=("Helvetica", 10, "bold")).pack()

        self.root.mainloop()

    def start_awake(self):
        self.active = True
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

        minutes = self.duration.get()
        self.seconds_left = minutes * 60 if minutes > 0 else -1  # -1 = infinite

        self.show_black_screen()

    def show_black_screen(self):
        self.full = tk.Toplevel()
        self.full.attributes('-fullscreen', True)
        self.full.configure(bg="black")
        self.full.focus_force()  # Makes sure ESC key works instantly
        self.full.bind("<Escape>", lambda e: self.stop_awake())

        self.clock_label = tk.Label(self.full, font=("Helvetica", 48, "bold"), fg="white", bg="black")
        self.clock_label.pack(expand=True)

        self.timer_label = tk.Label(self.full, font=("Helvetica", 24), fg="gray", bg="black")
        self.timer_label.pack()

        self.hint_label = tk.Label(self.full, text="Press ESC to exit", font=("Helvetica", 12, "italic"), fg="gray", bg="black")
        self.hint_label.pack(pady=20)

        self.update_display()

    def update_display(self):
        if not self.active:
            return

        now = datetime.now().strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
        self.clock_label.config(text=now)

        if self.seconds_left == -1:
            self.timer_label.config(text="Timer: ∞ Forever")
        else:
            mins = self.seconds_left // 60
            secs = self.seconds_left % 60
            self.timer_label.config(text=f"Time left: {mins:02d}:{secs:02d}")
            self.seconds_left -= 1
            if self.seconds_left < 0:
                self.stop_awake()
                return

        self.full.after(1000, self.update_display)

    def stop_awake(self):
        self.active = False
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        self.full.destroy()

# Run the app
SleepShield()
