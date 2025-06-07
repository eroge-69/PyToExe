import pygame
import random
import sys

# Настройки
FONT_SIZE = 20
FPS = 30

# Инициализация
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Matrix Animation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Consolas', FONT_SIZE, bold=True)

# Символы и столбцы
symbols = [chr(i) for i in range(33, 127)]
columns = WIDTH // FONT_SIZE
drops = [random.randint(0, HEIGHT // FONT_SIZE) for _ in range(columns)]

# Цвета
green = (0, 255, 0)
black = (0, 0, 0)

# Основной цикл
running = True
while running:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    for i in range(columns):
        char = random.choice(symbols)
        char_surface = font.render(char, True, green)
        x = i * FONT_SIZE
        y = drops[i] * FONT_SIZE
        screen.blit(char_surface, (x, y))

        if y > HEIGHT or random.random() > 0.975:
            drops[i] = 0
        else:
            drops[i] += 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
