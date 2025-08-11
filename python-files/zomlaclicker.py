# zomla_clicker.py — ZOMLA CLICKER (bez bazy danych)
# - brak SQLite (stan w pliku JSON) / albo wyłącz zapis całkiem: SAVE_ENABLED=False
# - efekty cząsteczek, ładne UI, dźwięk w locie (toggle)
# Uruchom: pip install pygame  (jeśli już masz, nic nie pobierasz dodatkowo)

import os, sys, math, time, json, random
import pygame
from pygame import gfxdraw

# ---------- USTAWIENIA ----------
WIDTH, HEIGHT = 900, 600
FPS = 60
TITLE = "ZOMLA CLICKER"
SAVE_ENABLED = True
SAVE_PATH = "zomla_save.json"

# Kolory
COL_BG_TOP = (28, 31, 45)
COL_BG_BOTTOM = (16, 18, 28)
COL_CARD = (36, 40, 58)
COL_ACCENT = (120, 190, 255)
COL_ACCENT_2 = (255, 200, 60)
COL_TEXT = (230, 235, 245)
COL_TEXT_DIM = (180, 188, 205)
COL_SUCCESS = (110, 210, 110)
COL_DANGER = (235, 90, 90)
WHITE = (255, 255, 255)

pygame.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ---------- AUDIO W LOCIE ----------
SOUND_AVAILABLE = True
click_snd = None
try:
    pygame.mixer.pre_init(44100, -16, 1, 256)
    pygame.mixer.init()
    import array
    sr = 44100
    dur = 0.06
    n = int(sr * dur)
    buf = array.array("h")
    f0 = 660.0
    for i in range(n):
        t = i / sr
        amp = int(3000 * (1 - i/n) ** 1.8)
        buf.append(int(amp * math.sin(2*math.pi*f0*t)))
    click_snd = pygame.mixer.Sound(buffer=buf)
except Exception:
    SOUND_AVAILABLE = False
    click_snd = None

# ---------- CZCIONKI ----------
def font(size, bold=False):
    try:
        return pygame.font.SysFont("Inter", size, bold=bold)
    except:
        return pygame.font.SysFont("Arial", size, bold=bold)

FONT_H1 = font(42, True)
FONT_H2 = font(28, True)
FONT_UI = font(22)
FONT_SMALL = font(16)

# ---------- UI NARZĘDZIA ----------
def draw_gradient_bg(surf, top, bot):
    for y in range(HEIGHT):
        r = y / (HEIGHT - 1)
        c = (
            int(top[0]*(1-r) + bot[0]*r),
            int(top[1]*(1-r) + bot[1]*r),
            int(top[2]*(1-r) + bot[2]*r),
        )
        pygame.draw.line(surf, c, (0, y), (WIDTH, y))

def draw_round_rect(surf, rect, color, radius=18):
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x+radius, y, w-2*radius, h))
    pygame.draw.rect(surf, color, (x, y+radius, w, h-2*radius))
    pygame.draw.circle(surf, color, (x+radius, y+radius), radius)
    pygame.draw.circle(surf, color, (x+w-radius, y+radius), radius)
    pygame.draw.circle(surf, color, (x+radius, y+h-radius), radius)
    pygame.draw.circle(surf, color, (x+w-radius, y+h-radius), radius)

def draw_shadow(surf, rect, spread=6, alpha=120):
    x, y, w, h = rect
    sh = pygame.Surface((w + spread*2, h + spread*2), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0,0,0,alpha), (spread, spread, w, h), border_radius=18)
    surf.blit(sh, (x - spread, y - spread))

def render_text(surf, text, fnt, color, pos, center=False):
    img = fnt.render(text, True, color)
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(img, r)
    return r

def numfmt(n):
    neg = n < 0
    n = abs(n)
    for unit in ["","K","M","B","T","Q"]:
        if n < 1000:
            s = f"{n:.2f}".rstrip("0").rstrip(".")
            return ("-" if neg else "") + s + unit
        n /= 1000.0
    return ("-" if neg else "") + f"{n:.2f}Q"

# ---------- STAN (bez bazy) ----------
DEFAULT_STATE = {
    "zomle": 0.0,
    "per_click": 1.0,
    "cps": 0.0,
    "up_bigger_level": 0,
    "up_auto_level": 0,
    "up_multi_level": 0,
    "sound_on": True
}

def load_state():
    if not SAVE_ENABLED or not os.path.exists(SAVE_PATH):
        return DEFAULT_STATE.copy()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        st = DEFAULT_STATE.copy()
        st.update({k: data.get(k, st[k]) for k in st.keys()})
        return st
    except Exception:
        return DEFAULT_STATE.copy()

def save_state(state):
    if not SAVE_ENABLED: 
        return
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass

# ---------- ZAŁADUJ OBRAZ KLIKANIA ----------
def load_click_image():
    path = "zomla.jpg"
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        max_side = 380
        w, h = img.get_width(), img.get_height()
        sc = max_side / max(w, h)
        return pygame.transform.smoothscale(img, (int(w*sc), int(h*sc)))
    # placeholder: ładny okrąg
    radius = 180
    size = radius*2 + 8
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    gfxdraw.filled_circle(surf, size//2, size//2, radius+4, (0,0,0,60))
    gfxdraw.filled_circle(surf, size//2, size//2, radius, (80, 120, 255, 240))
    gfxdraw.aacircle(surf, size//2, size//2, radius, (255,255,255,220))
    return surf

CLICK_IMG = load_click_image()
center_x = WIDTH * 0.32
center_y = HEIGHT * 0.54
click_rect = CLICK_IMG.get_rect(center=(center_x, center_y))

# ---------- MECHANIKI ----------
state = load_state()
float_texts = []      # "+X"
particles = []        # cząsteczki przy kliknięciu
last_save_ts = time.time()
multiplier_timer = 0.0
autosave_flash = 0.0

def price_bigger(l): return 20 * (1.18 ** l)        # +1/click
def price_auto(l):   return 80 * (1.22 ** l)        # +0.2 CPS
def price_multi(l):  return 250 * (1.35 ** l)       # 2× na 20s
def get_multiplier(): return 2.0 if multiplier_timer > 0 else 1.0

# ---------- BUTTON ----------
class Button:
    def __init__(self, rect, label, accent=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent
        self.hover = False
    def draw(self, surf):
        base = COL_ACCENT if self.accent else COL_CARD
        col = (min(base[0]+10,255), min(base[1]+10,255), min(base[2]+10,255)) if self.hover else base
        draw_shadow(surf, self.rect, spread=6, alpha=80)
        draw_round_rect(surf, self.rect, col, radius=16)
        render_text(surf, self.label, FONT_UI, WHITE if self.accent else COL_TEXT, self.rect.center, center=True)
    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

btn_bigger = Button((WIDTH-320, 210, 260, 68), "Bigger Tap (+1/click)")
btn_auto   = Button((WIDTH-320, 290, 260, 68), "Auto Zomler (+0.2 CPS)")
btn_multi  = Button((WIDTH-320, 370, 260, 68), "Golden Zomla (2×/20s)")
btn_sound  = Button((WIDTH-320, 450, 260, 52), "Dźwięk: ON")

# ---------- PĘTLA ----------
running = True
accum = 0.0

while running:
    dt = clock.tick(FPS) / 1000.0
    accum += dt

    # TŁO
    draw_gradient_bg(screen, COL_BG_TOP, COL_BG_BOTTOM)

    # LEWA i PRAWA KARTA
    left_panel = pygame.Rect(40, 80, int(WIDTH*0.55), HEIGHT-120)
    right_panel = pygame.Rect(WIDTH-320-40, 80, 320, HEIGHT-120)
    draw_shadow(screen, left_panel, spread=8, alpha=90)
    draw_round_rect(screen, left_panel, COL_CARD, 22)
    draw_shadow(screen, right_panel, spread=8, alpha=90)
    draw_round_rect(screen, right_panel, COL_CARD, 22)

    render_text(screen, "ZOMLA CLICKER",     FONT_H1, COL_TEXT, (40, 24))
    render_text(screen, "Ulepszenia",        FONT_H2, COL_TEXT, (WIDTH-320, 100))

    # GŁÓWNY STAN
    zomle_txt = f"Zomle: {numfmt(state['zomle'])}"
    per_click_txt = f"+{state['per_click']:.2f}/klik"
    cps_txt = f"{state['cps']:.2f} CPS"
    mult_txt = "Mnożnik 2× AKTYWNY" if multiplier_timer>0 else "Mnożnik: 1×"
    render_text(screen, zomle_txt, FONT_H2, COL_ACCENT_2, (40, 96))
    render_text(screen, per_click_txt, FONT_UI, COL_TEXT_DIM, (340, 102))
    render_text(screen, cps_txt,       FONT_UI, COL_TEXT_DIM, (520, 102))
    render_text(screen, mult_txt,      FONT_UI, COL_SUCCESS if multiplier_timer>0 else COL_TEXT_DIM, (680, 102))

    # OBRAZ KLIKANIA
    click_rect = CLICK_IMG.get_rect(center=(center_x, center_y))
    glow_rect = CLICK_IMG.get_rect(center=(center_x, center_y))
    glow_surf = pygame.Surface((glow_rect.width+60, glow_rect.height+60), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (COL_ACCENT[0], COL_ACCENT[1], COL_ACCENT[2], 35), glow_surf.get_rect())
    screen.blit(glow_surf, (glow_rect.x-30, glow_rect.y-30))
    screen.blit(CLICK_IMG, click_rect)

    # SKLEP – ceny/poziomy
    price1 = price_bigger(state["up_bigger_level"])
    price2 = price_auto(state["up_auto_level"])
    price3 = price_multi(state["up_multi_level"])
    render_text(screen, f"Poziom: {state['up_bigger_level']} • Cena: {numfmt(price1)}", FONT_SMALL, COL_TEXT_DIM, (WIDTH-320, 160))
    render_text(screen, f"Poziom: {state['up_auto_level']} • Cena: {numfmt(price2)}",   FONT_SMALL, COL_TEXT_DIM, (WIDTH-320, 188))
    render_text(screen, f"Poziom: {state['up_multi_level']} • Cena: {numfmt(price3)}",  FONT_SMALL, COL_TEXT_DIM, (WIDTH-320, 216))

    # PRZYCISKI
    btn_bigger.draw(screen); btn_auto.draw(screen); btn_multi.draw(screen)
    btn_sound.label = f"Dźwięk: {'ON' if state['sound_on'] and SOUND_AVAILABLE else 'OFF'}"
    btn_sound.draw(screen)

    # PŁYNĄCE TEKSTY
    for t in list(float_texts):
        t["ttl"] -= dt
        if t["ttl"] <= 0:
            float_texts.remove(t)
        else:
            t["x"] += t["vx"] * dt
            t["y"] += t["vy"] * dt
            alpha = max(0, min(255, int(255 * (t["ttl"] / t["ttl0"]))))
            img = FONT_UI.render(t["text"], True, t["col"])
            img.set_alpha(alpha)
            screen.blit(img, (t["x"], t["y"]))

    # CZĄSTECZKI
    for p in list(particles):
        p["ttl"] -= dt
        if p["ttl"] <= 0:
            particles.remove(p)
        else:
            p["vx"] *= 0.98
            p["vy"] += 400 * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            a = int(255 * (p["ttl"] / p["ttl0"]))
            pygame.draw.circle(screen, (COL_ACCENT[0], COL_ACCENT[1], COL_ACCENT[2], a), (int(p["x"]), int(p["y"])), max(1, int(p["r"])))

    # AUTOSAVE WSKAŹNIK
    if autosave_flash > 0:
        autosave_flash -= dt
        msg = "Zapisano" if SAVE_ENABLED else "Zapis wyłączony"
        render_text(screen, msg, FONT_SMALL, COL_TEXT_DIM, (WIDTH-140, HEIGHT-30))

    # DÓŁ
    render_text(screen, "Klikaj w ZOMLĘ, kupuj ulepszenia!  •  ESC = wyjście (auto-zapis).", FONT_SMALL, COL_TEXT_DIM, (40, HEIGHT-30))

    pygame.display.flip()

    # DODAWANIE CPS CO SEKUNDĘ
    while accum >= 1.0:
        gained = state["cps"] * get_multiplier()
        state["zomle"] += gained
        if gained > 0:
            float_texts.append({"text": f"+{gained:.1f}", "x": center_x + 140, "y": center_y - 140,
                                "ttl": 0.9, "ttl0": 0.9, "vx": 0, "vy": -35, "col": COL_TEXT_DIM})
        accum -= 1.0

    # ZDARZENIA
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_state(state); pygame.quit(); sys.exit(0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            save_state(state); pygame.quit(); sys.exit(0)

        if btn_bigger.handle(event):
            if state["zomle"] >= price1:
                state["zomle"] -= price1
                state["up_bigger_level"] += 1
                state["per_click"] += 1.0
            else:
                float_texts.append({"text":"Za mało Zomli!", "x": WIDTH-190, "y": 205, "ttl": 1.0, "ttl0":1.0, "vx":0, "vy":-30, "col": COL_DANGER})

        if btn_auto.handle(event):
            if state["zomle"] >= price2:
                state["zomle"] -= price2
                state["up_auto_level"] += 1
                state["cps"] += 0.2
            else:
                float_texts.append({"text":"Za mało Zomli!", "x": WIDTH-190, "y": 285, "ttl": 1.0, "ttl0":1.0, "vx":0, "vy":-30, "col": COL_DANGER})

        if btn_multi.handle(event):
            if state["zomle"] >= price3:
                state["zomle"] -= price3
                state["up_multi_level"] += 1
                multiplier_timer = max(multiplier_timer, 20.0)
            else:
                float_texts.append({"text":"Za mało Zomli!", "x": WIDTH-190, "y": 365, "ttl": 1.0, "ttl0":1.0, "vx":0, "vy":-30, "col": COL_DANGER})

        if btn_sound.handle(event):
            state["sound_on"] = not state["sound_on"]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if click_rect.collidepoint(mx, my):
                multi = get_multiplier()
                gained = state["per_click"] * multi
                state["zomle"] += gained
                # +X
                float_texts.append({
                    "text": f"+{gained:.0f}" if abs(gained - int(gained)) < 1e-6 else f"+{gained:.1f}",
                    "x": mx, "y": my, "ttl": 0.8, "ttl0": 0.8, "vx": 0, "vy": -120, "col": WHITE
                })
                # cząsteczki
                for _ in range(16):
                    ang = random.uniform(0, 2*math.pi)
                    spd = random.uniform(120, 260)
                    particles.append({
                        "x": mx, "y": my,
                        "vx": math.cos(ang)*spd,
                        "vy": math.sin(ang)*spd - 80,
                        "ttl": 0.5 + random.random()*0.4,
                        "ttl0": 0.9,
                        "r": random.uniform(1, 2.2),
                    })
                # dźwięk
                if state["sound_on"] and SOUND_AVAILABLE and click_snd:
                    click_snd.play()

    # ODLiczanie mnożnika
    if multiplier_timer > 0:
        multiplier_timer -= dt
        if multiplier_timer < 0:
            multiplier_timer = 0

    # AUTO-SAVE co 10s
    if SAVE_ENABLED and (time.time() - last_save_ts > 10):
        save_state(state)
        last_save_ts = time.time()
        autosave_flash = 1.5

