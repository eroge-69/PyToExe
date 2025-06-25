import pygame
import math
import random
import sys

pygame.init()
pygame.mouse.set_visible(False)  

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Doom")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
font_large = pygame.font.SysFont('Arial', 50)
font_medium = pygame.font.SysFont('Arial', 30)
font_small = pygame.font.SysFont('Arial', 20)


MENU = 0
GAME = 1
GAME_OVER = 2
VICTORY = 3
game_state = MENU
current_level = 1
max_levels = 5

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3
        self.health = 100
        self.ammo = 30
        self.score = 0

class Enemy:
    def __init__(self, x, y, color, speed, damage, health):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.damage = damage
        self.health = health
        self.size = 20
        self.attack_cooldown = 0

class Level:
    def __init__(self, number):
        self.number = number
        self.map_size = 8 + number * 2
        self.cell_size = 50
        self.generate_map()
        self.generate_enemies()
        
    def generate_map(self):
        self.game_map = [[1 for _ in range(self.map_size)] for _ in range(self.map_size)]
        
    
        for y in range(1, self.map_size-1):
            for x in range(1, self.map_size-1):
                if random.random() > 0.3:  
                    self.game_map[y][x] = 0
                
    
        self.game_map[1][1] = 0
        self.game_map[1][2] = 0
        self.game_map[2][1] = 0
        
    def generate_enemies(self):
        self.enemies = []
        enemy_count = 3 + self.number * 2
        
        for _ in range(enemy_count):
            while True:
                x = random.randint(1, self.map_size-2) * self.cell_size + self.cell_size//2
                y = random.randint(1, self.map_size-2) * self.cell_size + self.cell_size//2
            
            
                if math.sqrt((x - self.cell_size*1.5)**2 + (y - self.cell_size*1.5)**2) > 200:
                    break
            
            
            health = 80 + self.number * 20
            speed = 0.5 + self.number * 0.2
            damage = 5 + self.number * 2
            
            color = random.choice([RED, BLUE, GREEN, YELLOW, PURPLE])
            self.enemies.append(Enemy(x, y, color, speed, damage, health))


player = Player(100, 100)
level = None
weapon_img = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.rect(weapon_img, (150, 150, 150), (20, 50, 60, 20))
pygame.draw.rect(weapon_img, (100, 100, 100), (10, 60, 80, 10))
weapon_pos = 0
weapon_recoil = False
shooting = False


FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
STEP_ANGLE = FOV / NUM_RAYS

MOUSE_SENSITIVITY = 0.002
pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2) 

def start_level(level_num):
    global player, level
    player = Player(100, 100)
    level = Level(level_num)

def cast_ray(angle):
    
    v_x, v_y = 0, 0
    v_depth = 0
    v_texture = 0
    
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    
    x, dx = (player.x // level.cell_size) * level.cell_size, level.cell_size
    if cos_a > 0:
        x += level.cell_size
        dx = 1
    else:
        dx = -1
    
    for depth in range(0, MAX_DEPTH, level.cell_size):
        v_depth = (x - player.x) / cos_a
        y = player.y + v_depth * sin_a
        
        map_x = int(x // level.cell_size)
        map_y = int(y // level.cell_size)
        
        if 0 <= map_x < level.map_size and 0 <= map_y < level.map_size:
            if level.game_map[map_y][map_x] == 1:
                v_texture = level.game_map[map_y][map_x]
                v_x, v_y = x, y
                break
        x += dx * level.cell_size
    

    h_x, h_y = 0, 0
    h_depth = 0
    h_texture = 0
    
    y, dy = (player.y // level.cell_size) * level.cell_size, level.cell_size
    if sin_a > 0:
        y += level.cell_size
        dy = 1
    else:
        dy = -1
    
    for depth in range(0, MAX_DEPTH, level.cell_size):
        h_depth = (y - player.y) / sin_a
        x = player.x + h_depth * cos_a
        
        map_x = int(x // level.cell_size)
        map_y = int(y // level.cell_size)
        
        if 0 <= map_x < level.map_size and 0 <= map_y < level.map_size:
            if level.game_map[map_y][map_x] == 1:
                h_texture = level.game_map[map_y][map_x]
                h_x, h_y = x, y
                break
        y += dy * level.cell_size
    

    if v_depth and (not h_depth or v_depth < h_depth):
        return v_depth, v_x, v_y, v_texture
    else:
        return h_depth, h_x, h_y, h_texture

def draw_minimap():
    minimap_size = 150
    minimap_pos = (WIDTH - minimap_size - 10, 10)
    cell_size = minimap_size // level.map_size
    
    for y in range(level.map_size):
        for x in range(level.map_size):
            if level.game_map[y][x] == 1:
                pygame.draw.rect(screen, WHITE, 
                                (minimap_pos[0] + x * cell_size, 
                                 minimap_pos[1] + y * cell_size, 
                                 cell_size, cell_size))
    
    player_map_x = minimap_pos[0] + (player.x / (level.map_size * level.cell_size)) * minimap_size
    player_map_y = minimap_pos[1] + (player.y / (level.map_size * level.cell_size)) * minimap_size
    pygame.draw.circle(screen, RED, (int(player_map_x), int(player_map_y)), 3)
    
    end_x = player_map_x + math.cos(player.angle) * 15
    end_y = player_map_y + math.sin(player.angle) * 15
    pygame.draw.line(screen, RED, (player_map_x, player_map_y), (end_x, end_y), 2)
    

    for enemy in level.enemies:
        if enemy.health > 0:
            enemy_x = minimap_pos[0] + (enemy.x / (level.map_size * level.cell_size)) * minimap_size
            enemy_y = minimap_pos[1] + (enemy.y / (level.map_size * level.cell_size)) * minimap_size
            pygame.draw.circle(screen, enemy.color, (int(enemy_x), int(enemy_y)), 3)

def draw_enemies():
    for enemy in level.enemies:
        if enemy.health > 0:
        
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            
            
            distance = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) - player.angle
            
    
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            
        
            if -HALF_FOV <= angle <= HALF_FOV:
                
                size = min(200, int(level.cell_size * 5 / (distance + 0.0001) * 100))
                
        
                x_pos = (angle + HALF_FOV) / FOV * WIDTH
                x_pos = x_pos - size // 2
                
            
                y_pos = HEIGHT // 2 - size // 2
                
                
                pygame.draw.rect(screen, enemy.color, 
                                (int(x_pos), int(y_pos), size, size))
            
                
                health_width = size * enemy.health / 100
                pygame.draw.rect(screen, RED, (int(x_pos), int(y_pos - 10), int(size), 5))
                pygame.draw.rect(screen, GREEN, (int(x_pos), int(y_pos - 10), int(health_width), 5))

def draw_weapon():
    global weapon_pos, weapon_recoil
    

    if shooting:
        weapon_pos = 20
        weapon_recoil = True
    elif weapon_recoil:
        weapon_pos -= 1
        if weapon_pos <= 0:
            weapon_pos = 0
            weapon_recoil = False
    
    
    screen.blit(weapon_img, (WIDTH//2 - 50, HEIGHT - 150 + weapon_pos))
    

    pygame.draw.line(screen, RED, (WIDTH//2 - 10, HEIGHT//2), (WIDTH//2 + 10, HEIGHT//2), 2)
    pygame.draw.line(screen, RED, (WIDTH//2, HEIGHT//2 - 10), (WIDTH//2, HEIGHT//2 + 10), 2)

def check_collision(x, y):
    map_x, map_y = int(x // level.cell_size), int(y // level.cell_size)
    if 0 <= map_x < level.map_size and 0 <= map_y < level.map_size:
        return level.game_map[map_y][map_x] == 1
    return True

def check_enemy_hit():
    if player.ammo <= 0:
        return
    
    player.ammo -= 1
    

    for enemy in level.enemies[:]:
        if enemy.health > 0:
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx) - player.angle
        
        
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            
            
            if -0.1 <= angle <= 0.1 and distance < 200:
                enemy.health -= 25
                player.score += 10
                if enemy.health <= 0:
                    level.enemies.remove(enemy)
                    player.score += 50
                break

def update_enemies():
    for enemy in level.enemies:
        if enemy.health > 0:
            
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx /= dist
                dy /= dist
                
        
                new_x = enemy.x + dx * enemy.speed
                new_y = enemy.y + dy * enemy.speed
                
                if not check_collision(new_x, enemy.y):
                    enemy.x = new_x
                if not check_collision(enemy.x, new_y):
                    enemy.y = new_y
        
            if dist < 50 and enemy.attack_cooldown <= 0:
                player.health -= enemy.damage
                enemy.attack_cooldown = 60
            
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= 1

def draw_menu():
    screen.fill(BLACK)
    
    for i in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(20, 100)
        pygame.draw.rect(screen, GRAY, (x, y, size, size))
    

    title = font_large.render("PYTHON DOOM", True, RED)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    for i in range(1, max_levels+1):
        color = GREEN if i <= current_level else GRAY
        level_text = font_medium.render(f"Уровень {i}", True, color)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 200 + i * 50))
    instr = font_small.render("Выберите уровень (1-5) или ESC для выхода", True, WHITE)
    screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT - 50))

def draw_game():
    screen.fill(BLACK)
    

    ray_angle = player.angle - HALF_FOV
    for ray in range(NUM_RAYS):
        depth, x, y, texture = cast_ray(ray_angle)
        

        depth *= math.cos(player.angle - ray_angle)

        wall_height = min(int(level.cell_size * 300 / (depth + 0.0001)), HEIGHT)
        
        wall_pos = (HEIGHT - wall_height) // 2
        
        color_intensity = min(255, 255 / (1 + depth * depth * 0.0001))
        wall_color = (color_intensity, color_intensity, color_intensity)
        pygame.draw.rect(screen, wall_color, 
                        (ray * (WIDTH // NUM_RAYS), wall_pos, 
                         WIDTH // NUM_RAYS + 1, wall_height))
        
        ray_angle += STEP_ANGLE
    
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, GRAY, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    
    draw_enemies()
    
    draw_weapon()
    
    draw_minimap()
    health_text = font_small.render(f"Здоровье: {player.health}", True, WHITE)
    ammo_text = font_small.render(f"Патроны: {player.ammo}", True, WHITE)
    score_text = font_small.render(f"Очки: {player.score}", True, WHITE)
    level_text = font_small.render(f"Уровень: {current_level}", True, WHITE)
    
    screen.blit(health_text, (10, 10))
    screen.blit(ammo_text, (10, 40))
    screen.blit(score_text, (10, 70))
    screen.blit(level_text, (10, 100))

def draw_game_over():
    screen.fill(BLACK)
    game_over_text = font_large.render("GAME OVER", True, RED)
    score_text = font_medium.render(f"Ваш счет: {player.score}", True, WHITE)
    restart_text = font_small.render("Нажмите R для перезапуска или ESC для выхода", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))

def draw_victory():
    screen.fill(BLACK)
    victory_text = font_large.render("ПОБЕДА!", True, GREEN)
    score_text = font_medium.render(f"Ваш счет: {player.score}", True, WHITE)
    restart_text = font_small.render("Нажмите R для перезапуска или ESC для выхода", True, WHITE)
    
    screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))


clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == GAME:
                    game_state = MENU
                    pygame.mouse.set_visible(True)  
                else:
                    running = False
            elif game_state == MENU and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                current_level = int(pygame.key.name(event.key))
                start_level(current_level)
                game_state = GAME
                pygame.mouse.set_visible(False)  
                pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2) 
            elif game_state in (GAME_OVER, VICTORY) and event.key == pygame.K_r:
                game_state = MENU
                pygame.mouse.set_visible(True) 
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and game_state == GAME:
                shooting = True
                check_enemy_hit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                shooting = False

    if game_state == GAME:
        mouse_x, _ = pygame.mouse.get_pos()
        rel_x = mouse_x - WIDTH // 2
        player.angle += rel_x * MOUSE_SENSITIVITY
        pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)  
        
        keys = pygame.key.get_pressed()
        
        sin_a = math.sin(player.angle)
        cos_a = math.cos(player.angle)
        
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dx += cos_a * player.speed
            dy += sin_a * player.speed
        if keys[pygame.K_s]:
            dx -= cos_a * player.speed
            dy -= sin_a * player.speed
        if keys[pygame.K_a]:
            dx += sin_a * player.speed
            dy -= cos_a * player.speed
        if keys[pygame.K_d]:
            dx -= sin_a * player.speed
            dy += cos_a * player.speed
        
        new_x = player.x + dx
        new_y = player.y + dy
        
        if not check_collision(new_x, player.y):
            player.x = new_x
        if not check_collision(player.x, new_y):
            player.y = new_y
        
        update_enemies()
        
        if player.health <= 0:
            game_state = GAME_OVER
            pygame.mouse.set_visible(True)  
        elif not level.enemies and current_level < max_levels:
            current_level += 1
            start_level(current_level)
        elif not level.enemies and current_level == max_levels:
            game_state = VICTORY
            pygame.mouse.set_visible(True)  
    
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    elif game_state == VICTORY:
        draw_victory()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
