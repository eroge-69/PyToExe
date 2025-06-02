import pygame
import math
import random

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Bullet Rampage")

clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Fonts
title_font = pygame.font.SysFont("arialblack", 72)
prompt_font = pygame.font.SysFont("arial", 36)
font = pygame.font.SysFont(None, 30)

# Game variables
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_health = 50
max_health = 50
money = 0
score = 0

bullet_speed = 10
fire_cooldown = 500
last_fire_time = 0

enemies = []
enemy_speed = 1.5

bullets = []
bullet_radius = 5

wave_num = 1
wave_active = False
in_shop = False
in_cover = True
game_is_over = False

wave_enemy_count = 1

fire_rate_upgrade = 0
health_regen_upgrade = 0

# ESC pop-up variables
show_exit_popup = False

# Leaderboard variables
leaderboard_file = "leaderboard.txt"
leaderboard = []  # list of tuples (name, score)
entering_name = False
player_name = ""
max_name_length = 10

def load_leaderboard():
    global leaderboard
    leaderboard = []
    try:
        with open(leaderboard_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 2:
                        name, sc = parts
                        try:
                            sc = int(sc)
                            leaderboard.append((name, sc))
                        except:
                            pass
        leaderboard.sort(key=lambda x: x[1], reverse=True)
    except FileNotFoundError:
        pass

def save_leaderboard():
    global leaderboard
    with open(leaderboard_file, "w") as f:
        for name, sc in leaderboard[:10]:
            f.write(f"{name},{sc}\n")

def add_score_to_leaderboard(name, sc):
    global leaderboard
    leaderboard.append((name, sc))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    if len(leaderboard) > 10:
        leaderboard = leaderboard[:10]
    save_leaderboard()

def draw_leaderboard():
    # Draw leaderboard box on left side on cover screen
    box_width = 300
    box_height = HEIGHT - 100
    box_x = 20
    box_y = 50
    pygame.draw.rect(screen, GRAY, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 3)

    # Title
    title_surface = prompt_font.render("Leaderboard - Top 10", True, YELLOW)
    screen.blit(title_surface, (box_x + 20, box_y + 10))

    # Entries
    start_y = box_y + 50
    line_height = 30
    for i, (name, sc) in enumerate(leaderboard):
        text = f"{i+1}. {name}: {sc}"
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, (box_x + 20, start_y + i * line_height))

def draw_name_entry():
    # Draw prompt to enter name after game over
    screen.fill(BLACK)
    prompt = "Enter your name (max 10 chars):"
    draw_centered_text(prompt, (WIDTH // 2, HEIGHT // 2 - 40), YELLOW, prompt_font)
    # Draw the current name input
    name_surface = title_font.render(player_name, True, WHITE)
    name_rect = name_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(name_surface, name_rect)
    pygame.display.flip()

def draw_text(text, pos, color=YELLOW):
    surface = font.render(text, True, color)
    screen.blit(surface, pos)

def draw_centered_text(text, center_pos, color=YELLOW, font_obj=None):
    if font_obj is None:
        font_obj = font
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=center_pos)
    screen.blit(surface, rect)

def draw_player(pos, angle):
    pygame.draw.circle(screen, YELLOW, (int(pos[0]), int(pos[1])), 20)
    gun_length = 30
    end_x = pos[0] + math.cos(angle) * gun_length
    end_y = pos[1] + math.sin(angle) * gun_length
    pygame.draw.line(screen, YELLOW, pos, (end_x, end_y), 5)

def draw_bullet(bullet):
    pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), bullet_radius)

def draw_enemy(enemy):
    pygame.draw.circle(screen, RED, (int(enemy[0]), int(enemy[1])), 20)

def move_enemy(enemy, player_pos):
    dx = player_pos[0] - enemy[0]
    dy = player_pos[1] - enemy[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    dx, dy = dx / dist, dy / dist
    enemy[0] += dx * enemy_speed
    enemy[1] += dy * enemy_speed

def spawn_enemies(num):
    for _ in range(num):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -30
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + 30
        elif side == 'left':
            x = -30
            y = random.randint(0, HEIGHT)
        else:  # right
            x = WIDTH + 30
            y = random.randint(0, HEIGHT)
        enemies.append([x, y])

def draw_cover():
    screen.fill(BLACK)
    title_surface = title_font.render("Bullet Rampage", True, YELLOW)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(title_surface, title_rect)

    prompt_surface = prompt_font.render("Press any key to start", True, YELLOW)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(prompt_surface, prompt_rect)

    # Draw leaderboard on cover screen
    draw_leaderboard()

    pygame.display.flip()

def show_shop():
    screen.fill(BLACK)
    center_x = WIDTH // 2

    lines = [
        f"Money: ${money}",
        "SHOP (Press the red X to close the game)",
        "",
        "Click 1 - Increased Fire Rate (+10 ms faster) - $20",
        "Click 2 - Health Upgrade (+1 health) - $25",
        "",
        "Press SPACE to continue"
    ]

    start_y = HEIGHT // 2 - (len(lines) * 30) // 2
    for i, line in enumerate(lines):
        y = start_y + i * 40
        draw_centered_text(line, (center_x, y), YELLOW, font)

    pygame.display.flip()

def game_over_screen():
    screen.fill(BLACK)
    over_text = title_font.render("GAME OVER", True, RED)
    over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(over_text, over_rect)

    score_text = prompt_font.render(f"Score: {score}", True, YELLOW)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    screen.blit(score_text, score_rect)

    retry_text = prompt_font.render("Press R to retry or Q to quit", True, YELLOW)
    retry_rect = retry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
    screen.blit(retry_text, retry_rect)
    pygame.display.flip()

def reset_game():
    global player_health, money, score, wave_num, bullets, enemies, wave_enemy_count, enemy_speed, fire_cooldown, max_health
    player_health = max_health
    money = 0
    score = 0
    wave_num = 1
    bullets.clear()
    enemies.clear()
    wave_enemy_count = 1
    enemy_speed = 1.5
    fire_cooldown = 500
    max_health = 50

def start_wave():
    global wave_active, wave_enemy_count
    wave_active = True
    if wave_enemy_count <= 1:
        wave_enemy_count = 1
    else:
        wave_enemy_count = min(200, int(wave_enemy_count * 1.1))
    spawn_enemies(wave_enemy_count)

def draw_exit_popup():
    # Darken background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    popup_width = 400
    popup_height = 200
    popup_rect = pygame.Rect((WIDTH - popup_width) // 2, (HEIGHT - popup_height) // 2, popup_width, popup_height)
    pygame.draw.rect(screen, GRAY, popup_rect)
    pygame.draw.rect(screen, WHITE, popup_rect, 3)

    # Text
    draw_centered_text("Are you sure?", (popup_rect.centerx, popup_rect.top + 50), WHITE, title_font)
    # Buttons
    button_width = 120
    button_height = 50
    spacing = 40

    yes_rect = pygame.Rect(
        popup_rect.centerx - button_width - spacing // 2,
        popup_rect.bottom - 80,
        button_width,
        button_height
    )
    no_rect = pygame.Rect(
        popup_rect.centerx + spacing // 2,
        popup_rect.bottom - 80,
        button_width,
        button_height
    )

    pygame.draw.rect(screen, DARK_RED, yes_rect)
    pygame.draw.rect(screen, WHITE, no_rect)

    draw_centered_text("YES", yes_rect.center, WHITE, font)
    draw_centered_text("NO", no_rect.center, BLACK, font)

    # Draw X button top right
    x_button_rect_popup = pygame.Rect(popup_rect.right - 35, popup_rect.top + 5, 30, 30)
    pygame.draw.rect(screen, LIGHT_GRAY, x_button_rect_popup)
    pygame.draw.line(screen, RED, (x_button_rect_popup.left + 5, x_button_rect_popup.top + 5), (x_button_rect_popup.right - 5, x_button_rect_popup.bottom - 5), 3)
    pygame.draw.line(screen, RED, (x_button_rect_popup.left + 5, x_button_rect_popup.bottom - 5), (x_button_rect_popup.right - 5, x_button_rect_popup.top + 5), 3)

    return yes_rect, no_rect, x_button_rect_popup

# Red X button rect for main screen
x_button_rect = pygame.Rect(WIDTH - 40, 10, 30, 30)

# Load leaderboard at start
load_leaderboard()

running = True
while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if entering_name:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if player_name.strip() != "":
                        add_score_to_leaderboard(player_name.strip(), score)
                        entering_name = False
                        in_cover = True
                        game_is_over = False
                        player_name = ""
                        reset_game()
                else:
                    if len(player_name) < max_name_length and event.unicode.isprintable():
                        player_name += event.unicode
            elif in_cover:
                # Any key starts game
                in_cover = False
                wave_active = True
                spawn_enemies(wave_enemy_count)
            elif game_is_over:
                if event.key == pygame.K_r:
                    # Restart game
                    reset_game()
                    wave_active = True
                    game_is_over = False
                    spawn_enemies(wave_enemy_count)
                elif event.key == pygame.K_q:
                    running = False
            elif in_shop:
                if event.key == pygame.K_SPACE:
                    in_shop = False
                    wave_active = True
                    spawn_enemies(wave_enemy_count)
                elif event.key == pygame.K_1:
                    if money >= 20:
                        money -= 20
                        if fire_cooldown > 100:
                            fire_cooldown -= 10
                elif event.key == pygame.K_2:
                    if money >= 25:
                        money -= 25
                        max_health += 1
                        player_health = max_health

        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_exit_popup:
                yes_rect, no_rect, x_button_popup = draw_exit_popup()
                if yes_rect.collidepoint(event.pos):
                    running = False
                elif no_rect.collidepoint(event.pos):
                    show_exit_popup = False
                elif x_button_popup.collidepoint(event.pos):
                    show_exit_popup = False
            else:
                if x_button_rect.collidepoint(event.pos):
                    show_exit_popup = True

    if show_exit_popup:
        screen.fill(BLACK)
        draw_exit_popup()
        pygame.display.flip()
        continue

    if entering_name:
        draw_name_entry()
        continue

    if in_cover:
        draw_cover()
        continue

    if in_shop:
        show_shop()
        continue

    if game_is_over:
        game_over_screen()
        continue

    # Game logic when wave active

    # Player movement
    dx = 0
    dy = 0
    if keys[pygame.K_w]:
        dy -= player_speed
    if keys[pygame.K_s]:
        dy += player_speed
    if keys[pygame.K_a]:
        dx -= player_speed
    if keys[pygame.K_d]:
        dx += player_speed

    player_pos[0] += dx
    player_pos[1] += dy

    # Keep player in screen bounds
    player_pos[0] = max(20, min(WIDTH - 20, player_pos[0]))
    player_pos[1] = max(20, min(HEIGHT - 20, player_pos[1]))

    # Player angle to mouse
    angle = math.atan2(my - player_pos[1], mx - player_pos[0])

    # Shooting
    current_time = pygame.time.get_ticks()
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0] and current_time - last_fire_time > fire_cooldown:
        bullets.append([player_pos[0] + math.cos(angle) * 25, player_pos[1] + math.sin(angle) * 25, angle])
        last_fire_time = current_time

    # Update bullets
    for b in bullets[:]:
        b[0] += math.cos(b[2]) * bullet_speed
        b[1] += math.sin(b[2]) * bullet_speed
        if b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
            bullets.remove(b)

    # Update enemies
    for enemy in enemies[:]:
        move_enemy(enemy, player_pos)

        # Check collision with player
        dist = math.hypot(enemy[0] - player_pos[0], enemy[1] - player_pos[1])
        if dist < 40:
            player_health -= 1
            enemies.remove(enemy)
            if player_health <= 0:
                # Game over, ask for name
                if score > 0:
                    entering_name = True
                else:
                    in_cover = True
                game_is_over = True
                wave_active = False
                break

    # Check bullet-enemy collisions
    for b in bullets[:]:
        for enemy in enemies[:]:
            dist = math.hypot(enemy[0] - b[0], enemy[1] - b[1])
            if dist < 20 + bullet_radius:
                bullets.remove(b)
                enemies.remove(enemy)
                money += 1
                score += 10
                break

    # Check wave cleared
    if wave_active and len(enemies) == 0:
        wave_active = False
        wave_num += 1
        wave_enemy_count += 1
        enemy_speed += 0.1
        in_shop = True

    # Draw everything
    screen.fill(BLACK)
    draw_player(player_pos, angle)

    for bullet in bullets:
        draw_bullet(bullet)

    for enemy in enemies:
        draw_enemy(enemy)

    # Draw UI
    # Health bar
    health_bar_width = 200
    health_ratio = player_health / max_health
    pygame.draw.rect(screen, RED, (20, 20, health_bar_width, 25))
    pygame.draw.rect(screen, YELLOW, (20, 20, int(health_bar_width * health_ratio), 25))
    pygame.draw.rect(screen, WHITE, (20, 20, health_bar_width, 25), 2)

    # Score
    draw_text(f"Score: {score}", (20, 60))
    # Money
    draw_text(f"Money: ${money}", (20, 90))
    # Wave number
    draw_text(f"Wave: {wave_num}", (20, 120))

    # Draw red X button on top right
    pygame.draw.rect(screen, DARK_RED, x_button_rect)
    pygame.draw.line(screen, WHITE, (x_button_rect.left + 5, x_button_rect.top + 5), (x_button_rect.right - 5, x_button_rect.bottom - 5), 3)
    pygame.draw.line(screen, WHITE, (x_button_rect.left + 5, x_button_rect.bottom - 5), (x_button_rect.right - 5, x_button_rect.top + 5), 3)

    pygame.display.flip()

pygame.quit()
