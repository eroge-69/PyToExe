
import pygame
import random
pygame.init()
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undertale-like RPG")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
clock = pygame.time.Clock()
FPS = 60
player = pygame.Rect(300, 220, 40, 40)
player_speed = 4
bullets = []
STATE_EXPLORE = "explore"
STATE_BATTLE = "battle"
state = STATE_EXPLORE
font = pygame.font.SysFont("Arial", 20)
def draw_explore():
    win.fill((30, 30, 30))
    pygame.draw.rect(win, WHITE, player)
    txt = font.render("Exploring... Walk around. Random battles may occur.", True, WHITE)
    win.blit(txt, (10, 10))
def draw_battle():
    win.fill(BLACK)
    arena = pygame.Rect(220, 350, 200, 100)
    pygame.draw.rect(win, WHITE, arena, 2)
    pygame.draw.rect(win, RED, player)
    for bullet in bullets:
        pygame.draw.circle(win, RED, (int(bullet.x), int(bullet.y)), bullet.radius)
    txt = font.render("Dodge the bullets! Survive for 10 seconds!", True, WHITE)
    win.blit(txt, (160, 20))
def spawn_bullet():
    bullet = pygame.Rect(random.randint(220, 420), 350, 0, 0)
    bullet.radius = 5
    bullet.speed_x = random.choice([-2, -1, 1, 2])
    bullet.speed_y = -random.randint(2, 4)
    bullets.append(bullet)
battle_timer = 0
battle_duration = 10 * FPS
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if state == STATE_EXPLORE:
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_UP]:
            player.y -= player_speed
        if keys[pygame.K_DOWN]:
            player.y += player_speed
        if random.randint(0, 200) == 0:
            state = STATE_BATTLE
            player.x, player.y = 300, 380
            battle_timer = 0
            bullets.clear()
        draw_explore()
    elif state == STATE_BATTLE:
        battle_timer += 1
        if battle_timer % 15 == 0:
            spawn_bullet()
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed
        if keys[pygame.K_UP]:
            player.y -= player_speed
        if keys[pygame.K_DOWN]:
            player.y += player_speed
        player.clamp_ip(pygame.Rect(220, 350, 200, 100))
        for bullet in bullets:
            bullet.x += bullet.speed_x
            bullet.y += bullet.speed_y
        for bullet in bullets:
            dist = ((player.centerx - bullet.x)**2 + (player.centery - bullet.y)**2) ** 0.5
            if dist < bullet.radius + 20:
                state = STATE_EXPLORE
                player.x, player.y = 300, 220
        if battle_timer >= battle_duration:
            state = STATE_EXPLORE
            player.x, player.y = 300, 220
        draw_battle()
    pygame.display.update()
pygame.quit()
