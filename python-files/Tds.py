import pygame
import random
import math
import sys
import os

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы игры
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

# Загрузка шрифтов
try:
    font_small = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 48)
except:
    font_small = pygame.font.SysFont('arial', 24)
    font_medium = pygame.font.SysFont('arial', 36)
    font_large = pygame.font.SysFont('arial', 48)

# Структуры данных
class Enemy:
    def __init__(self, x, y, health, speed, enemy_type="normal"):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.speed = speed
        self.frozen = False
        self.freeze_time = 0
        self.path_index = 0
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        self.color = RED if enemy_type == "normal" else PURPLE
    
    def update(self, path):
        if self.frozen:
            self.freeze_time -= 1
            if self.freeze_time <= 0:
                self.frozen = False
            return
        
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            
            if abs(dx) > 0:
                self.x += self.speed * (1 if dx > 0 else -1)
            elif abs(dy) > 0:
                self.y += self.speed * (1 if dy > 0 else -1)
            
            if abs(self.x - target_x) < 0.1 and abs(self.y - target_y) < 0.1:
                self.path_index += 1
        
        self.rect.x = self.x * GRID_SIZE
        self.rect.y = self.y * GRID_SIZE
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Полоска здоровья
        health_width = (self.health / self.max_health) * GRID_SIZE
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 5, health_width, 3))
        
        # Тип врага
        if self.enemy_type == "boss":
            text = font_small.render("B", True, WHITE)
            surface.blit(text, (self.rect.x + 15, self.rect.y + 10))

class Tower:
    def __init__(self, x, y, damage, range_, fire_rate, color, cost, tower_type):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_
        self.fire_rate = fire_rate
        self.last_fire_time = 0
        self.color = color
        self.cost = cost
        self.tower_type = tower_type
        self.level = 1
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    
    def can_fire(self, current_time):
        return current_time - self.last_fire_time >= self.fire_rate
    
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.damage *= 1.5
            self.range += 0.5
            self.fire_rate *= 0.8
            return True
        return False
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Уровень башни
        level_text = font_small.render(str(self.level), True, WHITE)
        surface.blit(level_text, (self.rect.x + 15, self.rect.y + 15))

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed, damage, projectile_type="normal"):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.damage = damage
        self.projectile_type = projectile_type
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, 10, 10)
    
    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist <= self.speed:
            return True  # Попадание
        
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        self.rect.x = self.x * GRID_SIZE
        self.rect.y = self.y * GRID_SIZE
        return False
    
    def draw(self, surface):
        if self.projectile_type == "normal":
            pygame.draw.circle(surface, YELLOW, (self.rect.x + 5, self.rect.y + 5), 5)
        else:
            pygame.draw.circle(surface, BLUE, (self.rect.x + 5, self.rect.y + 5), 7)

# Игровые переменные
path = [(0, 5), (5, 5), (5, 2), (10, 2), (10, 8), (15, 8), (15, 5), (19, 5)]
enemies = []
towers = []
projectiles = []
player_health = 100
coins = 300
wave = 1
score = 0
selected_tower_type = None
show_range = False
range_pos = None
game_state = "playing"  # playing, game_over, victory
enemies_killed = 0
total_enemies_spawned = 0

# Типы башен
TOWER_TYPES = {
    'basic': {'damage': 20, 'range': 3, 'fire_rate': 1000, 'color': GREEN, 'cost': 50},
    'machine': {'damage': 10, 'range': 4, 'fire_rate': 500, 'color': BLUE, 'cost': 100},
    'rocket': {'damage': 40, 'range': 5, 'fire_rate': 2000, 'color': RED, 'cost': 150},
    'freezer': {'damage': 5, 'range': 3, 'fire_rate': 1500, 'color': PURPLE, 'cost': 120}
}

def spawn_enemy():
    global total_enemies_spawned
    
    if wave % 5 == 0 and total_enemies_spawned % 10 == 0:
        # Босс каждые 5 волн
        health = 200 + wave * 30
        speed = 0.03
        enemy_type = "boss"
    else:
        health = 50 + wave * 10
        speed = 0.05 + wave * 0.01
        enemy_type = "normal"
    
    enemy = Enemy(path[0][0], path[0][1], health, speed, enemy_type)
    enemies.append(enemy)
    total_enemies_spawned += 1

def can_place_tower(x, y):
    # Проверяем, можно ли поставить башню в этой позиции
    if (x, y) in path:
        return False
    
    for tower in towers:
        if tower.x == x and tower.y == y:
            return False
    
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)

def draw_path():
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        pygame.draw.line(screen, GRAY, 
                        (x1 * GRID_SIZE + GRID_SIZE // 2, y1 * GRID_SIZE + GRID_SIZE // 2),
                        (x2 * GRID_SIZE + GRID_SIZE // 2, y2 * GRID_SIZE + GRID_SIZE // 2), 20)

def draw_ui():
    # Статистика игры
    health_text = font_medium.render(f"Health: {player_health}", True, WHITE)
    coins_text = font_medium.render(f"Coins: {coins}", True, WHITE)
    wave_text = font_medium.render(f"Wave: {wave}", True, WHITE)
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    
    screen.blit(health_text, (10, 10))
    screen.blit(coins_text, (10, 50))
    screen.blit(wave_text, (10, 90))
    screen.blit(score_text, (10, 130))
    
    # Кнопки башен
    y_pos = HEIGHT - 120
    for i, (tower_type, stats) in enumerate(TOWER_TYPES.items()):
        button_color = stats['color'] if coins >= stats['cost'] else GRAY
        pygame.draw.rect(screen, button_color, (WIDTH - 150, y_pos + i * 60, 140, 50))
        pygame.draw.rect(screen, BLACK, (WIDTH - 150, y_pos + i * 60, 140, 50), 2)
        
        cost_text = font_small.render(f"{tower_type}", True, BLACK)
        price_text = font_small.render(f"${stats['cost']}", True, BLACK)
        
        screen.blit(cost_text, (WIDTH - 140, y_pos + i * 60 + 10))
        screen.blit(price_text, (WIDTH - 140, y_pos + i * 60 + 30))

def draw_range_preview():
    if show_range and range_pos:
        x, y = range_pos
        tower_stats = TOWER_TYPES[selected_tower_type]
        range_pixels = tower_stats['range'] * GRID_SIZE
        
        # Рисуем диапазон
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, 64), 
                          (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), 
                          range_pixels)
        screen.blit(surf, (0, 0))
        
        # Подсказка стоимости
        cost_text = font_small.render(f"Cost: ${tower_stats['cost']}", True, WHITE)
        screen.blit(cost_text, (x * GRID_SIZE, y * GRID_SIZE - 20))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font_large.render("GAME OVER", True, RED)
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_medium.render("Press R to restart", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

def draw_victory():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 100, 0, 180))
    screen.blit(overlay, (0, 0))
    
    victory_text = font_large.render("VICTORY!", True, GREEN)
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_medium.render("Press R to play again", True, WHITE)
    
    screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

def reset_game():
    global enemies, towers, projectiles, player_health, coins, wave, score
    global selected_tower_type, show_range, range_pos, game_state, enemies_killed, total_enemies_spawned
    
    enemies = []
    towers = []
    projectiles = []
    player_health = 100
    coins = 300
    wave = 1
    score = 0
    selected_tower_type = None
    show_range = False
    range_pos = None
    game_state = "playing"
    enemies_killed = 0
    total_enemies_spawned = 0

def main():
    global player_health, coins, wave, score, selected_tower_type, show_range, range_pos
    global game_state, enemies_killed
    
    running = True
    last_spawn_time = pygame.time.get_ticks()
    last_wave_time = pygame.time.get_ticks()
    spawn_interval = 2000  # 2 секунды между спавном врагов
    wave_duration = 30000  # 30 секунд на волну
    
    while running:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state != "playing":
                    reset_game()
                    continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
                # Проверяем клик по кнопкам башен
                y_pos = HEIGHT - 120
                for i, (tower_type, stats) in enumerate(TOWER_TYPES.items()):
                    button_rect = pygame.Rect(WIDTH - 150, y_pos + i * 60, 140, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        if coins >= stats['cost']:
                            selected_tower_type = tower_type
                            show_range = True
                        break
                
                # Размещение башни
                elif selected_tower_type and can_place_tower(grid_x, grid_y):
                    stats = TOWER_TYPES[selected_tower_type]
                    if coins >= stats['cost']:
                        towers.append(Tower(grid_x, grid_y, stats['damage'], 
                                          stats['range'], stats['fire_rate'],
                                          stats['color'], stats['cost'], selected_tower_type))
                        coins -= stats['cost']
                        selected_tower_type = None
                        show_range = False
                
                # Улучшение башни
                elif event.button == 3:  # Правая кнопка мыши
                    for tower in towers:
                        if tower.rect.collidepoint(mouse_x, mouse_y):
                            if coins >= tower.cost * 0.5:
                                if tower.upgrade():
                                    coins -= int(tower.cost * 0.5)
                            break
        
        if game_state == "playing":
            # Обновление позиции предпросмотра
            if selected_tower_type:
                range_pos = (grid_x, grid_y)
            
            # Спавн врагов
            enemies_to_spawn = min(5 + wave, 15)
            if (current_time - last_spawn_time > spawn_interval and 
                len(enemies) < enemies_to_spawn and 
                total_enemies_spawned < wave * 10):
                spawn_enemy()
                last_spawn_time = current_time
            
            # Смена волны
            if current_time - last_wave_time > wave_duration:
                wave += 1
                coins += 100
                last_wave_time = current_time
                total_enemies_spawned = 0
                
                # Победа после 20 волн
                if wave > 20:
                    game_state = "victory"
            
            # Обновление врагов
            for enemy in enemies[:]:
                enemy.update(path)
                if enemy.path_index >= len(path) - 1:
                    player_health -= 20 if enemy.enemy_type == "boss" else 10
                    enemies.remove(enemy)
                    
                    if player_health <= 0:
                        game_state = "game_over"
                        player_health = 0
            
            # Стрельба башен
            for tower in towers:
                if tower.can_fire(current_time):
                    closest_enemy = None
                    closest_dist = tower.range + 1
                    
                    for enemy in enemies:
                        dist = math.sqrt((enemy.x - tower.x)**2 + (enemy.y - tower.y)**2)
                        if dist <= tower.range and dist < closest_dist:
                            closest_dist = dist
                            closest_enemy = enemy
                    
                    if closest_enemy:
                        if tower.tower_type == "freezer":
                            closest_enemy.frozen = True
                            closest_enemy.freeze_time = 3000
                            projectile_type = "freeze"
                        else:
                            projectile_type = "normal"
                        
                        projectiles.append(Projectile(tower.x, tower.y, 
                                                     closest_enemy.x, closest_enemy.y,
                                                     0.1, tower.damage, projectile_type))
                        tower.last_fire_time = current_time
            
            # Обновление снарядов
            for projectile in projectiles[:]:
                if projectile.update():
                    for enemy in enemies[:]:
                        if abs(enemy.x - projectile.target_x) < 0.1 and abs(enemy.y - projectile.target_y) < 0.1:
                            enemy.health -= projectile.damage
                            if enemy.health <= 0:
                                coins += 50 if enemy.enemy_type == "boss" else 20
                                score += 200 if enemy.enemy_type == "boss" else 100
                                enemies_killed += 1
                                enemies.remove(enemy)
                            break
                    projectiles.remove(projectile)
        
        # Отрисовка
        screen.fill(BLACK)
        draw_grid()
        draw_path()
        
        if game_state == "playing":
            draw_range_preview()
            
            for tower in towers:
                tower.draw(screen)
            
            for enemy in enemies:
                enemy.draw(screen)
            
            for projectile in projectiles:
                projectile.draw(screen)
        
        draw_ui()
        
        if game_state == "game_over":
            draw_game_over()
        elif game_state == "victory":
            draw_victory()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
