import pygame
import sys
import os
from tkinter import Tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()

# Hide Tkinter root window
root = Tk()
root.withdraw()

# Screen setup
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("🏸 Badminton Scoreboard")

# Colors
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (0, 100, 200)
GREEN = (0, 180, 0)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)
LIGHT_GREEN = (10, 100, 0)


# Fonts (adaptive to screen size)
font_name = pygame.font.SysFont("Arial", int(HEIGHT * 0.05), bold=True)   # Player name
font_score = pygame.font.SysFont("Arial", int(HEIGHT * 0.30), bold=True)  # Score font
font_set = pygame.font.SysFont("Arial", int(HEIGHT * 0.05), bold=True)    # Set font
font_small = pygame.font.SysFont("Arial", int(HEIGHT * 0.03))             # Hint bar

# Scores & sets
player1_name, player2_name = "Player A", "Player B"
player1_score, player2_score = 0, 0
player1_sets, player2_sets = 0, 0

# Editable set points
max_sets = 3
player1_set_points = [0] * max_sets
player2_set_points = [0] * max_sets

# Editing states
editing_name = False
editing_player = None
current_input = ""

editing_banner = False
banner_img = None

editing_set = False
editing_set_player = None
editing_set_index = None
current_set_input = ""

# Clock
clock = pygame.time.Clock()

def load_image(file_path):
    if os.path.exists(file_path):
        try:
            return pygame.image.load(file_path)
        except:
            return None
    return None

def blit_centered(text, font, color, center_x, center_y):
    """Render text centered at given coordinates"""
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(center_x, center_y))
    screen.blit(surface, rect)

def get_next_set_row():
    """Find next row to store set results.
       Prefer rows where BOTH sides are empty; else any row with at least one empty cell.
    """
    for i in range(max_sets):
        if player1_set_points[i] == 0 and player2_set_points[i] == 0:
            return i
    for i in range(max_sets):
        if player1_set_points[i] == 0 or player2_set_points[i] == 0:
            return i
    return None  # No space left

# Game loop
while True:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Key handling
        if event.type == pygame.KEYDOWN:

            # Editing player name
            if editing_name:
                if event.key == pygame.K_RETURN:
                    if editing_player == 1:
                        player1_name = current_input or player1_name
                    else:
                        player2_name = current_input or player2_name
                    editing_name = False
                    current_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_input = current_input[:-1]
                else:
                    current_input += event.unicode

            # Editing set points
            elif editing_set:
                if event.key == pygame.K_RETURN:
                    try:
                        value = int(current_set_input)
                        if editing_set_player == 1:
                            player1_set_points[editing_set_index] = value
                        else:
                            player2_set_points[editing_set_index] = value
                    except:
                        pass
                    editing_set = False
                    current_set_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_set_input = current_set_input[:-1]
                else:
                    if event.unicode.isdigit():
                        current_set_input += event.unicode

            # Normal key actions
            else:
                # Player scores
                if event.key == pygame.K_q: player1_score += 1
                if event.key == pygame.K_w and player1_score > 0: player1_score -= 1
                if event.key == pygame.K_p: player2_score += 1
                if event.key == pygame.K_o and player2_score > 0: player2_score -= 1

                # Set win (log BOTH players' set points in same row)
                if event.key == pygame.K_z:  # Player 1 wins this set
                    row = get_next_set_row()
                    if row is not None:
                        player1_set_points[row] = player1_score
                        player2_set_points[row] = player2_score
                        player1_sets += 1
                        player1_score, player2_score = 0, 0

                if event.key == pygame.K_m:  # Player 2 wins this set
                    row = get_next_set_row()
                    if row is not None:
                        player1_set_points[row] = player1_score
                        player2_set_points[row] = player2_score
                        player2_sets += 1
                        player1_score, player2_score = 0, 0

                # Edit names
                if event.key == pygame.K_1: editing_name = True; editing_player = 1; current_input = ""
                if event.key == pygame.K_2: editing_name = True; editing_player = 2; current_input = ""

                # Reset everything
                if event.key == pygame.K_r:
                    player1_name, player2_name = "Player A", "Player B"
                    player1_score, player2_score = 0, 0
                    player1_sets, player2_sets = 0, 0
                    player1_set_points = [0] * max_sets
                    player2_set_points = [0] * max_sets

                # Exit
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            banner_height = int(HEIGHT * 0.12)
            if 0 <= mouse_y <= banner_height:
                file_path = filedialog.askopenfilename(
                    title="Select Banner Image",
                    filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
                )
                if file_path:
                    img = load_image(file_path)
                    if img:
                        banner_img = img

            # Click on set boxes
            set_box_width = int(WIDTH * 0.06)
            set_box_height = int(HEIGHT * 0.06)
            set_start_x = int(WIDTH * 0.45)
            set_start_y = int(HEIGHT * 0.3)
            for row in range(max_sets):
                for col in range(2):
                    rect = pygame.Rect(
                        set_start_x + col * set_box_width,
                        set_start_y + row * set_box_height,
                        set_box_width, set_box_height
                    )
                    if rect.collidepoint(mouse_x, mouse_y):
                        editing_set = True
                        editing_set_player = 1 if col == 0 else 2
                        editing_set_index = row
                        current_set_input = ""

    # Draw background
    screen.fill(BLACK)

    # Draw banner
    banner_height = int(HEIGHT * 0.12)
    if banner_img:
        screen.blit(pygame.transform.scale(banner_img, (WIDTH, banner_height)), (0, 0))
    else:
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, banner_height))
        pygame.draw.rect(screen, LIGHT_GREEN, (0, 0, WIDTH, banner_height), 5)

    # Player containers
    player1_rect = pygame.Rect(int(WIDTH * 0.05), int(HEIGHT * 0.25), int(WIDTH * 0.35), int(HEIGHT * 0.4))
    player2_rect = pygame.Rect(int(WIDTH * 0.6), int(HEIGHT * 0.25), int(WIDTH * 0.35), int(HEIGHT * 0.4))
    for rect in [player1_rect, player2_rect]:
        pygame.draw.rect(screen, BLACK, rect, border_radius=30)
        pygame.draw.rect(screen, LIGHT_GREEN, rect, width=int(HEIGHT * 0.015), border_radius=30)

    # Player names (top left of their boxes)
    display_name1 = current_input if editing_name and editing_player == 1 else player1_name
    display_name2 = current_input if editing_name and editing_player == 2 else player2_name
    screen.blit(font_name.render(display_name1, True, WHITE), (player1_rect.x + 20, player1_rect.y + 20))
    screen.blit(font_name.render(display_name2, True, WHITE), (player2_rect.x + 20, player2_rect.y + 20))

    # Scores (centered inside each box)
    blit_centered(str(player1_score), font_score, RED, player1_rect.centerx, player1_rect.centery)
    blit_centered(str(player2_score), font_score, RED, player2_rect.centerx, player2_rect.centery)

    # Draw editable set boxes (3 rows x 2 columns)
    set_box_width = int(WIDTH * 0.06)
    set_box_height = int(HEIGHT * 0.06)
    set_start_x = int(WIDTH * 0.45)
    set_start_y = int(HEIGHT * 0.3)
    for row in range(max_sets):
        for col in range(2):
            rect = pygame.Rect(set_start_x + col * set_box_width, set_start_y + row * set_box_height, set_box_width, set_box_height)
            pygame.draw.rect(screen, BLACK, rect)
            pygame.draw.rect(screen, LIGHT_GREEN, rect, 3)
            val = ""
            if editing_set and editing_set_player == 1 and editing_set_index == row and col == 0:
                val = current_set_input
            elif editing_set and editing_set_player == 2 and editing_set_index == row and col == 1:
                val = current_set_input
            else:
                val = str(player1_set_points[row]) if col == 0 else str(player2_set_points[row])
            blit_centered(val, font_set, WHITE, rect.centerx, rect.centery)

    # Sets total (center bottom)
    blit_centered(f"Sets: {player1_sets} - {player2_sets}", font_set, WHITE, WIDTH // 2, int(HEIGHT * 0.7))

    # Hint bar (bottom center)
    hint_text = "#Developed by Mohsin and Mustaq"
    
    blit_centered(hint_text, font_small, WHITE, WIDTH // 2, int(HEIGHT * 0.95))

    pygame.display.flip()
    clock.tick(30)
