# astro_dodger.py
# An enhanced top-down space-themed dodging game.

import pygame
import random
import sys
import os

# --- Initialization ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- Constants and Configuration ---

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 180, 255)  # Bright blue
ASTEROID_COLOR = (139, 145, 153)  # Gray
POWERUP_COLORS = {
    'shield': (46, 204, 113),  # Green
    'slow': (241, 196, 15),    # Yellow
    'score': (155, 89, 182)    # Purple
}

# Game Fonts
SCORE_FONT = pygame.font.SysFont("dejavusans", 30)
GAME_OVER_FONT = pygame.font.SysFont("dejavusans", 75)
RESTART_FONT = pygame.font.SysFont("dejavusans", 40)
TITLE_FONT = pygame.font.SysFont("dejavusans", 60)
MENU_FONT = pygame.font.SysFont("dejavusans", 40)

# Player Settings
PLAYER_SIZE = 40
PLAYER_SPEED = 8
INITIAL_LIVES = 3

# Asteroid Settings
ASTEROID_SIZE_MIN = 20
ASTEROID_SIZE_MAX = 50
ASTEROID_SPEED_MIN = 2
ASTEROID_SPEED_MAX = 6
ASTEROID_SPAWN_RATE = 30  # Frames between spawns
ASTEROID_SPAWN_ACCELERATION = 0.1  # How quickly spawn rate increases

# Starfield Settings
STAR_COUNT = 150
STAR_SPEED = 1

# Power-Up Settings
POWERUP_SIZE = 25
POWERUP_SPEED = 3
POWERUP_SPAWN_CHANCE = 0.002
POWERUP_DURATION = 300  # 5 seconds at 60 FPS
POWERUP_TYPES = ['shield', 'slow', 'score']

# Sound Effects
try:
    SOUNDS = {
        'explosion': pygame.mixer.Sound('explosion.wav'),
        'powerup': pygame.mixer.Sound('powerup.wav'),
        'background': pygame.mixer.Sound('background.wav')
    }
    SOUNDS['background'].set_volume(0.3)
    SOUNDS['background'].play(-1)  # Loop background music
except:
    print("Sound files not found. Continuing without sound.")
    SOUNDS = None

# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astro-Dodger")
clock = pygame.time.Clock()

# --- Game Classes ---

class Player:
    def __init__(self):
        self.reset()
        self.lives = INITIAL_LIVES
        self.invulnerable = 0
        
    def reset(self):
        self.points = [
            (SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5),
            (SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - PLAYER_SIZE / 2),
            (SCREEN_WIDTH / 2 + PLAYER_SIZE / 2, SCREEN_HEIGHT - PLAYER_SIZE / 2)
        ]
        self.rect = pygame.Rect(
            SCREEN_WIDTH / 2 - PLAYER_SIZE / 2,
            SCREEN_HEIGHT - PLAYER_SIZE * 1.5,
            PLAYER_SIZE, PLAYER_SIZE
        )
        
    def move(self, dx):
        new_x = self.rect.x + dx
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
            for i in range(len(self.points)):
                self.points[i] = (self.points[i][0] + dx, self.points[i][1])
    
    def draw(self):
        if self.invulnerable <= 0 or pygame.time.get_ticks() % 200 < 100:  # Blink when invulnerable
            pygame.draw.polygon(screen, PLAYER_COLOR, self.points)
    
    def hit(self):
        if self.invulnerable <= 0:
            self.lives -= 1
            self.invulnerable = 60  # 1 second invulnerability
            if SOUNDS:
                SOUNDS['explosion'].play()
            return True
        return False

class Asteroid:
    def __init__(self):
        size = random.randint(ASTEROID_SIZE_MIN, ASTEROID_SIZE_MAX)
        start_x = random.randint(0, SCREEN_WIDTH - size)
        self.rect = pygame.Rect(start_x, -size, size, size)
        self.speed = random.randint(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
    def update(self):
        self.rect.y += self.speed
        self.rotation += self.rotation_speed
        
    def draw(self):
        # Create a surface for rotation
        asteroid_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(asteroid_surface, ASTEROID_COLOR, (0, 0, self.rect.width, self.rect.height), border_radius=5)
        
        # Rotate and draw
        rotated = pygame.transform.rotate(asteroid_surface, self.rotation)
        screen.blit(rotated, (self.rect.x - (rotated.get_width() - self.rect.width) // 2,
                              self.rect.y - (rotated.get_height() - self.rect.height) // 2))

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = self.size
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)

class PowerUp:
    def __init__(self):
        self.type = random.choice(POWERUP_TYPES)
        start_x = random.randint(0, SCREEN_WIDTH - POWERUP_SIZE)
        self.rect = pygame.Rect(start_x, -POWERUP_SIZE, POWERUP_SIZE, POWERUP_SIZE)
        
    def update(self):
        self.rect.y += POWERUP_SPEED
        
    def draw(self):
        pygame.draw.rect(screen, POWERUP_COLORS[self.type], self.rect, border_radius=8)
        
        # Draw different symbols for different power-ups
        if self.type == 'shield':
            pygame.draw.circle(screen, WHITE, self.rect.center, POWERUP_SIZE // 3, 2)
        elif self.type == 'slow':
            pygame.draw.rect(screen, WHITE, (self.rect.centerx - 5, self.rect.centery - 5, 10, 10), 2)
        elif self.type == 'score':
            pygame.draw.polygon(screen, WHITE, [
                (self.rect.centerx, self.rect.top + 5),
                (self.rect.left + 5, self.rect.bottom - 5),
                (self.rect.right - 5, self.rect.bottom - 5)
            ])

# --- Game Functions ---

def show_menu():
    while True:
        screen.fill(BLACK)
        
        # Draw stars for background
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), random.randint(1, 2))
        
        title = TITLE_FONT.render("ASTRO-DODGER", True, PLAYER_COLOR)
        start = MENU_FONT.render("Press SPACE to Start", True, WHITE)
        quit_text = MENU_FONT.render("Press Q to Quit", True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 300))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        clock.tick(FPS)

def main_game():
    player = Player()
    asteroids = []
    stars = [Star() for _ in range(STAR_COUNT)]
    powerups = []
    
    # Game state
    running = True
    game_over = False
    score = 0
    high_score = 0
    asteroid_add_counter = 0
    asteroid_spawn_rate = ASTEROID_SPAWN_RATE
    
    # Power-up effects
    active_powerups = {
        'shield': 0,
        'slow': 0,
        'score': 0
    }
    
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or player.lives <= 0):
                    return main_game()  # Restart game
                if event.key == pygame.K_m and (game_over or player.lives <= 0):
                    return  # Return to menu
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        if not game_over and player.lives > 0:
            # Player Movement
            keys = pygame.key.get_pressed()
            move_speed = PLAYER_SPEED * (0.5 if active_powerups['slow'] > 0 else 1)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.move(-move_speed)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.move(move_speed)
            
            # Update stars
            for star in stars:
                star.update()
            
            # Update asteroids
            asteroid_add_counter += 1
            if asteroid_add_counter >= asteroid_spawn_rate:
                asteroid_add_counter = 0
                asteroids.append(Asteroid())
                if asteroid_spawn_rate > 10:
                    asteroid_spawn_rate -= ASTEROID_SPAWN_ACCELERATION
            
            for asteroid in asteroids[:]:
                asteroid.update()
                if asteroid.rect.top > SCREEN_HEIGHT:
                    asteroids.remove(asteroid)
                    score += 1
            
            # Update power-ups
            if random.random() < POWERUP_SPAWN_CHANCE and not any(p.active for p in powerups):
                powerups.append(PowerUp())
            
            for powerup in powerups[:]:
                powerup.update()
                if powerup.rect.top > SCREEN_HEIGHT:
                    powerups.remove(powerup)
            
            # Update active power-ups
            for power_type in active_powerups:
                if active_powerups[power_type] > 0:
                    active_powerups[power_type] -= 1
            
            # Update invulnerability
            if player.invulnerable > 0:
                player.invulnerable -= 1
            
            # Collision Detection
            for asteroid in asteroids[:]:
                if player.rect.colliderect(asteroid.rect):
                    if active_powerups['shield'] > 0:
                        asteroids.remove(asteroid)
                        score += 5
                    elif player.hit():
                        asteroids.remove(asteroid)
                        if player.lives <= 0:
                            game_over = True
            
            for powerup in powerups[:]:
                if player.rect.colliderect(powerup.rect):
                    powerups.remove(powerup)
                    active_powerups[powerup.type] = POWERUP_DURATION
                    if SOUNDS:
                        SOUNDS['powerup'].play()
                    if powerup.type == 'score':
                        score += 20
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw stars
        for star in stars:
            star.draw()
        
        # Draw asteroids and power-ups
        for asteroid in asteroids:
            asteroid.draw()
        for powerup in powerups:
            powerup.draw()
        
        # Draw player
        player.draw()
        
        # Draw shield effect if active
        if active_powerups['shield'] > 0:
            shield_surface = pygame.Surface((PLAYER_SIZE * 2, PLAYER_SIZE * 2), pygame.SRCALPHA)
            alpha = int(100 * (active_powerups['shield'] / POWERUP_DURATION))
            pygame.draw.circle(shield_surface, (0, 255, 0, alpha), (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE)
            screen.blit(shield_surface, (player.rect.centerx - PLAYER_SIZE, player.rect.centery - PLAYER_SIZE))
        
        # Draw score and lives
        score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
        lives_text = SCORE_FONT.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        # Draw active power-up indicators
        y_pos = 90
        for power_type, duration in active_powerups.items():
            if duration > 0:
                power_text = SCORE_FONT.render(f"{power_type.capitalize()}: {duration//60}s", True, POWERUP_COLORS[power_type])
                screen.blit(power_text, (10, y_pos))
                y_pos += 30
        
        # Draw game over screen
        if game_over or player.lives <= 0:
            high_score = max(score, high_score)
            
            game_over_text = GAME_OVER_FONT.render("GAME OVER", True, (255, 0, 0))
            score_text = RESTART_FONT.render(f"Score: {score}  High Score: {high_score}", True, WHITE)
            restart_text = RESTART_FONT.render("Press R to Restart", True, WHITE)
            menu_text = RESTART_FONT.render("Press M for Menu", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 110))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

# --- Main Program ---
if __name__ == "__main__":
    while True:
        show_menu()
        main_game()