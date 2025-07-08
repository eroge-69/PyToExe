import tkinter as tk
from tkinter import ttk
import time
import threading

# Main app window
root = tk.Tk()
root.title("BRND7N Loader")
root.geometry("500x450")
root.configure(bg="#1e1e1e")

# Styling
style = ttk.Style()
style.configure(
    "TButton",
    padding=6,
    relief="flat",
    background="#333",
    foreground="black",  # ← black button text
    font=('Segoe UI', 10)
)
style.map("TButton", background=[("active", "#444")])

# Fake log area (still green for contrast)
log_text = tk.Text(root, bg="#121212", fg="#00ff00", font=("Courier", 9), width=60, height=12)
log_text.place(x=20, y=250)

def log(msg):
    log_text.insert(tk.END, f"{msg}\n")
    log_text.see(tk.END)

# Feature toggles
features = ["Aimbot", "ESP", "No Recoil", "FOV Changer", "Skin Unlocker", "HWID Spoofer"]
feature_states = {}

def toggle_feature(name):
    state = feature_states.get(name, False)
    feature_states[name] = not state
    log(f"[+] {name} {'ENABLED' if not state else 'DISABLED'}")

# Mode selector
mode_label = tk.Label(root, text="Mode:", bg="#1e1e1e", fg="black", font=("Segoe UI", 10))
mode_label.place(x=20, y=20)

mode_var = tk.StringVar()
mode_dropdown = ttk.Combobox(root, textvariable=mode_var, values=["Legit", "Rage", "Stealth"])
mode_dropdown.current(0)
mode_dropdown.place(x=80, y=20)

# Activate all button
def activate_all():
    for f in features:
        feature_states[f] = True
        log(f"[+] {f} ENABLED")
    log("[*] All features loaded successfully.")

ttk.Button(root, text="Activate All", command=activate_all).place(x=360, y=20)

# Generate feature buttons
for i, feat in enumerate(features):
    ttk.Button(root, text=feat, command=lambda f=feat: toggle_feature(f)).place(x=50 + (i % 2) * 200, y=70 + (i // 2) * 40)

# Fake startup loading animation
def startup_sequence():
    messages = [
        "[*] Initializing BRND7N Loader...",
        "[*] Spoofing HWID...",
        "[*] Injecting Kernel-Level Driver...",
        "[*] Bypassing Anti-Cheat...",
        "[+] Loader Ready. Select features to enable."
    ]
    for msg in messages:
        log(msg)
        time.sleep(1.2)

threading.Thread(target=startup_sequence).start()

root.mainloop()

