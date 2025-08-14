import pygame, random, sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS, ROWS = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
FPS = 60

# Colors
colors = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],            # I
    [[1, 1], [1, 1]],          # O
    [[0, 1, 0], [1, 1, 1]],    # T
    [[1, 0, 0], [1, 1, 1]],    # L
    [[0, 0, 1], [1, 1, 1]],    # J
    [[1, 1, 0], [0, 1, 1]],    # S
    [[0, 1, 1], [1, 1, 0]]     # Z
]

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris - Name Lines")

# Fonts
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 20)  # smaller to fit message

# Board
board = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Name tracking
name = "HEATHER"
line_count = 0

def draw_board():
    screen.fill((0, 0, 0))
    # Draw blocks
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pygame.draw.rect(screen, board[y][x],
                                 (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, (0,0,0),
                                 (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
    # Draw letters at top, spaced evenly
    spacing = SCREEN_WIDTH // (len(name)+1)
    for i in range(line_count):
        letter_surf = font.render(name[i], True, (255, 255, 255))
        x_pos = i * spacing + (spacing // 2 - letter_surf.get_width() // 2)
        screen.blit(letter_surf, (x_pos, 5))

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(colors)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def valid_move(shape, offset_x, offset_y):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = x + offset_x
                new_y = y + offset_y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and board[new_y][new_x]:
                    return False
    return True

def place_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell and y + piece.y >= 0:
                board[y + piece.y][x + piece.x] = piece.color

def clear_lines():
    global line_count
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if 0 not in board[y]:
            del board[y]
            board.insert(0, [0 for _ in range(COLS)])
            cleared += 1
    for _ in range(cleared):
        if line_count < len(name):
            line_count += 1
    return cleared

def hard_drop(piece):
    while valid_move(piece.shape, piece.x, piece.y+1):
        piece.y += 1

def show_message(msg, duration=2000):
    screen.fill((0,0,0))
    spacing = SCREEN_WIDTH // (len(msg)+1)
    for i, char in enumerate(msg):
        letter_surf = large_font.render(char, True, (255, 255, 0))
        x_pos = i * spacing + (spacing // 2 - letter_surf.get_width() // 2)
        screen.blit(letter_surf, (x_pos, SCREEN_HEIGHT//2 - letter_surf.get_height()//2))
    pygame.display.update()
    pygame.time.delay(duration)

# Show starting message
show_message("Is Heather the greatest? Let's find out!", 2500)

# Initialize
clock = pygame.time.Clock()
fall_speed = 500  # milliseconds per step
fall_time = 0
current_piece = Piece()

while True:
    dt = clock.tick(FPS)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid_move(current_piece.shape, current_piece.x-1, current_piece.y):
                current_piece.x -= 1
            if event.key == pygame.K_RIGHT and valid_move(current_piece.shape, current_piece.x+1, current_piece.y):
                current_piece.x += 1
            if event.key == pygame.K_DOWN and valid_move(current_piece.shape, current_piece.x, current_piece.y+1):
                current_piece.y += 1
            if event.key == pygame.K_UP:
                rotated = [list(row) for row in zip(*current_piece.shape[::-1])]
                if valid_move(rotated, current_piece.x, current_piece.y):
                    current_piece.rotate()
            if event.key == pygame.K_SPACE:
                hard_drop(current_piece)
                place_piece(current_piece)
                cleared = clear_lines()
                if line_count >= len(name):
                    for _ in range(6):
                        screen.fill((0,0,0))
                        pygame.display.update()
                        pygame.time.delay(200)
                        msg_text = "HEATHER is the greatest!"
                        spacing = SCREEN_WIDTH // (len(msg_text)+1)
                        for i, char in enumerate(msg_text):
                            letter_surf = large_font.render(char, True, (255, 255, 0))
                            x_pos = i * spacing + (spacing // 2 - letter_surf.get_width() // 2)
                            screen.blit(letter_surf, (x_pos, SCREEN_HEIGHT//2 - letter_surf.get_height()//2))
                        pygame.display.update()
                        pygame.time.delay(200)
                    line_count = 0
                current_piece = Piece()

    # Automatic fall
    if fall_time >= fall_speed:
        if valid_move(current_piece.shape, current_piece.x, current_piece.y+1):
            current_piece.y += 1
        else:
            place_piece(current_piece)
            cleared = clear_lines()
            # Check for lose condition
            if any(board[0][x] for x in range(COLS)):
                show_message("I guess she isn't the greatest..", 3000)
                pygame.quit()
                sys.exit()
            if line_count >= len(name):
                for _ in range(6):
                    screen.fill((0,0,0))
                    pygame.display.update()
                    pygame.time.delay(200)
                    msg_text = "HEATHER is the greatest!"
                    spacing = SCREEN_WIDTH // (len(msg_text)+1)
                    for i, char in enumerate(msg_text):
                        letter_surf = large_font.render(char, True, (255, 255, 0))
                        x_pos = i * spacing + (spacing // 2 - letter_surf.get_width() // 2)
                        screen.blit(letter_surf, (x_pos, SCREEN_HEIGHT//2 - letter_surf.get_height()//2))
                    pygame.display.update()
                    pygame.time.delay(200)
                line_count = 0
            current_piece = Piece()
        fall_time = 0

    # Draw board and current piece
    draw_board()
    for y, row in enumerate(current_piece.shape):
        for x, cell in enumerate(row):
            if cell and y + current_piece.y >= 0:
                pygame.draw.rect(screen, current_piece.color,
                                 ((current_piece.x+x)*BLOCK_SIZE, (current_piece.y+y)*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, (0,0,0),
                                 ((current_piece.x+x)*BLOCK_SIZE, (current_piece.y+y)*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    pygame.display.update()
