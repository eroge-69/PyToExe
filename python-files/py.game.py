import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# بيانات المربع الأحمر
square_size = 50
square_x = 200
square_y = 300
square_speed = 5

# بيانات الدائرة الزرقاء
circle_radius = 25
circle_x = 600
circle_y = 300
circle_speed = 5

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # تحريك المربع الأحمر (WASD)
    if keys[pygame.K_w]:
        square_y -= square_speed
    if keys[pygame.K_s]:
        square_y += square_speed
    if keys[pygame.K_a]:
        square_x -= square_speed
    if keys[pygame.K_d]:
        square_x += square_speed

    # تحريك الدائرة الزرقاء (UHJK)
    if keys[pygame.K_u]:
        circle_y -= circle_speed
    if keys[pygame.K_j]:
        circle_y += circle_speed
    if keys[pygame.K_h]:
        circle_x -= circle_speed
    if keys[pygame.K_k]:
        circle_x += circle_speed

    # منع الخروج عن الشاشة
    square_x = max(0, min(square_x, WIDTH - square_size))
    square_y = max(0, min(square_y, HEIGHT - square_size))

    circle_x = max(circle_radius, min(circle_x, WIDTH - circle_radius))
    circle_y = max(circle_radius, min(circle_y, HEIGHT - circle_radius))

    screen.fill(BLACK)
    pygame.draw.rect(screen, RED, (square_x, square_y, square_size, square_size))
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), circle_radius)

    pygame.display.flip()
    clock.tick(60)
