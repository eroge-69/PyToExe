import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

def join_domain():
    """Fonction exécutée dans un thread pour ne pas bloquer l'UI."""
    join_btn.config(state="disabled")
    progress.start()

    domain = domain_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    ou_path = ou_entry.get()
    restart = restart_var.get()
    new_name = name_entry.get().strip()

    if not domain or not user or not password:
        messagebox.showerror("Erreur", "Veuillez remplir le domaine, l'utilisateur et le mot de passe")
        join_btn.config(state="normal")
        progress.stop()
        return

    try:
        # Renommer l'ordinateur si un nom est fourni
        if new_name:
            rename_cmd = [
                "powershell",
                "-Command",
                f"Rename-Computer -NewName '{new_name}' -Force -PassThru"
            ]
            subprocess.run(rename_cmd, capture_output=True, text=True)

        # Joindre le domaine
        command = [
            "powershell",
            "-Command",
            f"Add-Computer -DomainName {domain} -Credential "
            f"(New-Object System.Management.Automation.PSCredential('{domain}\\{user}', "
            f"(ConvertTo-SecureString '{password}' -AsPlainText -Force))) -Force"
        ]

        if ou_path:
            command[-1] += f" -OUPath '{ou_path}'"

        if restart:
            command[-1] += " -Restart"

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            messagebox.showinfo("Succès", "L’ordinateur a été renommé et ajouté au domaine avec succès.")
        else:
            messagebox.showerror("Erreur", f"Erreur lors de l’ajout au domaine :\n{result.stderr}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")
    finally:
        join_btn.config(state="normal")
        progress.stop()

def start_thread():
    threading.Thread(target=join_domain, daemon=True).start()

# Fenêtre principale
root = tk.Tk()
root.title("Joindre un domaine Windows")
root.geometry("480x380")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=5)

# Labels et entrées
ttk.Label(frame, text="Nom du domaine:").grid(row=0, column=0, sticky="w", pady=5)
domain_entry = ttk.Entry(frame, width=35)
domain_entry.grid(row=0, column=1, pady=5)

ttk.Label(frame, text="Utilisateur:").grid(row=1, column=0, sticky="w", pady=5)
user_entry = ttk.Entry(frame, width=35)
user_entry.grid(row=1, column=1, pady=5)

ttk.Label(frame, text="Mot de passe:").grid(row=2, column=0, sticky="w", pady=5)
password_entry = ttk.Entry(frame, width=35, show="*")
password_entry.grid(row=2, column=1, pady=5)

ttk.Label(frame, text="OU (optionnel):").grid(row=3, column=0, sticky="w", pady=5)
ou_entry = ttk.Entry(frame, width=35)
ou_entry.grid(row=3, column=1, pady=5)

ttk.Label(frame, text="Nouveau nom de l'ordinateur (optionnel):").grid(row=4, column=0, sticky="w", pady=5)
name_entry = ttk.Entry(frame, width=35)
name_entry.grid(row=4, column=1, pady=5)

# Redémarrage automatique
restart_var = tk.BooleanVar()
restart_check = ttk.Checkbutton(frame, text="Redémarrer après ajout", variable=restart_var)
restart_check.grid(row=5, column=0, columnspan=2, pady=5)

# Bouton et barre de progression
join_btn = ttk.Button(frame, text="Joindre le domaine", command=start_thread)
join_btn.grid(row=6, column=0, columnspan=2, pady=15)

progress = ttk.Progressbar(frame, mode="indeterminate")
progress.grid(row=7, column=0, columnspan=2, sticky="ew")

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=2)

root.mainloop()
