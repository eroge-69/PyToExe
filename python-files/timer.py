import tkinter as tk
from datetime import datetime, timedelta
import time

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Timer")
        self.root.attributes("-topmost", True)  # Always on top

        self.timer_running = False
        self.end_time = None

        # UI Elements
        self.time_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.time_label.pack(pady=5)

        self.timer_label = tk.Label(root, text="00:00", font=("Helvetica", 36))
        self.timer_label.pack(pady=10)

        self.end_time_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.end_time_label.pack(pady=5)

        self.start_25_btn = tk.Button(root, text="Start 25-min Block", command=lambda: self.start_timer(25))
        self.start_25_btn.pack(side="left", padx=10, pady=10)

        self.start_5_btn = tk.Button(root, text="Start 5-min Block", command=lambda: self.start_timer(5))
        self.start_5_btn.pack(side="right", padx=10, pady=10)

        self.update_clock()

    def update_clock(self):
        now = datetime.now()
        self.time_label.config(text=f"Now: {now.strftime('%H:%M:%S')}")

        if self.timer_running and self.end_time:
            remaining = self.end_time - now
            if remaining.total_seconds() > 0:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            else:
                self.timer_label.config(text="00:00")
                self.timer_running = False
                self.end_time_label.config(text="Timer finished!")

        self.root.after(1000, self.update_clock)

    def start_timer(self, minutes):
        self.end_time = datetime.now() + timedelta(minutes=minutes)
        self.timer_running = True
        self.end_time_label.config(text=f"Ends at: {self.end_time.strftime('%H:%M:%S')}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
