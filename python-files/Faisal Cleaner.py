import os
import shutil
import ctypes
import psutil
import time
import tkinter as tk
from tkinter import messagebox, ttk

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
        return False

def clean_temp():
    temp = os.getenv("TEMP")
    shutil.rmtree(temp, ignore_errors=True)
    os.makedirs(temp, exist_ok=True)
    log("Temp files cleaned.")

def clean_prefetch():
    prefetch = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Prefetch")
    shutil.rmtree(prefetch, ignore_errors=True)
    os.makedirs(prefetch, exist_ok=True)
    log("Prefetch cleaned.")

def clean_windows_update():
    os.system("net stop wuauserv")
    time.sleep(1)
    shutil.rmtree("C:\\Windows\\SoftwareDistribution\\Download", ignore_errors=True)
    os.makedirs("C:\\Windows\\SoftwareDistribution\\Download", exist_ok=True)
    os.system("net start wuauserv")
    log("Windows Update cache cleaned.")

def clean_browser_cache():
    localappdata = os.getenv("LOCALAPPDATA")
    chrome_cache = os.path.join(localappdata, "Google\\Chrome\\User Data\\Default\\Cache")
    shutil.rmtree(chrome_cache, ignore_errors=True)
    os.makedirs(chrome_cache, exist_ok=True)
    log("Browser cache cleaned.")

def clean_recycle_bin():
    os.system("PowerShell.exe -Command Clear-RecycleBin -Force")
    log("Recycle Bin cleaned.")

def clean_everything():
    progress.start()
    log("Cleaning started...")
    clean_temp()
    clean_prefetch()
    clean_windows_update()
    clean_browser_cache()
    clean_recycle_bin()
    log("All cleaning complete.")
    progress.stop()
    messagebox.showinfo("Done", "All tasks finished!")

def optimize_startup():
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v MyCleaner /t REG_SZ /d "" /f')
    log("Startup optimized.")

def boost_ram():
    os.system("EmptyStandbyList.exe workingsets")
    log("RAM Boosted.")

def log(text):
    output.insert(tk.END, text + "\n")
    output.see(tk.END)

if not run_as_admin():
    exit()

# GUI setup
root = tk.Tk()
root.title("HP Cleaner by Faisal Ahmed")
root.geometry("500x400")

label = tk.Label(root, text="HP Cleaner", font=("Arial", 18, "bold"), fg="green")
label.pack(pady=10)

btn1 = tk.Button(root, text="Clean Everything", command=clean_everything, bg="lightgreen")
btn1.pack(pady=5)

btn2 = tk.Button(root, text="Optimize Startup", command=optimize_startup)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="Boost RAM", command=boost_ram)
btn3.pack(pady=5)

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(pady=10, fill=tk.X, padx=20)

output = tk.Text(root, height=10)
output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
