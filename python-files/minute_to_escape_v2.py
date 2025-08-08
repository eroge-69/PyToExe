# Minute to Escape - Enhanced Alpha
# Creator: TheOM4R
# Features: multiple enemy types, traps, scoreboard, player colours, dynamic lighting, lore notes
import pygame, random, math, sys, json, time, os

pygame.init()
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Minute to Escape - Enhanced Alpha")
clock = pygame.time.Clock()

TILE = 32
MAP_W = SCREEN_W // TILE
MAP_H = SCREEN_H // TILE

HIGHSCORE_FILE = "highscores.txt"

# Player colour options (name, rgb)
PLAYER_COLOURS = [
    ("Ash", (200,180,160)),
    ("Crimson", (180,30,30)),
    ("Sage", (100,160,90)),
    ("Slate", (120,130,150)),
    ("Gold", (210,180,60)),
]

# Lore notes - short strings to place in the map
LORE_POOL = [
    "Note: The lanterns burn but do not warm",
    "Scrawl: They came from below, no light answered",
    "Entry: Day 47 - the stairs groaned and swallowed Sam",
    "Warning: Seal not to be opened - breach recorded",
    "Journal: I hid the map under the third tile",
]

def save_highscore(name, score):
    scores = []
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                for line in f:
                    part = line.strip().split(",")
                    if len(part) == 2:
                        scores.append((part[0], int(part[1])))
        except Exception:
            scores = []
    scores.append((name, int(score)))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
    with open(HIGHSCORE_FILE, "w") as f:
        for n,s in scores:
            f.write(f"{n},{s}\n")

def load_highscores():
    scores = []
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                for line in f:
                    part = line.strip().split(",")
                    if len(part) == 2:
                        scores.append((part[0], int(part[1])))
        except Exception:
            scores = []
    return scores

def generate_map():
    # Basic map with rooms and torches, traps, and lore notes
    m = [[1 for _ in range(MAP_W)] for _ in range(MAP_H)]
    rooms = []
    for _ in range(9):
        w = random.randint(3, 9)
        h = random.randint(3, 6)
        x = random.randint(1, MAP_W - w - 2)
        y = random.randint(1, MAP_H - h - 2)
        rooms.append((x,y,w,h))
        for iy in range(y, y+h):
            for ix in range(x, x+w):
                m[iy][ix] = 0
    # connect rooms with corridors
    for i in range(len(rooms)-1):
        x1,y1,_,_ = rooms[i]
        x2,y2,_,_ = rooms[i+1]
        cx = x1; cy = y1
        while cx != x2:
            m[cy][cx] = 0
            cx += 1 if x2>cx else -1
        while cy != y2:
            m[cy][cx] = 0
            cy += 1 if y2>cy else -1
    # place torches and traps and notes
    torches = []
    traps = []
    puddles = []
    notes = []
    for r in rooms:
        x,y,w,h = r
        # 0-2 torches per room
        for _ in range(random.randint(0,2)):
            tx = random.randint(x, x+w-1)
            ty = random.randint(y, y+h-1)
            torches.append((tx,ty, random.choice([True, False]))) # some torches flicker
        # traps
        if random.random() < 0.5:
            tx = random.randint(x, x+w-1)
            ty = random.randint(y, y+h-1)
            traps.append((tx,ty,0.0))  # spike cd timer inside
        # puddles (poison)
        if random.random() < 0.35:
            tx = random.randint(x, x+w-1)
            ty = random.randint(y, y+h-1)
            puddles.append((tx,ty))
        # notes
        if random.random() < 0.5:
            tx = random.randint(x, x+w-1)
            ty = random.randint(y, y+h-1)
            notes.append((tx,ty, random.choice(LORE_POOL)))
    # ensure map is not empty
    return m, torches, traps, puddles, notes

def find_floor_cell(m):
    for _ in range(2000):
        x = random.randrange(1, MAP_W-1)
        y = random.randrange(1, MAP_H-1)
        if m[y][x] == 0:
            return x, y
    return 1,1

class Player:
    def __init__(self, x, y, colour):
        self.x = x*TILE + TILE//2
        self.y = y*TILE + TILE//2
        self.speed = 140
        self.rect = pygame.Rect(0,0,18,18)
        self.dir = 0
        self.health = 3
        self.colour = colour
        self.score = 0
    def update(self, dt, m):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        if dx!=0 or dy!=0:
            ang = math.atan2(dy, dx)
            self.dir = ang
            nx = self.x + math.cos(ang)*self.speed*dt
            ny = self.y + math.sin(ang)*self.speed*dt
            if not collides(nx, self.y, m):
                self.x = nx
            if not collides(self.x, ny, m):
                self.y = ny
        self.rect.center = (int(self.x), int(self.y))

class Enemy:
    def __init__(self, x, y, etype):
        self.x = x*TILE + TILE//2
        self.y = y*TILE + TILE//2
        self.rect = pygame.Rect(0,0,18,18)
        self.etype = etype
        # behaviours by type
        if etype == "crawler":
            self.speed = random.uniform(70,110)
        elif etype == "guard":
            self.speed = random.uniform(30,50)
        elif etype == "shade":
            self.speed = random.uniform(80,120)
        elif etype == "stalker":
            self.speed = random.uniform(50,90)
        elif etype == "bomber":
            self.speed = random.uniform(20,40)
            self.timer = random.uniform(2.0,4.0)
        self.alive = True
    def update(self, dt, player, m):
        if not self.alive: return
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx,dy)
        if self.etype == "shade":
            # shade teleports occasionally when far
            if dist > 220 and random.random() < 0.01:
                # teleport closer
                ang = math.atan2(dy,dx)
                self.x = player.x - math.cos(ang)*random.randint(60,140)
                self.y = player.y - math.sin(ang)*random.randint(60,140)
            else:
                if dist < 300:
                    ang = math.atan2(dy,dx)
                    nx = self.x + math.cos(ang)*self.speed*dt
                    ny = self.y + math.sin(ang)*self.speed*dt
                    if not collides(nx, self.y, m):
                        self.x = nx
                    if not collides(self.x, ny, m):
                        self.y = ny
        elif self.etype == "bomber":
            # moves toward player, explodes when close or timer hits 0
            ang = math.atan2(dy,dx)
            nx = self.x + math.cos(ang)*self.speed*dt
            ny = self.y + math.sin(ang)*self.speed*dt
            if not collides(nx, self.y, m): self.x = nx
            if not collides(self.x, ny, m): self.y = ny
            self.timer -= dt
            if self.timer <= 0 or dist < 28:
                # explode (deal area damage flag to caller)
                self.alive = False
                return "explode", (self.x, self.y)
        else:
            if dist < 300:
                ang = math.atan2(dy,dx)
                nx = self.x + math.cos(ang)*self.speed*dt
                ny = self.y + math.sin(ang)*self.speed*dt
                if not collides(nx, self.y, m):
                    self.x = nx
                if not collides(self.x, ny, m):
                    self.y = ny
        self.rect.center = (int(self.x), int(self.y))
        return None

def collides(px, py, m):
    tx = int(px) // TILE
    ty = int(py) // TILE
    if tx<0 or tx>=MAP_W or ty<0 or ty>=MAP_H: return True
    return m[ty][tx] == 1

def draw_map(surface, m, camera_offset):
    for y in range(MAP_H):
        for x in range(MAP_W):
            sx = x*TILE - camera_offset[0]
            sy = y*TILE - camera_offset[1]
            if m[y][x] == 0:
                pygame.draw.rect(surface, (25,20,20), (sx,sy,TILE,TILE))
                pygame.draw.rect(surface, (35,30,28), (sx+2,sy+2,TILE-4,TILE-4),1)
            else:
                pygame.draw.rect(surface, (6,6,6), (sx,sy,TILE,TILE))

def build_light_mask(size, player_pos, player_dir, torches, flicker_state):
    # Create darkness mask and punch light circles for player and torches
    mask = pygame.Surface(size)
    mask.fill((0,0,0))
    mask.set_colorkey((1,1,1))
    cone = pygame.Surface(size, flags=pygame.SRCALPHA)
    cone.fill((0,0,0,230))
    # player light cone / circle
    px, py = player_pos
    # player has a light circle that faces dir
    pygame.draw.circle(cone, (0,0,0,0), player_pos, 110)
    # add narrow wedge to simulate torch facing
    points = [player_pos]
    for a in (player_dir-0.7, player_dir+0.7):
        points.append((px + 300*math.cos(a), py + 300*math.sin(a)))
    pygame.draw.polygon(cone, (0,0,0,0), points)
    # torches add smaller light circles; flicker_state influences radius
    for tx,ty, flick in torches:
        radius = 80 if not flick else 60 + int(20*math.sin(flicker_state*10 + tx + ty))
        pygame.draw.circle(cone, (0,0,0,0), (tx,ty), radius)
    mask.blit(cone, (0,0))
    return mask

def display_text_center(surf, text, y, size=28):
    font = pygame.font.SysFont("Arial", size)
    t = font.render(text, True, (230,230,230))
    surf.blit(t, (SCREEN_W//2 - t.get_width()//2, y))

def menu_select_colour():
    idx = 0
    while True:
        dt = clock.tick(30)/1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RIGHT:
                    idx = (idx+1) % len(PLAYER_COLOURS)
                if ev.key == pygame.K_LEFT:
                    idx = (idx-1) % len(PLAYER_COLOURS)
                if ev.key == pygame.K_RETURN:
                    return PLAYER_COLOURS[idx][1], PLAYER_COLOURS[idx][0]
                if ev.key == pygame.K_ESCAPE:
                    return PLAYER_COLOURS[0][1], PLAYER_COLOURS[0][0]
        screen.fill((10,10,10))
        display_text_center(screen, "Select Player Colour", 80, 30)
        # show options
        for i, (name, col) in enumerate(PLAYER_COLOURS):
            x = SCREEN_W//2 - 200 + i*100
            y = 220
            pygame.draw.rect(screen, col, (x, y, 60, 60))
            font = pygame.font.SysFont("Arial", 18)
            lbl = font.render(name, True, (220,220,220))
            screen.blit(lbl, (x+30 - lbl.get_width()//2, y+70))
            if i == idx:
                pygame.draw.rect(screen, (200,200,200), (x-4, y-4, 68, 68), 2)
        display_text_center(screen, "Left/Right to choose  Enter to confirm", SCREEN_H-60, 20)
        pygame.display.flip()

def show_highscores():
    scores = load_highscores()
    page = 0
    while True:
        dt = clock.tick(30)/1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return
        screen.fill((6,6,6))
        display_text_center(screen, "High Scores", 40, 36)
        font = pygame.font.SysFont("Arial", 22)
        for i, (n,s) in enumerate(scores[:10]):
            txt = font.render(f"{i+1}. {n} - {s}", True, (220,220,220))
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, 120 + i*30))
        display_text_center(screen, "Press Esc to go back", SCREEN_H-40, 18)
        pygame.display.flip()

def main_menu():
    sel = 0
    items = ["Play", "Choose Colour", "High Scores", "Quit"]
    while True:
        dt = clock.tick(30)/1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    sel = (sel+1) % len(items)
                if ev.key == pygame.K_UP:
                    sel = (sel-1) % len(items)
                if ev.key == pygame.K_RETURN:
                    if items[sel] == "Play":
                        return "play"
                    if items[sel] == "Choose Colour":
                        col, name = menu_select_colour()
                        return ("colour", col, name)
                    if items[sel] == "High Scores":
                        show_highscores()
                    if items[sel] == "Quit":
                        pygame.quit(); sys.exit()
        screen.fill((8,8,10))
        display_text_center(screen, "Minute to Escape", 60, 40)
        font = pygame.font.SysFont("Arial", 26)
        for i,it in enumerate(items):
            color = (250,250,80) if i==sel else (220,220,220)
            t = font.render(it, True, color)
            screen.blit(t, (SCREEN_W//2 - t.get_width()//2, 180 + i*50))
        display_text_center(screen, "Use Up/Down to navigate  Enter to choose", SCREEN_H-40, 18)
        pygame.display.flip()

def run_game(start_colour):
    # prepare map and entities
    game_map, torches, traps, puddles, notes = generate_map()
    # convert torch tile coords to pixel coords
    torches_px = [(tx*TILE + TILE//2, ty*TILE + TILE//2, flick) for (tx,ty,flick) in torches]
    px, py = find_floor_cell(game_map)
    player = Player(px, py, start_colour)
    # place exit far away
    ex, ey = find_floor_cell(game_map)
    while abs(ex-px) < 8 and abs(ey-py) < 8:
        ex, ey = find_floor_cell(game_map)
    exit_pos = (ex*TILE + TILE//2, ey*TILE + TILE//2)
    # spawn enemies with variety
    enemies = []
    types = ["crawler","guard","shade","stalker","bomber"]
    for _ in range(8):
        exx, eyy = find_floor_cell(game_map)
        et = random.choice(types)
        enemies.append(Enemy(exx, eyy, et))
    timer = 60.0
    flicker_state = 0.0
    attack_cool = 0.0
    lore_collected = 0
    # game loop
    while True:
        dt = clock.tick(60)/1000.0
        flicker_state += dt
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return None, 0  # back to menu
        attack_cool = max(0, attack_cool - dt)
        player.update(dt, game_map)
        # update enemies
        explosions = []
        for e in enemies[:]:
            ret = e.update(dt, player, game_map)
            if ret and isinstance(ret, tuple) and ret[0] == "explode":
                explosions.append(ret[1])
                try:
                    enemies.remove(e)
                except Exception:
                    pass
        # collisions and damage
        for e in enemies[:]:
            if player.rect.colliderect(e.rect) and e.alive:
                # different damage by type
                if e.etype == "guard":
                    player.health -= 2
                elif e.etype == "bomber":
                    player.health -= 2
                    e.alive = False
                else:
                    player.health -= 1
                try:
                    enemies.remove(e)
                except Exception:
                    pass
        # apply explosion area damage
        for expos in explosions:
            dx = abs(player.x - expos[0])
            dy = abs(player.y - expos[1])
            if dx*dx + dy*dy < (TILE*3)**2:
                player.health -= 2
        # traps: spikes have cooldown and can damage when active
        new_traps = []
        for (tx,ty,cd) in traps:
            cd = cd - dt
            active = False
            # spikes pop up briefly at intervals
            if cd <= 0:
                # random trigger chance
                if random.random() < 0.18:
                    cd = 1.0  # active for 1 sec
                    active = True
                else:
                    cd = random.uniform(1.0, 3.0)
            else:
                active = True
            # damage if player on tile and active
            if active:
                tile_x = tx*TILE + TILE//2
                tile_y = ty*TILE + TILE//2
                if abs(player.x - tile_x) < TILE//2 and abs(player.y - tile_y) < TILE//2:
                    player.health -= 1 * dt * 4  # continuous damage over the second
            new_traps.append((tx,ty,cd))
        traps = new_traps
        # puddles (poison) slow and damage
        for (pxi, pyi) in puddles:
            tile_x = pxi*TILE + TILE//2
            tile_y = pyi*TILE + TILE//2
            if abs(player.x - tile_x) < TILE//2 and abs(player.y - tile_y) < TILE//2:
                player.speed = 70
                player.health -= 0.5 * dt
            else:
                player.speed = 140
        # attack handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and attack_cool == 0:
            attack_cool = 0.35
            ax = player.x + math.cos(player.dir)*28
            ay = player.y + math.sin(player.dir)*28
            ar = pygame.Rect(0,0,28,28)
            ar.center = (ax, ay)
            for e in enemies[:]:
                if ar.colliderect(e.rect):
                    e.alive = False
                    try:
                        enemies.remove(e)
                    except Exception:
                        pass
                    player.score += 50
        # timer update and flicker state
        timer -= dt
        # check notes pickup
        for n in notes[:]:
            nx, ny, txt = n
            tile_x = nx*TILE + TILE//2
            tile_y = ny*TILE + TILE//2
            if abs(player.x - tile_x) < TILE//2 and abs(player.y - tile_y) < TILE//2:
                player.score += 20
                lore_collected += 1
                notes.remove(n)
                # show a quick message - appended to score display
        # check win/lose
        if timer <= 0 or player.health <= 0:
            return "fail", int(player.score + (60 - max(0,timer))*5)
        exrect = pygame.Rect(0,0,20,20)
        exrect.center = exit_pos
        if player.rect.colliderect(exrect):
            total = int(player.score + (60 - max(0,timer))*5 + lore_collected*30)
            return "win", total
        # draw everything
        screen.fill((0,0,0))
        camera = (player.x - SCREEN_W//2, player.y - SCREEN_H//2)
        draw_map(screen, game_map, camera)
        # draw puddles
        for (pxi,pyi) in puddles:
            pygame.draw.circle(screen, (40,80,20), (pxi*TILE - camera[0] + TILE//2, pyi*TILE - camera[1] + TILE//2), TILE//2)
        # draw traps (spikes)
        for (tx,ty,cd) in traps:
            txp = tx*TILE - camera[0] + TILE//2
            typ = ty*TILE - camera[1] + TILE//2
            # draw spike indicator
            pygame.draw.polygon(screen, (90,10,10), [(txp-10,typ+8),(txp,typ-12),(txp+10,typ+8)])
        # draw notes
        for (nx,ny,txt) in notes:
            pygame.draw.rect(screen, (180,140,120), (nx*TILE - camera[0] + 6, ny*TILE - camera[1] + 6, TILE-12, TILE-12))
        # draw exit
        pygame.draw.rect(screen, (40,120,40), (exit_pos[0]-camera[0]-12, exit_pos[1]-camera[1]-12,24,24))
        # draw enemies
        for e in enemies:
            col = (120,40,40)
            if e.etype == "crawler": col = (140,40,40)
            if e.etype == "guard": col = (90,10,10)
            if e.etype == "shade": col = (60,60,90)
            if e.etype == "stalker": col = (160,30,30)
            if e.etype == "bomber": col = (220,80,40)
            pygame.draw.rect(screen, col, (e.x-camera[0]-9, e.y-camera[1]-9,18,18))
        # draw player (shadow then player)
        pygame.draw.circle(screen, (0,0,0,150), (int(player.x-camera[0]), int(player.y-camera[1])), 12)
        pygame.draw.rect(screen, player.colour, (player.x-camera[0]-9, player.y-camera[1]-9,18,18))
        # build and apply lighting mask (torches in pixel coords)
        mask = build_light_mask((SCREEN_W, SCREEN_H), (SCREEN_W//2, SCREEN_H//2), player.dir, [(int(tx - camera[0]), int(ty - camera[1]), flick) for tx,ty,flick in torches_px], flicker_state)
        screen.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
        # HUD
        font = pygame.font.SysFont("Arial", 20)
        screen.blit(font.render(f"Time: {int(timer)}", True, (220,220,220)), (12,12))
        screen.blit(font.render(f"Health: {int(player.health)}", True, (220,220,220)), (12,36))
        screen.blit(font.render(f"Score: {int(player.score)}", True, (220,220,220)), (12,60))
        pygame.display.flip()

def main():
    # simple flow: menu -> choose colour -> play -> save score if win
    default_colour = PLAYER_COLOURS[0][1]
    while True:
        res = main_menu()
        start_colour = default_colour
        name = "Player"
        if res == "play":
            start_colour = default_colour
        elif isinstance(res, tuple) and res[0] == "colour":
            start_colour = res[1]
            default_colour = start_colour
        # run game
        result, score = run_game(start_colour)
        if result == "win":
            # ask for name (quick prompt)
            name = "TheOM4R"
            save_highscore(name, score)
            # show win screen
            show_screen = True
            t = 0.0
            while show_screen:
                dt = clock.tick(30)/1000.0
                t += dt
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        show_screen = False
                screen.fill((10,10,10))
                display_text_center(screen, f"You escaped! Score: {score}", SCREEN_H//2 - 20, 28)
                display_text_center(screen, "Press any key to continue", SCREEN_H//2 + 20, 18)
                pygame.display.flip()
        elif result == "fail":
            # show fail screen briefly
            show_screen = True
            t = 0.0
            while show_screen:
                dt = clock.tick(30)/1000.0
                t += dt
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        show_screen = False
                screen.fill((0,0,0))
                display_text_center(screen, "You failed. Try again", SCREEN_H//2 - 20, 28)
                display_text_center(screen, "Press any key to continue", SCREEN_H//2 + 20, 18)
                pygame.display.flip()

if __name__ == "__main__":
    main()
