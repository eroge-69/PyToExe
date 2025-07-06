import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 300, 600
CELL_SIZE = 30
COLUMNS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255), (255, 165, 0), (0, 255, 0),
    (255, 0, 0), (0, 0, 255), (160, 32, 240), (255, 255, 0)
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and (x + off_x < 0 or x + off_x >= COLUMNS or y + off_y >= ROWS or board[y + off_y][x + off_x]):
                return True
    return False

def join_board(board, shape, offset, color):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + off_y][x + off_x] = color

def clear_rows(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [0] * COLUMNS)
    return new_board

def new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    return Tetromino(shape, color)

def draw_board(screen, board):
    for y, row in enumerate(board):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def run_game():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    board = [[0] * COLUMNS for _ in range(ROWS)]
    piece = new_piece()
    fall_time = 0

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time > 500:
            if not check_collision(board, piece.shape, (piece.x, piece.y + 1)):
                piece.y += 1
            else:
                join_board(board, piece.shape, (piece.x, piece.y), piece.color)
                board = clear_rows(board)
                piece = new_piece()
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not check_collision(board, piece.shape, (piece.x - 1, piece.y)):
                    piece.x -= 1
                elif event.key == pygame.K_RIGHT and not check_collision(board, piece.shape, (piece.x + 1, piece.y)):
                    piece.x += 1
                elif event.key == pygame.K_DOWN and not check_collision(board, piece.shape, (piece.x, piece.y + 1)):
                    piece.y += 1
                elif event.key == pygame.K_UP:
                    old_shape = piece.shape
                    piece.rotate()
                    if check_collision(board, piece.shape, (piece.x, piece.y)):
                        piece.shape = old_shape  # Revert if collision

        draw_board(screen, board)
        draw_board(screen, [[piece.color if cell else 0 for cell in row] for row in piece.shape], piece.x, piece.y)
        pygame.display.update()

    pygame.quit()

# Add helper to draw the active piece
def draw_board(screen, shape, x_offset=0, y_offset=0):
    for y, row in enumerate(shape):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(screen, color, ((x + x_offset)*CELL_SIZE, (y + y_offset)*CELL_SIZE, CELL_SIZE, CELL_SIZE))

if __name__ == "__main__":
    run_game()
