#!/usr/bin/env python3
"""
TimerWindows - Simple Windows shutdown scheduler
Features:
- Shutdown after N minutes
- Shutdown at a specific clock time (HH:MM)
- Cancel scheduled shutdown
- Live countdown display
Requirements: Windows 10/11
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import datetime
import threading
import time
import sys
import os

class ShutdownScheduler:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TimerWindows - Shutdown Scheduler")
        self.root.geometry("460x320")
        self.root.resizable(False, False)

        self.shutdown_thread = None
        self.cancel_event = threading.Event()
        self.scheduled_epoch = None

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main, text="Windows Shutdown Scheduler", font=("Segoe UI", 14, "bold"))
        title.pack(pady=(0, 8))

        nb = ttk.Notebook(main)
        nb.pack(fill=tk.BOTH, expand=True)

        # Tab 1: By Minutes
        tab_minutes = ttk.Frame(nb)
        nb.add(tab_minutes, text="By Minutes")

        frm_m = ttk.Frame(tab_minutes, padding=10)
        frm_m.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm_m, text="Shutdown after (minutes):").grid(row=0, column=0, sticky=tk.W)
        self.minutes_var = tk.StringVar(value="15")
        ent_m = ttk.Entry(frm_m, width=10, textvariable=self.minutes_var)
        ent_m.grid(row=0, column=1, sticky=tk.W, padx=(8,0))

        btn_schedule_m = ttk.Button(frm_m, text="Schedule", command=self.schedule_by_minutes)
        btn_schedule_m.grid(row=0, column=2, padx=8)

        # Tab 2: By Time
        tab_time = ttk.Frame(nb)
        nb.add(tab_time, text="By Time")

        frm_t = ttk.Frame(tab_time, padding=10)
        frm_t.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm_t, text="Shutdown at time (HH:MM, 24h):").grid(row=0, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value="22:00")
        ent_t = ttk.Entry(frm_t, width=10, textvariable=self.time_var)
        ent_t.grid(row=0, column=1, sticky=tk.W, padx=(8,0))

        btn_schedule_t = ttk.Button(frm_t, text="Schedule", command=self.schedule_by_time)
        btn_schedule_t.grid(row=0, column=2, padx=8)

        # Controls
        ctrl = ttk.Frame(main)
        ctrl.pack(fill=tk.X, pady=(8, 0))

        self.countdown_var = tk.StringVar(value="No shutdown scheduled")
        lbl_cd = ttk.Label(ctrl, textvariable=self.countdown_var, font=("Segoe UI", 10))
        lbl_cd.pack(side=tk.LEFT)

        btn_cancel = ttk.Button(ctrl, text="Cancel Shutdown", command=self.cancel_shutdown)
        btn_cancel.pack(side=tk.RIGHT)

        # Footer
        foot = ttk.Frame(main)
        foot.pack(fill=tk.X, pady=(8,0))
        ttk.Label(foot, text="Note: App uses 'shutdown' command. Requires Windows.", foreground="#666").pack(side=tk.LEFT)

    def schedule_by_minutes(self):
        try:
            minutes = int(self.minutes_var.get().strip())
            if minutes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for minutes.")
            return

        seconds = minutes * 60
        self._schedule_shutdown_in(seconds)

    def schedule_by_time(self):
        text = self.time_var.get().strip()
        try:
            target = datetime.datetime.strptime(text, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Invalid Time", "Please use 24-hour format HH:MM, e.g. 21:30")
            return

        now = datetime.datetime.now()
        target_dt = datetime.datetime.combine(now.date(), target)
        if target_dt <= now:
            # schedule for next day
            target_dt += datetime.timedelta(days=1)
        delta = int((target_dt - now).total_seconds())
        self._schedule_shutdown_in(delta)

    def _schedule_shutdown_in(self, seconds):
        # Cancel any existing schedule
        self.cancel_shutdown(update_message=False)

        self.scheduled_epoch = int(time.time()) + seconds
        # Use Windows shutdown command
        try:
            # /s shutdown, /t seconds delay, /f force close apps
            subprocess.check_call(["shutdown", "/s", "/t", str(seconds), "/f"], shell=False)
        except Exception as e:
            messagebox.showerror("Failed", f"Failed to schedule shutdown: {e}")
            self.scheduled_epoch = None
            return

        # Start countdown thread
        self.cancel_event.clear()
        self.shutdown_thread = threading.Thread(target=self._countdown_loop, daemon=True)
        self.shutdown_thread.start()

        eta = datetime.datetime.fromtimestamp(self.scheduled_epoch).strftime("%Y-%m-%d %H:%M:%S")
        self.countdown_var.set(f"Shutdown scheduled at {eta} ({seconds} seconds)")
        messagebox.showinfo("Scheduled", f"Windows will shutdown at {eta}")

    def cancel_shutdown(self, update_message=True):
        try:
            subprocess.run(["shutdown", "/a"], shell=False, capture_output=True)
        except Exception:
            pass
        self.cancel_event.set()
        self.scheduled_epoch = None
        if update_message:
            self.countdown_var.set("No shutdown scheduled")

    def _countdown_loop(self):
        while not self.cancel_event.is_set() and self.scheduled_epoch:
            remaining = self.scheduled_epoch - int(time.time())
            if remaining <= 0:
                self.countdown_var.set("Shutting down now...")
                return
            mins, secs = divmod(remaining, 60)
            self.root.after(0, self.countdown_var.set, f"Time remaining: {mins:02d}:{secs:02d}")
            time.sleep(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Ensure running on Windows
    if os.name != 'nt':
        tk.Tk().withdraw()
        messagebox.showerror("Unsupported OS", "This app only works on Windows.")
        sys.exit(1)
    app = ShutdownScheduler()
    app.run()

