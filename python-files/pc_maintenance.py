import os
import psutil
import threading
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Meter
import GPUtil
import time

# --- פונקציות ---
def clean_temp_files():
    temp_dirs = [os.getenv('TEMP'), os.getenv('TMP'), r"C:\Windows\Temp"]
    cleaned_files = 0
    for temp_dir in temp_dirs:
        if temp_dir and os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                        cleaned_files += 1
                    except:
                        pass
    status_label.config(text=f"✅ ניקוי הושלם! נמחקו {cleaned_files} קבצים.")
    root.after(3000, lambda: status_label.config(text=""))

def update_stats():
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_load = gpus[0].load * 100
                gpu_mem = gpus[0].memoryUsed
                gpu_label.config(text=f"GPU: {gpu_load:.1f}% | זיכרון {gpu_mem}MB")
            else:
                gpu_label.config(text="GPU: לא זמין")
        except:
            gpu_label.config(text="GPU: לא זמין")
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp_label.config(text=f"טמפרטורת CPU: {temps['coretemp'][0].current}°C")
            else:
                temp_label.config(text="טמפרטורת CPU: לא זמין")
        except:
            temp_label.config(text="טמפרטורת CPU: לא זמין")

        cpu_meter.configure(amountused=cpu_percent)
        ram_meter.configure(amountused=ram.percent)
        disk_meter.configure(amountused=disk.percent)

# --- Splash Screen ---
splash = tk.Tk()
splash.overrideredirect(True)
splash.geometry("400x200+600+300")
splash.configure(bg="#222")
splash_label = tk.Label(splash, text="🖥️ תחזוקת מחשב", font=("Arial", 24), fg="white", bg="#222")
splash_label.pack(expand=True)

def show_main():
    splash.destroy()
    main_app()

splash.after(2000, show_main)  # מציג את המסך 2 שניות
splash.mainloop()

# --- Main App ---
def main_app():
    global root, cpu_meter, ram_meter, disk_meter, gpu_label, temp_label, status_label
    root = tk.Tk()
    root.title("אפליקציית תחזוקת מחשב")
    root.geometry("500x500")
    style = Style(theme="darkly")

    cpu_meter = Meter(root, metersize=150, amountused=0, metertype="full", subtext="CPU שימוש", bootstyle="info")
    cpu_meter.pack(pady=10)
    ram_meter = Meter(root, metersize=150, amountused=0, metertype="full", subtext="RAM שימוש", bootstyle="warning")
    ram_meter.pack(pady=10)
    disk_meter = Meter(root, metersize=150, amountused=0, metertype="full", subtext="שימוש דיסק", bootstyle="danger")
    disk_meter.pack(pady=10)

    gpu_label = tk.Label(root, text="GPU: טוען...", fg="white", bg="#222")
    gpu_label.pack(pady=5)
    temp_label = tk.Label(root, text="טמפרטורת CPU: טוען...", fg="white", bg="#222")
    temp_label.pack(pady=5)

    status_label = tk.Label(root, text="", fg="lightgreen", bg="#222")
    status_label.pack(pady=5)

    clean_button = tk.Button(root, text="🚀 ניקוי מהיר", command=lambda: threading.Thread(target=clean_temp_files).start(),
                             bg="green", fg="white", font=("Arial", 14))
    clean_button.pack(pady=15)

    threading.Thread(target=update_stats, daemon=True).start()
    root.mainloop()
