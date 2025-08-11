"""
DeepSeek — порт "Побег от Бабушки" с HTML/JS на Pygame
Сохранённый файл: /mnt/data/deepseek_pygame.py
Запуск: установи pygame (pip install pygame) и выполни:
    python /mnt/data/deepseek_pygame.py
Автор: сгенерировано ChatGPT (перевод и адаптация игрового HTML/JS)
"""

import pygame

import numpy as np

pygame.mixer.init(frequency=44100, size=-16, channels=2)

def generate_waveform(freq=440.0, duration=1.0, volume=0.5, wave_type='sine', sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    if wave_type == 'sine':
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == 'saw':
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    elif wave_type == 'noise':
        wave = np.random.uniform(-1, 1, size=t.shape)
    wave = (wave * volume * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return stereo_wave

def generate_background_music():
    notes = [
        (440, 0.3, 'square'), (494, 0.3, 'square'), (523, 0.3, 'square'),
        (587, 0.3, 'square'), (659, 0.3, 'square'), (698, 0.3, 'square'), (784, 0.3, 'square')
    ]
    waves = [generate_waveform(freq=f, duration=d, volume=0.3, wave_type=w) for f, d, w in notes]
    return np.concatenate(waves)

def generate_weather_effect(effect_type):
    if effect_type == 'rain':
        return generate_waveform(wave_type='noise', duration=1.5, volume=0.2)
    elif effect_type == 'wind':
        return generate_waveform(wave_type='noise', duration=1.5, volume=0.15)
    elif effect_type == 'leaves':
        noise = generate_waveform(wave_type='noise', duration=1.5, volume=0.1)
        mod = np.linspace(0.5, 1.0, noise.shape[0])
        noise = (noise.T * mod).T.astype(np.int16)
        return noise
    elif effect_type == 'snow':
        return generate_waveform(wave_type='noise', duration=1.5, volume=0.1)
    else:
        return generate_waveform(wave_type='noise', duration=1.0, volume=0.1)

def generate_event_sound(event_type):
    if event_type == 'level_up':
        return np.concatenate([generate_waveform(freq=880, duration=0.2, volume=0.4),
                               generate_waveform(freq=988, duration=0.2, volume=0.4)])
    elif event_type == 'win':
        return np.concatenate([generate_waveform(freq=880, duration=0.3, volume=0.4),
                               generate_waveform(freq=988, duration=0.3, volume=0.4),
                               generate_waveform(freq=1046, duration=0.3, volume=0.4)])
    elif event_type == 'lose':
        return generate_waveform(freq=220, duration=0.5, volume=0.4, wave_type='square')
    else:
        return generate_waveform(freq=440, duration=0.2, volume=0.3)

import random
import math
import sys
from dataclasses import dataclass

# ---- Конфигурация ----
WINDOW_W = 900
WINDOW_H = 600
FPS = 60

SEASONS = ['Весна', 'Лето', 'Осень', 'Зима']
SEASON_DURATION_MS = 20000  # длительность сезона в мс
BASE_PLAYER_SPEED = 2.0
JUMP_FORCE = 14.0
GRAVITY = 0.5
BASE_GRANDMA_SPEED = BASE_PLAYER_SPEED * 0.9
LEVEL_COUNT = 10
BASE_LEVEL_LENGTH = 5000  # в "пикселях" прогресса

# Перевод логики перезарядки/таймеров (в кадрах)
# TIME FIX: секунды = 3600  # 60 секунд при 60fps
BARRIER_COOLDOWN_SECONDS
# TIME FIX: секунды = 180   # 3 секунды
BARRIER_LIFETIME_SECONDS

# ---- Утилиты ----
def clamp(v, a, b):
    return max(a, min(b, v))

# ---- Классы игровыe ----
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 60
        self.color = pygame.Color('#3498db')
        self.normal_height = 60
        self.crouch_height = 40
        self.is_frozen = False
        self.velocity_y = 0.0
        self.is_jumping = False
        self.slowness = False  # замедлен в луже
        self.freeze_timer = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, current_player_speed, obstacles, season_name, dt):
        # TIME FIX: factor убран, работаем напрямую в секундах
        # заморозка
        if self.is_frozen:
            # TIME FIX: таймер теперь в секундах  # TIME FIX: таймеры в кадрах -> уменьшаем на factor
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.is_frozen = False
            return False  # вернуть on_ground False

        # движение вправо автоматически
        speed = current_player_speed
        if self.slowness and season_name != 'Зима':
            # при замедлении ставим скорость бабушки (по аналогии с JS)
            speed = BASE_GRANDMA_SPEED
        # TIME FIX: движение в секундах  # TIME FIX: перемещение с учётом delta_time
        self.x += speed * dt

        # гравитация
        # TIME FIX: движение в секундах  # TIME FIX: гравитация с учётом delta_time
        self.velocity_y += GRAVITY * dt
        # TIME FIX: движение в секундах  # TIME FIX: вертикальное движение с учётом delta_time
        self.y += self.velocity_y * dt

        # проверка земли
        if self.y + self.height > WINDOW_H - 50:
            self.y = WINDOW_H - 50 - self.height
            self.velocity_y = 0
            self.is_jumping = False
            on_ground = True
        else:
            on_ground = False

        # столкновения с препятствиями
        self.slowness = False
        for ob in obstacles:
            ob_rect = pygame.Rect(int(ob.x), int(ob.y), ob.width, ob.height)
            if self.rect().colliderect(ob_rect):
                # если столкновение сверху (наступили на препятствие)
                if self.y + self.height > ob.y and self.y < ob.y and self.velocity_y > 0:
                    self.y = ob.y - self.height
                    self.velocity_y = 0
                    self.is_jumping = False
                    on_ground = True
                elif ob.type == 'puddle':
                    self.slowness = True
                    if season_name == 'Зима':
                        self.is_frozen = True
                        # TIME FIX: секунды  # 2 секунды
                        self.freeze_timer = 2.0
                else:
                    # для других препятствий останавливаем игрока перед ним
                    self.x = ob.x - self.width

        return on_ground

    def draw(self, surf, camera_x, season_name, game_time):
        # тело
        px = int(self.x - camera_x)
        py = int(self.y)
        # голова
        pygame.draw.circle(surf, (255, 209, 102), (px + self.width//2, py - 15), 12)
        # тело
        col = (160, 210, 235) if self.is_frozen else self.color
        pygame.draw.rect(surf, col, (px, py, self.width, self.height))
        # ноги (простая анимация)
        leg_offset = math.sin(game_time / 100) * 5
        pygame.draw.rect(surf, col, (px - 5, py + self.height, 10, 15 + leg_offset))
        pygame.draw.rect(surf, col, (px + self.width - 5, py + self.height, 10, 15 - leg_offset))
        # руки
        arm_offset = math.cos(game_time / 100) * 5
        pygame.draw.rect(surf, col, (px - 5, py + 15, 5, 25 + arm_offset))
        pygame.draw.rect(surf, col, (px + self.width, py + 15, 5, 25 - arm_offset))
        # сезонные аксессуары
        if season_name == 'Весна':
            pygame.draw.rect(surf, (46, 204, 113), (px + self.width//2 - 15, py + 5, 30, 5))
        elif season_name == 'Лето':
            pygame.draw.polygon(surf, (231,76,60), [(px + self.width//2 -20, py-15),
                                                   (px + self.width//2 +20, py-15),
                                                   (px + self.width//2 +15, py-35),
                                                   (px + self.width//2 -15, py-35)])
        elif season_name == 'Осень':
            pygame.draw.rect(surf, (230,126,34), (px + self.width//2 - 15, py + 10, 30, 5))
            pygame.draw.rect(surf, (230,126,34), (px + self.width//2 + 10, py + 10, 5, 20))
        elif season_name == 'Зима':
            pygame.draw.polygon(surf, (231,76,60), [(px + self.width//2 -15, py-15),
                                                   (px + self.width//2 +15, py-15),
                                                   (px + self.width//2 +10, py-30),
                                                   (px + self.width//2 -10, py-30)])

        # глаза и рот
        pygame.draw.circle(surf, (26,42,108), (px + self.width//2 - 4, py - 15), 2)
        pygame.draw.circle(surf, (26,42,108), (px + self.width//2 + 4, py - 15), 2)
        pygame.draw.arc(surf, (26,42,108), (px + self.width//2 - 6, py - 13, 12, 10), math.pi, 2*math.pi, 1)

class Grandma:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 70
        self.color = pygame.Color('#e74c3c')
        self.attack_timer = 0
        self.stunned = False
        self.stun_timer = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, player_x, player_y, current_grandma_speed, barriers, is_feeding_scene, dt):
        # TIME FIX: factor убран, работаем напрямую в секундах
        if self.stunned or is_feeding_scene:
            if self.stunned:
                # TIME FIX: таймер теперь в секундах  # TIME FIX: таймер оглушения уменьшаем на factor
                self.stun_timer -= dt
                if self.stun_timer <= 0:
                    self.stunned = False
            return

        # движение к игроку
        if self.x < player_x:
            # TIME FIX: движение в секундах  # TIME FIX: перемещение бабушки с учётом delta_time
            self.x += current_grandma_speed * dt
        else:
            # TIME FIX: движение в секундах  # TIME FIX: перемещение бабушки с учётом delta_time
            self.x -= current_grandma_speed * dt

        # столкновение с барьерами
        for b in barriers:
            b_rect = pygame.Rect(int(b.x), int(b.y), b.width, b.height)
            if self.rect().colliderect(b_rect):
                self.stunned = True
                # TIME FIX: секунды
                self.stun_timer = 1.5

        # атака игрока (кормление)
        if abs(self.x - player_x) < 80 and abs(self.y - player_y) < 100:
            # TIME FIX: таймер теперь в секундах  # TIME FIX: таймер атаки в кадрах -> добавляем factor
            self.attack_timer += dt
            if self.attack_timer > FPS:  # примерно 1 секунда до сцены кормления (в кадрах эквивалент)
                self.attack_timer = 0
                return True  # триггер сцены кормления
        else:
            self.attack_timer = 0
        return False

    def draw(self, surf, camera_x):
        px = int(self.x - camera_x)
        py = int(self.y)
        # голова
        pygame.draw.circle(surf, (255,209,102), (px + self.width//2, py - 15), 15)
        # тело
        pygame.draw.rect(surf, self.color, (px, py, self.width, self.height))
        # ноги и руки
        pygame.draw.rect(surf, self.color, (px -5, py + self.height, 10, 15))
        pygame.draw.rect(surf, self.color, (px + self.width -5, py + self.height, 10, 15))
        pygame.draw.rect(surf, self.color, (px -5, py + 15, 5, 35))
        pygame.draw.rect(surf, self.color, (px + self.width, py + 15, 5, 35))
        # волосы
        pygame.draw.arc(surf, (247,178,103), (px -5, py -30, self.width+10, 40), math.pi, 2*math.pi)
        # рот
        pygame.draw.arc(surf, (26,42,108), (px + self.width//2 -6, py -5, 12, 8), math.pi, 2*math.pi, 1)
        # ключка
        pygame.draw.line(surf, (93,64,55), (px + self.width//2, py + 30), (px + self.width//2 - 40, py + 60), 5)
        # эффект оглушения
        if self.stunned:
            pygame.draw.rect(surf, (255,255,255,120), (px -10, py -30, self.width + 20, 10))

class Obstacle:
    def __init__(self, x, y, width, height, otype):
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)
        self.type = otype
        if otype == 'rock':
            self.points = self.generate_rock_shape(self.width, self.height)

    def generate_rock_shape(self, width, height):
        points = []
        segments = 8 + random.randint(0,4)
        cx = width/2
        cy = height/2
        for i in range(segments):
            angle = (i / segments) * math.pi * 2
            radius = width/2 * (0.7 + random.random() * 0.3)
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        return points

    def draw(self, surf, camera_x, season_name):
        px = int(self.x - camera_x)
        py = int(self.y)
        if self.type == 'hole':
            pygame.draw.rect(surf, (51,51,51), (px, py, self.width, self.height))
            grass_col = (224,247,250) if season_name == 'Зима' else (56,142,60)
            pygame.draw.rect(surf, grass_col, (px -10, py -10, self.width + 20, 10))
        elif self.type == 'log':
            pygame.draw.rect(surf, (139,69,19), (px, py-20, self.width, 40))
            for i in range(0, self.width, 15):
                pygame.draw.circle(surf, (93,64,55), (px + i, py), 5)
        elif self.type == 'rock':
            pts = [(int(px + pxoff), int(py + pyoff)) for (pxoff, pyoff) in self.points]
            # смещаем точки относительно холста
            # поскольку generate_rock_shape дал точки в локальной системе, рисуем многоугольник
            poly = [(int(self.x - camera_x + p[0] - int(self.x - camera_x)), int(self.y + p[1] - int(self.y))) for p in self.points]
            # проще — рисуем кругы/прямоугольники приближенно
            pygame.draw.polygon(surf, (119,119,119), [(int(self.x - camera_x + p[0]), int(self.y + p[1])) for p in self.points])
            for i in range(3):
                pxp = int(self.x - camera_x + self.width * (0.2 + random.random() * 0.6))
                pyp = int(self.y + self.height * (0.2 + random.random() * 0.6))
                pygame.draw.circle(surf, (153,153,153), (pxp, pyp), 2 + random.randint(0,3))
        elif self.type == 'bush':
            bush_h = self.height
            bush_w = self.width
            pygame.draw.circle(surf, (46,125,50), (int(self.x - camera_x + bush_w/2), int(self.y - bush_h/2)), int(bush_w/2))
            pygame.draw.circle(surf, (46,125,50), (int(self.x - camera_x + bush_w/2), int(self.y - bush_h)), int(bush_w/2))
            pygame.draw.circle(surf, (56,142,60), (int(self.x - camera_x + bush_w/2), int(self.y - bush_h/1.2)), int(bush_w/3))
        elif self.type == 'puddle':
            if season_name == 'Зима':
                pygame.draw.rect(surf, (200,230,255,150), (px, py, self.width, self.height))
                # трещины
                pygame.draw.line(surf, (150,200,255), (px+10, py+10), (px + self.width - 10, py + self.height - 10), 1)
                pygame.draw.line(surf, (150,200,255), (px + self.width - 10, py+10), (px+10, py + self.height - 10), 1)
            else:
                pygame.draw.rect(surf, (64,164,223,120), (px, py, self.width, self.height))
                for i in range(3):
                    pygame.draw.circle(surf, (100,180,255), (px + self.width//2, py + self.height//2), int(self.width/4) + i*5, 1)

class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 80
        # TIME FIX: секунды
        self.lifetime = BARRIER_LIFETIME_SECONDS

    def draw(self, surf, camera_x):
        px = int(self.x - camera_x)
        py = int(self.y)
        pygame.draw.rect(surf, (214,34,70), (px, py, self.width, self.height))
        for i in range(5):
            pygame.draw.rect(surf, (255,209,102), (px + 5, py + 10 + i*15, 10, 8))

    def update(self):
        # TIME FIX: уменьшаем lifetime на factor (кадровой эквивалент)
        self.lifetime -= factor
        return self.lifetime > 0

class WeatherEffect:
    def __init__(self, etype, x, y):
        self.type = etype
        self.x = x
        self.y = y
        self.init_effect()

    def init_effect(self):
        if self.type == 'flower':
            self.vx = -1 - random.random()*2
            self.vy = 0.5 + random.random()
            self.size = 3 + random.random()*5
            self.life = int(200 + random.random()*100)
        elif self.type == 'rain':
            self.vx = -1 - random.random()*2
            self.vy = 5 + random.random()*5
            self.size = 2
            self.life = 100
        elif self.type == 'leaf':
            self.vx = -2 - random.random()*3
            self.vy = 1 + random.random()
            self.size = 10 + random.random()*10
            self.life = int(300 + random.random()*200)
        elif self.type == 'snow':
            self.vx = -0.5 - random.random()
            self.vy = 1 + random.random()*0.5
            self.size = 2 + random.random()*3
            self.life = 400

    def update(self):
        # TIME FIX: движение в секундах  # TIME FIX: движение погоды с учётом delta_time
        self.x += self.vx * dt
        # TIME FIX: движение в секундах  # TIME FIX: движение погоды с учётом delta_time
        self.y += self.vy * dt
        # TIME FIX: жизнь в секундах  # TIME FIX: уменьшаем life на factor
        self.life -= dt
        if self.y > WINDOW_H:
            self.y = -20
            self.x = random.random() * WINDOW_W
        if self.x < -20:
            self.x = WINDOW_W + 20
        return self.life > 0

    def draw(self, surf):
        if self.type == 'flower':
            col = pygame.Color(0)
            col.hsla = (random.random()*30 + 330, 70, 60, 100)
            pygame.draw.circle(surf, col, (int(self.x), int(self.y)), int(self.size))
        elif self.type == 'rain':
            pygame.draw.line(surf, (100,180,255), (int(self.x), int(self.y)), (int(self.x - self.vx*2), int(self.y - self.vy*2)))
        elif self.type == 'leaf':
            s = pygame.Surface((int(self.size), int(self.size/2)), pygame.SRCALPHA)
            col = pygame.Color(0)
            col.hsla = (random.random()*30 + 20, 70, 45, 100)
            s.fill((0,0,0,0))
            pygame.draw.rect(s, col, (0,0,int(self.size), int(self.size/3)))
            surf.blit(pygame.transform.rotate(s, random.random()*360), (int(self.x), int(self.y)))
        elif self.type == 'snow':
            pygame.draw.circle(surf, (255,255,255), (int(self.x), int(self.y)), int(self.size))

# ---- Игровая логика и состояния ----
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_running = False

        self.current_level = 1
        self.player = None
        self.grandma = None
        self.obstacles = []
        self.barriers = []
        self.weather = []
        self.season_index = 0
        self.season_timer = 0
        self.season_duration = SEASON_DURATION_MS
        self.game_time = 0
        self.player_health = 3
        self.level_length = BASE_LEVEL_LENGTH
        self.level_progress = 0.0
        self.camera_x = 0.0
        self.barrier_cd = 0
        self.is_feeding_scene = False
        self.level_transition = False
        self.countdown = 2
        self.countdown_timer = 0
        self.lightning_active = False
        self.lightning_alpha = 0.0

        # шрифты
        pygame.font.init()
        self.font_big = pygame.font.SysFont('Segoe UI', 48)
        self.font_med = pygame.font.SysFont('Segoe UI', 28)
        self.font_small = pygame.font.SysFont('Segoe UI', 20)

        # стартовая инициализация
        self.init_game()

    def get_speed_factor(self, level):
        if 2 <= level <= 3:
            return 0.7
        elif 4 <= level <= 5:
            return 0.55
        elif 6 <= level <= 7:
            return 0.4
        elif 8 <= level <= 9:
            return 0.25
        elif level == 10:
            return 0.1
        return 1.0

    def init_game(self):
        speed_factor = self.get_speed_factor(self.current_level)  # TIME FIX: вычисляем множитель скорости по уровню
        self.current_player_speed = BASE_PLAYER_SPEED * speed_factor
        self.current_grandma_speed = BASE_GRANDMA_SPEED * speed_factor

        self.player = Player(100, WINDOW_H - 50 - 60)
        grandma_x = self.player.x - 200
        if grandma_x < 0:
            grandma_x = 0
        self.grandma = Grandma(grandma_x, WINDOW_H - 50 - 70)

        self.obstacles = []
        self.barriers = []
        self.generate_level(self.current_level)

        self.season_duration = SEASON_DURATION_MS
        self.season_index = random.randint(0,3)
        self.season_timer = 0
        self.game_time = 0
        self.player_health = 3
        self.level_progress = 0
        self.camera_x = 0
        self.barrier_cd = 0
        self.is_feeding_scene = False
        self.level_transition = False
        self.countdown = 2
        self.countdown_timer = 0
        self.lightning_active = False
        self.lightning_alpha = 0.0

        self.init_weather()
        self.update_health_display()

    def init_weather(self):
        self.weather = []
        s = SEASONS[self.season_index]
        if s == 'Весна':
            for i in range(50):
                self.weather.append(WeatherEffect('flower', random.random()*WINDOW_W, random.random()*WINDOW_H))
            for i in range(150):
                self.weather.append(WeatherEffect('rain', random.random()*WINDOW_W, random.random()*WINDOW_H))
        elif s == 'Лето':
            for i in range(200):
                self.weather.append(WeatherEffect('rain', random.random()*WINDOW_W, random.random()*WINDOW_H))
        elif s == 'Осень':
            for i in range(100):
                self.weather.append(WeatherEffect('leaf', random.random()*WINDOW_W, random.random()*WINDOW_H))
        elif s == 'Зима':
            for i in range(150):
                self.weather.append(WeatherEffect('snow', random.random()*WINDOW_W, random.random()*WINDOW_H))

    def generate_level(self, level):
        self.obstacles = []
        self.level_length = BASE_LEVEL_LENGTH + (level - 1) * 2000
        count = 12 + level * 4
        for i in range(count):
            x = 500 + random.random() * (self.level_length - 1000)
            y = WINDOW_H - 50
            typ = random.randint(0,4)
            if typ == 0:
                ob = Obstacle(x, y, 80 + random.random()*100, 50, 'hole')
            elif typ == 1:
                ob = Obstacle(x, y - 20, 100 + random.random()*100, 40, 'log')
            elif typ == 2:
                size = 40 + random.random()*50
                ob = Obstacle(x, y - size/2, size, size, 'rock')
            elif typ == 3:
                bushSize = 50 + random.random()*50
                ob = Obstacle(x, y - 30, bushSize, 30, 'bush')
            else:
                ob = Obstacle(x, y, 60 + random.random()*80, 10, 'puddle')
            self.obstacles.append(ob)

    def update_health_display(self):
        # Для pygame просто состояние в self.player_health
        pass

    def lose_health(self):
        self.player_health -= 1
        if self.player_health <= 0:
            self.game_over(True)
        # иначе продолжить

    def use_barrier(self):
        if self.barrier_cd <= 0:
            self.barriers.append(Barrier(self.player.x - 50, WINDOW_H - 130))
            # TIME FIX: секунды
            self.barrier_cd = BARRIER_COOLDOWN_SECONDS

    def check_level_complete(self):
        if self.level_progress >= self.level_length:
            self.show_level_complete()

    def show_level_complete(self):
        self.level_transition = True
        self.countdown = 2
        self.countdown_timer = FPS  # 1 сек для визуала сначала
        # показываем экран — логика в draw()
        # через несколько секунд продвинем уровень
        pygame.time.set_timer(pygame.USEREVENT + 2, 1000)

    def proceed_to_next_level(self):
        if self.current_level < LEVEL_COUNT:
            self.current_level += 1
            self.init_game()
        else:
            # победа
            self.game_over(False, victory=True)

    def game_over(self, caught=False, victory=False):
        self.game_running = False
        self.level_transition = False
        self.is_feeding_scene = False
        self.end_caught = caught
        self.end_victory = victory

    def show_feeding_scene(self):
        self.is_feeding_scene = True
        # короткая пауза сцены
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # через 1000ms вернёмся

    def draw_background(self):
        s = SEASONS[self.season_index]
        # градиент — приближённо рисуем двумя прямоугольниками
        if s == 'Весна':
            top = (135,206,235)
            bottom = (224,247,250)
            if self.lightning_active:
                top = (80,120,155)
                bottom = (48,77,109)
        elif s == 'Лето':
            top = (100,181,246)
            bottom = (187,222,251)
        elif s == 'Осень':
            top = (255,183,77)
            bottom = (255,243,224)
        else:
            top = (144,164,174)
            bottom = (236,239,241)

        # заполняем вертикально
        self.screen.fill(top)
        pygame.draw.rect(self.screen, bottom, (0, WINDOW_H//2, WINDOW_W, WINDOW_H//2))

        # солнце/луна
        if not (self.lightning_active and s == 'Весна'):
            sun_col = (255,235,59) if s in ('Лето','Весна') else (224,224,224)
            pygame.draw.circle(self.screen, sun_col, (800, 80), 40)

        # земля
        if s == 'Зима':
            ground_col = (224,247,250)
        elif s == 'Осень':
            ground_col = (141,110,99)
        else:
            ground_col = (56,142,60)
        pygame.draw.rect(self.screen, ground_col, (0, WINDOW_H - 50, WINDOW_W, 50))
        # тёмная полоса земли
        stripe = (255,255,255) if s == 'Зима' else (56,142,60)
        pygame.draw.rect(self.screen, stripe, (0, WINDOW_H - 50, WINDOW_W, 10))

        # деревья
        for i in range(20):
            x = int((i * 200 + self.camera_x/2) % (self.level_length + 1000))
            if x > self.camera_x - 100 and x < self.camera_x + WINDOW_W + 100:
                self.draw_tree(x, WINDOW_H - 50)

    def draw_tree(self, x, y):
        px = int(x - self.camera_x)
        pygame.draw.rect(self.screen, (93,64,55), (px - 10, y - 50, 20, 50))
        # крона
        s = SEASONS[self.season_index]
        if s == 'Весна':
            col = (129,199,132)
        elif s == 'Лето':
            col = (76,175,80)
        elif s == 'Осень':
            col = (255,179,0)
        else:
            col = (187,222,251)
        pygame.draw.circle(self.screen, col, (px, y - 100), 50)

        if s == 'Весна':
            # плоды
            for i in range(8):
                angle = i * math.pi * 2 / 8
                fx = int(px + math.cos(angle) * 35)
                fy = int(y - 100 + math.sin(angle) * 35)
                pygame.draw.circle(self.screen, (192,57,43), (fx, fy), 6)
        elif s == 'Лето':
            for i in range(6):
                angle = i * math.pi * 2 / 6
                fx = int(px + math.cos(angle) * 40)
                fy = int(y - 100 + math.sin(angle) * 40)
                pygame.draw.circle(self.screen, (231,76,60), (fx, fy), 8)
                pygame.draw.circle(self.screen, (39,174,96), (fx+5, fy-8), 5)
        elif s == 'Осень':
            for i in range(7):
                angle = i * math.pi * 2 / 7
                fx = int(px + math.cos(angle) * 35)
                fy = int(y - 100 + math.sin(angle) * 35)
                pygame.draw.circle(self.screen, (243,156,18), (fx, fy), 7)
        else:
            # снег и птицы
            for i in range(10):
                sx = int(px - 50 + random.random()*100)
                sy = int(y - 150 + random.random()*60)
                pygame.draw.circle(self.screen, (255,255,255), (sx, sy), 2)
            # птицы
            self.draw_bird(px - 30, y - 150)
            self.draw_bird(px + 20, y - 130)
            self.draw_bird(px + 40, y - 160)

    def draw_bird(self, x, y):
        pygame.draw.circle(self.screen, (155,89,182), (x, y), 8)
        pygame.draw.circle(self.screen, (155,89,182), (x+8, y-5), 5)
        pygame.draw.circle(self.screen, (255,255,255), (x+10, y-5), 2)
        pygame.draw.circle(self.screen, (0,0,0), (x+10, y-5), 1)
        pygame.draw.polygon(self.screen, (230,126,34), [(x+12, y-5), (x+18, y-5), (x+14, y-2)])
        pygame.draw.ellipse(self.screen, (142,68,173), (x-2, y, 10, 6))

    def draw_ui(self):
        # жизни
        for i in range(3):
            col = (255,0,0) if i < self.player_health else (120,120,120)
            pygame.draw.circle(self.screen, col, (60 + i*30, 30), 12)

        # уровень и прогресс
        progress_pct = int(self.level_progress / max(1, self.level_length) * 100)
        txt = f"Уровень: {self.current_level} | Прогресс: {progress_pct}%"
        surf = self.font_small.render(txt, True, (255,255,255))
        self.screen.blit(surf, (WINDOW_W - 300, 10))

        # способность преграда (E)
        # способность преграда (E)
        cd_pct = 0 if self.barrier_cd <= 0 else (1 - self.barrier_cd / BARRIER_COOLDOWN_SECONDS)  # TIME FIX: cooldown в секундах
        pygame.draw.rect(self.screen, (0,0,0,150), (10, WINDOW_H - 60, 220, 40))
        key_surf = self.font_small.render("E — Преграда", True, (255,255,255))
        self.screen.blit(key_surf, (20, WINDOW_H - 56))
        pygame.draw.rect(self.screen, (51,51,51), (140, WINDOW_H - 50, 100, 10))
        pygame.draw.rect(self.screen, (78,205,196), (140, WINDOW_H - 50, int(100 * cd_pct), 10))

    def update(self, dt):
        if not self.game_running:
            return

        self.game_time += dt
        self.season_timer += dt
        if self.season_timer >= self.season_duration:
            self.season_index = (self.season_index + 1) % len(SEASONS)
            self.season_timer = 0
            self.init_weather()

        # барьер
        if self.barrier_cd > 0:
            # TIME FIX: cooldown в секундах  # TIME FIX: уменьшаем CD в кадровом эквиваленте на factor
            self.barrier_cd -= dt

        # обновление погодных эффектов
        self.weather = [w for w in self.weather if w.update()]

        # молния (случайно весной/лете)
        if SEASONS[self.season_index] == 'Весна' and not self.lightning_active and random.random() < 0.0005:
            self.lightning_active = True
            self.lightning_alpha = 0.7
        if self.lightning_active:
            self.lightning_alpha -= 0.05
            if self.lightning_alpha <= 0:
                self.lightning_active = False

        # обновление барьеров
        self.barriers = [b for b in self.barriers if b.update()]

        # обновление игрока
        # TIME FIX
        on_ground = self.player.update(self.current_player_speed, self.obstacles, SEASONS[self.season_index], dt)

        # обновление бабушки (возвращает True если нужно сцена кормления)
        # TIME FIX
        feed_trigger = self.grandma.update(self.player.x, self.player.y, self.current_grandma_speed, self.barriers, self.is_feeding_scene, dt)
        if feed_trigger:
            self.show_feeding_scene()

        # обновление прогресса/камера
        self.level_progress = max(self.level_progress, self.player.x)
        self.camera_x = max(0, self.player.x - 300)

        self.update_health_display()

        self.check_level_complete()

    def draw(self):
        # задний фон и декорации
        self.draw_background()

        # земля полосы и земля уже нарисованы
        # рисуем препятствия
        for ob in self.obstacles:
            ob.draw(self.screen, self.camera_x, SEASONS[self.season_index])

        # барьеры
        for b in self.barriers:
            b.draw(self.screen, self.camera_x)

        # игрок и бабушка
        self.player.draw(self.screen, self.camera_x, SEASONS[self.season_index], self.game_time)
        self.grandma.draw(self.screen, self.camera_x)

        # погодные эффекты
        for w in self.weather:
            w.draw(self.screen)

        # эффект молнии
        if self.lightning_active:
            s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            s.fill((255,255,200, int(self.lightning_alpha*255)))
            self.screen.blit(s, (0,0))

        # UI
        self.draw_ui()

        # сцена кормления
        if self.is_feeding_scene:
            s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            s.fill((10,25,41,220))
            self.screen.blit(s, (0,0))
            self.draw_center_text("Бабушка поймала!", "Антон получает пирожок и теряет одну жизнь!", emoji="🥟")

        # экран перехода уровня
        if self.level_transition:
            s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            s.fill((10,25,41,240))
            self.screen.blit(s, (0,0))
            self.draw_center_text(f"Уровень {self.current_level} пройден!", f"Следующий уровень: {self.current_level+1}", emoji="🎉")
            # также выводим обратный отсчёт
            cd_surf = self.font_med.render(f"Начало через: {self.countdown}", True, (255,255,255))
            self.screen.blit(cd_surf, (WINDOW_W//2 - cd_surf.get_width()//2, WINDOW_H//2 + 80))

        # экран конца игры
        if not self.game_running and (hasattr(self, 'end_victory') and (self.end_victory or self.end_caught)):
            s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            s.fill((10,25,41,240))
            self.screen.blit(s, (0,0))
            if self.end_victory:
                self.draw_center_text("Победа!", "Антон успешно прошёл все 10 уровней и сбежал от бабушки!")
            else:
                self.draw_center_text("Бабушка поймала!", f"Антон не смог убежать от бабушки на уровне {self.current_level}! Попробуй ещё раз!")

    def draw_center_text(self, title, subtitle, emoji=None):
        # большой заголовок
        title_s = self.font_big.render(title, True, (78,205,196))
        sub_s = self.font_med.render(subtitle, True, (255,107,107))
        self.screen.blit(title_s, (WINDOW_W//2 - title_s.get_width()//2, WINDOW_H//2 - 80))
        self.screen.blit(sub_s, (WINDOW_W//2 - sub_s.get_width()//2, WINDOW_H//2 - 20))
        if emoji:
            emoji_s = self.font_med.render(emoji, True, (255,255,255))
            self.screen.blit(emoji_s, (WINDOW_W//2 - emoji_s.get_width()//2, WINDOW_H//2 + 20))

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_w, pygame.K_SPACE, pygame.K_UP):
                self.player_jump()
            if e.key in (pygame.K_e, pygame.K_f):
                self.use_barrier()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if mx < WINDOW_W // 2:
                self.player_jump()
            else:
                self.use_barrier()
        elif e.type == pygame.USEREVENT + 1:
            # завершение сцены кормления
            self.is_feeding_scene = False
            self.lose_health()
            # отодвинуть бабушку назад
            self.grandma.x = self.player.x - 200
            if self.grandma.x < 0:
                self.grandma.x = 0
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        elif e.type == pygame.USEREVENT + 2:
            # таймер для перехода уровня
            self.countdown -= 1
            if self.countdown <= 0:
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                self.level_transition = False
                if self.current_level < LEVEL_COUNT:
                    self.current_level += 1
                    self.init_game()
                else:
                    self.game_over(False, victory=True)

    def player_jump(self):
        if not self.player.is_frozen and not self.is_feeding_scene:
            if not self.player.is_jumping:
                self.player.velocity_y = -JUMP_FORCE
                self.player.is_jumping = True

    def run(self):
        # начальный экран
        showing_start = True

        while self.running:
            dt = self.clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    # если в игре — выйдем в главное меню или выйдем полностью
                    if self.game_running:
                        self.game_running = False
                    else:
                        self.running = False
                else:
                    if self.game_running:
                        self.handle_event(e)
                    else:
                        # если не запущена игра, реагируем на клавиши в меню
                        if e.type == pygame.KEYDOWN:
                            if showing_start:
                                if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                                    showing_start = False
                                    self.game_running = True
                                    self.init_game()
                            else:
                                # если игра остановлена на экране конца
                                if (hasattr(self, 'end_victory') and (self.end_victory or self.end_caught)):
                                    if e.key == pygame.K_r:
                                        # рестарт
                                        self.current_level = 1
                                        self.game_running = True
                                        self.init_game()
                                        showing_start = False
                                else:
                                    # запуск
                                    if e.key == pygame.K_RETURN:
                                        showing_start = False
                                        self.game_running = True
                                        self.init_game()

                        if e.type == pygame.MOUSEBUTTONDOWN and showing_start:
                            showing_start = False
                            self.game_running = True
                            self.init_game()

            # апдейт игрового состояния
            if self.game_running:
                # TIME FIX: передаём dt в секундах
                self.update(dt)
            # отрисовка
            if self.running:
                if not self.game_running:
                    # показываем стартовый экран
                    self.screen.fill((10,25,41))
                    title = self.font_big.render("Побег от Бабушки", True, (78,205,196))
                    subtitle = self.font_med.render("Четыре Сезона", True, (255,107,107))
                    info = self.font_small.render("Прыжок: W / ↑ / ПРОБЕЛ   Преграда: E / F", True, (255,255,255))
                    desc = self.font_small.render("Антон автоматически бежит через волшебный лес! Управляй прыжками и ставь преграды.", True, (255,255,255))
                    self.screen.blit(title, (WINDOW_W//2 - title.get_width()//2, 80))
                    self.screen.blit(subtitle, (WINDOW_W//2 - subtitle.get_width()//2, 150))
                    self.screen.blit(info, (WINDOW_W//2 - info.get_width()//2, 220))
                    self.screen.blit(desc, (WINDOW_W//2 - desc.get_width()//2, 260))
                    start_hint = self.font_small.render("Нажми ПРОБЕЛ или КЛИК мышью чтобы начать", True, (255,255,255))
                    self.screen.blit(start_hint, (WINDOW_W//2 - start_hint.get_width()//2, WINDOW_H - 80))
                else:
                    # нормальная отрисовка игрового мира
                    self.draw()

                pygame.display.flip()

        pygame.quit()

# ---- Основной запуск ----
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Побег от Бабушки — Pygame версия")
    game = Game(screen)
    game.run()

if __name__ == '__main__':
    main()



# ==== Инициализация фоновой музыки и звуков ====
bg_music = pygame.sndarray.make_sound(generate_background_music())
bg_music.set_volume(0.5)
bg_music.play(-1)

# Пример погодного звука (заменить на актуальный при смене сезона в игре)
current_weather_sound = pygame.sndarray.make_sound(generate_weather_effect('rain'))
current_weather_sound.set_volume(0.3)
current_weather_sound.play(-1)

# Пример событийных звуков
level_up_sound = pygame.sndarray.make_sound(generate_event_sound('level_up'))
win_sound = pygame.sndarray.make_sound(generate_event_sound('win'))
lose_sound = pygame.sndarray.make_sound(generate_event_sound('lose'))

# Управление звуком
volume = 0.5
mute = False

running = True
while running:
    # TIME FIX: время кадра в секундах
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                mute = not mute
                pygame.mixer.music.set_volume(0 if mute else volume)
                bg_music.set_volume(0 if mute else volume)
                current_weather_sound.set_volume(0 if mute else 0.3)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                volume = min(1.0, volume + 0.1)
                bg_music.set_volume(volume)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                volume = max(0.0, volume - 0.1)
                bg_music.set_volume(volume)
            elif event.key == pygame.K_1:
                level_up_sound.play()
            elif event.key == pygame.K_2:
                win_sound.play()
            elif event.key == pygame.K_3:
                lose_sound.play()

pygame.quit()


# === SOUND: start background music ===
bg_music = pygame.sndarray.make_sound(generate_background_music())
bg_music.set_volume(0.5)
bg_music.play(-1)




# === SOUND: level up ===
level_up_sound = pygame.sndarray.make_sound(generate_event_sound('level_up'))
level_up_sound.play()


# === SOUND: win ===
win_sound = pygame.sndarray.make_sound(generate_event_sound('win'))
win_sound.play()


# === SOUND: lose ===
lose_sound = pygame.sndarray.make_sound(generate_event_sound('lose'))
lose_sound.play()


# === SOUND: feeding grandma ===
feed_sound = pygame.sndarray.make_sound(generate_waveform(freq=660, duration=0.15, volume=0.4))
feed_sound.play()