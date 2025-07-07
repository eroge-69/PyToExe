import pygame
from qpython.network import Network
pygame.init()

screen=pygame.display.set_mode((0,0))

client_number=0

class player:
	def __init__(self,x,y,w,h,col):
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		self.col=col
		self.pos=self.x,self.y
		self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
	
	def draw(self,screen):
		pygame.draw.rect(screen,self.col,self.rect)
		
	def update(self):
		self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
		self.pos=self.x,self.y
		
def read_pos(strs):
	strs=strs.split(",")
	return (int(strs[0]),int(strs[1]))

def make_pos(tup):
		return str(tup[0])+","+str(tup[1])
		
def redraw(player,screen,p2):
	screen.fill('white')
	player.draw(screen)
	p2.draw(screen)
	pygame.display.flip()

def main():
	n=Network()
	startpos=read_pos(n.getpos())
	Player=player(startpos[0],startpos[1],100,100,'green')
	p2=player(0,0,100,100,'red')
	run=True
	while run:
		try:
			p2po=n.send(make_pos(Player.pos))
			p2pos=read_pos(p2po)
			p2.x=p2pos[0]
			p2.y=p2pos[1]
			p2.update()
		except:
			...
		for event in pygame.event.get():
			if event.type==pygame.FINGERMOTION:
				Player.x,Player.y=int(((event.x*screen.get_width())*10)//10),int(((event.y*screen.get_height())*10)//10)
				Player.update()
				
		redraw(Player,screen,p2)
	
main()