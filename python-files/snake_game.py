import pygame
import time
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 15
SNAKE_SIZE = 20
APPLE_SIZE = 20

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 40)


def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, [segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE])


def draw_apple(apple):
    pygame.draw.rect(screen, RED, [apple[0], apple[1], APPLE_SIZE, APPLE_SIZE])


def game_loop():
    snake = [[WIDTH / 2, HEIGHT / 2]]
    snake_direction = "RIGHT"

    apple = [random.randrange(0, WIDTH - APPLE_SIZE, APPLE_SIZE),
             random.randrange(0, HEIGHT - APPLE_SIZE, APPLE_SIZE)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_direction != "DOWN":
                    snake_direction = "UP"
                elif event.key == pygame.K_DOWN and snake_direction != "UP":
                    snake_direction = "DOWN"
                elif event.key == pygame.K_LEFT and snake_direction != "RIGHT":
                    snake_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and snake_direction != "LEFT":
                    snake_direction = "RIGHT"

        # Move the snake
        if snake_direction == "UP":
            snake[0][1] -= SNAKE_SIZE
        elif snake_direction == "DOWN":
            snake[0][1] += SNAKE_SIZE
        elif snake_direction == "LEFT":
            snake[0][0] -= SNAKE_SIZE
        elif snake_direction == "RIGHT":
            snake[0][0] += SNAKE_SIZE

        # Check for collisions with the walls
        if snake[0][0] >= WIDTH or snake[0][0] < 0 or snake[0][1] >= HEIGHT or snake[0][1] < 0:
            return

        # Check for collisions with itself
        for segment in snake[1:]:
            if snake[0] == segment:
                return

        # Check if the snake ate the apple
        if snake[0] == apple:
            snake.append([0, 0])
            apple = [random.randrange(0, WIDTH - APPLE_SIZE, APPLE_SIZE),
                     random.randrange(0, HEIGHT - APPLE_SIZE, APPLE_SIZE)]

        # Move the rest of the snake
        for i in range(len(snake) - 1, 