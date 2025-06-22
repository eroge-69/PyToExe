import pygame
import random
import sys
import os

pygame.init()

WIDTH = 600
HEIGHT = 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Gra Snake")

GREEN = (0, 160, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
FPS = 10
font = pygame.font.SysFont("Arial", 25)

HIGHSCORE_FILE = "highscore.txt"

# Ładuje najlepszy wynik z pliku
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

# Zapisuje najlepszy wynik do pliku
def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

# Ekran startowy - kliknij cokolwiek, aby zacząć
def start_screen():
    screen.fill(GREEN)
    title_text = font.render("Witaj w grze Snake", True, WHITE)
    instruction_text = font.render("Kliknij dowolny przycisk, aby rozpocząć", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

# Ekran końcowy - pokazuje wynik i najlepszy wynik
def game_over_screen(score, highscore):
    screen.fill(GREEN)
    game_over_text = font.render(f"Koniec gry! Twój wynik: {score}", True, RED)
    high_score_text = font.render(f"Najlepszy wynik: {highscore}", True, WHITE)
    instruction_text = font.render("Kliknij dowolny przycisk, aby zagrać ponownie", True, WHITE)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 3 + 40))
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

# Główna funkcja gry
def main_game():
    # Inicjalizacja pozycji węża (lista segmentów)
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = "RIGHT"
    next_direction = direction

    # Losowa pozycja jabłka na siatce (kratkach)
    apple = (random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
             random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE)

    score = 0
    highscore = load_highscore()

    # Rysuje węża jako niebieskie kwadraty
    def draw_snake(snake_list):
        for block in snake_list:
            pygame.draw.rect(screen, BLUE, pygame.Rect(block[0], block[1], CELL_SIZE, CELL_SIZE))

    # Rysuje jabłko jako czerwone kółko, które jest idealnie okrągłe
    def draw_apple(position):
        center = (position[0] + CELL_SIZE // 2, position[1] + CELL_SIZE // 2)
        radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(screen, RED, center, radius)

    # Rysuje aktualny wynik i najlepszy wynik na ekranie
    def draw_score(current, best):
        text = font.render(f"Wynik: {current}   Najlepszy: {best}", True, WHITE)
        screen.blit(text, (10, 10))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Blokada cofania się węża: nie pozwalamy iść w przeciwną stronę niż obecna
                if event.key == pygame.K_UP and direction != "DOWN":
                    next_direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    next_direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    next_direction = "RIGHT"

        direction = next_direction

        x, y = snake[0]
        if direction == "UP":
            y -= CELL_SIZE
        elif direction == "DOWN":
            y += CELL_SIZE
        elif direction == "LEFT":
            x -= CELL_SIZE
        elif direction == "RIGHT":
            x += CELL_SIZE

        new_head = (x, y)

        # Sprawdzamy kolizję ze ścianami lub z własnym ciałem
        if (
            x < 0 or x >= WIDTH or
            y < 0 or y >= HEIGHT or
            new_head in snake
        ):
            running = False  # Koniec gry

        else:
            snake.insert(0, new_head)

            # Jeśli wąż zjadł jabłko, punktujemy i losujemy nowe jabłko
            if new_head == apple:
                score += 1
                apple = (random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
                         random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE)
            else:
                snake.pop()  # Usuwamy ogon, jeśli nie zjedzono jabłka

            screen.fill(GREEN)  # Zielone tło
            draw_snake(snake)   # Rysujemy węża
            draw_apple(apple)   # Rysujemy jabłko
            draw_score(score, highscore)  # Wyniki
            pygame.display.update()
            clock.tick(FPS)

    # Po zakończeniu gry zapisujemy najlepszy wynik, jeśli jest nowy rekord
    if score > highscore:
        save_highscore(score)
        highscore = score

    return score, highscore  # Zwracamy wynik i najlepszy wynik

# --- Główna pętla programu ---

start_screen()  # Ekran startowy wyświetlamy raz na początku

while True:
    score, highscore = main_game()  # Gra się wykonuje i po śmierci wracamy tutaj
    game_over_screen(score, highscore)  # Ekran końcowy
    # Po kliknięciu w ekran końcowy gra zaczyna się od nowa automatycznie
