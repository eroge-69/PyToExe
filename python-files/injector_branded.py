import os
import time
import psutil
import tkinter as tk
from tkinter import filedialog, messagebox

# --- CONFIGURABLE PATHS ---
SCRIPT_FILE = "emerald_script.lua"           # Script to inject
INJECTED_PATH = "Injected.lua"               # Where the game reads injected code
ROBLOX_EXE = "C:/Program Files (x86)/Roblox/Versions/version-*/RobloxPlayerBeta.exe"  # Adjust if needed

# --- HELPERS ---
def find_roblox_process():
    for proc in psutil.process_iter(['pid', 'name']):
        if "RobloxPlayerBeta.exe" in proc.info['name']:
            return True
    return False

def wait_for_roblox():
    print("🔍 Waiting for RobloxPlayerBeta.exe...")
    while not find_roblox_process():
        time.sleep(1)
    print("✅ Roblox found!")

def launch_roblox():
    print("🚀 Launching Roblox...")
    found = False
    for root, dirs, files in os.walk("C:/Program Files (x86)/Roblox/Versions"):
        for file in files:
            if file == "RobloxPlayerBeta.exe":
                roblox_path = os.path.join(root, file)
                os.startfile(roblox_path)
                found = True
                return
    if not found:
        messagebox.showerror("Error", "RobloxPlayerBeta.exe not found.")

def inject_script():
    if not os.path.exists(SCRIPT_FILE):
        messagebox.showerror("Error", f"{SCRIPT_FILE} not found.")
        return
    with open(SCRIPT_FILE, "r", encoding="utf-8") as src:
        script = src.read()
    with open(INJECTED_PATH, "w", encoding="utf-8") as dst:
        dst.write(script)
    log_var.set(f"✅ Injected to {INJECTED_PATH}")
    print("✅ Script injected.")

# --- GUI ---
root = tk.Tk()
root.title("💎 Emerald Injector EX")
root.geometry("520x320")
root.configure(bg="#101010")

tk.Label(root, text="💎 Emerald Injector EX", font=("Arial", 16, "bold"), bg="#101010", fg="#00ffcc").pack(pady=12)
tk.Label(root, text="Injects emerald_script.lua ➜ Injected.lua", font=("Arial", 10), bg="#101010", fg="gray").pack()

tk.Button(root, text="Launch Roblox", command=launch_roblox, bg="#3333aa", fg="white", width=20, height=2).pack(pady=8)
tk.Button(root, text="Inject to Roblox", command=lambda:[wait_for_roblox(), inject_script()],
          bg="#00aa00", fg="white", width=20, height=2).pack(pady=8)

log_var = tk.StringVar()
tk.Label(root, textvariable=log_var, fg="#00ffcc", bg="#101010").pack(pady=10)

root.mainloop()
