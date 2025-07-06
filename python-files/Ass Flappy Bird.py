import pygame
import random
import sys
import os
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ass Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PIPE_COLOR = (0, 200, 0)
BIRD_COLOR = (255, 200, 0)
SKY_BLUE = (135, 206, 250)

# Game variables
gravity = 0.5
bird_movement = 0
bird_x = 50
bird_y = HEIGHT // 2
bird_radius = 20

pipe_width = 100  # Increased from 60 to 100
pipe_gap = 150
pipe_speed = 3
pipes = []

score = 0
font = pygame.font.SysFont(None, 40)

# High score handling
HIGHSCORE_FILE = "highscore.txt"
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_highscore(new_high):
    with open(HIGHSCORE_FILE, 'w') as f:
        f.write(str(new_high))

highscore = load_highscore()

clock = pygame.time.Clock()

# Load bird image
BIRD_IMAGE = pygame.image.load(r"C:\Users\USER\Downloads\Flappy Bird\i.png")
BIRD_IMAGE = pygame.transform.scale(BIRD_IMAGE, (bird_radius*2, bird_radius*2))

# Load pipe image
PIPE_IMAGE = pygame.image.load(r"C:\Users\USER\Downloads\Flappy Bird\e.png")
PIPE_IMAGE_DISPLAY = pygame.transform.scale(PIPE_IMAGE, (pipe_width*2, HEIGHT))

# Create masks for pixel-perfect collision
def get_mask(image):
    return pygame.mask.from_surface(image)

BIRD_MASK = get_mask(BIRD_IMAGE)
PIPE_MASK = get_mask(PIPE_IMAGE_DISPLAY)

pipe_id_counter = [0]  # Use a list to allow modification in create_pipe

def create_pipe():
    y = random.randint(100, HEIGHT - 200)
    pipe_id_counter[0] += 1
    return {'x': WIDTH, 'top': y, 'bottom': y + pipe_gap, 'id': pipe_id_counter[0]}

def draw_pipes(pipes):
    for pipe in pipes:
        # Center the pipe image on pipe['x']
        top_rect = PIPE_IMAGE_DISPLAY.get_rect(centerx=pipe['x'], top=pipe['top'] - HEIGHT)
        screen.blit(pygame.transform.flip(PIPE_IMAGE_DISPLAY, False, True), top_rect)
        bottom_rect = PIPE_IMAGE_DISPLAY.get_rect(centerx=pipe['x'], top=pipe['bottom'])
        screen.blit(PIPE_IMAGE_DISPLAY, bottom_rect)

def check_collision(bird_y, pipes):
    bird_rect = pygame.Rect(bird_x - bird_radius, int(bird_y) - bird_radius, bird_radius*2, bird_radius*2)
    for pipe in pipes:
        # Center the pipe image on pipe['x']
        # Top pipe
        top_rect = PIPE_IMAGE_DISPLAY.get_rect(centerx=pipe['x'], top=pipe['top'] - HEIGHT)
        offset_top = (top_rect.left - bird_rect.left, top_rect.top - bird_rect.top)
        # Bottom pipe
        bottom_rect = PIPE_IMAGE_DISPLAY.get_rect(centerx=pipe['x'], top=pipe['bottom'])
        offset_bottom = (bottom_rect.left - bird_rect.left, bottom_rect.top - bird_rect.top)
        # Pixel-perfect collision
        if BIRD_MASK.overlap(PIPE_MASK, offset_top) or BIRD_MASK.overlap(PIPE_MASK, offset_bottom):
            return True
    if bird_y - bird_radius < 0 or bird_y + bird_radius > HEIGHT:
        return True
    return False

def show_score(score, highscore=None):
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (10, 10))
    if highscore is not None:
        htext = font.render(f"High: {highscore}", True, BLACK)
        screen.blit(htext, (10, 40))

def draw_cloud(x, y, scale=1.0):
    # Draw a simple cloud using ellipses
    pygame.draw.ellipse(screen, WHITE, (x, y, 60*scale, 30*scale))
    pygame.draw.ellipse(screen, WHITE, (x+25*scale, y-10*scale, 50*scale, 35*scale))
    pygame.draw.ellipse(screen, WHITE, (x+40*scale, y+5*scale, 40*scale, 25*scale))

def explode_bird(screen, bird_rect, frames=20, particles=50):
    explosion = []
    for _ in range(particles):
        # Each particle: [x, y, dx, dy]
        x = bird_rect.centerx
        y = bird_rect.centery
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(2, 6)
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        explosion.append([x, y, dx, dy])
    for frame in range(frames):
        screen.fill(SKY_BLUE)
        draw_cloud(50, 80, 1.2)
        draw_cloud(200, 50, 0.8)
        draw_cloud(300, 120, 1.0)
        draw_pipes(pipes)
        show_score(score, highscore)
        for p in explosion:
            p[0] += p[2]
            p[1] += p[3]
            pygame.draw.rect(screen, (255, 0, 0), (int(p[0]), int(p[1]), 4, 4))
        pygame.display.flip()
        clock.tick(60)

def main():
    global bird_movement, bird_y, pipes, score, highscore
    # Bird rotation state
    bird_angle = 0
    target_angle = 0
    angle_speed = 4  # degrees per frame for smooth animation
    while True:
        # --- WAIT FOR START ---
        bird_movement = 0
        bird_y = HEIGHT // 2
        pipes = [create_pipe()]
        score = 0
        bird_angle = 0
        target_angle = 0
        waiting = True
        while waiting:
            screen.fill(SKY_BLUE)
            draw_cloud(50, 80, 1.2)
            draw_cloud(200, 50, 0.8)
            draw_cloud(300, 120, 1.0)
            # Draw bird image (no rotation on start screen)
            screen.blit(BIRD_IMAGE, (bird_x-bird_radius, int(bird_y)-bird_radius))
            draw_pipes(pipes)
            show_score(score, highscore)
            msg = font.render("Press SPACE to Start", True, BLACK)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
            reset_msg = font.render("R to reset high score", True, (180, 0, 0))
            screen.blit(reset_msg, (WIDTH // 2 - reset_msg.get_width() // 2, HEIGHT // 2 + 10))
            pygame.display.flip()
            action = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        action = 'start'
                    if event.key == pygame.K_r:
                        highscore = 0
                        save_highscore(0)
            if action == 'start':
                waiting = False
            clock.tick(60)

        # Main game loop
        running = True
        collided = False
        scored_pipes = set()
        while running:
            screen.fill(SKY_BLUE)
            draw_cloud(50, 80, 1.2)
            draw_cloud(200, 50, 0.8)
            draw_cloud(300, 120, 1.0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird_movement = -8
                        target_angle = 0  # Snap back up when flapping

            bird_movement += gravity
            bird_y += bird_movement

            # Bird rotation logic
            if bird_movement > 2:
                target_angle = 90
            else:
                target_angle = 0
            # Smoothly animate angle toward target_angle
            if bird_angle < target_angle:
                bird_angle = min(bird_angle + angle_speed, target_angle)
            elif bird_angle > target_angle:
                bird_angle = max(bird_angle - angle_speed, target_angle)

            for pipe in pipes:
                pipe['x'] -= pipe_speed
            # Score when bird passes the center of a pipe (only once per pipe)
            for pipe in pipes:
                if pipe['id'] not in scored_pipes and pipe['x'] < bird_x:
                    score += 1
                    scored_pipes.add(pipe['id'])
            if pipes[-1]['x'] < WIDTH - 200:
                pipes.append(create_pipe())
            if pipes[0]['x'] < -pipe_width:
                pipes.pop(0)

            # Draw rotated bird image
            rotated_bird = pygame.transform.rotate(BIRD_IMAGE, -bird_angle)  # Negative for clockwise
            bird_rect = rotated_bird.get_rect(center=(bird_x, int(bird_y)))
            screen.blit(rotated_bird, bird_rect.topleft)
            draw_pipes(pipes)
            show_score(score, highscore)

            if check_collision(bird_y, pipes):
                collided = True
                running = False

            pygame.display.flip()
            clock.tick(60)

        # Game over
        if collided:
            if score > highscore:
                highscore = score
                save_highscore(highscore)
            bird_rect = pygame.Rect(bird_x - bird_radius, int(bird_y) - bird_radius, bird_radius*2, bird_radius*2)
            explode_bird(screen, bird_rect)
            # Draw game over text and wait for restart on the same screen
            text = font.render(f"Game Over! Score: {score}", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
            htext = font.render(f"High Score: {highscore}", True, BLACK)
            screen.blit(htext, (WIDTH // 2 - htext.get_width() // 2, HEIGHT // 2 + 30))
            msg = font.render("Press SPACE to Restart", True, BLACK)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 + 70))
            pygame.display.flip()
            waiting_restart = True
            while waiting_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting_restart = False
                clock.tick(60)
        else:
            screen.fill(SKY_BLUE)
            draw_cloud(50, 80, 1.2)
            draw_cloud(200, 50, 0.8)
            draw_cloud(300, 120, 1.0)
            text = font.render(f"Game Over! Score: {score}", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
            htext = font.render(f"High Score: {highscore}", True, BLACK)
            screen.blit(htext, (WIDTH // 2 - htext.get_width() // 2, HEIGHT // 2 + 30))
            msg = font.render("Press SPACE to Restart", True, BLACK)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 + 70))
            pygame.display.flip()
            waiting_restart = True
            while waiting_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting_restart = False
                clock.tick(60)

if __name__ == "__main__":
    main()