import tkinter as tk
import configparser
import random

CONFIG_FILE = "config.ini"

def update_config():
    try:
        min_val = int(entry_min.get())
        max_val = int(entry_max.get())
        
        # Vérif bornes
        if not (0 <= min_val <= 12 and 0 <= max_val <= 12):
            result_label.config(text="⚠️ Valeurs entre 0 et 12 uniquement", fg="red")
            return
        
        if max_val < min_val:
            result_label.config(text="⚠️ Max doit être ≥ Min", fg="red")
            return
        
        # Tirage aléatoire
        random_val = random.randint(min_val, max_val)
        
        # Lire config
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE, encoding="utf-8")
        
        # Modifier la ligne
        config["MISSION"]["lead_plane_count_allied"] = str(random_val)
        
        # Sauvegarde
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
        
        # Affichage dans l'interface
        result_label.config(text=f"✅ Nouvelle valeur : {random_val}", fg="green")
    
    except ValueError:
        result_label.config(text="⚠️ Entrées invalides", fg="red")

# Création de la fenêtre
root = tk.Tk()
root.title("Config Mission Editor")

tk.Label(root, text="Valeur minimale (0-12) :").grid(row=0, column=0, padx=5, pady=5)
entry_min = tk.Entry(root)
entry_min.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Valeur maximale (0-12) :").grid(row=1, column=0, padx=5, pady=5)
entry_max = tk.Entry(root)
entry_max.grid(row=1, column=1, padx=5, pady=5)

btn = tk.Button(root, text="Générer et Modifier", command=update_config)
btn.grid(row=2, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()