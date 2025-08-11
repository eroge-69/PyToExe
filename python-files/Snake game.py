import pygame
import random
import time
import sys
import json
import os
import math
import sys, os



# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

# Change working directory to script's directory for better portability
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load sound effects with error handling
sound_effects = {
    "simple_food": "simple food.wav",
    "bonus_food": "bonus food.wav",
    "click": "click.wav",
    "collision": "collision.wav",
    "game_over": "game over.wav",
    "snake_bite": "snake bite itself.wav",
    "bonus_timer": "2x bonus.wav",
    "exit_confirmation": "exit confirmation.wav",
    "yes": "yes.wav",
    "no": "no.wav",
    "go": "go.wav",
    "welcome": "welcome.wav",
    "magnet_effect": "magnet_effect.wav",
    "m_effect": "m_effect.wav",
    "s_effect": "s_effect.wav",
    "shield_broken": "shield_broken.wav",
    "poison_food": "poison_food.wav",
    "coin": "coin.wav"
}

sounds = {}
for name, file in sound_effects.items():
    try:
        sounds[name] = pygame.mixer.Sound(file)
    except Exception as e:
        print(f"Error loading sound {file}: {e}")
        # Create silent sound as fallback
        sounds[name] = pygame.mixer.Sound(buffer=bytearray(44))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_BLUE = (30, 42, 71)
BLUE = (0, 0, 255)
GREEN = (50, 205, 50)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
PINK = (255, 192, 203)

# Screen dimensions
SCREEN_WIDTH = 1260
SCREEN_HEIGHT = 786
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 60) // GRID_SIZE  # Space for score

# Game settings
FPS = 60
SPEED_EASY = 7
SPEED_MEDIUM = 10
SPEED_HARD = 13

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Fonts
try:
    font_small = pygame.font.SysFont('arial', 20)
    font_medium = pygame.font.SysFont('arial', 30)
    font_large = pygame.font.SysFont('arial', 50)
    font_countdown = pygame.font.SysFont('orbitron', 120)
    font_coin = pygame.font.SysFont('orbitron', 30)
except:
    # Fallback fonts if primary fonts aren't available
    font_small = pygame.font.Font(None, 20)
    font_medium = pygame.font.Font(None, 30)
    font_large = pygame.font.Font(None, 50)
    font_countdown = pygame.font.Font(None, 120)
    font_coin = pygame.font.Font(None, 30)

# Snake color options for skin system
SNAKE_COLORS = {
    "RED": (255, 0, 0),
    "GREEN": (50, 205, 50),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "CYAN": (0, 255, 255),
    "ORANGE": (255, 165, 0),
    "PINK": (255, 192, 203)
}

# Themes
THEMES = {
    "Classic": {
        "background": DARK_BLUE,
        "snake": GREEN,
        "snake_head": DARK_GREEN,
        "food": RED,
        "text": WHITE,
        "boundary": WHITE
    },
    "Dark": {
        "background": (10, 10, 30),
        "snake": (0, 200, 0),
        "snake_head": (0, 150, 0),
        "food": (255, 50, 50),
        "text": (200, 200, 200),
        "boundary": (100, 100, 100)
    },
    "Neon": {
        "background": (0, 0, 0),
        "snake": (0, 255, 0),
        "snake_head": (0, 200, 0),
        "food": (255, 0, 0),
        "text": (255, 255, 255),
        "boundary": (0, 255, 255)
    },
    "Nature": {
        "background": (34, 139, 34),
        "snake": (139, 69, 19),
        "snake_head": (101, 67, 33),
        "food": (255, 215, 0),
        "text": (255, 255, 255),
        "boundary": (0, 100, 0)
    },
    "Royal": {
        "background": (75, 0, 130),
        "snake": (255, 215, 0),
        "snake_head": (218, 165, 32),
        "food": (255, 20, 147),
        "text": (255, 255, 255),
        "boundary": (0, 255, 255)
    }
}

# High score and settings files
HIGH_SCORE_FILE = "snake_highscore.json"
SETTINGS_FILE = "snake_settings.json"
VAULT_SETTINGS_FILE = "vault_settings.json"

# Global variables to hold loaded images
simple_food_img = None
bonus_food_imgs = None
special_food_img = None
magnus_food_img = None
shield_food_img = None
poison_food_img = None
speed_food_img = None
coin_img = None
coin_img_menu = None
background_img = None
menu_bg_img = None
intro_bg_img = None
exit_bg_img = None
start_bg_img = None
background_alpha = None
pause_overlay = None

# Skin images dictionaries
magnet_skins = {}
poison_skins = {}
shield_skins = {}
special_food_skins = {}
speed_boost_skins = {}
background_skins = {}

def load_vault_settings():
    """Load Game Vault settings"""
    default_settings = {
        "snake_skin": "GREEN",
        "magnet_skin": 1,
        "poison_skin": 1,
        "shield_skin": 1,
        "special_food_skin": 1,
        "speed_boost_skin": 1,
        "background_skin": 1,
        "owned_snake_skins": ["GREEN"],
        "owned_magnet_skins": [1],
        "owned_poison_skins": [1],
        "owned_shield_skins": [1],
        "owned_special_food_skins": [1],
        "owned_speed_boost_skins": [1],
        "owned_backgrounds": [1],
        "price_snake_skin": 50,
        "price_item_skin": 20,
        "price_background": 100
    }
    
    try:
        if os.path.exists(VAULT_SETTINGS_FILE):
            with open(VAULT_SETTINGS_FILE, 'r') as f:
                loaded_settings = json.load(f)
                # Validate loaded settings
                for key in default_settings:
                    if key not in loaded_settings:
                        loaded_settings[key] = default_settings[key]
                return loaded_settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading vault settings: {e}")
    
    return default_settings

def save_vault_settings(settings):
    """Save Game Vault settings safely by merging with existing file to avoid overwriting new purchases.

    This function will load the current vault file (if exists), merge owned lists by union and
    overwrite scalar values with the provided settings, then write back to disk.
    """
    try:
        existing = {}
        if os.path.exists(VAULT_SETTINGS_FILE):
            with open(VAULT_SETTINGS_FILE, 'r') as f:
                existing = json.load(f)
    except Exception as e:
        print(f"Warning: could not read existing vault settings: {e}")
        existing = {}
    # Merge logic: for lists of owned items, union them. For others, prefer provided 'settings'.
    merged = existing.copy()
    for k, v in settings.items():
        # keys that represent owned lists - if both are lists, union them
        if isinstance(v, list) and isinstance(existing.get(k), list):
            try:
                merged[k] = sorted(list({*existing.get(k, []), *v}), key=lambda x: (isinstance(x, int), x))
            except Exception:
                # fallback simple union
                merged[k] = list({*existing.get(k, []), *v})
        else:
            # For scalar values or when existing doesn't have the key, take the provided value
            merged[k] = v
    try:
        with open(VAULT_SETTINGS_FILE, 'w') as f:
            json.dump(merged, f)
    except Exception as e:
        print(f"Error saving vault settings safely: {e}")


def vault_purchase_item(settings, settings_file_ref, cost):
    """Attempt to purchase an item using total coins stored in main settings.
    Returns (success: bool, total_coins_after:int)."""
    try:
        main_settings = load_settings()
        total = main_settings.get('total_coins', 0)
        if total >= cost:
            total -= cost
            main_settings['total_coins'] = total
            save_settings(main_settings.get('boundary_mode', True), main_settings.get('theme', 'Classic'), total)
            return True, total
        else:
            return False, total
    except Exception as e:
        print(f"Error during purchase: {e}")
        return False, 0


def draw_coin_balance(surface, total_coins, x=None, y=10):
    """Draw coin icon and amount at top-right (used in vault and submenus)."""
    try:
        if coin_img_menu:
            xpos = x if x is not None else SCREEN_WIDTH - 100
            surface.blit(coin_img_menu, (xpos, y))
            coin_text = font_coin.render(f": {total_coins}", True, GOLD)
            coin_text_rect = coin_text.get_rect(topleft=(xpos + 30, y + (30 - coin_text.get_height()) // 2))
            surface.blit(coin_text, coin_text_rect)
    except Exception:
        pass

def save_and_reload_vault(vault_settings_local):
    """Save vault settings and return reloaded settings to ensure persistence across menus."""
    try:
        save_vault_settings(vault_settings_local)
    except Exception:
        pass
    return load_vault_settings()


def load_skin_images():
    """Load all skin images with error handling"""
    global magnet_skins, poison_skins, shield_skins, special_food_skins, speed_boost_skins, background_skins
    
    def create_placeholder(size, color):
        """Create a placeholder surface when image loading fails"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, *size))
        return surface
    
    # Load magnet effect skins
    for i in range(1, 6):
        try:
            img = pygame.image.load(f"m_effect ({i}).png").convert_alpha()
            magnet_skins[i] = pygame.transform.scale(img, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
        except Exception as e:
            print(f"Error loading m_effect ({i}).png: {e}")
            magnet_skins[i] = create_placeholder((int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)), BLUE)
    
    # Load poison food skins
    for i in range(1, 4):
        try:
            img = pygame.image.load(f"p_food ({i}).png").convert_alpha()
            poison_skins[i] = pygame.transform.scale(img, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
        except Exception as e:
            print(f"Error loading p_food ({i}).png: {e}")
            poison_skins[i] = create_placeholder((int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)), PURPLE)
    
    # Load shield skins
    for i in range(1, 6):
        try:
            img = pygame.image.load(f"shield ({i}).png").convert_alpha()
            shield_skins[i] = pygame.transform.scale(img, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
        except Exception as e:
            print(f"Error loading shield ({i}).png: {e}")
            shield_skins[i] = create_placeholder((int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)), CYAN)
    
    # Load special food skins
    for i in range(1, 4):
        try:
            img = pygame.image.load(f"s_food ({i}).png").convert_alpha()
            special_food_skins[i] = pygame.transform.scale(img, (int(GRID_SIZE * 2.0), int(GRID_SIZE * 2.0)))
        except Exception as e:
            print(f"Error loading s_food ({i}).png: {e}")
            special_food_skins[i] = create_placeholder((int(GRID_SIZE * 2.0), int(GRID_SIZE * 2.0)), GOLD)
    
    # Load speed boost skins
    for i in range(1, 5):
        try:
            img = pygame.image.load(f"boost ({i}).png").convert_alpha()
            speed_boost_skins[i] = pygame.transform.scale(img, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
        except Exception as e:
            print(f"Error loading boost ({i}).png: {e}")
            speed_boost_skins[i] = create_placeholder((int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)), (255, 0, 255))
    
    # Load background skins
    for i in range(1, 5):
        try:
            img = pygame.image.load(f"background{i}.png").convert()
            background_skins[i] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading background{i}.png: {e}")
            background_skins[i] = None

def load_images():
    """Load game images with error handling"""
    global simple_food_img, bonus_food_imgs, special_food_img, magnus_food_img, shield_food_img
    global poison_food_img, speed_food_img, coin_img, coin_img_menu, background_img, menu_bg_img
    global intro_bg_img, exit_bg_img, start_bg_img, background_alpha, pause_overlay
    
    def load_image(file, size=None, alpha=True):
        """Helper function to load an image with error handling"""
        try:
            img = pygame.image.load(file)
            if alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except Exception as e:
            print(f"Error loading image {file}: {e}")
            # Create a colored placeholder
            surface = pygame.Surface(size if size else (GRID_SIZE, GRID_SIZE), pygame.SRCALPHA if alpha else 0)
            color = RED if "food" in file else BLUE  # Default colors for different types
            pygame.draw.rect(surface, color, (0, 0, *surface.get_size()))
            return surface
    
    try:
        scale_factor = 1.5
        new_size = (int(GRID_SIZE * scale_factor), int(GRID_SIZE * scale_factor))
        special_size = (int(GRID_SIZE * 2.0), int(GRID_SIZE * 2.0))
        
        simple_food_img = load_image("simple food.png", new_size)
        bonus_food_imgs = [
            load_image("Bonus food (1).png", new_size),
            load_image("Bonus food (2).png", new_size),
            load_image("Bonus food (3).png", new_size),
            load_image("Bonus food (4).png", new_size)
        ]
        
        special_food_img = load_image("Special food (1).png", special_size)
        magnus_food_img = load_image("m_default.png", new_size)
        shield_food_img = load_image("shield_default.png", new_size)
        poison_food_img = load_image("poison_default.png", new_size)
        speed_food_img = load_image("speed_default.png", new_size)
        
        coin_img = load_image("coin.png", new_size)
        coin_img_menu = load_image("coin.png", (30, 30))
        
        background_img = load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
        menu_bg_img = load_image("menu.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
        intro_bg_img = load_image("intro.jpeg", (SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
        exit_bg_img = load_image("exit.jpeg", (SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
        start_bg_img = load_image("start.png", (SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
        
        background_alpha = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_alpha.fill((0, 0, 0))
        background_alpha.set_alpha(150)
        
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_overlay.fill((0, 0, 0))
        pause_overlay.set_alpha(200)
    except Exception as e:
        print(f"Error initializing images: {e}")

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.life = random.randint(20, 40)
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.5, 2)
        self.original_life = self.life
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        alpha = int(255 * (self.life / self.original_life))
        self.current_color = (*self.color[:3], alpha)
    
    def draw(self, surface):
        if len(self.current_color) == 4:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, self.current_color, (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))
        else:
            pygame.draw.circle(surface, self.current_color, (int(self.x), int(self.y)), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class Snake:
    def __init__(self, theme="Classic", skin_color="GREEN"):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.length = 1
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.skin_color = skin_color
        self.color = SNAKE_COLORS.get(skin_color, THEMES[theme]["snake"])
        self.head_color = tuple(max(0, c - 50) for c in self.color) if skin_color in SNAKE_COLORS else THEMES[theme]["snake_head"]
        self.score = 0
        self.speed = SPEED_EASY
        self.special_food_active = False
        self.special_food_timer = 0
        self.texture_offset = 0
        self.bonus_sound_playing = False
        self.particle_system = ParticleSystem()
        self.collision_particles = ParticleSystem()
        self.collision_time = 0
        self.is_colliding = False
        self.magnus_effect_active = False
        self.magnus_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        self.shield_count = 0
        self.speed_boost_active = False
        self.speed_boost_timer = 0
        self.coins_collected = 0
        self.shield_animation_frame = 0
        self.shield_particles = ParticleSystem()
    
    def create_skin_texture(self):
        texture = []
        base_color = self.color
        for i in range(10):
            shade_factor = 0.5 + (i * 0.05)
            texture_color = tuple(int(c * shade_factor) for c in base_color)
            texture.append(texture_color)
        return texture
        
    def get_head_position(self):
        return self.positions[0]
        
    def update(self, boundary_mode, food, coin):
        if self.is_colliding:
            return True
            
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x), (head[1] + y))
        
        # Handle magnet effect
        if self.magnus_effect_active:
            try:
                food_pos = food.position if getattr(food, 'position', None) is not None else None
                coin_pos = coin.position if getattr(coin, 'active', False) and getattr(coin, 'position', None) is not None else None
                items = []
                if food_pos is not None:
                    items.append((food_pos, food))
                if coin_pos is not None:
                    items.append((coin_pos, coin))
                for item_pos, item in items:
                    try:
                        ix, iy = int(item_pos[0]), int(item_pos[1])
                    except Exception:
                        continue
                    dx = head[0] - ix
                    dy = head[1] - iy
                    distance = math.hypot(dx, dy)
                    if distance > 0 and distance < 5:
                        move_x = dx / distance
                        move_y = dy / distance
                        new_item_pos = (int(ix + move_x * 2), int(iy + move_y * 2))
                        new_item_pos = (max(0, min(new_item_pos[0], GRID_WIDTH - 1)), max(0, min(new_item_pos[1], GRID_HEIGHT - 1)))
                        if new_item_pos not in self.positions:
                            try:
                                item.position = new_item_pos
                            except Exception:
                                pass
            except Exception as e:
                print(f"Magnet effect handling error: {e}")
        
        # Check boundary collision
        if boundary_mode and (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
                           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            if self.shield_active and self.shield_count > 0:
                sounds["shield_broken"].play()
                self.shield_count -= 1
                self.shield_active = False
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
                self.respawn_after_shield()
                return False
            self.handle_collision(new_head)
            return True
            
        # Wrap around if no boundary mode
        if not boundary_mode:
            new_head = ((new_head[0] % GRID_WIDTH), (new_head[1] % GRID_HEIGHT))
        
        # Check for self-collision
        if new_head in self.positions[1:]:
            if self.shield_active and self.shield_count > 0:
                sounds["shield_broken"].play()
                self.shield_count -= 1
                self.shield_active = False
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
                self.respawn_after_shield()
                return False
            self.handle_collision(new_head)
            return True
            
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
            
        self.texture_offset = (self.texture_offset + 1) % 10
        return False
        
    def handle_collision(self, position):
        self.is_colliding = True
        self.collision_time = time.time()
        center_x = position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = position[1] * GRID_SIZE + GRID_SIZE // 2
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        for _ in range(50):
            color = random.choice(colors)
            self.collision_particles.add_particles(center_x, center_y, color, 1)
        if position in self.positions[1:]:
            sounds["snake_bite"].play()
        else:
            sounds["collision"].play()
        pygame.mixer.Sound.stop(sounds["bonus_timer"])
        
    def respawn_after_shield(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        temp_length = self.length
        self.length = 1
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        head = self.positions[0]
        for _ in range(temp_length - 1):
            self.positions.append(head)
        self.is_colliding = False
        self.collision_particles = ParticleSystem()
        center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
        self.shield_particles.add_particles(center_x, center_y, (0, 255, 255, 200), 30)
        
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.length = 1
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.score = 0
        self.is_colliding = False
        self.collision_particles = ParticleSystem()
        self.magnus_effect_active = False
        self.shield_active = False
        self.shield_count = 0
        self.speed_boost_active = False
        self.coins_collected = 0
        self.shield_particles = ParticleSystem()
        
    def render(self, surface, theme):
        for i, p in enumerate(self.positions):
            texture_index = (i + self.texture_offset) % 10
            body_color = self.create_skin_texture()[texture_index]
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            if i == 0:
                if self.shield_active:
                    self.shield_animation_frame = (self.shield_animation_frame + 1) % 20
                    shield_color = (0, 255, 255, 150) if self.shield_animation_frame < 10 else (255, 255, 255, 150)
                    shield_surface = pygame.Surface((GRID_SIZE * 1.5, GRID_SIZE * 1.5), pygame.SRCALPHA)
                    pygame.draw.circle(shield_surface, shield_color, (GRID_SIZE * 0.75, GRID_SIZE * 0.75), GRID_SIZE * 0.75)
                    surface.blit(shield_surface, (p[0] * GRID_SIZE - GRID_SIZE // 4, p[1] * GRID_SIZE - GRID_SIZE // 4))
                    center_x = p[0] * GRID_SIZE + GRID_SIZE // 2
                    center_y = p[1] * GRID_SIZE + GRID_SIZE // 2
                    if self.shield_animation_frame % 5 == 0:
                        self.shield_particles.add_particles(center_x, center_y, (0, 255, 255, 200), 5)
                pygame.draw.rect(surface, self.head_color, rect)
                eye_size = GRID_SIZE // 5
                if self.direction == (0, -1):
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3), eye_size)
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3), eye_size)
                elif self.direction == (0, 1):
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3), eye_size)
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3), eye_size)
                elif self.direction == (-1, 0):
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3), eye_size)
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3), eye_size)
                else:
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + GRID_SIZE // 3), eye_size)
                    pygame.draw.circle(surface, BLACK, (p[0] * GRID_SIZE + 2 * GRID_SIZE // 3, p[1] * GRID_SIZE + 2 * GRID_SIZE // 3), eye_size)
            else:
                pygame.draw.rect(surface, body_color, rect)
                if i % 2 == 0:
                    pygame.draw.circle(surface, (body_color[0]//2, body_color[1]//2, body_color[2]//2), 
                                     (p[0] * GRID_SIZE + GRID_SIZE // 2, p[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 4)
        
        self.particle_system.update()
        self.particle_system.draw(surface)
        self.shield_particles.update()
        self.shield_particles.draw(surface)
        if self.is_colliding:
            self.collision_particles.update()
            self.collision_particles.draw(surface)

class Food:
    def __init__(self, theme="Classic", vault_settings=None):
        self.position = (0, 0)
        self.color = THEMES[theme]["food"]
        self.type = "normal"
        self.spawn_time = 0
        self.bonus_type = 0
        self.vault_settings = vault_settings or load_vault_settings()
        self.spawn_food()
        
    def spawn_food(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        self.spawn_time = time.time()
        rand = random.random()
        if rand < 0.03:
            self.type = "magnus"
        elif rand < 0.06:
            self.type = "shield"
        elif rand < 0.09:
            self.type = "poison"
        elif rand < 0.12:
            self.type = "speed"
        elif rand < 0.17:
            self.type = "special"
        elif rand < 0.32:
            self.type = "bonus"
            self.bonus_type = random.randint(0, 3)
        else:
            self.type = "normal"
            
    def render(self, surface):
        pos_x, pos_y = self.position
        
        if self.type == "special":
            skin_num = self.vault_settings.get("special_food_skin", 1)
            if skin_num in special_food_skins and special_food_skins[skin_num]:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - special_food_skins[skin_num].get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - special_food_skins[skin_num].get_height()) // 2
                surface.blit(special_food_skins[skin_num], (img_x, img_y))
            elif special_food_img:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - special_food_img.get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - special_food_img.get_height()) // 2
                surface.blit(special_food_img, (img_x, img_y))
            else:
                rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, GOLD, rect)
        elif self.type == "bonus" and bonus_food_imgs:
            img_x = pos_x * GRID_SIZE + (GRID_SIZE - bonus_food_imgs[self.bonus_type].get_width()) // 2
            img_y = pos_y * GRID_SIZE + (GRID_SIZE - bonus_food_imgs[self.bonus_type].get_height()) // 2
            surface.blit(bonus_food_imgs[self.bonus_type], (img_x, img_y))
        elif self.type == "normal" and simple_food_img:
            img_x = pos_x * GRID_SIZE + (GRID_SIZE - simple_food_img.get_width()) // 2
            img_y = pos_y * GRID_SIZE + (GRID_SIZE - simple_food_img.get_height()) // 2
            surface.blit(simple_food_img, (img_x, img_y))
        elif self.type == "magnus":
            skin_num = self.vault_settings.get("magnet_skin", 1)
            if skin_num in magnet_skins and magnet_skins[skin_num]:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - magnet_skins[skin_num].get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - magnet_skins[skin_num].get_height()) // 2
                surface.blit(magnet_skins[skin_num], (img_x, img_y))
            elif magnus_food_img:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - magnus_food_img.get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - magnus_food_img.get_height()) // 2
                surface.blit(magnus_food_img, (img_x, img_y))
            else:
                rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, BLUE, rect)
        elif self.type == "shield":
            skin_num = self.vault_settings.get("shield_skin", 1)
            if skin_num in shield_skins and shield_skins[skin_num]:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - shield_skins[skin_num].get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - shield_skins[skin_num].get_height()) // 2
                surface.blit(shield_skins[skin_num], (img_x, img_y))
            elif shield_food_img:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - shield_food_img.get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - shield_food_img.get_height()) // 2
                surface.blit(shield_food_img, (img_x, img_y))
            else:
                rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, CYAN, rect)
        elif self.type == "poison":
            skin_num = self.vault_settings.get("poison_skin", 1)
            if skin_num in poison_skins and poison_skins[skin_num]:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - poison_skins[skin_num].get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - poison_skins[skin_num].get_height()) // 2
                surface.blit(poison_skins[skin_num], (img_x, img_y))
            elif poison_food_img:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - poison_food_img.get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - poison_food_img.get_height()) // 2
                surface.blit(poison_food_img, (img_x, img_y))
            else:
                rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, PURPLE, rect)
        elif self.type == "speed":
            skin_num = self.vault_settings.get("speed_boost_skin", 1)
            if skin_num in speed_boost_skins and speed_boost_skins[skin_num]:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - speed_boost_skins[skin_num].get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - speed_boost_skins[skin_num].get_height()) // 2
                surface.blit(speed_boost_skins[skin_num], (img_x, img_y))
            elif speed_food_img:
                img_x = pos_x * GRID_SIZE + (GRID_SIZE - speed_food_img.get_width()) // 2
                img_y = pos_y * GRID_SIZE + (GRID_SIZE - speed_food_img.get_height()) // 2
                surface.blit(speed_food_img, (img_x, img_y))
            else:
                rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, (255, 0, 255), rect)
        else:
            rect = pygame.Rect(pos_x * GRID_SIZE, pos_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if self.type == "special":
                pygame.draw.rect(surface, GOLD, rect)
            elif self.type == "bonus":
                pygame.draw.rect(surface, random.choice([YELLOW, PURPLE, CYAN, ORANGE]), rect)
            elif self.type == "magnus":
                pygame.draw.rect(surface, BLUE, rect)
            elif self.type == "shield":
                pygame.draw.rect(surface, CYAN, rect)
            elif self.type == "poison":
                pygame.draw.rect(surface, PURPLE, rect)
            elif self.type == "speed":
                pygame.draw.rect(surface, (255, 0, 255), rect)
            else:
                pygame.draw.rect(surface, RED, rect)

class Coin:
    def __init__(self):
        self.position = (0, 0)
        self.spawn_time = 0
        self.active = False
        
    def spawn(self, snake_positions):
        if not self.active:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            while self.position in snake_positions:
                self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            self.spawn_time = time.time()
            self.active = True
            
    def render(self, surface):
        if self.active and coin_img:
            pos_x, pos_y = self.position
            img_x = pos_x * GRID_SIZE + (GRID_SIZE - coin_img.get_width()) // 2
            img_y = pos_y * GRID_SIZE + (GRID_SIZE - coin_img.get_height()) // 2
            surface.blit(coin_img, (img_x, img_y))
        elif self.active:
            pos_x, pos_y = self.position
            pygame.draw.circle(surface, GOLD, 
                              (pos_x * GRID_SIZE + GRID_SIZE // 2, pos_y * GRID_SIZE + GRID_SIZE // 2), 
                              GRID_SIZE // 2)

def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect

def draw_arrow_button(surface, x, y, direction, color, size=30):
    """Draw arrow button for skin selection"""
    points = []
    if direction == "left":
        points = [(x + size, y), (x, y + size//2), (x + size, y + size)]
    else:  # right
        points = [(x, y), (x + size, y + size//2), (x, y + size)]
    
    pygame.draw.polygon(surface, color, points)
    return pygame.Rect(x, y, size, size)

def load_high_scores():
    default_scores = {"easy": 0, "medium": 0, "hard": 0}
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                loaded_scores = json.load(f)
                # Validate loaded scores
                for key in default_scores:
                    if key not in loaded_scores:
                        loaded_scores[key] = default_scores[key]
                return loaded_scores
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading high scores: {e}")
    
    return default_scores

def save_high_scores(scores):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(scores, f)
    except IOError as e:
        print(f"Error saving high scores: {e}")

def load_settings():
    default_settings = {"boundary_mode": True, "theme": "Classic", "total_coins": 0}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Validate settings
                for key in default_settings:
                    if key not in settings:
                        settings[key] = default_settings[key]
                if settings.get('theme') not in THEMES:
                    settings['theme'] = "Classic"
                return settings
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading settings: {e}")
    
    return default_settings

def save_settings(boundary_mode, theme, total_coins):
    settings = {"boundary_mode": boundary_mode, "theme": theme, "total_coins": total_coins}
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except IOError as e:
        print(f"Error saving settings: {e}")


def show_skin_selector(title, skin_dict, current_skin, theme):
    """Generic skin selector for items. Purchase will keep the menu open on success,
    deduct coins from settings, and show a red 'Unsufficient coins' subtitle on failure for 2 seconds."""
    menu = True
    selected_skin = current_skin
    # Ensure we have a sensible max_skins
    try:
        max_skins = len(skin_dict) if skin_dict else 1
    except Exception:
        max_skins = 1

    unsuff_timer = 0.0  # timestamp when insufficient coins occurred (0 = none)
    UNSUFF_DURATION = 2.0  # seconds to show subtitle

    while menu:
        vault_settings_local = load_vault_settings()
        main_settings = load_settings()
        total_coins = main_settings.get('total_coins', 0)
        insufficient_warning = False

        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])

        # Title
        draw_text(title, font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 80, True)
        try:
            draw_coin_balance(screen, load_settings().get('total_coins', 0))
        except Exception:
            pass

        # Display current skin - centered between arrows
        has_img = False
        if selected_skin in skin_dict and skin_dict[selected_skin]:
            img = skin_dict[selected_skin]
            img_x = SCREEN_WIDTH // 2 - img.get_width() // 2
            img_y = SCREEN_HEIGHT // 2 - img.get_height() // 2
            screen.blit(img, (img_x, img_y))
            has_img = True
        else:
            # Fallback rectangle - centered between arrows
            rect_size = 80
            rect_x = SCREEN_WIDTH // 2 - rect_size // 2
            rect_y = SCREEN_HEIGHT // 2 - rect_size // 2
            pygame.draw.rect(screen, RED, (rect_x, rect_y, rect_size, rect_size))

        # Draw arrows
        left_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 15, "left", WHITE)
        right_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 - 15, "right", WHITE)

        # Skin number indicator
        draw_text(f"Skin {selected_skin}/{max_skins}", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, True)

        # Determine ownership for the skin being shown
        owned_flag = False
        price = 0
        if 'MAGNET' in title.upper():
            owned_flag = selected_skin in vault_settings_local.get('owned_magnet_skins', [])
            price = vault_settings_local.get('price_item_skin', 20)
        elif 'POISON' in title.upper():
            owned_flag = selected_skin in vault_settings_local.get('owned_poison_skins', [])
            price = vault_settings_local.get('price_item_skin', 20)
        elif 'SHIELD' in title.upper():
            owned_flag = selected_skin in vault_settings_local.get('owned_shield_skins', [])
            price = vault_settings_local.get('price_item_skin', 20)
        elif 'SPECIAL' in title.upper():
            owned_flag = selected_skin in vault_settings_local.get('owned_special_food_skins', [])
            price = vault_settings_local.get('price_item_skin', 20)
        elif 'SPEED' in title.upper():
            owned_flag = selected_skin in vault_settings_local.get('owned_speed_boost_skins', [])
            price = vault_settings_local.get('price_item_skin', 20)
        else:
            owned_flag = True
            price = 0

        # Buttons
        if owned_flag:
            apply_rect = draw_text("APPLY", font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 150, True)
        else:
            buy_text = f"BUY FOR {price}"
            buy_rect = draw_text(buy_text, font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 150, True)
            if coin_img_menu:
                icon_x = buy_rect.right + 5
                icon_y = buy_rect.top + (buy_rect.height - coin_img_menu.get_height()) // 2
                screen.blit(coin_img_menu, (icon_x, icon_y))
            apply_rect = buy_rect
        back_rect = draw_text("BACK", font_medium, RED, screen, SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 150, True)

        # If we have a timestamp, and it's within duration, show subtitle just under the item
        if unsuff_timer and (time.time() - unsuff_timer) < UNSUFF_DURATION:
            # Subtitle positioned under the preview (adjust Y offset as needed)
            y_offset = SCREEN_HEIGHT // 2 + 90
            if has_img:
                try:
                    y_offset = img_y + img.get_height() + 10
                except Exception:
                    y_offset = SCREEN_HEIGHT // 2 + 90
            draw_text("Unsufficient coins", font_small, RED, screen, SCREEN_WIDTH // 2, y_offset, True)
        else:
            # reset if expired
            if unsuff_timer and (time.time() - unsuff_timer) >= UNSUFF_DURATION:
                unsuff_timer = 0.0

        # Instructions
        draw_text("Use LEFT/RIGHT arrows or click arrow buttons to change skin", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if left_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected_skin = max(1, selected_skin - 1)
                elif right_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected_skin = min(max_skins, selected_skin + 1)
                elif apply_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    # If already owned, apply immediately and return selection
                    if owned_flag:
                        return selected_skin
                    else:
                        # Attempt purchase: check local total_coins first for quick feedback
                        main_settings = load_settings()
                        total_coins = main_settings.get('total_coins', 0)
                        if total_coins >= price:
                            # Deduct via vault_purchase_item (keeps single source of truth)
                            success, new_total = vault_purchase_item(vault_settings_local, VAULT_SETTINGS_FILE, price)
                            if success:
                                # Add to the appropriate owned list and save vault settings
                                if 'MAGNET' in title.upper():
                                    vault_settings_local.setdefault('owned_magnet_skins', []).append(selected_skin)
                                elif 'POISON' in title.upper():
                                    vault_settings_local.setdefault('owned_poison_skins', []).append(selected_skin)
                                elif 'SHIELD' in title.upper():
                                    vault_settings_local.setdefault('owned_shield_skins', []).append(selected_skin)
                                elif 'SPECIAL' in title.upper():
                                    vault_settings_local.setdefault('owned_special_food_skins', []).append(selected_skin)
                                elif 'SPEED' in title.upper():
                                    vault_settings_local.setdefault('owned_speed_boost_skins', []).append(selected_skin)
                                # Persist and reload to avoid any in-memory mismatch
                                save_vault_settings(vault_settings_local)
                                vault_settings_local = load_vault_settings()
                                sounds['coin'].play()
                                # Refresh total_coins for UI and keep menu open on the same item
                                main_settings = load_settings()
                                total_coins = main_settings.get('total_coins', 0)
                                owned_flag = selected_skin in vault_settings_local.get('owned_magnet_skins', []) or owned_flag
                                # do NOT return; remain on item as requested
                            else:
                                sounds['no'].play()
                                insufficient_warning = True
                                unsuff_timer = time.time()
                        else:
                            sounds['no'].play()
                            insufficient_warning = True
                            unsuff_timer = time.time()
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return current_skin
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sounds["click"].play()
                    selected_skin = max(1, selected_skin - 1)
                elif event.key == pygame.K_RIGHT:
                    sounds["click"].play()
                    selected_skin = min(max_skins, selected_skin + 1)
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    return selected_skin
                elif event.key == pygame.K_ESCAPE:
                    sounds["click"].play()
                    return current_skin

        pygame.display.update()
        clock.tick(FPS)

def show_snake_skin_menu(current_skin, theme):
    """Snake skin selection menu that supports buying without leaving the menu and shows warnings."""
    menu = True
    skin_names = list(SNAKE_COLORS.keys())
    current_index = skin_names.index(current_skin) if current_skin in skin_names else 0

    unsuff_timer = 0.0
    UNSUFF_DURATION = 2.0

    while menu:
        vault_settings_local = load_vault_settings()
        main_settings = load_settings()
        total_coins = main_settings.get('total_coins', 0)
        insufficient_warning = False

        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])

        # Title
        draw_text("SNAKE SKINS", font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 80, True)
        try:
            draw_coin_balance(screen, load_settings().get('total_coins', 0))
        except Exception:
            pass

        # Display current snake color
        current_skin_name = skin_names[current_index]
        current_color = SNAKE_COLORS[current_skin_name]

        # Draw snake preview - centered between arrows
        snake_size = 60
        snake_x = SCREEN_WIDTH // 2 - snake_size // 2
        snake_y = SCREEN_HEIGHT // 2 - snake_size // 2
        pygame.draw.rect(screen, current_color, (snake_x, snake_y, snake_size, snake_size))

        # Draw arrows
        left_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 15, "left", WHITE)
        right_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 - 15, "right", WHITE)

        # Skin name
        draw_text(current_skin_name, font_medium, current_color, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, True)

        # Buttons (BUY/APPLY for snake skins)
        owned_snakes = vault_settings_local.get('owned_snake_skins', [])
        snake_price = vault_settings_local.get('price_snake_skin', 50)
        if current_skin_name in owned_snakes:
            apply_rect = draw_text("APPLY", font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 150, True)
            is_owned = True
        else:
            buy_text = f"BUY FOR {snake_price}"
            buy_rect = draw_text(buy_text, font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 150, True)
            if coin_img_menu:
                icon_x = buy_rect.right + 5
                icon_y = buy_rect.top + (buy_rect.height - coin_img_menu.get_height()) // 2
                screen.blit(coin_img_menu, (icon_x, icon_y))
            apply_rect = buy_rect
            is_owned = False
        back_rect = draw_text("BACK", font_medium, RED, screen, SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 150, True)

        # show subtitle under preview if needed
        if unsuff_timer and (time.time() - unsuff_timer) < UNSUFF_DURATION:
            draw_text("Unsufficient coins", font_small, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55, True)
        else:
            if unsuff_timer and (time.time() - unsuff_timer) >= UNSUFF_DURATION:
                unsuff_timer = 0.0

        # Instructions
        draw_text("Use LEFT/RIGHT arrows or click arrow buttons to change skin", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if left_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    current_index = (current_index - 1) % len(skin_names)
                elif right_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    current_index = (current_index + 1) % len(skin_names)
                elif apply_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    if is_owned:
                        return skin_names[current_index]
                    else:
                        # Try to purchase
                        main_settings = load_settings()
                        total_coins = main_settings.get('total_coins', 0)
                        if total_coins >= snake_price:
                            success, new_total = vault_purchase_item(vault_settings_local, VAULT_SETTINGS_FILE, snake_price)
                            if success:
                                vault_settings_local.setdefault('owned_snake_skins', []).append(current_skin_name)
                                # Persist and reload vault settings
                                save_vault_settings(vault_settings_local)
                                vault_settings_local = load_vault_settings()
                                sounds['coin'].play()
                                insufficient_warning = False
                                # refresh ownership and keep menu open
                            else:
                                sounds['no'].play()
                                insufficient_warning = True
                                unsuff_timer = time.time()
                        else:
                            sounds['no'].play()
                            insufficient_warning = True
                            unsuff_timer = time.time()
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return current_skin
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sounds["click"].play()
                    current_index = (current_index - 1) % len(skin_names)
                elif event.key == pygame.K_RIGHT:
                    sounds["click"].play()
                    current_index = (current_index + 1) % len(skin_names)
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    return skin_names[current_index]
                elif event.key == pygame.K_ESCAPE:
                    sounds["click"].play()
                    return current_skin

        pygame.display.update()
        clock.tick(FPS)


def show_background_selector(current_bg, theme):
    """Background selector with purchase handling that keeps the menu open on success and shows warnings."""
    menu = True
    selected_bg = current_bg
    max_backgrounds = 4

    unsuff_timer = 0.0
    UNSUFF_DURATION = 2.0

    while menu:
        vault_settings_local = load_vault_settings()
        main_settings = load_settings()
        total_coins = main_settings.get('total_coins', 0)
        insufficient_warning = False

        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])

        # Title
        draw_text("GAME BACKGROUNDS", font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 80, True)
        try:
            draw_coin_balance(screen, load_settings().get('total_coins', 0))
        except Exception:
            pass

        # Display current background preview (smaller version)
        if selected_bg in background_skins and background_skins[selected_bg]:
            preview_img = pygame.transform.scale(background_skins[selected_bg], (300, 200))
            img_x = SCREEN_WIDTH // 2 - 150
            img_y = SCREEN_HEIGHT // 2 - 100
            screen.blit(preview_img, (img_x, img_y))
            pygame.draw.rect(screen, WHITE, (img_x, img_y, 300, 200), 2)
        else:
            # Fallback rectangle
            rect_x = SCREEN_WIDTH // 2 - 150
            rect_y = SCREEN_HEIGHT // 2 - 100
            pygame.draw.rect(screen, RED, (rect_x, rect_y, 300, 200))

        # Draw arrows
        left_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 15, "left", WHITE)
        right_arrow = draw_arrow_button(screen, SCREEN_WIDTH // 2 + 170, SCREEN_HEIGHT // 2 - 15, "right", WHITE)

        # Background number indicator
        draw_text(f"Background {selected_bg}/{max_backgrounds}", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, True)

        # Buttons (BUY/APPLY for backgrounds)
        owned_bg = vault_settings_local.get('owned_backgrounds', [])
        bg_price = vault_settings_local.get('price_background', 100)
        if selected_bg in owned_bg:
            apply_rect = draw_text("APPLY", font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 150, True)
            is_owned = True
        else:
            buy_text = f"BUY FOR {bg_price}"
            buy_rect = draw_text(buy_text, font_medium, GREEN, screen, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 150, True)
            if coin_img_menu:
                icon_x = buy_rect.right + 5
                icon_y = buy_rect.top + (buy_rect.height - coin_img_menu.get_height()) // 2
                screen.blit(coin_img_menu, (icon_x, icon_y))
            apply_rect = buy_rect
            is_owned = False
        back_rect = draw_text("BACK", font_medium, RED, screen, SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 150, True)

        # Show subtitle under preview if triggered
        if unsuff_timer and (time.time() - unsuff_timer) < UNSUFF_DURATION:
            draw_text("Unsufficient coins", font_small, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, True)
        else:
            if unsuff_timer and (time.time() - unsuff_timer) >= UNSUFF_DURATION:
                unsuff_timer = 0.0

        # Instructions
        draw_text("Use LEFT/RIGHT arrows or click arrow buttons to change background", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if left_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected_bg = max(1, selected_bg - 1)
                elif right_arrow.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected_bg = min(max_backgrounds, selected_bg + 1)
                elif apply_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    if is_owned:
                        return selected_bg
                    else:
                        main_settings = load_settings()
                        total_coins = main_settings.get('total_coins', 0)
                        if total_coins >= bg_price:
                            success, new_total = vault_purchase_item(vault_settings_local, VAULT_SETTINGS_FILE, bg_price)
                            if success:
                                vault_settings_local.setdefault('owned_backgrounds', []).append(selected_bg)
                                # Persist and reload to avoid mismatch
                                save_vault_settings(vault_settings_local)
                                vault_settings_local = load_vault_settings()
                                sounds['coin'].play()
                                insufficient_warning = False
                                is_owned = True
                                # keep menu open
                            else:
                                sounds['no'].play()
                                insufficient_warning = True
                                unsuff_timer = time.time()
                        else:
                            sounds['no'].play()
                            insufficient_warning = True
                            unsuff_timer = time.time()
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return current_bg
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    sounds["click"].play()
                    selected_bg = max(1, selected_bg - 1)
                elif event.key == pygame.K_RIGHT:
                    sounds["click"].play()
                    selected_bg = min(max_backgrounds, selected_bg + 1)
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    return selected_bg
                elif event.key == pygame.K_ESCAPE:
                    sounds["click"].play()
                    return current_bg

        pygame.display.update()
        clock.tick(FPS)


def show_item_skins_menu(theme, vault_settings):
    """Item skins submenu"""
    menu = True
    selected = "magnet"
    
    while menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Title
        draw_text("ITEM SKINS", font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 80, True)
        try:
            draw_coin_balance(screen, load_settings().get('total_coins', 0))
        except Exception:
            pass
        
        # Menu options with spacing
        magnet_rect = draw_text("MAGNET EFFECT SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 160, True)
        poison_rect = draw_text("POISON FOOD SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 220, True)
        shield_rect = draw_text("SHIELD SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 280, True)
        special_rect = draw_text("SPECIAL FOOD SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 340, True)
        speed_rect = draw_text("SPEED BOOST SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        back_rect = draw_text("BACK", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        
        # Apply colors based on hover or selection
        magnet_color = GREEN if magnet_rect.collidepoint(mouse_pos) or selected == "magnet" else THEMES[theme]["text"]
        poison_color = PURPLE if poison_rect.collidepoint(mouse_pos) or selected == "poison" else THEMES[theme]["text"]
        shield_color = CYAN if shield_rect.collidepoint(mouse_pos) or selected == "shield" else THEMES[theme]["text"]
        special_color = GOLD if special_rect.collidepoint(mouse_pos) or selected == "special" else THEMES[theme]["text"]
        speed_color = (255, 0, 255) if speed_rect.collidepoint(mouse_pos) or selected == "speed" else THEMES[theme]["text"]
        back_color = RED if back_rect.collidepoint(mouse_pos) or selected == "back" else THEMES[theme]["text"]
        
        draw_text("MAGNET EFFECT SKINS", font_medium, magnet_color, screen, SCREEN_WIDTH // 2, 160, True)
        draw_text("POISON FOOD SKINS", font_medium, poison_color, screen, SCREEN_WIDTH // 2, 220, True)
        draw_text("SHIELD SKINS", font_medium, shield_color, screen, SCREEN_WIDTH // 2, 280, True)
        draw_text("SPECIAL FOOD SKINS", font_medium, special_color, screen, SCREEN_WIDTH // 2, 340, True)
        draw_text("SPEED BOOST SKINS", font_medium, speed_color, screen, SCREEN_WIDTH // 2, 400, True)
        draw_text("BACK", font_medium, back_color, screen, SCREEN_WIDTH // 2, 480, True)
        
        # Instructions
        draw_text("Use UP/DOWN arrows to select, ENTER or click to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 550, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if magnet_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_skin_selector("MAGNET EFFECT SKINS", magnet_skins, vault_settings["magnet_skin"], theme)
                    vault_settings["magnet_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif poison_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_skin_selector("POISON FOOD SKINS", poison_skins, vault_settings["poison_skin"], theme)
                    vault_settings["poison_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif shield_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_skin_selector("SHIELD SKINS", shield_skins, vault_settings["shield_skin"], theme)
                    vault_settings["shield_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif special_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_skin_selector("SPECIAL FOOD SKINS", special_food_skins, vault_settings["special_food_skin"], theme)
                    vault_settings["special_food_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif speed_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_skin_selector("SPEED BOOST SKINS", speed_boost_skins, vault_settings["speed_boost_skin"], theme)
                    vault_settings["speed_boost_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sounds["click"].play()
                    options = ["magnet", "poison", "shield", "special", "speed", "back"]
                    current_index = options.index(selected)
                    selected = options[(current_index - 1) % len(options)]
                elif event.key == pygame.K_DOWN:
                    sounds["click"].play()
                    options = ["magnet", "poison", "shield", "special", "speed", "back"]
                    current_index = options.index(selected)
                    selected = options[(current_index + 1) % len(options)]
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected == "magnet":
                        new_skin = show_skin_selector("MAGNET EFFECT SKINS", magnet_skins, vault_settings["magnet_skin"], theme)
                        vault_settings["magnet_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "poison":
                        new_skin = show_skin_selector("POISON FOOD SKINS", poison_skins, vault_settings["poison_skin"], theme)
                        vault_settings["poison_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "shield":
                        new_skin = show_skin_selector("SHIELD SKINS", shield_skins, vault_settings["shield_skin"], theme)
                        vault_settings["shield_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "special":
                        new_skin = show_skin_selector("SPECIAL FOOD SKINS", special_food_skins, vault_settings["special_food_skin"], theme)
                        vault_settings["special_food_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "speed":
                        new_skin = show_skin_selector("SPEED BOOST SKINS", speed_boost_skins, vault_settings["speed_boost_skin"], theme)
                        vault_settings["speed_boost_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "back":
                        return
                elif event.key == pygame.K_ESCAPE:
                    sounds["click"].play()
                    return
        
        pygame.display.update()
        clock.tick(FPS)

def show_game_vault_menu(theme):
    """Main Game Vault menu"""
    menu = True
    selected = "snake_skins"
    vault_settings = load_vault_settings()
    
    while menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Title
        draw_text("GAME VAULT", font_large, GOLD, screen, SCREEN_WIDTH // 2, 80, True)
        try:
            draw_coin_balance(screen, load_settings().get('total_coins', 0))
        except Exception:
            pass
        
        # Menu options with proper spacing
        snake_rect = draw_text("SNAKE SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 160, True)
        item_rect = draw_text("ITEM SKINS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 220, True)
        background_rect = draw_text("GAME BACKGROUNDS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 280, True)
        back_rect = draw_text("BACK", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 360, True)
        
        # Apply colors based on hover or selection
        snake_color = GREEN if snake_rect.collidepoint(mouse_pos) or selected == "snake_skins" else THEMES[theme]["text"]
        item_color = CYAN if item_rect.collidepoint(mouse_pos) or selected == "item_skins" else THEMES[theme]["text"]
        background_color = PURPLE if background_rect.collidepoint(mouse_pos) or selected == "backgrounds" else THEMES[theme]["text"]
        back_color = RED if back_rect.collidepoint(mouse_pos) or selected == "back" else THEMES[theme]["text"]
        
        draw_text("SNAKE SKINS", font_medium, snake_color, screen, SCREEN_WIDTH // 2, 160, True)
        draw_text("ITEM SKINS", font_medium, item_color, screen, SCREEN_WIDTH // 2, 220, True)
        draw_text("GAME BACKGROUNDS", font_medium, background_color, screen, SCREEN_WIDTH // 2, 280, True)
        draw_text("BACK", font_medium, back_color, screen, SCREEN_WIDTH // 2, 360, True)
        
        # Instructions
        draw_text("Use UP/DOWN arrows to select, ENTER or click to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 450, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if snake_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_skin = show_snake_skin_menu(vault_settings["snake_skin"], theme)
                    vault_settings["snake_skin"] = new_skin
                    save_vault_settings(vault_settings)
                elif item_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    show_item_skins_menu(theme, vault_settings)
                elif background_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    new_bg = show_background_selector(vault_settings["background_skin"], theme)
                    vault_settings["background_skin"] = new_bg
                    save_vault_settings(vault_settings)
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sounds["click"].play()
                    if selected == "item_skins":
                        selected = "snake_skins"
                    elif selected == "backgrounds":
                        selected = "item_skins"
                    elif selected == "back":
                        selected = "backgrounds"
                elif event.key == pygame.K_DOWN:
                    sounds["click"].play()
                    if selected == "snake_skins":
                        selected = "item_skins"
                    elif selected == "item_skins":
                        selected = "backgrounds"
                    elif selected == "backgrounds":
                        selected = "back"
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected == "snake_skins":
                        new_skin = show_snake_skin_menu(vault_settings["snake_skin"], theme)
                        vault_settings["snake_skin"] = new_skin
                        save_vault_settings(vault_settings)
                    elif selected == "item_skins":
                        show_item_skins_menu(theme, vault_settings)
                    elif selected == "backgrounds":
                        new_bg = show_background_selector(vault_settings["background_skin"], theme)
                        vault_settings["background_skin"] = new_bg
                        save_vault_settings(vault_settings)
                    elif selected == "back":
                        return
                elif event.key == pygame.K_ESCAPE:
                    sounds["click"].play()
                    return
        
        pygame.display.update()
        clock.tick(FPS)

def show_countdown(theme, vault_settings):
    countdown = True
    current_number = 3
    start_time = time.time()
    alpha = 255
    scale = 1.0
    scale_direction = 0.05
    
    while countdown:
        try:
            if start_bg_img:
                screen.blit(start_bg_img, (0, 0))
            else:
                screen.fill(THEMES[theme]["background"])
        except Exception as e:
            print(f"Error displaying countdown background: {e}")
            screen.fill(THEMES[theme]["background"])
        
        elapsed = time.time() - start_time
        if elapsed < 1:
            current_number = 3
            color = GREEN
        elif elapsed < 2:
            current_number = 2
            color = YELLOW
        elif elapsed < 3:
            current_number = 1
            color = RED
        elif elapsed < 4:
            current_number = "GO!"
            color = RED
            if elapsed < 3.1:
                sounds["go"].play()
        else:
            countdown = False
            break
        
        scale += scale_direction
        if scale > 1.5 or scale < 1.0:
            scale_direction *= -1
        
        if isinstance(current_number, int):
            text = font_countdown.render(str(current_number), True, color)
            scaled_text = pygame.transform.scale(text, 
                (int(text.get_width() * scale), int(text.get_height() * scale)))
        else:
            scaled_text = font_countdown.render(current_number, True, color)
        
        text_rect = scaled_text.get_rect(center=(SCREEN_WIDTH - 200, SCREEN_HEIGHT//2))  # Moved to right side
        screen.blit(scaled_text, text_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
        clock.tick(FPS)

def show_intro():
    intro = True
    title_y = -100
    title_speed = 2
    
    sounds["welcome"].play()
    
    while intro:
        if intro_bg_img:
            screen.blit(intro_bg_img, (0, 0))
        else:
            screen.fill(DARK_BLUE)
        
        title_y += title_speed
        if title_y > SCREEN_HEIGHT // 4:
            title_y = SCREEN_HEIGHT // 4
            title_speed = 0
            
        draw_text("WELCOME TO", font_medium, WHITE, screen, SCREEN_WIDTH // 2, title_y - 50, True)
        draw_text("SNAKE GAME", font_large, RED, screen, SCREEN_WIDTH // 2, title_y, True)
        
        if title_speed == 0:
            draw_text("Press any key to continue", font_small, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and title_speed == 0:
                sounds["click"].play()
                intro = False
            if event.type == pygame.MOUSEBUTTONDOWN and title_speed == 0:
                sounds["click"].play()
                intro = False
        
        pygame.display.update()
        clock.tick(FPS)

def show_goodbye():
    goodbye = True
    start_time = time.time()
    rotation_angle = 0
    scale = 1.0
    alpha = 255
    
    sounds["yes"].play()
    
    while goodbye:
        if exit_bg_img:
            screen.blit(exit_bg_img, (0, 0))
        else:
            screen.fill(DARK_BLUE)
        
        elapsed = time.time() - start_time
        progress = min(elapsed / 4, 1.0)
        
        if elapsed > 3:
            alpha = int(255 * (1 - (elapsed - 3)))
        
        rotation_angle = (rotation_angle + 2) % 360
        scale = 1.0 + 0.3 * (elapsed % 0.5)
        
        text1 = font_medium.render("THANK YOU FOR PLAYING", True, WHITE)
        text2 = font_large.render("Good Bye !", True, RED)
        
        scaled_text1 = pygame.transform.scale_by(text1, 1.0 + 0.2 * (elapsed % 0.8))
        scaled_text2 = pygame.transform.scale_by(text2, scale)
        
        text1_rect = scaled_text1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        text2_rect = scaled_text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        
        if alpha < 255:
            scaled_text1.set_alpha(alpha)
            scaled_text2.set_alpha(alpha)
        
        screen.blit(scaled_text1, text1_rect)
        screen.blit(scaled_text2, text2_rect)
        
        if elapsed >= 4:
            pygame.time.delay(300)
            goodbye = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
        clock.tick(FPS)

def show_exit_confirmation(theme):
    confirm = True
    selected = "no"
    dialog_y = SCREEN_HEIGHT
    dialog_speed = 5
    sounds["exit_confirmation"].play(loops=-1)
    
    while confirm:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        dialog_y -= dialog_speed
        if dialog_y < SCREEN_HEIGHT // 3:
            dialog_y = SCREEN_HEIGHT // 3
            dialog_speed = 0
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw text first to ensure rects are defined
        yes_rect = draw_text("YES", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2 - 50, dialog_y + 70, True)
        no_rect = draw_text("NO", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2 + 50, dialog_y + 70, True)
        
        # Then apply colors based on hover or selection
        yes_color = GREEN if yes_rect.collidepoint(mouse_pos) or selected == "yes" else THEMES[theme]["text"]
        no_color = RED if no_rect.collidepoint(mouse_pos) or selected == "no" else THEMES[theme]["text"]
        
        draw_text("ARE YOU SURE TO EXIT?", font_medium, RED, screen, SCREEN_WIDTH // 2, dialog_y, True)
        draw_text("YES", font_medium, yes_color, screen, SCREEN_WIDTH // 2 - 50, dialog_y + 70, True)
        draw_text("NO", font_medium, no_color, screen, SCREEN_WIDTH // 2 + 50, dialog_y + 70, True)
        
        if dialog_speed == 0:
            draw_text("Use LEFT/RIGHT to select, ENTER to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, dialog_y + 120, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and dialog_speed == 0:
                mouse_pos = pygame.mouse.get_pos()
                if yes_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "yes"
                    sounds["exit_confirmation"].stop()
                    show_goodbye()
                    pygame.quit()
                    sys.exit()
                elif no_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "no"
                    sounds["exit_confirmation"].stop()
                    sounds["no"].play()
                    pygame.time.delay(300)
                    confirm = False
            if event.type == pygame.KEYDOWN and dialog_speed == 0:
                if event.key == pygame.K_LEFT:
                    sounds["click"].play()
                    selected = "yes"
                elif event.key == pygame.K_RIGHT:
                    sounds["click"].play()
                    selected = "no"
                elif event.key == pygame.K_RETURN:
                    sounds["exit_confirmation"].stop()
                    if selected == "yes":
                        show_goodbye()
                        pygame.quit()
                        sys.exit()
                    else:
                        sounds["no"].play()
                        pygame.time.delay(300)
                        confirm = False
        
        pygame.display.update()
        clock.tick(FPS)

def show_pause_menu(theme, snake, food, coin, boundary_mode, vault_settings):
    paused = True
    selected = "resume"
    dialog_y = SCREEN_HEIGHT
    dialog_speed = 5
    
    while paused:
        # Draw game background first (use selected background)
        bg_num = vault_settings.get("background_skin", 1)
        if bg_num in background_skins and background_skins[bg_num]:
            screen.blit(background_skins[bg_num], (0, 0))
        elif background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
            
        if background_alpha:
            screen.blit(background_alpha, (0, 0))
        
        # Draw game elements
        if boundary_mode:
            pygame.draw.rect(screen, THEMES[theme]["boundary"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)
        
        snake.render(screen, theme)
        if not snake.is_colliding:
            food.render(screen)
            if coin.active:
                coin.render(screen)
        
        score_text = f"Score: {snake.score}"
        if snake.special_food_active:
            score_text += " (2x BONUS!)"
            time_left = 10 - (time.time() - snake.special_food_timer)
            pygame.draw.rect(screen, GOLD, (10, 40, 200 * (time_left / 10), 10))
        
        if snake.magnus_effect_active:
            score_text += " (MAGNUS!)"
            time_left = 10 - (time.time() - snake.magnus_timer)
            pygame.draw.rect(screen, BLUE, (10, 40 if not snake.special_food_active else 55, 
                            200 * (time_left / 10), 10))
        
        if snake.shield_active:
            score_text += f" (SHIELD: {snake.shield_count})"
            time_left = 10 - (time.time() - snake.shield_timer)
            pygame.draw.rect(screen, CYAN, (10, 40 if not (snake.special_food_active or snake.magnus_effect_active) else 
                            (55 if snake.special_food_active or snake.magnus_effect_active else 70), 
                            200 * (time_left / 10), 10))
        
        if snake.speed_boost_active:
            score_text += " (SPEED!)"
            time_left = 10 - (time.time() - snake.speed_boost_timer)
            pygame.draw.rect(screen, PURPLE, (10, 40 if not (snake.special_food_active or snake.magnus_effect_active or snake.shield_active) else 
                            (55 if snake.special_food_active or snake.magnus_effect_active or snake.shield_active else 70), 
                            200 * (time_left / 10), 10))
        
        draw_text(score_text, font_small, THEMES[theme]["text"], screen, 10, 10)
        if coin_img_menu:
            screen.blit(coin_img_menu, (SCREEN_WIDTH - 100, 10))
            coin_text = font_coin.render(f": {snake.coins_collected}", True, GOLD)
            coin_text_rect = coin_text.get_rect(topleft=(SCREEN_WIDTH - 70, 10 + (30 - coin_text.get_height()) // 2))
            screen.blit(coin_text, coin_text_rect)
        
        # Draw pause overlay and menu
        if pause_overlay:
            screen.blit(pause_overlay, (0, 0))
        
        dialog_y -= dialog_speed
        if dialog_y < SCREEN_HEIGHT // 3:
            dialog_y = SCREEN_HEIGHT // 3
            dialog_speed = 0
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw text first to ensure rects are defined
        resume_rect = draw_text("RESUME", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2 - 100, dialog_y + 70, True)
        giveup_rect = draw_text("GIVE UP", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2 + 100, dialog_y + 70, True)
        
        # Then apply colors based on hover or selection
        resume_color = GREEN if resume_rect.collidepoint(mouse_pos) or selected == "resume" else THEMES[theme]["text"]
        giveup_color = RED if giveup_rect.collidepoint(mouse_pos) or selected == "giveup" else THEMES[theme]["text"]
        
        draw_text("WANT TO CONTINUE?", font_medium, WHITE, screen, SCREEN_WIDTH // 2, dialog_y, True)
        draw_text("RESUME", font_medium, resume_color, screen, SCREEN_WIDTH // 2 - 100, dialog_y + 70, True)
        draw_text("GIVE UP", font_medium, giveup_color, screen, SCREEN_WIDTH // 2 + 100, dialog_y + 70, True)
        
        if dialog_speed == 0:
            draw_text("Use LEFT/RIGHT to select, ENTER to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, dialog_y + 120, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and dialog_speed == 0:
                mouse_pos = pygame.mouse.get_pos()
                if resume_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "resume"
                    return True
                elif giveup_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "giveup"
                    return False
            if event.type == pygame.KEYDOWN and dialog_speed == 0:
                if event.key == pygame.K_LEFT:
                    sounds["click"].play()
                    selected = "resume"
                elif event.key == pygame.K_RIGHT:
                    sounds["click"].play()
                    selected = "giveup"
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected == "resume":
                        return True
                    else:
                        return False
        
        pygame.display.update()
        clock.tick(FPS)

def show_main_menu(boundary_mode, theme, total_coins):
    menu = True
    selected = "start"
    high_scores = load_high_scores()
    
    while menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw coin display
        if coin_img_menu:
            screen.blit(coin_img_menu, (SCREEN_WIDTH - 100, 10))
            coin_text = font_coin.render(f": {total_coins}", True, GOLD)
            coin_text_rect = coin_text.get_rect(topleft=(SCREEN_WIDTH - 70, 10 + (30 - coin_text.get_height()) // 2))
            screen.blit(coin_text, coin_text_rect)
        
        # Draw text first to ensure rects are defined
        start_rect = draw_text("START GAME", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 200, True)
        highscores_rect = draw_text("HIGH SCORES", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 250, True)
        vault_rect = draw_text("GAME VAULT", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 300, True)
        settings_rect = draw_text("SETTINGS", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 350, True)
        exit_rect = draw_text("EXIT", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        
        # Apply colors based on hover or selection
        start_color = GREEN if start_rect.collidepoint(mouse_pos) or selected == "start" else THEMES[theme]["text"]
        highscores_color = YELLOW if highscores_rect.collidepoint(mouse_pos) or selected == "highscores" else THEMES[theme]["text"]
        vault_color = GOLD if vault_rect.collidepoint(mouse_pos) or selected == "vault" else THEMES[theme]["text"]
        settings_color = CYAN if settings_rect.collidepoint(mouse_pos) or selected == "settings" else THEMES[theme]["text"]
        exit_color = RED if exit_rect.collidepoint(mouse_pos) or selected == "exit" else THEMES[theme]["text"]
        
        draw_text("MAIN MENU", font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 100, True)
        draw_text("START GAME", font_medium, start_color, screen, SCREEN_WIDTH // 2, 200, True)
        draw_text("HIGH SCORES", font_medium, highscores_color, screen, SCREEN_WIDTH // 2, 250, True)
        draw_text("GAME VAULT", font_medium, vault_color, screen, SCREEN_WIDTH // 2, 300, True)
        draw_text("SETTINGS", font_medium, settings_color, screen, SCREEN_WIDTH // 2, 350, True)
        draw_text("EXIT", font_medium, exit_color, screen, SCREEN_WIDTH // 2, 400, True)
        
        if start_rect.collidepoint(mouse_pos) or selected == "start":
            draw_text("Start a new game with selected difficulty", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        elif highscores_rect.collidepoint(mouse_pos) or selected == "highscores":
            draw_text("View your highest scores for each difficulty", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        elif vault_rect.collidepoint(mouse_pos) or selected == "vault":
            draw_text("Customize snake skins, item skins and game backgrounds", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        elif settings_rect.collidepoint(mouse_pos) or selected == "settings":
            draw_text("Change game theme and boundary settings", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        elif exit_rect.collidepoint(mouse_pos) or selected == "exit":
            draw_text("Exit the game", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 480, True)
        
        draw_text("Use UP/DOWN arrows to select, ENTER or click to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 550, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "start"
                    return show_difficulty_menu(theme), boundary_mode, theme, total_coins
                elif highscores_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "highscores"
                    show_high_scores_menu(high_scores, theme)
                elif vault_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "vault"
                    show_game_vault_menu(theme)
                    # reload settings after returning so UI shows updated coin balance
                    settings = load_settings()
                    total_coins = settings.get("total_coins", total_coins)
                elif settings_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "settings"
                    new_boundary_mode, new_theme = show_settings_menu(boundary_mode, theme)
                    return None, new_boundary_mode, new_theme, total_coins
                elif exit_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "exit"
                    show_exit_confirmation(theme)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sounds["click"].play()
                    if selected == "highscores":
                        selected = "start"
                    elif selected == "vault":
                        selected = "highscores"
                    elif selected == "settings":
                        selected = "vault"
                    elif selected == "exit":
                        selected = "settings"
                elif event.key == pygame.K_DOWN:
                    sounds["click"].play()
                    if selected == "start":
                        selected = "highscores"
                    elif selected == "highscores":
                        selected = "vault"
                    elif selected == "vault":
                        selected = "settings"
                    elif selected == "settings":
                        selected = "exit"
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected == "start":
                        return show_difficulty_menu(theme), boundary_mode, theme, total_coins
                    elif selected == "highscores":
                        show_high_scores_menu(high_scores, theme)
                    elif selected == "vault":
                        show_game_vault_menu(theme)
                        # refresh coin display after returning from vault
                        settings = load_settings()
                        total_coins = settings.get("total_coins", total_coins)
                    elif selected == "settings":
                        new_boundary_mode, new_theme = show_settings_menu(boundary_mode, theme)
                        return None, new_boundary_mode, new_theme, total_coins
                    elif selected == "exit":
                        show_exit_confirmation(theme)
        
        pygame.display.update()
        clock.tick(FPS)

def show_difficulty_menu(theme):
    menu = True
    selected = "easy"
    high_scores = load_high_scores()
    
    while menu:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw text first to ensure rects are defined
        easy_rect = draw_text("EASY", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 200, True)
        medium_rect = draw_text("MEDIUM", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 250, True)
        hard_rect = draw_text("HARD", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 300, True)
        back_rect = draw_text("BACK", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 350, True)
        
        # Apply colors based on hover or selection
        easy_color = GREEN if easy_rect.collidepoint(mouse_pos) or selected == "easy" else THEMES[theme]["text"]
        medium_color = YELLOW if medium_rect.collidepoint(mouse_pos) or selected == "medium" else THEMES[theme]["text"]
        hard_color = RED if hard_rect.collidepoint(mouse_pos) or selected == "hard" else THEMES[theme]["text"]
        back_color = CYAN if back_rect.collidepoint(mouse_pos) or selected == "back" else THEMES[theme]["text"]
        
        draw_text("SELECT DIFFICULTY", font_large, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 100, True)
        draw_text("EASY", font_medium, easy_color, screen, SCREEN_WIDTH // 2, 200, True)
        draw_text("MEDIUM", font_medium, medium_color, screen, SCREEN_WIDTH // 2, 250, True)
        draw_text("HARD", font_medium, hard_color, screen, SCREEN_WIDTH // 2, 300, True)
        draw_text("BACK", font_medium, back_color, screen, SCREEN_WIDTH // 2, 350, True)
        
        if easy_rect.collidepoint(mouse_pos) or selected == "easy":
            draw_text("Slow speed, good for beginners", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
            draw_text(f"High Score: {high_scores['easy']}", font_small, GREEN, screen, SCREEN_WIDTH // 2, 430, True)
        elif medium_rect.collidepoint(mouse_pos) or selected == "medium":
            draw_text("Moderate speed, balanced challenge", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
            draw_text(f"High Score: {high_scores['medium']}", font_small, YELLOW, screen, SCREEN_WIDTH // 2, 430, True)
        elif hard_rect.collidepoint(mouse_pos) or selected == "hard":
            draw_text("Fast speed, for expert players", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
            draw_text(f"High Score: {high_scores['hard']}", font_small, RED, screen, SCREEN_WIDTH // 2, 430, True)
        elif back_rect.collidepoint(mouse_pos) or selected == "back":
            draw_text("Return to main menu", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        
        draw_text("Use UP/DOWN arrows to select, ENTER or click to confirm", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 500, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if easy_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return "easy"
                elif medium_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return "medium"
                elif hard_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return "hard"
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sounds["click"].play()
                    if selected == "medium":
                        selected = "easy"
                    elif selected == "hard":
                        selected = "medium"
                    elif selected == "back":
                        selected = "hard"
                elif event.key == pygame.K_DOWN:
                    sounds["click"].play()
                    if selected == "easy":
                        selected = "medium"
                    elif selected == "medium":
                        selected = "hard"
                    elif selected == "hard":
                        selected = "back"
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected in ["easy", "medium", "hard"]:
                        return selected
                    elif selected == "back":
                        return None
        
        pygame.display.update()
        clock.tick(FPS)

def show_settings_menu(boundary_mode, current_theme):
    settings = True
    selected = "theme"
    temp_boundary_mode = boundary_mode
    temp_theme = current_theme
    theme_options = list(THEMES.keys())
    theme_index = theme_options.index(current_theme)
    
    while settings:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[temp_theme]["background"])
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw text first to ensure rects are defined
        theme_rect = draw_text("THEME: " + temp_theme, font_medium, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 180, True)
        boundary_text = "ON" if temp_boundary_mode else "OFF"
        boundary_rect = draw_text("BOUNDARY: " + boundary_text, font_medium, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 230, True)
        apply_rect = draw_text("APPLY", font_medium, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 280, True)
        back_rect = draw_text("BACK", font_medium, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 330, True)
        
        # Apply colors based on hover or selection
        theme_color = GREEN if theme_rect.collidepoint(mouse_pos) or selected == "theme" else THEMES[temp_theme]["text"]
        boundary_color = YELLOW if boundary_rect.collidepoint(mouse_pos) or selected == "boundary" else THEMES[temp_theme]["text"]
        apply_color = CYAN if apply_rect.collidepoint(mouse_pos) or selected == "apply" else THEMES[temp_theme]["text"]
        back_color = RED if back_rect.collidepoint(mouse_pos) or selected == "back" else THEMES[temp_theme]["text"]
        
        draw_text("SETTINGS", font_large, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 80, True)
        draw_text("THEME: " + temp_theme, font_medium, theme_color, screen, SCREEN_WIDTH // 2, 180, True)
        draw_text("BOUNDARY: " + boundary_text, font_medium, boundary_color, screen, SCREEN_WIDTH // 2, 230, True)
        draw_text("APPLY", font_medium, apply_color, screen, SCREEN_WIDTH // 2, 280, True)
        draw_text("BACK", font_medium, back_color, screen, SCREEN_WIDTH // 2, 330, True)
        
        if theme_rect.collidepoint(mouse_pos) or selected == "theme":
            draw_text("Change the visual theme of the game", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
            draw_text("Use LEFT/RIGHT or click to change theme", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 430, True)
        elif boundary_rect.collidepoint(mouse_pos) or selected == "boundary":
            draw_text("Toggle wall collisions (ON=Game Over when hit walls)", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
            draw_text("Press ENTER or click to toggle boundary mode", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 430, True)
        elif apply_rect.collidepoint(mouse_pos) or selected == "apply":
            draw_text("Apply and save current settings", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        elif back_rect.collidepoint(mouse_pos) or selected == "back":
            draw_text("Return to main menu without saving", font_small, THEMES[temp_theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if theme_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "theme"
                    theme_index = (theme_index + 1) % len(theme_options)
                    temp_theme = theme_options[theme_index]
                elif boundary_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    selected = "boundary"
                    temp_boundary_mode = not temp_boundary_mode
                elif apply_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return temp_boundary_mode, temp_theme
                elif back_rect.collidepoint(mouse_pos):
                    sounds["click"].play()
                    return boundary_mode, current_theme
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sounds["click"].play()
                    if selected == "boundary":
                        selected = "theme"
                    elif selected == "apply":
                        selected = "boundary"
                    elif selected == "back":
                        selected = "apply"
                elif event.key == pygame.K_DOWN:
                    sounds["click"].play()
                    if selected == "theme":
                        selected = "boundary"
                    elif selected == "boundary":
                        selected = "apply"
                    elif selected == "apply":
                        selected = "back"
                elif event.key == pygame.K_LEFT and selected == "theme":
                    sounds["click"].play()
                    theme_index = (theme_index - 1) % len(theme_options)
                    temp_theme = theme_options[theme_index]
                elif event.key == pygame.K_RIGHT and selected == "theme":
                    sounds["click"].play()
                    theme_index = (theme_index + 1) % len(theme_options)
                    temp_theme = theme_options[theme_index]
                elif event.key == pygame.K_RETURN:
                    sounds["click"].play()
                    if selected == "boundary":
                        temp_boundary_mode = not temp_boundary_mode
                    elif selected == "apply":
                        return temp_boundary_mode, temp_theme
                    elif selected == "back":
                        return boundary_mode, current_theme
        
        pygame.display.update()
        clock.tick(FPS)

def show_high_scores_menu(high_scores, theme):
    viewing = True
    
    while viewing:
        if menu_bg_img:
            screen.blit(menu_bg_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
        
        draw_text("HIGH SCORES", font_large, GOLD, screen, SCREEN_WIDTH // 2, 100, True)
        
        draw_text(f"EASY: {high_scores['easy']}", font_medium, GREEN, screen, SCREEN_WIDTH // 2, 200, True)
        draw_text(f"MEDIUM: {high_scores['medium']}", font_medium, YELLOW, screen, SCREEN_WIDTH // 2, 250, True)
        draw_text(f"HARD: {high_scores['hard']}", font_medium, RED, screen, SCREEN_WIDTH // 2, 300, True)
        
        draw_text("Press any key or click to return", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, 400, True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                sounds["click"].play()
                viewing = False
        
        pygame.display.update()
        clock.tick(FPS)

def game_loop(difficulty, boundary_mode=True, theme="Classic", total_coins=0):
    vault_settings = load_vault_settings()
    snake = Snake(theme, vault_settings["snake_skin"])
    food = Food(theme, vault_settings)
    coin = Coin()
    if difficulty == "easy":
        snake.speed = SPEED_EASY
    elif difficulty == "medium":
        snake.speed = SPEED_MEDIUM
    else:
        snake.speed = SPEED_HARD
    
    game_over = False
    paused = False
    clock = pygame.time.Clock()
    
    while food.position in snake.positions:
        food.spawn_food()
    
    show_countdown(theme, vault_settings)
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_ESCAPE:
                    paused = True
                    if show_pause_menu(theme, snake, food, coin, boundary_mode, vault_settings):
                        paused = False
                    else:
                        game_over = True
                        sounds["game_over"].play()
                        pygame.mixer.Sound.stop(sounds["bonus_timer"])
        
        if paused:
            continue
            
        collision = snake.update(boundary_mode, food, coin)
        
        if snake.is_colliding:
            if time.time() - snake.collision_time >= 2:
                sounds["game_over"].play()
                game_over = True
                break
        
        head = snake.get_head_position()
        if head == food.position and not snake.is_colliding:
            if food.type == "normal":
                sounds["simple_food"].play()
                snake.score += 5
                snake.length += 2
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (255, 50, 50, 150), 15)
            elif food.type == "bonus":
                sounds["bonus_food"].play()
                snake.score += 15
                snake.length += 3
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (255, 255, 0, 150), 25)
            elif food.type == "special":
                sounds["bonus_food"].play()
                snake.score += 30
                snake.length += 5
                snake.special_food_active = True
                snake.special_food_timer = time.time()
                snake.bonus_sound_playing = False
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (255, 215, 0, 200), 35)
            elif food.type == "magnus":
                sounds["magnet_effect"].play()
                snake.score += 20
                snake.length += 4
                snake.magnus_effect_active = True
                snake.magnus_timer = time.time()
                sounds["m_effect"].play()
                sounds["bonus_timer"].play(loops=-1)
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (0, 0, 255, 200), 30)
            elif food.type == "shield":
                sounds["s_effect"].play()
                snake.score += 25
                snake.length += 4
                snake.shield_active = True
                snake.shield_count = 1
                snake.shield_timer = time.time()
                sounds["bonus_timer"].play(loops=-1)
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (0, 255, 255, 200), 30)
            elif food.type == "poison":
                sounds["poison_food"].play()
                snake.score = max(0, snake.score - 15)
                snake.length = max(1, snake.length - 3)
                for _ in range(3):
                    if len(snake.positions) > 1:
                        snake.positions.pop()
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (128, 0, 128, 200), 30)
            elif food.type == "speed":
                sounds["s_effect"].play()
                snake.score += 20
                snake.length += 3
                snake.speed_boost_active = True
                snake.speed_boost_timer = time.time()
                sounds["bonus_timer"].play(loops=-1)
                center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
                center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
                snake.particle_system.add_particles(center_x, center_y, (255, 0, 255, 200), 30)
            
            food.spawn_food()
            while food.position in snake.positions:
                food.spawn_food()
        
        if coin.active and head == coin.position:
            sounds["coin"].play()
            snake.coins_collected += 1
            coin.active = False
            center_x = head[0] * GRID_SIZE + GRID_SIZE // 2
            center_y = head[1] * GRID_SIZE + GRID_SIZE // 2
            snake.particle_system.add_particles(center_x, center_y, (255, 215, 0, 200), 20)
        
        if not coin.active and random.random() < 0.01:
            coin.spawn(snake.positions)
        
        if snake.special_food_active:
            time_left = 10 - (time.time() - snake.special_food_timer)
            if time_left <= 0:
                snake.special_food_active = False
                snake.bonus_sound_playing = False
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
            elif not snake.bonus_sound_playing:
                sounds["bonus_timer"].play(loops=-1)
                snake.bonus_sound_playing = True
        
        if snake.magnus_effect_active:
            time_left = 10 - (time.time() - snake.magnus_timer)
            if time_left <= 0:
                snake.magnus_effect_active = False
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
        
        if snake.shield_active:
            time_left = 10 - (time.time() - snake.shield_timer)
            if time_left <= 0:
                snake.shield_active = False
                snake.shield_count = 0
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
        
        if snake.speed_boost_active:
            time_left = 10 - (time.time() - snake.speed_boost_timer)
            if time_left <= 0:
                snake.speed_boost_active = False
                pygame.mixer.Sound.stop(sounds["bonus_timer"])
        
        # Use selected background
        bg_num = vault_settings.get("background_skin", 1)
        if bg_num in background_skins and background_skins[bg_num]:
            screen.blit(background_skins[bg_num], (0, 0))
        elif background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(THEMES[theme]["background"])
            
        if background_alpha:
            screen.blit(background_alpha, (0, 0))
        
        if boundary_mode:
            pygame.draw.rect(screen, THEMES[theme]["boundary"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)
        
        snake.render(screen, theme)
        if not snake.is_colliding:
            food.render(screen)
            if coin.active:
                coin.render(screen)
        
        score_text = f"Score: {snake.score}"
        if snake.special_food_active:
            score_text += " (2x BONUS!)"
            time_left = 10 - (time.time() - snake.special_food_timer)
            pygame.draw.rect(screen, GOLD, (10, 40, 200 * (time_left / 10), 10))
        
        if snake.magnus_effect_active:
            score_text += " (MAGNUS!)"
            time_left = 10 - (time.time() - snake.magnus_timer)
            pygame.draw.rect(screen, BLUE, (10, 40 if not snake.special_food_active else 55, 
                            200 * (time_left / 10), 10))
        
        if snake.shield_active:
            score_text += f" (SHIELD: {snake.shield_count})"
            time_left = 10 - (time.time() - snake.shield_timer)
            pygame.draw.rect(screen, CYAN, (10, 40 if not (snake.special_food_active or snake.magnus_effect_active) else 
                            (55 if snake.special_food_active or snake.magnus_effect_active else 70), 
                            200 * (time_left / 10), 10))
        
        if snake.speed_boost_active:
            score_text += " (SPEED!)"
            time_left = 10 - (time.time() - snake.speed_boost_timer)
            pygame.draw.rect(screen, PURPLE, (10, 40 if not (snake.special_food_active or snake.magnus_effect_active or snake.shield_active) else 
                            (55 if snake.special_food_active or snake.magnus_effect_active or snake.shield_active else 70), 
                            200 * (time_left / 10), 10))
        
        draw_text(score_text, font_small, THEMES[theme]["text"], screen, 10, 10)
        if coin_img_menu:
            screen.blit(coin_img_menu, (SCREEN_WIDTH - 100, 10))
            coin_text = font_coin.render(f": {snake.coins_collected}", True, GOLD)
            coin_text_rect = coin_text.get_rect(topleft=(SCREEN_WIDTH - 70, 10 + (30 - coin_text.get_height()) // 2))
            screen.blit(coin_text, coin_text_rect)
        
        pygame.display.update()
        clock.tick(snake.speed * (1.5 if snake.speed_boost_active else 1.0))
    
    total_coins += snake.coins_collected
    high_scores = load_high_scores()
    if snake.score > high_scores[difficulty]:
        high_scores[difficulty] = snake.score
        save_high_scores(high_scores)
    
    # Use selected background for game over screen
    bg_num = vault_settings.get("background_skin", 1)
    if bg_num in background_skins and background_skins[bg_num]:
        screen.blit(background_skins[bg_num], (0, 0))
    elif background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(THEMES[theme]["background"])
        
    if background_alpha:
        screen.blit(background_alpha, (0, 0))
    
    draw_text("GAME OVER", font_large, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, True)
    draw_text(f"Final Score: {snake.score}", font_medium, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, True)
    draw_text(f"High Score: {high_scores[difficulty]}", font_medium, GOLD, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, True)
    draw_text(f"Coins Collected: {snake.coins_collected}", font_medium, GOLD, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, True)
    draw_text("Press any key to return to menu", font_small, THEMES[theme]["text"], screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, True)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                sounds["click"].play()
                waiting = False
                return total_coins
        clock.tick(FPS)

def main():
    # Load all images and skins
    load_images()
    load_skin_images()
    
    settings = load_settings()
    boundary_mode = settings["boundary_mode"]
    theme = settings["theme"]
    total_coins = settings.get("total_coins", 0)
    
    show_intro()
    while True:
        result, new_boundary_mode, new_theme, new_total_coins = show_main_menu(boundary_mode, theme, total_coins)
        
        if new_boundary_mode is not None:
            boundary_mode = new_boundary_mode
            theme = new_theme
            total_coins = new_total_coins
        
        if result in ["easy", "medium", "hard"]:
            total_coins = game_loop(result, boundary_mode, theme, total_coins)
            save_settings(boundary_mode, theme, total_coins)

if __name__ == "__main__":
    clock = pygame.time.Clock()
    main()
