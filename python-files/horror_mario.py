import pygame
import sys
import random
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horror Super Mario")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

BLACK = (0, 0, 0)
RED = (139, 0, 0)
DARK_GREY = (20, 20, 20)

player = pygame.Rect(100, HEIGHT - 150, 50, 50)
player_speed = 5
gravity = 1
velocity_y = 0
on_ground = False

enemies = []
def spawn_enemy():
    enemies.append(pygame.Rect(WIDTH + random.randint(0, 100), HEIGHT - 150, 50, 50))

light_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
light_radius = 150

jumpscare = pygame.image.load('jumpscare.png')
jumpscare = pygame.transform.scale(jumpscare, (WIDTH, HEIGHT))
show_jumpscare = False
jumpscare_timer = 0

background = pygame.Surface((WIDTH, HEIGHT))
background.fill(DARK_GREY)

try:
    pygame.mixer.music.load('horror_music.mp3')
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Δεν φορτώθηκε η μουσική:", e)

font = pygame.font.SysFont("comicsansms", 36)

def game_over():
    pygame.mixer.music.stop()
    screen.fill(BLACK)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 50))
    pygame.display.flip()
    pygame.time.delay(3000)
    pygame.quit()
    sys.exit()

spawn_timer = 0

while True:
    screen.blit(background, (0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= player_speed
    if keys[pygame.K_RIGHT]: player.x += player_speed
    if keys[pygame.K_SPACE] and on_ground:
        velocity_y = -20; on_ground = False

    velocity_y += gravity
    player.y += velocity_y
    if player.y >= HEIGHT - 150:
        player.y = HEIGHT - 150; velocity_y = 0; on_ground = True

    spawn_timer += 1
    if spawn_timer > 90:
        spawn_enemy(); spawn_timer = 0

    for e in enemies:
        e.x -= 4
        pygame.draw.rect(screen, RED, e)
        if player.colliderect(e):
            game_over()

    # Flashlight effect: mask με διάταξη φωτός γύρω από τον Mario
    light_mask.fill((0,0,0,180))
    pygame.draw.circle(light_mask, (0,0,0,0), player.center, light_radius)
    screen.blit(light_mask, (0,0))

    pygame.draw.rect(screen, (255,255,255), player)

    # Τυχαία jumpscare (1% κάθε frame)
    if not show_jumpscare and random.random() < 0.01:
        show_jumpscare = True
        jumpscare_timer = pygame.time.get_ticks()

    if show_jumpscare:
        screen.blit(jumpscare, (0,0))
        if pygame.time.get_ticks() - jumpscare_timer > 800:  # 800ms show
            show_jumpscare = False

    pygame.display.flip()
    clock.tick(60)
