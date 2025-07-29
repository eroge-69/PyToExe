
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk

def run_as_admin(commands):
    for cmd in commands:
        try:
            subprocess.run(["powershell", "-Command", f'Start-Process cmd -ArgumentList "/c {cmd}" -Verb RunAs'], shell=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

def uninstall_valorant():
    commands = [
        'taskkill /f /im VALORANT.exe',
        'taskkill /f /im RiotClientServices.exe',
        'sc stop vgc',
        'sc stop vgk',
        'rd /s /q "C:\Riot Games"',
        'rd /s /q "%ProgramData%\Riot Games"',
        'rd /s /q "%AppData%\Riot Games"'
    ]
    run_as_admin(commands)
    messagebox.showinfo("Done", "Valorant Uninstalled")

def uninstall_fortnite():
    commands = [
        'taskkill /f /im FortniteClient-Win64-Shipping.exe',
        'wmic product where "Name like '%Fortnite%'" call uninstall /nointeractive',
        'rd /s /q "C:\Program Files\Epic Games\Fortnite"',
        'rd /s /q "%ProgramData%\Epic"',
        'rd /s /q "%LocalAppData%\EpicGamesLauncher"'
    ]
    run_as_admin(commands)
    messagebox.showinfo("Done", "Fortnite Uninstalled")

def clean_vanguard():
    commands = [
        'sc stop vgc',
        'sc stop vgk',
        'sc delete vgc',
        'sc delete vgk',
        'del /f /q "C:\Windows\System32\drivers\vgc.sys"',
        'del /f /q "C:\Windows\System32\drivers\vgk.sys"',
        'rd /s /q "C:\Program Files\Riot Vanguard"',
        'rd /s /q "%LocalAppData%\Riot Vanguard"'
    ]
    run_as_admin(commands)
    messagebox.showinfo("Done", "Vanguard Cleaned")

def clean_eac():
    commands = [
        'sc stop EasyAntiCheat',
        'sc delete EasyAntiCheat',
        'rd /s /q "C:\Program Files (x86)\EasyAntiCheat"',
        'rd /s /q "%ProgramData%\EasyAntiCheat"',
        'rd /s /q "%LocalAppData%\EasyAntiCheat"'
    ]
    run_as_admin(commands)
    messagebox.showinfo("Done", "Easy Anti-Cheat Cleaned")

def full_clean():
    uninstall_valorant()
    uninstall_fortnite()
    clean_vanguard()
    clean_eac()
    messagebox.showinfo("Done", "Full Clean Completed. Reboot recommended.")

# GUI Setup
app = ThemedTk(theme="black")
app.title("🧹 Game + Anti-Cheat Cleaner")
app.geometry("400x360")
app.resizable(False, False)

style = ttk.Style(app)
style.configure('TButton', font=('Segoe UI', 11), padding=6)

ttk.Label(app, text="Game & Anti-Cheat Cleaner", font=('Segoe UI', 14, 'bold')).pack(pady=15)

ttk.Button(app, text="🗑️ Uninstall Valorant", command=uninstall_valorant).pack(pady=5)
ttk.Button(app, text="🗑️ Uninstall Fortnite", command=uninstall_fortnite).pack(pady=5)
ttk.Button(app, text="🧼 Clean Vanguard (vgc/vgk)", command=clean_vanguard).pack(pady=5)
ttk.Button(app, text="🧼 Clean Easy Anti-Cheat (EAC)", command=clean_eac).pack(pady=5)
ttk.Button(app, text="💣 Full Clean (All)", command=full_clean).pack(pady=10)

ttk.Button(app, text="Exit", command=app.quit).pack(pady=10)

app.mainloop()
