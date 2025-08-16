#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Мини‑Pong
---------

* 2 игрока (или один + ИИ)
* простая графика (прямоугольники + круг)
* FPS 60
* клавиши:
    - «W» / «S» – игрок 1 (слева)
    - «UP» / «DOWN» – игрок 2 (справа)
"""

import pygame
import sys

# ---------- Константы ----------
WIDTH, HEIGHT = 800, 600          # размер окна
PADDLE_W, PADDLE_H = 10, 100      # размеры ракеток
BALL_R = 10                      # радиус шарика
PADDLE_SPEED = 5                 # скорость ракеток
BALL_SPEED_X = 4                 # начальная скорость шарика по x
BALL_SPEED_Y = 4                 # начальная скорость шарика по y
FPS = 60

# ---------- Инициализация pygame ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Мини‑Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# ---------- Объекты ----------
# Позиции (верхний левый угол) ракеток
paddle1 = pygame.Rect(30, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
paddle2 = pygame.Rect(WIDTH - 30 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)

# Шарик
ball = pygame.Rect(WIDTH // 2 - BALL_R, HEIGHT // 2 - BALL_R, BALL_R * 2, BALL_R * 2)
ball_dx, ball_dy = BALL_SPEED_X, BALL_SPEED_Y

# Очки
score1 = score2 = 0

# ---------- Функции ----------
def reset_ball():
    """Возвращаем шарик в центр и случайную начальную скорость."""
    global ball_dx, ball_dy
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_dx = BALL_SPEED_X if pygame.time.get_ticks() % 2 == 0 else -BALL_SPEED_X
    ball_dy = BALL_SPEED_Y if pygame.time.get_ticks() % 2 == 0 else -BALL_SPEED_Y

def move_paddles(keys):
    """Движение ракеток по клавишам. Обрабатываем коллизии с границами."""
    if keys[pygame.K_w] and paddle1.top > 0:
        paddle1.y -= PADDLE_SPEED
    if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
        paddle1.y += PADDLE_SPEED
    if keys[pygame.K_UP] and paddle2.top > 0:
        paddle2.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
        paddle2.y += PADDLE_SPEED

def ball_move():
    """Перемещаем шарик, обрабатываем столкновения с ракетками и границами."""
    global ball_dx, ball_dy, score1, score2

    ball.x += ball_dx
    ball.y += ball_dy

    # Столкновение с верхней/нижней границей
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1

    # Столкновение с ракетками
    if ball.colliderect(paddle1) and ball_dx < 0:
        ball_dx *= -1
    if ball.colliderect(paddle2) and ball_dx > 0:
        ball_dx *= -1

    # Выход за левую/правую границу – очко
    if ball.left <= 0:
        score2 += 1
        reset_ball()
    if ball.right >= WIDTH:
        score1 += 1
        reset_ball()

def draw():
    """Отрисовка всего экрана."""
    screen.fill((0, 0, 0))  # черный фон

    # Ракетки
    pygame.draw.rect(screen, (255, 255, 255), paddle1)
    pygame.draw.rect(screen, (255, 255, 255), paddle2)

    # Шарик
    pygame.draw.ellipse(screen, (255, 255, 255), ball)

    # Очки
    score_text = font.render(f"{score1} : {score2}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    pygame.display.flip()

# ---------- Основной цикл ----------
reset_ball()  # ставим шарик в центр в начале

while True:
    # ---------- События ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ---------- Логика ----------
    keys = pygame.key.get_pressed()
    move_paddles(keys)
    ball_move()

    # ---------- Отрисовка ----------
    draw()

    # ---------- FPS ----------
    clock.tick(FPS)
