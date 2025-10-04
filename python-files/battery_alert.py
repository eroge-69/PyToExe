"""
Battery Alert! Tray App
Features:
- Tray icon shows battery % and charging status
- Settings window: slider + textbox for threshold, Save & Close, Exit App
- Notifications when battery hits threshold
- Auto-start on Windows boot with toggle
- Ready for PyInstaller packaging into .exe
"""

import os
import sys
import threading
import time
import psutil
from plyer import notification
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw
import pystray
import winreg

APP_NAME = "Battery Alert!"
CHECK_INTERVAL = 60  # seconds
DEFAULT_THRESHOLD = 20

class BatteryApp:
    def __init__(self):
        self.threshold = DEFAULT_THRESHOLD
        self.notified_low = False
        self.notified_full = False
        self.icon = None
        self._stop_event = threading.Event()
        self._last_tooltip = ""
        self.icon_image = self._create_icon()

    def _create_icon(self, size=64):
        img = Image.new("RGBA", (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        # battery body
        draw.rectangle([size*0.2, size*0.25, size*0.8, size*0.75], outline="black", width=3, fill="white")
        # battery nub
        draw.rectangle([size*0.8, size*0.4, size*0.95, size*0.6], fill="black")
        return img

    # Auto-start registry
    def register_autostart(self, enable=True):
        try:
            exe = sys.executable
            if exe.lower().endswith("python.exe"):
                exe = exe.replace("python.exe", "pythonw.exe")
            script = os.path.abspath(sys.argv[0])
            cmd = f'"{exe}" "{script}"'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
        except Exception:
            pass

    # Update tooltip
    def _update_tooltip(self, percent, charging):
        tooltip = f"{APP_NAME} | {percent}% | {'Charging' if charging else 'Discharging'} | Alert @{self.threshold}%"
        if tooltip != self._last_tooltip:
            self.icon.title = tooltip
            self._last_tooltip = tooltip

    # Send notification
    def _notify(self, title, msg):
        try:
            notification.notify(title=title, message=msg, app_name=APP_NAME, timeout=8)
        except:
            pass

    # Check battery
    def check_battery(self, manual=False):
        batt = psutil.sensors_battery()
        if not batt:
            return
        percent = batt.percent
        charging = batt.power_plugged
        self._update_tooltip(percent, charging)

        if percent <= self.threshold and not charging and not self.notified_low:
            self._notify("🔋 Low Battery", f"Battery is at {percent}%. Plug in your charger.")
            self.notified_low = True
        elif percent > self.threshold or charging:
            self.notified_low = False

        if percent >= 95 and charging and not self.notified_full:
            self._notify("⚡ Battery Full", "Battery ~95%+. Consider unplugging.")
            self.notified_full = True
        elif percent < 95 or not charging:
            self.notified_full = False

        if manual:
            self._notify("Battery Status", f"{percent}% - {'Charging' if charging else 'Not Charging'}")

    # Background monitoring
    def _monitor(self):
        while not self._stop_event.is_set():
            self.check_battery()
            for _ in range(CHECK_INTERVAL):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    # Settings window
    def _open_settings(self):
        win = tk.Tk()
        win.title(f"{APP_NAME} Settings")
        win.geometry("300x180")
        win.resizable(False, False)

        tk.Label(win, text="Set Low Battery Alert (%)").pack(pady=5)

        val = tk.IntVar(value=self.threshold)
        slider = ttk.Scale(win, from_=1, to=100, orient="horizontal", variable=val)
        slider.pack(padx=20, pady=5, fill="x")

        entry = tk.Entry(win, textvariable=val)
        entry.pack(pady=5)

        auto_start_var = tk.BooleanVar(value=self._is_autostart_enabled())
        def toggle_autostart():
            self.register_autostart(auto_start_var.get())
        tk.Checkbutton(win, text="Start with Windows", variable=auto_start_var, command=toggle_autostart).pack(pady=5)

        def save_close():
            self.threshold = val.get()
            messagebox.showinfo(APP_NAME, f"Threshold set to {self.threshold}%")
            win.destroy()

        ttk.Button(win, text="Save & Close", command=save_close).pack(side="left", padx=20, pady=10)
        ttk.Button(win, text="Exit App", command=self.stop).pack(side="right", padx=20, pady=10)

        win.mainloop()

    # Check if auto-start enabled
    def _is_autostart_enabled(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                value = winreg.QueryValueEx(key, APP_NAME)
                return True
        except FileNotFoundError:
            return False

    # Start tray app
    def start(self):
        threading.Thread(target=self._monitor, daemon=True).start()
        menu = (
            pystray.MenuItem("Check Now", lambda: self.check_battery(manual=True)),
            pystray.MenuItem("Settings", lambda: self._open_settings()),
            pystray.MenuItem("Exit", lambda: self.stop())
        )
        self.icon = pystray.Icon(APP_NAME, self.icon_image, APP_NAME, menu)
        self.icon.run()

    # Stop everything
    def stop(self):
        self._stop_event.set()
        self.icon.stop()
        sys.exit(0)

# Run app
if __name__ == "__main__":
    app = BatteryApp()
    app.start()
