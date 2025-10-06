import os
import pygame
from pygame.locals import *

pygame.init()
SCREEN = pygame.display.set_mode((640, 360))
pygame.display.set_caption("Klik – ucz się śpiewać")
FONT = pygame.font.SysFont(None, 36)

NOTES_DIR = os.path.join(os.path.dirname(__file__), "notes")
notes = {}

for fname in os.listdir(NOTES_DIR):
    if fname.lower().endswith(".wav"):
        key = os.path.splitext(fname)[0]
        notes[key] = pygame.mixer.Sound(os.path.join(NOTES_DIR, fname))

buttons = list(notes.keys())
cols = 5
btn_w, btn_h = 100, 60
gap = 15

def draw():
    SCREEN.fill((30, 30, 30))
    for i, name in enumerate(buttons):
        r = i // cols
        c = i % cols
        x = 30 + c * (btn_w + gap)
        y = 30 + r * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        pygame.draw.rect(SCREEN, (220, 220, 220), rect, border_radius=10)
        txt = FONT.render(name, True, (20, 20, 20))
        SCREEN.blit(txt, (x + 25, y + 15))
    pygame.display.flip()

running = True
while running:
    draw()
    for ev in pygame.event.get():
        if ev.type == QUIT:
            running = False
        elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            for i, name in enumerate(buttons):
                r = i // cols
                c = i % cols
                x = 30 + c * (btn_w + gap)
                y = 30 + r * (btn_h + gap)
                rect = pygame.Rect(x, y, btn_w, btn_h)
                if rect.collidepoint(mx, my):
                    notes[name].play()

pygame.quit()
