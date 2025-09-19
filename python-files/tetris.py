import pygame
import random

# Window and play area settings
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 700
PLAY_WIDTH, PLAY_HEIGHT = 300, 600  # 10 x 20 blocks
BLOCK_SIZE = PLAY_WIDTH // 10
TOP_LEFT_X = 30
TOP_LEFT_Y = 50
SIDE_PANEL_X = TOP_LEFT_X + PLAY_WIDTH + 40

# Colors
BLACK = (0, 0, 0)
GRAY = (45, 45, 45)
WHITE = (255, 255, 255)
BORDER = (30, 30, 30)
SHADOW = (70, 70, 70)
BG = (25, 25, 38)

COLORS = [
    (0, 255, 255),    # I
    (0, 0, 255),      # J
    (255, 165, 0),    # L
    (255, 255, 0),    # O
    (0, 255, 0),      # S
    (128, 0, 128),    # T
    (255, 0, 0)       # Z
]

SHAPES = [
    [[1, 1, 1, 1]],                              # I
    [[2, 0, 0], [2, 2, 2]],                      # J
    [[0, 0, 3], [3, 3, 3]],                      # L
    [[4, 4], [4, 4]],                            # O
    [[0, 5, 5], [5, 5, 0]],                      # S
    [[0, 6, 0], [6, 6, 6]],                      # T
    [[7, 7, 0], [0, 7, 7]],                      # Z
]

def rotate(shape):
    return [[shape[y][x] for y in range(len(shape))]
            for x in range(len(shape[0])-1, -1, -1)]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]

    def rotate(self):
        self.shape = rotate(self.shape)

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(10)] for _ in range(20)]
    for y in range(20):
        for x in range(10):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(shape):
    positions = []
    fmt = shape.shape
    for i, line in enumerate(fmt):
        for j, column in enumerate(line):
            if column != 0:
                positions.append((shape.x + j, shape.y + i))
    return positions

def valid_space(shape, grid):
    accepted_pos = [[(x, y) for x in range(10) if grid[y][x] == BLACK] for y in range(20)]
    accepted_pos = [x for sub in accepted_pos for x in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Tetromino(3, 0, random.choice(SHAPES))

def clear_rows(grid, locked):
    inc = 0
    for i in range(19, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            ind = i
            for j in range(10):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(
        label,
        (WINDOW_WIDTH // 2 - label.get_width() // 2, WINDOW_HEIGHT // 2 - label.get_height() // 2)
    )

def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(len(grid)):
        pygame.draw.line(surface, GRAY, (sx, sy + i*BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i*BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, GRAY, (sx + j*BLOCK_SIZE, sy), (sx + j*BLOCK_SIZE, sy + PLAY_HEIGHT))

def draw_3d_block(surface, x, y, color, size):
    pygame.draw.rect(surface, SHADOW, (x, y, size, size), border_radius=7)
    pygame.draw.rect(surface, color, (x+2, y+2, size-4, size-4), border_radius=7)
    highlight = tuple(min(255, int(c*1.3)) for c in color)
    pygame.draw.line(surface, highlight, (x+3, y+3), (x+size-6, y+3), 3)
    pygame.draw.line(surface, highlight, (x+3, y+3), (x+3, y+size-6), 3)

def draw_window(surface, grid, score=0, high_score=0, next_piece=None):
    surface.fill(BG)

    # Play area border
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X-6, TOP_LEFT_Y-6, PLAY_WIDTH+12, PLAY_HEIGHT+12), 4, border_radius=12)

    # Draw grid blocks
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            color = grid[i][j]
            if color != BLACK:
                bx = TOP_LEFT_X + j*BLOCK_SIZE
                by = TOP_LEFT_Y + i*BLOCK_SIZE
                draw_3d_block(surface, bx, by, color, BLOCK_SIZE)

    # Draw grid lines
    draw_grid(surface, grid)

    # Score Panel Background (taller)
    pygame.draw.rect(surface, (38,38,60), (SIDE_PANEL_X-20, TOP_LEFT_Y, 210, 370), border_radius=12)
    pygame.draw.rect(surface, WHITE, (SIDE_PANEL_X-20, TOP_LEFT_Y, 210, 370), 3, border_radius=12)

    # Score
    font = pygame.font.SysFont('consolas', 28, bold=True)
    label = font.render(f'Score', 1, WHITE)
    surface.blit(label, (SIDE_PANEL_X+34, TOP_LEFT_Y + 18))
    font_val = pygame.font.SysFont('consolas', 36, bold=True)
    score_label = font_val.render(f"{score}", 1, (255, 236, 100))
    surface.blit(score_label, (SIDE_PANEL_X+32, TOP_LEFT_Y + 50))

    # High Score
    font = pygame.font.SysFont('consolas', 22, bold=True)
    label = font.render(f'High Score', 1, WHITE)
    surface.blit(label, (SIDE_PANEL_X+8, TOP_LEFT_Y + 105))
    font_val = pygame.font.SysFont('consolas', 25, bold=True)
    score_label = font_val.render(f"{high_score}", 1, (180, 230, 255))
    surface.blit(score_label, (SIDE_PANEL_X+42, TOP_LEFT_Y + 135))

    # Next Piece
    font = pygame.font.SysFont('consolas', 25, bold=True)
    label = font.render('Next', 1, WHITE)
    surface.blit(label, (SIDE_PANEL_X+46, TOP_LEFT_Y + 190))

    if next_piece:
        fmt = next_piece.shape
        for i, line in enumerate(fmt):
            for j, column in enumerate(line):
                if column:
                    bx = SIDE_PANEL_X+30 + j*BLOCK_SIZE
                    by = TOP_LEFT_Y + 230 + i*BLOCK_SIZE
                    draw_3d_block(surface, bx, by, next_piece.color, BLOCK_SIZE)

def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.25

    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    score = 0
    high_score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(60)

        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        for _ in range(3):
                            current_piece.rotate()
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            score += [0, 40, 100, 300, 1200][cleared]  # Tetris scoring
            if score > high_score:
                high_score = score

        draw_window(win, grid, score, high_score, next_piece)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, 'GAME OVER', 55, (255, 80, 80))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

if __name__ == '__main__':
    main()