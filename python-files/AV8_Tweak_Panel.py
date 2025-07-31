
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# Define tweak categories and their corresponding script paths
tweaks = {
    "CPU": [
        "CPU/All/CPU.bat",
        "CPU/AMD/amdcpu.bat",
        "CPU/Intel/intel.bat",
        "CPU/Intel/KBoost.bat"
    ],
    "GPU": [
        "GPU/All/all gpu.bat",
        "GPU/AMD/AMD.bat",
        "GPU/AMD/Disable ULPS.reg",
        "GPU/Nvidia/Disable HDCP.bat",
        "GPU/Nvidia/nvidia__4.bat",
        "GPU/Nvidia/Nvidia_1_.bat",
        "GPU/Nvidia/Nvidia_2.bat",
        "GPU/Nvidia/Nvidia3.bat"
    ],
    "Debloat": [
        "Debloat/Disable Printer Features.bat",
        "Debloat/Uninstall-Preinstalled-Apps.bat"
    ],
    "Low Delay": [
        "Low Delay/! Low Delay - RUN ONLY ME.bat"
    ],
    "Cleaner": [
        "Clean/AutoDeleteTemp.bat"
    ],
    "Network": [
        "Network/!Reset Network.bat",
        "Network/#FSE-QOS for Games.bat",
        "Network/AutotuningLevel Disabled (no bufferbloat, lower speed).bat",
        "Network/AutotuningLevel Normal (normal speed, bufferbloat).bat",
        "Network/Disable Internet addons.reg",
        "Network/Disable Internet Probing.reg",
        "Network/Network default.bat",
        "Network/network.bat"
    ],
    "System": [
        "System/AdvancedServices.bat",
        "System/b.bat",
        "System/ClearLogFiles.bat",
        "System/DisableMitigations.bat",
        "System/DWMThreshold.reg",
        "System/IRPStack.reg",
        "System/QOS_Fortnite.bat",
        "System/ResourceSetsMODDED2.reg",
        "System/System.bat",
        "System/Windows.reg"
    ]
}

def run_file(path):
    try:
        ext = os.path.splitext(path)[1].lower()
        full_path = os.path.join(os.path.dirname(sys.argv[0]), path)
        if ext == ".bat" or ext == ".cmd":
            subprocess.run(["powershell", "-Command", f"Start-Process '{full_path}' -Verb runAs"], shell=True)
        elif ext == ".reg":
            subprocess.run(["regedit", "/s", full_path], shell=True)
        else:
            messagebox.showerror("Error", f"Unsupported file type: {ext}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_panel():
    root = tk.Tk()
    root.title("AV8 Tweak Panel")
    root.geometry("600x600")
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for category, scripts in tweaks.items():
        tk.Label(scrollable_frame, text=category, font=("Segoe UI", 12, "bold")).pack(pady=(10, 2))
        for script in scripts:
            btn = tk.Button(scrollable_frame, text=f"Run {os.path.basename(script)}", command=lambda s=script: run_file(s))
            btn.pack(pady=2)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    root.mainloop()

if __name__ == "__main__":
    create_panel()
