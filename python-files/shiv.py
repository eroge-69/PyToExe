import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Falling Blocks")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 10
player_speed = 5

# Enemy block
block_size = 50
block_x = random.randint(0, WIDTH - block_size)
block_y = 0
block_speed = 5

score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += player_speed

    # Move block
    block_y += block_speed
    if block_y > HEIGHT:
        block_y = 0
        block_x = random.randint(0, WIDTH - block_size)
        score += 1
        block_speed += 0.5  # Increase difficulty

    # Collision detection
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    block_rect = pygame.Rect(block_x, block_y, block_size, block_size)
    if player_rect.colliderect(block_rect):
        print("Game Over! Final Score:", score)
        running = False

    # Draw player and block
    pygame.draw.rect(screen, BLUE, player_rect)
    pygame.draw.rect(screen, RED, block_rect)

    # Display score
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

pygame.quit()
