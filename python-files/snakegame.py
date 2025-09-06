import pygame
import random

pygame.init()
pygame.mixer.init()  # Initialize mixer for music

# Play background music
pygame.mixer.music.load("Future, Metro Boomin - Drink N Dance (Lyrics).mp3")  # Make sure the file is in the same folder
pygame.mixer.music.play(-1)  # Loop indefinitely
pygame.mixer.music.set_volume(1000)  # Optional: set volume to 50%

# Window
WIDTH, HEIGHT = 1920, 1080
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake2 🐍")

# Colors
BLACK = (0, 0, 0)
RUNAWAY_SCORE = 10  # Score at which food starts moving away

# Settings
SNAKE_SIZE = 20
SNAKE_SPEED = 1  # Grid moves per second
FPS = 60  # Max FPS

font = pygame.font.SysFont("comicsansms", 35)

# Load images
background_image = pygame.image.load("baby.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

food_image = pygame.image.load("kevinheart.jpg")
food_image = pygame.transform.scale(food_image, (SNAKE_SIZE, SNAKE_SIZE))

snake_image = pygame.image.load("flight.png")
snake_image = pygame.transform.scale(snake_image, (SNAKE_SIZE, SNAKE_SIZE))

# Draw snake using image
def draw_snake(snake_list):
    for x, y in snake_list:
        win.blit(snake_image, (x, y))

# Draw score (color changed to black)
def draw_score(score):
    txt = font.render(f"Score: {score}", True, BLACK)
    win.blit(txt, (10, 10))

def place_food(snake_list):
    """Return a food (x,y) aligned to the grid and not on the snake."""
    while True:
        fx = random.randrange(0, WIDTH // SNAKE_SIZE) * SNAKE_SIZE
        fy = random.randrange(0, HEIGHT // SNAKE_SIZE) * SNAKE_SIZE
        if [fx, fy] not in snake_list:
            return fx, fy

def game_loop():
    game_over = False
    game_close = False

    x = (WIDTH // 2) // SNAKE_SIZE * SNAKE_SIZE
    y = (HEIGHT // 2) // SNAKE_SIZE * SNAKE_SIZE
    dx, dy = 0, 0
    snake_list = []
    snake_length = 1

    food_x, food_y = place_food(snake_list)
    clock = pygame.time.Clock()

    while not game_over:

        while game_close:
            win.blit(background_image, (0, 0))
            msg = font.render("Game Over! Press C to play again or Q to quit", True, (200,0,0))
            win.blit(msg, (WIDTH // 3, HEIGHT // 3))
            draw_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -SNAKE_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = SNAKE_SIZE, 0
                elif event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -SNAKE_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, SNAKE_SIZE

        x += dx
        y += dy

        # Boundary collision
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            game_close = True

        # Draw background and food
        win.blit(background_image, (0, 0))
        win.blit(food_image, (food_x, food_y))

        # Update snake body
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Self-collision
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # Draw snake and score
        draw_snake(snake_list)
        draw_score(snake_length - 1)
        pygame.display.update()

        # Food collision
        head_rect = pygame.Rect(x, y, SNAKE_SIZE, SNAKE_SIZE)
        food_rect = pygame.Rect(food_x, food_y, SNAKE_SIZE, SNAKE_SIZE)
        if head_rect.colliderect(food_rect):
            snake_length += 1
            food_x, food_y = place_food(snake_list)

        # Food moves slowly away after score threshold
        if snake_length - 1 >= RUNAWAY_SCORE:
            if x < food_x and food_x + SNAKE_SIZE < WIDTH:
                food_x += SNAKE_SIZE
            elif x > food_x and food_x - SNAKE_SIZE >= 0:
                food_x -= SNAKE_SIZE
            if y < food_y and food_y + SNAKE_SIZE < HEIGHT:
                food_y += SNAKE_SIZE
            elif y > food_y and food_y - SNAKE_SIZE >= 0:
                food_y -= SNAKE_SIZE

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_loop()
