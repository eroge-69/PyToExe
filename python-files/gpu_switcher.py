
import tkinter as tk
from tkinter import messagebox
import subprocess

# Hardware IDs
internal_gpu_id = 'PCI\\VEN_10DE&DEV_24DD&SUBSYS_77151558&REV_A1'
external_gpu_id = 'PCI\\VEN_10DE&DEV_2803&SUBSYS_16CF10DE&REV_A1'

def is_external_gpu_connected():
    try:
        result = subprocess.run(['devcon.exe', 'hwids', external_gpu_id], capture_output=True, text=True)
        return external_gpu_id in result.stdout
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Überprüfen der externen GPU: {e}")
        return False

def disable_internal_gpu():
    try:
        subprocess.run(['devcon.exe', 'disable', internal_gpu_id], check=True)
        messagebox.showinfo("Erfolg", "Die interne GPU wurde deaktiviert.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Deaktivieren der internen GPU: {e}")

def check_and_switch():
    if is_external_gpu_connected():
        disable_internal_gpu()
    else:
        messagebox.showinfo("Info", "Die externe GPU ist nicht angeschlossen.")

# GUI
root = tk.Tk()
root.title("GPU Umschalter")

tk.Button(root, text="Jetzt prüfen und umschalten", command=check_and_switch).pack(pady=10)
tk.Button(root, text="Beenden", command=root.quit).pack(pady=10)

root.mainloop()
