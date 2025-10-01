import pygame
import math
import random
import os
import time
import json
import pickle

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix DOOM Clone")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
DARK_GRAY = (40, 40, 40)
BROWN = (139, 69, 19)
DARK_RED = (100, 0, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

# Автоматическое определение пути к рабочему столу
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
GAME_FOLDER = os.path.join(DESKTOP_PATH, "doom-clone")
ASSETS_FOLDER = os.path.join(GAME_FOLDER, "assets")
SAVES_FOLDER = os.path.join(GAME_FOLDER, "saves")

# Создаем папки если их нет
def create_game_folders():
    folders = [
        GAME_FOLDER,
        SAVES_FOLDER,
        os.path.join(ASSETS_FOLDER, "weapons"),
        os.path.join(ASSETS_FOLDER, "enemy"), 
        os.path.join(ASSETS_FOLDER, "items"),
        os.path.join(ASSETS_FOLDER, "bullets"),
        os.path.join(ASSETS_FOLDER, "tiles")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print(f"Game folders created at: {GAME_FOLDER}")

create_game_folders()

# Функция проверки текстур
def verify_textures():
    """Проверяет наличие всех необходимых текстур"""
    required_textures = [
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\cyberdemon.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\enemy.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\hellknight.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\overmind.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\bullets\\bullet.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\ammo.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\medkit.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\key.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\tiles\\floor_tech.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\weapons\\pistol.png",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\weapons\\shotgun.png"
    ]
    
    print("=== Texture Verification ===")
    for path in required_textures:
        if os.path.exists(path):
            print(f"✓ {os.path.basename(path)}")
        else:
            print(f"✗ {os.path.basename(path)} - NOT FOUND")
    print("============================")

verify_textures()

# Система сохранения прогресса
class SaveSystem:
    def __init__(self):
        self.save_file = os.path.join(SAVES_FOLDER, "game_save.dat")
        
    def save_game(self, game_data):
        try:
            with open(self.save_file, 'wb') as f:
                pickle.dump(game_data, f)
            print("Game progress saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'rb') as f:
                    game_data = pickle.load(f)
                print("Game progress loaded successfully!")
                return game_data
            else:
                print("No save file found. Starting new game.")
                return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

save_system = SaveSystem()

# Класс пули
class Bullet:
    def __init__(self, x, y, angle, damage, speed=0.3, range=15.0):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.range = range
        self.distance_traveled = 0
        self.active = True
        
    def update(self, delta_time, enemies, level):
        if not self.active:
            return False
            
        move_x = math.cos(self.angle) * self.speed
        move_y = math.sin(self.angle) * self.speed
        
        self.x += move_x
        self.y += move_y
        self.distance_traveled += math.sqrt(move_x**2 + move_y**2)
        
        # Проверка столкновения со стенами
        map_x, map_y = int(self.x), int(self.y)
        if (map_x < 0 or map_x >= len(level[0]) or 
            map_y < 0 or map_y >= len(level) or
            level[map_y][map_x] in [1, 4]):
            self.active = False
            return True
            
        # Проверка столкновения с врагами
        for enemy in enemies:
            if enemy.state == "dead" or not enemy.active:
                continue
                
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.5:  # Радиус столкновения
                enemy.take_damage(self.damage)
                self.active = False
                return True
                
        # Проверка дистанции
        if self.distance_traveled >= self.range:
            self.active = False
            return True
            
        return False

# Класс игрока для одиночной игры
class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.color = RED
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.speed = 0.1
        self.height = 0.5
        self.has_key = False
        self.current_weapon = "pistol"
        self.last_shot = 0
        self.score = 0
        self.kills = 0
        self.bullets = []
        
    def move(self, keys, level, delta_time):
        move_x, move_y = 0, 0
        current_speed = self.speed
        
        if keys[pygame.K_LSHIFT]:
            current_speed *= 2.0
        
        if keys[pygame.K_w]:
            move_x = math.cos(self.angle) * current_speed
            move_y = math.sin(self.angle) * current_speed
        if keys[pygame.K_s]:
            move_x = -math.cos(self.angle) * current_speed
            move_y = -math.sin(self.angle) * current_speed
        
        if keys[pygame.K_a]:
            move_x = math.cos(self.angle - math.pi/2) * current_speed
            move_y = math.sin(self.angle - math.pi/2) * current_speed
        if keys[pygame.K_d]:
            move_x = math.cos(self.angle + math.pi/2) * current_speed
            move_y = math.sin(self.angle + math.pi/2) * current_speed
        
        new_x = self.x + move_x
        new_y = self.y + move_y
        
        if not self.check_collision(new_x, new_y, level):
            self.x = new_x
            self.y = new_y
    
    def rotate_with_mouse(self, mouse_rel_x, sensitivity=0.002):
        self.angle += mouse_rel_x * sensitivity
        self.angle %= 2 * math.pi
    
    def check_collision(self, x, y, level):
        map_x, map_y = int(x), int(y)
        if (map_x < 0 or map_x >= len(level[0]) or 
            map_y < 0 or map_y >= len(level)):
            return True
        return level[map_y][map_x] in [1, 4]  # Стена или закрытая дверь
    
    def shoot(self, weapons, player_stats):
        current_weapon_obj = weapons[self.current_weapon]
        current_time = time.time()
        
        if (current_time - self.last_shot >= current_weapon_obj.cooldown and 
            current_weapon_obj.ammo > 0):
            
            current_weapon_obj.ammo -= 1
            self.last_shot = current_time
            
            # Создаем пулю
            damage = player_stats["damage"] + current_weapon_obj.damage
            bullet = Bullet(self.x, self.y, self.angle, damage)
            self.bullets.append(bullet)
            
            return True
        return False
    
    def update_bullets(self, delta_time, enemies, level):
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            if bullet.update(delta_time, enemies, level):
                bullets_to_remove.append(i)
        
        # Удаляем обработанные пули с конца
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)
    
    def switch_weapon(self, keys, weapons):
        if keys[pygame.K_1]:
            self.current_weapon = "pistol"
        elif keys[pygame.K_2]:
            self.current_weapon = "shotgun"
    
    def take_damage(self, damage):
        if self.armor > 0:
            armor_damage = min(damage * 0.7, self.armor)
            self.armor -= armor_damage
            damage -= armor_damage
        
        self.health -= damage
        return self.health <= 0
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def add_armor(self, amount):
        self.armor = min(100, self.armor + amount)
    
    def render_minimap(self, screen, offset_x, offset_y, scale):
        pygame.draw.circle(screen, self.color, 
                          (offset_x + int(self.x * scale), 
                           offset_y + int(self.y * scale)), 
                          4)
        
        end_x = offset_x + int(self.x * scale) + math.cos(self.angle) * 12
        end_y = offset_y + int(self.y * scale) + math.sin(self.angle) * 12
        pygame.draw.line(screen, WHITE, 
                        (offset_x + int(self.x * scale), offset_y + int(self.y * scale)), 
                        (end_x, end_y), 2)

# Создаем игрока
player = Player(1.5, 1.5, 0)

# Общие настройки
fov = math.pi / 3
has_key = False
current_level = 1
MAX_LEVELS = 10

# Новая система прокачки
player_health = 100
player_max_health = 100
player_armor = 0
player_max_armor = 100
doomcoins = 0
player_level = 1
player_experience = 0
experience_to_next_level = 100

# Характеристики игрока (прокачиваемые)
player_stats = {
    "damage": 10,
    "speed": 1.0,
    "health_regen": 0.1,
    "luck": 1.0,
}

# Система оружия
class Weapon:
    def __init__(self, name, damage, range, cooldown, ammo, texture_path, flash_color):
        self.name = name
        self.damage = damage
        self.range = range
        self.cooldown = cooldown
        self.ammo = ammo
        self.max_ammo = ammo
        self.last_shot = 0
        self.texture = self.load_texture(texture_path)
        self.flash_color = flash_color
        
    def load_texture(self, path):
        try:
            if os.path.exists(path):
                texture = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(texture, (200, 150))
            else:
                print(f"Weapon texture not found: {path}")
                return self.create_default_texture()
        except Exception as e:
            print(f"Error loading weapon texture {path}: {e}")
            return self.create_default_texture()
            
    def create_default_texture(self):
        surf = pygame.Surface((200, 150), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 100), (50, 50, 100, 50))
        return surf

# Создаем оружие
weapons = {
    "pistol": Weapon("Pistol", 15, 10.0, 0.8, 30, 
                    "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\weapons\\pistol.png", 
                    (255, 255, 200)),
    "shotgun": Weapon("Shotgun", 40, 5.0, 1.2, 12, 
                     "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\weapons\\shotgun.png", 
                     (255, 255, 0))
}

# Настройки мира
TILE_SIZE = 1

# Система биомов
class Biome:
    def __init__(self, name, floor_texture_path, wall_texture_path, ceiling_color, floor_color):
        self.name = name
        self.floor_texture = self.load_texture(floor_texture_path, floor_color, 64)
        self.wall_texture = self.load_texture(wall_texture_path, (100, 100, 100), 64)
        self.ceiling_color = ceiling_color
        self.floor_color = floor_color
        
    def load_texture(self, path, default_color, size):
        try:
            if os.path.exists(path):
                texture = pygame.image.load(path).convert()
                return pygame.transform.scale(texture, (size, size))
            else:
                print(f"Texture not found: {path}")
                # Создаем текстуру по умолчанию
                surf = pygame.Surface((size, size))
                surf.fill(default_color)
                if "hell" in path:
                    for i in range(20):
                        x, y = random.randint(0, size-1), random.randint(0, size-1)
                        pygame.draw.circle(surf, (255, 100, 0), (x, y), random.randint(2, 5))
                elif "grass" in path:
                    for i in range(30):
                        x, y = random.randint(0, size-1), random.randint(0, size-1)
                        color = (0, random.randint(100, 150), 0)
                        pygame.draw.circle(surf, color, (x, y), random.randint(1, 3))
                else:
                    for i in range(0, size, 16):
                        pygame.draw.line(surf, (80, 80, 80), (i, 0), (i, size), 1)
                        pygame.draw.line(surf, (80, 80, 80), (0, i), (size, i), 1)
                return surf
        except Exception as e:
            print(f"Error loading texture {path}: {e}")
            surf = pygame.Surface((size, size))
            surf.fill(default_color)
            return surf

# Создаем биомы
BIOMES = {
    "tech": Biome(
        "tech",
        "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\tiles\\floor_tech.png",
        os.path.join(ASSETS_FOLDER, "tiles", "wall_tech.png"),
        (30, 30, 40),
        (50, 50, 60)
    ),
    "hell": Biome(
        "hell", 
        os.path.join(ASSETS_FOLDER, "tiles", "floor_hell.png"),
        os.path.join(ASSETS_FOLDER, "tiles", "wall_hell.png"),
        (20, 0, 0),
        (80, 20, 0)
    ),
    "grass": Biome(
        "grass",
        os.path.join(ASSETS_FOLDER, "tiles", "floor_grass.png"),
        os.path.join(ASSETS_FOLDER, "tiles", "wall_grass.png"),
        (0, 20, 10),
        (30, 60, 20)
    ),
    "ice": Biome(
        "ice",
        os.path.join(ASSETS_FOLDER, "tiles", "floor_tech.png"),
        os.path.join(ASSETS_FOLDER, "tiles", "wall_tech.png"),
        (20, 20, 40),
        (60, 60, 80)
    ),
    "lava": Biome(
        "lava",
        os.path.join(ASSETS_FOLDER, "tiles", "floor_hell.png"),
        os.path.join(ASSETS_FOLDER, "tiles", "wall_hell.png"),
        (40, 0, 0),
        (100, 30, 0)
    )
}

# Автоматическое определение доступных текстур врагов
def get_available_enemy_textures():
    enemy_textures = {}
    
    # Сопоставление путей к файлам с типами врагов
    enemy_paths = {
        6: "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\enemy.png",
        7: "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\hellknight.png", 
        8: "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\cyberdemon.png",
        9: "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\enemy\\overmind.png"
    }
    
    for enemy_type, path in enemy_paths.items():
        if os.path.exists(path):
            enemy_textures[enemy_type] = path
            print(f"Loaded enemy texture: {os.path.basename(path)} -> type {enemy_type}")
        else:
            print(f"Enemy texture not found: {path}")
            # Создаем стандартную текстуру как запасной вариант
            enemy_textures[enemy_type] = f"default_enemy_{enemy_type}"
    
    return enemy_textures

available_enemies = get_available_enemy_textures()

# Класс врага с улучшенным ИИ и текстурами из папки
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.setup_enemy_stats()
        self.state = "patrol"
        self.last_attack_time = 0
        self.attack_cooldown = 1.5
        self.last_state_change = time.time()
        self.patrol_points = []
        self.current_patrol_index = 0
        self.last_known_player_pos = None
        self.search_time = 0
        self.texture = self.load_texture()
        self.active = True
        self.generate_patrol_points()
        
    def load_texture(self):
        if self.type in available_enemies:
            texture_path = available_enemies[self.type]
            
            # Если это путь к файлу
            if isinstance(texture_path, str) and os.path.exists(texture_path):
                try:
                    texture = pygame.image.load(texture_path).convert_alpha()
                    texture = pygame.transform.scale(texture, (64, 64))
                    print(f"Successfully loaded enemy texture: {os.path.basename(texture_path)}")
                    return texture
                except Exception as e:
                    print(f"Error loading enemy texture {texture_path}: {e}")
            else:
                print(f"Enemy texture path invalid or file missing: {texture_path}")
        
        # Создаем текстуру по умолчанию на основе типа
        print(f"Using default texture for enemy type {self.type}")
        return self.create_default_texture()
        
    def create_default_texture(self):
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        colors = {
            6: (0, 150, 0),    # Zombie - зеленый
            7: (150, 150, 150), # Soldier - серый
            8: (150, 0, 0),    # Boss - красный
            9: (100, 0, 150),  # Demon - фиолетовый
        }
        color = colors.get(self.type, (100, 100, 100))
        
        # Разные формы для разных типов врагов
        if self.type == 6:  # Zombie
            pygame.draw.circle(surf, color, (32, 32), 25)
            pygame.draw.circle(surf, (color[0]//2, color[1]//2, color[2]//2), (32, 32), 20)
        elif self.type == 7:  # Soldier
            pygame.draw.rect(surf, color, (16, 16, 32, 32))
            pygame.draw.rect(surf, (color[0]//2, color[1]//2, color[2]//2), (20, 20, 24, 24))
        elif self.type == 8:  # Boss
            pygame.draw.polygon(surf, color, [(32, 10), (10, 54), (54, 54)])
            pygame.draw.polygon(surf, (color[0]//2, color[1]//2, color[2]//2), [(32, 15), (15, 50), (49, 50)])
        elif self.type == 9:  # Demon
            pygame.draw.circle(surf, color, (32, 32), 30)
            pygame.draw.circle(surf, (color[0]//2, color[1]//2, color[2]//2), (32, 32), 20)
        else:  # Default
            pygame.draw.ellipse(surf, color, (10, 15, 44, 34))
            pygame.draw.ellipse(surf, (color[0]//2, color[1]//2, color[2]//2), (15, 20, 34, 24))
        
        return surf
        
    def setup_enemy_stats(self):
        # Базовые характеристики в зависимости от типа
        base_stats = {
            6: {"health": 50, "speed": 0.025, "damage": 15, "range": 1.5, "detection": 4.0, "reward": 10},
            7: {"health": 100, "speed": 0.035, "damage": 25, "range": 2.5, "detection": 6.0, "reward": 25},
            8: {"health": 200, "speed": 0.03, "damage": 40, "range": 3.0, "detection": 8.0, "reward": 100},
            9: {"health": 150, "speed": 0.04, "damage": 30, "range": 2.8, "detection": 7.0, "reward": 75},
        }
        
        stats = base_stats.get(self.type, base_stats[6])
        
        self.health = stats["health"]
        self.max_health = stats["health"]
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.attack_range = stats["range"]
        self.detection_range = stats["detection"]
        self.doomcoin_reward = stats["reward"]
        
        # Цвета для мини-карты
        colors = {
            6: (0, 150, 0),    # Zombie
            7: (150, 150, 150), # Soldier
            8: (150, 0, 0),    # Boss
            9: (100, 0, 150),  # Demon
        }
        self.color = colors.get(self.type, (100, 100, 100))
    
    def generate_patrol_points(self):
        self.patrol_points = [(self.x, self.y)]
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(2.0, 5.0)
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            self.patrol_points.append((px, py))
    
    def update(self, player, level_map, delta_time):
        if self.state == "dead" or not self.active:
            return
            
        if player.health <= 0:
            self.state = "patrol"
            self.patrol_behavior(level_map, delta_time)
            return
            
        player_x, player_y = player.x, player.y
        dx = player_x - self.x
        dy = player_y - self.y
        min_distance = math.sqrt(dx*dx + dy*dy)
        
        if min_distance <= self.detection_range and self.has_line_of_sight(player_x, player_y, level_map):
            self.last_known_player_pos = (player_x, player_y)
            self.search_time = time.time()
            
            if min_distance <= self.attack_range:
                self.state = "attack"
                self.attack_player(player, delta_time)
            else:
                self.state = "chase"
                self.chase_player(player_x, player_y, level_map, delta_time)
        else:
            if self.state == "chase" and self.last_known_player_pos:
                if time.time() - self.search_time < 5.0:
                    dx_search = self.last_known_player_pos[0] - self.x
                    dy_search = self.last_known_player_pos[1] - self.y
                    dist_search = math.sqrt(dx_search*dx_search + dy_search*dy_search)
                    
                    if dist_search > 0.5:
                        self.move_towards(self.last_known_player_pos[0], self.last_known_player_pos[1], level_map, delta_time)
                    else:
                        self.state = "search"
                        self.search_time = time.time() + 3.0
                else:
                    self.state = "patrol"
                    self.last_known_player_pos = None
            elif self.state == "search":
                if time.time() < self.search_time:
                    angle = random.uniform(0, 2 * math.pi)
                    search_x = self.x + math.cos(angle) * self.speed * delta_time * 40
                    search_y = self.y + math.sin(angle) * self.speed * delta_time * 40
                    if not self.check_collision(search_x, search_y, level_map):
                        self.x = search_x
                        self.y = search_y
                else:
                    self.state = "patrol"
            else:
                self.state = "patrol"
                self.patrol_behavior(level_map, delta_time)
    
    def has_line_of_sight(self, target_x, target_y, level_map):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return True
            
        steps = max(abs(int(dx * 10)), abs(int(dy * 10)))
        x_inc = dx / steps
        y_inc = dy / steps
        
        x, y = self.x, self.y
        for _ in range(steps):
            x += x_inc
            y += y_inc
            map_x, map_y = int(x), int(y)
            
            if (map_x < 0 or map_x >= len(level_map[0]) or 
                map_y < 0 or map_y >= len(level_map)):
                return False
                
            if level_map[map_y][map_x] in [1, 4]:
                return False
                
            current_dist = math.sqrt((x - self.x)**2 + (y - self.y)**2)
            if current_dist > self.detection_range:
                return False
                
        return True
    
    def move_towards(self, target_x, target_y, level_map, delta_time):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            move_x = (dx/distance) * self.speed * delta_time * 60
            move_y = (dy/distance) * self.speed * delta_time * 60
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if not self.check_collision(new_x, self.y, level_map):
                self.x = new_x
            if not self.check_collision(self.x, new_y, level_map):
                self.y = new_y
    
    def chase_player(self, player_x, player_y, level_map, delta_time):
        self.move_towards(player_x, player_y, level_map, delta_time)
    
    def patrol_behavior(self, level_map, delta_time):
        if not self.patrol_points:
            return
            
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.3:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            self.move_towards(target_x, target_y, level_map, delta_time)
    
    def attack_player(self, player, delta_time):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            player.take_damage(self.damage)
            self.last_attack_time = current_time
    
    def check_collision(self, x, y, level_map):
        map_x, map_y = int(x), int(y)
        if (map_x < 0 or map_x >= len(level_map[0]) or 
            map_y < 0 or map_y >= len(level_map)):
            return True
        return level_map[map_y][map_x] in [1, 4]
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.state = "dead"
            self.active = False
            return True
        else:
            self.state = "hurt"
            self.search_time = time.time() + 5.0
            return False
    
    def render_minimap(self, screen, offset_x, offset_y, scale):
        if self.state != "dead" and self.active:
            if self.state == "hurt":
                color = WHITE
            elif self.state == "chase":
                color = RED
            elif self.state == "attack":
                color = (255, 100, 0)
            elif self.state == "search":
                color = YELLOW
            else:
                color = self.color
                
            pygame.draw.circle(screen, color, 
                              (offset_x + int(self.x * scale), 
                               offset_y + int(self.y * scale)), 
                              max(3, int(4 * self.health / self.max_health)))

# Загрузка текстур предметов
def load_item_textures():
    textures = {}
    
    try:
        # Ключ
        key_path = "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\key.png"
        if os.path.exists(key_path):
            key = pygame.image.load(key_path).convert_alpha()
            textures[3] = pygame.transform.scale(key, (64, 64))
            print("Loaded key texture")
        else:
            print(f"Key texture not found: {key_path}")
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill(YELLOW)
            pygame.draw.circle(surf, (255, 215, 0), (32, 32), 15)
            textures[3] = surf
        
        # Аптечка
        medkit_path = "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\medkit.png"
        if os.path.exists(medkit_path):
            medkit = pygame.image.load(medkit_path).convert_alpha()
            textures[10] = pygame.transform.scale(medkit, (64, 64))
            print("Loaded medkit texture")
        else:
            print(f"Medkit texture not found: {medkit_path}")
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill(RED)
            pygame.draw.rect(surf, (200, 0, 0), (16, 16, 32, 32))
            textures[10] = surf
        
        # Патроны
        ammo_path = "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\items\\ammo.png"
        if os.path.exists(ammo_path):
            ammo = pygame.image.load(ammo_path).convert_alpha()
            textures[11] = pygame.transform.scale(ammo, (64, 64))
            print("Loaded ammo texture")
        else:
            print(f"Ammo texture not found: {ammo_path}")
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill((200, 200, 100))
            pygame.draw.rect(surf, (180, 180, 80), (20, 20, 24, 24))
            textures[11] = surf
        
        # Пуля
        bullet_path = "C:\\Users\\timab\\OneDrive\\Desktop\\doom-clone\\assets\\bullets\\bullet.png"
        if os.path.exists(bullet_path):
            bullet = pygame.image.load(bullet_path).convert_alpha()
            textures["bullet"] = pygame.transform.scale(bullet, (32, 32))
            print("Loaded bullet texture")
        else:
            print(f"Bullet texture not found: {bullet_path}")
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 0), (16, 16), 8)
            textures["bullet"] = surf
        
        # Дверь (оставляем генерацию)
        door_path = os.path.join(ASSETS_FOLDER, "tiles", "door.png")
        if os.path.exists(door_path):
            door = pygame.image.load(door_path).convert()
            textures[4] = pygame.transform.scale(door, (64, 64))
        else:
            surf = pygame.Surface((64, 64))
            surf.fill((139, 69, 19))
            textures[4] = surf
        
        # Телепорт (оставляем генерацию)
        teleport_path = os.path.join(ASSETS_FOLDER, "tiles", "teleport.png")
        if os.path.exists(teleport_path):
            teleport = pygame.image.load(teleport_path).convert()
            textures[5] = pygame.transform.scale(teleport, (64, 64))
        else:
            surf = pygame.Surface((64, 64))
            surf.fill((75, 0, 130))
            textures[5] = surf
        
    except Exception as e:
        print(f"Item texture loading error: {e}")
    
    return textures

item_textures = load_item_textures()

# Улучшенная генерация уровней с алгоритмом Prim
def generate_maze_level(width, height, level_num):
    """Генерация уровня с использованием алгоритма Prim для создания лабиринта"""
    # Инициализация уровня стенами
    level = [[1 for _ in range(width)] for _ in range(height)]
    
    # Выбор биома в зависимости от уровня
    biome_keys = list(BIOMES.keys())
    global current_biome
    current_biome = biome_keys[level_num % len(biome_keys)]
    
    # Алгоритм Prim для генерации лабиринта
    def prim_maze():
        # Начинаем с центральной точки
        start_x, start_y = width // 2, height // 2
        level[start_y][start_x] = 0
        
        # Список frontier клеток
        frontiers = []
        for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 < nx < width-1 and 0 < ny < height-1:
                frontiers.append((nx, ny, start_x, start_y))
        
        while frontiers:
            # Выбираем случайную frontier клетку
            fx, fy, px, py = frontiers.pop(random.randint(0, len(frontiers)-1))
            
            if level[fy][fx] == 1:
                # Делаем проход
                level[fy][fx] = 0
                level[(fy + py) // 2][(fx + px) // 2] = 0
                
                # Добавляем новые frontier клетки
                for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                    nx, ny = fx + dx, fy + dy
                    if 0 < nx < width-1 and 0 < ny < height-1 and level[ny][nx] == 1:
                        frontiers.append((nx, ny, fx, fy))
    
    # Генерируем лабиринт
    prim_maze()
    
    # Добавляем дополнительные проходы для уменьшения сложности
    for _ in range(width * height // 20):
        x, y = random.randint(1, width-2), random.randint(1, height-2)
        if level[y][x] == 1:
            # Проверяем соседей
            neighbors = 0
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                if level[y+dy][x+dx] == 0:
                    neighbors += 1
            if neighbors >= 2:
                level[y][x] = 0
    
    # Размещаем стартовую позицию для игрока
    spawn_x, spawn_y = 1, 1
    level[spawn_y][spawn_x] = 2
    
    # Размещаем телепорт в самом дальнем углу
    teleport_x, teleport_y = width-2, height-2
    level[teleport_y][teleport_x] = 5
    
    # Размещаем ключ
    key_placed = False
    for _ in range(100):
        kx, ky = random.randint(1, width-2), random.randint(1, height-2)
        if level[ky][kx] == 0 and abs(kx - spawn_x) + abs(ky - spawn_y) > 5:
            level[ky][kx] = 3
            key_placed = True
            break
    
    # Размещаем дверь между стартом и телепортом
    door_placed = False
    for _ in range(100):
        dx, dy = random.randint(width//3, 2*width//3), random.randint(height//3, 2*height//3)
        if level[dy][dx] == 0:
            level[dy][dx] = 4
            door_placed = True
            break
    
    # Размещаем предметы
    items_to_place = [
        (9, 5 + level_num * 2),  # Монеты
        (10, 2 + level_num),     # Аптечки
        (11, 3 + level_num)      # Патроны
    ]
    
    for item_type, count in items_to_place:
        placed = 0
        attempts = 0
        while placed < count and attempts < 50:
            x, y = random.randint(1, width-2), random.randint(1, height-2)
            if level[y][x] == 0:
                level[y][x] = item_type
                placed += 1
            attempts += 1
    
    print(f"Generated maze level {level_num} with biome: {current_biome}")
    return level, [(spawn_x + 0.5, spawn_y + 0.5)]

# Функция проверки проходимости уровня
def is_level_passable(level, start_pos, end_pos):
    width, height = len(level[0]), len(level)
    visited = [[False for _ in range(width)] for _ in range(height)]
    
    def dfs(x, y):
        if (x < 0 or x >= width or y < 0 or y >= height or 
            visited[y][x] or level[y][x] in [1, 4]):
            return False
            
        if (x, y) == end_pos:
            return True
            
        visited[y][x] = True
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            if dfs(x + dx, y + dy):
                return True
                
        return False
    
    start_x, start_y = int(start_pos[0]), int(start_pos[1])
    end_x, end_y = int(end_pos[0]), int(end_pos[1])
    
    return dfs(start_x, start_y)

# Генерация проходимого уровня
def generate_passable_level(width, height, level_num=1):
    max_attempts = 5
    
    for attempt in range(max_attempts):
        level, spawn_positions = generate_maze_level(width, height, level_num)
        
        teleport_x, teleport_y = width-2, height-2
        if is_level_passable(level, spawn_positions[0], (teleport_x, teleport_y)):
            print(f"Level {level_num} generated successfully (attempt {attempt + 1})")
            return level, spawn_positions
        else:
            print(f"Level {level_num} failed passability check (attempt {attempt + 1}), retrying...")
    
    # Fallback - простой уровень
    print("Using fallback level generation")
    level = [[1 for _ in range(width)] for _ in range(height)]
    for y in range(1, height-1):
        for x in range(1, width-1):
            level[y][x] = 0
    
    spawn_x, spawn_y = 1, 1
    level[spawn_y][spawn_x] = 2
    
    level[height-2][width-2] = 5
    
    return level, [(spawn_x + 0.5, spawn_y + 0.5)]

# Создание врагов для уровня
def create_enemies_for_level(level, level_num):
    enemies = []
    width, height = len(level[0]), len(level)
    
    # Количество врагов увеличивается с уровнем
    enemy_count = min(3 + level_num * 2, 12)
    
    # Доступные типы врагов
    available_types = list(available_enemies.keys())
    if not available_types:
        available_types = [6, 7, 8]  # Стандартные типы если нет текстур
    
    for _ in range(enemy_count):
        placed = False
        attempts = 0
        while not placed and attempts < 50:
            x = random.randint(1, width-2)
            y = random.randint(1, height-2)
            
            if (level[y][x] == 0 and 
                abs(x - 1) > 3 and abs(y - 1) > 3):
                
                # Выбор типа врага в зависимости от уровня
                if level_num >= 8 and random.random() < 0.3:
                    enemy_type = random.choice([t for t in available_types if t >= 9])
                elif level_num >= 5 and random.random() < 0.4:
                    enemy_type = random.choice([t for t in available_types if t >= 8])
                elif level_num >= 3 and random.random() < 0.5:
                    enemy_type = random.choice([t for t in available_types if t >= 7])
                else:
                    enemy_type = random.choice(available_types)
                
                enemies.append(Enemy(x + 0.5, y + 0.5, enemy_type))
                placed = True
            attempts += 1
    
    print(f"Created {len(enemies)} enemies for level {level_num}")
    return enemies

# Система прокачки
class UpgradeSystem:
    def __init__(self):
        self.upgrades = {
            "damage": {"name": "Damage", "cost": 50, "level": 1, "max_level": 10},
            "speed": {"name": "Speed", "cost": 40, "level": 1, "max_level": 5},
            "health": {"name": "Health", "cost": 60, "level": 1, "max_level": 5},
            "regen": {"name": "Regen", "cost": 70, "level": 1, "max_level": 5},
            "luck": {"name": "Luck", "cost": 30, "level": 1, "max_level": 10},
        }
    
    def can_upgrade(self, stat):
        upgrade = self.upgrades[stat]
        return (doomcoins >= upgrade["cost"] and 
                upgrade["level"] < upgrade["max_level"])
    
    def purchase_upgrade(self, stat):
        global doomcoins, player_max_health, player_speed, player_stats
        
        if self.can_upgrade(stat):
            upgrade = self.upgrades[stat]
            doomcoins -= upgrade["cost"]
            upgrade["level"] += 1
            upgrade["cost"] = int(upgrade["cost"] * 1.5)
            
            if stat == "damage":
                player_stats["damage"] += 5
            elif stat == "speed":
                player_stats["speed"] += 0.1
            elif stat == "health":
                player_max_health += 20
            elif stat == "regen":
                player_stats["health_regen"] += 0.1
            elif stat == "luck":
                player_stats["luck"] += 0.2
            
            return True
        return False
    
    def render_shop(self, screen):
        shop_x, shop_y = WIDTH - 250, 150
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 32)
        
        shop_bg = pygame.Surface((240, 300))
        shop_bg.fill((30, 30, 30))
        shop_bg.set_alpha(200)
        screen.blit(shop_bg, (shop_x, shop_y))
        
        title = title_font.render("DOOM SHOP", True, YELLOW)
        screen.blit(title, (shop_x + 70, shop_y + 10))
        
        coins_text = font.render(f"DOOMCOINS: {doomcoins}", True, YELLOW)
        screen.blit(coins_text, (shop_x + 10, shop_y + 50))
        
        y_offset = 90
        for stat, data in self.upgrades.items():
            color = GREEN if self.can_upgrade(stat) else RED
            level_text = f"{data['name']} Lvl {data['level']}/{data['max_level']}"
            cost_text = f"Cost: {data['cost']} DC"
            
            upgrade_text = font.render(level_text, True, WHITE)
            cost_render = font.render(cost_text, True, color)
            
            screen.blit(upgrade_text, (shop_x + 10, shop_y + y_offset))
            screen.blit(cost_render, (shop_x + 10, shop_y + y_offset + 25))
            
            y_offset += 55

# Создаем систему прокачки
upgrade_system = UpgradeSystem()

# Инициализация игры
def initialize_game():
    global levels, level_enemies, level, enemies, LEVEL_WIDTH, LEVEL_HEIGHT
    global current_level, doomcoins, player_experience, player_level
    global player_stats, has_key
    
    # Пытаемся загрузить сохранение
    saved_data = save_system.load_game()
    
    if saved_data:
        # Восстанавливаем состояние из сохранения
        levels = saved_data.get('levels', {})
        level_enemies = saved_data.get('level_enemies', {})
        current_level = saved_data.get('current_level', 1)
        player_stats = saved_data.get('player_stats', player_stats)
        doomcoins = saved_data.get('doomcoins', 0)
        player_experience = saved_data.get('player_experience', 0)
        player_level = saved_data.get('player_level', 1)
        player_max_health = saved_data.get('player_max_health', 100)
        
        # Загружаем текущий уровень
        if current_level in levels:
            level_data = levels[current_level]
            level = level_data[0]
            spawn_positions = level_data[1]
            
            # Устанавливаем позицию игрока
            if spawn_positions:
                player.x, player.y = spawn_positions[0]
                player.health = player.max_health
                player.armor = 0
                player.has_key = False
            
            enemies = level_enemies.get(current_level, [])
            LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)
            
            # Восстанавливаем оружие
            for weapon in weapons.values():
                weapon.ammo = weapon.max_ammo
                
            print(f"Loaded level {current_level} from save")
        else:
            generate_new_level()
    else:
        generate_new_level()

def generate_new_level():
    global levels, level_enemies, level, enemies, LEVEL_WIDTH, LEVEL_HEIGHT
    
    # Генерируем уровни если их нет
    for i in range(1, MAX_LEVELS + 1):
        if i not in levels:
            level_data = generate_passable_level(20, 15, i)
            levels[i] = level_data
            level_enemies[i] = create_enemies_for_level(level_data[0], i)
    
    # Устанавливаем текущий уровень
    level_data = levels[current_level]
    level = level_data[0]
    spawn_positions = level_data[1]
    
    # Устанавливаем позицию игрока
    if spawn_positions:
        player.x, player.y = spawn_positions[0]
        player.health = player.max_health
        player.armor = 0
        player.has_key = False
    
    enemies = level_enemies[current_level]
    LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)
    
    # Восстанавливаем оружие
    for weapon in weapons.values():
        weapon.ammo = weapon.max_ammo
        
    has_key = False

def save_game_progress():
    game_data = {
        'levels': levels,
        'level_enemies': level_enemies,
        'current_level': current_level,
        'player_stats': player_stats,
        'doomcoins': doomcoins,
        'player_experience': player_experience,
        'player_level': player_level,
        'player_max_health': player_max_health
    }
    save_system.save_game(game_data)

# Инициализация глобальных переменных
levels = {}
level_enemies = {}

# Запускаем инициализацию игры
initialize_game()

# Функция для получения текстуры с учетом биома и типа объекта
def get_wall_texture(hit_type, distance):
    if hit_type in item_textures:
        texture = item_textures[hit_type]
    else:
        texture = BIOMES[current_biome].wall_texture
    
    darken_factor = max(0.3, 1.0 - distance * 0.2)
    darkened = texture.copy()
    darkened.fill((int(255 * darken_factor),) * 3, special_flags=pygame.BLEND_MULT)
    return darkened

# Функция для получения текстуры пола
def get_floor_texture():
    return BIOMES[current_biome].floor_texture

# Система стрельбы
def shoot():
    global doomcoins, player_experience, muzzle_flash_time, muzzle_flash_color, screen_flash_time
    
    if player.shoot(weapons, player_stats):
        current_weapon_obj = weapons[player.current_weapon]
        muzzle_flash_time = time.time()
        muzzle_flash_color = current_weapon_obj.flash_color
        screen_flash_time = time.time()

# Проверка повышения уровня
def check_level_up():
    global player_level, player_experience, experience_to_next_level, doomcoins
    
    if player_experience >= experience_to_next_level:
        player_level += 1
        player_experience = 0
        experience_to_next_level = int(experience_to_next_level * 1.5)
        doomcoins += 50
        player_max_health += 10
        
        # Лечим игрока при повышении уровня
        player.max_health = player_max_health
        player.heal(10)
            
        print(f"Level Up! Now level {player_level}")

# Рендеринг врагов в 3D
def render_enemies():
    sorted_enemies = sorted([e for e in enemies if e.state != "dead" and e.active], 
                           key=lambda e: -(e.x - player.x)**2 - (e.y - player.y)**2)
    
    for enemy in sorted_enemies:
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:
            continue
            
        enemy_angle = math.atan2(dy, dx)
        angle_diff = enemy_angle - player.angle
        
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        if abs(angle_diff) < fov/2:
            screen_x = (angle_diff + fov/2) / fov * WIDTH
            screen_x = int(screen_x)
            
            sprite_height = int(HEIGHT / distance * 1.5)
            sprite_width = int(sprite_height * 0.8)
            
            if sprite_height > 0 and 0 <= screen_x < WIDTH:
                enemy_texture = enemy.texture
                scaled_texture = pygame.transform.scale(enemy_texture, (sprite_width, sprite_height))
                
                screen_y = HEIGHT//2 - sprite_height//2
                screen.blit(scaled_texture, (screen_x - sprite_width//2, screen_y))

# Рендеринг HUD с оружием
def render_hud():
    weapon = weapons[player.current_weapon]
    screen.blit(weapon.texture, (WIDTH - 220, HEIGHT - 160))
    
    font = pygame.font.Font(None, 24)
    weapon_text = font.render(f"{weapon.name}: {weapon.ammo}/{weapon.max_ammo}", True, WHITE)
    screen.blit(weapon_text, (WIDTH - 220, HEIGHT - 180))
    
    if time.time() - muzzle_flash_time < 0.1:
        flash_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        flash_surface.fill((*muzzle_flash_color, 150))
        screen.blit(flash_surface, (WIDTH - 250, HEIGHT - 200))

# Рендеринг прицела
def render_crosshair():
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    size = 15
    thickness = 2
    
    # Горизонтальные линии
    pygame.draw.line(screen, WHITE, (center_x - size, center_y), (center_x - size//3, center_y), thickness)
    pygame.draw.line(screen, WHITE, (center_x + size//3, center_y), (center_x + size, center_y), thickness)
    
    # Вертикальные линии
    pygame.draw.line(screen, WHITE, (center_x, center_y - size), (center_x, center_y - size//3), thickness)
    pygame.draw.line(screen, WHITE, (center_x, center_y + size//3), (center_x, center_y + size), thickness)
    
    # Центральная точка
    pygame.draw.circle(screen, RED, (center_x, center_y), 2)

# Эффект вспышки при выстреле
def render_screen_flash():
    if time.time() - screen_flash_time < 0.05:  # Очень короткая вспышка
        flash_surface = pygame.Surface((WIDTH, HEIGHT))
        flash_surface.fill(YELLOW)
        flash_surface.set_alpha(80)  # Полупрозрачный желтый
        screen.blit(flash_surface, (0, 0))

# Функция рендеринга с синхронизированной миникартой
def render():
    screen.fill(BLACK)
    
    biome = BIOMES[current_biome]
    
    ceiling_surface = pygame.Surface((WIDTH, HEIGHT // 2))
    ceiling_surface.fill(biome.ceiling_color)
    screen.blit(ceiling_surface, (0, 0))
    
    floor_texture = get_floor_texture()
    for y in range(HEIGHT // 2, HEIGHT):
        row_height = y - HEIGHT // 2
        darkness = 1.0 - (row_height / (HEIGHT // 2)) * 0.5
        
        scale_factor = 1.0 + (row_height / (HEIGHT // 2)) * 2.0
        scaled_width = int(WIDTH * scale_factor)
        scaled_height = int(64 * scale_factor)
        
        if scaled_width > 0 and scaled_height > 0:
            scaled_floor = pygame.transform.scale(floor_texture, (scaled_width, scaled_height))
            offset_x = (scaled_width - WIDTH) // 2
            screen.blit(scaled_floor, (-offset_x, y - scaled_height//2))
            
            dark_surface = pygame.Surface((WIDTH, 1))
            dark_surface.fill((0, 0, 0))
            dark_surface.set_alpha(int(255 * (1 - darkness)))
            screen.blit(dark_surface, (0, y))
    
    # Рейкастинг стен
    for x in range(WIDTH):
        ray_angle = player.angle - fov / 2 + (x / WIDTH) * fov
        ray_angle %= 2 * math.pi
        
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        
        map_x, map_y = int(player.x), int(player.y)
        
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player.x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player.x) * delta_dist_x
            
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player.y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player.y) * delta_dist_y
        
        hit = 0
        side = 0
        hit_type = 1
        
        while hit == 0:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            if map_x < 0 or map_x >= LEVEL_WIDTH or map_y < 0 or map_y >= LEVEL_HEIGHT:
                hit = 1
            else:
                cell_type = level[map_y][map_x]
                if cell_type != 0:
                    hit = 1
                    hit_type = cell_type
        
        if side == 0:
            perp_wall_dist = (map_x - player.x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - player.y + (1 - step_y) / 2) / ray_dir_y
        
        perp_wall_dist = max(0.1, perp_wall_dist)
        
        line_height = int(HEIGHT / perp_wall_dist)
        draw_start = max(-line_height // 2 + HEIGHT // 2, 0)
        draw_end = min(line_height // 2 + HEIGHT // 2, HEIGHT)
        
        if hit_type != 0:
            wall_texture = get_wall_texture(hit_type, perp_wall_dist)
            
            if side == 0:
                wall_x = player.y + perp_wall_dist * ray_dir_y
            else:
                wall_x = player.x + perp_wall_dist * ray_dir_x
            wall_x -= math.floor(wall_x)
            
            tex_x = int(wall_x * 64)
            if (side == 0 and ray_dir_x > 0) or (side == 1 and ray_dir_y < 0):
                tex_x = 64 - tex_x - 1
            
            if line_height > 0:
                texture_slice = wall_texture.subsurface(tex_x, 0, 1, 64)
                scaled_slice = pygame.transform.scale(texture_slice, (1, line_height))
                screen.blit(scaled_slice, (x, draw_start))
    
    render_enemies()
    render_hud()
    render_synchronized_minimap()
    render_interface()
    render_crosshair()
    render_screen_flash()

# Синхронизированная миникарта
def render_synchronized_minimap():
    map_scale = 8
    map_x_offset = 10
    map_y_offset = 10
    
    map_surface = pygame.Surface((LEVEL_WIDTH * map_scale + 2, LEVEL_HEIGHT * map_scale + 2))
    map_surface.fill(BLACK)
    map_surface.set_alpha(220)
    
    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            rect = pygame.Rect(
                x * map_scale,
                y * map_scale,
                map_scale, map_scale
            )
            
            cell_type = level[y][x]
            color = BLACK
            if cell_type == 1:
                color = WHITE
                pygame.draw.rect(map_surface, color, rect)
                pygame.draw.rect(map_surface, DARK_GRAY, rect, 1)
            elif cell_type == 2:
                color = GREEN
            elif cell_type == 3:
                color = YELLOW
            elif cell_type == 4:
                color = BROWN
            elif cell_type == 5:
                color = PURPLE
            elif cell_type == 9:
                color = YELLOW
            elif cell_type == 10:
                color = RED
            elif cell_type == 11:
                color = (200, 200, 100)
            
            if color != BLACK and cell_type != 1:
                pygame.draw.rect(map_surface, color, rect)
                pygame.draw.rect(map_surface, DARK_GRAY, rect, 1)
    
    for enemy in enemies:
        if enemy.state != "dead" and enemy.active:
            enemy.render_minimap(map_surface, 0, 0, map_scale)
    
    player.render_minimap(map_surface, 0, 0, map_scale)
    
    screen.blit(map_surface, (map_x_offset, map_y_offset))

# Рендеринг интерфейса
def render_interface():
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    large_font = pygame.font.Font(None, 32)
    
    # Общая информация
    level_text = large_font.render(f"Level: {player_level}", True, YELLOW)
    xp_text = font.render(f"XP: {player_experience}/{experience_to_next_level}", True, WHITE)
    coins_text = large_font.render(f"DOOMCOINS: {doomcoins}", True, YELLOW)
    biome_text = font.render(f"Biome: {current_biome.upper()}", True, WHITE)
    game_level_text = font.render(f"Game Level: {current_level}/{MAX_LEVELS}", True, CYAN)
    
    screen.blit(level_text, (WIDTH - 220, 20))
    screen.blit(xp_text, (WIDTH - 220, 50))
    screen.blit(coins_text, (WIDTH - 220, 80))
    screen.blit(biome_text, (WIDTH - 220, 110))
    screen.blit(game_level_text, (WIDTH - 220, 140))
    
    # Информация об игроке
    player_y_offset = 180
    status = "ALIVE" if player.health > 0 else "DEAD"
    player_text = font.render(f"Player: {status} HP: {int(player.health)}", True, RED)
    score_text = font.render(f"Score: {player.score} Kills: {player.kills}", True, RED)
    
    screen.blit(player_text, (WIDTH - 220, player_y_offset))
    screen.blit(score_text, (WIDTH - 220, player_y_offset + 25))
    
    damage_text = font.render(f"Damage: {player_stats['damage']}", True, RED)
    speed_text = font.render(f"Speed: {player_stats['speed']:.1f}x", True, BLUE)
    screen.blit(damage_text, (WIDTH - 220, player_y_offset + 55))
    screen.blit(speed_text, (WIDTH - 220, player_y_offset + 80))
    
    upgrade_system.render_shop(screen)
    
    legend_y = 10 + LEVEL_HEIGHT * 8 + 10
    legend = [
        ("Player", RED), ("Spawn", GREEN), ("Key", YELLOW), ("Door", BROWN),
        ("Teleport", PURPLE), ("Coin", YELLOW), ("Medkit", RED), ("Ammo", (200, 200, 100))
    ]
    
    for i, (text, color) in enumerate(legend):
        x_pos = 10 + i * 80
        legend_text = small_font.render(text, True, WHITE)
        pygame.draw.rect(screen, color, (x_pos, legend_y, 10, 10))
        screen.blit(legend_text, (x_pos + 15, legend_y - 2))
    
    controls_y = HEIGHT - 120
    controls = [
        "CONTROLS: WASD=Move, Mouse=Look/Aim, LMB=Shoot, Shift=Sprint",
        "1-2: Switch weapons, 1-5: Buy upgrades, R: Restart, G: New Level",
        "F5: Save, F9: Load, ESC: Quit"
    ]
    
    for i, control in enumerate(controls):
        control_text = small_font.render(control, True, WHITE)
        screen.blit(control_text, (10, controls_y + i * 15))
    
    if current_level == MAX_LEVELS:
        victory_text = font.render("FINAL LEVEL! Find the teleport to win!", True, YELLOW)
        screen.blit(victory_text, (WIDTH // 2 - 180, HEIGHT - 30))
    
    # Проверяем, жив ли игрок
    if player.health <= 0:
        game_over_text = large_font.render("GAME OVER! Press R to restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 30))

# Функция проверки столкновений и взаимодействий
def check_interaction(new_x, new_y):
    global has_key, current_level, level, enemies, LEVEL_WIDTH, LEVEL_HEIGHT
    global doomcoins, player_experience
    
    map_x, map_y = int(new_x), int(new_y)
    
    if map_x < 0 or map_x >= LEVEL_WIDTH or map_y < 0 or map_y >= LEVEL_HEIGHT:
        return True
    
    cell_type = level[map_y][map_x]
    
    if cell_type == 1:
        return True
    elif cell_type == 3:
        level[map_y][map_x] = 0
        player.has_key = True
        has_key = True
        return False
    elif cell_type == 4:
        if has_key:
            level[map_y][map_x] = 0
            has_key = False
            player.has_key = False
            return False
        else:
            return True
    elif cell_type == 5:
        if current_level < MAX_LEVELS:
            current_level += 1
            if current_level not in levels:
                level_data = generate_passable_level(LEVEL_WIDTH, LEVEL_HEIGHT, current_level)
                levels[current_level] = level_data
                level_enemies[current_level] = create_enemies_for_level(level_data[0], current_level)
            
            level_data = levels[current_level]
            level = level_data[0]
            spawn_positions = level_data[1]
            
            # Устанавливаем позицию игрока
            if spawn_positions:
                player.x, player.y = spawn_positions[0]
                player.health = player.max_health
                player.armor = 0
                player.has_key = False
            
            enemies = level_enemies[current_level]
            LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)
            has_key = False
            
            # Восстанавливаем оружие
            for weapon in weapons.values():
                weapon.ammo = weapon.max_ammo
                
            print(f"Advanced to level {current_level}")
        else:
            print("Congratulations! You've completed all levels!")
        return False
    elif cell_type == 9:
        level[map_y][map_x] = 0
        coin_amount = 5 + int(5 * player_stats["luck"])
        doomcoins += coin_amount
        player_experience += coin_amount
        player.score += coin_amount * 10
        check_level_up()
        return False
    elif cell_type == 10:
        level[map_y][map_x] = 0
        player.heal(25)
        return False
    elif cell_type == 11:
        level[map_y][map_x] = 0
        weapons[player.current_weapon].ammo = min(weapons[player.current_weapon].max_ammo, 
                                               weapons[player.current_weapon].ammo + 10)
        return False
    
    return False

# Главный игровой цикл
clock = pygame.time.Clock()
running = True
last_time = time.time()
muzzle_flash_time = 0
screen_flash_time = 0
muzzle_flash_color = (255, 255, 200)

# Скрываем курсор мыши
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)  # Захватываем мышь

print("=" * 50)
print("Matrix DOOM Clone - Single Player Edition")
print("=" * 50)
print(f"Game folder: {GAME_FOLDER}")
print(f"Assets folder: {ASSETS_FOLDER}")
print(f"Available enemies: {len(available_enemies)} types")
print(f"Current level: {current_level}/{MAX_LEVELS}")
print(f"Current biome: {current_biome}")
print("Controls: WASD, Mouse Look, LMB Shoot, LShift Sprint")
print("Controls: F5=Save, F9=Load, R=Restart, G=New Level")
print("=" * 50)

while running:
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    
    # Регенерация здоровья для игрока
    if player.health > 0 and player.health < player.max_health:
        player.health = min(player.max_health, 
                          player.health + player_stats["health_regen"] * delta_time)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                generate_new_level()
                print(f"Level {current_level} restarted")
            elif event.key == pygame.K_g:
                # Генерируем новый уровень
                level_data = generate_passable_level(20, 15, current_level)
                levels[current_level] = level_data
                level_enemies[current_level] = create_enemies_for_level(level_data[0], current_level)
                
                level_data = levels[current_level]
                level = level_data[0]
                spawn_positions = level_data[1]
                
                if spawn_positions:
                    player.x, player.y = spawn_positions[0]
                    player.health = player.max_health
                    player.armor = 0
                    player.has_key = False
                
                enemies = level_enemies[current_level]
                LEVEL_WIDTH, LEVEL_HEIGHT = len(level[0]), len(level)
                has_key = False
                
                for weapon in weapons.values():
                    weapon.ammo = weapon.max_ammo
                    
                print(f"Generated new level {current_level}")
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                if upgrade_system.purchase_upgrade("damage"):
                    print("Damage upgraded!")
            elif event.key == pygame.K_2:
                if upgrade_system.purchase_upgrade("speed"):
                    print("Speed upgraded!")
            elif event.key == pygame.K_3:
                if upgrade_system.purchase_upgrade("health"):
                    print("Health upgraded!")
            elif event.key == pygame.K_4:
                if upgrade_system.purchase_upgrade("regen"):
                    print("Regen upgraded!")
            elif event.key == pygame.K_5:
                if upgrade_system.purchase_upgrade("luck"):
                    print("Luck upgraded!")
            elif event.key == pygame.K_F5:
                save_game_progress()
            elif event.key == pygame.K_F9:
                initialize_game()  # Перезагружаем игру из сохранения
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                shoot()
        elif event.type == pygame.MOUSEMOTION:
            # Поворот игрока с помощью мыши
            player.rotate_with_mouse(event.rel[0])
    
    keys = pygame.key.get_pressed()
    
    # Обработка управления для игрока
    if player.health > 0:  # Только живые игроки могут двигаться
        player.move(keys, level, delta_time)
        player.switch_weapon(keys, weapons)
    
    # Обновление пуль
    player.update_bullets(delta_time, enemies, level)
    
    # Обновление врагов
    for enemy in enemies:
        enemy.update(player, level, delta_time)
    
    # Проверка смерти игрока
    if player.health <= 0:
        # Автоматический рестарт через 3 секунды
        if time.time() - last_time > 3.0:
            generate_new_level()
            print("Player died! Level restarted.")
    
    render()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()