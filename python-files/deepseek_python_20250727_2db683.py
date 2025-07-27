import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FNF: Nightmare BF vs Corrupted Spirit BF")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)
GRAY = (50, 50, 50)
DARK_PURPLE = (75, 0, 130)

# Game state
score = 0
combo = 0
player_health = 100
enemy_health = 100
game_over = False

# Fonts
font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 32)

# Characters
class Character:
    def __init__(self, x, y, color, aura_color):
        self.x = x
        self.y = y
        self.color = color
        self.aura_color = aura_color
        self.animation_frame = 0
        self.sing_animations = ['left', 'down', 'up', 'right']
        self.width = 150
        self.height = 250
        
    def draw(self, surface):
        # Aura
        pygame.draw.circle(surface, self.aura_color, (self.x, self.y - 120), 70, 5)
        
        # Body
        pygame.draw.ellipse(surface, self.color, 
                           (self.x - 30, self.y - 90, 60, 80))
        
        # Head
        pygame.draw.ellipse(surface, self.color, 
                           (self.x - 40, self.y - 170, 80, 100))
        
        # Eyes
        pygame.draw.circle(surface, WHITE, (self.x - 15, self.y - 150), 10)
        pygame.draw.circle(surface, WHITE, (self.x + 15, self.y - 150), 10)
        
        # Mouth (animated)
        mouth_height = 5 + math.sin(pygame.time.get_ticks() / 200) * 5
        pygame.draw.ellipse(surface, BLACK, 
                           (self.x - 20, self.y - 140, 40, mouth_height))

# Create characters
nightmare_bf = Character(200, 350, PURPLE, DARK_PURPLE)
corrupted_spirit_bf = Character(600, 350, CYAN, CYAN)

# Notes
notes = []
note_speed = 5
note_colors = [RED, GREEN, BLUE, YELLOW]
note_directions = ['left', 'down', 'up', 'right']

# Arrow keys
keys = {
    pygame.K_LEFT: False,
    pygame.K_DOWN: False,
    pygame.K_UP: False,
    pygame.K_RIGHT: False
}

# Arrow hit positions
arrow_positions = {
    'left': (150, 450),
    'down': (210, 450),
    'up': (270, 450),
    'right': (330, 450)
}

# Game functions
def spawn_note():
    direction = random.choice(note_directions)
    color = note_colors[note_directions.index(direction)]
    notes.append({
        'x': WIDTH,
        'y': 400,
        'width': 50,
        'height': 50,
        'color': color,
        'direction': direction
    })

def draw_arrow(surface, x, y, direction, color):
    if direction == 'left':
        points = [(x + 10, y + 25), (x + 40, y + 10), (x + 40, y + 40)]
    elif direction == 'down':
        points = [(x + 10, y + 10), (x + 25, y + 40), (x + 40, y + 10)]
    elif direction == 'up':
        points = [(x + 10, y + 40), (x + 25, y + 10), (x + 40, y + 40)]
    elif direction == 'right':
        points = [(x + 40, y + 25), (x + 10, y + 10), (x + 10, y + 40)]
    
    pygame.draw.polygon(surface, color, points)

def draw_health_bar(surface, x, y, width, height, value, max_value, color):
    ratio = value / max_value
    pygame.draw.rect(surface, GRAY, (x, y, width, height))
    pygame.draw.rect(surface, color, (x, y, width * ratio, height))

def reset_game():
    global score, combo, player_health, enemy_health, notes, game_over
    score = 0
    combo = 0
    player_health = 100
    enemy_health = 100
    notes = []
    game_over = False

# Main game loop
clock = pygame.time.Clock()
spawn_timer = 0

running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in keys:
                keys[event.key] = True
            elif event.key == pygame.K_r and game_over:
                reset_game()
        elif event.type == pygame.KEYUP:
            if event.key in keys:
                keys[event.key] = False
    
    if not game_over:
        # Update game state
        # Spawn notes randomly
        spawn_timer += 1
        if spawn_timer >= 30:  # Adjust this value for note frequency
            if random.random() < 0.3:
                spawn_note()
            spawn_timer = 0
        
        # Update notes
        for note in notes[:]:
            note['x'] -= note_speed
            
            # Check if note is in hit area
            if note['x'] < 250:
                key_map = {
                    'left': pygame.K_LEFT,
                    'down': pygame.K_DOWN,
                    'up': pygame.K_UP,
                    'right': pygame.K_RIGHT
                }
                
                if keys[key_map[note['direction']]]:
                    # Hit note
                    score += 100
                    combo += 1
                    notes.remove(note)
                    
                    # Update health
                    player_health = min(100, player_health + 2)
                    enemy_health = max(0, enemy_health - 2)
                elif note['x'] < 200:
                    # Missed note
                    combo = 0
                    notes.remove(note)
                    
                    # Update health
                    player_health = max(0, player_health - 5)
                    enemy_health = min(100, enemy_health + 5)
        
        # Check game over
        if player_health <= 0 or enemy_health <= 0:
            game_over = True
    
    # Draw everything
    screen.fill(BLACK)
    
    # Draw stage
    pygame.draw.rect(screen, GRAY, (0, 400, WIDTH, 200))
    
    # Draw characters
    nightmare_bf.draw(screen)
    corrupted_spirit_bf.draw(screen)
    
    # Draw notes
    for note in notes:
        pygame.draw.rect(screen, note['color'], 
                        (note['x'], note['y'], note['width'], note['height']))
        draw_arrow(screen, note['x'], note['y'], note['direction'], WHITE)
    
    # Draw arrows at hit area
    for i, direction in enumerate(note_directions):
        x, y = arrow_positions[direction]
        draw_arrow(screen, x, y, direction, note_colors[i])
    
    # Draw UI
    # Health bars
    draw_health_bar(screen, 50, 50, 250, 20, player_health, 100, GREEN)
    draw_health_bar(screen, WIDTH - 300, 50, 250, 20, enemy_health, 100, RED)
    
    # Score and combo
    score_text = big_font.render(f"Score: {score}", True, YELLOW)
    combo_text = font.render(f"Combo: {combo}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    screen.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 60))
    
    # Game over message
    if game_over:
        if player_health <= 0:
            message = "You Lost! Press R to restart"
            color = RED
        else:
            message = "You Won! Press R to restart"
            color = GREEN
        
        game_over_text = big_font.render(message, True, color)
        screen.blit(game_over_text, 
                   (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()