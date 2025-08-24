# win_window_pygame.py
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys, os

# Si quieres forzar un backend en Windows con drivers antiguos:
# os.environ.setdefault("SDL_VIDEODRIVER", "windib")  # normalmente no hace falta

try:
    import pygame
except ImportError:
    print("ERROR: Necesitas instalar pygame (pip install pygame).")
    sys.exit(1)

WIDTH, HEIGHT = 960, 540
CAPTION = "WOMB-OS Game Window (pygame)"
BG = (24, 28, 35)
ACCENT = (255, 102, 153)

def init_pygame():
    pygame.init()
    # Preparar ventana redimensionable
    flags = pygame.RESIZABLE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption(CAPTION)

    # Ícono simple generado por código (evita depender de un PNG)
    icon = pygame.Surface((32, 32))
    icon.fill((0, 0, 0))
    pygame.draw.circle(icon, ACCENT, (16, 16), 12, 0)
    pygame.display.set_icon(icon)
    return screen

def draw_debug_overlay(screen, fps_clock):
    font = pygame.font.Font(None, 22)
    txt = "FPS: %0.1f  Size: %dx%d  F11: Fullscreen  ESC: Exit" % (
        fps_clock.get_fps(), screen.get_width(), screen.get_height()
    )
    surf = font.render(txt, True, (230, 230, 230))
    screen.blit(surf, (8, 8))

def toggle_fullscreen(current_screen):
    size = (current_screen.get_width(), current_screen.get_height())
    is_full = current_screen.get_flags() & pygame.FULLSCREEN
    if is_full:
        return pygame.display.set_mode(size, pygame.RESIZABLE)
    else:
        info = pygame.display.Info()
        return pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

def main():
    screen = init_pygame()
    clock = pygame.time.Clock()
    running = True

    # Para demostrar input: un “player” cuadrito
    px, py = screen.get_width() // 2, screen.get_height() // 2
    speed = 300.0  # px/seg
    rect_size = 40

    # Fixed timestep (simple): integrador con dt del clock
    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS cap
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    screen = toggle_fullscreen(screen)

        # Input continuo (WASD / flechas)
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += speed * dt

        px += dx; py += dy

        # Clamp a los bordes de ventana
        px = max(0, min(px, screen.get_width() - rect_size))
        py = max(0, min(py, screen.get_height() - rect_size))

        # Render
        screen.fill(BG)
        pygame.draw.rect(screen, ACCENT, (int(px), int(py), rect_size, rect_size))
        draw_debug_overlay(screen, clock)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()