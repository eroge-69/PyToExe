import pygame
import random
import asyncio
import platform
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Game")

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
WAREHOUSE_GRAY = (80, 80, 80)
WAREHOUSE_LINE = (60, 60, 60)
CARDBOARD = (165, 125, 80)
CARDBOARD_LINE = (100, 70, 50)
RED_SEMITRANS = (255, 0, 0, 100)
BLUE_SEMITRANS = (0, 0, 255, 100)
GREEN_SEMITRANS = (0, 255, 0, 100)

# Game object properties
ITEM_RADIUS = 40
MIN_ITEM_RADIUS = 20
BOX_SIZE = 200
MIN_BOX_SIZE = 100
OBSTACLE_RADIUS = 60
BOSS_RADIUS = 100
ITEMS = []
BOXES = []
OBSTACLES = []
BOSS = None

# Game state
score = 0
selected_item = None
time_left = 30.0
game_state = "start"
hearts = 3
level = 1
balls_sorted = 0
base_obstacle_speed = 120
speed_multiplier = 1.0
MAX_SPEED_MULTIPLIER = 3.0  # Cap for speed multiplier
temp_speed_boost = False
level_of_boost = 0
item_scale = 1.0
box_scale = 1.0
high_scores = []
entering_initials = False
current_initials = ""
choosing_reward = False
font = None  # Cached font object

def create_item():
    color = random.choice([RED, BLUE, GREEN])
    x = random.randint(ITEM_RADIUS, WIDTH - ITEM_RADIUS)
    y = random.randint(ITEM_RADIUS, HEIGHT - 600)
    return {
        "color": color,
        "pos": [x, y],
        "velocity": [0, 0],
        "last_pos": [x, y],
        "drag_time": 0,
        "touched": False
    }

def create_obstacle():
    x = random.randint(OBSTACLE_RADIUS, WIDTH - OBSTACLE_RADIUS)
    y = random.randint(OBSTACLE_RADIUS, HEIGHT - 600)
    angle = random.uniform(0, 2 * math.pi)
    return {
        "pos": [x, y],
        "velocity": [math.cos(angle) * base_obstacle_speed, math.sin(angle) * base_obstacle_speed],
        "time": 0,
        "pattern": random.choice(["straight", "zigzag", "circle"])
    }

def create_boss():
    x = WIDTH // 2
    y = HEIGHT // 2
    return {
        "pos": [x, y],
        "velocity": [0, 0],
        "time": 0
    }

def setup_boxes():
    global BOXES
    side = random.randint(0, 3)
    BOXES = []
    scaled_size = max(MIN_BOX_SIZE, BOX_SIZE * box_scale)
    open_sides = [random.choice(["top", "bottom", "left", "right"]) for _ in range(3)]
    if side == 0:  # Top
        BOXES = [
            {"color": RED_SEMITRANS, "rect": pygame.Rect(360, 100, scaled_size, scaled_size), "open_side": open_sides[0]},
            {"color": BLUE_SEMITRANS, "rect": pygame.Rect(860, 100, scaled_size, scaled_size), "open_side": open_sides[1]},
            {"color": GREEN_SEMITRANS, "rect": pygame.Rect(1360, 100, scaled_size, scaled_size), "open_side": open_sides[2]}
        ]
    elif side == 1:  # Bottom
        BOXES = [
            {"color": RED_SEMITRANS, "rect": pygame.Rect(360, HEIGHT - 300, scaled_size, scaled_size), "open_side": open_sides[0]},
            {"color": BLUE_SEMITRANS, "rect": pygame.Rect(860, HEIGHT - 300, scaled_size, scaled_size), "open_side": open_sides[1]},
            {"color": GREEN_SEMITRANS, "rect": pygame.Rect(1360, HEIGHT - 300, scaled_size, scaled_size), "open_side": open_sides[2]}
        ]
    elif side == 2:  # Left
        BOXES = [
            {"color": RED_SEMITRANS, "rect": pygame.Rect(100, 200, scaled_size, scaled_size), "open_side": open_sides[0]},
            {"color": BLUE_SEMITRANS, "rect": pygame.Rect(100, 440, scaled_size, scaled_size), "open_side": open_sides[1]},
            {"color": GREEN_SEMITRANS, "rect": pygame.Rect(100, 680, scaled_size, scaled_size), "open_side": open_sides[2]}
        ]
    elif side == 3:  # Right
        BOXES = [
            {"color": RED_SEMITRANS, "rect": pygame.Rect(WIDTH - 300, 200, scaled_size, scaled_size), "open_side": open_sides[0]},
            {"color": BLUE_SEMITRANS, "rect": pygame.Rect(WIDTH - 300, 440, scaled_size, scaled_size), "open_side": open_sides[1]},
            {"color": GREEN_SEMITRANS, "rect": pygame.Rect(WIDTH - 300, 680, scaled_size, scaled_size), "open_side": open_sides[2]}
        ]

def level_up():
    global level, speed_multiplier, temp_speed_boost, level_of_boost, box_scale, choosing_reward, OBSTACLES
    level += 1
    speed_multiplier = min(speed_multiplier * 1.05, MAX_SPEED_MULTIPLIER)
    if level % 3 == 0:
        OBSTACLES.append(create_obstacle())
    if level % 10 == 0:
        speed_multiplier = min(speed_multiplier * 1.5, MAX_SPEED_MULTIPLIER)
        temp_speed_boost = True
        level_of_boost = level
    if level % 8 == 0:
        box_scale = max(0.5, box_scale * 0.9)
    if level % 20 == 0 and (len(OBSTACLES) > 0 or hearts < 3):
        choosing_reward = True
    setup_boxes()
    ITEMS.extend([create_item() for _ in range(5)])

def setup():
    global ITEMS, OBSTACLES, BOSS, score, time_left, hearts, level, balls_sorted, speed_multiplier, temp_speed_boost, level_of_boost, item_scale, box_scale, game_state, high_scores, entering_initials, current_initials, choosing_reward, font
    ITEMS = [create_item() for _ in range(5)]
    OBSTACLES = [create_obstacle() for _ in range(3 + (level // 3))]
    BOSS = create_boss() if level >= 50 else None
    setup_boxes()
    score = 0
    time_left = 30.0
    hearts = 3
    level = 1
    balls_sorted = 0
    speed_multiplier = 1.0
    temp_speed_boost = False
    level_of_boost = 0
    item_scale = 1.0
    box_scale = 1.0
    game_state = "start"
    high_scores = []
    entering_initials = False
    current_initials = ""
    choosing_reward = False
    font = pygame.font.SysFont("arial", 48)  # Cache font
    pygame.font.init()
    pygame.display.update()

def update_obstacles(dt):
    for obstacle in OBSTACLES:
        obstacle["time"] += dt
        speed = base_obstacle_speed * speed_multiplier
        if obstacle["pattern"] == "straight":
            obstacle["pos"][0] += obstacle["velocity"][0] * dt
            obstacle["pos"][1] += obstacle["velocity"][1] * dt
        elif obstacle["pattern"] == "zigzag":
            obstacle["pos"][0] += math.cos(obstacle["time"] * 2) * speed * dt
            obstacle["pos"][1] += obstacle["velocity"][1] * dt
        elif obstacle["pattern"] == "circle":
            obstacle["pos"][0] += math.cos(obstacle["time"]) * speed * dt
            obstacle["pos"][1] += math.sin(obstacle["time"]) * speed * dt
        if obstacle["pos"][0] < OBSTACLE_RADIUS or obstacle["pos"][0] > WIDTH - OBSTACLE_RADIUS:
            obstacle["velocity"][0] *= -1
            obstacle["pos"][0] = max(OBSTACLE_RADIUS, min(WIDTH - OBSTACLE_RADIUS, obstacle["pos"][0]))
        if obstacle["pos"][1] < OBSTACLE_RADIUS or obstacle["pos"][1] > HEIGHT - 600:
            obstacle["velocity"][1] *= -1
            obstacle["pos"][1] = max(OBSTACLE_RADIUS, min(HEIGHT - 600, obstacle["pos"][1]))

def update_boss(dt):
    if BOSS and ITEMS:
        touched_items = [item for item in ITEMS if item["touched"]]
        if touched_items:
            closest_item = min(touched_items, key=lambda item: math.hypot(item["pos"][0] - BOSS["pos"][0], item["pos"][1] - BOSS["pos"][1]))
            dx = closest_item["pos"][0] - BOSS["pos"][0]
            dy = closest_item["pos"][1] - BOSS["pos"][1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                speed = base_obstacle_speed * speed_multiplier * 0.8
                BOSS["velocity"] = [dx / dist * speed, dy / dist * speed]
            BOSS["pos"][0] += BOSS["velocity"][0] * dt
            BOSS["pos"][1] += BOSS["velocity"][1] * dt
            if BOSS["pos"][0] < BOSS_RADIUS or BOSS["pos"][0] > WIDTH - BOSS_RADIUS:
                BOSS["velocity"][0] *= -1
                BOSS["pos"][0] = max(BOSS_RADIUS, min(WIDTH - BOSS_RADIUS, BOSS["pos"][0]))
            if BOSS["pos"][1] < BOSS_RADIUS or BOSS["pos"][1] > HEIGHT - 600:
                BOSS["velocity"][1] *= -1
                BOSS["pos"][1] = max(BOSS_RADIUS, min(HEIGHT - 600, BOSS["pos"][1]))

def check_collision(item_pos, item):
    for obstacle in OBSTACLES:
        dx = item_pos[0] - obstacle["pos"][0]
        dy = item_pos[1] - obstacle["pos"][1]
        if dx**2 + dy**2 < (ITEM_RADIUS * item_scale + OBSTACLE_RADIUS)**2:
            return True
    if BOSS:
        dx = item_pos[0] - BOSS["pos"][0]
        dy = item_pos[1] - BOSS["pos"][1]
        if dx**2 + dy**2 < (ITEM_RADIUS * item_scale + BOSS_RADIUS)**2:
            return True
    return False

def draw_warehouse_background():
    screen.fill(WAREHOUSE_GRAY)
    for i in range(0, WIDTH, 100):
        pygame.draw.line(screen, WAREHOUSE_LINE, (i, 0), (i, HEIGHT), 4)
    for i in range(0, HEIGHT, 100):
        pygame.draw.line(screen, WAREHOUSE_LINE, (0, i), (WIDTH, i), 4)

def draw():
    screen.fill(WAREHOUSE_GRAY)
    if game_state == "start":
        title_text = font.render("Sorting Game", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        rules = [
            "Rules:",
            "1. Drag colored balls to matching colored boxes.",
            "2. Correct match: +10 points, +2 seconds.",
            "3. Wrong match: -40 points, -3 seconds.",
            "4. Avoid gray obstacles and the black boss (level 50+).",
            "5. Collisions with obstacles/boss cost 1 heart.",
            "6. All balls sorted or deleted advances the level.",
            "7. Every 20 levels, choose to remove an obstacle or gain a heart.",
            "8. Game ends when time runs out or hearts reach 0.",
            "Press SPACE to start!"
        ]
        for i, rule in enumerate(rules):
            rule_text = font.render(rule, True, BLACK)
            rule_rect = rule_text.get_rect(center=(WIDTH // 2, 200 + i * 60))
            screen.blit(rule_text, rule_rect)
    elif game_state == "playing":
        draw_warehouse_background()
        for box in BOXES:
            # Draw cardboard base
            pygame.draw.rect(screen, CARDBOARD, box["rect"])
            # Draw flap lines, skipping the open side
            rect = box["rect"]
            if box["open_side"] != "top":
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.top), (rect.right, rect.top), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.top), (rect.left + rect.width // 2, rect.top + rect.height // 2), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.right, rect.top), (rect.right - rect.width // 2, rect.top + rect.height // 2), 4)
            if box["open_side"] != "bottom":
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.bottom), (rect.right, rect.bottom), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.bottom), (rect.left + rect.width // 2, rect.bottom - rect.height // 2), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.right, rect.bottom), (rect.right - rect.width // 2, rect.bottom - rect.height // 2), 4)
            if box["open_side"] != "left":
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.top), (rect.left + rect.width // 2, rect.top + rect.height // 2), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.left, rect.bottom), (rect.left + rect.width // 2, rect.bottom - rect.height // 2), 4)
            if box["open_side"] != "right":
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.right, rect.top), (rect.right - rect.width // 2, rect.top + rect.height // 2), 4)
                pygame.draw.line(screen, CARDBOARD_LINE, (rect.right, rect.bottom), (rect.right - rect.width // 2, rect.bottom - rect.height // 2), 4)
            # Draw semi-transparent color overlay
            pygame.draw.rect(screen, box["color"], box["rect"])
            # Draw black border
            pygame.draw.rect(screen, BLACK, box["rect"], 4)
        for obstacle in OBSTACLES:
            pygame.draw.circle(screen, WHITE, obstacle["pos"], OBSTACLE_RADIUS + 4)
            pygame.draw.circle(screen, GRAY, obstacle["pos"], OBSTACLE_RADIUS)
        if BOSS:
            pygame.draw.circle(screen, WHITE, BOSS["pos"], BOSS_RADIUS + 4)
            pygame.draw.circle(screen, BLACK, BOSS["pos"], BOSS_RADIUS)
        for item in ITEMS:
            pygame.draw.circle(screen, BLACK, item["pos"], ITEM_RADIUS * item_scale + 4)
            pygame.draw.circle(screen, item["color"], item["pos"], ITEM_RADIUS * item_scale)
        score_text = font.render(f"Score: {score}", True, BLACK)
        timer_text = font.render(f"Time: {max(0, int(time_left))}s", True, BLACK)
        hearts_text = font.render(f"Hearts: {'♥' * hearts}", True, RED)
        level_text = font.render(f"Level: {level}", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(timer_text, (WIDTH // 2 - 100, 20))
        screen.blit(hearts_text, (20, 80))
        screen.blit(level_text, (20, 140))
        if choosing_reward:
            prompt_text = font.render("Press O to remove an obstacle, H to gain a heart", True, BLACK)
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(prompt_text, prompt_rect)
    elif game_state == "game_over":
        draw_warehouse_background()
        game_over_text = font.render("Game Over! Press R to Restart", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)
        if entering_initials:
            prompt_text = font.render(f"Enter Initials: {current_initials}_", True, BLACK)
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            screen.blit(prompt_text, prompt_rect)
        else:
            high_score_text = font.render("High Scores:", True, BLACK)
            high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 160))
            screen.blit(high_score_text, high_score_rect)
            for i, (initials, hs) in enumerate(high_scores[:5]):
                hs_text = font.render(f"{i+1}. {initials}: {hs}", True, BLACK)
                hs_rect = hs_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 240 + i * 80))
                screen.blit(hs_text, hs_rect)
    pygame.display.flip()

def update_loop():
    global selected_item, score, ITEMS, time_left, game_state, hearts, balls_sorted, speed_multiplier, temp_speed_boost, BOSS, OBSTACLES, entering_initials, current_initials, high_scores, choosing_reward
    if game_state == "start":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "playing"
        draw()
        return

    if game_state == "game_over":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if entering_initials:
                    if event.key == pygame.K_RETURN and len(current_initials) == 3:
                        high_scores.append((current_initials, score))
                        high_scores.sort(key=lambda x: x[1], reverse=True)
                        entering_initials = False
                        current_initials = ""
                    elif event.key == pygame.K_BACKSPACE and current_initials:
                        current_initials = current_initials[:-1]
                    elif len(current_initials) < 3 and event.unicode.isalpha():
                        current_initials += event.unicode.upper()
                elif event.key == pygame.K_r:
                    setup()
                    game_state = "start"
        draw()
        return

    if choosing_reward:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o and OBSTACLES:
                    OBSTACLES.pop()
                    choosing_reward = False
                elif event.key == pygame.K_h and hearts < 3:
                    hearts += 1
                    choosing_reward = False
        draw()
        return

    dt = 1/60
    # Handle input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for item in ITEMS:
                item_pos = item["pos"]
                if (item_pos[0] - pos[0])**2 + (item_pos[1] - pos[1])**2 < (ITEM_RADIUS * item_scale)**2:
                    selected_item = item
                    selected_item["last_pos"] = item_pos[:]
                    selected_item["drag_time"] = 0
                    selected_item["velocity"] = [0, 0]
                    selected_item["touched"] = True
                    break
        elif event.type == pygame.MOUSEBUTTONUP and selected_item:
            pos = pygame.mouse.get_pos()
            dx = pos[0] - selected_item["last_pos"][0]
            dy = pos[1] - selected_item["last_pos"][1]
            drag_time = max(selected_item["drag_time"], 0.01)
            magnitude = math.hypot(dx, dy) / drag_time
            factor = math.exp(-((magnitude - 100)**2) / (2 * 50**2)) * 500
            selected_item["velocity"] = [min(dx / drag_time * factor, 1000), min(dy / drag_time * factor, 1000)]
            placed = False
            for box in BOXES:
                if box["rect"].collidepoint(pos):
                    if selected_item["color"] in [RED, BLUE, GREEN] and box["color"] in [RED_SEMITRANS, BLUE_SEMITRANS, GREEN_SEMITRANS]:
                        if selected_item["color"][0] == box["color"][0] and selected_item["color"][1] == box["color"][1] and selected_item["color"][2] == box["color"][2]:
                            score += 10
                            time_left += 2
                            balls_sorted += 1
                        else:
                            score = max(0, score - 40)
                            time_left = max(0, time_left - 3)
                        ITEMS.remove(selected_item)
                        placed = True
                        if not ITEMS:
                            level_up()
                        break
            selected_item = None
            if not placed and not entering_initials and (time_left <= 0 or hearts <= 0):
                entering_initials = True
                game_state = "game_over"
        elif event.type == pygame.MOUSEMOTION and selected_item:
            selected_item["pos"] = list(pygame.mouse.get_pos())
            selected_item["drag_time"] += dt

    # Update items and check collisions
    items_to_remove = []
    for item in ITEMS:
        if item != selected_item and item["touched"]:
            item["pos"][0] += item["velocity"][0] * dt
            item["pos"][1] += item["velocity"][1] * dt
            item["velocity"][0] *= 0.98
            item["velocity"][1] *= 0.98
            scaled_radius = ITEM_RADIUS * item_scale
            if item["pos"][0] < scaled_radius or item["pos"][0] > WIDTH - scaled_radius:
                item["velocity"][0] *= -1
                item["pos"][0] = max(scaled_radius, min(WIDTH - scaled_radius, item["pos"][0]))
            if item["pos"][1] < scaled_radius or item["pos"][1] > HEIGHT - 600:
                item["velocity"][1] *= -1
                item["pos"][1] = max(scaled_radius, min(HEIGHT - 600, item["pos"][1]))
            if check_collision(item["pos"], item):
                items_to_remove.append(item)

    if selected_item and check_collision(selected_item["pos"], selected_item):
        items_to_remove.append(selected_item)
        selected_item = None

    # Process item removals and check for level-up or game over
    for item in items_to_remove:
        if item in ITEMS:
            ITEMS.remove(item)
            hearts = max(0, hearts - 1)
            if not ITEMS:
                level_up()
            if hearts <= 0:
                game_state = "game_over"
                entering_initials = True

    # Update game state
    time_left = max(0, time_left - dt)
    speed_multiplier = min(speed_multiplier + 0.0001 * dt, MAX_SPEED_MULTIPLIER)
    if temp_speed_boost and level > level_of_boost:
        speed_multiplier = min(speed_multiplier * 0.8, MAX_SPEED_MULTIPLIER)
        temp_speed_boost = False
    update_obstacles(dt)
    if BOSS:
        update_boss(dt)
    if time_left <= 0 or hearts <= 0:
        game_state = "game_over"
        if not entering_initials:
            entering_initials = True
    
    draw()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / 60)  # 60 FPS

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())