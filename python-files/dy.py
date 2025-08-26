import pygame
import sys
import random
import os

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumping Cube Adventure")

# Cube properties
cube_size = 50
x = WIDTH // 4
y = HEIGHT - cube_size
velocity_y = 0
velocity_x = 0
gravity = 0.8
jump_strength = -15
jumping = False

# Colors
color_normal = (200, 50, 50)
color_jump_flash = (50, 200, 250)
bg_color = (30, 30, 30)
cactus_color = (0, 200, 0)

# Flash timer
jump_flash_duration = 10
jump_flash_timer = 0

# Cactus properties
cactus_width = 30
normal_speed = 5
boosted_speed = 8
cactus_speed = normal_speed
cactus_gap = 300
cacti = []
back_cacti = []

# Game state
game_over = False
font = pygame.font.SysFont(None, 60)
button_font = pygame.font.SysFont(None, 40)

# Speed control
start_time = pygame.time.get_ticks()
speed_boost_active = False

# Score system
score = 0
high_score = 0
scored_cacti = set()

clock = pygame.time.Clock()

def load_high_score():
    global high_score
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try:
                high_score = int(f.read())
            except:
                high_score = 0

def save_high_score():
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

def draw_cube_with_face(pos, size=50, color=(200, 50, 50)):
    x, y = pos
    pygame.draw.rect(screen, color, (x, y, size, size))
    eye_size = size // 6
    eye_offset_x = size // 5
    eye_offset_y = size // 4
    pygame.draw.rect(screen, (255, 255, 255), (x + eye_offset_x, y + eye_offset_y, eye_size, eye_size))
    pygame.draw.rect(screen, (255, 255, 255), (x + size - eye_offset_x - eye_size, y + eye_offset_y, eye_size, eye_size))
    mouth_width = size // 3
    mouth_height = size // 10
    mouth_x = x + (size - mouth_width) // 2
    mouth_y = y + size - eye_offset_y - mouth_height
    pygame.draw.rect(screen, (0, 0, 0), (mouth_x, mouth_y, mouth_width, mouth_height))

def spawn_cactus():
    # Front cacti
    for _ in range(random.randint(1, 3)):
        height = random.randint(40, 120)
        x_pos = WIDTH + random.randint(0, 200)
        y_pos = HEIGHT - height
        cactus_rect = pygame.Rect(x_pos, y_pos, cactus_width, height)
        cactus_id = random.randint(100000, 999999)
        cacti.append({"id": cactus_id, "rect": cactus_rect})

    # Back cacti
    for _ in range(random.randint(1, 2)):
        height = random.randint(40, 120)
        x_pos = -random.randint(100, 300)
        y_pos = HEIGHT - height
        cactus_rect = pygame.Rect(x_pos, y_pos, cactus_width, height)
        cactus_id = random.randint(100000, 999999)
        back_cacti.append({"id": cactus_id, "rect": cactus_rect})

def draw_cacti():
    for cactus in cacti + back_cacti:
        pygame.draw.rect(screen, cactus_color, cactus["rect"])

def check_collision(cube_rect):
    for cactus in cacti + back_cacti:
        if cube_rect.colliderect(cactus["rect"]):
            return True
    return False

def draw_game_over():
    text = font.render("You Died", True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    high_score_text = button_font.render(f"High Score: {high_score}", True, (255, 255, 0))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 3 + 60))
    button_text = button_font.render("Restart", True, (255, 255, 255))
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
    pygame.draw.rect(screen, (100, 100, 100), button_rect)
    screen.blit(button_text, (button_rect.x + 25, button_rect.y + 10))
    return button_rect

def reset_game():
    global x, y, velocity_y, jumping, jump_flash_timer, cacti, back_cacti, game_over
    global cactus_speed, start_time, speed_boost_active, score, scored_cacti
    x = WIDTH // 4
    y = HEIGHT - cube_size
    velocity_y = 0
    jumping = False
    jump_flash_timer = 0
    cacti = []
    back_cacti = []
    game_over = False
    cactus_speed = normal_speed
    start_time = pygame.time.get_ticks()
    speed_boost_active = False
    score = 0
    scored_cacti = set()

load_high_score()
spawn_timer = 0

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        velocity_x = 0
        if keys[pygame.K_LEFT]: velocity_x = -5
        if keys[pygame.K_RIGHT]: velocity_x = 5
        if keys[pygame.K_UP] and not jumping:
            velocity_y = jump_strength
            jumping = True
            jump_flash_timer = jump_flash_duration

        velocity_y += gravity
        y += velocity_y
        x += velocity_x

        if y + cube_size >= HEIGHT:
            y = HEIGHT - cube_size
            velocity_y = 0
            jumping = False

        x = max(0, min(WIDTH - cube_size, x))
        if jump_flash_timer > 0:
            jump_flash_timer -= 1

        # Speed control
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time >= 180000 and not speed_boost_active:
            cactus_speed = boosted_speed
            speed_boost_active = True
        if elapsed_time >= 600000 and speed_boost_active:
            cactus_speed = normal_speed
            speed_boost_active = False
            start_time = pygame.time.get_ticks()

        spawn_timer += 1
        if spawn_timer > cactus_gap:
            spawn_cactus()
            spawn_timer = 0

        # Move and score front cacti
        for cactus in cacti:
            cactus["rect"].x -= cactus_speed
            if jumping and x > cactus["rect"].x + cactus_width and cactus["id"] not in scored_cacti:
                score += 1
                scored_cacti.add(cactus["id"])

        # Move and score back cacti
        for cactus in back_cacti:
            cactus["rect"].x += cactus_speed
            if jumping and x < cactus["rect"].x and cactus["id"] not in scored_cacti:
                score += 1
                scored_cacti.add(cactus["id"])

        # Cleanup
        cacti = [c for c in cacti if c["rect"].x + cactus_width > 0]
        back_cacti = [c for c in back_cacti if c["rect"].x < WIDTH]

        cube_rect = pygame.Rect(x, y, cube_size, cube_size)
        if check_collision(cube_rect):
            game_over = True
            if score > high_score:
                high_score = score
                save_high_score()

    # Drawing
    screen.fill(bg_color)
    if not game_over:
        cube_color = color_jump_flash if jump_flash_timer > 0 else color_normal
        draw_cube_with_face((x, int(y)), size=cube_size, color=cube_color)
        draw_cacti()
        score_text = button_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    else:
        restart_button = draw_game_over()

    pygame.display.flip()
    clock.tick(60)
