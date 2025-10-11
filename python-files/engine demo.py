import pygame
import math

# === Настройки ===
WIDTH, HEIGHT = 400, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# === Простая модель куба ===
vertices = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
]

faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (0, 3, 7, 4),
]

def project(x, y, z):
    """Проекция 3D -> 2D"""
    f = 600 / (z + 5)
    x, y = x * f + WIDTH // 2, -y * f + HEIGHT // 2
    return int(x), int(y)

def draw_wireframe(angle):
    screen.fill(BLACK)
    rot_vertices = []
    for x, y, z in vertices:
        # Поворот по оси Y
        xz = x * math.cos(angle) - z * math.sin(angle)
        zz = x * math.sin(angle) + z * math.cos(angle)
        rot_vertices.append((xz, y, zz))
    
    for face in faces:
        points = [project(*rot_vertices[i]) for i in face]
        pygame.draw.polygon(screen, WHITE, points, 1)  # 1 = только линии

def fill_triangle(points, color):
    """Закраска треугольника (простая по точкам)"""
    pygame.draw.polygon(screen, color, points, 0)

# === Главный цикл ===
angle = 0
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    draw_wireframe(angle)
    # fill_triangle([(100, 100), (150, 200), (50, 200)], (0, 255, 0))  # пример заливки

    pygame.display.flip()
    clock.tick(30)
    angle += 0.03

pygame.quit()