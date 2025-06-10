# FortBrawl 2D with Admin System and Admin Panel
import pygame
import random
import sys
import json
import os

# Admin credentials
user = {
    "AdminUser": "q2025q!",
    "ModUser": "tutlix"
}

# Load settings
with open("settings/config.json", "r") as f:
    config = json.load(f)

nickname = config["nickname"]
current_color = config["color"]
volume = config["volume"]
control_keys = config["controls"]

# Ask for admin password at start
password = input(f"Welcome {nickname}! Enter password (or leave blank): ")
is_admin = user.get(nickname) == password

# Key map
key_map = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "space": pygame.K_SPACE,
    "a": pygame.K_a,
    "d": pygame.K_d,
    "w": pygame.K_w
}
controls = {action: key_map[key] for action, key in control_keys.items()}

# Load progress
score = config.get("progress", {}).get("score", 0)
level = config.get("progress", {}).get("level", 1)

# Initialize Pygame
pygame.init()

# Load sounds
shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")
click_sound = pygame.mixer.Sound("sounds/menu_click.wav")
pygame.mixer.music.load("sounds/background.mp3")
pygame.mixer.music.set_volume(volume)

# Set icon and screen
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FortBrawl 2D")

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Game states
MENU, PLAYING, GAME_OVER, ADMIN_PANEL = "menu", "playing", "game_over", "admin_panel"
game_state = MENU

# Colors and players
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
color_map = {
    "blue": (0, 0, 255), "green": (0, 255, 0), "red": (255, 0, 0),
    "yellow": (255, 255, 0), "purple": (128, 0, 128), "orange": (255, 165, 0)
}

players, bullets, bots = [], [], []
player_speed, bullet_speed, bot_speed, bot_spawn_rate = 5, 10, 2 + (level - 1), max(20, 49 - (level - 1) * 2)
update_timer = 0
last_shot_time, shoot_cooldown = 0, 120

# Draw helpers
def draw_text(text, x, y, size=24, color=BLACK):
    label = pygame.font.SysFont("Arial", size).render(text, True, color)
    screen.blit(label, (x, y))

def draw_button(text, x, y, width, height, color, hover_color):
    mouse = pygame.mouse.get_pos()
    pygame.draw.rect(screen, hover_color if x < mouse[0] < x+width and y < mouse[1] < y+height else color, (x, y, width, height))
    draw_text(text, x+10, y+10)

def draw_main_menu():
    player_preview = pygame.Rect(20, HEIGHT//2 + 140, 50, 50)
    screen.fill((200, 200, 200))
    screen.fill(WHITE)
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)
    draw_text("FortBrawl 2D", WIDTH//2-100, HEIGHT//3, 48)
    draw_button("Singleplayer", WIDTH//2-150, HEIGHT//2, 300, 50, GREEN, (0, 200, 0))
    draw_button("Multiplayer", WIDTH//2-150, HEIGHT//2+60, 300, 50, RED, (0, 200, 0))
    draw_button("Change Color", WIDTH//2-150, HEIGHT//2+120, 300, 50, GREEN, (0, 200, 0))
    draw_button("Change Nickname", WIDTH//2-150, HEIGHT//2+180, 300, 50, GREEN, (0, 200, 0))
    draw_text(f"Selected: {current_color}", 20, HEIGHT//2+100, 20)
    pygame.draw.rect(screen, color_map[current_color], player_preview)
    pygame.draw.rect(screen, (0, 0, 0), player_preview, 2)
    pygame.display.flip()

def draw_game():
    screen.fill(GREEN)
    for player in players:
        pygame.draw.rect(screen, color_map[current_color], player)
    for bullet in bullets:
        pygame.draw.rect(screen, RED, bullet)
    for bot in bots:
        pygame.draw.rect(screen, BLACK, bot)
    draw_text(f"Score: {score}  Nickname: {nickname}  Level: {level}", 10, 10)
    draw_text(f"Time: {int(update_timer)} seconds", 10, 40)
    pygame.display.flip()

def draw_game_over():
    screen.fill(WHITE)
    draw_text("Game Over", WIDTH//2 - 80, HEIGHT//2 - 40, 48)
    draw_text("Press R to return to menu", WIDTH//2 - 150, HEIGHT//2 + 20)
    pygame.display.flip()
    pygame.mixer.music.stop()

# Game logic functions
def reset_game(mode):
    global players, bullets, bots, score, level, bot_speed, bot_spawn_rate, game_state, last_shot_time
    players.clear()
    bullets.clear()
    bots.clear()
    score = 0
    level = 1
    bot_speed = 2
    bot_spawn_rate = 49
    game_state = PLAYING
    last_shot_time = pygame.time.get_ticks()
    pygame.mixer.music.stop()
    if mode == "single":
        players.append(pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 50))
    else:
        players.append(pygame.Rect(WIDTH//2 - 60, HEIGHT - 60, 50, 50))
        players.append(pygame.Rect(WIDTH//2 + 10, HEIGHT - 60, 50, 50))

def shoot(player):
    global last_shot_time
    current_time = pygame.time.get_ticks()
    if current_time - last_shot_time >= shoot_cooldown:
        x, y = player.centerx, player.top
        bullets.append(pygame.Rect(x - 2, y - 10, 4, 10))
        shoot_sound.play()
        last_shot_time = current_time

def spawn_bot():
    x = random.randint(0, WIDTH - 40)
    bots.append(pygame.Rect(x, 0, 40, 40))

def handle_events():
    global game_state, nickname, current_color, score, level, bot_speed, bot_spawn_rate
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            config["progress"] = {"score": score, "level": level}
            with open("settings/config.json", "w") as f:
                json.dump(config, f, indent=4)
            pygame.quit()
            sys.exit()
        if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if WIDTH//2 - 150 < mx < WIDTH//2 + 150:
                if HEIGHT//2 < my < HEIGHT//2 + 50:
                    click_sound.play()
                    reset_game("single")
                elif HEIGHT//2 + 60 < my < HEIGHT//2 + 110:
                    click_sound.play()
                    reset_game("multi")
                elif HEIGHT//2 + 120 < my < HEIGHT//2 + 170:
                    click_sound.play()
                    colors = list(color_map.keys())
                    idx = colors.index(current_color)
                    current_color = colors[(idx + 1) % len(colors)]
                    config["color"] = current_color
                    with open("settings/config.json", "w") as f:
                        json.dump(config, f, indent=4)
                elif HEIGHT//2 + 180 < my < HEIGHT//2 + 230:
                    click_sound.play()
                    nickname = input("Enter new nickname: ")
                    config["nickname"] = nickname
                    with open("settings/config.json", "w") as f:
                        json.dump(config, f, indent=4)
        elif game_state == GAME_OVER and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_state = MENU

    if game_state == PLAYING:
        if keys[controls["p1_left"]] and players[0].left > 0:
            players[0].move_ip(-player_speed, 0)
        if keys[controls["p1_right"]] and players[0].right < WIDTH:
            players[0].move_ip(player_speed, 0)
        if keys[controls["p1_shoot"]]:
            shoot(players[0])
        if len(players) == 2:
            if keys[controls["p2_left"]] and players[1].left > 0:
                players[1].move_ip(-player_speed, 0)
            if keys[controls["p2_right"]] and players[1].right < WIDTH:
                players[1].move_ip(player_speed, 0)
            if keys[controls["p2_shoot"]]:
                shoot(players[1])

def update_game():
    global score, level, bot_speed, bot_spawn_rate, game_state, update_timer
    for bullet in bullets[:]:
        bullet.move_ip(0, -bullet_speed)
        if bullet.bottom < 0:
            bullets.remove(bullet)
    for bot in bots[:]:
        bot.move_ip(0, bot_speed)
        for player in players:
            if bot.colliderect(player):
                game_state = GAME_OVER
                game_over_sound.play()
                config["progress"] = {"score": score, "level": level}
                with open("settings/config.json", "w") as f:
                    json.dump(config, f, indent=4)
        for bullet in bullets[:]:
            if bot.colliderect(bullet):
                bullets.remove(bullet)
                bots.remove(bot)
                score += 1
                explosion_sound.play()
                break
        if bot.top > HEIGHT:
            bots.remove(bot)
    if score >= level * 10:
        level += 1
        bot_speed += 1
        bot_spawn_rate = max(20, bot_spawn_rate - 2)
    if random.randint(1, bot_spawn_rate) == 1:
        spawn_bot()
    update_timer += clock.get_time() / 1000

# Main game loop
while True:
    handle_events()
    if game_state == MENU:
        draw_main_menu()
    elif game_state == PLAYING:
        update_game()
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    clock.tick(60)
