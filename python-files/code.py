# --- World Weaver's Ballad ---
# Version: 17.2 (The Final Initialization Fix)

import pygame
import sys
import os
import random
import time

# --- Initialization ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# --- Game Constants ---
GAME_WIDTH, GAME_HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
PLAYER_SIZE = int(TILE_SIZE * 0.8)

# Game Boy Color Palette
GB_DARKEST = (41, 51, 42)
WHITE = (188, 208, 148)
BLACK = GB_DARKEST

# Tile IDs
GRASS_TILE = 0
WALL_TILE = 1
SAPLING_TILE = 2
BRIDGE_TILE = 3
GOAL_TILE = 4
GOAL_LOCKED_TILE = 5

# Applause Meter Constants
MAX_APPLAUSE = 1000
APPLAUSE_PER_GROWTH = 50
APPLAUSE_PER_BREAK = 25
APPLAUSE_PENALTY_BUMP = -10
APPLAUSE_PENALTY_WASTE = -5
FLAWLESS_BONUS_TIME = 20
FLAWLESS_BONUS_APPLAUSE = 100

# --- Game Setup ---
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("World Weaver's Ballad")
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()

# --- Asset Loading ---
script_path = os.path.dirname(os.path.abspath(__file__))
def load_image(filename):
    path = os.path.join(script_path, "assets", filename)
    try: return pygame.image.load(path).convert_alpha()
    except: pygame.quit(); sys.exit(f"ERROR: Cannot load image: {filename}")
def load_sound(filename):
    path = os.path.join(script_path, "assets", filename)
    if not os.path.exists(path): return None
    return pygame.mixer.Sound(path)

# Load images
grass_img = load_image('grass.png'); wall_img = load_image('wall_bush.png'); tree_img = load_image('tree.png'); bridge_img = load_image('bridge.png'); win_img = load_image('win.png'); goal_locked_img = load_image('goal_locked.png'); player_spritesheet = load_image('player.png'); applause_frame_img = load_image('applause_meter_frame.png'); applause_fill_img = load_image('applause_meter_fill.png')

tile_images = {
    GRASS_TILE: pygame.transform.scale(grass_img, (TILE_SIZE, TILE_SIZE)),
    WALL_TILE: pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE)),
    SAPLING_TILE: pygame.transform.scale(tree_img, (TILE_SIZE, TILE_SIZE)),
    BRIDGE_TILE: pygame.transform.scale(bridge_img, (TILE_SIZE, TILE_SIZE)),
    GOAL_TILE: pygame.transform.scale(win_img, (TILE_SIZE, TILE_SIZE)),
    GOAL_LOCKED_TILE: pygame.transform.scale(goal_locked_img, (TILE_SIZE, TILE_SIZE)),
}

player_frames = [pygame.transform.scale(player_spritesheet.subsurface(pygame.Rect(i*8, 0, 8, 8)), (PLAYER_SIZE, PLAYER_SIZE)) for i in range(player_spritesheet.get_width() // 8)]

# Sound Loading & Volume Balancing
sfx_grow = load_sound('grow.wav'); sfx_win = load_sound('win.wav'); sfx_start = load_sound('start.wav'); sfx_unlock = load_sound('unlock.wav'); sfx_break = load_sound('break.wav'); sfx_applause = load_sound('sfx_applause.wav'); sfx_mistake = load_sound('sfx_mistake.wav')
if sfx_grow: sfx_grow.set_volume(0.6)
if sfx_win: sfx_win.set_volume(0.4)
if sfx_start: sfx_start.set_volume(0.5)
if sfx_unlock: sfx_unlock.set_volume(0.7)
if sfx_break: sfx_break.set_volume(0.8)
if sfx_applause: sfx_applause.set_volume(0.5)
if sfx_mistake: sfx_mistake.set_volume(0.6)

# --- Procedural Level Generation ---
MAP_WIDTH, MAP_HEIGHT = 20, 15
def generate_level(difficulty):
    new_map = [[WALL_TILE for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    cx, cy = random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2)
    start_pos = (cx, cy); new_map[cy][cx] = GRASS_TILE
    path_length = int((MAP_WIDTH * MAP_HEIGHT) * (0.2 + difficulty * 0.05))
    for _ in range(path_length):
        nx, ny = cx, cy
        if random.random() > 0.5: nx += random.choice([-1, 1])
        else: ny += random.choice([-1, 1])
        if 1 <= nx < MAP_WIDTH - 1 and 1 <= ny < MAP_HEIGHT - 1:
            cx, cy = nx, ny; new_map[cy][cx] = GRASS_TILE
    new_map[cy][cx] = GOAL_LOCKED_TILE
    num_saplings = 2 + difficulty
    for _ in range(num_saplings):
        while True:
            rx, ry = random.randint(1, MAP_WIDTH-2), random.randint(1, MAP_HEIGHT-2)
            if new_map[ry][rx] == GRASS_TILE: new_map[ry][rx] = SAPLING_TILE; break
    return {"map": new_map, "start_pos": start_pos}

TOTAL_LEVELS = 40
levels = [generate_level(i) for i in range(TOTAL_LEVELS)]

# --- Game State & Player Data ---
game_state = "title"; fullscreen = False; music_started = False; current_level_index = 0
player_tile_x, player_tile_y = 0, 0
player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
player_frame_index = 0; total_saplings = 0; saplings_grown = 0; break_uses_left = 0
applause_score = 0; level_start_time = 0
world_map = None # Initialize as None before first load

# --- Game Functions ---
def load_level(level_index):
    global world_map, player_tile_x, player_tile_y, total_saplings, saplings_grown, break_uses_left, level_start_time
    level_data = levels[level_index]
    world_map = [row.copy() for row in level_data["map"]]
    player_tile_x, player_tile_y = level_data["start_pos"]
    saplings_grown = 0
    total_saplings = sum(row.count(SAPLING_TILE) for row in world_map)
    break_uses_left = 5
    level_start_time = time.time()
    if total_saplings == 0: unlock_goals()

def update_applause(amount):
    global applause_score
    if amount > 0: play_sfx(sfx_applause)
    else: play_sfx(sfx_mistake)
    applause_score = max(0, min(MAX_APPLAUSE, applause_score + amount))

def play_sfx(sound):
    if sound: sound.play()

def unlock_goals():
    play_sfx(sfx_unlock)
    for r, row in enumerate(world_map):
        for c, tile in enumerate(row):
            if tile == GOAL_LOCKED_TILE: world_map[r][c] = GOAL_TILE

def draw_world_details(surface, world):
    for r, row in enumerate(world):
        for c, tile_id in enumerate(row):
            if tile_id != GRASS_TILE:
                surface.blit(tile_images[tile_id], (c * TILE_SIZE, r * TILE_SIZE))

def draw_text(surface, text, size, x, y, color, align="center"):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    surface.blit(text_surface, text_rect)

def draw_ui():
    objective_text = f"Scene {current_level_index + 1}: Prepare the Stage ({saplings_grown}/{total_saplings})"
    draw_text(game_surface, objective_text, 30, GAME_WIDTH / 2, TILE_SIZE / 2, WHITE)
    breakdown_text = f"Breakdown [2]: {break_uses_left}"
    draw_text(game_surface, breakdown_text, 30, TILE_SIZE, TILE_SIZE / 2, WHITE, align="midleft")
    meter_width = 200; meter_height = 20
    meter_x, meter_y = GAME_WIDTH / 2 - meter_width / 2, GAME_HEIGHT - TILE_SIZE
    fill_width = int((applause_score / MAX_APPLAUSE) * meter_width)
    pygame.draw.rect(game_surface, WHITE, (meter_x, meter_y, meter_width, meter_height), 2)
    pygame.draw.rect(game_surface, WHITE, (meter_x, meter_y, fill_width, meter_height))

# --- Main Game Loop ---
# --- THE FIX IS HERE: Load the first level before the loop starts ---
load_level(current_level_index)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) if fullscreen else pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)
            if game_state == "title":
                if event.key == pygame.K_SPACE:
                    play_sfx(sfx_start); game_state = "playing"
                    if not music_started:
                        music_path = os.path.join(script_path, "assets", 'music.mp3')
                        if os.path.exists(music_path):
                            pygame.mixer.music.load(music_path); pygame.mixer.music.set_volume(1.0); pygame.mixer.music.play(-1)
                            music_started = True
            elif game_state == "playing":
                if event.key == pygame.K_ESCAPE: game_state = "paused"
                target_x, target_y = player_tile_x, player_tile_y; moved = False
                if event.key in [pygame.K_w, pygame.K_UP]: target_y -= 1; moved = True
                elif event.key in [pygame.K_s, pygame.K_DOWN]: target_y += 1; moved = True
                elif event.key in [pygame.K_a, pygame.K_LEFT]: target_x -= 1; moved = True
                elif event.key in [pygame.K_d, pygame.K_RIGHT]: target_x += 1; moved = True
                if moved:
                    player_frame_index = (player_frame_index + 1) % len(player_frames)
                    if 0 <= target_y < MAP_HEIGHT and 0 <= target_x < MAP_WIDTH:
                        tile_id = world_map[target_y][target_x]
                        if tile_id in [GRASS_TILE, BRIDGE_TILE, GOAL_TILE]: player_tile_x, player_tile_y = target_x, target_y
                        else: update_applause(APPLAUSE_PENALTY_BUMP)
                if event.key == pygame.K_1:
                    transformed = False
                    for yo in range(-1, 2):
                        for xo in range(-1, 2):
                            cx, cy = player_tile_x + xo, player_tile_y + yo
                            if 0 <= cy < MAP_HEIGHT and 0 <= cx < MAP_WIDTH and world_map[cy][cx] == SAPLING_TILE:
                                world_map[cy][cx] = BRIDGE_TILE; saplings_grown += 1; transformed = True
                    if transformed: play_sfx(sfx_grow); update_applause(APPLAUSE_PER_GROWTH) 
                    else: update_applause(APPLAUSE_PENALTY_WASTE)
                    if total_saplings > 0 and saplings_grown == total_saplings: unlock_goals()
                if event.key == pygame.K_2:
                    if break_uses_left > 0:
                        broken = False
                        for yo in range(-1, 2):
                            for xo in range(-1, 2):
                                cx, cy = player_tile_x + xo, player_tile_y + yo
                                if 0 <= cy < MAP_HEIGHT and 0 <= cx < MAP_WIDTH and world_map[cy][cx] == WALL_TILE:
                                    world_map[cy][cx] = GRASS_TILE; broken = True
                        if broken: break_uses_left -= 1; play_sfx(sfx_break); update_applause(APPLAUSE_PER_BREAK)
                        else: update_applause(APPLAUSE_PENALTY_WASTE)
            elif game_state == "paused":
                if event.key == pygame.K_ESCAPE: game_state = "playing"
                if event.key == pygame.K_q: pygame.quit(); sys.exit()

    if game_state == "playing":
        if world_map[player_tile_y][player_tile_x] == GOAL_TILE:
            play_sfx(sfx_win)
            if time.time() - level_start_time < FLAWLESS_BONUS_TIME: update_applause(FLAWLESS_BONUS_APPLAUSE)
            current_level_index += 1
            if current_level_index < len(levels): load_level(current_level_index)
            else: game_state = "game_win"; pygame.mixer.music.fadeout(1000)
    
    # --- Drawing (Cleaned up logic) ---
    if game_state == "title":
        draw_text(game_surface, "World Weaver's Ballad", 80, GAME_WIDTH/2, GAME_HEIGHT/2 - 50, WHITE); draw_text(game_surface, "Press SPACE to Begin", 40, GAME_WIDTH/2, GAME_HEIGHT/2 + 50, WHITE)
    elif game_state in ["playing", "paused"]:
        for y in range(0, GAME_HEIGHT, TILE_SIZE):
            for x in range(0, GAME_WIDTH, TILE_SIZE): game_surface.blit(tile_images[GRASS_TILE], (x, y))
        draw_world_details(game_surface, world_map)
        draw_pos_x = (player_tile_x * TILE_SIZE) + (TILE_SIZE - PLAYER_SIZE) // 2
        draw_pos_y = (player_tile_y * TILE_SIZE) + (TILE_SIZE - PLAYER_SIZE) // 2
        game_surface.blit(player_frames[player_frame_index], (draw_pos_x, draw_pos_y))
        draw_ui()
        if game_state == "paused":
             draw_text(game_surface, "PAUSED", 80, GAME_WIDTH/2, GAME_HEIGHT/2 - 100, WHITE); draw_text(game_surface, "Press 'ESC' to Resume", 40, GAME_WIDTH/2, GAME_HEIGHT/2, WHITE); draw_text(game_surface, "Press 'Q' to Quit", 40, GAME_WIDTH/2, GAME_HEIGHT/2 + 50, WHITE)
    elif game_state == "game_win":
        draw_text(game_surface, "Curtain Call!", 80, GAME_WIDTH/2, GAME_HEIGHT/2 - 50, WHITE); draw_text(game_surface, f"Final Applause: {applause_score}", 40, GAME_WIDTH/2, GAME_HEIGHT/2 + 50, WHITE)

    win_w, win_h = screen.get_size(); scale = min(win_w / GAME_WIDTH, win_h / GAME_HEIGHT); scaled_w, scaled_h = int(GAME_WIDTH * scale), int(GAME_HEIGHT * scale)
    scaled_surface = pygame.transform.scale(game_surface, (scaled_w, scaled_h)); pos_x, pos_y = (win_w - scaled_w) / 2, (win_h - scaled_h) / 2
    screen.fill(BLACK); screen.blit(scaled_surface, (pos_x, pos_y))
    pygame.display.flip(); clock.tick(FPS)
