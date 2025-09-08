import pygame
import random
import math
import sys
import os
from pygame import mixer

# Инициализация Pygame и микшера
pygame.init()
mixer.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STELLAR - Cosmic Survival")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
DARK_SPACE = (5, 5, 15)
PURPLE = (128, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Загрузка звуковых эффектов
def load_sounds():
    sounds = {}
    
    try:
        import numpy as np
        
        sample_rate = 44100
        
        # Выстрел
        t = np.linspace(0, 0.1, int(sample_rate * 0.1))
        shoot_wave = 0.5 * np.sin(2 * np.pi * 880 * t) * np.exp(-10 * t)
        shoot_wave = (shoot_wave * 32767).astype(np.int16)
        sounds['shoot'] = pygame.sndarray.make_sound(shoot_wave)
        
        # Взрыв
        t = np.linspace(0, 0.5, int(sample_rate * 0.5))
        explosion_wave = 0.7 * np.random.random(len(t)) * np.exp(-4 * t)
        explosion_wave = (explosion_wave * 32767).astype(np.int16)
        sounds['explosion'] = pygame.sndarray.make_sound(explosion_wave)
        
        # Получение урона
        t = np.linspace(0, 0.3, int(sample_rate * 0.3))
        hit_wave = 0.8 * np.sin(2 * np.pi * 330 * t) * np.exp(-8 * t)
        hit_wave = (hit_wave * 32767).astype(np.int16)
        sounds['hit'] = pygame.sndarray.make_sound(hit_wave)
        
        # Game over
        t = np.linspace(0, 1.0, int(sample_rate * 1.0))
        game_over_wave = 0.6 * np.sin(2 * np.pi * 220 * t) * np.exp(-2 * t)
        game_over_wave = (game_over_wave * 32767).astype(np.int16)
        sounds['game_over'] = pygame.sndarray.make_sound(game_over_wave)
        
        # Power-up
        t = np.linspace(0, 0.4, int(sample_rate * 0.4))
        powerup_wave = 0.6 * np.sin(2 * np.pi * 660 * t) * np.exp(-3 * t)
        powerup_wave = (powerup_wave * 32767).astype(np.int16)
        sounds['powerup'] = pygame.sndarray.make_sound(powerup_wave)
        
        # Быстрый выстрел
        t = np.linspace(0, 0.05, int(sample_rate * 0.05))
        rapid_wave = 0.4 * np.sin(2 * np.pi * 1200 * t) * np.exp(-15 * t)
        rapid_wave = (rapid_wave * 32767).astype(np.int16)
        sounds['rapid'] = pygame.sndarray.make_sound(rapid_wave)
        
    except ImportError:
        print("numpy не установлен. Звуки отключены.")
        return {}
    
    return sounds

# Загружаем звуки
sounds = load_sounds()

def play_sound(sound_name, volume=0.5):
    if sound_name in sounds:
        sounds[sound_name].set_volume(volume)
        sounds[sound_name].play()

# Игрок
class Player:
    def __init__(self):
        self.radius = 15
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.lives = 3
        self.invincible = 0
        self.color = GREEN
        self.gun_angle = 0
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.rapid_fire_cooldown = 0
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.radius:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.radius:
            self.y += self.speed
    
    def update_gun_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.gun_angle = math.atan2(dy, dx)
    
    def shoot(self):
        if self.rapid_fire:
            if self.rapid_fire_cooldown <= 0:
                self.rapid_fire_cooldown = 5
                return True
            return False
        else:
            return True
    
    def update(self):
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
        
        if self.rapid_fire_cooldown > 0:
            self.rapid_fire_cooldown -= 1
    
    def draw(self):
        if self.invincible > 0 and pygame.time.get_ticks() % 200 < 100:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Рисуем пушку с учетом угла
        gun_length = 25
        end_x = self.x + math.cos(self.gun_angle) * gun_length
        end_y = self.y + math.sin(self.gun_angle) * gun_length
        pygame.draw.line(screen, BLUE, (self.x, self.y), (end_x, end_y), 4)
        
        # Индикатор режима стрельбы
        if self.rapid_fire:
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 8, 2)

# Враги
class Enemy:
    def __init__(self, level):
        self.radius = random.randint(8, 18 + level // 2)  # Увеличил размер врагов
        self.level = level
        
        side = random.choice(['top', 'right', 'bottom', 'left'])
        
        if side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = -self.radius
        elif side == 'right':
            self.x = WIDTH + self.radius
            self.y = random.randint(0, HEIGHT)
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.radius
        else:
            self.x = -self.radius
            self.y = random.randint(0, HEIGHT)
        
        speed_base = 4 + level * 0.5  # Увеличил скорость
        self.speed_x = 0
        self.speed_y = 0
        
        # 90% врагов целятся в игрока
        if random.random() < 0.9:
            target_x, target_y = player.x, player.y
        else:
            target_x, target_y = WIDTH // 2, HEIGHT // 2
        
        angle = math.atan2(target_y - self.y, target_x - self.x)
        variation = random.uniform(-0.2, 0.2)  # Меньшая вариация для более точного прицеливания
        self.speed_x = math.cos(angle + variation) * speed_base
        self.speed_y = math.sin(angle + variation) * speed_base
        
        # Разные типы врагов
        if random.random() < 0.1 + level * 0.05:  # Шанс быстрого врага увеличивается с уровнем
            self.color = (255, 100, 100)  # Красный - быстрый
            self.speed_x *= 1.5
            self.speed_y *= 1.5
            self.points = 20
        elif random.random() < 0.08 + level * 0.03:  # Шанс танка увеличивается с уровнем
            self.color = (100, 100, 255)  # Синий - танк
            self.radius *= 1.5
            self.speed_x *= 0.7
            self.speed_y *= 0.7
            self.points = 30
        else:
            self.color = (random.randint(150, 255), random.randint(0, 100), random.randint(0, 100))
            self.points = max(15, 40 - self.radius)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        if (self.x < -100 or self.x > WIDTH + 100 or 
            self.y < -100 or self.y > HEIGHT + 100):
            return True
        return False
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Глаз врага для индикации направления
        eye_x = self.x + math.cos(math.atan2(self.speed_y, self.speed_x)) * (self.radius * 0.7)
        eye_y = self.y + math.sin(math.atan2(self.speed_y, self.speed_x)) * (self.radius * 0.7)
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), self.radius // 3)

# Пули
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 12  # Увеличил скорость пуль
        self.radius = 3
        self.angle = angle
        self.damage = 1
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        # Эффект следа от пули
        trail_x = self.x - math.cos(self.angle) * 5
        trail_y = self.y - math.sin(self.angle) * 5
        pygame.draw.circle(screen, ORANGE, (int(trail_x), int(trail_y)), 1)
    
    def is_off_screen(self):
        return (self.x < -10 or self.x > WIDTH + 10 or 
                self.y < -10 or self.y > HEIGHT + 10)

# Бонусы
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.type = random.choice(['rapid_fire', 'life', 'shield'])
        self.speed_y = 2
        self.color = ORANGE if self.type == 'rapid_fire' else GREEN if self.type == 'life' else BLUE
    
    def update(self):
        self.y += self.speed_y
        return self.y > HEIGHT + 20
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Вращение бонуса
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

# Инициализация игры
player = Player()
enemies = []
bullets = []
powerups = []
score = 0
level = 1
game_over = False
bullet_cooldown = 0
particles = []
last_spawn_time = 0
last_powerup_time = 0
spawn_interval = 1500  # Уменьшил интервал спавна
powerup_interval = 10000  # Бонусы каждые 10 секунд
game_over_played = False
sound_enabled = True
paused = False
combo = 0
last_kill_time = 0
combo_timer = 0

# Фон - звезды
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(100)]
small_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 1.5)) for _ in range(200)]

# Шрифты
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
title_font = pygame.font.Font(None, 48)

def restart_game():
    global player, enemies, bullets, powerups, score, level, game_over
    global last_spawn_time, game_over_played, combo, last_kill_time, combo_timer
    player = Player()
    enemies = []
    bullets = []
    powerups = []
    score = 0
    level = 1
    game_over = False
    last_spawn_time = pygame.time.get_ticks()
    game_over_played = False
    combo = 0
    last_kill_time = 0
    combo_timer = 0
    if sound_enabled:
        play_sound('powerup')

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    
    # Обновляем угол пушки по положению мыши
    player.update_gun_angle(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not paused:
                if player.shoot():
                    bullets.append(Bullet(player.x, player.y, player.gun_angle))
                    if sound_enabled:
                        play_sound('shoot')
            
            elif event.key == pygame.K_r and game_over:
                restart_game()
            
            elif event.key == pygame.K_p:
                paused = not paused
                if sound_enabled and paused:
                    play_sound('shoot', 0.3)
            
            elif event.key == pygame.K_m:
                sound_enabled = not sound_enabled
                if sound_enabled:
                    play_sound('powerup', 0.4)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not paused:
            if event.button == 1:  # Левая кнопка мыши
                if player.shoot():
                    bullets.append(Bullet(player.x, player.y, player.gun_angle))
                    if sound_enabled:
                        play_sound('shoot')
    
    if paused:
        screen.fill(DARK_SPACE)
        for x, y, size in small_stars:
            pygame.draw.circle(screen, (150, 150, 200), (int(x), int(y)), size)
        for x, y, size in stars:
            pygame.draw.circle(screen, WHITE, (x, y), size)
        
        pause_text = big_font.render("PAUSED", True, YELLOW)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        instruction_text = font.render("Press P to continue", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(60)
        continue
    
    if game_over:
        if not game_over_played and sound_enabled:
            play_sound('game_over')
            game_over_played = True
    
    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()
        
        if player.invincible > 0:
            player.invincible -= 1
        
        if bullet_cooldown > 0:
            bullet_cooldown -= 1
        
        # Спавн врагов
        if current_time - last_spawn_time > max(300, spawn_interval - level * 50):  # Ускоряется с уровнем
            last_spawn_time = current_time
            enemies_to_spawn = min(8, 2 + level // 1)  # Больше врагов
            for _ in range(enemies_to_spawn):
                enemies.append(Enemy(level))
        
        # Спавн бонусов
        if current_time - last_powerup_time > powerup_interval:
            last_powerup_time = current_time
            if random.random() < 0.7:  # 70% шанс появления бонуса
                powerups.append(PowerUp(random.randint(50, WIDTH-50), -20))
        
        # Обновление врагов
        for enemy in enemies[:]:
            if enemy.update():
                enemies.remove(enemy)
                continue
            
            if player.invincible <= 0:
                dist = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
                if dist < enemy.radius + player.radius:
                    player.lives -= 1
                    player.invincible = 120
                    enemies.remove(enemy)
                    
                    if sound_enabled:
                        play_sound('hit')
                    
                    for _ in range(20):
                        particles.append({
                            'x': player.x, 'y': player.y,
                            'speed_x': random.uniform(-6, 6),
                            'speed_y': random.uniform(-6, 6),
                            'life': 50, 'color': RED
                        })
                    
                    combo = 0
                    combo_timer = 0
                    
                    if player.lives <= 0:
                        game_over = True
        
        # Обновление пуль
        for bullet in bullets[:]:
            bullet.update()
            
            if bullet.is_off_screen():
                bullets.remove(bullet)
                continue
            
            for enemy in enemies[:]:
                dist = math.sqrt((enemy.x - bullet.x)**2 + (enemy.y - bullet.y)**2)
                if dist < enemy.radius + bullet.radius:
                    # Комбо система
                    current_time = pygame.time.get_ticks()
                    if current_time - last_kill_time < 2000:  # 2 секунды для комбо
                        combo += 1
                        combo_timer = 120  # 2 секунды таймера комбо
                    else:
                        combo = 1
                    
                    last_kill_time = current_time
                    
                    # Бонус за комбо
                    combo_bonus = combo * 5
                    score += enemy.points + combo_bonus
                    enemies.remove(enemy)
                    
                    if sound_enabled:
                        play_sound('explosion')
                    
                    if bullet in bullets:
                        bullets.remove(bullet)
                    
                    for _ in range(25):
                        particles.append({
                            'x': enemy.x, 'y': enemy.y,
                            'speed_x': random.uniform(-8, 8),
                            'speed_y': random.uniform(-8, 8),
                            'life': 40, 'color': enemy.color
                        })
                    break
        
        # Обновление бонусов
        for powerup in powerups[:]:
            if powerup.update():
                powerups.remove(powerup)
                continue
            
            dist = math.sqrt((powerup.x - player.x)**2 + (powerup.y - player.y)**2)
            if dist < powerup.radius + player.radius:
                if powerup.type == 'rapid_fire':
                    player.rapid_fire = True
                    player.rapid_fire_timer = 300  # 5 секунд быстрой стрельбы
                    if sound_enabled:
                        play_sound('rapid')
                elif powerup.type == 'life':
                    player.lives = min(5, player.lives + 1)  # Макс 5 жизней
                    if sound_enabled:
                        play_sound('powerup')
                elif powerup.type == 'shield':
                    player.invincible = 180  # 3 секунды неуязвимости
                    if sound_enabled:
                        play_sound('powerup')
                
                powerups.remove(powerup)
                
                for _ in range(15):
                    particles.append({
                        'x': powerup.x, 'y': powerup.y,
                        'speed_x': random.uniform(-4, 4),
                        'speed_y': random.uniform(-4, 4),
                        'life': 30, 'color': powerup.color
                    })
        
        # Обновление комбо таймера
        if combo_timer > 0:
            combo_timer -= 1
        else:
            combo = 0
        
        # Повышение уровня
        if score >= level * 750:  # Увеличил требование для уровня
            level += 1
            if sound_enabled:
                play_sound('powerup', 0.3)
    
    # Обновление частиц
    for particle in particles[:]:
        particle['x'] += particle['speed_x']
        particle['y'] += particle['speed_y']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particles.remove(particle)
    
    # Отрисовка
    screen.fill(DARK_SPACE)
    
    for x, y, size in small_stars:
        pygame.draw.circle(screen, (150, 150, 200), (int(x), int(y)), size)
    
    for x, y, size in stars:
        pygame.draw.circle(screen, WHITE, (x, y), size)
    
    for particle in particles:
        alpha = min(255, particle['life'] * 8)
        color = particle['color']
        size = 2 + particle['life'] // 8
        pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), size)
    
    for enemy in enemies:
        enemy.draw()
    
    for bullet in bullets:
        bullet.draw()
    
    for powerup in powerups:
        powerup.draw()
    
    player.draw()
    
    # Интерфейс
    score_text = font.render(f"SCORE: {score}", True, CYAN)
    lives_text = font.render(f"LIVES: {player.lives}", True, GREEN)
    level_text = font.render(f"LEVEL: {level}", True, YELLOW)
    sound_text = font.render(f"SOUND: {'ON' if sound_enabled else 'OFF'}", True, WHITE)
    
    title_text = title_font.render("STELLAR", True, PURPLE)
    title_shadow = title_font.render("STELLAR", True, BLUE)
    
    screen.blit(title_shadow, (12, 12))
    screen.blit(title_text, (10, 10))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 50))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 90))
    screen.blit(sound_text, (WIDTH - sound_text.get_width() - 10, 130))
    
    # Отображение комбо
    if combo > 1:
        combo_text = font.render(f"COMBO x{combo}!", True, ORANGE)
        screen.blit(combo_text, (WIDTH - combo_text.get_width() - 10, 170))
    
    # Управление
    if not game_over:
        controls_text = font.render("CONTROLS: ARROWS = MOVE, MOUSE = AIM, LMB/SPACE = SHOOT, P = PAUSE, M = MUTE", True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
    
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        game_over_text = big_font.render("GAME OVER", True, RED)
        final_score = font.render(f"FINAL SCORE: {score}", True, YELLOW)
        restart_text = font.render("PRESS R TO RESTART", True, GREEN)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
