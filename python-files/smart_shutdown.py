import os
import ctypes
import tkinter as tk
from tkinter import messagebox
import threading
import time
import winsound
from PIL import Image, ImageDraw
import pystray

# DEFAULTS (used if user doesn't input anything)
DEFAULT_IDLE_LIMIT = 15 * 60      # seconds
DEFAULT_COUNTDOWN_DURATION = 120  # seconds
BEEP_INTERVAL = 10                # beep every X seconds during countdown

def get_idle_time():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis / 1000.0
    return 0

class ShutdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Auto Shutdown")
        self.root.geometry("420x300")
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.root.resizable(False, False)

        # Default state
        self.idle_limit = DEFAULT_IDLE_LIMIT
        self.countdown_duration = DEFAULT_COUNTDOWN_DURATION
        self.shutdown_scheduled = False
        self.countdown = self.countdown_duration

        # --- UI Elements ---
        self.setup_controls()

        # Background monitoring thread
        self.idle_thread = threading.Thread(target=self.monitor_idle)
        self.idle_thread.daemon = True
        self.idle_thread.start()

        self.icon = self.create_tray_icon()

    def setup_controls(self):
        # Input for idle time (minutes)
        tk.Label(self.root, text="Idle Time (minutes):").pack()
        self.idle_entry = tk.Entry(self.root)
        self.idle_entry.insert(0, str(DEFAULT_IDLE_LIMIT // 60))
        self.idle_entry.pack()

        # Input for countdown time (seconds)
        tk.Label(self.root, text="Countdown Duration (seconds):").pack()
        self.countdown_entry = tk.Entry(self.root)
        self.countdown_entry.insert(0, str(DEFAULT_COUNTDOWN_DURATION))
        self.countdown_entry.pack()

        # Apply button
        tk.Button(self.root, text="Apply Settings", command=self.apply_settings).pack(pady=5)

        # Status label
        self.status = tk.Label(self.root, text="Monitoring user activity...", font=("Arial", 12))
        self.status.pack(pady=10)

        # Countdown label
        self.timer_label = tk.Label(self.root, text="", font=("Arial", 24), fg="red")
        self.timer_label.pack(pady=10)

        # Cancel button
        self.cancel_button = tk.Button(self.root, text="Cancel Shutdown", command=self.cancel_shutdown, state='disabled')
        self.cancel_button.pack(pady=5)

    def apply_settings(self):
        try:
            idle_minutes = int(self.idle_entry.get())
            countdown_seconds = int(self.countdown_entry.get())
            self.idle_limit = idle_minutes * 60
            self.countdown_duration = countdown_seconds
            self.status.config(text=f"Settings applied: Idle={idle_minutes} min, Countdown={countdown_seconds} sec")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for time settings.")

    def monitor_idle(self):
        while True:
            idle = get_idle_time()
            if idle > self.idle_limit and not self.shutdown_scheduled:
                self.root.after(0, self.start_countdown)
            elif idle < 5 and self.shutdown_scheduled:
                self.root.after(0, self.cancel_shutdown)
            time.sleep(5)

    def start_countdown(self):
        self.shutdown_scheduled = True
        self.countdown = self.countdown_duration
        self.status.config(text="Idle detected! Countdown to shutdown:")
        self.cancel_button.config(state='normal')
        self.update_countdown()

    def update_countdown(self):
        if self.countdown > 0 and self.shutdown_scheduled:
            mins, secs = divmod(self.countdown, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

            if self.countdown % BEEP_INTERVAL == 0:
                threading.Thread(target=lambda: winsound.Beep(1000, 200)).start()

            self.countdown -= 1
            self.root.after(1000, self.update_countdown)
        elif self.shutdown_scheduled:
            self.execute_shutdown()

    def cancel_shutdown(self):
        self.shutdown_scheduled = False
        self.status.config(text="Shutdown cancelled. Monitoring resumed.")
        self.timer_label.config(text="")
        self.cancel_button.config(state='disabled')

    def execute_shutdown(self):
        self.status.config(text="Shutting down now...")
        self.timer_label.config(text="00:00")
        os.system("shutdown -s -t 5")

    def minimize_to_tray(self):
        self.root.withdraw()
        self.icon.run_detached()

    def restore_from_tray(self, icon, item):
        self.root.deiconify()
        icon.stop()

    def exit_app(self, icon, item):
        icon.stop()
        self.root.destroy()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), "white")
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill='black')

        return pystray.Icon(
            "SmartShutdown",
            image,
            "Smart Auto Shutdown",
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.restore_from_tray),
                pystray.MenuItem("Exit", self.exit_app)
            )
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = ShutdownApp(root)
    root.mainloop()
