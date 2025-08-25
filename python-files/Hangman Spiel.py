import pygame
import sys
import random

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Hagman")
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 0, 0)
GREEN = (0, 150, 0)

start_button = pygame.Rect(200, 160, 200, 60)

# Wortliste
word_pool = ["haus", "baum", "glas", "mond"]

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    rect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, rect)

def start_screen():
    while True:
        screen.fill(WHITE)
        draw_text("HAGMAN", font, BLACK, screen, 300, 80)
        pygame.draw.rect(screen, GRAY, start_button)
        draw_text("Start", small_font, BLACK, screen, start_button.centerx, start_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return

        pygame.display.flip()

def game_loop():
    word = random.choice(word_pool).upper()
    guessed_letters = []
    wrong_guesses = 0
    max_attempts = 6

    running = True
    while running:
        screen.fill(WHITE)

        # Anzeige des Wortes
        display_word = ""
        for letter in word:
            if letter in guessed_letters:
                display_word += letter + " "
            else:
                display_word += "_ "

        draw_text("Wort: " + display_word.strip(), small_font, BLACK, screen, 300, 100)
        draw_text(f"Fehlversuche: {wrong_guesses}/{max_attempts}", small_font, RED, screen, 300, 150)
        draw_text("Bisher geraten: " + " ".join(guessed_letters), small_font, BLACK, screen, 300, 200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    guess = event.unicode.upper()
                    if guess not in guessed_letters:
                        guessed_letters.append(guess)
                        if guess not in word:
                            wrong_guesses += 1

        if all(letter in guessed_letters for letter in word):
            return "win"
        elif wrong_guesses >= max_attempts:
            return "lose"

        pygame.display.flip()

def end_screen(result, correct_word):
    while True:
        screen.fill(WHITE)
        if result == "win":
            draw_text("Gewonnen!", font, GREEN, screen, 300, 120)
        else:
            draw_text("Game Over", font, RED, screen, 300, 120)
            draw_text(f"Das Wort war: {correct_word}", small_font, BLACK, screen, 300, 180)

        draw_text("Drücke R für Neustart oder Q zum Beenden", small_font, BLACK, screen, 300, 260)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

# Spielsteuerung
while True:
    start_screen()
    result = game_loop()
    end_state = end_screen(result, correct_word=result == "lose" and word.upper() or "")
    if end_state == "restart":
        continue
