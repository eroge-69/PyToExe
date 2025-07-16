import pygame
import sys
body = pygame.display.set_mode((1100,650))
pygame.display.set_caption("Strong effort")
running=True
color=(52,240,255)
lose=False
win=False
snakex=200
snakey=200
size=20
red=(0,0,0)
fps=250


clock=pygame.time.Clock()

while running:
    for event in pygame.event.get():
        
        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.KEYDOWN:
          if event.key==pygame.K_RIGHT:
            snakex=snakex+10
          
          if event.key==pygame.K_LEFT:
           snakex=snakex-10
          if event.key==pygame.K_UP:
              snakey=snakey-10
          if event.key==pygame.K_DOWN:
             snakey=snakey+10
          

    body.fill(color)
    pygame.draw.rect(body,red,[snakex,snakey,size,size])
    pygame.display.update()

    clock.tick(fps)




             
pygame.quit()
sys.exit()