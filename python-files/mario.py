import pygame
import sys
import random
import math

pygame.init()

# OYNA
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash – Qizil Og'iz Kayfiyatsiz 😕")

# RANGLAR
SKY_BLUE = (135, 206, 250)
WHITE = (255, 255, 255)
YELLOW = (255, 221, 51)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
TREE_GREEN = (0, 155, 0)
OBSTACLE_COLOR = (200, 0, 0)

# FPS va FONT
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("arial", 24)

# Qahramon
player_radius = 20
player_x = 100
player_y = SCREEN_HEIGHT - 60
player_y_velocity = 0
gravity = 1
jump_count = 0
max_jumps = 2

# To‘siq
obstacle = pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - 60, 30, 60)
score = 0
passed = False

# Bulutlar
clouds = [{'x': 100, 'y': 60}, {'x': 400, 'y': 100}, {'x': 700, 'y': 70}]
cloud_speed = 1

# Archalar
trees = [{'x': x} for x in range(0, SCREEN_WIDTH + 200, 60)]
tree_speed = 4

# Boshlash holati
game_over = False
waiting_to_start = True

def draw_cloud(x, y):
    pygame.draw.circle(screen, WHITE, (x, y), 20)
    pygame.draw.circle(screen, WHITE, (x + 20, y), 25)
    pygame.draw.circle(screen, WHITE, (x + 40, y), 20)

def draw_trees():
    for tree in trees:
        x = tree['x']
        for i in range(3):
            offset = i * 15
            pygame.draw.polygon(screen, TREE_GREEN, [
                (x + 30, SCREEN_HEIGHT - 60 - offset),
                (x + 10, SCREEN_HEIGHT - 30 - offset),
                (x + 50, SCREEN_HEIGHT - 30 - offset)
            ])

def draw_character(x, y, jumping):
    pygame.draw.circle(screen, YELLOW, (x, y), player_radius)
    pygame.draw.circle(screen, BLACK, (x - 7, y - 5), 3)
    pygame.draw.circle(screen, BLACK, (x + 7, y - 5), 3)
    if jumping:
        mouth_rect = pygame.Rect(x - 9, y + 2, 18, 12)
        pygame.draw.arc(screen, RED, mouth_rect, math.radians(0), math.radians(180), 0)
        pygame.draw.arc(screen, BLACK, mouth_rect, math.radians(0), math.radians(180), 2)
    else:
        pygame.draw.arc(screen, BLACK, (x - 7, y + 7, 14, 10), math.radians(180), math.radians(360), 2)

def reset_game():
    global player_y, player_y_velocity, jump_count, obstacle, score, passed, trees, waiting_to_start
    player_y = SCREEN_HEIGHT - 60
    player_y_velocity = 0
    jump_count = 0
    obstacle.x = SCREEN_WIDTH + random.randint(0, 300)
    score = 0
    passed = False
    trees = [{'x': x} for x in range(0, SCREEN_WIDTH + 200, 60)]
    waiting_to_start = True

# Game loop
while True:
    screen.fill(SKY_BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if waiting_to_start:
        msg = font.render("Boshlash uchun SPACE bosing", True, BLACK)
        screen.blit(msg, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        if keys[pygame.K_SPACE]:
            waiting_to_start = False

    elif not game_over:
        if keys[pygame.K_SPACE] and jump_count < max_jumps:
            player_y_velocity = -15
            jump_count += 1

        player_y += player_y_velocity
        player_y_velocity += gravity

        if player_y >= SCREEN_HEIGHT - 60:
            player_y = SCREEN_HEIGHT - 60
            player_y_velocity = 0
            jump_count = 0

        for cloud in clouds:
            cloud['x'] -= cloud_speed
            if cloud['x'] < -60:
                cloud['x'] = SCREEN_WIDTH + 100
            draw_cloud(cloud['x'], cloud['y'])

        for tree in trees:
            tree['x'] -= tree_speed
        if trees[0]['x'] < -60:
            trees.pop(0)
            trees.append({'x': trees[-1]['x'] + 60})
        draw_trees()

        pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))

        obstacle.x -= 4
        if obstacle.right < 0:
            obstacle.left = SCREEN_WIDTH + random.randint(200, 400)
            passed = False

        if not passed and obstacle.right < player_x:
            score += 1
            passed = True

        player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
        if obstacle.colliderect(player_rect):
            game_over = True

        draw_character(player_x, player_y, jump_count > 0)
        pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)
        screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))

    else:
        msg = font.render("GAME OVER – Qayta boshlash uchun R bosing", True, BLACK)
        screen.blit(msg, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
        if keys[pygame.K_r]:
            game_over = False
            reset_game()

    pygame.display.update()
    clock.tick(FPS)

