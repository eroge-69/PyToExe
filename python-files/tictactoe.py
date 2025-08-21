import pygame
import sys
import time
import math

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 600, 700
LINE_WIDTH = 10
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE//3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 20
SPACE = SQUARE_SIZE//4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)

# Fonts
FONT = pygame.font.SysFont("comicsans", 60)
GAME_OVER_FONT = pygame.font.SysFont("comicsans", 70)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

# Board
board = [["" for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]


def draw_lines():
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT - 100), LINE_WIDTH)


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == "O":
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                   (int(col * SQUARE_SIZE + SQUARE_SIZE // 2),
                                    int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == "X":
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE,
                                  row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)


def available_square(row, col):
    return board[row][col] == ""


def mark_square(row, col, player):
    board[row][col] = player


def is_full():
    return all(cell != "" for row in board for cell in row)


def check_winner():
    # Check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != "":
            return board[0][i]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]

    return None


def minimax(temp_board, depth, is_maximizing):
    winner = check_winner()
    if winner == "O":
        return 1
    elif winner == "X":
        return -1
    elif is_full():
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(3):
            for j in range(3):
                if temp_board[i][j] == "":
                    temp_board[i][j] = "O"
                    score = minimax(temp_board, depth + 1, False)
                    temp_board[i][j] = ""
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(3):
            for j in range(3):
                if temp_board[i][j] == "":
                    temp_board[i][j] = "X"
                    score = minimax(temp_board, depth + 1, True)
                    temp_board[i][j] = ""
                    best_score = min(score, best_score)
        return best_score


def best_move():
    best_score = -math.inf
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == "":
                board[i][j] = "O"
                score = minimax(board, 0, False)
                board[i][j] = ""
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move


def draw_text(text, font, y_offset=0):
    label = font.render(text, True, TEXT_COLOR)
    label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(label, label_rect)


def loading_screen():
    screen.fill(BG_COLOR)
    draw_text("Loading...", FONT)
    pygame.display.update()
    time.sleep(2)


def game_over_screen(result):
    screen.fill(BG_COLOR)
    if result == "X":
        draw_text("You Lost!", GAME_OVER_FONT)
    elif result == "Draw":
        draw_text("It's a Draw!", GAME_OVER_FONT)
    else:
        draw_text("You Win!", GAME_OVER_FONT)
    pygame.display.update()
    time.sleep(3)
    pygame.quit()
    sys.exit()


# --- Game Start ---
loading_screen()
screen.fill(BG_COLOR)
draw_lines()
pygame.display.update()

player_turn = True
game_over = False

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN and player_turn:
            mouseX = event.pos[0]
            mouseY = event.pos[1]

            clicked_row = mouseY // SQUARE_SIZE
            clicked_col = mouseX // SQUARE_SIZE

            if clicked_row < 3 and available_square(clicked_row, clicked_col):
                mark_square(clicked_row, clicked_col, "X")
                player_turn = False

    if not player_turn and not game_over:
        winner = check_winner()
        if winner or is_full():
            game_over = True
            result = winner if winner else "Draw"
            game_over_screen(result if result != "O" else "X")  # If AI wins, player lost

        else:
            move = best_move()
            if move:
                mark_square(move[0], move[1], "O")
            player_turn = True

    screen.fill(BG_COLOR)
    draw_lines()
    draw_figures()
    pygame.display.update()

    winner = check_winner()
    if winner or is_full():
        game_over = True
        result = winner if winner else "Draw"
        game_over_screen(result if result != "O" else "X")  # If AI wins, player lost
