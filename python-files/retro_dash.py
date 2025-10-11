import pygame, sys, random, os

# --- INIT ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Geometry Dash 🎵")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 24, bold=True)

# --- COLORS ---
BG = (15, 15, 30)
GROUND_COLOR = (40, 40, 70)
PLAYER_COLOR = (255, 200, 60)
BLOCK_COLOR = (90, 200, 255)
SPIKE_COLOR = (255, 80, 80)
TEXT_COLOR = (230, 230, 230)
SLOW_OVERLAY = (150, 150, 150, 80)

# --- PLAYER ---
player = pygame.Rect(100, HEIGHT - 60, 28, 28)
vel_y = 0
gravity = 1
jump_strength = -16
on_ground = True

# --- GAME STATE ---
speed = 6
score = 0
best = 0
alive = True
obstacles = []
spawn_timer = 0
slow_motion = False
slow_factor = 0.3
paused = False

# --- SCANLINES ---
scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 4):
    pygame.draw.line(scanlines, (0, 0, 0, 40), (0, y), (WIDTH, y))

# --- SOUNDS (PyInstaller friendly) ---
if getattr(sys, 'frozen', False):
    # Running as .exe
    script_dir = sys._MEIPASS
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

jump_path = os.path.join(script_dir, "jump.wav")
music_path = os.path.join(script_dir, "retro_music.wav")

jump_sound = None
if os.path.exists(jump_path):
    try:
        jump_sound = pygame.mixer.Sound(jump_path)
        jump_sound.set_volume(0.3)
    except pygame.error as e:
        print("Jump sound error:", e)
else:
    print("jump.wav not found!")

if os.path.exists(music_path):
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print("Music error:", e)
else:
    print("retro_music.wav not found!")

# --- RESET ---
def reset():
    global speed, score, obstacles, vel_y, alive
    speed = 6
    score = 0
    obstacles.clear()
    vel_y = 0
    player.x, player.y = 100, HEIGHT - 60
    alive = True

# --- SPAWN OBSTACLES ---
def spawn_obstacle():
    kind = random.choice(["spike", "stair", "block"])
    x_start = WIDTH + 20
    new_obs = []

    if kind == "spike":
        size = 30
        new_obs.append(("spike", x_start, HEIGHT - 20, size))
    elif kind == "block":
        w = random.randint(60, 150)
        h = random.randint(20, 50)
        y = HEIGHT - 20 - h
        new_obs.append(("block", x_start, y, w, h))
        # Add spike on top if block is wide
        if w >= 50 and random.random() < 0.5:
            new_obs.append(("spike", x_start + w//3, y, 20))
    elif kind == "stair":
        stair_w, stair_h = 30, 20
        steps = random.randint(3, 6)
        for i in range(steps):
            y = HEIGHT - 20 - stair_h*(i+1)
            new_obs.append(("block", x_start + i*stair_w, y, stair_w, stair_h))
            if random.random() < 0.3:
                new_obs.append(("spike", x_start + i*stair_w + 5, y, 20))

    obstacles.extend(new_obs)

# --- COLLISION ---
def collide(player, obs):
    kind = obs[0]
    if kind == "spike":
        _, x, base_y, size = obs
        spike_box = pygame.Rect(x+4, base_y - size + 6, size-8, size-6)
        return player.colliderect(spike_box)
    elif kind == "block":
        _, x, y, w, h = obs
        block_rect = pygame.Rect(x, y, w, h)
        if player.colliderect(block_rect):
            if player.bottom > y + 5 and player.top < y + h - 5:
                return True
    return False

# --- DRAW OBSTACLE ---
def draw_obstacle(obs):
    kind = obs[0]
    if slow_motion:
        block_col = (255, 255, 255)
        spike_col = (0, 0, 0)
        outline = (180, 180, 180)
    else:
        block_col = BLOCK_COLOR
        spike_col = SPIKE_COLOR
        outline = (255, 255, 255)

    if kind == "block":
        _, x, y, w, h = obs
        pygame.draw.rect(WIN, block_col, (x, y, w, h))
        pygame.draw.rect(WIN, outline, (x, y, w, h), 2)
    elif kind == "spike":
        _, x, base_y, size = obs
        points = [(x, base_y), (x + size//2, base_y - size), (x + size, base_y)]
        pygame.draw.polygon(WIN, spike_col, points)
        pygame.draw.polygon(WIN, outline, points, 2)

# --- DRAW WINDOW ---
def draw_window():
    if slow_motion:
        bg = (80, 80, 80)
        ground = (120, 120, 120)
        player_col = (255, 255, 255)
        player_outline = (0, 0, 0)
        text_col = (200, 200, 200)
    else:
        bg = BG
        ground = GROUND_COLOR
        player_col = PLAYER_COLOR
        player_outline = (255, 255, 255)
        text_col = TEXT_COLOR

    WIN.fill(bg)
    pygame.draw.rect(WIN, ground, (0, HEIGHT-20, WIDTH, 20))

    for o in obstacles:
        draw_obstacle(o)

    pygame.draw.rect(WIN, player_col, player)
    pygame.draw.rect(WIN, player_outline, player, 2)

    s = font.render(f"Score: {score}", True, text_col)
    b = font.render(f"Best: {best}", True, text_col)
    hint_c = font.render("Press C for dynamic mode", True, text_col)
    hint_v = font.render("Press V to pause", True, text_col)
    WIN.blit(s, (10, 10))
    WIN.blit(b, (10, 40))
    WIN.blit(hint_c, (WIDTH - hint_c.get_width() - 10, 10))
    WIN.blit(hint_v, (WIDTH - hint_v.get_width() - 10, 40))

    # Pause screen
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        WIN.blit(overlay, (0, 0))
        pause_msg = font.render("PAUSED", True, (255, 255, 255))
        resume_msg = font.render("V to resume", True, (200, 200, 200))
        WIN.blit(pause_msg, (WIDTH//2 - pause_msg.get_width()//2, HEIGHT//2 - 30))
        WIN.blit(resume_msg, (WIDTH//2 - resume_msg.get_width()//2, HEIGHT//2 + 10))

    if not alive:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        WIN.blit(overlay, (0, 0))
        msg1 = font.render("💀 GAME OVER 💀", True, (255, 200, 200))
        msg2 = font.render("Press SPACE to restart", True, (200, 200, 200))
        WIN.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2 - 40))
        WIN.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2))

    WIN.blit(scanlines, (0, 0))
    if slow_motion:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 150, 150, 80))
        WIN.blit(overlay, (0, 0))

    pygame.display.update()

# --- GAME UPDATE ---
def update_game(delta):
    global vel_y, on_ground, score, best, alive, spawn_timer, speed, obstacles

    vel_y += gravity * delta
    player.y += vel_y * delta

    if player.y + player.height >= HEIGHT-20:
        player.y = HEIGHT-20 - player.height
        vel_y = 0
        on_ground = True
    else:
        on_ground = False

    spawn_timer -= delta
    if spawn_timer <= 0:
        spawn_obstacle()
        spawn_timer = random.randint(50, 90)

    new_obs = []
    for o in obstacles:
        kind = o[0]
        if kind == "block":
            kind, x, y, w, h = o
            x -= speed * delta
            rect = pygame.Rect(x, y, w, h)
            if player.colliderect(rect):
                if vel_y >= 0 and player.bottom <= rect.top + 15:
                    player.bottom = rect.top
                    vel_y = 0
                    on_ground = True
                else:
                    alive = False
            if x + w > 0:
                new_obs.append((kind, x, y, w, h))
            else:
                score += 10
        elif kind == "spike":
            kind, x, base_y, size = o
            x -= speed * delta
            new_o = (kind, x, base_y, size)
            if collide(player, new_o):
                alive = False
            if x + size > 0:
                new_obs.append(new_o)
            else:
                score += 10
    obstacles[:] = new_obs

    if score % 200 == 0 and score > 0:
        speed += 0.3 * delta

    if not alive:
        best = max(best, score)

# --- MAIN LOOP ---
running = True
while running:
    dt = clock.tick(60) / 16
    delta = slow_factor if slow_motion else 1

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_c:
                slow_motion = not slow_motion
                pygame.mixer.music.set_volume(0.6 * (0.5 if slow_motion else 1))
            if e.key == pygame.K_v:
                paused = not paused

    keys = pygame.key.get_pressed()
    if alive and not paused:
        if keys[pygame.K_SPACE] and on_ground:
            vel_y = jump_strength
            on_ground = False
            if jump_sound:
                jump_sound.play()
        update_game(delta)
    elif not alive:
        if keys[pygame.K_SPACE]:
            reset()

    draw_window()
