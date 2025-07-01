# Dodger Game

import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_SIZE = 50
ENEMY_SIZE = 50
SPEED = 5

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger Game")

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, dx):
        if 0 <= self.rect.x + dx <= WIDTH - PLAYER_SIZE:
            self.rect.x += dx

# Enemy class
class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), 0, ENEMY_SIZE, ENEMY_SIZE)

    def fall(self):
        self.rect.y += SPEED

# Game loop
def main():
    clock = pygame.time.Clock()
    player = Player()
    enemies = [Enemy()]
    score = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-SPEED)
        if keys[pygame.K_RIGHT]:
            player.move(SPEED)

        # Update enemies
        for enemy in enemies:
            enemy.fall()
            if enemy.rect.y > HEIGHT:
                enemies.remove(enemy)
                enemies.append(Enemy())
                score += 1

            if player.rect.colliderect(enemy.rect):
                running = False

        # Drawing
        screen.fill(WHITE)
        pygame.draw.rect(screen, BLACK, player.rect)
        for enemy in enemies:
            pygame.draw.rect(screen, BLACK, enemy.rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
