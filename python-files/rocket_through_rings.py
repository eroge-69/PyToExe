
import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Rocket settings
ROCKET_WIDTH = 40
ROCKET_HEIGHT = 60
ROCKET_COLOR = WHITE

# Ring settings
RING_WIDTH = 80
RING_HEIGHT = 20
RING_COLOR = WHITE
RING_GAP = 200

# Game settings
GRAVITY = 0.5
JUMP_STRENGTH = -10
FPS = 60

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rocket Through Rings")

# Load rocket image
rocket_img = pygame.Surface((ROCKET_WIDTH, ROCKET_HEIGHT))
rocket_img.fill(ROCKET_COLOR)

# Load ring image
ring_img = pygame.Surface((RING_WIDTH, RING_HEIGHT))
ring_img.fill(RING_COLOR)

# Font for score
font = pygame.font.Font(None, 36)

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def main():
    clock = pygame.time.Clock()
    running = True

    # Rocket settings
    rocket_x = SCREEN_WIDTH // 4
    rocket_y = SCREEN_HEIGHT // 2
    rocket_speed_y = 0

    # Rings settings
    rings = []
    for i in range(5):
        ring_x = SCREEN_WIDTH + i * RING_GAP
        ring_y = random.randint(100, SCREEN_HEIGHT - 100)
        rings.append((ring_x, ring_y))

    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    rocket_speed_y = JUMP_STRENGTH

        # Rocket movement
        rocket_speed_y += GRAVITY
        rocket_y += rocket_speed_y

        # Ring movement
        for i in range(len(rings)):
            rings[i] = (rings[i][0] - 5, rings[i][1])
            if rings[i][0] < -RING_WIDTH:
                rings[i] = (SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 100))
                score += 1

        # Check for collisions
        for ring in rings:
            if rocket_x + ROCKET_WIDTH > ring[0] and rocket_x < ring[0] + RING_WIDTH:
                if rocket_y < ring[1] or rocket_y + ROCKET_HEIGHT > ring[1] + RING_HEIGHT:
                    running = False

        # Check if rocket is out of bounds
        if rocket_y > SCREEN_HEIGHT or rocket_y < 0:
            running = False

        # Draw everything
        screen.fill(BLACK)
        screen.blit(rocket_img, (rocket_x, rocket_y))
        for ring in rings:
            screen.blit(ring_img, ring)
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)

        pygame.display.flip()
        clock.tick(FPS)

    # Game over screen
    screen.fill(BLACK)
    draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20)
    draw_text(f"Final Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20)
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()

if __name__ == "__main__":
    main()
