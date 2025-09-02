import pygame
import sys
import datetime
import random
import time
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Перекидной календарь")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (220, 20, 60)
BLUE = (30, 144, 255)

# Шрифты
font_large = pygame.font.SysFont('Arial', 120, bold=True)
font_medium = pygame.font.SysFont('Arial', 60, bold=True)
font_small = pygame.font.SysFont('Arial', 30)

class CalendarPage:
    def __init__(self, date):
        self.date = date
        self.angle = 0
        self.flipping = False
        self.flip_progress = 0
        
    def draw(self, x, y, width, height):
        # Рисуем страницу календаря
        pygame.draw.rect(screen, WHITE, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Рисуем отверстия для перекидывания
        hole_radius = 5
        for i in range(3):
            pygame.draw.circle(screen, BLACK, (x + 20, y + height//4 + i*height//2), hole_radius)
            pygame.draw.circle(screen, BLACK, (x + width - 20, y + height//4 + i*height//2), hole_radius)
        
        # Отображаем дату
        day_text = font_large.render(str(self.date.day), True, RED)
        month_text = font_medium.render(self.date.strftime("%B"), True, BLACK)
        year_text = font_medium.render(str(self.date.year), True, BLUE)
        weekday_text = font_small.render(self.date.strftime("%A"), True, DARK_GRAY)
        
        screen.blit(day_text, (x + width//2 - day_text.get_width()//2, y + height//4))
        screen.blit(month_text, (x + width//2 - month_text.get_width()//2, y + height//2))
        screen.blit(year_text, (x + width//2 - year_text.get_width()//2, y + height//2 + 70))
        screen.blit(weekday_text, (x + width//2 - weekday_text.get_width()//2, y + height - 50))

def draw_background():
    # Градиентный фон
    for y in range(HEIGHT):
        color = (50, 50, 70 + y//20)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Рисуем тень под календарем
    shadow_surf = pygame.Surface((400, 600), pygame.SRCALPHA)
    shadow_surf.fill((0, 0, 0, 50))
    screen.blit(shadow_surf, (WIDTH//2 - 200 + 10, HEIGHT//2 - 300 + 10))

def main():
    clock = pygame.time.Clock()
    last_date = datetime.datetime.now().date()
    
    # Создаем текущую и следующую страницы
    current_page = CalendarPage(last_date)
    next_page = CalendarPage(last_date + datetime.timedelta(days=1))
    
    flip_timer = 0
    flip_interval = 5000  # 5 секунд между переворотами
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                running = False
        
        # Проверяем, нужно ли перевернуть страницу
        now = datetime.datetime.now().date()
        if now != last_date or (current_time - flip_timer > flip_interval and not current_page.flipping):
            current_page.flipping = True
            flip_timer = current_time
            last_date = now
            next_page = CalendarPage(now)
        
        # Обновляем анимацию переворота
        if current_page.flipping:
            current_page.flip_progress += 0.05
            if current_page.flip_progress >= 1:
                current_page.flipping = False
                current_page.flip_progress = 0
                current_page.date = next_page.date
        
        # Отрисовка
        screen.fill(BLACK)
        draw_background()
        
        # Позиция календаря
        calendar_x = WIDTH // 2 - 200
        calendar_y = HEIGHT // 2 - 300
        
        if current_page.flipping:
            # Анимация переворота
            progress = current_page.flip_progress
            if progress < 0.5:
                # Первая половина переворота - текущая страница поднимается
                scale = 1 - progress * 2
                current_page.draw(calendar_x, calendar_y, 400, 600)
            else:
                # Вторая половина - следующая страница опускается
                scale = (progress - 0.5) * 2
                next_page.draw(calendar_x, calendar_y, 400, 600)
        else:
            # Обычное отображение
            current_page.draw(calendar_x, calendar_y, 400, 600)
        
        # Отображаем текущее время
        time_text = font_small.render(datetime.datetime.now().strftime("%H:%M:%S"), True, WHITE)
        screen.blit(time_text, (20, HEIGHT - 40))
        
        # Инструкция для выхода
        exit_text = font_small.render("Нажмите любую клавишу или кнопку мыши для выхода", True, WHITE)
        screen.blit(exit_text, (WIDTH - exit_text.get_width() - 20, HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()