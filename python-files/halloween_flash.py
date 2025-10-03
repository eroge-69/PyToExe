import pygame
import time

# Configuration
flash_count = 3
flash_duration = 0.1  # Durée de la coupure (en secondes)
pause_between_flashes = 0.2  # Durée de visibilité normale entre 2 flashs
interval_minutes = 5  # Temps entre chaque série de flashs

def flash_black_screen():
    # Initialise Pygame et crée la fenêtre noir plein écran
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.FULLSCREEN)
    pygame.display.set_caption("Halloween Flash")
    pygame.mouse.set_visible(False)

    for _ in range(flash_count):
        # Affiche écran noir (recouvre le site)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        time.sleep(flash_duration)

        # Ferme la fenêtre pour revenir à la vue du site
        pygame.display.quit()
        time.sleep(pause_between_flashes)

        # Rouvre la fenêtre pour le prochain flash
        screen = pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

    # Ferme complètement après les 6 flashs
    pygame.quit()

# Boucle principale
try:
    while True:
        print(f"Waiting {interval_minutes} minutes before next flash...")
        time.sleep(interval_minutes * 60)
        print("Flashing in progress!")
        flash_black_screen()
except KeyboardInterrupt:
    print("Script Stopped.")
