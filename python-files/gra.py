"""
riverraid_retro.py
Retro River Raid — Atari-like style
- proceduralne segmenty rzeki (zmienna szerokość, proste brzegi)
- więcej paliwa na mapie
- dolny panel HUD: score, fuel bar, lives, time
- dźwięki generowane w pamięci (square, noise, gliss)
Wymagania: pygame
"""
import pygame
import random
import math
import sys
import io
import wave
import struct
from collections import deque
from time import perf_counter

# ---------- dźwięk (generowany w pamięci) ----------
SAMPLE_RATE = 22050
SAMPLE_WIDTH = 2  # 16-bit
CHANNELS = 1

# Pre-init mixer for better perf
try:
    pygame.mixer.pre_init(SAMPLE_RATE, -16, CHANNELS, 512)
except Exception:
    pass
pygame.init()

def make_wave_bytes_from_samples(samples, sample_rate=SAMPLE_RATE):
    """Z given list/iterable of floats [-1..1] produce WAV bytes 16-bit mono."""
    max_amp = (2 ** (SAMPLE_WIDTH * 8 - 1)) - 1
    frames = bytearray()
    for s in samples:
        val = int(max_amp * clamp(s, -1.0, 1.0))
        frames.extend(struct.pack('<h', val))
    bio = io.BytesIO()
    wf = wave.open(bio, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(sample_rate)
    wf.writeframes(frames)
    wf.close()
    bio.seek(0)
    return bio.read()

def clamp(v, a, b):
    return max(a, min(b, v))

def gen_square(freq=440.0, duration=0.12, volume=0.5):
    n = int(SAMPLE_RATE * duration)
    samples = []
    period = SAMPLE_RATE / freq
    for i in range(n):
        v = 1.0 if (i % period) < (period/2) else -1.0
        samples.append(v * volume)
    return make_wave_bytes_from_samples(samples)

def gen_noise(duration=0.2, volume=0.6):
    import random
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        env = 1.0 - (i / n)
        samples.append((random.uniform(-1,1)) * volume * env)
    return make_wave_bytes_from_samples(samples)

def gen_gliss(start=600, end=1200, duration=0.16, volume=0.35):
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / n
        freq = start + (end-start) * t
        samples.append(math.sin(2*math.pi*freq*(i/SAMPLE_RATE)) * volume)
    return make_wave_bytes_from_samples(samples)

def sound_from_wav_bytes(wav_bytes):
    try:
        return pygame.mixer.Sound(file=io.BytesIO(wav_bytes))
    except Exception:
        # fallback — maybe older pygame doesn't accept file=BytesIO
        return None

# create sounds (retro)
try:
    snd_shoot = sound_from_wav_bytes(gen_square(800, 0.08, 0.4))
    snd_explosion = sound_from_wav_bytes(gen_noise(0.24, 0.7))
    snd_pickup = sound_from_wav_bytes(gen_gliss(700, 1200, 0.12, 0.35))
    snd_crash = sound_from_wav_bytes(gen_square(160, 0.28, 0.45))
except Exception:
    snd_shoot = snd_explosion = snd_pickup = snd_crash = None

# ---------- konfiguracja gry ----------
WIDTH, HEIGHT = 480, 640
FPS = 60

# retro colors
COL_BG = (12, 12, 24)
COL_RIVER = (12, 56, 148)
COL_BANK = (26, 130, 26)
COL_SAND = (200, 180, 110)
COL_PLANE = (240, 220, 40)
COL_BULLET = (255, 240, 140)
COL_SHIP = (160, 40, 40)
COL_BRIDGE = (120, 90, 60)
COL_FUEL = (10, 150, 20)
COL_PANEL = (90, 90, 90)
COL_TEXT = (230, 230, 230)

# river parameters (segment-based, straight centerline)
RIVER_CENTER = WIDTH // 2
SEG_H = 14
NUM_SEGS = (HEIGHT // SEG_H) + 12
RIVER_MIN_HALF = 70
RIVER_MAX_HALF = 200

SCROLL_SPEED = 3  # how many segments per frame (we'll update N times per frame)
SPAWN_BASE_SHIP = 70
SPAWN_BASE_BRIDGE = 600
SPAWN_BASE_FUEL = 160

# ---------- River (segmenty) ----------
class River:
    def __init__(self):
        self.segs = deque()
        center = RIVER_CENTER
        half = (RIVER_MIN_HALF + RIVER_MAX_HALF)//2
        for _ in range(NUM_SEGS):
            self.segs.append((center, half))
        # velocities for smooth random walk
        self.cvel = 0.0
        self.hvel = 0.0

    def update_once(self):
        # pop bottom, append new top
        self.segs.popleft()
        pc, ph = self.segs[-1]
        # random walk for center and half-width (limited so river stays inside)
        self.cvel += random.uniform(-1.0, 1.0)
        self.cvel *= 0.85
        newc = int(pc + self.cvel)
        margin = 30
        newc = clamp(newc, margin + RIVER_MAX_HALF, WIDTH - margin - RIVER_MAX_HALF)
        self.hvel += random.uniform(-1.2, 1.2)
        self.hvel *= 0.80
        newh = int(ph + self.hvel)
        newh = clamp(newh, RIVER_MIN_HALF, RIVER_MAX_HALF)
        self.segs.append((newc, newh))

    def update(self):
        # scroll SCROLL_SPEED segments per frame to simulate movement
        for _ in range(SCROLL_SPEED):
            self.update_once()

    def draw(self, surf):
        # draw banks and river as polygons (retro: solid blocks, no smooth gradient)
        left_pts = []
        right_pts = []
        seg_list = list(self.segs)
        # map segments to vertical positions from bottom to top
        for i, (c, h) in enumerate(reversed(seg_list)):
            y = HEIGHT - i*SEG_H
            left_pts.append((c - h, y))
            right_pts.append((c + h, y))
        # create bank polys (simple narrow strips next to river)
        river_poly = left_pts + right_pts[::-1]
        # draw background
        surf.fill(COL_BG)
        # draw sand beyond banks
        # left sand polygon (from x=0 to left bank)
        left_polygon = [(0, HEIGHT), (0, 0)] + left_pts + [(0, HEIGHT)]
        right_polygon = [(WIDTH, HEIGHT), (WIDTH, 0)] + right_pts + [(WIDTH, HEIGHT)]
        pygame.draw.polygon(surf, COL_SAND, left_polygon)
        pygame.draw.polygon(surf, COL_SAND, right_polygon)
        # draw river mid
        pygame.draw.polygon(surf, COL_RIVER, river_poly)
        # draw banks rim (thin)
        for i in range(0, len(left_pts), 6):
            lx, ly = left_pts[i]
            rx, ry = right_pts[i]
            pygame.draw.rect(surf, COL_BANK, (lx-6, ly-2, 6, 4))
            pygame.draw.rect(surf, COL_BANK, (rx, ry-2, 6, 4))

    def bounds_at_y(self, y):
        # find segment index corresponding to y
        idx = int((HEIGHT - y) / SEG_H)
        idx = clamp(idx, 0, len(self.segs)-1)
        c, h = list(self.segs)[idx]
        return c - h, c + h

    def inside(self, x, y):
        l, r = self.bounds_at_y(y)
        return (l + 8) < x < (r - 8)

# ---------- Sprites (retro look) ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, river):
        super().__init__()
        self.river = river
        # retro plane surface small
        w, h = 28, 20
        self.image = pygame.Surface((w,h))
        self.image.set_colorkey((0,0,0))
        self._draw_retro_plane()
        self.rect = self.image.get_rect(center=(RIVER_CENTER, HEIGHT - 140))
        self.speed = 4
        self.lives = 3
        self.invuln = 0

    def _draw_retro_plane(self):
        img = self.image
        img.fill((0,0,0))
        # simple blocky plane: body + wings
        pygame.draw.rect(img, COL_PLANE, (10,2,8,16))   # fuselage
        pygame.draw.rect(img, COL_PLANE, (2,8,24,4))    # wings
        pygame.draw.rect(img, (30,30,30), (12,6,4,4))   # cockpit dark

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        newx = self.rect.centerx + dx
        l, r = self.river.bounds_at_y(self.rect.centery)
        newx = clamp(newx, l + 16, r - 16)
        self.rect.centerx = newx
        if self.invuln > 0:
            self.invuln -= 1

    def shoot(self):
        b = Bullet(self.rect.centerx, self.rect.top - 4)
        all_sprites.add(b); bullets.add(b)
        if snd_shoot:
            try: snd_shoot.play()
            except: pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3,8))
        self.image.fill(COL_BULLET)
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, size=1.0):
        super().__init__()
        w = int(40 * size)
        h = int(14 * size)
        self.image = pygame.Surface((w+8, h+6))
        self.image.set_colorkey((0,0,0))
        self._draw_ship(w,h)
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = random.uniform(0.6, 1.6)
        self.size = size

    def _draw_ship(self, w, h):
        img = self.image
        img.fill((0,0,0))
        pygame.draw.rect(img, COL_SHIP, (0,4,w,h-4))
        # bow as triangle (simple)
        pygame.draw.polygon(img, COL_SHIP, [(w-1,4),(w+6,h//2+3),(w-1,h+1)])
        pygame.draw.rect(img, (30,30,30), (4,2,w//3,4))

    def update(self):
        # ships move 'down' (in screen coords) since river moves up
        self.rect.y += self.speed + SCROLL_SPEED
        # small sway
        self.rect.x += math.sin((self.rect.y/20.0) + (pygame.time.get_ticks()/300.0)) * 0.4
        if self.rect.top > HEIGHT + 30:
            self.kill()

class Bridge(pygame.sprite.Sprite):
    def __init__(self, centerx, y, width):
        super().__init__()
        h = 18
        self.image = pygame.Surface((width, h))
        self.image.set_colorkey((0,0,0))
        self.image.fill((0,0,0))
        pygame.draw.rect(self.image, COL_BRIDGE, (0,4,width,8))
        # pillars
        for i in range(3):
            px = int(width*(0.15 + i*0.33))
            pygame.draw.rect(self.image, (60,40,30), (px,10,6,8))
        self.rect = self.image.get_rect(center=(centerx,y))

    def update(self):
        self.rect.y += SCROLL_SPEED
        if self.rect.top > HEIGHT + 20:
            self.kill()

class Fuel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12,16))
        self.image.set_colorkey((0,0,0))
        self.image.fill((0,0,0))
        # retro fuel can (small rectangle with "F" like block)
        pygame.draw.rect(self.image, COL_FUEL, (2,2,8,12))
        pygame.draw.rect(self.image, (0,0,0), (5,0,2,4))
        # add letter-like pixel block "F"
        pygame.draw.rect(self.image, (255,255,255), (3,3,6,2))
        pygame.draw.rect(self.image, (255,255,255), (3,6,4,2))
        pygame.draw.rect(self.image, (255,255,255), (3,9,6,2))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 1

    def update(self):
        self.rect.y += self.speed + SCROLL_SPEED
        if self.rect.top > HEIGHT + 10:
            self.kill()

# ---------- utility spawn functions ----------
def spawn_ship(river):
    # spawn near top within river bounds
    center, half = list(river.segs)[-6]
    x = random.randint(center - half + 20, center + half - 20)
    y = -24
    s = Ship(x,y,size=random.choice([0.9,1.0,1.2]))
    all_sprites.add(s); ships.add(s)

def spawn_bridge(river):
    center, half = list(river.segs)[-7]
    width = int((half*2) * random.uniform(0.55, 0.95))
    b = Bridge(center, -18, width)
    all_sprites.add(b); bridges.add(b)

def spawn_fuel(river):
    center, half = list(river.segs)[-8]
    x = random.randint(center - half + 20, center + half - 20)
    f = Fuel(x, -18)
    all_sprites.add(f); fuels.add(f)

# ---------- HUD panel ----------
def draw_panel(surf, score, fuel, lives, elapsed):
    panel_h = 48
    pygame.draw.rect(surf, COL_PANEL, (0, HEIGHT-panel_h, WIDTH, panel_h))
    # draw separators retro style
    pygame.draw.line(surf, (140,140,140), (0, HEIGHT-panel_h), (WIDTH, HEIGHT-panel_h), 2)
    # text
    txt_score = small_font.render(f"SCORE: {score}", True, COL_TEXT)
    txt_lives = small_font.render(f"LIVES: {lives}", True, COL_TEXT)
    txt_time = small_font.render(f"TIME: {int(elapsed)}s", True, COL_TEXT)
    surf.blit(txt_score, (12, HEIGHT-panel_h+6))
    surf.blit(txt_time, (200, HEIGHT-panel_h+6))
    surf.blit(txt_lives, (350, HEIGHT-panel_h+6))
    # fuel bar (retro small blocks)
    bar_x = 12; bar_y = HEIGHT-panel_h+28
    bar_w = 200; bar_h = 10
    pygame.draw.rect(surf, (40,40,40), (bar_x, bar_y, bar_w, bar_h))
    # filled portion
    fill_w = int(bar_w * (fuel/100.0))
    if fill_w > 0:
        pygame.draw.rect(surf, (250,200,60), (bar_x, bar_y, fill_w, bar_h))
    # border
    pygame.draw.rect(surf, (220,220,220), (bar_x, bar_y, bar_w, bar_h), 1)

# ---------- main game loop and menu ----------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RiverRaid Retro")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)
small_font = pygame.font.SysFont("Consolas", 16)
big_font = pygame.font.SysFont("Consolas", 36)

def show_menu(last_scores):
    waiting = True
    while waiting:
        screen.fill(COL_BG)
        title = big_font.render("RIVER RAID (retro)", True, (240,220,80))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        hint = font.render("SPACJA - GRAJ   |   ← → - RUCH   |   ESC - Wyjście", True, COL_TEXT)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 160))
        # last 3 scores
        sub = font.render("Ostatnie wyniki:", True, COL_TEXT)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 220))
        for i, sc in enumerate(list(last_scores)[-3:][::-1]):
            s = font.render(f"{i+1}. {sc}", True, (150,220,150))
            screen.blit(s, (WIDTH//2 - s.get_width()//2, 260 + i*26))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    waiting = False
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

def game_loop(last_scores):
    global all_sprites, bullets, ships, bridges, fuels
    # sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    ships = pygame.sprite.Group()
    bridges = pygame.sprite.Group()
    fuels = pygame.sprite.Group()

    # world
    river = River()
    player = Player(river)
    all_sprites.add(player)

    score = 0
    fuel = 100
    elapsed_start = perf_counter()
    spawn_timer = 0
    running = True

    # increase fuel density: smaller spawn base -> more frequent
    ship_rate = SPAWN_BASE_SHIP
    bridge_rate = SPAWN_BASE_BRIDGE
    fuel_rate = SPAWN_BASE_FUEL // 2  # more fuel

    while running:
        dt = clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    player.shoot()
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # update world: scroll river
        river.update()

        spawn_timer += 1
        # spawn logic with randomness
        if spawn_timer % max(6, int(ship_rate * random.uniform(0.7,1.4))) == 0 and random.random() < 0.9:
            spawn_ship(river)
        if spawn_timer % max(200, int(bridge_rate * random.uniform(0.8,1.2))) == 0 and random.random() < 0.5:
            spawn_bridge(river)
        if spawn_timer % max(80, int(fuel_rate * random.uniform(0.7,1.3))) == 0 and random.random() < 0.85:
            spawn_fuel(river)

        # update sprites
        all_sprites.update()

        # bullet hits ship
        hits = pygame.sprite.groupcollide(ships, bullets, True, True)
        for h in hits:
            score += int(200 * getattr(h, 'size', 1.0))
            if snd_explosion:
                try: snd_explosion.play()
                except: pass

        # bullet hits bridge -> destroy bridge
        hitsb = pygame.sprite.groupcollide(bridges, bullets, True, True)
        for h in hitsb:
            score += 350
            if snd_explosion:
                try: snd_explosion.play()
                except: pass

        # player collision with ships/bridges
        if player.invuln == 0:
            if pygame.sprite.spritecollideany(player, ships) or pygame.sprite.spritecollideany(player, bridges):
                player.lives -= 1
                player.invuln = FPS * 2
                if snd_crash:
                    try: snd_crash.play()
                    except: pass
                if player.lives <= 0:
                    running = False

        # pick up fuel
        grabs = pygame.sprite.spritecollide(player, fuels, True)
        for g in grabs:
            fuel = min(100, fuel + 30)
            score += 40
            if snd_pickup:
                try: snd_pickup.play()
                except: pass

        # distance/time rewards and fuel consumption
        # consume fuel ~1 per second
        if pygame.time.get_ticks() % 1000 < 16:
            fuel -= 1
            score += 2
        if fuel <= 0:
            running = False

        # ensure player inside river - small penalty nudging
        if not river.inside(player.rect.centerx, player.rect.centery):
            l, r = river.bounds_at_y(player.rect.centery)
            target = (l + r) // 2
            player.rect.centerx += clamp(target - player.rect.centerx, -6, 6)
            score = max(0, score - 8)

        # drawing
        river.draw(screen)
        # draw sprites above river
        all_sprites.draw(screen)
        # HUD panel bottom
        elapsed = perf_counter() - elapsed_start
        draw_panel(screen, score, fuel, player.lives, elapsed)
        pygame.display.flip()

    return score

def main():
    last_scores = deque(maxlen=10)
    while True:
        show_menu(last_scores)
        sc = game_loop(last_scores)
        last_scores.append(sc)
        # simple game over screen
        over_time = True
        t0 = perf_counter()
        while over_time:
            clock.tick(FPS)
            screen.fill(COL_BG)
            txt = big_font.render("GAME OVER", True, (220,80,80))
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 160))
            s = font.render(f"Wynik: {sc}", True, COL_TEXT)
            screen.blit(s, (WIDTH//2 - s.get_width()//2, 230))
            cont = font.render("SPACJA - graj ponownie   |   ESC - wyjście", True, COL_TEXT)
            screen.blit(cont, (WIDTH//2 - cont.get_width()//2, 300))
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        over_time = False
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
