import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Car Racing Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

# Car settings
CAR_WIDTH, CAR_HEIGHT = 50, 100

# Load car image or draw a rectangle as a placeholder
# For simplicity, we'll draw a rectangle as player's car
player_x = WIDTH // 2 - CAR_WIDTH // 2
player_y = HEIGHT - CAR_HEIGHT - 10
player_speed = 5

# Enemy car settings
enemy_width, enemy_height = 50, 100
enemy_speed = 7
enemy_x = random.randint(0, WIDTH - enemy_width)
enemy_y = -enemy_height

# Score
score = 0
font = pygame.font.SysFont(None, 36)

clock = pygame.time.Clock()

def draw_player(x, y):
    pygame.draw.rect(screen, RED, (x, y, CAR_WIDTH, CAR_HEIGHT))

def draw_enemy(x, y):
    pygame.draw.rect(screen, GREEN, (x, y, enemy_width, enemy_height))

def show_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def game_over():
    over_text = font.render("GAME OVER!", True, RED)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(2000)

def main():
    global player_x, enemy_x, enemy_y, score

    running = True

    while running:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Key press handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - CAR_WIDTH:
            player_x += player_speed

        # Move enemy car down
        enemy_y += enemy_speed

        # Reset enemy when it goes off screen
        if enemy_y > HEIGHT:
            enemy_y = -enemy_height
            enemy_x = random.randint(0, WIDTH - enemy_width)
            score += 1  # Increase score when enemy passes

        # Draw player and enemy
        draw_player(player_x, player_y)
        draw_enemy(enemy_x, enemy_y)
        show_score(score)

        # Check collision
        player_rect = pygame.Rect(player_x, player_y, CAR_WIDTH, CAR_HEIGHT)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
        if player_rect.colliderect(enemy_rect):
            game_over()
            running = False

        pygame.display.update()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
