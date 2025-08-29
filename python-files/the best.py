# -*- coding: utf-8 -*-
import random, sys, os

# Enable ANSI colors on Windows 10+
if os.name=='nt':
    import ctypes
    kernel32=ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11),7)

# Cross-platform getch
if os.name=='nt':
    import msvcrt
    def getch():
        ch=msvcrt.getch()
        if ch in b'\x00\xe0': msvcrt.getch(); return ''
        try: return ch.decode('utf-8').lower()
        except: return ''
else:
    import tty, termios
    def getch():
        fd=sys.stdin.fileno()
        old=termios.tcgetattr(fd)
        try: tty.setraw(fd); ch=sys.stdin.read(1)
        finally: termios.tcsetattr(fd,termios.TCSADRAIN,old)
        return ch.lower()

# ANSI colors
COLORS={'GRASS':'\033[32m','TREE':'\033[33m','BUSH':'\033[32;1m','PLAYER':'\033[33;1m','WALL':'\033[37;1m','FLOOR':'\033[37m','DOOR':'\033[33;1m','MOUNTAIN':'\033[37;1m','WATER':'\033[34;1m','BRIDGE':'\033[33;1m','RESET':'\033[0m'}

# Tiles
T_GRASS='.'; T_TREE='|'; T_PLAYER='@'; T_WALL='#'; T_FLOOR='-'; T_DOOR='+'; T_MOUNTAIN='^'; T_WATER='~'; T_BUSH='☘' if os.name!='nt' else '*'; T_BRIDGE=','
PASSABLE={T_GRASS,T_FLOOR,T_DOOR,T_BRIDGE}
MAP_W,MAP_H=140,60

# --- Utilities ---
def clear_screen(): os.system('cls' if os.name=='nt' else 'clear')
def clamp(n,a,b): return max(a,min(n,b))

# --- Map generation functions ---
def make_empty_map(w,h): return [[T_GRASS]*w for _ in range(h)]

def generate_mountains(grid,rng):
    H,W=len(grid),len(grid[0])
    peaks = [(rng.randint(0,W-1), rng.randint(0,H-1), rng.randint(3,6)) for _ in range(3)]
    for y in range(H):
        for x in range(W):
            min_dist = min([((px - x)**2 + (py - y)**2)**0.5 for px,py,r in peaks])
            p = max(0, 0.15 - min_dist/25.0 + rng.uniform(-0.03,0.03))
            if rng.random()<p: grid[y][x]=T_MOUNTAIN
    return grid

def generate_water(grid,rng,lakes=6):
    H,W=len(grid),len(grid[0]); created=0; attempts=0
    while created<lakes and attempts<lakes*10:
        attempts+=1
        x=rng.randint(2,W-3); y=rng.randint(2,H-3)
        if grid[y][x]!=T_GRASS: continue
        size=rng.randint(12,180); stack=[(x,y)]; touched=set()
        while stack and len(touched)<size:
            cx,cy=stack.pop()
            if (cx,cy) in touched or grid[cy][cx]!=T_GRASS: continue
            touched.add((cx,cy))
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=cx+dx,cy+dy
                if 1<nx<W-1 and 1<ny<H-1 and rng.random()<0.85: stack.append((nx,ny))
        if len(touched)>=8:
            for cx,cy in touched: grid[cy][cx]=T_WATER
            created+=1
    # Add bridges horizontally across rivers
    for y in range(H):
        water_runs = []
        start=None
        for x in range(W):
            if grid[y][x]==T_WATER and start is None: start=x
            elif grid[y][x]!=T_WATER and start is not None:
                if x-start>2 and rng.random()<0.2:
                    for bx in range(start,x): grid[y][bx]=T_BRIDGE
                start=None
        if start is not None and W-start>2 and rng.random()<0.2:
            for bx in range(start,W): grid[y][bx]=T_BRIDGE
    return grid

def scatter_vegetation(grid,rng):
    H,W=len(grid),len(grid[0])
    for y in range(H):
        for x in range(W):
            if grid[y][x]!=T_GRASS: continue
            r=rng.random()
            if r<0.012: grid[y][x]=T_TREE
            elif r<0.012+0.008: grid[y][x]=T_BUSH
    return grid

def rect_intersects(grid,x,y,w,h):
    H,W=len(grid),len(grid[0])
    for iy in range(y,y+h):
        for ix in range(x,x+w):
            if ix<0 or iy<0 or ix>=W or iy>=H or grid[iy][ix]!=T_GRASS: return True
    return False

def place_cabins(grid,rng,count=7):
    H,W=len(grid),len(grid[0]); cabins=[]; attempts=0
    while len(cabins)<count and attempts<60:
        attempts+=1
        cw,ch=rng.randint(4,10),rng.randint(4,10)
        x,y=rng.randint(2,W-cw-3),rng.randint(2,H-ch-3)
        if rect_intersects(grid,x,y,cw,ch): continue
        for iy in range(y,y+ch):
            for ix in range(x,x+cw):
                grid[iy][ix]=T_WALL if iy in (y,y+ch-1) or ix in (x,x+cw-1) else T_FLOOR
        for ix in range(x+1,x+cw-1):
            if grid[y][ix]==T_WALL: grid[y][ix]=T_DOOR; break
        cabins.append((x,y,cw,ch))
    return grid,cabins

def place_player(grid,rng):
    H,W=len(grid),len(grid[0])
    for _ in range(2000):
        x,y=rng.randint(2,W-3),rng.randint(2,H-3)
        if grid[y][x]==T_GRASS: return x,y
    return 1,1

def generate_map(seed=None):
    rng=random.Random(seed)
    grid=make_empty_map(MAP_W,MAP_H)
    grid=generate_mountains(grid,rng)
    grid=generate_water(grid,rng)
    grid=scatter_vegetation(grid,rng)
    grid,cabins=place_cabins(grid,rng)
    px,py=place_player(grid,rng)
    return grid,(px,py),cabins

def render_view(grid,player_pos,view_w=41,view_h=21):
    H,W=len(grid),len(grid[0]); px,py=player_pos
    left=clamp(px-view_w//2,0,W-view_w); top=clamp(py-view_h//2,0,H-view_h)
    lines=[]
    for y in range(top,top+view_h):
        row=[]
        for x in range(left,left+view_w):
            c=grid[y][x]; color=COLORS['RESET']
            if (x,y)==(px,py): color=COLORS['PLAYER']; c=T_PLAYER
            elif c==T_GRASS: color=COLORS['GRASS']
            elif c==T_TREE: color=COLORS['TREE']
            elif c==T_BUSH: color=COLORS['BUSH']
            elif c==T_WALL: color=COLORS['WALL']
            elif c==T_FLOOR: color=COLORS['FLOOR']
            elif c==T_DOOR: color=COLORS['DOOR']
            elif c==T_MOUNTAIN: color=COLORS['MOUNTAIN']
            elif c==T_WATER: color=COLORS['WATER']
            elif c==T_BRIDGE: color=COLORS['BRIDGE']
            row.append(f"{color}{c}{COLORS['RESET']}")
        lines.append(''.join(row))
    return '\n'.join(lines)

def is_passable(grid,x,y): return 0<=x<len(grid[0]) and 0<=y<len(grid) and grid[y][x] in PASSABLE

def game_loop(seed=None):
    grid,(px,py),cabins=generate_map(seed)
    help_text="WASD move, R regenerate, Q quit"
    while True:
        clear_screen(); print(render_view(grid, (px,py)))
        print(help_text)
        ch=getch()
        if ch=='q': break
        elif ch=='r': grid,(px,py),cabins=generate_map(seed); continue
        dx=dy=0
        if ch=='w': dy=-1
        elif ch=='s': dy=1
        elif ch=='a': dx=-1
        elif ch=='d': dx=1
        nx,ny=px+dx,py+dy
        if is_passable(grid,nx,ny): px,py=nx,ny

if __name__=='__main__': game_loop()
