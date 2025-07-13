import pygame
import random
import math
import sys
import time
import json
import os

# Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quad: Military Bomber")
clock = pygame.time.Clock()

# Game States
MENU, PLAYING, GAME_OVER, MISSION_SELECT, MISSION_FAILED, JET_SELECT = 0, 1, 2, 3, 4, 5
game_state = MENU

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
LIGHT_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Mission Progress
progress_file = "progress.json"
grades_file = "grades.json"
jets_file = "jets.json"


def load_data(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                # Ensure all required keys exist
                if filename == progress_file:
                    if "completed_missions" not in data:
                        data["completed_missions"] = default["completed_missions"]
                    if "unlocked_missions" not in data:
                        data["unlocked_missions"] = default["unlocked_missions"]
                return data
        return default
    except:
        return default


def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


# Initialize with proper default values
progress = load_data(progress_file, {"completed_missions": 0, "unlocked_missions": 1})
grades = load_data(grades_file, {str(i): "F" for i in range(7)})  # 7 missions
jets = load_data(jets_file, {"default": "plane.png", "custom_jets": {}})

current_mission_index = 0
mission_mode = False
mission_scroll_offset = 0
selected_jet = jets["default"]

missions = [
    {
        "name": "Training Run",
        "description": "Destroy 5 terrain segments",
        "target": 5,
        "type": "destruction",
        "time_limit": 0,
        "unlock_condition": "complete_previous"
    },
    {
        "name": "Distance Challenge",
        "description": "Fly 500 meters",
        "target": 500,
        "type": "distance",
        "time_limit": 0,
        "unlock_condition": "complete_previous"
    },
    {
        "name": "Precision Strike",
        "description": "Destroy 10 targets in 30 seconds",
        "target": 10,
        "type": "timed_destruction",
        "time_limit": 30,
        "unlock_condition": "complete_previous"
    },
    {
        "name": "Endurance Test",
        "description": "Stay airborne for 45 seconds",
        "target": 45,
        "type": "survival",
        "time_limit": 45,
        "unlock_condition": "complete_2_previous"
    },
    {
        "name": "Demolition Expert",
        "description": "Destroy 20 targets in 500 meters",
        "target": 20,
        "type": "distance_destruction",
        "time_limit": 0,
        "unlock_condition": "complete_3_previous"
    },
    {
        "name": "Speed Run",
        "description": "Fly 800 meters in 40 seconds",
        "target": 800,
        "type": "timed_distance",
        "time_limit": 40,
        "unlock_condition": "complete_4_previous"
    },
    {
        "name": "Master Bomber",
        "description": "Destroy 30 targets with 80% accuracy",
        "target": 30,
        "type": "precision",
        "time_limit": 0,
        "unlock_condition": "complete_all_previous"
    }
]


# Load plane image
def load_plane_image(path=None):
    try:
        img_path = path if path else selected_jet
        img = pygame.image.load(img_path).convert_alpha()
        return pygame.transform.scale(img, (100, 50))
    except:
        # Create a default plane if image loading fails
        surf = pygame.Surface((100, 50), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (60, 60, 65), [(0, 25), (80, 10), (100, 25), (80, 40)])
        return surf


plane_img = load_plane_image()

# Crosshair
crosshair_img = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(crosshair_img, RED, (12, 12), 10, 2)
pygame.draw.line(crosshair_img, RED, (12, 2), (12, 22), 2)
pygame.draw.line(crosshair_img, RED, (2, 12), (22, 12), 2)

# Background
sky_img = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    shade = 135 + int(70 * y / HEIGHT)
    pygame.draw.line(sky_img, (shade, 206, 235), (0, y), (WIDTH, y))

# Constants
SCROLL_SPEED = 3
PLANE_X = WIDTH // 2 - 50
BOMB_GRAVITY = 0.5
TERRAIN_SEGMENT_WIDTH = 10

# Power-ups
POWERUP_TYPES = ["speed_boost", "rapid_fire", "invincibility"]
powerups = []
powerup_active = None
powerup_timer = 0

terrain_map = {}


def get_terrain_height(segment_index):
    if segment_index not in terrain_map:
        offset = 30 * math.sin(segment_index * 0.15)
        base = HEIGHT - 100
        terrain_map[segment_index] = base + offset + random.randint(-5, 5)
    return terrain_map[segment_index]


def destroy_terrain_at(segment_index, impact_y, radius=20):
    for i in range(segment_index - 2, segment_index + 3):
        if i in terrain_map:
            y = terrain_map[i]
            dist = abs(i - segment_index)
            lower = radius * (1 - dist / 2)
            if y - lower < impact_y:
                terrain_map[i] += lower


# Game reset
def reset_game():
    global plane_y, bombs, scroll_x, explosions, particles
    global destroyed_segments, mission_timer_start, mission_complete
    global terrain_map, bombs_dropped, hits, mission_start_time
    global powerups, powerup_active, powerup_timer

    terrain_map = {}  # Reset terrain for new generation
    plane_y = HEIGHT // 3
    bombs = []
    scroll_x = 0
    explosions = []
    particles = []
    destroyed_segments = 0
    bombs_dropped = 0
    hits = 0
    mission_timer_start = time.time()
    mission_start_time = time.time()
    mission_complete = False
    powerups = []
    powerup_active = None
    powerup_timer = 0


reset_game()


# Effects
def create_explosion(x, y, radius=30):
    explosions.append({"x": x, "y": y, "radius": 5, "max_radius": radius, "time": 0})


def create_particles(x, y, count=20):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        particles.append({
            "x": x, "y": y,
            "dx": math.cos(angle) * speed,
            "dy": math.sin(angle) * speed,
            "life": random.randint(20, 40),
            "size": random.randint(2, 4)
        })


def create_powerup(x, y):
    powerup_type = random.choice(POWERUP_TYPES)
    powerups.append({
        "x": x,
        "y": y,
        "type": powerup_type,
        "width": 30,
        "height": 30
    })


# UI elements
def draw_text(text, size, color, x, y, font_name=None, centered=False):
    font = pygame.font.SysFont(font_name or "Arial", size, bold=True)
    img = font.render(text, True, color)
    if centered:
        x -= img.get_width() // 2
    screen.blit(img, (x, y))


def draw_button(text, x, y, w, h, color=GRAY, hover_color=(70, 70, 70)):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    btn_color = hover_color if rect.collidepoint(mouse) else color
    pygame.draw.rect(screen, btn_color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    draw_text(text, 28, WHITE, x + w // 2, y + h // 2 - 15, centered=True)
    return rect.collidepoint(mouse) and click[0]


def draw_terrain():
    points = []
    for x in range(0, WIDTH + TERRAIN_SEGMENT_WIDTH, TERRAIN_SEGMENT_WIDTH):
        world_x = x + scroll_x
        index = world_x // TERRAIN_SEGMENT_WIDTH
        height = get_terrain_height(index)
        points.append((x, height))
    if points:
        points = [(points[0][0], HEIGHT)] + points + [(points[-1][0], HEIGHT)]
        pygame.draw.polygon(screen, (40, 60, 40), points)


def calculate_grade(mission_index, performance):
    mission = missions[mission_index]
    target = mission["target"]

    if mission["type"] in ["destruction", "timed_destruction", "distance_destruction"]:
        ratio = performance["hits"] / mission["target"]
    elif mission["type"] in ["distance", "timed_distance"]:
        ratio = performance["distance"] / mission["target"]
    elif mission["type"] == "survival":
        ratio = performance["time"] / mission["target"]
    elif mission["type"] == "precision":
        accuracy = performance["hits"] / performance["bombs"] if performance["bombs"] > 0 else 0
        ratio = (performance["hits"] / mission["target"]) * (0.5 + accuracy * 0.5)

    if ratio >= 1.5: return "S"
    if ratio >= 1.2: return "A"
    if ratio >= 1.0: return "B"
    if ratio >= 0.8: return "C"
    if ratio >= 0.6: return "D"
    return "F"


def save_grade(mission_index, grade):
    grades[str(mission_index)] = grade
    save_data(grades_file, grades)


def is_mission_unlocked(mission_index):
    if mission_index == 0:
        return True

    mission = missions[mission_index]
    completed = progress["completed_missions"]

    if mission["unlock_condition"] == "complete_previous":
        return mission_index <= completed + 1
    elif mission["unlock_condition"] == "complete_2_previous":
        return mission_index <= completed + 1 and completed >= 1
    elif mission["unlock_condition"] == "complete_3_previous":
        return mission_index <= completed + 1 and completed >= 2
    elif mission["unlock_condition"] == "complete_4_previous":
        return mission_index <= completed + 1 and completed >= 3
    elif mission["unlock_condition"] == "complete_all_previous":
        return completed >= len(missions) - 1

    return False


# Main game loop
running = True
mission_end_time = None
performance_stats = {}

while running:
    screen.blit(sky_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state in [GAME_OVER, MISSION_FAILED]:
                if event.key == pygame.K_r:
                    game_state = PLAYING
                    reset_game()
                elif event.key == pygame.K_e:
                    game_state = MENU
            elif game_state == PLAYING and event.key == pygame.K_ESCAPE:
                game_state = MENU
            elif game_state == MISSION_SELECT and event.key == pygame.K_DOWN:
                mission_scroll_offset = min(mission_scroll_offset + 100, len(missions) * 80 - HEIGHT + 200)
            elif game_state == MISSION_SELECT and event.key == pygame.K_UP:
                mission_scroll_offset = max(mission_scroll_offset - 100, 0)

        # Handle mouse wheel for mission scrolling
        if event.type == pygame.MOUSEWHEEL and game_state == MISSION_SELECT:
            mission_scroll_offset = max(0, min(mission_scroll_offset - event.y * 20, len(missions) * 80 - HEIGHT + 200))

    if game_state == MENU:
        draw_text("QUAD: Military Bomber", 48, BLACK, WIDTH // 2, 50, "Arial", True)
        draw_text("MISSION MODE", 24, BLACK, WIDTH // 2, 120, "Arial", True)

        if draw_button("FREE FLIGHT", 300, 180, 200, 60):
            mission_mode = False
            game_state = PLAYING
            reset_game()
        if draw_button("MISSIONS", 300, 260, 200, 60):
            game_state = MISSION_SELECT
        if draw_button("SELECT JET", 300, 340, 200, 60):
            game_state = JET_SELECT
        if draw_button("QUIT", 300, 420, 200, 60):
            running = False

        pygame.display.flip()

    elif game_state == MISSION_SELECT:
        # Draw missions with scrollable view
        draw_text("MISSIONS", 42, BLACK, WIDTH // 2, 40, "Arial", True)

        # Create a surface for the scrollable area
        missions_surface = pygame.Surface((WIDTH, len(missions) * 80 + 100))
        missions_surface.fill(LIGHT_BLUE)

        for i, m in enumerate(missions):
            y = 100 + i * 80
            locked = not is_mission_unlocked(i)

            # Mission box
            box_color = (200, 200, 200) if locked else (220, 220, 255)
            pygame.draw.rect(missions_surface, box_color, (100, y, 600, 70), border_radius=8)
            pygame.draw.rect(missions_surface, BLACK, (100, y, 600, 70), 2, border_radius=8)

            # Mission info
            status = "LOCKED" if locked else f"GRADE: {grades.get(str(i), 'N/A')}"
            draw_text(f"{m['name']} ({status})", 22, BLACK, 120, y + 15, None, False)
            draw_text(m['description'], 18, BLACK, 120, y + 40, None, False)

            # Start button if unlocked
            if not locked:
                btn_rect = pygame.Rect(620, y + 15, 70, 40)
                mouse_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - mission_scroll_offset + 40)
                btn_color = (100, 255, 100) if btn_rect.collidepoint(mouse_pos) else (50, 200, 50)
                pygame.draw.rect(missions_surface, btn_color, btn_rect, border_radius=5)
                pygame.draw.rect(missions_surface, BLACK, btn_rect, 2, border_radius=5)
                draw_text("START", 18, BLACK, 655, y + 35, None, True)

        # Blit the scrollable surface
        screen.blit(missions_surface, (0, -mission_scroll_offset + 40))

        # Draw scroll indicator
        if len(missions) * 80 > HEIGHT - 200:
            scroll_ratio = mission_scroll_offset / (len(missions) * 80 - HEIGHT + 200)
            scrollbar_height = HEIGHT * 0.3
            scrollbar_y = 100 + (HEIGHT - 200 - scrollbar_height) * scroll_ratio
            pygame.draw.rect(screen, (100, 100, 100), (WIDTH - 20, scrollbar_y, 10, scrollbar_height), border_radius=5)

        # Check for mission selection clicks
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - mission_scroll_offset + 40)
            for i, m in enumerate(missions):
                if not is_mission_unlocked(i):
                    continue

                y = 100 + i * 80
                btn_rect = pygame.Rect(620, y + 15, 70, 40)
                if btn_rect.collidepoint(mouse_pos):
                    current_mission_index = i
                    mission_mode = True
                    game_state = PLAYING
                    reset_game()
                    break

        if draw_button("BACK", WIDTH // 2 - 100, HEIGHT - 80, 200, 50):
            game_state = MENU

        pygame.display.flip()

    elif game_state == JET_SELECT:
        draw_text("SELECT YOUR JET", 42, BLACK, WIDTH // 2, 40, "Arial", True)

        # Default jet
        if draw_button("DEFAULT JET", 250, 120, 300, 60):
            selected_jet = "plane.png"
            plane_img = load_plane_image()
            game_state = MENU

        # Custom jets
        y_offset = 200
        for name, path in jets["custom_jets"].items():
            if draw_button(f"USE {name.upper()}", 250, y_offset, 300, 60):
                selected_jet = path
                plane_img = load_plane_image(path)
                game_state = MENU
            y_offset += 80

        # Add new jet button
        if draw_button("ADD NEW JET", 250, y_offset, 300, 60, (100, 200, 255)):
            # Simple file dialog would be better, but for simplicity we'll just check for files
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(title="Select Jet Image",
                                                       filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
                if file_path:
                    jet_name = os.path.splitext(os.path.basename(file_path))[0]
                    jets["custom_jets"][jet_name] = file_path
                    save_data(jets_file, jets)
                    # Reload the jet selection screen
                    jets = load_data(jets_file, {"default": "plane.png", "custom_jets": {}})
            except:
                draw_text("Error: Could not open file dialog", 24, RED, WIDTH // 2, y_offset + 80, "Arial", True)

        if draw_button("BACK", WIDTH // 2 - 100, HEIGHT - 80, 200, 50):
            game_state = MENU

        pygame.display.flip()

    elif game_state == PLAYING:
        # Simplified controls - plane follows mouse Y with damping
        target_y = pygame.mouse.get_pos()[1] - 25
        plane_y += (target_y - plane_y) * 0.1

        # Keep plane on screen
        plane_y = max(0, min(HEIGHT - 50, plane_y))

        # Adjust scroll speed based on powerup
        current_scroll_speed = SCROLL_SPEED * 2 if powerup_active == "speed_boost" else SCROLL_SPEED
        scroll_x += current_scroll_speed

        # Bomb dropping - adjust for rapid fire powerup
        bomb_cooldown = 10  # frames
        if pygame.mouse.get_pressed()[0]:
            if len(bombs) < 50 and (powerup_active != "rapid_fire" or pygame.time.get_ticks() % 5 == 0):
                mx, my = pygame.mouse.get_pos()
                bombs.append({
                    "x": PLANE_X + 70,
                    "y": plane_y + 25,
                    "vy": 0,
                    "speed_x": (mx - (PLANE_X + 70)) * 0.03
                })
                bombs_dropped += 1

        # Update bombs
        for b in bombs[:]:
            b["x"] += b["speed_x"]
            b["y"] += b["vy"]
            b["vy"] += BOMB_GRAVITY
            index = int((b["x"] + scroll_x) // TERRAIN_SEGMENT_WIDTH)

            # Check for terrain hit
            if b["y"] >= get_terrain_height(index):
                create_explosion(b["x"], b["y"])
                create_particles(b["x"], b["y"], 30)
                destroy_terrain_at(index, b["y"])
                destroyed_segments += 1
                hits += 1
                bombs.remove(b)

                # Random chance to spawn powerup (10%)
                if random.random() < 0.1:
                    create_powerup(b["x"], b["y"] - 30)
            elif b["y"] > HEIGHT:  # Missed
                bombs.remove(b)

        # Check for powerup collection
        for p in powerups[:]:
            # Check collision with plane
            plane_rect = pygame.Rect(PLANE_X, plane_y, 100, 50)
            powerup_rect = pygame.Rect(p["x"], p["y"], p["width"], p["height"])

            if plane_rect.colliderect(powerup_rect):
                powerup_active = p["type"]
                powerup_timer = time.time() + 10  # 10 seconds duration
                powerups.remove(p)
                create_explosion(p["x"] + p["width"] // 2, p["y"] + p["height"] // 2, 20)
                create_particles(p["x"] + p["width"] // 2, p["y"] + p["height"] // 2, 30)

        # Check for crash (unless invincibility powerup is active)
        plane_index = int((PLANE_X + scroll_x) // TERRAIN_SEGMENT_WIDTH)
        if plane_y + 50 >= get_terrain_height(plane_index) and powerup_active != "invincibility":
            create_explosion(PLANE_X + 50, plane_y + 25)
            create_particles(PLANE_X + 50, plane_y + 25, 50)
            if mission_mode:
                performance_stats = {
                    "distance": scroll_x // 10,
                    "time": time.time() - mission_start_time,
                    "hits": hits,
                    "bombs": bombs_dropped
                }
                game_state = MISSION_FAILED
            else:
                game_state = GAME_OVER

        # Update explosions
        for e in explosions[:]:
            e["time"] += 1
            if e["time"] < 15:
                e["radius"] += 2
            else:
                explosions.remove(e)

        # Update particles
        for p in particles[:]:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)

        # Update powerups
        if powerup_active and time.time() > powerup_timer:
            powerup_active = None

        # Draw everything
        draw_terrain()

        for e in explosions:
            pygame.draw.circle(screen, (255, 150, 0), (int(e["x"]), int(e["y"])), int(e["radius"]))

        for p in particles:
            pygame.draw.circle(screen, (255, 100, 0), (int(p["x"]), int(p["y"])), p["size"])

        for b in bombs:
            pygame.draw.circle(screen, (30, 30, 30), (int(b["x"]), int(b["y"])), 6)

        # Draw powerups
        for p in powerups:
            if p["type"] == "speed_boost":
                pygame.draw.rect(screen, YELLOW, (p["x"], p["y"], p["width"], p["height"]))
                draw_text("SPD", 18, BLACK, p["x"] + p["width"] // 2, p["y"] + p["height"] // 2 - 9, centered=True)
            elif p["type"] == "rapid_fire":
                pygame.draw.rect(screen, RED, (p["x"], p["y"], p["width"], p["height"]))
                draw_text("RFD", 18, BLACK, p["x"] + p["width"] // 2, p["y"] + p["height"] // 2 - 9, centered=True)
            elif p["type"] == "invincibility":
                pygame.draw.rect(screen, PURPLE, (p["x"], p["y"], p["width"], p["height"]))
                draw_text("INV", 18, BLACK, p["x"] + p["width"] // 2, p["y"] + p["height"] // 2 - 9, centered=True)
            pygame.draw.rect(screen, BLACK, (p["x"], p["y"], p["width"], p["height"]), 2)

        screen.blit(plane_img, (PLANE_X, plane_y))
        screen.blit(crosshair_img, pygame.mouse.get_pos())

        # Draw HUD
        elapsed = time.time() - mission_timer_start
        distance = scroll_x // 10

        draw_text(f"Altitude: {HEIGHT - int(plane_y)}", 20, WHITE, 10, 10)
        draw_text(f"Distance: {distance}m", 20, WHITE, 10, 40)
        draw_text(f"Destroyed: {destroyed_segments}", 20, WHITE, 10, 70)

        # Draw active powerup
        if powerup_active:
            time_left = max(0, powerup_timer - time.time())
            if powerup_active == "speed_boost":
                draw_text(f"SPEED BOOST: {int(time_left)}s", 20, YELLOW, WIDTH // 2 - 100, 10)
            elif powerup_active == "rapid_fire":
                draw_text(f"RAPID FIRE: {int(time_left)}s", 20, RED, WIDTH // 2 - 100, 10)
            elif powerup_active == "invincibility":
                draw_text(f"INVINCIBLE: {int(time_left)}s", 20, PURPLE, WIDTH // 2 - 100, 10)

        if mission_mode:
            mission = missions[current_mission_index]
            draw_text(f"Mission: {mission['name']}", 20, WHITE, 10, 100)

            if mission["time_limit"] > 0:
                time_left = max(0, mission["time_limit"] - elapsed)
                draw_text(f"Time: {int(time_left)}s", 20, WHITE, 10, 130)

            # Check mission completion
            mission_complete = False
            if mission["type"] == "destruction" and destroyed_segments >= mission["target"]:
                mission_complete = True
            elif mission["type"] == "distance" and distance >= mission["target"]:
                mission_complete = True
            elif mission["type"] == "timed_destruction" and destroyed_segments >= mission["target"] and elapsed <= \
                    mission["time_limit"]:
                mission_complete = True
            elif mission["type"] == "survival" and elapsed >= mission["target"]:
                mission_complete = True
            elif mission["type"] == "distance_destruction" and destroyed_segments >= mission["target"] and distance <= \
                    mission["target"] * 25:
                mission_complete = True
            elif mission["type"] == "timed_distance" and distance >= mission["target"] and elapsed <= mission[
                "time_limit"]:
                mission_complete = True
            elif mission["type"] == "precision" and destroyed_segments >= mission["target"] and (
            hits / bombs_dropped if bombs_dropped > 0 else 0) >= 0.8:
                mission_complete = True

            if mission_complete:
                performance_stats = {
                    "distance": distance,
                    "time": elapsed,
                    "hits": hits,
                    "bombs": bombs_dropped
                }
                grade = calculate_grade(current_mission_index, performance_stats)
                save_grade(current_mission_index, grade)

                if current_mission_index == progress["completed_missions"]:
                    progress["completed_missions"] += 1
                    # Unlock next mission based on unlock conditions
                    for i, m in enumerate(missions):
                        if i > progress["unlocked_missions"] and is_mission_unlocked(i):
                            progress["unlocked_missions"] = i
                    save_data(progress_file, progress)

                draw_text("MISSION COMPLETE!", 48, GREEN, WIDTH // 2, HEIGHT // 2 - 50, "Arial", True)
                draw_text(f"Grade: {grade}", 36, GREEN, WIDTH // 2, HEIGHT // 2 + 20, "Arial", True)
                pygame.display.flip()
                pygame.time.wait(3000)
                game_state = MISSION_SELECT

        pygame.display.flip()

    elif game_state == GAME_OVER:
        draw_text("GAME OVER", 64, RED, WIDTH // 2, HEIGHT // 2 - 100, "Arial", True)
        draw_text("Press R to restart or E to exit", 24, WHITE, WIDTH // 2, HEIGHT // 2, "Arial", True)
        pygame.display.flip()

    elif game_state == MISSION_FAILED:
        draw_text("MISSION FAILED", 64, RED, WIDTH // 2, HEIGHT // 2 - 100, "Arial", True)

        mission = missions[current_mission_index]
        if mission["type"] == "timed_destruction":
            draw_text(f"Targets destroyed: {hits}/{mission['target']}", 24, WHITE, WIDTH // 2, HEIGHT // 2 - 30,
                      "Arial", True)
            draw_text(f"Time elapsed: {int(performance_stats['time'])}/{mission['time_limit']}s", 24, WHITE, WIDTH // 2,
                      HEIGHT // 2, "Arial", True)
        elif mission["type"] == "survival":
            draw_text(f"Time survived: {int(performance_stats['time'])}/{mission['target']}s", 24, WHITE, WIDTH // 2,
                      HEIGHT // 2 - 30, "Arial", True)
        elif mission["type"] == "timed_distance":
            draw_text(f"Distance: {performance_stats['distance']}/{mission['target']}m", 24, WHITE, WIDTH // 2,
                      HEIGHT // 2 - 30, "Arial", True)
            draw_text(f"Time elapsed: {int(performance_stats['time'])}/{mission['time_limit']}s", 24, WHITE, WIDTH // 2,
                      HEIGHT // 2, "Arial", True)
        elif mission["type"] == "precision":
            accuracy = (hits / bombs_dropped) if bombs_dropped > 0 else 0
            draw_text(f"Accuracy: {accuracy * 100:.1f}% (needed 80%)", 24, WHITE, WIDTH // 2, HEIGHT // 2 - 30, "Arial",
                      True)

        draw_text("Press R to retry or E to exit", 24, WHITE, WIDTH // 2, HEIGHT // 2 + 50, "Arial", True)
        pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()