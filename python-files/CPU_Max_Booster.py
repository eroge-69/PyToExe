
import tkinter as tk
import subprocess
import psutil
import os

def boost_and_launch():
    try:
        subprocess.run(["reg", "add", r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management",
                        "/v", "LargeSystemCache", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
        subprocess.run(["reg", "add", r"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
                        "/v", "NetworkThrottlingIndex", "/t", "REG_DWORD", "/d", "4294967295", "/f"], check=True)
        subprocess.run(["reg", "add", r"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
                        "/v", "SystemResponsiveness", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
        fortnite_path = r"D:\\games\\Fortnite\\FortniteGame\\Binaries\\Win64\\FortniteClient-Win64-Shipping.exe"
        if os.path.exists(fortnite_path):
            subprocess.Popen(fortnite_path)
            status_label.config(text="🎮 Fortnite launched with Boost!")
        else:
            status_label.config(text="❌ Fortnite path not found.")
    except Exception as e:
        status_label.config(text=f"❌ Boost Failed: {e}")

def reset_settings():
    try:
        subprocess.run(["reg", "add", r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management",
                        "/v", "LargeSystemCache", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
        subprocess.run(["reg", "add", r"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
                        "/v", "NetworkThrottlingIndex", "/t", "REG_DWORD", "/d", "10", "/f"], check=True)
        subprocess.run(["reg", "add", r"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile",
                        "/v", "SystemResponsiveness", "/t", "REG_DWORD", "/d", "20", "/f"], check=True)
        status_label.config(text="🔁 Settings Reset.")
    except Exception as e:
        status_label.config(text=f"❌ Reset Failed: {e}")

def update_stats():
    usage = psutil.cpu_percent(interval=1)
    freq = psutil.cpu_freq()
    cores = psutil.cpu_count(logical=False)
    threads = psutil.cpu_count(logical=True)
    stat_text = f"Usage: {usage}% | Speed: {round(freq.current, 2)} MHz\nCores: {cores} | Threads: {threads}"
    stats_label.config(text=stat_text)
    window.after(2000, update_stats)

window = tk.Tk()
window.title("CPU Max Booster")
window.geometry("400x320")

tk.Label(window, text="CPU Max Booster", font=("Arial", 14)).pack(pady=10)
tk.Button(window, text="🎮 Boost & Launch Fortnite", font=("Arial", 12), command=boost_and_launch).pack(pady=5)
tk.Button(window, text="🔁 Reset to Normal", font=("Arial", 12), command=reset_settings).pack(pady=5)

status_label = tk.Label(window, text="", font=("Arial", 11))
status_label.pack(pady=10)

stats_label = tk.Label(window, text="", font=("Consolas", 10))
stats_label.pack(pady=10)

update_stats()
window.mainloop()
