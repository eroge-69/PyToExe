import pygame
import random
import sys

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Particle class
class Particle:
    def __init__(self):
        self.x = random.uniform(0, 800)
        self.y = random.uniform(0, 600)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.size = random.randint(2, 5)

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Wrap around screen
        if self.x < 0: self.x = 800
        if self.x > 800: self.x = 0
        if self.y < 0: self.y = 600
        if self.y > 600: self.y = 0

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)

# Create particles
particles = [Particle() for _ in range(100)]

# Main loop
while True:
    screen.fill((0, 0, 0))
    for particle in particles:
        particle.move()
        particle.draw()

    pygame.display.flip()
    clock.tick(60)

    # Exit on ESC or close
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
