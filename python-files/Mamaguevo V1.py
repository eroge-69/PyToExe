import pygame
import random
import math
import sys

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Mamaguevo V1")

WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
STEEL = (70, 130, 180)
GOLD = (255, 215, 0)
DARK_GREEN = (0, 100, 0)
FLAME = (255, 120, 0)
GRAY = (120, 120, 120)

clock = pygame.time.Clock()
FPS = 60

# --- Variables globales ---
weapons = {
    "pistola": {"damage": 1.5, "cooldown": 400, "bullets": 1, "spread": 0.01},
    "escopeta": {"damage": 0.35, "cooldown": 650, "bullets": 7, "spread": 0.28},
    "ametralladora": {"damage": 0.22, "cooldown": 120, "bullets": 1, "spread": 0.07},
    "lanzacohetes": {"damage": 5, "cooldown": 1000, "bullets": 1, "spread": 0, "explosion_radius": 90},
    "lanzallamas": {"damage": 0.09, "cooldown": 30, "bullets": 1, "spread": 0.22, "range": 170}
}

weapon_names = {
    "pistola": "Pistola",
    "escopeta": "Escopeta",
    "ametralladora": "Ametralladora",
    "lanzacohetes": "RPG",
    "lanzallamas": "Lanzallamas"
}

player = pygame.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
player2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 40, 40)
player_speed = 5
lives = 3
max_lives = 3
player_level = 1
player_xp = 0
xp_to_next_level = 100
bullets = []
bullet_speed = 7
bullet_cooldown = 500
last_shot = 0
enemies = []
enemy_bullets = []
enemy_spawn_timer = 0
enemy_spawn_interval = 5000
special_ability_cooldown = 0
special_ability_ready = False
current_weapon = "pistola"
power_ups = []
power_up_spawn_timer = 0
power_up_spawn_interval = 10000
paused = False
wave = 1
enemies_defeated = 0
wave_timer = 0
game_started = False
special_ability_radius = 100
upgrade_points = 0
show_upgrade_menu_flag = False
selected_weapon_for_upgrade = None
explosions = []
two_players = False
pvp_mode = False
pvp_bullets = []
pvp_lives = [5, 5]
pvp_last_shot = [0, 0]
pvp_cooldown = 400

pvp_zone_radius = min(WIDTH, HEIGHT) // 2 - 60
pvp_zone_shrink_speed = 0.25
pvp_zone_center = (WIDTH // 2, HEIGHT // 2)
pvp_zone_min_radius = 80

def button(win, rect, color, text, font, text_color=WHITE):
    pygame.draw.rect(win, color, rect, border_radius=12)
    label = font.render(text, True, text_color)
    win.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

def main_menu():
    global two_players, pvp_mode
    font = pygame.font.SysFont(None, 80)
    font2 = pygame.font.SysFont(None, 50)
    title = font.render("Mamaguevo V1", True, YELLOW)
    btn1 = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 130, 400, 80)
    btn2 = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 20, 400, 80)
    btn3 = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 90, 400, 80)
    while True:
        win.fill(BLACK)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 220))
        button(win, btn1, (60, 180, 60), "2 Jugadores", font2)
        button(win, btn2, (60, 60, 180), "Un Jugador", font2)
        button(win, btn3, (180, 60, 60), "PVP", font2)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if btn1.collidepoint(mx, my):
                    two_players = True
                    pvp_mode = False
                    return
                elif btn2.collidepoint(mx, my):
                    two_players = False
                    pvp_mode = False
                    return
                elif btn3.collidepoint(mx, my):
                    pvp_mode = True
                    return

def get_target_vector(source, target):
    if hasattr(source, 'rect'):
        source = source.rect
    if hasattr(target, 'rect'):
        target = target.rect
    dx = target.centerx - source.centerx
    dy = target.centery - source.centery
    distance = math.hypot(dx, dy)
    if distance == 0:
        return 0, 0
    return dx / distance, dy / distance

def shoot_bullets(source, target, weapon):
    dx, dy = get_target_vector(source, target)
    angle = math.atan2(dy, dx)
    if current_weapon == "lanzacohetes":
        bullet_dx = math.cos(angle)
        bullet_dy = math.sin(angle)
        bullets.append({'rect': pygame.Rect(source.centerx, source.centery, 10, 10), 'dir': (bullet_dx, bullet_dy), 'damage': weapon["damage"], 'type': 'rpg', 'anim': 0})
    elif current_weapon == "lanzallamas":
        for _ in range(weapon["bullets"]):
            spread = random.uniform(-weapon["spread"], weapon["spread"])
            bullet_dx = math.cos(angle + spread)
            bullet_dy = math.sin(angle + spread)
            bullets.append({'rect': pygame.Rect(source.centerx, source.centery, 8, 8), 'dir': (bullet_dx, bullet_dy), 'damage': weapon["damage"], 'type': 'flame', 'range': weapon["range"], 'distance': 0, 'anim': random.randint(0, 10)})
    else:
        for _ in range(weapon["bullets"]):
            spread = random.uniform(-weapon["spread"], weapon["spread"])
            bullet_dx = math.cos(angle + spread)
            bullet_dy = math.sin(angle + spread)
            bullets.append({'rect': pygame.Rect(source.centerx, source.centery, 6, 6), 'dir': (bullet_dx, bullet_dy), 'damage': weapon["damage"], 'type': current_weapon, 'anim': random.randint(0, 10)})

class Enemy:
    def __init__(self, x, y, speed, health, enemy_type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.speed = speed
        self.health = health
        self.type = enemy_type
        self.shoot_cooldown = random.randint(1000, 3000) if enemy_type == 'disparador' else float('inf')
        self.last_shot = pygame.time.get_ticks()
        self.hit_timer = 0
    def update(self, now): pass

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 30, 'boss')
        self.shoot_cooldown = 1000
        self.size = 60
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.phase = 1
        self.phase_timer = 0
    def update(self, now):
        if self.health < 20 and self.phase == 1:
            self.phase = 2
            self.shoot_cooldown = 600
        if self.health < 10 and self.phase == 2:
            self.phase = 3
            self.shoot_cooldown = 300
        if self.phase >= 2 and now - self.phase_timer > 3000:
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                dx, dy = math.cos(rad), math.sin(rad)
                enemy_bullets.append({'rect': pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8), 'dir': (dx, dy)})
            self.phase_timer = now

class Kamikaze(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 3, 1, 'kamikaze')

class Blindado(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 10, 'blindado')

class Invocador(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 3, 'invocador')
        self.summon_cooldown = 5000
        self.last_summon = pygame.time.get_ticks()
    def update(self, now):
        if now - self.last_summon > self.summon_cooldown:
            spawn_enemy_near(self.rect.x, self.rect.y)
            self.last_summon = now

class Disparador(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 1.5, 2, 'disparador')
        self.shoot_cooldown = 1200
        self.last_burst = pygame.time.get_ticks()
        self.burst_count = 0
    def update(self, now):
        dist = math.hypot(player.centerx - self.rect.centerx, player.centery - self.rect.centery)
        if dist < 300:
            if now - self.last_shot > self.shoot_cooldown:
                if self.burst_count < 3:
                    dx, dy = get_target_vector(self.rect, player)
                    enemy_bullets.append({'rect': pygame.Rect(self.rect.centerx, self.rect.centery, 6, 6), 'dir': (dx, dy)})
                    self.last_shot = now
                    self.burst_count += 1
                else:
                    self.burst_count = 0
                    self.last_shot = now + 600

class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.type = power_type

class Explosion:
    def __init__(self, x, y, radius, duration=350):
        self.x = x
        self.y = y
        self.radius = radius
        self.timer = duration
        self.max_timer = duration
    def draw(self, surface):
        alpha = int(255 * (self.timer / self.max_timer))
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 170, 0, alpha), (self.radius, self.radius), int(self.radius * (self.timer / self.max_timer)))
        surface.blit(surf, (self.x - self.radius, self.y - self.radius))

def spawn_power_up():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x, y = random.randint(0, WIDTH), 0
    elif side == 'bottom':
        x, y = random.randint(0, WIDTH), HEIGHT - 30
    elif side == 'left':
        x, y = 0, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH - 30, random.randint(0, HEIGHT)
    power_type = random.choice(['vida', 'daño', 'velocidad'])
    power_ups.append(PowerUp(x, y, power_type))

def spawn_enemy_near(x, y):
    offset_x = random.randint(-40, 40)
    offset_y = random.randint(-40, 40)
    enemies.append(Enemy(x + offset_x, y + offset_y, 2, 1, 'normal'))

def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x, y = random.randint(0, WIDTH), 0
    elif side == 'bottom':
        x, y = random.randint(0, WIDTH), HEIGHT - 30
    elif side == 'left':
        x, y = 0, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH - 30, random.randint(0, HEIGHT)
    enemy_type = random.choice(['normal', 'rapido', 'lento', 'disparador', 'kamikaze', 'blindado', 'invocador'])
    if enemy_type == 'normal':
        enemies.append(Enemy(x, y, 2 + wave * 0.5, 1, 'normal'))
    elif enemy_type == 'rapido':
        enemies.append(Enemy(x, y, 4 + wave * 0.5, 1, 'rapido'))
    elif enemy_type == 'lento':
        enemies.append(Enemy(x, y, 1, 3 + wave, 'lento'))
    elif enemy_type == 'disparador':
        enemies.append(Disparador(x, y))
    elif enemy_type == 'kamikaze':
        enemies.append(Kamikaze(x, y))
    elif enemy_type == 'blindado':
        enemies.append(Blindado(x, y))
    elif enemy_type == 'invocador':
        enemies.append(Invocador(x, y))

def draw_bullet_anim(bullet):
    t = pygame.time.get_ticks()
    if bullet['type'] == 'pistola':
        pygame.draw.ellipse(win, WHITE, bullet['rect'].inflate(4, 0))
        pygame.draw.line(win, YELLOW, bullet['rect'].center, (bullet['rect'].centerx + bullet['dir'][0]*10, bullet['rect'].centery + bullet['dir'][1]*10), 2)
    elif bullet['type'] == 'escopeta':
        color = (255, 220, 120)
        pygame.draw.ellipse(win, color, bullet['rect'].inflate(8, 0))
        for i in range(2):
            pygame.draw.line(win, (255, 200, 0), bullet['rect'].center, (bullet['rect'].centerx + bullet['dir'][0]*random.randint(8, 16), bullet['rect'].centery + bullet['dir'][1]*random.randint(8, 16)), 1)
    elif bullet['type'] == 'ametralladora':
        col = (min(255, 180 + (t//30)%75), 255, 255)
        pygame.draw.rect(win, col, bullet['rect'])
        pygame.draw.line(win, BLUE, bullet['rect'].center, (bullet['rect'].centerx + bullet['dir'][0]*8, bullet['rect'].centery + bullet['dir'][1]*8), 1)
    elif bullet['type'] == 'rpg':
        pygame.draw.rect(win, ORANGE, bullet['rect'])
        pygame.draw.circle(win, RED, bullet['rect'].center, 7, 2)
        tail = (bullet['rect'].centerx - bullet['dir'][0]*14, bullet['rect'].centery - bullet['dir'][1]*14)
        pygame.draw.line(win, YELLOW, bullet['rect'].center, tail, 4)
    elif bullet['type'] == 'flame':
        flame_colors = [(255, 180, 0), (255, 120, 0), (255, 80, 0)]
        pygame.draw.circle(win, random.choice(flame_colors), bullet['rect'].center, random.randint(4, 7))

def show_upgrade_menu():
    global upgrade_points, current_weapon, show_upgrade_menu_flag, weapons, bullet_speed

    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)

    weapon_list = list(weapons.keys())
    buttons = []
    for i, weapon_name in enumerate(weapon_list):
        button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100 + i * 60, 300, 50)
        buttons.append((button_rect, weapon_name))

    back_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 50)

    while show_upgrade_menu_flag:
        win.fill(BLACK)
        upgrade_text = font.render("Selecciona un Arma para Mejorar", True, YELLOW)
        win.blit(upgrade_text, (WIDTH // 2 - upgrade_text.get_width() // 2, HEIGHT // 2 - 180))

        points_text = small_font.render(f"Puntos de mejora: {upgrade_points}", True, WHITE)
        win.blit(points_text, (WIDTH // 2 - points_text.get_width() // 2, HEIGHT // 2 - 120))

        for button_rect, weapon_name in buttons:
            button(win, button_rect, GREEN, weapon_names[weapon_name], small_font)

        button(win, back_button_rect, RED, "Volver", small_font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for button_rect, weapon_name in buttons:
                    if button_rect.collidepoint(mx, my):
                        show_weapon_upgrade_options(weapon_name)
                if back_button_rect.collidepoint(mx, my):
                    show_upgrade_menu_flag = False
                    return

def show_weapon_upgrade_options(weapon_name):
    global upgrade_points, weapons, bullet_speed, show_upgrade_menu_flag

    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)

    upgrade_options = [
        {"name": f"Mejorar Daño ({weapons[weapon_name]['damage']})", "action": "damage"},
        {"name": f"Mejorar Velocidad de disparo ({weapons[weapon_name]['cooldown']})", "action": "cooldown"},
        {"name": f"Mejorar Velocidad de bala ({bullet_speed})", "action": "bullet_speed"},
    ]

    buttons = []
    for i, option in enumerate(upgrade_options):
        button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 60, 300, 50)
        buttons.append((button_rect, option))

    back_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 50)

    while True:
        win.fill(BLACK)
        upgrade_text = font.render(f"Mejorar {weapon_names[weapon_name]}", True, YELLOW)
        win.blit(upgrade_text, (WIDTH // 2 - upgrade_text.get_width() // 2, HEIGHT // 2 - 150))

        points_text = small_font.render(f"Puntos de mejora: {upgrade_points}", True, WHITE)
        win.blit(points_text, (WIDTH // 2 - points_text.get_width() // 2, HEIGHT // 2 - 100))

        for button_rect, option in buttons:
            button(win, button_rect, GREEN, option["name"], small_font)

        button(win, back_button_rect, RED, "Volver", small_font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for button_rect, option in buttons:
                    if button_rect.collidepoint(mx, my):
                        if upgrade_points > 0:
                            if option["action"] == "damage":
                                weapons[weapon_name]["damage"] += 0.5
                            elif option["action"] == "cooldown":
                                weapons[weapon_name]["cooldown"] = max(50, weapons[weapon_name]["cooldown"] - 50)
                            elif option["action"] == "bullet_speed":
                                bullet_speed += 1
                            upgrade_points -= 1
                if back_button_rect.collidepoint(mx, my):
                    return

def pvp_loop():
    global player, player2, pvp_bullets, pvp_lives, pvp_last_shot, pvp_zone_radius
    player = pygame.Rect(WIDTH // 3, HEIGHT // 2, 40, 40)
    player2 = pygame.Rect(WIDTH * 2 // 3, HEIGHT // 2, 40, 40)
    pvp_bullets = []
    pvp_lives = [5, 5]
    pvp_last_shot = [0, 0]
    pvp_zone_radius = min(WIDTH, HEIGHT) // 2 - 60
    running = True
    font = pygame.font.SysFont(None, 48)
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.y -= player_speed
        if keys[pygame.K_s]:
            player.y += player_speed
        if keys[pygame.K_a]:
            player.x -= player_speed
        if keys[pygame.K_d]:
            player.x += player_speed
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if keys[pygame.K_UP]:
            player2.y -= player_speed
        if keys[pygame.K_DOWN]:
            player2.y += player_speed
        if keys[pygame.K_LEFT]:
            player2.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player2.x += player_speed
        player2.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - pvp_last_shot[0] > pvp_cooldown:
            dx, dy = get_target_vector(player, player2)
            rect = pygame.Rect(player.centerx - 4, player.centery - 4, 8, 8)
            pvp_bullets.append({"rect": rect, "dir": (dx, dy), "owner": 0})
            pvp_last_shot[0] = now
        if keys[pygame.K_RETURN] and now - pvp_last_shot[1] > pvp_cooldown:
            dx, dy = get_target_vector(player2, player)
            rect = pygame.Rect(player2.centerx - 4, player2.centery - 4, 8, 8)
            pvp_bullets.append({"rect": rect, "dir": (dx, dy), "owner": 1})
            pvp_last_shot[1] = now

        for bullet in pvp_bullets[:]:
            bullet['rect'].x += bullet['dir'][0] * bullet_speed * 1.2
            bullet['rect'].y += bullet['dir'][1] * bullet_speed * 1.2
            if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(bullet['rect']):
                pvp_bullets.remove(bullet)
                continue
            if bullet['owner'] == 0 and bullet['rect'].colliderect(player2):
                pvp_lives[1] -= 1
                pvp_bullets.remove(bullet)
            elif bullet['owner'] == 1 and bullet['rect'].colliderect(player):
                pvp_lives[0] -= 1
                pvp_bullets.remove(bullet)

        if pvp_zone_radius > pvp_zone_min_radius:
            pvp_zone_radius -= pvp_zone_shrink_speed

        for i, rect in enumerate([player, player2]):
            dist = math.hypot(rect.centerx - pvp_zone_center[0], rect.centery - pvp_zone_center[1])
            if dist > pvp_zone_radius:
                if pygame.time.get_ticks() % 15 == 0:
                    pvp_lives[i] -= 1

        win.fill(BLACK)
        pygame.draw.circle(win, (0, 220, 0), pvp_zone_center, int(pvp_zone_radius), 8)
        pygame.draw.rect(win, GREEN, player)
        pygame.draw.rect(win, BLUE, player2)
        for bullet in pvp_bullets:
            draw_bullet_anim({'type': 'pistola', 'rect': bullet['rect'], 'dir': bullet['dir']})

        l1 = font.render(f"Jugador 1: {pvp_lives[0]}", True, GREEN)
        l2 = font.render(f"Jugador 2: {pvp_lives[1]}", True, BLUE)
        win.blit(l1, (60, 40))
        win.blit(l2, (WIDTH - l2.get_width() - 60, 40))

        if pvp_lives[0] <= 0 or pvp_lives[1] <= 0:
            winner = "Jugador 2" if pvp_lives[0] <= 0 else "Jugador 1"
            msg = font.render(f"{winner} GANA!", True, YELLOW)
            win.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(2000)
            main_menu()
            return

        pygame.display.flip()

def pause_screen():
    win.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    pause_text = font.render("PAUSA", True, WHITE)
    win.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height() // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                waiting = False

def game_over():
    win.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("GAME OVER", True, RED)
    win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    font = pygame.font.SysFont(None, 36)
    stats_text = font.render(f"Enemigos derrotados: {enemies_defeated}", True, WHITE)
    level_text = font.render(f"Nivel alcanzado: {player_level}", True, WHITE)
    restart_text = font.render("Presiona R para reiniciar o Q para salir", True, WHITE)
    win.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 + 20))
    win.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 + 60))
    win.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    reset_game()
                if event.key == pygame.K_q:
                    waiting = False
                    main_menu()
                    return

def reset_game():
    global player, player2, player_speed, lives, player_level, player_xp, xp_to_next_level, bullets, enemies, enemy_bullets, power_ups, enemy_spawn_timer, power_up_spawn_timer, last_shot, special_ability_ready, special_ability_cooldown, wave, enemies_defeated, wave_timer, game_started, max_lives, upgrade_points, show_upgrade_menu_flag, explosions, two_players, pvp_mode
    player = pygame.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
    player2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 40, 40)
    player_speed = 5
    lives = 3
    max_lives = 3
    player_level = 1
    player_xp = 0
    xp_to_next_level = 100
    bullets = []
    enemies = []
    enemy_bullets = []
    power_ups = []
    enemy_spawn_timer = 0
    power_up_spawn_timer = 0
    last_shot = 0
    special_ability_ready = False
    special_ability_cooldown = 0
    wave = 1
    enemies_defeated = 0
    wave_timer = 0
    game_started = False
    upgrade_points = 0
    show_upgrade_menu_flag = False
    explosions = []
    two_players = False
    pvp_mode = False
    game_loop()

def game_loop():
    global player_xp, lives, player_speed, current_weapon, power_up_spawn_timer, enemy_spawn_timer, last_shot, special_ability_ready, special_ability_cooldown, wave_timer, enemies_defeated, paused, game_started, upgrade_points, two_players, pvp_mode, wave, player_level, xp_to_next_level, show_upgrade_menu_flag

    if not game_started:
        main_menu()
        if pvp_mode:
            pvp_loop()
            return
        game_started = True

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_screen()
                if event.key == pygame.K_1:
                    current_weapon = "pistola"
                elif event.key == pygame.K_2:
                    current_weapon = "escopeta"
                elif event.key == pygame.K_3:
                    current_weapon = "ametralladora"
                elif event.key == pygame.K_4:
                    current_weapon = "lanzacohetes"
                elif event.key == pygame.K_5:
                    current_weapon = "lanzallamas"
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if paused:
            continue

        win.fill(BLACK)
        keys = pygame.key.get_pressed()
        move_x = move_y = 0
        if keys[pygame.K_w]:
            player.y -= player_speed
            move_y -= 1
        if keys[pygame.K_s]:
            player.y += player_speed
            move_y += 1
        if keys[pygame.K_a]:
            player.x -= player_speed
            move_x -= 1
        if keys[pygame.K_d]:
            player.x += player_speed
            move_x += 1
        player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if two_players:
            if keys[pygame.K_UP]:
                player2.y -= player_speed
            if keys[pygame.K_DOWN]:
                player2.y += player_speed
            if keys[pygame.K_LEFT]:
                player2.x -= player_speed
            if keys[pygame.K_RIGHT]:
                player2.x += player_speed
            player2.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if keys[pygame.K_SPACE]:
            special_ability_ready = False

        now = pygame.time.get_ticks()
        weapon = weapons[current_weapon]
        can_shoot = now - last_shot > weapon["cooldown"]
        if can_shoot and enemies:
            closest = min(enemies, key=lambda e: math.hypot(player.centerx - e.rect.centerx, player.centery - e.rect.centery))
            shoot_bullets(player, closest, weapon)
            if two_players:
                closest2 = min(enemies, key=lambda e: math.hypot(player2.centerx - e.rect.centerx, player2.centery - e.rect.centery))
                shoot_bullets(player2, closest2, weapon)
            last_shot = now

        for bullet in bullets[:]:
            if bullet.get('type') == 'rpg':
                bullet['rect'].x += bullet['dir'][0] * bullet_speed * 0.9
                bullet['rect'].y += bullet['dir'][1] * bullet_speed * 0.9
                if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(bullet['rect']):
                    bullets.remove(bullet)
                    continue
                hit = False
                for enemy in enemies[:]:
                    if bullet['rect'].colliderect(enemy.rect):
                        explosions.append(Explosion(bullet['rect'].centerx, bullet['rect'].centery, weapons['lanzacohetes']['explosion_radius']))
                        for e in enemies[:]:
                            dist = math.hypot(bullet['rect'].centerx - e.rect.centerx, bullet['rect'].centery - e.rect.centery)
                            if dist < weapons['lanzacohetes']['explosion_radius']:
                                e.health -= weapons['lanzacohetes']['damage']
                                e.hit_timer = 300
                                if e.health <= 0:
                                    if e.type == 'kamikaze':
                                        if math.hypot(player.centerx - e.rect.centerx, player.centery - e.rect.centery) < 60:
                                            lives -= 1
                                    enemies.remove(e)
                                    enemies_defeated += 1
                                    player_xp += 10
                                    if player_xp >= xp_to_next_level:
                                        player_level += 1
                                        player_xp = 0
                                        xp_to_next_level = int(xp_to_next_level * 1.5)
                                        upgrade_points += 1
                                        show_upgrade_menu_flag = True
                        bullets.remove(bullet)
                        hit = True
                        break
                if hit:
                    continue
            elif bullet.get('type') == 'flame':
                bullet['rect'].x += bullet['dir'][0] * 4
                bullet['rect'].y += bullet['dir'][1] * 4
                bullet['distance'] = bullet.get('distance', 0) + 4
                if bullet['distance'] > weapons['lanzallamas']['range']:
                    bullets.remove(bullet)
                    continue
                for enemy in enemies[:]:
                    if bullet['rect'].colliderect(enemy.rect):
                        enemy.health -= bullet['damage']
                        enemy.hit_timer = 100
                        if enemy.health <= 0:
                            if enemy.type == 'kamikaze':
                                if math.hypot(player.centerx - enemy.rect.centerx, player.centery - enemy.rect.centery) < 60:
                                    lives -= 1
                            enemies.remove(enemy)
                            enemies_defeated += 1
                            player_xp += 10
                            if player_xp >= xp_to_next_level:
                                player_level += 1
                                player_xp = 0
                                xp_to_next_level = int(xp_to_next_level * 1.5)
                                upgrade_points += 1
                                show_upgrade_menu_flag = True
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
            else:
                bullet['rect'].x += bullet['dir'][0] * bullet_speed
                bullet['rect'].y += bullet['dir'][1] * bullet_speed
                if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(bullet['rect']):
                    bullets.remove(bullet)

        for enemy in enemies[:]:
            if hasattr(enemy, 'update'):
                enemy.update(now)

        for bullet in enemy_bullets[:]:
            bullet['rect'].x += bullet['dir'][0] * 3
            bullet['rect'].y += bullet['dir'][1] * 3
            if not pygame.Rect(0, 0, WIDTH, HEIGHT).contains(bullet['rect']):
                enemy_bullets.remove(bullet)

        enemy_spawn_timer += dt
        if enemy_spawn_timer > enemy_spawn_interval:
            for _ in range(1 + wave // 2):
                spawn_enemy()
            enemy_spawn_timer = 0

        power_up_spawn_timer += dt
        if power_up_spawn_timer > power_up_spawn_interval:
            spawn_power_up()
            power_up_spawn_timer = 0

        for enemy in enemies:
            dx, dy = get_target_vector(enemy.rect, player)
            enemy.rect.x += dx * enemy.speed
            enemy.rect.y += dy * enemy.speed
            enemy.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        for bullet in bullets[:]:
            if bullet.get('type') in ['rpg', 'flame']:
                continue
            for enemy in enemies[:]:
                if bullet['rect'].colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemy.health -= bullet['damage']
                    enemy.hit_timer = 300
                    if enemy.health <= 0:
                        if enemy.type == 'kamikaze':
                            if math.hypot(player.centerx - enemy.rect.centerx, player.centery - enemy.rect.centery) < 60:
                                lives -= 1
                        enemies.remove(enemy)
                        enemies_defeated += 1
                        player_xp += 10
                        if player_xp >= xp_to_next_level:
                            player_level += 1
                            player_xp = 0
                            xp_to_next_level = int(xp_to_next_level * 1.5)
                            upgrade_points += 1
                            show_upgrade_menu_flag = True
                    break

        for bullet in enemy_bullets[:]:
            if bullet['rect'].colliderect(player):
                enemy_bullets.remove(bullet)
                lives -= 1
                if lives <= 0:
                    game_over()
                    return
            if two_players and bullet['rect'].colliderect(player2):
                enemy_bullets.remove(bullet)
                lives -= 1
                if lives <= 0:
                    game_over()
                    return

        for enemy in enemies[:]:
            if player.colliderect(enemy.rect):
                if enemy.type == 'kamikaze':
                    lives -= 2
                else:
                    lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    game_over()
                    return
            if two_players and player2.colliderect(enemy.rect):
                if enemy.type == 'kamikaze':
                    lives -= 2
                else:
                    lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    game_over()
                    return

        for power_up in power_ups[:]:
            if player.colliderect(power_up.rect) or (two_players and player2.colliderect(power_up.rect)):
                if power_up.type == 'vida':
                    lives = min(lives + 1, max_lives)
                elif power_up.type == 'daño':
                    weapons[current_weapon]["damage"] += 0.5
                elif power_up.type == 'velocidad':
                    player_speed += 1
                power_ups.remove(power_up)

        pygame.draw.rect(win, GREEN, player)
        if two_players:
            pygame.draw.rect(win, BLUE, player2)

        for bullet in bullets:
            draw_bullet_anim(bullet)

        for bullet in enemy_bullets:
            pygame.draw.ellipse(win, YELLOW, bullet['rect'])

        for explosion in explosions[:]:
            explosion.draw(win)
            explosion.timer -= dt
            if explosion.timer <= 0:
                explosions.remove(explosion)

        for enemy in enemies:
            if enemy.hit_timer > 0:
                pygame.draw.rect(win, WHITE, enemy.rect)
                enemy.hit_timer -= dt
            else:
                if enemy.type == 'normal':
                    pygame.draw.rect(win, RED, enemy.rect)
                elif enemy.type == 'rapido':
                    pygame.draw.polygon(win, ORANGE, [
                        (enemy.rect.centerx, enemy.rect.top),
                        (enemy.rect.right, enemy.rect.centery),
                        (enemy.rect.centerx, enemy.rect.bottom),
                        (enemy.rect.left, enemy.rect.centery)
                    ])
                elif enemy.type == 'lento':
                    pygame.draw.ellipse(win, PURPLE, enemy.rect)
                elif enemy.type == 'disparador':
                    pygame.draw.polygon(win, CYAN, [
                        (enemy.rect.centerx, enemy.rect.top),
                        (enemy.rect.right, enemy.rect.bottom),
                        (enemy.rect.left, enemy.rect.bottom)
                    ])
                elif enemy.type == 'kamikaze':
                    pygame.draw.circle(win, PINK, enemy.rect.center, enemy.rect.width // 2)
                    pygame.draw.circle(win, RED, enemy.rect.center, enemy.rect.width // 4, 2)
                elif enemy.type == 'blindado':
                    pygame.draw.rect(win, STEEL, enemy.rect)
                    pygame.draw.rect(win, DARK_GREEN, enemy.rect.inflate(-10, -10))
                elif enemy.type == 'invocador':
                    pygame.draw.ellipse(win, (128, 0, 128), enemy.rect)
                    pygame.draw.circle(win, YELLOW, enemy.rect.center, 8)
                elif enemy.type == 'boss':
                    pygame.draw.ellipse(win, GOLD, enemy.rect)
                    pygame.draw.rect(win, RED, enemy.rect.inflate(-20, -20))

        for power_up in power_ups:
            if power_up.type == 'vida':
                pygame.draw.circle(win, RED, power_up.rect.center, 12)
                pygame.draw.line(win, WHITE, (power_up.rect.centerx, power_up.rect.centery - 6), (power_up.rect.centerx, power_up.rect.centery + 6), 3)
                pygame.draw.line(win, WHITE, (power_up.rect.centerx - 6, power_up.rect.centery), (power_up.rect.centerx + 6, power_up.rect.centery), 3)
            elif power_up.type == 'daño':
                pygame.draw.polygon(win, (255, 0, 0), [
                    (power_up.rect.centerx, power_up.rect.top),
                    (power_up.rect.right, power_up.rect.centery),
                    (power_up.rect.centerx, power_up.rect.bottom),
                    (power_up.rect.left, power_up.rect.centery)
                ])
            elif power_up.type == 'velocidad':
                pygame.draw.ellipse(win, (0, 255, 0), power_up.rect)
                pygame.draw.line(win, WHITE, (power_up.rect.left + 4, power_up.rect.centery),
                                 (power_up.rect.right - 4, power_up.rect.centery), 2)

        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Vidas: {lives}", True, BLUE)
        level_text = font.render(f"Nivel: {player_level}", True, BLUE)
        xp_text = font.render(f"XP: {player_xp}/{xp_to_next_level}", True, BLUE)
        weapon_text = font.render(f"Arma: {current_weapon}", True, BLUE)
        wave_text = font.render(f"Oleada: {wave}", True, BLUE)
        upg_text = font.render(f"Puntos de mejora: {upgrade_points}", True, YELLOW)

        def draw_health_bar(surface, x, y, width, height, current_health, max_health):
            health_ratio = current_health / max_health
            pygame.draw.rect(surface, RED, (x, y, width, height))
            pygame.draw.rect(surface, GREEN, (x, y, width * health_ratio, height))
        draw_health_bar(win, 10, HEIGHT - 40, 200, 20, lives, max_lives)

        xp_bar_width = 200
        xp_bar_height = 20
        xp_bar_x = WIDTH - xp_bar_width - 20
        xp_bar_y = 20
        xp_bar_progress = (player_xp / xp_to_next_level) * xp_bar_width
        pygame.draw.rect(win, WHITE, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
        pygame.draw.rect(win, BLUE, (xp_bar_x, xp_bar_y, xp_bar_progress, xp_bar_height))

        win.blit(text, (10, 10))
        win.blit(level_text, (10, 50))
        win.blit(xp_text, (10, 90))
        win.blit(weapon_text, (10, 130))
        win.blit(wave_text, (10, 170))
        win.blit(upg_text, (10, 210))

        wave_timer += dt
        if wave_timer > 30000:
            wave += 1
            wave_timer = 0
            spawn_enemy()

        if len(enemies) == 0:
            wave += 1
            for _ in range(2 + wave):
                spawn_enemy()

        if show_upgrade_menu_flag:
            show_upgrade_menu()

        pygame.display.flip()

game_loop()
