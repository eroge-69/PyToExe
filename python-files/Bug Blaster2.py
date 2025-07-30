import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug Blaster")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

player_width = 60
player_height = 20
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 7


bullets = []
bullet_speed = 10

bugs = []
bug_spawn_time = 30  
bug_radius = 20
bug_speed = 3
score = 0


running = True
frame_count = 0

while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed

   
    if keys[pygame.K_SPACE]:
        if len(bullets) < 5:  
            bullets.append([player_x + player_width // 2, player_y])

  
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)


    if frame_count % bug_spawn_time == 0:
        bug_x = random.randint(0, WIDTH - bug_radius)
        bugs.append([bug_x, 0])

 
    for bug in bugs[:]:
        bug[1] += bug_speed
        if bug[1] > HEIGHT:
            bugs.remove(bug)

    
    for bullet in bullets[:]:
        for bug in bugs[:]:
            bx, by = bullet
            bug_x, bug_y = bug
            distance = ((bx - bug_x) ** 2 + (by - bug_y) ** 2) ** 0.5
            if distance < bug_radius:
                bullets.remove(bullet)
                bugs.remove(bug)
                score += 1
                break

  
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))


    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, bullet, 5)


    for bug in bugs:
        pygame.draw.circle(screen, RED, bug, bug_radius)


    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
    frame_count += 1

pygame.quit()
