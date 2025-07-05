import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import ctypes
import sys

ADMIN_PASSWORD = "1234"  # Change this to your desired admin password

class CafeShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CafeShield - Session Timer")
        self.root.geometry("300x200")

        self.time_left = 0
        self.running = False

        self.label = tk.Label(root, text="Enter session time (mins):")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack()

        self.start_btn = tk.Button(root, text="Start Session", command=self.start_session)
        self.start_btn.pack(pady=5)

        self.timer_label = tk.Label(root, text="Time left: 00:00")
        self.timer_label.pack(pady=10)

        self.admin_btn = tk.Button(root, text="Admin Override", command=self.admin_override)
        self.admin_btn.pack()

    def start_session(self):
        try:
            minutes = int(self.entry.get())
            self.time_left = minutes * 60
            self.running = True
            threading.Thread(target=self.countdown).start()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a number.")

    def countdown(self):
        while self.time_left > 0 and self.running:
            mins, secs = divmod(self.time_left, 60)
            time_format = f"{mins:02}:{secs:02}"
            self.timer_label.config(text=f"Time left: {time_format}")
            time.sleep(1)
            self.time_left -= 1

        if self.running:
            self.lock_screen()

    def lock_screen(self):
        messagebox.showinfo("Session Ended", "Time's up! Locking the system.")
        if sys.platform == 'win32':
            ctypes.windll.user32.LockWorkStation()
        else:
            os.system('gnome-screensaver-command -l')

    def admin_override(self):
        pwd = tk.simpledialog.askstring("Admin", "Enter admin password:", show='*')
        if pwd == ADMIN_PASSWORD:
            self.running = False
            self.timer_label.config(text="Session ended by admin")
        else:
            messagebox.showerror("Access Denied", "Wrong password!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeShieldApp(root)
    root.mainloop()
