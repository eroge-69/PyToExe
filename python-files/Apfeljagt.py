# -*- coding: utf-8 -*-
"""
Created on Wed May 21 09:39:32 2025

@author: A143VU03
"""

import pgzrun
import random
import time
TITLE='Apfeljagt'


WIDTH = 800
HEIGHT = 600

snake_size = 20
snake = [(100, 100), (80, 100), (60, 100)]
direction = (20, 0)
score = 0
game_over = False
last_move = 0
move_delay = 0.2

food = Actor("apple1")
food.pos = (random.randint(0, WIDTH // 20 - 1) * 20 + 10,
            random.randint(0, HEIGHT // 20 - 1) * 20 + 10)

def draw():
    screen.clear()
    screen.fill("black")

    if game_over:
        screen.draw.text("Game Over", center=(400, 250), fontsize=50, color="red")
        screen.draw.text(f"Punkte: {score}", center=(400, 300), fontsize=30, color="white")
        screen.draw.text("Drücke eine Taste zum Neustarten", center=(400, 350), fontsize=25, color="white")
    else:
        for index in range(len(snake)):
            part = Actor("snakehead") if index == 0 else Actor("snakebody")
            part.topleft = snake[index]
            part.draw()
        food.draw()
        screen.draw.text(f"Punkte: {score}", topleft=(10, 10), fontsize=30, color="white")

def update():
    global game_over, last_move, score

    if game_over:
        return

    if time.time() - last_move < move_delay:
        return

    last_move = time.time()

    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])
    snake.insert(0, new_head)

    if check_collision(new_head, food.pos):
        score += 1
        food.pos = (random.randint(0, WIDTH // 20 - 1) * 20 + 10,
                    random.randint(0, HEIGHT // 20 - 1) * 20 + 10)
    else:
        snake.pop()

    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT or
        new_head in snake[1:]):
        game_over = True

def check_collision(a, b):
    return abs(a[0] + 10 - b[0]) < 20 and abs(a[1] + 10 - b[1]) < 20

def reset_game():
    global snake, direction, score, game_over
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = (20, 0)
    food.pos = (random.randint(0, WIDTH // 20 - 1) * 20 + 10,
                random.randint(0, HEIGHT // 20 - 1) * 20 + 10)
    score = 0
    game_over = False

def on_key_down(key):
    global direction

    if game_over:
        reset_game()
        return

    if key == keys.UP and direction != (0, 20):
        direction = (0, -20)
    elif key == keys.DOWN and direction != (0, -20):
        direction = (0, 20)
    elif key == keys.LEFT and direction != (20, 0):
        direction = (-20, 0)
    elif key == keys.RIGHT and direction != (-20, 0):
        direction = (20, 0)

pgzrun.go()
