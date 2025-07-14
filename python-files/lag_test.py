import pygame
import time

# Initialize Pygame
pygame.init()

# Screen dimensions and FPS settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
SUN_COLOR = (255, 255, 100)
SKY_TOP_COLOR = (135, 206, 250)  # Sky blue
SKY_BOTTOM_COLOR = (255, 255, 255)  # Lighter sky at horizon

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Light Test")

# Font for FPS display
font = pygame.font.SysFont('Arial', 20)

# Clock object to manage FPS
clock = pygame.time.Clock()

# Play/Pause state
paused = False

# Function to draw the FPS
def draw_fps(fps):
    fps_text = font.render(f"FPS: {fps}", True, WHITE)
    screen.blit(fps_text, (10, 10))

# Function to draw the sky (gradient)
def draw_sky():
    for y in range(HEIGHT):
        # Gradually transition from light blue at the horizon to sky blue at the top
        color = (
            int(SKY_TOP_COLOR[0] * (1 - y / HEIGHT) + SKY_BOTTOM_COLOR[0] * (y / HEIGHT)),
            int(SKY_TOP_COLOR[1] * (1 - y / HEIGHT) + SKY_BOTTOM_COLOR[1] * (y / HEIGHT)),
            int(SKY_TOP_COLOR[2] * (1 - y / HEIGHT) + SKY_BOTTOM_COLOR[2] * (y / HEIGHT))
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

# Function to draw the sun
def draw_sun():
    pygame.draw.circle(screen, SUN_COLOR, (WIDTH // 2, HEIGHT // 3), 50)

# Function to draw the baseplate
def draw_baseplate():
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - 100, WIDTH, 100))

# Main game loop
running = True
while running:
    start_time = time.time()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # Toggle paused state

    # Fill the screen with black (background)
    screen.fill(BLACK)

    # Draw the sky and sun
    draw_sky()
    draw_sun()

    # If not paused, render the scene
    if not paused:
        # Draw the baseplate
        draw_baseplate()

        # Simulate a simple lighting effect by creating a light "mask"
        light_surface = pygame.Surface((WIDTH, HEIGHT))
        light_surface.fill((255, 255, 255))
        light_surface.set_alpha(50)  # Light intensity
        screen.blit(light_surface, (0, 0))

        # Draw the FPS UI
        draw_fps(clock.get_fps())
    
    else:
        # Draw the paused screen
        paused_text = font.render("Paused (Press Space to Play)", True, WHITE)
        screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2))

    # Update the screen
    pygame.display.flip()
    
    # Control the FPS
    elapsed_time = time.time() - start_time
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
