import pygame
import sys
import threading
from pynput import keyboard
from ctypes import windll, Structure, c_long, byref
from collections import deque
import os
import math

# === Windows cursor tracker ===
class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_mouse_pos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y

# === Global State Container ===
class State:
    def __init__(self):
        self.rotation_enabled = True
        self.zoom = 1.0
        self.player_pos = [0.0, 0.0]
        self.facing_angle = -math.pi / 2
        self.path = deque()
        self.checkpoints = []
        self.checkpoint_visible = True
        self.mouse_dx_buffer = [0]
        self.pressed_keys = set()

S = State()

# === Pygame init ===
pygame.init()
WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
CENTER = (CENTER_X, CENTER_Y)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BETNAV — Version 0.1")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
# === Sensitivity Input Prompt ===
def get_sensitivity():
    input_box = pygame.Rect(CENTER_X - 100, CENTER_Y, 200, 30)
    text = ''
    while True:
        screen.fill((20, 20, 20))
        prompt = font.render("Enter mouse sensitivity (0.10–2.00):", True, (255, 255, 255))
        warning = font.render("Center mouse & face NORTH. Stay still.", True, (255, 50, 50))
        screen.blit(prompt, (CENTER_X - prompt.get_width() // 2, CENTER_Y - 60))
        screen.blit(warning, (CENTER_X - warning.get_width() // 2, CENTER_Y - 100))
        pygame.draw.rect(screen, (60, 60, 60), input_box)
        txt_surface = font.render(text, True, (0, 255, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        return max(0.10, min(2.00, float(text)))
                    except:
                        text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 6:
                    text += event.unicode

sensitivity = get_sensitivity()

# === Countdown Before Start ===
def show_countdown():
    start = pygame.time.get_ticks()
    while True:
        remaining = max(0, 10 - (pygame.time.get_ticks() - start) // 1000)
        screen.fill((0, 0, 0))
        msg = font.render(f"Initializing in {remaining}... DO NOT MOVE!", True, (255, 0, 0))
        screen.blit(msg, (CENTER_X - msg.get_width() // 2, CENTER_Y))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        if remaining == 0:
            break
        clock.tick(60)

show_countdown()

# === Lock Mouse and Initialize Input ===
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
windll.user32.SetCursorPos(CENTER_X, CENTER_Y)
# === External Mouse Tracker Thread ===
def track_mouse():
    last_x, _ = get_mouse_pos()
    while True:
        x, _ = get_mouse_pos()
        dx = x - last_x
        last_x = x
        if S.rotation_enabled:
            S.mouse_dx_buffer[0] += dx
        pygame.time.wait(1)

threading.Thread(target=track_mouse, daemon=True).start()

# === Global Keyboard Input Thread ===
def track_keys():
    from pynput.keyboard import Key

    def on_press(key):
        try:
            k = key.char.lower()
            S.pressed_keys.add(k)
        except:
            if key == Key.shift: S.pressed_keys.add("shift")
            elif key in [Key.tab, Key.esc]:
                S.rotation_enabled = not S.rotation_enabled
            elif key == Key.v and "shift" in S.pressed_keys:
                S.checkpoint_visible = not S.checkpoint_visible

    def on_release(key):
        try:
            k = key.char.lower()
            if k in S.pressed_keys:
                S.pressed_keys.remove(k)
        except:
            if key == Key.shift and "shift" in S.pressed_keys:
                S.pressed_keys.remove("shift")

    keyboard.Listener(on_press=on_press, on_release=on_release).start()

threading.Thread(target=track_keys, daemon=True).start()

# === Drawing Functions ===
def draw_path():
    for pt in S.path:
        x = CENTER_X + (pt[0] - S.player_pos[0]) * S.zoom
        y = CENTER_Y + (pt[1] - S.player_pos[1]) * S.zoom
        pygame.draw.circle(screen, (0, 100, 0), (int(x), int(y)), max(1, int(2 * S.zoom)))

def draw_player():
    pygame.draw.circle(screen, (0, 255, 0), CENTER, int(6 * S.zoom))
    arrow_x = CENTER_X + math.cos(S.facing_angle) * 12 * S.zoom
    arrow_y = CENTER_Y + math.sin(S.facing_angle) * 12 * S.zoom
    pygame.draw.line(screen, (0, 255, 0), CENTER, (arrow_x, arrow_y), int(2 * S.zoom))

def draw_spawn():
    x = CENTER_X - S.player_pos[0] * S.zoom
    y = CENTER_Y - S.player_pos[1] * S.zoom
    pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), max(4, int(4 * S.zoom)))

def draw_checkpoints():
    if not S.checkpoint_visible:
        return
    for pt in S.checkpoints:
        x = CENTER_X + (pt[0] - S.player_pos[0]) * S.zoom
        y = CENTER_Y + (pt[1] - S.player_pos[1]) * S.zoom
        pygame.draw.polygon(screen, (255, 0, 0), [
            (x, y - 6 * S.zoom),
            (x - 5 * S.zoom, y + 4 * S.zoom),
            (x + 5 * S.zoom, y + 4 * S.zoom)
        ])
# === Main Game Loop ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                S.zoom = min(S.zoom + 0.1, 5.0)
            elif event.key == pygame.K_o:
                S.zoom = max(S.zoom - 0.1, 0.2)
            elif event.key == pygame.K_x:
                S.path.clear()
                S.checkpoints.clear()  # 💥 Clear all red checkpoints too
                S.player_pos = [0.0, 0.0]
                S.facing_angle = -math.pi / 2
            elif event.key == pygame.K_v:
                S.checkpoints.append(S.player_pos[:])

    # === External 360° Rotation Fix ===
    mouse_x, _ = get_mouse_pos()
    dx = mouse_x - CENTER_X
    windll.user32.SetCursorPos(CENTER_X, CENTER_Y)  # Always re-center
    if S.rotation_enabled:
        S.facing_angle += dx * (sensitivity * 0.0035)

    # === Movement (WASD + Shift sprint)
    move_x, move_y = 0, 0
    fx, fy = math.cos(S.facing_angle), math.sin(S.facing_angle)
    sx, sy = math.cos(S.facing_angle + math.pi / 2), math.sin(S.facing_angle + math.pi / 2)
    if 'w' in S.pressed_keys: move_x += fx; move_y += fy
    if 's' in S.pressed_keys: move_x -= fx; move_y -= fy
    if 'a' in S.pressed_keys: move_x += sx; move_y += sy
    if 'd' in S.pressed_keys: move_x -= sx; move_y -= sy

    if move_x or move_y:
        mag = math.hypot(move_x, move_y)
        speed = 3.5 if "shift" in S.pressed_keys else 1.5
        S.player_pos[0] += (move_x / mag) * speed * sensitivity
        S.player_pos[1] += (move_y / mag) * speed * sensitivity
        S.path.append(S.player_pos[:])
        if len(S.path) > 10000: S.path.popleft()

    # === Render All Layers ===
    screen.fill((0, 0, 0))
    draw_path()
    draw_spawn()
    draw_checkpoints()
    draw_player()
    pygame.display.flip()
    clock.tick(60)
