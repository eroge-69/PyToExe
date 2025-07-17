import tkinter as tk
import subprocess
import shutil
import os
import sys

def install():
    base_dir = os.path.dirname(sys.argv[0])
    ps1_source = os.path.join(base_dir, "log_backup_configurable.ps1")
    config_source = os.path.join(base_dir, "config.txt")
    xml_source = os.path.join(base_dir, "log_backup_task_15ian_15iul.xml")

    ps1_target = r"C:\Windows\Temp\log_backup.ps1"
    config_target = r"C:\Windows\Temp\config.txt"

    try:
        shutil.copy(ps1_source, ps1_target)
        shutil.copy(config_source, config_target)
    except Exception as e:
        output.set("Eroare copiere: " + str(e))
        return

    try:
        subprocess.run([
            "schtasks", "/Create", "/TN", "Backup.Logs", "/XML", xml_source, "/RU", "", "/F"
        ], check=True, shell=True)
        output.set("Instalare completă cu configurare externă!")
    except subprocess.CalledProcessError as e:
        output.set("Eroare creare task: " + str(e))

root = tk.Tk()
root.title("Backup.Logs - Inspectoratul de Jandarmi Județean Giurgiu")
root.geometry("420x200")

tk.Label(root, text="Inspectoratul de Jandarmi Județean Giurgiu", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(root, text="Backup.Logs", font=("Arial", 12)).pack()

tk.Button(root, text="Install", command=install, width=20).pack(pady=15)
output = tk.StringVar()
tk.Label(root, textvariable=output, fg="green").pack()

root.mainloop()