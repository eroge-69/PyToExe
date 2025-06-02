import pygame
import random

# Initialize Pygame
pygame.init()

# Set screen dimensions and create display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet Rampage")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 36)

# Player class
class Player:
    def __init__(self):
        self.image = pygame.Surface((40, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = 100
        self.ammo = 50
        self.speed = 5

    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Bullet class
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        dx = target_x - x
        dy = target_y - y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.1)
        self.vel_x = dx / dist * self.speed
        self.vel_y = dy / dist * self.speed

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self):
        screen.blit(self.image, self.rect)

    def off_screen(self):
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT)

# Enemy class
class Enemy:
    def __init__(self):
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.speed = random.uniform(1, 3)

    def update(self, player_pos):
        dx = player_pos[0] - self.rect.x
        dy = player_pos[1] - self.rect.y
        dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.1)
        self.rect.x += dx / dist * self.speed
        self.rect.y += dy / dist * self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Game variables
player = Player()
bullets = []
enemies = [Enemy() for _ in range(5)]
score = 0

clock = pygame.time.Clock()

running = True
while running:
    clock.tick(60)  # 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player.ammo > 0:
                mx, my = pygame.mouse.get_pos()
                bullet = Bullet(player.rect.centerx, player.rect.centery, mx, my)
                bullets.append(bullet)
                player.ammo -= 1

    keys = pygame.key.get_pressed()
    player.move(keys)

    # Update bullets
    for bullet in bullets[:]:
        bullet.update()
        if bullet.off_screen():
            bullets.remove(bullet)

    # Update enemies
    for enemy in enemies:
        enemy.update(player.rect.center)

    # Check collisions
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.rect.colliderect(bullet.rect):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                enemies.append(Enemy())
                break

    # Drawing
    screen.fill(BLACK)
    player.draw()
    for bullet in bullets:
        bullet.draw()
    for enemy in enemies:
        enemy.draw()

    # Draw HUD
    health_text = font.render(f'Health: {player.health}', True, WHITE)
    ammo_text = font.render(f'Ammo: {player.ammo}', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(ammo_text, (10, 50))
    screen.blit(score_text, (10, 90))

    pygame.display.flip()

pygame.quit()





pip install pyinstaller

