
import pygame
import random

pygame.init()

# Screen size
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Snake Game")

print("Snake game started")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Block size (snake and food)
BLOCK_SIZE = 20

clock = pygame.time.Clock()
FPS = 10
speed = FPS

font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 60)

def message(text, color, x, y, use_title_font=False):
    msg_font = title_font if use_title_font else font
    msg = msg_font.render(text, True, color)
    screen.blit(msg, (x, y))

def game_over():
    screen.fill(BLACK)
    message("Game Over! Press Q to Quit or R to Restart", RED, 50, HEIGHT // 2 - 20)
    pygame.display.update()

def main_menu():
    in_menu = True
    while in_menu:
        screen.fill(BLACK)
        message("Block Snake Game", GREEN, WIDTH // 2 - 170, HEIGHT // 2 - 100, use_title_font=True)
        message("Press SPACE to Start", WHITE, WIDTH // 2 - 130, HEIGHT // 2)
        message("Press Q to Quit", WHITE, WIDTH // 2 - 100, HEIGHT // 2 + 40)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_menu = False
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    in_menu = False
                    main()  # Start the game
                elif event.key == pygame.K_q:
                    in_menu = False
                    pygame.quit()
                    return

def main():
    global speed
    snake_pos = [WIDTH // 2, HEIGHT // 2]
    snake_body = [[snake_pos[0], snake_pos[1]]]
    direction = "RIGHT"
    change_to = direction

    food_pos = [random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)]

    score = 0
    running = True
    game_end = False

    while running:
        while game_end:
            game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_end = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        game_end = False
                    if event.key == pygame.K_r:
                        speed = FPS
                        main()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    change_to = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    change_to = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    change_to = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    change_to = "RIGHT"

        direction = change_to

        # Move snake
        if direction == "UP":
            snake_pos[1] -= BLOCK_SIZE
        elif direction == "DOWN":
            snake_pos[1] += BLOCK_SIZE
        elif direction == "LEFT":
            snake_pos[0] -= BLOCK_SIZE
        elif direction == "RIGHT":
            snake_pos[0] += BLOCK_SIZE

        snake_body.insert(0, list(snake_pos))

        if snake_pos == food_pos:
            score += 1
            food_pos = [random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)]
            if speed < 25:
                speed += 1
        else:
            snake_body.pop()

        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

        for block in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(block[0], block[1], BLOCK_SIZE, BLOCK_SIZE))

        if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= HEIGHT):
            game_end = True

        for block in snake_body[1:]:
            if snake_pos == block:
                game_end = True

        message(f"Score: {score}", BLACK, 10, 10)

        pygame.display.update()
        clock.tick(speed)

    pygame.quit()

if __name__ == "__main__":
    main_menu()