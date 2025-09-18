import pygame
import sys
import math
import random
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки экрана
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Doom - PULIXER")

# Размеры игрового мира
WORLD_WIDTH = SCREEN_WIDTH * 3
WORLD_HEIGHT = SCREEN_HEIGHT * 3

# Камера
camera_x = WORLD_WIDTH // 2 - SCREEN_WIDTH // 2
camera_y = WORLD_HEIGHT // 2 - SCREEN_HEIGHT // 2

# Версия игры
GAME_VERSION = "1.0.0"

# Настройки игрока
player_gender = "male"  # По умолчанию мужской пол

# Уровни сложности с улучшенными параметрами
DIFFICULTY_LEVELS = {
    "Легкий": {
        "enemy_speed": 1.0, 
        "enemy_health": 20, 
        "enemy_count": 5, 
        "shielded_enemy_count": 1,
        "asteroid_count": 3, 
        "enemy_bullet_speed": 4, 
        "enemy_attack_range": 300,
        "accuracy": 0.4,
        "damage_multiplier": 1.0,
        "shielded_shoot_rate": 45
    },
    "Средний": {
        "enemy_speed": 1.5, 
        "enemy_health": 30, 
        "enemy_count": 8, 
        "shielded_enemy_count": 2,
        "asteroid_count": 5, 
        "enemy_bullet_speed": 5, 
        "enemy_attack_range": 350,
        "accuracy": 0.65,
        "damage_multiplier": 1.5,
        "shielded_shoot_rate": 35
    },
    "Сложный": {
        "enemy_speed": 2.0, 
        "enemy_health": 40, 
        "enemy_count": 12, 
        "shielded_enemy_count": 3,
        "asteroid_count": 8, 
        "enemy_bullet_speed": 6, 
        "enemy_attack_range": 400,
        "accuracy": 0.86,
        "damage_multiplier": 2.5,
        "shielded_shoot_rate": 25
    }
}
current_difficulty = "Средний"

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
DARK_BLUE = (0, 40, 85)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
BRIGHT_RED = (255, 50, 50)

# Шрифты
title_font = pygame.font.SysFont("Arial", 72, bold=True)
menu_font = pygame.font.SysFont("Arial", 42)
small_font = pygame.font.SysFont("Arial", 24)

# Состояния игры
MENU = 0
LOADING = 1
GAME = 2
SETTINGS = 3
DIFFICULTY_SELECT = 4
GAME_OVER = 5

# Текущее состояние
game_state = MENU

# Время для анимации
clock = pygame.time.Clock()
loading_progress = 0
loading_time = 0
menu_time = 0

# Эффекты попаданий
screen_shake = 0
hit_particles = []

# Загрузка звуков - ИСПРАВЛЕННАЯ ВЕРСИЯ
def load_sound(filename):
    """Функция для безопасной загрузки звуков"""
    try:
        # Пытаемся загрузить звук
        sound = pygame.mixer.Sound(filename)
        return sound
    except Exception as e:
        print(f"Ошибка загрузки звука {filename}: {e}")
        # Создаем заглушку для отсутствующего звука
        return None

# Создаем папку для звуков, если она не существует
if not os.path.exists("sounds"):
    os.makedirs("sounds")
    print("Создана папка sounds для звуковых файлов")

# Загружаем звуки
menu_ambient = load_sound("sounds/menu_ambient.wav")
game_music = load_sound("sounds/game_music.wav")
hit_sound = load_sound("sounds/hit.wav")
reload_sound = load_sound("sounds/reload.wav")

# Функция для загрузки лица главного героя
def load_player_face(gender):
    try:
        if gender == "female":
            face = pygame.image.load("player_face_female.png").convert_alpha()
        else:
            face = pygame.image.load("player_face_male.png").convert_alpha()
        face = pygame.transform.scale(face, (80, 80))
        return face
    except Exception as e:
        print(f"Ошибка загрузки изображения игрока: {e}")
        return None

# Загрузка лица игрока по умолчанию
player_face = load_player_face(player_gender)

# Класс для частиц эффектов
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size -= 0.1
        
    def draw(self, surface):
        alpha = min(255, self.lifetime * 6)
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

# Класс для анимированных кораблей в меню
class MenuShip:
    def __init__(self):
        self.x = -100
        self.y = random.randint(50, SCREEN_HEIGHT - 150)
        self.speed = random.uniform(2, 4)
        self.size = random.randint(15, 30)
        self.color = RED
        self.direction = random.choice([-1, 1])
        self.alpha = random.randint(100, 200)
        
        if self.direction == -1:
            self.x = SCREEN_WIDTH + 100
            
    def update(self):
        self.x += self.speed * self.direction
        
    def draw(self, surface):
        if self.direction == 1:
            points = [
                (self.x + self.size, self.y),
                (self.x - self.size//2, self.y - self.size//2),
                (self.x - self.size//2, self.y + self.size//2)
            ]
        else:
            points = [
                (self.x - self.size, self.y),
                (self.x + self.size//2, self.y - self.size//2),
                (self.x + self.size//2, self.y + self.size//2)
            ]
        
        ship_surface = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        pygame.draw.polygon(ship_surface, (*self.color, self.alpha), [
            (p[0] - self.x + self.size*1.5, p[1] - self.y + self.size*1.5) for p in points
        ])
        surface.blit(ship_surface, (self.x - self.size*1.5, self.y - self.size*1.5))
        
    def is_off_screen(self):
        if self.direction == 1:
            return self.x > SCREEN_WIDTH + 100
        else:
            return self.x < -100

# Список кораблей в меню
menu_ships = []

# Загрузка фонового изображения для меню
def load_menu_background():
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(BLACK)
    
    for _ in range(2000):
        x = random.randint(0, SCREEN_WIDTH - 1)
        y = random.randint(0, SCREEN_HEIGHT - 1)
        brightness = random.randint(100, 255)
        size = random.randint(1, 2)
        pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), size)
    
    return background

menu_background = load_menu_background()

# Создание игрового фона
def create_game_background():
    background = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    background.fill(BLACK)
    
    for _ in range(5000):
        x = random.randint(0, WORLD_WIDTH - 1)
        y = random.randint(0, WORLD_HEIGHT - 1)
        brightness = random.randint(100, 255)
        background.set_at((x, y), (brightness, brightness, brightness))
    
    return background

game_background = create_game_background()

# Класс для кнопок меню
class Button:
    def __init__(self, text, y_offset, width=300, height=50):
        self.text = text
        self.y_offset = y_offset
        self.color = WHITE
        self.hover_color = BLUE
        self.current_color = self.color
        self.width = width
        self.height = height
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - width//2, SCREEN_HEIGHT//2 + y_offset, width, height)
        
    def draw(self, surface):
        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.current_color, self.rect, 3, border_radius=10)
        
        text_surf = menu_font.render(self.text, True, self.current_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False

# Класс для переключателей в настройки
class ToggleButton:
    def __init__(self, text, y_offset, width=400, height=50, options=["Выкл", "Вкл"], default_index=0):
        self.text = text
        self.y_offset = y_offset
        self.width = width
        self.height = height
        self.options = options
        self.current_index = default_index
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - width//2, SCREEN_HEIGHT//2 + y_offset, width, height)
        self.color = WHITE
        self.hover_color = BLUE
        
    def draw(self, surface):
        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.color, self.rect, 3, border_radius=10)
        
        # Текст настройки
        text_surf = small_font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Текущее значение
        value_text = small_font.render(self.options[self.current_index], True, YELLOW)
        value_rect = value_text.get_rect(midright=(self.rect.right - 10, self.rect.centery))
        surface.blit(value_text, value_rect)
        
    def check_hover(self, pos):
        return self.rect.collidepoint(pos)
        
    def toggle(self):
        self.current_index = (self.current_index + 1) % len(self.options)
        return self.current_index

# Создание кнопок меню
start_button = Button("Начать игру", -50)
settings_button = Button("Настройки", 25)
difficulty_button = Button("Уровень сложности", 100)
exit_button = Button("Выйти из игры", 175)

# Кнопки для экрана выбора сложности
easy_button = Button("Легкий", -100)
medium_button = Button("Средний", -25)
hard_button = Button("Сложный", 50)
back_button = Button("Назад", 125)

# Переключатели для настроек
gender_toggle = ToggleButton("Пол игрока", -50, options=["Мужской", "Женский"], default_index=0)
back_settings_button = Button("Назад", 150)

# Класс для игрока
class Player:
    def __init__(self):
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.radius = 25
        self.speed = 3
        self.color = WHITE
        self.health = 100
        self.max_health = 100
        self.weapons = ["Лазерная пушка"]
        self.current_weapon = 0
        self.score = 0
        self.kills = 0
        self.hit_count = 0  # Счетчик попаданий (только для статистики)
        self.ammo = 20  # Ограничение патронов
        self.max_ammo = 20
        self.reloading = False
        self.reload_time = 0
        self.reload_duration = 180  # 3 секунды при 60 FPS
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            points = [
                (screen_x + self.radius, screen_y),
                (screen_x - self.radius//2, screen_y - self.radius),
                (screen_x - self.radius//2, screen_y + self.radius)
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, BLUE, points, 2)
        
    def move(self, keys):
        if keys[pygame.K_a] and self.x - self.radius > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x + self.radius < WORLD_WIDTH:
            self.x += self.speed
        if keys[pygame.K_w] and self.y - self.radius > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y + self.radius < WORLD_HEIGHT:
            self.y += self.speed
            
    def take_damage(self, amount):
        self.health -= amount
        self.hit_count += 1  # Только для статистики, не для определения смерти
        global screen_shake, hit_particles
        
        # Эффект тряски экрана
        screen_shake = 10
        
        # Создание частиц эффекта попадания
        for _ in range(15):
            hit_particles.append(Particle(self.x, self.y, RED))
            
        # Проигрывание звука попадания
        if hit_sound:
            hit_sound.play()
            
        if self.health < 0:
            self.health = 0
            
    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
            
    def reload(self):
        if not self.reloading and self.ammo < self.max_ammo:
            self.reloading = True
            self.reload_time = self.reload_duration
            if reload_sound:
                reload_sound.play()
                
    def update_reload(self):
        if self.reloading:
            self.reload_time -= 1
            if self.reload_time <= 0:
                self.ammo = self.max_ammo
                self.reloading = False

# Класс для пуль игрока
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        
        angle = math.atan2(target_y - y, target_x - x)
        self.speed = 10
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        self.color = GREEN
        self.radius = 3
        self.damage = 15
            
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(screen_x), int(screen_y)), self.radius - 1, 1)
        
    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > WORLD_WIDTH or self.y < 0 or self.y > WORLD_HEIGHT)

# Класс для пуль врагов
class EnemyBullet:
    def __init__(self, x, y, target_x, target_y, speed, damage):
        self.x = x
        self.y = y
        
        angle = math.atan2(target_y - y, target_x - x)
        self.speed = speed
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
        self.color = RED
        self.radius = 4
        self.damage = damage
            
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.radius)
        
    def is_out_of_bounds(self):
        return (self.x < 0 or self.x > WORLD_WIDTH or self.y < 0 or self.y > WORLD_HEIGHT)

# Класс для врагов
class Enemy:
    def __init__(self, difficulty="Средний"):
        self.radius = 20
        
        margin = 200
        self.x = random.randint(margin, WORLD_WIDTH - margin)
        self.y = random.randint(margin, WORLD_HEIGHT - margin)
        
        difficulty_settings = DIFFICULTY_LEVELS[difficulty]
        self.speed = difficulty_settings["enemy_speed"]
        self.health = difficulty_settings["enemy_health"]
        self.bullet_speed = difficulty_settings["enemy_bullet_speed"]
        self.attack_range = difficulty_settings["enemy_attack_range"]
        self.accuracy = difficulty_settings["accuracy"]
        self.damage_multiplier = difficulty_settings["damage_multiplier"]
        self.max_health = self.health
        
        self.color = RED
        self.attack_cooldown = 0
        self.attack_rate = 90
        self.shoot_cooldown = 0
        self.shoot_rate = 60
        
        self.state = "patrol"
        self.patrol_timer = random.randint(60, 180)
        self.patrol_dx = random.uniform(-1, 1)
        self.patrol_dy = random.uniform(-1, 1)
        self.evade_timer = 0
        
    def update(self, player, bullets):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        bullet_near = False
        for bullet in bullets:
            bullet_dx = bullet.x - self.x
            bullet_dy = bullet.y - self.y
            bullet_dist = math.sqrt(bullet_dx*bullet_dx + bullet_dy*bullet_dy)
            
            if bullet_dist < 150:
                bullet_near = True
                self.state = "evade"
                self.evade_timer = 30
                evade_angle = math.atan2(bullet_dy, bullet_dx) + math.pi
                self.x += math.cos(evade_angle) * self.speed * 1.5
                self.y += math.sin(evade_angle) * self.speed * 1.5
                break
        
        if not bullet_near:
            if self.evade_timer > 0:
                self.evade_timer -= 1
            else:
                if distance < self.attack_range:
                    self.state = "chase"
                    angle = math.atan2(dy, dx)
                    self.x += math.cos(angle) * self.speed
                    self.y += math.sin(angle) * self.speed
                    
                    if distance < self.attack_range * 0.6:
                        self.state = "attack"
                else:
                    self.state = "patrol"
                    self.patrol_timer -= 1
                    if self.patrol_timer <= 0:
                        self.patrol_timer = random.randint(60, 180)
                        self.patrol_dx = random.uniform(-1, 1)
                        self.patrol_dy = random.uniform(-1, 1)
                    
                    self.x += self.patrol_dx * self.speed * 0.5
                    self.y += self.patrol_dy * self.speed * 0.5
                    
                    if self.x < 0 or self.x > WORLD_WIDTH or self.y < 0 or self.y > WORLD_HEIGHT:
                        self.patrol_dx = -self.patrol_dx
                        self.patrol_dy = -self.patrol_dy
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            angle = math.atan2(camera_y + SCREEN_HEIGHT//2 - self.y, camera_x + SCREEN_WIDTH//2 - self.x)
            
            points = [
                (screen_x + math.cos(angle) * self.radius, screen_y + math.sin(angle) * self.radius),
                (screen_x + math.cos(angle + 2.5) * self.radius, screen_y + math.sin(angle + 2.5) * self.radius),
                (screen_x + math.cos(angle - 2.5) * self.radius, screen_y + math.sin(angle - 2.5) * self.radius)
            ]
            
            pygame.draw.polygon(surface, self.color, points)
            
            if self.state == "patrol":
                state_color = GRAY
            elif self.state == "chase":
                state_color = YELLOW
            elif self.state == "evade":
                state_color = PURPLE
            else:
                state_color = WHITE
                
            pygame.draw.polygon(surface, state_color, points, 2)
    
    def shoot(self, player):
        # Враги теперь могут стрелять в состоянии evade (уклонения)
        if self.shoot_cooldown <= 0 and (self.state == "attack" or self.state == "evade") and random.random() < 0.03:
            self.shoot_cooldown = self.shoot_rate
            
            # Улучшенная система стрельбы с учетом точности
            if random.random() < self.accuracy:
                # Точный выстрел
                return EnemyBullet(self.x, self.y, player.x, player.y, 
                                 self.bullet_speed, int(25 * self.damage_multiplier))
            else:
                # Неточный выстрел (промах)
                offset_x = random.uniform(-100, 100)
                offset_y = random.uniform(-100, 100)
                return EnemyBullet(self.x, self.y, player.x + offset_x, player.y + offset_y,
                                 self.bullet_speed, int(15 * self.damage_multiplier))
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

# Новый класс для врагов с щитом
class ShieldedEnemy(Enemy):
    def __init__(self, difficulty="Средний"):
        super().__init__(difficulty)
        self.radius = 25  # Немного больше обычного врага
        self.color = PURPLE
        
        difficulty_settings = DIFFICULTY_LEVELS[difficulty]
        self.shield_health = 3  # Щит может поглотить 3 пули
        self.max_shield_health = 3
        self.shoot_rate = difficulty_settings["shielded_shoot_rate"]  # Стреляет чаще
        
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            # Рисуем щит (ярко-красный круг)
            if self.shield_health > 0:
                shield_radius = self.radius + 5
                pygame.draw.circle(surface, BRIGHT_RED, (int(screen_x), int(screen_y)), shield_radius, 3)
            
            # Рисуем самого врага (шар)
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.radius)
            
            # Рисуем состояние
            if self.state == "patrol":
                state_color = GRAY
            elif self.state == "chase":
                state_color = YELLOW
            elif self.state == "evade":
                state_color = PURPLE
            else:
                state_color = WHITE
                
            pygame.draw.circle(surface, state_color, (int(screen_x), int(screen_y)), self.radius, 2)
    
    def take_damage(self, amount):
        if self.shield_health > 0:
            self.shield_health -= 1
            return False
        else:
            self.health -= amount
            return self.health <= 0

# Класс для астероидов
class Asteroid:
    def __init__(self, size="medium"):
        self.size = size
        if size == "large":
            self.radius = 40
            self.speed = 1.0
            self.health = 50
        elif size == "medium":
            self.radius = 25
            self.speed = 1.5
            self.health = 30
        else:
            self.radius = 15
            self.speed = 2.0
            self.health = 15
            
        self.max_health = self.health
        
        margin = 100
        self.x = random.randint(margin, WORLD_WIDTH - margin)
        self.y = random.randint(margin, WORLD_HEIGHT - margin)
        
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        
        length = math.sqrt(self.dx*self.dx + self.dy*self.dy)
        if length > 0:
            self.dx /= length
            self.dy /= length
            
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.rotation += self.rotation_speed
        
        if self.x < 0 or self.x > WORLD_WIDTH:
            self.dx = -self.dx
        if self.y < 0 or self.y > WORLD_HEIGHT:
            self.dy = -self.dy
            
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            points = []
            for i in range(8):
                angle = math.radians(i * 45 + self.rotation)
                variation = random.uniform(0.8, 1.2)
                px = screen_x + math.cos(angle) * self.radius * variation
                py = screen_y + math.sin(angle) * self.radius * variation
                points.append((px, py))
                
            pygame.draw.polygon(surface, GRAY, points)
            pygame.draw.polygon(surface, WHITE, points, 1)
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

# Класс для предметов
class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.radius = 15
        
        if item_type == "health":
            self.color = RED
        elif item_type == "ammo":
            self.color = YELLOW
        else:
            self.color = BLUE
            
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(screen_x), int(screen_y)), self.radius - 3, 2)
            
            if self.type == "health":
                pygame.draw.line(surface, WHITE, (int(screen_x), int(screen_y - 5)), (int(screen_x), int(screen_y + 5)), 2)
                pygame.draw.line(surface, WHITE, (int(screen_x - 5), int(screen_y)), (int(screen_x + 5), int(screen_y)), 2)
            elif self.type == "ammo":
                pygame.draw.rect(surface, WHITE, (int(screen_x - 4), int(screen_y - 4), 8, 8), 1)
            else:
                points = [(int(screen_x), int(screen_y - 6)), (int(screen_x - 6), int(screen_y)), 
                         (int(screen_x), int(screen_y + 6)), (int(screen_x + 6), int(screen_y))]
                pygame.draw.polygon(surface, WHITE, points, 1)

# Создание игровых объектов
player = Player()
bullets = []
enemy_bullets = []
enemies = []
asteroids = []
items = []
score = 0
game_time = 0

# Функция для отрисовки меню
def draw_menu():
    global menu_time, menu_ships
    
    screen.blit(menu_background, (0, 0))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Добавляем пролетающие корабли на фон
    menu_time += 1/60
    if menu_time > 3 and random.random() < 0.01 and len(menu_ships) < 5:
        menu_ships.append(MenuShip())
    
    for ship in menu_ships[:]:
        ship.update()
        ship.draw(screen)
        if ship.is_off_screen():
            menu_ships.remove(ship)
    
    title_text = title_font.render("PULIXER", True, BLUE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    subtitle_text = small_font.render("КОСМИЧЕСКИЙ ШУТЕР", True, WHITE)
    screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 180))
    
    version_text = small_font.render(f"Версия: {GAME_VERSION}", True, WHITE)
    screen.blit(version_text, (20, 20))
    
    difficulty_text = small_font.render(f"Сложность: {current_difficulty}", True, YELLOW)
    screen.blit(difficulty_text, (SCREEN_WIDTH - difficulty_text.get_width() - 20, 20))
    
    start_button.draw(screen)
    settings_button.draw(screen)
    difficulty_button.draw(screen)
    exit_button.draw(screen)
    
    copyright_text = small_font.render("© 2025 PixelForge Studios", True, WHITE)
    screen.blit(copyright_text, (SCREEN_WIDTH//2 - copyright_text.get_width()//2, SCREEN_HEIGHT - 50))
    
    exit_hint = small_font.render("Нажмите ESC для выхода из полноэкранного режима", True, YELLOW)
    screen.blit(exit_hint, (SCREEN_WIDTH//2 - exit_hint.get_width()//2, SCREEN_HEIGHT - 30))

# Функция для отрисовки экрана загрузки
def draw_loading_screen():
    global loading_progress, loading_time
    
    screen.blit(menu_background, (0, 0))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    loading_text = menu_font.render("ЗАГРУЗКА", True, BLUE)
    screen.blit(loading_text, (SCREEN_WIDTH//2 - loading_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    
    pygame.draw.rect(screen, DARK_BLUE, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 300, 30), border_radius=5)
    pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH//2 - 145, SCREEN_HEIGHT//2 + 25, 290 * (loading_progress/100), 20), border_radius=5)
    
    percent_text = small_font.render(f"{int(loading_progress)}%", True, WHITE)
    screen.blit(percent_text, (SCREEN_WIDTH//2 - percent_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    loading_progress += 0.5
    loading_time += 1
    
    if loading_progress >= 100:
        return True
    return False

# Функция для обновления камера
def update_camera():
    global camera_x, camera_y
    
    target_x = player.x - SCREEN_WIDTH // 2
    target_y = player.y - SCREEN_HEIGHT // 2
    
    camera_x += (target_x - camera_x) * 0.05
    camera_y += (target_y - camera_y) * 0.05
    
    camera_x = max(0, min(camera_x, WORLD_WIDTH - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - SCREEN_HEIGHT))

# Функция для отрисовки HUD
def draw_hud():
    # Лицо главного героя в левом верхнем углу
    if player_face:
        screen.blit(player_face, (20, 20))
    
    # Панель здоровья (сдвигаем ниже портрета)
    pygame.draw.rect(screen, DARK_BLUE, (20, 110, 200, 25), border_radius=5)
    health_width = max(0, (player.health / player.max_health) * 190)
    pygame.draw.rect(screen, RED, (25, 115, health_width, 15), border_radius=3)
    
    # Панель патронов
    pygame.draw.rect(screen, DARK_BLUE, (20, 140, 200, 25), border_radius=5)
    ammo_width = max(0, (player.ammo / player.max_ammo) * 190)
    pygame.draw.rect(screen, YELLOW, (25, 145, ammo_width, 15), border_radius=3)
    
    # Перезарядка
    if player.reloading:
        reload_text = small_font.render("ПЕРЕЗАРЯДКА...", True, RED)
        screen.blit(reload_text, (25, 170))
    
    # Счет и убийства
    score_text = small_font.render(f"Счет: {player.score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
    
    kills_text = small_font.render(f"Убийств: {player.kills}", True, WHITE)
    screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 20, 50))
    
    # Время игры
    minutes = game_time // 3600
    seconds = (game_time % 3600) // 60
    time_text = small_font.render(f"Время: {minutes:02d}:{seconds:02d}", True, WHITE)
    screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 80))
    
    # Сложность
    difficulty_text = small_font.render(f"Сложность: {current_difficulty}", True, YELLOW)
    screen.blit(difficulty_text, (SCREEN_WIDTH - difficulty_text.get_width() - 20, 110))
    
    # Подсказки управления
    controls_text = small_font.render("WASD - движение, ЛКМ - стрельба, R - перезарядка, ESC - меню", True, GRAY)
    screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 30))

# Функция для отрисовки экрана настроек
def draw_settings():
    screen.blit(menu_background, (0, 0))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    title_text = menu_font.render("НАСТРОЙКИ", True, BLUE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    gender_toggle.draw(screen)
    back_settings_button.draw(screen)
    
    # Показываем превью выбранного пола
    gender_preview = load_player_face("female" if gender_toggle.current_index == 1 else "male")
    if gender_preview:
        screen.blit(gender_preview, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2 - 150))
    
    gender_label = small_font.render("Выбранный пол:", True, WHITE)
    screen.blit(gender_label, (SCREEN_WIDTH//2 - gender_label.get_width()//2, SCREEN_HEIGHT//2 - 180))

# Функция для отрисовки экрана выбора сложности
def draw_difficulty_select():
    screen.blit(menu_background, (0, 0))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    title_text = menu_font.render("ВЫБЕРИТЕ СЛОЖНОСТЬ", True, BLUE)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    easy_button.draw(screen)
    medium_button.draw(screen)
    hard_button.draw(screen)
    back_button.draw(screen)
    
    # Описание выбранной сложности
    difficulty_settings = DIFFICULTY_LEVELS[current_difficulty]
    desc_text = small_font.render(
        f"Скорость врагов: {difficulty_settings['enemy_speed']} | "
        f"Здоровье врагов: {difficulty_settings['enemy_health']} | "
        f"Количество врагов: {difficulty_settings['enemy_count']}", 
        True, WHITE
    )
    screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, SCREEN_HEIGHT//2 + 200))

# Функция для отрисовки экрана Game Over
def draw_game_over():
    screen.blit(menu_background, (0, 0))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over_text = title_font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))
    
    score_text = menu_font.render(f"Счет: {player.score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 250))
    
    kills_text = menu_font.render(f"Убийств: {player.kills}", True, WHITE)
    screen.blit(kills_text, (SCREEN_WIDTH//2 - kills_text.get_width()//2, 300))
    
    time_text = menu_font.render(f"Время выживания: {game_time//3600:02d}:{(game_time%3600)//60:02d}", True, WHITE)
    screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 350))
    
    hits_text = menu_font.render(f"Получено попаданий: {player.hit_count}", True, WHITE)
    screen.blit(hits_text, (SCREEN_WIDTH//2 - hits_text.get_width()//2, 400))
    
    retry_button = Button("Попробовать снова", 100)
    menu_button = Button("В главное меню", 175)
    
    retry_button.draw(screen)
    menu_button.draw(screen)
    
    return retry_button, menu_button

# Функция для генерации врагов
def spawn_enemies(count, difficulty):
    new_enemies = []
    for _ in range(count):
        if random.random() < 0.2:  # 20% шанс появления врага с щитом
            new_enemies.append(ShieldedEnemy(difficulty))
        else:
            new_enemies.append(Enemy(difficulty))
    return new_enemies

# Функция для генерации астероидов
def spawn_asteroids(count):
    new_asteroids = []
    for _ in range(count):
        size = random.choice(["large", "medium", "small"])
        new_asteroids.append(Asteroid(size))
    return new_asteroids

# Функция для проверки столкновений
def check_collisions():
    global score, hit_particles
    
    # Проверка столкновений пуль с врагами
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            dx = bullet.x - enemy.x
            dy = bullet.y - enemy.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < enemy.radius + bullet.radius:
                if enemy.take_damage(bullet.damage):
                    player.score += 100
                    player.kills += 1
                    
                    # Создание частиц при уничтожении врага
                    for _ in range(20):
                        hit_particles.append(Particle(enemy.x, enemy.y, RED))
                    
                    # Шанс выпадения предмета
                    if random.random() < 0.3:
                        item_type = random.choice(["health", "ammo"])
                        items.append(Item(enemy.x, enemy.y, item_type))
                    
                    enemies.remove(enemy)
                
                if bullet in bullets:
                    bullets.remove(bullet)
                break
    
    # Проверка столкновений пуль с астероидов
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            dx = bullet.x - asteroid.x
            dy = bullet.y - asteroid.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < asteroid.radius + bullet.radius:
                if asteroid.take_damage(bullet.damage):
                    player.score += 50
                    
                    # Создание частиц при уничтожении астероида
                    for _ in range(15):
                        hit_particles.append(Particle(asteroid.x, asteroid.y, GRAY))
                    
                    asteroids.remove(asteroid)
                
                if bullet in bullets:
                    bullets.remove(bullet)
                break
    
    # Проверка столкновений вражеских пуль с игроком
    for bullet in enemy_bullets[:]:
        dx = bullet.x - player.x
        dy = bullet.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < player.radius + bullet.radius:
            player.take_damage(bullet.damage)
            enemy_bullets.remove(bullet)
    
    # Проверка столкновений врагов с игроком
    for enemy in enemies:
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < player.radius + enemy.radius:
            player.take_damage(5)
            
            # Отталкивание игрока
            angle = math.atan2(dy, dx)
            player.x -= math.cos(angle) * 10
            player.y -= math.sin(angle) * 10
    
    # Проверка столкновений астероидов с игроком
    for asteroid in asteroids:
        dx = asteroid.x - player.x
        dy = asteroid.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < player.radius + asteroid.radius:
            player.take_damage(10)
            
            # Отталкивание игрока
            angle = math.atan2(dy, dx)
            player.x -= math.cos(angle) * 15
            player.y -= math.sin(angle) * 15
    
    # Проверка столкновений с предметами
    for item in items[:]:
        dx = item.x - player.x
        dy = item.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < player.radius + item.radius:
            if item.type == "health":
                player.heal(25)
            elif item.type == "ammo":
                player.ammo = min(player.max_ammo, player.ammo + 10)
            
            items.remove(item)

# Основной игровой цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME:
                    game_state = MENU
                elif game_state == SETTINGS or game_state == DIFFICULTY_SELECT:
                    game_state = MENU
                else:
                    running = False
                    
            if game_state == GAME:
                if event.key == pygame.K_r:
                    player.reload()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                if game_state == MENU:
                    if start_button.check_hover(mouse_pos):
                        game_state = LOADING
                        loading_progress = 0
                        loading_time = 0
                    elif settings_button.check_hover(mouse_pos):
                        game_state = SETTINGS
                    elif difficulty_button.check_hover(mouse_pos):
                        game_state = DIFFICULTY_SELECT
                    elif exit_button.check_hover(mouse_pos):
                        running = False
                        
                elif game_state == SETTINGS:
                    if gender_toggle.check_hover(mouse_pos):
                        gender_toggle.toggle()
                        # Обновляем изображение игрока
                        player_gender = "female" if gender_toggle.current_index == 1 else "male"
                        player_face = load_player_face(player_gender)
                    elif back_settings_button.check_hover(mouse_pos):
                        game_state = MENU
                        
                elif game_state == DIFFICULTY_SELECT:
                    if easy_button.check_hover(mouse_pos):
                        current_difficulty = "Легкий"
                    elif medium_button.check_hover(mouse_pos):
                        current_difficulty = "Средний"
                    elif hard_button.check_hover(mouse_pos):
                        current_difficulty = "Сложный"
                    elif back_button.check_hover(mouse_pos):
                        game_state = MENU
                        
                elif game_state == GAME:
                    if player.ammo > 0 and not player.reloading:
                        target_x = mouse_pos[0] + camera_x
                        target_y = mouse_pos[1] + camera_y
                        bullets.append(Bullet(player.x, player.y, target_x, target_y))
                        player.ammo -= 1
                        
                elif game_state == GAME_OVER:
                    retry_button, menu_button = draw_game_over()
                    if retry_button.check_hover(mouse_pos):
                        # Перезапуск игры
                        player = Player()
                        bullets = []
                        enemy_bullets = []
                        enemies = spawn_enemies(DIFFICULTY_LEVELS[current_difficulty]["enemy_count"], current_difficulty)
                        asteroids = spawn_asteroids(DIFFICULTY_LEVELS[current_difficulty]["asteroid_count"])
                        items = []
                        game_time = 0
                        game_state = GAME
                    elif menu_button.check_hover(mouse_pos):
                        game_state = MENU
    
    # Обновление состояний кнопок
    if game_state == MENU:
        start_button.check_hover(mouse_pos)
        settings_button.check_hover(mouse_pos)
        difficulty_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)
        
    elif game_state == SETTINGS:
        back_settings_button.check_hover(mouse_pos)
        
    elif game_state == DIFFICULTY_SELECT:
        easy_button.check_hover(mouse_pos)
        medium_button.check_hover(mouse_pos)
        hard_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
    
    # Обработка состояний игры
    if game_state == MENU:
        if menu_ambient:
            if not pygame.mixer.get_busy():
                menu_ambient.play(-1)
        draw_menu()  # Добавлена отрисовка меню
        
    elif game_state == LOADING:
        if menu_ambient:
            menu_ambient.stop()
            
        if draw_loading_screen():
            # Инициализация игры после загрузки
            player = Player()
            bullets = []
            enemy_bullets = []
            
            difficulty_settings = DIFFICULTY_LEVELS[current_difficulty]
            enemies = spawn_enemies(difficulty_settings["enemy_count"], current_difficulty)
            asteroids = spawn_asteroids(difficulty_settings["asteroid_count"])
            items = []
            
            game_time = 0
            
            if game_music:
                game_music.play(-1)
                
            game_state = GAME
            
    elif game_state == GAME:
        # Обновление игрока
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update_reload()
        
        # Обновление камеры
        update_camera()
        
        # Обновление пуль
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds():
                bullets.remove(bullet)
                
        # Обновление вражеских пуль
        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.is_out_of_bounds():
                enemy_bullets.remove(bullet)
                
        # Обновление врагов
        for enemy in enemies:
            enemy.update(player, bullets)
            bullet = enemy.shoot(player)
            if bullet:
                enemy_bullets.append(bullet)
                
        # Обновление астероидов
        for asteroid in asteroids:
            asteroid.update()
            
        # Проверка столкновений
        check_collisions()
        
        # Обновление частиц
        for particle in hit_particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                hit_particles.remove(particle)
                
        # Спавн новых врагов
        if len(enemies) < DIFFICULTY_LEVELS[current_difficulty]["enemy_count"] // 2:
            new_enemies = spawn_enemies(1, current_difficulty)
            enemies.extend(new_enemies)
            
        # Спавн новых астероидов
        if len(asteroids) < DIFFICULTY_LEVELS[current_difficulty]["asteroid_count"] // 2:
            new_asteroids = spawn_asteroids(1)
            asteroids.extend(new_asteroids)
            
        # Увеличение сложности со временем
        game_time += 1
        if game_time % 1800 == 0:  # Каждые 30 секунд
            difficulty_settings = DIFFICULTY_LEVELS[current_difficulty]
            if len(enemies) < difficulty_settings["enemy_count"] * 1.5:
                new_enemies = spawn_enemies(2, current_difficulty)
                enemies.extend(new_enemies)
                
        # Проверка смерти игрока
        if player.health <= 0:
            game_state = GAME_OVER
            if game_music:
                game_music.stop()
        
        # Отрисовка игры
        screen.blit(game_background, (-camera_x, -camera_y))
        
        # Применение эффекта тряски экрана
        shake_offset_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_offset_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        
        if screen_shake > 0:
            screen_shake -= 1
            
        # Отрисовка объектов с учетом тряски
        for asteroid in asteroids:
            asteroid.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
            
        for item in items:
            item.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
            
        for enemy in enemies:
            enemy.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
            
        for bullet in bullets:
            bullet.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
            
        for bullet in enemy_bullets:
            bullet.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
            
        player.draw(screen, camera_x + shake_offset_x, camera_y + shake_offset_y)
        
        # Отрисовка частиц
        for particle in hit_particles:
            particle.draw(screen)
            
        # Отрисовка HUD
        draw_hud()
        
    elif game_state == SETTINGS:
        draw_settings()
        
    elif game_state == DIFFICULTY_SELECT:
        draw_difficulty_select()
        
    elif game_state == GAME_OVER:
        retry_button, menu_button = draw_game_over()
        retry_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()