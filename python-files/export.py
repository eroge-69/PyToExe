#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 20:50:04 2025

@author: sm
"""


import pygame
import sys
import math
import os

REVEAL_RADIUS = 150
FEATHER = 80

base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
BACKGROUND_IMAGE = os.path.join(base_path, "background.jpg")
FOREGROUND_IMAGE = os.path.join(base_path, "foreground.jpg")

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Reveal mit Verschieben/Drehen & Soft-Edge")
clock = pygame.time.Clock()

bg_orig = pygame.image.load(BACKGROUND_IMAGE).convert_alpha()
fg_orig = pygame.image.load(FOREGROUND_IMAGE).convert_alpha()

def scale_to_window(surf, win_size, zoom=1.0):
    w, h = surf.get_size()
    W, H = win_size
    # Skalierung auf Fenster + Zoom
    ratio = min(W / w, H / h) * zoom
    return pygame.transform.smoothscale(surf, (max(1, int(w * ratio)), max(1, int(h * ratio))))

def centered_rect(surf, win_size, offset=(0, 0)):
    sw, sh = surf.get_size()
    W, H = win_size
    return pygame.Rect((W - sw) // 2 + offset[0], (H - sh) // 2 + offset[1], sw, sh)

def create_feathered_circle(radius, feather):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = radius
    for y in range(size):
        for x in range(size):
            dist = math.hypot(x - cx, y - cy)
            if dist < radius - feather:
                alpha = 255
            elif dist < radius:
                alpha = int(255 * (radius - dist) / feather)
            else:
                alpha = 0
            surf.set_at((x, y), (255, 255, 255, alpha))
    return surf

mask_surf = create_feathered_circle(REVEAL_RADIUS, FEATHER)
mask_w, mask_h = mask_surf.get_size()

fg_angle = 0
fg_offset = pygame.Vector2()
step, step_shift = 1, 5
angle_step, angle_step_ctrl = 0.5, 3

zoom = 1.0
zoom_min = 0.5
zoom_max = 5.0
zoom_step = 0.1

def handle_keys(event, angle, offset, zoom):
    mod = event.mod
    shift, ctrl = (mod & pygame.KMOD_SHIFT), (mod & pygame.KMOD_CTRL)
    key = event.key
    if shift and ctrl:
        if key == pygame.K_LEFT: angle -= angle_step_ctrl
        elif key == pygame.K_RIGHT: angle += angle_step_ctrl
    elif shift:
        if key == pygame.K_LEFT: angle -= angle_step
        elif key == pygame.K_RIGHT: angle += angle_step
    elif ctrl:
        if key == pygame.K_LEFT: offset.x -= step_shift
        elif key == pygame.K_RIGHT: offset.x += step_shift
        elif key == pygame.K_UP: offset.y -= step_shift
        elif key == pygame.K_DOWN: offset.y += step_shift
    else:
        # Zoom +/-
        if key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            zoom = min(zoom_max, zoom + zoom_step)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            zoom = max(zoom_min, zoom - zoom_step)
        # Offset Moves
        elif key == pygame.K_LEFT:
            offset.x -= step
        elif key == pygame.K_RIGHT:
            offset.x += step
        elif key == pygame.K_UP:
            offset.y -= step
        elif key == pygame.K_DOWN:
            offset.y += step
    return angle % 360, offset, zoom

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
        if e.type == pygame.KEYDOWN:
            fg_angle, fg_offset, zoom = handle_keys(e, fg_angle, fg_offset, zoom)
            if e.key == pygame.K_SPACE:
                # Tausche die Bilder
                bg_orig, fg_orig = fg_orig, bg_orig
                fg_angle = -fg_angle
                fg_offset = -fg_offset
                mask_surf = create_feathered_circle(REVEAL_RADIUS, FEATHER)

    win_size = screen.get_size()
    bg_scaled = scale_to_window(bg_orig, win_size)  # Hintergrund ohne Zoom, Fenster-skalieren

    # Vordergrund mit Fenstergröße und Zoom skalieren
    fg_scaled = scale_to_window(fg_orig, win_size, zoom)

    # Rotation mit Antialiasing via rotozoom(scale=1)
    fg_rot = pygame.transform.rotozoom(fg_scaled, fg_angle, 1)
    fg_w, fg_h = fg_rot.get_size()

    # Mausposition
    mx, my = pygame.mouse.get_pos()

    # Bildrechteck zentriert mit Offset
    fg_rect = centered_rect(fg_rot, win_size, (fg_offset.x, fg_offset.y))

    # Berechne Offset-Verschiebung für Zoom um Maus:
    # Relativ zum Fensterzentrum
    win_cx, win_cy = win_size[0] // 2, win_size[1] // 2

    # Verhältnis der Maus im Fenster (0..1)
    if win_size[0] != 0 and win_size[1] != 0:
        rel_mx = mx / win_size[0]
        rel_my = my / win_size[1]
    else:
        rel_mx = rel_my = 0.5

    # Verschiebung kompensieren, so dass Zoom auf Maus zentriert bleibt
    # Je mehr gezoomt, desto stärker Verschiebung
    # Diese Verschiebung ersetzt parteiweise fg_offset.x/y (kumulativ), darum nur sichtbar bei Zoom-Änderung
    zoom_offset_x = (win_cx - mx) * (zoom - 1)
    zoom_offset_y = (win_cy - my) * (zoom - 1)

    # Nutze zoom_offset mit dem normalen fg_offset
    total_offset = fg_offset + pygame.Vector2(zoom_offset_x, zoom_offset_y)

    # Aktualisiertes Rechteck mit Zoom-Offset
    fg_rect = centered_rect(fg_rot, win_size, (total_offset.x, total_offset.y))

    screen.blit(bg_scaled, centered_rect(bg_scaled, win_size))

    rel_x, rel_y = mx - fg_rect.left, my - fg_rect.top

    mask_x, mask_y = rel_x - REVEAL_RADIUS, rel_y - REVEAL_RADIUS
    img_w, img_h = fg_rot.get_size()

    area_left = max(0, -mask_x)
    area_top = max(0, -mask_y)
    area_w = min(mask_w - area_left, img_w - max(mask_x, 0))
    area_h = min(mask_h - area_top, img_h - max(mask_y, 0))

    if area_w > 0 and area_h > 0:
        mask_area = pygame.Rect(area_left, area_top, area_w, area_h)
        mask_pos = (max(mask_x, 0), max(mask_y, 0))

        temp_fg = fg_rot.copy()
        temp_mask = pygame.Surface(fg_rot.get_size(), pygame.SRCALPHA)
        temp_mask.fill((255, 255, 255, 0))
        temp_mask.blit(mask_surf, mask_pos, area=mask_area)
        temp_fg.blit(temp_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(temp_fg, fg_rect)
    else:
        screen.blit(fg_rot, fg_rect)

    pygame.display.flip()
    clock.tick(100)

