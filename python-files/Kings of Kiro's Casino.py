import pygame, sys, random

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 1000
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kings of Kiro's Casino")

# Colors and font
WHITE, BLACK = (255,255,255), (0,0,0)
BLUE, RED, GREEN, GRAY, YELLOW = (0,120,255), (200,0,0), (0,200,0), (100,100,100), (255,210,0)
font = pygame.font.SysFont("Arial", 40)
font_small = pygame.font.SysFont("Arial", 24, bold=True)
font_big = pygame.font.SysFont("Arial", 60, bold=True)

# Set the app icon (optional)
try:
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
except:
    pass

# Menu options
menu_options = [
    "Instructions",
    "Difficulty",
    "Russian Roulette",
    "Black Joker",
    "Slots",
    "Poker",
    "Plinko",
    "Fishing Frenzy",
    "Crossy Road",
    "Quit"
]
selected = 0

clock = pygame.time.Clock()

# ---------------- CASINO STATE ---------------- #

credits = 1000
score = 0
bet = 10
difficulty = "Normal"  # Easy, Normal, Hard

def clamp_credits():
    global credits
    credits = max(0, credits)

def add_credits(amount):
    global credits
    credits += amount
    clamp_credits()

def add_score(amount):
    global score
    score = max(0, score + amount)

def draw_hud(extra=None):
    bar = pygame.Rect(0, 0, WIDTH, 50)
    pygame.draw.rect(WINDOW, (30,30,30), bar)
    pygame.draw.rect(WINDOW, (80,80,80), bar, 2)
    hud = font_small.render(f"Credits: {credits}    Score: {score}    Bet: {bet}    Diff: {difficulty}", True, WHITE)
    WINDOW.blit(hud, (20, 12))
    if extra:
        extra_txt = font_small.render(extra, True, WHITE)
        WINDOW.blit(extra_txt, (WIDTH - extra_txt.get_width() - 20, 12))

def get_diff_params():
    # Returns a dictionary of difficulty scaling parameters
    # You can tune these numbers to taste.
    if difficulty == "Easy":
        return {
            "cost_mult": 0.8,
            "payout_mult": 1.2,
            "speed_mult": 0.8,
            "risk_penalty_mult": 0.8,
            "reward_lane_credit": 12,  # Crossy Road lane bonus credits (per 10 score)
            "slots_payout_mult": 6,
        }
    if difficulty == "Hard":
        return {
            "cost_mult": 1.2,
            "payout_mult": 0.8,
            "speed_mult": 1.3,
            "risk_penalty_mult": 1.2,
            "reward_lane_credit": 8,
            "slots_payout_mult": 4,
        }
    # Normal
    return {
        "cost_mult": 1.0,
        "payout_mult": 1.0,
        "speed_mult": 1.0,
        "risk_penalty_mult": 1.0,
        "reward_lane_credit": 10,
        "slots_payout_mult": 5,
    }

# ---------------- DRAWING HELPERS ---------------- #

def draw_star(surface, x, y, size=20, color=(255,255,0)):
    points = []
    for i in range(10):
        angle = i * 36
        radius = size if i % 2 == 0 else size // 2
        vec = pygame.math.Vector2(0, -radius).rotate(angle)
        points.append((x + vec.x, y + vec.y))
    pygame.draw.polygon(surface, color, points)

def draw_cherry(surface, x, y):
    pygame.draw.circle(surface, (200,0,0), (x,y), 16)
    pygame.draw.circle(surface, (200,0,0), (x+26,y), 16)
    pygame.draw.line(surface, (0,200,0), (x+13,y-18), (x+13,y-38), 4)
    pygame.draw.circle(surface, (0,160,0), (x+13,y-40), 5)

def draw_seven(surface, x, y, color=(255,0,0)):
    text = font_big.render("7", True, color)
    surface.blit(text, (x-18, y-40))

def draw_card(surface, rect, rank, suit, face_color=(255,255,255), border_color=(0,0,0)):
    pygame.draw.rect(surface, face_color, rect, border_radius=6)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=6)
    label = font_small.render(f"{rank}{suit}", True, border_color)
    surface.blit(label, (rect.x+8, rect.y+6))
    cx, cy = rect.center
    if suit == "♥":
        pygame.draw.circle(surface, (220,0,0), (cx-10, cy-10), 10)
        pygame.draw.circle(surface, (220,0,0), (cx+10, cy-10), 10)
        pygame.draw.polygon(surface, (220,0,0), [(cx-20, cy-5),(cx+20, cy-5),(cx, cy+25)])
    elif suit == "♦":
        pygame.draw.polygon(surface, (220,0,0), [(cx, cy-20),(cx+15, cy),(cx, cy+20),(cx-15, cy)])
    elif suit == "♠":
        pygame.draw.polygon(surface, (0,0,0), [(cx, cy-25),(cx+20, cy),(cx-20, cy)])
        pygame.draw.circle(surface, (0,0,0), (cx-10, cy-5), 10)
        pygame.draw.circle(surface, (0,0,0), (cx+10, cy-5), 10)
        pygame.draw.rect(surface, (0,0,0), (cx-3, cy+10, 6, 18))
    elif suit == "♣":
        pygame.draw.circle(surface, (0,0,0), (cx, cy-15), 10)
        pygame.draw.circle(surface, (0,0,0), (cx-12, cy), 10)
        pygame.draw.circle(surface, (0,0,0), (cx+12, cy), 10)
        pygame.draw.rect(surface, (0,0,0), (cx-3, cy+8, 6, 18))

def draw_button(surface, rect, text_str, bg=(40,40,40), fg=WHITE):
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, (200,200,200), rect, 2, border_radius=8)
    t = font_small.render(text_str, True, fg)
    surface.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

def math_sine(seed, x):
    # simple pseudo-wave without importing math for aesthetics
    return ((seed*13 + x) % 20 - 10) / 10.0

# ---------------- INSTRUCTIONS ---------------- #

def instructions():
    running = True
    lines = [
        "Welcome to Kings of Kiro's Casino!",
        "",
        "Controls:",
        "- Use UP/DOWN to navigate menus",
        "- ENTER to select",
        "- ESC to return to the menu",
        "",
        "Global:",
        "- Credits are used to play; Score is your performance.",
        "- On exit, your Score converts into Credits (cashout).",
        "",
        "Games:",
        "Russian Roulette: Pay to spin; survive for score.",
        "Black Joker: Draw cards, avoid the Joker. Streaks grant score.",
        "Slots: Spin reels; adjust bet with +/-.",
        "Poker: Deal 5 cards; payouts for hand types.",
        "Plinko: Drop a ball; bin multipliers pay credits.",
        "Fishing Frenzy: Move boat, drop hook, catch fish.",
        "Crossy Road: Hop forward, avoid cars; score per lane.",
        "",
        "Difficulty:",
        "- Easy: Cheaper costs, higher payouts, slower obstacles.",
        "- Normal: Balanced.",
        "- Hard: Higher costs, lower payouts, faster obstacles.",
    ]
    while running:
        clock.tick(60)
        WINDOW.fill((0,0,0))
        title = font.render("Instructions", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, line in enumerate(lines):
            txt = font_small.render(line, True, WHITE)
            WINDOW.blit(txt, (60, 160 + i*30))
        hint = font_small.render("Press ESC to return", True, BLUE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-80))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

# ---------------- DIFFICULTY MENU ---------------- #

def difficulty_menu():
    global difficulty
    options = ["Easy","Normal","Hard"]
    idx = options.index(difficulty)
    running = True
    while running:
        clock.tick(60)
        WINDOW.fill((0,0,0))
        title = font.render("Select Difficulty", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, opt in enumerate(options):
            color = BLUE if i == idx else WHITE
            txt = font.render(opt, True, color)
            WINDOW.blit(txt, (WIDTH//2 - txt.get_width()//2, 220 + i*60))
        hint = font_small.render("UP/DOWN to choose, ENTER to confirm, ESC to cancel", True, WHITE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_UP: idx = (idx-1) % len(options)
                if e.key == pygame.K_DOWN: idx = (idx+1) % len(options)
                if e.key == pygame.K_RETURN:
                    difficulty = options[idx]
                    return

# ---------------- GAME: RUSSIAN ROULETTE ---------------- #
# Cost scales with difficulty; survive reward = score bonus; lose penalty scales.

def russian_roulette():
    global credits, score
    params = get_diff_params()
    running = True
    chambers = 6
    bullet_index = random.randint(0, chambers-1)
    current_index = 0
    result_text = "SPACE: spin & shoot  |  ESC: exit"
    base_cost = 50
    play_cost = int(base_cost * params["cost_mult"])
    lose_penalty = int(25 * params["risk_penalty_mult"])

    def draw_cylinder(center):
        pygame.draw.circle(WINDOW, GRAY, center, 120)
        pygame.draw.circle(WINDOW, (80,80,80), center, 90)
        for i in range(chambers):
            angle_deg = i * (360 / chambers)
            offset = pygame.math.Vector2(0, -60).rotate(angle_deg)
            hole_center = (center[0] + offset.x, center[1] + offset.y)
            pygame.draw.circle(WINDOW, (0,0,0), (int(hole_center[0]), int(hole_center[1])), 18)
            if i == bullet_index:
                pygame.draw.circle(WINDOW, (230,230,0), (int(hole_center[0]), int(hole_center[1])), 6)
        pointer = pygame.math.Vector2(0, -90).rotate(current_index * (360 / chambers))
        pygame.draw.line(WINDOW, YELLOW, center, (center[0]+pointer.x, center[1]+pointer.y), 6)

    while running:
        clock.tick(60)
        WINDOW.fill((20,20,20))
        draw_hud(f"Cost: {play_cost}")
        title = font.render("Russian Roulette", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        draw_cylinder((WIDTH//2, HEIGHT//2))
        msg = font_small.render(result_text, True, WHITE)
        WINDOW.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 + 160))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_SPACE:
                    if credits < play_cost:
                        result_text = "Not enough credits!"
                        continue
                    add_credits(-play_cost)
                    spin_frames = random.randint(30, 90)
                    for _ in range(spin_frames):
                        current_index = (current_index + 1) % chambers
                        WINDOW.fill((20,20,20))
                        draw_hud(f"Cost: {play_cost}")
                        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
                        draw_cylinder((WIDTH//2, HEIGHT//2))
                        pygame.display.flip()
                        clock.tick(60)
                    if current_index == bullet_index:
                        result_text = "BANG! You lose. SPACE to respin."
                        add_credits(-lose_penalty)
                        bullet_index = random.randint(0, chambers-1)
                    else:
                        reward_score = int(100 * params["payout_mult"])
                        result_text = f"Click... Survived! +{reward_score} score. SPACE to play again."
                        add_score(reward_score)

# ---------------- GAME: BLACK JOKER ---------------- #
# Draw cost scales; 1-in-8 Joker; streak milestones grant score scaled by difficulty.

def black_joker():
    global credits, score
    params = get_diff_params()
    running = True
    deck_ranks = ["A","K","Q","J","10","9","8","7"]
    suits = ["♠","♥","♦","♣"]
    msg = "SPACE: draw  |  ESC: exit"
    last_card = None
    base_cost = 20
    draw_cost = int(base_cost * params["cost_mult"])
    streak = 0

    while running:
        clock.tick(60)
        WINDOW.fill((0,100,0))
        draw_hud(f"Cost: {draw_cost} per draw | Streak: {streak}")
        title = font.render("Black Joker", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        draw_button(WINDOW, pygame.Rect(WIDTH//2-60, 240, 120, 180), "Draw")

        if last_card:
            rect = pygame.Rect(WIDTH//2-180, 520, 120, 180)
            rank, suit = last_card
            color = (220,0,0) if rank == "Joker" else (255,255,255)
            draw_card(WINDOW, rect, rank if rank != "Joker" else "J", suit if rank != "Joker" else "🃏", color)

        hint = font_small.render(msg, True, WHITE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, 750))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_SPACE:
                    if credits < draw_cost:
                        msg = "Not enough credits."
                        continue
                    add_credits(-draw_cost)
                    if random.randint(1,8) == 1:
                        last_card = ("Joker", "🃏")
                        msg = "BLACK JOKER! You lose. Streak reset. SPACE to draw."
                        streak = 0
                    else:
                        last_card = (random.choice(deck_ranks), random.choice(suits))
                        streak += 1
                        if streak % 5 == 0:
                            bonus = int(50 * params["payout_mult"])
                            add_score(bonus)
                            msg = f"Nice! {streak} draws survived. +{bonus} score. SPACE to draw."

# ---------------- GAME: SLOTS ---------------- #
# Spin costs bet; payout multiplier scales with difficulty; +score for 3-of-a-kind.

def slots():
    global credits, score, bet
    params = get_diff_params()
    running = True
    reels = [["cherry","star","seven","cherry","star","seven"],
             ["star","seven","cherry","star","seven","cherry"],
             ["seven","cherry","star","seven","cherry","star"]]
    positions = [0,0,0]
    spinning = [False, False, False]
    spin_timer = [0,0,0]

    def draw_symbol(sym, x, y):
        if sym == "cherry": draw_cherry(WINDOW, x, y)
        elif sym == "star": draw_star(WINDOW, x, y, 20)
        elif sym == "seven": draw_seven(WINDOW, x, y)

    while running:
        clock.tick(60)
        WINDOW.fill((30,30,30))
        draw_hud("SPACE: Spin | +/-: Change bet | ESC: Exit")
        title = font.render("Slots", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        frame = pygame.Rect(160, 260, 480, 260)
        pygame.draw.rect(WINDOW, (180,180,180), frame, border_radius=12)
        window_rect = pygame.Rect(180, 280, 440, 220)
        pygame.draw.rect(WINDOW, (40,40,40), window_rect, border_radius=12)

        for i in range(3):
            if spinning[i]:
                spin_timer[i] -= 1
                if spin_timer[i] <= 0:
                    spinning[i] = False
                else:
                    positions[i] = (positions[i] + 1) % len(reels[i])

        for i in range(3):
            sym = reels[i][positions[i]]
            cx = 240 + i*150
            cy = 390
            draw_symbol(sym, cx, cy)

        draw_button(WINDOW, pygame.Rect(320, 560, 160, 50), "SPACE to Spin")
        hint = font_small.render("ESC to exit", True, WHITE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, 630))

        if not any(spinning) and reels[0][positions[0]] == reels[1][positions[1]] == reels[2][positions[2]]:
            win_txt = font.render("WIN!", True, YELLOW)
            WINDOW.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 220))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    bet = min(200, bet + 5)
                if e.key == pygame.K_MINUS:
                    bet = max(5, bet - 5)
                if e.key == pygame.K_SPACE and not any(spinning):
                    if credits < bet:
                        continue
                    add_credits(-bet)
                    spinning = [True, True, True]
                    spin_timer = [
                        random.randint(30, 60),
                        random.randint(50, 90),
                        random.randint(70, 120)
                    ]
        # Award when all stop
        if not any(spinning):
            if reels[0][positions[0]] == reels[1][positions[1]] == reels[2][positions[2]]:
                payout_mult = params["slots_payout_mult"]
                win = bet * payout_mult
                add_credits(win)
                add_score(int(100 * params["payout_mult"]))

# ---------------- GAME: POKER ---------------- #
# 5-card deal cost scales; payouts scale by difficulty; score proportional to payout.

def evaluate_hand(hand):
    ranks_order = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    counts = {}
    suits = {}
    for r, s in hand:
        counts[r] = counts.get(r, 0) + 1
        suits[s] = suits.get(s, 0) + 1
    values = sorted([ranks_order.index(r) for r, _ in hand])
    is_flush = max(suits.values()) == 5
    is_straight = all(values[i]+1 == values[i+1] for i in range(4))
    kind = sorted(counts.values(), reverse=True)
    if is_straight and is_flush: return ("Straight Flush", 200)
    if 4 in kind: return ("Four of a Kind", 100)
    if 3 in kind and 2 in kind: return ("Full House", 60)
    if is_flush: return ("Flush", 40)
    if is_straight: return ("Straight", 30)
    if 3 in kind: return ("Three of a Kind", 20)
    if kind.count(2) == 2: return ("Two Pair", 15)
    if 2 in kind: return ("One Pair", 10)
    return ("High Card", 0)

def poker():
    global credits, score
    params = get_diff_params()
    ranks = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
    suits = ["♠","♥","♦","♣"]
    running = True
    hand = []
    result = ""
    base_cost = 25
    play_cost = int(base_cost * params["cost_mult"])
    table_rect = pygame.Rect(60, 300, WIDTH-120, 260)

    while running:
        clock.tick(60)
        WINDOW.fill((5,80,5))
        draw_hud(f"Cost: {play_cost} | SPACE: Deal | ESC: Exit")
        title = font.render("Poker (5-Card Deal)", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        pygame.draw.ellipse(WINDOW, (0,120,0), table_rect)
        pygame.draw.ellipse(WINDOW, (10,160,10), table_rect.inflate(-30,-30), 6)

        for i, (r, s) in enumerate(hand):
            rect = pygame.Rect(120 + i*130, 330, 100, 150)
            draw_card(WINDOW, rect, r, s)

        if result:
            res = font.render(result, True, YELLOW)
            WINDOW.blit(res, (WIDTH//2 - res.get_width()//2, 260))

        draw_button(WINDOW, pygame.Rect(WIDTH//2-80, 600, 160, 50), "SPACE to Deal")
        hint = font_small.render("ESC to return", True, WHITE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, 660))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_SPACE:
                    if credits < play_cost:
                        result = "Not enough credits."
                        continue
                    add_credits(-play_cost)
                    hand = [(random.choice(ranks), random.choice(suits)) for _ in range(5)]
                    name, payout = evaluate_hand(hand)
                    scaled_payout = int(payout * params["payout_mult"])
                    if scaled_payout > 0:
                        add_credits(scaled_payout)
                        add_score(scaled_payout * 2)
                    result = f"{name}  |  Payout: {scaled_payout}"

# ---------------- GAME: PLINKO ---------------- #
# Drop cost scales; bin multipliers shuffled; ball deflects with random angles; trail effect.

def plinko():
    global credits, score
    params = get_diff_params()
    running = True
    pegs = []
    rows = 6
    cols = 8
    spacing_x = WIDTH // (cols + 2)
    spacing_y = 80
    start_y = 220

    for r in range(rows):
        for c in range(cols):
            offset = spacing_x//2 if r % 2 == 1 else 0
            x = spacing_x + c*spacing_x + offset
            y = start_y + r*spacing_y
            pegs.append((x, y))

    ball_x, ball_y = WIDTH//2, 160
    ball_vx, ball_vy = 0, int(5 * params["speed_mult"])
    ball_radius = 10
    bins = [pygame.Rect(i*(WIDTH//8), HEIGHT-120, WIDTH//8, 100) for i in range(8)]
    multipliers = [0, 2, 5, 1, 10, 1, 5, 2]
    random.shuffle(multipliers)
    landed = None
    base_cost = 5
    drop_cost = int(base_cost * params["cost_mult"])
    trail = []

    while running:
        clock.tick(60)
        WINDOW.fill((25,25,25))
        draw_hud(f"Cost: {drop_cost} | SPACE: Drop | ESC: Exit")
        title = font.render("Plinko", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        pygame.draw.rect(WINDOW, (180,180,180), (60, 160, WIDTH-120, HEIGHT-240), 5, border_radius=12)

        for (x, y) in pegs:
            pygame.draw.circle(WINDOW, (220,220,220), (x, y), 6)

        for i, b in enumerate(bins):
            pygame.draw.rect(WINDOW, (40,40,40), b)
            pygame.draw.rect(WINDOW, (160,160,160), b, 2)
            label = font_small.render(f"x{multipliers[i]}", True, WHITE)
            WINDOW.blit(label, (b.centerx - label.get_width()//2, b.y + 8))

        if landed is None:
            ball_x += ball_vx
            ball_y += ball_vy

            for (x, y) in pegs:
                dx, dy = ball_x - x, ball_y - y
                dist2 = dx*dx + dy*dy
                if dist2 < (ball_radius + 6)**2:
                    angle = random.uniform(-30, 30)
                    vec = pygame.math.Vector2(ball_vx, ball_vy).rotate(angle)
                    ball_vx, ball_vy = vec.x, vec.y
                    break

            if ball_y > HEIGHT-140:
                for i, b in enumerate(bins):
                    if b.collidepoint(ball_x, ball_y):
                        landed = i
                        break

            trail.append((int(ball_x), int(ball_y)))
            if len(trail) > 20:
                trail.pop(0)

        for i, (tx, ty) in enumerate(trail):
            pygame.draw.circle(WINDOW, (240,60,60), (tx, ty), 4)

        pygame.draw.circle(WINDOW, (240,60,60), (int(ball_x), int(ball_y)), ball_radius)

        draw_button(WINDOW, pygame.Rect(WIDTH//2-90, HEIGHT-170, 180, 40), "SPACE to Drop Again")
        hint = font_small.render("ESC to return", True, WHITE)
        WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-120))

        if landed is not None:
            payout = multipliers[landed] * drop_cost
            payout = int(payout * params["payout_mult"])
            win_txt = font.render(f"Landed x{multipliers[landed]}  |  Win: {payout}", True, YELLOW)
            WINDOW.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 220))
            add_credits(payout)
            add_score(payout)
            landed = None
            ball_x, ball_y = WIDTH//2, 160
            ball_vx, ball_vy = 0, int(5 * params["speed_mult"])
            trail.clear()

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_SPACE:
                    if credits < drop_cost:
                        continue
                    add_credits(-drop_cost)
                    ball_x, ball_y = WIDTH//2, 160
                    ball_vx, ball_vy = 0, int(5 * params["speed_mult"])
                    landed = None
                    trail.clear()

# ---------------- GAME: FISHING FRENZY ---------------- #
# Fish count and movement scale with difficulty; catch rewards scale; no penalty.

def fishing_frenzy():
    global credits, score
    params = get_diff_params()
    running = True
    boat_x = WIDTH//2 - 50
    hook = None
    fish_count = 8 if difficulty == "Easy" else (8 if difficulty == "Normal" else 10)
    fish = [pygame.Rect(random.randint(40, WIDTH-140), random.randint(280, HEIGHT-120), 50, 24) for _ in range(fish_count)]
    fish_dir = [random.choice([-2, 2]) for _ in fish]

    def draw_ocean():
        WINDOW.fill((20,120,220))
        pygame.draw.rect(WINDOW, (135,206,235), (0,0, WIDTH,180))
        pygame.draw.rect(WINDOW, (20,120,220), (0,180, WIDTH, HEIGHT-180))
        for i in range(10):
            pygame.draw.arc(WINDOW, (180,220,255), (i*80, 210, 120, 60), 0, 3.14, 2)

    def draw_boat(x):
        pygame.draw.rect(WINDOW, (139,69,19), (x, 160, 120, 30))
        pygame.draw.polygon(WINDOW, (160,82,45), [(x,190), (x+120,190), (x+100,210), (x+20,210)])
        pygame.draw.polygon(WINDOW, WHITE, [(x+60, 160), (x+60, 110), (x+100, 160)])

    def draw_fish_rect(rect):
        pygame.draw.ellipse(WINDOW, (20,200,120), rect)
        tail = [(rect.right, rect.centery), (rect.right+14, rect.centery-8), (rect.right+14, rect.centery+8)]
        pygame.draw.polygon(WINDOW, (20,200,120), tail)
        pygame.draw.circle(WINDOW, BLACK, (rect.x+8, rect.y+8), 3)

    catch_credit = int(10 * params["payout_mult"])
    catch_score  = int(20 * params["payout_mult"])

    while running:
        clock.tick(60)
        draw_ocean()
        draw_hud("Arrow keys: Move | SPACE: Hook | ESC: Exit")
        title = font.render("Fishing Frenzy", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        draw_boat(boat_x)

        if hook:
            pygame.draw.line(WINDOW, (240,240,240), (boat_x+60, 160), (hook.x, hook.y), 3)

        for i, f in enumerate(fish):
            f.x += int(fish_dir[i] * params["speed_mult"])
            f.y += int(2 * math_sine(i, f.x))
            if f.x < 30 or f.x > WIDTH-150:
                fish_dir[i] *= -1
            draw_fish_rect(f)

        if hook:
            hook.y += int(6 * params["speed_mult"])
            for f in fish[:]:
                if hook.colliderect(f):
                    idx = fish.index(f)
                    fish.remove(f)
                    fish_dir.pop(idx)
                    hook = None
                    add_credits(catch_credit)
                    add_score(catch_score)
                    break
            if hook and hook.y > HEIGHT-60:
                hook = None

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                if e.key == pygame.K_LEFT: boat_x -= 20
                if e.key == pygame.K_RIGHT: boat_x += 20
                if e.key == pygame.K_SPACE and not hook:
                    hook = pygame.Rect(boat_x+60, 160, 6, 6)

# ---------------- GAME: CROSSY ROAD ---------------- #
# Car speeds and penalties scale with difficulty; lane score adds credits on thresholds.

def crossy_road():
    global credits, score
    params = get_diff_params()
    player = pygame.Rect(WIDTH//2, HEIGHT-70, 30,30)
    lanes = [260, 340, 420, 500, 580, 660, 740]
    cars = [pygame.Rect(random.randint(-200, WIDTH), y, 80, 30) for y in lanes]
    base_speeds = [random.choice([4,5,6]) for _ in cars]
    speeds = [int(s * params["speed_mult"]) * random.choice([-1,1]) for s in base_speeds]
    running = True
    lane_score_tick = 0
    crash_penalty = int(20 * params["risk_penalty_mult"])

    while running:
        clock.tick(60)
        WINDOW.fill((60,200,60))
        draw_hud("Arrows: Move | ESC: Exit")
        pygame.draw.rect(WINDOW, (80,80,80), (0, 240, WIDTH, 560))
        for i in range(6):
            pygame.draw.rect(WINDOW, (255,255,255), (0, 280 + i*80, WIDTH, 6))
        title = font.render("Crossy Road", True, WHITE)
        WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        pygame.draw.rect(WINDOW, (255,255,0), player)
        pygame.draw.circle(WINDOW, (0,0,0), (player.centerx-5, player.centery-6), 3)
        pygame.draw.circle(WINDOW, (0,0,0), (player.centerx+5, player.centery-6), 3)
        pygame.draw.polygon(WINDOW, (255,120,0), [(player.centerx, player.y), (player.centerx+8, player.y+8), (player.centerx-8, player.y+8)])

        for i, c in enumerate(cars):
            pygame.draw.rect(WINDOW, (200,0,0) if speeds[i]>0 else (0,120,240), c, border_radius=6)
            pygame.draw.circle(WINDOW, (20,20,20), (c.x+16, c.y+26), 8)
            pygame.draw.circle(WINDOW, (20,20,20), (c.x+64, c.y+26), 8)
            c.x += speeds[i]
            if c.x < -120: c.x = WIDTH + 20
            if c.x > WIDTH + 20: c.x = -120
            if player.colliderect(c):
                add_credits(-crash_penalty)
                return

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return
                prev_y = player.y
                if e.key == pygame.K_UP:
                    player.y -= 40
                if e.key == pygame.K_DOWN:
                    player.y += 40
                if e.key == pygame.K_LEFT: player.x -= 40
                if e.key == pygame.K_RIGHT: player.x += 40
                if player.y < prev_y:
                    add_score(5)
                    lane_score_tick += 5
                    if lane_score_tick >= 10:
                        add_credits(get_diff_params()["reward_lane_credit"])
                        lane_score_tick = 0

# ---------------- MENU ---------------- #

def draw_menu():
    WINDOW.fill((15,15,20))
    for i in range(120):
        pygame.draw.rect(WINDOW, (15+i,15+i,40+i//3), (0, i, WIDTH, 1))
    title = font.render("Kings of Kiro's Casino", True, WHITE)
    WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    bar = font_small.render(f"Credits: {credits}   Score: {score}   Bet: {bet}   Diff: {difficulty}", True, WHITE)
    WINDOW.blit(bar, (WIDTH//2 - bar.get_width()//2, 150))

    for i, option in enumerate(menu_options):
        color = BLUE if i == selected else WHITE
        text = font.render(option, True, color)
        WINDOW.blit(text, (WIDTH//2 - text.get_width()//2, 220 + i*60))

    hint = font_small.render("Use +/- in Slots to change bet.", True, WHITE)
    WINDOW.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
    pygame.display.update()

def main_menu():
    global selected, credits, score
    running = True
    while running:
        clock.tick(60)
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    choice = menu_options[selected]
                    if choice == "Quit":
                        running = False
                    elif choice == "Instructions":
                        instructions()
                    elif choice == "Difficulty":
                        difficulty_menu()
                    elif choice == "Russian Roulette":
                        russian_roulette()
                    elif choice == "Black Joker":
                        black_joker()
                    elif choice == "Slots":
                        slots()
                    elif choice == "Poker":
                        poker()
                    elif choice == "Plinko":
                        plinko()
                    elif choice == "Fishing Frenzy":
                        fishing_frenzy()
                    elif choice == "Crossy Road":
                        crossy_road()

    # Cash out score into credits before quitting
    credits += score
    score = 0

    # Cashout screen
    WINDOW.fill((0,0,0))
    msg = font.render(f"Final Cashout: {credits} credits", True, WHITE)
    WINDOW.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

main_menu()
