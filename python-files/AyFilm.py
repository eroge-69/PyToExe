import tkinter as tk
from tkinter import ttk, messagebox
import requests
import time
import threading

# Remplacez "VOTRE_CLE_API" par votre propre cl� API TMDB
API_KEY = 'VOTRE_CLE_API'
BASE_URL = 'https://api.themoviedb.org/3/search/movie'
POPULAR_URL = 'https://api.themoviedb.org/3/movie/popular'

# Fonction pour rechercher des films sur TMDB avec une simulation de t�l�chargement
def rechercher_film():
    # R�cup�rer les donn�es des champs
    query = entry_recherche.get()
    genre = combo_genre.get()
    annee = entry_annee.get()
    note_min = entry_note_min.get()

    # V�rification des donn�es
    if not query:
        messagebox.showwarning("Erreur", "Veuillez entrer un titre de film.")
        return

    # Masquer les r�sultats pr�c�dents et afficher la barre de progression
    listbox_resultats.delete(0, tk.END)
    barre_progression.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    bouton_rechercher.config(state=tk.DISABLED)
    bouton_telecharger.config(state=tk.DISABLED)

    # Param�tres de recherche avec les filtres
    params = {
        'api_key': API_KEY,
        'query': query,
        'language': 'fr-FR',
        'page': 1,
        'year': annee if annee else None,
        'vote_average.gte': note_min if note_min else None,
    }

    if genre != "Tous les genres":
        params['with_genres'] = genre

    # Lancer la recherche en parall�le
    threading.Thread(target=simuler_telechargement, args=(params,)).start()

# Fonction pour simuler le t�l�chargement et effectuer la recherche des films
def simuler_telechargement(params):
    # Simulation de t�l�chargement (en faisant une pause)
    for i in range(101):
        time.sleep(0.05)  # Pause pour simuler un t�l�chargement
        barre_progression['value'] = i
        root.update_idletasks()  # Mise � jour de l'interface pour afficher la progression

    # Requ�te TMDB pour rechercher les films
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # V�rifie si la requ�te est r�ussie (code 200)
        data = response.json()

        # Mettre � jour l'interface avec les r�sultats
        if data['results']:
            afficher_resultats(data['results'])
        else:
            messagebox.showerror("Erreur 404", f"Aucun film trouv� avec ces crit�res.")
            
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur de connexion", f"Une erreur est survenue lors de la connexion � TMDB : {e}")
    
    # R�activer le bouton apr�s la recherche
    bouton_rechercher.config(state=tk.NORMAL)
    bouton_telecharger.config(state=tk.NORMAL)
    barre_progression.grid_forget()

# Fonction pour afficher les r�sultats dans la liste
def afficher_resultats(films):
    # Effacer les r�sultats pr�c�dents
    listbox_resultats.delete(0, tk.END)

    for film in films:
        titre = film['title']
        date_sortie = film['release_date'][:4]  # Prend juste l'ann�e
        listbox_resultats.insert(tk.END, f"{titre} ({date_sortie})")

    # Afficher les d�tails du premier film trouv�
    afficher_details_film(films[0])

# Fonction pour afficher les d�tails du film s�lectionn�
def afficher_details_film(film):
    label_titre.config(text=f"Titre: {film['title']}")
    label_sortie.config(text=f"Date de sortie: {film['release_date']}")
    label_resume.config(text=f"R�sum�: {film['overview']}")

    poster_url = f"https://image.tmdb.org/t/p/w500{film['poster_path']}" if film['poster_path'] else None
    if poster_url:
        img_data = requests.get(poster_url).content
        img = tk.PhotoImage(data=img_data)
        label_image.config(image=img)
        label_image.image = img  # Garder une r�f�rence de l'image
    else:
        label_image.config(image='')

# Fonction pour r�cup�rer et afficher les films populaires
def afficher_films_populaires():
    params = {'api_key': API_KEY, 'language': 'fr-FR', 'page': 1}
    try:
        response = requests.get(POPULAR_URL, params=params)
        response.raise_for_status()
        data = response.json()
        afficher_resultats(data['results'])
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue lors de la r�cup�ration des films populaires : {e}")

# Cr�ation de la fen�tre principale
root = tk.Tk()
root.title("AyFilm")
root.geometry("600x600")
root.config(bg="#f2f2f2")  # Fond clair

# Style du texte et des composants
font_principal = ('SF Pro Display Bold', 12)
font_boutons = ('SF Pro Display Bold', 12, 'bold')
couleur_boutons = "#4CAF50"  # Vert
couleur_boutons_hover = "#45a049"  # Un vert un peu plus fonc�

# Barre de recherche
label_recherche = tk.Label(root, text="Recherche de films:", font=('SF Pro Display Bold', 14), bg="#f2f2f2", fg="#333")
label_recherche.grid(row=0, column=0, padx=10, pady=20, sticky='w')

entry_recherche = tk.Entry(root, font=font_principal, width=40)
entry_recherche.grid(row=1, column=0, padx=10, pady=5, columnspan=3)

# Filtre par genre
label_genre = tk.Label(root, text="Genre:", font=font_principal, bg="#f2f2f2", fg="#333")
label_genre.grid(row=2, column=0, padx=10, pady=10, sticky="w")
genres = ["Tous les genres", "Action", "Com�die", "Drame", "Romance", "Horreur", "Science-fiction"]
combo_genre = ttk.Combobox(root, values=genres, state="readonly", font=font_principal)
combo_genre.set("Tous les genres")
combo_genre.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Filtre par ann�e
label_annee = tk.Label(root, text="Ann�e de sortie (facultatif):", font=font_principal, bg="#f2f2f2", fg="#333")
label_annee.grid(row=3, column=0, padx=10, pady=10, sticky="w")

entry_annee = tk.Entry(root, font=font_principal, width=10)
entry_annee.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Filtre par note minimale
label_note_min = tk.Label(root, text="Note minimale (facultatif):", font=font_principal, bg="#f2f2f2", fg="#333")
label_note_min.grid(row=4, column=0, padx=10, pady=10, sticky="w")

entry_note_min = tk.Entry(root, font=font_principal, width=10)
entry_note_min.grid(row=4, column=1, padx=10, pady=10, sticky="w")

# Bouton de recherche
def on_button_hover(event):
    bouton_rechercher.config(bg=couleur_boutons_hover)

def on_button_leave(event):
    bouton_rechercher.config(bg=couleur_boutons)

bouton_rechercher = tk.Button(root, text="Rechercher", font=font_boutons, bg=couleur_boutons, fg="white", command=rechercher_film)
bouton_rechercher.grid(row=5, column=0, columnspan=3, pady=10)

# Bouton de films populaires
bouton_populaires = tk.Button(root, text="Films populaires", font=font_boutons, bg=couleur_boutons, fg="white", command=afficher_films_populaires)
bouton_populaires.grid(row=6, column=0, columnspan=3, pady=10)

# Liste des r�sultats
listbox_resultats = tk.Listbox(root, font=font_principal, width=60, height=10, selectmode=tk.SINGLE)
listbox_resultats.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

# Labels pour afficher les d�tails du film
label_titre = tk.Label(root, text="Titre: ", font=('SF Pro Display Bold', 14), bg="#f2f2f2")
label_titre.grid(row=8, column=0, padx=10, pady=5, sticky="w")

label_sortie = tk.Label(root, text="Date de sortie: ", font=('SF Pro Display Bold', 14), bg="#f2f2f2")
label_sortie.grid(row=9, column=0, padx=10, pady=5, sticky="w")

label_resume = tk.Label(root, text="R�sum�: ", font=('SF Pro Display Bold', 14), bg="#f2f2f2")
label_resume.grid(row=10, column=0, padx=10, pady=5, sticky="w")

# Label pour l'image du film
label_image = tk.Label(root)
label_image.grid(row=8, column=1, rowspan=3, padx=10, pady=10)

# Barre de progression
barre_progression = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
barre_progression.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()