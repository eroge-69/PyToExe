import pygame,sys,json,math,os,random
from pygame.locals import *
WIDTH,HEIGHT=800,600
FPS=60
PLAYER_RADIUS=15
ENEMY_RADIUS=18
SAVE_FILE='save.json'
pygame.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Eviter')
clock=pygame.time.Clock()
font=pygame.font.SysFont(None,32)
fontb=pygame.font.SysFont(None,48)
def load_save():
 d={'best_time':0.0,'score':0}
 if not os.path.exists(SAVE_FILE):return d
 try:
  with open(SAVE_FILE,'r')as f:return{'best_time':float(json.load(f).get('best_time',0.0)),'score':int(json.load(f).get('score',0))}
 except:return d
def save_save(s):
 try:
  with open(SAVE_FILE,'w')as f:json.dump(s,f)
 except:pass
class Button:
 def __init__(s,r,t,f):s.r=pygame.Rect(r);s.t=t;s.f=f
 def d(s,sc):pygame.draw.rect(sc,(200,200,200),s.r,border_radius=8);pygame.draw.rect(sc,(100,100,100),s.r,3,border_radius=8);txt=s.f.render(s.t,1,(20,20,20));sc.blit(txt,txt.get_rect(center=s.r.center))
 def c(s,p):return s.r.collidepoint(p)
class Bullet:
 def __init__(s,p,t):s.p=list(p);dx,dy=t[0]-p[0],t[1]-p[1];d=math.hypot(dx,dy)or 1;s.v=[dx/d*400,dy/d*400];s.l=2
 def u(s,dt):s.p[0]+=s.v[0]*dt;s.p[1]+=s.v[1]*dt
 def draw(s,sc):pygame.draw.circle(sc,(255,255,0),(int(s.p[0]),int(s.p[1])),s.l)
def dist(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def main():
 save=load_save();bt=save['best_time'];sc=save['score'];st='menu';pp=[WIDTH//2,HEIGHT//2];pt=pp[:];ep=[50,50];bs=[];bb=[];b_time=0;start=0;et=0;pause_t=0
 btn=Button((WIDTH//2-100,HEIGHT//2-30,200,60),'JOUER',font)
 run=1
 last_click=0
 while run:
  dt=clock.tick(FPS)/1000
  for e in pygame.event.get():
   if e.type==QUIT:run=0
   elif e.type==MOUSEBUTTONDOWN and e.button==1:
    if st=='menu'and btn.c(e.pos):st='playing';pp=[WIDTH//2,HEIGHT//2];pt=pp[:];ep=[50,50];bs=[];bb=[];b_time=pygame.time.get_ticks();start=pygame.time.get_ticks();et=0;pause_t=0;last_click=pygame.time.get_ticks()
    elif st=='playing':
     now=pygame.time.get_ticks()
     if now-last_click<300:bb.append(Bullet(pp,e.pos))
     else:pt=list(e.pos)
     last_click=now
  if st=='playing':
   dx,dy=pt[0]-pp[0],pt[1]-pp[1];d=math.hypot(dx,dy)
   if d>1:step=min(300*dt,d);pp[0]+=dx/d*step;pp[1]+=dy/d*step
   pp[0]=max(PLAYER_RADIUS,min(WIDTH-PLAYER_RADIUS,pp[0]));pp[1]=max(PLAYER_RADIUS,min(HEIGHT-PLAYER_RADIUS,pp[1]))
   et=(pygame.time.get_ticks()-start)/1000
   if pause_t>0:pause_t-=dt
   else:
    es=80+et*10;dx,dy=pp[0]-ep[0],pp[1]-ep[1];d=math.hypot(dx,dy)or 1;ep[0]+=dx/d*es*dt;ep[1]+=dy/d*es*dt
   if dist(pp,ep)<=PLAYER_RADIUS+ENEMY_RADIUS:
    beat=et>bt
    if beat:sc+=10;bt=et
    else:sc-=2
    save={'best_time':bt,'score':sc};save_save(save);st='menu'
   if pygame.time.get_ticks()-b_time>3000:bs.append([random.randint(20,WIDTH-20),random.randint(20,HEIGHT-20)]);b_time=pygame.time.get_ticks()
   for s in bs[:]:
    if dist(pp,s)<=PLAYER_RADIUS+10:sc+=1;bs.remove(s)
   for b in bb[:]:
    b.u(dt)
    if dist(b.p,ep)<=ENEMY_RADIUS+2:pause_t=2;bb.remove(b)
  screen.fill((30,30,40))
  if st=='menu':
   t=fontb.render('Eviter',1,(240,240,240));screen.blit(t,t.get_rect(center=(WIDTH//2,HEIGHT//2-120)))
   btn.d(screen)
   i=font.render(f'Meilleur:{bt:.2f}s Score:{sc}',1,(220,220,220));screen.blit(i,(20,20))
  else:
   pygame.draw.circle(screen,(50,130,240),(int(pp[0]),int(pp[1])),PLAYER_RADIUS)
   pygame.draw.circle(screen,(220,50,50),(int(ep[0]),int(ep[1])),ENEMY_RADIUS)
   for s in bs:pygame.draw.circle(screen,(0,255,0),s,8)
   for b in bb:b.draw(screen)
   screen.blit(font.render(f'Temps:{et:.2f}s',1,(240,240,240)),(20,20))
   screen.blit(font.render(f'Meilleur:{bt:.2f}s',1,(200,200,200)),(20,50))
   screen.blit(font.render(f'Score:{sc}',1,(200,200,200)),(20,80))
  pygame.display.flip()
 pygame.quit();sys.exit()
if __name__=='__main__':main()
