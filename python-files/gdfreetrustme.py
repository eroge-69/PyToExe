import pygame # pyright: ignore[reportMissingImports]
import sys
import random

#important
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Geometry Dash! (100% free!) No Virus! Real Game By Temmie Creator Of Geometry Dash! (Definitely) (Trust Me Bro)")


#color
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

#text stuff
score = 0
font = pygame.font.Font('freesansbold.ttf',32)
textx = 10
texty = 10
d = 0

#tags
sprites = []
mobilesprites = []
traps = []

#optimization
obstaclesOnScreen = 0

#objects
class object:
    def __init__(self,posx,posy,width,height,speedx,speedy,color,isMobile,isTrap):
        sprites.append(self)
        self.x = posx
        self.y = posy
        self.w = width
        self.h = height
        self.sx = speedx
        self.sy = speedy
        self.c = color
        self.onGround = False
        if isMobile:
            mobilesprites.append(self)
        else:
            del self.sx,self.sy
        if isTrap:
            self.isDisabled = False
            traps.append(self)
    def getBottom(object):
        return object.y+object.h/2
    def getTop(object):
        return object.y-object.h/2
    def getRight(object):
        return object.x+object.w/2
    def getLeft(object):
        return object.x-object.w/2
    def accelerate(object,value):
        object.sy += value

trapspeed = -2.5

scorekeeper = object(150,300,5,5,-2.5,0,WHITE,True,False)
player = object(100,300,50,50,0,5,BLUE,True,False)
ground = object(0,500,800,50,0,0,BLACK,False,False)

#obstacles

#obstacle = object(550,450,50,50,trapspeed,0,RED,True,True)
anchor = 550

#random obstacle is picked next; can be changed
def createObstacle(anchor,limit):
    match random.randint(0,11):
        case 0: #one trap
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            limit += 1
        case 1: #two traps in row
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            limit += 2
        case 2: #three traps in row
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            limit += 3
        case 3: #two in a column
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,400,50,50,trapspeed,0,RED,True,True)
            limit += 2
        case 4: #square
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor,400,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,400,50,50,trapspeed,0,RED,True,True)
            limit += 4
        case 5: #staircase left
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor,400,50,50,trapspeed,0,RED,True,True)
            limit += 3
        case 6: #staircase right
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,400,50,50,trapspeed,0,RED,True,True)
            limit += 3
        case 7: #seperated two in a row (same as three in a row)
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            limit += 2
        case 8: #three in a column
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,400,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,375,50,50,trapspeed,0,RED,True,True)
            limit += 3
        case 9: #tight jump
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor,300,50,50,trapspeed,0,RED,True,True)
            limit += 2
        case 10: #tight jump with two column
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+150,400,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor,300,50,50,trapspeed,0,RED,True,True)
            limit += 3
        case 11: #mock spike (same as three in a row)
            obstacle = object(anchor,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+100,450,50,50,trapspeed,0,RED,True,True)
            obstacle = object(anchor+50,400,50,50,trapspeed,0,RED,True,True)
            limit += 4
    return anchor + 500, limit



#framerate
clock = pygame.time.Clock()

collision = True

#main
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player.onGround:
                player.sy = -6
                collision = False
    
    #gravity for player only
    player.accelerate(1/10)

    #optimization, max 20 objects on screen so it shouldnt lag as much
    #if obstaclesOnScreen <= 20:
    #since you cant delete class instances the easiest optimization technique is just making it generate obstacles slower
    if score%6 == 0:
        anchor, obstaclesOnScreen = createObstacle(anchor,obstaclesOnScreen)
    #
    #sacrificed playability for preformance, if you find a better way you can fix it
    #optimization removed
    #
    #please find new optimization there are >11k objects by 200m

    #update position for mobile sprites
    for sprite in mobilesprites:
        sprite.x += sprite.sx
        sprite.y += sprite.sy
    
    #collision detection for player only
    if collision:
        if player.getBottom() > ground.getTop() and player.getTop() < ground.getBottom():
            player.onGround = True
            player.sy = 0
            player.y += -0.1
        else:
            player.onGround = False
        #die from traps
        for trap in traps:
            if player.getRight() > trap.getLeft() and player.getLeft() < trap.getRight() and player.getBottom() > trap.getTop() and player.getTop() < trap.getBottom():
                textx = 200
                texty = 250
                scorekeeper.sx = 0
                player.y = 1000
                d = 100
                for trap in traps:
                    trap.sx = 0
    #this SHOULD remove sprites when offscreen (optimization) but it generates them in front faster so it doesnt matter lol
    #mightve fixed it now
    #made the game worse; ~80m obstacle generation slows
    for trap in traps:
        #if trap.x < -50 and not trap.isDisabled:
        #    obstaclesOnScreen -= 1
        #    trap.isDisabled = True
        #    del trap
        if trap.x < -50:
            del trap
    #how score is tracked
    if scorekeeper.x < player.x:
        scorekeeper.x += 50
        score += 1

    #draw
    screen.fill(WHITE)
    for sprite in sprites:
        pygame.draw.rect(screen, sprite.c, (sprite.x, sprite.y, sprite.w, sprite.h))
    #show score
    s = font.render("Distance Travelled: "+str(score)+"m",True,BLACK)
    t = font.render("Click to jump!",True,BLACK)
    screen.blit(s,(textx,texty))
    screen.blit(t,(textx+565+d,texty))
    #optimization debug
    #print(obstaclesOnScreen)
    pygame.display.flip()
    
    
    collision = True

    #60 fps
    clock.tick(60)
