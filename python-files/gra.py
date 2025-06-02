import pygame
import sys
import random
import os
from datetime import datetime

pygame.init()
screen = pygame.display.set_mode((1200, 800))
bg = pygame.transform.scale(pygame.image.load('tlo.png'), (1200, 800))
player = pygame.image.load('samolot.png')
enemy = pygame.image.load('samolot2.png')
powerup_img = pygame.transform.scale(pygame.image.load('powerup.jpg'), (100, 80))
font = pygame.font.SysFont(None, 48)

x, y = 600, 400
player_speed = 5
player_width, player_height = player.get_size()
p_rect = pygame.Rect(x, y, player_width, player_height)

enemies = []
powerups = []
score = 0
score_timer = pygame.time.get_ticks()
start_time = pygame.time.get_ticks()
spawn_timer = pygame.time.get_ticks()
spawn_delay = 2000
enemy_speed = 2
powerup_spawn_timer = pygame.time.get_ticks()
powerup_spawn_delay = random.randint(10000, 30000)
powerup_duration = 10000
speed_boost_active = False
speed_boost_end = 0
invincibility_active = False
invincibility_end = 0

def zapisz_wynik(wynik):
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plik = "baza_wynikow.txt"
    wyniki = []
    try:
        if os.path.exists(plik):
            with open(plik, "r", encoding="utf-8") as f:
                for linia in f:
                    linia = linia.strip()
                    if linia:
                        cz = linia.split(" ", 1)
                        if cz[0].isdigit() and len(cz) > 1:
                            wyniki.append((int(cz[0]), cz[1]))
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")
    
    wyniki.append((wynik, teraz))
    wyniki.sort(reverse=True, key=lambda x: x[0])
    
    try:
        with open(plik, "w", encoding="utf-8") as f:
            for w, d in wyniki:
                f.write(f"{w} {d}\n")
    except Exception as e:
        print(f"Błąd podczas zapisu pliku: {e}")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            zapisz_wynik(score)
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    move_speed = 8 if speed_boost_active else 5
    x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * move_speed
    y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * move_speed
    x = max(0, min(1200 - player_width, x))
    y = max(0, min(800 - player_height, y))
    p_rect.topleft = (x, y)

    now = pygame.time.get_ticks()

    if now - spawn_timer > spawn_delay:
        enemies.append(pygame.Rect(1200, random.randint(0, 750), 50, 50))
        spawn_timer = now

    if now - powerup_spawn_timer > powerup_spawn_delay:
        powerup_type = random.choice(["speed", "invincibility"])
        powerups.append((pygame.Rect(1200, random.randint(0, 750), 50, 50), powerup_type))
        powerup_spawn_timer = now
        powerup_spawn_delay = random.randint(10000, 30000)

    if now - score_timer > 1000:
        score += 1
        score_timer = now

    level = (now - start_time) // 10000
    enemy_speed = 2 + level
    spawn_delay = max(500, 2000 - level * 150)

    if speed_boost_active and now > speed_boost_end:
        speed_boost_active = False
    if invincibility_active and now > invincibility_end:
        invincibility_active = False

    screen.blit(bg, (0, 0))
    screen.blit(player, (x, y))

    for e in enemies[:]:
        e.x -= enemy_speed
        screen.blit(enemy, e.topleft)
        if p_rect.colliderect(e) and not invincibility_active:
            zapisz_wynik(score)
            pygame.quit()
            sys.exit()
        if e.x < -50:
            enemies.remove(e)

    for p, p_type in powerups[:]:
        p.x -= 3
        screen.blit(powerup_img, p.topleft)
        if p_rect.colliderect(p):
            if p_type == "speed":
                speed_boost_active = True
                speed_boost_end = now + powerup_duration
            elif p_type == "invincibility":
                invincibility_active = True
                invincibility_end = now + powerup_duration
            powerups.remove((p, p_type))
        if p.x < -50:
            powerups.remove((p, p_type))

    screen.blit(font.render(f'Punkty: {score}', True, (255, 255, 255)), (10, 10))
    if speed_boost_active:
        time_left = (speed_boost_end - now) // 1000
        screen.blit(font.render(f'Speed Boost: {time_left}s', True, (0, 255, 0)), (10, 50))
    if invincibility_active:
        time_left = (invincibility_end - now) // 1000
        screen.blit(font.render(f'Invincibility: {time_left}s', True, (0, 255, 255)), (10, 90))

    pygame.display.flip()
    pygame.time.delay(16)
