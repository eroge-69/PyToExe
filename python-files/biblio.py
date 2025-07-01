import tkinter as tk
from tkinter import messagebox
from tkinter.simpledialog import askstring
import json
import os

class BibliothequeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de gestion de bibliothèque")
        self.root.geometry("800x600")
        self.root.config(bg="#f0f0f0")

        # Chargement des livres depuis un fichier JSON
        self.bibliotheque = self.charger_livres()

        # Créer les widgets
        self.create_widgets()

    def create_widgets(self):
        # Titre de l'application
        self.title_label = tk.Label(self.root, text="Gestion de bibliothèque", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#000000")
        self.title_label.grid(row=0, column=0, columnspan=4, pady=20)

        # Frame pour ajouter un livre
        self.add_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.add_frame.grid(row=1, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

        # Titre
        self.titre_label = tk.Label(self.add_frame, text="Titre", font=("Arial", 12), bg="#f0f0f0")
        self.titre_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.titre_entry = tk.Entry(self.add_frame, width=40)
        self.titre_entry.grid(row=0, column=1, padx=10, pady=5)

        # Auteur
        self.auteur_label = tk.Label(self.add_frame, text="Auteur", font=("Arial", 12), bg="#f0f0f0")
        self.auteur_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.auteur_entry = tk.Entry(self.add_frame, width=40)
        self.auteur_entry.grid(row=1, column=1, padx=10, pady=5)

        # Année de publication
        self.annee_label = tk.Label(self.add_frame, text="Année de publication", font=("Arial", 12), bg="#f0f0f0")
        self.annee_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.annee_entry = tk.Entry(self.add_frame, width=40)
        self.annee_entry.grid(row=2, column=1, padx=10, pady=5)

        # Bouton pour ajouter un livre
        self.add_button = tk.Button(self.add_frame, text="Ajouter un livre", command=self.ajouter_livre, bg="#0277bd", fg="white", font=("Arial", 12))
        self.add_button.grid(row=3, columnspan=2, pady=10)

        # Frame pour afficher et gérer les livres
        self.manage_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.manage_frame.grid(row=2, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

        # Liste des livres avec scrollbar
        self.books_listbox_frame = tk.Frame(self.manage_frame, bg="#f0f0f0")
        self.books_listbox_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.books_listbox = tk.Listbox(self.books_listbox_frame, width=60, height=15, font=("Arial", 12))
        self.books_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self.books_listbox_frame, orient="vertical", command=self.books_listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.books_listbox.config(yscrollcommand=self.scrollbar.set)

        # Frame pour la recherche avancée et les boutons en haut à droite
        self.action_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.action_frame.grid(row=0, column=4, rowspan=3, pady=10, padx=10, sticky="nsew")

        # Recherche avancée
        self.search_label = tk.Label(self.action_frame, text="Recherche avancée", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.search_label.grid(row=0, column=0, padx=10, pady=10)

        # Recherche par titre
        self.search_titre_label = tk.Label(self.action_frame, text="Titre", font=("Arial", 12), bg="#f0f0f0")
        self.search_titre_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.search_titre_entry = tk.Entry(self.action_frame, width=20)
        self.search_titre_entry.grid(row=1, column=1, padx=10, pady=5)

        # Recherche par auteur
        self.search_auteur_label = tk.Label(self.action_frame, text="Auteur", font=("Arial", 12), bg="#f0f0f0")
        self.search_auteur_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.search_auteur_entry = tk.Entry(self.action_frame, width=20)
        self.search_auteur_entry.grid(row=2, column=1, padx=10, pady=5)

        # Recherche par année
        self.search_annee_label = tk.Label(self.action_frame, text="Année", font=("Arial", 12), bg="#f0f0f0")
        self.search_annee_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.search_annee_entry = tk.Entry(self.action_frame, width=20)
        self.search_annee_entry.grid(row=3, column=1, padx=10, pady=5)

        # Bouton de recherche
        self.search_button = tk.Button(self.action_frame, text="Rechercher", command=self.rechercher_livre, bg="#0277bd", fg="white", font=("Arial", 12))
        self.search_button.grid(row=4, columnspan=2, pady=10)

        # Bouton pour afficher tous les livres
        self.show_button = tk.Button(self.action_frame, text="Afficher tous les livres", command=self.afficher_livres, bg="#0277bd", fg="white", font=("Arial", 12))
        self.show_button.grid(row=5, columnspan=2, pady=10)

        # Bouton pour supprimer un livre sélectionné
        self.delete_button = tk.Button(self.action_frame, text="Supprimer le livre sélectionné", command=self.supprimer_livre, bg="#f4511e", fg="white", font=("Arial", 12))
        self.delete_button.grid(row=6, columnspan=2, pady=10)

        # Bouton pour modifier un livre sélectionné
        self.edit_button = tk.Button(self.action_frame, text="Modifier le livre sélectionné", command=self.modifier_livre, bg="#FFA500", fg="white", font=("Arial", 12))
        self.edit_button.grid(row=7, columnspan=2, pady=10)

        # Configurer les colonnes et les lignes pour qu'elles s'étendent
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=0)  # Colonne pour les boutons

    def ajouter_livre(self):
        """ Ajouter un livre à la bibliothèque """
        titre = self.titre_entry.get()
        auteur = self.auteur_entry.get()
        annee = self.annee_entry.get()

        livre = {"titre": titre, "auteur": auteur, "annee": annee}
        self.bibliotheque.append(livre)
        self.titre_entry.delete(0, tk.END)
        self.auteur_entry.delete(0, tk.END)
        self.annee_entry.delete(0, tk.END)
        messagebox.showinfo("Succès", f"Le livre '{titre}' a été ajouté.")
        self.afficher_livres()
        self.sauvegarder_livres()

    def modifier_livre(self):
        """ Modifier un livre sélectionné """
        try:
            selected_book_index = self.books_listbox.curselection()[0]  # Récupérer l'index du livre sélectionné
            selected_book = self.books_listbox.get(selected_book_index)  # Récupérer les détails du livre sélectionné
            titre = selected_book.split(' | ')[0]  # Extraire le titre du livre

            # Chercher le livre dans la bibliothèque
            for livre in self.bibliotheque:
                if livre['titre'] == titre:
                    # Demander les nouvelles informations
                    nouveau_titre = askstring("Modifier le titre", "Nouveau titre:", initialvalue=livre['titre'])
                    if not nouveau_titre:
                        break

                    nouvel_auteur = askstring("Modifier l'auteur", "Nouvel auteur:", initialvalue=livre['auteur'])
                    if not nouvel_auteur:
                        break

                    nouvelle_annee = askstring("Modifier l'année", "Nouvelle année de publication:", initialvalue=livre['annee'])
                    if not nouvelle_annee:
                        break

                    # Mettre à jour les informations
                    livre['titre'] = nouveau_titre
                    livre['auteur'] = nouvel_auteur
                    livre['annee'] = nouvelle_annee

                    messagebox.showinfo("Succès", f"Le livre '{nouveau_titre}' a été modifié.")
                    self.afficher_livres()
                    self.sauvegarder_livres()
                    break

        except IndexError:
            messagebox.showwarning("Attention", "Veuillez sélectionner un livre à modifier.")

    def supprimer_livre(self):
        """ Supprimer un livre de la bibliothèque """
        try:
            selected_book_index = self.books_listbox.curselection()[0]  # Récupérer l'index du livre sélectionné
            selected_book = self.books_listbox.get(selected_book_index)  # Récupérer les détails du livre sélectionné
            titre = selected_book.split(' | ')[0]  # Extraire le titre du livre

            # Supprimer le livre de la liste des livres
            for livre in self.bibliotheque:
                if livre['titre'] == titre:
                    self.bibliotheque.remove(livre)
                    break

            self.afficher_livres()
            messagebox.showinfo("Succès", f"Le livre '{titre}' a été supprimé.")
            self.sauvegarder_livres()
        except IndexError:
            messagebox.showwarning("Attention", "Veuillez sélectionner un livre à supprimer.")

    def rechercher_livre(self):
        """ Rechercher un livre avec des critères avancés """
        search_titre = self.search_titre_entry.get().lower()
        search_auteur = self.search_auteur_entry.get().lower()
        search_annee = self.search_annee_entry.get()

        results = []

        # Recherche par titre
        if search_titre:
            results = [livre for livre in self.bibliotheque if search_titre in livre['titre'].lower()]
        
        # Recherche par auteur
        if search_auteur:
            results = [livre for livre in results if search_auteur in livre['auteur'].lower()]

        # Recherche par année
        if search_annee:
            if search_annee.isdigit():
                results = [livre for livre in results if search_annee == livre['annee']]
            else:
                messagebox.showwarning("Attention", "L'année doit être un nombre.")
                return

        if not results:
            messagebox.showerror("Résultat", "Aucun livre trouvé.")
        else:
            self.books_listbox.delete(0, tk.END)
            for livre in results:
                self.books_listbox.insert(tk.END, f"{livre['titre']} | {livre['auteur']} | {livre['annee']}")

    def afficher_livres(self):
        """ Afficher tous les livres de la bibliothèque """
        self.books_listbox.delete(0, tk.END)
        if not self.bibliotheque:
            messagebox.showinfo("Info", "Aucun livre dans la bibliothèque.")
        else:
            for livre in self.bibliotheque:
                self.books_listbox.insert(tk.END, f"{livre['titre']} | {livre['auteur']} | {livre['annee']}")

    def sauvegarder_livres(self):
        """ Sauvegarder les livres dans un fichier JSON """
        with open("bibliotheque livres.json", "w") as f:
            json.dump(self.bibliotheque, f)

    def charger_livres(self):
        """ Charger les livres depuis un fichier JSON """
        if os.path.exists("bibliotheque livres.json"):
            with open("bibliotheque livres.json", "r") as f:
                return json.load(f)
        return []

# Créer la fenêtre principale
root = tk.Tk()

# Créer une instance de l'application
app = BibliothequeApp(root)

# Démarrer l'application
root.mainloop()
