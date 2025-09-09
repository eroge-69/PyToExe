import pygame
import pygame.gfxdraw
import sys
import math

# Инициализация Pygame
pygame.init()

# Цвета
BACKGROUND_COLOR = (15, 15, 25)
WINDOW_COLOR = (30, 30, 45)
ACCENT_COLOR = (80, 120, 220)
HOVER_COLOR = (100, 140, 240)
TEXT_COLOR = (230, 230, 250)
CHECKBOX_COLOR = (60, 60, 80)
CHECKBOX_CHECKED_COLOR = (90, 160, 250)
SLIDER_COLOR = (70, 70, 90)
SLIDER_HANDLE_COLOR = (100, 150, 250)
ERROR_COLOR = (220, 80, 80)

# Настройки окна
WIDTH, HEIGHT = 400, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SINEVKPC")

# Шрифты
title_font = pygame.font.SysFont("Arial", 28, bold=True)
font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)

# Состояния элементов
checkboxes = {
    "3D Box": False,
    "2D Box": False,
    "Skeleton": False,
    "Hat": False,
    "Tracer": False,
    "Enable": False,
    "Show aimbot FOV": False,
    "Auto fire": False,
    "Autowin": False
}

slider_value = 50  # Значение по умолчанию для ползунка
slider_dragging = False

# Функция для рисования скругленного прямоугольника
def draw_rounded_rect(surface, rect, color, corner_radius=10):
    """Draw a rectangle with rounded corners"""
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x + corner_radius, y, width - 2 * corner_radius, height))
    pygame.draw.rect(surface, color, (x, y + corner_radius, width, height - 2 * corner_radius))
    
    # Рисуем окружности в углах
    pygame.draw.circle(surface, color, (x + corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + width - corner_radius, y + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + corner_radius, y + height - corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (x + width - corner_radius, y + height - corner_radius), corner_radius)

# Функция для рисования красивого чекбокса
def draw_checkbox(surface, x, y, checked, text, hover=False):
    checkbox_rect = pygame.Rect(x, y, 20, 20)
    
    # Рисуем фон чекбокса
    if hover:
        pygame.draw.rect(surface, HOVER_COLOR, checkbox_rect, border_radius=5)
    else:
        pygame.draw.rect(surface, CHECKBOX_COLOR, checkbox_rect, border_radius=5)
    
    # Если отмечен, рисуем галочку
    if checked:
        pygame.draw.line(surface, CHECKBOX_CHECKED_COLOR, (x + 4, y + 10), (x + 8, y + 15), 3)
        pygame.draw.line(surface, CHECKBOX_CHECKED_COLOR, (x + 8, y + 15), (x + 16, y + 5), 3)
    
    # Рисуем текст
    text_surface = font.render(text, True, TEXT_COLOR)
    surface.blit(text_surface, (x + 30, y))
    
    return checkbox_rect

# Функция для рисования ползунка
def draw_slider(surface, x, y, width, value, text):
    # Рисуем текст
    text_surface = font.render(text, True, TEXT_COLOR)
    surface.blit(text_surface, (x, y - 25))
    
    # Рисуем фон ползунка
    slider_rect = pygame.Rect(x, y, width, 8)
    pygame.draw.rect(surface, SLIDER_COLOR, slider_rect, border_radius=4)
    
    # Рисуем заполненную часть
    fill_width = int((value / 100) * width)
    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, 8)
        pygame.draw.rect(surface, ACCENT_COLOR, fill_rect, border_radius=4)
    
    # Рисуем ручку ползунка
    handle_x = x + fill_width - 6
    handle_rect = pygame.Rect(handle_x, y - 6, 12, 20)
    pygame.draw.rect(surface, SLIDER_HANDLE_COLOR, handle_rect, border_radius=6)
    
    # Рисуем значение
    value_text = small_font.render(f"{value}%", True, TEXT_COLOR)
    surface.blit(value_text, (x + width + 10, y - 5))
    
    return handle_rect

# Функция для рисования кнопки закрытия
def draw_close_button(surface, x, y):
    button_rect = pygame.Rect(x, y, 30, 30)
    
    # Рисуем круглую кнопку
    pygame.draw.circle(surface, (220, 80, 80), (x + 15, y + 15), 15)
    
    # Рисуем крестик
    pygame.draw.line(surface, TEXT_COLOR, (x + 8, y + 8), (x + 22, y + 22), 2)
    pygame.draw.line(surface, TEXT_COLOR, (x + 22, y + 8), (x + 8, y + 22), 2)
    
    return button_rect

# Основной цикл
running = True
clock = pygame.time.Clock()
error_message = ""
error_time = 0

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверка чекбоксов
            for i, (key, value) in enumerate(checkboxes.items()):
                if i < 6:  # Первые 6 чекбоксов
                    checkbox_rect = pygame.Rect(50, 100 + i * 40, 20, 20)
                    if checkbox_rect.collidepoint(mouse_pos):
                        checkboxes[key] = not value
                
                elif checkboxes["Enable"]:  # Остальные чекбоксы, если Enable активен
                    checkbox_rect = pygame.Rect(50, 380 + (i-6) * 40, 20, 20)
                    if checkbox_rect.collidepoint(mouse_pos):
                        checkboxes[key] = not value
            
            # Проверка ползунка
            if checkboxes["Enable"]:
                handle_rect = pygame.Rect(50 + int((slider_value / 100) * 300) - 6, 345, 12, 20)
                if handle_rect.collidepoint(mouse_pos):
                    slider_dragging = True
            
            # Проверка кнопки закрытия
            close_rect = pygame.Rect(WIDTH - 40, 10, 30, 30)
            if close_rect.collidepoint(mouse_pos):
                running = False
        
        if event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
        
        if event.type == pygame.MOUSEMOTION:
            if slider_dragging and checkboxes["Enable"]:
                # Обновляем значение ползунка
                x_pos = max(50, min(mouse_pos[0], 350))
                slider_value = int(((x_pos - 50) / 300) * 100)
    
    # Проверка, все ли чекбоксы отмечены
    if all(checkboxes.values()) and error_message == "":
        error_message = "Ошибка: нельзя включать все функции одновременно!"
        error_time = pygame.time.get_ticks()
    
    # Очистка сообщения об ошибке через 3 секунды
    if error_message and pygame.time.get_ticks() - error_time > 3000:
        error_message = ""
    
    # Отрисовка фона
    window.fill(BACKGROUND_COLOR)
    
    # Отрисовка основного окна
    draw_rounded_rect(window, (20, 20, WIDTH - 40, HEIGHT - 40), WINDOW_COLOR, 15)
    
    # Отрисовка заголовка
    title_text = title_font.render("SINEVKPC", True, ACCENT_COLOR)
    window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))
    
    # Отрисовка чекбоксов
    for i, (key, value) in enumerate(checkboxes.items()):
        if i < 6:  # Первые 6 чекбоксов
            checkbox_rect = pygame.Rect(50, 100 + i * 40, 20, 20)
            hover = checkbox_rect.collidepoint(mouse_pos)
            draw_checkbox(window, 50, 100 + i * 40, value, key, hover)
    
    # Если Enable активен, отображаем дополнительные опции
    if checkboxes["Enable"]:
        # Рисуем разделитель
        pygame.draw.line(window, (60, 60, 80), (50, 340), (WIDTH - 50, 340), 2)
        
        # Рисуем ползунок
        handle_rect = draw_slider(window, 50, 365, 300, slider_value, "Aimbot FOV")
        
        # Рисуем дополнительные чекбоксы
        for i, (key, value) in enumerate(list(checkboxes.items())[6:]):
            checkbox_rect = pygame.Rect(50, 380 + i * 40, 20, 20)
            hover = checkbox_rect.collidepoint(mouse_pos)
            draw_checkbox(window, 50, 380 + i * 40, value, key, hover)
    
    # Рисуем кнопку закрытия
    close_rect = draw_close_button(window, WIDTH - 40, 10)
    
    # Отображение сообщения об ошибке
    if error_message:
        error_text = small_font.render(error_message, True, ERROR_COLOR)
        window.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT - 60))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()