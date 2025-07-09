import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import os
import datetime
import threading

SERVER_PATH = r"\\w11700100infra\telediff\app"
LOCAL_PATH = r"C:\\pmf\\rappinst"
LOG_PATH = os.path.join(LOCAL_PATH, "installation_log.txt")

os.makedirs(LOCAL_PATH, exist_ok=True)
if os.path.exists(LOG_PATH):
    os.remove(LOG_PATH)

root = tk.Tk()
root.title("Mise à jour automatique des Postes - CPAM de VESOUL")
root.geometry("900x650")
root.minsize(700, 500)
root.configure(bg="#d0e7ff")  # Bleu clair doux

style = ttk.Style(root)
style.theme_use('clam')

# Boutons bleu avec texte blanc
style.configure("TButton",
                font=("Segoe UI", 11, "bold"),
                padding=6,
                foreground="white",
                background="#1a73e8",
                borderwidth=0)
style.map("TButton",
          background=[('active', '#155ab6'), ('!disabled', '#1a73e8')])

# Checkbox bleu foncé texte
style.configure("TCheckbutton",
                font=("Segoe UI", 11, "bold"),
                background="#d0e7ff",
                foreground="#0d47a1")

# Barre de progression bleu vif
style.configure("Horizontal.TProgressbar",
                thickness=22,
                troughcolor="#a6c8ff",
                background="#1967d2",
                bordercolor="#0b3d91",
                lightcolor="#4285f4",
                darkcolor="#0b3d91")

# Cadre logs bleu foncé bord et fond blanc cassé
frame_logs_bg = "#f9faff"  # blanc cassé
frame_logs_bd = "#0d47a1"  # bleu foncé

frame_logs = tk.LabelFrame(root, text="Journaux d'installation",
                           font=("Segoe UI", 12, "bold"),
                           bg=frame_logs_bg, fg=frame_logs_bd,
                           padx=10, pady=10, bd=3, relief=tk.GROOVE)
frame_logs.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

log_console = tk.Text(frame_logs, height=25, font=("Consolas", 11),
                      bg=frame_logs_bg, fg="#000000", wrap="word",
                      relief=tk.FLAT)
log_console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(frame_logs, command=log_console.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_console.config(yscrollcommand=scrollbar.set, state="disabled")

progress = ttk.Progressbar(root, orient="horizontal", length=860,
                           mode="determinate", style="Horizontal.TProgressbar")
progress.pack(pady=(0, 15))

force_var = tk.BooleanVar()
chk_force = ttk.Checkbutton(root, text="Forcer l'installation (même si PROGRES est ouvert)",
                            variable=force_var)
chk_force.pack(pady=(0, 15))

frame_btn = tk.Frame(root, bg="#d0e7ff")
frame_btn.pack(pady=10)

btn_quit = ttk.Button(frame_btn, text="Quitter", command=root.destroy)
btn_quit.pack(side=tk.RIGHT, padx=10)

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"{timestamp} : {message}"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(full_message + "\n")
    def append_log():
        log_console.config(state="normal")
        log_console.insert(tk.END, full_message + "\n")
        log_console.see(tk.END)
        log_console.config(state="disabled")
    root.after(0, append_log)

def is_process_running(name):
    try:
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8", errors="ignore")
        return name.lower() in output.lower()
    except Exception as e:
        log_message(f"Erreur dans is_process_running : {e}")
        return False

def ensure_progres_closed():
    if force_var.get():
        log_message("Installation forcée par l'utilisateur.")
        return True
    messagebox.showinfo("Vérification requise", "Vérifiez que PROGRES PE et PN sont fermés.")
    while True:
        still_running = []
        if is_process_running("lnpn.exe"):
            still_running.append("PROGRES PN")
        if is_process_running("lnpg.exe"):
            still_running.append("PROGRES PE")

        if still_running:
            retry = messagebox.askretrycancel("Programmes ouverts", f"Encore ouverts : {', '.join(still_running)}")
            if not retry:
                log_message("Installation annulée.")
                return False
        else:
            return True

def scan_apps_to_install():
    apps = []
    today = datetime.datetime.now()
    try:
        folders = os.listdir(SERVER_PATH)
        log_message(f"Scan des dossiers dans {SERVER_PATH}...")
    except Exception as e:
        messagebox.showerror("Erreur", f"Accès serveur impossible : {e}")
        log_message(f"Erreur accès serveur : {e}")
        return []

    for folder in folders:
        app_dir = os.path.join(SERVER_PATH, folder)
        if not os.path.isdir(app_dir):
            continue
        log_message(f"Analyse du dossier : {folder}")
        for file in os.listdir(app_dir):
            if file.lower().endswith(".ini"):
                ini_path = os.path.join(app_dir, file)
                try:
                    with open(ini_path, encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    activate = any("Activate=True" in line for line in lines)
                    date_line = next((line for line in lines if line.startswith("Date=")), None)
                    app_date = datetime.datetime.min
                    if date_line:
                        try:
                            app_date = datetime.datetime.strptime(date_line.split("=")[1].strip(), "%d/%m/%Y")
                        except Exception:
                            pass
                    log_file = os.path.join(LOCAL_PATH, f"{os.path.splitext(file)[0]}.log")
                    if activate and app_date <= today and not os.path.exists(log_file):
                        apps.append(os.path.splitext(file)[0])
                        log_message(f"Application détectée à installer : {os.path.splitext(file)[0]}")
                except Exception as e:
                    log_message(f"Erreur INI ({ini_path}) : {e}")
    log_message(f"Scan terminé, {len(apps)} application(s) trouvée(s) à installer.")
    return apps

def install_apps(apps_to_install):
    if not ensure_progres_closed():
        return
    progress["maximum"] = len(apps_to_install)
    progress["value"] = 0
    for app in apps_to_install:
        app_path = None
        for folder in os.listdir(SERVER_PATH):
            if app.lower() in folder.lower():
                app_path = os.path.join(SERVER_PATH, folder)
                break
        if not app_path:
            log_message(f"Chemin non trouvé pour {app}, installation sautée.")
            progress["value"] += 1
            root.update_idletasks()
            continue
        files = os.listdir(app_path)
        exe = next((f for f in files if f.lower().endswith((".exe", ".msi", ".bat")) and app.lower() in f.lower()), None)
        if exe:
            try:
                exe_path = os.path.join(app_path, exe)
                log_app_path = os.path.join(LOCAL_PATH, f"{app}.log")
                log_message(f"Début installation de {app} avec {exe}")
                if exe.lower().endswith(".msi"):
                    subprocess.run(["msiexec", "/i", exe_path, "/qn", "/norestart"], check=True)
                else:
                    subprocess.run([exe_path, "/S", "/VERYSILENT", "/NORESTART"], check=True)
                log_message(f"Installation réussie : {app}")
                with open(log_app_path, "a", encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.now()} : Installation réussie\n")
            except Exception as e:
                log_message(f"Erreur installation {app} : {e}")
        else:
            log_message(f"Pas de fichier exécutable trouvé pour {app}, installation sautée.")
        progress["value"] += 1
        root.update_idletasks()
    messagebox.showinfo("Terminé", "Installation terminée.")
    root.destroy()

def start_installation():
    apps = scan_apps_to_install()
    if not apps:
        messagebox.showinfo("Information", "Aucune application à installer.")
        root.destroy()
        return
    threading.Thread(target=install_apps, args=(apps,), daemon=True).start()

root.after(1000, start_installation)
root.mainloop()
