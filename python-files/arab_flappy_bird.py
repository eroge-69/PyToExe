import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_SPEED = 3

# Colors (Arab-themed palette)
DESERT_SAND = (238, 203, 173)
GOLDEN_YELLOW = (255, 215, 0)
DEEP_BLUE = (0, 100, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.radius = 20
        
    def jump(self):
        self.velocity = JUMP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
    def draw(self, screen):
        # Draw bird as a golden circle with Arabic-style decoration
        pygame.draw.circle(screen, GOLDEN_YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # Eye
        pygame.draw.circle(screen, BLACK, (int(self.x + 8), int(self.y - 5)), 3)
        # Beak
        pygame.draw.polygon(screen, (255, 140, 0), 
                          [(int(self.x + self.radius), int(self.y)), 
                           (int(self.x + self.radius + 10), int(self.y - 3)),
                           (int(self.x + self.radius + 10), int(self.y + 3))])

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Top pipe (minaret style)
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(screen, DEEP_BLUE, (self.x, 0, PIPE_WIDTH, self.height), 3)
        # Minaret top
        pygame.draw.rect(screen, GOLDEN_YELLOW, (self.x - 5, self.height - 20, PIPE_WIDTH + 10, 20))
        
        # Bottom pipe (minaret style)
        bottom_y = self.height + PIPE_GAP
        pygame.draw.rect(screen, GREEN, (self.x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y))
        pygame.draw.rect(screen, DEEP_BLUE, (self.x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y), 3)
        # Minaret top
        pygame.draw.rect(screen, GOLDEN_YELLOW, (self.x - 5, bottom_y, PIPE_WIDTH + 10, 20))
        
    def collides_with(self, bird):
        if (bird.x + bird.radius > self.x and bird.x - bird.radius < self.x + PIPE_WIDTH):
            if (bird.y - bird.radius < self.height or bird.y + bird.radius > self.height + PIPE_GAP):
                return True
        return False

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arab Flappy Bird - الطائر العربي")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
        
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    elif self.game_over:
                        self.reset_game()
                    else:
                        self.bird.jump()
        return True
        
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        self.bird.update()
        
        # Check ground/ceiling collision
        if self.bird.y > SCREEN_HEIGHT - self.bird.radius or self.bird.y < self.bird.radius:
            self.game_over = True
            
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.x + PIPE_WIDTH < 0:
                self.pipes.remove(pipe)
            if pipe.collides_with(self.bird):
                self.game_over = True
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                
        # Add new pipes
        if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - 200:
            self.pipes.append(Pipe(SCREEN_WIDTH))
            
    def draw_background(self):
        # Desert gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(DESERT_SAND[0] + (DEEP_BLUE[0] - DESERT_SAND[0]) * color_ratio * 0.3)
            g = int(DESERT_SAND[1] + (DEEP_BLUE[1] - DESERT_SAND[1]) * color_ratio * 0.3)
            b = int(DESERT_SAND[2] + (DEEP_BLUE[2] - DESERT_SAND[2]) * color_ratio * 0.3)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
    def draw(self):
        self.draw_background()
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
            
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_shadow = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_shadow, (12, 12))
        self.screen.blit(score_text, (10, 10))
        
        # Draw instructions or game over
        if not self.game_started:
            title_text = self.font.render("Arab Flappy Bird", True, GOLDEN_YELLOW)
            arabic_text = self.small_font.render("الطائر العربي", True, GOLDEN_YELLOW)
            instruction_text = self.small_font.render("Press SPACE to start", True, WHITE)
            
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 200))
            self.screen.blit(arabic_text, (SCREEN_WIDTH//2 - arabic_text.get_width()//2, 240))
            self.screen.blit(instruction_text, (SCREEN_WIDTH//2 - instruction_text.get_width()//2, 300))
            
        elif self.game_over:
            game_over_text = self.font.render("Game Over!", True, WHITE)
            final_score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 250))
            self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, 290))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 320))
            
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()