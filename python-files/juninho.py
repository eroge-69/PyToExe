import pygame
from pygame.locals import *
from sys import exit

pygame.init()

largura = 720
altura = 480

x = largura / 2
y = 0

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Programa que mostra uma tela")

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_a:
                x = x - 20
            if event.key == K_d:
                x = x + 20

    tela.fill((0, 0, 0))
    pygame.draw.rect(tela, (255, 0, 0), (x, y, 40, 50))

    y += 1
    if y >= altura:
        y = 0

    pygame.display.update()
    clock.tick(60)
