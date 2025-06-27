# GULA CLICKER – pełna wersja z nagrodami, osiągnięciami, scrollowanym sklepem i efektami kliknięcia
import pygame
import sys
import time
import random

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gula Clicker")

try:
    FONT = pygame.font.Font("Montserrat-Bold.ttf", 28)
    FONT_SMALL = pygame.font.Font("Montserrat-Regular.ttf", 22)
except:
    FONT = pygame.font.SysFont("Arial", 28)
    FONT_SMALL = pygame.font.SysFont("Arial", 22)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 170, 50)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 100)

try:
    background_img = pygame.image.load("tapeta.jpg").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background_img = None
    print("Brak pliku tapeta.jpg")

try:
    gula_img = pygame.image.load("gula.png").convert_alpha()
    gula_img = pygame.transform.scale(gula_img, (300, 433))
except:
    print("Brak pliku gula.png")
    pygame.quit()
    sys.exit()

gula_rect = gula_img.get_rect(center=(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30))
scale = 1.0
scale_timer = 0

try:
    click_sound = pygame.mixer.Sound("click.wav")
except:
    click_sound = None
    print("Brak pliku click.wav")

score = 0
points_per_click = 1
points_per_second = 0
last_auto_click = time.time()

level = 1
level_cost = 1000
MAX_LEVEL = 100

cosmetics = 0
cosmetic_cost = 5000

shop_scroll = 0

achievements = []
particles = []

class Upgrade:
    def __init__(self, name, upgrade_type, amount, cost):
        self.name = name
        self.type = upgrade_type
        self.amount = amount
        self.cost = cost
        self.owned = 0
        self.rect = None

    def buy(self):
        self.owned += 1
        self.cost = int(self.cost * 1.5)

upgrades = []
for i in range(1, 21):
    if i % 2 == 0:
        upgrades.append(Upgrade(f"+{i}/s", "passive", i, 100 * i))
    else:
        upgrades.append(Upgrade(f"+{i*2}/click", "click", i*2, 100 * i))

upgrades.append(Upgrade("LEVEL", "level", 0, level_cost))
upgrades.append(Upgrade("GWIAZDKI", "cosmetic", 0, cosmetic_cost))

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255
        self.vel_y = -random.uniform(1, 2)
        self.size = random.randint(10, 20)

    def update(self):
        self.y += self.vel_y
        self.alpha -= 5
        return self.alpha > 0

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 0, self.alpha), (self.size // 2, self.size // 2), self.size // 2)
        surface.blit(s, (self.x, self.y))

def draw_shop(start_y):
    panel_x = SCREEN_WIDTH - 330
    panel_width = 310
    y = start_y - shop_scroll
    for upgrade in upgrades:
        rect = pygame.Rect(panel_x, y, panel_width, 80)
        pygame.draw.rect(screen, LIGHT_GRAY, rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, rect, 2, border_radius=10)
        label = f"{upgrade.name} ({upgrade.owned}) - ${upgrade.cost}"
        screen.blit(FONT_SMALL.render(label, True, BLACK), (panel_x + 10, y + 25))
        upgrade.rect = rect
        y += 90

def check_achievements():
    global achievements
    if score >= 1000 and "Zdobyto 1000 punktów!" not in achievements:
        achievements.append("Zdobyto 1000 punktów!")
    if level >= 10 and "Poziom 10 osiągnięty!" not in achievements:
        achievements.append("Poziom 10 osiągnięty!")
    if points_per_click >= 100 and "100 pkt/klik!" not in achievements:
        achievements.append("100 pkt/klik!")

def draw_achievements():
    y = SCREEN_HEIGHT - 30 * len(achievements)
    for ach in achievements:
        pygame.draw.rect(screen, YELLOW, (20, y, 360, 25), border_radius=5)
        screen.blit(FONT_SMALL.render(ach, True, BLACK), (30, y + 2))
        y += 30

clock = pygame.time.Clock()
running = True

while running:
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        screen.fill(ORANGE)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if gula_rect.collidepoint(event.pos):
                    score += points_per_click
                    scale = 0.9
                    scale_timer = time.time()
                    if click_sound:
                        click_sound.play()
                    for _ in range(5):
                        particles.append(Particle(gula_rect.centerx, gula_rect.centery))
                for upgrade in upgrades:
                    if upgrade.rect and upgrade.rect.collidepoint(event.pos):
                        if upgrade.type == "level":
                            if level < MAX_LEVEL and score >= level_cost:
                                score -= level_cost
                                level += 1
                                points_per_click += 1
                                if level % 10 == 0:
                                    points_per_click += int(points_per_click * 0.25)
                                    points_per_second += 10
                                level_cost = int(level_cost * 1.15)
                        elif upgrade.type == "cosmetic":
                            if score >= cosmetic_cost:
                                score -= cosmetic_cost
                                cosmetics += 1
                                cosmetic_cost = int(cosmetic_cost * 1.3)
                        elif score >= upgrade.cost:
                            score -= upgrade.cost
                            upgrade.buy()
                            if upgrade.type == "click":
                                points_per_click += upgrade.amount
                            elif upgrade.type == "passive":
                                points_per_second += upgrade.amount
            elif event.button == 4:
                shop_scroll = max(0, shop_scroll - 30)
            elif event.button == 5:
                shop_scroll += 30

    now = time.time()
    if now - last_auto_click >= 1:
        score += points_per_second
        last_auto_click = now

    if scale < 1.0 and time.time() - scale_timer > 0.1:
        scale = 1.0

    scaled_img = pygame.transform.scale(gula_img, (int(gula_img.get_width() * scale), int(gula_img.get_height() * scale)))
    scaled_rect = scaled_img.get_rect(center=gula_rect.center)
    screen.blit(scaled_img, scaled_rect)

    pygame.draw.rect(screen, WHITE, (30, 30, 300, 190), border_radius=10)
    pygame.draw.rect(screen, BLACK, (30, 30, 300, 190), 2, border_radius=10)
    screen.blit(FONT.render(f"Punkty: {score}", True, GREEN), (50, 40))
    screen.blit(FONT_SMALL.render(f"Na klik: {points_per_click}", True, BLACK), (50, 80))
    screen.blit(FONT_SMALL.render(f"Na sekundę: {points_per_second}", True, BLACK), (50, 110))
    screen.blit(FONT_SMALL.render(f"Poziom: {level} / {MAX_LEVEL}", True, BLACK), (50, 140))
    screen.blit(FONT_SMALL.render(f"Gwiazdki: {cosmetics}", True, BLACK), (50, 170))

    draw_shop(30)
    check_achievements()
    draw_achievements()

    # Animowane gwiazdki
    particles = [p for p in particles if p.update()]
    for p in particles:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
