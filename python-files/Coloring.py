import pygame 
import os
os.chdir('/storage/emulated/0/')
from pygame_etools.xyconverter import xy_convert
from pygame_etools.eprint import printx
pygame.init()
os.chdir('/storage/emulated/0/Coloring')

size=40

fingerx,fingery=0,0
sizechn=False
sizechp=False
screen=pygame.display.set_mode((5,5))
blue_rect=pygame.Rect(0,200,100,100)
blue_rect.center=100,200
black_rect=pygame.Rect(0,200,100,100)
black_rect.center=100,400
red_rect=pygame.Rect(0,200,100,100)
red_rect.center=100,600
green_rect=pygame.Rect(0,200,100,100)
green_rect.center=100,800
brown_rect=pygame.Rect(0,200,100,100)
brown_rect.center=100,1000
purple_rect=pygame.Rect(0,200,100,100)
purple_rect.center=1820,200
yellow_rect=pygame.Rect(0,200,100,100)
yellow_rect.center=1820,400
cyan_rect=pygame.Rect(0,200,100,100)
cyan_rect.center=1820,600
orange_rect=pygame.Rect(0,200,100,100)
orange_rect.center=1820,800
pink_rect=pygame.Rect(0,200,100,100)
pink_rect.center=1820,1000
surface=pygame.surface.Surface((100,100))
clear_=pygame.image.load('cross.png').convert()
cleard=pygame.transform.scale(clear_,(50,50))
close=pygame.transform.scale(clear_,(100,100))
close_rect=close.get_rect(center=(920,100))
d=pygame.image.load('up.png').convert()
e=pygame.image.load('down.png').convert()
up=pygame.transform.scale(d,(100,100))
down=pygame.transform.scale(e,(100,100))
up_rect=up.get_rect(center=(200,100))
down_rect=down.get_rect(center=(350,100))
eraser_img=pygame.image.load('Eraser.png').convert()
Eraser=pygame.transform.scale(eraser_img,(100,100))
Eraser_rect=Eraser.get_rect()
Eraser_rect.center=(1820,50)
clear_rect=cleard.get_rect(center=(50,50))
finger_rect=pygame.Rect(fingerx,fingery,100,100)
run=True
col='black'
def clear():
	screen.fill('white')
clear()
while run:
	colrect='blue'
	for event in pygame.event.get():
		if event.type==pygame.FINGERMOTION:
			pos=xy_convert(event.x,event.y)
			pygame.draw.circle(screen,col,pos,size)
		if event.type==pygame.FINGERDOWN:
			pos=xy_convert(event.x,event.y)
			fingerx,fingery=pos
			finger_rect.center=pos
			if finger_rect.colliderect(blue_rect):
				colrect='green'
				col='blue'
			elif finger_rect.colliderect(clear_rect):
				clear()
			elif finger_rect.colliderect(close_rect):
				run=False
			elif finger_rect.colliderect(black_rect):
				col='black'
			elif finger_rect.colliderect(red_rect):
				col='red'
			elif finger_rect.colliderect(green_rect):
				col='green'
			elif finger_rect.colliderect(cyan_rect):
				col='cyan'
			elif finger_rect.colliderect(yellow_rect):
				col='yellow'
			elif finger_rect.colliderect(purple_rect):
				col='purple'
			elif finger_rect.colliderect(down_rect):
				sizechn=True
			elif finger_rect.colliderect(up_rect):
				sizechp=True
			elif finger_rect.colliderect(brown_rect):
				col='brown'
			elif finger_rect.colliderect(pink_rect):
				col='pink'
			elif finger_rect.colliderect(orange_rect):
				col='orange'
			elif finger_rect.colliderect(Eraser_rect):
				col='white'
			
			else:
				pygame.draw.circle(screen,col,pos,size)
		if event.type==pygame.FINGERUP:
			sizechn=False
			sizechp=False	
	if sizechn:
				screen.blit(surface,(450,100))	
				surface.fill('white')
				pygame.draw.circle(surface,col,(50,50),size)
				printx(surface,str(size),(0,0),50,'black')
				size-=1
	elif sizechp:
				screen.blit(surface,(450,100))	
				surface.fill('white')
				pygame.draw.circle(surface,col,(50,50),size)
				printx(surface,str(size),(0,0),50,'black')
				size+=1
				
	pygame.draw.rect(screen,colrect,blue_rect)
	pygame.draw.rect(screen,'black',black_rect)
	pygame.draw.rect(screen,'red',red_rect)
	pygame.draw.rect(screen,'green',green_rect)
	pygame.draw.rect(screen,'brown',brown_rect)
	pygame.draw.rect(screen,'purple',purple_rect)
	pygame.draw.rect(screen,'yellow',yellow_rect)
	pygame.draw.rect(screen,'cyan',cyan_rect)
	pygame.draw.rect(screen,'pink',pink_rect)
	pygame.draw.rect(screen,'orange',orange_rect)
	screen.blit(cleard,clear_rect)
	screen.blit(close,close_rect)
	screen.blit(down,down_rect)
	screen.blit(up,up_rect)
	screen.blit(Eraser,Eraser_rect)
	pygame.display.flip()
			