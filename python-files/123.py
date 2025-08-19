import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Driving Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# Clock
clock = pygame.time.Clock()

# Car setup
car_width = 50
car_height = 100
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 10
car_speed = 7

# Obstacle setup
obstacle_width = 50
obstacle_height = 100
obstacle_speed = 7
obstacle_x = random.randint(0, WIDTH - obstacle_width)
obstacle_y = -obstacle_height

score = 0
font = pygame.font.SysFont(None, 40)

def display_score(score):
    text = font.render("Score: " + str(score), True, BLACK)
    screen.blit(text, (10, 10))

# Game loop
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > 0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed

    # Move obstacles
    obstacle_y += obstacle_speed
    if obstacle_y > HEIGHT:
        obstacle_y = -obstacle_height
        obstacle_x = random.randint(0, WIDTH - obstacle_width)
        score += 1  # increase score when obstacle passes

    # Draw car
    pygame.draw.rect(screen, BLACK, (car_x, car_y, car_width, car_height))

    # Draw obstacle
    pygame.draw.rect(screen, RED, (obstacle_x, obstacle_y, obstacle_width, obstacle_height))

    # Collision detection
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)
    if car_rect.colliderect(obstacle_rect):
        print("Game Over! Final Score:", score)
        running = False

    # Show score
    display_score(score)

    pygame.display.flip()

pygame.quit()
sys.exit()
