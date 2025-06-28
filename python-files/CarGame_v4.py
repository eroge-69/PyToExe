To convert the provided HTML and JavaScript code into Python, we can use the `pygame` library, which is well-suited for creating games and multimedia applications. Below is the Python equivalent of the given HTML and JavaScript code using `pygame`.

First, ensure you have `pygame` installed. You can install it using pip:

```sh
pip install pygame
```

Here is the Python code:

```python
import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Car dimensions
CAR_WIDTH = 50
CAR_HEIGHT = 100

# Game settings
enemy_speed_yellow = 5
enemy_speed_green = 2
enemy_interval = 1500
score = 0

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game")

# Load assets
player_car = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
player_car.fill(RED)

# Clock
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def game_over():
    draw_text("GAME OVER", font, RED, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
    pygame.display.flip()
    pygame.time.wait(2000)
    main()

def main():
    global score, enemy_speed_yellow, enemy_speed_green, enemy_interval

    # Player car settings
    car_x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
    car_y = SCREEN_HEIGHT - CAR_HEIGHT - 20
    move_left = False
    move_right = False

    # Enemies
    enemies = []

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move_left = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move_right = False

        # Move player car
        if move_left and not move_right:
            car_x -= 5
        if move_right and not move_left:
            car_x += 5

        car_x = max(0, min(SCREEN_WIDTH - CAR_WIDTH, car_x))

        # Create enemies
        if random.randint(0, enemy_interval) == 0:
            enemy_color = GREEN if score >= 60 else YELLOW
            enemy = pygame.Surface((CAR_WIDTH, CAR_HEIGHT))
            enemy.fill(enemy_color)
            enemy_x = random.randint(0, SCREEN_WIDTH - CAR_WIDTH)
            enemy_y = -CAR_HEIGHT
            enemies.append([enemy, enemy_x, enemy_y])

        # Move enemies
        for enemy in enemies:
            enemy[2] += enemy_speed_yellow if enemy[0].get_at((0, 0)) == YELLOW else enemy_speed_green
            if enemy[2] > SCREEN_HEIGHT:
                enemies.remove(enemy)
                score += 1
                if score == 30:
                    enemy_speed_yellow = int(enemy_speed_yellow * 1.1)
                    enemy_interval = 1300
                if score == 60:
                    enemy_speed_yellow = 7
                    enemy_interval = 900

        # Check for collisions
        for enemy in enemies:
            if (car_x < enemy[1] + CAR_WIDTH and
                car_x + CAR_WIDTH > enemy[1] and
                car_y < enemy[2] + CAR_HEIGHT and
                car_y + CAR_HEIGHT > enemy[2]):
                game_over()

        # Draw everything
        screen.fill(BLACK)
        screen.blit(player_car, (car_x, car_y))
        for enemy in enemies:
            screen.blit(enemy[0], (enemy[1], enemy[2]))
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
```

This Python code uses `pygame` to create a similar car game as described in the HTML and JavaScript code. The game includes a player-controlled car, enemy cars that move down the screen, and a scoring system. The game ends and restarts when the player car collides with an enemy car.