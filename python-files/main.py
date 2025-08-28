import pygame
import random
import sys

# --- Config ---
GRID_SIZE = 3
HOLE_SIZE = 120
BORDER = 80
TOP_BAR_HEIGHT = 100
HOLE_GAP = 120
MOLE_POP_HEIGHT = 40
KO_DISPLAY_TIME = 500  # ms KO stays up
POP_ANIM_TIME = 180

START_POPUP_INTERVAL = 1500    # How long each mole stays up at start (ms)
MIN_POPUP_INTERVAL = 500
START_SPAWN_INTERVAL = 1200    # How often new moles spawn at start (ms)
MIN_SPAWN_INTERVAL = 600

SPEEDUP_POPUP_PER_HIT = 10     # ms decrease per hit (stay-up time)
SPEEDUP_SPAWN_PER_HIT = 10     # ms decrease per hit (spawn rate)

BOARD_SIZE = GRID_SIZE * HOLE_SIZE + (GRID_SIZE - 1) * HOLE_GAP
SCREEN_SIZE = BOARD_SIZE + BORDER * 2

DIRT_BROWN = (150, 90, 30)
HOLE_COLOR = (40, 25, 10)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

LEADERBOARD_FILE = "data/leaderboard.txt"
MAX_LEADERBOARD = 10

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + TOP_BAR_HEIGHT))
pygame.display.set_caption("Whack-a-Mole")
clock = pygame.time.Clock()

def get_font(size, bold=True):
    try:
        return pygame.font.Font("LuckiestGuy-Regular.ttf", size)
    except:
        return pygame.font.SysFont("comic sans ms", size, bold=bold)

font = get_font(48)
small_font = get_font(36)

grass_img = pygame.image.load("assets/grass.jpg")
grass_img = pygame.transform.scale(grass_img, (SCREEN_SIZE, SCREEN_SIZE + TOP_BAR_HEIGHT))
mole_img = pygame.image.load("assets/mole_asset.png").convert_alpha()
mole_img_ko = pygame.image.load("assets/mole_asset_ko.png").convert_alpha()
life_icon = pygame.image.load("assets/life_icon.png").convert_alpha()

ASSET_SCALE = HOLE_SIZE / mole_img.get_width() * 1.3
asset_w = int(mole_img.get_width() * ASSET_SCALE)
asset_h = int(mole_img.get_height() * ASSET_SCALE)
mole_img = pygame.transform.scale(mole_img, (asset_w, asset_h))
mole_img_ko = pygame.transform.scale(mole_img_ko, (asset_w, asset_h))
life_icon = pygame.transform.scale(life_icon, (60, 60))

pygame.mixer.init()
sound_choices = [
    ("sounds/ouch.wav", 20), ("sounds/ow.wav", 20), ("sounds/owie.wav", 20),
    ("sounds/guah.wav", 15), ("sounds/stop.wav", 15),
    ("sounds/thathurts.wav", 10), ("sounds/acceptmytrade.wav", 5),
]
sounds, weights, weight_cumulative = [], [], []
for filename, weight in sound_choices:
    sounds.append(pygame.mixer.Sound(filename))
    weights.append(weight)
weight_total = sum(weights)
cumsum = 0
for w in weights:
    cumsum += w
    weight_cumulative.append(cumsum)
def play_weighted_sound():
    r = random.uniform(0, weight_total)
    for i, cum_w in enumerate(weight_cumulative):
        if r < cum_w:
            sounds[i].play()
            break

hole_positions = []
for y in range(GRID_SIZE):
    for x in range(GRID_SIZE):
        cx = BORDER + x * (HOLE_SIZE + HOLE_GAP) + HOLE_SIZE // 2
        cy = TOP_BAR_HEIGHT + BORDER + y * (HOLE_SIZE + HOLE_GAP) + HOLE_SIZE // 2 + 20
        hole_positions.append((cx, cy))

def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        entries = []
        for line in lines:
            if "," in line:
                name, score = line.rsplit(",", 1)
                entries.append((name, int(score)))
        entries.sort(key=lambda x: -x[1])
        return entries[:MAX_LEADERBOARD]
    except Exception:
        return []

def save_leaderboard(entries):
    entries.sort(key=lambda x: -x[1])
    with open(LEADERBOARD_FILE, "w") as f:
        for name, score in entries[:MAX_LEADERBOARD]:
            f.write(f"{name},{score}\n")

def draw_button(rect, text, highlighted, font, y_offset=0):
    color = (110, 170, 250) if highlighted else (220, 220, 220)
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, (80, 120, 200), rect, 3, border_radius=15)
    surf = font.render(text, True, BLACK)
    screen.blit(surf, (rect.x + rect.w//2 - surf.get_width()//2, rect.y + rect.h//2 - surf.get_height()//2 + y_offset))

def draw_background():
    screen.blit(grass_img, (0, 0))

def draw_topbar(score, lives, max_lives=3):
    lives_text = small_font.render("Lives:", True, BLACK)
    screen.blit(lives_text, (10, 15))
    for i in range(lives):
        screen.blit(life_icon, (10 + lives_text.get_width() + 10 + i * 65, 5))
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(topright=(SCREEN_SIZE - 10, 20))
    screen.blit(score_text, score_rect)

def show_title_screen():
    BUTTON_W = 320
    BUTTON_H = 80
    BUTTON_GAP = 38
    font_btn = get_font(48)
    font_lead = get_font(38)
    draw_background()
    big_font = get_font(90)
    word1 = "Whack-a-M"
    word2 = "le"
    y_logo = 120
    surf1 = big_font.render(word1, True, WHITE)
    surf2 = big_font.render(word2, True, WHITE)
    o_space = 74
    total_logo_width = surf1.get_width() + o_space + surf2.get_width()
    x_logo = (SCREEN_SIZE - total_logo_width) // 2
    screen.blit(surf1, (x_logo, y_logo))
    cx = x_logo + surf1.get_width() + o_space // 2
    cy = y_logo + big_font.get_height() // 2 + 10
    HOLE_W, HOLE_H = 64, 30
    pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W//2, cy - HOLE_H//2, HOLE_W, HOLE_H))
    MOLE_O_POP_HEIGHT = 16
    mole_logo_scale = HOLE_W / asset_w * 1.1
    mole_logo_w = int(asset_w * mole_logo_scale)
    mole_logo_h = int(asset_h * mole_logo_scale)
    mole_logo_img = pygame.transform.smoothscale(mole_img, (mole_logo_w, mole_logo_h))
    hole_top_y = cy - HOLE_H//2
    mole_bottom_y = hole_top_y + MOLE_O_POP_HEIGHT
    screen.blit(mole_logo_img, (cx - mole_logo_w // 2, mole_bottom_y - mole_logo_h))
    lip_rect = pygame.Rect(cx - HOLE_W//2, cy - HOLE_H//2, HOLE_W, int(HOLE_H // 1.2))
    pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
    screen.blit(surf2, (cx + HOLE_W//2, y_logo))

    btn_y = SCREEN_SIZE // 2 + 50
    btn1 = pygame.Rect(SCREEN_SIZE//2 - BUTTON_W//2, btn_y, BUTTON_W, BUTTON_H)
    btn2 = pygame.Rect(SCREEN_SIZE//2 - BUTTON_W//2, btn_y + BUTTON_H + BUTTON_GAP, BUTTON_W, BUTTON_H)
    highlighted = [False, False]

    in_title = True
    showing_leaderboard = False
    leaderboard = load_leaderboard()
    while in_title:
        mx, my = pygame.mouse.get_pos()
        highlighted[0] = btn1.collidepoint(mx, my)
        highlighted[1] = btn2.collidepoint(mx, my)
        draw_background()
        screen.blit(surf1, (x_logo, y_logo))
        screen.blit(mole_logo_img, (cx - mole_logo_w // 2, mole_bottom_y - mole_logo_h))
        pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
        screen.blit(surf2, (cx + HOLE_W//2, y_logo))
        if showing_leaderboard:
            # Table settings
            leaderboard = load_leaderboard()
            table_width = 410
            table_x = SCREEN_SIZE//2 - table_width//2
            table_y = btn_y - 162   # moved up by 22 pixels
            row_height = 34
            header_height = 36
            table_height = 10*row_height + header_height + 44 # +44 for more room at bottom
            pygame.draw.rect(screen, (255,255,255,220), (table_x-12, table_y-12, table_width+24, table_height+24), border_radius=15)

            col1_x = table_x + 16
            col2_x = table_x + 70
            col3_x = table_x + 280
            header_y = table_y + 2 # moved header up by 10 pixels

            # Column headers (blue)
            header_font = get_font(36, bold=True)
            header_color = (50, 110, 210)
            screen.blit(header_font.render("#", True, header_color), (col1_x, header_y))
            screen.blit(header_font.render("NAME", True, header_color), (col2_x, header_y))
            screen.blit(header_font.render("SCORE", True, header_color), (col3_x, header_y))
            # Line under headers
            pygame.draw.line(screen, (150,150,150), (table_x+10, header_y+45), (table_x+table_width-10, header_y+45), 2)
            # Table entries
            row_font = get_font(38)
            for i in range(MAX_LEADERBOARD):
                row_y = header_y + 40 + i*row_height
                if i < len(leaderboard):
                    name = leaderboard[i][0][:6].upper()
                    score = str(leaderboard[i][1])
                    screen.blit(row_font.render(str(i+1), True, BLACK), (col1_x, row_y))
                    screen.blit(row_font.render(name, True, BLACK), (col2_x, row_y))
                    screen.blit(row_font.render(score, True, BLACK), (col3_x, row_y))
            # Back button (now with more space below)
            back_rect = pygame.Rect(SCREEN_SIZE//2 - 120, table_y+table_height+26, 240, 62)
            highlight_back = back_rect.collidepoint(mx, my)
            draw_button(back_rect, "Back", highlight_back, font_btn, y_offset=4)
        else:
            draw_button(btn1, "Start Game", highlighted[0], font_btn)
            draw_button(btn2, "Leaderboard", highlighted[1], font_btn)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if showing_leaderboard:
                    back_rect = pygame.Rect(SCREEN_SIZE//2 - 120, table_y+table_height+26, 240, 62)
                    if back_rect.collidepoint(mx, my):
                        showing_leaderboard = False
                else:
                    if btn1.collidepoint(mx, my):
                        return
                    elif btn2.collidepoint(mx, my):
                        showing_leaderboard = True
        clock.tick(60)

def show_countdown():
    try:
        countdown_sound = pygame.mixer.Sound("sounds/count_down.wav")
        countdown_sound.set_volume(0.3)
    except:
        countdown_sound = None

    countdown_font = get_font(140)
    if countdown_sound:
        countdown_sound.play()
    for num in ["3", "2", "1"]:
        draw_background()
        draw_topbar(0, 3)  # Show score and lives (0 and 3) above the holes during countdown
        for (cx, cy) in hole_positions:
            HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
            pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
            lip_rect = pygame.Rect(cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H // 1.2)
            pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
        surf = countdown_font.render(num, True, WHITE)
        screen.blit(surf, (SCREEN_SIZE // 2 - surf.get_width() // 2, SCREEN_SIZE // 2 - surf.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(1000)
    # --- STOP COUNTDOWN SOUND HERE ---
    if countdown_sound:
        countdown_sound.stop()

def show_game_over(final_score):
    draw_background()
    for (cx, cy) in hole_positions:
        HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
        pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
        hole_top_y = cy - HOLE_H // 2
        mole_bottom_y = hole_top_y + MOLE_POP_HEIGHT
        screen.blit(mole_img, (cx - asset_w // 2, mole_bottom_y - asset_h))
        lip_rect = pygame.Rect(cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H // 1.2)
        pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
    overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + TOP_BAR_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))
    big_font = get_font(90)
    score_font = get_font(64)
    prompt_font = get_font(46)
    over = big_font.render("Game Over!", True, WHITE)
    score_msg = score_font.render(f"Score: {final_score}", True, WHITE)
    screen.blit(over, (SCREEN_SIZE // 2 - over.get_width() // 2, SCREEN_SIZE // 2 - 180))
    screen.blit(score_msg, (SCREEN_SIZE // 2 - score_msg.get_width() // 2, SCREEN_SIZE // 2 - 40))

    # Input for initials/name (ALL CAPS, 6 char limit) - box moved lower, centered text
    prompt = prompt_font.render("Enter your name:", True, WHITE)
    input_box = pygame.Rect(SCREEN_SIZE//2 - 140, SCREEN_SIZE//2 + 180, 280, 60)  # moved down by +25
    input_color = (230, 230, 230)
    user_text = ""
    entering = True
    leaderboard = load_leaderboard()
    while entering:
        draw_background()
        for (cx, cy) in hole_positions:
            HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
            pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
            hole_top_y = cy - HOLE_H // 2
            mole_bottom_y = hole_top_y + MOLE_POP_HEIGHT
            screen.blit(mole_img, (cx - asset_w // 2, mole_bottom_y - asset_h))
            lip_rect = pygame.Rect(cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H // 1.2)
            pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + TOP_BAR_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        screen.blit(over, (SCREEN_SIZE // 2 - over.get_width() // 2, SCREEN_SIZE // 2 - 180))
        screen.blit(score_msg, (SCREEN_SIZE // 2 - score_msg.get_width() // 2, SCREEN_SIZE // 2 - 40))
        screen.blit(prompt, (SCREEN_SIZE // 2 - prompt.get_width() // 2, SCREEN_SIZE // 2 + 80))
        pygame.draw.rect(screen, input_color, input_box, border_radius=10)
        user_surface = prompt_font.render(user_text, True, BLACK)
        # Center user text in the input box:
        screen.blit(
            user_surface,
            (
                input_box.x + (input_box.w - user_surface.get_width()) // 2,
                input_box.y + (input_box.h - user_surface.get_height()) // 2
            )
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = user_text.strip()[:6].upper() if user_text.strip() else "ANON"
                    leaderboard.append((name, final_score))
                    save_leaderboard(leaderboard)
                    entering = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif len(user_text) < 6 and (event.unicode.isalnum() or event.unicode in " -_"):
                    user_text += event.unicode.upper()
        clock.tick(30)
    # Wait for click to continue to title
    pygame.time.wait(500)
    waiting = True
    press_font = get_font(38)
    press_msg = press_font.render("Click to return to title...", True, WHITE)
    while waiting:
        draw_background()
        for (cx, cy) in hole_positions:
            HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
            pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
            hole_top_y = cy - HOLE_H // 2
            mole_bottom_y = hole_top_y + MOLE_POP_HEIGHT
            screen.blit(mole_img, (cx - asset_w // 2, mole_bottom_y - asset_h))
            lip_rect = pygame.Rect(cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H // 1.2)
            pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + TOP_BAR_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        screen.blit(over, (SCREEN_SIZE // 2 - over.get_width() // 2, SCREEN_SIZE // 2 - 180))
        screen.blit(score_msg, (SCREEN_SIZE // 2 - score_msg.get_width() // 2, SCREEN_SIZE // 2 - 40))
        screen.blit(press_msg, (SCREEN_SIZE // 2 - press_msg.get_width() // 2, SCREEN_SIZE // 2 + 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        clock.tick(30)

def draw_hole_and_mole(cx, cy, show_mole, ko=False, vertical_offset=0):
    HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
    pygame.draw.ellipse(screen, HOLE_COLOR, (cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H))
    if show_mole:
        img = mole_img_ko if ko else mole_img
        hole_top_y = cy - HOLE_H // 2
        mole_bottom_y = hole_top_y + vertical_offset + MOLE_POP_HEIGHT
        screen.blit(img, (cx - asset_w // 2, mole_bottom_y - asset_h))
    lip_rect = pygame.Rect(cx - HOLE_W // 2, cy - HOLE_H // 2, HOLE_W, HOLE_H // 1.2)
    pygame.draw.ellipse(screen, DIRT_BROWN, lip_rect)

# ------------ MULTI-MOLE WITH ANIMATION LOGIC --------------
class ActiveMole:
    def __init__(self, hole, spawn_time, popup_interval):
        self.hole = hole
        self.spawn_time = spawn_time
        self.status = "popping_up"     # or "up", "ko", "popping_down"
        self.anim_start = spawn_time
        self.offset = HOLE_SIZE // 2   # animation vertical offset
        self.popup_interval = popup_interval
        self.ko_time = None

    def update(self, now):
        # Animation logic
        if self.status == "popping_up":
            t = min((now - self.anim_start) / POP_ANIM_TIME, 1.0)
            self.offset = int(HOLE_SIZE // 2 * (1 - t))
            if t >= 1.0:
                self.status = "up"
                self.offset = 0
        elif self.status == "popping_down":
            t = min((now - self.anim_start) / POP_ANIM_TIME, 1.0)
            self.offset = int(HOLE_SIZE // 2 * t)
            if t >= 1.0:
                return "remove"
        elif self.status == "ko":
            self.offset = 0
            if now - self.ko_time > KO_DISPLAY_TIME:
                return "remove"
        elif self.status == "up":
            self.offset = 0
            if now - self.anim_start > self.popup_interval:
                self.status = "popping_down"
                self.anim_start = now
        return "keep"

# --- Main Game Loop ---
while True:
    show_title_screen()
    show_countdown()
    score = 0
    lives = 3

    popup_interval = START_POPUP_INTERVAL
    spawn_interval = START_SPAWN_INTERVAL
    # Spawn first mole immediately after countdown:
    last_spawn_time = pygame.time.get_ticks() - spawn_interval
    active_moles = []

    running = True
    while running:
        now = pygame.time.get_ticks()

        # --- SPAWN MOLE LOGIC ---
        if now - last_spawn_time >= spawn_interval:
            # Try to spawn a mole if any free hole
            used_holes = {mole.hole for mole in active_moles}
            free_holes = [i for i in range(GRID_SIZE * GRID_SIZE) if i not in used_holes]
            if free_holes:
                hole = random.choice(free_holes)
                active_moles.append(ActiveMole(hole, now, popup_interval))
                last_spawn_time = now

        # --- DRAW EVERYTHING ---
        draw_background()
        draw_topbar(score, lives)
        # Draw moles
        for mole in active_moles:
            cx, cy = hole_positions[mole.hole]
            if mole.status == "ko":
                draw_hole_and_mole(cx, cy, True, ko=True, vertical_offset=mole.offset)
            else:
                draw_hole_and_mole(cx, cy, True, ko=False, vertical_offset=mole.offset)
        # Draw empty holes
        for idx, (cx, cy) in enumerate(hole_positions):
            if not any(m.hole == idx for m in active_moles):
                draw_hole_and_mole(cx, cy, False)
        pygame.display.flip()
        clock.tick(60)

        # --- UPDATE MOLES & REMOVE FINISHED ONES ---
        remove_list = []
        for mole in active_moles:
            result = mole.update(now)
            if result == "remove":
                if mole.status == "popping_down":
                    lives -= 1
                    if lives == 0:
                        running = False
                remove_list.append(mole)
        active_moles = [mole for mole in active_moles if mole not in remove_list]

        # --- HANDLE EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for mole in active_moles:
                    if mole.status == "up":
                        cx, cy = hole_positions[mole.hole]
                        HOLE_W, HOLE_H = HOLE_SIZE, HOLE_SIZE // 2
                        hole_top_y = cy - HOLE_H // 2
                        mole_bottom_y = hole_top_y + mole.offset + MOLE_POP_HEIGHT
                        mole_rect = pygame.Rect(cx - asset_w // 2, mole_bottom_y - asset_h, asset_w, asset_h)
                        if mole_rect.collidepoint(mx, my):
                            score += 1
                            play_weighted_sound()
                            mole.status = "ko"
                            mole.ko_time = now
                            # speed up game
                            popup_interval = max(MIN_POPUP_INTERVAL, popup_interval - SPEEDUP_POPUP_PER_HIT)
                            spawn_interval = max(MIN_SPAWN_INTERVAL, spawn_interval - SPEEDUP_SPAWN_PER_HIT)
                            break  # only hit one mole per click

    show_game_over(score)
