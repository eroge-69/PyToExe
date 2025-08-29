import pygame
import sys
import math
import random
import pygame.mixer
import sys
import os

# Handle bundled resources when compiled
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
else:
    # Running as normal script
    base_path = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    return os.path.join(base_path, relative_path)

# Initialize pygame
pygame.init()
pygame.mixer.init()

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Sound effects
# Sound effects
shoot_sounds = []
hit_sound = None
wave_sound = None
sound_available = False

try:
    # Load shoot sounds
    for i in range(1, 6):
        try:
            sound_path = resource_path(f"laserShoot ({i}).wav")
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(0.5)
            shoot_sounds.append(sound)
            print(f"Loaded sound: {sound_path}")  # Debug
        except Exception as e:
            print(f"Warning: Could not load laserShoot ({i}).wav: {e}")

    # Load hit sound
    try:
        sound_path = resource_path("hitHurt (5).wav")
        hit_sound = pygame.mixer.Sound(sound_path)
        hit_sound.set_volume(0.5)
        print(f"Loaded sound: {sound_path}")  # Debug
    except Exception as e:
        print(f"Warning: Could not load hitHurt (5).wav: {e}")

    # Load wave change sound
    try:
        sound_path = resource_path("synth (2).wav")
        wave_sound = pygame.mixer.Sound(sound_path)
        wave_sound.set_volume(0.5)
        print(f"Loaded sound: {sound_path}")  # Debug
    except Exception as e:
        print(f"Warning: Could not load synth (2).wav: {e}")

    # Load background music
    try:
        sound_path = resource_path("Dyson Sphere – Soundtrack (2018).wav")
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(0.25)
        print(f"Loaded music: {sound_path}")  # Debug
    except Exception as e:
        print(f"Warning: Could not load background music: {e}")

    # Only mark sound as available if at least some sounds loaded
    if shoot_sounds or hit_sound or wave_sound:
        sound_available = True
        print("Sound system initialized successfully")
    else:
        print("No sound files could be loaded")

except Exception as e:
    print(f"Error initializing sound system: {e}")
# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hydrocarbon Defender")

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
POWDER_BLUE = (176, 224, 230)
CARBON_GRAY = (80, 80, 80)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)


# Game state
class GameState:
    def __init__(self):
        self.running = False
        self.score = 0
        self.wave = 1
        self.health = 100
        self.current_weapon = 'combustion'
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.wave_start_time = 0
        self.enemies_spawned = 0
        self.wave_in_progress = False
        self.wave_duration = 32000  # 30 seconds per wave
        self.last_spawn_time = 0
        self.last_shot_time = 0
        self.shot_cooldown = 140  # 7 shots per second limit (1000ms/7 ≈ 140ms)
        self.wave_transition = False
        self.wave_transition_start = 0
        self.wave_transition_duration = 1500  # 1.5 seconds
        self.wave_time_remaining = 0
        self.show_countdown = False
        self.countdown_delay = 2000  # 2 seconds delay before showing countdown
        self.developer_mode = False
        self.konami_index = 0  # Tracks progress through Konami code
        self.konami_code = [
            pygame.K_UP, pygame.K_UP,
            pygame.K_DOWN, pygame.K_DOWN,
            pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_b, pygame.K_a
        ]
        self.last_key_time = 0  # To reset code if too much time passes


game_state = GameState()

# Hydrocarbon definitions
hydrocarbons = {
    'methane': {'formula': 'CH4', 'carbons': 1, 'bonds': 'single', 'color': WHITE, 'speed': 0.6, 'health': 1},
    'ethane': {'formula': 'C2H6', 'carbons': 2, 'bonds': 'single', 'color': WHITE, 'speed': 0.7, 'health': 1},
    'propane': {'formula': 'C3H8', 'carbons': 3, 'bonds': 'single', 'color': WHITE, 'speed': 0.8, 'health': 2},
    'butane': {'formula': 'C4H10', 'carbons': 4, 'bonds': 'single', 'color': WHITE, 'speed': 0.7, 'health': 2},
    'pentane': {'formula': 'C5H12', 'carbons': 5, 'bonds': 'single', 'color': WHITE, 'speed': 0.9, 'health': 3},
    'ethene': {'formula': 'C2H4', 'carbons': 2, 'bonds': 'double', 'color': YELLOW, 'speed': 1, 'health': 2},
    'ethyne': {'formula': 'C2H2', 'carbons': 2, 'bonds': 'triple', 'color': PURPLE, 'speed': 1.1, 'health': 3},
    'propene': {'formula': 'C3H4', 'carbons': 3, 'bonds': 'double', 'color': YELLOW, 'speed': 0.9, 'health': 2},
    'propyne': {'formula': 'C3H4', 'carbons': 3, 'bonds': 'triple', 'color': PURPLE, 'speed': 1, 'health': 3},
}

# Weapon effectiveness
weapon_effectiveness = {
    'combustion': {'methane', 'ethane'},
    'cracking': {'propane', 'butane', 'pentane', 'propene'},
    'hydrogenation': {'ethene', 'ethyne', 'propene', 'propyne'}
}


# Enemy class
class Enemy:
    def __init__(self, enemy_type, x, y):
        self.type = enemy_type
        self.data = hydrocarbons[enemy_type]
        self.x = x
        self.y = y
        self.health = self.data['health']
        self.max_health = self.data['health']
        self.speed = self.data['speed']  # Already reduced by 25% in the definitions
        self.radius = 25 + self.data['carbons'] * 3
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_speed = 0.02
        self.bond_length = 20

    def update(self):
        # Move toward center
        center_x, center_y = WIDTH / 2, HEIGHT / 2
        dx = center_x - self.x
        dy = center_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

        self.angle += self.rotation_speed

    def draw(self):
        # Draw molecular structure based on type
        self.draw_molecular_structure()

        # Draw formula below
        font = pygame.font.SysFont('Arial', 14)
        text = font.render(self.data['formula'], True, WHITE)
        screen.blit(text, (self.x - text.get_width() // 2, self.y + self.radius + 5))

    def draw_molecular_structure(self):
        carbon_radius = 8
        hydrogen_radius = 5

        if self.type == 'methane':
            # Central carbon
            pygame.draw.circle(screen, CARBON_GRAY, (self.x, self.y), carbon_radius)

            # 4 hydrogens around it
            for i in range(4):
                angle = (i * 2 * math.pi) / 4
                hx = self.x + math.cos(angle) * self.bond_length
                hy = self.y + math.sin(angle) * self.bond_length

                # Bond line
                pygame.draw.line(screen, LIGHT_GRAY, (self.x, self.y), (hx, hy), 2)

                # Hydrogen
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type == 'ethane':
            # Two carbons
            cx1 = self.x - self.bond_length / 2
            cx2 = self.x + self.bond_length / 2
            pygame.draw.circle(screen, CARBON_GRAY, (cx1, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx2, self.y), carbon_radius)

            # C-C bond
            pygame.draw.line(screen, LIGHT_GRAY, (cx1 + carbon_radius, self.y), (cx2 - carbon_radius, self.y), 3)

            # Hydrogens - fixed to be horizontal instead of diagonal
            h_positions = [
                (cx1 - self.bond_length, self.y),  # Left
                (cx1, self.y - self.bond_length),  # Top
                (cx1, self.y + self.bond_length),  # Bottom
                (cx2 + self.bond_length, self.y),  # Right
                (cx2, self.y - self.bond_length),  # Top
                (cx2, self.y + self.bond_length),  # Bottom
            ]

            for hx, hy in h_positions:
                carbon_x = cx1 if hx <= self.x else cx2
                pygame.draw.line(screen, LIGHT_GRAY, (carbon_x, self.y), (hx, hy), 2)
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type in ['propane', 'butane', 'pentane']:
            # Chain of carbons
            chain_length = self.data['carbons']
            spacing = self.bond_length
            start_x = self.x - (chain_length - 1) * spacing / 2

            # Draw carbons and bonds
            for i in range(chain_length):
                cx = start_x + i * spacing
                pygame.draw.circle(screen, CARBON_GRAY, (cx, self.y), carbon_radius)

                # Bond to next carbon
                if i < chain_length - 1:
                    pygame.draw.line(screen, LIGHT_GRAY, (cx + carbon_radius, self.y),
                                     (cx + spacing - carbon_radius, self.y), 3)

            # Add hydrogens
            for i in range(chain_length):
                cx = start_x + i * spacing

                if i == 0:  # First carbon
                    h_positions = [
                        (cx - self.bond_length, self.y),  # Left
                        (cx, self.y - self.bond_length),  # Top
                        (cx, self.y + self.bond_length),  # Bottom
                    ]
                elif i == chain_length - 1:  # Last carbon
                    h_positions = [
                        (cx + self.bond_length, self.y),  # Right
                        (cx, self.y - self.bond_length),  # Top
                        (cx, self.y + self.bond_length),  # Bottom
                    ]
                else:  # Middle carbons
                    h_positions = [
                        (cx, self.y - self.bond_length),  # Top
                        (cx, self.y + self.bond_length),  # Bottom
                    ]

                for hx, hy in h_positions:
                    pygame.draw.line(screen, LIGHT_GRAY, (cx, self.y), (hx, hy), 2)
                    pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type == 'ethene':
            # Two carbons with double bond
            cx1 = self.x - self.bond_length / 2
            cx2 = self.x + self.bond_length / 2
            pygame.draw.circle(screen, CARBON_GRAY, (cx1, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx2, self.y), carbon_radius)

            # Double bond
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y - 3),
                             (cx2 - carbon_radius, self.y - 3), 4)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y + 3),
                             (cx2 - carbon_radius, self.y + 3), 4)

            # Hydrogens
            h_positions = [
                (cx1, self.y - self.bond_length),  # Top left
                (cx1, self.y + self.bond_length),  # Bottom left
                (cx2, self.y - self.bond_length),  # Top right
                (cx2, self.y + self.bond_length),  # Bottom right
            ]

            for hx, hy in h_positions:
                carbon_x = cx1 if hx <= self.x else cx2
                pygame.draw.line(screen, LIGHT_GRAY, (carbon_x, self.y), (hx, hy), 2)
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type == 'ethyne':
            # Two carbons with triple bond
            cx1 = self.x - self.bond_length / 2
            cx2 = self.x + self.bond_length / 2
            pygame.draw.circle(screen, CARBON_GRAY, (cx1, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx2, self.y), carbon_radius)

            # Triple bond
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y - 4),
                             (cx2 - carbon_radius, self.y - 4), 3)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y),
                             (cx2 - carbon_radius, self.y), 3)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y + 4),
                             (cx2 - carbon_radius, self.y + 4), 3)

            # Hydrogens
            h_positions = [
                (cx1 - self.bond_length, self.y),  # Left
                (cx2 + self.bond_length, self.y),  # Right
            ]

            for i, (hx, hy) in enumerate(h_positions):
                carbon_x = cx1 if i == 0 else cx2
                pygame.draw.line(screen, LIGHT_GRAY, (carbon_x, self.y), (hx, hy), 2)
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type == 'propene':
            # Three carbons with double bond between first two
            spacing = self.bond_length
            cx1 = self.x - spacing
            cx2 = self.x
            cx3 = self.x + spacing
            pygame.draw.circle(screen, CARBON_GRAY, (cx1, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx2, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx3, self.y), carbon_radius)

            # Double bond between first two carbons
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y - 3),
                             (cx2 - carbon_radius, self.y - 3), 4)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y + 3),
                             (cx2 - carbon_radius, self.y + 3), 4)

            # Single bond between second and third carbons
            pygame.draw.line(screen, LIGHT_GRAY, (cx2 + carbon_radius, self.y),
                             (cx3 - carbon_radius, self.y), 3)

            # Hydrogens
            h_positions = [
                (cx1, self.y - self.bond_length),  # Top left
                (cx1, self.y + self.bond_length),  # Bottom left
                (cx1 - self.bond_length, self.y),  # Left of first carbon
                (cx2, self.y - self.bond_length),  # Top middle
                (cx2, self.y + self.bond_length),  # Bottom middle
                (cx3, self.y - self.bond_length),  # Top right
                (cx3, self.y + self.bond_length),  # Bottom right
                (cx3 + self.bond_length, self.y),  # Right of third carbon
            ]

            # Draw bonds to hydrogens
            carbon_positions = [(cx1, self.y), (cx1, self.y), (cx1, self.y),
                                (cx2, self.y), (cx2, self.y),
                                (cx3, self.y), (cx3, self.y), (cx3, self.y)]

            for i, ((hx, hy), (cx, cy)) in enumerate(zip(h_positions, carbon_positions)):
                pygame.draw.line(screen, LIGHT_GRAY, (cx, cy), (hx, hy), 2)
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

        elif self.type == 'propyne':
            # Three carbons with triple bond between first two
            spacing = self.bond_length
            cx1 = self.x - spacing
            cx2 = self.x
            cx3 = self.x + spacing
            pygame.draw.circle(screen, CARBON_GRAY, (cx1, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx2, self.y), carbon_radius)
            pygame.draw.circle(screen, CARBON_GRAY, (cx3, self.y), carbon_radius)

            # Triple bond between first two carbons
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y - 4),
                             (cx2 - carbon_radius, self.y - 4), 3)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y),
                             (cx2 - carbon_radius, self.y), 3)
            pygame.draw.line(screen, self.data['color'], (cx1 + carbon_radius, self.y + 4),
                             (cx2 - carbon_radius, self.y + 4), 3)

            # Single bond between second and third carbons
            pygame.draw.line(screen, LIGHT_GRAY, (cx2 + carbon_radius, self.y),
                             (cx3 - carbon_radius, self.y), 3)

            # Hydrogens
            h_positions = [
                (cx1 - self.bond_length, self.y),  # Left of first carbon
                (cx2, self.y - self.bond_length),  # Top middle
                (cx2, self.y + self.bond_length),  # Bottom middle
                (cx3, self.y - self.bond_length),  # Top right
                (cx3, self.y + self.bond_length),  # Bottom right
                (cx3 + self.bond_length, self.y),  # Right of third carbon
            ]

            # Draw bonds to hydrogens
            carbon_positions = [(cx1, self.y), (cx2, self.y), (cx2, self.y),
                                (cx3, self.y), (cx3, self.y), (cx3, self.y)]

            for i, ((hx, hy), (cx, cy)) in enumerate(zip(h_positions, carbon_positions)):
                pygame.draw.line(screen, LIGHT_GRAY, (cx, cy), (hx, hy), 2)
                pygame.draw.circle(screen, POWDER_BLUE, (hx, hy), hydrogen_radius)

    def take_damage(self, weapon_type):
        if weapon_type in weapon_effectiveness and self.type in weapon_effectiveness[weapon_type]:
            # Correct weapon type - destroy the enemy
            self.health = 0

            # Handle special effects based on weapon type
            if weapon_type == 'cracking':
                splits = []
                if self.type == 'propane':
                    splits = ['methane', 'ethane']
                elif self.type == 'butane':
                    splits = ['ethane', 'ethane']
                elif self.type == 'pentane':
                    splits = ['propane', 'ethane']
                elif self.type == 'propene':
                    splits = ['ethene', 'methane']
                return {'destroyed': True, 'splits': splits}

            elif weapon_type == 'hydrogenation':
                if self.data['bonds'] == 'double':
                    # Convert to alkane
                    if self.data['carbons'] == 2:
                        return {'destroyed': True, 'converts': 'ethane'}
                    else:
                        return {'destroyed': True, 'converts': 'propane'}
                elif self.data['bonds'] == 'triple':
                    # Convert to alkene
                    if self.data['carbons'] == 2:
                        return {'destroyed': True, 'converts': 'ethene'}
                    else:
                        return {'destroyed': True, 'converts': 'propene'}

            # For combustion, just destroy
            return {'destroyed': True, 'splits': []}
        else:
            # Wrong weapon type - no effect
            return {'destroyed': False, 'splits': []}


# Bullet class
class Bullet:
    def __init__(self, x, y, target_x, target_y, bullet_type):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.speed = 12

        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)

        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed

        self.colors = {
            'combustion': RED,
            'cracking': GREEN,
            'hydrogenation': BLUE
        }

        self.trail = []

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Add current position to trail
        self.trail.append((self.x, self.y))
        # Keep trail length limited
        if len(self.trail) > 10:
            self.trail.pop(0)

        return (self.x < 0 or self.x > WIDTH or
                self.y < 0 or self.y > HEIGHT)

    def draw(self):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = i / len(self.trail) * 150
            trail_color = (*self.colors[self.type][:3], int(alpha))
            pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), 3)

        # Draw bullet
        pygame.draw.circle(screen, self.colors[self.type], (int(self.x), int(self.y)), 5)

        # Add glow effect
        pygame.draw.circle(screen, self.colors[self.type], (int(self.x), int(self.y)), 8, 2)

    def check_collision(self, enemy):
        dx = self.x - enemy.x
        dy = self.y - enemy.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < enemy.radius + 5


# Particle effect class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = 30

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size *= 0.95
        return self.lifetime <= 0

    def draw(self):
        alpha = min(255, self.lifetime * 8)
        pygame.draw.circle(screen, (*self.color[:3], alpha), (int(self.x), int(self.y)), int(self.size))


# Draw wave transition animation
def draw_wave_transition():
    if not game_state.wave_transition:
        return

    elapsed = pygame.time.get_ticks() - game_state.wave_transition_start
    progress = min(1.0, elapsed / game_state.wave_transition_duration)

    # Calculate alpha (fade in and out)
    if progress < 0.3:  # Fade in
        alpha = int(255 * (progress / 0.3))
    elif progress < 0.7:  # Stay visible
        alpha = 255
    else:  # Fade out
        alpha = int(255 * (1.0 - (progress - 0.7) / 0.3))

    # Create text surface
    font = pygame.font.SysFont('Arial', 144, bold=True)
    text = font.render(f"WAVE {game_state.wave}", True, WHITE)

    # Set alpha
    text.set_alpha(alpha)

    # Draw centered with a slight shadow for better visibility
    shadow_text = font.render(f"WAVE {game_state.wave}", True, BLACK)
    screen.blit(shadow_text, (WIDTH // 2 - text.get_width() // 2 + 2, HEIGHT // 4 - text.get_height() // 2 + 2))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4 - text.get_height() // 2))

    # Check if transition is complete
    if progress >= 1.0:
        game_state.wave_transition = False

# Spawn enemies for the current wave
def spawn_enemies():
    if game_state.wave_in_progress:
        return

    wave_types = {
        1: ['methane', 'ethane'],
        2: ['methane', 'ethane', 'propane'],
        3: ['propane', 'butane', 'ethene'],
        4: ['butane', 'pentane', 'ethene', 'ethyne'],
        5: ['pentane', 'ethene', 'ethyne', 'propene', 'propyne']
    }

    types = wave_types.get(min(game_state.wave, 5), wave_types[5])
    total_enemies = 5 + game_state.wave

    # Increase wave duration after wave 5, 10, 15, etc.
    base_duration = 32000  # 30 seconds
    extra_time = (game_state.wave // 5) * 5000  # Add 5 seconds for every 3 waves
    game_state.wave_duration = base_duration + extra_time

    game_state.wave_start_time = pygame.time.get_ticks()
    game_state.wave_time_remaining = game_state.wave_duration
    game_state.enemies_spawned = 0
    game_state.wave_in_progress = True
    game_state.show_countdown = False
    game_state.last_spawn_time = 0

    # Trigger wave transition animation
    game_state.wave_transition = True
    game_state.wave_transition_start = pygame.time.get_ticks()

    # Play wave transition sound for all waves including first
    if sound_available and wave_sound:
        wave_sound.play()

    game_state.wave_start_time = pygame.time.get_ticks()
    game_state.enemies_spawned = 0
    game_state.wave_in_progress = True
    game_state.last_spawn_time = 0


# Draw HUD
def draw_hud():
    font = pygame.font.SysFont('Arial', 24)

    # Score
    score_text = font.render(f"Score: {game_state.score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    # Wave
    wave_text = font.render(f"Wave: {game_state.wave}", True, WHITE)
    screen.blit(wave_text, (20, 50))

    # Health
    health_text = font.render(f"Health: {game_state.health}", True, WHITE)
    screen.blit(health_text, (20, 80))

    # Wave timer (only show if wave is in progress and after 2 seconds for waves > 1)
    if game_state.wave_in_progress and game_state.show_countdown:
        seconds_left = math.ceil(game_state.wave_time_remaining / 1000)
        timer_font = pygame.font.SysFont('Arial', 36, bold=True)
        timer_text = timer_font.render(f"{seconds_left}", True, WHITE)

        # Draw with shadow for better visibility
        shadow_text = timer_font.render(f"{seconds_left}", True, BLACK)
        screen.blit(shadow_text, (WIDTH // 2 - timer_text.get_width() // 2 + 2, 22))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 20))

    # Weapon selection - minimized UI
    weapons_y = HEIGHT - 40
    weapons = [
        ('combustion', 'Q', RED),
        ('cracking', 'W', GREEN),
        ('hydrogenation', 'E', BLUE)
    ]

    for i, (weapon_type, weapon_key, color) in enumerate(weapons):
        is_active = game_state.current_weapon == weapon_type
        bg_color = color if is_active else GRAY

        # Draw weapon indicator
        pygame.draw.circle(screen, bg_color, (WIDTH // 2 - 60 + i * 60, weapons_y), 15)

        # Draw key text
        key_font = pygame.font.SysFont('Arial', 16)
        key_text = key_font.render(weapon_key, True, WHITE if is_active else LIGHT_GRAY)
        screen.blit(key_text, (WIDTH // 2 - 60 + i * 60 - key_text.get_width() // 2,
                               weapons_y - key_text.get_height() // 2))


# Draw instructions screen
def draw_instructions():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    font_large = pygame.font.SysFont('Arial', 36)
    font_medium = pygame.font.SysFont('Arial', 24)
    font_small = pygame.font.SysFont('Arial', 18)

    title = font_large.render("Hydrocarbon Defender", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    mission = font_medium.render("Misi: bakar senyawa-senyawa hidrokarbon!", True, WHITE)
    screen.blit(mission, (WIDTH // 2 - mission.get_width() // 2, 160))

    # Instructions
    instructions = [
        "Perluru Pembakaran (Merah): Membakar metana (CH4) and etana (C2H6)",
        "Peluru Thermal Cracking (Hijau): memisah rantai alkana panjang (C3+) menjadi rantai lebih pendek",
        "Peluru Hidrogenisasi (Biru): Memicu reaksi adisi, alkena (kuning) dan alkuna (ungu) menjadi alkana"
    ]

    for i, instruction in enumerate(instructions):
        text = font_small.render(instruction, True, LIGHT_GRAY)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 220 + i * 30))

    hint = font_small.render("Gunakan Q, W, atau E untuk memilih peluru, gunakan peluru yang tepat!", True, POWDER_BLUE)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))

    # Start button
    button_rect = pygame.Rect(WIDTH // 2 - 100, 380, 200, 50)
    pygame.draw.rect(screen, GREEN, button_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=8)

    start_text = font_medium.render("Start Game", True, BLACK)
    screen.blit(start_text, (button_rect.centerx - start_text.get_width() // 2,
                             button_rect.centery - start_text.get_height() // 2))

    return button_rect


# Draw game over screen
def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    font_large = pygame.font.SysFont('Arial', 48)
    font_medium = pygame.font.SysFont('Arial', 28)

    title = font_large.render("Game Over!", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

    score_text = font_medium.render(f"Final Score: {game_state.score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 230))

    wave_text = font_medium.render(f"Waves Completed: {game_state.wave - 1}", True, WHITE)
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 270))

    # Play again button
    button_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 50)
    pygame.draw.rect(screen, GREEN, button_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=8)

    again_text = font_medium.render("Play Again", True, BLACK)
    screen.blit(again_text, (button_rect.centerx - again_text.get_width() // 2,
                             button_rect.centery - again_text.get_height() // 2))

    return button_rect


# Start game function
def start_game():
    game_state.running = True
    game_state.score = 0
    game_state.wave = 1
    game_state.health = 100
    game_state.enemies = []
    game_state.bullets = []
    game_state.particles = []
    game_state.wave_in_progress = False
    game_state.enemies_spawned = 0
    spawn_enemies()

    if sound_available:
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# End game function
def end_game():
    game_state.running = False

    # Fade out background music
    if sound_available:
        pygame.mixer.music.fadeout(2000)  # 2 second fadeout

# Update game state
def update():
    if not game_state.running:
        return

    current_time = pygame.time.get_ticks()

    # Spawn enemies for current wave
    if game_state.wave_in_progress:
        wave_types = {
            1: ['methane', 'ethane'],
            2: ['methane', 'ethane', 'propane'],
            3: ['propane', 'butane', 'ethene'],
            4: ['butane', 'pentane', 'ethene', 'ethyne'],
            5: ['pentane', 'ethene', 'ethyne', 'propene', 'propyne']
        }

        types = wave_types.get(min(game_state.wave, 5), wave_types[5])
        total_enemies = 5 + game_state.wave  # Reduced from 8 + wave*2

        # Check if wave time is up
        if current_time - game_state.wave_start_time > game_state.wave_duration:
            game_state.wave_in_progress = False
            # If wave time is up, clear all enemies
            game_state.enemies = []
        elif (game_state.enemies_spawned < total_enemies and
              current_time - game_state.last_spawn_time > 2000):  # Spawn every 1.5 seconds (slower) spawnrate
            enemy_type = random.choice(types)
            angle = random.uniform(0, 2 * math.pi)
            distance = 500
            x = WIDTH / 2 + math.cos(angle) * distance
            y = HEIGHT / 2 + math.sin(angle) * distance

            game_state.enemies.append(Enemy(enemy_type, x, y))
            game_state.enemies_spawned += 1
            game_state.last_spawn_time = current_time

    # Update enemies
    for enemy in game_state.enemies[:]:
        enemy.update()

        # Check if enemy reached center
        center_x, center_y = WIDTH / 2, HEIGHT / 2
        distance = math.sqrt((enemy.x - center_x) ** 2 + (enemy.y - center_y) ** 2)

        if distance < 50:
            game_state.health -= 10
            game_state.enemies.remove(enemy)

            if game_state.health <= 0:
                end_game()

    # Update bullets
    for bullet in game_state.bullets[:]:
        if bullet.update():
            game_state.bullets.remove(bullet)
            continue

        # Check collisions
        for enemy in game_state.enemies[:]:
            if bullet.check_collision(enemy):
                result = enemy.take_damage(bullet.type)

                # Create particles only if it was the correct weapon
                if result['destroyed']:
                    for _ in range(10):
                        game_state.particles.append(Particle(enemy.x, enemy.y, bullet.colors[bullet.type]))
                    if sound_available:
                        hit_sound.play()

                if bullet in game_state.bullets:
                    game_state.bullets.remove(bullet)

                if result['destroyed']:
                    game_state.score += 10 * enemy.data['carbons']

                    # Handle splits
                    if 'splits' in result and result['splits']:
                        for split_type in result['splits']:
                            offset_x = (random.random() - 0.5) * 60
                            offset_y = (random.random() - 0.5) * 40
                            game_state.enemies.append(Enemy(split_type, enemy.x + offset_x, enemy.y + offset_y))

                    # Handle conversions
                    if 'converts' in result:
                        game_state.enemies.append(Enemy(result['converts'], enemy.x, enemy.y))

                    if enemy in game_state.enemies:
                        game_state.enemies.remove(enemy)

                break

    # Update particles
    for particle in game_state.particles[:]:
        if particle.update():
            game_state.particles.remove(particle)

    # Check if wave completed
    if (not game_state.wave_in_progress and
            len(game_state.enemies) == 0 and
            game_state.enemies_spawned >= (5 + game_state.wave)):
        game_state.wave += 1
        game_state.score += 100
        spawn_enemies()

    # Update wave timer
    if game_state.wave_in_progress:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - game_state.wave_start_time
        game_state.wave_time_remaining = max(0, game_state.wave_duration - elapsed)

        # Show countdown after 2 seconds for all waves
        if elapsed > game_state.countdown_delay:
            game_state.show_countdown = True
        else:
            game_state.show_countdown = False

        # Check if wave time is up
        if game_state.wave_time_remaining <= 0:
            game_state.wave_in_progress = False
            game_state.show_countdown = False
            # Clear all enemies when time is up
            game_state.enemies = []


# Draw everything
def draw():
    # Clear screen with white background
    screen.fill(BLACK)

    # Draw wave transition if activef
    if game_state.wave_transition:
        draw_wave_transition()

    # Draw subtle background pattern
    for i in range(0, WIDTH, 40):
        for j in range(0, HEIGHT, 40):
            alpha = 20
            pygame.draw.circle(screen, (30, 30, 40, alpha), (i, j), 1)

    # Draw center target
    pygame.draw.circle(screen, (0, 100, 0, 100), (WIDTH // 2, HEIGHT // 2), 50, 2)
    pygame.draw.circle(screen, (0, 150, 0, 50), (WIDTH // 2, HEIGHT // 2), 30, 2)
    pygame.draw.circle(screen, (0, 200, 0, 30), (WIDTH // 2, HEIGHT // 2), 10, 2)

    # Draw enemies
    for enemy in game_state.enemies:
        enemy.draw()

    # Draw bullets
    for bullet in game_state.bullets:
        bullet.draw()

    # Draw particles
    for particle in game_state.particles:
        particle.draw()

    # Draw HUD
    draw_hud()

    # Draw instructions or game over screen
    if not game_state.running:
        if game_state.health <= 0:
            button_rect = draw_game_over()
            return button_rect
        else:
            button_rect = draw_instructions()
            return button_rect

    return None


# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        button_rect = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if not game_state.running:
                        # Check if click is on start/restart button
                        if button_rect and button_rect.collidepoint(event.pos):
                            start_game()
                    else:
                        # Check if we can shoot (7 CPS limit)
                        current_time = pygame.time.get_ticks()
                        if current_time - game_state.last_shot_time >= game_state.shot_cooldown:
                            # Shoot bullet toward mouse position
                            target_x, target_y = event.pos
                            bullet = Bullet(WIDTH / 2, HEIGHT / 2, target_x, target_y, game_state.current_weapon)
                            game_state.bullets.append(bullet)
                            game_state.last_shot_time = current_time

                            # Play shoot sound
                            if sound_available:
                                random.choice(shoot_sounds).play()

            if event.type == pygame.KEYDOWN:
                if not game_state.running:
                    if event.key == pygame.K_SPACE:
                        start_game()
                else:
                    if event.key == pygame.K_q:
                        game_state.current_weapon = 'combustion'
                    elif event.key == pygame.K_w:
                        game_state.current_weapon = 'cracking'
                    elif event.key == pygame.K_e:
                        game_state.current_weapon = 'hydrogenation'

                    # Konami code detection
                    current_time = pygame.time.get_ticks()
                    # Reset if too much time has passed since last key
                    if current_time - game_state.last_key_time > 2000:  # 2 seconds
                        game_state.konami_index = 0

                    # Check if the pressed key matches the next in Konami code
                    if event.key == game_state.konami_code[game_state.konami_index]:
                        game_state.konami_index += 1
                        game_state.last_key_time = current_time

                        # If full code entered, toggle developer mode
                        if game_state.konami_index >= len(game_state.konami_code):
                            game_state.developer_mode = not game_state.developer_mode
                            game_state.konami_index = 0  # Reset for next time

                            if game_state.developer_mode:
                                game_state.health = 999999
                                print("Developer mode enabled - Infinite health")
                            else:
                                game_state.health = 100
                                print("Developer mode disabled")
                    else:
                        # Wrong key, reset Konami code progress
                        game_state.konami_index = 0

        update()
        button_rect = draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()