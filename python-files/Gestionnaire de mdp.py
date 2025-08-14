import json
import random
import string
import os

FICHIER = "mots_de_passe.json"

# Générer un mot de passe aléatoire
def generer_mdp(longueur=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(longueur))

# Charger les mots de passe depuis le fichier
def charger_mdp():
    if os.path.exists(FICHIER):
        with open(FICHIER, "r") as f:
            return json.load(f)
    return {}

# Sauvegarder les mots de passe dans le fichier
def sauvegarder_mdp(mdp_dict):
    with open(FICHIER, "w") as f:
        json.dump(mdp_dict, f, indent=4)

# Ajouter un mot de passe
def ajouter_mdp(site, motdepasse):
    mdp_dict = charger_mdp()
    mdp_dict[site] = motdepasse
    sauvegarder_mdp(mdp_dict)
    print(f"Mot de passe pour {site} ajouté.")

# Afficher un mot de passe
def afficher_mdp(site):
    mdp_dict = charger_mdp()
    if site in mdp_dict:
        print(f"Mot de passe pour {site} : {mdp_dict[site]}")
    else:
        print(f"Aucun mot de passe trouvé pour {site}.")

# Menu principal
def menu():
    while True:
        print("\n--- Gestionnaire de mots de passe ---")
        print("1. Ajouter un mot de passe")
        print("2. Afficher un mot de passe")
        print("3. Générer un mot de passe aléatoire")
        print("4. Quitter")
        choix = input("Choisissez une option : ")

        if choix == "1":
            site = input("Nom du site/application : ")
            mdp = input("Mot de passe (laissez vide pour générer un mot de passe aléatoire) : ")
            if not mdp:
                mdp = generer_mdp()
                print(f"Mot de passe généré : {mdp}")
            ajouter_mdp(site, mdp)
        elif choix == "2":
            site = input("Nom du site/application : ")
            afficher_mdp(site)
        elif choix == "3":
            print(f"Mot de passe aléatoire : {generer_mdp()}")
        elif choix == "4":
            break
        else:
            print("Option invalide, réessayez.")

if __name__ == "__main__":
    menu()
