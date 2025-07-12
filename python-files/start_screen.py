# -*- coding: utf-8 -*-
import pygame
import sys
import subprocess

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("KasabaSim Baslangic")

font = pygame.font.SysFont("Arial", 36)
button_rect = pygame.Rect(300, 400, 200, 60)
bg_image = pygame.image.load("assets/maps/menu_background.png")  # senin çizdiğin giriş ekranı

running = True
def new_func(font):
    text_surface = font.render("Baslat!", True, (255, 255, 255))
    return text_surface

while running:
    screen.blit(bg_image, (0, 0))

    pygame.draw.rect(screen, (20, 100, 200), button_rect)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3)

    text_surface = new_func(font)
    screen.blit(text_surface, (button_rect.x + 40, button_rect.y + 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            pygame.quit()
            subprocess.call(["python", "main.py"])
            sys.exit()

    pygame.display.flip()
