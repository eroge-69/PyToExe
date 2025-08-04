
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox

def delete_folder_contents(path):
    if not os.path.exists(path):
        return
    for filename in os.listdir(path):
        try:
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)
        except Exception as e:
            print(f"Ошибка удаления {file_path}: {e}")

def clear_temp():
    paths = [
        os.environ.get("TEMP"),
        os.environ.get("TMP"),
        os.path.join(os.environ.get("SystemRoot"), "Temp")
    ]
    for path in paths:
        delete_folder_contents(path)

def clear_software_distribution():
    subprocess.run("net stop wuauserv", shell=True)
    subprocess.run("net stop bits", shell=True)
    delete_folder_contents(r"C:\Windows\SoftwareDistribution\Download")
    subprocess.run("net start wuauserv", shell=True)
    subprocess.run("net start bits", shell=True)

def clear_prefetch():
    delete_folder_contents(r"C:\Windows\Prefetch")

def clear_recycle_bin():
    subprocess.run('PowerShell.exe -Command "Clear-RecycleBin -Force"', shell=True)

def run_cleanup():
    try:
        clear_temp()
        clear_software_distribution()
        clear_prefetch()
        clear_recycle_bin()
        messagebox.showinfo("Успешно", "Очистка завершена!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# GUI
root = tk.Tk()
root.title("Очистка системы")
root.geometry("300x150")
root.resizable(False, False)

button = tk.Button(root, text="Очистить систему", command=run_cleanup, font=("Arial", 12), bg="#4CAF50", fg="white")
button.pack(pady=40)

root.mainloop()
