#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pygame
import random

# Initialize
pygame.init()

# Screen
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
SKY_BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
BROWN = (150, 75, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BUILDING_COLOR = (100, 100, 150)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 36, True)

# Bird
bird_radius = 15
bird_x = 100
bird_y = HEIGHT // 2
bird_movement = 0
gravity = 0.5
jump_strength = -9

# Ground
ground_height = 100

# Pipes
pipe_width = 70
pipe_gap = 160
pipe_color = GREEN
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)
pipe_heights = [200, 250, 300, 350]

# Clouds
cloud = pygame.Surface((60, 30), pygame.SRCALPHA)
pygame.draw.ellipse(cloud, (255, 255, 255, 180), [0, 0, 60, 30])
cloud_x = 0

# Score
score = 0
high_score = 0

# Game State
state = "main_menu"  # "main_menu", "game", "game_over"

# Functions
def draw_bird(x, y):
    # Body
    pygame.draw.circle(screen, YELLOW, (x, y), bird_radius)

    # Eye
    pygame.draw.circle(screen, BLACK, (x + 7, y - 5), 3)

    # Red Beak (choch)
    beak_points = [
        (x + bird_radius, y),
        (x + bird_radius + 8, y - 4),
        (x + bird_radius + 8, y + 4)
    ]
    pygame.draw.polygon(screen, RED, beak_points)

def create_pipes():
    height = random.choice(pipe_heights)
    top = pygame.Rect(WIDTH, 0, pipe_width, height)
    bottom = pygame.Rect(WIDTH, height + pipe_gap, pipe_width, HEIGHT - height - pipe_gap - ground_height)
    return top, bottom

def move_pipes(pipes):
    for pipe in pipes:
        pipe.x -= 5
    return [pipe for pipe in pipes if pipe.right > 0]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, pipe_color, pipe, border_radius=8)

def check_collision(pipes, bird_rect):
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - ground_height:
        return False
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    return True

def display_score(score, high_score):
    text = font.render(f"Score: {int(score)}  High Score: {int(high_score)}", True, BLACK)
    screen.blit(text, (10, 10))

def draw_ground():
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - ground_height, WIDTH, ground_height))

def draw_clouds(x):
    screen.blit(cloud, (x % WIDTH, 50))
    screen.blit(cloud, ((x + 200) % WIDTH, 100))

def draw_buildings(x):
    building_width = 40
    for i in range(0, WIDTH + building_width, building_width):
        height = 100 + (i % 80)
        rect = pygame.Rect((x + i) % WIDTH, HEIGHT - ground_height - height, building_width, height)
        pygame.draw.rect(screen, BUILDING_COLOR, rect)

def reset_game():
    global bird_y, bird_movement, pipe_list, score
    bird_y = HEIGHT // 2
    bird_movement = 0
    pipe_list.clear()
    score = 0

# Main loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(SKY_BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "main_menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state = "game"
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False

        elif state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_movement = jump_strength
            if event.type == SPAWNPIPE:
                pipe_list.extend(create_pipes())

        elif state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "main_menu"

    # Background
    draw_buildings(cloud_x)
    draw_clouds(cloud_x)

    if state == "main_menu":
        draw_ground()

        # Title
        title = big_font.render("Flappy Bird", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))

        # Instructions
        start_text = font.render("Press SPACE to Start", True, BLACK)
        quit_text = font.render("Press Q to Quit", True, BLACK)
        screen.blit(start_text, start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        # Footer
        credit_text = font.render("Flappy Bird by Avyaan", True, BLACK)
        screen.blit(credit_text, credit_text.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    elif state == "game":
        bird_movement += gravity
        bird_y += bird_movement
        bird_rect = pygame.Rect(bird_x - bird_radius, bird_y - bird_radius, bird_radius * 2, bird_radius * 2)

        pipe_list = move_pipes(pipe_list)

        draw_pipes(pipe_list)  # Draw pipes after buildings for proper layer

        for pipe in pipe_list:
            if pipe.right == bird_x:
                score += 0.5

        if score > high_score:
            high_score = score

        if not check_collision(pipe_list, bird_rect):
            state = "game_over"

        draw_bird(bird_x, int(bird_y))
        draw_ground()
        display_score(score, high_score)
        cloud_x -= 1

    elif state == "game_over":
        draw_ground()

        over = big_font.render("Game Over!", True, BLACK)
        screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        restart = font.render("Press SPACE for Main Menu", True, BLACK)
        screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))

        display_score(score, high_score)

    pygame.display.update()

pygame.quit()


# In[ ]:




