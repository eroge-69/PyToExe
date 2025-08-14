import pygame
import random
import sys
import math
import pyttsx3

# TTS init
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Uzay Macerası - Vahşi ve Erişilebilir")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
STONE_COLORS = [YELLOW, GREEN, BLUE, PURPLE, RED, ORANGE, WHITE]

# Player settings
player_size = 50
player_x = 100
player_y = SCREEN_HEIGHT // 2
player_speed_y = 5
player_jump_speed = -15
player_gravity = 1
player_velocity_y = 0
player_flying = False
player_in_vehicle = False
player_is_ball = False
ball_duration = 60
ball_timer = 0
ball_cooldown = 180
ball_cooldown_timer = 0
vehicle_boost = 2
player_projectiles = []
player_projectile_speed = 10
player_spinning = False
spin_cooldown = 0
SPIN_COOLDOWN_MAX = 120
spin_duration = 30
spin_timer = 0
SPIN_THRESHOLD = 5
bite_cooldown = 0
BITE_COOLDOWN_MAX = 90  # 1.5 saniye

# Robot friend settings
robot_friend_x = 50
robot_friend_y = SCREEN_HEIGHT // 2
robot_friend_advice_timer = 0
ADVICE_INTERVAL = 300

# Obstacles, etc.
obstacles = []
enemies = []
robots = []
vehicles = []
obstacle_speed = 5
enemy_speed = 6
robot_speed = 5
vehicle_speed = 7
spawn_rate = 60
frame_count = 0

falling_stones = []
falling_stone_spawn_rate = 30
falling_frame_count = 0
falling_stone_speed = 4

projectiles = []
projectile_speed = 7

stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(100)]

font = pygame.font.Font(None, 48)

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_PAUSED = 3
STATE_EXIT_CONFIRM = 4
game_state = STATE_MENU

# Buttons
start_button = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 80)
exit_button = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2, 400, 80)
pause_button = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 40)
exit_yes_button = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50, 190, 80)
exit_no_button = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 - 50, 190, 80)

pygame.mixer.init()
def play_beep(freq=440, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    max_amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    samples = int(sample_rate * duration)
    sound = pygame.mixer.Sound(pygame.sndarray.make_sound([max_amplitude * math.sin(2.0 * math.pi * freq * t / sample_rate) for t in range(samples)]))
    sound.play()

def reset_game():
    global player_x, player_y, player_velocity_y, player_flying, player_in_vehicle, player_is_ball, ball_timer, ball_cooldown_timer, obstacles, enemies, robots, vehicles, falling_stones, projectiles, player_projectiles, frame_count, falling_frame_count, spawn_rate, obstacle_speed, enemy_speed, robot_speed, vehicle_speed, player_spinning, spin_cooldown, spin_timer, robot_friend_x, robot_friend_y, robot_friend_advice_timer, bite_cooldown
    player_x = 100
    player_y = SCREEN_HEIGHT // 2
    player_velocity_y = 0
    player_flying = False
    player_in_vehicle = False
    player_is_ball = False
    ball_timer = 0
    ball_cooldown_timer = 0
    obstacles = []
    enemies = []
    robots = []
    vehicles = []
    falling_stones = []
    projectiles = []
    player_projectiles = []
    frame_count = 0
    falling_frame_count = 0
    spawn_rate = 60
    obstacle_speed = 5
    enemy_speed = 6
    robot_speed = 5
    vehicle_speed = 7
    player_spinning = False
    spin_cooldown = 0
    spin_timer = 0
    bite_cooldown = 0
    robot_friend_x = 50
    robot_friend_y = SCREEN_HEIGHT // 2
    robot_friend_advice_timer = 0
    speak("Oyun sıfırlandı. Oyuna başla.")

def draw_player(x, y, in_vehicle=False, spinning=False, is_ball=False):
    if is_ball:
        pygame.draw.circle(screen, GREEN, (int(x + player_size//2), int(y + player_size//2)), player_size//2)
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            pygame.draw.line(screen, GREEN, (x + player_size//2, y + player_size//2),
                            (x + player_size//2 + math.cos(angle) * 60, y + player_size//2 + math.sin(angle) * 60), 2)
    elif in_vehicle:
        draw_vehicle(x, y + 20, has_owner=False)
        points = [
            (x + 20, y - 10),
            (x + 40, y - 40),
            (x + 60, y - 10),
            (x + 50, y + 10),
            (x + 70, y + 30)
        ]
        if spinning:
            points = [(p[0] + 20 * math.cos(spin_timer / 5), p[1] + 20 * math.sin(spin_timer / 5)) for p in points]
        pygame.draw.polygon(screen, GREEN, points)
        pygame.draw.rect(screen, RED, (x + 80, y + 10, 20, 10))
    else:
        points = [
            (x, y),
            (x + 20, y - 30),
            (x + 40, y),
            (x + 30, y + 20),
            (x + 50, y + 40),
            (x + 10, y + 50),
            (x - 10, y + 30),
            (x - 20, y + 10)
        ]
        if spinning:
            points = [(p[0] + 20 * math.cos(spin_timer / 5), p[1] + 20 * math.sin(spin_timer / 5)) for p in points]
        pygame.draw.polygon(screen, GREEN, points)

def draw_obstacle(x, y):
    pygame.draw.polygon(screen, WHITE, [(x, y), (x + 30, y - 20), (x + 60, y)])

def draw_enemy(x, y):
    pygame.draw.circle(screen, RED, (x + 25, y + 25), 25)
    pygame.draw.polygon(screen, WHITE, [(x + 20, y + 10), (x + 25, y + 20), (x + 30, y + 10)])

def draw_robot(x, y):
    pygame.draw.rect(screen, GRAY, (x + 10, y + 20, 30, 40))
    pygame.draw.circle(screen, GRAY, (x + 25, y + 10), 15)
    pygame.draw.rect(screen, GRAY, (x - 10, y + 20, 20, 30))
    pygame.draw.rect(screen, GRAY, (x + 40, y + 20, 20, 30))

def draw_vehicle(x, y, has_owner=True):
    pygame.draw.polygon(screen, BLUE, [(x, y), (x + 40, y - 20), (x + 80, y), (x + 60, y + 20), (x + 20, y + 20)])
    if has_owner:
        pygame.draw.circle(screen, RED, (x + 40, y - 10), 10)
    pygame.draw.rect(screen, RED, (x + 80, y + 10, 20, 10))

def draw_stone(x, y, color, size):
    pygame.draw.circle(screen, color, (int(x), int(y)), size)

def draw_projectile(x, y, color=YELLOW, size=5):
    pygame.draw.circle(screen, color, (int(x), int(y)), size)

def draw_robot_friend(x, y):
    pygame.draw.circle(screen, BLUE, (int(x + 20), int(y + 20)), 20)
    pygame.draw.rect(screen, BLUE, (x + 10, y + 40, 20, 10))
    pygame.draw.line(screen, WHITE, (x + 20, y + 10), (x + 20, y - 10))

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def check_ball_collision(player_rect):
    destroyed = []
    for obs in obstacles[:]:
        obs_rect = pygame.Rect(obs[0], obs[1], 60, 40)
        if check_collision(player_rect, obs_rect):
            obstacles.remove(obs)
            destroyed.append("Engel")
    for en in enemies[:]:
        en_rect = pygame.Rect(en[0], en[1], 50, 50)
        if check_collision(player_rect, en_rect):
            enemies.remove(en)
            destroyed.append("Canavar")
    for rob in robots[:]:
        rob_rect = pygame.Rect(rob[0] - 10, rob[1], 70, 60)
        if check_collision(player_rect, rob_rect):
            robots.remove(rob)
            destroyed.append("Robot")
    for veh in vehicles[:]:
        veh_rect = pygame.Rect(veh[0], veh[1], 80, 40)
        if check_collision(player_rect, veh_rect):
            vehicles.remove(veh)
            destroyed.append("Araç")
    for stone in falling_stones[:]:
        stone_rect = pygame.Rect(stone[0] - stone[3], stone[1] - stone[3], stone[3]*2, stone[3]*2)
        if check_collision(player_rect, stone_rect):
            falling_stones.remove(stone)
            destroyed.append("Taş")
    for proj in projectiles[:]:
        proj_rect = pygame.Rect(proj[0] - proj[5], proj[1] - proj[5], proj[5]*2, proj[5]*2)
        if check_collision(player_rect, proj_rect):
            projectiles.remove(proj)
            destroyed.append("Fırlatılan taş")
    if destroyed:
        speak(f"{', '.join(destroyed)} patlatıldı.")
        play_beep(1200, 0.15)

def check_spin_collision(player_rect):
    destroyed = []
    for obs in obstacles[:]:
        obs_rect = pygame.Rect(obs[0], obs[1], 60, 40)
        if check_collision(player_rect, obs_rect):
            obstacles.remove(obs)
            destroyed.append("Engel")
    for en in enemies[:]:
        en_rect = pygame.Rect(en[0], en[1], 50, 50)
        if check_collision(player_rect, en_rect):
            enemies.remove(en)
            destroyed.append("Canavar")
    for rob in robots[:]:
        rob_rect = pygame.Rect(rob[0] - 10, rob[1], 70, 60)
        if check_collision(player_rect, rob_rect):
            robots.remove(rob)
            destroyed.append("Robot")
    for veh in vehicles[:]:
        veh_rect = pygame.Rect(veh[0], veh[1], 80, 40)
        if check_collision(player_rect, veh_rect):
            vehicles.remove(veh)
            destroyed.append("Araç")
    for stone in falling_stones[:]:
        stone_rect = pygame.Rect(stone[0] - stone[3], stone[1] - stone[3], stone[3]*2, stone[3]*2)
        if check_collision(player_rect, stone_rect):
            falling_stones.remove(stone)
            destroyed.append("Taş")
    for proj in projectiles[:]:
        proj_rect = pygame.Rect(proj[0] - proj[5], proj[1] - proj[5], proj[5]*2, proj[5]*2)
        if check_collision(player_rect, proj_rect):
            projectiles.remove(proj)
            destroyed.append("Fırlatılan taş")
    if destroyed:
        speak(f"{', '.join(destroyed)} parçalandı.")
        play_beep(1000, 0.1)

def check_bite_collision(player_rect):
    destroyed = []
    for en in enemies[:]:
        en_rect = pygame.Rect(en[0], en[1], 50, 50)
        if check_collision(player_rect, en_rect):
            enemies.remove(en)
            destroyed.append("Canavar")
    for rob in robots[:]:
        rob_rect = pygame.Rect(rob[0] - 10, rob[1], 70, 60)
        if check_collision(player_rect, rob_rect):
            robots.remove(rob)
            destroyed.append("Robot")
    if destroyed:
        speak(f"{', '.join(destroyed)} yendi.")
        play_beep(1100, 0.2)

def give_robot_advice():
    total_enemies = len(enemies) + len(robots)
    advice = random.choice([
        "Dikkat et, düşmanlar yaklaşıyor, yukarı veya aşağı hareket et!",
        "Bir araç bul, onunla düşmanları patlat!",
        f"{total_enemies} düşman var, S ile dön, B ile top ol veya E ile ısır!",
        "Taşlar düşüyor, dikkatli uç!",
        "F ile ateş et, düşmanları uzaktan yok et!",
        "Robotlar peşinde, hızlı hareket et!",
        "Canavarlar taş fırlatabilir, dikkat et!"
    ])
    speak(advice)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 1)
    
    if game_state == STATE_MENU or game_state == STATE_GAME_OVER:
        screen.blit(font.render("Oyuna Başla - Enter Bas", True, GREEN), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100))
        screen.blit(font.render("Çıkış - Escape Bas", True, RED), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
        if game_state == STATE_MENU:
            speak("Hoş geldin. Oyuna başla için enter, çıkış için escape bas. Kontroller: Yukarı aşağı ok tuşları hareket, space zıpla ve uç, F ateş et araçtayken, S dönerek tokatla, B top olup patlat, E ısır.")
        else:
            speak("Oyun bitti. Tekrar oynamak için enter, çıkmak için escape bas.")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING
                    speak("Oyun başladı.")
                    play_beep(880, 0.2)
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_EXIT_CONFIRM
                    speak("Çıkmak istiyor musunuz? Evet için Y, hayır için N bas.")
    
    elif game_state == STATE_EXIT_CONFIRM:
        screen.blit(font.render("Çıkmak istiyor musunuz?", True, WHITE), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100))
        screen.blit(font.render("Evet - Y Bas", True, GREEN), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
        screen.blit(font.render("Hayır - N Bas", True, RED), (SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 - 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    running = False
                    speak("Oyun kapanıyor.")
                if event.key == pygame.K_n:
                    game_state = STATE_MENU if game_state == STATE_MENU else STATE_GAME_OVER
                    speak("Çıkış iptal edildi.")
    
    elif game_state == STATE_PAUSED:
        screen.blit(font.render("Mola Verildi - Oyun Duraklatıldı", True, YELLOW), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
        screen.blit(font.render("Devam Et - P Bas", True, GREEN), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 10))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_state = STATE_PLAYING
                    speak("Mola bitti, oyun başladı.")
                    play_beep(880, 0.2)
    
    elif game_state == STATE_PLAYING:
        screen.blit(font.render("Mola - P Bas", True, YELLOW), (pause_button.x + 10, pause_button.y + 5))
        
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not player_flying and not player_is_ball:
                        player_velocity_y = player_jump_speed
                    player_flying = True
                    speak("Zıplama.")
                if event.key == pygame.K_f and player_in_vehicle:
                    proj_x = player_x + 100
                    proj_y = player_y + 15
                    player_projectiles.append([proj_x, proj_y, player_projectile_speed, 0])
                    speak("Ateş edildi.")
                    play_beep(660, 0.1)
                if event.key == pygame.K_s and spin_cooldown <= 0 and len(enemies) + len(robots) >= SPIN_THRESHOLD and not player_is_ball:
                    player_spinning = True
                    spin_timer = spin_duration
                    spin_cooldown = SPIN_COOLDOWN_MAX
                    speak("Dönerek tokat atıldı.")
                    play_beep(770, 0.2)
                if event.key == pygame.K_b and ball_cooldown_timer <= 0 and not player_in_vehicle:
                    player_is_ball = True
                    ball_timer = ball_duration
                    ball_cooldown_timer = ball_cooldown
                    player_velocity_y = player_jump_speed
                    speak("Top oldun, düşmanların üzerine düş!")
                    play_beep(900, 0.2)
                if event.key == pygame.K_e and bite_cooldown <= 0 and not player_is_ball and not player_in_vehicle:
                    bite_cooldown = BITE_COOLDOWN_MAX
                    check_bite_collision(pygame.Rect(player_x - 20, player_y - 20, player_size + 40, player_size + 40))
                    speak("Isırdın!")
                    play_beep(1100, 0.2)
                if event.key == pygame.K_p:
                    game_state = STATE_PAUSED
                    speak("Mola verildi, oyun duraklatıldı. Devam için P bas.")
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player_flying = False
        
        speed_multiplier = vehicle_boost if player_in_vehicle else 1
        if keys[pygame.K_UP] and not player_is_ball:
            player_y -= player_speed_y * speed_multiplier
        if keys[pygame.K_DOWN] and not player_is_ball:
            player_y += player_speed_y * speed_multiplier
        
        if player_flying or player_is_ball:
            player_y += player_velocity_y
            player_velocity_y += player_gravity / 2
        else:
            player_y += player_velocity_y
            player_velocity_y += player_gravity
        
        if player_y > SCREEN_HEIGHT - player_size:
            player_y = SCREEN_HEIGHT - player_size
            player_velocity_y = 0
        if player_y < 0:
            player_y = 0
            player_velocity_y = 0
        
        if player_spinning:
            spin_timer -= 1
            if spin_timer <= 0:
                player_spinning = False
        if spin_cooldown > 0:
            spin_cooldown -= 1
        
        if player_is_ball:
            ball_timer -= 1
            if ball_timer <= 0:
                player_is_ball = False
                speak("Top formu bitti, normal forma döndün.")
                play_beep(600, 0.1)
        if ball_cooldown_timer > 0:
            ball_cooldown_timer -= 1
        
        if bite_cooldown > 0:
            bite_cooldown -= 1
        
        robot_friend_y = player_y
        draw_robot_friend(robot_friend_x, robot_friend_y)
        robot_friend_advice_timer += 1
        if robot_friend_advice_timer >= ADVICE_INTERVAL:
            give_robot_advice()
            robot_friend_advice_timer = 0
        
        draw_player(player_x, player_y, player_in_vehicle, player_spinning, player_is_ball)
        player_rect = pygame.Rect(player_x - 20, player_y - 20, player_size + 40, player_size + 40) if (player_spinning or player_is_ball) else pygame.Rect(player_x, player_y, player_size, player_size)
        
        if player_spinning:
            check_spin_collision(player_rect)
        if player_is_ball:
            check_ball_collision(player_rect)
        
        frame_count += 1
        if frame_count >= spawn_rate:
            rand = random.random()
            if rand < 0.3:
                obs_y = random.randint(0, SCREEN_HEIGHT - 50)
                obstacles.append([SCREEN_WIDTH, obs_y])
                speak("Engel yaklaşıyor.")
            elif rand < 0.5:
                en_y = random.randint(0, SCREEN_HEIGHT - 50)
                enemies.append([SCREEN_WIDTH, en_y, 0])
                speak("Canavar yaklaşıyor.")
                play_beep(220, 0.3)
            elif rand < 0.7:
                rob_y = random.randint(0, SCREEN_HEIGHT - 50)
                robots.append([SCREEN_WIDTH, rob_y])
                speak("Robot yaklaşıyor.")
            else:
                veh_y = random.randint(0, SCREEN_HEIGHT - 50)
                has_owner = random.random() < 0.5
                vehicles.append([SCREEN_WIDTH, veh_y, has_owner, False])
                speak("Uzay aracı yaklaşıyor.")
            frame_count = 0
            spawn_rate = max(20, spawn_rate - 1)
            obstacle_speed += 0.01
            enemy_speed += 0.01
            robot_speed += 0.01
            vehicle_speed += 0.01
        
        for obs in obstacles[:]:
            obs[0] -= obstacle_speed
            draw_obstacle(obs[0], obs[1])
            obs_rect = pygame.Rect(obs[0], obs[1], 60, 40)
            if check_collision(player_rect, obs_rect):
                if player_in_vehicle or player_is_ball:
                    obstacles.remove(obs)
                    speak("Engel parçalandı." if player_in_vehicle else "Engel patlatıldı.")
                else:
                    game_state = STATE_GAME_OVER
                    speak("Çarpışma, oyun bitti.")
            if obs[0] < -60:
                obstacles.remove(obs)
        
        fo