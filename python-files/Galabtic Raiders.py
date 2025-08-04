import pygame
import sys
import random
import math
import time
import json
import os
from pygame import gfxdraw
import warnings

# Игнорируем предупреждения
warnings.filterwarnings("ignore", category=UserWarning)

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Полноэкранный режим
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("ГАЛАКТИЧЕСКИЙ РЕЙДЕР: ЭПИЧЕСКОЕ ПУТЕШЕСТВИЕ")

# Цвета
BACKGROUND = (5, 5, 25)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 100)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (100, 150, 255)
PURPLE = (200, 100, 255)
ORANGE = (255, 150, 50)
CYAN = (100, 255, 255)
MAGENTA = (255, 100, 200)
GOLD = (255, 215, 0)
DARK_BLUE = (10, 10, 40)
LIGHT_BLUE = (100, 200, 255)
LIGHT_PURPLE = (180, 120, 220)
DARK_RED = (150, 0, 0)
STEEL_BLUE = (70, 130, 180)
BRONZE = (205, 127, 50)
SILVER = (200, 200, 200)
PLASMA_BLUE = (0, 150, 255)
PLASMA_PURPLE = (180, 0, 255)

# Шрифты
try:
    font_large = pygame.font.Font("freesansbold.ttf", 72)
    font_medium = pygame.font.Font("freesansbold.ttf", 42)
    font_small = pygame.font.Font("freesansbold.ttf", 32)
    font_tiny = pygame.font.Font("freesansbold.ttf", 24)
    font_achievement = pygame.font.Font("freesansbold.ttf", 20)
    font_button = pygame.font.Font("freesansbold.ttf", 30)
    font_boss = pygame.font.Font("freesansbold.ttf", 86)
except:
    font_large = pygame.font.SysFont("Arial", 72, bold=True)
    font_medium = pygame.font.SysFont("Arial", 42, bold=True)
    font_small = pygame.font.SysFont("Arial", 32, bold=True)
    font_tiny = pygame.font.SysFont("Arial", 24, bold=True)
    font_achievement = pygame.font.SysFont("Arial", 20, bold=True)
    font_button = pygame.font.SysFont("Arial", 30, bold=True)
    font_boss = pygame.font.SysFont("Arial", 86, bold=True)

# Звездное поле
stars = []
for _ in range(2000):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.uniform(0.5, 3.0)
    speed = random.uniform(0.2, 1.2)
    brightness = random.randint(150, 255)
    stars.append([x, y, size, speed, brightness])

# Небо с туманностью
nebulas = []
for _ in range(10):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT // 2)
    radius = random.randint(300, 700)
    color = random.choice([(100, 20, 100), (20, 50, 150), (50, 150, 200), (80, 30, 120)])
    nebulas.append([x, y, radius, color])

# Класс для уведомлений о достижениях
class AchievementNotification:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.timer = 300
        self.y_pos = -100
        self.target_y = 20
        self.alpha = 0
        self.surface = pygame.Surface((450, 90), pygame.SRCALPHA)
        self.active = True
        
    def update(self):
        if self.y_pos < self.target_y:
            self.y_pos += 4
        if self.alpha < 255:
            self.alpha += 5
            
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            
    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, (30, 10, 50, self.alpha), (0, 0, 450, 90), border_radius=18)
        pygame.draw.rect(self.surface, (100, 50, 150, self.alpha), (0, 0, 450, 90), 4, border_radius=18)
        pygame.draw.circle(self.surface, (GOLD[0], GOLD[1], GOLD[2], self.alpha), (45, 45), 30)
        star_points = [
            (45, 18), (50, 35), (70, 35), (55, 45),
            (60, 65), (45, 52), (30, 65), (35, 45),
            (20, 35), (40, 35)
        ]
        pygame.draw.polygon(self.surface, (255, 255, 255, self.alpha), star_points)
        title_surf = font_achievement.render(self.title, True, (255, 215, 0, self.alpha))
        desc_surf = font_achievement.render(self.description, True, (220, 220, 220, self.alpha))
        self.surface.blit(title_surf, (85, 25))
        self.surface.blit(desc_surf, (85, 55))
        surface.blit(self.surface, (25, self.y_pos))

# Класс для анимации появления босса
class BossIntro:
    def __init__(self, boss_name, boss_level):
        self.boss_name = boss_name
        self.boss_level = boss_level
        self.timer = 300
        self.y_pos = HEIGHT // 4
        self.alpha = 0
        self.scale = 0.1
        
    def update(self):
        self.timer -= 1
        if self.alpha < 255:
            self.alpha += 5
        if self.scale < 1.0:
            self.scale += 0.05
        return self.timer > 0
        
    def draw(self, surface):
        # Фон
        overlay = pygame.Surface((WIDTH, 250), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha // 2))
        surface.blit(overlay, (0, self.y_pos - 60))
        
        # Текст
        name_text = font_boss.render(f"{self.boss_name}", True, (255, 50, 50, self.alpha))
        level_text = font_medium.render(f"Уровень {self.boss_level}", True, (255, 215, 0, self.alpha))
        
        # Анимация масштабирования
        scaled_width = int(name_text.get_width() * self.scale)
        scaled_height = int(name_text.get_height() * self.scale)
        scaled_surf = pygame.transform.scale(name_text, (scaled_width, scaled_height))
        
        x_pos = WIDTH // 2 - scaled_width // 2
        surface.blit(scaled_surf, (x_pos, self.y_pos))
        
        # Уровень босса
        surface.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, self.y_pos + scaled_height + 15))

# Класс корабля помощи
class HelperShip:
    def __init__(self, x, y, side):
        self.x = x
        self.y = y
        self.radius = 25
        self.speed = 4
        self.color = GREEN if side == "left" else CYAN
        self.secondary_color = (50, 200, 50) if side == "left" else (50, 200, 200)
        self.side = side
        self.health = 70
        self.max_health = 70
        self.last_shot = 0
        self.shot_cooldown = 100
        self.active_timer = 600  # 10 секунд при 60 FPS
        self.move_direction = 1
        self.move_timer = 0
        self.particles = []
        
    def update(self):
        self.active_timer -= 1
        if self.active_timer <= 0:
            return False
            
        # Движение
        self.move_timer += 1
        if self.move_timer > 30:
            self.move_timer = 0
            self.move_direction *= -1
            
        self.x += self.speed * self.move_direction
        self.y -= 0.5
        
        # Ограничение экрана
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        
        # Создание частиц двигателя
        if random.random() > 0.5:
            particle_x = self.x + random.randint(-5, 5)
            particle_y = self.y + self.radius
            size = random.randint(2, 6)
            speed = random.uniform(1.0, 2.5)
            life = random.randint(10, 25)
            self.particles.append({
                'x': particle_x,
                'y': particle_y,
                'size': size,
                'speed': speed,
                'life': life,
                'color': random.choice([ORANGE, YELLOW, RED])
            })
        
        # Обновление частиц
        for particle in self.particles[:]:
            particle['y'] += particle['speed']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
        return True
        
    def shoot(self, current_time):
        if current_time - self.last_shot > self.shot_cooldown:
            self.last_shot = current_time
            return [Projectile(self.x, self.y - self.radius, 2, "Импульсный лазер", 'helper')]
        return []
        
    def draw(self, surface):
        # Корпус
        points = [
            (self.x, self.y - self.radius),
            (self.x - self.radius * 0.7, self.y + self.radius * 0.3),
            (self.x - self.radius * 0.5, self.y + self.radius),
            (self.x + self.radius * 0.5, self.y + self.radius),
            (self.x + self.radius * 0.7, self.y + self.radius * 0.3)
        ]
        
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, self.secondary_color, points, 3)
        
        # Кабина
        pygame.draw.circle(surface, self.secondary_color, (int(self.x), int(self.y - self.radius * 0.2)), self.radius * 0.3)
        
        # Частицы двигателя
        for particle in self.particles:
            alpha = min(255, particle['life'] * 15)
            pygame.draw.circle(
                surface, 
                (*particle['color'], alpha), 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
        
        # Полоска здоровья
        health_width = 50
        health_height = 5
        pygame.draw.rect(surface, (80, 80, 80), 
                        (self.x - health_width//2, self.y - self.radius - 18, 
                         health_width, health_height))
        pygame.draw.rect(surface, GREEN, 
                        (self.x - health_width//2, self.y - self.radius - 18, 
                         health_width * (self.health / self.max_health), health_height))

# Класс игрока
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 200
        self.radius = 35
        self.speed = 7
        self.color = BLUE
        self.secondary_color = LIGHT_BLUE
        self.health = 120
        self.max_health = 120
        self.shield = 120
        self.max_shield = 120
        self.energy = 250
        self.max_energy = 250
        self.score = 0
        self.credits = 600
        self.weapon_type = "Импульсный лазер"
        self.weapon_level = 1
        self.engine_level = 1
        self.shield_level = 1
        self.last_shot = 0
        self.shot_cooldown = 200
        self.direction = 0
        self.thrust = 0
        self.special_ability = "Усиление щита"
        self.ability_cooldown = 0
        self.ability_duration = 0
        self.dodge_cooldown = 0
        self.invincibility = 0
        self.kill_count = 0
        self.abilities = {
            "Усиление щита": {"level": 1, "cost": 250},
            "Замедление времени": {"level": 0, "cost": 350},
            "Усиление урона": {"level": 0, "cost": 450},
            "Ракетный залп": {"level": 0, "cost": 550},
            "Энергетический взрыв": {"level": 0, "cost": 650},
            "Вызов помощи": {"level": 0, "cost": 750}  # Новая способность
        }
        self.ship_upgrades = {
            "Корпус": {"level": 1, "cost": 150},
            "Двигатель": {"level": 1, "cost": 200},
            "Щиты": {"level": 1, "cost": 250},
            "Вооружение": {"level": 1, "cost": 300}
        }
        self.ship_skins = {
            "Стандартный": {"owned": True, "equipped": True, "cost": 0, "color": BLUE, "secondary": LIGHT_BLUE},
            "Элитный": {"owned": False, "equipped": False, "cost": 1200, "color": PURPLE, "secondary": LIGHT_PURPLE},
            "Ветеран": {"owned": False, "equipped": False, "cost": 3000, "color": GOLD, "secondary": ORANGE},
            "Легендарный": {"owned": False, "equipped": False, "cost": 6000, "color": CYAN, "secondary": PLASMA_BLUE},
            "Плазменный": {"owned": False, "equipped": False, "cost": 9000, "color": PLASMA_PURPLE, "secondary": MAGENTA}
        }
        self.achievements = {
            "Первый выстрел": False,
            "10 убийств": False,
            "50 убийств": False,
            "100 убийств": False,
            "500 убийств": False,
            "1000 убийств": False,
            "Боссобой": False,
            "Повелитель боссов": False,
            "Уровень 10": False,
            "Уровень 50": False,
            "Уровень 100": False,
            "Мастер щита": False,
            "Мастер оружия": False,
            "Богач": False,
            "Миллионер": False,
            "Коллекционер": False,
            "Неуязвимый": False,
            "Скоростной": False,
            "Экономист": False,
            "Перфекционист": False,
            "Мастер помощи": False  # Новое достижение
        }
        self.auto_fire = False
        self.engine_particles = []
        self.skin_effects = {}
        self.total_play_time = 0
        self.start_time = time.time()
        self.dodge_count = 0
        self.boss_kills = 0
        self.helper_ships = []  # Корабли помощи
        self.helper_timer = 0  # Таймер для помощи
        
    def draw(self, surface):
        # Применение выбранного скина
        current_skin = None
        for skin, data in self.ship_skins.items():
            if data["equipped"]:
                current_skin = data
                break
        
        if current_skin:
            self.color = current_skin["color"]
            self.secondary_color = current_skin["secondary"]
        
        # Анимация двигателя
        if self.thrust > 0:
            # Создание новых частиц
            if random.random() > 0.3:
                particle_x = self.x + random.randint(-12, 12)
                particle_y = self.y + self.radius
                size = random.randint(4, 10)
                speed = random.uniform(1.5, 3.5)
                life = random.randint(15, 35)
                self.engine_particles.append({
                    'x': particle_x,
                    'y': particle_y,
                    'size': size,
                    'speed': speed,
                    'life': life,
                    'color': random.choice([ORANGE, RED, YELLOW])
                })
        
        # Обновление частиц двигателя
        for particle in self.engine_particles[:]:
            particle['y'] += particle['speed']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.engine_particles.remove(particle)
        
        # Отрисовка частиц двигателя
        for particle in self.engine_particles:
            alpha = min(255, particle['life'] * 10)
            pygame.draw.circle(
                surface, 
                (*particle['color'], alpha), 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
        
        # Основной корпус
        points = [
            (self.x, self.y - self.radius),
            (self.x - self.radius * 0.9, self.y + self.radius * 0.3),
            (self.x - self.radius * 0.7, self.y + self.radius),
            (self.x + self.radius * 0.7, self.y + self.radius),
            (self.x + self.radius * 0.9, self.y + self.radius * 0.3)
        ]
        
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, self.secondary_color, points, 3)
        
        # Кабина
        pygame.draw.ellipse(surface, self.secondary_color, 
                          (self.x - self.radius/3, self.y - self.radius/2, 
                           self.radius*2/3, self.radius/2))
        pygame.draw.ellipse(surface, DARK_BLUE, 
                          (self.x - self.radius/3, self.y - self.radius/2, 
                           self.radius*2/3, self.radius/2), 3)
        
        # Эффекты скина
        if current_skin and ("Плазменный" in current_skin.get("name", "") or 
                             "Плазменный" in self.ship_skins and self.ship_skins["Плазменный"]["equipped"]):
            # Плазменная анимация
            pulse = (pygame.time.get_ticks() // 40) % 100
            alpha = abs(50 - pulse) * 5
            glow_surface = pygame.Surface((self.radius * 5, self.radius * 5), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*PLASMA_PURPLE, alpha), 
                              (self.radius * 2.5, self.radius * 2.5), self.radius * 2.2, 4)
            surface.blit(glow_surface, (self.x - self.radius * 2.5, self.y - self.radius * 2.5))
            
            # Искры
            if random.random() > 0.8:
                spark_x = self.x + random.randint(-int(self.radius*0.9), int(self.radius*0.9))
                spark_y = self.y + random.randint(-int(self.radius*0.9), int(self.radius*0.9))
                pygame.draw.line(surface, PLASMA_BLUE, 
                               (self.x, self.y), 
                               (spark_x, spark_y), 
                               2)
        
        # Щит
        if self.shield > 0:
            shield_alpha = min(150, int(self.shield / self.max_shield * 200))
            shield_color = GREEN
            if self.special_ability == "Усиление щита" and self.ability_duration > 0:
                shield_color = CYAN
            shield_surface = pygame.Surface((self.radius * 5, self.radius * 5), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*shield_color, shield_alpha), 
                              (self.radius * 2.5, self.radius * 2.5), self.radius * 2.2, 4)
            surface.blit(shield_surface, (self.x - self.radius * 2.5, self.y - self.radius * 2.5))
        
        # Эффект неуязвимости
        if self.invincibility > 0:
            alpha = 255 if pygame.time.get_ticks() % 200 < 100 else 100
            invincible_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(invincible_surface, (*CYAN, alpha), 
                              (self.radius * 2, self.radius * 2), self.radius * 2, 5)
            surface.blit(invincible_surface, (self.x - self.radius * 2, self.y - self.radius * 2))
    
    def move(self, keys):
        self.direction = 0
        self.thrust = 0
        
        move_x, move_y = 0, 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x = -self.speed
            self.direction = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = self.speed
            self.direction = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y = -self.speed
            self.thrust = 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = self.speed
            self.thrust = 1
            
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071
            
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + move_x))
        self.y = max(self.radius + 50, min(HEIGHT - self.radius, self.y + move_y))
            
        if self.energy < self.max_energy:
            self.energy += 0.06 * self.ship_upgrades["Двигатель"]["level"]
            
        if self.shield < self.max_shield and self.health == self.max_health:
            self.shield += 0.025 * self.ship_upgrades["Щиты"]["level"]
            
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
            
        if self.invincibility > 0:
            self.invincibility -= 1
            
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
            
        if self.ability_duration > 0:
            self.ability_duration -= 1
            
        # Обновление кораблей помощи
        for helper in self.helper_ships[:]:
            if not helper.update():
                self.helper_ships.remove(helper)
                
        # Обновление таймера помощи
        if self.helper_timer > 0:
            self.helper_timer -= 1
    
    def shoot(self, current_time):
        if current_time - self.last_shot > self.shot_cooldown and self.energy > 5:
            self.last_shot = current_time
            self.energy -= 5
            
            projectiles = []
            
            if self.weapon_type == "Импульсный лазер":
                for i in range(self.ship_upgrades["Вооружение"]["level"]):
                    offset = (i - (self.ship_upgrades["Вооружение"]["level"] - 1) / 2) * 18
                    projectiles.append(Projectile(self.x + offset, self.y - self.radius, self.weapon_level, self.weapon_type, 'player'))
            elif self.weapon_type == "Плазма":
                for i in range(-1, 2):
                    projectiles.append(Projectile(self.x + i*12, self.y - self.radius, self.weapon_level, self.weapon_type, 'player'))
            elif self.weapon_type == "Ракеты":
                projectiles.append(Projectile(self.x, self.y - self.radius, self.weapon_level, self.weapon_type, 'player'))
            elif self.weapon_type == "Рельсотрон":
                projectiles.append(Projectile(self.x, self.y - self.radius, self.weapon_level, self.weapon_type, 'player'))
            
            return projectiles
        return []
    
    def activate_ability(self):
        if self.ability_cooldown == 0 and self.energy > 30:
            self.energy -= 30
            ability_level = self.abilities[self.special_ability]["level"]
            
            self.ability_cooldown = 600 - (ability_level - 1) * 100
            self.ability_duration = 300 + (ability_level - 1) * 50
            
            if self.special_ability == "Усиление щита":
                self.shield = min(self.max_shield, self.shield + 60 * ability_level)
                return True
            elif self.special_ability == "Ракетный залп":
                return [Projectile(self.x, self.y - self.radius, self.weapon_level, "Ракеты", 'player') for _ in range(6 * ability_level)]
            elif self.special_ability == "Замедление времени":
                return True
            elif self.special_ability == "Усиление урона":
                return True
            elif self.special_ability == "Энергетический взрыв":
                explosions = []
                for _ in range(6 * ability_level):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.randint(60, 250)
                    explosions.append({
                        'x': self.x + math.cos(angle) * distance,
                        'y': self.y + math.sin(angle) * distance,
                        'size': random.randint(25, 50),
                        'timer': 35
                    })
                return explosions
            elif self.special_ability == "Вызов помощи":  # Новая способность
                if self.helper_timer <= 0 and self.credits >= 150:
                    self.helper_timer = 600  # 10 секунд
                    self.credits -= 150
                    
                    # Создаем два корабля помощи
                    self.helper_ships.append(HelperShip(self.x - 120, self.y - 60, "left"))
                    self.helper_ships.append(HelperShip(self.x + 120, self.y - 60, "right"))
                    return True
        return False
    
    def dodge(self):
        if self.dodge_cooldown == 0 and self.energy > 15:
            self.energy -= 15
            self.dodge_cooldown = 180
            self.invincibility = 30
            self.dodge_count += 1
            return True
        return False

# Класс снаряда
class Projectile:
    def __init__(self, x, y, level, weapon_type, source):
        self.x = x
        self.y = y
        self.level = level
        self.weapon_type = weapon_type
        self.source = source
        self.trail = []
        
        if weapon_type == "Импульсный лазер":
            self.speed = 14
            self.radius = 4 + level
            self.color = BLUE
            self.damage = 30 + (level - 1) * 6
            self.homing = False
        elif weapon_type == "Плазма":
            self.speed = 10
            self.radius = 6 + level
            self.color = PLASMA_PURPLE
            self.damage = 18 + (level - 1) * 5
            self.homing = False
        elif weapon_type == "Ракеты":
            self.speed = 7
            self.radius = 7 + level
            self.color = ORANGE
            self.damage = 40 + (level - 1) * 10
            self.homing = True
        elif weapon_type == "Рельсотрон":
            self.speed = 18
            self.radius = 3 + level
            self.color = CYAN
            self.damage = 50 + (level - 1) * 12
            self.homing = False
        
        self.lifetime = 140
        self.dx = 0
        self.dy = 0
        
    def move(self, enemies):
        # Сохраняем позицию для следа
        if len(self.trail) < 6:
            self.trail.append((self.x, self.y))
        else:
            self.trail.pop(0)
            self.trail.append((self.x, self.y))
        
        if self.dx != 0 or self.dy != 0:
            self.x += self.dx
            self.y += self.dy
        elif self.homing and enemies and self.source == 'player':
            closest_enemy = None
            min_distance = float('inf')
            
            for enemy in enemies:
                if enemy.y < self.y:
                    distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
            
            if closest_enemy and min_distance < 350:
                dx = closest_enemy.x - self.x
                dy = closest_enemy.y - self.y
                distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                
                self.x += dx / distance * 2.5
                self.y += dy / distance * 2.5
        else:
            if self.source == 'player':
                self.y -= self.speed
            else:
                self.y += self.speed
        
        self.lifetime -= 1
    
    def draw(self, surface):
        # Отрисовка следа
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 100 - i * 15
            size = max(1, self.radius - i)
            if size > 0:
                pygame.draw.circle(surface, (*self.color, alpha), (int(trail_x), int(trail_y)), size)
        
        # Отрисовка снаряда
        if self.weapon_type == "Импульсный лазер":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)
            
            length = 18 + self.level * 4
            points = [
                (self.x - self.radius/2, self.y + length/2),
                (self.x + self.radius/2, self.y + length/2),
                (self.x, self.y - length/2)
            ]
            pygame.draw.polygon(surface, (*self.color, 150), points)
            
        elif self.weapon_type == "Плазма":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)
            
            pulse = (pygame.time.get_ticks() // 40) % 10
            pygame.draw.circle(surface, (*MAGENTA, 100), (int(self.x), int(self.y)), self.radius + pulse/2, 1)
            
        elif self.weapon_type == "Ракеты":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            
            flame_length = random.randint(6, 12)
            flame_dir = 1 if self.source == 'player' else -1
            pygame.draw.line(surface, YELLOW, (self.x, self.y + self.radius * flame_dir), 
                           (self.x, self.y + (self.radius + flame_length) * flame_dir), 4)
            
            pygame.draw.line(surface, RED, 
                           (self.x - self.radius, self.y - self.radius/2 * flame_dir),
                           (self.x - self.radius*1.5, self.y), 3)
            pygame.draw.line(surface, RED, 
                           (self.x + self.radius, self.y - self.radius/2 * flame_dir),
                           (self.x + self.radius*1.5, self.y), 3)
            
        elif self.weapon_type == "Рельсотрон":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            
            for _ in range(4):
                offset_x = random.uniform(-self.radius*1.8, self.radius*1.8)
                offset_y = random.uniform(-self.radius*1.8, self.radius*1.8)
                pygame.draw.line(surface, CYAN, (self.x, self.y), 
                               (self.x + offset_x, self.y + offset_y), 2)
    
    def is_off_screen(self):
        if self.source == 'player':
            return self.y < 0 or self.lifetime <= 0
        else:
            return self.y > HEIGHT or self.lifetime <= 0

# Класс врага
class Enemy:
    def __init__(self, level, enemy_type=None):
        self.boss_names = [
            "Азраэль Разрушитель",
            "К'Тан Пожиратель",
            "Зорг Бессмертный",
            "Некрон Повелитель Тьмы",
            "Мал'Горит Истребитель Галактик"
        ]
        
        if enemy_type:
            self.type = enemy_type
        else:
            if level < 5:
                types = ["Истребитель"]
            elif level < 10:
                types = ["Истребитель", "Перехватчик"]
            elif level < 20:
                types = ["Истребитель", "Перехватчик", "Бомбардировщик"]
            else:
                types = ["Истребитель", "Перехватчик", "Бомбардировщик", "Крейсер"]
            
            if level % 10 == 0:
                self.type = "Босс"
                self.boss_name = random.choice(self.boss_names)
            else:
                self.type = random.choice(types)
        
        self.level = level
        self.spawn_time = pygame.time.get_ticks()
        
        if self.type == "Истребитель":
            self.radius = 30
            self.speed = 2.2 + level * 0.18
            self.color = (255, 100, 100)
            self.secondary_color = (200, 50, 50)
            self.health = 30 + level * 5
            self.value = 25
            self.fire_rate = 160
            self.projectile_type = "Импульсный лазер"
            self.move_pattern = random.choice(["Прямолинейно", "Зигзаг", "Круговое", "Волна", "Преследование"])
        elif self.type == "Бомбардировщик":
            self.radius = 45
            self.speed = 1.4 + level * 0.12
            self.color = (180, 140, 100)
            self.secondary_color = (150, 100, 70)
            self.health = 80 + level * 10
            self.value = 60
            self.fire_rate = 220
            self.projectile_type = "Ракеты"
            self.move_pattern = random.choice(["Прямолинейно", "Зигзаг", "Спираль"])
        elif self.type == "Перехватчик":
            self.radius = 25
            self.speed = 2.8 + level * 0.25
            self.color = (100, 180, 255)
            self.secondary_color = (70, 140, 220)
            self.health = 25 + level * 4
            self.value = 35
            self.fire_rate = 100
            self.projectile_type = "Плазма"
            self.move_pattern = random.choice(["Преследование", "Волна", "Зигзаг"])
        elif self.type == "Крейсер":
            self.radius = 40
            self.speed = 1.7 + level * 0.12
            self.color = (180, 100, 220)
            self.secondary_color = (150, 70, 200)
            self.health = 90 + level * 12
            self.value = 80
            self.fire_rate = 80
            self.projectile_type = "Рельсотрон"
            self.move_pattern = random.choice(["Прямолинейно", "Спираль", "Круговое"])
        elif self.type == "Босс":
            self.radius = 100
            self.speed = 1.0 + (level // 10) * 0.4
            self.color = (220, 50, 50)
            self.secondary_color = (180, 30, 30)
            self.health = 500 + (level // 10) * 300
            self.value = 600
            self.fire_rate = 40
            self.projectile_type = "Плазма"
            self.move_pattern = "Босс"
            self.special_attack_timer = 0
            
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(-100, -self.radius)
        self.max_health = self.health
        self.last_shot = pygame.time.get_ticks() - random.randint(0, 1000)
        self.pattern_timer = 0
        self.is_boss = (self.type == "Босс")
        self.target_x = self.x
        self.target_y = self.y
        self.change_target_timer = 0
        self.fire_cooldown = True
        self.cooldown_end = self.spawn_time + 5000
        self.cooldown_duration = random.randint(10000, 15000)  # 10-15 секунд отдыха
        self.fire_duration = random.randint(20000, 25000)      # 20-25 секунд стрельбы
        
        if self.type == "Босс":
            self.cooldown_duration = random.randint(5000, 8000)
            self.fire_duration = random.randint(15000, 20000)
        
    def move(self, player_x, player_y):
        self.pattern_timer += 1
        self.change_target_timer += 1
        
        if self.type == "Босс":
            self.special_attack_timer += 1
        
        if self.change_target_timer > 60 or (self.target_x == self.x and self.target_y == self.y):
            self.change_target_timer = 0
            if self.move_pattern == "Преследование":
                self.target_x = player_x + random.randint(-100, 100)
                self.target_y = player_y - 200
            elif self.move_pattern == "Волна":
                self.target_x = random.randint(self.radius, WIDTH - self.radius)
                self.target_y = self.y + 100
            elif self.move_pattern == "Спираль":
                self.target_x = self.x + random.randint(-50, 50)
                self.target_y = self.y + 50
            else:
                self.target_x = self.x
                self.target_y = self.y + 100
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = max(0.1, math.sqrt(dx*dx + dy*dy))
        
        if distance > 5:
            move_speed = min(self.speed, distance)
            self.x += (dx / distance) * move_speed
            self.y += (dy / distance) * move_speed
            
        if self.move_pattern == "Зигзаг":
            self.x += math.sin(self.pattern_timer * 0.1) * 4
        elif self.move_pattern == "Круговое":
            self.x += math.sin(self.pattern_timer * 0.05) * 5
            self.y += math.cos(self.pattern_timer * 0.05) * 0.7
        elif self.move_pattern == "Волна":
            self.x += math.sin(self.pattern_timer * 0.08) * 5
        elif self.move_pattern == "Спираль":
            self.x += math.sin(self.pattern_timer * 0.03) * 4
            self.y += math.cos(self.pattern_timer * 0.03) * 0.7
        elif self.move_pattern == "Босс":
            if self.pattern_timer % 300 < 150:
                self.x += math.sin(self.pattern_timer * 0.02) * 2
            else:
                self.x -= math.sin(self.pattern_timer * 0.02) * 2
            
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = min(HEIGHT * 0.7, self.y)
            
    def draw(self, surface):
        # Истребитель
        if self.type == "Истребитель":
            hull_points = [
                (self.x, self.y - self.radius),
                (self.x - self.radius*0.9, self.y + self.radius*0.2),
                (self.x - self.radius*0.7, self.y + self.radius*0.7),
                (self.x + self.radius*0.7, self.y + self.radius*0.7),
                (self.x + self.radius*0.9, self.y + self.radius*0.2)
            ]
            pygame.draw.polygon(surface, self.color, hull_points)
            pygame.draw.polygon(surface, self.secondary_color, hull_points, 3)
            
            wing_points = [
                (self.x - self.radius*0.5, self.y - self.radius*0.2),
                (self.x - self.radius*1.4, self.y - self.radius*0.6),
                (self.x - self.radius*0.9, self.y + self.radius*0.1),
                (self.x - self.radius*0.5, self.y + self.radius*0.3)
            ]
            pygame.draw.polygon(surface, self.secondary_color, wing_points)
            
            wing_points = [
                (self.x + self.radius*0.5, self.y - self.radius*0.2),
                (self.x + self.radius*1.4, self.y - self.radius*0.6),
                (self.x + self.radius*0.9, self.y + self.radius*0.1),
                (self.x + self.radius*0.5, self.y + self.radius*0.3)
            ]
            pygame.draw.polygon(surface, self.secondary_color, wing_points)
            
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.x), int(self.y - self.radius*0.3)), self.radius*0.35)
            pygame.draw.circle(surface, DARK_BLUE, (int(self.x), int(self.y - self.radius*0.3)), self.radius*0.35, 3)
            
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x - self.radius*0.25, self.y + self.radius*0.4, 
                            self.radius*0.5, self.radius*0.35))
            flame_size = random.randint(4, 10)
            pygame.draw.rect(surface, ORANGE, 
                           (self.x - self.radius*0.2, self.y + self.radius*0.75, 
                            self.radius*0.4, flame_size))
            
        # Бомбардировщик
        elif self.type == "Бомбардировщик":
            pygame.draw.ellipse(surface, self.color, 
                               (self.x - self.radius*0.9, self.y - self.radius*0.5, 
                                self.radius*1.8, self.radius*0.9))
            pygame.draw.ellipse(surface, self.secondary_color, 
                               (self.x - self.radius*0.9, self.y - self.radius*0.5, 
                                self.radius*1.8, self.radius*0.9), 3)
            
            pygame.draw.rect(surface, self.secondary_color, 
                           (self.x - self.radius*1.4, self.y - self.radius*0.1, 
                            self.radius*2.8, self.radius*0.5))
            
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.x), int(self.y - self.radius*0.2)), self.radius*0.35)
            pygame.draw.circle(surface, DARK_BLUE, (int(self.x), int(self.y - self.radius*0.2)), self.radius*0.35, 3)
            
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x - self.radius*0.8, self.y + self.radius*0.2, 
                            self.radius*0.5, self.radius*0.45))
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x + self.radius*0.3, self.y + self.radius*0.2, 
                            self.radius*0.5, self.radius*0.45))
            
            flame_size = random.randint(6, 14)
            pygame.draw.rect(surface, ORANGE, 
                           (self.x - self.radius*0.7, self.y + self.radius*0.65, 
                            self.radius*0.35, flame_size))
            pygame.draw.rect(surface, ORANGE, 
                           (self.x + self.radius*0.35, self.y + self.radius*0.65, 
                            self.radius*0.35, flame_size))
            
        # Перехватчик
        elif self.type == "Перехватчик":
            hull_points = [
                (self.x, self.y - self.radius),
                (self.x - self.radius*0.8, self.y),
                (self.x, self.y + self.radius),
                (self.x + self.radius*0.8, self.y)
            ]
            pygame.draw.polygon(surface, self.color, hull_points)
            pygame.draw.polygon(surface, self.secondary_color, hull_points, 3)
            
            wing_points = [
                (self.x - self.radius*0.6, self.y - self.radius*0.2),
                (self.x - self.radius*1.7, self.y - self.radius*0.9),
                (self.x - self.radius*1.2, self.y + self.radius*0.1),
                (self.x - self.radius*0.5, self.y + self.radius*0.2)
            ]
            pygame.draw.polygon(surface, self.secondary_color, wing_points)
            
            wing_points = [
                (self.x + self.radius*0.6, self.y - self.radius*0.2),
                (self.x + self.radius*1.7, self.y - self.radius*0.9),
                (self.x + self.radius*1.2, self.y + self.radius*0.1),
                (self.x + self.radius*0.5, self.y + self.radius*0.2)
            ]
            pygame.draw.polygon(surface, self.secondary_color, wing_points)
            
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.x), int(self.y - self.radius*0.3)), self.radius*0.3)
            
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x - self.radius*0.2, self.y + self.radius*0.7, 
                            self.radius*0.4, self.radius*0.35))
            flame_size = random.randint(5, 11)
            pygame.draw.rect(surface, ORANGE, 
                           (self.x - self.radius*0.15, self.y + self.radius*1.05, 
                            self.radius*0.3, flame_size))
            
        # Крейсер
        elif self.type == "Крейсер":
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.radius, self.y - self.radius*0.5, 
                            self.radius*2, self.radius*0.9))
            pygame.draw.rect(surface, self.secondary_color, 
                           (self.x - self.radius, self.y - self.radius*0.5, 
                            self.radius*2, self.radius*0.9), 3)
            
            pygame.draw.rect(surface, self.secondary_color, 
                           (self.x - self.radius*0.7, self.y - self.radius*0.9, 
                            self.radius*1.4, self.radius*0.5))
            
            pygame.draw.rect(surface, STEEL_BLUE, 
                           (self.x - self.radius*1.0, self.y - self.radius*0.3, 
                            self.radius*0.4, self.radius*0.7))
            pygame.draw.rect(surface, STEEL_BLUE, 
                           (self.x + self.radius*0.6, self.y - self.radius*0.3, 
                            self.radius*0.4, self.radius*0.7))
            
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x - self.radius*0.9, self.y + self.radius*0.3, 
                            self.radius*0.5, self.radius*0.35))
            pygame.draw.rect(surface, DARK_RED, 
                           (self.x + self.radius*0.4, self.y + self.radius*0.3, 
                            self.radius*0.5, self.radius*0.35))
            
            flame_size = random.randint(6, 12)
            pygame.draw.rect(surface, ORANGE, 
                           (self.x - self.radius*0.8, self.y + self.radius*0.65, 
                            self.radius*0.35, flame_size))
            pygame.draw.rect(surface, ORANGE, 
                           (self.x + self.radius*0.45, self.y + self.radius*0.65, 
                            self.radius*0.35, flame_size))
            
        # Босс
        elif self.type == "Босс":
            # Основной корпус
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, self.secondary_color, (int(self.x), int(self.y)), self.radius, 6)
            
            # Детали корпуса
            for i in range(10):
                angle = i * (2 * math.pi / 10)
                dx = math.cos(angle) * self.radius * 0.8
                dy = math.sin(angle) * self.radius * 0.8
                pygame.draw.circle(surface, BRONZE, (int(self.x + dx), int(self.y + dy)), self.radius*0.18)
            
            # Орудия
            for i in range(8):
                angle = i * (2 * math.pi / 8) + (pygame.time.get_ticks() / 800)
                dx = math.cos(angle) * self.radius
                dy = math.sin(angle) * self.radius
                pygame.draw.line(surface, RED, (self.x, self.y), 
                               (self.x + dx, self.y + dy), 10)
                pygame.draw.circle(surface, STEEL_BLUE, (int(self.x + dx*0.7), int(self.y + dy*0.7)), self.radius*0.25)
            
            # Кабина
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.x), int(self.y)), self.radius*0.45)
            pygame.draw.circle(surface, DARK_BLUE, (int(self.x), int(self.y)), self.radius*0.45, 4)
        
        # Полоска здоровья
        health_width = 70 if not self.is_boss else 250
        health_height = 8 if not self.is_boss else 15
        y_offset = -25 if not self.is_boss else -50
        
        pygame.draw.rect(surface, (80, 80, 80), 
                        (self.x - health_width//2, self.y - self.radius + y_offset, 
                         health_width, health_height))
        pygame.draw.rect(surface, RED, 
                        (self.x - health_width//2, self.y - self.radius + y_offset, 
                         health_width * (self.health / self.max_health), health_height))
        
        # Для босса добавляем уровень
        if self.is_boss:
            level_text = font_medium.render(f"Босс: {self.boss_name}", True, YELLOW)
            surface.blit(level_text, (self.x - level_text.get_width()//2, self.y - self.radius - 70))
    
    def shoot(self, current_time, player_x, player_y):
        if current_time - self.spawn_time < 5000:
            return []
        
        if self.fire_cooldown:
            if current_time > self.cooldown_end:
                self.fire_cooldown = False
                self.fire_end = current_time + self.fire_duration
        else:
            if current_time > self.fire_end:
                self.fire_cooldown = True
                self.cooldown_end = current_time + self.cooldown_duration
                return []
        
        if not self.fire_cooldown:
            if self.type == "Босс":
                if current_time - self.last_shot > self.fire_rate + random.randint(-50, 50):
                    self.last_shot = current_time
                    projectiles = []
                    
                    # Основной выстрел в игрока
                    dx = player_x - self.x
                    dy = player_y - self.y
                    distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                    p = Projectile(self.x, self.y + self.radius, 1, "Плазма", 'enemy')
                    p.dx = dx / distance * 3.5
                    p.dy = dy / distance * 3.5
                    projectiles.append(p)
                    
                    # Вспомогательные выстрелы
                    angle = (pygame.time.get_ticks() / 40) % (2 * math.pi)
                    for i in range(5):
                        dx = math.cos(angle + i * math.pi/2.5) * 4.5
                        dy = math.sin(angle + i * math.pi/2.5) * 4.5
                        p = Projectile(self.x, self.y + self.radius, 1, "Плазма", 'enemy')
                        p.dx = dx
                        p.dy = dy
                        projectiles.append(p)
                    
                    # Специальная атака
                    if self.special_attack_timer > 250:
                        self.special_attack_timer = 0
                        for i in range(10):
                            angle = i * (2 * math.pi / 10)
                            p = Projectile(self.x, self.y + self.radius, 1, "Плазма", 'enemy')
                            p.dx = math.cos(angle) * 3.5
                            p.dy = math.sin(angle) * 3.5
                            projectiles.append(p)
                    
                    return projectiles
            else:
                if random.random() < 0.85:
                    if current_time - self.last_shot > self.fire_rate + random.randint(-50, 50):
                        self.last_shot = current_time
                        
                        if self.type == "Бомбардировщик":
                            projectiles = []
                            for i in range(-1, 2):
                                projectiles.append(Projectile(self.x + i*18, self.y + self.radius, 1, self.projectile_type, 'enemy'))
                            return projectiles
                        elif self.type == "Крейсер":
                            projectiles = []
                            angles = [-0.4, 0, 0.4]
                            for angle in angles:
                                p = Projectile(self.x, self.y + self.radius, 1, self.projectile_type, 'enemy')
                                p.dx = math.sin(angle) * 2.5
                                p.dy = 1.2
                                projectiles.append(p)
                            return projectiles
                        elif self.type == "Перехватчик":
                            dx = player_x - self.x
                            dy = player_y - self.y
                            distance = max(0.1, math.sqrt(dx*dx + dy*dy))
                            p = Projectile(self.x, self.y + self.radius, 1, self.projectile_type, 'enemy')
                            p.dx = dx / distance * 2.5
                            p.dy = dy / distance * 2.5
                            return [p]
                        else:
                            offset_x = random.randint(-15, 15)
                            return [Projectile(self.x + offset_x, self.y + self.radius, 1, self.projectile_type, 'enemy')]
        return []
    
    def is_off_screen(self):
        return self.y > HEIGHT + self.radius

# Класс бонуса
class Bonus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.speed = 3.5
        self.type = random.choice(["Здоровье", "Щит", "Энергия", "Оружие", "Способность", "Кредиты"])
        self.colors = {
            "Здоровье": RED,
            "Щит": GREEN,
            "Энергия": BLUE,
            "Оружие": PURPLE,
            "Способность": ORANGE,
            "Кредиты": GOLD
        }
        self.color = self.colors[self.type]
        self.pulse = 0
        self.value = random.randint(15, 60) if self.type == "Кредиты" else 0
        
    def move(self):
        self.y += self.speed
        self.pulse = (self.pulse + 0.12) % (2 * math.pi)
        
    def draw(self, surface):
        pulse_size = math.sin(self.pulse) * 4
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius + pulse_size)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius + pulse_size, 3)
        
        symbol = ""
        if self.type == "Здоровье": symbol = "♥"
        elif self.type == "Щит": symbol = "⛊"
        elif self.type == "Энергия": symbol = "⚡"
        elif self.type == "Оружие": symbol = "⚔"
        elif self.type == "Способность": symbol = "★"
        elif self.type == "Кредиты": symbol = "¢"
        
        text = font_medium.render(symbol, True, WHITE)
        surface.blit(text, (self.x - text.get_width()//2, self.y - text.get_height()//2))
        
        if self.type == "Кредиты":
            value_text = font_tiny.render(str(self.value), True, WHITE)
            surface.blit(value_text, (self.x - value_text.get_width()//2, self.y + 18))
    
    def is_off_screen(self):
        return self.y > HEIGHT + self.radius

# Класс взрыва
class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size * 5
        self.current_size = size
        self.growth_rate = size * 0.6
        self.color = ORANGE
        self.alpha = 255
        self.particles = []
        
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 9)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(1.5, 6.0),
                'lifetime': random.randint(25, 70),
                'color': random.choice([ORANGE, YELLOW, RED, (255, 180, 0)])
            })
        
    def update(self):
        self.current_size += self.growth_rate
        self.alpha -= 7
        
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['lifetime'] -= 1
            p['size'] *= 0.96
        
        return self.alpha > 0
        
    def draw(self, surface):
        if self.current_size < self.max_size:
            alpha_surface = pygame.Surface((self.current_size * 2, self.current_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.color, self.alpha), 
                              (self.current_size, self.current_size), self.current_size)
            surface.blit(alpha_surface, (self.x - self.current_size, self.y - self.current_size))
        
        for p in self.particles:
            if p['lifetime'] > 0:
                alpha = min(255, p['lifetime'] * 5)
                pygame.draw.circle(surface, (*p['color'], alpha), 
                                  (int(p['x']), int(p['y'])), p['size'])

# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        
        if len(text) > 15:
            parts = text.split()
            if len(parts) > 1:
                mid = len(parts) // 2
                self.text_lines = [
                    " ".join(parts[:mid]),
                    " ".join(parts[mid:])
                ]
            else:
                self.text_lines = [text]
        else:
            self.text_lines = [text]
        
        self.text_surfs = [font_button.render(line, True, WHITE) for line in self.text_lines]
        self.text_rects = []
        
        total_height = sum(surf.get_height() for surf in self.text_surfs)
        current_y = self.rect.centery - total_height // 2
        
        for surf in self.text_surfs:
            rect = surf.get_rect(centerx=self.rect.centerx, centery=current_y + surf.get_height() // 2)
            self.text_rects.append(rect)
            current_y += surf.get_height()
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=18)
        pygame.draw.rect(surface, WHITE, self.rect, 4, border_radius=18)
        
        shadow = pygame.Rect(self.rect.x + 6, self.rect.y + 6, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 120), shadow, border_radius=18)
        
        for surf, rect in zip(self.text_surfs, self.text_rects):
            surface.blit(surf, rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered
        
    def is_clicked(self, pos, clicked):
        return self.rect.collidepoint(pos) and clicked

# Класс игры
class Game:
    def __init__(self):
        self.player = Player()
        self.projectiles = []
        self.enemies = []
        self.bonuses = []
        self.explosions = []
        self.level = 1
        self.max_level = 100
        self.game_state = "Меню"
        self.score = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1000
        self.starfield_speed = 0.6
        self.last_level_up = 0
        self.boss_active = False
        self.boss = None
        self.boss_intro = None
        self.level_progress = 0
        self.level_requirements = self.generate_level_requirements()
        self.save_file = "save_game.json"
        self.time_scale = 1.0
        self.damage_boost = 1.0
        self.achievement_notifications = []
        self.ability_explosions = []
        self.game_start_time = time.time()
        
        # Прокрутка для экранов
        self.instructions_scroll_offset = 0
        self.achievements_scroll_offset = 0
        self.scroll_dragging = False
        self.scroll_drag_start = 0
        
        button_width, button_height = 400, 80
        button_spacing = 35
        start_y = HEIGHT//2 - 220
        
        self.buttons = [
            Button(WIDTH//2 - button_width//2, start_y, button_width, button_height, "Новая игра", BLUE, LIGHT_BLUE),
            Button(WIDTH//2 - button_width//2, start_y + button_height + button_spacing, button_width, button_height, "Продолжить", GREEN, (100, 255, 100)),
            Button(WIDTH//2 - button_width//2, start_y + 2*(button_height + button_spacing), button_width, button_height, "Кастомизация", PURPLE, (220, 100, 255)),
            Button(WIDTH//2 - button_width//2, start_y + 3*(button_height + button_spacing), button_width, button_height, "Инструкции", ORANGE, (255, 180, 50)),
            Button(WIDTH//2 - button_width//2, start_y + 4*(button_height + button_spacing), button_width, button_height, "Достижения", LIGHT_PURPLE, (180, 120, 220)),
            Button(WIDTH//2 - button_width//2, start_y + 5*(button_height + button_spacing), button_width, button_height, "Выход", RED, (255, 100, 100))
        ]
        
        custom_button_width, custom_button_height = 280, 70
        self.customization_buttons = [
            Button(WIDTH//2 - 350, HEIGHT//2 - 170, custom_button_width, custom_button_height, "Цвета", PURPLE, (220, 100, 255)),
            Button(WIDTH//2 - 350, HEIGHT//2 - 60, custom_button_width, custom_button_height, "Модели", ORANGE, (255, 180, 50)),
            Button(WIDTH//2 - 350, HEIGHT//2 + 50, custom_button_width, custom_button_height, "Способности", CYAN, (100, 255, 255)),
            Button(WIDTH//2 - 350, HEIGHT//2 + 160, custom_button_width, custom_button_height, "Назад", BLUE, LIGHT_BLUE)
        ]
        
        self.load_game()
        
    def generate_level_requirements(self):
        requirements = {}
        for i in range(1, 101):
            if i % 10 == 0:
                requirements[i] = 1
            else:
                requirements[i] = 10 + (i // 10) * 5 + (i % 10) * 3
        return requirements
    
    def spawn_enemy(self):
        if self.boss_active and self.boss:
            return
            
        if self.level_progress < self.level_requirements[self.level]:
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
                self.enemies.append(Enemy(self.level))
                self.enemy_spawn_timer = current_time
                self.enemy_spawn_delay = max(300, 1300 - self.level * 18)
                self.enemy_spawn_delay += random.randint(-100, 100)
    
    def spawn_boss(self):
        self.boss_active = True
        self.boss = Enemy(self.level, "Босс")
        self.boss_intro = BossIntro(self.boss.boss_name, self.level)
        self.enemies.append(self.boss)
    
    def spawn_bonus(self, x, y):
        if random.random() < 0.3:
            self.bonuses.append(Bonus(x, y))
    
    def create_explosion(self, x, y, size):
        self.explosions.append(Explosion(x, y, size))
    
    def save_game(self):
        # Обновляем общее время игры
        self.player.total_play_time += time.time() - self.game_start_time
        self.game_start_time = time.time()
        
        data = {
            "level": self.level,
            "score": self.player.score,
            "credits": self.player.credits,
            "kill_count": self.player.kill_count,
            "boss_kills": self.player.boss_kills,
            "dodge_count": self.player.dodge_count,
            "weapon_type": self.player.weapon_type,
            "weapon_level": self.player.weapon_level,
            "engine_level": self.player.engine_level,
            "shield_level": self.player.shield_level,
            "abilities": self.player.abilities,
            "ship_upgrades": self.player.ship_upgrades,
            "ship_skins": self.player.ship_skins,
            "achievements": self.player.achievements,
            "total_play_time": self.player.total_play_time
        }
        
        try:
            with open(self.save_file, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load_game(self):
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    
                self.level = data.get("level", 1)
                self.player.score = data.get("score", 0)
                self.player.credits = data.get("credits", 600)
                self.player.kill_count = data.get("kill_count", 0)
                self.player.boss_kills = data.get("boss_kills", 0)
                self.player.dodge_count = data.get("dodge_count", 0)
                self.player.weapon_type = data.get("weapon_type", "Импульсный лазер")
                self.player.weapon_level = data.get("weapon_level", 1)
                self.player.engine_level = data.get("engine_level", 1)
                self.player.shield_level = data.get("shield_level", 1)
                self.player.abilities = data.get("abilities", self.player.abilities)
                self.player.ship_upgrades = data.get("ship_upgrades", self.player.ship_upgrades)
                
                # Загрузка скинов с проверкой полей
                saved_skins = data.get("ship_skins", {})
                for skin_name in self.player.ship_skins:
                    if skin_name in saved_skins:
                        # Объединяем сохраненные данные с данными по умолчанию
                        for key in ["owned", "equipped", "cost", "color", "secondary"]:
                            if key in saved_skins[skin_name]:
                                self.player.ship_skins[skin_name][key] = saved_skins[skin_name][key]
                
                # Загрузка достижений
                saved_achievements = data.get("achievements", {})
                for achievement in self.player.achievements:
                    if achievement in saved_achievements:
                        self.player.achievements[achievement] = saved_achievements[achievement]
                
                self.player.total_play_time = data.get("total_play_time", 0)
                
                return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        return False
    
    def reset_game(self):
        self.player = Player()
        self.projectiles = []
        self.enemies = []
        self.bonuses = []
        self.explosions = []
        self.level = 1
        self.score = 0
        self.boss_active = False
        self.boss = None
        self.boss_intro = None
        self.level_progress = 0
        self.level_requirements = self.generate_level_requirements()
        self.time_scale = 1.0
        self.damage_boost = 1.0
        self.achievement_notifications = []
        self.ability_explosions = []
        self.game_start_time = time.time()
        self.instructions_scroll_offset = 0
        self.achievements_scroll_offset = 0
    
    def start_level(self):
        self.projectiles = []
        self.enemies = []
        self.bonuses = []
        self.explosions = []
        self.level_progress = 0
        self.boss_active = False
        self.boss = None
        self.boss_intro = None
        self.time_scale = 1.0
        self.damage_boost = 1.0
        self.ability_explosions = []
        
        self.player.health = self.player.max_health
        self.player.shield = self.player.max_shield
        self.player.energy = self.player.max_energy
        self.player.x = WIDTH // 2
        self.player.y = HEIGHT - 200
        
        if self.level % 10 == 0:
            self.spawn_boss()
        
        self.enemy_spawn_timer = pygame.time.get_ticks()
    
    def check_achievements(self):
        achievements_to_check = [
            ("Первый выстрел", self.player.kill_count >= 1),
            ("10 убийств", self.player.kill_count >= 10),
            ("50 убийств", self.player.kill_count >= 50),
            ("100 убийств", self.player.kill_count >= 100),
            ("500 убийств", self.player.kill_count >= 500),
            ("1000 убийств", self.player.kill_count >= 1000),
            ("Боссобой", self.player.boss_kills >= 1),
            ("Повелитель боссов", self.player.boss_kills >= 10),
            ("Уровень 10", self.level >= 10),
            ("Уровень 50", self.level >= 50),
            ("Уровень 100", self.level >= 100),
            ("Мастер щита", self.player.shield_level >= 5),
            ("Мастер оружия", self.player.weapon_level >= 10),
            ("Богач", self.player.credits >= 1500),
            ("Миллионер", self.player.credits >= 1000000),
            ("Коллекционер", all(skin["owned"] for skin in self.player.ship_skins.values())),
            ("Неуязвимый", self.player.dodge_count >= 100),
            ("Скоростной", self.player.engine_level >= 10),
            ("Экономист", self.player.credits >= 50000),
            ("Перфекционист", all(self.player.achievements[ach] for ach in self.player.achievements if ach != "Перфекционист")),
            ("Мастер помощи", self.player.abilities["Вызов помощи"]["level"] >= 1)  # Новое достижение
        ]
        
        descriptions = {
            "Первый выстрел": "Уничтожьте 1 врага",
            "10 убийств": "Уничтожьте 10 врагов",
            "50 убийств": "Уничтожьте 50 врагов",
            "100 убийств": "Уничтожьте 100 врагов",
            "500 убийств": "Уничтожьте 500 врагов",
            "1000 убийств": "Уничтожьте 1000 врагов",
            "Боссобой": "Победите 1 босса",
            "Повелитель боссов": "Победите 10 боссов",
            "Уровень 10": "Достигните 10 уровня",
            "Уровень 50": "Достигните 50 уровня",
            "Уровень 100": "Достигните 100 уровня",
            "Мастер щита": "Улучшите щиты до 5 уровня",
            "Мастер оружия": "Улучшите оружие до 10 уровня",
            "Богач": "Заработайте 1500 кредитов",
            "Миллионер": "Заработайте 1,000,000 кредитов",
            "Коллекционер": "Купите все скины корабля",
            "Неуязвимый": "Выполните 100 уклонений",
            "Скоростной": "Улучшите двигатель до 10 уровня",
            "Экономист": "Заработайте 50,000 кредитов",
            "Перфекционист": "Откройте все достижения",
            "Мастер помощи": "Используйте способность 'Вызов помощи'"
        }
        
        for achievement, condition in achievements_to_check:
            if not self.player.achievements.get(achievement, False) and condition:
                self.player.achievements[achievement] = True
                self.achievement_notifications.append(
                    AchievementNotification(achievement, descriptions.get(achievement, ""))
                )

    def handle_events(self):
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_scroll = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "Игра":
                        self.game_state = "Пауза"
                    elif self.game_state == "Пауза":
                        self.game_state = "Игра"
                    elif self.game_state == "Меню":
                        self.save_game()
                        pygame.quit()
                        sys.exit()
                    elif self.game_state in ["Инструкции", "Достижения", "Кастомизация"]:
                        self.game_state = "Меню"
                        
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                        
                if event.key == pygame.K_SPACE and self.game_state == "Игра":
                    self.player.auto_fire = True
                
                if event.key == pygame.K_q and self.game_state == "Игра":
                    ability_result = self.player.activate_ability()
                    if ability_result:
                        if self.player.special_ability == "Ракетный залп":
                            if isinstance(ability_result, list):
                                self.projectiles.extend(ability_result)
                        elif self.player.special_ability == "Энергетический взрыв":
                            if isinstance(ability_result, list):
                                for explosion in ability_result:
                                    self.ability_explosions.append({
                                        'x': explosion['x'],
                                        'y': explosion['y'],
                                        'size': explosion['size'],
                                        'timer': explosion['timer']
                                    })
                
                if event.key == pygame.K_e and self.game_state == "Игра":
                    self.player.dodge()
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.game_state == "Игра":
                    self.player.auto_fire = False
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = True
                
                if event.button == 4:  # Колесико вверх
                    mouse_scroll = 1
                elif event.button == 5:  # Колесико вниз
                    mouse_scroll = -1
                elif event.button == 1:  # Левая кнопка мыши
                    # Проверка на захват скроллбара
                    if self.game_state == "Инструкции":
                        scrollbar_rect = pygame.Rect(WIDTH - 30, 150, 20, HEIGHT - 300)
                        if scrollbar_rect.collidepoint(mouse_pos):
                            self.scroll_dragging = True
                            self.scroll_drag_start = mouse_pos[1]
                    elif self.game_state == "Достижения":
                        scrollbar_rect = pygame.Rect(WIDTH - 30, 150, 20, HEIGHT - 300)
                        if scrollbar_rect.collidepoint(mouse_pos):
                            self.scroll_dragging = True
                            self.scroll_drag_start = mouse_pos[1]
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    self.scroll_dragging = False
                
            if self.game_state == "Меню":
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(mouse_pos, mouse_clicked):
                        if i == 0:
                            self.reset_game()
                            self.start_level()
                            self.game_state = "Игра"
                        elif i == 1:
                            self.start_level()
                            self.game_state = "Игра"
                        elif i == 2:
                            self.game_state = "Кастомизация"
                        elif i == 3:
                            self.game_state = "Инструкции"
                        elif i == 4:
                            self.game_state = "Достижения"
                        elif i == 5:
                            self.save_game()
                            pygame.quit()
                            sys.exit()
                
            elif self.game_state == "Конец игры":
                restart_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 220, 360, 80, "Новая игра", BLUE, LIGHT_BLUE)
                menu_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 320, 360, 80, "Главное меню", GREEN, (100, 255, 100))
                
                if restart_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.reset_game()
                    self.start_level()
                    self.game_state = "Игра"
                elif menu_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.game_state = "Меню"
                
            elif self.game_state == "Улучшения":
                health_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 220, 300, 80, "Здоровье +25", RED, (255, 100, 100))
                shield_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 110, 300, 80, "Щит +25", GREEN, (100, 255, 100))
                weapon_btn = Button(WIDTH//2 - 350, HEIGHT//2, 300, 80, "Оружие +1", PURPLE, (200, 100, 255))
                engine_btn = Button(WIDTH//2 - 350, HEIGHT//2 + 110, 300, 80, "Двигатель +1", ORANGE, (255, 180, 50))
                back_btn = Button(WIDTH//2 + 50, HEIGHT//2 + 110, 300, 80, "Продолжить", BLUE, LIGHT_BLUE)
                
                if health_btn.is_clicked(mouse_pos, mouse_clicked) and self.player.credits >= 150:
                    self.player.credits -= 150
                    self.player.max_health += 25
                    self.player.health = self.player.max_health
                elif shield_btn.is_clicked(mouse_pos, mouse_clicked) and self.player.credits >= 150:
                    self.player.credits -= 150
                    self.player.max_shield += 25
                    self.player.shield = self.player.max_shield
                elif weapon_btn.is_clicked(mouse_pos, mouse_clicked) and self.player.credits >= 200 and self.player.weapon_level < 10:
                    self.player.credits -= 200
                    self.player.weapon_level += 1
                elif engine_btn.is_clicked(mouse_pos, mouse_clicked) and self.player.credits >= 200:
                    self.player.credits -= 200
                    self.player.engine_level += 1
                    self.player.speed += 0.7
                elif back_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.game_state = "Игра"
                    self.start_level()
                
            elif self.game_state == "Кастомизация":
                for i, button in enumerate(self.customization_buttons):
                    if button.is_clicked(mouse_pos, mouse_clicked):
                        if i == 3:
                            self.game_state = "Меню"
                
            elif self.game_state == "Инструкции":
                back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
                if back_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.game_state = "Меню"
                
            elif self.game_state == "Достижения":
                back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
                if back_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.game_state = "Меню"
                
            elif self.game_state == "Пауза":
                resume_btn = Button(WIDTH//2 - 180, HEIGHT//2, 360, 80, "Продолжить", GREEN, (100, 255, 100))
                menu_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 110, 360, 80, "Главное меню", BLUE, LIGHT_BLUE)
                
                if resume_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.game_state = "Игра"
                elif menu_btn.is_clicked(mouse_pos, mouse_clicked):
                    self.save_game()
                    self.game_state = "Меню"
            
            # Обработка прокрутки колесиком мыши
            if mouse_scroll != 0:
                if self.game_state == "Инструкции":
                    self.instructions_scroll_offset += mouse_scroll * 50
                    # Ограничение прокрутки
                    max_scroll = 2000  # Максимальная прокрутка
                    self.instructions_scroll_offset = max(0, min(max_scroll, self.instructions_scroll_offset))
                elif self.game_state == "Достижения":
                    self.achievements_scroll_offset += mouse_scroll * 50
                    # Ограничение прокрутки
                    max_scroll = 2000  # Максимальная прокрутка
                    self.achievements_scroll_offset = max(0, min(max_scroll, self.achievements_scroll_offset))
            
            if self.scroll_dragging and self.game_state == "Инструкции":
                self.instructions_scroll_offset += (mouse_pos[1] - self.scroll_drag_start) * 0.5
                self.scroll_drag_start = mouse_pos[1]
                # Ограничение прокрутки
                max_scroll = 2000
                self.instructions_scroll_offset = max(0, min(max_scroll, self.instructions_scroll_offset))
            elif self.scroll_dragging and self.game_state == "Достижения":
                self.achievements_scroll_offset += (mouse_pos[1] - self.scroll_drag_start) * 0.5
                self.scroll_drag_start = mouse_pos[1]
                # Ограничение прокрутки
                max_scroll = 2000
                self.achievements_scroll_offset = max(0, min(max_scroll, self.achievements_scroll_offset))
            
            if self.game_state == "Меню":
                for button in self.buttons:
                    button.check_hover(mouse_pos)
            elif self.game_state == "Кастомизация":
                for button in self.customization_buttons:
                    button.check_hover(mouse_pos)
            elif self.game_state == "Инструкции":
                back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
                back_btn.check_hover(mouse_pos)
            elif self.game_state == "Достижения":
                back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
                back_btn.check_hover(mouse_pos)
            elif self.game_state == "Конец игры":
                restart_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 220, 360, 80, "Новая игра", BLUE, LIGHT_BLUE)
                menu_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 320, 360, 80, "Главное меню", GREEN, (100, 255, 100))
                restart_btn.check_hover(mouse_pos)
                menu_btn.check_hover(mouse_pos)
            elif self.game_state == "Пауза":
                resume_btn = Button(WIDTH//2 - 180, HEIGHT//2, 360, 80, "Продолжить", GREEN, (100, 255, 100))
                menu_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 110, 360, 80, "Главное меню", BLUE, LIGHT_BLUE)
                resume_btn.check_hover(mouse_pos)
                menu_btn.check_hover(mouse_pos)
            elif self.game_state == "Улучшения":
                health_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 220, 300, 80, "Здоровье +25", RED, (255, 100, 100))
                shield_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 110, 300, 80, "Щит +25", GREEN, (100, 255, 100))
                weapon_btn = Button(WIDTH//2 - 350, HEIGHT//2, 300, 80, "Оружие +1", PURPLE, (200, 100, 255))
                engine_btn = Button(WIDTH//2 - 350, HEIGHT//2 + 110, 300, 80, "Двигатель +1", ORANGE, (255, 180, 50))
                back_btn = Button(WIDTH//2 + 50, HEIGHT//2 + 110, 300, 80, "Продолжить", BLUE, LIGHT_BLUE)
                health_btn.check_hover(mouse_pos)
                shield_btn.check_hover(mouse_pos)
                weapon_btn.check_hover(mouse_pos)
                engine_btn.check_hover(mouse_pos)
                back_btn.check_hover(mouse_pos)

    def update(self):
        if self.game_state != "Игра":
            return
            
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Обновление анимации появления босса
        if self.boss_intro:
            if not self.boss_intro.update():
                self.boss_intro = None
        
        # Обновление взрывов способностей
        for explosion in self.ability_explosions[:]:
            explosion['timer'] -= 1
            if explosion['timer'] <= 0:
                self.ability_explosions.remove(explosion)
                self.create_explosion(explosion['x'], explosion['y'], explosion['size'])
        
        if self.player.auto_fire:
            new_projectiles = self.player.shoot(current_time)
            if new_projectiles:
                self.projectiles.extend(new_projectiles)
        
        # Стрельба кораблей помощи
        for helper in self.player.helper_ships:
            helper_projectiles = helper.shoot(current_time)
            if helper_projectiles:
                self.projectiles.extend(helper_projectiles)
        
        self.spawn_enemy()
        
        for projectile in self.projectiles[:]:
            projectile.move(self.enemies)
            if projectile.is_off_screen():
                self.projectiles.remove(projectile)
        
        for enemy in self.enemies[:]:
            enemy.move(self.player.x, self.player.y)
            
            enemy_projectile = enemy.shoot(current_time, self.player.x, self.player.y)
            if enemy_projectile:
                if isinstance(enemy_projectile, list):
                    self.projectiles.extend(enemy_projectile)
                else:
                    self.projectiles.append(enemy_projectile)
            
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                if not enemy.is_boss:
                    self.player.health -= 8
        
        for bonus in self.bonuses[:]:
            bonus.move()
            if bonus.is_off_screen():
                self.bonuses.remove(bonus)
        
        for explosion in self.explosions[:]:
            if not explosion.update():
                self.explosions.remove(explosion)
        
        self.check_achievements()
        
        for notification in self.achievement_notifications[:]:
            notification.update()
            if not notification.active:
                self.achievement_notifications.remove(notification)
        
        for projectile in self.projectiles[:]:
            for enemy in self.enemies[:]:
                dx = projectile.x - enemy.x
                dy = projectile.y - enemy.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < projectile.radius + enemy.radius and projectile.source in ['player', 'helper']:
                    damage = projectile.damage * self.damage_boost
                    
                    enemy.health -= damage
                    
                    if enemy.health <= 0:
                        self.score += enemy.value
                        self.player.score += enemy.value
                        self.player.kill_count += 1
                        self.player.credits += enemy.value // 3
                        self.player.energy = min(self.player.max_energy, self.player.energy + 60)
                        self.level_progress += 1
                        self.create_explosion(enemy.x, enemy.y, enemy.radius)
                        
                        if enemy.is_boss:
                            self.boss_active = False
                            self.boss = None
                            self.player.boss_kills += 1
                            self.player.credits += 1200
                            
                            for _ in range(12):
                                self.spawn_bonus(enemy.x, enemy.y)
                        
                        self.enemies.remove(enemy)
                        
                        self.spawn_bonus(enemy.x, enemy.y)
                    
                    if projectile in self.projectiles and not projectile.homing:
                        self.projectiles.remove(projectile)
                    break
        
        for projectile in self.projectiles[:]:
            if projectile.source == 'enemy':
                dx = projectile.x - self.player.x
                dy = projectile.y - self.player.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < projectile.radius + self.player.radius and self.player.invincibility == 0:
                    damage = projectile.damage
                    
                    if self.player.shield > 0:
                        self.player.shield -= damage
                        if self.player.shield < 0:
                            self.player.health += self.player.shield
                            self.player.shield = 0
                    else:
                        self.player.health -= damage
                    
                    self.projectiles.remove(projectile)
                    self.create_explosion(projectile.x, projectile.y, 12)
                    
                    if self.player.health <= 0:
                        self.game_state = "Конец игры"
                        self.save_game()
        
        for enemy in self.enemies[:]:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.player.radius + enemy.radius and self.player.invincibility == 0:
                damage = max(8, enemy.radius)
                
                if self.player.shield > 0:
                    self.player.shield -= damage
                    if self.player.shield < 0:
                        self.player.health += self.player.shield
                        self.player.shield = 0
                else:
                    self.player.health -= damage
                
                self.create_explosion(enemy.x, enemy.y, enemy.radius // 2)
                
                if self.player.health <= 0:
                    self.game_state = "Конец игры"
                    self.save_game()
        
        for bonus in self.bonuses[:]:
            dx = self.player.x - bonus.x
            dy = self.player.y - bonus.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.player.radius + bonus.radius:
                if bonus.type == "Здоровье":
                    self.player.health = min(self.player.max_health, self.player.health + 25)
                elif bonus.type == "Щит":
                    self.player.shield = min(self.player.max_shield, self.player.shield + 35)
                elif bonus.type == "Энергия":
                    self.player.energy = min(self.player.max_energy, self.player.energy + 50)
                elif bonus.type == "Оружие":
                    weapons = ["Импульсный лазер", "Плазма", "Ракеты", "Рельсотрон"]
                    self.player.weapon_type = random.choice(weapons)
                elif bonus.type == "Способность":
                    self.player.ability_cooldown = 0
                elif bonus.type == "Кредиты":
                    self.player.credits += bonus.value
                
                self.bonuses.remove(bonus)
                self.create_explosion(bonus.x, bonus.y, 12)
        
        # Проверка взрывов способностей
        for explosion in self.ability_explosions:
            for enemy in self.enemies[:]:
                dx = explosion['x'] - enemy.x
                dy = explosion['y'] - enemy.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < explosion['size'] + enemy.radius:
                    damage = 60
                    enemy.health -= damage
                    
                    if enemy.health <= 0:
                        self.score += enemy.value
                        self.player.score += enemy.value
                        self.player.kill_count += 1
                        self.player.credits += enemy.value // 3
                        self.player.energy = min(self.player.max_energy, self.player.energy + 60)
                        self.level_progress += 1
                        self.create_explosion(enemy.x, enemy.y, enemy.radius)
                        
                        if enemy.is_boss:
                            self.boss_active = False
                            self.boss = None
                            self.player.boss_kills += 1
                            self.player.credits += 1200
                            
                            for _ in range(12):
                                self.spawn_bonus(enemy.x, enemy.y)
                        
                        self.enemies.remove(enemy)
                        self.spawn_bonus(enemy.x, enemy.y)
        
        if self.level_progress >= self.level_requirements[self.level]:
            self.level += 1
            if self.level > self.max_level:
                self.game_state = "Победа"
                self.save_game()
            else:
                self.player.credits += self.level * 60
                self.game_state = "Улучшения"

    def draw_starfield(self, surface):
        for nebula in nebulas:
            x, y, radius, color = nebula
            alpha_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*color, 35), (radius, radius), radius)
            surface.blit(alpha_surface, (x - radius, y - radius))
        
        for star in stars:
            x, y, size, speed, brightness = star
            y += self.starfield_speed * speed
            if y > HEIGHT:
                y = 0
                x = random.randint(0, WIDTH)
            star[1] = y
            
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(x), int(y)), size)
            
            if brightness > 200 and size > 1.5:
                glow_size = size * 2.5
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, 60), (glow_size, glow_size), glow_size)
                surface.blit(glow_surface, (x - glow_size, y - glow_size))
    
    def draw_ui(self, surface):
        # Уменьшенные счетчики в правом верхнем углу
        score_text = font_small.render(f"Очки: {self.player.score}", True, YELLOW)
        level_text = font_small.render(f"Уровень: {self.level}/100", True, PURPLE)
        credits_text = font_small.render(f"Кредиты: {self.player.credits}", True, GOLD)
        kills_text = font_small.render(f"Уничтожено: {self.player.kill_count}", True, WHITE)
        
        surface.blit(score_text, (WIDTH - score_text.get_width() - 25, 25))
        surface.blit(level_text, (WIDTH - level_text.get_width() - 25, 70))
        surface.blit(credits_text, (WIDTH - credits_text.get_width() - 25, 115))
        surface.blit(kills_text, (WIDTH - kills_text.get_width() - 25, 160))
        
        # Таймеры способностей
        if self.player.helper_timer > 0:
            helper_time = self.player.helper_timer // 60
            helper_text = font_tiny.render(f"Помощь: {helper_time} сек", True, GREEN)
            surface.blit(helper_text, (WIDTH - helper_text.get_width() - 25, 205))
        
        # Полоски здоровья, щита и энергии
        bar_width = 250
        pygame.draw.rect(surface, (50, 50, 70), (25, 25, bar_width, 25))
        health_width = (bar_width - 5) * (self.player.health / self.player.max_health)
        health_color = RED if self.player.health < 40 else GREEN
        pygame.draw.rect(surface, health_color, (27, 27, health_width, 21))
        
        pygame.draw.rect(surface, (50, 50, 70), (25, 60, bar_width, 25))
        shield_width = (bar_width - 5) * (self.player.shield / self.player.max_shield)
        shield_color = CYAN if self.player.special_ability == "Усиление щита" and self.player.ability_duration > 0 else GREEN
        pygame.draw.rect(surface, shield_color, (27, 62, shield_width, 21))
        
        pygame.draw.rect(surface, (50, 50, 70), (25, 95, bar_width, 25))
        energy_width = (bar_width - 5) * (self.player.energy / self.player.max_energy)
        pygame.draw.rect(surface, BLUE, (27, 97, energy_width, 21))
        
        # Текстовые метки для полосок
        health_text = font_tiny.render(f"HP: {int(self.player.health)}", True, WHITE)
        shield_text = font_tiny.render(f"SH: {int(self.player.shield)}", True, WHITE)
        energy_text = font_tiny.render(f"EN: {int(self.player.energy)}", True, WHITE)
        
        surface.blit(health_text, (bar_width + 35, 28))
        surface.blit(shield_text, (bar_width + 35, 63))
        surface.blit(energy_text, (bar_width + 35, 98))
        
        # Оружие и характеристики
        weapon_text = font_tiny.render(f"Оружие: {self.player.weapon_type} Ур. {self.player.weapon_level}", True, WHITE)
        engine_text = font_tiny.render(f"Двигатель: Ур. {self.player.engine_level}", True, WHITE)
        shield_level_text = font_tiny.render(f"Щит: Ур. {self.player.shield_level}", True, WHITE)
        
        surface.blit(weapon_text, (25, HEIGHT - 90))
        surface.blit(engine_text, (25, HEIGHT - 60))
        surface.blit(shield_level_text, (25, HEIGHT - 30))
        
        # Способности и уклонение
        ability_text = font_tiny.render(f"Способность: {self.player.special_ability}", True, ORANGE)
        surface.blit(ability_text, (WIDTH - 400, HEIGHT - 90))
        
        ability_status = "Активна" if self.player.ability_duration > 0 else f"Готовность: {100 - self.player.ability_cooldown//6}%"
        ability_color = GREEN if self.player.ability_duration > 0 else YELLOW
        ability_status_text = font_tiny.render(ability_status, True, ability_color)
        surface.blit(ability_status_text, (WIDTH - 400, HEIGHT - 60))
        
        dodge_status = "Готов" if self.player.dodge_cooldown == 0 else f"Перезарядка: {100 - self.player.dodge_cooldown//1.8}%"
        dodge_color = GREEN if self.player.dodge_cooldown == 0 else YELLOW
        dodge_text = font_tiny.render(f"Уклонение: {dodge_status}", True, dodge_color)
        surface.blit(dodge_text, (WIDTH - 400, HEIGHT - 30))
        
        # Прогресс уровня по центру вверху
        progress_text = font_small.render(f"Прогресс: {self.level_progress}/{self.level_requirements[self.level]}", True, CYAN)
        surface.blit(progress_text, (WIDTH//2 - progress_text.get_width()//2, 30))
        
        # Управление внизу по центру
        controls_text = font_tiny.render("Управление: WASD/СТРЕЛКИ - движение, ПРОБЕЛ - огонь, Q - способность, E - уклонение, ESC - пауза", True, (180, 180, 180))
        surface.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 35))
        
        # Уведомления о достижениях
        for notification in self.achievement_notifications:
            notification.draw(surface)
        
        # Анимация появления босса
        if self.boss_intro:
            self.boss_intro.draw(surface)
            
        # Взрывы способностей
        for explosion in self.ability_explosions:
            pygame.draw.circle(surface, (255, 120, 120, 160), 
                             (int(explosion['x']), int(explosion['y'])), 
                             explosion['size'])
            pygame.draw.circle(surface, (255, 220, 60, 220), 
                             (int(explosion['x']), int(explosion['y'])), 
                             explosion['size'], 3)
    
    def draw_menu(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("ГАЛАКТИЧЕСКИЙ РЕЙДЕР", True, CYAN)
        title_shadow = font_large.render("ГАЛАКТИЧЕСКИЙ РЕЙДЕР", True, BLUE)
        
        for i in range(4):
            offset = i * 3
            surface.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + offset, 120 + offset))
        
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        subtitle = font_medium.render("Эпическое космическое приключение", True, YELLOW)
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 200))
        
        for button in self.buttons:
            button.draw(surface)
        
        # Улучшенное отображение статистики
        stats_y = HEIGHT - 220
        stats = [
            f"Текущий уровень: {self.level}",
            f"Лучший счет: {self.player.score}",
            f"Всего уничтожено: {self.player.kill_count}",
            f"Кредиты: {self.player.credits}"
        ]
        
        for stat in stats:
            text = font_small.render(stat, True, YELLOW)
            surface.blit(text, (WIDTH - text.get_width() - 35, stats_y))
            stats_y += 45
        
        # Время игры
        total_time = self.player.total_play_time + (time.time() - self.game_start_time)
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        time_text = font_small.render(f"Время игры: {hours}ч {minutes}м", True, CYAN)
        surface.blit(time_text, (35, HEIGHT - 120))
        
        copyright_text = font_tiny.render("© 2023 Галактический Рейдер. Все права защищены", True, (170, 170, 170))
        surface.blit(copyright_text, (WIDTH//2 - copyright_text.get_width()//2, HEIGHT - 50))
    
    def draw_instructions(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("ИНСТРУКЦИЯ И ПРАВИЛА", True, YELLOW)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        
        # Создаем поверхность для текста инструкции
        content_height = 2500
        content_surface = pygame.Surface((WIDTH - 100, content_height), pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 0))
        
        instructions = [
            "ЦЕЛЬ ИГРЫ:",
            "Пройти 100 уровней космических сражений, уничтожая вражеские корабли и побеждая боссов.",
            "Каждый 10-й уровень - босс (10, 20, 30, ..., 100), которого нужно уничтожить.",
            "",
            "=== УПРАВЛЕНИЕ ===",
            "W, A, S, D или СТРЕЛКИ - Движение корабля",
            "ПРОБЕЛ - Огонь из основного оружия",
            "Q - Активировать специальную способность",
            "E - Уклонение (кратковременная неуязвимость)",
            "ESC - Пауза/Продолжить игру",
            "F11 - Переключить полноэкранный режим",
            "",
            "=== СИСТЕМА УРОВНЕЙ ===",
            "- Игра состоит из 100 уровней сложности",
            "- На каждом уровне нужно уничтожить определенное количество врагов",
            "- Каждый 10-й уровень - босс, который требует особой тактики",
            "- После каждого уровня вы получаете кредиты для улучшений",
            "",
            "=== СПОСОБНОСТИ ===",
            "1. Усиление щита - временно усиливает щиты",
            "2. Замедление времени - замедляет врагов и их снаряды",
            "3. Усиление урона - увеличивает урон вашего оружия",
            "4. Ракетный залп - выпускает залп самонаводящихся ракет",
            "5. Энергетический взрыв - создает мощные взрывы вокруг корабля",
            "6. Вызов помощи - призывает два корабля поддержки на 10 секунд (стоит кредиты)",
            "",
            "=== КАСТОМИЗАЦИЯ ===",
            "- Меняйте внешний вид своего корабля",
            "- Разблокируйте новые модели и цвета",
            "- Каждая модель имеет уникальные визуальные эффекты",
            "",
            "=== СОВЕТЫ ===",
            "1. Собирайте бонусы для восстановления и усиления",
            "2. Используйте способности в критических ситуациях",
            "3. Уклоняйтесь от снарядов и врагов",
            "4. Улучшайте корабль между уровнями",
            "5. На босс-уровнях атакуйте слабые места противника",
            "6. Используйте 'Вызов помощи' в сложных моментах",
            "",
            "=== ТЕХНИКА ИГРЫ ===",
            "- Враги атакуют волнами: 20-25 секунд стрельбы, затем 10-15 секунд отдыха",
            "- Боссы атакуют постоянно, но с разной интенсивностью",
            "- Корабли поддержки стреляют непрерывно в течение 10 секунд",
            "- Используйте уклонение, чтобы избежать столкновений и снарядов",
            "",
            "=== ЭКОНОМИКА ===",
            "- За уничтожение врагов вы получаете кредиты",
            "- За прохождение уровня вы получаете бонусные кредиты",
            "- Кредиты можно тратить на улучшения корабля и способности",
            "- Способность 'Вызов помощи' стоит 150 кредитов за использование",
            "",
            "=== ДОСТИЖЕНИЯ ===",
            "- В игре 21 уникальное достижение",
            "- Открывайте достижения за выполнение различных задач",
            "- Новое достижение: 'Мастер помощи' за использование способности 'Вызов помощи'",
            "",
            "Удачи в галактических сражениях! Покажите, кто здесь главный!"
        ]
        
        y_pos = 20 - self.instructions_scroll_offset
        for line in instructions:
            text = font_small.render(line, True, WHITE)
            content_surface.blit(text, (50, y_pos))
            y_pos += 40
        
        # Отрисовка области контента
        content_rect = pygame.Rect(50, 150, WIDTH - 100, HEIGHT - 250)
        surface.blit(content_surface, (50, 150), (0, self.instructions_scroll_offset, WIDTH - 100, HEIGHT - 250))
        
        # Рамка области контента
        pygame.draw.rect(surface, (100, 100, 150), content_rect, 3, border_radius=10)
        
        # Скроллбар
        scrollbar_rect = pygame.Rect(WIDTH - 30, 150, 20, HEIGHT - 250)
        pygame.draw.rect(surface, (80, 80, 100), scrollbar_rect, border_radius=10)
        
        # Ползунок скроллбара
        max_scroll = content_height - (HEIGHT - 250)
        if max_scroll > 0:
            scroll_percentage = self.instructions_scroll_offset / max_scroll
            slider_height = max(50, (HEIGHT - 250) * (HEIGHT - 250) / content_height)
            slider_y = 150 + scroll_percentage * ((HEIGHT - 250) - slider_height)
            
            slider_rect = pygame.Rect(WIDTH - 28, slider_y, 16, slider_height)
            pygame.draw.rect(surface, (150, 150, 180), slider_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, slider_rect, 2, border_radius=8)
        
        back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
        back_btn.draw(surface)
    
    def draw_achievements(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("ДОСТИЖЕНИЯ", True, GOLD)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        
        achievements = [
            ("Первый выстрел", "Уничтожьте 1 врага", self.player.achievements.get("Первый выстрел", False)),
            ("10 убийств", "Уничтожьте 10 врагов", self.player.achievements.get("10 убийств", False)),
            ("50 убийств", "Уничтожьте 50 врагов", self.player.achievements.get("50 убийств", False)),
            ("100 убийств", "Уничтожьте 100 врагов", self.player.achievements.get("100 убийств", False)),
            ("500 убийств", "Уничтожьте 500 врагов", self.player.achievements.get("500 убийств", False)),
            ("1000 убийств", "Уничтожьте 1000 врагов", self.player.achievements.get("1000 убийств", False)),
            ("Боссобой", "Победите 1 босса", self.player.achievements.get("Боссобой", False)),
            ("Повелитель боссов", "Победите 10 боссов", self.player.achievements.get("Повелитель боссов", False)),
            ("Уровень 10", "Достигните 10 уровня", self.player.achievements.get("Уровень 10", False)),
            ("Уровень 50", "Достигните 50 уровня", self.player.achievements.get("Уровень 50", False)),
            ("Уровень 100", "Достигните 100 уровня", self.player.achievements.get("Уровень 100", False)),
            ("Мастер щита", "Улучшите щиты до 5 уровня", self.player.achievements.get("Мастер щита", False)),
            ("Мастер оружия", "Улучшите оружие до 10 уровня", self.player.achievements.get("Мастер оружия", False)),
            ("Богач", "Заработайте 1500 кредитов", self.player.achievements.get("Богач", False)),
            ("Миллионер", "Заработайте 1,000,000 кредитов", self.player.achievements.get("Миллионер", False)),
            ("Коллекционер", "Купите все скины корабля", self.player.achievements.get("Коллекционер", False)),
            ("Неуязвимый", "Выполните 100 уклонений", self.player.achievements.get("Неуязвимый", False)),
            ("Скоростной", "Улучшите двигатель до 10 уровня", self.player.achievements.get("Скоростной", False)),
            ("Экономист", "Заработайте 50,000 кредитов", self.player.achievements.get("Экономист", False)),
            ("Перфекционист", "Откройте все достижения", self.player.achievements.get("Перфекционист", False)),
            ("Мастер помощи", "Используйте способность 'Вызов помощи'", self.player.achievements.get("Мастер помощи", False))
        ]
        
        # Определяем высоту контента для скроллинга
        content_height = (len(achievements) + 1) // 2 * 100 + 100
        
        y_pos = 160 - self.achievements_scroll_offset
        x_offset = 120
        for i, (title, desc, unlocked) in enumerate(achievements):
            if i % 2 == 0:
                x = x_offset
            else:
                x = WIDTH // 2 + 60
                y_pos -= 90
                
            color = GOLD if unlocked else (110, 110, 130)
            pygame.draw.rect(surface, color, (x, y_pos, 550, 80), 3, border_radius=12)
            
            title_text = font_medium.render(title, True, color)
            surface.blit(title_text, (x + 85, y_pos + 15))
            
            desc_text = font_small.render(desc, True, WHITE if unlocked else (190, 190, 190))
            surface.blit(desc_text, (x + 85, y_pos + 50))
            
            if unlocked:
                pygame.draw.circle(surface, GOLD, (x + 45, y_pos + 40), 30)
                pygame.draw.polygon(surface, WHITE, [
                    (x + 30, y_pos + 40),
                    (x + 45, y_pos + 55),
                    (x + 60, y_pos + 30)
                ])
            else:
                pygame.draw.circle(surface, (90, 90, 90), (x + 45, y_pos + 40), 30)
                pygame.draw.circle(surface, (110, 110, 110), (x + 45, y_pos + 40), 30, 3)
                lock_rect = pygame.Rect(x + 35, y_pos + 25, 20, 25)
                pygame.draw.rect(surface, (110, 110, 110), lock_rect)
                pygame.draw.rect(surface, (110, 110, 110), (x + 30, y_pos + 35, 30, 20))
            
            if i % 2 == 1:
                y_pos += 100
            elif i % 2 == 0:
                y_pos += 90
        
        # Скроллбар
        scrollbar_rect = pygame.Rect(WIDTH - 30, 150, 20, HEIGHT - 250)
        pygame.draw.rect(surface, (80, 80, 100), scrollbar_rect, border_radius=10)
        
        # Ползунок скроллбара
        max_scroll = content_height - (HEIGHT - 250)
        if max_scroll > 0:
            scroll_percentage = self.achievements_scroll_offset / max_scroll
            slider_height = max(50, (HEIGHT - 250) * (HEIGHT - 250) / content_height)
            slider_y = 150 + scroll_percentage * ((HEIGHT - 250) - slider_height)
            
            slider_rect = pygame.Rect(WIDTH - 28, slider_y, 16, slider_height)
            pygame.draw.rect(surface, (150, 150, 180), slider_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, slider_rect, 2, border_radius=8)
        
        back_btn = Button(WIDTH//2 - 180, HEIGHT - 120, 360, 80, "Назад", BLUE, LIGHT_BLUE)
        back_btn.draw(surface)
    
    def draw_game_over(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("КОРАБЛЬ УНИЧТОЖЕН", True, RED)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        score_text = font_medium.render(f"Ваш счет: {self.player.score}", True, YELLOW)
        surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//4 + 120))
        
        level_text = font_medium.render(f"Достигнутый уровень: {self.level}", True, PURPLE)
        surface.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//4 + 190))
        
        kills_text = font_medium.render(f"Уничтожено врагов: {self.player.kill_count}", True, CYAN)
        surface.blit(kills_text, (WIDTH//2 - kills_text.get_width()//2, HEIGHT//4 + 260))
        
        credits_text = font_medium.render(f"Заработано кредитов: {self.player.credits}", True, GOLD)
        surface.blit(credits_text, (WIDTH//2 - credits_text.get_width()//2, HEIGHT//4 + 330))
        
        restart_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 220, 360, 80, "Новая игра", GREEN, (100, 255, 100))
        menu_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 320, 360, 80, "Главное меню", BLUE, LIGHT_BLUE)
        
        restart_btn.draw(surface)
        menu_btn.draw(surface)
    
    def draw_pause(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("ПАУЗА", True, YELLOW)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        stats = [
            f"Уровень: {self.level}",
            f"Очки: {self.player.score}",
            f"Убийств: {self.player.kill_count}",
            f"Здоровье: {int(self.player.health)}/{self.player.max_health}",
            f"Щит: {int(self.player.shield)}/{self.player.max_shield}",
            f"Оружие: {self.player.weapon_type} Ур. {self.player.weapon_level}",
            f"Кредиты: {self.player.credits}"
        ]
        
        y_pos = HEIGHT//3
        for stat in stats:
            text = font_medium.render(stat, True, CYAN)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 55
        
        resume_btn = Button(WIDTH//2 - 180, y_pos, 360, 80, "Продолжить", GREEN, (100, 255, 100))
        menu_btn = Button(WIDTH//2 - 180, y_pos + 110, 360, 80, "Главное меню", BLUE, LIGHT_BLUE)
        
        resume_btn.draw(surface)
        menu_btn.draw(surface)
    
    def draw_upgrade(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("УЛУЧШЕНИЕ КОРАБЛЯ", True, GREEN)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        subtitle = font_medium.render(f"У вас {self.player.credits} кредитов. Выберите улучшение:", True, YELLOW)
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 200))
        
        health_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 220, 300, 80, "Здоровье +25", RED, (255, 100, 100))
        shield_btn = Button(WIDTH//2 - 350, HEIGHT//2 - 110, 300, 80, "Щит +25", GREEN, (100, 255, 100))
        weapon_btn = Button(WIDTH//2 - 350, HEIGHT//2, 300, 80, "Оружие +1", PURPLE, (200, 100, 255))
        engine_btn = Button(WIDTH//2 - 350, HEIGHT//2 + 110, 300, 80, "Двигатель +1", ORANGE, (255, 180, 50))
        back_btn = Button(WIDTH//2 + 50, HEIGHT//2 + 110, 300, 80, "Продолжить", BLUE, LIGHT_BLUE)
        
        info_texts = [
            f"Цена: 150 кредитов",
            f"Цена: 150 кредитов",
            f"Цена: 200 кредитов",
            f"Цена: 200 кредитов"
        ]
        
        y_pos = HEIGHT//2 - 250
        for text in info_texts:
            info = font_small.render(text, True, WHITE)
            surface.blit(info, (WIDTH//2 - 350, y_pos))
            y_pos += 110
        
        health_btn.draw(surface)
        shield_btn.draw(surface)
        weapon_btn.draw(surface)
        engine_btn.draw(surface)
        back_btn.draw(surface)
    
    def draw_customization(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("КАСТОМИЗАЦИЯ КОРАБЛЯ", True, MAGENTA)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        credits_text = font_medium.render(f"Ваши кредиты: {self.player.credits}", True, YELLOW)
        surface.blit(credits_text, (WIDTH//2 - credits_text.get_width()//2, 200))
        
        for button in self.customization_buttons:
            button.draw(surface)
    
    def draw_victory(self, surface):
        self.draw_starfield(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))
        
        title = font_large.render("ПОБЕДА! ГАЛАКТИКА СПАСЕНА", True, GOLD)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        stats = [
            f"Всего очков: {self.player.score}",
            f"Уничтожено врагов: {self.player.kill_count}",
            f"Заработано кредитов: {self.player.credits}",
            f"Пройдено уровней: {self.max_level}",
            "",
            "Вы доказали, что достойны звания",
            "Величайшего Галактического Рейдера!"
        ]
        
        y_pos = HEIGHT//3 + 60
        for stat in stats:
            text = font_medium.render(stat, True, CYAN if stat == stats[-1] else WHITE)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += 55
        
        menu_btn = Button(WIDTH//2 - 180, HEIGHT - 180, 360, 80, "Главное меню", GREEN, (100, 255, 100))
        menu_btn.draw(surface)

    def draw(self, surface):
        surface.fill(BACKGROUND)
        self.draw_starfield(surface)
        
        for bonus in self.bonuses:
            bonus.draw(surface)
            
        for enemy in self.enemies:
            enemy.draw(surface)
            
        for projectile in self.projectiles:
            projectile.draw(surface)
            
        for explosion in self.explosions:
            explosion.draw(surface)
            
        # Отрисовка кораблей помощи
        for helper in self.player.helper_ships:
            helper.draw(surface)
            
        self.player.draw(surface)
        
        if self.game_state == "Игра":
            self.draw_ui(surface)
        
        if self.game_state == "Меню":
            self.draw_menu(surface)
        elif self.game_state == "Инструкции":
            self.draw_instructions(surface)
        elif self.game_state == "Достижения":
            self.draw_achievements(surface)
        elif self.game_state == "Конец игры":
            self.draw_game_over(surface)
        elif self.game_state == "Пауза":
            self.draw_pause(surface)
        elif self.game_state == "Улучшения":
            self.draw_upgrade(surface)
        elif self.game_state == "Кастомизация":
            self.draw_customization(surface)
        elif self.game_state == "Победа":
            self.draw_victory(surface)

# Основной цикл игры
def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        game.handle_events()
        
        if game.game_state == "Игра":
            game.update()
        
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
