
import time
import threading
import tkinter as tk
from tkinter import messagebox
from pynvml import *
import os

class GPUMonitor:
    def __init__(self):
        nvmlInit()
        self.handle = nvmlDeviceGetHandleByIndex(0)
        self.keep_monitoring = False
        self.inactive_time = 0
        self.active = False
        self.threshold_minutes = 10

    def get_gpu_usage(self):
        util = nvmlDeviceGetUtilizationRates(self.handle)
        return util.gpu

    def monitor(self, status_label, timer_label):
        try:
            self.threshold_minutes = int(threshold_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka menit yang valid.")
            return

        self.keep_monitoring = True
        self.inactive_time = 0
        self.active = False
        total_seconds = self.threshold_minutes * 60

        while self.keep_monitoring:
            usage = self.get_gpu_usage()
            status_label.config(text=f"GPU Usage: {usage}%")

            if usage >= 80:
                self.inactive_time = 0
                self.active = True
            elif self.active:
                self.inactive_time += 1
            else:
                self.inactive_time = 0

            minutes = self.inactive_time // 60
            seconds = self.inactive_time % 60
            timer_label.config(text=f"Timer: {minutes:02}:{seconds:02}")

            if self.inactive_time >= total_seconds:
                print("GPU idle terlalu lama. Mematikan komputer...")
                os.system("shutdown /s /t 1")
                break

            time.sleep(1)

    def stop(self):
        self.keep_monitoring = False
        nvmlShutdown()

def start_monitoring():
    monitor_thread = threading.Thread(
        target=gpu_monitor.monitor, args=(status_label, timer_label), daemon=True
    )
    monitor_thread.start()

app = tk.Tk()
app.title("GPU Render Monitor")
app.geometry("320x200")

gpu_monitor = GPUMonitor()

tk.Label(app, text="GPU RENDER MONITOR", font=("Arial", 14)).pack(pady=5)

tk.Label(app, text="Jeda waktu (menit):").pack()
threshold_entry = tk.Entry(app)
threshold_entry.insert(0, "10")
threshold_entry.pack()

status_label = tk.Label(app, text="GPU Usage: --%", font=("Arial", 12))
status_label.pack(pady=5)

timer_label = tk.Label(app, text="Timer: 00:00", font=("Arial", 12))
timer_label.pack()

tk.Button(app, text="Start Monitoring", command=start_monitoring).pack(pady=10)

app.protocol("WM_DELETE_WINDOW", lambda: (gpu_monitor.stop(), app.destroy()))
app.mainloop()
