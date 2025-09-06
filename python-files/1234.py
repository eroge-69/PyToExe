import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Фейерверк под курсором")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)

# Класс для частиц фейерверка
class Particle:
    def __init__(self, pos):
        self.x, self.y = pos
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -2)  # Летят вверх и разлетаются
        self.life = 30  # Длительность жизни
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Гравитация
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))  # Затухание
            color = (
                min(255, self.color[0] + 50),
                min(255, self.color[1] + 50),
                min(255, self.color[2] + 50)
            )
            size = max(1, self.life // 5)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)

# Список всех частиц
particles = []

# Основной цикл
running = True
while running:
    screen.fill(BLACK)  # Заливаем фон чёрным

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Вариант 1: Фейерверк при клике
    # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #     for _ in range(100):
    #         particles.append(Particle(event.pos))

    # Вариант 2: Фейерверк при движении мыши (без клика)
    mouse_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # Только при зажатой левой кнопке
        for _ in range(5):  # Можно увеличить количество частиц
            particles.append(Particle(mouse_pos))

    # Обновляем и рисуем частицы
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()