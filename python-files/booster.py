
import os
import subprocess
import customtkinter as ctk
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def boost_system():
    logbox.insert("end", "Zatrzymywanie zbędnych usług...\n")
    os.system("sc stop DiagTrack >nul 2>&1")
    os.system("sc stop SysMain >nul 2>&1")
    logbox.insert("end", "Usługi zatrzymane.\n")

    if brave_var.get():
        logbox.insert("end", "Wyłączanie Brave...\n")
        os.system("taskkill /f /im brave.exe >nul 2>&1")

    if bluetooth_var.get():
        logbox.insert("end", "Wyłączanie Bluetooth...\n")
        os.system("net stop bthserv >nul 2>&1")

    logbox.insert("end", "Czyszczenie pamięci podręcznej...\n")
    os.system("del /q/f/s %TEMP%\* >nul 2>&1")

    logbox.insert("end", "Gotowe!\n")

    if selected.get() == "TLauncher":
        path = os.path.expanduser("~\\AppData\\Roaming\\.minecraft\\TLauncher.exe")
        logbox.insert("end", f"Uruchamianie: {path}\n")
        subprocess.Popen(path)
    elif selected.get() == "Roblox":
        path = "C:\\Users\\Skup\\AppData\\Local\\Roblox\\Versions\\version-9bf2d7ce6a0345d5\\RobloxPlayerBeta.exe"
        logbox.insert("end", f"Uruchamianie: {path}\n")
        subprocess.Popen(path)

def start_boost():
    threading.Thread(target=boost_system).start()

app = ctk.CTk()
app.title("MinecraftBooster 20.01 PRO")
app.geometry("600x500")

title = ctk.CTkLabel(app, text="🔥 MinecraftBooster 20.01 PRO 🔥", font=ctk.CTkFont(size=20, weight="bold"))
title.pack(pady=10)

frame = ctk.CTkFrame(app)
frame.pack(pady=10)

brave_var = ctk.BooleanVar()
bluetooth_var = ctk.BooleanVar()
checkbox1 = ctk.CTkCheckBox(frame, text="Zamknij Brave", variable=brave_var)
checkbox1.pack(anchor="w")
checkbox2 = ctk.CTkCheckBox(frame, text="Wyłącz Bluetooth", variable=bluetooth_var)
checkbox2.pack(anchor="w")

selected = ctk.StringVar(value="TLauncher")
radio1 = ctk.CTkRadioButton(app, text="TLauncher", variable=selected, value="TLauncher")
radio1.pack()
radio2 = ctk.CTkRadioButton(app, text="Roblox", variable=selected, value="Roblox")
radio2.pack()

boost_button = ctk.CTkButton(app, text="ZBOOSTUJ MNIE", command=start_boost)
boost_button.pack(pady=10)

logbox = ctk.CTkTextbox(app, height=200, width=580)
logbox.pack(pady=5)

app.mainloop()
