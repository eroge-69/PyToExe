import pygame
import sys
import os

pygame.init()
screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Слава России")
pygame.mouse.set_visible(False)  # Скрыть курсор

# Цвета флага России
BACKGROUND = (255, 255, 255)  # Белый
TEXT_COLOR = (0, 0, 0)  # Черный

# Шрифт
try:
    font = pygame.font.SysFont('arial', 150, bold=True)
except:
    try:
        font = pygame.font.SysFont('dejavusans', 150, bold=True)
    except:
        font = pygame.font.Font(None, 150)

# Главный цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
            # Блокируем все события закрытия
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_F4] and (event.mod & pygame.KMOD_ALT):
                    continue
            continue
    
    # Отрисовка текста
    screen.fill(BACKGROUND)
    text = font.render("СЛАВА РОССИИ", True, TEXT_COLOR)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()
