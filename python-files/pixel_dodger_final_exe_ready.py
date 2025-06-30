
import pygame, random, sys, json, os
import numpy as np

WIDTH, HEIGHT = 320, 240
FPS = 60
PLAYER_SIZE = 16
ENEMY_SIZE = 16
POWER_SIZE = 12
SAVE_FILE = "savegame.json"

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pixel Dodger")
game_surface = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 16)

def make_sprite(size, color, border=None):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, size, size))
    if border:
        pygame.draw.rect(surf, border, (0, 0, size, size), 2)
    return surf

player_img = make_sprite(PLAYER_SIZE, (50, 200, 255), (255, 255, 255))
enemy_img = make_sprite(ENEMY_SIZE, (255, 50, 50))
inv_img = make_sprite(POWER_SIZE, (255, 255, 100))
slowmo_img = make_sprite(POWER_SIZE, (100, 255, 255))

def generate_beep(freq=440, duration_ms=200, volume=0.5):
    sample_rate = 44100
    samples = int(sample_rate * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms / 1000.0, samples, False)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t))
    audio = (volume * 32767 * wave).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

beep = generate_beep()

pygame.joystick.init()
joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
if joy: joy.init()

def load_state():
    if os.path.exists(SAVE_FILE):
        return json.load(open(SAVE_FILE))
    return {"high_score": 0}

def save_state(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

state = load_state()
high_score = state["high_score"]
player = pygame.Rect(WIDTH // 2, HEIGHT - 32, PLAYER_SIZE, PLAYER_SIZE)

def generate_bg(color, stars=30, haze=10):
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(color)
    for _ in range(stars):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        pygame.draw.circle(bg, (200, 200, 255), (x, y), 1)
    for _ in range(haze):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        w = random.randint(30, 60)
        h = random.randint(5, 15)
        alpha = random.randint(30, 70)
        haze_color = (*color, alpha)
        fog = pygame.Surface((w, h), pygame.SRCALPHA)
        fog.fill(haze_color)
        bg.blit(fog, (x, y))
    return bg

backgrounds = [
    generate_bg((10, 10, 30)),
    generate_bg((40, 0, 30)),
    generate_bg((0, 40, 20)),
    generate_bg((60, 30, 0)),
]

def get_background(score):
    level = (score // 25) % len(backgrounds)
    return backgrounds[level]

def pause_menu():
    options = ["Resume", "Restart", "Quit"]
    selected = 0
    while True:
        game_surface.fill((0, 0, 0))
        game_surface.blit(font.render("PAUSED", True, (255, 255, 255)), (130, 70))
        for i, text in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            game_surface.blit(font.render(text, True, color), (110, 110 + i * 25))
        scaled = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif e.key == pygame.K_RETURN:
                    if selected == 0: return  # Resume
                    elif selected == 1: game_loop()  # Restart
                    elif selected == 2:
                        pygame.quit(); sys.exit()
        if joy:
            if joy.get_hat(0)[1] == 1:
                selected = (selected - 1) % len(options)
            elif joy.get_hat(0)[1] == -1:
                selected = (selected + 1) % len(options)
            if joy.get_button(0):
                if selected == 0: return
                elif selected == 1: game_loop()
                elif selected == 2:
                    pygame.quit(); sys.exit()

def game_loop():
    running = True
    global high_score
    score = 0
    speed = 4
    inv_timer = slowmo_timer = 0
    obstacles = []
    powerups = []
    player.x = WIDTH // 2
    timers = dict(obs=0, score=0, diff=0, power=0)

    while True:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if e.type == pygame.QUIT:
                save_state({"high_score": high_score})
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            pause_menu()
            continue
        move = 0
        if keys[pygame.K_LEFT]: move = -4
        if keys[pygame.K_RIGHT]: move = 4
        if joy:
            ax = joy.get_axis(0)
            if abs(ax) > 0.2:
                move = int(ax * 4)
        player.x = max(0, min(player.x + move, WIDTH - PLAYER_SIZE))

        for k in timers: timers[k] += 1
        if timers["obs"] > 30:
            x = random.randint(0, WIDTH - ENEMY_SIZE)
            obstacles.append(pygame.Rect(x, -ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE))
            timers["obs"] = 0
        if timers["power"] > 300:
            kind = "inv" if score % 2 == 0 else "slowmo"
            x = random.randint(0, WIDTH - POWER_SIZE)
            powerups.append((kind, pygame.Rect(x, -POWER_SIZE, POWER_SIZE, POWER_SIZE)))
            timers["power"] = 0
        if timers["score"] > FPS:
            score += 1
            timers["score"] = 0
        if timers["diff"] > FPS * 10:
            speed += 1
            timers["diff"] = 0

        powerups = [(k, r.move(0, 2)) for k, r in powerups if r.y < HEIGHT]
        for k, r in powerups:
            if player.colliderect(r):
                if k == "inv": inv_timer = FPS * 5
                if k == "slowmo": slowmo_timer = FPS * 5

        obs_speed = speed // 2 if slowmo_timer > 0 else speed
        obstacles = [r.move(0, obs_speed) for r in obstacles if r.y < HEIGHT]

        if inv_timer == 0 and any(player.colliderect(o) for o in obstacles):
            beep.play()
            if score > high_score:
                high_score = score
                save_state({"high_score": high_score})
            game_over_screen(score, high_score)
            return

        inv_timer = max(0, inv_timer - 1)
        slowmo_timer = max(0, slowmo_timer - 1)

        bg = get_background(score)
        game_surface.blit(bg, (0, 0))
        game_surface.blit(player_img, player)
        for r in obstacles:
            game_surface.blit(enemy_img, r)
        for k, r in powerups:
            game_surface.blit(inv_img if k == "inv" else slowmo_img, r)
        game_surface.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (8, 8))
        game_surface.blit(font.render(f"High: {high_score}", True, (255, 255, 255)), (8, 28))
        scaled = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

def game_over_screen(score, high_score):
    beep.play()
    game_surface.fill((0, 0, 0))
    game_surface.blit(font.render("GAME OVER", True, (255, 255, 255)), (100, 90))
    game_surface.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (110, 115))
    game_surface.blit(font.render(f"High Score: {high_score}", True, (255, 255, 255)), (110, 135))
    game_surface.blit(font.render("Press Enter to Retry", True, (255, 255, 255)), (70, 160))
    scaled = pygame.transform.scale(game_surface, screen.get_size())
    screen.blit(scaled, (0, 0))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]: return
        if joy and joy.get_button(0): return

def menu():
    game_surface.fill((0, 0, 0))
    game_surface.blit(font.render("PIXEL DODGER", True, (255, 255, 255)), (80, 100))
    game_surface.blit(font.render("Press Enter to Play", True, (255, 255, 255)), (60, 130))
    scaled = pygame.transform.scale(game_surface, screen.get_size())
    screen.blit(scaled, (0, 0))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]: return
        if joy and joy.get_button(0): return

while True:
    menu()
    game_loop()