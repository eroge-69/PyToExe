# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 17:14:09 2024

@author: Dual Force
"""
import pygame
import os
from PIL import Image

# Chemin du dossier du script
dossier_script = os.path.dirname(os.path.abspath(__file__))

# Liste des images redimensionnées
liste = []

# Lecture du fichier de propriétés
path = os.path.join(dossier_script, "..", "AppProperties", "Properties.txt")
with open(path, "r") as fichier:
    li = fichier.readlines()
    li[0] = li[0].split("Name :")
    li[2] = li[2].split("Icon :")
    li[4] = li[4].split("GoodImage :")
    li[5] = li[5].split("OriginImagePath :")
    li[0] = li[0][1].strip()
    li[2] = li[2][1].strip()
    li[4] = li[4][1].strip()
    li[5] = li[5][1].strip()

# Extraction des propriétés
AppName = li[0]
Icon = li[2]
GoodImage = li[4]
OriginPath = li[5]

print(AppName, Icon, OriginPath, GoodImage)

# Chemins des dossiers source et destination
dossier_image_source = os.path.join(dossier_script, "..", "Image", "Image")
if OriginPath:
    dossier_image_source = OriginPath

dossier_image_destination = os.path.join(dossier_script, "..", "Image", "ImageRedimentioné")

# Création du dossier de destination s'il n'existe pas
if not os.path.exists(dossier_image_destination):
    os.makedirs(dossier_image_destination)

# Hauteur voulue pour le redimensionnement
hauteur_voulue = 1080

# Parcourir et redimensionner les images du dossier source
for filename in os.listdir(dossier_image_source):
    if filename.endswith((".jpg", ".jpeg", ".png")):  # Filtrer les fichiers image
        chemin_image_source = os.path.join(dossier_image_source, filename)
        chemin_image_destination = os.path.join(dossier_image_destination, f"image_{filename}")

        try:
            # Charger l'image avec PIL
            img = Image.open(chemin_image_source)
            imgsize = img.size

            # Calculer la largeur tout en maintenant les proportions
            largeur_voulue = int((imgsize[0] / imgsize[1]) * hauteur_voulue)

            # Redimensionner l'image
            img_redimensionnee = img.resize((largeur_voulue, hauteur_voulue))

            # Convertir l'image en mode RGB si nécessaire avant de la sauvegarder
            if img_redimensionnee.mode in ('RGBA', 'LA'):
                img_redimensionnee = img_redimensionnee.convert('RGB')

            # Enregistrer l'image redimensionnée
            img_redimensionnee.save(chemin_image_destination)
            print(f"Redimensionnement de {filename} et enregistrement en tant que image_{filename}")

            # Ajouter à la liste
            liste.append(filename)

        except Exception as e:
            print(f"Erreur lors du traitement de {filename}: {e}")

print("Toutes les images ont été redimensionnées avec succès.")
print(liste)

#############################################################################################
# Initialisation de Pygame
pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption(AppName)
icon_path = os.path.join(dossier_script, "..", "AppProperties", Icon)
icon_surface = pygame.image.load(icon_path)
pygame.display.set_icon(icon_surface)

# Variables de gestion du jeu
GameRun = True
i = 0
click = False
clock = pygame.time.Clock()  # Limitation du framerate

# Boucle principale du jeu
while GameRun:
    if click:
        # Affichage d'une image spéciale (GoodImage) lorsque cliqué
        Screen.fill((0, 0, 0))
        path_GoodImage = os.path.join(dossier_script, "..", "AppProperties", GoodImage)
        image = pygame.image.load(path_GoodImage).convert()
    else:
        # Affichage de l'image redimensionnée courante
        Screen.fill((0, 0, 0))
        image_filename = liste[i]
        image_path = os.path.join(dossier_image_destination, f"image_{image_filename}")
        image = pygame.image.load(image_path).convert()

    # Centrer l'image à l'écran
    image_rect = image.get_rect()
    x = (SCREEN_WIDTH - image_rect.width) // 2
    y = (SCREEN_HEIGHT - image_rect.height) // 2
    Screen.blit(image, (x, y))

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameRun = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 or event.button == 4:
                i = len(liste) - 1 if i == 0 else i - 1
            elif event.button == 2:
                click = not click
            else:
                i = 0 if i == len(liste) - 1 else i + 1

    # Mise à jour de l'affichage
    pygame.display.update()
    clock.tick(60)  # Limiter à 60 FPS

# Quitter Pygame
pygame.quit()

"""
Commande pour créer un exécutable :
pyinstaller --onefile game.py
"""
