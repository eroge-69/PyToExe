import pygame
import random
import sys

# Ustawienia
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
FPS = 60

# Inicjalizacja
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Buble Clicker")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

# Wczytanie tła i skalowanie
bg_raw = pygame.image.load("bubletlo.png").convert()
background_img = pygame.transform.scale(bg_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Wczytanie grafiki bublów
bubble_img = pygame.image.load("bubel.png").convert_alpha()

# Wczytanie dźwięku
try:
    pop_sound = pygame.mixer.Sound("bubel.mp3")
except:
    pop_sound = None

# Dane kolorów i punktów
COLOR_DATA = [
    ("szary", (150, 150, 150), 1, 50),
    ("zielony", (0, 200, 0), 2, 25),
    ("niebieski", (50, 120, 255), 3, 15),
    ("fioletowy", (160, 0, 220), 5, 5),
    ("czerwony", (179, 0, 0), 10, 4),
    ("złoty", (255, 215, 0), 50, 1)
]

# Wynik i modyfikatory
score = 0
spawn_rate = 30
points_multiplier = 1
upgrade_buble_more = False
upgrade_buble_double = False

# Sklep
shop_open = False
shop_x = SCREEN_WIDTH
target_shop_x = SCREEN_WIDTH
shop_width = 300
shop_height = 200

# Kolorowanie bublów
def colorize(image, color):
    colored = image.copy()
    overlay = pygame.Surface(colored.get_size(), pygame.SRCALPHA)
    overlay.fill(color + (0,))
    colored.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return colored

# Losowanie koloru
def pick_color_variant():
    variants = COLOR_DATA
    weights = [c[3] for c in variants]
    chosen = random.choices(variants, weights=weights, k=1)[0]
    return chosen[0], chosen[1], chosen[2]

# Klasa bublów
class Bubble:
    def __init__(self):
        self.name, self.color, self.points = pick_color_variant()
        self.scale = random.uniform(0.2, 0.5)
        scale_factor = 1 / 8 * self.scale
        img = colorize(bubble_img, self.color)
        self.image_original = pygame.transform.rotozoom(img, 0, scale_factor)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, max(0, SCREEN_WIDTH - self.rect.width))
        self.rect.y = SCREEN_HEIGHT + random.randint(0, 100)
        self.speed = random.uniform(1.0, 3.0)
        self.popped = False
        self.pop_time = 0
        self.animation_duration = 300

    def move(self):
        if not self.popped:
            self.rect.y -= self.speed

    def draw(self, surface):
        if self.popped:
            elapsed = pygame.time.get_ticks() - self.pop_time
            progress = elapsed / self.animation_duration
            if progress <= 1.0:
                scale = max(0.1, 1 - progress)
                alpha = max(0, 255 * (1 - progress))
                img = pygame.transform.rotozoom(self.image_original, 0, scale)
                img.set_alpha(alpha)
                rect = img.get_rect(center=self.rect.center)
                surface.blit(img, rect)
        else:
            surface.blit(self.image, self.rect)

    def pop(self):
        global score
        self.popped = True
        self.pop_time = pygame.time.get_ticks()
        score += self.points * points_multiplier
        if pop_sound:
            pop_sound.play()

    def is_done(self):
        return self.popped and pygame.time.get_ticks() - self.pop_time > self.animation_duration

# Lista bublów
bubbles = []
spawn_timer = 0

# Główna pętla gry
running = True
while running:
    clock.tick(FPS)
    screen.blit(background_img, (0, 0))

    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Kliknięcie w przycisk SHOP
            if SCREEN_WIDTH - 120 < mx < SCREEN_WIDTH - 20 and 50 < my < 80:
                shop_open = not shop_open
                target_shop_x = SCREEN_WIDTH - shop_width if shop_open else SCREEN_WIDTH

            # Kliknięcie w przyciski w sklepie
            if shop_open and shop_x <= SCREEN_WIDTH - shop_width + 10:
                if target_shop_x + 20 < mx < target_shop_x + 280:
                    # Więcej bublów za 100
                    if 70 < my < 110 and not upgrade_buble_more and score >= 100:
                        score -= 100
                        spawn_rate = 15
                        upgrade_buble_more = True
                    # 2x buble za 500
                    elif 120 < my < 160 and not upgrade_buble_double and score >= 500:
                        score -= 500
                        points_multiplier = 2
                        upgrade_buble_double = True
            else:
                for b in bubbles:
                    if not b.popped and b.rect.collidepoint((mx, my)):
                        b.pop()
                        break

    # Animacja sklepu
    shop_x += (target_shop_x - shop_x) * 0.3

    # Spawnowanie bublów
    spawn_timer += 1
    if spawn_timer > spawn_rate:
        bubbles.append(Bubble())
        spawn_timer = 0

    # Aktualizacja i rysowanie
    for b in bubbles[:]:
        b.move()
        b.draw(screen)
        if b.is_done() or (not b.popped and b.rect.bottom < 0):
            bubbles.remove(b)

    # HUD: tytuł i wynik
    screen.blit(font.render("Buble Clicker", True, (0, 0, 0)), (10, 10))
    wynik_txt = font.render(f"Wynik: {score}", True, (0, 0, 0))
    screen.blit(wynik_txt, (SCREEN_WIDTH - 220, 10))

    # Przycisk SHOP poniżej wyniku
    pygame.draw.rect(screen, (30, 144, 255), (SCREEN_WIDTH - 120, 50, 100, 30), border_radius=8)
    shop_txt = font.render("SHOP", True, (255, 255, 255))
    screen.blit(shop_txt, (SCREEN_WIDTH - 100, 52))

    # Panel sklepu
    if shop_x < SCREEN_WIDTH:
        shop_surface = pygame.Surface((shop_width, shop_height), pygame.SRCALPHA)
        shop_surface.fill((0, 0, 0, 180))  # ciemne półprzezroczyste tło
        screen.blit(shop_surface, (shop_x, 50))
        pygame.draw.rect(screen, (255, 255, 255), (shop_x, 50, shop_width, shop_height), 2)

        # Przycisk: więcej bublów
        pygame.draw.rect(screen, (0, 200, 0), (shop_x + 20, 70, 260, 30), border_radius=6)
        label1 = "Kup: Więcej bublów (100)" if not upgrade_buble_more else "✔ Kupiono: Więcej bublów"
        screen.blit(font.render(label1, True, (255, 255, 255)), (shop_x + 25, 72))

        # Przycisk: 2x buble
        pygame.draw.rect(screen, (0, 100, 200), (shop_x + 20, 120, 260, 30), border_radius=6)
        label2 = "Kup: 2x buble (500)" if not upgrade_buble_double else "✔ Kupiono: 2x buble"
        screen.blit(font.render(label2, True, (255, 255, 255)), (shop_x + 25, 122))

    pygame.display.flip()

pygame.quit()
sys.exit()
