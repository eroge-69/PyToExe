import pygame
import random
import time
pygame.init()
score = 0
w = 900
h = 900
screen = pygame.display.set_mode((w,h))
square = pygame.Rect((438,438,24,24))
coin = pygame.Rect((0,0,10,10))
run = True

font = pygame.font.SysFont("comfortaa", 50)

def draw_text(text,font,color,x,y):
    screen.fill((0,0,0))

    text = font.render(text, True, color)
    screen.blit(text, (x,y))

def coin_collect():
    coinx = random.randint(200,800) - coin.x
    coiny = random.randint(200,800) - coin.y
    coin.move_ip(coinx,coiny)
    t = 5

coin_collect()

def time():
    square = pygame.Rect((438, 438, 24, 24))
    score = 0
    coin_collect()

while run:
    if square.colliderect(coin):
        score += 1
        coin_collect()

    key = pygame.key.get_pressed()
    if key[pygame.K_w] == True:
        square.move_ip(0,-1)
    elif key[pygame.K_s] == True:
        square.move_ip(0,1)
    elif key[pygame.K_a] == True:
        square.move_ip(-1,0)
    elif key[pygame.K_d] == True:
        square.move_ip(1,0)

    scoreprint = str(score)
    screen.fill((0, 0, 0))
    draw_text(scoreprint, font, (255, 255, 255), 440, 10)

    pygame.draw.rect(screen,(255,255,255),square)
    pygame.draw.rect(screen, (255, 255, 0), coin)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()