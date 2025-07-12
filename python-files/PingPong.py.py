import pygame
import random
import sys

pygame.init()

# Initial resolution
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pong (InfDev)")

# Colors
GREEN = (0, 153, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

# Game variables
ball_pos = [0.5, 0.125]  # Relative: 50% width, 12.5% height
ball_radius_ratio = 0.03  # 3% of the smaller screen dimension
ball_dx = 0.01
ball_dy = 0.01

paddle_width_ratio = 0.2
paddle_height_ratio = 0.04
paddle_y_ratio = 0.9

score = 0
high_score = 0  # New high score variable
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

def get_scaled_rect(width, height, x_ratio, y_ratio, w_ratio, h_ratio):
    return pygame.Rect(
        int(width * x_ratio),
        int(height * y_ratio),
        int(width * w_ratio),
        int(height * h_ratio)
    )

def game_loop():
    global ball_pos, ball_dx, ball_dy, score, high_score, WIDTH, HEIGHT, win

    pygame.time.delay(500)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        win.fill(GREEN)

        mouse_x, _ = pygame.mouse.get_pos()
        paddle_width = WIDTH * paddle_width_ratio
        paddle_height = HEIGHT * paddle_height_ratio
        paddle_x = mouse_x - paddle_width / 2
        paddle_y = HEIGHT * paddle_y_ratio

        # Ball pixel size
        ball_radius = int(min(WIDTH, HEIGHT) * ball_radius_ratio)

        # Move ball
        ball_pos[0] += ball_dx
        ball_pos[1] += ball_dy

        ball_x = int(ball_pos[0] * WIDTH)
        ball_y = int(ball_pos[1] * HEIGHT)

        # Bounce off walls
        if ball_x <= ball_radius or ball_x >= WIDTH - ball_radius:
            ball_dx = -ball_dx
        if ball_y <= ball_radius:
            ball_dy = -ball_dy

        # Collision with paddle
        if (paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height and
            paddle_x <= ball_x <= paddle_x + paddle_width):
            ball_dy = -ball_dy
            ball_dx = random.choice([-0.015, -0.012, -0.01, 0.01, 0.012, 0.015])
            score += 1

        # Missed paddle
        if ball_y > HEIGHT:
            if score > high_score:
                high_score = score
            score = 0
            ball_pos = [0.5, 0.125]
            ball_dx = random.choice([-0.01, 0.01])
            ball_dy = 0.01
            pygame.time.delay(1000)

        # Draw paddle
        pygame.draw.rect(win, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

        # Draw ball
        pygame.draw.circle(win, ORANGE, (ball_x, ball_y), ball_radius)

        # Draw scores
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        win.blit(score_text, (10, 10))
        win.blit(high_score_text, (10, 50))

        pygame.display.update()
        clock.tick(60)

game_loop()
