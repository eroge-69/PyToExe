#!/usr/bin/env python3
import pygame
import random
import math
import json
import os

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - 1978 Style")

# Load sounds with error handling
def load_sound(filename):
    try:
        return pygame.mixer.Sound(filename)
    except pygame.error:
        # Create a silent sound if file doesn't exist
        sound = pygame.mixer.Sound(pygame.Surface((1, 1)))
        sound.set_volume(0)
        return sound

shoot_sound = load_sound('shoot.wav')
explosion_sound = load_sound('explosion.wav')

# Clock for controlling game speed
clock = pygame.time.Clock()
FPS = 60

# Authentic 80's Space Invaders color palette
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)           # Classic invader green
    RED = (255, 0, 0)             # UFO and explosions
    YELLOW = (255, 255, 0)        # Player laser
    CYAN = (0, 255, 255)          # UI elements
    ORANGE = (255, 165, 0)        # Explosions
    DARK_GREEN = (0, 128, 0)      # Darker green for variety
    PURPLE = (255, 0, 255)        # Special effects
    
    # Enemy colors by type (authentic arcade colors)
    INVADER_TOP = (255, 255, 255)    # Top row - white (highest points)
    INVADER_MID = (0, 255, 0)        # Middle rows - green  
    INVADER_BOTTOM = (0, 255, 255)   # Bottom rows - cyan
    
    # Level-based color schemes
    LEVEL_SCHEMES = {
        1: {'bg': BLACK, 'stars': WHITE, 'ui': WHITE, 'barriers': GREEN},
        2: {'bg': (5, 5, 20), 'stars': CYAN, 'ui': CYAN, 'barriers': CYAN},
        3: {'bg': (20, 5, 5), 'stars': YELLOW, 'ui': YELLOW, 'barriers': YELLOW},
        4: {'bg': (10, 0, 20), 'stars': PURPLE, 'ui': PURPLE, 'barriers': PURPLE},
        5: {'bg': (0, 20, 10), 'stars': GREEN, 'ui': GREEN, 'barriers': GREEN},
    }

# Game constants
PLAYER_SPEED = 5
BULLET_SPEED = 8
ENEMY_SPEED_BASE = 0.5
INVADER_ROWS = 5
INVADERS_PER_ROW = 11
INVADER_WIDTH = 32
INVADER_HEIGHT = 24
BARRIER_COUNT = 4

# Player movement boundaries
PLAYER_MIN_Y = 300  # Can't go higher than this
PLAYER_MAX_Y = SCREEN_HEIGHT - 30  # Bottom boundary

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.brightness = random.randint(50, 255)
        self.twinkle_speed = random.uniform(0.5, 2.0)
        self.twinkle_phase = random.uniform(0, math.pi * 2)
    
    def update(self):
        self.twinkle_phase += self.twinkle_speed * 0.05
        current_brightness = int(self.brightness + math.sin(self.twinkle_phase) * 50)
        current_brightness = max(50, min(255, current_brightness))
        return current_brightness
    
    def draw(self, surface):
        brightness = self.update()
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 1)

class Bullet:
    def __init__(self, x, y, direction=-1, speed=BULLET_SPEED):
        self.x = x
        self.y = y
        self.direction = direction  # -1 for up, 1 for down
        self.speed = speed
        self.active = True
        self.width = 2
        self.height = 8
    
    def update(self):
        self.y += self.speed * self.direction
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, surface):
        if self.active:
            if self.direction == -1:  # Player bullet
                color = Colors.YELLOW
            else:  # Enemy bullet
                color = Colors.WHITE
            
            pygame.draw.rect(surface, color, 
                           (self.x - self.width//2, self.y - self.height//2, 
                            self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.last_shot = 0
        self.shot_cooldown = 200  # milliseconds
        
        # Hit effect variables
        self.hit_timer = 0
        self.hit_duration = 1000  # 1 second of invincibility
        self.hit_flash_interval = 100  # Flash every 100ms
        self.is_hit = False
        self.visible = True
    
    def update(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.width//2, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(SCREEN_WIDTH - self.width//2, self.x + self.speed)
        
        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(PLAYER_MIN_Y, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(PLAYER_MAX_Y, self.y + self.speed)
    
    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot > self.shot_cooldown
    
    def shoot(self):
        if self.can_shoot():
            self.last_shot = pygame.time.get_ticks()
            shoot_sound.play()
            return Bullet(self.x, self.y - self.height//2, -1)
        return None
    
    def update_hit_effect(self):
        """Update hit effect timer and flashing"""
        if self.is_hit:
            current_time = pygame.time.get_ticks()
            time_since_hit = current_time - self.hit_timer
            
            if time_since_hit >= self.hit_duration:
                # End hit effect
                self.is_hit = False
                self.visible = True
            else:
                # Flash effect during invincibility
                flash_cycle = (time_since_hit // self.hit_flash_interval) % 2
                self.visible = flash_cycle == 0
    
    def take_hit(self):
        """Handle player getting hit"""
        if not self.is_hit:  # Only take damage if not already hit
            self.lives -= 1
            self.is_hit = True
            self.hit_timer = pygame.time.get_ticks()
            explosion_sound.play()
            return True
        return False
    
    def is_invincible(self):
        """Check if player is currently invincible"""
        return self.is_hit
    
    def draw(self, surface):
        # Only draw if visible (for flashing effect)
        if self.visible:
            # Choose color based on hit state
            color = Colors.RED if self.is_hit else Colors.GREEN
            
            # Draw authentic player ship (simplified tank-like design)
            # Base
            pygame.draw.rect(surface, color, 
                            (self.x - self.width//2, self.y - 5, self.width, 10))
            # Cannon
            pygame.draw.rect(surface, color, 
                            (self.x - 2, self.y - self.height//2, 4, self.height//2))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)

class Invader:
    SPRITES = {
        'squid': [  # Top row enemies (10 points)
            ['  ▄▄▄▄▄▄  ', '▄▄▄▄▄▄▄▄▄▄', '██▄██▄██▄', '▄▄▄▄▄▄▄▄▄▄', '  ▄    ▄  '],
            ['  ▄▄▄▄▄▄  ', '▄▄▄▄▄▄▄▄▄▄', '██▄██▄██▄', '▄▄▄▄▄▄▄▄▄▄', ' ▄ ▄  ▄ ▄ ']
        ],
        'crab': [   # Middle row enemies (20 points)
            [' ▄    ▄ ', '  ▄▄▄▄  ', ' ▄▄▄▄▄▄ ', '▄▄ ▄▄ ▄▄', '▄      ▄'],
            [' ▄    ▄ ', '▄ ▄▄▄▄ ▄', ' ▄▄▄▄▄▄ ', ' ▄ ▄▄ ▄ ', '  ▄  ▄  ']
        ],
        'octopus': [ # Bottom row enemies (30 points)
            ['   ▄▄   ', ' ▄▄▄▄▄▄ ', '▄▄▄▄▄▄▄▄', '▄ ▄▄▄▄ ▄', '  ▄  ▄  '],
            ['   ▄▄   ', ' ▄▄▄▄▄▄ ', '▄▄▄▄▄▄▄▄', ' ▄ ▄▄ ▄ ', ' ▄    ▄ ']
        ]
    }
    
    def __init__(self, x, y, invader_type, row):
        self.x = x
        self.y = y
        self.type = invader_type
        self.row = row
        self.width = INVADER_WIDTH
        self.height = INVADER_HEIGHT
        self.animation_frame = 0
        self.last_animation = 0
        self.animation_speed = 500  # milliseconds
        self.alive = True
        
        # Point values and colors based on type
        if invader_type == 'squid':
            self.points = 30
            self.color = Colors.INVADER_TOP
        elif invader_type == 'crab':
            self.points = 20
            self.color = Colors.INVADER_MID
        else:  # octopus
            self.points = 10
            self.color = Colors.INVADER_BOTTOM
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation > self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.last_animation = current_time
    
    def draw(self, surface):
        if self.alive:
            # Simple block-based sprite for authentic look
            sprite_size = 4
            sprite_data = self.SPRITES[self.type][self.animation_frame]
            
            for row, line in enumerate(sprite_data):
                for col, char in enumerate(line):
                    if char == '▄' or char == '█':
                        pygame.draw.rect(surface, self.color,
                                       (self.x - len(line) * sprite_size // 2 + col * sprite_size,
                                        self.y - len(sprite_data) * sprite_size // 2 + row * sprite_size,
                                        sprite_size, sprite_size))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)

class UFO:
    def __init__(self):
        self.x = -50
        self.y = 80
        self.width = 48
        self.height = 20
        self.speed = 2
        self.active = False
        self.alive = True
        self.points = random.choice([50, 100, 150, 300])  # Authentic UFO scoring
        self.last_appearance = 0
        self.appearance_interval = random.randint(15000, 30000)  # 15-30 seconds
    
    def should_appear(self):
        current_time = pygame.time.get_ticks()
        return (current_time - self.last_appearance > self.appearance_interval and 
                not self.active and random.randint(1, 100) == 1)
    
    def activate(self):
        self.active = True
        self.alive = True
        self.x = -50
        self.last_appearance = pygame.time.get_ticks()
    
    def update(self):
        if self.active and self.alive:
            self.x += self.speed
            if self.x > SCREEN_WIDTH + 50:
                self.active = False
                self.appearance_interval = random.randint(15000, 30000)
    
    def draw(self, surface):
        if self.active and self.alive:
            # Draw classic UFO shape
            pygame.draw.ellipse(surface, Colors.RED, 
                              (self.x - self.width//2, self.y - self.height//2 + 5, 
                               self.width, self.height//2))
            pygame.draw.ellipse(surface, Colors.YELLOW, 
                              (self.x - self.width//3, self.y - self.height//2, 
                               self.width//3*2, self.height//3))
    
    def get_rect(self):
        if self.active and self.alive:
            return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                              self.width, self.height)
        return pygame.Rect(0, 0, 0, 0)

class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 60
        self.pixels = self.create_barrier_pixels()
    
    def create_barrier_pixels(self):
        # Create classic barrier shape with pixel-perfect destruction
        pixels = []
        for row in range(self.height // 4):
            pixel_row = []
            for col in range(self.width // 4):
                # Create barrier shape
                center_x, center_y = self.width // 8, self.height // 8
                dist_from_center = math.sqrt((col - center_x)**2 + (row - center_y)**2)
                
                if (row < self.height // 8 and 
                    col > self.width // 16 and col < self.width // 8 - self.width // 16):
                    pixel_row.append(False)  # Hollow interior
                elif dist_from_center < self.height // 12:
                    pixel_row.append(True)   # Barrier pixel exists
                else:
                    pixel_row.append(False)  # Empty space
            pixels.append(pixel_row)
        return pixels
    
    def draw(self, surface, color=Colors.GREEN):
        pixel_size = 4
        for row in range(len(self.pixels)):
            for col in range(len(self.pixels[row])):
                if self.pixels[row][col]:
                    pygame.draw.rect(surface, color,
                                   (self.x + col * pixel_size, 
                                    self.y + row * pixel_size, 
                                    pixel_size, pixel_size))
    
    def hit(self, bullet_rect):
        # Check collision and destroy pixels
        pixel_size = 4
        destroyed = False
        
        for row in range(len(self.pixels)):
            for col in range(len(self.pixels[row])):
                if self.pixels[row][col]:
                    pixel_rect = pygame.Rect(self.x + col * pixel_size, 
                                           self.y + row * pixel_size, 
                                           pixel_size, pixel_size)
                    if bullet_rect.colliderect(pixel_rect):
                        # Destroy a small area around the hit
                        for dr in range(-1, 2):
                            for dc in range(-1, 2):
                                new_row, new_col = row + dr, col + dc
                                if (0 <= new_row < len(self.pixels) and 
                                    0 <= new_col < len(self.pixels[new_row])):
                                    self.pixels[new_row][new_col] = False
                        destroyed = True
                        return True
        return False

class Game:
    def __init__(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.player_bullets = []
        self.enemy_bullets = []
        self.invaders = []
        self.barriers = []
        self.ufo = UFO()
        self.stars = [Star() for _ in range(50)]
        
        self.score = 0
        self.high_score = self.load_high_score()
        self.wave = 1
        self.game_state = "playing"  # playing, game_over, paused
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.invader_direction = 1
        self.invader_drop_timer = 0
        self.invader_shoot_timer = 0
        self.invader_move_timer = 0
        self.invader_move_interval = 500  # milliseconds
        
        # Level-based visual effects
        self.level_transition_timer = 0
        self.level_transition_duration = 2000  # 2 seconds
        self.showing_level_transition = False
        
        # Screen effects
        self.screen_flash_timer = 0
        self.screen_flash_duration = 200  # Flash duration in ms
        self.screen_flash_active = False
        
        self.setup_wave()
    
    def load_high_score(self):
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    return json.load(f)['high_score']
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def setup_wave(self):
        self.invaders = []
        self.barriers = []
        
        # Create invader formation (5 rows x 11 columns)
        start_x = 100
        start_y = 150
        spacing_x = 50
        spacing_y = 40
        
        for row in range(INVADER_ROWS):
            for col in range(INVADERS_PER_ROW):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                
                # Assign invader types based on row
                if row == 0:
                    invader_type = 'squid'
                elif row <= 2:
                    invader_type = 'crab'
                else:
                    invader_type = 'octopus'
                
                self.invaders.append(Invader(x, y, invader_type, row))
        
        # Create barriers
        barrier_spacing = SCREEN_WIDTH // (BARRIER_COUNT + 1)
        for i in range(BARRIER_COUNT):
            x = barrier_spacing * (i + 1) - 40
            y = SCREEN_HEIGHT - 200
            self.barriers.append(Barrier(x, y))
        
        # Adjust difficulty based on wave
        self.invader_move_interval = max(200, 500 - (self.wave - 1) * 50)
        
        # Show level transition for waves > 1
        if self.wave > 1:
            self.showing_level_transition = True
            self.level_transition_timer = pygame.time.get_ticks()
    
    def update(self, keys):
        if self.game_state == "playing":
            # Update player
            self.player.update(keys)
            self.player.update_hit_effect()
            
            # Update screen flash effect
            if self.screen_flash_active:
                current_time = pygame.time.get_ticks()
                if current_time - self.screen_flash_timer > self.screen_flash_duration:
                    self.screen_flash_active = False
            
            # Handle shooting
            if keys[pygame.K_SPACE]:
                bullet = self.player.shoot()
                if bullet:
                    self.player_bullets.append(bullet)
            
            # Update bullets
            for bullet in self.player_bullets[:]:
                bullet.update()
                if not bullet.active:
                    self.player_bullets.remove(bullet)
            
            for bullet in self.enemy_bullets[:]:
                bullet.update()
                if not bullet.active:
                    self.enemy_bullets.remove(bullet)
            
            # Update invaders
            current_time = pygame.time.get_ticks()
            if current_time - self.invader_move_timer > self.invader_move_interval:
                self.move_invaders()
                self.invader_move_timer = current_time
            
            for invader in self.invaders:
                invader.update()
            
            # Check invader collisions with player
            for invader in self.invaders:
                if (invader.alive and not self.player.is_invincible() and 
                    invader.get_rect().colliderect(self.player.get_rect())):
                    if self.player.take_hit():
                        self.trigger_screen_flash()
                    # Reset invader position after collision
                    invader.x = random.randint(100, SCREEN_WIDTH - 100)
                    invader.y = random.randint(150, 300)
                    break
            
            # Update UFO
            if self.ufo.should_appear():
                self.ufo.activate()
            self.ufo.update()
            
            # Handle collisions
            self.handle_collisions()
            
            # Check win/lose conditions
            if not any(invader.alive for invader in self.invaders):
                self.wave += 1
                self.setup_wave()
            
            # Handle level transition
            if self.showing_level_transition:
                current_time = pygame.time.get_ticks()
                if current_time - self.level_transition_timer > self.level_transition_duration:
                    self.showing_level_transition = False
            
            if any(invader.alive and invader.y > SCREEN_HEIGHT - 100 for invader in self.invaders):
                self.game_state = "game_over"
            
            if self.player.lives <= 0:
                self.game_state = "game_over"
    
    def move_invaders(self):
        # Check if any invader hits the edge
        hit_edge = False
        alive_invaders = [inv for inv in self.invaders if inv.alive]
        
        if alive_invaders:
            leftmost = min(inv.x for inv in alive_invaders)
            rightmost = max(inv.x for inv in alive_invaders)
            
            if (leftmost <= 50 and self.invader_direction == -1) or \
               (rightmost >= SCREEN_WIDTH - 50 and self.invader_direction == 1):
                hit_edge = True
        
        # Move invaders
        for invader in self.invaders:
            if invader.alive:
                if hit_edge:
                    invader.y += 20
                else:
                    invader.x += 10 * self.invader_direction
        
        if hit_edge:
            self.invader_direction *= -1
        
        # Random invader shooting
        if random.randint(1, 100) == 1:
            alive_invaders = [inv for inv in self.invaders if inv.alive]
            if alive_invaders:
                shooter = random.choice(alive_invaders)
                self.enemy_bullets.append(Bullet(shooter.x, shooter.y + 20, 1, 4))
    
    def handle_collisions(self):
        # Player bullets vs invaders
        for bullet in self.player_bullets[:]:
            for invader in self.invaders:
                if invader.alive and bullet.get_rect().colliderect(invader.get_rect()):
                    explosion_sound.play()
                    invader.alive = False
                    bullet.active = False
                    self.score += invader.points
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                    break
        
        # Player bullets vs UFO
        for bullet in self.player_bullets[:]:
            if self.ufo.active and self.ufo.alive and bullet.get_rect().colliderect(self.ufo.get_rect()):
                explosion_sound.play()
                self.ufo.alive = False
                bullet.active = False
                self.score += self.ufo.points
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
        
        # Bullets vs barriers
        all_bullets = self.player_bullets + self.enemy_bullets
        for bullet in all_bullets[:]:
            for barrier in self.barriers:
                if barrier.hit(bullet.get_rect()):
                    bullet.active = False
                    break
        
        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if bullet.get_rect().colliderect(self.player.get_rect()):
                if self.player.take_hit():
                    self.trigger_screen_flash()
                bullet.active = False
                break
    
    def get_level_colors(self):
        """Get color scheme for current level"""
        level_index = ((self.wave - 1) % 5) + 1
        return Colors.LEVEL_SCHEMES.get(level_index, Colors.LEVEL_SCHEMES[1])
    
    def trigger_screen_flash(self):
        """Trigger screen flash effect when player gets hit"""
        self.screen_flash_active = True
        self.screen_flash_timer = pygame.time.get_ticks()
    
    def draw(self, surface):
        # Get level-specific colors
        level_colors = self.get_level_colors()
        
        # Clear screen with level-specific background
        surface.fill(level_colors['bg'])
        
        # Add screen flash effect if active
        if self.screen_flash_active:
            flash_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_overlay.set_alpha(100)
            flash_overlay.fill(Colors.RED)
            surface.blit(flash_overlay, (0, 0))
        
        # Draw starfield with level-specific star color
        for star in self.stars:
            brightness = star.update()
            star_color = tuple(int(c * brightness / 255) for c in level_colors['stars'])
            pygame.draw.circle(surface, star_color, (int(star.x), int(star.y)), 1)
        
        if self.game_state == "playing":
            # Draw game objects
            self.player.draw(surface)
            
            for bullet in self.player_bullets:
                bullet.draw(surface)
            
            for bullet in self.enemy_bullets:
                bullet.draw(surface)
            
            for invader in self.invaders:
                if invader.alive:
                    invader.draw(surface)
            
            for barrier in self.barriers:
                barrier.draw(surface, level_colors['barriers'])
            
            self.ufo.draw(surface)
            
            # Draw UI
            self.draw_ui(surface)
            
            # Draw level transition
            if self.showing_level_transition:
                self.draw_level_transition(surface)
        
        elif self.game_state == "game_over":
            self.draw_game_over(surface)
    
    def draw_ui(self, surface):
        level_colors = self.get_level_colors()
        ui_color = level_colors['ui']
        
        # Score
        score_text = self.font.render(f"SCORE: {self.score:06d}", True, ui_color)
        surface.blit(score_text, (20, 20))
        
        # High score
        high_score_text = self.font.render(f"HIGH: {self.high_score:06d}", True, ui_color)
        surface.blit(high_score_text, (SCREEN_WIDTH - 250, 20))
        
        # Lives with visual indicator
        lives_color = Colors.RED if self.player.lives <= 1 else ui_color
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, lives_color)
        surface.blit(lives_text, (20, 60))
        
        # Draw life indicators as small ships
        for i in range(self.player.lives):
            life_x = 20 + i * 25
            life_y = 90
            # Mini ship representation
            pygame.draw.rect(surface, ui_color, (life_x, life_y, 15, 4))
            pygame.draw.rect(surface, ui_color, (life_x + 6, life_y - 4, 3, 4))
        
        # Wave
        wave_text = self.font.render(f"WAVE: {self.wave}", True, ui_color)
        surface.blit(wave_text, (SCREEN_WIDTH - 150, 60))
        
        # Level indicator
        level_index = ((self.wave - 1) % 5) + 1
        level_text = self.small_font.render(f"LEVEL: {level_index}", True, ui_color)
        surface.blit(level_text, (SCREEN_WIDTH // 2 - 40, 20))
        
        # Movement hint for first wave
        if self.wave == 1:
            hint_text = self.small_font.render("WASD/Arrows to move, SPACE to shoot", True, ui_color)
            surface.blit(hint_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 30))
        
        # Show hit indicator when player is invincible
        if self.player.is_invincible():
            invincible_text = self.small_font.render("INVINCIBLE!", True, Colors.YELLOW)
            surface.blit(invincible_text, (self.player.x - 35, self.player.y - 40))
        
        # UFO score indicator
        if self.ufo.active and not self.ufo.alive:
            points_text = self.small_font.render(f"{self.ufo.points}", True, Colors.YELLOW)
            surface.blit(points_text, (self.ufo.x - 20, self.ufo.y - 30))
    
    def draw_level_transition(self, surface):
        """Draw level transition screen"""
        level_colors = self.get_level_colors()
        level_index = ((self.wave - 1) % 5) + 1
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK)
        surface.blit(overlay, (0, 0))
        
        # Level transition text
        level_text = self.font.render(f"LEVEL {level_index}", True, level_colors['ui'])
        wave_text = self.font.render(f"WAVE {self.wave}", True, level_colors['ui'])
        
        surface.blit(level_text, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 - 40))
        surface.blit(wave_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 10))
        
        # Color scheme name
        scheme_names = {
            1: "CLASSIC",
            2: "DEEP SPACE", 
            3: "MARS INVASION",
            4: "NEBULA STORM",
            5: "ALIEN WORLD"
        }
        scheme_text = self.small_font.render(scheme_names.get(level_index, "UNKNOWN"), True, level_colors['ui'])
        surface.blit(scheme_text, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2 + 50))
    
    def draw_game_over(self, surface):
        level_colors = self.get_level_colors()
        
        game_over_text = self.font.render("GAME OVER", True, Colors.RED)
        surface.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
        
        final_score_text = self.font.render(f"FINAL SCORE: {self.score:06d}", True, level_colors['ui'])
        surface.blit(final_score_text, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2))
        
        restart_text = self.small_font.render("Press R to restart or Q to quit", True, level_colors['ui'])
        surface.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 50))
    
    def restart(self):
        self.__init__()

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r and game.game_state == "game_over":
                    game.restart()
                elif event.key == pygame.K_p and game.game_state == "playing":
                    game.game_state = "paused"
                elif event.key == pygame.K_p and game.game_state == "paused":
                    game.game_state = "playing"
        
        # Get pressed keys for continuous input
        keys = pygame.key.get_pressed()
        
        # Update game
        if game.game_state != "paused":
            game.update(keys)
        
        # Draw everything
        game.draw(screen)
        
        # Show pause message
        if game.game_state == "paused":
            pause_text = game.font.render("PAUSED - Press P to continue", True, Colors.YELLOW)
            screen.blit(pause_text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()