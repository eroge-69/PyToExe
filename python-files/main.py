import pygame
import math
import sys
import random

pygame.init()
pygame.mixer.init()

# === 🎵 Музика ===
pygame.mixer.music.load("Duality.mp3")  # Замінити на свій файл
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# === Екран ===
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гра: Обертай і стріляй")
clock = pygame.time.Clock()

# === Кольори ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
BLUE = (0, 200, 255)
GRAY = (150, 150, 150)

# === Шрифт ===
font = pygame.font.SysFont("arial", 30)
large_font = pygame.font.SysFont("arial", 40)

# === Початковий стан гри ===
def reset_game():
    return {
        "player_pos": [WIDTH // 2, HEIGHT // 2],
        "player_hp": 3,
        "bullets": [],
        "enemies": [],
        "explosions": [],
        "score": 0,
        "game_over": False,
        "last_enemy_spawn": pygame.time.get_ticks()
    }

# === Ворог ===
def spawn_enemy(state):
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, WIDTH)
        y = -20
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT + 20
    elif side == "left":
        x = -20
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH + 20
        y = random.randint(0, HEIGHT)

    state["enemies"].append({
        "pos": [x, y],
        "size": 30
    })

# === Поворот гравця ===
def rotate_center(image, angle):
    return pygame.transform.rotate(image, angle)

# === Ігрові змінні ===
state = reset_game()
player_size = (60, 20)
bullet_speed = 10
enemy_speed = 2
enemy_spawn_delay = 2000
restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50)

# === Основний цикл ===
running = True
while running:
    screen.fill(BLACK)
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Стрільба
        if not state["game_over"] and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - state["player_pos"][0], my - state["player_pos"][1]
            angle = math.atan2(dy, dx)
            vx = math.cos(angle) * bullet_speed
            vy = math.sin(angle) * bullet_speed
            state["bullets"].append({"pos": list(state["player_pos"]), "vel": [vx, vy]})

        # Перезапуск гри
        if state["game_over"] and event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.collidepoint(event.pos):
                state = reset_game()

    # === Програш ===
    if state["game_over"]:
        game_over_text = large_font.render("Гру закінчено!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))

        pygame.draw.rect(screen, GRAY, restart_button)
        restart_text = font.render("Перезапустити", True, BLACK)
        screen.blit(restart_text, (restart_button.x + 20, restart_button.y + 10))

        pygame.display.flip()
        continue

    # === Спавн ворогів ===
    if pygame.time.get_ticks() - state["last_enemy_spawn"] > enemy_spawn_delay:
        spawn_enemy(state)
        state["last_enemy_spawn"] = pygame.time.get_ticks()

    # === Поворот гравця ===
    mx, my = pygame.mouse.get_pos()
    dx, dy = mx - state["player_pos"][0], my - state["player_pos"][1]
    angle_degrees = -math.degrees(math.atan2(dy, dx))

    player_surf = pygame.Surface(player_size)
    player_surf.fill(BLUE)
    player_surf.set_colorkey(BLACK)
    rotated_player = rotate_center(player_surf, angle_degrees)
    player_rect = rotated_player.get_rect(center=state["player_pos"])
    screen.blit(rotated_player, player_rect)

    # === Кулі ===
    for bullet in state["bullets"]:
        bullet["pos"][0] += bullet["vel"][0]
        bullet["pos"][1] += bullet["vel"][1]
        pygame.draw.circle(screen, RED, (int(bullet["pos"][0]), int(bullet["pos"][1])), 5)
    state["bullets"] = [
        b for b in state["bullets"]
        if 0 <= b["pos"][0] <= WIDTH and 0 <= b["pos"][1] <= HEIGHT
    ]

    # === Вороги ===
    new_enemies = []
    for enemy in state["enemies"]:
        ex, ey = enemy["pos"]
        dx, dy = state["player_pos"][0] - ex, state["player_pos"][1] - ey
        angle = math.atan2(dy, dx)
        enemy["pos"][0] += math.cos(angle) * enemy_speed
        enemy["pos"][1] += math.sin(angle) * enemy_speed

        enemy_rect = pygame.Rect(enemy["pos"][0] - 15, enemy["pos"][1] - 15, 30, 30)
        hit = False

        for bullet in state["bullets"]:
            if enemy_rect.collidepoint(bullet["pos"][0], bullet["pos"][1]):
                state["bullets"].remove(bullet)
                state["score"] += 1
                # 💥 Додаємо вибух
                state["explosions"].append({
                    "pos": enemy["pos"][:],
                    "time": pygame.time.get_ticks()
                })
                hit = True
                break

        if not hit and enemy_rect.colliderect(player_rect):
            state["player_hp"] -= 1
            if state["player_hp"] <= 0:
                state["game_over"] = True
            hit = True

        if not hit:
            new_enemies.append(enemy)
            pygame.draw.circle(screen, GREEN, (int(enemy["pos"][0]), int(enemy["pos"][1])), enemy["size"] // 2)

    state["enemies"] = new_enemies

    # === 💥 Вибухи ===
    current_time = pygame.time.get_ticks()
    new_explosions = []
    for exp in state["explosions"]:
        elapsed = current_time - exp["time"]
        if elapsed < 300:
            radius = 30 - (elapsed / 10)
            alpha = 255 - int(elapsed / 300 * 255)
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 150, 0, alpha), (30, 30), int(radius))
            screen.blit(surf, (exp["pos"][0] - 30, exp["pos"][1] - 30))
            new_explosions.append(exp)
    state["explosions"] = new_explosions

    # === Текст ===
    score_text = font.render(f"Рахунок: {state['score']}", True, WHITE)
    hp_text = font.render(f"Здоров’я: {state['player_hp']}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(hp_text, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
