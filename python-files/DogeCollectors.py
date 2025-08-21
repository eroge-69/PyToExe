import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doge Coin Catcher")

# Colors
WHITE = (80, 34, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 223, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)

# Load images
doge_default = pygame.image.load("Angry_Doge.png")
doge_default = pygame.transform.scale(doge_default, (50, 50))

doge_skins = {
    "Angry Doge": {"image": doge_default, "cost": 0},
    "Cool Doge": {"image": pygame.transform.scale(pygame.image.load("Cool_Doge.png"), (50, 50)), "cost": 50},
    "Happy Doge": {"image": pygame.transform.scale(pygame.image.load("Happy_Doge.png"), (50, 50)), "cost": 100}
}

coin_img = pygame.image.load("Dogecoin.png")
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Fonts
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 60)

# Game settings
player_speed = 8
coin_speed = 3
spawn_rate = 60  # increase for fewer coins

# File paths
skin_file = "skin_save.txt"
owned_file = "owned_skins.txt"
coins_file = "dogecoins.txt"

# Load total Dogecoins
if os.path.exists(coins_file):
    with open(coins_file, "r") as f:
        try:
            total_doge_coins = int(f.read().strip())
        except:
            total_doge_coins = 0
else:
    total_doge_coins = 0

# Load last selected skin
if os.path.exists(skin_file):
    with open(skin_file, "r") as f:
        selected_skin = f.read().strip()
        if selected_skin not in doge_skins:
            selected_skin = "Angry Doge"
else:
    selected_skin = "Angry Doge"

# Load owned skins
if os.path.exists(owned_file):
    with open(owned_file, "r") as f:
        owned_skins = f.read().splitlines()
        if not owned_skins:
            owned_skins = ["Angry Doge"]
else:
    owned_skins = ["Angry Doge"]

def save_skin():
    with open(skin_file, "w") as f:
        f.write(selected_skin)

def save_owned_skins():
    with open(owned_file, "w") as f:
        for skin in owned_skins:
            f.write(f"{skin}\n")

def save_coins():
    with open(coins_file, "w") as f:
        f.write(str(total_doge_coins))

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Doge Coin Catcher", big_font, BLACK, screen, WIDTH // 2, HEIGHT // 4)
        draw_text("Press ENTER to Start", font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Press S for Shop", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Press ESC to Quit", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 100)
        draw_text(f"Total Dogecoins: {total_doge_coins}", font, BLACK, screen, WIDTH // 2, HEIGHT - 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_coins()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()
                if event.key == pygame.K_s:
                    shop_menu()
                if event.key == pygame.K_ESCAPE:
                    save_coins()
                    pygame.quit()
                    sys.exit()

def shop_menu():
    global total_doge_coins, selected_skin, owned_skins
    button_height = 50
    button_width = 300
    button_start_y = 120
    gap = 20
    buttons = []

    for i, (name, data) in enumerate(doge_skins.items()):
        rect = pygame.Rect(WIDTH // 2 - button_width // 2, button_start_y + i * (button_height + gap), button_width, button_height)
        buttons.append((rect, name, data["cost"]))

    while True:
        screen.fill(WHITE)
        draw_text("Shop", big_font, BLACK, screen, WIDTH // 2, 50)
        draw_text("Click a skin to buy/select it", font, BLACK, screen, WIDTH // 2, 90)
        draw_text("Press ESC to Return", font, BLACK, screen, WIDTH // 2, HEIGHT - 30)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_coins()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        for rect, name, cost in buttons:
            # Draw button color
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, LIGHT_GRAY, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)

            # Determine label
            if name == selected_skin:
                text = f"{name} - Equipped"
            elif name in owned_skins:
                text = f"{name} - Owned"
            else:
                text = f"{name} - Cost: {cost}"
            
            color = BLACK if (name in owned_skins or cost <= total_doge_coins) else (150, 150, 150)
            draw_text(text, font, color, screen, rect.centerx, rect.centery)

            # Handle mouse click
            if rect.collidepoint(mouse_pos) and mouse_clicked:
                if name in owned_skins or cost <= total_doge_coins:
                    selected_skin = name
                    if name not in owned_skins:
                        total_doge_coins -= cost
                        save_coins()
                        owned_skins.append(name)
                        save_owned_skins()
                    save_skin()

        pygame.display.flip()

def game_over_screen(score):
    global total_doge_coins
    total_doge_coins += score
    save_coins()
    while True:
        screen.fill(WHITE)
        draw_text("GAME OVER", big_font, BLACK, screen, WIDTH // 2, HEIGHT // 3)
        draw_text(f"Score this round: {score}", font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
        draw_text(f"Total Dogecoins: {total_doge_coins}", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 40)
        draw_text("Press ENTER to Return to Main Menu", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_coins()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main_menu()

def game_loop():
    player_x = WIDTH // 2
    player_y = HEIGHT - 60
    coin_list = []
    score = 0
    frame_count = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_coins()
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - 50, player_x))

        if frame_count % spawn_rate == 0:
            coin_x = random.randint(0, WIDTH - 30)
            coin_list.append([coin_x, -30])

        for coin in coin_list:
            coin[1] += coin_speed

        for coin in coin_list[:]:
            if (player_x < coin[0] + 30 and player_x + 50 > coin[0] and
                player_y < coin[1] + 30 and player_y + 50 > coin[1]):
                score += 1
                coin_list.remove(coin)
            elif coin[1] > HEIGHT:
                game_over_screen(score)

        screen.fill(WHITE)
        screen.blit(doge_skins[selected_skin]["image"], (player_x, player_y))
        for coin in coin_list:
            screen.blit(coin_img, (coin[0], coin[1]))

        draw_text(f"Score: {score}", font, BLACK, screen, 60, 20)
        draw_text(f"Total Dogecoins: {total_doge_coins}", font, BLACK, screen, WIDTH - 120, 20)
        pygame.display.flip()

# Start game
main_menu()
