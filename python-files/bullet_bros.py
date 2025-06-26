import pygame
import math
import sys
import os
import random

pygame.mixer.init()

pygame.mixer.music.load("music.ogg")  # or .mp3
pygame.mixer.music.set_volume(0.3)    # 0.0 to 1.0
pygame.mixer.music.play(-1)           # Loop forever

sfx_shoot = pygame.mixer.Sound("shoot.wav")
sfx_hit = pygame.mixer.Sound("hit.wav")
sfx_enemy_die = pygame.mixer.Sound("enemy_die.wav")
def show_title_screen(screen, WIDTH, HEIGHT):
    font_big = pygame.font.SysFont(None, 96)
    font_small = pygame.font.SysFont(None, 48)
    screen.fill((30, 30, 30))
    title = font_big.render("Bullet Bros", True, (255, 220, 80))
    prompt = font_small.render("Press any key or button to start", True, (200, 200, 200))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
    screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                waiting = False


def randomize_enemies(tilemap):
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == 4:
                tilemap[y][x] = random.choice([3, 6, 7])

def load_levels(filename):
    levels = []
    with open(filename) as f:
        level = []
        for line in f:
            line = line.strip()
            if not line or line == '---':
                if level:
                    levels.append(level)
                    level = []
            else:
                # Accept space or comma separated
                row = [int(x) for x in line.replace(',', ' ').split()]
                level.append(row)
        if level:
            levels.append(level)
    return levels

# --- Settings ---
TILE_SIZE = 75
PLAYER_SPEED = 4
BULLET_SPEED = 12
SHOOT_COOLDOWN = 150  # ms

# --- Tilemap: 0 = floor, 1 = wall, 2 = player spawn, 3 = enemy ---
levels = load_levels("tilemaps.txt")
current_level = 0
tilemap = levels[current_level]
randomize_enemies(tilemap)



ROWS = len(tilemap)
COLS = len(tilemap[0])
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
show_title_screen(screen, WIDTH, HEIGHT)
# --- Load textures ---
def load_texture(name, scale=1.0):
    path = os.path.join(os.path.dirname(__file__), name)
    img = pygame.image.load(path).convert_alpha()
    if scale != 1.0:
        img = pygame.transform.smoothscale(img, (int(TILE_SIZE * scale), int(TILE_SIZE * scale)))
    else:
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    return img

ground_img = load_texture("ground.png")
wall_img = load_texture("wall.png")
player1_img = load_texture("player1.png", 0.75)
player2_img = load_texture("player2.png", 0.75)
enemy_imgs = {
    4: load_texture("enemy1.png", 0.75),
    6: load_texture("enemy2.png", 0.75),
    7: load_texture("enemy3.png", 0.75),
}
bullet1_img = load_texture("bullet1.png", 1)
bullet2_img = load_texture("bullet2.png", 1)
gundot_img = load_texture("gundot.png", 1)  # 85% of tile size, adjust as needed

#Names the window:
pygame.display.set_caption("Bullet Bros")


# --- Gamepad setup ---
pygame.joystick.init()
gamepad = None
for i in range(pygame.joystick.get_count()):
    js = pygame.joystick.Joystick(i)
    js.init()
    name = js.get_name().lower()
    print(f"Detected joystick {i}: {name}")
    # Skip if it's the RB3 Keyboard or similar
    if "keyboard" in name or "harmonix" in name:
        continue
    gamepad = js
    print("Controller selected:", name)
    break
if not gamepad:
    print("No suitable controller detected!")

def apply_deadzone(value, deadzone=0.2):
    return value if abs(value) > deadzone else 0

# --- Find player spawn and enemies ---
class Enemy:
    def __init__(self, rect, etype):
        self.rect = rect
        self.etype = etype
        # For DVD bouncer, random diagonal direction
        if etype == 7:
            angle = random.choice([math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4])
            self.dx = math.cos(angle)
            self.dy = math.sin(angle)

enemies = []
for y, row in enumerate(tilemap):
    for x, tile in enumerate(row):
        if tile == 2:
            p1_pos = [x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2]
        elif tile == 5:
            p2_pos = [x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2]
        elif tile in (3, 6, 7):
            rect = pygame.Rect(x * TILE_SIZE + 8, y * TILE_SIZE + 8, TILE_SIZE-16, TILE_SIZE-16)
            enemies.append(Enemy(rect, tile))

bullets = []
last_shot = 0
shoot_angle = 0

def get_tile_rect(x, y):
    return pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

def collide_walls(rect):
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == 1:
                if rect.colliderect(get_tile_rect(x, y)):
                    return True
    return False



levels = load_levels("tilemaps.txt")
current_level = 0
tilemap = levels[current_level]

# --- Player state ---
p1_pos = [0, 0]
p2_pos = [0, 0]
p1_bullets = []
p2_bullets = []
p1_killed = 0
p2_killed = 0
p1_totalkills = 0
p2_totalkills = 0

def reset_level():
    global p1_pos, p2_pos, enemies, p1_bullets, p2_bullets, p1_killed, p2_killed, p1_spawn, p2_spawn
    enemies = []
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            if tile == 2:
                p1_pos = [x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2]
                p1_spawn = list(p1_pos)
            elif tile == 5:
                p2_pos = [x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2]
                p2_spawn = list(p2_pos)
            elif tile in (3, 6, 7):
                rect = pygame.Rect(x * TILE_SIZE + 8, y * TILE_SIZE + 8, TILE_SIZE-16, TILE_SIZE-16)
                enemies.append(Enemy(rect, tile))  # <-- always use Enemy!
    p1_bullets = []
    p2_bullets = []
    p1_killed = 0
    p2_killed = 0

reset_level()

running = True
last_shot_p1 = 0
last_shot_p2 = 0
shoot_angle_p1 = 0
shoot_angle_p2 = 0

while running:
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()
    mx, my = pygame.mouse.get_pos()

    # --- Player 1 (Keyboard+Mouse) movement ---
    dx1 = dy1 = 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy1 -= PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy1 += PLAYER_SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx1 -= PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx1 += PLAYER_SPEED

    # Try to move Player 1
    px1, py1 = p1_pos
    new_rect = pygame.Rect(px1 + dx1 - 16, py1 - 16, 32, 32)
    if not collide_walls(new_rect):
        px1 += dx1
    new_rect = pygame.Rect(px1 - 16, py1 + dy1 - 16, 32, 32)
    if not collide_walls(new_rect):
        py1 += dy1
    p1_pos = [px1, py1]

    # --- Player 2 (Controller) movement ---
    dx2 = dy2 = 0
    if gamepad:
        pygame.event.pump()
        axis_left_x = apply_deadzone(gamepad.get_axis(0))
        axis_left_y = apply_deadzone(gamepad.get_axis(1))
        dx2 += int(axis_left_x * PLAYER_SPEED)
        dy2 += int(axis_left_y * PLAYER_SPEED)
    px2, py2 = p2_pos
    new_rect = pygame.Rect(px2 + dx2 - 16, py2 - 16, 32, 32)
    if not collide_walls(new_rect):
        px2 += dx2
    new_rect = pygame.Rect(px2 - 16, py2 + dy2 - 16, 32, 32)
    if not collide_walls(new_rect):
        py2 += dy2
    p2_pos = [px2, py2]

    # --- Player 1 Aim ---
    shoot_angle_p1 = math.atan2(my - py1, mx - px1)

    # --- Player 2 Aim ---
    if gamepad:
        axis_right_x = axis_right_y = 0
        num_axes = gamepad.get_numaxes()
        if num_axes > 3:
            axis_right_x = apply_deadzone(gamepad.get_axis(3))
        if num_axes > 4:
            axis_right_y = apply_deadzone(gamepad.get_axis(4))
        # If your right stick is on different axes, adjust the indices above!
        if abs(axis_right_x) > 0.2 or abs(axis_right_y) > 0.2:
            shoot_angle_p2 = math.atan2(axis_right_y, axis_right_x)
        # else: keep previous shoot_angle_p2

    # --- Shooting ---
    mouse_pressed = pygame.mouse.get_pressed()[0]
    space_pressed = keys[pygame.K_SPACE]
    now = pygame.time.get_ticks()
    # Player 1 shoot
    if (mouse_pressed or space_pressed) and now - last_shot_p1 > SHOOT_COOLDOWN:
        bullet_dx = math.cos(shoot_angle_p1) * BULLET_SPEED
        bullet_dy = math.sin(shoot_angle_p1) * BULLET_SPEED
        p1_bullets.append([px1, py1, bullet_dx, bullet_dy])
        last_shot_p1 = now
        sfx_shoot.play()
    # Player 2 shoot
    gamepad_shoot = gamepad and gamepad.get_button(0)
    if gamepad_shoot and now - last_shot_p2 > SHOOT_COOLDOWN:
        bullet_dx = math.cos(shoot_angle_p2) * BULLET_SPEED
        bullet_dy = math.sin(shoot_angle_p2) * BULLET_SPEED
        p2_bullets.append([px2, py2, bullet_dx, bullet_dy])
        last_shot_p2 = now
        sfx_shoot.play()

    # --- Update bullets and check for enemy hits ---
    for bullet in p1_bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        bullet_rect = pygame.Rect(bullet[0]-4, bullet[1]-4, 8, 8)
        if collide_walls(bullet_rect):
            p1_bullets.remove(bullet)
            continue
        for enemy in enemies[:]:
            if bullet_rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                p1_bullets.remove(bullet)
                p1_killed += 1
                p1_totalkills += 1   # <--- Add this line
                sfx_enemy_die.play()
                break

    for bullet in p2_bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        bullet_rect = pygame.Rect(bullet[0]-4, bullet[1]-4, 8, 8)
        if collide_walls(bullet_rect):
            p2_bullets.remove(bullet)
            continue
        for enemy in enemies[:]:
            if bullet_rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                p2_bullets.remove(bullet)
                p2_killed += 1
                p2_totalkills += 1   # <--- Add this line
                sfx_enemy_die.play()
                break

    # --- Enemy AI ---
    ENEMY_SPEED = 2  # You can tweak this

    for enemy in enemies:
        ex, ey = enemy.rect.center

        if enemy.etype == 3:
            # Run away from closest player
            dist_p1 = math.hypot(ex - p1_pos[0], ey - p1_pos[1])
            dist_p2 = math.hypot(ex - p2_pos[0], ey - p2_pos[1])
            tx, ty = (p1_pos if dist_p1 < dist_p2 else p2_pos)
            dx = ex - tx
            dy = ey - ty
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                move_x = int(dx * ENEMY_SPEED)
                move_y = int(dy * ENEMY_SPEED)
                new_rect = enemy.rect.move(move_x, 0)
                if not collide_walls(new_rect):
                    enemy.rect.x += move_x
                new_rect = enemy.rect.move(0, move_y)
                if not collide_walls(new_rect):
                    enemy.rect.y += move_y

        elif enemy.etype == 6:
            # Chase closest player
            dist_p1 = math.hypot(ex - p1_pos[0], ey - p1_pos[1])
            dist_p2 = math.hypot(ex - p2_pos[0], ey - p2_pos[1])
            tx, ty = (p1_pos if dist_p1 < dist_p2 else p2_pos)
            dx = tx - ex
            dy = ty - ey
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
                move_x = int(dx * ENEMY_SPEED)
                move_y = int(dy * ENEMY_SPEED)
                new_rect = enemy.rect.move(move_x, 0)
                if not collide_walls(new_rect):
                    enemy.rect.x += move_x
                new_rect = enemy.rect.move(0, move_y)
                if not collide_walls(new_rect):
                    enemy.rect.y += move_y

        elif enemy.etype == 7:
            # DVD bouncer
            move_x = int(enemy.dx * ENEMY_SPEED)
            move_y = int(enemy.dy * ENEMY_SPEED)
            new_rect_x = enemy.rect.move(move_x, 0)
            new_rect_y = enemy.rect.move(0, move_y)
            bounced = False
            if collide_walls(new_rect_x):
                enemy.dx *= -1
                bounced = True
            else:
                enemy.rect.x += move_x
            if collide_walls(new_rect_y):
                enemy.dy *= -1
                bounced = True
            else:
                enemy.rect.y += move_y
            # If stuck, randomize direction
            if bounced and collide_walls(enemy.rect):
                angle = random.choice([math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4])
                enemy.dx = math.cos(angle)
                enemy.dy = math.sin(angle)

    # --- Level switching ---
    if len(enemies) == 0:
        current_level += 1
        if current_level < len(levels):
            tilemap = levels[current_level]
            randomize_enemies(tilemap)   # <--- Add this line!
            reset_level()
        else:
            print("All levels complete!")
            running = False

    # --- Player-Enemy Collision (subtract score and respawn) ---
    p1_rect = pygame.Rect(px1-16, py1-16, 32, 32)
    p2_rect = pygame.Rect(px2-16, py2-16, 32, 32)
    for enemy in enemies:
        if p1_rect.colliderect(enemy.rect):
            if p1_totalkills > 0:
                p1_totalkills -= 1
            p1_pos = list(p1_spawn)
            sfx_hit.play()
        if p2_rect.colliderect(enemy.rect):
            if p2_totalkills > 0:
                p2_totalkills -= 1
            p2_pos = list(p2_spawn)
            sfx_hit.play()

    # --- Draw ---
    screen.fill((30, 30, 30))
    for y, row in enumerate(tilemap):
        for x, tile in enumerate(row):
            rect = get_tile_rect(x, y)
            if tile == 1:
                screen.blit(wall_img, rect)
            else:
                screen.blit(ground_img, rect)
    # Centered blit for 75% scaled images
    player_img_size = int(TILE_SIZE * 0.75)
    # Player 1
    screen.blit(player1_img, (int(px1) - player_img_size // 2, int(py1) - player_img_size // 2))
    # Player 2
    screen.blit(player2_img, (int(px2) - player_img_size // 2, int(py2) - player_img_size // 2))
    # Enemies
    for enemy in enemies:
        screen.blit(enemy_imgs[enemy.etype], (enemy.rect.centerx - player_img_size // 2, enemy.rect.centery - player_img_size // 2))
    # Player 1 gun dot
    gun1_x = int(px1 + math.cos(shoot_angle_p1) * 24)
    gun1_y = int(py1 + math.sin(shoot_angle_p1) * 24)
    gun1_angle = -math.degrees(shoot_angle_p1)  # Negative for pygame's y-axis
    rotated_gundot1 = pygame.transform.rotate(gundot_img, gun1_angle)
    rect1 = rotated_gundot1.get_rect(center=(gun1_x, gun1_y))
    screen.blit(rotated_gundot1, rect1)
    for bullet in p1_bullets:
        screen.blit(bullet1_img, (int(bullet[0])-TILE_SIZE//4, int(bullet[1])-TILE_SIZE//4))
    # Player 2 gun dot
    gun2_x = int(px2 + math.cos(shoot_angle_p2) * 24)
    gun2_y = int(py2 + math.sin(shoot_angle_p2) * 24)
    gun2_angle = -math.degrees(shoot_angle_p2)
    rotated_gundot2 = pygame.transform.rotate(gundot_img, gun2_angle)
    rect2 = rotated_gundot2.get_rect(center=(gun2_x, gun2_y))
    screen.blit(rotated_gundot2, rect2)
    for bullet in p2_bullets:
        screen.blit(bullet2_img, (int(bullet[0])-TILE_SIZE//4, int(bullet[1])-TILE_SIZE//4))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()

# --- Show winner and scores in a Pygame window ---
pygame.init()
font_big = pygame.font.SysFont(None, 72)
font_small = pygame.font.SysFont(None, 48)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((30, 30, 30))

# Determine winner
if p1_totalkills > p2_totalkills:
    winner_text = "Player 1 Wins!"
    winner_color = (80,180,255)
elif p2_totalkills > p1_totalkills:
    winner_text = "Player 2 Wins!"
    winner_color = (180,80,255)
else:
    winner_text = "It's a tie!"
    winner_color = (200,200,200)

# Render texts
text_winner = font_big.render(winner_text, True, winner_color)
text_p1 = font_small.render(f"Player 1: {p1_totalkills} points", True, (80,180,255))
text_p2 = font_small.render(f"Player 2: {p2_totalkills} points", True, (180,80,255))

# Blit texts
screen.blit(text_winner, text_winner.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
screen.blit(text_p1, text_p1.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
screen.blit(text_p2, text_p2.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))
pygame.display.flip()

# Wait for quit
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            waiting = False
pygame.quit()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

levels = load_levels("tilemaps.txt")