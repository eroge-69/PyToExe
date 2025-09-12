import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Player settings
PLAYER_SPEED = 4
BULLET_SPEED = 8
ENEMY_SPEED = 1
ENEMY_DROP_SPEED = 20
BOSS_SPEED = 2
BOSS_BULLET_SPEED = 4

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(50, 255)
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.rect(screen, color, (self.x, self.y, 1, 1))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 26
        self.height = 16
        self.speed = PLAYER_SPEED
        
    def move_left(self):
        if self.x > 0:
            self.x -= self.speed
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        # Classic Space Invaders player sprite (pixel art style)
        # Draw main body
        pygame.draw.rect(screen, GREEN, (self.x + 12, self.y, 2, 4))
        pygame.draw.rect(screen, GREEN, (self.x + 10, self.y + 4, 6, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 8, self.y + 6, 10, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 6, self.y + 8, 14, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 2, self.y + 10, 22, 2))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + 12, 26, 4))
        
        # Draw cannon details
        pygame.draw.rect(screen, GREEN, (self.x + 4, self.y + 14, 2, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 8, self.y + 14, 2, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 16, self.y + 14, 2, 2))
        pygame.draw.rect(screen, GREEN, (self.x + 20, self.y + 14, 2, 2))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 2
        self.height = 6
        self.speed = BULLET_SPEED
        
    def update(self):
        self.y -= self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return self.y < 0

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.x = x
        self.y = y
        self.width = 22
        self.height = 16
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.enemy_type = enemy_type  # 0=bottom, 1=middle, 2=top
        self.animation_frame = 0
        self.animation_timer = 0
        
    def update(self, move_down=False):
        if move_down:
            self.y += ENEMY_DROP_SPEED
            self.direction *= -1
        else:
            self.x += self.speed * self.direction
            
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 30:  # Change frame every 30 ticks
            self.animation_frame = 1 - self.animation_frame
            self.animation_timer = 0
            
    def draw(self, screen):
        colors = [CYAN, MAGENTA, YELLOW]  # Bottom, middle, top row colors
        color = colors[self.enemy_type]
        
        frame = self.animation_frame
        
        if self.enemy_type == 0:  # Bottom enemies (squid-like)
            if frame == 0:
                # Frame 1
                pygame.draw.rect(screen, color, (self.x + 8, self.y, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 2, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 4, 18, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 6, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 8, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 6, self.y + 10, 10, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 12, 4, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 12, 4, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 20, self.y + 14, 2, 2))
            else:
                # Frame 2
                pygame.draw.rect(screen, color, (self.x + 8, self.y, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 2, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 4, 18, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 6, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 8, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 6, self.y + 10, 10, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 8, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 12, self.y + 14, 2, 2))
                
        elif self.enemy_type == 1:  # Middle enemies (crab-like)
            if frame == 0:
                pygame.draw.rect(screen, color, (self.x + 2, self.y, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 18, self.y, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 2, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 2, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 4, 18, 2))
                pygame.draw.rect(screen, color, (self.x + 0, self.y + 6, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 8, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 8, self.y + 10, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 6, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 14, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 14, 2, 2))
            else:
                pygame.draw.rect(screen, color, (self.x + 2, self.y, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 18, self.y, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 2, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 2, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 4, 18, 2))
                pygame.draw.rect(screen, color, (self.x + 0, self.y + 6, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 8, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 8, self.y + 10, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 18, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 0, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 20, self.y + 14, 2, 2))
                
        else:  # Top enemies (octopus-like)
            if frame == 0:
                pygame.draw.rect(screen, color, (self.x + 6, self.y, 10, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 2, 18, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 4, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 6, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 14, self.y + 6, 6, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 8, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 10, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 6, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 14, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 18, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 14, 2, 2))
            else:
                pygame.draw.rect(screen, color, (self.x + 6, self.y, 10, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 2, 18, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 4, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 6, 6, 2))
                pygame.draw.rect(screen, color, (self.x + 14, self.y + 6, 6, 2))
                pygame.draw.rect(screen, color, (self.x, self.y + 8, 22, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 10, 14, 2))
                pygame.draw.rect(screen, color, (self.x + 0, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 4, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 16, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 20, self.y + 12, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 2, self.y + 14, 2, 2))
                pygame.draw.rect(screen, color, (self.x + 18, self.y + 14, 2, 2))

class UFO:
    def __init__(self):
        self.x = -60
        self.y = 40
        self.width = 32
        self.height = 14
        self.speed = 2
        self.active = False
        self.spawn_timer = random.randint(600, 1200)  # Random spawn time
        
    def update(self):
        if not self.active:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.active = True
                self.x = -self.width
                self.spawn_timer = random.randint(1200, 2400)
        else:
            self.x += self.speed
            if self.x > SCREEN_WIDTH:
                self.active = False
                
    def draw(self, screen):
        if self.active:
            # UFO sprite
            pygame.draw.rect(screen, RED, (self.x + 6, self.y, 20, 2))
            pygame.draw.rect(screen, RED, (self.x + 2, self.y + 2, 28, 2))
            pygame.draw.rect(screen, RED, (self.x, self.y + 4, 32, 2))
            pygame.draw.rect(screen, RED, (self.x + 4, self.y + 6, 24, 2))
            pygame.draw.rect(screen, RED, (self.x + 8, self.y + 8, 16, 2))
            pygame.draw.rect(screen, RED, (self.x + 12, self.y + 10, 8, 2))
            pygame.draw.rect(screen, RED, (self.x + 14, self.y + 12, 4, 2))

class Boss:
    def __init__(self, x, y, boss_type=1):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 48
        self.speed = BOSS_SPEED
        self.direction = 1
        self.boss_type = boss_type
        self.max_health = 15 + (boss_type - 1) * 10
        self.health = self.max_health
        self.shoot_timer = 0
        self.shoot_delay = 80 - (boss_type * 15)
        self.bullets = []
        
    def update(self):
        self.x += self.speed * self.direction
        
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
            
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()
            self.shoot_timer = 0
            
        for bullet in self.bullets[:]:
            bullet.y += BOSS_BULLET_SPEED
            if bullet.y > SCREEN_HEIGHT:
                self.bullets.remove(bullet)
    
    def shoot(self):
        if self.boss_type == 1:
            bullet_x = self.x + self.width // 2 - 1
            bullet_y = self.y + self.height
            self.bullets.append(pygame.Rect(bullet_x, bullet_y, 2, 6))
        elif self.boss_type == 2:
            for offset in [-16, 0, 16]:
                bullet_x = self.x + self.width // 2 - 1 + offset
                bullet_y = self.y + self.height
                self.bullets.append(pygame.Rect(bullet_x, bullet_y, 2, 6))
        else:
            for offset in [-24, -12, 0, 12, 24]:
                bullet_x = self.x + self.width // 2 - 1 + offset
                bullet_y = self.y + self.height
                self.bullets.append(pygame.Rect(bullet_x, bullet_y, 2, 6))
    
    def take_damage(self):
        self.health -= 1
        return self.health <= 0
    
    def draw(self, screen):
        colors = [PURPLE, ORANGE, RED]
        color = colors[min(self.boss_type - 1, 2)]
        
        # Large boss sprite (simplified pixel art)
        pygame.draw.rect(screen, color, (self.x + 16, self.y, 32, 4))
        pygame.draw.rect(screen, color, (self.x + 8, self.y + 4, 48, 4))
        pygame.draw.rect(screen, color, (self.x + 4, self.y + 8, 56, 4))
        pygame.draw.rect(screen, color, (self.x, self.y + 12, 64, 8))
        pygame.draw.rect(screen, color, (self.x + 8, self.y + 20, 48, 8))
        pygame.draw.rect(screen, color, (self.x + 16, self.y + 28, 32, 8))
        pygame.draw.rect(screen, color, (self.x + 24, self.y + 36, 16, 4))
        pygame.draw.rect(screen, color, (self.x + 28, self.y + 40, 8, 4))
        pygame.draw.rect(screen, color, (self.x + 30, self.y + 44, 4, 4))
        
        # Eyes
        pygame.draw.rect(screen, WHITE, (self.x + 16, self.y + 16, 4, 4))
        pygame.draw.rect(screen, WHITE, (self.x + 44, self.y + 16, 4, 4))
        
        # Health bar
        health_bar_width = self.width
        health_percentage = self.health / self.max_health
        
        pygame.draw.rect(screen, RED, (self.x, self.y - 8, health_bar_width, 4))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, int(health_bar_width * health_percentage), 4))
        
        # Boss bullets
        for bullet in self.bullets:
            pygame.draw.rect(screen, RED, bullet)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SPACE INVADERS")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 13, SCREEN_HEIGHT - 60)
        self.bullets = []
        self.enemies = []
        self.boss = None
        self.ufo = UFO()
        self.stars = [Star() for _ in range(100)]
        
        # Game state
        self.score = 0
        self.wave = 1
        self.boss_level = 0
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.game_over = False
        self.win = False
        self.lives = 3
        
        # Create enemies
        self.create_enemies()
        
    def create_enemies(self):
        """Create a grid of enemies with different types"""
        self.enemies = []
        rows = 5
        cols = 11
        enemy_width = 22
        enemy_height = 16
        padding_x = 8
        padding_y = 8
        
        start_x = (SCREEN_WIDTH - (cols * (enemy_width + padding_x) - padding_x)) // 2
        start_y = 80
        
        for row in range(rows):
            enemy_type = 2 if row == 0 else (1 if row in [1, 2] else 0)
            for col in range(cols):
                x = start_x + col * (enemy_width + padding_x)
                y = start_y + row * (enemy_height + padding_y)
                self.enemies.append(Enemy(x, y, enemy_type))
    
    def spawn_boss(self):
        """Spawn a boss after every wave"""
        self.boss_level += 1
        boss_x = SCREEN_WIDTH // 2 - 32
        boss_y = 60
        self.boss = Boss(boss_x, boss_y, min(self.boss_level, 3))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.win:
                    # Shoot bullet (limit to 3 bullets on screen)
                    if len(self.bullets) < 3:
                        bullet_x = self.player.x + self.player.width // 2 - 1
                        bullet_y = self.player.y
                        self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and (self.game_over or self.win):
                    # Restart game
                    self.restart_game()
        return True
    
    def update(self):
        if self.game_over or self.win:
            return
            
        # Update stars
        for star in self.stars:
            star.update()
            
        # Update UFO
        self.ufo.update()
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Check UFO collision
        if self.ufo.active:
            for bullet in self.bullets[:]:
                if (bullet.x < self.ufo.x + self.ufo.width and
                    bullet.x + bullet.width > self.ufo.x and
                    bullet.y < self.ufo.y + self.ufo.height and
                    bullet.y + bullet.height > self.ufo.y):
                    
                    self.bullets.remove(bullet)
                    self.score += random.choice([100, 200, 300, 500])  # Random bonus
                    self.ufo.active = False
                    break
        
        # Update boss if present
        if self.boss:
            self.boss.update()
            
            # Check boss bullet collision with player
            for bullet in self.boss.bullets[:]:
                if (bullet.x < self.player.x + self.player.width and
                    bullet.x + bullet.width > self.player.x and
                    bullet.y < self.player.y + self.player.height and
                    bullet.y + bullet.height > self.player.y):
                    self.boss.bullets.remove(bullet)
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
            
            # Check player bullets vs boss
            for bullet in self.bullets[:]:
                if (bullet.x < self.boss.x + self.boss.width and
                    bullet.x + bullet.width > self.boss.x and
                    bullet.y < self.boss.y + self.boss.height and
                    bullet.y + bullet.height > self.boss.y):
                    
                    self.bullets.remove(bullet)
                    if self.boss.take_damage():
                        boss_points = 200 * self.boss.boss_type
                        self.score += boss_points
                        self.boss = None
                        self.wave += 1
                        self.create_enemies()
                    break
        
        else:
            # Regular enemy logic (only when no boss)
            if self.enemies:
                # Check if any enemy has hit the screen edge
                move_down = False
                leftmost_enemy = min(self.enemies, key=lambda e: e.x)
                rightmost_enemy = max(self.enemies, key=lambda e: e.x + e.width)
                
                if (leftmost_enemy.x <= 0 and leftmost_enemy.direction == -1) or \
                   (rightmost_enemy.x + rightmost_enemy.width >= SCREEN_WIDTH and rightmost_enemy.direction == 1):
                    move_down = True
                
                # Update all enemies together
                for enemy in self.enemies:
                    enemy.update(move_down)
                    
                    # Check if enemies reached the bottom
                    if enemy.y + enemy.height >= self.player.y:
                        self.game_over = True
                
                # Check bullet-enemy collisions
                for bullet in self.bullets[:]:
                    for enemy in self.enemies[:]:
                        if (bullet.x < enemy.x + enemy.width and
                            bullet.x + bullet.width > enemy.x and
                            bullet.y < enemy.y + enemy.height and
                            bullet.y + bullet.height > enemy.y):
                            
                            self.bullets.remove(bullet)
                            # Different points for different enemy types
                            points = [10, 20, 30][enemy.enemy_type]
                            self.score += points
                            self.enemies.remove(enemy)
                            break
                
                # Check if all enemies are destroyed
                if not self.enemies:
                    self.spawn_boss()
            
            elif not self.boss:
                self.spawn_boss()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw game objects
        if not self.game_over:
            self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw UFO
        self.ufo.draw(self.screen)
            
        # Draw boss if present
        if self.boss:
            self.boss.draw(self.screen)
        
        # Draw HUD
        score_text = self.font.render(f"SCORE: {self.score:06d}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 35))
        
        wave_text = self.font.render(f"WAVE: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 120, 10))
        
        if self.boss:
            boss_text = self.font.render(f"BOSS LEVEL {self.boss.boss_type}", True, YELLOW)
            text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, 25))
            self.screen.blit(boss_text, text_rect)
            
        # Draw bonus UFO indicator
        if self.ufo.active:
            bonus_text = self.font.render("BONUS UFO!", True, RED)
            self.screen.blit(bonus_text, (SCREEN_WIDTH//2 - 50, 50))
        
        # Draw game over or win message
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press R to restart", True, WHITE)
            text_rect2 = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(restart_text, text_rect2)
        elif self.win:
            win_text = self.big_font.render("CONGRATULATIONS!", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(win_text, text_rect)
            
            restart_text = self.font.render("Press R to restart", True, WHITE)
            text_rect2 = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(restart_text, text_rect2)
        
        # Draw instructions at bottom
        if not self.game_over and not self.win:
            instructions = [
                "MOVE: A/D or Arrow Keys  |  SHOOT: SPACE  |  Destroy all invaders!"
            ]
            for i, instruction in enumerate(instructions):
                text = pygame.font.Font(None, 20).render(instruction, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30 + i * 20))
                self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.player = Player(SCREEN_WIDTH // 2 - 13, SCREEN_HEIGHT - 60)
        self.bullets = []
        self.enemies = []
        self.boss = None
        self.ufo = UFO()
        self.score = 0
        self.wave = 1
        self.boss_level = 0
        self.game_over = False
        self.win = False
        self.lives = 3
        self.create_enemies()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()