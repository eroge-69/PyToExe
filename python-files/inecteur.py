import tkinter as tk
from tkinter import messagebox
import pyperclip
import os

# 📁 Nom du fichier cheat
nom_fichier = "cheat.txt"  # Mets ton vrai nom ici si c'est différent

def copier_cheat():
    if not os.path.exists(nom_fichier):
        messagebox.showerror("❌ Erreur", f"Fichier '{nom_fichier}' introuvable.")
        return

    try:
        with open(nom_fichier, "r", encoding="utf-8") as f:
            contenu = f.read()
            pyperclip.copy(contenu)
            messagebox.showinfo("✅ Succès", "Le code du cheat a bien été copié dans le presse-papier !")
    except Exception as e:
        messagebox.showerror("❌ Erreur", f"Impossible de lire le fichier : {e}")

# 🖼️ Interface
fenetre = tk.Tk()
fenetre.title("Midous Copier Auto")
fenetre.geometry("400x200")
fenetre.configure(bg="#111")

label = tk.Label(fenetre, text=f"📂 Fichier détecté : {nom_fichier}", bg="#111", fg="#0f0", font=("Arial", 14))
label.pack(pady=20)

bouton = tk.Button(fenetre, text="📋 Copier le cheat", command=copier_cheat, bg="#00ff99", fg="#000", font=("Arial", 12))
bouton.pack(pady=10)

fenetre.mainloop()
