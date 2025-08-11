# Suppress deprecation noise before any imports
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module=r"pygame\.pkgdata")
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
print("MAZERS 1.1 public beta -----------------")
print("gathering map info")
print("gathered")
print("gathering chapter info")
print("gathered")
print("getting lvl data")
print("gathered")
print("--------------------")
print("thank you for downloading Mazers :)")
print("hope you enjoy the game its took a while to get this update out")
print("join the discord if you want to keep up with the development")
print("hope you have fun !!! ")
print("--------WARNING-------")
print("mazers is still in a public beta testing stage")
print("the game has a few rendering bugs and movement bugs")
print("but good news unlike the other version maps are actually kinda fun ")
print("but be prepared for the devils corridor >:D")
print("--------UPDATES-------")
print("Mapping is made easyier")
print("Ui changes ")
print("Maps are seperate files")
print("game is no longer open source")
print("removed colours due to them makeing mapping more confusing")



# Ensure pkg_resources is available (future-proof for setuptools changes)
try:
    import pkg_resources  # noqa: F401
except Exception:
    import subprocess, sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools<81"])
    except Exception:
        pass

import pygame, math, sys, os, tkinter as tk
from tkinter import filedialog

# === Settings ===
W, H = 800, 600
FOV = math.pi / 3
RAYS, DEPTH = 160, 1000
SCALE, STEP = 64, 5
ROT_SPEED = 0.05

# === Colors ===
WHITE, GRAY = (240, 240, 240), (120, 120, 120)
BG, SKY, FLOOR = (22, 22, 28), (30, 30, 40), (35, 40, 35)
ACCENT = (80, 220, 80)

# === Storage ===
PACK_DIR = "map_packs"
COMPLETED_FILE = os.path.join(PACK_DIR, "completed.txt")

# ---------------- Utilities ----------------
def ensure_dir():
    os.makedirs(PACK_DIR, exist_ok=True)

def list_packs():
    return sorted([f for f in os.listdir(PACK_DIR) if f.lower().endswith(".txt") and f != "completed.txt"])

def import_pack():
    root = tk.Tk(); root.withdraw()
    path = filedialog.askopenfilename(title="Select Map Pack", filetypes=[("Text files", "*.txt")])
    try: root.update()
    except Exception: pass
    root.destroy()
    if not path: return None
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    dest = os.path.join(PACK_DIR, name)
    i = 1
    while os.path.exists(dest):
        dest = os.path.join(PACK_DIR, f"{base}_{i}{ext}"); i += 1
    try:
        with open(path, "rb") as in_f, open(dest, "wb") as out_f:
            out_f.write(in_f.read())
        return os.path.basename(dest)
    except Exception:
        return None

def load_maps(file_name):
    full = os.path.join(PACK_DIR, file_name)
    with open(full, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    blocks = [b for b in raw.split("\n\n") if b.strip()]
    maps = []
    for b in blocks:
        lines = [ln.rstrip("\r\n") for ln in b.splitlines() if ln.strip()]
        if not lines: continue
        width = max(len(ln) for ln in lines)
        lines = [ln.ljust(width, "#") for ln in lines]
        maps.append([list(row) for row in lines])
    if not maps: raise ValueError("Empty or invalid map pack.")
    return maps

def load_completed():
    if not os.path.exists(COMPLETED_FILE): return set()
    with open(COMPLETED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def mark_completed(pack_name):
    completed = load_completed()
    if pack_name not in completed:
        with open(COMPLETED_FILE, "a", encoding="utf-8") as f:
            f.write(pack_name + "\n")

def find_player(map_data):
    for y, row in enumerate(map_data):
        for x, t in enumerate(row):
            if t == "P":
                return x * SCALE + SCALE // 2, y * SCALE + SCALE // 2
    return SCALE + SCALE // 2, SCALE + SCALE // 2

# ---------------- Rendering ----------------
def render(screen, px, py, angle, map_data):
    screen.fill(SKY)
    pygame.draw.rect(screen, FLOOR, (0, H // 2, W, H // 2))
    col_w = max(1, W // RAYS)
    for r in range(RAYS):
        a = angle - FOV / 2 + FOV * r / RAYS
        sin_a, cos_a = math.sin(a), math.cos(a)
        for d in range(1, DEPTH):
            x = int((px + d * cos_a) / SCALE)
            y = int((py + d * sin_a) / SCALE)
            if 0 <= y < len(map_data) and 0 <= x < len(map_data[0]):
                tile = map_data[y][x]
                if tile in "#G":
                    depth = d * math.cos(a - angle)
                    h = min(int(35000 / (depth + 0.0001)), H)
                    color = ACCENT if tile == "G" else (200 - min(int(depth / 4), 160),) * 3
                    pygame.draw.rect(screen, color, (r * col_w, H // 2 - h // 2, col_w, h))
                    break
            else:
                break

def draw_text(screen, lines, y0=10, color=WHITE):
    font = pygame.font.SysFont("consolas", 20)
    y = y0
    for text in lines:
        surf = font.render(text, True, color)
        screen.blit(surf, (10, y))
        y += 26

def level_complete_screen(screen, level_num, final=False, pack_name=""):
    font = pygame.font.SysFont("consolas", 32)
    small = pygame.font.SysFont("consolas", 20)
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    title_txt = f"Level {level_num} Complete!" if not final else f"Pack Complete: {pack_name}"
    sub_txt = "Press Enter to continue..."
    title = font.render(title_txt, True, ACCENT)
    sub = small.render(sub_txt, True, WHITE)
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return
        screen.blit(overlay, (0, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 30))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))
        pygame.display.flip()
        clock.tick(60)

# ---------------- Game Loop ----------------
def game(screen, pack_name, maps):
    clock = pygame.time.Clock()
    lvl = 0
    angle = 0.0
    map_data = maps[lvl]
    px, py = find_player(map_data)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return "menu"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: angle -= ROT_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: angle += ROT_SPEED
        move = STEP if (keys[pygame.K_UP] or keys[pygame.K_w]) else (-STEP if (keys[pygame.K_DOWN] or keys[pygame.K_s]) else 0)
        if move:
            dx, dy = math.cos(angle) * move, math.sin(angle) * move
            tx, ty = int((px + dx) / SCALE), int((py + dy) / SCALE)
            if 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0]) and map_data[ty][tx] != "#":
                px += dx; py += dy

        gx, gy = int(px / SCALE), int(py / SCALE)
        if 0 <= gy < len(map_data) and 0 <= gx < len(map_data[0]) and map_data[gy][gx] == "G":
            if lvl + 1 >= len(maps):
                mark_completed(pack_name)
                level_complete_screen(screen, lvl + 1, final=True, pack_name=pack_name)
                return "menu"
            level_complete_screen(screen, lvl + 1)
            lvl += 1
            map_data = maps[lvl]
            px, py = find_player(map_data)
            angle = 0.0

        render(screen, px, py, angle, map_data)
        draw_text(screen, [
            f"Mazers 1.1 — {pack_name}",
            f"Level {lvl + 1}/{len(maps)}",
            "Arrows/WASD • Esc to Menu"
        ], 10, ACCENT)

        pygame.display.flip()
        clock.tick(60)

# ---------------- Menu UI ----------------
def menu(screen):
    clock = pygame.time.Clock()
    title_f = pygame.font.SysFont("consolas", 36)
    small = pygame.font.SysFont("consolas", 20)
    info, info_time = "", 0
    sel = 0
    while True:
        packs = list_packs()
        completed = load_completed()
        sel = (sel % len(packs)) if packs else 0

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit", None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "quit", None
                if e.key == pygame.K_UP and packs: sel = (sel - 1) % len(packs)
                elif e.key == pygame.K_DOWN and packs: sel = (sel + 1) % len(packs)
                elif e.key == pygame.K_RETURN and packs: return "play", packs[sel]
                elif e.key in (pygame.K_i, pygame.K_a):
                    name = import_pack()
                    info = f"Imported: {name}" if name else "Import failed."
                    info_time = pygame.time.get_ticks()

        screen.fill(BG)
        title = title_f.render("MAZERS 1.1", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 40))

        hint = small.render("Enter: Play • ↑↓: Select • I/A: Import Pack • Esc: Quit", True, GRAY)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, 100))

        y0 = 200
        if packs:
            for i, p in enumerate(packs):
                color = ACCENT if i == sel else WHITE
                label = p + (" ✅" if p in completed else "")
                lbl = small.render(label, True, color)
                screen.blit(lbl, (W // 2 - lbl.get_width() // 2, y0 + i * 28))
        else:
            msg = small.render("No map packs yet. Press I to import one.", True, GRAY)
            screen.blit(msg, (W // 2 - msg.get_width() // 2, y0))

        if info and pygame.time.get_ticks() - info_time < 3000:
            note = small.render(info, True, ACCENT)
            screen.blit(note, (W // 2 - note.get_width() // 2, H - 40))

        pygame.display.flip()
        clock.tick(60)

# ---------------- Entry Point ----------------
def main():
    pygame.init()
    pygame.display.set_caption("Mazers 1.1")
    screen = pygame.display.set_mode((W, H))
    ensure_dir()

    while True:
        action, payload = menu(screen)
        if action == "quit":
            pygame.quit(); sys.exit()
        elif action == "play":
            try:
                maps = load_maps(payload)
            except Exception as e:
                clock = pygame.time.Clock()
                small = pygame.font.SysFont("consolas", 20)
                msg = small.render(f"Failed to load: {e}", True, WHITE)
                t0 = pygame.time.get_ticks()
                while pygame.time.get_ticks() - t0 < 2000:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                    screen.fill(BG)
                    screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 10))
                    pygame.display.flip()
                    clock.tick(60)
                continue

            result = game(screen, payload, maps)
            if result == "quit":
                pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()