import ctypes
import pygame
import random
import math
import sys
from enum import Enum
from typing import List, Tuple


_SCORE = ctypes.c_int(0)

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
GAME_TITLE = "NEXUS CTF - Space Defender Challenge"


TARGET_SCORE = 1000000 
POINTS_PER_ENEMY = 100
POINTS_PER_COIN = 250
POINTS_PER_POWERUP = 500
BASE_ENEMY_SPEED = 2
BASE_SPAWN_RATE = 60


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    GREEN = (50, 255, 100)
    BLUE = (50, 150, 255)
    YELLOW = (255, 255, 50)
    ORANGE = (255, 165, 0)
    PURPLE = (200, 50, 255)
    CYAN = (0, 255, 255)
    DARK_BLUE = (10, 20, 40)
    DARK_PURPLE = (30, 10, 50)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    NEON_GREEN = (57, 255, 20)
    NEON_PINK = (255, 16, 240)
    DARK_RED = (139, 0, 0)

class EntityType(Enum):
    PLAYER = 1
    ENEMY_BASIC = 2
    ENEMY_FAST = 3
    ENEMY_TANK = 4
    COIN = 5
    POWERUP_SHIELD = 6
    POWERUP_MULTISHOT = 7
    BULLET_PLAYER = 8
    BULLET_ENEMY = 9
    EXPLOSION = 10
    PARTICLE = 11

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    FLAG_SCREEN = 5

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int,int,int],
                 velocity: Tuple[float,float], lifetime: int):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface):
        size = int(self.size * (self.lifetime / max(1, self.max_lifetime)))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Explosion:
    def __init__(self, x: float, y: float, size: str = 'medium'):
        self.x = x
        self.y = y
        self.particles: List[Particle] = []
        self.frame = 0
        self.max_frames = 30
        particle_counts = {'small': 15, 'medium': 30, 'large': 50}
        particle_count = particle_counts.get(size, 30)
        
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            colors = [Colors.ORANGE, Colors.RED, Colors.YELLOW, Colors.WHITE]
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color, (vx, vy), random.randint(20, 40)))

    def update(self) -> bool:
        self.frame += 1
        self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0 or self.frame < self.max_frames

    def draw(self, screen: pygame.Surface):
        for p in self.particles:
            p.draw(screen)

class Bullet:
    def __init__(self, x: float, y: float, velocity: Tuple[float,float],
                 damage: int, owner_type: EntityType, color: Tuple[int,int,int]):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.damage = damage
        self.owner_type = owner_type
        self.color = color
        self.width = 4
        self.height = 12
        self.active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if (self.y < -20 or self.y > WINDOW_HEIGHT + 20 or
            self.x < -20 or self.x > WINDOW_WIDTH + 20):
            self.active = False

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 8
        self.health = 100
        self.max_health = 100
        self.shield_active = False
        self.shield_time = 0
        self.multishot_active = False
        self.multishot_time = 0
        self.shoot_cooldown = 0
        self.max_shoot_cooldown = 10
        self.invulnerable = False
        self.invulnerable_time = 0
        self.trail_particles: List[Particle] = []

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.width // 2, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(WINDOW_WIDTH - self.width // 2, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(self.height // 2, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(WINDOW_HEIGHT - self.height // 2, self.y + self.speed)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False

        if self.multishot_active:
            self.multishot_time -= 1
            if self.multishot_time <= 0:
                self.multishot_active = False

        if self.invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False

        if random.random() < 0.3:
            particle = Particle(self.x, self.y + self.height // 2,
                                Colors.CYAN, (random.uniform(-1,1), random.uniform(2,4)), 20)
            self.trail_particles.append(particle)

        self.trail_particles = [p for p in self.trail_particles if p.update()]

    def shoot(self) -> List[Bullet]:
        if self.shoot_cooldown > 0:
            return []
        bullets = []
        self.shoot_cooldown = self.max_shoot_cooldown
        
        if self.multishot_active:
            for angle_offset in [-20, 0, 20]:
                angle_rad = math.radians(270 + angle_offset)
                vx = math.cos(angle_rad) * 10
                vy = math.sin(angle_rad) * 10
                bullets.append(Bullet(self.x, self.y - self.height // 2, (vx, vy), 
                                      20, EntityType.BULLET_PLAYER, Colors.CYAN))
        else:
            bullets.append(Bullet(self.x, self.y - self.height // 2, (0, -12), 
                                  20, EntityType.BULLET_PLAYER, Colors.CYAN))
        return bullets

    def take_damage(self, damage: int) -> bool:
        if self.invulnerable or self.shield_active:
            return True
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return False
        self.invulnerable = True
        self.invulnerable_time = 60
        return True

    def activate_shield(self):
        self.shield_active = True
        self.shield_time = 300

    def activate_multishot(self):
        self.multishot_active = True
        self.multishot_time = 300

    def draw(self, screen: pygame.Surface):
        for p in self.trail_particles:
            p.draw(screen)
            
        if self.shield_active:
            pygame.draw.circle(screen, Colors.CYAN, (int(self.x), int(self.y)), self.width, 2)
            
        if self.invulnerable and self.invulnerable_time % 10 < 5:
            return
            
        points = [
            (self.x, self.y - self.height // 2),
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height // 2)
        ]
        pygame.draw.polygon(screen, Colors.NEON_GREEN, points)
        pygame.draw.polygon(screen, Colors.WHITE, points, 2)
        pygame.draw.circle(screen, Colors.CYAN, (int(self.x), int(self.y)), 8)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                           self.width, self.height)

class Enemy:
    def __init__(self, x: float, y: float, enemy_type: EntityType):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.active = True
        self.shoot_cooldown = 0
        
        if enemy_type == EntityType.ENEMY_BASIC:
            self.width = 40
            self.height = 40
            self.speed = 2
            self.health = 50
            self.max_health = 50
            self.color = Colors.RED
            self.points = POINTS_PER_ENEMY
            self.shoot_rate = 120
        elif enemy_type == EntityType.ENEMY_FAST:
            self.width = 30
            self.height = 30
            self.speed = 4
            self.health = 30
            self.max_health = 30
            self.color = Colors.ORANGE
            self.points = int(POINTS_PER_ENEMY * 1.5)
            self.shoot_rate = 90
        else:
            self.width = 60
            self.height = 60
            self.speed = 1
            self.health = 150
            self.max_health = 150
            self.color = Colors.PURPLE
            self.points = POINTS_PER_ENEMY * 3
            self.shoot_rate = 60
            
        self.movement_pattern = random.choice(['straight', 'zigzag', 'sine'])
        self.movement_timer = 0

    def update(self) -> bool:
        self.movement_timer += 1
        
        if self.movement_pattern == 'straight':
            self.y += self.speed
        elif self.movement_pattern == 'zigzag':
            self.y += self.speed
            self.x += math.sin(self.movement_timer * 0.1) * 3
        else:
            self.y += self.speed
            self.x += math.sin(self.movement_timer * 0.05) * 5
            
        self.x = max(self.width // 2, min(WINDOW_WIDTH - self.width // 2, self.x))
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        return self.y < WINDOW_HEIGHT + 100

    def shoot(self, player_x: float, player_y: float) -> List[Bullet]:
        if self.shoot_cooldown > 0:
            return []
        bullets = []
        self.shoot_cooldown = self.shoot_rate
        
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            vx = (dx / distance) * 6
            vy = (dy / distance) * 6
            bullets.append(Bullet(self.x, self.y + self.height // 2, (vx, vy), 
                                  10, EntityType.BULLET_ENEMY, Colors.RED))
        return bullets

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        return self.health > 0

    def draw(self, screen: pygame.Surface):
        points = [
            (self.x, self.y + self.height // 2),
            (self.x - self.width // 2, self.y - self.height // 2),
            (self.x + self.width // 2, self.y - self.height // 2)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, Colors.WHITE, points, 2)
        
        bar_width = self.width
        bar_height = 5
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.height // 2 - 15
        pygame.draw.rect(screen, Colors.DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / max(1, self.max_health)))
        pygame.draw.rect(screen, Colors.GREEN, (bar_x, bar_y, health_width, bar_height))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                           self.width, self.height)

class Coin:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 3
        self.active = True
        self.rotation = 0
        self.pulse = 0

    def update(self) -> bool:
        self.y += self.speed
        self.rotation += 5
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        return self.y < WINDOW_HEIGHT + 50

    def draw(self, screen: pygame.Surface):
        pulse_size = self.size + int(math.sin(self.pulse) * 3)
        pygame.draw.circle(screen, Colors.YELLOW, (int(self.x), int(self.y)), pulse_size + 5)
        pygame.draw.circle(screen, Colors.GOLD, (int(self.x), int(self.y)), pulse_size)
        pygame.draw.circle(screen, Colors.ORANGE, (int(self.x), int(self.y)), max(1, pulse_size - 5))
        
        font = pygame.font.Font(None, 24)
        text = font.render("$", True, Colors.ORANGE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class PowerUp:
    def __init__(self, x: float, y: float, powerup_type: EntityType):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.size = 25
        self.speed = 2
        self.active = True
        self.rotation = 0

    def update(self) -> bool:
        self.y += self.speed
        self.rotation += 3
        return self.y < WINDOW_HEIGHT + 50

    def draw(self, screen: pygame.Surface):
        color = Colors.CYAN if self.type == EntityType.POWERUP_SHIELD else Colors.NEON_PINK
        symbol = "S" if self.type == EntityType.POWERUP_SHIELD else "M"
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size + 8)
        pygame.draw.circle(screen, Colors.WHITE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), max(1, self.size - 3))
        
        font = pygame.font.Font(None, 32)
        text = font.render(symbol, True, Colors.WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class StarField:
    def __init__(self, star_count: int = 150):
        self.stars = []
        for _ in range(star_count):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            speed = random.uniform(0.5, 3)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            self.stars.append({'x': x, 'y': y, 'speed': speed, 'size': size, 'brightness': brightness})

    def update(self):
        for s in self.stars:
            s['y'] += s['speed']
            if s['y'] > WINDOW_HEIGHT:
                s['y'] = 0
                s['x'] = random.randint(0, WINDOW_WIDTH)

    def draw(self, screen: pygame.Surface):
        for s in self.stars:
            color = (s['brightness'], s['brightness'], s['brightness'])
            pygame.draw.circle(screen, color, (int(s['x']), int(s['y'])), s['size'])

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.state = GameState.PLAYING
        
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.coins: List[Coin] = []
        self.powerups: List[PowerUp] = []
        self.explosions: List[Explosion] = []
        self.starfield = StarField(200)

        self.score = _SCORE
        self.high_score = 0
        self.combo = 0
        self.combo_timer = 0
        
        self.enemy_spawn_timer = 0
        self.enemy_spawn_rate = BASE_SPAWN_RATE
        self.coin_spawn_timer = 0
        self.coin_spawn_rate = 180
        self.powerup_spawn_timer = 0
        self.powerup_spawn_rate = 600
        
        self.enemies_killed = 0
        self.total_shots_fired = 0
        self.play_time = 0
        
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.flag_revealed = False

        self.flag = "NEXUS{ch4ng3_th3_rul35_br34k_th3_g4m3}"
        
        print("="*60)
        print("NEXUS CTF - Game Hacking Challenge")
        print("="*60)
        print(f"Target Score: {TARGET_SCORE:,}")
        print("Hint: Your score is stored in memory as a 4-byte integer")
        print("Use Cheat Engine to find and modify it!")
        print("="*60)

        try:
            addr = ctypes.addressof(_SCORE)
            print(f"Cheat Engine friendly address (4-byte int): 0x{addr:x}")
        except Exception:
            pass
        print(f"Process PID: {os.getpid() if 'os' in globals() else 'unknown'}")

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.FLAG_SCREEN:
                        return False
                    elif self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.PLAYING:
                        bullets = self.player.shoot()
                        self.bullets.extend(bullets)
                        self.total_shots_fired += len(bullets)
                    elif self.state == GameState.GAME_OVER:
                        self.reset_game()
                        
                if event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self.reset_game()
        return True

    def reset_game(self):
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.enemies.clear()
        self.bullets.clear()
        self.coins.clear()
        self.powerups.clear()
        self.explosions.clear()
        self.score.value = 0
        self.combo = 0
        self.combo_timer = 0
        self.enemies_killed = 0
        self.total_shots_fired = 0
        self.play_time = 0
        self.state = GameState.PLAYING
        self.flag_revealed = False

    def spawn_enemy(self):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = -50
        r = random.random()
        if r < 0.6:
            t = EntityType.ENEMY_BASIC
        elif r < 0.9:
            t = EntityType.ENEMY_FAST
        else:
            t = EntityType.ENEMY_TANK
        self.enemies.append(Enemy(x, y, t))

    def spawn_coin(self):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = -30
        self.coins.append(Coin(x, y))

    def spawn_powerup(self):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = -30
        t = random.choice([EntityType.POWERUP_SHIELD, EntityType.POWERUP_MULTISHOT])
        self.powerups.append(PowerUp(x, y, t))

    def add_score(self, amount: int):
        self.score.value += amount
        if self.score.value > self.high_score:
            self.high_score = self.score.value
            
        if self.score.value >= TARGET_SCORE and not self.flag_revealed:
            self.flag_revealed = True
            self.state = GameState.FLAG_SCREEN
            print("\n" + "="*60)
            print("🚩 FLAG CAPTURED! 🚩")
            print("="*60)
            print(f"Flag: {self.flag}")
            print("Congratulations! You've mastered memory manipulation!")
            print("="*60 + "\n")

    def check_collisions(self):
        for bullet in self.bullets[:]:
            if bullet.owner_type != EntityType.BULLET_PLAYER:
                continue
            for enemy in self.enemies[:]:
                if bullet.active and enemy.active and bullet.get_rect().colliderect(enemy.get_rect()):
                    bullet.active = False
                    if not enemy.take_damage(bullet.damage):
                        try:
                            self.enemies.remove(enemy)
                        except ValueError:
                            pass
                        self.explosions.append(Explosion(enemy.x, enemy.y, 'medium'))
                        self.add_score(enemy.points)
                        self.enemies_killed += 1
                        self.combo += 1
                        self.combo_timer = 120
                        if random.random() < 0.3:
                            self.coins.append(Coin(enemy.x, enemy.y))

        # Enemy bullets vs player
        for bullet in self.bullets[:]:
            if bullet.owner_type != EntityType.BULLET_ENEMY:
                continue
            if bullet.active and bullet.get_rect().colliderect(self.player.get_rect()):
                bullet.active = False
                if not self.player.take_damage(bullet.damage):
                    self.explosions.append(Explosion(self.player.x, self.player.y, 'large'))
                    self.state = GameState.GAME_OVER

        for coin in self.coins[:]:
            if coin.get_rect().colliderect(self.player.get_rect()):
                try:
                    self.coins.remove(coin)
                except ValueError:
                    pass
                self.add_score(POINTS_PER_COIN)


        for pu in self.powerups[:]:
            if pu.get_rect().colliderect(self.player.get_rect()):
                try:
                    self.powerups.remove(pu)
                except ValueError:
                    pass
                if pu.type == EntityType.POWERUP_SHIELD:
                    self.player.activate_shield()
                else:
                    self.player.activate_multishot()

    def update(self, dt):
        if self.state != GameState.PLAYING:
            return
            
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Spawn handling
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_rate:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()

        self.coin_spawn_timer += 1
        if self.coin_spawn_timer >= self.coin_spawn_rate:
            self.coin_spawn_timer = 0
            self.spawn_coin()

        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_rate:
            self.powerup_spawn_timer = 0
            self.spawn_powerup()

        for e in self.enemies[:]:
            alive = e.update()
            if not alive:
                try:
                    self.enemies.remove(e)
                except ValueError:
                    pass

            new_bullets = e.shoot(self.player.x, self.player.y)
            self.bullets.extend(new_bullets)

        for b in self.bullets[:]:
            b.update()
            if not b.active:
                try:
                    self.bullets.remove(b)
                except ValueError:
                    pass

        for c in self.coins[:]:
            if not c.update():
                try:
                    self.coins.remove(c)
                except ValueError:
                    pass

        for p in self.powerups[:]:
            if not p.update():
                try:
                    self.powerups.remove(p)
                except ValueError:
                    pass

        for ex in self.explosions[:]:
            if not ex.update():
                try:
                    self.explosions.remove(ex)
                except ValueError:
                    pass

        self.starfield.update()
        self.check_collisions()

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        self.play_time += dt

    def draw(self):
        self.screen.fill(Colors.DARK_BLUE)
        self.starfield.draw(self.screen)

        for coin in self.coins:
            coin.draw(self.screen)
        for pu in self.powerups:
            pu.draw(self.screen)
        for e in self.enemies:
            e.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        for ex in self.explosions:
            ex.draw(self.screen)

        self.player.draw(self.screen)

        score_text = self.font_small.render(f"Score: {self.score.value:,}", True, Colors.WHITE)
        target_text = self.font_tiny.render(f"Target: {TARGET_SCORE:,}", True, Colors.GOLD)
        hs_text = self.font_tiny.render(f"High: {self.high_score:,}", True, Colors.SILVER)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(target_text, (10, 45))
        self.screen.blit(hs_text, (10, 70))
        
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = WINDOW_WIDTH - health_bar_width - 10
        health_bar_y = 10
        
        pygame.draw.rect(self.screen, Colors.DARK_RED, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = int(health_bar_width * (self.player.health / self.player.max_health))
        pygame.draw.rect(self.screen, Colors.GREEN, 
                        (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        pygame.draw.rect(self.screen, Colors.WHITE, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        
        health_text = self.font_tiny.render(f"HP: {self.player.health}/{self.player.max_health}", 
                                           True, Colors.WHITE)
        self.screen.blit(health_text, (health_bar_x + 5, health_bar_y + 2))
        
        powerup_y = 40
        if self.player.shield_active:
            shield_text = self.font_tiny.render(f"Shield: {self.player.shield_time // 60}s", 
                                               True, Colors.CYAN)
            self.screen.blit(shield_text, (WINDOW_WIDTH - 200, powerup_y))
            powerup_y += 25
            
        if self.player.multishot_active:
            multi_text = self.font_tiny.render(f"Multishot: {self.player.multishot_time // 60}s", 
                                              True, Colors.NEON_PINK)
            self.screen.blit(multi_text, (WINDOW_WIDTH - 200, powerup_y))


        if self.combo > 1:
            combo_text = self.font_medium.render(f"COMBO x{self.combo}!", True, Colors.GOLD)
            combo_rect = combo_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.blit(combo_text, combo_rect)



        # Game state overlays
        if self.state == GameState.PAUSED:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(Colors.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font_large.render("PAUSED", True, Colors.WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
            
            resume_text = self.font_small.render("Press ESC to resume", True, Colors.WHITE)
            resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(resume_text, resume_rect)

        if self.state == GameState.GAME_OVER:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(Colors.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font_large.render("GAME OVER", True, Colors.RED)
            go_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
            self.screen.blit(game_over_text, go_rect)
            
            final_score_text = self.font_medium.render(f"Final Score: {self.score.value:,}", True, Colors.WHITE)
            fs_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(final_score_text, fs_rect)
            
            restart_text = self.font_small.render("Press R to restart", True, Colors.WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(restart_text, restart_rect)

        if self.state == GameState.FLAG_SCREEN or self.flag_revealed:

            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            border_color = Colors.GOLD if (pygame.time.get_ticks() // 500) % 2 == 0 else Colors.NEON_PINK
            pygame.draw.rect(self.screen, border_color, 
                           (50, 150, WINDOW_WIDTH - 100, WINDOW_HEIGHT - 300), 5)
            
            congrats_text = self.font_large.render("FLAG CAPTURED", True, Colors.GOLD)
            congrats_rect = congrats_text.get_rect(center=(WINDOW_WIDTH // 2, 220))
            self.screen.blit(congrats_text, congrats_rect)
            
            flag_text = self.font_medium.render(self.flag, True, Colors.NEON_PINK)
            flag_rect = flag_text.get_rect(center=(WINDOW_WIDTH // 2, 320))
            
            flag_bg = pygame.Rect(flag_rect.x - 20, flag_rect.y - 10, 
                                 flag_rect.width + 40, flag_rect.height + 20)
            pygame.draw.rect(self.screen, Colors.DARK_PURPLE, flag_bg)
            pygame.draw.rect(self.screen, Colors.NEON_PINK, flag_bg, 3)
            self.screen.blit(flag_text, flag_rect)
            
            achievement_text = self.font_small.render("Achievement Unlocked:", True, Colors.WHITE)
            achievement_rect = achievement_text.get_rect(center=(WINDOW_WIDTH // 2, 420))
            self.screen.blit(achievement_text, achievement_rect)
            
            skill_text = self.font_small.render("Memory Manipulation Master", True, Colors.CYAN)
            skill_rect = skill_text.get_rect(center=(WINDOW_WIDTH // 2, 460))
            self.screen.blit(skill_text, skill_rect)
            
            stats_y = 520
            stats = [
                f"Final Score: {self.score.value:,}",
                f"Enemies Killed: {self.enemies_killed}",
                f"Shots Fired: {self.total_shots_fired}",
            ]
            
            for stat in stats:
                stat_text = self.font_tiny.render(stat, True, Colors.SILVER)
                stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, stats_y))
                self.screen.blit(stat_text, stat_rect)
                stats_y += 30
            
            exit_text = self.font_small.render("Press ESC to exit", True, Colors.YELLOW)
            exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
            self.screen.blit(exit_text, exit_rect)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    import time, os
    time.sleep(3)
    game = Game()
    game.run()