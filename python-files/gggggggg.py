# backrooms_editor.py
import pygame
import sys
import json
from pathlib import Path

pygame.init()
pygame.mixer.init()  # placeholder if you want to add sounds later

# ---- Window / grid ----
SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
pygame.display.set_caption("Backrooms Isometric Editor")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 24)
SMALL_FONT = pygame.font.SysFont(None, 18)

TILE_W = 60
TILE_H = 30
GRID_COLS = 50
GRID_ROWS = 50
GRID_ORIGIN = (SCREEN_W // 2, 100)
BOTTOM_BAR_H = 48

SAVE_FILE = Path.cwd() / "map.json"

# ---- Tile definitions: category -> list of (name, color) ----
tile_types = {
    # Floors (multiple subtypes)
    "1": [
        ("Regular", (200, 170, 120)),
        ("Wood", (170, 120, 70)),
        ("Marble", (230, 230, 240)),
        ("Gray Carpet", (150, 150, 150)),
        ("Stone Tile", (190, 190, 170)),
        ("Backrooms Carpet", (255, 250, 170))
    ],
    # Walls (including Backrooms)
    "2": [
        ("Concrete", (180, 180, 180)),
        ("Brick", (160, 80, 60)),
        ("Metal", (100, 100, 120)),
        ("Backrooms", (255, 255, 150))
    ],
    # Furniture
    "3": [
        ("Desk", (100, 100, 200)),
        ("Couch", (150, 80, 200)),
        ("Lamp", (255, 200, 100)),
        ("Chair", (140, 100, 60)),
        ("Table", (120, 90, 60)),
        ("Bed", (160, 120, 120)),
        ("Plant", (60, 140, 60)),
        ("Shelf", (110, 80, 50))
    ]
}

# ---- State ----
state = "main_menu"   # "main_menu", "editor", "pause", "settings"
current_tile = "1"    # "1" floor, "2" wall, "3" furniture
current_subtype_index = {"1": 0, "2": 0, "3": 0}
eraser_mode = False
fullscreen = False

# store tiles:
# floors: dict (col,row) -> subtype_index
floor_tiles = {}
# walls & props: lists of (col,row, category, subtype_index)
wall_tiles = []
prop_tiles = []

# Dragging state
dragging = False
drag_start = None  # (col,row)
drag_mode_category = None  # "erase" or "1"/"2"/"3"

# UI toggle
settings = {"music": False, "sfx": False, "vhs": False}

# ---------- Utility functions ----------
def safe_print(*a, **k):
    try:
        print(*a, **k)
    except Exception:
        pass

def darken(color, f):
    return tuple(max(0, min(255, int(c * f))) for c in color)

def grid_to_screen(col, row):
    """Return top middle point of iso tile (x,y) for drawing diamond top."""
    ox, oy = GRID_ORIGIN
    x = ox + (col - row) * (TILE_W // 2)
    y = oy + (col + row) * (TILE_H // 2)
    return int(x), int(y)

def screen_to_grid(mx, my):
    """Convert real mouse coords to integer grid coords."""
    ox, oy = GRID_ORIGIN
    mx_rel = mx - ox
    my_rel = my - oy
    # inverse of the isometric transform
    col = (mx_rel / (TILE_W / 2) + my_rel / (TILE_H / 2)) / 2
    row = (my_rel / (TILE_H / 2) - mx_rel / (TILE_W / 2)) / 2
    return int(round(col)), int(round(row))

def clamp(col, row):
    c = max(0, min(GRID_COLS - 1, col))
    r = max(0, min(GRID_ROWS - 1, row))
    return c, r

# Bresenham line algorithm to get grid points between two tiles (works all directions)
def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx >= dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        points.append((x1, y1))
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        points.append((x1, y1))
    return points

# ---- Drawing primitives ----
def draw_diamond(x, y, color, border=True):
    w, h = TILE_W, TILE_H
    pts = [(x, y), (x + w//2, y - h//2), (x + w, y), (x + w//2, y + h//2)]
    pygame.draw.polygon(screen, color, pts)
    if border:
        pygame.draw.polygon(screen, (0,0,0), pts, 1)

def draw_wall(x, y, color):
    w, h = TILE_W, TILE_H
    top = [(x, y), (x + w//2, y - h//2), (x + w, y), (x + w//2, y + h//2)]
    left = [(x, y), (x + w//2, y + h//2), (x + w//2, y + h//2 + 60), (x, y + 60)]
    right = [(x + w//2, y + h//2), (x + w, y), (x + w, y + 60), (x + w//2, y + h//2 + 60)]
    pygame.draw.polygon(screen, color, top)
    pygame.draw.polygon(screen, darken(color, 0.85), left)
    pygame.draw.polygon(screen, darken(color, 0.7), right)
    pygame.draw.polygon(screen, (0,0,0), top, 1)
    pygame.draw.polygon(screen, (0,0,0), left, 1)
    pygame.draw.polygon(screen, (0,0,0), right, 1)

def draw_prop(x, y, color, name=None):
    w, h = TILE_W, TILE_H
    base = [(x + 10, y + 5), (x + w//2, y - 5), (x + w - 10, y + 5), (x + w//2, y + h//2 + 5)]
    pygame.draw.polygon(screen, color, base)
    pygame.draw.polygon(screen, (0,0,0), base, 1)
    if name and "Lamp" in name:
        pygame.draw.circle(screen, (255, 240, 160), (x + w//2, y), 5)

# ---- Save / Load ----
def save_map(path=SAVE_FILE):
    try:
        data = {
            "floors": [[c, r, int(sub)] for (c,r), sub in floor_tiles.items()],
            "walls": [[c, r, cat, int(sub)] for (c,r,cat,sub) in wall_tiles],
            "props": [[c, r, cat, int(sub)] for (c,r,cat,sub) in prop_tiles]
        }
        with open(path, "w") as f:
            json.dump(data, f)
        safe_print(f"Map saved to {path}")
    except PermissionError:
        safe_print("Save failed: Permission denied. Trying script folder fallback...")
        try:
            fallback = Path.cwd() / "map.json"
            with open(fallback, "w") as f:
                json.dump(data, f)
            safe_print(f"Saved to fallback: {fallback}")
        except Exception as e:
            safe_print("Save fallback failed:", e)
    except Exception as e:
        safe_print("Save failed:", e)

def load_map(path=SAVE_FILE):
    global floor_tiles, wall_tiles, prop_tiles
    try:
        if not Path(path).exists():
            safe_print("Load file not found:", path)
            return
        with open(path, "r") as f:
            raw = json.load(f)
        # defensive parsing
        floors = {}
        for item in raw.get("floors", []):
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                c, r, sub = int(item[0]), int(item[1]), int(item[2])
                c, r = clamp(c, r)
                sub = max(0, min(sub, len(tile_types["1"]) - 1))
                floors[(c, r)] = sub
        walls = []
        for item in raw.get("walls", []):
            if isinstance(item, (list, tuple)) and len(item) >= 4:
                c, r, cat, sub = int(item[0]), int(item[1]), str(item[2]), int(item[3])
                c, r = clamp(c, r)
                if cat not in tile_types:
                    cat = "2"
                sub = max(0, min(sub, len(tile_types[cat]) - 1))
                walls.append((c, r, cat, sub))
        props = []
        for item in raw.get("props", []):
            if isinstance(item, (list, tuple)) and len(item) >= 4:
                c, r, cat, sub = int(item[0]), int(item[1]), str(item[2]), int(item[3])
                c, r = clamp(c, r)
                if cat not in tile_types:
                    cat = "3"
                sub = max(0, min(sub, len(tile_types[cat]) - 1))
                props.append((c, r, cat, sub))
        floor_tiles = floors
        wall_tiles = walls
        prop_tiles = props
        safe_print(f"Map loaded from {path}")
    except Exception as e:
        safe_print("Load failed:", e)

# ---- Helpers for placing/removing ----
def remove_at(c, r):
    floor_tiles.pop((c, r), None)
    global wall_tiles, prop_tiles
    wall_tiles = [t for t in wall_tiles if not (t[0] == c and t[1] == r)]
    prop_tiles = [t for t in prop_tiles if not (t[0] == c and t[1] == r)]

def place_floor(c, r, sub):
    floor_tiles[(c, r)] = int(sub)

def place_wall(c, r, cat, sub):
    # ensure floor beneath
    floor_tiles.setdefault((c, r), 0)
    global wall_tiles
    wall_tiles = [t for t in wall_tiles if not (t[0] == c and t[1] == r)]
    wall_tiles.append((c, r, cat, int(sub)))

def place_prop(c, r, cat, sub):
    floor_tiles.setdefault((c, r), 0)
    global prop_tiles
    prop_tiles = [t for t in prop_tiles if not (t[0] == c and t[1] == r)]
    prop_tiles.append((c, r, cat, int(sub)))

# ---- UI buttons ----
def button_rect(center_x, center_y, w, h):
    return pygame.Rect(int(center_x - w//2), int(center_y - h//2), w, h)

def draw_button(rect, text, hovered=False):
    color = (240, 230, 100) if hovered else (255, 240, 130)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=6)
    surf = FONT.render(text, True, (10,10,10))
    tw, th = surf.get_size()
    screen.blit(surf, (rect.x + (rect.w - tw)//2, rect.y + (rect.h - th)//2))

# ---- Menus ----
def draw_main_menu():
    screen.fill((240, 230, 140))  # Backrooms yellow
    w, h = screen.get_size()
    title = FONT.render("THE BACKROOMS - Editor", True, (30, 30, 30))
    screen.blit(title, (w//2 - title.get_width()//2, 60))
    # Menu buttons
    btn_w, btn_h = 240, 56
    centers = [(w//2, 180), (w//2, 260), (w//2, 340), (w//2, 420)]
    names = ["Start / Editor", "Load Game", "Settings", "Quit"]
    mouse = pygame.mouse.get_pos()
    mx, my = mouse
    for i, (cx, cy) in enumerate(centers):
        rect = button_rect(cx, cy, btn_w, btn_h)
        hovered = rect.collidepoint(mx, my)
        draw_button(rect, names[i], hovered)

def draw_settings_menu():
    screen.fill((235, 225, 120))
    w, h = screen.get_size()
    title = FONT.render("Settings", True, (30,30,30))
    screen.blit(title, (20, 20))
    # toggles
    music_txt = f"Music: {'On' if settings['music'] else 'Off'}  (Toggle M)"
    sfx_txt = f"SFX: {'On' if settings['sfx'] else 'Off'}  (Toggle K)"
    vhs_txt = f"VHS overlay: {'On' if settings['vhs'] else 'Off'}  (Toggle V)"
    screen.blit(FONT.render(music_txt, True, (10,10,10)), (20, 80))
    screen.blit(FONT.render(sfx_txt, True, (10,10,10)), (20, 120))
    screen.blit(FONT.render(vhs_txt, True, (10,10,10)), (20, 160))
    screen.blit(SMALL_FONT.render("Press Esc to return to main menu", True, (60,60,60)), (20, h-40))

def draw_pause_menu():
    # semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((10,10,10,160))
    screen.blit(overlay, (0,0))
    w, h = screen.get_size()
    title = FONT.render("Paused", True, (255, 240, 150))
    screen.blit(title, (w//2 - title.get_width()//2, h//2 - 120))
    # buttons
    btn_w, btn_h = 220, 46
    centers = [(w//2, h//2 - 20), (w//2, h//2 + 50), (w//2, h//2 + 120)]
    names = ["Resume", "Save Game", "Load Game"]
    mouse = pygame.mouse.get_pos()
    mx, my = mouse
    for i, (cx, cy) in enumerate(centers):
        rect = button_rect(cx, cy, btn_w, btn_h)
        hovered = rect.collidepoint(mx, my)
        draw_button(rect, names[i], hovered)

# ---- Editor drawing & UI ----
def draw_bottom_bar():
    w, h = screen.get_size()
    rect = pygame.Rect(0, h - BOTTOM_BAR_H, w, BOTTOM_BAR_H)
    pygame.draw.rect(screen, (30, 30, 30), rect)
    pygame.draw.line(screen, (10,10,10), (0, h - BOTTOM_BAR_H), (w, h - BOTTOM_BAR_H), 2)
    # selected indicator
    subtype_list = tile_types.get(current_tile, [])
    idx = current_subtype_index.get(current_tile, 0)
    if subtype_list:
        name = subtype_list[idx][0]
    else:
        name = "?"
    mode = "ERASER" if eraser_mode else f"{'Floor' if current_tile=='1' else ('Wall' if current_tile=='2' else 'Furniture')} - {name}"
    txt = f"State: Editor    Selected: {mode}    Keys: 1/2/3 Switch    ←/→ Cycle subtype    E Toggle Eraser    S Save    L Load    Esc Pause"
    surf = SMALL_FONT.render(txt, True, (230,230,230))
    screen.blit(surf, (10, h - BOTTOM_BAR_H + 12))

def draw_editor():
    # background tint (subtle Backrooms ambience)
    screen.fill((230, 220, 140))

    # We'll draw previews on an overlay with alpha so transparent shapes work
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # draw grid (we'll draw all tiles within visible range)
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            gx, gy = grid_to_screen(c, r)
            # floor color defaults to light grey, or stored subtype
            if (c, r) in floor_tiles:
                sub = floor_tiles[(c, r)]
                color = tile_types["1"][sub][1]
            else:
                color = (230,230,230)
            draw_diamond(gx, gy, color)

    # draw props (sorted)
    for c, r, cat, sub in sorted(prop_tiles, key=lambda t: (t[0]+t[1], t[1], t[0])):
        gx, gy = grid_to_screen(c, r)
        sublist = tile_types.get(cat, [])
        name, color = sublist[sub] if sub < len(sublist) else ("?", (220,20,20))
        draw_prop(gx, gy, color, name)

    # draw walls last
    for c, r, cat, sub in sorted(wall_tiles, key=lambda t: (t[0]+t[1], t[1], t[0])):
        gx, gy = grid_to_screen(c, r)
        sublist = tile_types.get(cat, [])
        name, color = sublist[sub] if sub < len(sublist) else ("?", (220,20,20))
        draw_wall(gx, gy, color)

    # --- Preview: draw dragging preview line (translucent) on overlay ---
    if dragging and drag_start:
        try:
            mouse_col, mouse_row = clamp(*screen_to_grid(*pygame.mouse.get_pos()))
            x0, y0 = drag_start
            line = bresenham_line(x0, y0, mouse_col, mouse_row)
            for (c, r) in line:
                gx, gy = grid_to_screen(c, r)
                # draw translucent diamond on overlay
                pts = [(gx, gy), (gx + TILE_W//2, gy - TILE_H//2), (gx + TILE_W, gy), (gx + TILE_W//2, gy + TILE_H//2)]
                pygame.draw.polygon(overlay, (255, 200, 0, 110), pts)
                pygame.draw.polygon(overlay, (200, 140, 0, 180), pts, 1)
        except Exception:
            pass

    # --- Hover preview for wall placement (single tile) ---
    mx, my = pygame.mouse.get_pos()
    hover_col, hover_row = screen_to_grid(mx, my)
    hover_col, hover_row = clamp(hover_col, hover_row)
    if state == "editor" and current_tile == "2":
        # get color for current wall subtype
        subtype_idx = current_subtype_index["2"]
        subtype_list = tile_types.get("2", [])
        if subtype_list and 0 <= subtype_idx < len(subtype_list):
            base_color = subtype_list[subtype_idx][1]
        else:
            base_color = (200, 200, 200)
        # compute wall faces relative points like draw_wall but on overlay with alpha
        gx, gy = grid_to_screen(hover_col, hover_row)
        w, h = TILE_W, TILE_H
        top = [(gx, gy), (gx + w//2, gy - h//2), (gx + w, gy), (gx + w//2, gy + h//2)]
        left = [(gx, gy), (gx + w//2, gy + h//2), (gx + w//2, gy + h//2 + 60), (gx, gy + 60)]
        right = [(gx + w//2, gy + h//2), (gx + w, gy), (gx + w, gy + 60), (gx + w//2, gy + h//2 + 60)]
        # draw translucent faces
        pygame.draw.polygon(overlay, (*base_color, 120), top)
        pygame.draw.polygon(overlay, (*darken(base_color, 0.85), 110), left)
        pygame.draw.polygon(overlay, (*darken(base_color, 0.7), 100), right)
        pygame.draw.polygon(overlay, (0,0,0,150), top, 1)
        pygame.draw.polygon(overlay, (0,0,0,150), left, 1)
        pygame.draw.polygon(overlay, (0,0,0,150), right, 1)

    # blit overlay so previews appear above tiles but below UI
    screen.blit(overlay, (0,0))

    # draw cursor highlight centered under mouse
    mx, my = pygame.mouse.get_pos()
    gx, gy = grid_to_screen(*clamp(*screen_to_grid(mx, my)))
    pts = [(gx, gy), (gx + TILE_W//2, gy - TILE_H//2), (gx + TILE_W, gy), (gx + TILE_W//2, gy + TILE_H//2)]
    pygame.draw.polygon(screen, (255,255,0), pts, 2)

    # if dragging show preview line (legacy non-alpha fallback removed; handled above)
    # (kept for logic clarity but actual visual is in overlay)

    draw_bottom_bar()

# ---- Main app loop ----
def main_loop():
    global state, current_tile, current_subtype_index, eraser_mode
    global dragging, drag_start, drag_mode_category, fullscreen
    running = True

    # ensure initial load attempt
    try:
        load_map()
    except Exception:
        pass

    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # window resize - adjust origin to keep center-ish
            if event.type == pygame.VIDEORESIZE:
                w, h = event.size
                pygame.display.set_mode((w, h), pygame.RESIZABLE)
                # recompute origin x to keep it centered
                GRID_ORIGIN = (w // 2, GRID_ORIGIN[1])

            # Key events (global)
            if event.type == pygame.KEYDOWN:
                if state == "main_menu":
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif state == "settings":
                    if event.key == pygame.K_ESCAPE:
                        state = "main_menu"
                    elif event.key == pygame.K_m:
                        settings["music"] = not settings["music"]
                    elif event.key == pygame.K_k:
                        settings["sfx"] = not settings["sfx"]
                    elif event.key == pygame.K_v:
                        settings["vhs"] = not settings["vhs"]
                elif state == "editor":
                    # tile/category switching
                    if event.unicode in tile_types:
                        current_tile = event.unicode
                    elif event.key == pygame.K_LEFT:
                        current_subtype_index[current_tile] = (current_subtype_index[current_tile] - 1) % len(tile_types[current_tile])
                    elif event.key == pygame.K_RIGHT:
                        current_subtype_index[current_tile] = (current_subtype_index[current_tile] + 1) % len(tile_types[current_tile])
                    elif event.key == pygame.K_e:
                        eraser_mode = not eraser_mode
                    elif event.key == pygame.K_s:
                        save_map(SAVE_FILE)
                    elif event.key == pygame.K_l:
                        load_map(SAVE_FILE)
                    elif event.key == pygame.K_ESCAPE:
                        state = "pause"
                elif state == "pause":
                    if event.key == pygame.K_ESCAPE:
                        state = "editor"
                    # allow quick save/load while paused
                    elif event.key == pygame.K_s:
                        save_map(SAVE_FILE)
                    elif event.key == pygame.K_l:
                        load_map(SAVE_FILE)

            # Mouse clicks & drag logic depend on state
            if state == "main_menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    w, h = screen.get_size()
                    # menu button centers same as draw_main_menu
                    btn_centers = [(w//2, 180), (w//2, 260), (w//2, 340), (w//2, 420)]
                    btn_w, btn_h = 240, 56
                    for i, (cx, cy) in enumerate(btn_centers):
                        rect = button_rect(cx, cy, btn_w, btn_h)
                        if rect.collidepoint(event.pos):
                            if i == 0:  # Start / Editor
                                state = "editor"
                            elif i == 1:  # Load
                                load_map(SAVE_FILE)
                                state = "editor"
                            elif i == 2:  # Settings
                                state = "settings"
                            elif i == 3:  # Quit
                                running = False

            elif state == "settings":
                if event.type == pygame.KEYDOWN:
                    pass  # handled above

            elif state == "pause":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    w, h = screen.get_size()
                    centers = [(w//2, h//2 - 20), (w//2, h//2 + 50), (w//2, h//2 + 120)]
                    btn_w, btn_h = 220, 46
                    for i, (cx, cy) in enumerate(centers):
                        rect = button_rect(cx, cy, btn_w, btn_h)
                        if rect.collidepoint(event.pos):
                            if i == 0:
                                state = "editor"  # Resume
                            elif i == 1:
                                save_map(SAVE_FILE)
                            elif i == 2:
                                load_map(SAVE_FILE)

            elif state == "editor":
                # start dragging (left mouse down)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    col, row = screen_to_grid(*event.pos)
                    col, row = clamp(col, row)
                    dragging = True
                    drag_start = (col, row)
                    drag_mode_category = "erase" if eraser_mode else current_tile
                    # Place or erase tile immediately on click
                    if eraser_mode:
                        remove_at(col, row)
                    else:
                        if current_tile == "1":
                            place_floor(col, row, current_subtype_index["1"])
                        elif current_tile == "2":
                            place_wall(col, row, "2", current_subtype_index["2"])
                        elif current_tile == "3":
                            place_prop(col, row, "3", current_subtype_index["3"])
                # release -> apply line (this is already applied continuously during drag, but keep for full-line finalization)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                    col2, row2 = screen_to_grid(*event.pos)
                    col2, row2 = clamp(col2, row2)
                    x0, y0 = drag_start
                    line = bresenham_line(x0, y0, col2, row2)
                    for (c, r) in line:
                        if drag_mode_category == "erase":
                            remove_at(c, r)
                        elif drag_mode_category == "1":
                            place_floor(c, r, current_subtype_index["1"])
                        elif drag_mode_category == "2":
                            place_wall(c, r, "2", current_subtype_index["2"])
                        elif drag_mode_category == "3":
                            place_prop(c, r, "3", current_subtype_index["3"])
                    dragging = False
                    drag_start = None
                    drag_mode_category = None
                # right click single erase
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    col, row = screen_to_grid(*event.pos)
                    col, row = clamp(col, row)
                    remove_at(col, row)
            # end editor input

        # continuous single-click painting (when user holds left mouse, but hasn't started drag)
        if state == "editor":
            buttons = pygame.mouse.get_pressed()
            if buttons[0] and not dragging:
                # paint repeatedly (fast paint)
                col, row = screen_to_grid(*pygame.mouse.get_pos())
                col, row = clamp(col, row)
                if eraser_mode:
                    remove_at(col, row)
                else:
                    if current_tile == "1":
                        place_floor(col, row, current_subtype_index["1"])
                    elif current_tile == "2":
                        place_wall(col, row, "2", current_subtype_index["2"])
                    elif current_tile == "3":
                        place_prop(col, row, "3", current_subtype_index["3"])

        # ---- Render per-state ----
        if state == "main_menu":
            draw_main_menu()
        elif state == "settings":
            draw_settings_menu()
        elif state == "pause":
            # render editor under pause overlay to give context
            draw_editor()
            draw_pause_menu()
        elif state == "editor":
            draw_editor()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    safe_print("Save file path:", SAVE_FILE)
    main_loop()
