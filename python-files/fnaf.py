import pygame as pg, random, sys

pg.init()
W,H=800,600
screen=pg.display.set_mode((W,H))
pg.display.set_caption("FNAF Simplu - 60s/hour")

font=pg.font.SysFont("Arial",24)

# culori
COL_BG=(10,10,10)
COL_OFFICE=(40,40,40)
COL_TABLE=(90,90,90)
COL_BONNIE=(120,60,200)
COL_CHICA=(240,220,50)
COL_FOXY=(200,40,40)
COL_FREDDY=(180,100,50)
COL_TEXT=(250,250,250)
COL_YELLOW=(250,250,100)

# camere
CAM_LIST=["1A","1B","2A","2B","3","4A","4B","5","7"]

# trasee
PATH_BONNIE=["1A","1B","2A","2B","OFFICE_LEFT"]
PATH_CHICA=["1A","1B","4A","4B","OFFICE_RIGHT"]
PATH_FREDDY=["1A","1B","4A","4B","OFFICE_RIGHT"]

class Anim:
    def __init__(self,name,color,path):
        self.name=name
        self.color=color
        self.path=path
        self.pos=0
        self.room=path[0]
        self.timer=pg.time.get_ticks()
        self.delay=random.randint(4000,7000)
    def update(self):
        now=pg.time.get_ticks()
        if now-self.timer>self.delay:
            if self.pos<len(self.path)-1:
                self.pos+=1
                self.room=self.path[self.pos]
            else:
                if self.room=="OFFICE_LEFT" and not game.left.closed:
                    game.gameover(self)
                if self.room=="OFFICE_RIGHT" and not game.right.closed:
                    game.gameover(self)
                self.pos=0
                self.room=self.path[0]
            self.timer=now
            self.delay=random.randint(4000,7000)

class Foxy:
    def __init__(self):
        self.name="Foxy"; self.color=COL_FOXY
        self.room="7"; self.stage=0
        self.timer=pg.time.get_ticks()
        self.warning=False
        self.warn_time=0
    def update(self):
        now=pg.time.get_ticks()
        if now-self.timer>5000:
            if game.active_cam!="7": # daca nu-l privesti
                self.stage=min(3,self.stage+1)
            self.timer=now
        if self.stage>=3:
            if not self.warning:
                self.warning=True
                self.warn_time=pg.time.get_ticks()
            if now-self.warn_time>2000:
                if game.left.closed:
                    game.power-=5  # consum curent
                    self.stage=0
                    self.warning=False
                else:
                    game.gameover(self)
    def draw_on_cam(self,feed):
        if self.room=="7":
            pg.draw.circle(screen,self.color,feed.center,40+self.stage*20)
            game.text("FOXY",feed.centerx,feed.centery-60,center=True)

class Door:
    def __init__(self,side):
        self.side=side
        self.closed=False
        self.light=False

class Game:
    def __init__(self):
        self.running=True
        self.clock=pg.time.Clock()
        self.active_cam=None
        self.left=Door("left")
        self.right=Door("right")
        self.power=100
        self.last_power=pg.time.get_ticks()
        self.bonnie=Anim("Bonnie",COL_BONNIE,PATH_BONNIE)
        self.chica=Anim("Chica",COL_CHICA,PATH_CHICA)
        self.freddy=Anim("Freddy",COL_FREDDY,PATH_FREDDY)
        self.foxy=Foxy()
        self.start_time=pg.time.get_ticks()
        self.hour=0
    def text(self,txt,x,y,col=COL_TEXT,center=False):
        s=font.render(txt,True,col)
        r=s.get_rect()
        if center: r.center=(x,y)
        else: r.topleft=(x,y)
        screen.blit(s,r)
    def draw_office(self):
        screen.fill(COL_OFFICE)
        pg.draw.rect(screen,COL_TABLE,(W//2-100,H-120,200,60))
        pg.draw.circle(screen,(200,200,200),(W//2,80),15)
        if self.left.closed: pg.draw.rect(screen,(80,80,80),(0,150,60,300))
        else: pg.draw.rect(screen,(0,0,0),(0,150,60,300))
        if self.right.closed: pg.draw.rect(screen,(80,80,80),(W-60,150,60,300))
        else: pg.draw.rect(screen,(0,0,0),(W-60,150,60,300))
        if self.left.light and self.power>0:
            pg.draw.polygon(screen,COL_YELLOW,[(180,200),(360,120),(360,420)])
            if self.bonnie.room=="OFFICE_LEFT":
                pg.draw.circle(screen,self.bonnie.color,(80,H//2),60)
            if self.foxy.warning: # Foxy chiar la usa
                pg.draw.circle(screen,self.foxy.color,(100,H//2),70)
        if self.right.light and self.power>0:
            pg.draw.polygon(screen,COL_YELLOW,[(W-180,200),(W-360,120),(W-360,420)])
            if self.chica.room=="OFFICE_RIGHT":
                pg.draw.circle(screen,self.chica.color,(W-80,H//2),60)
            if self.freddy.room=="OFFICE_RIGHT":
                pg.draw.circle(screen,self.freddy.color,(W-120,H//2),70)
    def draw_cams(self):
        screen.fill(COL_BG)
        feed=pg.Rect(100,80,600,360)
        pg.draw.rect(screen,(20,20,20),feed)
        self.text("CAM "+self.active_cam,feed.centerx,feed.top-30,center=True)
        if self.bonnie.room==self.active_cam:
            pg.draw.circle(screen,self.bonnie.color,feed.center,40)
            self.text("BONNIE",feed.centerx,feed.centery-60,center=True)
        if self.chica.room==self.active_cam:
            pg.draw.circle(screen,self.chica.color,(feed.centerx+80,feed.centery),40)
            self.text("CHICA",feed.centerx+80,feed.centery-60,center=True)
        if self.freddy.room==self.active_cam:
            pg.draw.circle(screen,self.freddy.color,(feed.centerx-80,feed.centery),40)
            self.text("FREDDY",feed.centerx-80,feed.centery-60,center=True)
        if self.active_cam=="7": self.foxy.draw_on_cam(feed)
        if self.active_cam=="1A":
            if self.bonnie.pos==0: pg.draw.circle(screen,self.bonnie.color,(feed.centerx-100,feed.centery+40),40)
            if self.chica.pos==0: pg.draw.circle(screen,self.chica.color,(feed.centerx+100,feed.centery+40),40)
            if self.freddy.pos==0: pg.draw.circle(screen,self.freddy.color,(feed.centerx,feed.centery-40),40)
    def hud(self):
        hour_text="12 AM" if self.hour==0 else f"{self.hour} AM"
        self.text(f"Power: {int(self.power)}%",10,10)
        self.text(hour_text,W-120,10)
        if self.foxy.warning:
            self.text("FOXY IS COMING!",W//2,H//2,col=(255,0,0),center=True)
    def update_power(self):
        now=pg.time.get_ticks()
        if now-self.last_power>1000:
            usage=1
            if self.left.closed: usage+=1
            if self.right.closed: usage+=1
            if self.left.light: usage+=1
            if self.right.light: usage+=1
            if self.active_cam: usage+=1
            self.power-=usage*0.05
            self.last_power=now
            if self.power<=0: self.gameover(None)
    def update_time(self):
        now=pg.time.get_ticks()
        hours=(now-self.start_time)//60000
        self.hour=hours
        if self.hour>=6: self.win()
    def gameover(self,who):
        screen.fill((0,0,0))
        if who: self.text(f"{who.name} te-a prins!",W//2,H//2,center=True)
        else: self.text("Ai ramas fara curent!",W//2,H//2,center=True)
        pg.display.flip(); pg.time.wait(4000)
        pg.quit(); sys.exit()
    def win(self):
        screen.fill((0,0,0))
        self.text("6 AM! Ai supravietuit!",W//2,H//2,center=True)
        pg.display.flip(); pg.time.wait(4000)
        pg.quit(); sys.exit()
    def run(self):
        while self.running:
            for e in pg.event.get():
                if e.type==pg.QUIT: pg.quit(); sys.exit()
                if e.type==pg.KEYDOWN:
                    if e.key==pg.K_SPACE:
                        if self.active_cam: self.active_cam=None
                        else: self.active_cam="1A"
                    if e.key in [pg.K_1,pg.K_2,pg.K_3,pg.K_4,pg.K_5,pg.K_6,pg.K_7,pg.K_8,pg.K_9]:
                        self.active_cam=CAM_LIST[int(e.unicode)-1]
                    if e.key==pg.K_a: self.left.closed=not self.left.closed
                    if e.key==pg.K_d: self.right.closed=not self.right.closed
                    if e.key==pg.K_q: self.left.light=not self.left.light
                    if e.key==pg.K_e: self.right.light=not self.right.light
            self.bonnie.update(); self.chica.update(); self.freddy.update(); self.foxy.update()
            self.update_power(); self.update_time()
            if self.active_cam: self.draw_cams()
            else: self.draw_office()
            self.hud()
            pg.display.flip(); self.clock.tick(30)

game=Game()
game.run()
