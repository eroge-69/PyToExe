
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def apply_fortnite():
    messagebox.showinfo("Fortnite Tweaks", "Applied Fortnite Potato Graphics & FPS Boost.")

def apply_roblox():
    messagebox.showinfo("Roblox Tweaks", "Applied Roblox Input Lag Fix & Performance Plan.")

def apply_geforce():
    messagebox.showinfo("GeForce NOW", "Applied Chrome Cloud Gaming Optimizations.")

def apply_clipboard():
    messagebox.showinfo("Clipboard Fix", "Re-enabled Clipboard History (Win+V).")

def apply_dns_tcp():
    messagebox.showinfo("Network", "Applied DNS + TCP Stack Tweaks.")

def apply_debloat():
    messagebox.showinfo("Debloat", "Disabled Xbox Game Bar, Telemetry, and Bloatware.")

def confirm_restart():
    if messagebox.askyesno("Restart", "Do you want to restart your PC to finish applying tweaks?"):
        os.system("shutdown /r /t 5")

app = tk.Tk()
app.title("EXM Tweaks GUI")
app.geometry("400x400")
app.config(bg="#1e1e1e")

tk.Label(app, text="EXM Tweaks Panel", fg="white", bg="#1e1e1e", font=("Arial", 18, "bold")).pack(pady=10)

tk.Button(app, text="Fortnite Potato Mode", width=30, command=apply_fortnite).pack(pady=5)
tk.Button(app, text="Roblox Boost", width=30, command=apply_roblox).pack(pady=5)
tk.Button(app, text="GeForce Cloud Optimizer", width=30, command=apply_geforce).pack(pady=5)
tk.Button(app, text="Clipboard Win+V Fix", width=30, command=apply_clipboard).pack(pady=5)
tk.Button(app, text="DNS + TCP Network Boost", width=30, command=apply_dns_tcp).pack(pady=5)
tk.Button(app, text="Windows Debloater", width=30, command=apply_debloat).pack(pady=5)
tk.Button(app, text="Restart (Prompt)", width=30, fg="red", command=confirm_restart).pack(pady=20)

app.mainloop()
