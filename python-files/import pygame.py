import pygame
import math
import random
import sys
import os

# Resource path function for EXE compatibility
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize Pygame
pygame.init()

# Game Information
GAME_NAME = "MineCraft 3D + Calculator"
GAME_VERSION = "1.0"
DEVELOPER = "Your Name"

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"{GAME_NAME} v{GAME_VERSION}")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (86, 125, 70)
DIRT_BROWN = (155, 118, 83)
STONE_GRAY = (120, 120, 120)

# Game States
MENU = 0
GAME_3D = 1
CALCULATOR = 2

current_state = MENU

# Calculator Class
class Calculator:
    def __init__(self):
        self.display = "0"
        self.buttons = []
        self.create_buttons()
        self.result = 0
        self.operator = ""
        self.waiting_operand = True
    
    def create_buttons(self):
        buttons_layout = [
            [350, 200, 80, 50, "7", GRAY], [440, 200, 80, 50, "8", GRAY], 
            [530, 200, 80, 50, "9", GRAY], [620, 200, 80, 50, "/", DARK_GRAY],
            [350, 260, 80, 50, "4", GRAY], [440, 260, 80, 50, "5", GRAY], 
            [530, 260, 80, 50, "6", GRAY], [620, 260, 80, 50, "*", DARK_GRAY],
            [350, 320, 80, 50, "1", GRAY], [440, 320, 80, 50, "2", GRAY], 
            [530, 320, 80, 50, "3", GRAY], [620, 320, 80, 50, "-", DARK_GRAY],
            [350, 380, 80, 50, "0", GRAY], [440, 380, 80, 50, ".", GRAY], 
            [530, 380, 80, 50, "=", GREEN], [620, 380, 80, 50, "+", DARK_GRAY],
            [350, 440, 170, 50, "Clear", RED], [530, 440, 170, 50, "All Clear", BLUE],
        ]
        self.buttons = buttons_layout
    
    def draw(self, screen):
        # Calculator background
        pygame.draw.rect(screen, (40, 40, 40), (330, 150, 370, 360))
        pygame.draw.rect(screen, WHITE, (330, 150, 370, 360), 3)
        
        # Display
        pygame.draw.rect(screen, BLACK, (350, 160, 340, 40))
        font = pygame.font.SysFont('arial', 32, bold=True)
        display_text = font.render(self.display, True, GREEN)
        screen.blit(display_text, (360, 170))
        
        # Buttons
        for button in self.buttons:
            x, y, w, h, text, color = button
            pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
            pygame.draw.rect(screen, WHITE, (x, y, w, h), 2, border_radius=8)
            
            btn_font = pygame.font.SysFont('arial', 22, bold=True)
            btn_text = btn_font.render(text, True, BLACK if color != DARK_GRAY else WHITE)
            text_rect = btn_text.get_rect(center=(x + w//2, y + h//2))
            screen.blit(btn_text, text_rect)
    
    def handle_click(self, pos):
        x, y = pos
        for button in self.buttons:
            btn_x, btn_y, btn_w, btn_h, text, color = button
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                self.button_pressed(text)
                return True
        return False
    
    def button_pressed(self, text):
        if text.isdigit() or text == '.':
            if self.waiting_operand:
                self.display = text
                self.waiting_operand = False
            else:
                if text == '.' and '.' in self.display:
                    return
                self.display += text
        elif text in ['+', '-', '*', '/']:
            if not self.waiting_operand:
                self.calculate()
            self.operator = text
            self.result = float(self.display)
            self.waiting_operand = True
        elif text == '=':
            self.calculate()
            self.operator = ""
            self.waiting_operand = True
        elif text == 'Clear':
            self.display = "0"
            self.waiting_operand = True
        elif text == 'All Clear':
            self.display = "0"
            self.result = 0
            self.operator = ""
            self.waiting_operand = True
    
    def calculate(self):
        if self.operator and not self.waiting_operand:
            try:
                current = float(self.display)
                if self.operator == '+': 
                    self.result += current
                elif self.operator == '-': 
                    self.result -= current
                elif self.operator == '*': 
                    self.result *= current
                elif self.operator == '/': 
                    if current != 0: 
                        self.result /= current
                    else: 
                        self.display = "Error"
                        return
                
                self.display = str(round(self.result, 6))
                if '.' in self.display:
                    self.display = self.display.rstrip('0').rstrip('.')
            except:
                self.display = "Error"

# 3D World System
class Player:
    def __init__(self):
        self.x = 8.0
        self.y = 15.0
        self.z = 8.0
        self.yaw = 0.0
        self.speed = 0.1

player = Player()
calculator = Calculator()

# World Generation
WORLD_SIZE = 24
world = {}

def generate_world():
    for x in range(WORLD_SIZE):
        for z in range(WORLD_SIZE):
            height = int(8 + math.sin(x * 0.3) * 3 + math.cos(z * 0.3) * 3)
            height = max(3, min(20, height))
            
            for y in range(height):
                if y < height - 3:
                    world[(x, y, z)] = 3  # Stone
                elif y < height - 1:
                    world[(x, y, z)] = 2  # Dirt
                else:
                    world[(x, y, z)] = 1  # Grass

generate_world()

# Block Colors
BLOCK_COLORS = {
    1: GRASS_GREEN, 
    2: DIRT_BROWN, 
    3: STONE_GRAY
}

def render_3d_world():
    # Sky and ground
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, (50, 70, 40), (0, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT//2))
    
    FOV = math.pi / 3
    HALF_FOV = FOV / 2
    MAX_DIST = 20
    
    # Simple raycasting
    for screen_x in range(0, SCREEN_WIDTH, 2):
        camera_x = 2 * screen_x / SCREEN_WIDTH - 1
        ray_angle = player.yaw + math.atan(camera_x * math.tan(HALF_FOV))
        
        ray_dir_x = math.cos(ray_angle)
        ray_dir_z = math.sin(ray_angle)
        
        ray_x, ray_z = player.x, player.z
        hit_wall = False
        distance = 0
        
        while not hit_wall and distance < MAX_DIST:
            ray_x += ray_dir_x * 0.1
            ray_z += ray_dir_z * 0.1
            distance += 0.1
            
            # Check blocks
            for check_y in range(20, -1, -1):
                block_pos = (int(ray_x), check_y, int(ray_z))
                if block_pos in world:
                    block_type = world[block_pos]
                    
                    # Calculate wall height
                    wall_height = int(SCREEN_HEIGHT / (distance + 0.1))
                    wall_top = SCREEN_HEIGHT//2 - wall_height//2
                    wall_bottom = SCREEN_HEIGHT//2 + wall_height//2
                    
                    # Get color with shading
                    color = BLOCK_COLORS.get(block_type, GRASS_GREEN)
                    darken = max(0.3, 1.0 - distance / MAX_DIST)
                    shaded_color = (
                        int(color[0] * darken),
                        int(color[1] * darken),
                        int(color[2] * darken)
                    )
                    
                    # Draw wall slice
                    for screen_y in range(max(0, wall_top), min(SCREEN_HEIGHT, wall_bottom)):
                        screen.set_at((screen_x, screen_y), shaded_color)
                        if screen_x + 1 < SCREEN_WIDTH:
                            screen.set_at((screen_x + 1, screen_y), shaded_color)
                    
                    hit_wall = True
                    break

# Menu System
def draw_menu():
    screen.fill((30, 30, 60))
    
    # Title
    title_font = pygame.font.SysFont('arial', 60, bold=True)
    title = title_font.render(GAME_NAME, True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    version_font = pygame.font.SysFont('arial', 24)
    version = version_font.render(f"Version {GAME_VERSION}", True, WHITE)
    screen.blit(version, (SCREEN_WIDTH//2 - version.get_width()//2, 180))
    
    # Menu Buttons
    buttons = [
        [SCREEN_WIDTH//2 - 100, 250, 200, 50, "3D World", GREEN],
        [SCREEN_WIDTH//2 - 100, 320, 200, 50, "Calculator", BLUE],
        [SCREEN_WIDTH//2 - 100, 390, 200, 50, "Quit", RED]
    ]
    
    for button in buttons:
        x, y, w, h, text, color = button
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, WHITE, (x, y, w, h), 3, border_radius=10)
        
        btn_font = pygame.font.SysFont('arial', 28, bold=True)
        btn_text = btn_font.render(text, True, BLACK)
        text_rect = btn_text.get_rect(center=(x + w//2, y + h//2))
        screen.blit(btn_text, text_rect)
    
    # Controls info
    controls_font = pygame.font.SysFont('arial', 18)
    controls = [
        "Controls: ESC - Menu, F1 - 3D World, F2 - Calculator",
        "3D Controls: WASD - Move, Mouse - Look around"
    ]
    
    for i, text in enumerate(controls):
        control_text = controls_font.render(text, True, WHITE)
        screen.blit(control_text, (SCREEN_WIDTH//2 - control_text.get_width()//2, 500 + i*30))

def handle_menu_click(pos):
    x, y = pos
    buttons = [
        [SCREEN_WIDTH//2 - 100, 250, 200, 50],  # 3D World
        [SCREEN_WIDTH//2 - 100, 320, 200, 50],  # Calculator
        [SCREEN_WIDTH//2 - 100, 390, 200, 50]   # Quit
    ]
    
    for i, button in enumerate(buttons):
        btn_x, btn_y, btn_w, btn_h = button
        if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
            return i + 1  # 1: 3D World, 2: Calculator, 3: Quit
    return 0

# Main Game Loop
def main():
    global current_state
    
    print(f"🎮 {GAME_NAME} v{GAME_VERSION} Started!")
    print("📍 Controls: ESC - Menu, F1 - 3D World, F2 - Calculator")
    print("🎯 3D Controls: WASD - Move, Mouse - Look around")
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if current_state == MENU:
                    choice = handle_menu_click(mouse_pos)
                    if choice == 1: 
                        current_state = GAME_3D
                        pygame.mouse.set_visible(False)
                    elif choice == 2: 
                        current_state = CALCULATOR
                        pygame.mouse.set_visible(True)
                    elif choice == 3: 
                        running = False
                
                elif current_state == CALCULATOR:
                    calculator.handle_click(mouse_pos)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    pygame.mouse.set_visible(True)
                elif event.key == pygame.K_F1:
                    current_state = GAME_3D
                    pygame.mouse.set_visible(False)
                elif event.key == pygame.K_F2:
                    current_state = CALCULATOR
                    pygame.mouse.set_visible(True)
        
        # 3D World Movement
        if current_state == GAME_3D:
            keys = pygame.key.get_pressed()
            mouse_rel = pygame.mouse.get_rel()
            player.yaw += mouse_rel[0] * 0.003
            
            if keys[pygame.K_w]:
                player.x += math.cos(player.yaw) * player.speed
                player.z += math.sin(player.yaw) * player.speed
            if keys[pygame.K_s]:
                player.x -= math.cos(player.yaw) * player.speed
                player.z -= math.sin(player.yaw) * player.speed
            if keys[pygame.K_a]:
                player.x += math.cos(player.yaw - math.pi/2) * player.speed
                player.z += math.sin(player.yaw - math.pi/2) * player.speed
            if keys[pygame.K_d]:
                player.x += math.cos(player.yaw + math.pi/2) * player.speed
                player.z += math.sin(player.yaw + math.pi/2) * player.speed
            
            # Keep player in bounds
            player.x = max(1, min(WORLD_SIZE - 2, player.x))
            player.z = max(1, min(WORLD_SIZE - 2, player.z))
        
        # Rendering
        if current_state == MENU:
            draw_menu()
        elif current_state == GAME_3D:
            render_3d_world()
            
            # HUD
            font = pygame.font.SysFont('arial', 20)
            pos_text = font.render(f'Position: X:{player.x:.1f} Z:{player.z:.1f}', True, WHITE)
            screen.blit(pos_text, (20, 20))
            
            help_text = font.render('ESC: Menu | WASD: Move | Mouse: Look', True, YELLOW)
            screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 30))
            
        elif current_state == CALCULATOR:
            screen.fill((20, 20, 40))
            calculator.draw(screen)
            
            font = pygame.font.SysFont('arial', 24)
            title = font.render('Calculator - Press ESC for Menu', True, YELLOW)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # FPS Counter
        fps_font = pygame.font.SysFont('arial', 18)
        fps_text = fps_font.render(f'FPS: {int(clock.get_fps())}', True, WHITE)
        screen.blit(fps_text, (SCREEN_WIDTH - 80, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    