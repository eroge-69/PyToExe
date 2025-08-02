import pygame
import random
import os

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Sounds ---
nextLoopSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","beep.wav"))
boostCatchSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","beep.wav"))
loopCatchSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","loopSound.wav"))
hitSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","crash.wav"))
gameOverSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","gameover.wav"))
buttonPressSound = pygame.mixer.Sound(os.path.join("GMTK Game Jam 2025","Assets","buttonpress.wav"))
music = pygame.mixer.music.load(os.path.join("GMTK Game Jam 2025","Assets","BGMusic.wav"))
pygame.mixer.music.play(-1)
def draw_text(surface, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("comicsans", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

# --- Images ---
ASTEROID = pygame.image.load(os.path.join("GMTK Game Jam 2025","Assets","Asteroid_Brown.png")).convert_alpha()
ASTEROID = pygame.transform.scale(ASTEROID,(64,64))
BG = pygame.image.load(os.path.join("GMTK Game Jam 2025","Assets","bg.jpg"))
SHIP = pygame.image.load(os.path.join("GMTK Game Jam 2025","Assets","player.png")).convert_alpha()
SHIP = pygame.transform.scale(SHIP,(56,100))  # Rounded sizes

# Create speed boost and loop images (use simple circles if you don't have images)
BOOST_IMG = pygame.image.load(os.path.join("GMTK Game Jam 2025","Assets","SpeedBoost.png"))
BOOST_IMG = pygame.transform.scale(BOOST_IMG,(50,50))  # Cyan circle for boost

LOOP_IMG = pygame.image.load(os.path.join("GMTK Game Jam 2025","Assets","Loop.png"))
LOOP_IMG = pygame.transform.scale(LOOP_IMG,(50,70))

# --- Game Variables ---
FPS = 60
SHIP_SPEED = 5
OBSTACLE_SPEED = 3
LOOP_TIME = 7  # seconds per loop

game_state = "main_menu"
loop_timer = LOOP_TIME * FPS
loop_count = 1
score = 0
lives = 1
loops_collected = 0

# Speed boost variables
boost_active = False
boost_start_time = 0

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 200)

# --- Player ---
ship_rect = SHIP.get_rect(center=(WIDTH // 2, HEIGHT - 50))

# --- Objects ---
obstacles = []   # List of dicts: {"rect":..., "img":..., "angle":...}
boosts = []      # List of pygame.Rect for boosts
loops = []       # List of pygame.Rect for loops

OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40  # Use square for asteroids for simplicity

# --- Functions ---

def spawn_obstacle():
    global loop_count
    # X-position depends on loop count, clamp to screen bounds
    x_min = max(0, ship_rect.x - 70)
    x_max = min(WIDTH - OBSTACLE_WIDTH, ship_rect.x + 70)

    if loop_count <= 2:
        x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
    elif loop_count > 13:
        x = random.randint(max(0, ship_rect.x - 45), min(WIDTH - OBSTACLE_WIDTH, ship_rect.x + 45))
    elif loop_count > 11:
        x = random.randint(max(0, ship_rect.x - 55), min(WIDTH - OBSTACLE_WIDTH, ship_rect.x + 55))
    elif loop_count > 8:
        x = random.randint(max(0, ship_rect.x - 70), min(WIDTH - OBSTACLE_WIDTH, ship_rect.x + 70))
    elif loop_count > 5:
        x = random.randint(max(0, ship_rect.x - 100), min(WIDTH - OBSTACLE_WIDTH, ship_rect.x + 100))
    else:
        x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        
    obstacle = {
        "rect": pygame.Rect(x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
        "img": ASTEROID,
        "angle": random.randint(0, 360)  # optional rotation
    }
    obstacles.append(obstacle)

def restart_game():
    global ship_rect, score, loop_count, obstacles, game_state, LOOP_TIME
    global lives, loops_collected, boosts, loops, OBSTACLE_SPEED, SHIP_SPEED
    global boost_active, boost_start_time
    buttonPressSound.play()
    
    ship_rect = SHIP.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    score = 0
    loop_count = 1
    LOOP_TIME = 7
    obstacles = []
    boosts = []
    loops = []
    game_state = "playing"
    lives = 1
    loops_collected = 0
    OBSTACLE_SPEED = 3
    SHIP_SPEED = 5
    boost_active = False
    boost_start_time = 0
def draw_main_menu():
    screen.blit(BG, (0, 0))
    draw_text(screen, "Wormhole Rush", 60, WIDTH // 2, HEIGHT // 2 - 100)
    
    # Draw start button
    global start_button
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, (50, 200, 100), start_button)
    draw_text(screen, "Start Game", 36, WIDTH // 2, HEIGHT // 2 + 25)
    
   
    draw_text(screen, "Arrow Keys or WASD. Avoid Asteroids,", 18, WIDTH // 2, HEIGHT // 2 + 100)
    draw_text(screen, "Grab All Loops. You gain a life for every 5 loops collected.", 18, WIDTH // 2, HEIGHT // 2 + 130)
    draw_text(screen,"Speed Boosts cost 15 points/dodges. Loops give 5.", 18, WIDTH // 2, HEIGHT // 2 + 160)
    draw_text(screen,"Lose 2 lives for missed loops.", 18, WIDTH // 2, HEIGHT // 2 + 190)
    draw_text(screen,"Lose 1 for getting hit by asteroids.", 18, WIDTH // 2, HEIGHT // 2 + 220)
# --- Game Loop ---
running = True
spawn_cooldown = 0
font = pygame.font.SysFont("comicsans", 20)
font1 = pygame.font.SysFont("comicsans", 50)

while running:
    clock.tick(FPS)
    screen.blit(BG, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "main_menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(pygame.mouse.get_pos()):
                    restart_game()  # start game from beginning

        if game_state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_again_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)
                if play_again_button.collidepoint(pygame.mouse.get_pos()):
                    game_state = "playing"
                    restart_game()
                elif main_menu_button.collidepoint(pygame.mouse.get_pos()):
                    game_state = "main_menu"                    
    keys = pygame.key.get_pressed()
    if game_state == "playing":
        # Handle player movement with current speed
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and ship_rect.left > 0:
            ship_rect.x -= SHIP_SPEED
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and ship_rect.right < WIDTH:
            ship_rect.x += SHIP_SPEED

        # Loop timer countdown
        loop_timer -= 1
        if loop_timer <= 0:
            loop_count += 1
            loop_timer = LOOP_TIME * FPS
            OBSTACLE_SPEED += 1  # increase difficulty each loop
            nextLoopSound.play()

        # Spawn logic: 75% asteroid, 15% boost, 10% loop
        spawn_cooldown -= 1
        if spawn_cooldown <= 0:
            spawn_chance = random.random()
            x_pos = random.randint(50, WIDTH - 50)
            if spawn_chance < 0.75:
                # Asteroid
                spawn_obstacle()
            elif spawn_chance < 0.90:
                # Speed boost
                boost_rect = BOOST_IMG.get_rect(center=(x_pos, -30))
                boosts.append(boost_rect)
            else:
                # Loop
                loop_rect = LOOP_IMG.get_rect(center=(x_pos, -30))
                loops.append(loop_rect)
            spawn_cooldown = max(15, 60 - loop_count * 2)  # faster spawns as loops increase

        # Update obstacles
        for ob in obstacles[:]:
            ob["rect"].y += OBSTACLE_SPEED
            if ob["rect"].colliderect(ship_rect):
                hitSound.play()
                lives -= 1
                obstacles.remove(ob)
                if lives <= 0:
                    game_state = "game_over"
                    gameOverSound.play()
            elif ob["rect"].y > HEIGHT:
                obstacles.remove(ob)
                score += 1  # survived obstacle

        # Update boosts
        for boost in boosts[:]:
            boost.y += OBSTACLE_SPEED
            if boost.colliderect(ship_rect) and score >= 15:
                boosts.remove(boost)
                boost_active = True
                boost_start_time = pygame.time.get_ticks()
                SHIP_SPEED = 7
                score = max(0, score - 15)
                boostCatchSound.play()
            elif boost.y > HEIGHT:
                boosts.remove(boost)

        # Update loops
        for loop in loops[:]:
            loop.y += OBSTACLE_SPEED
            if loop.colliderect(ship_rect):
                loops.remove(loop)
                score += 5
                loops_collected += 1
                loopCatchSound.play()
                if loops_collected % 5 == 0:
                    lives += 1
            elif loop.y > HEIGHT:
                loops.remove(loop)
                lives -= 2
                if lives <= 0:
                    game_state = "game_over"
                    gameOverSound.play()

        # Handle speed boost duration (20 seconds)
        if boost_active:
            elapsed = pygame.time.get_ticks() - boost_start_time
            if elapsed >= 20000:
                SHIP_SPEED = 5
                boost_active = False

    # Draw all
    if game_state == "playing":
        # Draw ship
        screen.blit(SHIP, ship_rect)

        # Draw obstacles (with rotation)
        for ob in obstacles:
            rotated_img = pygame.transform.rotate(ob["img"], ob["angle"])
            rotated_rect = rotated_img.get_rect(center=ob["rect"].center)
            screen.blit(rotated_img, rotated_rect.topleft)
            ob["angle"] += 2  # rotate

        # Draw boosts
        for boost in boosts:
            screen.blit(BOOST_IMG, boost)

        # Draw loops
        for loop in loops:
            screen.blit(LOOP_IMG, loop)

        # Draw HUD
        draw_text(screen, f"Loop: {loop_count}", 24, 60, 20)
        draw_text(screen, f"Score: {score}", 24, 60, 50)
        draw_text(screen, f"Lives: {lives}", 24, WIDTH - 80, 20)
        draw_text(screen, f"Loops Collected: {loops_collected}", 24, WIDTH - 120, 50)

    elif game_state == "game_over":
        draw_text(screen, f"You reached loop {loop_count}!", 48, WIDTH // 2, HEIGHT // 2 - 60)
        draw_text(screen, f"Score: {score}", 36, WIDTH // 2, HEIGHT // 2 - 10)
        play_again_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)
        pygame.draw.rect(screen, (50, 150, 250), play_again_button)
        draw_text(screen, "Play Again", 32, WIDTH//2, HEIGHT//2+60 )
        main_menu_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50)
        pygame.draw.rect(screen, (200, 100, 100), main_menu_button)
        draw_text(screen, "Main Menu", 32, WIDTH//2, HEIGHT//2 + 135)
        
    if game_state == "main_menu":
        draw_main_menu()
        
    pygame.display.flip()

pygame.quit()
