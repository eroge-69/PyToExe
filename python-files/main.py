import pygame
import random
import math
from fractions import Fraction
from typing import Tuple, List, Optional

# =========================
# Réglages généraux & UI
# =========================
WIDTH, HEIGHT = 900, 600
FPS = 60

# Caméra (zoom/pan)
MIN_SCALE, MAX_SCALE = 20, 140
INITIAL_SCALE = 60

# Couleurs
AXIS_COLOR = (50, 50, 50)
GRID_COLOR = (220, 220, 220)
BG_COLOR   = (245, 245, 245)
TEXT_COLOR = (20, 20, 20)
OK_COLOR   = (30, 170, 80)    # vert
BAD_COLOR  = (200, 60, 60)    # rouge
POINT_COLOR= (30, 100, 220)
BTN_BG     = (255, 255, 255)
BTN_BORDER = (210, 210, 210)
NEUTRAL_CURVE = (0, 0, 0)

# Snap & placement (mini-jeu "Tracer par points")
SNAP_TO_INTEGER = True
GHOST_ALPHA = 110
GHOST_BORDER_ALPHA = 160
TOLERANCE_UNITS = 0.3
SAME_POINT_EPS = 1e-6

# Déplacement clavier
PAN_SPEED_PX = 10
PAN_SPEED_PX_FAST = 20

# Auto-suivant
AUTO_NEXT_DELAY_MS = 800

# Tolérance vérif a,b (mini-jeu "Deviner a,b")
TOL_EQ = 1e-3

# =========================
# Outils coords (caméra)
# =========================
def world_to_screen(x: float, y: float, scale: float, ox: float, oy: float) -> Tuple[int, int]:
    return int(ox + x * scale), int(oy - y * scale)

def screen_to_world(sx: int, sy: int, scale: float, ox: float, oy: float) -> Tuple[float, float]:
    return (sx - ox) / scale, (oy - sy) / scale

def zoom_at_cursor(scale: float, ox: float, oy: float, mx: int, my: int, step: float) -> Tuple[float,float,float]:
    new_scale = max(MIN_SCALE, min(MAX_SCALE, scale * step))
    if new_scale == scale: return scale, ox, oy
    wx = (mx - ox) / scale; wy = (oy - my) / scale
    return new_scale, mx - wx * new_scale, my + wy * new_scale

# =========================
# Modèle & formats
# =========================
def gcd(a: int, b: int) -> int:
    return math.gcd(a, b)

def simplify_fraction(p: int, q: int) -> Tuple[int,int]:
    g = gcd(abs(p), abs(q)); p//=g; q//=g
    if q < 0: p, q = -p, -q
    return p, q

class Linear:
    """y = a x + b (a_value numérique pour calcul; a_repr/b_repr pour joli affichage)"""
    def __init__(self, a_value: float, b_value: float, a_repr: Optional[str]=None, b_repr: Optional[str]=None):
        self.a = a_value; self.b = b_value
        self.a_repr = a_repr; self.b_repr = b_repr

    def f(self, x: float) -> float:
        return self.a * x + self.b

    def label(self) -> str:
        def fmt_num(k: float) -> str:
            if abs(k - int(k)) < 1e-9: return str(int(k))
            s = f"{k:.2f}".rstrip("0").rstrip("."); return s if s else "0"
        # a-term
        ax = ""
        if abs(self.a) >= 1e-9:
            if self.a_repr is not None:
                if self.a_repr in ("1","+1"): ax = "x"
                elif self.a_repr == "-1": ax = "-x"
                else: ax = f"{self.a_repr}x"
            else:
                if abs(self.a - 1) < 1e-9: ax = "x"
                elif abs(self.a + 1) < 1e-9: ax = "-x"
                else: ax = f"{fmt_num(self.a)}x"
        # b-term
        tail = ""
        if abs(self.b) >= 1e-9:
            btxt = self.b_repr if self.b_repr is not None else fmt_num(self.b)
            tail = btxt if ax=="" else (f" + {btxt}" if self.b>0 else f" - {btxt.lstrip('-')}")
        if ax=="" and tail=="": return "y = 0"
        return "y = " + ax + tail

# =========================
# Générateurs par niveau
# =========================
def gen_level_1() -> Linear:
    # a, b entiers relatifs
    a = random.randint(-5, 5); b = random.randint(-9, 9)
    if a==0 and b==0: b = random.choice([-2,-1,1,2])
    return Linear(a, b, str(a), str(b))

def gen_fraction(non_integer_only=True) -> Tuple[float,str]:
    p = random.choice([i for i in range(-9,10) if i!=0])
    q = random.randint(2,9)
    p,q = simplify_fraction(p,q)
    val = p/q
    if non_integer_only and abs(val - int(val)) < 1e-9:
        return gen_fraction(True)
    sign = "-" if val < 0 else ""
    return val, f"{sign}({abs(p)}/{q})"

def gen_level_2() -> Linear:
    # a = fraction non entière, b entier
    a_val, a_txt = gen_fraction(True)
    b = random.randint(-9, 9)
    return Linear(a_val, b, a_txt, str(b))

def gen_level_3() -> Linear:
    # a = fraction ou décimal non entier, b entier
    if random.random() < 0.5:
        a_val, a_txt = gen_fraction(True); a_repr = a_txt
    else:
        choices = [-3.5, -2.5, -1.5, -1.2, -0.5, 0.5, 0.75, 1.2, 1.5, 2.5, 3.75]
        a_val = random.choice(choices); a_repr = f"{a_val}".rstrip("0").rstrip(".")
    b = random.randint(-9, 9)
    return Linear(a_val, b, a_repr, str(b))

def get_gen(level: int):
    return {1: gen_level_1, 2: gen_level_2, 3: gen_level_3}[level]

# =========================
# Dessins généraux
# =========================
def draw_grid(surface: pygame.Surface, scale: float, ox: float, oy: float):
    surface.fill(BG_COLOR)
    x_min, y_max = screen_to_world(0, 0, scale, ox, oy)
    x_max, y_min = screen_to_world(WIDTH, HEIGHT, scale, ox, oy)
    xi0, xi1 = int(x_min)-1, int(x_max)+1
    yi0, yi1 = int(y_min)-1, int(y_max)+1
    for i in range(xi0, xi1+1):
        sx,_ = world_to_screen(i,0,scale,ox,oy)
        pygame.draw.line(surface, GRID_COLOR, (sx,0), (sx,HEIGHT))
    for j in range(yi0, yi1+1):
        _,sy = world_to_screen(0,j,scale,ox,oy)
        pygame.draw.line(surface, GRID_COLOR, (0,sy), (WIDTH,sy))
    sx0, sy0 = world_to_screen(0,0,scale,ox,oy)
    pygame.draw.line(surface, AXIS_COLOR, (0,sy0), (WIDTH,sy0), 2)
    pygame.draw.line(surface, AXIS_COLOR, (sx0,0), (sx0,HEIGHT), 2)
    font = pygame.font.SysFont(None, 18)
    if 0<=sy0<=HEIGHT:
        for i in range(xi0, xi1+1):
            if i==0: continue
            sx,_ = world_to_screen(i,0,scale,ox,oy)
            pygame.draw.line(surface, AXIS_COLOR, (sx,sy0-4), (sx,sy0+4), 2)
            surface.blit(font.render(str(i), True, AXIS_COLOR), (sx-6, sy0+6))
    if 0<=sx0<=WIDTH:
        for j in range(yi0, yi1+1):
            if j==0: continue
            _,sy = world_to_screen(0,j,scale,ox,oy)
            pygame.draw.line(surface, AXIS_COLOR, (sx0-4,sy), (sx0+4,sy), 2)
            surface.blit(font.render(str(j), True, AXIS_COLOR), (sx0+6, sy-8))

def draw_function(surface: pygame.Surface, func: Linear, scale: float, ox: float, oy: float, color=(0,0,0), width: int = 3):
    x_left,_  = screen_to_world(0,0,scale,ox,oy)
    x_right,_ = screen_to_world(WIDTH,0,scale,ox,oy)
    p1 = world_to_screen(x_left,  func.f(x_left),  scale,ox,oy)
    p2 = world_to_screen(x_right, func.f(x_right), scale,ox,oy)
    pygame.draw.line(surface, color, p1, p2, width)

# =========================
# Helpers mini-jeu "Tracer par points"
# =========================
def draw_points(surface: pygame.Surface, pts_world: List[Tuple[float,float]], scale: float, ox: float, oy: float):
    for (x, y) in pts_world:
        sx, sy = world_to_screen(x, y, scale, ox, oy)
        pygame.draw.circle(surface, POINT_COLOR, (sx, sy), 7)
        pygame.draw.circle(surface, (255,255,255), (sx, sy), 3)

def draw_mode_button(surface: pygame.Surface, mode_pan: bool) -> pygame.Rect:
    label = "Mode: Déplacement" if mode_pan else "Mode: Sélection"
    font = pygame.font.SysFont(None, 22, bold=True)
    txt = font.render(label, True, (40,40,40))
    padx, pady = 12, 8
    w = txt.get_width() + 2*padx
    h = txt.get_height() + 2*pady
    rect = pygame.Rect(WIDTH - w - 16, HEIGHT - h - 16, w, h)
    pygame.draw.rect(surface, BTN_BG, rect, border_radius=10)
    pygame.draw.rect(surface, BTN_BORDER, rect, 2, border_radius=10)
    surface.blit(txt, (rect.x + padx, rect.y + pady))
    return rect

def draw_toggle_auto_next(surface: pygame.Surface, enabled: bool, right_of: Optional[pygame.Rect]=None) -> pygame.Rect:
    label = "Auto-suivant"
    font = pygame.font.SysFont(None, 20)
    txt = font.render(label, True, (40,40,40))

    sw_w, sw_h = 44, 24
    gap = 10
    h = 36
    if right_of:
        rect = pygame.Rect(right_of.x - (txt.get_width()+gap+sw_w+28), right_of.y, txt.get_width()+gap+sw_w+16, right_of.height)
    else:
        rect = pygame.Rect(WIDTH - (txt.get_width()+gap+sw_w+28), HEIGHT - h - 16, txt.get_width()+gap+sw_w+16, h)

    pygame.draw.rect(surface, BTN_BG, rect, border_radius=10)
    pygame.draw.rect(surface, BTN_BORDER, rect, 2, border_radius=10)
    tx = rect.x + 10
    ty = rect.y + (rect.height - txt.get_height())//2
    surface.blit(txt, (tx, ty))
    sw_x = tx + txt.get_width() + gap
    sw_y = rect.y + (rect.height - sw_h)//2
    track = pygame.Rect(sw_x, sw_y, sw_w, sw_h)
    pygame.draw.rect(surface, (230,230,230), track, border_radius=12)
    if enabled:
        pygame.draw.rect(surface, (170,230,180), track, border_radius=12)
        knob_center = (sw_x + sw_w - sw_h//2, sw_y + sw_h//2)
    else:
        knob_center = (sw_x + sw_h//2, sw_y + sw_h//2)
    pygame.draw.circle(surface, (255,255,255), knob_center, sw_h//2 - 2)
    pygame.draw.circle(surface, (0,0,0), knob_center, sw_h//2 - 2, 1)
    return rect

def within_tolerance(func: Linear, point: Tuple[float,float], eps_units: float) -> bool:
    x, y = point
    return abs(y - func.f(x)) <= eps_units

def points_distinct(p1: Tuple[float,float], p2: Tuple[float,float], eps: float = SAME_POINT_EPS) -> bool:
    return (abs(p1[0] - p2[0]) > eps) or (abs(p1[1] - p2[1]) > eps)

def draw_ghost_point(surface: pygame.Surface, pos_world: Tuple[float,float], scale: float, ox: float, oy: float):
    wx, wy = pos_world
    sx, sy = world_to_screen(wx, wy, scale, ox, oy)
    ghost = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(ghost, (POINT_COLOR[0], POINT_COLOR[1], POINT_COLOR[2], GHOST_ALPHA), (10, 10), 7)
    pygame.draw.circle(ghost, (255, 255, 255, GHOST_ALPHA), (10, 10), 3)
    pygame.draw.circle(ghost, (0, 0, 0, GHOST_BORDER_ALPHA), (10, 10), 7, width=1)
    surface.blit(ghost, (sx - 10, sy - 10))

# =========================
# UI génériques (menu + champs)
# =========================
class InputBox:
    def __init__(self, rect: pygame.Rect, placeholder: str = ""):
        self.rect = rect
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.font.SysFont(None, 26)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                pass
            else:
                ch = event.unicode
                if ch in "0123456789-./, ":
                    self.text += ch
    def value(self) -> Optional[float]:
        s = self.text.strip().replace(",", ".")
        if not s: return None
        try:
            if "/" in s: return float(Fraction(s))
            return float(s)
        except Exception:
            return None
    def draw(self, surface):
        pygame.draw.rect(surface, BTN_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, BTN_BORDER, self.rect, 2 if not self.active else 3, border_radius=8)
        txt = self.text if self.text else self.placeholder
        color = (20,20,20) if self.text else (130,130,130)
        surf = self.font.render(txt, True, color)
        surface.blit(surf, (self.rect.x+8, self.rect.y + (self.rect.h - surf.get_height())//2))

# =========================
# États & menu
# =========================
STATE_MENU = "menu"
STATE_POINTS = "points"  # tracer par points
STATE_AB = "ab"          # deviner a,b

def draw_menu(screen, level: int) -> Tuple[pygame.Rect, pygame.Rect, List[Tuple[pygame.Rect,int]]]:
    screen.fill((20,20,26))
    font_title = pygame.font.SysFont(None, 48, bold=True)
    font_big = pygame.font.SysFont(None, 36, bold=True)
    font = pygame.font.SysFont(None, 24)
    title = "Choisis ton mode de jeu"
    screen.blit(font_title.render(title, True, (240,240,255)), (WIDTH//2 - font_title.size(title)[0]//2, 80))

    # Boutons modes
    btn_w, btn_h, gap = 360, 56, 14
    x = WIDTH//2 - btn_w//2
    y = 180
    btn_points = pygame.Rect(x, y, btn_w, btn_h)
    btn_ab     = pygame.Rect(x, y + btn_h + gap, btn_w, btn_h)
    for rect, label in [(btn_points, "Tracer par points"), (btn_ab, "Deviner a et b")]:
        pygame.draw.rect(screen, (255,255,255), rect, border_radius=12)
        pygame.draw.rect(screen, (200,200,220), rect, 2, border_radius=12)
        t = font_big.render(label, True, (40,40,60))
        screen.blit(t, (rect.x + (rect.w - t.get_width())//2, rect.y + (rect.h - t.get_height())//2))

    # Niveaux
    levels_rects: List[Tuple[pygame.Rect,int]] = []
    lev_y = btn_ab.bottom + 40
    lev_label = "Niveau : (actuel = %d)" % level
    screen.blit(font_big.render(lev_label, True, (230,230,240)), (x, lev_y))
    lev_y += 10
    w, h = 110, 40
    for i in [1,2,3]:
        r = pygame.Rect(x + (i-1)*(w+12), lev_y + 30, w, h)
        pygame.draw.rect(screen, (255,255,255), r, border_radius=10)
        pygame.draw.rect(screen, (200,200,220), r, 2, border_radius=10)
        t = font.render(f"Niveau {i}", True, (40,40,60))
        screen.blit(t, (r.x + (w - t.get_width())//2, r.y + (h - t.get_height())//2))
        levels_rects.append((r, i))
    tips = "Niv.1: a,b entiers | Niv.2: a fraction, b entier | Niv.3: a fraction ou décimal, b entier"
    screen.blit(font.render(tips, True, (210,210,220)), (x, lev_y + 30 + h + 18))
    return btn_points, btn_ab, levels_rects

# =========================
# Programme principal
# =========================
def main():
    pygame.init()
    pygame.display.set_caption("Fonctions affines – 2 mini-jeux")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_big = pygame.font.SysFont(None, 34, bold=True)
    font_expr = pygame.font.SysFont(None, 42, bold=True)  # pour l’expression top-gauche

    # Caméra
    scale = INITIAL_SCALE
    ox, oy = WIDTH/2, HEIGHT/2

    # Menu / niveau
    state = STATE_MENU
    level = 1
    gen = get_gen(level)

    # Commun
    func = gen()
    auto_next = True
    auto_next_deadline: Optional[int] = None

    # ---- "Tracer par points" state ----
    placed_points: List[Tuple[float,float]] = []
    mode_pan = False
    btn_mode_rect = pygame.Rect(0,0,0,0)
    btn_auto_rect = pygame.Rect(0,0,0,0)
    feedback = ""
    feedback_color = TEXT_COLOR
    show_true_curve = False
    last_result_ok: Optional[bool] = None
    score_points = 0

    # ---- "Deviner a,b" state ----
    attempts_ab = 0
    message_ab = ""
    msg_color_ab = TEXT_COLOR
    show_colored_curve_ab = False
    curve_ok_ab = False

    input_a = InputBox(pygame.Rect(0, 0, 150, 40), "ex: 3/2 ou -1")
    input_b = InputBox(pygame.Rect(0, 0, 150, 40), "ex: 2 ou -4.5")
    label_a_surf = font.render("a =", True, TEXT_COLOR)
    label_b_surf = font.render("b =", True, TEXT_COLOR)
    auto_toggle_rect = pygame.Rect(WIDTH - 140, HEIGHT - 48, 130, 36)

    running = True
    dragging = False
    drag_start_mouse = (0, 0)
    drag_start_oxoy = (ox, oy)

    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # ---------------- Events ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # MENU
            if state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn_points, btn_ab, levels_rects = draw_menu(screen, level)
                    if btn_points.collidepoint(event.pos):
                        state = STATE_POINTS
                        func = gen(); placed_points.clear()
                        feedback = ""; show_true_curve = False; last_result_ok = None
                        auto_next_deadline = None
                        scale, ox, oy = INITIAL_SCALE, WIDTH/2, HEIGHT/2
                        continue
                    if btn_ab.collidepoint(event.pos):
                        state = STATE_AB
                        func = gen()
                        input_a.text = ""; input_b.text = ""
                        message_ab = ""; show_colored_curve_ab = False; curve_ok_ab = False
                        auto_next_deadline = None
                        scale, ox, oy = INITIAL_SCALE, WIDTH/2, HEIGHT/2
                        continue
                    for r, lvl in levels_rects:
                        if r.collidepoint(event.pos):
                            level = lvl
                            gen = get_gen(level)
                continue

            # POINTS
            if state == STATE_POINTS:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = STATE_MENU
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_PAGEUP):
                        mx,my = pygame.mouse.get_pos(); scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1.1)
                    elif event.key in (pygame.K_MINUS, pygame.K_PAGEDOWN):
                        mx,my = pygame.mouse.get_pos(); scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1/1.1)
                    elif event.key == pygame.K_TAB:
                        mode_pan = not mode_pan
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btn_mode_rect.collidepoint(event.pos):
                            mode_pan = not mode_pan
                        elif btn_auto_rect.collidepoint(event.pos):
                            auto_next = not auto_next
                            auto_next_deadline = None
                        else:
                            if mode_pan:
                                dragging = True
                                drag_start_mouse = event.pos
                                drag_start_oxoy = (ox, oy)
                            else:
                                xw, yw = screen_to_world(*event.pos, scale, ox, oy)
                                if SNAP_TO_INTEGER: xw, yw = round(xw), round(yw)
                                placed_points.append((xw, yw))
                                if len(placed_points) > 2: placed_points.pop(0)
                                show_true_curve = False; last_result_ok = None; auto_next_deadline=None
                    elif event.button == 3:
                        if not mode_pan and placed_points:
                            placed_points.pop()
                            show_true_curve = False; last_result_ok = None; auto_next_deadline=None
                    elif event.button == 4:
                        mx,my = event.pos; scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1.1)
                    elif event.button == 5:
                        mx,my = event.pos; scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1/1.1)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if dragging and mode_pan:
                        mx,my = event.pos
                        dx = mx - drag_start_mouse[0]; dy = my - drag_start_mouse[1]
                        ox = drag_start_oxoy[0] + dx; oy = drag_start_oxoy[1] + dy

            # AB
            if state == STATE_AB:
                # touches de zoom/pan toujours actives
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = STATE_MENU
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_PAGEUP):
                        mx, my = pygame.mouse.get_pos()
                        scale, ox, oy = zoom_at_cursor(scale, ox, oy, mx, my, 1.1)
                    elif event.key in (pygame.K_MINUS, pygame.K_PAGEDOWN):
                        mx, my = pygame.mouse.get_pos()
                        scale, ox, oy = zoom_at_cursor(scale, ox, oy, mx, my, 1/1.1)
                    elif event.key in (pygame.K_LEFT, pygame.K_q):   ox += PAN_SPEED_PX
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):  ox -= PAN_SPEED_PX
                    elif event.key in (pygame.K_UP, pygame.K_z):     oy += PAN_SPEED_PX
                    elif event.key in (pygame.K_DOWN, pygame.K_s):   oy -= PAN_SPEED_PX

                # champs (après gestion +/− pour ne pas “manger” le zoom)
                input_a.handle_event(event)
                input_b.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if auto_toggle_rect.collidepoint(event.pos):
                            auto_next = not auto_next
                            auto_next_deadline = None
                    elif event.button == 4:
                        mx,my = event.pos; scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1.1)
                    elif event.button == 5:
                        mx,my = event.pos; scale,ox,oy = zoom_at_cursor(scale,ox,oy,mx,my,1/1.1)

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_TAB, ):
                        if input_a.active:
                            input_a.active=False; input_b.active=True
                        elif input_b.active:
                            input_b.active=False; input_a.active=True
                        else:
                            input_a.active=True
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        va = input_a.value(); vb = input_b.value()
                        attempts_ab += 1
                        if va is None or vb is None:
                            message_ab = "⚠️ Entrées invalides (décimaux/fractions ex: -3/2)."
                            msg_color_ab = BAD_COLOR
                            show_colored_curve_ab = False; curve_ok_ab=False; auto_next_deadline=None
                        else:
                            ok_a = abs(va - func.a) <= TOL_EQ
                            ok_b = abs(vb - func.b) <= TOL_EQ
                            curve_ok_ab = ok_a and ok_b
                            if curve_ok_ab:
                                message_ab = f"✅ Correct !  y = {func.label()[4:]}"
                                msg_color_ab = OK_COLOR
                            else:
                                message_ab = f"❌ Mauvais.  Solution : {func.label()}"
                                msg_color_ab = BAD_COLOR
                            show_colored_curve_ab = True
                            if auto_next: auto_next_deadline = now + AUTO_NEXT_DELAY_MS
                    elif event.key == pygame.K_c:
                        input_a.text=""; input_b.text=""
                        show_colored_curve_ab=False; curve_ok_ab=False; message_ab=""; auto_next_deadline=None

        # Déplacement clavier continu (les deux modes)
        keys = pygame.key.get_pressed()
        if state in (STATE_POINTS, STATE_AB):
            speed = PAN_SPEED_PX_FAST if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else PAN_SPEED_PX
            if keys[pygame.K_LEFT] or keys[pygame.K_q]:   ox += speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  ox -= speed
            if keys[pygame.K_UP] or keys[pygame.K_z]:     oy += speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:   oy -= speed

        # Auto-suivant commun
        if auto_next and auto_next_deadline is not None and now >= auto_next_deadline:
            func = gen()
            auto_next_deadline = None
            if state == STATE_POINTS:
                placed_points.clear(); show_true_curve=False; last_result_ok=None; feedback=""
            elif state == STATE_AB:
                input_a.text=""; input_b.text=""; show_colored_curve_ab=False; curve_ok_ab=False; message_ab=""

        # ---------------- Rendu ----------------
        if state == STATE_MENU:
            draw_menu(screen, level)
            pygame.display.flip()
            continue

        draw_grid(screen, scale, ox, oy)

        # Bandeau haut (affiche l'expression en haut-gauche)
        # En POINTS: expression exacte   |   En AB: expression générique
        expr_text = func.label() if state == STATE_POINTS else "y = ax + b"
        expr_surf = font_expr.render(expr_text, True, TEXT_COLOR)
        bar_h = max(80, expr_surf.get_height() + 20)
        pygame.draw.rect(screen, (255,255,255), (0,0,WIDTH,bar_h))
        pygame.draw.line(screen, (210,210,210), (0,bar_h), (WIDTH,bar_h), 1)
        screen.blit(expr_surf, (16, 10))

        # ligne d'infos/contrôles sous l'expression
        if state == STATE_POINTS:
            ctrl_info = "Clic gauche = poser/déplacer (selon mode) | Clic droit = annuler"
            info_extra = f"Niveau {level} | Échelle: {scale:.1f} px/u" + (" | SNAP ENTIER: ON" if SNAP_TO_INTEGER else " | SNAP ENTIER: OFF")
            screen.blit(font.render(ctrl_info, True, (60,60,60)), (16, expr_surf.get_height() + 14))
            screen.blit(font.render(info_extra, True, (90,90,90)), (16, expr_surf.get_height() + 34))
        else:
            ctrl_info = "Entrée: valider | Tab: changer champ | C: effacer | Molette/=/−/PgUp/PgDn: zoom | ZQSD/Flèches: déplacer"
            info_extra = f"Niveau {level} | Échelle: {scale:.1f} px/u"
            screen.blit(font.render(ctrl_info, True, (60,60,60)), (16, expr_surf.get_height() + 14))
            screen.blit(font.render(info_extra, True, (90,90,90)), (16, expr_surf.get_height() + 34))

        # ======= MODE POINTS =======
        if state == STATE_POINTS:
            # Évaluer si 2 points
            if len(placed_points) == 2 and auto_next_deadline is None:
                p1, p2 = placed_points
                if not points_distinct(p1, p2):
                    feedback = "⚠️ Deux points identiques : choisis deux points distincts."
                    feedback_color = BAD_COLOR
                    last_result_ok = False
                    show_true_curve = True
                    auto_next_deadline = now + AUTO_NEXT_DELAY_MS if auto_next else None
                else:
                    p1_ok = within_tolerance(func, p1, TOLERANCE_UNITS)
                    p2_ok = within_tolerance(func, p2, TOLERANCE_UNITS)
                    last_result_ok = bool(p1_ok and p2_ok)
                    if last_result_ok:
                        feedback = "✅ Bravo !"; feedback_color = OK_COLOR
                        score_points += 1
                    else:
                        feedback = "❌ Au moins un point n'est pas sur la droite."; feedback_color = BAD_COLOR
                    show_true_curve = True
                    if auto_next: auto_next_deadline = now + AUTO_NEXT_DELAY_MS

            # Courbe (neutre / verte / rouge)
            if show_true_curve:
                draw_function(screen, func, scale, ox, oy, OK_COLOR if last_result_ok else BAD_COLOR)


            # Points + fantôme
            draw_points(screen, placed_points, scale, ox, oy)
            mx,my = pygame.mouse.get_pos()
            wx, wy = screen_to_world(mx, my, scale, ox, oy)
            if not mode_pan:
                ghost_world = (round(wx), round(wy)) if SNAP_TO_INTEGER else (wx, wy)
                draw_ghost_point(screen, ghost_world, scale, ox, oy)
            cursor_label = (f"({round(wx)}, {round(wy)})" if SNAP_TO_INTEGER else f"({wx:.2f}, {wy:.2f})")
            screen.blit(font.render(cursor_label, True, (80,80,80)), (mx + 12, my - 20))

            # Feedback + score
            fb_txt = font.render(feedback, True, feedback_color)
            screen.blit(fb_txt, (16, bar_h + 8))
            score_txt = font.render(f"Score : {score_points}", True, (0,0,0))
            screen.blit(score_txt, (WIDTH - 16 - score_txt.get_width(), bar_h + 8))

            # Boutons bas-droite
            btn_mode_rect = draw_mode_button(screen, mode_pan)
            btn_auto_rect = draw_toggle_auto_next(screen, auto_next, btn_mode_rect)

        # ======= MODE AB =======
        elif state == STATE_AB:
            # CENTRAGE ABSOLU des champs au MILIEU de l'écran
            la_w, la_h = label_a_surf.get_size()
            lb_w, lb_h = label_b_surf.get_size()
            SMALL_GAP = 10
            BLOCK_GAP = 40
            a_block_w = la_w + SMALL_GAP + input_a.rect.w
            b_block_w = lb_w + SMALL_GAP + input_b.rect.w
            total_w = a_block_w + BLOCK_GAP + b_block_w
            x0 = WIDTH // 2 - total_w // 2
            row_y = HEIGHT // 2 - input_a.rect.h // 2  # VRAI milieu vertical

            label_a_pos = (x0, row_y + (input_a.rect.h - la_h)//2)
            input_a.rect = pygame.Rect(x0 + la_w + SMALL_GAP, row_y, input_a.rect.w, input_a.rect.h)

            x1 = x0 + a_block_w + BLOCK_GAP
            label_b_pos = (x1, row_y + (input_b.rect.h - lb_h)//2)
            input_b.rect = pygame.Rect(x1 + lb_w + SMALL_GAP, row_y, input_b.rect.w, input_b.rect.h)

            # Dessin labels + champs
            screen.blit(label_a_surf, label_a_pos)
            input_a.draw(screen)
            screen.blit(label_b_surf, label_b_pos)
            input_b.draw(screen)

            # Courbe
            if show_colored_curve_ab:
                draw_function(screen, func, scale, ox, oy, OK_COLOR if curve_ok_ab else BAD_COLOR)
            else:
                draw_function(screen, func, scale, ox, oy, NEUTRAL_CURVE)

            # Message
            if message_ab:
                screen.blit(font.render(message_ab, True, msg_color_ab), (16, bar_h + 8))

            # Toggle auto-suivant (bas-droite)
            auto_toggle_rect = draw_toggle_auto_next(screen, auto_next)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
