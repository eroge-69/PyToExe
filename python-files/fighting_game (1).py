
import pygame
import random

# تهيئة Pygame
pygame.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("لعبة القتال البسيطة")

# الألوان
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# إعدادات اللاعبين
player_size = 50
player1 = pygame.Rect(100, HEIGHT - player_size - 50, player_size, player_size)
player2 = pygame.Rect(650, HEIGHT - player_size - 50, player_size, player_size)

# السرعة
speed = 5

# الطاقة
health1, health2 = 100, 100

# الخط
font = pygame.font.SysFont("Arial", 24)

# اللعبة الرئيسية
running = True
while running:
    screen.fill(WHITE)

    # الأحداث
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # مفاتيح اللاعب 1 (WASD + Space)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player1.x > 0:
        player1.x -= speed
    if keys[pygame.K_d] and player1.x < WIDTH - player_size:
        player1.x += speed
    if keys[pygame.K_w] and player1.y > 0:
        player1.y -= speed
    if keys[pygame.K_s] and player1.y < HEIGHT - player_size:
        player1.y += speed
    if keys[pygame.K_SPACE] and player1.colliderect(player2):
        health2 -= 1

    # مفاتيح اللاعب 2 (Arrow Keys + Enter)
    if keys[pygame.K_LEFT] and player2.x > 0:
        player2.x -= speed
    if keys[pygame.K_RIGHT] and player2.x < WIDTH - player_size:
        player2.x += speed
    if keys[pygame.K_UP] and player2.y > 0:
        player2.y -= speed
    if keys[pygame.K_DOWN] and player2.y < HEIGHT - player_size:
        player2.y += speed
    if keys[pygame.K_RETURN] and player2.colliderect(player1):
        health1 -= 1

    # رسم اللاعبين
    pygame.draw.rect(screen, RED, player1)
    pygame.draw.rect(screen, BLUE, player2)

    # رسم الطاقة
    text1 = font.render(f"Player 1 Health: {health1}", True, RED)
    text2 = font.render(f"Player 2 Health: {health2}", True, BLUE)
    screen.blit(text1, (20, 20))
    screen.blit(text2, (500, 20))

    # تحديث الشاشة
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
