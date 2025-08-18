import pygame
import sys
import time

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puzzle Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)

# Fonts with fallback: Gotham → Arial → Sans Serif
def get_font(names, size):
    for name in names:
        try:
            return pygame.font.SysFont(name, size)
        except:
            continue
    return pygame.font.SysFont(None, size)

font = get_font(["Gotham", "Arial", "Sans Serif"], 30)
timer_font = get_font(["Gotham", "Arial", "Sans Serif"], 40)
win_font = get_font(["Gotham", "Arial", "Sans Serif"], 24)

# Button grid setup
BUTTON_SIZE = 80
PADDING = 10
ROWS, COLS = 5, 6  # 5x6 grid (last row only 2 buttons)

buttons = []
selected = set()

for i in range(26):
    row, col = divmod(i, COLS)
    x = col * (BUTTON_SIZE + PADDING) + 50
    y = row * (BUTTON_SIZE + PADDING) + 100
    rect = pygame.Rect(x, y, BUTTON_SIZE, BUTTON_SIZE)
    buttons.append(rect)

# Submit button
submit_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 80, 160, 50)

# Correct answers (indices of buttons, 1-based)
VALID_CHOICES = {1, 2, 5, 11, 15, 18, 20, 21}

# Timer setup
start_time = time.time()
TIME_LIMIT = 180  # 3 minutes

# Game state
game_state = "playing"

def draw_buttons():
    for i, rect in enumerate(buttons):
        color = RED if (i + 1) in selected else GRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        label = font.render(str(i + 1), True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    # Submit button (red)
    pygame.draw.rect(screen, RED, submit_rect)
    pygame.draw.rect(screen, WHITE, submit_rect, 2)
    label = font.render("Submit", True, WHITE)
    label_rect = label.get_rect(center=submit_rect.center)
    screen.blit(label, label_rect)


def draw_timer():
    elapsed = int(time.time() - start_time)
    remaining = max(0, TIME_LIMIT - elapsed)
    mins, secs = divmod(remaining, 60)
    timer_text = f"{mins:02}:{secs:02}"
    label = timer_font.render(timer_text, True, WHITE)
    screen.blit(label, (WIDTH // 2 - 40, 20))
    return remaining > 0

def draw_win_screen():
    screen.fill(BLACK)

    # Title
    title_text = "CONGRATULATIONS PLAYER"
    title_label = win_font.render(title_text, True, WHITE)
    title_rect = title_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(title_label, title_rect)

    # Message lines
    message_lines = [
        "COLLECT 10 PIECES.",
        "YOU WILL REMAIN IN PRISON FOR YOUR REMAINING TIME",
        "BEFORE THE NEXT CHALLENGE BUT YOU WILL BE IMMUNE",
        "FROM THE DEATH MATCH IF IT HASN'T YET HAPPENED."
    ]

    line_spacing = 30
    start_y = HEIGHT // 2 - 50

    for i, line in enumerate(message_lines):
        line_label = win_font.render(line, True, WHITE)
        line_rect = line_label.get_rect(center=(WIDTH // 2, start_y + i * line_spacing))
        screen.blit(line_label, line_rect)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "playing":
            pos = pygame.mouse.get_pos()

            # Check puzzle buttons
            for i, rect in enumerate(buttons):
                if rect.collidepoint(pos):
                    if (i + 1) in selected:
                        selected.remove(i + 1)
                    else:
                        selected.add(i + 1)

            # Check submit button
            if submit_rect.collidepoint(pos):
                if selected == VALID_CHOICES:
                    game_state = "win"
                else:
                    print("Incorrect. Try again!")

    screen.fill(BLACK)

    if game_state == "playing":
        draw_buttons()
        time_left = draw_timer()
        if not time_left:
            # game_state = "lose" # You could add a lose state here
            pass

    elif game_state == "win":
        draw_win_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()
