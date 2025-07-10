import pygame
import sys
import random

# --- Настройки ---
WIDTH, HEIGHT = 960, 640
FPS = 60

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CyberClash - Full")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28)
small_font = pygame.font.SysFont("consolas", 20)

# --- Цвета ---
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 80, 80)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 100)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# --- Глобальные переменные ---
game_state = "menu"
selected_brawler = 0

# --- Кнопка ---
def draw_button(text, rect, hover=False):
    color = GRAY if hover else WHITE
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    txt = font.render(text, True, BLACK)
    screen.blit(txt, (rect.x + 20, rect.y + 10))

# --- Список бойцов ---
brawlers = [{"name": f"Brawler {i+1}", "color": (random.randint(100,255), random.randint(100,255), random.randint(100,255))} for i in range(40)]

# --- Игровая функция ---
def start_game(brawler_index):
    # Импортируется внутрь функции, чтобы изоляция была
    import math
    player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    player_speed = 4
    player_hp = 100
    max_hp = 100
    ammo = 3
    max_ammo = 3
    reload_cooldown = 60
    reload_timer = 0

    bullets = []
    bullet_speed = 12
    enemy_count = 5
    enemies = []
    healing_zones = [pygame.Rect(200, 150, 80, 80), pygame.Rect(700, 450, 80, 80)]

    for _ in range(enemy_count):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        enemy = {"pos": pygame.Vector2(x, y), "hp": 60, "state": "chase", "cooldown": 0}
        enemies.append(enemy)

    def draw_health_bar(x, y, hp, max_hp, w=40, h=5):
        ratio = hp / max_hp
        pygame.draw.rect(screen, RED, (x, y, w, h))
        pygame.draw.rect(screen, GREEN, (x, y, w * ratio, h))

    running = True
    while running:
        screen.fill((30, 30, 30))
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and ammo > 0:
                mx, my = pygame.mouse.get_pos()
                direction = pygame.Vector2(mx, my) - player_pos
                direction = direction.normalize()
                bullets.append({"pos": player_pos.copy(), "dir": direction})
                ammo -= 1

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0:
            move = move.normalize()
            player_pos += move * player_speed

        if ammo < max_ammo:
            reload_timer += 1
            if reload_timer >= reload_cooldown:
                ammo += 1
                reload_timer = 0

        for zone in healing_zones:
            pygame.draw.rect(screen, (100, 200, 100), zone)
            if zone.collidepoint(player_pos):
                player_hp = min(player_hp + 0.2, max_hp)

        for bullet in bullets[:]:
            bullet["pos"] += bullet["dir"] * bullet_speed
            if not (0 <= bullet["pos"].x <= WIDTH and 0 <= bullet["pos"].y <= HEIGHT):
                bullets.remove(bullet)

        for bullet in bullets:
            pygame.draw.circle(screen, YELLOW, (int(bullet["pos"].x), int(bullet["pos"].y)), 5)

        for enemy in enemies:
            direction = player_pos - enemy["pos"]
            dist = direction.length()
            if enemy["hp"] < 20:
                enemy["state"] = "flee"
            elif dist < 300:
                enemy["state"] = "chase"
            else:
                enemy["state"] = "idle"

            if enemy["state"] == "chase" and dist > 40:
                enemy["pos"] += direction.normalize() * 2
            elif enemy["state"] == "flee":
                enemy["pos"] -= direction.normalize() * 3

            for bullet in bullets:
                if enemy["pos"].distance_to(bullet["pos"]) < 20:
                    enemy["hp"] -= 25
                    bullets.remove(bullet)
                    break

            for zone in healing_zones:
                if zone.collidepoint(enemy["pos"]):
                    enemy["hp"] = min(enemy["hp"] + 0.2, 60)

            pygame.draw.circle(screen, RED, (int(enemy["pos"].x), int(enemy["pos"].y)), 20)
            draw_health_bar(enemy["pos"].x - 20, enemy["pos"].y - 30, enemy["hp"], 60)

        pygame.draw.circle(screen, brawlers[brawler_index]["color"], (int(player_pos.x), int(player_pos.y)), 20)
        draw_health_bar(player_pos.x - 20, player_pos.y - 30, player_hp, max_hp)

        for i in range(max_ammo):
            color = YELLOW if i < ammo else GRAY
            pygame.draw.rect(screen, color, (10 + i * 25, HEIGHT - 30, 20, 20))

        pygame.display.flip()

# --- Главный цикл ---
while True:
    screen.fill((20, 20, 20))
    mx, my = pygame.mouse.get_pos()

    if game_state == "menu":
        title = font.render("CyberClash", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        play_btn = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
        select_btn = pygame.Rect(WIDTH//2 - 100, 320, 200, 50)
        exit_btn = pygame.Rect(WIDTH//2 - 100, 390, 200, 50)

        draw_button("Играть", play_btn, play_btn.collidepoint(mx, my))
        draw_button("Выбор бойца", select_btn, select_btn.collidepoint(mx, my))
        draw_button("Выход", exit_btn, exit_btn.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(mx, my):
                    game_state = "game"
                    start_game(selected_brawler)
                    game_state = "menu"
                elif select_btn.collidepoint(mx, my):
                    game_state = "select"
                elif exit_btn.collidepoint(mx, my):
                    pygame.quit(); sys.exit()

    elif game_state == "select":
        screen.fill((10, 10, 10))
        txt = font.render("Выберите бойца", True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 30))

        for i, b in enumerate(brawlers):
            x = 50 + (i % 10) * 90
            y = 100 + (i // 10) * 90
            rect = pygame.Rect(x, y, 80, 80)
            pygame.draw.rect(screen, b["color"], rect)
            if rect.collidepoint(mx, my):
                pygame.draw.rect(screen, YELLOW, rect, 4)
            label = small_font.render(str(i+1), True, BLACK)
            screen.blit(label, (x + 25, y + 30))

        back_btn = pygame.Rect(20, 20, 100, 40)
        draw_button("Назад", back_btn, back_btn.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mx, my):
                    game_state = "menu"
                for i in range(len(brawlers)):
                    x = 50 + (i % 10) * 90
                    y = 100 + (i // 10) * 90
                    if pygame.Rect(x, y, 80, 80).collidepoint(mx, my):
                        selected_brawler = i
                        game_state = "menu"

    pygame.display.flip()
    clock.tick(FPS)
pyinstaller --onefile --icon=cyberclash.ico cyberclash_full.py
