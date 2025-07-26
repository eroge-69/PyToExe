import pygame, sys, time
from pygame.locals import *
pygame.init()

window = pygame.display.set_mode((1, 1), 0, 32)
screen_position = window.get_rect()
pygame.display.set_caption('One Pixel Game')

colour_value_1 = 0
colour_value_2 = 0
colour_value_3 = 0
increase_1 = False
decrease_1 = False
increase_2 = False
decrease_2 = False
increase_3 = False
decrease_3 = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_1:
                increase_1 = True
            elif event.key == K_2:
                decrease_1 = True
            if event.key == K_3:
                increase_2 = True
            elif event.key == K_4:
                decrease_2 = True
            if event.key == K_5:
                increase_3 = True
            elif event.key == K_6:
                decrease_3 = True
        if event.type == KEYUP:
            if event.key == K_1:
                increase_1 = False
            elif event.key == K_2:
                decrease_1 = False
            if event.key == K_3:
                increase_2 = False
            elif event.key == K_4:
                decrease_2 = False
            if event.key == K_5:
                increase_3 = False
            elif event.key == K_6:
                decrease_3 = False

    if increase_1 and colour_value_1 < 255:
        colour_value_1 += 1
    if decrease_1 and colour_value_1 > 0:
        colour_value_1 -= 1
    if increase_2 and colour_value_2 < 255:
        colour_value_2 += 1
    if decrease_2 and colour_value_2 > 0:
        colour_value_2 -= 1
    if increase_3 and colour_value_3 < 255:
        colour_value_3 += 1
    if decrease_3 and colour_value_3 > 0:
        colour_value_3 -= 1

    window.fill((colour_value_1, colour_value_2, colour_value_3))
    pygame.display.update()
    time.sleep(0.01)
