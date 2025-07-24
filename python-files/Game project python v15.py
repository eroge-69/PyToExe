import pygame
import random
import sys
import time
import math
import json
import os
import base64

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_BLUE = (0, 0, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (200, 200, 200)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying game..?")
clock = pygame.time.Clock()

# Game variables
score = 0
coins = 0
game_speed = 5
base_speed = 5
player_health = 100
max_health = 100
game_paused = False
game_over = False
invincible = False
invincible_time = 0
invincible_duration = 5
space_pressed = False
bullets = []
base_defense_level = 0  # Base defense level
defense_level = 0  # Effective defense level (decreases with radiation)

# SAM Machine variables
sam_active = False
sam_can_be_activated = False
sam_activated_time = 0
sam_rocket_hits = 0
sam_escape_triggered = False
sam_escape_progress = 0
sam_escape_time_limit = 15
sam_escape_start_time = 0
sam_rainbow_color_hue = 0
sam_escape_decrease_rate = 0.07
last_sam_escape_decrease_time = 0
SAM_ESCAPE_DECREASE_INTERVAL = 1

# SAM health regeneration variables
SAM_HEAL_AMOUNT_PER_MS = 0.1
SAM_HEAL_INTERVAL_MS = 1
last_sam_heal_time = 0

# Radiation variables
radiation_level = 0
max_radiation = 100
suitable_radiation_purchased = False
radiation_reduction_start_time = 0
last_radiation_reduction_time = 0
RADIATION_REDUCTION_DELAY = 6000
RADIATION_REDUCTION_INTERVAL = 100
RADIATION_AMOUNT_PER_REDUCTION = 0.1

# Passive Healing variables
passive_healing_rate = 0
last_passive_heal_time = 0

# Pop-Up Closer variables
popup_closer_delay = 0
last_popup_close_time = 0

# Popup variables
scammer_popups = []
virus_popups = []

# Scammer messages
SCAMMER_MESSAGES = [
    "You won 10.000 coins! Click 'Yes' to get your prize!",
    "You won an upgrade! Click 'Yes' to claim your prize!",
    "You won 99.999 VBucks. Click 'Okay' to get your prize!"
]

# Virus messages
VIRUS_MESSAGES = [
    "One of your upgrade is gotten a virus! Click to 'Install' to install a Anti-Virus.",
    "ONE OF YOUR UPGRADES ARE ENCRYPTED! QUICKLY CLICK 'Yes'!!"
]

# Difficulty variable
difficulty = "Normal"

# Menu variables
show_main_menu = True
in_difficulty_menu = False
in_settings_menu = False
in_text_settings_menu = False

# Settings variables
fullscreen_enabled = False
menu_text_size = 20
ingame_text_size = 20
dialogue_text_size = 20
MIN_TEXT_SIZE = 10
MAX_TEXT_SIZE = 30

# Player
player_size = 30
player_x = 100
player_y = HEIGHT // 2
player_velocity = 0
gravity = 0.5
base_jetpack_strength = -0.8
jetpack_strength = base_jetpack_strength

# Shop variables
in_shop = False
shop_scroll_offset = 0

# Guide variables
in_guide = False
guide_scroll_offset = 0
guide_horizontal_scroll_offset = 0

# Idiot Pop-up variables
idiot_popups = []
last_idiot_popup_time = 0
idiot_popup_interval = 10000
IDIOT_POPUP_CLICK_TIME_LIMIT = 4
IDIOT_POPUP_DAMAGE_PER_2MS = 0.1
IDIOT_POPUP_DUPLICATION_MULTIPLIER = 2
IDIOT_POPUP_COINS_AWARDED = 50

# Shop items
shop_items = {
    "health_upgrade": {
        "name": "Health Upgrade",
        "description": "Increases maximum health by 50. Recommended upgrade.",
        "price": 70,
        "max_upgrades": 5,
        "upgrades": 0
    },
    "invincibility_powerup_shop": {
        "name": "Invincibility Power-Up",
        "description": "Become invincible for 5 seconds when collected",
        "price": 80,
        "max_upgrades": 5,
        "upgrades": 0,
        "duration": 5
    },
    "jetpack_upgrade": {
        "name": "Jetpack Power",
        "description": "Increases flight speed by 0.3. (On v17 though. :P)",
        "price": 99999999999999999,
        "max_upgrades": 999999,
        "upgrades": 0,
        "price_increase": 0
    },
    "sam_machine": {
        "name": "S.A.M Machine",
        "description": "Oh my god. Why is it here???",
        "price": 200,
        "max_upgrades": 1,
        "upgrades": 0
    },
    "healing_powerup": {
        "name": "Healing Power-Up",
        "description": "Spawns + power-ups that heal 30 HP (40 more per upgrade)",
        "price": 100,
        "max_upgrades": 2,
        "upgrades": 0,
        "base_heal_amount": 30,
        "heal_increase_per_upgrade": 40
    },
    "passive_regeneration": {
        "name": "Passive Regeneration",
        "description": "Restores health slowly, Made by StickSLASH (+0.1 HP/ms)",
        "price": 100,
        "max_upgrades": 5,
        "upgrades": 0,
        "regen_per_upgrade": 0.1
    },
    "suitable_radiation": {
        "name": "Suitable Radiation",
        "description": "Reducing radiation after 6 seconds. Good for health!",
        "price": 150,
        "max_upgrades": 1,
        "upgrades": 0
    },
    "popup_closer": {
        "name": "Pop-Up Closer",
        "description": "Automatically closes Annoying Pop-ups (4s -> 1s)",
        "price": 150,
        "max_upgrades": 3,
        "upgrades": 0,
        "base_delay": 4,
        "delay_reduction_per_upgrade": 1
    },
    "defense_upgrade": {
        "name": "Defense Upgrade",
        "description": "Reduces damage taken from obstacles by 10% per level (max 50%).",
        "price": 100,
        "upgrades": 0,
        "max_upgrades": 5,
        "defense_per_upgrade": 0.1,
        "price_increase": 50,
        "base_price": 100
    },
    "anti_scam": {
        "name": "Anti-Scam",
        "description": "Close pop-ups faster (5s -> 1s) and earn coins when closing them.",
        "price": 175,
        "upgrades": 0,
        "max_upgrades": 5,
        "base_time": 5.0,
        "time_reduction": 1.0,
        "price_increase": 50,
        "base_price": 175
    }
}

# Permanent Upgrade System
permanent_upgrades = {
    "suitable_radiation_purchased": False
}

# Guide content
guide_content = """
# A guide for game.

## Gameplay
- **Movement**: Hold **Space** to activate the jetpack. The player rises against gravity and falls when released.
- **Objective**: Avoid obstacles and rockets, collect coins, and achieve the highest score possible.
- **Health**: The red bar in the top left shows your health. Colliding with obstacles or rockets reduces health. The game ends if health reaches 0.
- **Radiation**: The orange bar shows radiation level. Above 50%, it causes health loss over time and reduces defense. Radiation power-downs and rockets increase it.
- **Defense**: The gray bar shows defense level. As radiation increases, defense decreases (at 100% radiation, defense is 0%). The red portion shows lost defense.
- **Coins**: Yellow squares are coins, collect them to spend in the shop.

## Controls
- **Space**: Activates the jetpack, moving the player upward.
- **T**: Activates the S.A.M Machine if purchased and available.
- **Left Click**: Fires bullets when S.A.M is active (to destroy rockets).
- **ESC**: Pauses the game or exits.
- **Right/Left Arrow Keys (in Guide)**: Scrolls the guide horizontally.
- **Up/Down Arrow Keys (in Guide)**: Scrolls the guide vertically.

## Power-Ups and Power-Downs
- **Invincibility (Purple)**: Grants invincibility for 5 seconds (or more with upgrades) when collected.
- **SAM Power-Up (Blue)**: Grants the ability to activate S.A.M. Press 'T' to activate.
- **Radiation (Red)**: Increases radiation level by 70%, high radiation causes health loss and defense reduction.

## S.A.M Machine
- When S.A.M is activated, obstacles disappear, and rockets appear more frequently.
- After 5 rocket hits, escape mode begins. Press **Space** to increase escape progress (green bar).
- Reach 100% within 15 seconds to escape S.A.M successfully. Otherwise, lose 99% of health.

## Pop-ups

### IDIOT Pop-ups
- Randomly appearing gray boxes that bounce around the screen.
- Click the red 'X' in the top right to close and earn 25 coins.
- No longer deal damage to the player.
- If Pop-Up Closer is purchased, pop-ups close automatically (from 4s to 1s).

### SCAMMER Pop-ups
- Yellow popups with tempting offers.
- Clicking the main button will do something mysterious.
- Click the red 'X' in the top right to close and earn 10 coins.
- Auto-close time is reduced by Anti-Scam upgrades.

### VIRUS Pop-ups
- Red popups with warning messages.
- Clicking the main button will do something mysterious.
- Click the red 'X' in the top right to close and earn 10 coins.
- Auto-close time is reduced by Anti-Scam upgrades.

### Anti-Scam Upgrade
- Reduces auto-close time for all popups (5s -> 1s at max level).
- Earn coins when closing popups.
- Protects against Virus popups removing important upgrades.

## Shop
- **Health Upgrade**: Increases maximum health by 50 (max 5 times).
- **Invincibility Power-Up**: Increases invincibility duration and allows power-up to spawn in-game.
- **Jetpack Power**: Increases jetpack speed by 0.3 (Not on this version).
- **S.A.M Machine**: Oh my god. Why is that here?
- **Healing power-up**: No guide yet...
- **Passive Regeneration**: Restores 0.1 HP/s (max 5 times).
- **Suitable Radiation**: Reduces radiation after a 6-second delay.
- **Pop-Up Closer**: Automatically closes pop-ups (4s -> 1s).
- **Defense Upgrade**: Provides 10% damage resistance (max 50%).
"""

# Save/load game functions
def save_game():
    global coins, shop_items, permanent_upgrades, difficulty
    save_data = {
        "coins": coins,
        "shop_items": {key: {"upgrades": item["upgrades"]} for key, item in shop_items.items()},
        "permanent_upgrades": permanent_upgrades,
        "difficulty": difficulty
    }
    try:
        encoded_data = base64.b64encode(json.dumps(save_data, indent=4).encode('utf-8')).decode('utf-8')
        with open("savegame.txt", "w") as f:
            f.write(encoded_data)
        print("Game saved!")
    except Exception as e:
        print(f"Save error: {e}")

def load_game():
    global coins, shop_items, permanent_upgrades, difficulty, max_health, player_health, invincible_duration, jetpack_strength, sam_can_be_activated, passive_healing_rate, suitable_radiation_purchased, popup_closer_delay, base_defense_level, defense_level
    try:
        if os.path.exists("savegame.txt"):
            with open("savegame.txt", "r") as f:
                encoded_data = f.read()
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            save_data = json.loads(decoded_data)
            coins = save_data.get("coins", 0)
            for item_name, item_data in save_data.get("shop_items", {}).items():
                if item_name in shop_items:
                    shop_items[item_name]["upgrades"] = item_data.get("upgrades", 0)
            permanent_upgrades.update(save_data.get("permanent_upgrades", {}))
            difficulty = save_data.get("difficulty", "Normal")
            
            # Update game state based on loaded data
            max_health = 100 + (shop_items["health_upgrade"]["upgrades"] * 50)
            player_health = max_health
            invincible_duration = 5 + (3 * shop_items["invincibility_powerup_shop"]["upgrades"])
            jetpack_strength = base_jetpack_strength - (0.3 * shop_items["jetpack_upgrade"]["upgrades"])
            sam_can_be_activated = shop_items["sam_machine"]["upgrades"] > 0
            passive_healing_rate = shop_items["passive_regeneration"]["upgrades"] * shop_items["passive_regeneration"]["regen_per_upgrade"]
            suitable_radiation_purchased = permanent_upgrades.get("suitable_radiation_purchased", False)
            popup_closer_delay = shop_items["popup_closer"]["base_delay"] - (shop_items["popup_closer"]["upgrades"] * shop_items["popup_closer"]["delay_reduction_per_upgrade"]) if shop_items["popup_closer"]["upgrades"] > 0 else 0
            base_defense_level = shop_items["defense_upgrade"]["upgrades"] * shop_items["defense_upgrade"]["defense_per_upgrade"]
            defense_level = base_defense_level * (1 - radiation_level / max_radiation)  # Effective defense based on radiation
            
            apply_difficulty_settings()
            print("Game loaded!")
        else:
            print("Save file not found, continuing with default values.")
    except Exception as e:
        print(f"Load error: {e}")

# Load game data at start
load_game()

def apply_permanent_upgrades():
    global suitable_radiation_purchased
    suitable_radiation_purchased = permanent_upgrades.get("suitable_radiation_purchased", False)

apply_permanent_upgrades()

# Game objects
obstacles = []
coins_list = []
rockets = []
powerups = []
last_obstacle_time = 0
obstacle_interval = 1500
last_coin_time = 0
coin_interval = 200
last_rocket_time = 0
rocket_interval = 5000
last_powerup_time = 0
powerup_interval = 10000
last_sam_powerup_time = 0
sam_powerup_interval = 60000
last_bullet_time = 0
bullet_interval = 300

# Fonts (will be updated dynamically)
font_small = None
font_medium = None
font_large = None
font_menu = None
font_ingame = None
font_dialogue = None

def update_fonts():
    global font_small, font_medium, font_large, font_menu, font_ingame, font_dialogue
    font_small = pygame.font.SysFont('Arial', 20)
    font_medium = pygame.font.SysFont('Arial', 30)
    font_large = pygame.font.SysFont('Arial', 50)
    font_menu = pygame.font.SysFont('Arial', menu_text_size)
    font_ingame = pygame.font.SysFont('Arial', ingame_text_size)
    font_dialogue = pygame.font.SysFont('Arial', dialogue_text_size)

# Initialize fonts
update_fonts()

# Adjust game parameters based on difficulty
def apply_difficulty_settings():
    global base_speed, obstacle_interval, rocket_interval, powerup_interval
    if difficulty == "Easy":
        base_speed = 4
        obstacle_interval = 2000
        rocket_interval = 7000
        powerup_interval = 15000
    elif difficulty == "Normal":
        base_speed = 5
        obstacle_interval = 1500
        rocket_interval = 5000
        powerup_interval = 10000
    elif difficulty == "Hard":
        base_speed = 6
        obstacle_interval = 1000
        rocket_interval = 3000
        powerup_interval = 7000

apply_difficulty_settings()

def reset_game():
    global player_y, player_velocity, obstacles, coins_list, rockets, powerups, bullets, score, game_speed, player_health, invincible, invincible_time, sam_active, sam_can_be_activated, sam_activated_time, sam_rocket_hits, sam_escape_triggered, sam_escape_progress, sam_escape_time_limit, sam_escape_start_time, radiation_level, passive_healing_rate, last_passive_heal_time, jetpack_strength, idiot_popups, last_idiot_popup_time, radiation_reduction_start_time, last_radiation_reduction_time, last_sam_escape_decrease_time, last_sam_heal_time, popup_closer_delay, last_popup_close_time, base_defense_level, defense_level
    player_y = HEIGHT // 2
    player_velocity = 0
    obstacles = []
    coins_list = []
    rockets = []
    powerups = []
    bullets = []
    idiot_popups = []
    score = 0
    game_speed = base_speed
    player_health = max_health
    invincible = False
    invincible_time = 0
    sam_active = False
    sam_activated_time = 0
    sam_rocket_hits = 0
    sam_escape_triggered = False
    sam_escape_progress = 0
    sam_escape_start_time = 0
    radiation_level = 0
    passive_healing_rate = shop_items["passive_regeneration"]["upgrades"] * shop_items["passive_regeneration"]["regen_per_upgrade"]
    last_passive_heal_time = 0
    jetpack_strength = base_jetpack_strength - (0.3 * shop_items["jetpack_upgrade"]["upgrades"])
    base_defense_level = shop_items["defense_upgrade"]["upgrades"] * shop_items["defense_upgrade"]["defense_per_upgrade"]
    defense_level = base_defense_level  # Defense is full at reset since radiation is 0
    last_idiot_popup_time = pygame.time.get_ticks()
    radiation_reduction_start_time = 0
    last_radiation_reduction_time = 0
    last_sam_escape_decrease_time = 0
    last_sam_heal_time = 0
    last_popup_close_time = 0
    popup_closer_delay = shop_items["popup_closer"]["base_delay"] - (shop_items["popup_closer"]["upgrades"] * shop_items["popup_closer"]["delay_reduction_per_upgrade"]) if shop_items["popup_closer"]["upgrades"] > 0 else 0
    if not permanent_upgrades.get("suitable_radiation_purchased", False):
        shop_items["suitable_radiation"]["upgrades"] = 0

def spawn_obstacle():
    height = random.randint(50, 150)
    gap = random.randint(150, 250)
    top_obstacle = pygame.Rect(WIDTH, 0, 50, HEIGHT // 2 - gap // 2)
    bottom_obstacle = pygame.Rect(WIDTH, HEIGHT // 2 + gap // 2, 50, HEIGHT)
    obstacles.extend([top_obstacle, bottom_obstacle])

def spawn_coin():
    y = random.randint(50, HEIGHT - 50)
    coins_list.append(pygame.Rect(WIDTH, y, 20, 20))

def spawn_rocket():
    y = random.randint(50, HEIGHT - 50)
    rockets.append(pygame.Rect(WIDTH, y, 40, 20))

def spawn_invincibility_powerup_in_game():
    y = random.randint(50, HEIGHT - 50)
    powerups.append({"rect": pygame.Rect(WIDTH, y, 25, 25), "type": "invincibility_in_game"})

def spawn_sam_powerup():
    y = random.randint(50, HEIGHT - 50)
    powerups.append({"rect": pygame.Rect(WIDTH, y, 30, 30), "type": "sam_powerup"})

def spawn_healing_powerup():
    if shop_items["healing_powerup"]["upgrades"] > 0:
        y = random.randint(50, HEIGHT - 50)
        heal_amount = shop_items["healing_powerup"]["base_heal_amount"] + \
                     (shop_items["healing_powerup"]["upgrades"] * shop_items["healing_powerup"]["heal_increase_per_upgrade"])
        powerups.append({"rect": pygame.Rect(WIDTH, y, 30, 30), "type": "healing_powerup", "heal_amount": heal_amount})

def spawn_radiation_powerdown():
    y = random.randint(50, HEIGHT - 50)
    powerups.append({"rect": pygame.Rect(WIDTH, y, 25, 25), "type": "radiation_powerdown"})

def spawn_virus_popup():
    global virus_popups
    # Create a popup with random position and message
    popup_width, popup_height = 350, 180
    x = random.randint(50, WIDTH - popup_width - 50)
    y = random.randint(50, HEIGHT - popup_height - 50)
    
    # Create a rect for the popup
    popup_rect = pygame.Rect(x, y, popup_width, popup_height)
    
    # Choose a random message
    message = random.choice(VIRUS_MESSAGES)
    
    # Calculate auto-close time based on Anti-Scam upgrades
    auto_close_time = 8000  # 8 seconds base
    anti_scam_upgrades = shop_items["anti_scam"]["upgrades"]
    if anti_scam_upgrades > 0:
        auto_close_time = max(1000, 8000 - (anti_scam_upgrades * 1600))  # 8s, 6.4s, 4.8s, 3.2s, 1.6s, 1s
    
    # Create button rect at the bottom of the popup
    button_width, button_height = 100, 30
    button_x = popup_rect.x + popup_rect.width - 120  # Position on the right side
    button_y = popup_rect.y + popup_rect.height - 40
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Add the popup to the list
    virus_popups.append({
        "rect": popup_rect,
        "message": message,
        "spawn_time": pygame.time.get_ticks(),
        "button_text": "Install",
        "button_rect": button_rect,
        "auto_close_time": auto_close_time,
        "coins_awarded": 25
    })

def spawn_scammer_popup():
    global scammer_popups
    # Create a popup with random position and message
    popup_width, popup_height = 300, 150
    x = random.randint(50, WIDTH - popup_width - 50)
    y = random.randint(50, HEIGHT - popup_height - 50)
    
    # Create a rect for the popup
    popup_rect = pygame.Rect(x, y, popup_width, popup_height)
    
    # Choose a random message
    message = random.choice(SCAMMER_MESSAGES)
    
    # Calculate auto-close time based on Anti-Scam upgrades
    auto_close_time = 10000  # 10 seconds base
    anti_scam_upgrades = shop_items["anti_scam"]["upgrades"]
    if anti_scam_upgrades > 0:
        auto_close_time = max(1000, 10000 - (anti_scam_upgrades * 2000))  # 10s, 8s, 6s, 4s, 2s, 1s
    
    # Create button rect at the bottom of the popup
    button_width, button_height = 80, 30
    button_x = popup_rect.x + (popup_rect.width - button_width) // 2
    button_y = popup_rect.y + popup_rect.height - 40
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Add the popup to the list
    scammer_popups.append({
        "rect": popup_rect,
        "message": message,
        "spawn_time": pygame.time.get_ticks(),
        "button_text": random.choice(["Yes", "Okay"]),
        "button_rect": button_rect,
        "auto_close_time": auto_close_time,
        "coins_awarded": 25
    })

def spawn_idiot_popup(initial_duplication_damage_level=1.0):
    popup_width, popup_height = 200, 100
    x = random.randint(0, WIDTH - popup_width)
    y = random.randint(0, HEIGHT - popup_height)
    dx = random.choice([-1, 1]) * random.randint(1, 3)
    dy = random.choice([-1, 1]) * random.randint(1, 3)
    
    # Calculate auto-close time based on Anti-Scam upgrades
    auto_close_time = 4000  # 4 seconds base
    anti_scam_upgrades = shop_items["anti_scam"]["upgrades"]
    if anti_scam_upgrades > 0:
        auto_close_time = max(1000, 4000 - (anti_scam_upgrades * 800))  # 4s, 3.2s, 2.4s, 1.6s, 0.8s, 1s
    
    idiot_popups.append({
        "rect": pygame.Rect(x, y, popup_width, popup_height),
        "spawn_time_ms": pygame.time.get_ticks(),
        "dx": dx,
        "dy": dy,
        "duplication_damage_level": initial_duplication_damage_level,
        "last_damage_apply_time_ms": pygame.time.get_ticks(),
        "type": "idiot",
        "auto_close_time": auto_close_time,
        "coins_awarded": 25
    })

def draw_player():
    if sam_active:
        pygame.draw.rect(screen, DARK_BLUE, (player_x, player_y, player_size, player_size))
    elif invincible and int(time.time() * 2) % 2 == 0:
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    else:
        pygame.draw.rect(screen, GREEN, (player_x, player_y, player_size, player_size))

def draw_health_bar():
    bar_width = 200
    bar_height = 20
    fill = (player_health / max_health) * bar_width
    outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
    fill_rect = pygame.Rect(10, 10, fill, bar_height)
    if sam_active:
        global sam_rainbow_color_hue
        sam_rainbow_color_hue = (sam_rainbow_color_hue + 5) % 360
        rainbow_color = hsv_to_rgb(sam_rainbow_color_hue, 1, 1)
        pygame.draw.rect(screen, rainbow_color, fill_rect)
    else:
        pygame.draw.rect(screen, RED, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

def draw_defense_bar():
    bar_width = 200
    bar_height = 20
    base_fill = (base_defense_level / 0.5) * bar_width  # Maximum 50% defense
    effective_fill = (defense_level / 0.5) * bar_width
    outline_rect = pygame.Rect(10, 70, bar_width, bar_height)
    base_fill_rect = pygame.Rect(10, 70, base_fill, bar_height)
    effective_fill_rect = pygame.Rect(10, 70, effective_fill, bar_height)
    lost_fill_rect = pygame.Rect(10 + effective_fill, 70, base_fill - effective_fill, bar_height)
    pygame.draw.rect(screen, GRAY, base_fill_rect)  # Base defense (gray)
    pygame.draw.rect(screen, RED, lost_fill_rect)   # Lost defense (red)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)
    defense_text = font_small.render(f"Defense: {defense_level * 100:.0f}%", True, WHITE)
    screen.blit(defense_text, (outline_rect.right + 5, 70))

def hsv_to_rgb(h, s, v):
    h = h / 60.0
    i = int(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    if i == 0: return (int(v * 255), int(t * 255), int(p * 255))
    elif i == 1: return (int(q * 255), int(v * 255), int(p * 255))
    elif i == 2: return (int(p * 255), int(v * 255), int(t * 255))
    elif i == 3: return (int(p * 255), int(q * 255), int(v * 255))
    elif i == 4: return (int(t * 255), int(p * 255), int(v * 255))
    else: return (int(v * 255), int(p * 255), int(q * 255))

def draw_hud():
    draw_health_bar()
    draw_defense_bar()  # Draw new defense bar
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))
    coin_text = font_small.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(coin_text, (WIDTH - 150, 40))
    jetpack_text = font_small.render(f"Jetpack: {abs(jetpack_strength):.1f}", True, GREEN)
    screen.blit(jetpack_text, (WIDTH - 150, 70))
    bar_width = 200
    bar_height = 20
    radiation_fill = (radiation_level / max_radiation) * bar_width
    radiation_outline_rect = pygame.Rect(10, 40, bar_width, bar_height)
    radiation_fill_rect = pygame.Rect(10, 40, radiation_fill, bar_height)
    pygame.draw.rect(screen, ORANGE, radiation_fill_rect)
    pygame.draw.rect(screen, WHITE, radiation_outline_rect, 2)
    radiation_text = font_small.render(f"Rad: {radiation_level:.0f}%", True, WHITE)
    screen.blit(radiation_text, (radiation_outline_rect.right + 5, 40))
    if invincible:
        remaining = max(0, invincible_duration - (time.time() - invincible_time))
        inv_text = font_small.render(f"Invincible: {remaining:.1f}s", True, BLUE)
        screen.blit(inv_text, (WIDTH // 2 - 70, 10))
    if sam_active:
        sam_text = font_small.render("S.A.M Active!", True, DARK_BLUE)
        screen.blit(sam_text, (WIDTH // 2 - 70, 40))
        sam_hits_text = font_small.render(f"SAM Hits: {sam_rocket_hits}/5", True, DARK_BLUE)
        screen.blit(sam_hits_text, (WIDTH // 2 - 70, 70))
        if sam_escape_triggered:
            draw_sam_escape_bars()

def draw_sam_escape_bars():
    bar_width = 300
    bar_height = 30
    time_elapsed = time.time() - sam_escape_start_time
    time_remaining = max(0, sam_escape_time_limit - time_elapsed)
    time_fill = (time_remaining / sam_escape_time_limit) * bar_width
    time_outline_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, HEIGHT - 100, bar_width, bar_height)
    time_fill_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, HEIGHT - 100, time_fill, bar_height)
    pygame.draw.rect(screen, RED, time_fill_rect)
    pygame.draw.rect(screen, WHITE, time_outline_rect, 2)
    time_text = font_small.render(f"Time: {time_remaining:.1f}s", True, WHITE)
    screen.blit(time_text, (time_outline_rect.centerx - time_text.get_width() // 2, time_outline_rect.centery - time_text.get_height() // 2))
    escape_fill = (sam_escape_progress / 100) * bar_width
    escape_outline_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, HEIGHT - 60, bar_width, bar_height)
    escape_fill_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, HEIGHT - 60, escape_fill, bar_height)
    pygame.draw.rect(screen, GREEN, escape_fill_rect)
    pygame.draw.rect(screen, WHITE, escape_outline_rect, 2)
    escape_text = font_small.render(f"Escape: {sam_escape_progress:.0f}%", True, WHITE)
    screen.blit(escape_text, (escape_outline_rect.centerx - escape_text.get_width() // 2, escape_outline_rect.centery - escape_text.get_height() // 2))

def draw_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Game Paused", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    resume_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
    shop_button = pygame.Rect(WIDTH // 2 - 100, 270, 200, 50)
    save_button = pygame.Rect(WIDTH // 2 - 100, 340, 200, 50)
    load_button = pygame.Rect(WIDTH // 2 - 100, 410, 200, 50)
    main_menu_button = pygame.Rect(WIDTH // 2 - 100, 480, 200, 50)
    exit_button = pygame.Rect(WIDTH // 2 - 100, 550, 200, 50)
    pygame.draw.rect(screen, GREEN, resume_button)
    pygame.draw.rect(screen, YELLOW, shop_button)
    pygame.draw.rect(screen, BLUE, save_button)
    pygame.draw.rect(screen, BLUE, load_button)
    pygame.draw.rect(screen, BLUE, main_menu_button)
    pygame.draw.rect(screen, RED, exit_button)
    resume_text = font_medium.render("Resume", True, BLACK)
    shop_text = font_medium.render("Shop", True, BLACK)
    save_text = font_medium.render("Save Game", True, BLACK)
    load_text = font_medium.render("Load Game", True, BLACK)
    main_menu_text = font_medium.render("Main Menu", True, BLACK)
    exit_text = font_medium.render("Exit", True, BLACK)
    screen.blit(resume_text, (resume_button.centerx - resume_text.get_width() // 2, resume_button.centery - resume_text.get_height() // 2))
    screen.blit(shop_text, (shop_button.centerx - shop_text.get_width() // 2, shop_button.centery - shop_text.get_height() // 2))
    screen.blit(save_text, (save_button.centerx - save_text.get_width() // 2, save_button.centery - save_text.get_height() // 2))
    screen.blit(load_text, (load_button.centerx - load_text.get_width() // 2, load_button.centery - load_text.get_height() // 2))
    screen.blit(main_menu_text, (main_menu_button.centerx - main_menu_text.get_width() // 2, main_menu_button.centery - main_menu_text.get_height() // 2))
    screen.blit(exit_text, (exit_button.centerx - exit_text.get_width() // 2, exit_button.centery - exit_text.get_height() // 2))
    return resume_button, shop_button, save_button, load_button, main_menu_button, exit_button

def draw_shop():
    global shop_scroll_offset
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Shop", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
    coin_text = font_medium.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(coin_text, (WIDTH // 2 - coin_text.get_width() // 2, 80))
    item_buttons = []
    total_items_height = len(shop_items) * 100
    shop_display_y_start = 150
    shop_display_height = HEIGHT - shop_display_y_start - 80
    max_scroll_offset = max(0, total_items_height - shop_display_height)
    shop_scroll_offset = max(0, min(shop_scroll_offset, max_scroll_offset))
    scrollable_surface = pygame.Surface((WIDTH - 200, total_items_height), pygame.SRCALPHA)
    y_offset_on_surface = 0
    for item_name, item_data in shop_items.items():
        display_upgrades = item_data["upgrades"]
        if item_name == "suitable_radiation":
            display_upgrades = 1 if permanent_upgrades.get("suitable_radiation_purchased", False) else 0
        item_rect = pygame.Rect(0, y_offset_on_surface, WIDTH - 200, 80)
        pygame.draw.rect(scrollable_surface, GRAY, item_rect)
        pygame.draw.rect(scrollable_surface, WHITE, item_rect, 2)
        name_text = font_medium.render(item_data["name"], True, WHITE)
        scrollable_surface.blit(name_text, (10, y_offset_on_surface + 10))
        desc_text = font_small.render(item_data["description"], True, WHITE)
        scrollable_surface.blit(desc_text, (10, y_offset_on_surface + 35))
        is_maxed = False
        if item_name == "suitable_radiation":
            is_maxed = permanent_upgrades.get("suitable_radiation_purchased", False)
        else:
            is_maxed = (item_data["upgrades"] >= item_data["max_upgrades"])
        if not is_maxed:
            price = item_data["price"] + (item_data["upgrades"] * item_data.get("price_increase", 0))
            price_text = font_small.render(f"Price: {price} coins", True, YELLOW)
            scrollable_surface.blit(price_text, (10, y_offset_on_surface + 55))
            buy_button_local = pygame.Rect(WIDTH - 280, y_offset_on_surface + 20, 70, 40)
            pygame.draw.rect(scrollable_surface, GREEN, buy_button_local)
            buy_text = font_small.render("Buy", True, BLACK)
            scrollable_surface.blit(buy_text, (buy_button_local.centerx - buy_text.get_width() // 2, buy_button_local.centery - buy_text.get_height() // 2))
            buy_button_global = pygame.Rect(100 + buy_button_local.x, shop_display_y_start + buy_button_local.y - shop_scroll_offset, buy_button_local.width, buy_button_local.height)
            item_buttons.append((item_name, buy_button_global, price))
        else:
            max_text = font_small.render("MAXED", True, GREEN)
            scrollable_surface.blit(max_text, (WIDTH - 280, y_offset_on_surface + 30))
        if item_data["max_upgrades"] != float('inf'):
            upgrades_text = font_small.render(f"Upgrades: {display_upgrades}/{item_data['max_upgrades']}", True, WHITE)
            scrollable_surface.blit(upgrades_text, (WIDTH - 380, y_offset_on_surface + 55))
        else:
            upgrades_text = font_small.render(f"Purchased: {display_upgrades}", True, WHITE)
            scrollable_surface.blit(upgrades_text, (WIDTH - 380, y_offset_on_surface + 55))
        y_offset_on_surface += 100
    screen.blit(scrollable_surface, (100, shop_display_y_start), (0, shop_scroll_offset, WIDTH - 200, shop_display_height))
    if total_items_height > shop_display_height:
        scrollbar_width = 10
        scrollbar_x = WIDTH - 90
        scrollbar_height = (shop_display_height / total_items_height) * shop_display_height
        scrollbar_y = shop_display_y_start + (shop_scroll_offset / total_items_height) * shop_display_height
        scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, LIGHT_GRAY, scrollbar_rect, border_radius=5)
    back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 60, 200, 50)
    pygame.draw.rect(screen, RED, back_button)
    back_text = font_medium.render("Back", True, BLACK)
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))
    return item_buttons, back_button

def draw_guide():
    global guide_scroll_offset, guide_horizontal_scroll_offset
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Game Guide", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
    
    # Split guide text into lines and calculate approximate height and width
    guide_lines = guide_content.split('\n')
    line_height = font_small.get_height()
    total_guide_height = len(guide_lines) * line_height
    max_line_width = max([font_small.size(line)[0] for line in guide_lines])
    total_guide_width = max_line_width
    guide_display_y_start = 100
    guide_display_height = HEIGHT - guide_display_y_start - 80
    guide_display_width = WIDTH - 200
    max_scroll_offset = max(0, total_guide_height - guide_display_height)
    max_horizontal_scroll_offset = max(0, total_guide_width - guide_display_width)
    guide_scroll_offset = max(0, min(guide_scroll_offset, max_horizontal_scroll_offset))
    guide_horizontal_scroll_offset = max(0, min(guide_horizontal_scroll_offset, max_horizontal_scroll_offset))
    
    # Scrollable surface
    scrollable_surface = pygame.Surface((total_guide_width, total_guide_height), pygame.SRCALPHA)
    y_offset = 0
    for line in guide_lines:
        text = font_small.render(line, True, WHITE)
        scrollable_surface.blit(text, (0, y_offset))
        y_offset += line_height
    screen.blit(scrollable_surface, (100, guide_display_y_start), (guide_horizontal_scroll_offset, guide_scroll_offset, guide_display_width, guide_display_height))
    
    # Vertical scrollbar
    if total_guide_height > guide_display_height:
        scrollbar_width = 10
        scrollbar_x = WIDTH - 90
        scrollbar_height = (guide_display_height / total_guide_height) * guide_display_height
        scrollbar_y = guide_display_y_start + (guide_scroll_offset / total_guide_height) * guide_display_height
        scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, LIGHT_GRAY, scrollbar_rect, border_radius=5)
    
    # Horizontal scrollbar
    if total_guide_width > guide_display_width:
        scrollbar_height = 10
        scrollbar_y = HEIGHT - 80
        scrollbar_width = (guide_display_width / total_guide_width) * guide_display_width
        scrollbar_x = 100 + (guide_horizontal_scroll_offset / total_guide_width) * guide_display_width
        scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, LIGHT_GRAY, scrollbar_rect, border_radius=5)
    
    # Menu button (top right)
    menu_button = pygame.Rect(WIDTH - 150, 30, 100, 40)
    pygame.draw.rect(screen, BLUE, menu_button)
    menu_text = font_medium.render("Menu", True, BLACK)
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))
    
    return menu_button

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Game Over", True, RED)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 180))
    coins_text = font_medium.render(f"Total Coins: {coins}", True, YELLOW)
    screen.blit(coins_text, (WIDTH // 2 - coins_text.get_width() // 2, 220))
    restart_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
    shop_button = pygame.Rect(WIDTH // 2 - 100, 370, 200, 50)
    main_menu_button = pygame.Rect(WIDTH // 2 - 100, 440, 200, 50)
    exit_button = pygame.Rect(WIDTH // 2 - 100, 510, 200, 50)
    pygame.draw.rect(screen, GREEN, restart_button)
    pygame.draw.rect(screen, YELLOW, shop_button)
    pygame.draw.rect(screen, BLUE, main_menu_button)
    pygame.draw.rect(screen, RED, exit_button)
    restart_text = font_medium.render("Restart", True, BLACK)
    shop_text = font_medium.render("Shop", True, BLACK)
    main_menu_text = font_medium.render("Main Menu", True, BLACK)
    exit_text = font_medium.render("Exit", True, BLACK)
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width() // 2, restart_button.centery - restart_text.get_height() // 2))
    screen.blit(shop_text, (shop_button.centerx - shop_text.get_width() // 2, shop_button.centery - shop_text.get_height() // 2))
    screen.blit(main_menu_text, (main_menu_button.centerx - main_menu_text.get_width() // 2, main_menu_button.centery - main_menu_text.get_height() // 2))
    screen.blit(exit_text, (exit_button.centerx - exit_text.get_width() // 2, exit_button.centery - exit_text.get_height() // 2))
    return restart_button, shop_button, main_menu_button, exit_button

def check_all_upgrades_purchased():
    # Check if all upgrades except jetpack_upgrade are at max level
    for item_name, item in shop_items.items():
        if item_name == "jetpack_upgrade":
            continue  # Skip jetpack_upgrade as it's not required
        if item["upgrades"] < item.get("max_upgrades", 1):
            return False
    return True

def draw_main_menu():
    all_upgrades_purchased = check_all_upgrades_purchased()
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    title_text = font_large.render("Flying Game..?", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Calculate button positions
    button_width, button_height = 200, 50
    button_x = WIDTH // 2 - button_width // 2
    buttons = []
    
    # Add buttons to the list with their y-positions
    buttons.append(("Settings", ORANGE, 150))
    buttons.append(("Start Game", GREEN, 210))
    buttons.append(("Difficulty", YELLOW, 270))
    buttons.append(("Guide", PURPLE, 330))
    buttons.append(("Save", BLUE, 390))
    buttons.append(("Load", BLUE, 450))
    
    # Add COMPLETED button if all upgrades are purchased
    if all_upgrades_purchased:
        buttons.append(("COMPLETED", (255, 215, 0), 510))  # Gold color for COMPLETED
    else:
        buttons.append(("Exit", RED, 510))
    
    # Draw buttons and store their rects
    button_rects = {}
    for text, color, y in buttons:
        button_rect = pygame.Rect(button_x, y, button_width, button_height)
        pygame.draw.rect(screen, color, button_rect)
        button_text = font_menu.render(text, True, BLACK)
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, 
                                 button_rect.centery - button_text.get_height() // 2))
        button_rects[text.lower().replace(" ", "_") + "_button"] = button_rect
    
    # Return all button rects in the same format as before
    return (
        button_rects["settings_button"],
        button_rects["start_game_button"],
        button_rects["difficulty_button"],
        button_rects["guide_button"],
        button_rects["save_button"],
        button_rects["load_button"],
        button_rects["completed_button"] if all_upgrades_purchased else button_rects["exit_button"]
    )

def draw_difficulty_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Select Difficulty", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    easy_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
    normal_button = pygame.Rect(WIDTH // 2 - 100, 270, 200, 50)
    hard_button = pygame.Rect(WIDTH // 2 - 100, 340, 200, 50)
    menu_button = pygame.Rect(WIDTH - 150, 30, 100, 40)
    button_color_easy = GREEN if difficulty == "Easy" else GRAY
    button_color_normal = YELLOW if difficulty == "Normal" else GRAY
    button_color_hard = RED if difficulty == "Hard" else GRAY
    pygame.draw.rect(screen, button_color_easy, easy_button)
    pygame.draw.rect(screen, button_color_normal, normal_button)
    pygame.draw.rect(screen, button_color_hard, hard_button)
    pygame.draw.rect(screen, BLUE, menu_button)
    easy_text = font_medium.render("Easy", True, BLACK)
    normal_text = font_medium.render("Normal", True, BLACK)
    hard_text = font_medium.render("Hard", True, BLACK)
    menu_text = font_medium.render("Menu", True, BLACK)
    screen.blit(easy_text, (easy_button.centerx - easy_text.get_width() // 2, easy_button.centery - easy_text.get_height() // 2))
    screen.blit(normal_text, (normal_button.centerx - normal_text.get_width() // 2, normal_button.centery - normal_text.get_height() // 2))
    screen.blit(hard_text, (hard_button.centerx - hard_text.get_width() // 2, hard_button.centery - hard_text.get_height() // 2))
    screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))
    return easy_button, normal_button, hard_button, menu_button

def draw_settings_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Settings", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    text_settings_button = pygame.Rect(WIDTH // 2 - 100, 150, 200, 50)
    fullscreen_button = pygame.Rect(WIDTH // 2 - 100, 220, 200, 50)
    reset_data_button = pygame.Rect(WIDTH // 2 - 100, 290, 200, 50)
    back_button = pygame.Rect(WIDTH // 2 - 100, 360, 200, 50)
    
    pygame.draw.rect(screen, PURPLE, text_settings_button)
    pygame.draw.rect(screen, BLUE if not fullscreen_enabled else GREEN, fullscreen_button)
    pygame.draw.rect(screen, RED, reset_data_button)
    pygame.draw.rect(screen, GRAY, back_button)
    
    text_settings_text = font_menu.render("Text Settings", True, BLACK)
    fullscreen_text = font_menu.render(f"Fullscreen: {'ON' if fullscreen_enabled else 'OFF'}", True, BLACK)
    reset_data_text = font_menu.render("Reset Game Data", True, BLACK)
    back_text = font_menu.render("Back", True, BLACK)
    
    screen.blit(text_settings_text, (text_settings_button.centerx - text_settings_text.get_width() // 2, text_settings_button.centery - text_settings_text.get_height() // 2))
    screen.blit(fullscreen_text, (fullscreen_button.centerx - fullscreen_text.get_width() // 2, fullscreen_button.centery - fullscreen_text.get_height() // 2))
    screen.blit(reset_data_text, (reset_data_button.centerx - reset_data_text.get_width() // 2, reset_data_button.centery - reset_data_text.get_height() // 2))
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))
    
    return text_settings_button, fullscreen_button, reset_data_button, back_button

def draw_text_settings_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    title_text = font_large.render("Text Settings", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
    
    # Menu text size slider
    menu_label = font_medium.render(f"Menu Text Size: {menu_text_size}px", True, WHITE)
    screen.blit(menu_label, (50, 100))
    menu_slider_rect = pygame.Rect(50, 130, 300, 20)
    pygame.draw.rect(screen, GRAY, menu_slider_rect)
    menu_slider_pos = int(((menu_text_size - MIN_TEXT_SIZE) / (MAX_TEXT_SIZE - MIN_TEXT_SIZE)) * 300)
    menu_slider_handle = pygame.Rect(50 + menu_slider_pos - 5, 125, 10, 30)
    pygame.draw.rect(screen, WHITE, menu_slider_handle)
    
    # In-game text size slider
    ingame_label = font_medium.render(f"In-Game Text Size: {ingame_text_size}px", True, WHITE)
    screen.blit(ingame_label, (50, 180))
    ingame_slider_rect = pygame.Rect(50, 210, 300, 20)
    pygame.draw.rect(screen, GRAY, ingame_slider_rect)
    ingame_slider_pos = int(((ingame_text_size - MIN_TEXT_SIZE) / (MAX_TEXT_SIZE - MIN_TEXT_SIZE)) * 300)
    ingame_slider_handle = pygame.Rect(50 + ingame_slider_pos - 5, 205, 10, 30)
    pygame.draw.rect(screen, WHITE, ingame_slider_handle)
    
    # Dialogue text size slider
    dialogue_label = font_medium.render(f"Dialogue Text Size: {dialogue_text_size}px", True, WHITE)
    screen.blit(dialogue_label, (50, 260))
    dialogue_slider_rect = pygame.Rect(50, 290, 300, 20)
    pygame.draw.rect(screen, GRAY, dialogue_slider_rect)
    dialogue_slider_pos = int(((dialogue_text_size - MIN_TEXT_SIZE) / (MAX_TEXT_SIZE - MIN_TEXT_SIZE)) * 300)
    dialogue_slider_handle = pygame.Rect(50 + dialogue_slider_pos - 5, 285, 10, 30)
    pygame.draw.rect(screen, WHITE, dialogue_slider_handle)
    
    # Preview text
    preview_label = font_medium.render("Preview:", True, WHITE)
    screen.blit(preview_label, (450, 100))
    
    menu_preview = font_menu.render("Menu Text Sample", True, WHITE)
    screen.blit(menu_preview, (450, 130))
    
    ingame_preview = font_ingame.render("In-Game Text Sample", True, WHITE)
    screen.blit(ingame_preview, (450, 170))
    
    dialogue_preview = font_dialogue.render("Dialogue Text Sample", True, WHITE)
    screen.blit(dialogue_preview, (450, 210))
    
    back_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)
    pygame.draw.rect(screen, GRAY, back_button)
    back_text = font_medium.render("Back", True, BLACK)
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))
    
    return menu_slider_rect, menu_slider_handle, ingame_slider_rect, ingame_slider_handle, dialogue_slider_rect, dialogue_slider_handle, back_button

def toggle_fullscreen():
    global fullscreen_enabled, screen
    fullscreen_enabled = not fullscreen_enabled
    if fullscreen_enabled:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

def reset_game_data():
    global coins, score, shop_items, permanent_upgrades, max_health, player_health, base_defense_level, defense_level, passive_healing_rate, suitable_radiation_purchased, popup_closer_delay, sam_can_be_activated, invincible_duration, jetpack_strength
    # Reset all game data to initial values
    coins = 0
    score = 0
    max_health = 100
    player_health = 100
    base_defense_level = 0
    defense_level = 0
    passive_healing_rate = 0
    suitable_radiation_purchased = False
    popup_closer_delay = 0
    sam_can_be_activated = False
    invincible_duration = 5
    jetpack_strength = base_jetpack_strength
    
    # Reset shop items
    for item in shop_items.values():
        item["upgrades"] = 0
    
    # Reset permanent upgrades
    permanent_upgrades = {
        "suitable_radiation_purchased": False
    }
    
    # Save the reset data
    save_game()
    print("Game data has been reset!")

def buy_item(item_name, price):
    global coins, max_health, player_health, invincible_duration, jetpack_strength, sam_can_be_activated, passive_healing_rate, suitable_radiation_purchased, radiation_reduction_start_time, popup_closer_delay, base_defense_level, defense_level
    item = shop_items[item_name]
    if item_name == "suitable_radiation" and permanent_upgrades.get("suitable_radiation_purchased", False):
        print("Suitable Radiation already permanently purchased!")
        return
    if coins >= price:
        coins -= price
        item["upgrades"] += 1
        if item_name == "health_upgrade":
            max_health += 50
            player_health = max_health
        elif item_name == "invincibility_powerup_shop":
            invincible_duration = 5 + (3 * item["upgrades"])
        elif item_name == "jetpack_upgrade":
            jetpack_strength -= 0.3
        elif item_name == "sam_machine":
            sam_can_be_activated = True
        elif item_name == "healing_potion":
            player_health = min(max_health, player_health + item["heal_amount"])
        elif item_name == "passive_regeneration":
            passive_healing_rate = item["upgrades"] * item["regen_per_upgrade"]
        elif item_name == "suitable_radiation":
            suitable_radiation_purchased = True
            permanent_upgrades["suitable_radiation_purchased"] = True
            if radiation_level > 0:
                radiation_reduction_start_time = pygame.time.get_ticks()
            print("Suitable Radiation permanently purchased!")
        elif item_name == "popup_closer":
            popup_closer_delay = item["base_delay"] - (item["upgrades"] * item["delay_reduction_per_upgrade"])
            print(f"Pop-Up Closer purchased! New delay: {popup_closer_delay}s")
        elif item_name == "defense_upgrade":
            base_defense_level = item["upgrades"] * item["defense_per_upgrade"]
            defense_level = base_defense_level * (1 - radiation_level / max_radiation)
            print(f"Defense Upgrade purchased! Base defense: {base_defense_level * 100:.0f}%")
    else:
        print("Not enough coins!")

# Game loop
running = True

while running:
    current_time = pygame.time.get_ticks()
    current_time_sec = time.time()

    # Update defense level based on radiation
    defense_level = base_defense_level * (1 - radiation_level / max_radiation)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_paused and not game_over and not show_main_menu and not in_guide and not in_difficulty_menu:
                space_pressed = True
                if sam_escape_triggered:
                    sam_escape_progress += 2
                    if sam_escape_progress >= 100:
                        sam_escape_triggered = False
                        sam_active = False
                        sam_escape_progress = 0
                        sam_rocket_hits = 0
            if event.key == pygame.K_ESCAPE:
                if in_text_settings_menu:
                    in_text_settings_menu = False
                elif in_settings_menu:
                    in_settings_menu = False
                    show_main_menu = True
                elif in_shop:
                    in_shop = False
                elif in_guide:
                    in_guide = False
                    show_main_menu = True
                elif in_difficulty_menu:
                    in_difficulty_menu = False
                    show_main_menu = True
                elif game_paused:
                    game_paused = False
                elif game_over:
                    pass
                elif show_main_menu:
                    running = False
                else:
                    game_paused = not game_paused
            if event.key == pygame.K_t and sam_can_be_activated and not sam_active and not game_paused and not game_over and not show_main_menu and not in_guide and not in_difficulty_menu:
                sam_active = True
                sam_activated_time = time.time()
                sam_rocket_hits = 0
                obstacles.clear()
                sam_can_be_activated = False
            if in_guide:
                if event.key == pygame.K_LEFT:
                    guide_horizontal_scroll_offset -= 20
                elif event.key == pygame.K_RIGHT:
                    guide_horizontal_scroll_offset += 20
                elif event.key == pygame.K_UP:
                    guide_scroll_offset -= 20
                elif event.key == pygame.K_DOWN:
                    guide_scroll_offset += 20
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1:
                if show_main_menu:
                    all_upgrades_purchased = check_all_upgrades_purchased()
                    settings_button, start_game_button, difficulty_button, guide_button, save_button, load_button, completed_or_exit_button = draw_main_menu()
                    if settings_button.collidepoint(mouse_pos):
                        show_main_menu = False
                        in_settings_menu = True
                    elif start_game_button.collidepoint(mouse_pos):
                        show_main_menu = False
                        reset_game()
                    elif difficulty_button.collidepoint(mouse_pos):
                        show_main_menu = False
                        in_difficulty_menu = True
                    elif guide_button.collidepoint(mouse_pos):
                        show_main_menu = False
                        in_guide = True
                        guide_scroll_offset = 0
                        guide_horizontal_scroll_offset = 0
                    elif save_button.collidepoint(mouse_pos):
                        save_game()
                    elif load_button.collidepoint(mouse_pos):
                        load_game()
                        reset_game()
                    elif completed_or_exit_button.collidepoint(mouse_pos):
                        if all_upgrades_purchased:
                            # Handle COMPLETED button click
                            print("COMPLETED button clicked!")
                            # Add your completed phase logic here
                        else:
                            running = False
                elif in_difficulty_menu:
                    easy_button, normal_button, hard_button, menu_button = draw_difficulty_menu()
                    if easy_button.collidepoint(mouse_pos):
                        difficulty = "Easy"
                        apply_difficulty_settings()
                        print(f"Difficulty set to: {difficulty}")
                    elif normal_button.collidepoint(mouse_pos):
                        difficulty = "Normal"
                        apply_difficulty_settings()
                        print(f"Difficulty set to: {difficulty}")
                    elif hard_button.collidepoint(mouse_pos):
                        difficulty = "Hard"
                        apply_difficulty_settings()
                        print(f"Difficulty set to: {difficulty}")
                    elif menu_button.collidepoint(mouse_pos):
                        in_difficulty_menu = False
                        show_main_menu = True
                elif in_settings_menu:
                    if in_text_settings_menu:
                        # Handle text settings menu
                        menu_slider_rect, menu_slider_handle, ingame_slider_rect, ingame_slider_handle, dialogue_slider_rect, dialogue_slider_handle, back_button = draw_text_settings_menu()
                        
                        # Check for slider drag
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if menu_slider_rect.collidepoint(mouse_pos):
                                # Update menu text size
                                mouse_x = mouse_pos[0] - menu_slider_rect.left
                                menu_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / menu_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                            elif ingame_slider_rect.collidepoint(mouse_pos):
                                # Update in-game text size
                                mouse_x = mouse_pos[0] - ingame_slider_rect.left
                                ingame_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / ingame_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                            elif dialogue_slider_rect.collidepoint(mouse_pos):
                                # Update dialogue text size
                                mouse_x = mouse_pos[0] - dialogue_slider_rect.left
                                dialogue_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / dialogue_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                            elif back_button.collidepoint(mouse_pos):
                                in_text_settings_menu = False
                        
                        # Handle slider dragging
                        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:  # Left mouse button is held
                            if menu_slider_rect.collidepoint(mouse_pos):
                                mouse_x = mouse_pos[0] - menu_slider_rect.left
                                menu_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / menu_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                            elif ingame_slider_rect.collidepoint(mouse_pos):
                                mouse_x = mouse_pos[0] - ingame_slider_rect.left
                                ingame_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / ingame_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                            elif dialogue_slider_rect.collidepoint(mouse_pos):
                                mouse_x = mouse_pos[0] - dialogue_slider_rect.left
                                dialogue_text_size = max(MIN_TEXT_SIZE, min(MAX_TEXT_SIZE, int(MIN_TEXT_SIZE + (mouse_x / dialogue_slider_rect.width) * (MAX_TEXT_SIZE - MIN_TEXT_SIZE))))
                                update_fonts()
                    else:
                        # Handle main settings menu
                        text_settings_button, fullscreen_button, reset_data_button, back_button = draw_settings_menu()
                        
                        if text_settings_button.collidepoint(mouse_pos):
                            in_text_settings_menu = True
                        elif fullscreen_button.collidepoint(mouse_pos):
                            toggle_fullscreen()
                        elif reset_data_button.collidepoint(mouse_pos):
                            reset_game_data()
                        elif back_button.collidepoint(mouse_pos):
                            in_settings_menu = False
                            show_main_menu = True
                elif in_guide:
                    menu_button = draw_guide()
                    if menu_button.collidepoint(mouse_pos):
                        in_guide = False
                        show_main_menu = True
                elif sam_active and not sam_escape_triggered and current_time - last_bullet_time > bullet_interval:
                    bullets.append(pygame.Rect(player_x + player_size, player_y + player_size // 2 - 2, 10, 5))
                    last_bullet_time = current_time
                elif game_paused and not in_shop:
                    resume_button, shop_button, save_button, load_button, main_menu_button, exit_button = draw_pause_menu()
                    if resume_button.collidepoint(mouse_pos):
                        game_paused = False
                    elif shop_button.collidepoint(mouse_pos):
                        in_shop = True
                    elif save_button.collidepoint(mouse_pos):
                        save_game()
                    elif load_button.collidepoint(mouse_pos):
                        load_game()
                        reset_game()
                    elif main_menu_button.collidepoint(mouse_pos):
                        show_main_menu = True
                        game_paused = False
                        reset_game()
                    elif exit_button.collidepoint(mouse_pos):
                        running = False
                elif in_shop:
                    item_buttons, back_button = draw_shop()
                    if back_button.collidepoint(mouse_pos):
                        in_shop = False
                    else:
                        for item_name, button, price in item_buttons:
                            if button.collidepoint(mouse_pos):
                                buy_item(item_name, price)
                elif game_over:
                    restart_button, shop_button, main_menu_button, exit_button = draw_game_over()
                    if restart_button.collidepoint(mouse_pos):
                        reset_game()
                        game_over = False
                    elif shop_button.collidepoint(mouse_pos):
                        in_shop = True
                    elif main_menu_button.collidepoint(mouse_pos):
                        show_main_menu = True
                        game_over = False
                        reset_game()
                    elif exit_button.collidepoint(mouse_pos):
                        running = False
                
                # Handle idiot popup close button
                for popup in idiot_popups[:]:
                    x_button_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
                    if x_button_rect.collidepoint(mouse_pos):
                        # Award coins when closing idiot popup
                        coins += popup.get("coins_awarded", 25)
                        idiot_popups.remove(popup)
                
                # Handle scammer popup button clicks
                for popup in scammer_popups[:]:
                    # Check if close button (X) was clicked
                    close_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
                    if close_rect.collidepoint(mouse_pos):
                        # Award coins when closing scammer popup
                        coins += popup.get("coins_awarded", 25)
                        scammer_popups.remove(popup)
                        break
                    # Check if main button was clicked
                    elif popup["button_rect"].collidepoint(mouse_pos):
                        # Player clicked the button - take 70% of their coins
                        coins_lost = int(coins * 0.7)
                        coins = max(0, coins - coins_lost)  # Ensure coins don't go negative
                        scammer_popups.remove(popup)
                        break
                
                # Handle virus popup button clicks
                for popup in virus_popups[:]:
                    # Check if close button (X) was clicked
                    close_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
                    if close_rect.collidepoint(mouse_pos):
                        # Award coins when closing virus popup
                        coins += popup.get("coins_awarded", 25)
                        virus_popups.remove(popup)
                        break
                    # Check if main button was clicked
                    elif popup["button_rect"].collidepoint(mouse_pos):
                        # Player clicked the button - remove a random upgrade
                        upgrade_keys = [key for key in shop_items.keys() 
                                     if shop_items[key]["upgrades"] > 0 
                                     and key not in ["suitable_radiation", "popup_closer", "anti_scam"]]
                        if upgrade_keys:
                            upgrade_to_remove = random.choice(upgrade_keys)
                            shop_items[upgrade_to_remove]["upgrades"] = 0
                            # Reapply upgrades to update game state
                            apply_permanent_upgrades()
                            # Show feedback about removed upgrade
                            feedback_text = f"Virus removed {upgrade_to_remove.replace('_', ' ').title()}!"
                            feedback_surface = font_small.render(feedback_text, True, RED)
                            screen.blit(feedback_surface, (WIDTH // 2 - feedback_surface.get_width() // 2, HEIGHT - 50))
                            pygame.display.flip()
                            pygame.time.delay(1500)  # Show feedback for 1.5 seconds
                        virus_popups.remove(popup)
                        break
                
                if event.button == 4 or event.button == 5:  # Mouse wheel up or down
                    max_total_height = len(guide_content.split('\n')) * font_small.get_height()
                    display_height = HEIGHT - 100 - 80
                    max_scroll_offset = max(0, max_total_height - display_height)
                    scroll_amount = 20
                    if event.button == 4:
                        guide_scroll_offset -= scroll_amount
                    elif event.button == 5:
                        guide_scroll_offset += scroll_amount
                    guide_scroll_offset = max(0, min(guide_scroll_offset, max_scroll_offset))
        if in_guide and event.type == pygame.MOUSEWHEEL:
            scroll_amount = 20
            if event.x != 0:
                max_line_width = max([font_small.size(line)[0] for line in guide_content.split('\n')])
                total_guide_width = max_line_width
                guide_display_width = WIDTH - 200
                max_horizontal_scroll_offset = max(0, total_guide_width - guide_display_width)
                guide_horizontal_scroll_offset -= event.x * scroll_amount
                guide_horizontal_scroll_offset = max(0, min(guide_horizontal_scroll_offset, max_horizontal_scroll_offset))
            if event.y != 0:
                max_total_height = len(guide_content.split('\n')) * font_small.get_height()
                display_height = HEIGHT - 100 - 80
                max_scroll_offset = max(0, max_total_height - display_height)
                guide_scroll_offset -= event.y * scroll_amount
                guide_scroll_offset = max(0, min(guide_scroll_offset, max_scroll_offset))
        elif in_shop and (event.type == pygame.MOUSEWHEEL and event.y != 0):
            scroll_amount = 20
            max_total_height = len(shop_items) * 100
            display_height = HEIGHT - 150 - 80
            max_scroll_offset = max(0, max_total_height - display_height)
            shop_scroll_offset -= event.y * scroll_amount
            shop_scroll_offset = max(0, min(shop_scroll_offset, max_scroll_offset))

    if game_over or game_paused or in_shop or show_main_menu or in_guide or in_difficulty_menu or in_settings_menu or in_text_settings_menu:
        screen.fill(BLACK)
        if show_main_menu:
            draw_main_menu()
        elif in_difficulty_menu:
            draw_difficulty_menu()
        elif in_guide:
            draw_guide()
        elif game_paused and not in_shop:
            draw_pause_menu()
        elif in_shop:
            draw_shop()
        elif in_settings_menu:
            if in_text_settings_menu:
                draw_text_settings_menu()
            else:
                draw_settings_menu()
        elif game_over:
            draw_game_over()
        for popup in idiot_popups:
            pygame.draw.rect(screen, GRAY, popup["rect"])
            pygame.draw.rect(screen, WHITE, popup["rect"], 2)
            idiot_text = font_medium.render("IDIOT!", True, RED)
            screen.blit(idiot_text, (popup["rect"].centerx - idiot_text.get_width() // 2, popup["rect"].centery - idiot_text.get_height() // 2))
            x_button_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
            pygame.draw.rect(screen, RED, x_button_rect)
            x_text = font_small.render("X", True, WHITE)
            screen.blit(x_text, (x_button_rect.centerx - x_text.get_width() // 2, x_button_rect.centery - x_text.get_height() // 2))
            time_remaining_for_duplication = max(0, IDIOT_POPUP_CLICK_TIME_LIMIT - (current_time - popup["spawn_time_ms"]) / 1000)
            timer_text = font_small.render(f"{time_remaining_for_duplication:.1f}s", True, WHITE)
            screen.blit(timer_text, (popup["rect"].left + 5, popup["rect"].bottom - 25))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    if current_time - last_obstacle_time > obstacle_interval and not sam_active:
        spawn_obstacle()
        last_obstacle_time = current_time
    if current_time - last_coin_time > coin_interval:
        spawn_coin()
        last_coin_time = current_time
    rocket_spawn_interval = rocket_interval
    if sam_active:
        rocket_spawn_interval = 1000
    if current_time - last_rocket_time > rocket_spawn_interval:
        spawn_rocket()
        last_rocket_time = current_time
    if current_time - last_powerup_time > powerup_interval:
        rand = random.random()
        if rand < 0.3:
            spawn_radiation_powerdown()
        elif rand < 0.6 and shop_items["healing_powerup"]["upgrades"] > 0:
            spawn_healing_powerup()
        last_powerup_time = current_time
    if shop_items["invincibility_powerup_shop"]["upgrades"] > 0 and current_time - last_powerup_time > powerup_interval and random.random() < 0.15:
        spawn_invincibility_powerup_in_game()
    if shop_items["sam_machine"]["upgrades"] > 0 and current_time - last_sam_powerup_time > sam_powerup_interval and not sam_can_be_activated and not sam_active:
        spawn_sam_powerup()
        last_sam_powerup_time = current_time
    if current_time - last_idiot_popup_time > idiot_popup_interval:
        spawn_idiot_popup()
        last_idiot_popup_time = current_time
        
    # Spawn scammer popup occasionally (every 15-25 seconds)
    if current_time - globals().get('last_scammer_popup_time', 0) > 15000 + random.randint(0, 10000):
        spawn_scammer_popup()
        globals()['last_scammer_popup_time'] = current_time
    
    # Spawn virus popup occasionally (every 20-30 seconds)
    if current_time - globals().get('last_virus_popup_time', 0) > 20000 + random.randint(0, 10000):
        spawn_virus_popup()
        globals()['last_virus_popup_time'] = current_time

    player_velocity += gravity
    if space_pressed and not sam_escape_triggered:
        player_velocity += jetpack_strength
    player_y += player_velocity
    if player_y < 0:
        player_y = 0
        player_velocity = 0
    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size
        player_velocity = 0
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    for powerup_obj in powerups[:]:
        powerup_obj["rect"].x -= game_speed
        if powerup_obj["rect"].right < 0:
            powerups.remove(powerup_obj)
            continue
        if player_rect.colliderect(powerup_obj["rect"]):
            if powerup_obj["type"] == "invincibility_in_game":
                invincible = True
                invincible_time = time.time()
            elif powerup_obj["type"] == "sam_powerup":
                if shop_items["sam_machine"]["upgrades"] > 0:
                    sam_can_be_activated = True
            elif powerup_obj["type"] == "radiation_powerdown":
                radiation_level = min(max_radiation, radiation_level + (max_radiation * 0.70))
                defense_level = base_defense_level * (1 - radiation_level / max_radiation)
                if suitable_radiation_purchased and radiation_reduction_start_time == 0:
                    radiation_reduction_start_time = current_time
            elif powerup_obj["type"] == "healing_powerup":
                player_health = min(max_health, player_health + powerup_obj["heal_amount"])
                heal_text = font_small.render(f"+{int(powerup_obj['heal_amount'])} HP", True, GREEN)
                screen.blit(heal_text, (player_x, player_y - 20))
            powerups.remove(powerup_obj)

    for obstacle in obstacles[:]:
        obstacle.x -= game_speed
        if obstacle.right < 0:
            obstacles.remove(obstacle)
            continue
        if not invincible and player_rect.colliderect(obstacle):
            damage = 30 * (1 - defense_level)
            player_health -= damage
            obstacles.remove(obstacle)
            if player_health <= 0:
                game_over = True

    for coin in coins_list:
        coin.x -= game_speed
        if coin.right < 0:
            coins_list.remove(coin)
            continue
        if player_rect.colliderect(coin):
            coins += 1
            coins_list.remove(coin)
            score += 5

    for rocket in rockets[:]:
        rocket.x -= game_speed + 2
        if rocket.y < player_y:
            rocket.y += 2
        elif rocket.y > player_y:
            rocket.y -= 2
        if rocket.right < 0:
            rockets.remove(rocket)
            continue
        if player_rect.colliderect(rocket):
            if not invincible and not sam_active:
                damage = 50 * (1 - defense_level)
                player_health -= damage
                radiation_level = min(max_radiation, radiation_level + (max_radiation * 0.10))
                defense_level = base_defense_level * (1 - radiation_level / max_radiation)
                if suitable_radiation_purchased and radiation_reduction_start_time == 0:
                    radiation_reduction_start_time = current_time
                rockets.remove(rocket)
                if player_health <= 0:
                    game_over = True
            elif sam_active:
                sam_rocket_hits += 1
                rockets.remove(rocket)
                if sam_rocket_hits >= 5 and not sam_escape_triggered:
                    sam_escape_triggered = True
                    sam_escape_start_time = time.time()

    for bullet in bullets:
        bullet.x += 10
        if bullet.left > WIDTH:
            bullets.remove(bullet)
            continue
        for rocket in rockets[:]:
            if bullet.colliderect(rocket):
                rockets.remove(rocket)
                bullets.remove(bullet)
                break

    if invincible and time.time() - invincible_time > invincible_duration:
        invincible = False

    if passive_healing_rate > 0:
        player_health = min(max_health, player_health + (passive_healing_rate / FPS))

    if sam_active:
        if current_time - last_sam_heal_time >= SAM_HEAL_INTERVAL_MS:
            player_health = min(max_health, player_health + SAM_HEAL_AMOUNT_PER_MS)
            last_sam_heal_time = current_time

    if sam_escape_triggered:
        if not space_pressed and current_time - last_sam_escape_decrease_time >= SAM_ESCAPE_DECREASE_INTERVAL:
            sam_escape_progress = max(0, sam_escape_progress - sam_escape_decrease_rate)
            last_sam_escape_decrease_time = current_time
        if time.time() - sam_escape_start_time > sam_escape_time_limit:
            sam_active = False
            sam_escape_triggered = False
            sam_escape_progress = 0
            sam_rocket_hits = 0
            damage = (max_health * 0.99) * (1 - defense_level)
            player_health -= damage
            if player_health <= 0:
                game_over = True

    if radiation_level > 50:
        damage = (0.1 / FPS) * (1 - defense_level)
        player_health -= damage
        player_health = max(0, player_health)
        if player_health <= 0:
            game_over = True

    if suitable_radiation_purchased and radiation_level > 0:
        if radiation_reduction_start_time == 0:
            radiation_reduction_start_time = current_time
        if current_time - radiation_reduction_start_time >= RADIATION_REDUCTION_DELAY:
            if current_time - last_radiation_reduction_time >= RADIATION_REDUCTION_INTERVAL:
                radiation_level = max(0, radiation_level - RADIATION_AMOUNT_PER_REDUCTION)
                defense_level = base_defense_level * (1 - radiation_level / max_radiation)
                last_radiation_reduction_time = current_time
                if radiation_level == 0:
                    radiation_reduction_start_time = 0
                    last_radiation_reduction_time = 0

    # Handle idiot popups - No more damage, just bounce around
    for popup in idiot_popups[:]:
        popup["rect"].x += popup["dx"]
        popup["rect"].y += popup["dy"]
        if popup["rect"].left < 0 or popup["rect"].right > WIDTH:
            popup["dx"] *= -1
            popup["rect"].x = max(0, min(popup["rect"].x, WIDTH - popup["rect"].width))
        if popup["rect"].top < 0 or popup["rect"].bottom > HEIGHT:
            popup["dy"] *= -1
            popup["rect"].y = max(0, min(popup["rect"].y, HEIGHT - popup["rect"].height))

    current_time = pygame.time.get_ticks()
    for popup in scammer_popups[:]:
        # Auto-close popup after timeout (scales with Anti-Scam upgrades)
        if current_time - popup.get("spawn_time", current_time) > popup.get("auto_close_time", 10000):
            # Award coins when popup auto-closes
            coins += popup.get("coins_awarded", 25)
            scammer_popups.remove(popup)

    current_time = pygame.time.get_ticks()
    for popup in virus_popups[:]:
        # Auto-close popup after timeout (scales with Anti-Scam upgrades)
        if current_time - popup.get("spawn_time", current_time) > popup.get("auto_close_time", 8000):
            # Award coins when popup auto-closes
            coins += popup.get("coins_awarded", 10)
            virus_popups.remove(popup)

    game_speed = base_speed + score // 500
    score += 1

    screen.fill(BLACK)
    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, obstacle)
    for coin in coins_list:
        pygame.draw.rect(screen, YELLOW, coin)
    for rocket in rockets:
        pygame.draw.rect(screen, (255, 100, 0), rocket)
    for powerup_obj in powerups:
        if powerup_obj["type"] == "invincibility_in_game":
            pygame.draw.rect(screen, PURPLE, powerup_obj["rect"])
        elif powerup_obj["type"] == "sam_powerup":
            pygame.draw.rect(screen, BLUE, powerup_obj["rect"])
        elif powerup_obj["type"] == "radiation_powerdown":
            pygame.draw.rect(screen, RED, powerup_obj["rect"])
        elif powerup_obj["type"] == "healing_powerup":
            pygame.draw.rect(screen, GREEN, powerup_obj["rect"])
            # Draw a plus sign
            plus_rect = powerup_obj["rect"].inflate(-10, -10)
            pygame.draw.rect(screen, WHITE, (plus_rect.centerx - 3, plus_rect.top, 6, plus_rect.height))
            pygame.draw.rect(screen, WHITE, (plus_rect.left, plus_rect.centery - 3, plus_rect.width, 6))
    for bullet in bullets:
        pygame.draw.rect(screen, GRAY, bullet)
    # Draw idiot popups
    for popup in idiot_popups:
        pygame.draw.rect(screen, GRAY, popup["rect"])
        pygame.draw.rect(screen, WHITE, popup["rect"], 2)
        idiot_text = font_medium.render("IDIOT!", True, RED)
        screen.blit(idiot_text, (popup["rect"].centerx - idiot_text.get_width() // 2, popup["rect"].centery - idiot_text.get_height() // 2))
        # Draw close button (X) in top-right corner
        x_button_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
        pygame.draw.rect(screen, RED, x_button_rect)
        x_text = font_small.render("X", True, WHITE)
        screen.blit(x_text, (x_button_rect.centerx - x_text.get_width() // 2, x_button_rect.centery - x_text.get_height() // 2))
    
    # Draw scammer popups
    for popup in scammer_popups:
        # Draw popup background and border
        pygame.draw.rect(screen, (240, 230, 140), popup["rect"])  # Light yellow background
        pygame.draw.rect(screen, (200, 200, 0), popup["rect"], 3)  # Gold border
        
        # Draw close button (X) in top-right corner
        x_button_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
        pygame.draw.rect(screen, (200, 0, 0), x_button_rect)  # Red button
        x_text = font_small.render("X", True, WHITE)
        screen.blit(x_text, (x_button_rect.centerx - x_text.get_width() // 2, x_button_rect.centery - x_text.get_height() // 2))
        
        # Draw message (split into multiple lines if needed)
        words = popup["message"].split(' ')
        lines = []
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + ' ' + word
            if font_small.size(test_line)[0] < popup["rect"].width - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Render each line of text
        y_offset = 10
        for line in lines:
            text_surface = font_small.render(line, True, BLACK)
            screen.blit(text_surface, (popup["rect"].x + 10, popup["rect"].y + y_offset))
            y_offset += text_surface.get_height() + 2
        
        # Draw button
        pygame.draw.rect(screen, (0, 200, 0), popup["button_rect"])  # Green button
        pygame.draw.rect(screen, (0, 100, 0), popup["button_rect"], 2)  # Darker green border
        button_text = font_small.render(popup["button_text"], True, WHITE)
        screen.blit(button_text, (popup["button_rect"].centerx - button_text.get_width() // 2, 
                                 popup["button_rect"].centery - button_text.get_height() // 2))
    
    # Draw virus popups
    for popup in virus_popups:
        # Draw popup background and border
        pygame.draw.rect(screen, (255, 200, 200), popup["rect"])  # Light red background
        pygame.draw.rect(screen, (200, 0, 0), popup["rect"], 3)  # Red border
        
        # Draw close button (X) in top-right corner
        x_button_rect = pygame.Rect(popup["rect"].right - 25, popup["rect"].top + 5, 20, 20)
        pygame.draw.rect(screen, (100, 0, 0), x_button_rect)  # Dark red button
        x_text = font_small.render("X", True, WHITE)
        screen.blit(x_text, (x_button_rect.centerx - x_text.get_width() // 2, x_button_rect.centery - x_text.get_height() // 2))
        
        # Draw warning symbol
        warning_rect = pygame.Rect(popup["rect"].x + 10, popup["rect"].y + 10, 40, 40)
        pygame.draw.polygon(screen, (200, 0, 0), [
            (warning_rect.centerx, warning_rect.top),
            (warning_rect.right, warning_rect.bottom),
            (warning_rect.left, warning_rect.bottom)
        ])
        warning_text = font_small.render("!", True, WHITE)
        screen.blit(warning_text, (warning_rect.centerx - warning_text.get_width() // 2, 
                                 warning_rect.centery - warning_text.get_height() // 2 + 5))
        
        # Draw message (split into multiple lines if needed)
        words = popup["message"].split(' ')
        lines = []
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + ' ' + word
            if font_small.size(test_line)[0] < popup["rect"].width - 60:  # Leave space for warning symbol
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Render each line of text
        y_offset = 10
        for line in lines:
            text_surface = font_small.render(line, True, BLACK)
            screen.blit(text_surface, (popup["rect"].x + 60, popup["rect"].y + y_offset))  # Start after warning symbol
            y_offset += text_surface.get_height() + 2
        
        # Draw button
        pygame.draw.rect(screen, (200, 0, 0), popup["button_rect"])  # Red button
        pygame.draw.rect(screen, (100, 0, 0), popup["button_rect"], 2)  # Darker red border
        button_text = font_small.render(popup["button_text"], True, WHITE)
        screen.blit(button_text, (popup["button_rect"].centerx - button_text.get_width() // 2, 
                                 popup["button_rect"].centery - button_text.get_height() // 2))
    draw_player()
    draw_hud()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
