import os
import random
import string
from datetime import datetime
from tkinter import Tk, filedialog

# Fonction qui génère un nom aléatoire
def nom_aleatoire(longueur=12):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longueur))

def renommer_fichiers(dossier):
    compteur = 0

    if not os.path.isdir(dossier):
        print(f"❌ Le dossier spécifié n'existe pas : {dossier}")
        return

    for nom_fichier in os.listdir(dossier):
        chemin_complet = os.path.join(dossier, nom_fichier)

        if os.path.isfile(chemin_complet) and nom_fichier != "log.txt":
            extension = os.path.splitext(nom_fichier)[1]

            # Nouveau nom unique
            nouveau_nom = nom_aleatoire() + extension
            chemin_nouveau = os.path.join(dossier, nouveau_nom)

            while os.path.exists(chemin_nouveau):
                nouveau_nom = nom_aleatoire() + extension
                chemin_nouveau = os.path.join(dossier, nouveau_nom)

            os.rename(chemin_complet, chemin_nouveau)
            compteur += 1
            print(f"{nom_fichier} → {nouveau_nom}")

    # Mise à jour du log
    log_path = os.path.join(dossier, "log.txt")
    with open(log_path, "a", encoding="utf-8") as log:
        date_heure = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        log.write(f"{date_heure} - {compteur} fichiers renommés dans le dossier : {dossier}\n")

    print(f"\n✅ {compteur} fichiers renommés. Historique mis à jour dans {log_path}")


if __name__ == "__main__":
    # Ouvre une fenêtre pour choisir le dossier
    Tk().withdraw()  # cache la fenêtre principale Tkinter
    dossier = filedialog.askdirectory(title="Sélectionnez un dossier à renommer")

    if dossier:
        renommer_fichiers(dossier)
    else:
        print("❌ Aucun dossier sélectionné.")
