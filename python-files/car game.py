Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Car Driving Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Clock
clock = pygame.time.Clock()

# Car settings
car_width = 50
car_height = 100
car = pygame.Rect(WIDTH // 2 - car_width // 2, HEIGHT - car_height - 20, car_width, car_height)
car_speed = 5

# Obstacle settings
obstacle_width = 50
obstacle_height = 100
obstacle = pygame.Rect(random.randint(0, WIDTH - obstacle_width), -obstacle_height, obstacle_width, obstacle_height)
obstacle_speed = 5

# Road lines
lines = [pygame.Rect(WIDTH // 2 - 5, i * 150, 10, 80) for i in range(5)]

# Game loop
def game_loop():
    running = True
    while running:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
...                 sys.exit()
... 
...         keys = pygame.key.get_pressed()
...         if keys[pygame.K_LEFT] and car.left > 0:
...             car.x -= car_speed
...         if keys[pygame.K_RIGHT] and car.right < WIDTH:
...             car.x += car_speed
... 
...         # Draw road lines
...         for line in lines:
...             pygame.draw.rect(screen, WHITE, line)
...             line.y += 10
...             if line.y > HEIGHT:
...                 line.y = -80
... 
...         # Move and draw obstacle
...         obstacle.y += obstacle_speed
...         if obstacle.y > HEIGHT:
...             obstacle.y = -obstacle_height
...             obstacle.x = random.randint(0, WIDTH - obstacle_width)
...         
...         pygame.draw.rect(screen, RED, obstacle)
... 
...         # Draw car
...         pygame.draw.rect(screen, YELLOW, car)
... 
...         # Collision check
...         if car.colliderect(obstacle):
...             font = pygame.font.SysFont(None, 75)
...             text = font.render("Game Over", True, RED)
...             screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
...             pygame.display.flip()
...             pygame.time.wait(2000)
...             return
... 
...         pygame.display.update()
...         clock.tick(60)
... 
... game_loop()
