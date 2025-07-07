import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import psutil  # pip install psutil

def run_bat(file_name):
    try:
        subprocess.Popen(
            [file_name],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exécuter {file_name}\n\n{e}")
    refresh_status()

def check_process(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and name.lower() in proc.info['name'].lower():
            return True
    return False

def refresh_status():
    apache_running = check_process("httpd.exe")
    mysql_running = check_process("mysqld.exe")

    apache_status = "✅ Apache actif" if apache_running else "❌ Apache arrêté"
    mysql_status = "✅ MySQL actif" if mysql_running else "❌ MySQL arrêté"

    status_label.config(text=f"{apache_status}\n{mysql_status}")

# === Fenêtre principale ===
app = tk.Tk()
app.title("UFDOS Studio Control Panel")
app.geometry("320x230")
app.resizable(False, False)

# === Titre ===
label = tk.Label(app, text="UFDOS STUDIO CMS", font=("Arial", 14, "bold"))
label.pack(pady=10)

# === Boutons de contrôle ===
btn_start = tk.Button(app, text="▶️ Démarrer", width=25, bg="green", fg="white", command=lambda: run_bat("demarer.bat"))
btn_start.pack(pady=5)

btn_stop = tk.Button(app, text="⏹️ Arrêter", width=25, bg="red", fg="white", command=lambda: run_bat("arreter.bat"))
btn_stop.pack(pady=5)

# === Statut ===
status_label = tk.Label(app, text="", font=("Arial", 11), justify="center")
status_label.pack(pady=10)

btn_refresh = tk.Button(app, text="🔄 Rafraîchir le statut", command=refresh_status)
btn_refresh.pack()

refresh_status()  # Statut au démarrage
app.mainloop()
