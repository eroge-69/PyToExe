import pygame
import random
import sys
import json
import os
import serial
import threading
import time  # For delay in test mode

# === Arduino Serial Setup ===
arduino = serial.Serial('COM3', 9600)  # Change COM port if needed
arduino.flush()

input_states = set()

def read_serial():
    global input_states
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode().strip()
            input_states.add(line)

threading.Thread(target=read_serial, daemon=True).start()

# === Initialize Pygame ===
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1050, 1680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Arcade")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 60)
small_font = pygame.font.SysFont("Arial", 50)

gravity = 0.75
bird_movement = 0
score = 0
pipe_speed = 2
bg_speed = 1
pipe_gap = 200
lives = 3

waiting_for_coin = True
ready_to_start = False
game_active = False
test_mode = False
hit_pause = False
hit_time = 0
show_game_over_screen = False
game_over_time = 0
final_score = 0
final_tickets = 0

settings = {
    "coin_per_game": 2,  # <<< REQUIRE 2 COINS PER CREDIT
    "difficulty": "normal",
    "score_per_pipe": 1,
    "score_per_ticket": 5,
    "chances_per_game": 3,
    "demo_sound": "ON"
}
current_setting = 0
setting_keys = list(settings.keys())

def save_settings():
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings.update(json.load(f))

load_settings()

bg = pygame.image.load("bg.jpg").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
bg_x = 0

player_img = pygame.image.load("AA1.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (int(WIDTH * 0.10), int(HEIGHT * 0.06)))  # scales proportionally
bird_rect = player_img.get_rect(center=(100, HEIGHT // 2))

pipe_img = pygame.image.load("pipe_bottom.png").convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (int(WIDTH * 0.15), int(HEIGHT * 0.90)))
pipe_top_img = pygame.image.load("pipe_top.png").convert_alpha()
pipe_top_img = pygame.transform.scale(pipe_top_img, (int(WIDTH * 0.15), int(HEIGHT * 0.90)))
pipe_list = []

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 4500)

# === Sounds ===
flap_sound = pygame.mixer.Sound("flap.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
point_sound = pygame.mixer.Sound("point.wav")
coin_sound = pygame.mixer.Sound("coin.wav")
start_sound = pygame.mixer.Sound("start.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")
demo_bgm = pygame.mixer.Sound("demo.WAV")

def draw_pipes(pipes):
    for pipe in pipes:
        img = pipe_img if pipe['type'] == 'bottom' else pipe_top_img
        screen.blit(img, pipe['rect'])

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe['rect']):
            hit_sound.play()
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        hit_sound.play()
        return False
    return True

def display_score(score):
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def display_lives(lives):
    text = font.render(f"Chances: {lives}", True, (255, 100, 100))
    screen.blit(text, (WIDTH - text.get_width() - 10, 10))

def display_test_mode():
    screen.fill((30, 30, 30))
    title = font.render("TEST MODE", True, (255, 255, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    for i, key in enumerate(setting_keys):
        value = settings[key]
        color = (255, 255, 0) if i == current_setting else (255, 255, 255)
        text = small_font.render(f"{key.replace('_', ' ').title()}: {value}", True, color)
        screen.blit(text, (40, 120 + i * 40))
    exit_text = small_font.render("Press SAVE to Exit", True, (200, 255, 200))
    screen.blit(exit_text, (40, HEIGHT - 60))

def reset_game():
    global bird_movement, score, pipe_list, bird_rect, lives, hit_pause
    bird_rect.center = (100, HEIGHT // 2)
    pipe_list.clear()
    bird_movement = 0
    score = 0
    lives = settings["chances_per_game"]
    hit_pause = False

def apply_difficulty():
    global gravity, pipe_gap
    if settings["difficulty"] == "easy":
        gravity = 1
        pipe_gap = 500
    elif settings["difficulty"] == "normal":
        gravity = 0.8
        pipe_gap = 300
    else:
        gravity = 0.8
        pipe_gap = 250

coin_count = 0
coins_inserted = 0
apply_difficulty()

# === Game Loop ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWNPIPE and (game_active or waiting_for_coin) and not hit_pause:
            h = random.randint(200, 800)
            b = pipe_img.get_rect(midtop=(WIDTH, h + pipe_gap))
            t = pipe_top_img.get_rect(midbottom=(WIDTH, h))
            pipe_list.append({'rect': b, 'type': 'bottom', 'passed': False})
            pipe_list.append({'rect': t, 'type': 'top'})

    # === Play demo sound if waiting ===
    if waiting_for_coin and settings["demo_sound"] == "ON" and not pygame.mixer.get_busy():
        demo_bgm.play(-1)

    # === Handle Arduino Input ===
    if "TEST" in input_states:
        test_mode = True
        waiting_for_coin = ready_to_start = game_active = False
        show_game_over_screen = False
        demo_bgm.stop()
        input_states.clear()

    if test_mode:
        if "DOWN" in input_states:
            current_setting = (current_setting + 1) % len(setting_keys)
            time.sleep(0.5)
        elif "UP" in input_states:
            current_setting = (current_setting - 1) % len(setting_keys)
            time.sleep(0.5)
        elif "DEC" in input_states:
            key = setting_keys[current_setting]
            if isinstance(settings[key], int):
                settings[key] = max(1, settings[key] - 1)
            elif key == "difficulty":
                settings[key] = {"easy": "hard", "normal": "easy", "hard": "normal"}[settings[key]]
            elif key == "demo_sound":
                settings[key] = "OFF" if settings[key] == "ON" else "ON"
            time.sleep(0.5)
        elif "INC" in input_states:
            key = setting_keys[current_setting]
            if isinstance(settings[key], int):
                settings[key] += 1
            elif key == "difficulty":
                settings[key] = {"easy": "normal", "normal": "hard", "hard": "easy"}[settings[key]]
            elif key == "demo_sound":
                settings[key] = "ON" if settings[key] == "OFF" else "OFF"
            time.sleep(0.5)
        elif "SAVE" in input_states:
            save_settings()
            apply_difficulty()
            test_mode = False
            waiting_for_coin = True
        input_states.clear()

    if not test_mode and not show_game_over_screen:
        if waiting_for_coin and "COIN" in input_states:
            coins_inserted += 1
            coin_sound.play()
            demo_bgm.stop()
            if coins_inserted >= settings["coin_per_game"]:
                waiting_for_coin = False
                ready_to_start = True
            input_states.clear()

        elif ready_to_start and "START" in input_states:
            if coins_inserted >= settings["coin_per_game"]:
                coins_inserted -= settings["coin_per_game"]
                game_active = True
                ready_to_start = False
                start_sound.play()
                reset_game()
            input_states.clear()

        elif game_active and not hit_pause and "START" in input_states:
            bird_movement = -10
            flap_sound.play()
            input_states.clear()

    if test_mode:
        display_test_mode()

    elif show_game_over_screen:
        screen.fill((0, 0, 0))
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        score_text = small_font.render(f"Score: {final_score}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
        ticket_text = small_font.render(f"Tickets: {final_tickets}", True, (255, 255, 0))
        screen.blit(ticket_text, (WIDTH//2 - ticket_text.get_width()//2, HEIGHT//2 + 30))
        if pygame.time.get_ticks() - game_over_time >= 5000:
            for _ in range(final_tickets):
                arduino.write(b"TICKET_ON\n")
                pygame.time.wait(300)
                arduino.write(b"TICKET_OFF\n")
                pygame.time.wait(300)
            show_game_over_screen = False
            waiting_for_coin = True
            pipe_list.clear()
            bird_rect.center = (100, HEIGHT // 2)
            bird_movement = 0

    else:
        if not hit_pause:
            bg_x -= bg_speed
            if bg_x <= -WIDTH:
                bg_x = 0
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))

        if waiting_for_coin:
            t = font.render("INSERT COIN", True, (255, 50, 0))
            screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 50))
            needed = settings["coin_per_game"]
            c = small_font.render(f"Coins: {coins_inserted}/{needed}", True, (255, 0, 0))
            screen.blit(c, (WIDTH//2 - c.get_width()//2, HEIGHT//2 + 700))
        elif ready_to_start:
            t = font.render("Press START", True, (150, 255, 60))
            screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2))

        if game_active or waiting_for_coin:
            is_demo = waiting_for_coin and not game_active

            if hit_pause:
                if pygame.time.get_ticks() - hit_time >= 1000:
                    hit_pause = False
                    bird_rect.center = (100, HEIGHT // 2)
                    bird_movement = 0
                    pipe_list.clear()
                else:
                    t = font.render("Get Ready...", True, (255, 255, 0))
                    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2))
                    pygame.display.update()
                    continue

            bird_movement += gravity
            bird_rect.centery += bird_movement
            screen.blit(player_img, bird_rect)

            pipe_speed = 2 + (score // 10)
            for pipe in pipe_list:
                pipe['rect'].centerx -= pipe_speed
            draw_pipes(pipe_list)

            if is_demo and bird_rect.bottom > HEIGHT - 100:
                bird_movement = -10

            if is_demo and (bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT):
                bird_rect.center = (100, HEIGHT // 2)
                bird_movement = 0
                pipe_list.clear()

            if not is_demo and not check_collision(pipe_list):
                lives -= 1
                if lives > 0:
                    hit_pause = True
                    hit_time = pygame.time.get_ticks()
                else:
                    game_over_sound.play()
                    game_active = False
                    show_game_over_screen = True
                    game_over_time = pygame.time.get_ticks()
                    final_score = score
                    final_tickets = final_score // settings["score_per_ticket"]

            for pipe in pipe_list:
                if pipe['type'] == 'bottom' and not pipe.get('passed') and pipe['rect'].centerx < bird_rect.centerx:
                    pipe['passed'] = True
                    if not is_demo:
                        score += settings["score_per_pipe"]
                        point_sound.play()

            if not is_demo:
                display_score(score)
                display_lives(lives)

    pygame.display.update()
    clock.tick(60)
