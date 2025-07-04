import pygame
import numpy as np
import random

# Bildschirmgröße
WIDTH, HEIGHT = 1920, 1080

# Initialisierung
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Glitch Attack')

clock = pygame.time.Clock()

running = True
while running:
    # Zufällige Pixel erzeugen
    arr = np.random.randint(0, 255, (HEIGHT, WIDTH, 3), dtype=np.uint8)

    # Kleine Glitch-Effekte: Zeilen verschieben
    for _ in range(50):
        y = random.randint(0, HEIGHT - 1)
        shift = random.randint(-100, 100)
        arr[y] = np.roll(arr[y], shift, axis=0)

    # Großes Surface daraus machen
    surface = pygame.surfarray.make_surface(np.rot90(arr))

    screen.blit(surface, (0, 0))
    pygame.display.update()

    # Optional CPU überlasten
    for _ in range(1000000):
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
