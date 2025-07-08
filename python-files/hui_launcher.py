import tkinter as tk
import subprocess
import os
import glob

# Finder nyeste Roblox-version
def find_latest_roblox_exe(exe_name):
    base_path = r"C:\Users\Thormod Andersen\AppData\Local\Roblox\Versions"
    try:
        versions = glob.glob(os.path.join(base_path, "version-*"))
        versions.sort(reverse=True)
        for version in versions:
            exe_path = os.path.join(version, exe_name)
            if os.path.exists(exe_path):
                return exe_path
    except Exception as e:
        print(f"Fejl ved Roblox-version: {e}")
    return None

# Stier til spil og apps
apps = {
    "Spore": r"steam://rungameid/17390",
    "Minecraft": r"C:\Users\Thormod Andersen\AppData\Roaming\.minecraft\TLauncher.exe",
    "The Sims 4": r"steam://rungameid/1222670",
    "Garry's Mod": r"steam://rungameid/4000",
    "Steam": r"C:\Program Files (x86)\Steam\steam.exe",
    "Roblox": find_latest_roblox_exe("RobloxPlayerBeta.exe"),
    "Roblox Studio": find_latest_roblox_exe("RobloxStudioBeta.exe"),
    "Mine Filer": r"C:\Users\Thormod Andersen\Documents"
}

# Funktion til at starte programmer
def launch_app(app_path):
    try:
        if app_path.startswith("steam://"):
            os.startfile(app_path)
        elif os.path.isdir(app_path):  # Hvis det er en mappe
            os.startfile(app_path)
        else:
            subprocess.Popen(app_path)
    except Exception as e:
        print(f"Kunne ikke starte {app_path}: {e}")

# GUI
root = tk.Tk()
root.title("🎮 HuiConsol Launcher")
root.geometry("420x550")
root.config(bg="#1e1e1e")

title = tk.Label(root, text="🎮 HuiConsol Launcher", font=("Arial", 20, "bold"), bg="#1e1e1e", fg="white")
title.pack(pady=20)

# Knapper
for name, path in apps.items():
    if path:  # Hvis stien eksisterer
        btn = tk.Button(root, text=name, command=lambda p=path: launch_app(p),
                        width=30, height=2, bg="#333", fg="white", font=("Arial", 12, "bold"))
        btn.pack(pady=5)

# Luk-knap
exit_btn = tk.Button(root, text="Afslut", command=root.destroy,
                     width=30, height=2, bg="#a00", fg="white", font=("Arial", 12, "bold"))
exit_btn.pack(pady=20)

root.mainloop()
