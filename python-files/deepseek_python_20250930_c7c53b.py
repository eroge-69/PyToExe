import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кликер игра")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Счётчик кликов
click_count = 0

# Параметры кликабельного объекта (красный круг)
object_radius = 50
object_x = WIDTH // 2
object_y = HEIGHT // 2
object_color = RED

# Шрифт для отображения счётчика
font = pygame.font.SysFont('Arial', 36)

def draw_object():
    """Рисует кликабельный объект"""
    pygame.draw.circle(screen, object_color, (object_x, object_y), object_radius)
    pygame.draw.circle(screen, BLACK, (object_x, object_y), object_radius, 2)

def draw_counter():
    """Рисует счётчик кликов"""
    counter_text = f"Кликов: {click_count}"
    text_surface = font.render(counter_text, True, BLUE)
    screen.blit(text_surface, (20, 20))

def is_click_on_object(pos):
    """Проверяет, был ли клик по объекту"""
    x, y = pos
    distance = ((x - object_x) ** 2 + (y - object_y) ** 2) ** 0.5
    return distance <= object_radius

def main():
    global click_count
    
    running = True
    while running:
        screen.fill(WHITE)
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if is_click_on_object(event.pos):
                        click_count += 1
                        # Можно добавить анимацию или звук при клике
                        print(f"Клик! Всего кликов: {click_count}")
        
        # Отрисовка
        draw_object()
        draw_counter()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()