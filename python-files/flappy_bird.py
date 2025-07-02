import sys
import random

try:
    import pygame
except ImportError:
    print("Pygame is not installed. Please install it to run this game.")
    sys.exit(1)


pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 155, 255)
GREEN = (0, 200, 0)

# Game variables
GRAVITY = 0.5
BIRD_JUMP = -8
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_VEL = 3
FPS = 60

# Bird
bird_x = 50
bird_y = HEIGHT // 2
bird_vel = 0
bird_radius = 20

# Pipes
pipes = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1500)

score = 0
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

def draw_bird(y):
    pygame.draw.circle(SCREEN, BLUE, (bird_x, int(y)), bird_radius)

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(SCREEN, GREEN, pipe['top'])
        pygame.draw.rect(SCREEN, GREEN, pipe['bottom'])

def check_collision(bird_y, pipes):
    bird_rect = pygame.Rect(bird_x - bird_radius, int(bird_y) - bird_radius, bird_radius*2, bird_radius*2)
    if bird_y - bird_radius < 0 or bird_y + bird_radius > HEIGHT:
        return True
    for pipe in pipes:
        if bird_rect.colliderect(pipe['top']) or bird_rect.colliderect(pipe['bottom']):
            return True
    return False

def reset_game():
    global bird_y, bird_vel, pipes, score
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipes = []
    score = 0
    pygame.time.set_timer(SPAWNPIPE, 1500)


def main():
    global bird_y, bird_vel, pipes, score
    running = True
    game_active = True
    reset_game()
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird_vel = BIRD_JUMP
                if event.type == SPAWNPIPE:
                    pipe_height = random.randint(50, HEIGHT - PIPE_GAP - 50)
                    top_rect = pygame.Rect(WIDTH, 0, PIPE_WIDTH, pipe_height)
                    bottom_rect = pygame.Rect(WIDTH, pipe_height + PIPE_GAP, PIPE_WIDTH, HEIGHT - pipe_height - PIPE_GAP)
                    pipes.append({'top': top_rect, 'bottom': bottom_rect, 'passed': False})
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        reset_game()
                        game_active = True

        if game_active:
            bird_vel += GRAVITY
            bird_y += bird_vel

            # Move pipes
            for pipe in pipes:
                pipe['top'].x -= PIPE_VEL
                pipe['bottom'].x -= PIPE_VEL

            # Remove off-screen pipes
            pipes = [pipe for pipe in pipes if pipe['top'].x + PIPE_WIDTH > 0]

            # Score
            for pipe in pipes:
                if not pipe['passed'] and pipe['top'].x + PIPE_WIDTH < bird_x:
                    score += 1
                    pipe['passed'] = True

            # Draw everything
            SCREEN.fill(WHITE)
            draw_bird(bird_y)
            draw_pipes(pipes)
            score_text = font.render(f'Score: {score}', True, BLACK)
            SCREEN.blit(score_text, (10, 10))
            pygame.display.flip()

            # Check collision
            if check_collision(bird_y, pipes):
                game_active = False
        else:
            # Game over screen
            SCREEN.fill(WHITE)
            draw_bird(bird_y)
            draw_pipes(pipes)
            score_text = font.render(f'Score: {score}', True, BLACK)
            SCREEN.blit(score_text, (10, 10))
            game_over_text = font.render('Game Over!', True, BLACK)
            restart_text = font.render('Press R to Restart', True, BLACK)
            SCREEN.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 40))
            SCREEN.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 10))
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
