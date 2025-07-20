import pygame
import random

# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 500, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Dodger")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 30)

# Player variables
player_width = 50
player_height = 50
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_vel = 7  # Speed

# Block variables
block_width = 50
block_height = 50
block_vel = 5
blocks = []

# Score
score = 0
run = True
game_over = False

def draw_window():
    win.fill(WHITE)
    pygame.draw.rect(win, BLUE, (player_x, player_y, player_width, player_height))
    for bx, by in blocks:
        pygame.draw.rect(win, RED, (bx, by, block_width, block_height))
    score_text = font.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score_text, (10, 10))
    pygame.display.update()

while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if not game_over:
        # Add new blocks randomly
        if random.randint(1, 20) == 1:
            new_x = random.randint(0, WIDTH - block_width)
            blocks.append([new_x, -block_height])

        # Move blocks down
        for block in blocks:
            block[1] += block_vel

        # Remove blocks that go off screen
        blocks = [block for block in blocks if block[1] < HEIGHT]

        # Check for collision
        for bx, by in blocks:
            if (player_x < bx + block_width and
                player_x + player_width > bx and
                player_y < by + block_height and
                player_y + player_height > by):
                game_over = True

        # Move player with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_vel
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_vel

        score += 1
        draw_window()
    else:
        win.fill(WHITE)
        over_text = font.render("Game Over! Score: " + str(score), 1, RED)
        win.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

pygame.quit()