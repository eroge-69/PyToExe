# breakout.py — Breakout (Pygame) FULLSCREEN + téglalap blokkok + biztonságos alsó zóna + sebesség nehézségtől
# Bónuszok: Multiball (piros), Háló (cián), Tűzfal (narancs: alul+oldalt, 5s, érintésre 20×)

import random
import math
import pygame as pg

# ------- Globál alapok (W,H később fullscreen után frissül) -------
W, H = 960, 720
BG = (18, 20, 26)
HUD = (235, 240, 245)

# Ütő/Paddle (paddle Y-t mindig H alapján számoljuk)
PADDLE_W, PADDLE_H = 160, 18
PADDLE_SPEED_LIMIT = 2200  # px/s

def get_paddle_y() -> int:
    return H - 60

# Labda sebesség (alap), nehézségi szint ezt szorozza
BALL_SPEED_BASE = 560.0
BALL_SPEED_MIN_BASE = 420.0
BALL_SPEED_MAX_BASE = 780.0

# Blokk zóna és margók
LEFT_MARGIN = 40
RIGHT_MARGIN = 40
TOP_Y = 100
SAFE_GAP = 200  # biztonsági távolság az ütő és a blokkok alja között

# Bónuszok (súlyok: [multiball, net, fire])
BONUS_KIND_WEIGHTS_DEFAULT = [0.5, 0.3, 0.2]
BONUS_SPEED = 220.0
BONUS_W, BONUS_H = 24, 14
BONUS_COLOR_MULTIBALL = (220, 50, 60)    # piros
BONUS_COLOR_NET = (60, 200, 255)         # cián
BONUS_COLOR_FIRE = (255, 140, 40)        # narancs

# Háló (alsó védőrács)
NET_HEIGHT = 18
NET_MARGIN = 8
NET_COLOR = (60, 200, 255)
NET_LINE_ALPHA = 110
NET_DURATION = 10.0

# Tűzfal (alul + oldalt)
FIRE_HEIGHT = 14
FIRE_MARGIN = 6
FIRE_SIDE_WIDTH = 14
FIRE_SIDE_MARGIN = 6
FIRE_COLOR = (255, 120, 40)
FIRE_DURATION = 5.0
FIRE_MULT = 20.0
FIRE_BG_ALPHA = 70
FIRE_LINE_ALPHA = 150

LIVES_START = 3

# --------- Nehézségi profilok ---------
# target = megcélzott blokkszám, cols/rows = rács felbontás
# speed_mult = labdasebesség szorzó (könnyű lassabb, hard gyorsabb)
DIFFICULTIES = {
    "könnyű": {
        "target": 100,
        "cols": 14, "rows": 8,
        "bonus_drop_chance": 0.36,
        "speed_mult": 0.85,
    },
    "közepes": {
        "target": 200,
        "cols": 20, "rows": 12,
        "bonus_drop_chance": 0.18,
        "speed_mult": 1.00,
    },
    "rohadjál meg": {
        "target": 1000,
        "cols": 40, "rows": 30,
        "bonus_drop_chance": 0.09,
        "speed_mult": 1.25,
    },
}

def clamp(x, a, b): return a if x < a else b if x > b else x

# ---------------- pályagenerálás (téglalapok + biztonságos alsó sáv) ----------------
def make_level(cols, rows, target):
    bricks = []
    total_width = W - LEFT_MARGIN - RIGHT_MARGIN
    paddle_y = get_paddle_y()
    bottom_play_y = paddle_y - SAFE_GAP                   # a blokkrács alja nem mehet ez alá
    total_height = max(120, bottom_play_y - TOP_Y)

    # téglalap: legyen a cella magasabb szélben, alacsonyabb magasságban (cell_h < cell_w)
    cell_w = max(20, total_width // cols)
    cell_h = max(12, min(total_height // rows, int(cell_w * 0.55)))  # téglalap, nem kocka

    # ha így túl magas lenne, csökkentjük az effektív sorok számát
    rows_effective = max(1, min(rows, total_height // cell_h))
    max_cells = cols * rows_effective

    # minden cella téglalap (kicsi belső margó a vizuál miatt)
    cells = []
    for r in range(rows_effective):
        for c in range(cols):
            x = LEFT_MARGIN + c * cell_w
            y = TOP_Y + r * cell_h
            rect = pg.Rect(x+3, y+3, max(6, cell_w-6), max(8, cell_h-6))
            cells.append(rect)

    target = min(target, max_cells)
    chosen_idx = set(random.sample(range(len(cells)), target))
    for i, rect in enumerate(cells):
        if i in chosen_idx:
            # zöld/sárga/piros (1/2/3 HP) súlyozva
            color, hp = random.choices(
                [((40,200,90),1), ((245,200,40),2), ((220,50,60),3)],
                weights=[0.35, 0.35, 0.30], k=1
            )[0]
            bricks.append({"rect": rect, "hp": hp, "color": color})
    return bricks

def new_ball(x, y, vx, vy, primary=False, color=(240,240,255)):
    return {
        "x": float(x), "y": float(y),
        "vx": float(vx), "vy": float(vy),
        "primary": primary, "color": color,
        "boost_timer": 0.0  # tűzfal boost ideje (ha >0)
    }

# -------------- játék állapot --------------
def reset_ball_and_paddle(state):
    paddle_y = get_paddle_y()
    state["paddle_x"] = W // 2 - PADDLE_W // 2
    bx = state["paddle_x"] + PADDLE_W // 2
    by = paddle_y - 10 - 1
    angle = random.uniform(math.radians(25), math.radians(155))
    v = BALL_SPEED_BASE * state["speed_mult"]
    vx = math.cos(angle) * v
    vy = -abs(math.sin(angle)) * v
    state["balls"] = [new_ball(bx, by, vx, vy, primary=True, color=(240,240,255))]

def new_game(diff_name):
    d = DIFFICULTIES[diff_name]
    st = {
        "difficulty": diff_name,
        "paddle_x": W//2 - PADDLE_W//2,
        "bricks": make_level(d["cols"], d["rows"], d["target"]),
        "bonus_drop_chance": d["bonus_drop_chance"],
        "bonus_kind_weights": BONUS_KIND_WEIGHTS_DEFAULT[:],
        "speed_mult": d["speed_mult"],
        "lives": LIVES_START,
        "score": 0,
        "won": False,
        "lost": False,
        "balls": [],
        "bonuses": [],      # {rect, vy, kind}
        "net_timer": 0.0,   # háló ideje
        "fire_timer": 0.0,  # tűzfal ideje
    }
    reset_ball_and_paddle(st)
    return st

# -------------- rajzolás --------------
def draw_game(state, screen, font, bigfont):
    screen.fill(BG)

    # blokkok (téglalapok)
    for b in state["bricks"]:
        col = b["color"]; hp = b["hp"]
        shade = 40 * (hp-1)
        c = (min(col[0]+shade,255), min(col[1]+shade,255), min(col[2]+shade,255))
        pg.draw.rect(screen, c, b["rect"], border_radius=5)
        pg.draw.rect(screen, (255,255,255), b["rect"], width=1, border_radius=5)

    # bónusz kapszulák
    for bonus in state["bonuses"]:
        r = bonus["rect"]
        col = BONUS_COLOR_MULTIBALL if bonus["kind"]=="multiball" else (BONUS_COLOR_NET if bonus["kind"]=="net" else BONUS_COLOR_FIRE)
        pg.draw.rect(screen, col, r, border_radius=r.h//2)
        pg.draw.rect(screen, (255,255,255), r, width=2, border_radius=r.h//2)
        cx, cy = r.center
        if bonus["kind"] == "multiball":
            for i in (-1,0,1): pg.draw.line(screen, (255,255,255), (cx+i*5, cy-3), (cx+i*5, cy+3), 2)
        elif bonus["kind"] == "net":
            for i in (-6,0,6):
                pg.draw.line(screen, (255,255,255), (cx-8, cy+i), (cx+8, cy+i), 1)
                pg.draw.line(screen, (255,255,255), (cx+i, cy-8), (cx+i, cy+8), 1)
        else:
            pg.draw.polygon(screen, (255,255,255), [(cx, cy-5), (cx-6, cy+5), (cx+6, cy+5)], 1)

    # védőháló (alul)
    if state["net_timer"] > 0.0:
        net_top = H - NET_MARGIN - NET_HEIGHT
        net_bg = pg.Surface((W, NET_HEIGHT), pg.SRCALPHA); net_bg.fill((*NET_COLOR, 45))
        screen.blit(net_bg, (0, net_top))
        line = pg.Surface((1, NET_HEIGHT), pg.SRCALPHA); line.fill((*NET_COLOR, NET_LINE_ALPHA))
        for x in range(0, W, 16): screen.blit(line, (x, net_top))
        row = pg.Surface((W, 1), pg.SRCALPHA); row.fill((*NET_COLOR, NET_LINE_ALPHA))
        for y in range(net_top, net_top+NET_HEIGHT, 8): screen.blit(row, (0, y))

    # tűzfal (ALUL + OLDALT)
    if state["fire_timer"] > 0.0:
        fire_top = H - FIRE_MARGIN - FIRE_HEIGHT
        fire_bg = pg.Surface((W, FIRE_HEIGHT), pg.SRCALPHA); fire_bg.fill((*FIRE_COLOR, FIRE_BG_ALPHA))
        screen.blit(fire_bg, (0, fire_top))
        for x in range(0, W, 12):
            h = FIRE_HEIGHT // 2 + int(4*math.sin(pg.time.get_ticks()*0.01 + x*0.2))
            pg.draw.line(screen, (255,200,80, FIRE_LINE_ALPHA),
                         (x, fire_top + FIRE_HEIGHT), (x, fire_top + FIRE_HEIGHT - h), 2)
        # bal sáv
        left_x = FIRE_SIDE_MARGIN
        left_bg = pg.Surface((FIRE_SIDE_WIDTH, H), pg.SRCALPHA); left_bg.fill((*FIRE_COLOR, FIRE_BG_ALPHA))
        screen.blit(left_bg, (left_x, 0))
        for y in range(0, H, 12):
            w = FIRE_SIDE_WIDTH // 2 + int(4*math.cos(pg.time.get_ticks()*0.01 + y*0.2))
            pg.draw.line(screen, (255,200,80, FIRE_LINE_ALPHA),
                         (left_x, y), (left_x + w, y), 2)
        # jobb sáv
        right_x = W - FIRE_SIDE_MARGIN - FIRE_SIDE_WIDTH
        right_bg = pg.Surface((FIRE_SIDE_WIDTH, H), pg.SRCALPHA); right_bg.fill((*FIRE_COLOR, FIRE_BG_ALPHA))
        screen.blit(right_bg, (right_x, 0))
        for y in range(0, H, 12):
            w = FIRE_SIDE_WIDTH // 2 + int(4*math.cos(pg.time.get_ticks()*0.01 + y*0.2))
            pg.draw.line(screen, (255,200,80, FIRE_LINE_ALPHA),
                         (right_x + FIRE_SIDE_WIDTH - w, y), (right_x + FIRE_SIDE_WIDTH, y), 2)

    # ütő
    paddle_y = get_paddle_y()
    paddle = pg.Rect(int(state["paddle_x"]), paddle_y, PADDLE_W, PADDLE_H)
    pg.draw.rect(screen, (180, 195, 230), paddle, border_radius=10)
    pg.draw.rect(screen, (255,255,255), paddle, width=2, border_radius=10)

    # labdák
    for ball in state["balls"]:
        pg.draw.circle(screen, ball["color"], (int(ball["x"]), int(ball["y"])), 10)
        pg.draw.circle(screen, (255,255,255), (int(ball["x"]), int(ball["y"])), 10, 2)

    # HUD
    hud = f"[{state['difficulty']}]  Pont: {state['score']}   Életek: {state['lives']}   Blokkok: {len(state['bricks'])}"
    if state["net_timer"] > 0.0:  hud += f"   Háló: {state['net_timer']:.1f}s"
    if state["fire_timer"] > 0.0: hud += f"   Tűzfal: {state['fire_timer']:.1f}s"
    surf = font.render(hud, True, HUD)
    screen.blit(surf, (16, 16))

    if state["won"]:
        t = bigfont.render("GYŐZELEM! (R = új játék, M = menü)", True, (120, 255, 150))
        screen.blit(t, (W//2 - t.get_width()//2, H//2 - 24))
    elif state["lost"]:
        t = bigfont.render("VESZTETTÉL! (R = új játék, M = menü)", True, (255, 120, 120))
        screen.blit(t, (W//2 - t.get_width()//2, H//2 - 24))

def draw_menu(screen, title_font, font, hovered=None):
    screen.fill(BG)
    title = title_font.render("BREAKOUT", True, (255,255,255))
    screen.blit(title, (W//2 - title.get_width()//2, 120))

    items = [
        ("1) Könnyű – 100 téglalap, sok bónusz (lassabb labda)", "könnyű"),
        ("2) Közepes – 200 téglalap, fele bónusz", "közepes"),
        ("3) Rohadjál meg – 1000 téglalap, negyed bónusz (gyorsabb labda)", "rohadjál meg"),
    ]
    buttons = []
    y = 260
    for text, key in items:
        surf = font.render(text, True, (240,240,240))
        rect = pg.Rect(W//2 - 480, y, 960, 60)
        color = (60, 70, 90) if hovered == key else (40, 45, 60)
        pg.draw.rect(screen, color, rect, border_radius=12)
        pg.draw.rect(screen, (255,255,255), rect, width=2, border_radius=12)
        screen.blit(surf, (rect.x + 20, rect.y + 16))
        buttons.append((rect, key))
        y += 90

    tip = font.render("Válassz: kattints vagy nyomd meg 1 / 2 / 3  •  Esc: kilép", True, (220,220,230))
    screen.blit(tip, (W//2 - tip.get_width()//2, y + 20))
    return buttons

# -------------- ütközések --------------
def reflect_on_rect(ball_x, ball_y, vx, vy, rect):
    nearest_x = max(rect.left, min(ball_x, rect.right))
    nearest_y = max(rect.top,  min(ball_y, rect.bottom))
    dx = ball_x - nearest_x
    dy = ball_y - nearest_y
    if dx*dx + dy*dy > 10*10:
        return False, vx, vy
    overlap_left   = abs((ball_x + 10) - rect.left)
    overlap_right  = abs(rect.right  - (ball_x - 10))
    overlap_top    = abs((ball_y + 10) - rect.top)
    overlap_bottom = abs(rect.bottom - (ball_y - 10))
    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
    if min_overlap in (overlap_left, overlap_right): vx = -vx
    else: vy = -vy
    return True, vx, vy

def spawn_bonus_at(rect, state):
    kind = random.choices(["multiball", "net", "fire"], weights=state["bonus_kind_weights"], k=1)[0]
    x, y = rect.centerx - BONUS_W//2, rect.centery - BONUS_H//2
    state["bonuses"].append({"rect": pg.Rect(x, y, BONUS_W, BONUS_H),
                             "vy": BONUS_SPEED, "kind": kind})

def apply_multiball(state, paddle_rect):
    cx = paddle_rect.centerx
    cy = paddle_rect.top - 12
    angles = [math.radians(a) for a in (75, 90, 105)]
    speed = BALL_SPEED_BASE * 0.95 * state["speed_mult"]
    for ang in angles:
        vx = speed * math.cos(ang)
        vy = -abs(speed * math.sin(ang))
        state["balls"].append(new_ball(cx, cy, vx, vy, primary=False, color=(220,50,60)))

def activate_net(state):  state["net_timer"]  += NET_DURATION
def activate_fire(state): state["fire_timer"] += FIRE_DURATION

# -------------- játéklogika --------------
def step(state, dt):
    if state["won"] or state["lost"]:
        return

    # időzítők
    prev_fire = state["fire_timer"]
    if state["net_timer"]  > 0.0: state["net_timer"]  = max(0.0, state["net_timer"]  - dt)
    if state["fire_timer"] > 0.0: state["fire_timer"] = max(0.0, state["fire_timer"] - dt)
    fire_active = state["fire_timer"] > 0.0
    net_active  = state["net_timer"]  > 0.0
    net_top     = H - NET_MARGIN  - NET_HEIGHT
    fire_top    = H - FIRE_MARGIN - FIRE_HEIGHT
    left_band_r = FIRE_SIDE_MARGIN + FIRE_SIDE_WIDTH
    right_band_l= W - (FIRE_SIDE_MARGIN + FIRE_SIDE_WIDTH)

    # ha most járt le a tűzfal: vegyük le a boostot minden labdáról
    if prev_fire > 0 and state["fire_timer"] <= 0:
        for ball in state["balls"]:
            if ball["boost_timer"] > 0:
                ball["vx"] /= FIRE_MULT; ball["vy"] /= FIRE_MULT
                ball["boost_timer"] = 0.0

    # ütő egérkövetés
    mx, _ = pg.mouse.get_pos()
    target_x = mx - PADDLE_W // 2
    dx = target_x - state["paddle_x"]
    maxstep = PADDLE_SPEED_LIMIT * dt
    if abs(dx) > maxstep: dx = math.copysign(maxstep, dx)
    state["paddle_x"] = clamp(state["paddle_x"] + dx, 0, W - PADDLE_W)
    paddle_y = get_paddle_y()
    paddle = pg.Rect(int(state["paddle_x"]), paddle_y, PADDLE_W, PADDLE_H)

    # bónuszok frissítése (tűzfalnál pattannak)
    kept = []
    for bonus in state["bonuses"]:
        r = bonus["rect"]
        r.y += int(bonus["vy"] * dt)
        if r.colliderect(paddle):
            if bonus["kind"] == "multiball": apply_multiball(state, paddle)
            elif bonus["kind"] == "net":     activate_net(state)
            else:                             activate_fire(state)
        elif fire_active and r.bottom >= fire_top:
            r.bottom = fire_top; bonus["vy"] = -abs(bonus["vy"])
        elif r.top <= H:
            kept.append(bonus)
    state["bonuses"] = kept

    # labdák
    to_remove = []
    for i, ball in enumerate(state["balls"]):
        bx = ball["x"] + ball["vx"] * dt
        by = ball["y"] + ball["vy"] * dt

        # falak (felső + alap oldalsó)
        if bx - 10 < 0:
            bx = 10; ball["vx"] = abs(ball["vx"])
        if bx + 10 > W:
            bx = W - 10; ball["vx"] = -abs(ball["vx"])
        if by - 10 < 0:
            by = 10; ball["vy"] = abs(ball["vy"])

        # tűzfal OLDALSÓ sáv
        if fire_active:
            if bx - 10 <= left_band_r:
                bx = left_band_r + 10 + 1
                if ball["boost_timer"] <= 0:
                    ball["vx"] *= FIRE_MULT; ball["vy"] *= FIRE_MULT
                ball["boost_timer"] = max(ball["boost_timer"], state["fire_timer"])
                ball["vx"] = abs(ball["vx"])
            elif bx + 10 >= right_band_l:
                bx = right_band_l - 10 - 1
                if ball["boost_timer"] <= 0:
                    ball["vx"] *= FIRE_MULT; ball["vy"] *= FIRE_MULT
                ball["boost_timer"] = max(ball["boost_timer"], state["fire_timer"])
                ball["vx"] = -abs(ball["vx"])

        # ütő
        if ball["vy"] > 0:
            hit, vx, vy = reflect_on_rect(bx, by, ball["vx"], ball["vy"], paddle)
            if hit:
                # eltalált hely szerint állítható szög
                rel = ((bx - paddle.centerx) / (PADDLE_W/2))
                angle = math.radians(25 + 55 * max(-1, min(1, rel)))
                # sebességkorlát nehézség és boost alapján
                diff_mult = state["speed_mult"]
                boost_mult = FIRE_MULT if ball["boost_timer"] > 0 else 1.0
                sp_min = BALL_SPEED_MIN_BASE * diff_mult * boost_mult
                sp_max = BALL_SPEED_MAX_BASE * diff_mult * boost_mult
                speed = max(sp_min, min(sp_max, math.hypot(vx, vy)*1.02))
                vx = speed * math.sin(angle)
                vy = -abs(speed * math.cos(angle))
                ball["vx"], ball["vy"] = vx, vy
                bx = ball["x"]; by = paddle.top - 10 - 1

        # blokkok
        if state["bricks"]:
            new_list = []
            bounced = False
            destroyed_now = 0
            for b in state["bricks"]:
                if not bounced:
                    hit, vx, vy = reflect_on_rect(bx, by, ball["vx"], ball["vy"], b["rect"])
                    if hit:
                        ball["vx"], ball["vy"] = vx, vy
                        b["hp"] -= 1
                        if b["hp"] <= 0:
                            destroyed_now += 1
                            # pont: zöld 10, sárga 20, piros 30
                            if b["color"][1] > 180: state["score"] += 10
                            elif b["color"][0] > 200: state["score"] += 20
                            else: state["score"] += 30
                            if random.random() < state["bonus_drop_chance"]:
                                spawn_bonus_at(b["rect"], state)
                        else:
                            new_list.append(b)
                        bounced = True
                    else:
                        new_list.append(b)
                else:
                    new_list.append(b)
            state["bricks"] = new_list
            if destroyed_now and not state["bricks"]:
                state["won"] = True

        # tűzfal ALUL
        if state["fire_timer"] > 0.0 and ball["vy"] > 0 and by + 10 >= fire_top:
            by = fire_top - 10 - 1
            if ball["boost_timer"] <= 0:
                ball["vx"] *= FIRE_MULT; ball["vy"] *= FIRE_MULT
            ball["boost_timer"] = max(ball["boost_timer"], state["fire_timer"])
            ball["vy"] = -abs(ball["vy"])

        # háló (ha nincs tűzfal)
        if state["net_timer"] > 0.0 and ball["vy"] > 0 and by + 10 >= net_top and not (state["fire_timer"] > 0.0 and by + 10 >= fire_top):
            by = net_top - 10 - 1
            ball["vy"] = -abs(ball["vy"])
            diff_mult = state["speed_mult"]
            boost_mult = FIRE_MULT if ball["boost_timer"] > 0 else 1.0
            sp_min = BALL_SPEED_MIN_BASE * diff_mult * boost_mult
            sp_max = BALL_SPEED_MAX_BASE * diff_mult * boost_mult
            speed = min(sp_max, max(sp_min, math.hypot(ball["vx"], ball["vy"])*1.02))
            ang = math.atan2(-abs(ball["vy"]), ball["vx"])
            ball["vx"] = speed * math.cos(ang)
            ball["vy"] = -abs(speed * math.sin(ang))

        # boost időzítő
        if ball["boost_timer"] > 0.0:
            ball["boost_timer"] -= dt
            if ball["boost_timer"] <= 0.0:
                ball["vx"] /= FIRE_MULT; ball["vy"] /= FIRE_MULT
                ball["boost_timer"] = 0.0

        # alsó perem (ha nincs aktív védőelem)
        if by - 10 > H:
            if ball["primary"]:
                state["lives"] -= 1
                if state["lives"] <= 0:
                    state["lost"] = True
                    return
                else:
                    state["bonuses"].clear()
                    state["net_timer"] = 0.0
                    state["fire_timer"] = 0.0
                    reset_ball_and_paddle(state)
                    return
            else:
                to_remove.append(i)
        else:
            ball["x"], ball["y"] = bx, by

    # extra labdák törlése
    for idx in reversed(to_remove):
        if 0 <= idx < len(state["balls"]) and not state["balls"][idx]["primary"]:
            state["balls"].pop(idx)

# -------------- MAIN --------------
def main():
    global W, H
    pg.init()
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)  # FULLSCREEN
    pg.display.set_caption("Breakout – fullscreen + téglalap blokkok")
    W, H = screen.get_size()  # frissítjük a globális méretet a logikához
    clock = pg.time.Clock()
    font = pg.font.SysFont("consolas", 22)
    bigfont = pg.font.SysFont("consolas", 42, bold=True)
    title_font = pg.font.SysFont("consolas", 64, bold=True)

    mode = "menu"
    state = None

    running = True
    while running:
        dt = clock.tick(144) / 1000.0
        if dt > 0.03: dt = 0.03

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif mode == "menu":
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE: running = False
                    elif e.key == pg.K_1: state = new_game("könnyű"); mode = "play"
                    elif e.key == pg.K_2: state = new_game("közepes"); mode = "play"
                    elif e.key == pg.K_3: state = new_game("rohadjál meg"); mode = "play"
                elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = pg.mouse.get_pos()
                    buttons = draw_menu(screen, title_font, font)
                    for rect, key in buttons:
                        if rect.collidepoint(mx, my):
                            state = new_game(key); mode = "play"; break
            else:
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_ESCAPE: running = False
                    elif e.key == pg.K_r: state = new_game(state["difficulty"])
                    elif e.key == pg.K_m: mode = "menu"; state = None

        if mode == "menu":
            mx, my = pg.mouse.get_pos()
            hovered = None
            buttons = draw_menu(screen, title_font, font)
            for rect, key in buttons:
                if rect.collidepoint(mx, my):
                    hovered = key
            draw_menu(screen, title_font, font, hovered=hovered)
        else:
            step(state, dt)
            draw_game(state, screen, font, bigfont)

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()
