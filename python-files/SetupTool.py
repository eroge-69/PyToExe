
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil

def run_setup():
    new_name = entry.get().strip()
    if not new_name:
        messagebox.showwarning("Hiányzó adat", "Kérlek, add meg az új gépnevet.")
        return

    script_path = os.path.abspath("SetupPostSysprep.ps1")
    command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
    os.environ["CUSTOM_NEW_NAME"] = new_name

    try:
        # Lemásoljuk a szkriptet a Startup mappába
        startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\Windows\Start Menu\Programs\Startup")
        dest_script = os.path.join(startup_path, "SetupPostSysprep.ps1")
        shutil.copyfile(script_path, dest_script)

        subprocess.run(command, check=True)
        messagebox.showinfo("Sysprep fut", "A rendszer leáll. Indítás után automatikusan folytatódik a beállítás.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Hiba", f"Hiba történt: {e}")

root = tk.Tk()
root.title("Gépnév beállítása + Sysprep + AD")
root.geometry("400x150")
root.resizable(False, False)

label = tk.Label(root, text="Add meg az új gépnevet:")
label.pack(pady=(20, 5))

entry = tk.Entry(root, width=40)
entry.pack()

start_button = tk.Button(root, text="Indítás", command=run_setup)
start_button.pack(pady=10)

root.mainloop()
