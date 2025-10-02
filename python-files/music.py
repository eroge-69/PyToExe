import pygame
import pygame.mixer_music
import sys

pygame.init()
pygame.mixer.init()

pygame.mixer_music.load("14-Cool-Edge-Night.wav")
pygame.mixer_music.play()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.mixer.music.stop()
pygame.quit()
sys.exit()