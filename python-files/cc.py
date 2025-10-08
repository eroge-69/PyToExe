import pygame
import random
import math
import sys
from pygame import gfxdraw

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Security Intro")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)

# Fonts
title_font = pygame.font.SysFont('Courier New', 48, bold=True)
subtitle_font = pygame.font.SysFont('Courier New', 24)
binary_font = pygame.font.SysFont('Courier New', 16)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Matrix Rain Effect
class MatrixRain:
    def __init__(self):
        self.columns = WIDTH // 20
        self.drops = [1] * self.columns
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
    
    def draw(self, surface):
        surface.fill((0, 0, 0, 10), special_flags=pygame.BLEND_RGBA_SUB)
        for i in range(self.columns):
            char = random.choice(self.chars)
            x = i * 20
            y = self.drops[i] * 20
            
            # Draw character with fading effect
            alpha = 255 if y < HEIGHT else max(0, 255 - (y - HEIGHT) // 2)
            text = binary_font.render(char, True, (0, alpha, 0))
            surface.blit(text, (x, y))
            
            if y > HEIGHT and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1

# Binary Particles
class BinaryParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = random.choice(["0110", "1011", "1100", "1001"])
        self.speed = random.uniform(0.5, 1.5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 100
        self.max_life = 100
    
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y -= self.speed
        self.life -= 1
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        text = binary_font.render(self.value, True, (0, alpha, 0))
        surface.blit(text, (self.x, self.y))

# Shield Icon
class Shield:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 80
        self.pulse = 0
        self.particles = []
        self.particle_timer = 0
    
    def update(self):
        self.pulse += 0.05
        self.particle_timer += 1
        
        # Create new particles periodically
        if self.particle_timer % 20 == 0:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, 50)
            px = self.x + math.cos(angle) * dist
            py = self.y + math.sin(angle) * dist
            self.particles.append(BinaryParticle(px, py))
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self, surface):
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
        
        # Calculate pulse effect
        pulse_size = self.size + math.sin(self.pulse) * 10
        
        # Draw shield outline
        points = [
            (self.x, self.y - pulse_size),
            (self.x + pulse_size * 0.7, self.y - pulse_size * 0.7),
            (self.x + pulse_size * 0.7, self.y + pulse_size * 0.3),
            (self.x, self.y + pulse_size),
            (self.x - pulse_size * 0.7, self.y + pulse_size * 0.3),
            (self.x - pulse_size * 0.7, self.y - pulse_size * 0.7)
        ]
        
        # Draw shield with glow effect
        for i in range(5):
            alpha = 50 - i * 10
            glow_size = pulse_size + i * 5
            glow_points = [
                (self.x, self.y - glow_size),
                (self.x + glow_size * 0.7, self.y - glow_size * 0.7),
                (self.x + glow_size * 0.7, self.y + glow_size * 0.3),
                (self.x, self.y + glow_size),
                (self.x - glow_size * 0.7, self.y + glow_size * 0.3),
                (self.x - glow_size * 0.7, self.y - glow_size * 0.7)
            ]
            pygame.draw.polygon(surface, (0, alpha, 0), glow_points, 1)
        
        # Draw main shield
        pygame.draw.polygon(surface, GREEN, points, 3)
        
        # Draw checkmark
        checkmark_points = [
            (self.x - pulse_size * 0.3, self.y),
            (self.x - pulse_size * 0.1, self.y + pulse_size * 0.3),
            (self.x + pulse_size * 0.3, self.y - pulse_size * 0.2)
        ]
        pygame.draw.lines(surface, GREEN, False, checkmark_points, 4)

# Loading Bar
class LoadingBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.progress = 0
        self.percentage = 0
    
    def update(self):
        if self.progress < 100:
            self.progress += 0.5
            self.percentage = int(self.progress)
    
    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, DARK_GREEN, (self.x, self.y, self.width, self.height))
        
        # Draw progress
        progress_width = int(self.width * (self.progress / 100))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, progress_width, self.height))
        
        # Draw percentage text
        percentage_text = subtitle_font.render(f"{self.percentage}%", True, GREEN)
        text_rect = percentage_text.get_rect(center=(self.x + self.width // 2, self.y - 20))
        surface.blit(percentage_text, text_rect)

# Circuit Lines
class CircuitLine:
    def __init__(self, x1, y1, x2, y2, delay):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.delay = delay
        self.timer = 0
        self.active = False
        self.position = 0
    
    def update(self):
        self.timer += 1
        if self.timer > self.delay:
            self.active = True
            self.position += 5
            if self.position > 100:
                self.position = 0
    
    def draw(self, surface):
        if self.active:
            # Calculate current position
            current_x = self.x1 + (self.x2 - self.x1) * (self.position / 100)
            current_y = self.y1 + (self.y2 - self.y1) * (self.position / 100)
            
            # Draw line
            pygame.draw.line(surface, DARK_GREEN, (self.x1, self.y1), (self.x2, self.y2), 1)
            
            # Draw moving dot
            pygame.draw.circle(surface, GREEN, (int(current_x), int(current_y)), 3)

# Main function
def main():
    # Create objects
    matrix_rain = MatrixRain()
    shield = Shield(WIDTH // 2, HEIGHT // 2 - 50)
    loading_bar = LoadingBar(WIDTH // 2 - 150, HEIGHT - 100, 300, 10)
    
    # Create circuit lines
    circuit_lines = [
        CircuitLine(0, HEIGHT // 4, WIDTH, HEIGHT // 4, 0),
        CircuitLine(0, 3 * HEIGHT // 4, WIDTH, 3 * HEIGHT // 4, 30),
        CircuitLine(0, HEIGHT // 2, WIDTH // 2, HEIGHT // 2, 60),
        CircuitLine(WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT // 2, 90)
    ]
    
    # Title and subtitle
    title_alpha = 0
    subtitle_alpha = 0
    
    # Main loop
    running = True
    start_time = pygame.time.get_ticks()
    
    while running:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Fill background
        screen.fill(BLACK)
        
        # Draw matrix rain
        matrix_rain.draw(screen)
        
        # Update and draw circuit lines
        for line in circuit_lines:
            line.update()
            line.draw(screen)
        
        # Update and draw shield
        shield.update()
        shield.draw(screen)
        
        # Update title and subtitle alpha
        if elapsed > 0.5:
            title_alpha = min(255, int((elapsed - 0.5) * 500))
        if elapsed > 1.5:
            subtitle_alpha = min(255, int((elapsed - 1.5) * 500))
        
        # Draw title with glow effect
        if title_alpha > 0:
            title_text = title_font.render("CYBER SECURITY", True, GREEN)
            title_text.set_alpha(title_alpha)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            
            # Draw glow
            for i in range(5):
                glow_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
                glow_text = title_font.render("CYBER SECURITY", True, (0, 255 - i * 30, 0, 50 - i * 10))
                glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
                glow_surface.blit(glow_text, glow_rect)
                screen.blit(glow_surface, (title_rect.x - 10, title_rect.y - 10))
            
            screen.blit(title_text, title_rect)
        
        # Draw subtitle
        if subtitle_alpha > 0:
            subtitle_text = subtitle_font.render("Protecting Your Digital World", True, GREEN)
            subtitle_text.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
            screen.blit(subtitle_text, subtitle_rect)
        
        # Update and draw loading bar
        if elapsed > 2:
            loading_bar.update()
            loading_bar.draw(screen)
        
        # Check if 5 seconds have passed
        if elapsed >= 5:
            # Fade out effect
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.set_alpha(int((elapsed - 5) * 500))
            fade_surface.fill(BLACK)
            screen.blit(fade_surface, (0, 0))
            
            if elapsed >= 5.5:
                running = False
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()