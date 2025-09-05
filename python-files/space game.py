import pygame
import sys

pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game with Your Images")

# Load your actual images
background = pygame.image.load("starry_space.png")
spaceship = pygame.image.load("spaceship.png")

# Spaceship starting position
ship_x, ship_y = WIDTH // 2, HEIGHT // 2

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display your images exactly as they are
    screen.blit(background, (0, 0))
    screen.blit(spaceship, (ship_x - spaceship.get_width() // 2, ship_y - spaceship.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()