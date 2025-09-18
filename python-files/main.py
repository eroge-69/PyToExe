"""
Bosnia and Herzegovina — Simple Map Jigsaw + City Quiz (main.py)

This is the same program as before: simplified jigsaw of BiH map + city quiz.

See README.txt for instructions.
"""
import sys, math, random, pygame

WIDTH, HEIGHT = 1000, 700
FPS = 60
WHITE, BLACK, GRAY = (255,255,255), (0,0,0), (200,200,200)
GREEN, RED, BLUE, YELLOW = (100,180,100), (200,80,80), (80,120,200), (240,220,100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bosnia & Herzegovina — Jigsaw + City Quiz")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
bigfont = pygame.font.SysFont(None, 40)

pieces_def = [
    {"poly":[(0.15,0.15),(0.35,0.12),(0.45,0.22),(0.38,0.32),(0.22,0.30)], "color":(200,150,150)},
    {"poly":[(0.05,0.28),(0.15,0.15),(0.22,0.30),(0.12,0.42)], "color":(150,200,150)},
    {"poly":[(0.45,0.22),(0.65,0.18),(0.78,0.26),(0.62,0.36),(0.50,0.30)], "color":(150,150,200)},
    {"poly":[(0.28,0.34),(0.38,0.32),(0.50,0.30),(0.48,0.42),(0.32,0.46)], "color":(200,200,150)},
    {"poly":[(0.50,0.30),(0.62,0.36),(0.58,0.52),(0.47,0.46)], "color":(180,150,220)},
    {"poly":[(0.22,0.46),(0.47,0.46),(0.50,0.62),(0.28,0.70),(0.12,0.56)], "color":(150,220,200)},
    {"poly":[(0.50,0.62),(0.65,0.58),(0.78,0.70),(0.60,0.78),(0.50,0.70)], "color":(220,170,150)},
]
cities = {
    "Sarajevo": (0.40,0.40),
    "Banja Luka": (0.24,0.22),
    "Mostar": (0.40,0.60),
    "Tuzla": (0.57,0.36),
    "Zenica": (0.35,0.36),
    "Bijeljina": (0.70,0.22),
    "Prijedor": (0.18,0.25),
    "Doboj": (0.56,0.44),
    "Brčko": (0.66,0.30)
}
MAP_X, MAP_Y, MAP_W, MAP_H = 200, 60, 560, 560
def norm_to_map(pt): return (MAP_X + int(pt[0]*MAP_W), MAP_Y + int(pt[1]*MAP_H))
def point_dist(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])

class Piece:
    def __init__(self, poly_norm, color):
        self.target_poly=[norm_to_map(p) for p in poly_norm]
        self.color=color
        xs,ys=[p[0] for p in self.target_poly],[p[1] for p in self.target_poly]
        self.target_rect=pygame.Rect(min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys))
        self.offset=(random.randint(-300,300),random.randint(-200,200))
        self.update_current_poly()
        self.placed=False
    def update_current_poly(self):
        self.current_poly=[(x+self.offset[0],y+self.offset[1]) for (x,y) in self.target_poly]
        xs,ys=[p[0] for p in self.current_poly],[p[1] for p in self.current_poly]
        self.rect=pygame.Rect(min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys))
    def draw(self,surf,highlight=False):
        pygame.draw.polygon(surf,self.color,self.current_poly)
        pygame.draw.polygon(surf,BLACK,self.current_poly,2 if highlight else 1)
    def try_snap(self):
        tx=sum(p[0] for p in self.target_poly)/len(self.target_poly)
        ty=sum(p[1] for p in self.target_poly)/len(self.target_poly)
        cx=sum(p[0] for p in self.current_poly)/len(self.current_poly)
        cy=sum(p[1] for p in self.current_poly)/len(self.current_poly)
        if point_dist((tx,ty),(cx,cy))<30:
            dx,dy=tx-cx,ty-cy
            self.offset=(self.offset[0]+dx,self.offset[1]+dy)
            self.update_current_poly(); self.placed=True; return True
        return False

pieces=[Piece(d["poly"],d["color"]) for d in pieces_def]; random.shuffle(pieces)
dragging=None; drag_offset=(0,0)
game_state="jigsaw"; quiz_city_list=list(cities.keys()); random.shuffle(quiz_city_list)
quiz_index=0; quiz_score=0
def all_placed(): return all(p.placed for p in pieces)
def draw_cities(surf,show_labels=False):
    for n,pn in cities.items():
        pos=norm_to_map(pn); pygame.draw.circle(surf,BLACK,pos,5)
        if show_labels: surf.blit(font.render(n,True,BLACK),(pos[0]+6,pos[1]-6))

running=True
while running:
    clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: running=False
        elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            mx,my=ev.pos
            if game_state=="jigsaw":
                for p in reversed(pieces):
                    if p.rect.collidepoint((mx,my)) and not p.placed:
                        dragging=p; drag_offset=(mx-p.offset[0],my-p.offset[1]); pieces.remove(p); pieces.append(p); break
            elif game_state=="quiz" and quiz_index<len(quiz_city_list):
                target=norm_to_map(cities[quiz_city_list[quiz_index]])
                if point_dist((mx,my),target)<18:
                    quiz_score+=1; quiz_index+=1
                    if quiz_index>=len(quiz_city_list): game_state="done"
        elif ev.type==pygame.MOUSEBUTTONUP and ev.button==1 and dragging:
            dragging.try_snap(); dragging=None
            if all_placed(): game_state="quiz"
        elif ev.type==pygame.MOUSEMOTION and dragging:
            mx,my=ev.pos; dragging.offset=(mx-drag_offset[0],my-drag_offset[1]); dragging.update_current_poly()

    screen.fill(WHITE)
    if game_state=="jigsaw":
        for p in pieces: p.draw(screen,p is dragging)
    elif game_state=="quiz":
        for p in pieces: p.draw(screen)
        screen.blit(bigfont.render("Click: "+quiz_city_list[quiz_index],True,BLUE),(20,20))
        draw_cities(screen)
    elif game_state=="done":
        for p in pieces: p.draw(screen)
        draw_cities(screen,True)
        screen.blit(bigfont.render(f"Score {quiz_score}/{len(quiz_city_list)}",True,GREEN),(20,20))
    pygame.display.flip()
pygame.quit(); sys.exit()
