import pygame
import math
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DOOM Python Port")
clock = pygame.time.Clock()

# Игровые константы
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 4
MAX_DEPTH = 16
PLAYER_SPEED = 0.05
ROTATION_SPEED = 0.05

# Настройки мини-карты
MAP_WIDTH = 10
MAP_HEIGHT = 10
MAP_CELL_SIZE = 6
MAP_X = SCREEN_WIDTH - MAP_WIDTH * MAP_CELL_SIZE - 10
MAP_Y = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
WALL_COLOR = (100, 100, 100)
WALL_DARK_COLOR = (70, 70, 70)
FLOOR_COLOR = (80, 80, 80)
CEILING_COLOR = (30, 30, 30)

# Игровой мир
map_data = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

# Положение игрока
player = {
    'x': 3.0,
    'y': 3.0,
    'angle': 0.0,
    'health': 100,
    'ammo': 50
}

# Противники
enemies = [
    {'x': 3.5, 'y': 3.5, 'health': 30, 'color': GREEN, 'type': "zombie"},
    {'x': 5.5, 'y': 5.5, 'health': 50, 'color': RED, 'type': "demon"}
]

# Оружие
weapon = {
    'damage': 25,
    'cooldown': 0,
    'max_cooldown': 10
}

# Шрифт для HUD
font = pygame.font.Font(None, 36)

def is_wall(x, y):
    """Проверка столкновения со стенами"""
    map_x, map_y = int(x), int(y)
    if map_x < 0 or map_x >= len(map_data[0]) or map_y < 0 or map_y >= len(map_data):
        return True
    return map_data[map_y][map_x] == 1

def cast_ray(angle):
    """Бросок луча DDA алгоритмом"""
    ray_x, ray_y = player['x'], player['y']
    ray_dir_x, ray_dir_y = math.cos(angle), math.sin(angle)
    
    map_x, map_y = int(ray_x), int(ray_y)
    
    if ray_dir_x == 0:
        delta_dist_x = float('inf')
    else:
        delta_dist_x = abs(1 / ray_dir_x)
        
    if ray_dir_y == 0:
        delta_dist_y = float('inf')
    else:
        delta_dist_y = abs(1 / ray_dir_y)
    
    if ray_dir_x < 0:
        step_x = -1
        side_dist_x = (ray_x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - ray_x) * delta_dist_x
    
    if ray_dir_y < 0:
        step_y = -1
        side_dist_y = (ray_y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - ray_y) * delta_dist_y
    
    hit = False
    side = 0
    
    # DDA алгоритм
    for _ in range(MAX_DEPTH):
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        if map_x < 0 or map_x >= len(map_data[0]) or map_y < 0 or map_y >= len(map_data):
            break
        
        if map_data[map_y][map_x] == 1:
            hit = True
            break
    
    if not hit:
        return float('inf'), side
    
    if side == 0:
        distance = (map_x - ray_x + (1 - step_x) / 2) / ray_dir_x
    else:
        distance = (map_y - ray_y + (1 - step_y) / 2) / ray_dir_y
    
    return distance, side

def render_3d_view():
    """Отрисовка 3D вида"""
    ray_width = SCREEN_WIDTH // NUM_RAYS
    
    for x in range(NUM_RAYS):
        screen_x = x * ray_width
        ray_angle = player['angle'] - HALF_FOV + (x / float(NUM_RAYS)) * FOV
        distance, side = cast_ray(ray_angle)
        
        if distance == float('inf'):
            continue
            
        # Коррекция искажения "рыбий глаз"
        distance = distance * math.cos(player['angle'] - ray_angle)
        
        # Высота стены
        wall_height = min(int(SCREEN_HEIGHT / distance), SCREEN_HEIGHT)
        
        # Позиция стены на экране
        wall_start = (SCREEN_HEIGHT - wall_height) // 2
        wall_end = wall_start + wall_height
        
        # Цвет стены
        if side == 1:
            color = WALL_DARK_COLOR
        else:
            color = WALL_COLOR
        
        # Отрисовка вертикальной линии
        pygame.draw.rect(screen, color, (screen_x, wall_start, ray_width, wall_height))
        
        # Отрисовка пола и потолка
        pygame.draw.rect(screen, CEILING_COLOR, (screen_x, 0, ray_width, wall_start))
        pygame.draw.rect(screen, FLOOR_COLOR, (screen_x, wall_end, ray_width, SCREEN_HEIGHT - wall_end))

def render_enemies():
    """Отрисовка врагов"""
    for enemy in enemies:
        if enemy['health'] > 0:
            # Вектор от игрока к врагу
            dx = enemy['x'] - player['x']
            dy = enemy['y'] - player['y']
            
            # Расстояние и угол
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) - player['angle']
            
            # Коррекция угла
            while angle < -math.pi:
                angle += 2 * math.pi
            while angle > math.pi:
                angle -= 2 * math.pi
            
            # Проверка, находится ли враг в поле зрения
            if abs(angle) < HALF_FOV and dist < 10:
                # Позиция на экране
                screen_x = int((angle + HALF_FOV) / FOV * SCREEN_WIDTH)
                size = max(20, int(100 / dist))
                screen_y = (SCREEN_HEIGHT - size) // 2
                
                # Отрисовка врага
                pygame.draw.rect(screen, enemy['color'], 
                               (screen_x - size//2, screen_y, size, size))

def draw_minimap():
    """Отрисовка мини-карты"""
    # Рамка мини-карты
    pygame.draw.rect(screen, DARK_GRAY, 
                    (MAP_X - 2, MAP_Y - 2, 
                     MAP_WIDTH * MAP_CELL_SIZE + 4, 
                     MAP_HEIGHT * MAP_CELL_SIZE + 4))
    
    # Вычисляем видимую область карты
    start_map_x = max(0, int(player['x']) - MAP_WIDTH // 2)
    start_map_y = max(0, int(player['y']) - MAP_HEIGHT // 2)
    
    # Отрисовка клеток карты
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            map_x = start_map_x + x
            map_y = start_map_y + y
            
            # Проверяем границы карты
            if map_y < len(map_data) and map_x < len(map_data[0]):
                if map_data[map_y][map_x] == 1:
                    color = LIGHT_GRAY  # стена
                else:
                    color = DARK_GRAY   # пол
            else:
                color = BLACK  # за пределами карты
            
            # Рисуем клетку
            pygame.draw.rect(screen, color,
                           (MAP_X + x * MAP_CELL_SIZE,
                            MAP_Y + y * MAP_CELL_SIZE,
                            MAP_CELL_SIZE, MAP_CELL_SIZE))
    
    # Отрисовка врагов на мини-карте
    for enemy in enemies:
        if enemy['health'] > 0:
            ex, ey = int(enemy['x']), int(enemy['y'])
            if (start_map_x <= ex < start_map_x + MAP_WIDTH and
                start_map_y <= ey < start_map_y + MAP_HEIGHT):
                mx = MAP_X + (ex - start_map_x) * MAP_CELL_SIZE
                my = MAP_Y + (ey - start_map_y) * MAP_CELL_SIZE
                pygame.draw.rect(screen, RED, (mx, my, MAP_CELL_SIZE, MAP_CELL_SIZE))
    
    # Отрисовка игрока на мини-карте
    px = MAP_X + (player['x'] - start_map_x) * MAP_CELL_SIZE
    py = MAP_Y + (player['y'] - start_map_y) * MAP_CELL_SIZE
    
    # Ограничиваем позицию игрока в пределах мини-карты
    px = max(MAP_X, min(MAP_X + MAP_WIDTH * MAP_CELL_SIZE - 1, px))
    py = max(MAP_Y, min(MAP_Y + MAP_HEIGHT * MAP_CELL_SIZE - 1, py))
    
    pygame.draw.circle(screen, GREEN, (int(px), int(py)), MAP_CELL_SIZE // 2)
    
    # Отрисовка направления взгляда игрока
    dx = math.cos(player['angle']) * MAP_CELL_SIZE
    dy = math.sin(player['angle']) * MAP_CELL_SIZE
    pygame.draw.line(screen, GREEN, (px, py), (px + dx, py + dy), 2)

def draw_hud():
    """Отрисовка HUD"""
    # Здоровье и патроны
    health_text = font.render("HEALTH: " + str(player['health']), True, RED)
    ammo_text = font.render("AMMO: " + str(player['ammo']), True, WHITE)
    
    screen.blit(health_text, (10, SCREEN_HEIGHT - 40))
    screen.blit(ammo_text, (200, SCREEN_HEIGHT - 40))
    
    # Оружие
    if weapon['cooldown'] > 0:
        color = LIGHT_GRAY
    else:
        color = WHITE
    
    # Простая отрисовка оружия
    pygame.draw.polygon(screen, color, [
        (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 30),
        (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 30),
        (SCREEN_WIDTH - 30, SCREEN_HEIGHT - 60),
        (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 60)
    ])

def handle_input():
    """Обработка ввода"""
    keys = pygame.key.get_pressed()
    move_x, move_y = 0, 0
    
    if keys[pygame.K_w]:
        move_x += math.cos(player['angle']) * PLAYER_SPEED
        move_y += math.sin(player['angle']) * PLAYER_SPEED
    if keys[pygame.K_s]:
        move_x -= math.cos(player['angle']) * PLAYER_SPEED
        move_y -= math.sin(player['angle']) * PLAYER_SPEED
    if keys[pygame.K_a]:
        move_x += math.cos(player['angle'] - math.pi/2) * PLAYER_SPEED
        move_y += math.sin(player['angle'] - math.pi/2) * PLAYER_SPEED
    if keys[pygame.K_d]:
        move_x += math.cos(player['angle'] + math.pi/2) * PLAYER_SPEED
        move_y += math.sin(player['angle'] + math.pi/2) * PLAYER_SPEED
    
    if keys[pygame.K_LEFT]:
        player['angle'] -= ROTATION_SPEED
    if keys[pygame.K_RIGHT]:
        player['angle'] += ROTATION_SPEED
    
    # Нормализация угла
    while player['angle'] < 0:
        player['angle'] += 2 * math.pi
    while player['angle'] > 2 * math.pi:
        player['angle'] -= 2 * math.pi
    
    # Проверка столкновений
    if not is_wall(player['x'] + move_x, player['y']):
        player['x'] += move_x
    if not is_wall(player['x'], player['y'] + move_y):
        player['y'] += move_y
    
    # Обработка выстрела
    if keys[pygame.K_SPACE] and weapon['cooldown'] == 0 and player['ammo'] > 0:
        weapon['cooldown'] = weapon['max_cooldown']
        player['ammo'] -= 1
        
        # Проверка попадания
        for enemy in enemies:
            if enemy['health'] > 0:
                dx = enemy['x'] - player['x']
                dy = enemy['y'] - player['y']
                angle = math.atan2(dy, dx)
                angle_diff = abs(angle - player['angle'])
                
                if angle_diff < 0.3 and math.sqrt(dx*dx + dy*dy) < 5:
                    enemy['health'] -= weapon['damage']
                    print("Попадание! У врага осталось " + str(enemy['health']) + " здоровья")
    
    if weapon['cooldown'] > 0:
        weapon['cooldown'] -= 1

def main():
    """Главный игровой цикл"""
    running = True
    
    print("DOOM Python Port")
    print("WASD - движение, стрелки - поворот, пробел - стрельба")
    print("ESC - выход")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        handle_input()
        
        # Очистка экрана
        screen.fill(BLACK)
        
        # Рендеринг
        render_3d_view()
        render_enemies()
        draw_minimap()
        draw_hud()
        
        pygame.display.flip()
        clock.tick(60)

# Запуск игры
if __name__ == "__main__":
    try:
        main()
    except:
        print("Произошла ошибка во время выполнения игры")
    pygame.quit()
    sys.exit()