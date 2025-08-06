import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 600, 700
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

pygame.display.set_caption("TicTacToe")

font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 40)

board = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
player = 2
game_over = False

class Button:
    def __init__(self, text, x, y, width, height, font, base_color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, screen):
        color = self.hover_color if self.is_hovered() else self.base_color
        pygame.draw.rect(screen, color, self.rect, 0, 5)
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        screen.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2,
                                   self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self):
        return self.is_hovered() and pygame.mouse.get_pressed()[0]

play_vs_ai_button = Button("Play vs AI", WIDTH // 2 - 150, 300, 300, 70, font, LINE_COLOR, (30, 170, 150))
play_vs_player_button = Button("Play vs Player", WIDTH // 2 - 150, 400, 300, 70, font, LINE_COLOR, (30, 170, 150))


def main_menu():
    screen.fill(BG_COLOR)
    title = font.render('Tic Tac Toe', True, LINE_COLOR)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

    play_vs_ai_button.draw(screen)
    play_vs_player_button.draw(screen)

    pygame.display.update()

def draw_board():
    screen.fill(BG_COLOR)
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, row * SQUARE_SIZE + 100), (WIDTH, row * SQUARE_SIZE + 100), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (col * SQUARE_SIZE, 100), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def animate_circle(row, col):
    steps = 30
    center = (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2 + 100))
    for i in range(1, steps + 1):
        pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS * i // steps, CIRCLE_WIDTH)
        pygame.display.update()
        pygame.time.delay(10)

def animate_cross(row, col):
    steps = 30
    start1 = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + 100)
    end1 = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE + 100)
    start2 = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE + 100)
    end2 = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE + 100)
    
    for i in range(1, steps + 1):
        pygame.draw.line(screen, CROSS_COLOR, start1, ((start1[0] + (end1[0] - start1[0]) * i // steps), (start1[1] + (end1[1] - start1[1]) * i // steps)), CROSS_WIDTH)
        pygame.draw.line(screen, CROSS_COLOR, start2, ((start2[0] + (end2[0] - start2[0]) * i // steps), (start2[1] + (end2[1] - start2[1]) * i // steps)), CROSS_WIDTH)
        pygame.display.update()
        pygame.time.delay(10)

def minimax(board, depth, is_maximizing):
    if check_win(1):
        return 1
    if check_win(2):
        return -1
    if check_tie():
        return 0

    if is_maximizing:
        best_score = -math.inf
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    board[row][col] = 1
                    score = minimax(board, depth + 1, False)
                    board[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    board[row][col] = 2
                    score = minimax(board, depth + 1, True)
                    board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score

def ai_move():
    best_score = -math.inf
    best_move = None
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 0:
                board[row][col] = 1
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    best_move = (row, col)

    if best_move:
        row, col = best_move
        board[row][col] = 1
        animate_circle(row, col)

def check_win(player):
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            return True
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            return True
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        return True
    return False

def check_tie():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 0:
                return False
    return True

def reset_game():
    global board, player, game_over
    board = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    player = 2  
    game_over = False
    draw_board()
    display_turn(player)

def display_turn(player, vs_ai=False):
    screen.fill(BG_COLOR, (0, 0, WIDTH, 100))
    if vs_ai:
        if player == 1:
            turn_text = small_font.render("AI's Turn", True, TEXT_COLOR)
        else:
            turn_text = small_font.render("Your Turn", True, TEXT_COLOR)
    else:
        if player == 1:
            turn_text = small_font.render("Player 1's Turn (O)", True, TEXT_COLOR)
        else:
            turn_text = small_font.render("Player 2's Turn (X)", True, TEXT_COLOR)
    
    screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, 30))
    pygame.display.update()

def game_loop(vs_ai=False):
    global game_over, player
    reset_game()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouseX = event.pos[0]
                mouseY = event.pos[1]

                clicked_row = int((mouseY - 100) // SQUARE_SIZE)
                clicked_col = int(mouseX // SQUARE_SIZE)

                if mouseY > 100 and board[clicked_row][clicked_col] == 0:
                    if player == 2:
                        board[clicked_row][clicked_col] = 2
                        animate_cross(clicked_row, clicked_col)
                        if check_win(2):
                            print("Player 2 wins!")
                            game_over = True
                    elif player == 1 and not vs_ai:
                        board[clicked_row][clicked_col] = 1
                        animate_circle(clicked_row, clicked_col)
                        if check_win(1):
                            print("Player 1 wins!")
                            game_over = True

                    player = 3 - player
                    display_turn(player, vs_ai)

            if vs_ai and player == 1 and not game_over:
                pygame.time.wait(500)
                ai_move()
                if check_win(1):
                    print("AI wins!")
                    game_over = True
                player = 2
                display_turn(player, vs_ai)

        if check_tie() and not game_over:
            print("It's a tie!")
            game_over = True
        
        pygame.display.update()

    pygame.time.wait(1500)
    return

def main():
    running = True
    while running:
        main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_vs_ai_button.is_clicked():
                    game_loop(vs_ai=True)
                if play_vs_player_button.is_clicked():
                    game_loop(vs_ai=False)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
