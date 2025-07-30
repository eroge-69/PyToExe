import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import ttk
import yaml

# --- Load settings.yaml ---
with open("settings.yaml", "r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)

# --- Detect OS ---
def detect_os():
    if settings.get("os_override") != "auto":
        return settings.get("os_override").lower()
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.split("=")[1].strip().replace('"', '')
                        break
        except:
            pass
        if "arch" in distro or "cachyos" in distro:
            return "arch"
        elif "ubuntu" in distro or "debian" in distro:
            return "debian"
    return "unknown"

current_os = detect_os()

# --- GUI ---
root = tk.Tk()
root.title("Cross-platform App Installer")

frame = ttk.Frame(root, padding=10)
frame.grid()

# OS dropdown
os_var = tk.StringVar(value=current_os)
ttk.Label(frame, text="Huidig OS:").grid(column=0, row=0, sticky="w")
os_dropdown = ttk.Combobox(frame, textvariable=os_var, values=["windows", "arch", "debian"], state="readonly")
os_dropdown.grid(column=1, row=0)

# Checkboxes
ttk.Label(frame, text="Beschikbare software:").grid(column=0, row=1, columnspan=2, sticky="w", pady=(10, 0))
app_vars = []
app_info = []

for idx, app in enumerate(settings["apps"]):
    var = tk.BooleanVar()
    cb = ttk.Checkbutton(frame, text=f"{app['name']} ({app['category']})", variable=var)
    cb.grid(column=0, row=idx+2, columnspan=2, sticky="w")
    app_vars.append(var)
    app_info.append(app)

# Install button
def install_selected():
    selected_os = os_var.get()
    for var, app in zip(app_vars, app_info):
        if var.get():
            pkg_name = app["package"].get(selected_os)
            if not pkg_name:
                print(f"[!] Geen pakket gevonden voor {app['name']} op {selected_os}")
                continue
            print(f"[+] Installeren: {app['name']} ({pkg_name})")
            try:
                if selected_os == "windows":
                    subprocess.run(["winget", "install", "--id", pkg_name, "-e", "--silent"], check=True)
                elif selected_os == "arch":
                    subprocess.run(["paru", "-S", "--noconfirm", pkg_name], check=True)
                elif selected_os == "debian":
                    subprocess.run(["sudo", "apt", "install", "-y", pkg_name], check=True)
                else:
                    print(f"[!] Onbekend OS: {selected_os}")
            except Exception as e:
                print(f"[X] Fout bij installeren van {app['name']}: {e}")

ttk.Button(frame, text="Installeer Geselecteerde", command=install_selected).grid(column=0, row=len(app_info)+2, columnspan=2, pady=(10, 0))

root.mainloop()
