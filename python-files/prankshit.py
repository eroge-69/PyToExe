#!/usr/bin/env python3
"""
harmless_spam_prank.py
Safe local-only popup spammer for testing/pranks.
- Each popup auto-closes after `popup_duration` seconds.
- You can stop the spawning at any time with the Stop button.
- There is a safety cap (MAX_POPUPS) to avoid going wild.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import sys

# ---------- CONFIG ----------
MAX_POPUPS = 200         # absolute upper limit (safety)
DEFAULT_COUNT = 30       # default number of popups to create
DEFAULT_INTERVAL = 0.12  # seconds between spawns
POPUP_DURATION = 4.0     # seconds each popup stays before auto-close
POPUP_SIZE = (260, 90)   # width, height of each popup
# ----------------------------

class SpammerApp:
    def __init__(self, root):
        self.root = root
        root.title("Harmless Popup Spammer — local only")
        root.resizable(False, False)

        frm = ttk.Frame(root, padding=12)
        frm.grid(row=0, column=0)

        ttk.Label(frm, text="Message:").grid(row=0, column=0, sticky="w")
        self.msg_var = tk.StringVar(value="YOU ARE A IDIOT (kidding!)")
        ttk.Entry(frm, width=40, textvariable=self.msg_var).grid(row=0, column=1, columnspan=2, pady=4)

        ttk.Label(frm, text="Count:").grid(row=1, column=0, sticky="w")
        self.count_var = tk.IntVar(value=DEFAULT_COUNT)
        ttk.Entry(frm, width=10, textvariable=self.count_var).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Interval (s):").grid(row=2, column=0, sticky="w")
        self.interval_var = tk.DoubleVar(value=DEFAULT_INTERVAL)
        ttk.Entry(frm, width=10, textvariable=self.interval_var).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text=f"Popup duration (s): {POPUP_DURATION}").grid(row=3, column=0, columnspan=3, sticky="w", pady=(6,0))

        # buttons
        self.start_btn = ttk.Button(frm, text="Start Spam", command=self.start_spam)
        self.start_btn.grid(row=4, column=0, pady=10, sticky="w")

        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop_spam, state="disabled")
        self.stop_btn.grid(row=4, column=1, pady=10, sticky="w")

        self.status_lbl = ttk.Label(frm, text="Idle")
        self.status_lbl.grid(row=5, column=0, columnspan=3, sticky="w")

        # control flags
        self._stop_event = threading.Event()
        self._spawn_thread = None
        self._active_popups = set()
        self._popup_lock = threading.Lock()

        # bind ESC to stop quickly
        root.bind("<Escape>", lambda e: self.stop_spam())

    def start_spam(self):
        # validate inputs
        try:
            count = int(self.count_var.get())
            interval = float(self.interval_var.get())
        except Exception:
            self.status_lbl.config(text="Invalid inputs")
            return

        if count < 1:
            self.status_lbl.config(text="Count must be >= 1")
            return

        if count > MAX_POPUPS:
            self.status_lbl.config(text=f"Count capped to {MAX_POPUPS} for safety")
            count = MAX_POPUPS
            self.count_var.set(MAX_POPUPS)

        if interval < 0:
            self.status_lbl.config(text="Interval must be >= 0")
            return

        # disable start, enable stop
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._stop_event.clear()
        self.status_lbl.config(text=f"Spawning {count} popups... (Esc or Stop to cancel)")

        # spawn in separate thread so UI remains responsive
        self._spawn_thread = threading.Thread(target=self._spawn_loop, args=(count, interval), daemon=True)
        self._spawn_thread.start()

    def stop_spam(self):
        self._stop_event.set()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_lbl.config(text="Stopping spawn... (closing active popups)")

        # close all active popups
        with self._popup_lock:
            popups = list(self._active_popups)
        for w in popups:
            try:
                w.destroy()
            except Exception:
                pass

        # small delay to let thread finish
        self.status_lbl.after(300, lambda: self.status_lbl.config(text="Stopped"))

    def _spawn_loop(self, count, interval):
        created = 0
        while created < count and not self._stop_event.is_set():
            # spawn one popup on the Tk main thread
            self.root.after(0, self._create_popup, created + 1)
            created += 1
            time.sleep(interval)
        # done or stopped
        if not self._stop_event.is_set():
            # all spawned, wait for popups to close naturally
            self.status_lbl.after(0, lambda: self.status_lbl.config(text="Spawn complete — waiting for popups to close"))
            # when everything closes, enable start button again
            self._wait_for_popups_then_reset()
        else:
            self.status_lbl.after(0, lambda: self.status_lbl.config(text="Spawn cancelled"))

        # re-enable start/disable stop in case stop wasn't pressed earlier
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _wait_for_popups_then_reset(self):
        def check():
            with self._popup_lock:
                remaining = len(self._active_popups)
            if remaining == 0:
                self.status_lbl.config(text="All popups closed — Idle")
                return
            else:
                self.status_lbl.config(text=f"{remaining} popups active...")
                self.status_lbl.after(400, check)
        check()

    def _create_popup(self, seq):
        # each popup is a small Toplevel window that auto-closes after POPUP_DURATION
        msg = self.msg_var.get()
        w = tk.Toplevel(self.root)
        w.wm_overrideredirect(True)  # no titlebar for more "prank" look
        width, height = POPUP_SIZE
        # random position near screen center (so they don't hide off-screen)
        sw = w.winfo_screenwidth()
        sh = w.winfo_screenheight()
        x = random.randint(max(0, sw//4), min(sw-width, 3*sw//4))
        y = random.randint(max(0, sh//4), min(sh-height, 3*sh//4))
        w.geometry(f"{width}x{height}+{x}+{y}")

        frm = ttk.Frame(w, relief="raised", padding=8)
        frm.pack(fill="both", expand=True)
        lbl = ttk.Label(frm, text=msg, font=("Segoe UI", 11, "bold"))
        lbl.pack(expand=True, fill="both")

        # add a small close button so user can individually close
        close_btn = ttk.Button(frm, text="Close", command=w.destroy)
        close_btn.pack(side="bottom", pady=(6,0))

        # track it
        with self._popup_lock:
            self._active_popups.add(w)

        # ensure it's destroyed after POPUP_DURATION seconds
        def auto_close(win=w):
            time.sleep(POPUP_DURATION)
            try:
                win.destroy()
            except Exception:
                pass

        threading.Thread(target=auto_close, daemon=True).start()

        # when window destroyed, remove from active set
        def on_destroy(event=None, win=w):
            with self._popup_lock:
                self._active_popups.discard(win)

        w.bind("<Destroy>", on_destroy)

# Run app
def main():
    root = tk.Tk()
    app = SpammerApp(root)
    # center small main window
    root.update_idletasks()
    w = 420; h = 190
    sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
