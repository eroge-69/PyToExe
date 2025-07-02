
import tkinter as tk
from tkinter import messagebox
import random
import json
import os

stats_file = "stats.txt"
messages = [
    "Bonjour 👋",
    "Tu es génial 💪",
    "Bonne journée ☀️",
    "Python c’est cool 🐍",
    "Surprise 🎉"
]

# Charger ou initialiser les stats
if os.path.exists(stats_file):
    with open(stats_file, "r") as f:
        stats = json.load(f)
else:
    stats = {
        "app_launches": 0,
        "button_clicks": 0,
        "last_message": ""
    }

stats["app_launches"] += 1

def save_stats():
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

def update_stats_label():
    stats_label.config(text=f"App lancée : {stats['app_launches']} fois\n"
                             f"Clics : {stats['button_clicks']}\n"
                             f"Dernier message : {stats['last_message']}")

def show_random_message():
    msg = random.choice(messages)
    messagebox.showinfo("Message", msg)
    stats["button_clicks"] += 1
    stats["last_message"] = msg
    save_stats()
    update_stats_label()

# Création de la fenêtre principale
root = tk.Tk()
root.title("App Aléatoire avec Stats")
root.geometry("350x220")

# Bouton principal
button = tk.Button(root, text="Afficher un message", command=show_random_message, font=("Arial", 12))
button.pack(pady=10)

# Label de stats
stats_label = tk.Label(root, text="", font=("Arial", 10), justify="left")
stats_label.pack(pady=10)

update_stats_label()
save_stats()

root.mainloop()
