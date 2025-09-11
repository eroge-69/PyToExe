import tkinter as tk
from tkinter import messagebox
import os

# Chemin du fichier INT contenant les contacts
FICHIER_CONTACTS = "contacts.INT"

# Dossier contenant les fichiers .msg
DOSSIER_MSG = r"X:\LOGISTIQUE\75 - TRANSPORT\FICHES COLISAGES (ne pas supprimer)"

def lire_contacts(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return [ligne.strip() for ligne in f if ligne.strip()]
    except FileNotFoundError:
        messagebox.showerror("Erreur", f"Fichier {fichier} introuvable.")
        return []

def ouvrir_msg(nom_contact):
    nom_fichier = f"{nom_contact}.msg"
    chemin_fichier = os.path.join(DOSSIER_MSG, nom_fichier)

    if os.path.exists(chemin_fichier):
        try:
            os.startfile(chemin_fichier)  # Ouvre avec l'application par défaut (Outlook ici)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier :\n{e}")
    else:
        messagebox.showwarning("Fichier manquant", f"Le fichier {nom_fichier} est introuvable dans le dossier.")

def creer_interface():
    fenetre = tk.Tk()
    fenetre.title("Sélecteur de contact - Fiches Colisages")
    fenetre.geometry("400x150")

    tk.Label(fenetre, text="Choisissez un contact :").pack(pady=10)

    contacts = lire_contacts(FICHIER_CONTACTS)
    if not contacts:
        fenetre.destroy()
        return

    contact_selectionne = tk.StringVar(fenetre)
    contact_selectionne.set(contacts[0])  # Valeur par défaut

    menu = tk.OptionMenu(fenetre, contact_selectionne, *contacts)
    menu.pack()

    bouton = tk.Button(fenetre, text="Ouvrir fiche colisage", command=lambda: ouvrir_msg(contact_selectionne.get()))
    bouton.pack(pady=20)

    fenetre.mainloop()

if __name__ == "__main__":
    creer_interface()
