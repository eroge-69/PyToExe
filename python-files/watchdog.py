import tkinter as tk
from tkinter import messagebox
import threading
import time
import subprocess

class WatchdogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Still Watching Monitor")
        self.root.geometry("320x200")
        self.running = False
        self.thread = None

        self.label = tk.Label(root, text="Press 'Run' to start monitoring.")
        self.label.pack(pady=10)

        # Timeout input in minutes
        self.timeout_label = tk.Label(root, text="Timeout (minutes):")
        self.timeout_label.pack()
        self.timeout_entry = tk.Entry(root)
        self.timeout_entry.insert(0, "1")  # Default timeout 1 minute
        self.timeout_entry.pack()

        self.run_button = tk.Button(root, text="Run", command=self.start_monitoring)
        self.run_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def start_monitoring(self):
        try:
            self.timeout_minutes = int(self.timeout_entry.get())
            if self.timeout_minutes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Timeout", "Please enter a positive number for the timeout in minutes.")
            return

        self.timeout_seconds = self.timeout_minutes * 60  # Convert minutes to seconds

        if not self.running:
            self.running = True
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.thread.start()
            self.label.config(text="Monitoring started...")

    def stop_monitoring(self):
        self.running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.label.config(text="Monitoring stopped.")

    def monitor_loop(self):
        while self.running:
            for _ in range(3600):  # wait 1 hour, checking every second
                if not self.running:
                    return
                time.sleep(1)
            if self.running:
                self.ask_user()

    def ask_user(self):
        responded = [False]

        def on_timeout():
            if not responded[0]:
                popup.destroy()
                shutdown()

        def on_yes():
            responded[0] = True
            popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.title("Still Watching?")
        popup.geometry("300x100")
        popup.attributes("-topmost", True)

        tk.Label(popup, text="Are you still watching?").pack(pady=10)
        tk.Button(popup, text="Yes", command=on_yes).pack()

        timer = threading.Timer(self.timeout_seconds, on_timeout)  # Timeout in seconds
        timer.start()

        popup.mainloop()
        timer.cancel()

def shutdown():
    subprocess.call("shutdown /s /t 0", shell=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = WatchdogApp(root)
    root.mainloop()
