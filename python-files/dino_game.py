import pygame
import random

pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 300
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chrome Dino Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
FPS = 60

# Load images
dino_img = pygame.image.load("dino.png").convert_alpha()
cactus_img = pygame.image.load("cactus.png").convert_alpha()

# Scale images to appropriate size
DINO_WIDTH, DINO_HEIGHT = 60, 60
dino_img = pygame.transform.scale(dino_img, (DINO_WIDTH, DINO_HEIGHT))

CACTUS_WIDTH, CACTUS_HEIGHT = 30, 50
cactus_img = pygame.transform.scale(cactus_img, (CACTUS_WIDTH, CACTUS_HEIGHT))

# Sounds (optional)
try:
    jump_sound = pygame.mixer.Sound('jump.wav')
except:
    jump_sound = None

try:
    collision_sound = pygame.mixer.Sound('collision.wav')
except:
    collision_sound = None

font = pygame.font.SysFont(None, 30)

def draw_dino(x, y):
    SCREEN.blit(dino_img, (x, y))

def draw_obstacle(x, y):
    SCREEN.blit(cactus_img, (x, y))

def show_score(score):
    text = font.render(f"Score: {score}", True, BLACK)
    SCREEN.blit(text, (650, 10))

def game_over_screen():
    SCREEN.fill(WHITE)
    game_over_text = font.render("Game Over! Click to Try Again.", True, BLACK)
    SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False  # Restart game

def main():
    # Dino variables
    dino_x = 50
    dino_y = HEIGHT - DINO_HEIGHT - 40
    dino_y_velocity = 0
    gravity = 1
    jump_power = 15
    is_jumping = False

    # Obstacles
    obstacle_speed = 7
    obstacles = []
    spawn_timer = 0
    spawn_delay = random.randint(1500, 3000)

    score = 0
    run = True
    while run:
        dt = clock.tick(FPS)
        SCREEN.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping:
                    dino_y_velocity = -jump_power
                    is_jumping = True
                    if jump_sound:
                        jump_sound.play()

        # Dino jump physics
        dino_y += dino_y_velocity
        dino_y_velocity += gravity

        if dino_y >= HEIGHT - DINO_HEIGHT - 40:
            dino_y = HEIGHT - DINO_HEIGHT - 40
            is_jumping = False

        # Obstacle spawning
        spawn_timer += dt
        if spawn_timer > spawn_delay:
            spawn_timer = 0
            spawn_delay = random.randint(1500, 3000)
            obstacles.append([WIDTH, HEIGHT - CACTUS_HEIGHT - 40])

        # Move and remove obstacles
        for obstacle in list(obstacles):
            obstacle[0] -= obstacle_speed
            if obstacle[0] < -CACTUS_WIDTH:
                obstacles.remove(obstacle)
                score += 1

        # Drawing
        draw_dino(dino_x, dino_y)
        for obstacle in obstacles:
            draw_obstacle(obstacle[0], obstacle[1])

        # Collision detection
        dino_rect = pygame.Rect(dino_x, dino_y, DINO_WIDTH, DINO_HEIGHT)
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], CACTUS_WIDTH, CACTUS_HEIGHT)
            if dino_rect.colliderect(obstacle_rect):
                if collision_sound:
                    collision_sound.play()
                run = False

        show_score(score)
        pygame.display.update()

    # Game over and wait for retry
    game_over_screen()
    main()  # Restart game

if __name__ == "__main__":
    main()
