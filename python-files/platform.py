import pygame
import sys

# --- Game Constants ---
WIDTH, HEIGHT = 600, 400
GRAVITY = 0.6
JUMP_POWER = -10
MOVE_SPEED = 4
PLAYER_RADIUS = 18

# --- Game State ---
stage = 1
platforms = []
target = {'x': 0, 'y': 0, 'r': 18}
player = {'x': 0, 'y': 0, 'vx': 0, 'vy': 0, 'onGround': False}
keys = {}

# --- Stage Definitions ---
def setup_stage(stage_num):
    global stage, platforms
    platforms.clear()
    # Reset player
    player['x'] = 60
    player['y'] = 350
    player['vx'] = 0
    player['vy'] = 0
    player['onGround'] = False

    # Define platforms and target for each stage
    if stage_num == 1:
        platforms.extend([
            {'x': 30, 'y': 370, 'w': 540, 'h': 16, 'dx': 0},  # Ground
            {'x': 80, 'y': 280, 'w': 120, 'h': 14, 'dx': 0},
            {'x': 260, 'y': 210, 'w': 100, 'h': 14, 'dx': 0},
            {'x': 410, 'y': 140, 'w': 120, 'h': 14, 'dx': 0}
        ])
        target.update({'x': 520, 'y': 120, 'r': 18})
    elif stage_num == 2:
        platforms.extend([
            {'x': 30, 'y': 370, 'w': 540, 'h': 16, 'dx': 0},  # Ground
            {'x': 100, 'y': 290, 'w': 70, 'h': 12, 'dx': 1.2},
            {'x': 250, 'y': 220, 'w': 60, 'h': 12, 'dx': -1.5},
            {'x': 400, 'y': 160, 'w': 70, 'h': 12, 'dx': 1.8}
        ])
        target.update({'x': 520, 'y': 140, 'r': 18})
    elif stage_num == 3:
        platforms.extend([
            {'x': 30, 'y': 370, 'w': 540, 'h': 16, 'dx': 0},  # Ground
            {'x': 90, 'y': 300, 'w': 40, 'h': 10, 'dx': 2.0},
            {'x': 230, 'y': 230, 'w': 40, 'h': 10, 'dx': -2.4},
            {'x': 370, 'y': 170, 'w': 40, 'h': 10, 'dx': 2.8},
            {'x': 240, 'y': 110, 'w': 60, 'h': 10, 'dx': 0}
        ])
        target.update({'x': 530, 'y': 90, 'r': 18})

setup_stage(stage)

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game - Red Circle")
clock = pygame.time.Clock()

def update():
    global stage
    # --- Move platforms (for moving ones) ---
    for i, plat in enumerate(platforms):
        if stage == 2 and i > 0:
            plat['x'] += plat['dx']
            if plat['x'] < 80 or plat['x'] + plat['w'] > 520:
                plat['dx'] *= -1
        if stage == 3 and i > 0:
            plat['x'] += plat['dx']
            if plat['x'] < 60 or plat['x'] + plat['w'] > 540:
                plat['dx'] *= -1

    # --- Player movement ---
    player['vx'] = 0
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        player['vx'] = -MOVE_SPEED
    if pressed[pygame.K_RIGHT]:
        player['vx'] = MOVE_SPEED

    # Jump
    if pressed[pygame.K_SPACE] and player['onGround']:
        player['vy'] = JUMP_POWER
        player['onGround'] = False

    # Apply gravity
    player['vy'] += GRAVITY
    player['x'] += player['vx']
    player['y'] += player['vy']

    # --- Collision with platforms ---
    player['onGround'] = False
    for plat in platforms:
        # AABB collision
        if (player['x'] + PLAYER_RADIUS > plat['x'] and
            player['x'] - PLAYER_RADIUS < plat['x'] + plat['w'] and
            player['y'] + PLAYER_RADIUS > plat['y'] and
            player['y'] + PLAYER_RADIUS < plat['y'] + plat['h'] and
            player['vy'] >= 0):
            player['y'] = plat['y'] - PLAYER_RADIUS
            player['vy'] = 0
            player['onGround'] = True

    # --- Collision with edges ---
    if player['x'] - PLAYER_RADIUS < 0:
        player['x'] = PLAYER_RADIUS
    if player['x'] + PLAYER_RADIUS > WIDTH:
        player['x'] = WIDTH - PLAYER_RADIUS
    if player['y'] + PLAYER_RADIUS > HEIGHT:
        player['y'] = 350
        player['x'] = 60
        player['vy'] = 0

    # --- Check if player reaches target ---
    dx = player['x'] - target['x']
    dy = player['y'] - target['y']
    if (dx * dx + dy * dy) ** 0.5 < PLAYER_RADIUS + target['r']:
        if stage < 3:
            stage += 1
            setup_stage(stage)
        else:
            print("Congratulations! You completed all stages!")
            stage = 1
            setup_stage(stage)

def draw():
    screen.fill((34, 34, 34))  # Background
    # Draw platforms
    for plat in platforms:
        pygame.draw.rect(screen, (255, 255, 255), (plat['x'], plat['y'], plat['w'], plat['h']))
    # Draw target
    pygame.draw.circle(screen, (0, 255, 0), (int(target['x']), int(target['y'])), target['r'])
    # Draw player
    pygame.draw.circle(screen, (255, 0, 0), (int(player['x']), int(player['y'])), PLAYER_RADIUS)
    # Draw instructions
    font = pygame.font.SysFont(None, 24)
    text = font.render("Arrow keys to move, Space to jump. Reach the green target!", True, (255, 255, 255))
    screen.blit(text, (20, 10))
    pygame.display.flip()

def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        update()
        draw()
        clock.tick(60)

game_loop()