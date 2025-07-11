import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# Lilac color palette with light lilac UI
COLORS = {
    'bg_dark': (35, 25, 45),
    'bg_light': (65, 45, 85),
    'player': (160, 130, 200),
    'player_glow': (210, 180, 255),
    'obstacle': (120, 90, 160),
    'obstacle_glow': (170, 140, 210),
    'ground': (100, 70, 130),
    'white': (255, 255, 255),
    'danger': (210, 130, 180),
    'wave': (190, 150, 230),
    'wave_glow': (230, 200, 255),
    'ui_light_lilac': (200, 180, 230),  # Light lilac for UI
    'ui_glow': (220, 200, 250)         # Lighter glow for UI
}

class Player:
    def __init__(self, x, y, screen_height):
        self.x = x
        self.y = y
        self.screen_height = screen_height
        self.width = 40
        self.height = 40
        self.vel_y = 0
        self.vel_x = 0
        # Adjusted physics for 1 block high, 3 blocks long jump
        self.jump_strength = -12  # Reduced for precise 1-block height
        self.gravity = 0.6  # Adjusted gravity
        self.on_ground = False
        self.on_block = False
        self.rotation = 0
        self.rotation_speed = -10  # Changed to negative for opposite direction
        self.mode = 'cube'  # 'cube', 'plane', or 'wave'
        self.plane_thrust = -0.5
        self.plane_gravity = 0.3
        self.max_vel_y = 10
        
        # Wave mode properties - diagonal movement
        self.wave_speed = 6  # Diagonal speed
        self.wave_vel_x = 0
        self.wave_vel_y = 0
        
    def set_mode(self, mode):
        self.mode = mode
        if mode == 'plane':
            self.y = self.screen_height // 2
            self.vel_y = 0
            self.on_ground = False
            self.on_block = False
        elif mode == 'wave':
            self.y = self.screen_height // 2
            self.vel_y = 0
            self.vel_x = 0
            self.wave_vel_x = 0
            self.wave_vel_y = 0
            self.on_ground = False
            self.on_block = False
        else:  # cube
            self.y = self.screen_height - 100 - self.height
            self.vel_y = 0
            self.vel_x = 0
            
    def update_screen_height(self, screen_height):
        self.screen_height = screen_height
            
    def update(self, thrust_input=False, obstacles=[]):
        if self.mode == 'cube':
            # Cube physics with block collision
            self.vel_y += self.gravity
            self.y += self.vel_y
            
            # Ground collision
            ground_y = self.screen_height - 100 - self.height
            if self.y >= ground_y:
                self.y = ground_y
                self.vel_y = 0
                self.on_ground = True
                self.on_block = False
                self.rotation = 0
            else:
                self.on_ground = False
                
            # Block collision detection
            player_rect = self.get_rect()
            self.on_block = False
            
            for obstacle in obstacles:
                if obstacle.type == 'block' and obstacle.mode == 'cube':
                    obstacle_rect = obstacle.get_rect()
                    
                    # Check if player is landing on top of block
                    if (player_rect.colliderect(obstacle_rect) and 
                        self.vel_y > 0 and 
                        player_rect.bottom - self.vel_y <= obstacle_rect.top + 5):
                        
                        self.y = obstacle_rect.top - self.height
                        self.vel_y = 0
                        self.on_block = True
                        self.rotation = 0
                        break
                        
            # Rotation when jumping
            if not (self.on_ground or self.on_block):
                self.rotation += self.rotation_speed
                
        elif self.mode == 'plane':
            # Plane physics
            if thrust_input:
                self.vel_y += self.plane_thrust
            else:
                self.vel_y += self.plane_gravity
                
            # Limit velocity
            self.vel_y = max(-self.max_vel_y, min(self.max_vel_y, self.vel_y))
            self.y += self.vel_y
            
            # Screen boundaries
            if self.y < 0:
                self.y = 0
                self.vel_y = 0
            elif self.y > self.screen_height - 100 - self.height:
                self.y = self.screen_height - 100 - self.height
                self.vel_y = 0
                
            # Plane rotation based on velocity
            self.rotation = self.vel_y * 3
            
        elif self.mode == 'wave':
            # Wave mode - diagonal movement at 45 degrees
            if thrust_input:
                # Up-right diagonal (45 degrees up)
                self.wave_vel_x = self.wave_speed * math.cos(math.radians(-45))  # Right
                self.wave_vel_y = self.wave_speed * math.sin(math.radians(-45))  # Up
            else:
                # Down-right diagonal (45 degrees down)
                self.wave_vel_x = self.wave_speed * math.cos(math.radians(45))   # Right
                self.wave_vel_y = self.wave_speed * math.sin(math.radians(45))   # Down
                
            # Apply movement
            self.y += self.wave_vel_y
            
            # Screen boundaries
            if self.y < 0:
                self.y = 0
                self.wave_vel_y = abs(self.wave_vel_y)  # Bounce down
            elif self.y > self.screen_height - 100 - self.height:
                self.y = self.screen_height - 100 - self.height
                self.wave_vel_y = -abs(self.wave_vel_y)  # Bounce up
                
            # Wave rotation based on direction
            if thrust_input:
                self.rotation = -45  # Up-right
            else:
                self.rotation = 45   # Down-right
            
    def jump(self):
        if self.mode == 'cube' and (self.on_ground or self.on_block):
            self.vel_y = self.jump_strength
            self.on_ground = False
            self.on_block = False
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        if self.mode == 'cube':
            # Original cube drawing code
            cube_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(cube_surface, COLORS['player'], (0, 0, self.width, self.height))
            pygame.draw.rect(cube_surface, COLORS['player_glow'], (0, 0, self.width, self.height), 3)
            pygame.draw.line(cube_surface, COLORS['player_glow'], (0, 0), (self.width, self.height), 2)
            pygame.draw.line(cube_surface, COLORS['player_glow'], (self.width, 0), (0, self.height), 2)
            
            if not (self.on_ground or self.on_block):
                rotated_surface = pygame.transform.rotate(cube_surface, self.rotation)
                rotated_rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
                screen.blit(rotated_surface, rotated_rect)
            else:
                screen.blit(cube_surface, (self.x, self.y))
                
        elif self.mode == 'plane':
            # Draw airplane
            plane_surface = pygame.Surface((self.width + 20, self.height), pygame.SRCALPHA)
            
            # Main body
            pygame.draw.ellipse(plane_surface, COLORS['player'], (10, 10, self.width, self.height - 20))
            
            # Wings
            pygame.draw.polygon(plane_surface, COLORS['player'], [
                (5, self.height//2), (25, self.height//2 - 15), (35, self.height//2 - 10), (25, self.height//2 + 15)
            ])
            
            # Tail
            pygame.draw.polygon(plane_surface, COLORS['player'], [
                (0, self.height//2 - 5), (15, self.height//2 - 12), (15, self.height//2 + 12), (0, self.height//2 + 5)
            ])
            
            # Glow effect
            pygame.draw.ellipse(plane_surface, COLORS['player_glow'], (10, 10, self.width, self.height - 20), 2)
            
            # Rotate plane based on movement
            rotated_surface = pygame.transform.rotate(plane_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_surface, rotated_rect)
            
        elif self.mode == 'wave':
            # Draw wave as diamond/rhombus shape
            wave_surface = pygame.Surface((self.width + 15, self.height + 15), pygame.SRCALPHA)
            
            center_x = (self.width + 15) // 2
            center_y = (self.height + 15) // 2
            
            # Diamond/rhombus points
            diamond_points = [
                (center_x + 12, center_y),      # Right point
                (center_x, center_y - 12),      # Top point
                (center_x - 12, center_y),      # Left point
                (center_x, center_y + 12),      # Bottom point
            ]
            
            # Draw main diamond shape
            pygame.draw.polygon(wave_surface, COLORS['wave'], diamond_points)
            pygame.draw.polygon(wave_surface, COLORS['wave_glow'], diamond_points, 3)
            
            # Add inner diamond for detail
            inner_points = [
                (center_x + 6, center_y),
                (center_x, center_y - 6),
                (center_x - 6, center_y),
                (center_x, center_y + 6),
            ]
            pygame.draw.polygon(wave_surface, COLORS['wave_glow'], inner_points, 2)
            
            # Add center dot
            pygame.draw.circle(wave_surface, COLORS['wave_glow'], (center_x, center_y), 2)
            
            # Rotate diamond based on movement direction
            rotated_surface = pygame.transform.rotate(wave_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_surface, rotated_rect)

class Obstacle:
    def __init__(self, x, obstacle_type='spike', mode='cube', screen_height=600):
        self.x = x
        self.type = obstacle_type
        self.mode = mode
        self.speed = 8
        self.screen_height = screen_height
        
        if mode == 'cube':
            if obstacle_type == 'spike':
                self.width = 40
                self.height = 60
                self.y = self.screen_height - 100 - self.height
            elif obstacle_type == 'double_spike':
                self.width = 80  # Two spikes side by side
                self.height = 60
                self.y = self.screen_height - 100 - self.height
            elif obstacle_type == 'triple_spike':
                self.width = 120  # Three spikes side by side
                self.height = 60
                self.y = self.screen_height - 100 - self.height
            elif obstacle_type == 'block':
                self.width = 40
                self.height = 40
                self.y = self.screen_height - 100 - self.height
                
        elif mode == 'plane':
            if obstacle_type == 'floating_block':
                self.width = 40
                self.height = 40
                self.y = random.randint(50, self.screen_height - 150)
            elif obstacle_type == 'vertical_bar':
                self.width = 20
                self.height = random.randint(100, 200)
                self.y = random.randint(0, self.screen_height - 100 - self.height)
            elif obstacle_type == 'ring':
                self.width = 60
                self.height = 60
                self.y = random.randint(100, self.screen_height - 200)
            elif obstacle_type == 'ceiling_spike':
                self.width = 40
                self.height = 50
                self.y = 0  # Hangs from ceiling
            elif obstacle_type == 'floating_spike':
                self.width = 35
                self.height = 35
                self.y = random.randint(80, self.screen_height - 180)
            elif obstacle_type == 'double_ring':
                self.width = 80
                self.height = 60
                self.y = random.randint(100, self.screen_height - 200)
            elif obstacle_type == 'narrow_passage':
                self.width = 25
                self.height = random.randint(150, 250)
                self.y = random.randint(50, self.screen_height - 150 - self.height)
            elif obstacle_type == 'moving_block':
                self.width = 35
                self.height = 35
                self.y = self.screen_height // 2
                self.move_amplitude = 60
                self.move_time = 0
                
        elif mode == 'wave':
            if obstacle_type == 'narrow_gap':
                self.width = 20
                self.height = random.randint(80, 120)
                self.y = random.randint(50, self.screen_height - 150 - self.height)
            elif obstacle_type == 'wave_barrier':
                self.width = 15
                self.height = random.randint(60, 100)
                self.y = random.randint(100, self.screen_height - 200)
            elif obstacle_type == 'moving_wall':
                self.width = 25
                self.height = 80
                self.y = self.screen_height // 2 - self.height // 2
                self.move_amplitude = 50
                self.move_time = 0
            elif obstacle_type == 'diagonal_spike':
                self.width = 30
                self.height = 30
                self.y = random.randint(60, self.screen_height - 160)
            elif obstacle_type == 'wave_tunnel':
                self.width = 20
                self.height = random.randint(100, 150)
                self.y = random.randint(40, self.screen_height - 140 - self.height)
            elif obstacle_type == 'pulsing_barrier':
                self.width = 18
                self.height = random.randint(70, 110)
                self.y = random.randint(80, self.screen_height - 180)
                self.pulse_time = 0
                self.base_width = self.width
            elif obstacle_type == 'zigzag_wall':
                self.width = 22
                self.height = 60
                self.y = self.screen_height // 2 - self.height // 2
                self.zigzag_time = 0
                self.zigzag_amplitude = 80
            elif obstacle_type == 'rotating_cross':
                self.width = 40
                self.height = 40
                self.y = random.randint(100, self.screen_height - 200)
                self.rotation = 0
            elif obstacle_type == 'wave_mine':
                self.width = 25
                self.height = 25
                self.y = random.randint(70, self.screen_height - 170)
                self.pulse_time = 0
            
    def update(self):
        self.x -= self.speed
        
        # Special movement for plane mode obstacles
        if self.mode == 'plane' and self.type == 'moving_block':
            self.move_time += 1
            self.y = self.screen_height // 2 + math.sin(self.move_time * 0.1) * self.move_amplitude
        
        # Special movement for wave mode obstacles
        elif self.mode == 'wave':
            if self.type == 'moving_wall':
                self.move_time += 1
                self.y = self.screen_height // 2 - self.height // 2 + math.sin(self.move_time * 0.08) * self.move_amplitude
            elif self.type == 'pulsing_barrier':
                self.pulse_time += 1
                pulse_factor = 1 + 0.3 * math.sin(self.pulse_time * 0.15)
                self.width = int(self.base_width * pulse_factor)
            elif self.type == 'zigzag_wall':
                self.zigzag_time += 1
                self.y = self.screen_height // 2 - self.height // 2 + math.sin(self.zigzag_time * 0.12) * self.zigzag_amplitude
            elif self.type == 'rotating_cross':
                self.rotation += 3
            elif self.type == 'wave_mine':
                self.pulse_time += 1
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        if self.mode == 'cube':
            if self.type == 'spike':
                # Draw single equilateral triangle
                center_x = self.x + self.width // 2
                top_point = (center_x, self.y)
                bottom_left = (self.x, self.y + self.height)
                bottom_right = (self.x + self.width, self.y + self.height)
                
                points = [top_point, bottom_left, bottom_right]
                pygame.draw.polygon(screen, COLORS['obstacle'], points)
                pygame.draw.polygon(screen, COLORS['obstacle_glow'], points, 3)
                
            elif self.type == 'double_spike':
                # Draw two spikes side by side
                spike_width = self.width // 2
                
                # First spike
                center_x1 = self.x + spike_width // 2
                points1 = [
                    (center_x1, self.y),
                    (self.x, self.y + self.height),
                    (self.x + spike_width, self.y + self.height)
                ]
                pygame.draw.polygon(screen, COLORS['obstacle'], points1)
                pygame.draw.polygon(screen, COLORS['obstacle_glow'], points1, 3)
                
                # Second spike
                center_x2 = self.x + spike_width + spike_width // 2
                points2 = [
                    (center_x2, self.y),
                    (self.x + spike_width, self.y + self.height),
                    (self.x + self.width, self.y + self.height)
                ]
                pygame.draw.polygon(screen, COLORS['obstacle'], points2)
                pygame.draw.polygon(screen, COLORS['obstacle_glow'], points2, 3)
                
            elif self.type == 'triple_spike':
                # Draw three spikes side by side
                spike_width = self.width // 3
                
                for i in range(3):
                    spike_x = self.x + i * spike_width
                    center_x = spike_x + spike_width // 2
                    points = [
                        (center_x, self.y),
                        (spike_x, self.y + self.height),
                        (spike_x + spike_width, self.y + self.height)
                    ]
                    pygame.draw.polygon(screen, COLORS['danger'], points)
                    pygame.draw.polygon(screen, COLORS['obstacle_glow'], points, 3)
                    
            elif self.type == 'block':
                pygame.draw.rect(screen, COLORS['obstacle'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['obstacle_glow'], (self.x, self.y, self.width, self.height), 3)
                
        elif self.mode == 'plane':
            if self.type == 'floating_block':
                pygame.draw.rect(screen, COLORS['obstacle'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['obstacle_glow'], (self.x, self.y, self.width, self.height), 3)
            elif self.type == 'vertical_bar':
                pygame.draw.rect(screen, COLORS['danger'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['obstacle_glow'], (self.x, self.y, self.width, self.height), 2)
            elif self.type == 'ring':
                pygame.draw.circle(screen, COLORS['obstacle'], (self.x + self.width//2, self.y + self.height//2), self.width//2, 8)
                pygame.draw.circle(screen, COLORS['obstacle_glow'], (self.x + self.width//2, self.y + self.height//2), self.width//2, 3)
            elif self.type == 'ceiling_spike':
                # Upside down triangle
                points = [
                    (self.x + self.width//2, self.y + self.height),  # Bottom point
                    (self.x, self.y),  # Top left
                    (self.x + self.width, self.y)  # Top right
                ]
                pygame.draw.polygon(screen, COLORS['danger'], points)
                pygame.draw.polygon(screen, COLORS['obstacle_glow'], points, 3)
            elif self.type == 'floating_spike':
                # Diamond shape
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                points = [
                    (center_x, self.y),  # Top
                    (self.x + self.width, center_y),  # Right
                    (center_x, self.y + self.height),  # Bottom
                    (self.x, center_y)  # Left
                ]
                pygame.draw.polygon(screen, COLORS['danger'], points)
                pygame.draw.polygon(screen, COLORS['obstacle_glow'], points, 2)
            elif self.type == 'double_ring':
                # Two rings side by side
                ring_radius = self.height // 2 - 5
                pygame.draw.circle(screen, COLORS['obstacle'], (self.x + ring_radius + 5, self.y + self.height//2), ring_radius, 6)
                pygame.draw.circle(screen, COLORS['obstacle'], (self.x + self.width - ring_radius - 5, self.y + self.height//2), ring_radius, 6)
                pygame.draw.circle(screen, COLORS['obstacle_glow'], (self.x + ring_radius + 5, self.y + self.height//2), ring_radius, 2)
                pygame.draw.circle(screen, COLORS['obstacle_glow'], (self.x + self.width - ring_radius - 5, self.y + self.height//2), ring_radius, 2)
            elif self.type == 'narrow_passage':
                pygame.draw.rect(screen, COLORS['danger'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['obstacle_glow'], (self.x, self.y, self.width, self.height), 2)
            elif self.type == 'moving_block':
                pygame.draw.rect(screen, COLORS['obstacle'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['obstacle_glow'], (self.x, self.y, self.width, self.height), 3)
                
        elif self.mode == 'wave':
            if self.type == 'narrow_gap':
                pygame.draw.rect(screen, COLORS['wave'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 3)
            elif self.type == 'wave_barrier':
                pygame.draw.rect(screen, COLORS['danger'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 2)
            elif self.type == 'moving_wall':
                pygame.draw.rect(screen, COLORS['wave'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 3)
            elif self.type == 'diagonal_spike':
                # Diamond spike
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                points = [
                    (center_x, self.y),
                    (self.x + self.width, center_y),
                    (center_x, self.y + self.height),
                    (self.x, center_y)
                ]
                pygame.draw.polygon(screen, COLORS['danger'], points)
                pygame.draw.polygon(screen, COLORS['wave_glow'], points, 2)
            elif self.type == 'wave_tunnel':
                pygame.draw.rect(screen, COLORS['wave'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 3)
            elif self.type == 'pulsing_barrier':
                pygame.draw.rect(screen, COLORS['danger'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 2)
            elif self.type == 'zigzag_wall':
                pygame.draw.rect(screen, COLORS['wave'], (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, COLORS['wave_glow'], (self.x, self.y, self.width, self.height), 3)
            elif self.type == 'rotating_cross':
                # Draw rotating cross
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                
                # Create cross surface
                cross_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                # Horizontal bar
                pygame.draw.rect(cross_surface, COLORS['danger'], (5, self.height//2 - 3, self.width - 10, 6))
                # Vertical bar
                pygame.draw.rect(cross_surface, COLORS['danger'], (self.width//2 - 3, 5, 6, self.height - 10))
                
                # Rotate and draw
                rotated_surface = pygame.transform.rotate(cross_surface, self.rotation)
                rotated_rect = rotated_surface.get_rect(center=(center_x, center_y))
                screen.blit(rotated_surface, rotated_rect)
            elif self.type == 'wave_mine':
                # Pulsing circle mine
                pulse_factor = 1 + 0.2 * math.sin(self.pulse_time * 0.2)
                radius = int((self.width // 2) * pulse_factor)
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                pygame.draw.circle(screen, COLORS['danger'], (center_x, center_y), radius)
                pygame.draw.circle(screen, COLORS['wave_glow'], (center_x, center_y), radius, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GeoDash")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.fullscreen = False
        
        # Game objects
        self.player = Player(100, SCREEN_HEIGHT - 140, SCREEN_HEIGHT)
        self.obstacles = []
        self.score = 0
        self.spawn_timer = 0
        self.background_offset = 0
        self.thrust_input = False
        
        # Mode switching
        self.modes = ['cube', 'plane', 'wave']
        self.current_mode_index = 0
        self.last_mode_switch_score = 0
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Update player screen height reference
        screen_height = self.screen.get_height()
        self.player.update_screen_height(screen_height)
        
        # Update player position if in cube mode to stay on ground
        if self.player.mode == 'cube':
            self.player.y = screen_height - 100 - self.player.height
        
    def get_current_mode(self):
        return self.modes[self.current_mode_index]
        
    def get_next_mode(self):
        next_index = (self.current_mode_index + 1) % len(self.modes)
        return self.modes[next_index]
        
    def check_mode_switch(self):
        # Switch mode every 100 points
        if self.score >= self.last_mode_switch_score + 100:
            self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
            screen_height = self.screen.get_height()
            self.player.update_screen_height(screen_height)
            self.player.set_mode(self.get_current_mode())
            self.last_mode_switch_score = self.score
            # Clear existing obstacles when switching modes
            self.obstacles.clear()
        
    def spawn_obstacle(self):
        current_mode = self.get_current_mode()
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        if current_mode == 'cube':
            obstacle_types = ['spike', 'block', 'double_spike', 'triple_spike']
        elif current_mode == 'plane':
            obstacle_types = ['floating_block', 'vertical_bar', 'ring', 'ceiling_spike', 
                            'floating_spike', 'double_ring', 'narrow_passage', 'moving_block']
        elif current_mode == 'wave':
            obstacle_types = ['narrow_gap', 'wave_barrier', 'moving_wall', 'diagonal_spike',
                            'wave_tunnel', 'pulsing_barrier', 'zigzag_wall', 'rotating_cross', 'wave_mine']
            
        obstacle_type = random.choice(obstacle_types)
        self.obstacles.append(Obstacle(screen_width, obstacle_type, current_mode, screen_height))
        
    def update(self):
        if not self.game_over:
            # Check for mode switching
            self.check_mode_switch()
            
            # Update player with obstacle list for collision detection
            self.player.update(self.thrust_input, self.obstacles)
            
            # Update obstacles
            for obstacle in self.obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    self.obstacles.remove(obstacle)
                    self.score += 10
                    
            # Spawn obstacles - increased frequency for plane and wave modes
            self.spawn_timer += 1
            if self.get_current_mode() == 'cube':
                spawn_rate = random.randint(60, 120)
            elif self.get_current_mode() == 'plane':
                spawn_rate = random.randint(40, 80)  # More frequent
            elif self.get_current_mode() == 'wave':
                spawn_rate = random.randint(35, 75)  # Most frequent
            
            if self.spawn_timer > spawn_rate:
                self.spawn_obstacle()
                self.spawn_timer = 0
                
            # Check collisions (excluding block tops for cube mode)
            player_rect = self.player.get_rect()
            for obstacle in self.obstacles:
                obstacle_rect = obstacle.get_rect()
                
                # Special collision for cube mode with blocks
                if (self.player.mode == 'cube' and obstacle.type == 'block' and 
                    obstacle.mode == 'cube'):
                    # Only collide with sides and bottom of blocks, not top
                    if (player_rect.colliderect(obstacle_rect) and 
                        not (player_rect.bottom <= obstacle_rect.top + 10 and self.player.vel_y >= 0)):
                        self.game_over = True
                        break
                else:
                    # Normal collision for all other obstacles
                    if player_rect.colliderect(obstacle_rect):
                        self.game_over = True
                        break
                    
            # Update background
            self.background_offset -= 2
            if self.background_offset <= -100:
                self.background_offset = 0
                
    def draw_background(self):
        # Get current screen size
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Draw gradient background
        for y in range(screen_height):
            color_ratio = y / screen_height
            r = int(COLORS['bg_dark'][0] + (COLORS['bg_light'][0] - COLORS['bg_dark'][0]) * color_ratio)
            g = int(COLORS['bg_dark'][1] + (COLORS['bg_light'][1] - COLORS['bg_dark'][1]) * color_ratio)
            b = int(COLORS['bg_dark'][2] + (COLORS['bg_light'][2] - COLORS['bg_dark'][2]) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (screen_width, y))
            
        # Draw moving grid pattern
        grid_size = 50
        for x in range(int(self.background_offset), screen_width + grid_size, grid_size):
            pygame.draw.line(self.screen, COLORS['ground'], (x, 0), (x, screen_height), 1)
        for y in range(0, screen_height, grid_size):
            pygame.draw.line(self.screen, COLORS['ground'], (0, y), (screen_width, y), 1)
            
    def draw_ground(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Draw ground
        ground_y = screen_height - 100
        pygame.draw.rect(self.screen, COLORS['ground'], (0, ground_y, screen_width, 100))
        
        # Draw ground pattern
        for x in range(0, screen_width, 40):
            pygame.draw.line(self.screen, COLORS['obstacle'], (x, ground_y), (x, screen_height), 2)
            
    def draw_ui(self):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Draw score with light lilac background
        score_text = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10), pygame.SRCALPHA)
        score_bg.fill((*COLORS['ui_light_lilac'], 180))
        pygame.draw.rect(score_bg, COLORS['ui_glow'], (0, 0, score_bg.get_width(), score_bg.get_height()), 2)
        self.screen.blit(score_bg, (10, 10))
        self.screen.blit(score_text, (20, 15))
        
        # Draw current mode with light lilac background
        mode_text = self.font.render(f"Mode: {self.get_current_mode().upper()}", True, COLORS['white'])
        mode_bg = pygame.Surface((mode_text.get_width() + 20, mode_text.get_height() + 10), pygame.SRCALPHA)
        mode_bg.fill((*COLORS['ui_light_lilac'], 180))
        pygame.draw.rect(mode_bg, COLORS['ui_glow'], (0, 0, mode_bg.get_width(), mode_bg.get_height()), 2)
        self.screen.blit(mode_bg, (10, 50))
        self.screen.blit(mode_text, (20, 55))
        
        # Draw next mode switch info with light lilac background
        points_to_switch = 100 - (self.score - self.last_mode_switch_score)
        if points_to_switch > 0:
            switch_text = self.font.render(f"Next mode ({self.get_next_mode().upper()}) in: {points_to_switch} points", True, COLORS['white'])
            switch_bg = pygame.Surface((switch_text.get_width() + 20, switch_text.get_height() + 10), pygame.SRCALPHA)
            switch_bg.fill((*COLORS['ui_light_lilac'], 180))
            pygame.draw.rect(switch_bg, COLORS['ui_glow'], (0, 0, switch_bg.get_width(), switch_bg.get_height()), 2)
            self.screen.blit(switch_bg, (10, 90))
            self.screen.blit(switch_text, (20, 95))
        
        # Draw fullscreen hint with light lilac background
        fullscreen_text = self.font.render("F11 - Fullscreen", True, COLORS['white'])
        fullscreen_bg = pygame.Surface((fullscreen_text.get_width() + 20, fullscreen_text.get_height() + 10), pygame.SRCALPHA)
        fullscreen_bg.fill((*COLORS['ui_light_lilac'], 180))
        pygame.draw.rect(fullscreen_bg, COLORS['ui_glow'], (0, 0, fullscreen_bg.get_width(), fullscreen_bg.get_height()), 2)
        self.screen.blit(fullscreen_bg, (screen_width - fullscreen_bg.get_width() - 10, 10))
        self.screen.blit(fullscreen_text, (screen_width - fullscreen_text.get_width() - 20, 15))
        
        # Draw instructions
        if len(self.obstacles) == 0 and self.score == 0:
            if self.get_current_mode() == 'cube':
                instruction_text = self.font.render("CUBE MODE: Press SPACE or CLICK to jump! Can jump on blocks!", True, COLORS['white'])
            elif self.get_current_mode() == 'plane':
                instruction_text = self.font.render("PLANE MODE: Hold SPACE or CLICK to fly up!", True, COLORS['white'])
            elif self.get_current_mode() == 'wave':
                instruction_text = self.font.render("WAVE MODE: Hold SPACE/CLICK = up-right, Release = down-right!", True, COLORS['white'])
                
            # Background for instructions
            instruction_bg = pygame.Surface((instruction_text.get_width() + 40, instruction_text.get_height() + 20), pygame.SRCALPHA)
            instruction_bg.fill((*COLORS['ui_light_lilac'], 200))
            pygame.draw.rect(instruction_bg, COLORS['ui_glow'], (0, 0, instruction_bg.get_width(), instruction_bg.get_height()), 3)
            instruction_rect = instruction_bg.get_rect(center=(screen_width//2, 150))
            self.screen.blit(instruction_bg, instruction_rect)
            text_rect = instruction_text.get_rect(center=(screen_width//2, 150))
            self.screen.blit(instruction_text, text_rect)
            
            auto_switch_text = self.font.render("Modes switch automatically every 100 points!", True, COLORS['white'])
            auto_switch_bg = pygame.Surface((auto_switch_text.get_width() + 40, auto_switch_text.get_height() + 20), pygame.SRCALPHA)
            auto_switch_bg.fill((*COLORS['ui_light_lilac'], 200))
            pygame.draw.rect(auto_switch_bg, COLORS['ui_glow'], (0, 0, auto_switch_bg.get_width(), auto_switch_bg.get_height()), 3)
            auto_switch_rect = auto_switch_bg.get_rect(center=(screen_width//2, 190))
            self.screen.blit(auto_switch_bg, auto_switch_rect)
            auto_text_rect = auto_switch_text.get_rect(center=(screen_width//2, 190))
            self.screen.blit(auto_switch_text, auto_text_rect)
            
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill(COLORS['bg_dark'])
            self.screen.blit(overlay, (0, 0))
            
            # Game over background
            game_over_text = self.big_font.render("GAME OVER", True, COLORS['white'])
            game_over_bg = pygame.Surface((game_over_text.get_width() + 60, game_over_text.get_height() + 30), pygame.SRCALPHA)
            game_over_bg.fill((*COLORS['ui_light_lilac'], 220))
            pygame.draw.rect(game_over_bg, COLORS['danger'], (0, 0, game_over_bg.get_width(), game_over_bg.get_height()), 4)
            game_over_rect = game_over_bg.get_rect(center=(screen_width//2, screen_height//2 - 50))
            self.screen.blit(game_over_bg, game_over_rect)
            game_over_text_rect = game_over_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
            self.screen.blit(game_over_text, game_over_text_rect)
            
            # Final score
            final_score_text = self.font.render(f"Final Score: {self.score}", True, COLORS['white'])
            final_score_bg = pygame.Surface((final_score_text.get_width() + 40, final_score_text.get_height() + 20), pygame.SRCALPHA)
            final_score_bg.fill((*COLORS['ui_light_lilac'], 200))
            pygame.draw.rect(final_score_bg, COLORS['ui_glow'], (0, 0, final_score_bg.get_width(), final_score_bg.get_height()), 3)
            final_score_rect = final_score_bg.get_rect(center=(screen_width//2, screen_height//2))
            self.screen.blit(final_score_bg, final_score_rect)
            final_score_text_rect = final_score_text.get_rect(center=(screen_width//2, screen_height//2))
            self.screen.blit(final_score_text, final_score_text_rect)
            
            # Restart instruction
            restart_text = self.font.render("Press R to restart or ESC to quit", True, COLORS['white'])
            restart_bg = pygame.Surface((restart_text.get_width() + 40, restart_text.get_height() + 20), pygame.SRCALPHA)
            restart_bg.fill((*COLORS['ui_light_lilac'], 200))
            pygame.draw.rect(restart_bg, COLORS['ui_glow'], (0, 0, restart_bg.get_width(), restart_bg.get_height()), 3)
            restart_rect = restart_bg.get_rect(center=(screen_width//2, screen_height//2 + 50))
            self.screen.blit(restart_bg, restart_rect)
            restart_text_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
            self.screen.blit(restart_text, restart_text_rect)
            
    def restart_game(self):
        screen_height = self.screen.get_height()
        self.game_over = False
        self.player = Player(100, screen_height - 140, screen_height)
        self.current_mode_index = 0
        self.player.set_mode(self.get_current_mode())
        self.obstacles = []
        self.score = 0
        self.spawn_timer = 0
        self.thrust_input = False
        self.last_mode_switch_score = 0
        
    def handle_events(self):
        keys = pygame.key.get_pressed()
        
        # Handle continuous input for plane and wave modes
        if self.get_current_mode() in ['plane', 'wave']:
            self.thrust_input = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and self.get_current_mode() == 'cube':
                    self.player.jump()
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over and self.get_current_mode() == 'cube':
                    self.player.jump()
                    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            
            # Draw everything
            self.draw_background()
            self.draw_ground()
            
            # Draw game objects
            self.player.draw(self.screen)
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
                
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
