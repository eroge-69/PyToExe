import pygame
from pygame.locals import *

pygame.init()

# --- Grundeinstellungen ---
FPS = 120
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
screen_w, screen_h = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("Jump & Run - Multi Level mit Kamera und beweglichen Plattformen")

# --- Farben ---
SKY = (135, 206, 235)
GROUND_COLOR = (100, 180, 100)
PLATFORM_COLOR = (120, 120, 120)
PLAYER_COLOR = (200, 50, 50)
BLACK = (0, 0, 0)

# --- Fonts ---
font = pygame.font.SysFont(None, 28)

# --- Spieler ---
player_w, player_h = 40, 60
player_rect = pygame.Rect(100, 100, player_w, player_h)
player_x = float(player_rect.x)
player_y = float(player_rect.y)
player_speed = 6.0
player_vel_y = 0.0
GRAVITY = 0.6
JUMP_POWER = 16.0

# --- Jump-Buffer + Coyote-Time ---
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.12
time_since_left_ground = 0.0
jump_buffer_timer = 0.0

# --- Kamera ---
camera_x = 0.0

# --- Levelerstellung ---
def make_levels(w, h):
    return [
        # Level 1 – einfache Sprünge
        [
            pygame.Rect(0, h - 40, w * 2, 40),
            pygame.Rect(int(0.25*w), h - 150, int(0.20*w), 20),
            pygame.Rect(int(0.55*w), h - 230, int(0.20*w), 20),
            pygame.Rect(int(0.85*w), h - 310, int(0.20*w), 20),
        ],
        # Level 2 – schwieriger, aber machbar
        [
            pygame.Rect(0, h - 40, w * 2, 40),
            pygame.Rect(int(0.15*w), h - 130, int(0.18*w), 20),
            pygame.Rect(int(0.40*w), h - 200, int(0.18*w), 20),
            pygame.Rect(int(0.65*w), h - 270, int(0.18*w), 20),
            pygame.Rect(int(0.90*w), h - 340, int(0.18*w), 20),
        ],
        # Level 3 – bewegliche Plattformen
        [
            pygame.Rect(0, h - 40, w * 2, 40),
            {"rect": pygame.Rect(int(0.25*w), h - 180, int(0.20*w), 20), "dir": 1, "range": 200, "speed": 2},
            {"rect": pygame.Rect(int(0.7*w), h - 280, int(0.20*w), 20), "dir": -1, "range": 250, "speed": 2},
        ],
    ]

levels = make_levels(screen_w, screen_h)
current_level = 0
platforms = levels[current_level]

def load_level(idx):
    global current_level, platforms, player_x, player_y, player_vel_y, time_since_left_ground, camera_x
    current_level = idx
    platforms = levels[current_level]
    player_x, player_y = 100.0, 100.0
    player_vel_y = 0.0
    time_since_left_ground = 0.0
    camera_x = 0.0
    player_rect.topleft = (int(player_x), int(player_y))

# --- Spielschleife ---
running = True
on_ground = False

while running:
    dt = clock.tick(FPS) / 1000.0  # Sekunden seit letztem Frame

    # --- Events ---
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                jump_buffer_timer = JUMP_BUFFER_TIME
            if event.key == K_ESCAPE:
                running = False
            if event.key == pygame.K_F11:
                # Fullscreen toggle
                screen = pygame.display.set_mode((0,0), FULLSCREEN) if screen.get_flags() & FULLSCREEN == 0 else pygame.display.set_mode((0,0))
                screen_w, screen_h = screen.get_size()
                levels = make_levels(screen_w, screen_h)
                load_level(min(current_level, len(levels)-1))

    keys = pygame.key.get_pressed()

    # --- Horizontalbewegung ---
    move_x = 0
    if keys[K_LEFT] or keys[K_a]:
        move_x = -player_speed
    if keys[K_RIGHT] or keys[K_d]:
        move_x = player_speed

    player_x += move_x
    player_rect.x = int(player_x)

    # --- Seitliche Kollision ---
    for plat in platforms:
        if isinstance(plat, dict):
            rect = plat["rect"]
        else:
            rect = plat
        if player_rect.colliderect(rect):
            if move_x > 0:
                player_x = rect.left - player_rect.width
            elif move_x < 0:
                player_x = rect.right
            player_rect.x = int(player_x)

    # --- Vertikalphysik ---
    player_vel_y += GRAVITY
    player_y += player_vel_y
    player_rect.y = int(player_y)
    on_ground = False

    for plat in platforms:
        if isinstance(plat, dict):
            rect = plat["rect"]
        else:
            rect = plat

        if player_rect.colliderect(rect):
            # Landen
            if player_vel_y > 0 and player_rect.bottom > rect.top and player_rect.centery < rect.top:
                player_y = rect.top - player_rect.height
                player_vel_y = 0
                on_ground = True
                player_rect.y = int(player_y)
            # Kopfstoß
            elif player_vel_y < 0 and player_rect.top < rect.bottom and player_rect.centery > rect.bottom:
                player_y = rect.bottom
                player_vel_y = 0
                player_rect.y = int(player_y)

    # --- Jump Buffer + Coyote Time ---
    if on_ground:
        time_since_left_ground = 0
    else:
        time_since_left_ground += dt

    if jump_buffer_timer > 0:
        jump_buffer_timer -= dt

    if (on_ground or time_since_left_ground <= COYOTE_TIME) and jump_buffer_timer > 0:
        player_vel_y = -JUMP_POWER
        jump_buffer_timer = 0
        on_ground = False

    # Variable Sprunghöhe (wenn Space losgelassen)
    if not keys[K_SPACE] and player_vel_y < 0:
        player_vel_y *= 0.5

    # --- Bewegliche Plattformen aktualisieren ---
    for plat in platforms:
        if isinstance(plat, dict):
            rect = plat["rect"]
            plat["range"] -= plat["speed"] * plat["dir"]
            rect.x += plat["speed"] * plat["dir"]
            if abs(plat["range"]) <= 0:
                plat["dir"] *= -1
                plat["range"] = 200  # neue Bewegungsspanne

    # --- Kamera folgt Spieler ---
    camera_x = player_rect.centerx - screen_w // 2
    if camera_x < 0:
        camera_x = 0

    # --- Levelwechsel & Reset ---
    if player_rect.right - camera_x > screen_w:
        if current_level < len(levels) - 1:
            load_level(current_level + 1)
        else:
            print("🎉 Alle Level geschafft!")
            running = False

    if player_rect.top > screen_h:
        load_level(current_level)

    # --- Zeichnen ---
    screen.fill(SKY)
    for idx, plat in enumerate(platforms):
        color = GROUND_COLOR if (not isinstance(plat, dict) and idx == 0) else PLATFORM_COLOR
        rect = plat["rect"] if isinstance(plat, dict) else plat
        draw_rect = rect.move(-camera_x, 0)
        pygame.draw.rect(screen, color, draw_rect)

    pygame.draw.rect(screen, PLAYER_COLOR, player_rect.move(-camera_x, 0))
    info = f"Level {current_level+1}/{len(levels)} | A/D oder Pfeile = Laufen | SPACE = Springen | ESC = Beenden | F11 = Fullscreen"
    screen.blit(font.render(info, True, BLACK), (20, 20))

    pygame.display.flip()

pygame.quit()

