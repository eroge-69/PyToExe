
import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 500, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Unikaj przeszkód")

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size - 10
player_speed = 7

obstacle_width = 50
obstacle_height = 50
obstacle_speed = 5
obstacles = []

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_window(score):
    win.fill(WHITE)
    pygame.draw.rect(win, BLUE, (player_x, player_y, player_size, player_size))
    for obs in obstacles:
        pygame.draw.rect(win, RED, obs)
    text = font.render(f"Wynik: {score}", True, BLACK)
    win.blit(text, (10, 10))
    pygame.display.update()

def main():
    global player_x
    run = True
    score = 0
    spawn_timer = 0

    while run:
        clock.tick(60)
        spawn_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed

        if spawn_timer > 30:
            x_pos = random.randint(0, WIDTH - obstacle_width)
            obstacles.append(pygame.Rect(x_pos, 0, obstacle_width, obstacle_height))
            spawn_timer = 0
            score += 1

        for obs in list(obstacles):
            obs.y += obstacle_speed
            if obs.y > HEIGHT:
                obstacles.remove(obs)
            elif obs.colliderect(pygame.Rect(player_x, player_y, player_size, player_size)):
                print("Przegrałeś!")
                run = False

        draw_window(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
