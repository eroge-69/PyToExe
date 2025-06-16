import pygame
import random
import sys

# Inicjalizacja
pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = 40
PLAYER_SPEED = 5
ENEMY_SPEED = 2
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Ekran i czcionka
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wiaterowa Bitwa")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

TILE_SIZE = 100
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

# Zmienne globalne
control_scheme = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "shoot_up": pygame.K_UP, "shoot_down": pygame.K_DOWN, "shoot_left": pygame.K_LEFT, "shoot_right": pygame.K_SPACE}
graphics_mode = "basic"
game_mode = "easy"

# Przycisk
def draw_button(text, x, y, w, h):
    pygame.draw.rect(screen, GRAY, (x, y, w, h))
    txt = font.render(text, True, BLACK)
    screen.blit(txt, (x + 10, y + 10))
    return pygame.Rect(x, y, w, h)

# Ekran startowy

def start_screen():
    while True:
        screen.fill(WHITE)
        title = font.render("Wiaterowa Bitwa", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        play_btn = draw_button("GRAJ", WIDTH//2 - 75, 300, 150, 50)
        opt_btn = draw_button("OPCJE", WIDTH//2 - 75, 400, 150, 50)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(e.pos):
                    return "play"
                elif opt_btn.collidepoint(e.pos):
                    return "options"

# Wybór poziomu trudności

def difficulty_screen():
    global game_mode
    while True:
        screen.fill(WHITE)
        screen.blit(font.render("Wybierz poziom trudności", True, BLACK), (WIDTH//2 - 150, 150))

        easy_btn = draw_button("Łatwy", WIDTH//2 - 75, 250, 150, 50)
        hard_btn = draw_button("Trudny", WIDTH//2 - 75, 350, 150, 50)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn.collidepoint(e.pos):
                    game_mode = "easy"
                    return
                elif hard_btn.collidepoint(e.pos):
                    game_mode = "hard"
                    return

# Fighter klasa
class Fighter(pygame.sprite.Sprite):
    def __init__(self, x, y, control=False, health=100):
        super().__init__()
        self.control = control
        self.health = health
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.color = (0, 128, 255) if control else (255, 0, 0)
        self.rect = self.image.get_rect(center=(x, y))
        self.update_graphics()

    def update_graphics(self):
        self.image.fill(self.color)

    def update(self, player=None):
        if self.control:
            keys = pygame.key.get_pressed()
            dx = keys[control_scheme["right"]] - keys[control_scheme["left"]]
            dy = keys[control_scheme["down"]] - keys[control_scheme["up"]]
            self.rect.x += dx * PLAYER_SPEED
            self.rect.y += dy * PLAYER_SPEED
        else:
            if player:
                if self.rect.x < player.rect.x:
                    self.rect.x += ENEMY_SPEED
                elif self.rect.x > player.rect.x:
                    self.rect.x -= ENEMY_SPEED
                if self.rect.y < player.rect.y:
                    self.rect.y += ENEMY_SPEED
                elif self.rect.y > player.rect.y:
                    self.rect.y -= ENEMY_SPEED

                if self.rect.colliderect(player.rect):
                    player.health -= 1

# Pocisk
class Spear(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx * TILE_SIZE
        self.dy = dy * TILE_SIZE
        self.distance_traveled = 0

    def update(self):
        if self.distance_traveled >= 3 * TILE_SIZE:
            self.kill()
            return
        self.rect.x += self.dx // 3
        self.rect.y += self.dy // 3
        self.distance_traveled += abs(self.dx // 3) + abs(self.dy // 3)

# Główna gra

def main_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()

    hp = 100
    ammo = 15 if game_mode == "easy" else 25

    player = Fighter(100, HEIGHT//2, control=True, health=hp)

    for _ in range(5):
        x = random.randint(400, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        enemy_hp = 100 if game_mode == "easy" else 225
        enemy = Fighter(x, y, control=False, health=enemy_hp)
        enemies.add(enemy)
        all_sprites.add(enemy)

    all_sprites.add(player)

    # Sojusznicy
    for _ in range(3):
        x = random.randint(50, 300)
        y = random.randint(50, HEIGHT - 50)
        ally = Fighter(x, y, control=False, health=100)
        ally.color = GREEN
        ally.update_graphics()
        all_sprites.add(ally)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if ammo > 0:
                    if keys[control_scheme["shoot_right"]]:
                        projectiles.add(Spear(player.rect.centerx, player.rect.centery, 1, 0)); ammo -= 1
                    if keys[control_scheme["shoot_left"]]:
                        projectiles.add(Spear(player.rect.centerx, player.rect.centery, -1, 0)); ammo -= 1
                    if keys[control_scheme["shoot_up"]]:
                        projectiles.add(Spear(player.rect.centerx, player.rect.centery, 0, -1)); ammo -= 1
                    if keys[control_scheme["shoot_down"]]:
                        projectiles.add(Spear(player.rect.centerx, player.rect.centery, 0, 1)); ammo -= 1

        all_sprites.update(player)
        projectiles.update()

        for proj in projectiles:
            for enemy in enemies:
                if proj.rect.colliderect(enemy.rect):
                    enemy.health -= 25
                    proj.kill()
                    if enemy.health <= 0:
                        enemy.kill()

        screen.fill(WHITE)

        for x in range(0, WIDTH, TILE_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        all_sprites.draw(screen)
        projectiles.draw(screen)

        hp_text = font.render(f"HP: {player.health} | Amunicja: {ammo}", True, BLACK)
        screen.blit(hp_text, (10, 10))

        if player.health <= 0:
            end_text = font.render("Zgon – zostałeś rozjechany", True, RED)
            screen.blit(end_text, (WIDTH//2 - 200, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

        if ammo <= 0 and len(enemies) > 0:
            end_text = font.render("Przegrana – skończyła się amunicja!", True, RED)
            screen.blit(end_text, (WIDTH//2 - 250, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

        if len(enemies) == 0:
            win_text = font.render("Pokonałeś skurwieli!", True, GREEN)
            screen.blit(win_text, (WIDTH//2 - 200, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            return

        pygame.display.flip()

# Opcje

def options_screen():
    global control_scheme
    while True:
        screen.fill(WHITE)
        screen.blit(font.render("OPCJE", True, BLACK), (WIDTH//2 - 50, 100))

        wsad_btn = draw_button("Sterowanie: WSAD", WIDTH//2 - 150, 250, 300, 50)
        arrow_btn = draw_button("Sterowanie: Strzałki", WIDTH//2 - 150, 320, 300, 50)
        back_btn = draw_button("Wróć", WIDTH//2 - 60, 450, 120, 50)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if wsad_btn.collidepoint(e.pos):
                    control_scheme = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "shoot_up": pygame.K_UP, "shoot_down": pygame.K_DOWN, "shoot_left": pygame.K_LEFT, "shoot_right": pygame.K_SPACE}
                elif arrow_btn.collidepoint(e.pos):
                    control_scheme = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "shoot_up": pygame.K_w, "shoot_down": pygame.K_s, "shoot_left": pygame.K_a, "shoot_right": pygame.K_SPACE}
                elif back_btn.collidepoint(e.pos):
                    return

# Flow gry
while True:
    action = start_screen()
    if action == "play":
        difficulty_screen()
        main_game()
    elif action == "options":
        options_screen()

