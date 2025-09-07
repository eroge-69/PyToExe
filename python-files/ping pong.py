import pygame

import random 

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player_1 = pygame.Rect((100, 400, 50, 200))

player_2 = pygame.Rect((650, 400, 50, 200))

ball = pygame.Rect((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 50, 50))

ball_speed_x = -1

ball_speed_y = 2

ball_speed_x_variance = 1

ball_speed_y_variance = 1

random_side_x = 0

random_side_y = 0

clock = pygame.time.Clock()

Timer = 100

run = True

while run:

    screen.fill ((255, 255, 255))

    pygame.draw.rect(screen, (255, 0, 0), player_1)

    pygame.draw.rect(screen, (0, 0, 255), player_2)

    pygame.draw.rect(screen, (0, 255, 0), ball)


    ball_speed_x_variance = random.uniform(1, 1.3)

    ball_speed_y_variance = random.uniform(1, 1.3)

    random_side_x = random.uniform(-1, 1)

    random_side_y = random.uniform(-1, 1)

    clock.tick(60)

    if ball.top < 0:
        ball_speed_y = -ball_speed_y * ball_speed_y_variance

    if ball.bottom > 600:
        ball_speed_y = -ball_speed_y * ball_speed_y_variance


    if ball.colliderect(player_1):
        ball_speed_x = -ball_speed_x * ball_speed_x_variance

        ball.move_ip((10, 0))

    if ball.colliderect(player_2):
        ball_speed_x = -ball_speed_x * ball_speed_x_variance

        ball.move_ip((-10, 0))




    ball.move_ip (ball_speed_x, ball_speed_y)


    key = pygame.key.get_pressed()

    if key[pygame.K_r] or ball.left < 0:
        ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        ball_speed_x = random.choice([-1, 1]) * 2
        ball_speed_y = random.choice([-1, 1]) * 2
  


    if key[pygame.K_r] or ball.right > SCREEN_WIDTH:
        ball.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        ball_speed_x = random.choice([-1, 1]) * 2
        ball_speed_y = random.choice([-1, 1]) * 2

    if key[pygame.K_w] == True:
        player_1.move_ip(0, -3)

    if key[pygame.K_s] == True:
        player_1.move_ip(0, 3)

    if key[pygame.K_UP] == True:
        player_2.move_ip(0, -3)

    if key[pygame.K_DOWN] == True:
        player_2.move_ip(0, 3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()