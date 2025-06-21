import tkinter as tk
from tkinter import messagebox
import ctypes
import subprocess
import sys

services = {
    "SysMain": "SysMain (Superfetch)",
    "WSearch": "Windows Search",
    "DiagTrack": "Connected User Experiences and Telemetry",
    "DPS": "Diagnostic Policy Service",
    "TrkWks": "Distributed Link Tracking Client",
    "MapsBroker": "Downloaded Maps Manager",
    "PcaSvc": "Program Compatibility Assistant Service",
    "Fax": "Fax",
    "Spooler": "Print Spooler",
    "RemoteRegistry": "Remote Registry",
    "seclogon": "Secondary Logon",
    "CscService": "Offline Files",
    "WerSvc": "Windows Error Reporting Service",
    "stisvc": "Windows Image Acquisition (WIA)",
    "wisvc": "Windows Insider Service",
    "WbioSrvc": "Windows Biometric Service",
    "bthserv": "Bluetooth Support Service",
    "TermService": "Remote Desktop Services",
    "wuauserv": "Windows Update Service"
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_services(selected_services):
    for svc in selected_services:
        subprocess.call(f"sc stop {svc}", shell=True)
        subprocess.call(f"sc config {svc} start= disabled", shell=True)
    messagebox.showinfo("PS XT Optimize", "Selected services have been disabled.")

def run_gui():
    root = tk.Tk()
    root.title("PS XT Optimize")
    root.geometry("400x600")
    tk.Label(root, text="Select Services to Disable:", font=("Arial", 12, "bold")).pack(pady=10)

    checkboxes = {}
    for svc, name in services.items():
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=name, variable=var, anchor='w', justify='left')
        chk.pack(fill='x', padx=20)
        checkboxes[svc] = var

    def on_disable():
        selected = [svc for svc, var in checkboxes.items() if var.get()]
        if selected:
            disable_services(selected)
        else:
            messagebox.showwarning("No Selection", "Please select at least one service.")

    disable_button = tk.Button(root, text="Disable Selected Services", command=on_disable, bg="red", fg="white")
    disable_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    if is_admin():
        run_gui()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
