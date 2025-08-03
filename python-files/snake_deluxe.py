import pygame
import random
import os

pygame.init()

# === Innstillinger ===
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
YELLOW = (255, 255, 102)
GOLD = (255, 215, 0)
FPS = {"Lett": 10, "Middels": 15, "Vanskelig": 20}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Deluxe")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 25)
score_font = pygame.font.SysFont("consolas", 20)

HIGHSCORE_FILE = "highscore.txt"

# === Lyd ===
try:
    pygame.mixer.init()
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1)
    eat_sound = pygame.mixer.Sound("eat.wav")
    gameover_sound = pygame.mixer.Sound("gameover.wav")
except:
    print("Lydfiler mangler eller kunne ikke lastes.")

# === Highscore-fil ===
if not os.path.exists(HIGHSCORE_FILE):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write("0")

def get_highscore():
    with open(HIGHSCORE_FILE, "r") as f:
        return int(f.read())

def save_highscore(score):
    high = get_highscore()
    if score > high:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))

# === Tegnefunksjoner ===
def draw_snake(snake_list):
    for block in snake_list:
        pygame.draw.rect(screen, BLACK, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def draw_walls():
    # Øverste og nederste kant
    for x in range(0, WIDTH, BLOCK_SIZE):
        screen.fill(RED, (x, 0, BLOCK_SIZE, BLOCK_SIZE))
        screen.fill(RED, (x, HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    # Venstre og høyre kant
    for y in range(0, HEIGHT, BLOCK_SIZE):
        screen.fill(RED, (0, y, BLOCK_SIZE, BLOCK_SIZE))
        screen.fill(RED, (WIDTH - BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE))

def show_score(score):
    val = score_font.render("Poeng: " + str(score), True, YELLOW)
    screen.blit(val, [10, 10])
    hs = get_highscore()
    hs_txt = score_font.render("Highscore: " + str(hs), True, YELLOW)
    screen.blit(hs_txt, [WIDTH - 180, 10])

# === Menyfunksjoner ===
def menu():
    selected = 0
    options = ["Start Spill", "Avslutt"]
    while True:
        screen.fill(BLUE)
        title = font.render("🐍 SNAKE DELUXE", True, YELLOW)
        screen.blit(title, [WIDTH//2 - title.get_width()//2, 60])
        for i, opt in enumerate(options):
            color = GREEN if i == selected else WHITE
            txt = font.render(opt, True, color)
            screen.blit(txt, [WIDTH//2 - txt.get_width()//2, 150 + i*40])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif e.key == pygame.K_RETURN:
                    if options[selected] == "Start Spill":
                        return choose_difficulty()
                    else:
                        pygame.quit()
                        quit()

def choose_difficulty():
    selected = 0
    levels = list(FPS.keys())
    while True:
        screen.fill(BLUE)
        title = font.render("Velg vanskelighetsgrad", True, YELLOW)
        screen.blit(title, [WIDTH//2 - title.get_width()//2, 60])
        for i, lvl in enumerate(levels):
            color = GREEN if i == selected else WHITE
            txt = font.render(lvl, True, color)
            screen.blit(txt, [WIDTH//2 - txt.get_width()//2, 150 + i*40])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(levels)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(levels)
                elif e.key == pygame.K_RETURN:
                    return levels[selected]

# === Spill-løkke ===
def game_loop(difficulty):
    game_over = False
    game_close = False

    x, y = WIDTH/2, HEIGHT/2
    dx, dy = 0, 0
    snake_list = []
    snake_len = 1
    score = 0

    # Vanlig mat
    food = [
        random.randrange(1, (WIDTH-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE,
        random.randrange(1, (HEIGHT-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
    ]
    # Spesialmat
    special_food = None
    special_timer = 0

    speed = FPS[difficulty]

    while not game_over:
        # Game over-skjerm
        while game_close:
            screen.fill(BLUE)
            msg = font.render("Game Over! Trykk C for nytt spill eller Q for å avslutte", True, RED)
            screen.blit(msg, [WIDTH/2 - msg.get_width()/2, HEIGHT/2 - 20])
            pygame.display.update()
            try:
                pygame.mixer.Sound.play(gameover_sound)
            except:
                pass
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif e.key == pygame.K_c:
                        game_loop(difficulty)

        # Håndter input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                game_over = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                elif e.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK_SIZE, 0
                elif e.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                elif e.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK_SIZE

        x += dx
        y += dy

        # Kollisjon med vegg eller kant
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            game_close = True
        if difficulty != "Lett":
            # Vegger gir game over
            if x == 0 or x == WIDTH-BLOCK_SIZE or y == 0 or y == HEIGHT-BLOCK_SIZE:
                game_close = True

        screen.fill(BLUE)
        if difficulty != "Lett":
            draw_walls()

        # Tegn vanlig mat
        pygame.draw.rect(screen, GREEN, [food[0], food[1], BLOCK_SIZE, BLOCK_SIZE])
        # Tegn spesialmat
        if special_food:
            pygame.draw.rect(screen, GOLD, [special_food[0], special_food[1], BLOCK_SIZE, BLOCK_SIZE])
            special_timer -= 1
            if special_timer <= 0:
                special_food = None

        # Oppdater slangens posisjon
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_len:
            del snake_list[0]
        for seg in snake_list[:-1]:
            if seg == snake_head:
                game_close = True

        draw_snake(snake_list)
        show_score(score)
        pygame.display.update()

        # Spis vanlig mat
        if x == food[0] and y == food[1]:
            food = [
                random.randrange(1, (WIDTH-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE,
                random.randrange(1, (HEIGHT-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
            ]
            snake_len += 1
            score += 10
            try:
                pygame.mixer.Sound.play(eat_sound)
            except:
                pass
            # 1 av 5 sjanse for spesialmat
            if random.randint(1,5) == 1 and not special_food:
                special_food = [
                    random.randrange(1, (WIDTH-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE,
                    random.randrange(1, (HEIGHT-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
                ]
                special_timer = 50

        # Spis spesialmat
        if special_food and x == special_food[0] and y == special_food[1]:
            score += 30
            snake_len += 3
            special_food = None
            try:
                pygame.mixer.Sound.play(eat_sound)
            except:
                pass

        clock.tick(speed)

    save_highscore(score)
    pygame.quit()
    quit()

# === Start spillet ===
if __name__ == "__main__":
    diff = menu()
    game_loop(diff)
