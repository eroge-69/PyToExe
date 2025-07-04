import cv2
import pygame
import sys

# ---------- Initialisation ----------
pygame.init()
pygame.mixer.init()                     # Pour l'audio
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("RickRoll")
clock = pygame.time.Clock()

# ---------- Audio ----------
pygame.mixer.music.load("rickroll.ogg") # Ou .mp3 si ça marche chez toi
pygame.mixer.music.play()

# ---------- Vidéo ----------
cap = cv2.VideoCapture("rickroll.mp4")
if not cap.isOpened():
    print("Erreur : impossible de lire la vidéo.")
    sys.exit()

# Boucle principale
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:                         # Fin de la vidéo
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, screen.get_size())        # Adapter à l'écran
    surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    screen.blit(surface, (0, 0))
    pygame.display.update()

    # Ignore toutes les entrées utilisateur
    for event in pygame.event.get():
        pass

    # Quitte dès que l'audio est terminé
    if not pygame.mixer.music.get_busy():
        break

    clock.tick(30)  # 30 FPS

# ---------- Nettoyage ----------
cap.release()
pygame.quit()
sys.exit()
