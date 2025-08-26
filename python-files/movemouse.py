import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# External dependency for mouse movement:
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False


class MoveMouseApp:
    """
    Tkinter GUI that:
      - Shows a "Start stop timer" toggle button
      - Shows a progress bar that counts DOWN from 30 seconds
      - When it reaches zero, performs a small mouse circle
      - Automatically restarts the countdown while running
    """

    def __init__(self, root):
        # --- Config / constants ---
        self.root = root
        self.root.title("MoveMouse")

        # Countdown settings
        self.total_seconds = 30               # full cycle length
        self.tick_ms = 100                    # update every 100 ms
        self.progress_max = self.total_seconds * (1000 // self.tick_ms)

        # State
        self.running = False                  # is the timer active?
        self.ticks_remaining = self.progress_max
        self.after_job = None                 # handle for scheduled after()

        # --- UI ---
        self.build_ui()

        # Handle window close cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Start/stop toggle button
        self.toggle_btn = ttk.Button(
            container,
            text="Start stop timer",
            command=self.toggle
        )
        self.toggle_btn.grid(row=0, column=0, sticky="ew")

        # Countdown progress bar (counts down from full to zero)
        self.progress = ttk.Progressbar(
            container,
            orient="horizontal",
            mode="determinate",
            maximum=self.progress_max,
            length=320
        )
        self.progress.grid(row=1, column=0, pady=(8, 0), sticky="ew")

        # Set initial progress (full bar)
        self.progress["value"] = self.progress_max

        # Grow horizontally
        container.columnconfigure(0, weight=1)

    # ----------------------------
    # Timer control
    # ----------------------------
    def toggle(self):
        """Start or stop the countdown."""
        if not self.running:
            self.running = True
            self.schedule_tick()
        else:
            self.running = False
            self.cancel_tick()

    def schedule_tick(self):
        """Schedule the next countdown step."""
        if self.after_job is None:
            self.after_job = self.root.after(self.tick_ms, self.on_tick)

    def cancel_tick(self):
        """Cancel a scheduled tick (if any)."""
        if self.after_job is not None:
            try:
                self.root.after_cancel(self.after_job)
            except Exception:
                pass
            self.after_job = None

    def on_tick(self):
        """Run on each tick: update remaining time and progress bar."""
        self.after_job = None  # we're running the scheduled job now

        if not self.running:
            return

        # Decrement remaining "ticks"
        self.ticks_remaining -= 1
        if self.ticks_remaining < 0:
            self.ticks_remaining = 0

        # Update the UI progress bar to show time *remaining*
        self.progress["value"] = self.ticks_remaining

        # If reached zero, trigger the mouse move then reset
        if self.ticks_remaining == 0:
            self.on_zero_reached()
        else:
            # Schedule the next tick if still running
            if self.running:
                self.schedule_tick()

    def on_zero_reached(self):
        """Handle end-of-countdown: draw mouse circle, then reset & continue."""
        # Kick off the mouse move in a background thread so UI stays responsive
        if PYAUTOGUI_AVAILABLE:
            t = threading.Thread(target=self.draw_mouse_circle, daemon=True)
            t.start()
        else:
            # If pyautogui is not installed, inform the user once.
            messagebox.showwarning(
                "pyautogui not available",
                "Mouse movement requires 'pyautogui'.\n\nInstall it with:\n\npip install pyautogui"
            )

        # Reset countdown for next cycle
        self.ticks_remaining = self.progress_max
        self.progress["value"] = self.ticks_remaining

        # Continue running unless user stopped it in the meantime
        if self.running:
            self.schedule_tick()

    # ----------------------------
    # Mouse movement
    # ----------------------------
    def draw_mouse_circle(self):
        """
        Draw a small circle with the mouse around its current position.
        Uses a modest radius and short duration to avoid big jumps.
        """
        try:
            # Capture current mouse position as the circle center
            center_x, center_y = pyautogui.position()

            # Circle parameters (tweak to taste)
            radius = 30               # pixels
            steps = 36                # number of points around the circle
            per_step_duration = 0.01  # seconds per move

            # Optional: reduce failsafe chance (keeps default True)
            # pyautogui.FAILSAFE = True

            for i in range(steps + 1):  # +1 to return close to start
                angle = (2 * math.pi) * (i / steps)
                x = int(center_x + radius * math.cos(angle))
                y = int(center_y + radius * math.sin(angle))
                # Short, smooth move to next point
                pyautogui.moveTo(x, y, duration=per_step_duration)

        except Exception as e:
            # If something goes wrong (permissions, etc), surface it once.
            # Avoid Tk calls from background thread: queue to main thread.
            self.root.after(0, lambda: messagebox.showerror(
                "Mouse move error",
                f"Could not move the mouse:\n{e}"
            ))

    # ----------------------------
    # Cleanup
    # ----------------------------
    def on_close(self):
        """Stop timer and close the app."""
        self.running = False
        self.cancel_tick()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MoveMouseApp(root)
    root.mainloop()
