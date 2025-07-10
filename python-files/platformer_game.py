
import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Player settings
player_size = (50, 50)
player_pos = [100, HEIGHT - 150]
player_vel = [0, 0]
player_speed = 5
jump_power = 15
gravity = 1
on_ground = False

# Platform settings
platforms = [
    pygame.Rect(0, HEIGHT - 50, WIDTH, 50),
    pygame.Rect(300, HEIGHT - 150, 200, 20),
    pygame.Rect(550, HEIGHT - 250, 200, 20)
]

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_vel[0] = -player_speed
    elif keys[pygame.K_RIGHT]:
        player_vel[0] = player_speed
    else:
        player_vel[0] = 0

    if keys[pygame.K_SPACE] and on_ground:
        player_vel[1] = -jump_power
        on_ground = False

    # Apply gravity
    player_vel[1] += gravity

    # Move player
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]

    # Create player rect
    player_rect = pygame.Rect(player_pos[0], player_pos[1], *player_size)

    # Collision detection
    on_ground = False
    for platform in platforms:
        if player_rect.colliderect(platform) and player_vel[1] >= 0:
            player_pos[1] = platform.top - player_size[1]
            player_vel[1] = 0
            on_ground = True

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)

    # Draw player
    pygame.draw.rect(screen, BLUE, player_rect)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
