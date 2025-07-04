import pygame
import sys
import math
import os
import platform
from collections import deque

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BETNAV v2.2.2")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 20)

base_dir = os.path.expanduser("~/Downloads/BETNAV")
asset_dir = os.path.join(base_dir, "betnav_screens")
logo_path = os.path.join(base_dir, "betnav_logo.png")

def load_image(path, fallback_size=(WIDTH, HEIGHT), fallback_color=(0, 0, 0)):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        surf = pygame.Surface(fallback_size)
        surf.fill(fallback_color)
        return surf

dpi_bg = load_image(os.path.join(asset_dir, "betnav_dpi.png"))
map_bg = load_image(os.path.join(asset_dir, "betnav_map_bg.png"))
logo_img = load_image(logo_path, fallback_size=(351, 407))

class State:
    def __init__(self):
        self.mode = "title"
        self.dpi_input = ""
        self.dpi = 800
        self.rotation_enabled = True
        self.zoom = 1.0
        self.player_pos = [0.0, 0.0]
        self.spawn_pos = [0.0, 0.0]
        self.facing_angle = -math.pi / 2
        self.path = deque()
        self.checkpoints = []
        self.roll_offset = 0
        self.sensitivity_multiplier = 1.0

S = State()

keys_pressed = set()
v_pressed_last_frame = False
x_pressed_last_frame = False
rotation_toggle_last_frame = False

prep_start_time = None

def apply_dpi():
    try:
        dpi = max(200, min(6400, int(S.dpi_input)))
        S.dpi = dpi
        S.mode = "prep"
        global prep_start_time
        prep_start_time = pygame.time.get_ticks()
    except ValueError:
        S.dpi_input = ""

def update_rotation(mouse_dx):
    if S.rotation_enabled and S.mode == "map":
        if mouse_dx != 0:
            pixels_per_rotation = 2600 * (S.dpi / 800)
            angle_per_pixel = 2 * math.pi / pixels_per_rotation
            S.facing_angle += mouse_dx * angle_per_pixel * S.sensitivity_multiplier

def update_movement():
    fx, fy = math.cos(S.facing_angle), math.sin(S.facing_angle)
    sx, sy = math.cos(S.facing_angle + math.pi / 2), math.sin(S.facing_angle + math.pi / 2)
    dx = dy = 0
    forward = 'w' in keys_pressed
    backward = 's' in keys_pressed
    left = 'a' in keys_pressed
    right = 'd' in keys_pressed
    shift = 'shift' in keys_pressed
    ctrl = 'ctrl' in keys_pressed
    if forward: dx += fx; dy += fy
    if backward: dx -= fx; dy -= fy
    if left: dx -= sx; dy -= sy
    if right: dx += sx; dy += sy
    if ctrl: speed = 1.0
    elif shift and forward: speed = 4.0
    else: speed = 2.0
    if dx or dy:
        mag = math.hypot(dx, dy)
        S.player_pos[0] += (dx / mag) * speed
        S.player_pos[1] += (dy / mag) * speed
        S.path.append(S.player_pos[:])
        if len(S.path) > 10000: S.path.popleft()

def draw_overlay_lines():
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y), 1)

def draw_rolling_overlay():
    S.roll_offset = (S.roll_offset + 1) % HEIGHT
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(HEIGHT):
        alpha = int(24 * (1 - abs(i - S.roll_offset) / HEIGHT))
        pygame.draw.line(overlay, (0, 0, 0, alpha), (0, i), (WIDTH, i))
    screen.blit(overlay, (0, 0))

def draw_spawn_circle():
    dx = (S.spawn_pos[0] - S.player_pos[0]) * S.zoom
    dy = (S.spawn_pos[1] - S.player_pos[1]) * S.zoom
    pygame.draw.circle(screen, (255, 255, 255), (CENTER_X + int(dx), CENTER_Y + int(dy)), int(6 * S.zoom))

def draw_path():
    for pt in S.path:
        dx = (pt[0] - S.player_pos[0]) * S.zoom
        dy = (pt[1] - S.player_pos[1]) * S.zoom
        pygame.draw.circle(screen, (0, 100, 0), (CENTER_X + int(dx), CENTER_Y + int(dy)), max(1, int(2 * S.zoom)))

def draw_checkpoints():
    for pt in S.checkpoints:
        dx = (pt[0] - S.player_pos[0]) * S.zoom
        dy = (pt[1] - S.player_pos[1]) * S.zoom
        size = int(6 * S.zoom)
        size = max(2, min(size, 32))
        rect = pygame.Rect(CENTER_X + dx - size // 2, CENTER_Y + dy - size // 2, size, size)
        pygame.draw.rect(screen, (255, 0, 0), rect)

def draw_player_arrow():
    a = S.facing_angle
    scale = 1.0 + S.zoom * 0.5
    p1 = (CENTER_X + math.cos(a) * 14 * scale, CENTER_Y + math.sin(a) * 14 * scale)
    p2 = (CENTER_X + math.cos(a + 2.5) * 8 * scale, CENTER_Y + math.sin(a + 2.5) * 8 * scale)
    p3 = (CENTER_X + math.cos(a - 2.5) * 8 * scale, CENTER_Y + math.sin(a - 2.5) * 8 * scale)
    pygame.draw.polygon(screen, (0, 255, 0), [p1, p2, p3])

def draw_sensitivity_display():
    msg1 = f"Sensitivity: {S.sensitivity_multiplier:.2f}"
    msg2 = "[ and ] to adjust"
    surf1 = font.render(msg1, True, (0, 255, 0))
    surf2 = font.render(msg2, True, (255, 255, 255))
    rect1 = surf1.get_rect(center=(CENTER_X, 40))
    rect2 = surf2.get_rect(center=(CENTER_X, 64))
    screen.blit(surf1, rect1)
    screen.blit(surf2, rect2)

def show_title_screen():
    screen.fill((0, 0, 0))
    logo_rect = logo_img.get_rect(center=(CENTER_X, CENTER_Y))
    screen.blit(logo_img, logo_rect)
    pygame.display.flip()
    pygame.time.wait(1500)
    S.mode = "dpi"

show_title_screen()
pygame.mouse.set_visible(True)
pygame.event.set_grab(False)
pygame.mouse.set_pos((CENTER_X, CENTER_Y))

while True:
    mouse_dx = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(pygame.key.name(event.key))
            if S.mode == "dpi":
                if event.key == pygame.K_BACKSPACE:
                    S.dpi_input = S.dpi_input[:-1]
                elif event.key == pygame.K_RETURN:
                    apply_dpi()
                elif event.unicode.isprintable() and len(S.dpi_input) < 6:
                    S.dpi_input += event.unicode
        elif event.type == pygame.KEYUP:
            keys_pressed.discard(pygame.key.name(event.key))
        elif event.type == pygame.MOUSEMOTION:
            mouse_dx += event.rel[0]

    # Recenter mouse every frame if rotating
    if S.rotation_enabled and S.mode == "map":
        pygame.mouse.set_pos((CENTER_X, CENTER_Y))

    if S.mode == "prep":
        elapsed = pygame.time.get_ticks() - prep_start_time
        if elapsed >= 10000:
            S.mode = "map"
        else:
            screen.fill((0, 0, 0))
            seconds_left = 10 - (elapsed // 1000)
            txt = font.render(f"Starting in {seconds_left} seconds...", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(CENTER_X, CENTER_Y)))
            pygame.display.flip()
            clock.tick(60)
            continue

    if S.mode == "map":
        update_rotation(mouse_dx)
        update_movement()

        if 'i' in keys_pressed: S.zoom = min(10.0, S.zoom * 1.01)
        if 'o' in keys_pressed: S.zoom = max(0.1, S.zoom * 0.99)
        if '[' in keys_pressed: S.sensitivity_multiplier = max(0.1, S.sensitivity_multiplier - 0.01)
        if ']' in keys_pressed: S.sensitivity_multiplier = min(5.0, S.sensitivity_multiplier + 0.01)

        if 'v' in keys_pressed and not v_pressed_last_frame:
            S.checkpoints.append(S.player_pos[:])
        v_pressed_last_frame = 'v' in keys_pressed

        if 'x' in keys_pressed and not x_pressed_last_frame:
            S.path.clear()
            S.checkpoints.clear()
            S.player_pos = [0.0, 0.0]
            S.spawn_pos = [0.0, 0.0]
            S.facing_angle = -math.pi / 2
        x_pressed_last_frame = 'x' in keys_pressed

        toggle_now = any(k in keys_pressed for k in ('tab', 'alt', 'escape'))
        if toggle_now and not rotation_toggle_last_frame:
            S.rotation_enabled = not S.rotation_enabled
        rotation_toggle_last_frame = toggle_now

    if S.mode == "dpi":
        screen.fill((0, 0, 0))
        rect = dpi_bg.get_rect(center=(CENTER_X, CENTER_Y))
        screen.blit(dpi_bg, rect)
        box = pygame.Rect(CENTER_X - 100, CENTER_Y + 90, 200, 36)
        pygame.draw.rect(screen, (20, 20, 20), box)
        pygame.draw.rect(screen, (0, 255, 0), box, 2)
        text = font.render(S.dpi_input, True, (0, 255, 0))
        screen.blit(text, (box.x + 10, box.y + 6))
    elif S.mode == "map":
        screen.blit(pygame.transform.smoothscale(map_bg, (WIDTH, HEIGHT)), (0, 0))
        draw_spawn_circle()
        draw_path()
        draw_checkpoints()
        draw_player_arrow()
        draw_sensitivity_display()

    draw_overlay_lines()
    draw_rolling_overlay()
    pygame.display.flip()
    clock.tick(60)
