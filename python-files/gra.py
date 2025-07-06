import pygame
pygame.init()

ekran = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Moja Gra")
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    ekran.fill((0, 0, 255))
    pygame.display.flip()

pygame.quit()
