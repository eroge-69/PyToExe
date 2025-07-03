import pygame
import random
import sys
import time
import math

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
pygame.display.set_caption("Dodge the Falling Blocks")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
GREEN = (40, 180, 90)
YELLOW = (255, 220, 50)
GOLD = (255, 215, 0)
GREEN_BLOCK = (60, 255, 60)
PURPLE = (140, 70, 200)
CYAN = (50, 220, 220)
TITLE_FONT = pygame.font.SysFont("arialblack", 64)
BUTTON_FONT = pygame.font.SysFont("arial", 48)
SCORE_FONT = pygame.font.SysFont("arial", 36)

PLAYER_SIZE = (80, 100)
OBSTACLE_SIZE = (80, 80)
BASE_PLAYER_SPEED = 10
OBSTACLE_SPEED = 7
HIGHSCORE_FILE = "high_score.txt"

BASE_SPEED_COST = 50
BASE_SHIELD_COST = 100
BASE_SHOCKWAVE_COST = 200
BASE_DOUBLE_COINS_COST = 150
BASE_EXTRA_LIFE_COST = 120
BASE_VERTICAL_MOVE_COST = 180

# Difficulty scaling constants
DIFFICULTY_INTERVAL = 300      # Increase difficulty every 300 score points
SPEED_INCREMENT = 1            # How much to increase obstacle speed each interval
SPAWN_CHANCE_INCREMENT = 2     # How much to increase spawn chance each interval

class Shockwave:
    def __init__(self, center, color=(0, 200, 255), max_radius=None, duration=30):
        self.center = center
        self.color = color
        self.max_radius = max_radius if max_radius else int(1.5 * max(WIDTH, HEIGHT))
        self.duration = duration
        self.frame = 0
        self.alive = True

    def update(self):
        self.frame += 1
        if self.frame >= self.duration:
            self.alive = False

    @property
    def radius(self):
        return int(self.max_radius * (self.frame / self.duration))

    def draw(self, surface):
        if not self.alive:
            return
        alpha = max(0, 180 - int(180 * (self.frame / self.duration)))
        if self.radius > 0:
            shock_surf = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(
                shock_surf,
                (*self.color, alpha),
                (self.max_radius, self.max_radius),
                self.radius,
                width=24
            )
            surf_rect = shock_surf.get_rect(center=self.center)
            surface.blit(shock_surf, surf_rect)

    def collides(self, rect):
        cx, cy = rect.center
        dx = cx - self.center[0]
        dy = cy - self.center[1]
        return dx*dx + dy*dy <= self.radius*self.radius

def load_high_score():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

def draw_text_center(text, font, color, surface, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH//2, y))
    surface.blit(rendered, rect)
    return rect

def draw_button(text, font, color, surface, center, width=300, height=80, hover=False, owned=False, outline=BLACK):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = center
    if owned:
        bg_color = GREEN
    elif hover:
        bg_color = YELLOW
    else:
        bg_color = WHITE
    pygame.draw.rect(surface, bg_color, rect, border_radius=18)
    pygame.draw.rect(surface, outline, rect, 4, border_radius=18)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return rect

def main_menu(high_score, coins):
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text_center("Dodge the Blocks", TITLE_FONT, WHITE, screen, HEIGHT//6)
        draw_text_center(f"High Score: {high_score}", SCORE_FONT, BLUE, screen, HEIGHT//6 + 70)
        draw_text_center(f"Coins: {coins}", SCORE_FONT, GREEN, screen, HEIGHT//6 + 120)

        mx, my = pygame.mouse.get_pos()
        play_btn = draw_button("Play", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2 - 100),
                               hover=pygame.Rect(WIDTH//2-150, HEIGHT//2-140, 300, 80).collidepoint((mx, my)))
        upgrade_btn = draw_button("Upgrades", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2),
                                  hover=pygame.Rect(WIDTH//2-150, HEIGHT//2-40, 300, 80).collidepoint((mx, my)))
        customize_btn = draw_button("Customize", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2 + 100),
                                  hover=pygame.Rect(WIDTH//2-150, HEIGHT//2+60, 300, 80).collidepoint((mx, my)))
        quit_btn = draw_button("Quit", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2 + 200),
                               hover=pygame.Rect(WIDTH//2-150, HEIGHT//2+160, 300, 80).collidepoint((mx, my)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return "play"
                elif upgrade_btn.collidepoint(event.pos):
                    return "upgrades"
                elif customize_btn.collidepoint(event.pos):
                    return "customize"
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

def customize_menu(player_color):
    clock = pygame.time.Clock()
    color_options = [
        ("Blue", (50, 100, 220)),
        ("Green", (40, 180, 90)),
        ("Yellow", (255, 220, 50)),
        ("Purple", (140, 70, 200)),
        ("Cyan", (50, 220, 220)),
        ("White", (230, 230, 230)),
    ]
    selected_color = 0
    for i, (_, color) in enumerate(color_options):
        if color == player_color:
            selected_color = i

    while True:
        screen.fill(BLACK)
        draw_text_center("Customize Player", TITLE_FONT, WHITE, screen, HEIGHT//10)
        y_start = HEIGHT//4
        draw_text_center("Color", SCORE_FONT, WHITE, screen, y_start)
        for i, (name, color) in enumerate(color_options):
            rect = pygame.Rect(WIDTH//2 - 120, y_start + 30 + i*60, 240, 44)
            pygame.draw.rect(screen, color, rect, border_radius=18)
            if i == selected_color:
                pygame.draw.rect(screen, YELLOW, rect, 5, border_radius=18)
            text = SCORE_FONT.render(name, True, BLACK if sum(color) > 400 else WHITE)
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

        back_btn = draw_button("Back", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT - 120), width=300, height=80,
                               hover=pygame.Rect(WIDTH//2-150, HEIGHT-160, 300, 80).collidepoint(pygame.mouse.get_pos()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_color > 0:
                    selected_color -= 1
                elif event.key == pygame.K_DOWN and selected_color < len(color_options) - 1:
                    selected_color += 1
                elif event.key == pygame.K_RETURN:
                    return color_options[selected_color][1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (name, color) in enumerate(color_options):
                    rect = pygame.Rect(WIDTH//2 - 120, y_start + 30 + i*60, 240, 44)
                    if rect.collidepoint(event.pos):
                        selected_color = i
                if back_btn.collidepoint(event.pos):
                    return color_options[selected_color][1]
        pygame.display.flip()
        clock.tick(60)

# upgrades_menu, pause_menu, game_over_screen remain unchanged

def upgrades_menu(coins, speed_level, shield, shockwave, double_coins, extra_life, vertical_move,
                  speed_cost, shield_cost, shockwave_cost, double_coins_cost, extra_life_cost, vertical_move_cost):
    clock = pygame.time.Clock()
    info = ""
    upgrades = [
        ("Speed +", speed_cost, "speed", False),
        ("Shield", shield_cost, "shield", shield),
        ("Shockwave", shockwave_cost, "shockwave", shockwave),
        ("Double Coins", double_coins_cost, "double_coins", double_coins),
        ("Extra Life", extra_life_cost, "extra_life", extra_life),
        ("Vertical Move", vertical_move_cost, "vertical_move", vertical_move)
    ]
    btn_width = 320
    btn_height = 90
    btn_gap_x = 60
    btn_gap_y = 40
    upgrades_per_row = 3
    rows = (len(upgrades) + upgrades_per_row - 1) // upgrades_per_row
    total_row_width = upgrades_per_row * btn_width + (upgrades_per_row - 1) * btn_gap_x
    start_y = HEIGHT//2 - (rows * btn_height + (rows - 1) * btn_gap_y)//2 + btn_height//2

    while True:
        screen.fill(BLACK)
        draw_text_center("Upgrades", TITLE_FONT, WHITE, screen, HEIGHT//6)
        draw_text_center(f"Coins: {coins}", SCORE_FONT, GREEN, screen, HEIGHT//6 + 60)

        mx, my = pygame.mouse.get_pos()
        btns = []
        for i, (name, cost, key, owned) in enumerate(upgrades):
            row = i // upgrades_per_row
            col = i % upgrades_per_row
            row_y = start_y + row * (btn_height + btn_gap_y)
            row_x = WIDTH//2 - total_row_width//2 + col * (btn_width + btn_gap_x) + btn_width//2
            label = f"{name} ({cost}c)"
            hover = pygame.Rect(row_x - btn_width//2, row_y - btn_height//2, btn_width, btn_height).collidepoint((mx, my))
            btn = draw_button(label, SCORE_FONT, BLACK, screen, (row_x, row_y), width=btn_width, height=btn_height, hover=hover, owned=owned)
            btns.append((btn, key))

        back_btn = draw_button("Back", BUTTON_FONT, BLACK, screen, (WIDTH//2, start_y + rows * (btn_height + btn_gap_y)), width=300, height=80,
                               hover=pygame.Rect(WIDTH//2-150, start_y + rows * (btn_height + btn_gap_y)-40, 300, 80).collidepoint((mx, my)))

        if info:
            draw_text_center(info, SCORE_FONT, RED, screen, start_y + rows * (btn_height + btn_gap_y) + 210)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for idx, (btn, key) in enumerate(btns):
                    if btn.collidepoint(event.pos):
                        if key == "speed":
                            if coins >= speed_cost:
                                coins -= speed_cost
                                speed_level += 1
                                speed_cost = int(BASE_SPEED_COST * (1.5 ** (speed_level - 1)))
                                upgrades[0] = ("Speed +", speed_cost, "speed", False)
                                info = "Speed upgraded!"
                            else:
                                info = "Not enough coins!"
                        elif key == "shield":
                            if shield:
                                info = "Already have shield!"
                            elif coins >= shield_cost:
                                coins -= shield_cost
                                shield = True
                                upgrades[1] = ("Shield", shield_cost, "shield", True)
                                info = "Shield purchased!"
                            else:
                                info = "Not enough coins!"
                        elif key == "shockwave":
                            if shockwave:
                                info = "Already have shockwave!"
                            elif coins >= shockwave_cost:
                                coins -= shockwave_cost
                                shockwave = True
                                upgrades[2] = ("Shockwave", shockwave_cost, "shockwave", True)
                                info = "Shockwave purchased!"
                            else:
                                info = "Not enough coins!"
                        elif key == "double_coins":
                            if double_coins:
                                info = "Already have double coins!"
                            elif coins >= double_coins_cost:
                                coins -= double_coins_cost
                                double_coins = True
                                upgrades[3] = ("Double Coins", double_coins_cost, "double_coins", True)
                                info = "Double coins purchased!"
                            else:
                                info = "Not enough coins!"
                        elif key == "extra_life":
                            if extra_life:
                                info = "Already have extra life!"
                            elif coins >= extra_life_cost:
                                coins -= extra_life_cost
                                extra_life = True
                                upgrades[4] = ("Extra Life", extra_life_cost, "extra_life", True)
                                info = "Extra life purchased!"
                            else:
                                info = "Not enough coins!"
                        elif key == "vertical_move":
                            if vertical_move:
                                info = "Already have vertical movement!"
                            elif coins >= vertical_move_cost:
                                coins -= vertical_move_cost
                                vertical_move = True
                                upgrades[5] = ("Vertical Move", vertical_move_cost, "vertical_move", True)
                                info = "Vertical movement purchased!"
                            else:
                                info = "Not enough coins!"
                if back_btn.collidepoint(event.pos):
                    return coins, speed_level, shield, shockwave, double_coins, extra_life, vertical_move, speed_cost, shield_cost, shockwave_cost, double_coins_cost, extra_life_cost, vertical_move_cost

        pygame.display.flip()
        clock.tick(60)

def pause_menu():
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text_center("Paused", TITLE_FONT, WHITE, screen, HEIGHT//3)
        mx, my = pygame.mouse.get_pos()
        resume_btn = draw_button("Resume", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2 - 60), width=300, height=80,
                                hover=pygame.Rect(WIDTH//2-150, HEIGHT//2-100, 300, 80).collidepoint((mx, my)))
        menu_btn = draw_button("Main Menu", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//2 + 60), width=300, height=80,
                              hover=pygame.Rect(WIDTH//2-150, HEIGHT//2+20, 300, 80).collidepoint((mx, my)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_btn.collidepoint(event.pos):
                    return "resume"
                elif menu_btn.collidepoint(event.pos):
                    return "menu"
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(score, high_score, new_high, coins_earned, coins):
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text_center("Game Over!", TITLE_FONT, RED, screen, HEIGHT//3)
        draw_text_center(f"Score: {score}", SCORE_FONT, WHITE, screen, HEIGHT//3 + 80)
        draw_text_center(f"High Score: {high_score}", SCORE_FONT, BLUE, screen, HEIGHT//3 + 130)
        draw_text_center(f"Coins: +{coins_earned} (Total: {coins})", SCORE_FONT, GREEN, screen, HEIGHT//3 + 180)
        if new_high:
            draw_text_center("New High Score!", SCORE_FONT, RED, screen, HEIGHT//3 + 230)

        mx, my = pygame.mouse.get_pos()
        menu_btn = draw_button("Main Menu", BUTTON_FONT, BLACK, screen, (WIDTH//2, HEIGHT//3 + 320), width=300, height=80,
                               hover=pygame.Rect(WIDTH//2-150, HEIGHT//3+280, 300, 80).collidepoint((mx, my)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    return

        pygame.display.flip()
        clock.tick(60)

def game_loop(high_score, player_speed, shield_owned, shockwave_owned, double_coins, extra_life, vertical_move, player_color):
    clock = pygame.time.Clock()
    player_x = WIDTH // 2 - PLAYER_SIZE[0] // 2
    player_y = HEIGHT - PLAYER_SIZE[1] - 30
    obstacles = []
    gold_blocks = []
    green_blocks = []
    score = 0
    running = True
    game_over = False
    shield_active = shield_owned
    shield_used = False
    extra_life_used = False
    invincible = False
    invincible_time = 0
    shockwave_ready = shockwave_owned

    # Difficulty scaling variables
    obstacle_speed = OBSTACLE_SPEED
    spawn_chance = 20  # Lower is harder (was 20 originally)
    last_difficulty_increase = 0

    shockwave_cooldown = 30000
    last_shockwave_time = -shockwave_cooldown
    shockwaves = []
    coins_gained = 0

    while running:
        screen.fill(BLACK)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_result = pause_menu()
                    if pause_result == "menu":
                        return "menu"
                if (shockwave_ready and event.key == pygame.K_SPACE and
                    now - last_shockwave_time >= shockwave_cooldown):
                    last_shockwave_time = now
                    player_rect = pygame.Rect(player_x, player_y, *PLAYER_SIZE)
                    shockwaves.append(Shockwave(player_rect.center))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
            player_x -= player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < WIDTH - PLAYER_SIZE[0]:
            player_x += player_speed
        if vertical_move:
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_y > 0:
                player_y -= player_speed
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_y < HEIGHT - PLAYER_SIZE[1]:
                player_y += player_speed

        # Difficulty scaling: increase speed and spawn rate as score increases
        if score // DIFFICULTY_INTERVAL > last_difficulty_increase:
            last_difficulty_increase = score // DIFFICULTY_INTERVAL
            obstacle_speed += SPEED_INCREMENT
            spawn_chance = max(5, spawn_chance - SPAWN_CHANCE_INCREMENT)  # Don't go below 5

        for _ in range(1):
            if random.randint(1, spawn_chance) == 1:
                x_pos = random.randint(0, WIDTH - OBSTACLE_SIZE[0])
                obstacles.append(pygame.Rect(x_pos, 0, *OBSTACLE_SIZE))

        if random.randint(1, 160) == 1:
            x_pos = random.randint(0, WIDTH - OBSTACLE_SIZE[0])
            gold_blocks.append(pygame.Rect(x_pos, 0, *OBSTACLE_SIZE))

        if extra_life and random.randint(1, 200) == 1:
            x_pos = random.randint(0, WIDTH - OBSTACLE_SIZE[0])
            green_blocks.append(pygame.Rect(x_pos, 0, *OBSTACLE_SIZE))

        for obs in obstacles:
            obs.y += obstacle_speed
        for gold in gold_blocks:
            gold.y += obstacle_speed
        for green in green_blocks:
            green.y += obstacle_speed

        obstacles = [obs for obs in obstacles if obs.y < HEIGHT]
        gold_blocks = [gold for gold in gold_blocks if gold.y < HEIGHT]
        green_blocks = [green for green in green_blocks if green.y < HEIGHT]

        player_rect = pygame.Rect(player_x, player_y, *PLAYER_SIZE)
        if invincible:
            pygame.draw.rect(screen, YELLOW, player_rect.inflate(12, 12), border_radius=18)
        pygame.draw.rect(screen, player_color, player_rect, border_radius=12)

        for obs in obstacles:
            pygame.draw.rect(screen, RED, obs, border_radius=12)
        for gold in gold_blocks:
            pygame.draw.rect(screen, GOLD, gold, border_radius=12)
        for green in green_blocks:
            pygame.draw.rect(screen, GREEN_BLOCK, green, border_radius=12)

        score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
        high_score_text = SCORE_FONT.render(f"High Score: {high_score}", True, BLUE)
        screen.blit(score_text, (20, 20))
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 20, 20))
        if shield_active and not shield_used:
            shield_text = SCORE_FONT.render("Shield: ON", True, GREEN)
            screen.blit(shield_text, (20, 70))
        if extra_life and not extra_life_used:
            el_text = SCORE_FONT.render("Extra Life: ON", True, GREEN)
            screen.blit(el_text, (20, 120))
        if invincible:
            inv_text = SCORE_FONT.render("Invincible!", True, YELLOW)
            screen.blit(inv_text, (20, 170))

        if shockwave_ready:
            cd = max(0, (shockwave_cooldown - (now - last_shockwave_time)) // 1000)
            if cd == 0:
                sw_text = SCORE_FONT.render("Shockwave: SPACE", True, WHITE)
            else:
                sw_text = SCORE_FONT.render(f"Shockwave: {cd}s", True, YELLOW)
            screen.blit(sw_text, (20, 220))

        for shock in shockwaves[:]:
            shock.update()
            shock.draw(screen)
            obstacles = [obs for obs in obstacles if not shock.collides(obs)]
            gold_blocks = [gold for gold in gold_blocks if not shock.collides(gold)]
            green_blocks = [green for green in green_blocks if not shock.collides(green)]
            if not shock.alive:
                shockwaves.remove(shock)

        if invincible and time.time() - invincible_time > 3:
            invincible = False

        for obs in obstacles:
            if player_rect.colliderect(obs):
                if shield_active and not shield_used:
                    shield_used = True
                    invincible = True
                    invincible_time = time.time()
                    obstacles.remove(obs)
                    shield_active = False
                    break
                elif extra_life and not extra_life_used and not invincible:
                    extra_life_used = True
                    invincible = True
                    invincible_time = time.time()
                    obstacles.remove(obs)
                    break
                elif invincible:
                    continue
                else:
                    game_over = True
                    running = False

        for gold in gold_blocks[:]:
            if player_rect.colliderect(gold):
                coins_gained += 10
                gold_blocks.remove(gold)

        for green in green_blocks[:]:
            if player_rect.colliderect(green):
                if extra_life and extra_life_used:
                    extra_life_used = False
                    green_blocks.remove(green)
                else:
                    green_blocks.remove(green)

        if not game_over:
            score += 1

        pygame.display.flip()
        clock.tick(60)

    new_high = False
    if score > high_score:
        save_high_score(score)
        high_score = score
        new_high = True

    coins_earned = score // 10
    if double_coins:
        coins_earned *= 2
    coins_earned += coins_gained

    return score, high_score, new_high, coins_earned

def main():
    high_score = load_high_score()
    coins = 0
    speed_level = 1
    player_speed = BASE_PLAYER_SPEED
    shield = False
    shockwave = False
    double_coins = False
    extra_life = False
    vertical_move = False
    speed_cost = BASE_SPEED_COST
    shield_cost = BASE_SHIELD_COST
    shockwave_cost = BASE_SHOCKWAVE_COST
    double_coins_cost = BASE_DOUBLE_COINS_COST
    extra_life_cost = BASE_EXTRA_LIFE_COST
    vertical_move_cost = BASE_VERTICAL_MOVE_COST
    player_color = (50, 100, 220)  # Default blue

    while True:
        menu_choice = main_menu(high_score, coins)
        if menu_choice == "play":
            player_speed = BASE_PLAYER_SPEED + (speed_level - 1) * 2
            result = game_loop(
                high_score, player_speed, shield, shockwave, double_coins, extra_life, vertical_move, player_color
            )
            if result == "menu":
                continue  # Go back to main menu safely
            score, high_score, new_high, coins_earned = result
            coins += coins_earned
            shield = False
            shockwave = shockwave
            double_coins = double_coins
            extra_life = extra_life
            vertical_move = vertical_move
            game_over_screen(score, high_score, new_high, coins_earned, coins)
        elif menu_choice == "upgrades":
            coins, speed_level, shield, shockwave, double_coins, extra_life, vertical_move, speed_cost, shield_cost, shockwave_cost, double_coins_cost, extra_life_cost, vertical_move_cost = upgrades_menu(
                coins, speed_level, shield, shockwave, double_coins, extra_life, vertical_move,
                speed_cost, shield_cost, shockwave_cost, double_coins_cost, extra_life_cost, vertical_move_cost
            )
        elif menu_choice == "customize":
            player_color = customize_menu(player_color)

if __name__ == "__main__":
    main()



