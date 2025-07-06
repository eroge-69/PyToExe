import pygame
import random
import math
import sys
import os

# --- INIT ---
pygame.init()
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Shooter - Niveaux & IA")

# --- COLORS ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 210, 0)
GRAY  = (120, 120, 120)
BLOOD = (170, 15, 15)
OBSTACLE = (80, 60, 30)
BAR_BG = (40, 40, 40)

# --- CONST ---
PLAYER_WIDTH, PLAYER_HEIGHT = 20, 60
ENEMY_WIDTH, ENEMY_HEIGHT = 20, 60
BULLET_RADIUS = 6
GROUND_HEIGHT = 80
GRAVITY = 1
JUMP_POWER = 16
SPEED = 6
ENEMY_SPEED = 3
ENEMY_BULLET_SPEED = 10
FIRE_RATE = 90  # frames between enemy shots

# --- SOUNDS (optionally put shoot.wav and win.wav in the folder) ---
shoot_sound = None
win_sound = None
if os.path.isfile("shoot.wav"):
    shoot_sound = pygame.mixer.Sound("shoot.wav")
if os.path.isfile("win.wav"):
    win_sound = pygame.mixer.Sound("win.wav")

# --- CLASSES ---
class BloodParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.radius = random.randint(2, 4)
        self.life = random.randint(12, 22)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5
        self.life -= 1
    def draw(self, win, offset_x):
        if self.life > 0:
            pygame.draw.circle(win, BLOOD, (int(self.x - offset_x), int(self.y)), self.radius)

class Obstacle:
    def __init__(self, rect):
        self.rect = rect
    def draw(self, win, offset_x):
        pygame.draw.rect(win, OBSTACLE, pygame.Rect(self.rect.left - offset_x, self.rect.top, self.rect.width, self.rect.height))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.on_ground = False
        self.bullets = []
        self.life = 100
        self.invuln = 0
        self.facing = 1
        self.anim_time = 0
        self.last_dx = 0
    def move(self, dx, platforms, obstacles):
        prev_x = self.x
        self.x += dx
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        self.x = max(0, min(self.mapw - PLAYER_WIDTH, self.x))
        for plat in platforms + [o.rect for o in obstacles]:
            if self.rect().colliderect(plat) and prev_x + PLAYER_WIDTH <= plat.left:
                self.x = plat.left - PLAYER_WIDTH
            elif self.rect().colliderect(plat) and prev_x >= plat.right:
                self.x = plat.right
        if dx != 0:
            self.anim_time += abs(dx) * 0.11
            self.last_dx = dx
        else:
            self.anim_time += abs(self.last_dx) * 0.03
    def jump(self):
        if self.on_ground:
            self.vy = -JUMP_POWER
            self.on_ground = False
    def update(self, platforms, obstacles):
        self.vy += GRAVITY
        self.y += self.vy
        self.on_ground = False
        for plat in platforms + [o.rect for o in obstacles]:
            if self.rect().colliderect(plat) and self.vy > 0:
                self.y = plat.top - PLAYER_HEIGHT
                self.vy = 0
                self.on_ground = True
        if self.y + PLAYER_HEIGHT > HEIGHT - GROUND_HEIGHT:
            self.y = HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
            self.vy = 0
            self.on_ground = True
        if self.invuln > 0:
            self.invuln -= 1
    def rect(self):
        return pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
    def draw(self, win, offset_x, mouse_pos):
        center_x = int(self.x - offset_x + PLAYER_WIDTH // 2)
        y = int(self.y)
        mx, my = mouse_pos
        px = center_x
        py = y + 25
        angle = math.atan2(my - py, (mx + offset_x) - self.x - PLAYER_WIDTH//2)
        arm_length = 26
        step = math.sin(self.anim_time * 0.25)
        leg_a = math.radians(22) * step
        leg_b = -math.radians(22) * step
        arm_swing = math.radians(18) * step
        head = (px, y + 10)
        body0 = (px, y + 10)
        body1 = (px, y + PLAYER_HEIGHT)
        # Bras droit (pistolet)
        arm_r0 = (px, y + 25)
        arm_r1 = (
            int(px + math.cos(angle) * arm_length),
            int(y + 25 + math.sin(angle) * arm_length)
        )
        gun_len = 15
        gun_x = int(arm_r1[0] + math.cos(angle) * gun_len)
        gun_y = int(arm_r1[1] + math.sin(angle) * gun_len)
        hand_r = arm_r1
        # Bras gauche = balancier
        arm_l0 = (px, y + 25)
        swing_l = arm_swing
        arm_l1 = (
            int(px + math.cos(-math.pi/2 + swing_l) * 20),
            int(y + 25 + math.sin(-math.pi/2 + swing_l) * 22)
        )
        leg0 = (px, y + PLAYER_HEIGHT)
        leg_l = (
            int(leg0[0] + math.sin(leg_a) * 18),
            int(leg0[1] + math.cos(leg_a) * 23)
        )
        leg_r = (
            int(leg0[0] + math.sin(leg_b) * 18),
            int(leg0[1] + math.cos(leg_b) * 23)
        )
        # Players turns red when invulnerable
        color = RED if self.invuln > 0 and (self.invuln // 5) % 2 == 0 else BLACK
        pygame.draw.line(win, color, body0, body1, 3)
        pygame.draw.circle(win, color, head, 10, 2)
        pygame.draw.line(win, color, arm_r0, arm_r1, 4)
        pygame.draw.line(win, (60, 60, 60), arm_r1, (gun_x, gun_y), 8)
        pygame.draw.line(win, (120, 120, 120), arm_r1, (gun_x, gun_y), 3)
        pygame.draw.circle(win, (180,120,70), hand_r, 4)
        pygame.draw.line(win, color, arm_l0, arm_l1, 3)
        pygame.draw.line(win, color, leg0, leg_l, 3)
        pygame.draw.line(win, color, leg0, leg_r, 3)
        # Draw life bar
        pygame.draw.rect(win, BAR_BG, (center_x-32, y-18, 64, 10))
        pygame.draw.rect(win, GREEN, (center_x-32, y-18, int(64 * self.life / 100), 10))
        pygame.draw.rect(win, BLACK, (center_x-32, y-18, 64, 10), 1)

class Enemy:
    def __init__(self, x, y, armed, mapw):
        self.x = x
        self.y = y
        self.armed = armed
        self.vy = 0
        self.target = None
        self.fire_cooldown = random.randint(0, FIRE_RATE)
        self.bullets = []
        self.alive = True
        self.anim_time = random.uniform(0, 10)
        self.mapw = mapw
    def rect(self):
        return pygame.Rect(self.x, self.y, ENEMY_WIDTH, ENEMY_HEIGHT)
    def update(self, player, platforms, obstacles):
        if not self.alive: return
        self.vy += GRAVITY
        self.y += self.vy
        on_ground = False
        for plat in platforms + [o.rect for o in obstacles]:
            if self.rect().colliderect(plat) and self.vy > 0:
                self.y = plat.top - ENEMY_HEIGHT
                self.vy = 0
                on_ground = True
        if self.y + ENEMY_HEIGHT > HEIGHT - GROUND_HEIGHT:
            self.y = HEIGHT - GROUND_HEIGHT - ENEMY_HEIGHT
            self.vy = 0
            on_ground = True
        # Mouvement IA
        if self.armed:
            # Essaie de viser le joueur mais ne fonce pas
            if abs(self.x - player.x) > 300:
                self.x += ENEMY_SPEED if self.x < player.x else -ENEMY_SPEED
            # Tire si aligné
            self.fire_cooldown -= 1
            if self.fire_cooldown <= 0:
                # Check si rien bloque la ligne de vue
                can_shoot = True
                for obs in obstacles:
                    if obs.rect.clipline(self.x+ENEMY_WIDTH//2, self.y+25, player.x+PLAYER_WIDTH//2, player.y+25):
                        can_shoot = False
                        break
                if can_shoot:
                    px, py = self.x+ENEMY_WIDTH//2, self.y+25
                    angle = math.atan2((player.y+25)-py, (player.x+PLAYER_WIDTH//2)-px)
                    self.bullets.append(Bullet(px + math.cos(angle)*32, py + math.sin(angle)*32, angle, ENEMY_BULLET_SPEED, "enemy"))
                    self.fire_cooldown = FIRE_RATE + random.randint(0,40)
        else:
            # Court partout (petit IA marrante)
            if not hasattr(self, "tgt"):
                self.tgt = random.randint(0, self.mapw-ENEMY_WIDTH)
            if abs(self.x - self.tgt) < 10:
                self.tgt = random.randint(0, self.mapw-ENEMY_WIDTH)
            if self.x < self.tgt:
                self.x += ENEMY_SPEED+1
            else:
                self.x -= ENEMY_SPEED+1
    def draw(self, win, offset_x):
        center_x = int(self.x - offset_x + ENEMY_WIDTH // 2)
        y = int(self.y)
        self.anim_time += 0.13
        step = math.sin(self.anim_time * 0.23)
        leg_a = math.radians(22) * step
        leg_b = -math.radians(22) * step
        arm_swing = math.radians(18) * step
        head = (center_x, y + 10)
        body0 = (center_x, y + 10)
        body1 = (center_x, y + ENEMY_HEIGHT)
        # Bras
        arm_l0 = (center_x, y + 25)
        arm_l1 = (
            int(center_x + math.cos(-math.pi/2 + arm_swing) * 20),
            int(y + 25 + math.sin(-math.pi/2 + arm_swing) * 22)
        )
        arm_r0 = (center_x, y + 25)
        if self.armed:
            # Bras droit vise le joueur (pistolet)
            angle = 0
            if self.target:
                mx, my = self.target
                angle = math.atan2(my - (y+25), mx - center_x)
            else:
                angle = 0
            arm_r1 = (
                int(center_x + math.cos(angle) * 26),
                int(y + 25 + math.sin(angle) * 26)
            )
            gun_len = 15
            gun_x = int(arm_r1[0] + math.cos(angle) * gun_len)
            gun_y = int(arm_r1[1] + math.sin(angle) * gun_len)
            hand_r = arm_r1
        else:
            # Bras normaux
            arm_r1 = (
                int(center_x + math.cos(-math.pi/2 - arm_swing) * 20),
                int(y + 25 + math.sin(-math.pi/2 - arm_swing) * 22)
            )
            hand_r = arm_r1
        leg0 = (center_x, y + ENEMY_HEIGHT)
        leg_l = (
            int(leg0[0] + math.sin(leg_a) * 18),
            int(leg0[1] + math.cos(leg_a) * 23)
        )
        leg_r = (
            int(leg0[0] + math.sin(leg_b) * 18),
            int(leg0[1] + math.cos(leg_b) * 23)
        )
        pygame.draw.line(win, RED, body0, body1, 3)
        pygame.draw.circle(win, RED, head, 10, 2)
        pygame.draw.line(win, RED, arm_l0, arm_l1, 3)
        pygame.draw.line(win, RED, arm_r0, arm_r1, 4 if self.armed else 3)
        if self.armed:
            pygame.draw.line(win, (60, 60, 60), arm_r1, (gun_x, gun_y), 8)
            pygame.draw.line(win, (120, 120, 120), arm_r1, (gun_x, gun_y), 3)
            pygame.draw.circle(win, (180,120,70), hand_r, 4)
        pygame.draw.line(win, RED, leg0, leg_l, 3)
        pygame.draw.line(win, RED, leg0, leg_r, 3)

class Bullet:
    def __init__(self, x, y, angle, speed, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = BULLET_RADIUS
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.owner = owner  # "player" or "enemy"
    def update(self):
        self.x += self.vx
        self.y += self.vy
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
    def draw(self, win, offset_x):
        color = BLACK if self.owner == "player" else RED
        pygame.draw.circle(win, color, (int(self.x - offset_x), int(self.y)), self.radius)

# --- MAP GENERATION ---
def make_platforms_and_obstacles(level, MAP_WIDTH):
    plats = []
    plats.append(pygame.Rect(0, HEIGHT - GROUND_HEIGHT, MAP_WIDTH, GROUND_HEIGHT))
    plat_num = 10 + level
    for _ in range(plat_num):
        plat_width = random.randint(120, 200)
        plat_height = 20
        plat_x = random.randint(0, MAP_WIDTH - plat_width)
        plat_y = random.randint(120, HEIGHT - 200)
        plats.append(pygame.Rect(plat_x, plat_y, plat_width, plat_height))
    # Obstacles (caisses)
    obstacles = []
    obs_num = 3 + level
    for _ in range(obs_num):
        w = random.randint(50, 90)
        h = random.randint(32, 60)
        x = random.randint(0, MAP_WIDTH - w)
        y = HEIGHT - GROUND_HEIGHT - h
        obstacles.append(Obstacle(pygame.Rect(x, y, w, h)))
    return plats, obstacles

def spawn_enemies(platforms, obstacles, n=9, level=1, MAP_WIDTH=2700):
    enemies = []
    total = n + level*2
    for _ in range(total):
        armed = random.random() < min(0.55, 0.16 + 0.11*level)
        plat = random.choice(platforms[1:])
        x = random.randint(plat.left, plat.right - ENEMY_WIDTH)
        y = plat.top - ENEMY_HEIGHT
        e = Enemy(x, y, armed, MAP_WIDTH)
        enemies.append(e)
    return enemies

# --- MENU ---
def menu_victoire(win, level, maxlevel):
    font = pygame.font.SysFont(None, 64)
    text = font.render("Bravo ! Niveau fini !", True, GREEN)
    choix_font = pygame.font.SysFont(None, 36)
    if level < maxlevel:
        nextlevel = choix_font.render("N = prochain niveau", True, BLACK)
    else:
        nextlevel = choix_font.render("Félicitations, tous les niveaux finis !", True, BLACK)
    rejouer = choix_font.render("R = recommencer ce niveau", True, BLACK)
    quitter = choix_font.render("Echap = quitter", True, BLACK)
    win.fill(WHITE)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 140))
    win.blit(nextlevel, (WIDTH // 2 - nextlevel.get_width() // 2, HEIGHT // 2 - 50))
    win.blit(rejouer, (WIDTH // 2 - rejouer.get_width() // 2, HEIGHT // 2 + 10))
    win.blit(quitter, (WIDTH // 2 - quitter.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    attente = True
    result = None
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n and level < maxlevel:
                    return "next"
                elif event.key == pygame.K_r:
                    return "replay"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
    return result

def menu_defaite(win):
    font = pygame.font.SysFont(None, 64)
    text = font.render("Tu es mort !", True, RED)
    choix_font = pygame.font.SysFont(None, 36)
    rejouer = choix_font.render("R = recommencer le niveau", True, BLACK)
    quitter = choix_font.render("Echap = quitter", True, BLACK)
    win.fill(WHITE)
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
    win.blit(rejouer, (WIDTH // 2 - rejouer.get_width() // 2, HEIGHT // 2))
    win.blit(quitter, (WIDTH // 2 - quitter.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.flip()
    attente = True
    result = None
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "replay"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
    return result

# --- MAIN LOOP ---
def main():
    level = 1
    maxlevel = 5
    MAP_WIDTH = WIDTH * 3
    while True:
        # --- Setup level ---
        platforms, obstacles = make_platforms_and_obstacles(level, MAP_WIDTH)
        player = Player(100, HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT)
        player.mapw = MAP_WIDTH
        enemies = spawn_enemies(platforms, obstacles, n=7, level=level, MAP_WIDTH=MAP_WIDTH)
        blood_particles = []
        run = True
        offset_x = 0
        enemy_bullets = []
        clock = pygame.time.Clock()
        while run:
            clock.tick(60)
            WIN.fill(WHITE)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # --- Events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.life > 0:
                    px = player.x + PLAYER_WIDTH//2
                    py = player.y + 25
                    angle = math.atan2(mouse_y - py, mouse_x + offset_x - px)
                    bullet_x = px + math.cos(angle)*32
                    bullet_y = py + math.sin(angle)*32
                    player.bullets.append(Bullet(bullet_x, bullet_y, angle, 17, "player"))
                    if shoot_sound:
                        shoot_sound.play()
            # --- Input ---
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_q]:
                dx = -SPEED
            if keys[pygame.K_d]:
                dx = SPEED
            if keys[pygame.K_SPACE]:
                player.jump()
            player.move(dx, platforms, obstacles)
            player.update(platforms, obstacles)
            # Camera
            offset_x = int(player.x - WIDTH/2)
            offset_x = max(0, min(offset_x, MAP_WIDTH - WIDTH))
            # Bullets (player)
            for bullet in player.bullets[:]:
                bullet.update()
                collided = False
                # Obstacles stop bullets
                for obs in obstacles:
                    if obs.rect.colliderect(bullet.rect()):
                        collided = True
                        break
                for enemy in enemies:
                    if enemy.alive and bullet.owner == "player" and bullet.rect().colliderect(enemy.rect()):
                        enemy.alive = False
                        collided = True
                        for _ in range(15):
                            blood_particles.append(BloodParticle(bullet.x, bullet.y))
                        break
                if bullet.x < 0 or bullet.x > MAP_WIDTH or bullet.y < 0 or bullet.y > HEIGHT or collided:
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
            # Bullets (enemies)
            for enemy in enemies:
                enemy.update(player, platforms, obstacles)
                for b in enemy.bullets[:]:
                    b.update()
                    # Obstacles stop bullets
                    hit = False
                    for obs in obstacles:
                        if obs.rect.colliderect(b.rect()):
                            hit = True
                    if b.rect().colliderect(player.rect()) and player.invuln == 0:
                        player.life -= 15
                        player.invuln = 30
                        hit = True
                        for _ in range(10):
                            blood_particles.append(BloodParticle(b.x, b.y))
                    if b.x < 0 or b.x > MAP_WIDTH or b.y < 0 or b.y > HEIGHT or hit:
                        enemy.bullets.remove(b)
            # Ennemis non armés blessent si touche
            for enemy in enemies:
                if not enemy.armed and enemy.alive and player.rect().colliderect(enemy.rect()) and player.invuln == 0:
                    player.life -= 6
                    player.invuln = 20
                    for _ in range(7):
                        blood_particles.append(BloodParticle(player.x+PLAYER_WIDTH//2, player.y+PLAYER_HEIGHT//2))
            # Particules de sang
            for p in blood_particles[:]:
                p.update()
                if p.life <= 0 or p.y > HEIGHT:
                    blood_particles.remove(p)
            # Drawing
            for plat in platforms:
                pygame.draw.rect(WIN, GRAY, pygame.Rect(plat.left - offset_x, plat.top, plat.width, plat.height))
            for obs in obstacles:
                obs.draw(WIN, offset_x)
            for p in blood_particles:
                p.draw(WIN, offset_x)
            for enemy in enemies:
                if enemy.alive:
                    enemy.target = (player.x - offset_x + PLAYER_WIDTH // 2, player.y + 25)
                    enemy.draw(WIN, offset_x)
                for b in enemy.bullets:
                    b.draw(WIN, offset_x)
            player.draw(WIN, offset_x, (mouse_x, mouse_y))
            for bullet in player.bullets:
                bullet.draw(WIN, offset_x)
            # HUD
            font = pygame.font.SysFont(None, 36)
            txt = font.render(f"Ennemis restants : {sum(1 for e in enemies if e.alive)}", True, BLACK)
            WIN.blit(txt, (16, 10))
            pygame.draw.rect(WIN, BAR_BG, (16, 50, 160, 18))
            pygame.draw.rect(WIN, GREEN, (16, 50, int(160 * player.life / 100), 18))
            pygame.draw.rect(WIN, BLACK, (16, 50, 160, 18), 2)
            # Win/lose conditions
            if player.life <= 0:
                pygame.time.wait(700)
                result = menu_defaite(WIN)
                if result == "replay":
                    run = False
                else:
                    pygame.quit(); sys.exit()
            elif all(not e.alive for e in enemies):
                if win_sound:
                    win_sound.play()
                pygame.time.wait(700)
                result = menu_victoire(WIN, level, maxlevel)
                if result == "next":
                    level += 1
                    if level > maxlevel:
                        pygame.quit(); sys.exit()
                    run = False
                elif result == "replay":
                    run = False
                elif result == "quit":
                    pygame.quit(); sys.exit()
            pygame.display.update()

if __name__ == "__main__":
    main()