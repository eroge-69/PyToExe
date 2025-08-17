# super_pixel.py
import pygame, sys, os
from dataclasses import dataclass

pygame.init()
pygame.display.set_caption("Super Pixel")

# -------- Settings --------
WIDTH, HEIGHT = 960, 540
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

TILE = 32
GRAVITY = 0.7
MOVE_SPEED = 4
JUMP_SPEED = 13
MAX_FALL = 20
FONT = pygame.font.SysFont("arial", 20)

# Colors
SKY = (200, 240, 255)   # bright sky
GROUND = (90, 70, 50)
BRICK = (180, 80, 60)
PLAYER_COL = (240, 230, 80)
ENEMY_COL = (200, 50, 70)
COIN_COL = (255, 215, 0)
FLAG_COL = (70, 200, 120)
UI_BG = (50, 50, 50)
UI_FG = (255, 255, 255)

# -------- Levels --------
LEVELS = [
[
    "                                                                 ",
    "                                                                 ",
    "             C     C      XX             C                       ",
    "       XX                        XX                               ",
    "                   XXX                 C                          ",
    "   P            C       C      XXX                                 ",
    "XXXXXXX     XXXXXXXX         XXXXXXX          E        C       F   ",
    "XXXXXXX  C  XXXXXXXX     C   XXXXXXX   C   XXXXX    XXXXX   XXXXX  ",
    "XXXXXXX XXXXXXXX   XXX XXXXX XXXXXXXX XXX XXXXXXX XXXXXXX XXXXXXXX ",
    "XXXXXXX XXXXXXXX   XXX XXXXX XXXXXXXX XXX XXXXXXX XXXXXXX XXXXXXXX ",
],
[
    "                                                                 ",
    "                                                                 ",
    "       C       C          E         C      C                     ",
    "             XXXX                     XXXX                       ",
    "   P      C        C     XXXXX      C                            ",
    "XXXXXXX        XXXXXXX        XXXXXXXX         F                  ",
    "XXXXXXX   E    XXXXXXX   C    XXXXXXXX    C  XXXXX  E   XXXXX     ",
    "XXXXXXX XXXXXXX   XXXX XXXXXXX XXXXXXX XXXXX XXXXX XXXXX XXXXX    ",
    "XXXXXXX XXXXXXX   XXXX XXXXXXX XXXXXXX XXXXX XXXXX XXXXX XXXXX    ",
    "XXXXXXX XXXXXXX   XXXX XXXXXXX XXXXXXX XXXXX XXXXX XXXXX XXXXX    ",
],
]

# -------- Music --------
def try_music():
    try:
        if os.path.exists("music.mp3"):
            pygame.mixer.music.load("music.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            print("🎵 Music playing (music.mp3)")
        else:
            print("⚠ No music.mp3 found, running silent.")
    except Exception as e:
        print("Music error:", e)

def sign(x): return (x > 0) - (x < 0)

@dataclass
class Camera:
    offset_x: int = 0
    def apply(self, rect): return rect.move(-self.offset_x, 0)
    def update(self, target_rect, level_width):
        self.offset_x = max(0, min(target_rect.centerx - WIDTH//2,
                                   level_width - WIDTH))

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(BRICK if (x//TILE + y//TILE) % 2 else GROUND)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        s = TILE // 2
        self.image = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COIN_COL, (s//2, s//2), s//2)
        self.rect = self.image.get_rect(center=(x+TILE//2, y+TILE//2))

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE*2), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (220,220,220), (0,0,4,TILE*2))
        pygame.draw.polygon(self.image, FLAG_COL,
                            [(4,8),(TILE, TILE//2),(4,TILE-8)])
        self.rect = self.image.get_rect(bottomleft=(x, y + TILE))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(ENEMY_COL)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = pygame.Vector2(-2, 0)
    def update(self, tiles):
        self.rect.x += int(self.vel.x)
        for t in tiles:
            if self.rect.colliderect(t.rect):
                if self.vel.x > 0: self.rect.right = t.rect.left
                else: self.rect.left = t.rect.right
                self.vel.x *= -1

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(PLAYER_COL)
        pygame.draw.rect(self.image, (240,90,80), (0,0,TILE,TILE//4))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.vel = pygame.Vector2(0,0)
        self.on_ground = False
        self.coins = 0
        self.lives = 3
        self.win = False
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vel.x = -MOVE_SPEED
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vel.x = MOVE_SPEED
        else: self.vel.x = 0
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = -JUMP_SPEED
    def physics(self, tiles):
        self.vel.y = min(self.vel.y + GRAVITY, MAX_FALL)
        self.rect.x += int(self.vel.x)
        for t in tiles:
            if self.rect.colliderect(t.rect):
                if self.vel.x > 0: self.rect.right = t.rect.left
                elif self.vel.x < 0: self.rect.left = t.rect.right
        self.rect.y += int(self.vel.y)
        self.on_ground = False
        for t in tiles:
            if self.rect.colliderect(t.rect):
                if self.vel.y > 0:
                    self.rect.bottom = t.rect.top; self.vel.y = 0; self.on_ground=True
                elif self.vel.y < 0:
                    self.rect.top = t.rect.bottom; self.vel.y = 0
    def update(self, tiles, coins, enemies, flag, level_height):
        if self.win: return
        self.handle_input(); self.physics(tiles)
        for c in list(coins):
            if self.rect.colliderect(c.rect): self.coins+=1; c.kill()
        for e in list(enemies):
            if self.rect.colliderect(e.rect): self.lives-=1; e.kill()
        if flag and self.rect.colliderect(flag.rect): self.win=True
        # Fall check
        if self.rect.top > level_height + 200:
            self.lives -= 1
            self.rect.topleft = (64,64)
            self.vel = pygame.Vector2(0,0)

def build_level(level_data):
    tiles=pygame.sprite.Group(); coins=pygame.sprite.Group()
    enemies=pygame.sprite.Group(); player=None; flag=None
    for j,row in enumerate(level_data):
        for i,ch in enumerate(row):
            x,y=i*TILE, j*TILE
            if ch=="X": tiles.add(Tile(x,y))
            elif ch=="P": player=Player(x,y-TILE)
            elif ch=="C": coins.add(Coin(x,y))
            elif ch=="E": enemies.add(Enemy(x,y-TILE))
            elif ch=="F": flag=Flag(x,y-TILE)
    if player is None: player=Player(64,64)
    return tiles, coins, enemies, player, flag

def draw_ui(player, level_idx):
    pygame.draw.rect(SCREEN, UI_BG, (0,0,WIDTH,38))
    txt=f"Level:{level_idx+1}/{len(LEVELS)} | Coins:{player.coins}  Lives:{player.lives}"
    SCREEN.blit(FONT.render(txt, True, UI_FG),(10,5))
    controls="Controls: Arrows/WASD = Move/Jump, Space = Jump, Esc = Quit"
    SCREEN.blit(FONT.render(controls, True, UI_FG),(10,20))

def main():
    try_music()
    level_idx = 0
    while level_idx < len(LEVELS):
        level = LEVELS[level_idx]
        tiles,coins,enemies,player,flag=build_level(level)
        camera=Camera()
        level_width=len(level[0])*TILE
        level_height=len(level)*TILE

        while True:
            CLOCK.tick(FPS)
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            player.update(tiles,coins,enemies,flag, level_height)
            enemies.update(tiles)
            camera.update(player.rect, level_width)

            SCREEN.fill(SKY)
            for t in tiles: SCREEN.blit(t.image, camera.apply(t.rect))
            for c in coins: SCREEN.blit(c.image, camera.apply(c.rect))
            for en in enemies: SCREEN.blit(en.image, camera.apply(en.rect))
            if flag: SCREEN.blit(flag.image, camera.apply(flag.rect))
            SCREEN.blit(player.image, camera.apply(player.rect))
            draw_ui(player, level_idx)

            if player.win:
                SCREEN.blit(FONT.render("You Win this Level! Press Enter for next.", True,(0,0,0)),
                            (WIDTH//2-180, 60))
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    level_idx += 1
                    break
            if player.lives <= 0:
                SCREEN.blit(FONT.render("Game Over! Press Esc to quit.", True,(200,0,0)),
                            (WIDTH//2-150, 60))

            pygame.display.flip()

if __name__=="__main__": main()
