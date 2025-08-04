import tkinter as tk
from tkinter import messagebox
import psutil
import subprocess
import time
import os
import json

CONFIG_FILE = "config.json"
CS2_APP_ID = "730"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {"cores": "1,4"}
    return {"cores": "1,4"}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def set_affinity(proc, cores):
    try:
        proc.cpu_affinity(cores)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось задать affinity: {e}")
        return False

def run_cs2():
    cores_str = entry.get()
    cores = [int(x) for x in cores_str.split(",") if x.isdigit()]
    if not cores:
        messagebox.showerror("Ошибка", "Введите номера ядер через запятую, например: 1,4")
        return
    save_config({"cores": cores_str})

    try:
        subprocess.Popen(["start", "", f"steam://run/{CS2_APP_ID}"], shell=True)
        messagebox.showinfo("Ожидание", "Запускаем CS2... Ждём 10 секунд для поиска процесса")
        time.sleep(10)

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and "cs2.exe" in proc.info['name'].lower():
                if set_affinity(proc, cores):
                    messagebox.showinfo("Успех", f"CS2 закреплён за ядрами: {cores}")
                return

        messagebox.showerror("Ошибка", "Процесс cs2.exe не найден")
    except Exception as e:
        messagebox.showerror("Ошибка запуска", str(e))

root = tk.Tk()
root.title("CS2 CPU Affinity")

cfg = load_config()

tk.Label(root, text="Ядра для CS2 (через запятую):").pack(pady=5)
entry = tk.Entry(root, width=20)
entry.pack(pady=5)
entry.insert(0, cfg.get("cores", "1,4"))

tk.Button(root, text="Запустить CS2", command=run_cs2).pack(pady=10)

root.mainloop()
