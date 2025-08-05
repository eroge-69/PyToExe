import tkinter as tk
import requests

# Ändra till en intern sida som bara fungerar via F5 Tunnel
INTERNAL_URL = "https://myndighetskort.arbetsformedlingen.se/eleg/dist/index.html#!/selfadmin"

def check_connection():
    try:
        response = requests.get(INTERNAL_URL, timeout=3)
        if response.status_code == 200:
            status_label.config(text="✅ Tunnel aktiv", fg="green")
        else:
            status_label.config(text="⚠️ Nåddes men felkod", fg="orange")
    except requests.exceptions.RequestException:
        status_label.config(text="❌ Ingen anslutning", fg="red")

import subprocess
import os

def manual_trigger():
    status_label.config(text="🔄 Startar Machine Tunnel...", fg="blue")
    exe_path = r"C:\WINDOWS\SysWOW64\F5MachineTunnelService.exe"

    if os.path.exists(exe_path):
        try:
            subprocess.Popen([exe_path], shell=True)
            status_label.config(text="✅ Tjänsten försökt startas", fg="green")
        except Exception as e:
            status_label.config(text=f"❌ Fel: {e}", fg="red")
    else:
        status_label.config(text="❌ EXE hittades inte", fg="red")


# GUI-fönster
window = tk.Tk()
window.title("F5 Machine Tunnel Checker")
window.geometry("300x200")

status_label = tk.Label(window, text="Tryck för att kontrollera", font=("Arial", 14))
status_label.pack(pady=20)

check_button = tk.Button(window, text="Kontrollera tunnel", command=check_connection)
check_button.pack(pady=5)

manual_button = tk.Button(window, text="Trigga anslutning", command=manual_trigger)
manual_button.pack(pady=5)

window.mainloop()
