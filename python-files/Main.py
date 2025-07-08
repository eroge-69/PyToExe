import pygame
import math

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
HALF_HEIGHT = HEIGHT // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Doom-like")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Настройки игрока
player_x, player_y = 150, 150
player_angle = 0
player_speed = 3
rotation_speed = 0.05

# Карта (1 - стена, 0 - пустое пространство)
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

MAP_SIZE = len(game_map)
CELL_SIZE = 64

# Настройки raycasting
FOV = math.pi / 3  # Поле зрения (60 градусов)
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
STEP_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 800

# Текстуры (упрощенные)
wall_textures = {
    1: RED,
    2: GREEN,
    3: BLUE,
    4: WHITE
}

# Мини-карта
MINIMAP_SCALE = 0.2
MINIMAP_SIZE = int(MAP_SIZE * CELL_SIZE * MINIMAP_SCALE)
MINIMAP_POS = (10, 10)

def cast_rays():
    rays = []
    ray_angle = player_angle - HALF_FOV
    
    for ray in range(NUM_RAYS):
        # Проверка горизонтальных линий сетки
        y_intercept = (player_y // CELL_SIZE) * CELL_SIZE
        y_intercept += CELL_SIZE if math.sin(ray_angle) > 0 else 0
        
        x_horizontal = player_x + (y_intercept - player_y) / math.tan(ray_angle)
        y_step = CELL_SIZE
        y_step *= 1 if math.sin(ray_angle) > 0 else -1
        x_step = CELL_SIZE / math.tan(ray_angle)
        x_step *= 1 if (math.sin(ray_angle) > 0 and math.tan(ray_angle) > 0) or (math.sin(ray_angle) < 0 and math.tan(ray_angle) < 0) else -1
        
        next_horizontal_x = x_horizontal
        next_horizontal_y = y_intercept
        
        horizontal_wall_found = False
        horizontal_wall_x, horizontal_wall_y = 0, 0
        horizontal_wall_content = 0
        
        for i in range(MAX_DEPTH // CELL_SIZE):
            map_x = int(next_horizontal_x) // CELL_SIZE
            map_y = int(next_horizontal_y) // CELL_SIZE if math.sin(ray_angle) > 0 else (int(next_horizontal_y) // CELL_SIZE) - 1
            
            if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
                if game_map[map_y][map_x] != 0:
                    horizontal_wall_found = True
                    horizontal_wall_x = next_horizontal_x
                    horizontal_wall_y = next_horizontal_y
                    horizontal_wall_content = game_map[map_y][map_x]
                    break
                else:
                    next_horizontal_x += x_step
                    next_horizontal_y += y_step
            else:
                break
        
        # Проверка вертикальных линий сетки
        x_intercept = (player_x // CELL_SIZE) * CELL_SIZE
        x_intercept += CELL_SIZE if math.cos(ray_angle) > 0 else 0
        
        y_vertical = player_y + (x_intercept - player_x) * math.tan(ray_angle)
        x_step = CELL_SIZE
        x_step *= 1 if math.cos(ray_angle) > 0 else -1
        y_step = CELL_SIZE * math.tan(ray_angle)
        y_step *= 1 if (math.cos(ray_angle) > 0 and math.tan(ray_angle) > 0) or (math.cos(ray_angle) < 0 and math.tan(ray_angle) < 0) else -1
        
        next_vertical_x = x_intercept
        next_vertical_y = y_vertical
        
        vertical_wall_found = False
        vertical_wall_x, vertical_wall_y = 0, 0
        vertical_wall_content = 0
        
        for i in range(MAX_DEPTH // CELL_SIZE):
            map_x = int(next_vertical_x) // CELL_SIZE if math.cos(ray_angle) > 0 else (int(next_vertical_x) // CELL_SIZE) - 1
            map_y = int(next_vertical_y) // CELL_SIZE
            
            if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
                if game_map[map_y][map_x] != 0:
                    vertical_wall_found = True
                    vertical_wall_x = next_vertical_x
                    vertical_wall_y = next_vertical_y
                    vertical_wall_content = game_map[map_y][map_x]
                    break
                else:
                    next_vertical_x += x_step
                    next_vertical_y += y_step
            else:
                break
        
        # Выбор ближайшей стены
        if horizontal_wall_found and vertical_wall_found:
            horizontal_distance = math.sqrt((horizontal_wall_x - player_x) ** 2 + (horizontal_wall_y - player_y) ** 2)
            vertical_distance = math.sqrt((vertical_wall_x - player_x) ** 2 + (vertical_wall_y - player_y) ** 2)
            
            if horizontal_distance < vertical_distance:
                distance = horizontal_distance
                wall_x = horizontal_wall_x
                wall_y = horizontal_wall_y
                wall_content = horizontal_wall_content
                is_vertical = False
            else:
                distance = vertical_distance
                wall_x = vertical_wall_x
                wall_y = vertical_wall_y
                wall_content = vertical_wall_content
                is_vertical = True
        elif horizontal_wall_found:
            distance = math.sqrt((horizontal_wall_x - player_x) ** 2 + (horizontal_wall_y - player_y) ** 2)
            wall_x = horizontal_wall_x
            wall_y = horizontal_wall_y
            wall_content = horizontal_wall_content
            is_vertical = False
        elif vertical_wall_found:
            distance = math.sqrt((vertical_wall_x - player_x) ** 2 + (vertical_wall_y - player_y) ** 2)
            wall_x = vertical_wall_x
            wall_y = vertical_wall_y
            wall_content = vertical_wall_content
            is_vertical = True
        else:
            distance = MAX_DEPTH
            wall_content = 0
            is_vertical = False
        
        # Исправление "эффекта рыбьего глаза"
        distance *= math.cos(player_angle - ray_angle)
        
        # Расчет высоты стены
        wall_height = (CELL_SIZE * HEIGHT) / (distance + 0.0001)
        wall_height = min(wall_height, HEIGHT)
        
        rays.append({
            'distance': distance,
            'wall_height': wall_height,
            'wall_content': wall_content,
            'is_vertical': is_vertical,
            'ray_angle': ray_angle
        })
        
        ray_angle += STEP_ANGLE
    
    return rays

def draw_3d_view(rays):
    for i, ray in enumerate(rays):
        wall_height = ray['wall_height']
        wall_color = wall_textures.get(ray['wall_content'], WHITE)
        
        # Затемнение вертикальных стен для эффекта глубины
        if ray['is_vertical']:
            wall_color = tuple(max(0, c - 50) for c in wall_color)
        
        # Рисуем пол
        pygame.draw.rect(screen, DARK_GRAY, (i * 2, HALF_HEIGHT + wall_height // 2, 2, HEIGHT - (HALF_HEIGHT + wall_height // 2)))
        
        # Рисуем стену
        pygame.draw.rect(screen, wall_color, (i * 2, HALF_HEIGHT - wall_height // 2, 2, wall_height))
        
        # Рисуем потолок
        pygame.draw.rect(screen, GRAY, (i * 2, 0, 2, HALF_HEIGHT - wall_height // 2))

def draw_minimap():
    minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
    minimap_surface.fill(BLACK)
    
    # Рисуем карту
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if game_map[y][x] != 0:
                pygame.draw.rect(minimap_surface, WHITE, 
                                (x * CELL_SIZE * MINIMAP_SCALE, 
                                 y * CELL_SIZE * MINIMAP_SCALE, 
                                 CELL_SIZE * MINIMAP_SCALE, 
                                 CELL_SIZE * MINIMAP_SCALE))
    
    # Рисуем игрока
    player_minimap_x = player_x * MINIMAP_SCALE
    player_minimap_y = player_y * MINIMAP_SCALE
    pygame.draw.circle(minimap_surface, GREEN, (int(player_minimap_x), int(player_minimap_y)), 5)
    
    # Рисуем направление взгляда
    end_x = player_minimap_x + math.cos(player_angle) * 20
    end_y = player_minimap_y + math.sin(player_angle) * 20
    pygame.draw.line(minimap_surface, RED, 
                    (player_minimap_x, player_minimap_y), 
                    (end_x, end_y), 2)
    
    screen.blit(minimap_surface, MINIMAP_POS)

def check_collision(x, y):
    # Проверяем все 4 угла вокруг игрока
    for dx, dy in [(0, 0), (20, 0), (-20, 0), (0, 20), (0, -20)]:
        check_x = x + dx
        check_y = y + dy
        
        map_x = int(check_x) // CELL_SIZE
        map_y = int(check_y) // CELL_SIZE
        
        if 0 <= map_x < MAP_SIZE and 0 <= map_y < MAP_SIZE:
            if game_map[map_y][map_x] != 0:
                return True
    return False

# Основной игровой цикл
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Управление
    keys = pygame.key.get_pressed()
    
    # Поворот
    if keys[pygame.K_LEFT]:
        player_angle -= rotation_speed
    if keys[pygame.K_RIGHT]:
        player_angle += rotation_speed
    
    # Движение вперед/назад
    move_x = math.cos(player_angle) * player_speed
    move_y = math.sin(player_angle) * player_speed
    
    if keys[pygame.K_w]:
        new_x = player_x + move_x
        new_y = player_y + move_y
        if not check_collision(new_x, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y):
            player_y = new_y
    
    if keys[pygame.K_s]:
        new_x = player_x - move_x
        new_y = player_y - move_y
        if not check_collision(new_x, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y):
            player_y = new_y
    
    # Боковое движение
    if keys[pygame.K_a]:
        new_x = player_x - move_y
        new_y = player_y + move_x
        if not check_collision(new_x, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y):
            player_y = new_y
    
    if keys[pygame.K_d]:
        new_x = player_x + move_y
        new_y = player_y - move_x
        if not check_collision(new_x, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y):
            player_y = new_y
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Raycasting
    rays = cast_rays()
    
    # 3D вид
    draw_3d_view(rays)
    
    # Мини-карта
    draw_minimap()
    
    pygame.display.flip()

pygame.quit()