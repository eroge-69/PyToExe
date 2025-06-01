import pygame
import random
import sys
import os
import subprocess

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THROTTLE - version 0.2")

# Colors
GRAY = (50, 50, 50)
SMOKE_GRAY = (120, 120, 120)
SKID_COLOR = (20, 20, 20, 120)
FIRE_COLOR = (255, 100, 0, 180)
DARK_GRAY = (30, 30, 30)
BLACK = (0, 0, 0)
BUTTON_COLOR = (80, 80, 80)
HOVER_COLOR = (120, 120, 120)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
FPS = 60

CAR_WIDTH, CAR_HEIGHT = 32, 64
player_x = WIDTH // 2 - CAR_WIDTH // 2
player_y = HEIGHT - CAR_HEIGHT - 80
player_speed = 5

HITBOX_MARGIN_X = 6
HITBOX_MARGIN_Y = 12

CURRENT_DIR = os.path.dirname(__file__)
ASSETS_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "assets"))
FONT_PATH = os.path.join(ASSETS_PATH, "font.ttf")
TITLE_FONT_PATH = os.path.join(ASSETS_PATH, "title_font.ttf")

# Fonts
title_font = pygame.font.Font(TITLE_FONT_PATH, 25)
button_font = pygame.font.Font(FONT_PATH, 28)

# Button class
class Button:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = HOVER_COLOR if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

# Load assets
player_img = pygame.image.load(os.path.join(ASSETS_PATH, "driver.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (CAR_WIDTH, CAR_HEIGHT))

enemy_base_img = pygame.image.load(os.path.join(ASSETS_PATH, "car.png")).convert_alpha()
enemy_base_img = pygame.transform.scale(enemy_base_img, (CAR_WIDTH, CAR_HEIGHT))

road_texture = pygame.image.load(os.path.join(ASSETS_PATH, "road.png")).convert()
TILE_SIZE = 128
road_texture = pygame.transform.scale(road_texture, (TILE_SIZE, TILE_SIZE))

police_img = pygame.image.load(os.path.join(ASSETS_PATH, "police.png")).convert_alpha()
police_img = pygame.transform.scale(police_img, (CAR_WIDTH, CAR_HEIGHT))
police_y = player_y + 80
police_x = player_x
police_speed = 0.03

# Sounds
crash_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "crash.mp3"))
honk_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "honk.mp3"))
turn_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "turn.mp3"))
turn_sound.set_volume(0.5)

# Background Music
pygame.mixer.music.load(os.path.join(ASSETS_PATH, "song.wav"))
pygame.mixer.music.play(-1)

# Police Sirens
police_sirens = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "policesirens.mp3"))
police_sirens.set_volume(0.2)
police_sirens.play(-1)

enemy_speed = 5
enemy_spawn_delay = 600
last_enemy_spawn_time = pygame.time.get_ticks()
enemies = []

particles = []
skid_marks = []

turning_sound_playing = False

# --- Utility functions ---

def tint_surface(image, tint_color):
    tinted_image = image.copy()
    tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint.fill(tint_color)
    tinted_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

def spawn_enemy():
    count = random.randint(1, 3)
    attempts = 0
    spawned = 0
    max_attempts_per_enemy = 10

    while spawned < count and attempts < count * max_attempts_per_enemy:
        x = random.randint(0, WIDTH - CAR_WIDTH)
        dx = 0 if random.random() < 0.75 else random.choice([-1, 1]) * random.uniform(0.3, 1.0)
        rect = pygame.Rect(x + HITBOX_MARGIN_X // 2, -CAR_HEIGHT + HITBOX_MARGIN_Y // 2,
                           CAR_WIDTH - HITBOX_MARGIN_X, CAR_HEIGHT - HITBOX_MARGIN_Y)

        overlap = any(rect.colliderect(e['rect'].inflate(10, 0)) for e in enemies)
        if not overlap:
            tinted_img = tint_surface(enemy_base_img, (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255),
                255
            ))
            enemies.append({
                'rect': rect,
                'dx': dx,
                'dy': enemy_speed,
                'img_orig': tinted_img,
                'img': tinted_img,
                'angle': 0,
                'crashed': False,
                'rotation_speed': 0,
            })
            spawned += 1
        attempts += 1

def create_smoke(x, y):
    particles.append({'x': x, 'y': y, 'radius': 3, 'alpha': 100})

def create_fire(x, y):
    particles.append({
        'x': x + random.randint(-5, 5),
        'y': y + random.randint(-5, 5),
        'radius': random.uniform(2, 5),
        'alpha': 180,
        'color': FIRE_COLOR,
        'dy': random.uniform(-1.5, -0.5),
        'dx': random.uniform(-0.5, 0.5),
    })

def create_skid_mark(x, y):
    skid_marks.append({'x': x, 'y': y, 'width': 10, 'height': 3, 'alpha': 120})

def update_particles():
    for particle in particles[:]:
        particle['y'] += particle.get('dy', 1)
        particle['x'] += particle.get('dx', 0)
        particle['radius'] -= 0.15
        particle['alpha'] -= 7
        if particle['radius'] <= 0 or particle['alpha'] <= 0:
            particles.remove(particle)
        else:
            size = int(particle['radius'] * 2)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            color = particle.get('color', SMOKE_GRAY)
            pygame.draw.circle(
                surf,
                (color[0], color[1], color[2], int(particle['alpha'])),
                (size // 2, size // 2),
                int(particle['radius'])
            )
            screen.blit(surf, (particle['x'], particle['y']))

def update_skid_marks():
    for skid in skid_marks[:]:
        skid['alpha'] -= 1
        skid['y'] += 1
        if skid['alpha'] <= 0:
            skid_marks.remove(skid)
        else:
            surf = pygame.Surface((skid['width'], skid['height']), pygame.SRCALPHA)
            surf.fill((SKID_COLOR[0], SKID_COLOR[1], SKID_COLOR[2], int(skid['alpha'])))
            screen.blit(surf, (skid['x'], skid['y']))

def show_death_screen():
    crash_sound.play()
    respawn_button = Button("Respawn", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, 'respawn')
    menu_button = Button("Menu", WIDTH // 2 - 75, HEIGHT // 2 + 70, 150, 50, 'menu')
    buttons = [respawn_button, menu_button]

    death_particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT),
                        'size': random.randint(2, 5), 'speed': random.uniform(0.5, 1.5)} for _ in range(50)]

    while True:
        screen.fill(DARK_GRAY)
        for p in death_particles:
            p['y'] += p['speed']
            if p['y'] > HEIGHT:
                p['y'] = 0
                p['x'] = random.randint(0, WIDTH)
            pygame.draw.circle(screen, BLACK, (int(p['x']), int(p['y'])), p['size'])

        title_surf = title_font.render("You Crashed", True, (200, 0, 0))
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.rect.collidepoint(event.pos):
                        if btn.action == 'respawn':
                            return 'respawn'
                        elif btn.action == 'menu':
                            subprocess.Popen(["python", os.path.join(CURRENT_DIR, "menu.py")])
                            pygame.quit()
                            sys.exit()

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Main game loop
running = True
while running:
    clock.tick(FPS)

    # Draw road
    for y in range(0, HEIGHT, TILE_SIZE):
        for x in range(0, WIDTH, TILE_SIZE):
            screen.blit(road_texture, (x, y))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            honk_sound.play()

    # Player movement
    keys = pygame.key.get_pressed()
    turning_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    turning_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

    if turning_left or turning_right:
        if not turning_sound_playing:
            turn_sound.play(-1)
            turning_sound_playing = True
    else:
        if turning_sound_playing:
            turn_sound.stop()
            turning_sound_playing = False

    if turning_left:
        player_x -= player_speed
    if turning_right:
        player_x += player_speed

    player_x = max(0, min(player_x, WIDTH - CAR_WIDTH))

    # Police follows with delay
    police_x += (player_x - police_x) * police_speed
    screen.blit(police_img, (police_x, police_y))

    # Rects
    player_rect = pygame.Rect(player_x + HITBOX_MARGIN_X // 2,
                              player_y + HITBOX_MARGIN_Y // 2,
                              CAR_WIDTH - HITBOX_MARGIN_X,
                              CAR_HEIGHT - HITBOX_MARGIN_Y)

    # Effects
    create_smoke(player_x + CAR_WIDTH // 2 - 2, player_y + CAR_HEIGHT - 5)

    if turning_left or turning_right:
        create_skid_mark(player_x + 6, player_y + CAR_HEIGHT - 10)
        create_skid_mark(player_x + CAR_WIDTH - 16, player_y + CAR_HEIGHT - 10)

    # Enemies
    if pygame.time.get_ticks() - last_enemy_spawn_time > enemy_spawn_delay:
        spawn_enemy()
        last_enemy_spawn_time = pygame.time.get_ticks()

    for enemy in enemies[:]:
        enemy['rect'].y += enemy['dy']
        enemy['rect'].x += enemy['dx']
        if enemy['rect'].left < HITBOX_MARGIN_X // 2 or enemy['rect'].right > WIDTH - HITBOX_MARGIN_X // 2:
            enemy['dx'] *= -1
        if enemy['rect'].top > HEIGHT:
            enemies.remove(enemy)

    # Crashes
    for i, enemy1 in enumerate(enemies):
        for j in range(i + 1, len(enemies)):
            enemy2 = enemies[j]
            if enemy1['rect'].colliderect(enemy2['rect']):
                for e in (enemy1, enemy2):
                    if not e['crashed']:
                        e['crashed'] = True
                        e['rotation_speed'] = random.uniform(-5, 5)
                        crash_sound.play()

    for enemy in enemies:
        if enemy['crashed']:
            enemy['angle'] += enemy['rotation_speed']
            create_fire(enemy['rect'].centerx, enemy['rect'].centery)
        else:
            enemy['angle'] += random.uniform(-1, 1)
            enemy['angle'] = max(min(enemy['angle'], 20), -20)

    for enemy in enemies:
        if not enemy['crashed'] and player_rect.colliderect(enemy['rect']):
            result = show_death_screen()
            if result == 'respawn':
                enemies.clear()
                particles.clear()
                skid_marks.clear()
                player_x = WIDTH // 2 - CAR_WIDTH // 2
                police_x = player_x
                last_enemy_spawn_time = pygame.time.get_ticks()
                break

    update_particles()
    update_skid_marks()

    # Draw player
    screen.blit(player_img, (player_x, player_y))

    # Draw enemies
    for enemy in enemies:
        rotated_img = pygame.transform.rotate(enemy['img_orig'], enemy['angle'])
        new_rect = rotated_img.get_rect(center=enemy['rect'].center)
        screen.blit(rotated_img, new_rect.topleft)

    pygame.display.flip()

pygame.quit()
sys.exit()
