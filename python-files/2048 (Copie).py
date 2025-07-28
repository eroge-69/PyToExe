###############################
### IMPORTATION DES MODULES ###
###############################

from math import *
from random import *
from tkinter import *
from tkinter import messagebox
from time import *

##############################
### FONCTIONS ET VARIABLES ###
##############################

grille = [[0 for i in range(4)] for j in range(4)]

def Actualiser_fenêtre(root):
    for widget in root.winfo_children(): 
        widget.destroy()

    Fond = Canvas(root, background="#F0B479", width=500, height=500)
    Fond.pack(fill="both", expand=True)

    Taille_cases = 100
    Taille_texte = 15          
    Décalage_X = 50
    Décalage_Y = 50

    # Création de la grille
    for ligne in range(4):
        for colonne in range(4):
            valeur = grille[ligne][colonne]
            texte = str(valeur) if valeur != 0 else ""
            case = Label(root, text = texte, width = 4, height = 2, font = ("Arial", Taille_texte, "bold"), background = "#F0B479", relief = "raised", borderwidth=5)

            x = Décalage_X + colonne * Taille_cases
            y = Décalage_Y + ligne * Taille_cases
            case.place(x = x, y = y, width = Taille_cases, height = Taille_cases)

def Deplacer_blocs(root, direction : str):
    for deplacement in range(4):
        if direction == "gauche":
            for ligne in range(len(grille)):
                for colonne in range(len(grille)):
                    if grille[ligne][colonne] == 0:
                        if colonne+1 < len(grille) and grille[ligne][colonne+1] != 0:
                            grille[ligne][colonne] = grille[ligne][colonne+1]
                            grille[ligne][colonne+1] = 0

        if direction == "droite":
            for ligne in range(len(grille)):
                for colonne in range(len(grille)):
                    if grille[ligne][colonne] == 0:
                        if colonne-1 >= 0 and grille[ligne][colonne-1] != 0:
                            grille[ligne][colonne] = grille[ligne][colonne-1]
                            grille[ligne][colonne-1] = 0

        if direction == "haut":
            for ligne in range(len(grille)):
                for colonne in range(len(grille)):
                    if grille[ligne][colonne] == 0:
                        if ligne+1 < len(grille) and grille[ligne+1][colonne] != 0:
                            grille[ligne][colonne] = grille[ligne+1][colonne]
                            grille[ligne+1][colonne] = 0

        if direction == "bas":
            for ligne in range(len(grille)):
                for colonne in range(len(grille)):
                    if grille[ligne][colonne] == 0:
                        if ligne-1 >= 0 and grille[ligne-1][colonne] != 0:
                            grille[ligne][colonne] = grille[ligne-1][colonne]
                            grille[ligne-1][colonne] = 0

def Fusionner_blocs(root, direction: str):
    if direction == "gauche":
        for ligne in range(4):
            for colonne in range(3):
                if grille[ligne][colonne] != 0 and grille[ligne][colonne] == grille[ligne][colonne + 1]:
                    grille[ligne][colonne] *= 2
                    grille[ligne][colonne + 1] = 0

    elif direction == "droite":
        for ligne in range(4):
            for colonne in range(3, 0, -1):
                if grille[ligne][colonne] != 0 and grille[ligne][colonne] == grille[ligne][colonne - 1]:
                    grille[ligne][colonne] *= 2
                    grille[ligne][colonne - 1] = 0

    elif direction == "haut":
        for colonne in range(4):
            for ligne in range(3):
                if grille[ligne][colonne] != 0 and grille[ligne][colonne] == grille[ligne + 1][colonne]:
                    grille[ligne][colonne] *= 2
                    grille[ligne + 1][colonne] = 0

    elif direction == "bas":
        for colonne in range(4):
            for ligne in range(3, 0, -1):
                if grille[ligne][colonne] != 0 and grille[ligne][colonne] == grille[ligne - 1][colonne]:
                    grille[ligne][colonne] *= 2
                    grille[ligne - 1][colonne] = 0

def Ajouter_blocs(root):
    ligne = randint(0,3)
    colonne = randint(0,3)
    while grille[ligne][colonne] != 0:
            ligne = randint(0,3)
            colonne = randint(0,3)
    grille[ligne][colonne] = choice([2, 2, 2, 2, 4])

    Actualiser_fenêtre(root)

def Fin_du_jeu(root):
    for ligne in range(4):
        for colonne in range(4):
            if grille[ligne][colonne] == 0:
                return  # Il reste une case vide

            if colonne < 3 and grille[ligne][colonne] == grille[ligne][colonne + 1]:
                return  # Fusion possible à droite
            if ligne < 3 and grille[ligne][colonne] == grille[ligne + 1][colonne]:
                return  # Fusion possible en bas

    messagebox.showinfo("Game Over", "Plus de mouvement possible !\nLa partie est terminée.")

######################################
### AFFICHAGE DE LA FENÊTRE DE JEU ###
######################################

root = Tk()
root.title("2048")
root.geometry("500x500")
root.resizable(False, False)
root.configure(background="#F0B479")

def Gestion_touches(event):
    ancienne_grille = [ligne.copy() for ligne in grille]

    if event.keysym == "Left":
        Deplacer_blocs(root, "gauche")
        Fusionner_blocs(root, "gauche")
        Deplacer_blocs(root, "gauche")

        if grille != ancienne_grille:
            Ajouter_blocs(root)
        Fin_du_jeu(root)

    if event.keysym == "Right":
        Deplacer_blocs(root, "droite")
        Fusionner_blocs(root, "droite")
        Deplacer_blocs(root, "droite")

        if grille != ancienne_grille:
            Ajouter_blocs(root)
        Fin_du_jeu(root)

    if event.keysym == "Up":
        Deplacer_blocs(root, "haut")
        Fusionner_blocs(root, "haut")
        Deplacer_blocs(root, "haut")

        if grille != ancienne_grille:
            Ajouter_blocs(root)
        Fin_du_jeu(root)

    if event.keysym == "Down":
        Deplacer_blocs(root, "bas")
        Fusionner_blocs(root, "bas")
        Deplacer_blocs(root, "bas")

        if grille != ancienne_grille:
            Ajouter_blocs(root)
        Fin_du_jeu(root)

###################################################################
### FERMETURE DE LA FENÊTRE DE JEU ET FONCTIONS SUPPLÉMENTAIRES ###
###################################################################

Ajouter_blocs(root)
root.bind("<Key>", Gestion_touches)
root.mainloop()