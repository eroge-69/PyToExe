import threading

import math
import random

import os
import time

import pygame
import sys

current_directory = os.getcwd()

shared = current_directory+"/shared"
shared = os.path.realpath(shared)

## simple pygame stuff

pygame.init()

fps = 0
start_time = time.time()

width = 1000
height = 1000

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("wip","icon.ico")

font = pygame.font.SysFont("Impact",35)

clock = pygame.time.Clock()
gameRunning = True
inMenu = True
noSplatters = False

maxMarbles = 100
marbleCount = 2
remainingMarbles = 0
spawned = False

powerups = ["sawblade","speed"]
gamePowerups = []
powerupSize = 55

marbleImageNames = ["basic.png", "love.png", "sad.png", "zombie.png", "-_-.png", "angry.png"]
marbles = []
splatters = []

marbleSpeed = 2

playX = width / 3
playY = height / 3.5

playSizeX = width / 3
playSizeY = height / 9

playCollide = pygame.Rect(playX, playY, playSizeX, playSizeY)

quitX = width / 3
quitY = height * 0.45

quitSizeX = width / 3
quitSizeY = height / 9

quitCollide = pygame.Rect(quitX, quitY, quitSizeX, quitSizeY)

leftX = width / 5
marbleButtonY = height / 3.45

marbleButtonSizeX = width / 10
marbleButtonSizeY = height / 10

leftCollide = pygame.Rect(leftX, marbleButtonY, marbleButtonSizeX, marbleButtonSizeY)

rightX = width / 15

rightCollide = pygame.Rect(rightX, marbleButtonY, marbleButtonSizeX, marbleButtonSizeY)

## functions

def splatter(posX,posY,marblecolor,sizemodify):

    global noSplatters
    global splatters

    if noSplatters:

        return

    splatters.append([posX,posY,random.randint(60,200)*sizemodify,random.randint(60,200)*sizemodify,random.randint(-360,360),marblecolor]) ## posX, posY, randomSizeX, randomSizeY, randomRotation, color of the parent marble

def powerupsStart(interval):

    global inMenu
    global remainingMarbles
    global gamePowerups
    global powerups

    while True:

        time.sleep(1)

        if not inMenu and len(gamePowerups) < 3 and remainingMarbles > 1:

            posX = random.randint(100,900)
            posY = random.randint(100,900)

            newPowerup = powerups[random.randint(0,len(powerups) - 1)]
            gamePowerups.append([newPowerup,posX,posY]) ## random powerup, powerup posX, powerup posY

            time.sleep(interval)

## rendering

start_time = time.time()

powerupThread = threading.Thread(target=powerupsStart,args=(8,))
powerupThread.start()

while gameRunning:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            
            gameRunning = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            if playCollide.collidepoint(mouse_pos):
                
                if inMenu:

                    if marbleCount >= 2:

                        inMenu = False

            if quitCollide.collidepoint(mouse_pos):
                    
                    if inMenu:
                        
                        gameRunning = False

                        pygame.quit()
                        sys.exit()

            if leftCollide.collidepoint(mouse_pos):
                
                if inMenu:

                    if marbleCount > 2:
                        
                        marbleCount -= 1

            if rightCollide.collidepoint(mouse_pos):
                
                if inMenu:

                    if marbleCount < maxMarbles:
                        
                        marbleCount += 1
    
    if inMenu == True:

        marbles.clear()
        splatters.clear()
        gamePowerups.clear()
        marbleSpeed = 5

        remainingMarbles = 0
        spawned = False
        
        pygame.display.set_caption("Marble Game Customizer", "icon.ico")
        pygame.display.set_icon(pygame.image.load(current_directory+"/icon.ico"))
        screen.fill((12, 13, 20))

        pygame.draw.rect(screen, (0,255,0), playCollide)
        pygame.draw.rect(screen, (255,0,0), quitCollide)
        pygame.draw.rect(screen, (155,155,155), leftCollide)
        pygame.draw.rect(screen, (255,255,255), rightCollide)

        color = (255,255,255)
        color2 = (255,255,255)

        if marbleCount >= 25:

            color = (255,0,0)

        if fps <= 30:

            color2 = (255,255,0)
        
        if fps <= 15:

            color2 = (255,0,0)
        
        text_surface = font.render(f'Number of Marbles: {marbleCount}', True, color)
        screen.blit(text_surface, (playX, height / 10))

        text_surface2 = font.render(f'FPS: {round(fps)}', True, color2)
        screen.blit(text_surface2, (playX, height / 6))

    elif inMenu == False:

        color2 = (255,255,255)

        if fps <= 30:

            color2 = (255,255,0)
        
        if fps <= 15:

            color2 = (255,0,0)
        
        pygame.display.set_caption(f"Marble Game: {remainingMarbles} Remaining", "gameIcon.ico")
        screen.fill((13, 16, 38, 0))

        if not spawned:

            pygame.display.set_icon(pygame.image.load(current_directory+"/gameIcon.ico"))
            
            remainingMarbles = marbleCount


            for marbleFound in range(remainingMarbles):

                marbles.append([0, 0, "basic.png", 0, 0, 0, 0, "marble", 2, (255,255,255, 255), False]) ## posX, posY, marbleImage, sizeX, sizeY, moveX, moveY, marbleName, lives, color, hasSawblade
        
        newcount = 0
        nameCounting = 0

        for foundSplatter in splatters:

            if noSplatters:

                continue
            
            image = pygame.image.load(shared+"/splatter1.png").convert_alpha()
            image = pygame.transform.rotate(image,foundSplatter[4])
            newImage = pygame.transform.scale(image, (foundSplatter[2],foundSplatter[3]))

            tint_color = foundSplatter[5]

            tint_surface = newImage.copy()
            tint_surface.fill(tint_color, None, pygame.BLEND_RGBA_MULT)

            screen.blit(tint_surface, (foundSplatter[0],foundSplatter[1]))

        for foundPowerup in gamePowerups:

            image = pygame.image.load(shared+"/powerups/"+foundPowerup[0]+".png").convert_alpha()
            newImage = pygame.transform.scale(image, (powerupSize,powerupSize))

            screen.blit(newImage, (foundPowerup[1], foundPowerup[2]))

        for marbleFound in marbles:
            
            newcount += 1
            posX = 0
            posY = 0
            image = "/basic.png"

            if not spawned:

                nameCounting += 1
                
                posX = random.randint(100,900)
                posY = random.randint(100,900)
                image = "/"+marbleImageNames[random.randint(0,len(marbleImageNames)-1)]

                marbleFound[0] = posX
                marbleFound[1] = posY
                marbleFound[2] = image
                marbleFound[3] = 90
                marbleFound[4] = 90
                marbleFound[5] = random.randint(-100,100)/100
                marbleFound[6] = random.randint(-100,100)/100
                marbleFound[7] = "marble"+str(nameCounting)
                marbleFound[8] = 2
                marbleFound[9] = (random.randint(150,255),random.randint(150,255),random.randint(150,255))

                if marbleFound[5] == 0 and marbleFound[6] == 0:

                    marbleFound[5] = random.randint(1,100)/100 or random.randint(-100,-1)/100

                if marbleFound[6] == 0 and marbleFound[5] == 0:

                    marbleFound[6] = random.randint(1,100)/100 or random.randint(-100,-1)/100

            else:

                image = pygame.image.load(shared+"/marbles"+marbleFound[2]).convert_alpha()

                if marbleFound[5] < 0:

                    pygame.transform.flip(image,True,False)
                
                imagePosX = marbleFound[0]
                imagePosY = marbleFound[1]

                imageSizeX = marbleFound[3]
                imageSizeY = marbleFound[4]

                newImage = pygame.transform.scale(image, (imageSizeX,imageSizeY))

                tint_color = marbleFound[9]

                tint_surface = newImage.copy()
                tint_surface.fill(tint_color, None, pygame.BLEND_RGBA_MIN)

                screen.blit(tint_surface, (imagePosX,imagePosY))

                if remainingMarbles <= 1:

                    continue

                marbleFound[0] = (marbleFound[0] + marbleFound[5] * marbleSpeed)
                marbleFound[1] = (marbleFound[1] + marbleFound[6] * marbleSpeed)

                if marbleFound[0] <= width*0.01 or marbleFound[0] >= width*0.9:

                    marbleFound[5] = -marbleFound[5]

                    ##if marbleFound[1] < (height * 0.46):

                        ##marbleFound[6]

                    ##marbleFound[6] = random.randint(1,100)/100 or random.randint(-100,-1)/100

                if marbleFound[1] <= height*0.1 or marbleFound[1] >= height*0.9:

                    marbleFound[6] = -marbleFound[6]
                    ##marbleFound[5] = random.randint(1,100)/100 or random.randint(-100,-1)/100

                if marbleFound[0] <= 0 or marbleFound[0] >= width * 0.95:

                    marbles.remove(marbleFound)

                if marbleFound[1] <= 0 or marbleFound[1] >= height * 0.95:

                    marbles.remove(marbleFound)
                
                if marbleFound[10]:

                    sawImage = pygame.image.load(shared+"/sawblade.png").convert_alpha()
                    newSawImage = pygame.transform.scale(sawImage, (marbleFound[3] + 50, marbleFound[4] + 50))
                    #newSawImage = pygame.transform.rotate(newSawImage, random.randint(-2,2))
                    screen.blit(newSawImage, (imagePosX-25,imagePosY-25))

                collision = pygame.Rect(imagePosX, imagePosY, imageSizeX, imageSizeY)

                for collisions in marbles:
                    
                    if collisions == marbleFound:
                        
                        continue

                    newCollision = pygame.Rect(collisions[0], collisions[1], collisions[3], collisions[4])

                    if collision.colliderect(newCollision):

                        #collisions[5] = -collisions[5]
                        #collisions[6] = -collisions[6]

                        #marbleFound[5] = -marbleFound[5]
                        #marbleFound[6] = -marbleFound[6]

                        if marbleFound[10]:

                            if not collisions[10]:

                                collisions[8] -= 1

                                if collisions[8] <= 0:

                                    splatter(collisions[0],collisions[1],collisions[9],1)
                                    marbles.remove(collisions)

                                else:

                                    splatter(collisions[0],collisions[1],collisions[9],0.5)

                                marbleFound[10] = False

                            else:
                                
                                marbleFound[10] = False
                                collisions[10] = False



                for collisions in gamePowerups:

                    newCollision = pygame.Rect(collisions[1], collisions[2], powerupSize, powerupSize)

                    if collision.colliderect(newCollision):

                        if collisions[0] == "sawblade":

                            marbleFound[10] = True

                        if collisions[0] == "speed":

                            marbleFound[5] = random.randint(-100,100)/100
                            marbleFound[6] = random.randint(-100,100)/100

                            if marbleFound[5] == 0 and marbleFound[6] == 0:

                                marbleFound[5] = random.randint(1,100)/100 or random.randint(-100,-1)/100

                            if marbleFound[6] == 0 and marbleFound[5] == 0:

                                marbleFound[6] = random.randint(1,100)/100 or random.randint(-100,-1)/100

                        gamePowerups.remove(collisions)

        remainingMarbles = newcount

        spawned = True

        text_surface = font.render(f'Marbles Remaining: {remainingMarbles}', True, (255,255,255))
        screen.blit(text_surface, (playX, height / 25))

        text_surface2 = font.render(f'FPS: {round(fps)}', True, color2)
        screen.blit(text_surface2, (playX, height / 12))

    if not inMenu:

        if remainingMarbles < 2 and remainingMarbles > 0:

            marbleCount = 2

            winningMarble = marbles[0]
            text_surface = font.render(f'{winningMarble[7]} wins!', True, (0,255,0))
            screen.blit(text_surface, (playX, height / 5))
            
            pygame.display.update()

            time.sleep(2)

            inMenu = True

        if remainingMarbles < 1:

            marbleCount = 2

            winningMarble = None
            text_surface = font.render("no marbles win!", True, (255,255,0))
            screen.blit(text_surface, (playX, height / 5))
            
            pygame.display.update()

            time.sleep(2)

            inMenu = True
    
    pygame.display.update()
        
    fps = clock.get_fps()

    clock.tick(60)

pygame.quit()
sys.exit()