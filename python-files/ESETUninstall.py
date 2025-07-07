import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def uninstall_programs():
    programs_to_uninstall = [
        "ESET Management Agent",
        "ESET Endpoint Antivirus",
        "ESET Inspect Connector"
    ]
    
    total_programs = len(programs_to_uninstall)
    
    progress_bar["maximum"] = total_programs
    
    for idx, program in enumerate(programs_to_uninstall, start=1):
        command = f"echo Y | wmic product where name='{program}' call uninstall /nointeractive"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        progress_bar["value"] = idx
        root.update_idletasks()  # Mettre à jour l'interface graphique
        print(f"{program} désinstallé avec succès.")
    
    messagebox.showinfo("Terminé", "Tous les programmes ont été désinstallés avec succès.")

def show_copyright():
    messagebox.showinfo("Avis de droit d'auteur", copyright_notice)

# Avis de droit d'auteur
copyright_notice = """
Désinstallation ESET - Copyright © [2023] [Wilfried CHEVALIER]
Ce programme est développé en PYTHON [Open Source].
Société PROXIEL
"""

# Création de la fenêtre principale
root = tk.Tk()
root.title("Désinstallation ESET")
root.geometry("300x150")

# Barre de progression
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=20)

# Bouton pour lancer la désinstallation
start_button = tk.Button(root, text="Désinstaller produits ESET", command=uninstall_programs)
start_button.pack()

# Bouton pour afficher l'avis de droit d'auteur
copyright_button = tk.Button(root, text="Avis de droit d'auteur", command=show_copyright)
copyright_button.pack()

root.mainloop()