import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving Square Game")

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Set up clock for frame rate
clock = pygame.time.Clock()

# Define the player properties
player_size = 50
player_x = (screen_width - player_size) // 2
player_y = (screen_height - player_size) // 2
player_speed = 5

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle keys pressed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Boundary checking to keep square within the window
    player_x = max(0, min(screen_width - player_size, player_x))
    player_y = max(0, min(screen_height - player_size, player_y))
    
    # Fill the background
    screen.fill(WHITE)
    
    # Draw the square (player)
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
sys.exit(exec)
