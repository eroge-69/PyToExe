
import pygame
import time
import sys
import os

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("SEGA Logo")
BLACK = (0, 0, 0)

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(base_path, "sega_logo.png")
sound_path = os.path.join(base_path, "sega_sound.mp3")

logo = pygame.image.load(logo_path)
sound = pygame.mixer.Sound(sound_path)
sound.play()

running = True
start_time = time.time()

while running:
    screen.fill(BLACK)
    rect = logo.get_rect(center=(320, 240))
    screen.blit(logo, rect)
    pygame.display.flip()

    if time.time() - start_time > 3:
        running = False

pygame.quit()
sys.exit()
