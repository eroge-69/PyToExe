#!/usr/bin/env python3
"""
untitled platformer — Pygame / Pygame-CE
Now with:
- Main Menu (title: "untitled platformer")
- Level Select (main + custom)
- In-game Level Editor / Creator with a unique object palette
- You can augment main levels; changes persist for this session
- Pause overlay has clickable buttons: Resume / Back to Menu
- Background music for menu & gameplay (+ M to mute), optional click sound

Controls (Play)
- Move: A/D or ←/→
- Jump: W / ↑ / Space (coyote + buffer + variable)
- Wall-slide & Wall-jump
- Dash (8-direction): Shift + direction (WASD/Arrows). None = forward.
- Drop through semisolid: S / ↓
- Pause: Esc
- Restart: R
- Level select (paused): 1..9
- M: mute/unmute music (global)

Editor (shown in HUD)
- Left click: place  |  Right click: delete (of active tool)  |  Scroll or [ ]: cycle tool
- T: cycle tool category panel | G: toggle grid
- For Moving Platforms: -/= speed (H/V orientation by tool)
- For Spring: -/= power | For Wind: -/= size | For Enemy: -/= patrol width
- F2: Playtest | F6: Save edits | Esc: back to menu

Audio files (optional, place next to this .py or in ./assets/):
- menu_music.ogg / .mp3
- game_music.ogg / .mp3   (fallback names also supported: bg_music.*)
- click.wav
"""

import sys, math, random, os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Center window
os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

# ---- robust pygame import (Windows tip for 3.12) ----
try:
    import pygame
except Exception:
    import traceback, struct
    print("\nFailed to import pygame for THIS Python interpreter.\n", flush=True)
    print("Python:", sys.version)
    print("Bitness:", f"{8*struct.calcsize('P')} bit")
    print("\nWindows tip: install Python 3.12 and run with:")
    print("  py -3.12 -m pip install --upgrade pip setuptools wheel")
    print("  py -3.12 -m pip install --only-binary=:all: pygame")
    print("  py -3.12 untitled_platformer_full.py\n")
    traceback.print_exc()
    sys.exit(1)

# ---------------- Config ----------------
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 36

GRAVITY = 0.72
MAX_X = 6.6
GROUND_ACCEL = 0.95
AIR_ACCEL = 0.52
GROUND_FRICTION = 0.82
AIR_DRAG = 0.94
JUMP_V = -12.6
COYOTE = 8
JUMP_BUFFER = 8

# Wall tech
WALL_SLIDE_GRAVITY = 0.28
WALL_JUMP_VY = -12.0
WALL_JUMP_VX = 7.3
WALL_COYOTE = 10

# Dash
DASH_SPEED = 13.0
DASH_TIME = 9
DASH_COOLDOWN = 36

# Colors
WHITE=(240,240,240); BLACK=(18,18,18); GREY=(90,90,90)
RED=(230,76,60); YELLOW=(255,214,10); ORANGE=(255,149,5)
CYAN=(50,219,240); PURPLE=(155,89,182); GREEN=(140,198,63)
BLUE=(74,144,226); SKY1=(22,24,35); SKY2=(10,10,14)

def clamp(v, lo, hi): return lo if v<lo else hi if v>hi else v
def rect_from_grid(x,y,w=1,h=1): return pygame.Rect(x*TILE, y*TILE, w*TILE, h*TILE)

# --------------- Entities ---------------
@dataclass
class Platform:
    rect: pygame.Rect
    semisolid: bool=False
    moving: bool=False
    vel: pygame.Vector2=field(default_factory=lambda: pygame.Vector2())
    bounds: Optional[pygame.Rect]=None
    disappear_cycle: Optional[int]=None  # frames
    def update(self):
        if self.moving and self.bounds:
            self.rect.x += int(self.vel.x)
            self.rect.y += int(self.vel.y)
            if not self.bounds.contains(self.rect):
                if self.rect.left<self.bounds.left or self.rect.right>self.bounds.right:
                    self.vel.x*=-1; self.rect.x+=int(self.vel.x*2)
                if self.rect.top<self.bounds.top or self.rect.bottom>self.bounds.bottom:
                    self.vel.y*=-1; self.rect.y+=int(self.vel.y*2)
    def active(self, frame)->bool:
        if self.disappear_cycle is None: return True
        return (frame % self.disappear_cycle) < (self.disappear_cycle//2)

@dataclass
class Hazard: rect: pygame.Rect

@dataclass
class Spring: rect: pygame.Rect; power: float=-16.0

@dataclass
class Enemy:
    rect: pygame.Rect; dir:int=1; speed:float=2.0
    patrol: Optional[pygame.Rect]=None
    def update(self):
        self.rect.x += int(self.speed*self.dir)
        if self.patrol:
            if self.rect.left<=self.patrol.left or self.rect.right>=self.patrol.right:
                self.dir*=-1

@dataclass
class Coin: rect: pygame.Rect; taken: bool=False
@dataclass
class Key: rect: pygame.Rect; taken: bool=False
@dataclass
class Gate: rect: pygame.Rect; locked: bool=True
@dataclass
class Checkpoint: rect: pygame.Rect
@dataclass
class Exit: rect: pygame.Rect
@dataclass
class Wind: rect: pygame.Rect; force: float=0.35; low_grav: bool=False

@dataclass
class Player:
    rect: pygame.Rect
    vel: pygame.Vector2=field(default_factory=lambda: pygame.Vector2())
    on_ground: bool=False
    coyote:int=0; jump_buf:int=0
    facing:int=1
    spawn: Tuple[int,int]=(0,0)
    dashing: int=0
    dash_cd: int=0
    wall_dir: int=0
    wall_coyote: int=0
    alive: bool=True

# --------------- Level ------------------
@dataclass
class Level:
    name: str
    start: Tuple[int,int]
    platforms: List[Platform]
    hazards: List[Hazard]
    springs: List[Spring]
    enemies: List[Enemy]
    coins: List[Coin]
    key: Optional[Key]
    gate: Optional[Gate]
    checkpoints: List[Checkpoint]
    exits: List[Exit]
    winds: List[Wind]
    bg_top: Tuple[int,int,int]=(22,24,35)
    bg_bottom: Tuple[int,int,int]=(10,10,14)
    tip: str=""

# --------------- Built-in Levels -----------------
def builtin_levels()->List[Level]:
    L=[]
    # Level 1
    plats=[
        Platform(rect_from_grid(0,14,40,2)),
        Platform(rect_from_grid(6,11,4,1)),
        Platform(rect_from_grid(12,9,4,1)),
        Platform(rect_from_grid(18,7,4,1)),
        Platform(rect_from_grid(24,9,4,1)),
        Platform(rect_from_grid(30,11,4,1)),
    ]
    hazards=[Hazard(rect_from_grid(10,13,2,1)), Hazard(rect_from_grid(21,13,2,1))]
    coins=[Coin(rect_from_grid(7,10)), Coin(rect_from_grid(13,8)),
           Coin(rect_from_grid(19,6)), Coin(rect_from_grid(25,8)), Coin(rect_from_grid(31,10))]
    key=Key(rect_from_grid(36,12))
    gate=Gate(rect_from_grid(38,12,1,2), locked=True)
    L.append(Level("1. First Steps",(2*TILE,12*TILE), plats, hazards, [], [], coins, key, gate,
                   [Checkpoint(rect_from_grid(3,13))], [Exit(rect_from_grid(39,11))], [],
                   SKY1, SKY2, "Wall-jump & dash are enabled."))

    # Level 2
    plats=[
        Platform(rect_from_grid(0,14,40,2)),
        Platform(rect_from_grid(6,11,4,1), moving=True, vel=pygame.Vector2(1.3,0), bounds=rect_from_grid(6,11,10,1)),
        Platform(rect_from_grid(18,10,4,1), moving=True, vel=pygame.Vector2(-1.5,0), bounds=rect_from_grid(12,10,10,1)),
        Platform(rect_from_grid(28,8,4,1), moving=True, vel=pygame.Vector2(0,-1.2), bounds=pygame.Rect(28*TILE,6*TILE,4*TILE,4*TILE)),
    ]
    L.append(Level("2. Conveyors of Fate",(2*TILE,12*TILE), plats, [Hazard(rect_from_grid(10,13,6,1))],
                   [], [], [Coin(rect_from_grid(7,10)), Coin(rect_from_grid(19,9)), Coin(rect_from_grid(29,7))],
                   None, None, [Checkpoint(rect_from_grid(3,13)), Checkpoint(rect_from_grid(22,13))],
                   [Exit(rect_from_grid(35,12))], [], (18,24,32), (12,12,16), "Ride the rhythm."))

    # Level 3
    plats=[
        Platform(rect_from_grid(0,14,40,2)),
        Platform(rect_from_grid(6,12,5,1)),
        Platform(rect_from_grid(14,10,5,1)),
        Platform(rect_from_grid(22,8,5,1)),
        Platform(rect_from_grid(30,10,5,1)),
    ]
    springs=[Spring(rect_from_grid(16,9), power=-17.5), Spring(rect_from_grid(32,9), power=-16.0)]
    enemies=[Enemy(rect_from_grid(6,11,2,1), patrol=rect_from_grid(6,11,5,1)),
             Enemy(rect_from_grid(22,7,2,1), patrol=rect_from_grid(22,7,5,1))]
    L.append(Level("3. Bounce & Weave",(2*TILE,12*TILE), plats, [], springs, enemies,
                   [Coin(rect_from_grid(7,11)), Coin(rect_from_grid(15,9)), Coin(rect_from_grid(31,9))],
                   Key(rect_from_grid(36,12)), Gate(rect_from_grid(38,12,1,2), locked=True),
                   [Checkpoint(rect_from_grid(3,13)), Checkpoint(rect_from_grid(20,13))],
                   [Exit(rect_from_grid(39,11))], [], (22,18,28), (12,10,12), "Springs boost; watch patrols!"))

    # Level 4
    plats=[
        Platform(rect_from_grid(0,14,40,2)),
        Platform(rect_from_grid(8,12,4,1), disappear_cycle=120),
        Platform(rect_from_grid(14,10,4,1), disappear_cycle=90),
        Platform(rect_from_grid(20,8,4,1), disappear_cycle=60),
        Platform(rect_from_grid(26,10,4,1), disappear_cycle=90),
        Platform(rect_from_grid(12,6,3,1), semisolid=True),
        Platform(rect_from_grid(18,5,3,1), semisolid=True),
    ]
    L.append(Level("4. Blink & Breeze",(2*TILE,12*TILE), plats,
                   [Hazard(rect_from_grid(10,13,3,1)), Hazard(rect_from_grid(24,13,3,1))],
                   [], [], [Coin(rect_from_grid(9,11)), Coin(rect_from_grid(15,9)), Coin(rect_from_grid(21,7)), Coin(rect_from_grid(27,9))],
                   None, None, [Checkpoint(rect_from_grid(3,13)), Checkpoint(rect_from_grid(18,13))],
                   [Exit(rect_from_grid(35,12))], [Wind(rect_from_grid(10,6,18,8), force=0.35, low_grav=True)],
                   (14,28,22), (8,12,12), "Green zone: wind + low gravity."))

    # Level 5
    plats=[
        Platform(rect_from_grid(0,14,40,2)),
        Platform(rect_from_grid(8,12,4,1)),
        Platform(rect_from_grid(12,10,4,1)),
        Platform(rect_from_grid(16,8,4,1)),
        Platform(rect_from_grid(20,6,4,1)),
        Platform(rect_from_grid(24,4,4,1)),
        Platform(rect_from_grid(28,2,4,1)),
    ]
    L.append(Level("5. Summit Sprint",(2*TILE,12*TILE), plats, [Hazard(rect_from_grid(0,15,40,1))],
                   [Spring(rect_from_grid(10,11), power=-18.0)],
                   [Enemy(rect_from_grid(22,5,2,1), patrol=rect_from_grid(20,5,8,1))],
                   [Coin(rect_from_grid(13,9)), Coin(rect_from_grid(17,7)), Coin(rect_from_grid(21,5)), Coin(rect_from_grid(25,3)), Coin(rect_from_grid(29,1))],
                   Key(rect_from_grid(34,1)), Gate(rect_from_grid(36,1,1,2), locked=True),
                   [Checkpoint(rect_from_grid(4,13)), Checkpoint(rect_from_grid(22,7))],
                   [Exit(rect_from_grid(37,0))], [], (12,20,36), (4,6,12), "Use wall-jumps & dash!"))
    return L

# ----------------- Game -----------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("untitled platformer")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.big = pygame.font.SysFont("consolas", 44, bold=True)
        self.levels = builtin_levels()
        self.custom_levels: List[Level] = []
        self.idx=0; self.frame=0
        self.paused=False
        self.state="menu"  # "menu" | "playing" | "editor" | "select"
        self._init_menu()

        # ---- audio init (non-fatal if mixer not available) ----
        self.music_ok = False
        self.music_muted = False
        self.snd_click = None
        try:
            pygame.mixer.init()
            self.music_ok = True
        except Exception:
            self.music_ok = False  # run silently if no audio device

        self._load_audio()

        # start menu music at boot
        self._play_music("menu")

        self.editor_context = None  # (level_ref, is_main_level: bool)
        self.load_level()

    # ---------- Audio helpers ----------
    def _find_first_existing(self, names):
        for n in names:
            if os.path.isfile(n):
                return n
        # assets/ fallback
        for n in names:
            p = os.path.join("assets", n)
            if os.path.isfile(p):
                return p
        return None

    def _load_audio(self):
        self.menu_music_path = self._find_first_existing(["menu_music.ogg", "menu_music.mp3"])
        self.game_music_path = self._find_first_existing(["game_music.ogg", "game_music.mp3", "bg_music.ogg", "bg_music.mp3"])
        click = self._find_first_existing(["click.wav"])
        if self.music_ok and click:
            try:
                self.snd_click = pygame.mixer.Sound(click)
            except Exception:
                self.snd_click = None

    def _play_music(self, which="menu"):
        if not self.music_ok:
            return
        path = self.menu_music_path if which == "menu" else self.game_music_path
        if not path:
            return
        try:
            pygame.mixer.music.load(path)
            if not self.music_muted:
                pygame.mixer.music.play(-1)  # loop
        except Exception:
            pass

    def _stop_music(self):
        if self.music_ok:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def _mute_toggle(self):
        # Toggle mute without stopping playback state
        self.music_muted = not self.music_muted
        if not self.music_ok:
            return
        try:
            if self.music_muted:
                pygame.mixer.music.set_volume(0.0)
            else:
                pygame.mixer.music.set_volume(1.0)
        except Exception:
            pass

    # ---------- Menu / Select ----------
    def _init_menu(self):
        self.menu_items = [
            ("Play (Start Level 1)", "play"),
            ("Level Select", "select"),
            ("Editor: Edit Main Level", "edit_main"),
            ("Editor: New Custom Level", "edit_new"),
            ("Quit", "quit"),
        ]

    def draw_menu(self):
        self.draw_bg_plain((18,22,30),(8,10,14))
        title = self.big.render("untitled platformer", True, WHITE)
        self.screen.blit(title,(WIDTH//2-title.get_width()//2, 60))
        for i,(label,_) in enumerate(self.menu_items):
            r=pygame.Rect(WIDTH//2-220, 150+i*56, 440, 42)
            pygame.draw.rect(self.screen, (45,50,60), r, border_radius=10)
            self.screen.blit(self.font.render(f"{i+1}. {label}", True, WHITE),(r.x+16, r.y+10))
        tip="Use 1-5 or click. In editor: F2 playtest, F6 save edits, ESC back. (M: mute)"
        self.screen.blit(self.font.render(tip, True, (210,210,210)), (20, HEIGHT-34))

    def handle_menu(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_m:
                self._mute_toggle()
            n = event.key - pygame.K_1
            if 0<=n<len(self.menu_items): self._menu_action(self.menu_items[n][1])
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            mx,my=event.pos
            for i,_ in enumerate(self.menu_items):
                r=pygame.Rect(WIDTH//2-220, 150+i*56, 440, 42)
                if r.collidepoint(mx,my):
                    if self.snd_click: self.snd_click.play()
                    self._menu_action(self.menu_items[i][1])

    def _menu_action(self, action):
        if action=="play":
            self.idx=0; self.state="playing"; self.paused=False; self.load_level()
            self._stop_music(); self._play_music("game")
        elif action=="select":
            self.state="select"
            self._stop_music(); self._play_music("menu")
        elif action=="edit_main":
            self.idx=0; self.load_level(); self.editor_begin()
            self._stop_music(); self._play_music("menu")
        elif action=="edit_new":
            self._create_blank_custom()
            self.idx=len(self.levels) + len(self.custom_levels)-1
            self.editor_begin()
            self._stop_music(); self._play_music("menu")
        elif action=="quit":
            pygame.quit(); sys.exit(0)

    def draw_select(self):
        self.draw_bg_plain((20,24,34),(10,12,16))
        self.screen.blit(self.big.render("Select Level", True, WHITE),(WIDTH//2-150,50))
        y=130; i=0
        for i,lv in enumerate(self.levels):
            txt=f"{i+1}. {lv.name}  (main)"
            self._draw_select_row(60,y,txt,i, is_custom=False); y+=46
        for j,lv in enumerate(self.custom_levels):
            txt=f"{i+j+2}. {lv.name}  (custom)"
            self._draw_select_row(60,y,txt,i+j+1, is_custom=True); y+=46
        self.screen.blit(self.font.render("Esc: Back to Menu  (M: mute)", True, WHITE),(20, HEIGHT-34))

    def _draw_select_row(self, x,y, text, idx, is_custom):
        r=pygame.Rect(x,y, WIDTH-2*x, 38)
        pygame.draw.rect(self.screen, (45,50,60), r, border_radius=8)
        self.screen.blit(self.font.render(text, True, WHITE),(x+12,y+9))

    def handle_select(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_m: self._mute_toggle()
            if event.key==pygame.K_ESCAPE:
                self.state="menu"; return
            n=event.key - pygame.K_1
            total=len(self.levels)+len(self.custom_levels)
            if 0<=n<total:
                self.idx=n; self.state="playing"; self.paused=False; self.load_level()
                self._stop_music(); self._play_music("game")
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            mx,my=event.pos
            y=130; rows=[]
            total=len(self.levels)+len(self.custom_levels)
            for i in range(total):
                r=pygame.Rect(60,y, WIDTH-120, 38); rows.append(r); y+=46
            for i,r in enumerate(rows):
                if r.collidepoint(mx,my):
                    if self.snd_click: self.snd_click.play()
                    self.idx=i; self.state="playing"; self.paused=False; self.load_level()
                    self._stop_music(); self._play_music("game")

    # --------- Level load/reset ----------
    def load_level(self, checkpoint:Optional[Tuple[int,int]]=None):
        L = self._level_by_index(self.idx)
        # clone entities for a fresh run
        self.platforms=[Platform(p.rect.copy(), p.semisolid, p.moving, p.vel.copy(),
                                 p.bounds.copy() if p.bounds else None, p.disappear_cycle) for p in L.platforms]
        self.hazards=[Hazard(h.rect.copy()) for h in L.hazards]
        self.springs=[Spring(s.rect.copy(), s.power) for s in L.springs]
        self.enemies=[Enemy(e.rect.copy(), e.dir, e.speed, e.patrol.copy() if e.patrol else None) for e in L.enemies]
        self.coins=[Coin(c.rect.copy()) for c in L.coins]
        self.key=Key(L.key.rect.copy()) if L.key else None
        self.gate=Gate(L.gate.rect.copy(), L.gate.locked) if L.gate else None
        self.checkpoints=[Checkpoint(ch.rect.copy()) for ch in L.checkpoints]
        self.exits=[Exit(x.rect.copy()) for x in L.exits]
        self.winds=[Wind(w.rect.copy(), w.force, w.low_grav) for w in L.winds]
        sx,sy = checkpoint if checkpoint else L.start
        self.player=Player(pygame.Rect(sx, sy, int(TILE*0.9), int(TILE*0.95)))
        self.player.spawn=(sx,sy)
        self.cam = pygame.Vector2(0,0)
        self.collected=0
        self.frame=0
        self.level_tip=L.tip
        self.bg_top=L.bg_top; self.bg_bottom=L.bg_bottom

    def _level_by_index(self, idx)->Level:
        if idx < len(self.levels): return self.levels[idx]
        else: return self.custom_levels[idx-len(self.levels)]

    # -------------- Input (play) --------------
    def handle_input(self):
        k=pygame.key.get_pressed()
        if k[pygame.K_ESCAPE]: self.paused=True
        if not self.paused and self.player.alive:
            ax = (k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a])
            if ax!=0: self.player.facing = 1 if ax>0 else -1

            if self.player.on_ground:
                self.player.vel.x = (self.player.vel.x + ax*GROUND_ACCEL)
                if ax==0: self.player.vel.x *= GROUND_FRICTION
            else:
                self.player.vel.x = (self.player.vel.x + ax*AIR_ACCEL) * AIR_DRAG
            self.player.vel.x = clamp(self.player.vel.x, -MAX_X, MAX_X)

            jump = k[pygame.K_SPACE] or k[pygame.K_w] or k[pygame.K_UP]
            drop = k[pygame.K_s] or k[pygame.K_DOWN]
            dash_key = k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT]

            if jump: self.player.jump_buf = JUMP_BUFFER
            if drop and self.player.on_ground: self.player.rect.y += 4  # drop through semisolid

            # Wall jump (with wall coyote)
            can_wall = (self.player.wall_dir != 0) or (self.player.wall_coyote > 0)
            if can_wall and self.player.jump_buf>0:
                wd = self.player.wall_dir if self.player.wall_dir!=0 else (1 if self.player.facing<0 else -1)
                self.player.vel.y = WALL_JUMP_VY
                self.player.vel.x = WALL_JUMP_VX * (-wd)
                self.player.jump_buf=0; self.player.on_ground=False; self.player.wall_coyote=0

            if (self.player.on_ground or self.player.coyote>0) and self.player.jump_buf>0:
                self.player.vel.y = JUMP_V
                self.player.on_ground=False; self.player.coyote=0; self.player.jump_buf=0

            if not jump and self.player.vel.y<0: self.player.vel.y *= 0.72

            if dash_key and self.player.dashing==0 and self.player.dash_cd==0:
                dx = ((k[pygame.K_RIGHT] or k[pygame.K_d]) - (k[pygame.K_LEFT] or k[pygame.K_a]))
                dy = ((k[pygame.K_DOWN]  or k[pygame.K_s]) - (k[pygame.K_UP]   or k[pygame.K_w]))
                if dx==0 and dy==0: dx=self.player.facing
                v = pygame.Vector2(dx, dy)
                if v.length_squared()==0: v.x = self.player.facing
                v = v.normalize() * DASH_SPEED
                self.player.vel.x, self.player.vel.y = v.x, v.y
                self.player.dashing = DASH_TIME
                self.player.dash_cd = DASH_COOLDOWN

    # -------------- Physics (play) --------------
    def apply_wind(self)->bool:
        low=False
        for w in self.winds:
            if self.player.rect.colliderect(w.rect):
                self.player.vel.x += w.force
                if w.low_grav: low=True
        return low

    def physics(self):
        for e in self.enemies: e.update()
        for p in self.platforms: p.update()

        low = self.apply_wind()

        if self.player.dashing>0: self.player.dashing-=1
        else:
            g = WALL_SLIDE_GRAVITY if self.player.wall_dir!=0 and self.player.vel.y>0 else GRAVITY*(0.65 if low else 1.0)
            self.player.vel.y += g
        if self.player.dash_cd>0: self.player.dash_cd-=1

        self.player.rect.x += int(self.player.vel.x); self.collide(True)
        self.player.on_ground=False
        self.player.rect.y += int(self.player.vel.y); self.collide(False)

        for s in self.springs:
            if self.player.rect.colliderect(s.rect):
                self.player.vel.y = s.power; self.player.on_ground=False
        for h in self.hazards:
            if self.player.rect.colliderect(h.rect): self.die()
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect): self.die()

        for c in self.coins:
            if not c.taken and self.player.rect.colliderect(c.rect):
                c.taken=True; self.collected+=1
        if self.key and (not self.key.taken) and self.player.rect.colliderect(self.key.rect):
            self.key.taken=True
            if self.gate: self.gate.locked=False

        for ch in self.checkpoints:
            if self.player.rect.colliderect(ch.rect):
                self.player.spawn=(ch.rect.x, ch.rect.y - self.player.rect.height)

        can_exit = (self.gate is None or not self.gate.locked)
        # keep the “collect all coins” rule for levels 2 & 4 as example
        if self.idx in (1,3):
            if any(not c.taken for c in self.coins): can_exit=False

        for ex in self.exits:
            if can_exit and self.player.rect.colliderect(ex.rect): self.next_level()

        if self.player.rect.top > HEIGHT+600 or not self.player.alive:
            sx,sy=self.player.spawn; self.load_level((sx,sy))

        if self.player.on_ground: self.player.coyote=COYOTE
        else: self.player.coyote=max(0, self.player.coyote-1)
        self.player.jump_buf=max(0, self.player.jump_buf-1)

        if self.player.wall_dir!=0: self.player.wall_coyote = WALL_COYOTE
        else: self.player.wall_coyote = max(0, self.player.wall_coyote-1)

    def die(self): self.player.alive=False

    def collide(self, horizontal:bool):
        r=self.player.rect
        if horizontal: self.player.wall_dir=0
        for p in self.platforms:
            if not p.active(self.frame): continue
            if p.semisolid:
                if not horizontal and self.player.vel.y>=0:
                    feet=r.bottom
                    if p.rect.left<=r.centerx<=p.rect.right and p.rect.top-12<=feet<=p.rect.top+12:
                        r.bottom=p.rect.top; self.player.vel.y=0; self.player.on_ground=True
                continue
            if r.colliderect(p.rect):
                if horizontal:
                    if self.player.vel.x>0:
                        r.right=p.rect.left; self.player.wall_dir=1
                    elif self.player.vel.x<0:
                        r.left=p.rect.right; self.player.wall_dir=-1
                    self.player.vel.x=0
                else:
                    if self.player.vel.y>0:
                        r.bottom=p.rect.top; self.player.vel.y=0; self.player.on_ground=True
                    elif self.player.vel.y<0:
                        r.top=p.rect.bottom; self.player.vel.y=0
        if self.gate and self.gate.locked and r.colliderect(self.gate.rect):
            if horizontal:
                if self.player.vel.x>0:
                    r.right=self.gate.rect.left; self.player.wall_dir=1
                elif self.player.vel.x<0:
                    r.left=self.gate.rect.right; self.player.wall_dir=-1
                self.player.vel.x=0
            else:
                if self.player.vel.y>0:
                    r.bottom=self.gate.rect.top; self.player.vel.y=0; self.player.on_ground=True
                elif self.player.vel.y<0:
                    r.top=self.gate.rect.bottom; self.player.vel.y=0

    # ---------- Camera & draw (play) ----------
    def update_camera(self):
        target=pygame.Vector2(self.player.rect.centerx - WIDTH//2, self.player.rect.centery - HEIGHT//2)
        self.cam += (target-self.cam)*0.1

    def parallax(self, rect:pygame.Rect, factor:float)->pygame.Rect:
        return rect.move(int(-self.cam.x*factor), int(-self.cam.y*factor))

    def draw_bg_plain(self, top, bot):
        for y in range(HEIGHT):
            t=y/HEIGHT
            c=(int(top[0]*(1-t)+bot[0]*t), int(top[1]*(1-t)+bot[1]*t), int(top[2]*(1-t)+bot[2]*t))
            pygame.draw.line(self.screen, c, (0,y),(WIDTH,y))

    def draw_bg(self):
        top=self.bg_top; bot=self.bg_bottom
        for y in range(HEIGHT):
            t=y/HEIGHT
            c=(int(top[0]*(1-t)+bot[0]*t), int(top[1]*(1-t)+bot[1]*t), int(top[2]*(1-t)+bot[2]*t))
            pygame.draw.line(self.screen, c, (0,y),(WIDTH,y))
        random.seed(7)
        for i in range(120):
            x=(i*97)%(WIDTH*3); y=(i*41)%(HEIGHT*3)
            pygame.draw.circle(self.screen, (210,210,230), ((x-int(self.cam.x*0.2))%WIDTH, (y-int(self.cam.y*0.2))%HEIGHT),1)

    def draw_world(self):
        for p in self.platforms:
            rr=self.parallax(p.rect,1.0)
            col=(100,100,110) if p.active(self.frame) else (60,60,70)
            pygame.draw.rect(self.screen, col, rr)
        for h in self.hazards:
            rr=self.parallax(h.rect,1.0); pygame.draw.rect(self.screen, RED, rr)
        for e in self.enemies:
            rr=self.parallax(e.rect,1.0); pygame.draw.rect(self.screen, ORANGE, rr)
            eye=pygame.Rect(rr.centerx + e.dir*6 -4, rr.top+8, 8,8); pygame.draw.rect(self.screen, BLACK, eye)
        for s in self.springs:
            rr=self.parallax(s.rect,1.0); pygame.draw.rect(self.screen, CYAN, rr); pygame.draw.rect(self.screen, BLACK, rr,2)
        for c in self.coins:
            if not c.taken:
                rr=self.parallax(c.rect,1.0)
                pygame.draw.circle(self.screen, YELLOW, rr.center, 10)
                pygame.draw.circle(self.screen, (255,240,160), rr.center, 10,2)
        if self.key and not self.key.taken:
            rr=self.parallax(self.key.rect,1.0); pygame.draw.rect(self.screen, (255,240,160), rr)
            pygame.draw.circle(self.screen, BLACK, (rr.centerx+8, rr.centery),3,1)
        if self.gate:
            rr=self.parallax(self.gate.rect,1.0); pygame.draw.rect(self.screen, PURPLE if self.gate.locked else GREEN, rr)
        for ch in self.checkpoints:
            rr=self.parallax(ch.rect,1.0); pygame.draw.rect(self.screen, (60,210,140), rr); pygame.draw.rect(self.screen, (20,80,40), rr,2)
        for ex in self.exits:
            rr=self.parallax(ex.rect,1.0); pygame.draw.rect(self.screen, BLUE, rr); pygame.draw.rect(self.screen, WHITE, rr,2)
        pr=self.parallax(self.player.rect,1.0)
        pygame.draw.rect(self.screen, (245,245,245), pr, border_radius=6)
        pygame.draw.circle(self.screen, BLACK, (pr.centerx + self.player.facing*6, pr.centery-6), 3)
        for w in self.winds:
            rr=self.parallax(w.rect,1.0)
            s=pygame.Surface(rr.size, pygame.SRCALPHA); s.fill((80,200,160,64 if w.low_grav else 40))
            self.screen.blit(s, rr.topleft)
            for i in range(rr.top, rr.bottom, 18):
                pygame.draw.polygon(self.screen, (220,250,240,180), [(rr.left+8,i+6),(rr.left+22,i),(rr.left+22,i+12)])

    def draw_ui(self):
        L = self._level_by_index(self.idx)
        text=f"{L.name}   Coins {sum(c.taken for c in self.coins)}/{len(self.coins)}"
        if self.key: text += f"  Key: {'✓' if self.key.taken else '—'}  Gate: {'Open' if self.gate and not self.gate.locked else ('Locked' if self.gate else '—')}"
        if self.player.dash_cd>0: text += f"   Dash CD: {self.player.dash_cd//FPS + (1 if self.player.dash_cd%FPS else 0)}s"
        self.screen.blit(self.font.render(text, True, WHITE), (16,12))
        tip = L.tip or "Shift = Dash (8 directions). Wall-slide to line up wall-jumps."
        self.screen.blit(self.font.render(tip, True, (210,210,210)), (16,36))

    def draw_pause(self):
        s=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,160)); self.screen.blit(s,(0,0))
        t=self.big.render("Paused", True, WHITE); self.screen.blit(t,(WIDTH//2-t.get_width()//2,80))
        lines = [
            "Esc: Resume   R: Restart   M: Mute music",
            "1..9: Level select",
            "Move: A/D or ←/→   Jump: Space/W/↑",
            "Dash: Shift (+ direction)   Drop: S/↓"
        ]
        for i,ln in enumerate(lines):
            self.screen.blit(self.font.render(ln, True, WHITE),(WIDTH//2-260, 160+i*28))

        # Buttons
        btn_w, btn_h = 220, 42
        x = WIDTH//2 - btn_w//2
        y1 = 160 + len(lines)*28 + 24
        y2 = y1 + 54

        self.pause_btn_resume = pygame.Rect(x, y1, btn_w, btn_h)
        self.pause_btn_menu   = pygame.Rect(x, y2, btn_w, btn_h)

        for rect, label in [(self.pause_btn_resume, "Resume"), (self.pause_btn_menu, "Back to Menu")]:
            pygame.draw.rect(self.screen, (45,50,60), rect, border_radius=10)
            self.screen.blit(self.font.render(label, True, WHITE), (rect.x+24, rect.y+10))

    def next_level(self):
        total=len(self.levels)+len(self.custom_levels)
        self.idx=(self.idx+1)%total
        self.load_level()

    # ----------------- Editor -----------------
    def _create_blank_custom(self):
        # Start with a floor and an exit
        plats=[Platform(rect_from_grid(0,14,40,2))]
        new=Level("Custom Level", (2*TILE,12*TILE), plats, [], [], [], [], None, None, [Checkpoint(rect_from_grid(3,13))], [Exit(rect_from_grid(35,12))], [],
                  (22,24,35),(10,10,14),"Make something cool!")
        self.custom_levels.append(new)

    def editor_begin(self):
        # begin editing current index
        self.state="editor"
        self.editor_context=("main" if self.idx<len(self.levels) else "custom", self.idx<len(self.levels))
        self.edit_tool_groups=[
            ("Platforms", ["Solid","Semisolid","Move H","Move V"]),
            ("Hazards", ["Hazard","Spring","Enemy"]),
            ("Items", ["Coin","Key","Gate"]),
            ("Logic", ["Checkpoint","Exit"]),
            ("Zones", ["Wind"]),
        ]
        self.tool_group_idx=0
        self.tool_idx=0
        self.show_grid=True
        self.wind_size=(3,2)  # tiles
        self.enemy_patrol_w=5 # tiles
        self.move_speed=1.2
        self.spring_power=-16.0

    def draw_editor(self):
        # draw world (no camera)
        self.draw_bg_plain((24,24,30),(10,10,12))
        # grid
        if self.show_grid:
            for x in range(0,WIDTH,TILE): pygame.draw.line(self.screen,(40,40,48),(x,0),(x,HEIGHT))
            for y in range(0,HEIGHT,TILE): pygame.draw.line(self.screen,(40,40,48),(0,y),(WIDTH,y))
        # existing
        self.cam=pygame.Vector2(0,0)
        self.draw_world()
        # HUD
        gname, tools = self.edit_tool_groups[self.tool_group_idx]
        tool_name = tools[self.tool_idx]
        hud = f"[Editor] Group: {gname}  Tool: {tool_name}   (T) switch group  [ ] cycle tool"
        self.screen.blit(self.font.render(hud, True, WHITE),(12,8))
        sub = "LMB place | RMB delete | F2 playtest | F6 save | Esc menu | G grid | M mute"
        self.screen.blit(self.font.render(sub, True, (210,210,210)),(12,32))
        specifics=""
        if tool_name.startswith("Move"):
            specifics=f"H/V orientation, speed -/+: {self.move_speed:.1f}"
        elif tool_name=="Spring":
            specifics=f"power -/+: {self.spring_power:.1f}"
        elif tool_name=="Wind":
            specifics=f"size -/+ tiles: {self.wind_size[0]}x{self.wind_size[1]}"
        elif tool_name=="Enemy":
            specifics=f"patrol width -/+: {self.enemy_patrol_w} tiles"
        if specifics:
            self.screen.blit(self.font.render(specifics, True, (200,220,220)), (12,56))

    def handle_editor_event(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_m: self._mute_toggle()
            if event.key==pygame.K_ESCAPE:
                self.state="menu"; self._stop_music(); self._play_music("menu"); return
            if event.key==pygame.K_t:
                self.tool_group_idx=(self.tool_group_idx+1)%len(self.edit_tool_groups)
                self.tool_idx=0
            if event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                d= -1 if event.key==pygame.K_LEFTBRACKET else 1
                gname, tools = self.edit_tool_groups[self.tool_group_idx]
                self.tool_idx=(self.tool_idx+d)%len(tools)
            if event.key==pygame.K_g: self.show_grid=not self.show_grid
            if event.key==pygame.K_F2:  # playtest
                self.state="playing"; self.paused=False; self.load_level()
                self._stop_music(); self._play_music("game")
            if event.key==pygame.K_F6:  # save back to level object
                self._save_back_to_level()
            if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.move_speed=max(0.4, self.move_speed-0.2)
                self.spring_power-=1.0
                self.enemy_patrol_w=max(3, self.enemy_patrol_w-1)
                self.wind_size=(max(1,self.wind_size[0]-1), max(1,self.wind_size[1]-1))
            if event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                self.move_speed=min(3.0, self.move_speed+0.2)
                self.spring_power+=1.0
                self.enemy_patrol_w=min(12, self.enemy_patrol_w+1)
                self.wind_size=(min(24,self.wind_size[0]+1), min(16,self.wind_size[1]+1))
        if event.type==pygame.MOUSEBUTTONDOWN:
            gx,gy = (event.pos[0]//TILE, event.pos[1]//TILE)
            gname, tools = self.edit_tool_groups[self.tool_group_idx]
            tool = tools[self.tool_idx]
            if event.button==1:
                self._editor_place(tool, gx, gy)
            if event.button==3:
                self._editor_delete(tool, gx, gy)

    def _editor_place(self, tool, gx, gy):
        r=rect_from_grid(gx,gy,1,1)
        if tool=="Solid":
            self.platforms.append(Platform(r))
        elif tool=="Semisolid":
            self.platforms.append(Platform(r, semisolid=True))
        elif tool in ("Move H","Move V"):
            if tool=="Move H":
                vel=pygame.Vector2(self.move_speed,0); b=rect_from_grid(max(0,gx-5),gy,11,1)
            else:
                vel=pygame.Vector2(0,-self.move_speed); b=rect_from_grid(gx,max(0,gy-4),1,9)
            self.platforms.append(Platform(r, moving=True, vel=vel, bounds=b))
        elif tool=="Hazard":
            self.hazards.append(Hazard(r))
        elif tool=="Spring":
            self.springs.append(Spring(r, power=self.spring_power))
        elif tool=="Enemy":
            patrol=rect_from_grid(max(0,gx-self.enemy_patrol_w//2),gy,self.enemy_patrol_w,1)
            self.enemies.append(Enemy(r, patrol=patrol))
        elif tool=="Coin":
            self.coins.append(Coin(r))
        elif tool=="Key":
            self.key=Key(r)
        elif tool=="Gate":
            self.gate=Gate(rect_from_grid(gx,gy,1,2), locked=True)
        elif tool=="Checkpoint":
            self.checkpoints.append(Checkpoint(r))
        elif tool=="Exit":
            self.exits.append(Exit(r))
        elif tool=="Wind":
            w,h=self.wind_size
            self.winds.append(Wind(rect_from_grid(gx,gy,w,h), force=0.35, low_grav=False))

    def _editor_delete(self, tool, gx, gy):
        r=rect_from_grid(gx,gy,1,1)
        def pop_first(seq,pred):
            for i,o in enumerate(seq):
                if pred(o): seq.pop(i); return True
            return False
        if tool in ("Solid","Semisolid","Move H","Move V"):
            pop_first(self.platforms, lambda p: p.rect.colliderect(r))
        elif tool=="Hazard":
            pop_first(self.hazards, lambda h: h.rect.colliderect(r))
        elif tool=="Spring":
            pop_first(self.springs, lambda s: s.rect.colliderect(r))
        elif tool=="Enemy":
            pop_first(self.enemies, lambda e: e.rect.colliderect(r))
        elif tool=="Coin":
            pop_first(self.coins, lambda c: c.rect.colliderect(r))
        elif tool=="Key":
            if self.key and self.key.rect.colliderect(r): self.key=None
        elif tool=="Gate":
            if self.gate and self.gate.rect.colliderect(r): self.gate=None
        elif tool=="Checkpoint":
            pop_first(self.checkpoints, lambda c: c.colliderect(r))
        elif tool=="Exit":
            pop_first(self.exits, lambda e: e.rect.colliderect(r))
        elif tool=="Wind":
            pop_first(self.winds, lambda w: w.rect.colliderect(r))

    def _save_back_to_level(self):
        # Build a Level object from current editor buffers and overwrite in the source list.
        name = (self._level_by_index(self.idx).name or "Edited Level")
        start = self._level_by_index(self.idx).start
        L = Level(name, start,
                  [Platform(p.rect.copy(), p.semisolid, p.moving, p.vel.copy(), p.bounds.copy() if p.bounds else None, p.disappear_cycle) for p in self.platforms],
                  [Hazard(h.rect.copy()) for h in self.hazards],
                  [Spring(s.rect.copy(), s.power) for s in self.springs],
                  [Enemy(e.rect.copy(), e.dir, e.speed, e.patrol.copy() if e.patrol else None) for e in self.enemies],
                  [Coin(c.rect.copy()) for c in self.coins],
                  Key(self.key.rect.copy()) if self.key else None,
                  Gate(self.gate.rect.copy(), self.gate.locked) if self.gate else None,
                  self.checkpoints[:],
                  [Exit(x.rect.copy()) for x in self.exits],
                  [Wind(w.rect.copy(), w.force, w.low_grav) for w in self.winds],
                  self.bg_top, self.bg_bottom, self.level_tip)
        if self.idx < len(self.levels):
            self.levels[self.idx]=L
        else:
            self.custom_levels[self.idx-len(self.levels)]=L

    # -------------- Main Loop --------------
    def run(self):
        while True:
            dt=self.clock.tick(FPS)
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); sys.exit(0)

                if self.state=="menu":
                    self.handle_menu(e)

                elif self.state=="select":
                    self.handle_select(e)

                elif self.state=="editor":
                    self.handle_editor_event(e)

                elif self.state=="playing":
                    if e.type==pygame.KEYDOWN:
                        if e.key==pygame.K_m: self._mute_toggle()
                        if e.key==pygame.K_r: self.load_level()
                        if e.key==pygame.K_ESCAPE:
                            if self.paused: self.paused=False
                            else: self.paused=True
                        if self.paused and pygame.K_1<=e.key<=pygame.K_9:
                            n=e.key-pygame.K_1
                            if n < len(self.levels)+len(self.custom_levels):
                                self.idx=n; self.load_level()

                    if e.type==pygame.MOUSEBUTTONDOWN and self.paused and e.button==1:
                        mx,my = e.pos
                        if hasattr(self, "pause_btn_resume") and self.pause_btn_resume.collidepoint(mx,my):
                            if self.snd_click: self.snd_click.play()
                            self.paused = False
                        elif hasattr(self, "pause_btn_menu") and self.pause_btn_menu.collidepoint(mx,my):
                            if self.snd_click: self.snd_click.play()
                            # go back to main menu + switch music
                            self.state = "menu"
                            self.paused = False
                            self._stop_music(); self._play_music("menu")

            # update & draw
            if self.state=="menu":
                self.draw_menu()

            elif self.state=="select":
                self.draw_select()

            elif self.state=="editor":
                self.draw_editor()

            elif self.state=="playing":
                if not self.paused:
                    self.handle_input(); self.physics(); self.update_camera()
                self.draw_bg(); self.draw_world(); self.draw_ui()
                if self.paused: self.draw_pause()

            pygame.display.flip(); self.frame+=1

def main(): Game().run()
if __name__=="__main__": main()
