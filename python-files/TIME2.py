import pygame
import random

# Game configuration
s_width, s_height = 300, 600
play_width, play_height = 200, 400
block_size = 20
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# Define the shapes (4×4 matrices) and their rotations
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255,   0),
    (255, 0,   0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0,   0, 255),
    (128,   0, 128)
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(play_width // block_size)] for _ in range(play_height // block_size)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, char in enumerate(row):
            if char == '0':
                positions.append((piece.x + j, piece.y + i))
    # Offset to remove padding
    positions = [(x - 2, y - 4) for (x, y) in positions]
    return positions


def valid_space(piece, grid):
    accepted_positions = [
        (j, i) for i, row in enumerate(grid) for j, col in enumerate(row) if col == (0, 0, 0)
    ]
    for pos in convert_shape_format(piece):
        if pos not in accepted_positions and pos[1] > -1:
            return False
    return True


def check_lost(positions):
    for _, y in positions:
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(play_width // block_size // 2, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (
        top_left_x + play_width / 2 - label.get_width() / 2,
        top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (top_left_x + j * block_size,
                 top_left_y + i * block_size,
                 block_size, block_size),
                0
            )
    # grid lines
    for i in range(len(grid)):
        pygame.draw.line(
            surface, (128, 128, 128),
            (top_left_x, top_left_y + i * block_size),
            (top_left_x + play_width, top_left_y + i * block_size)
        )
    for j in range(len(grid[0])):
        pygame.draw.line(
            surface, (128, 128, 128),
            (top_left_x + j * block_size, top_left_y),
            (top_left_x + j * block_size, top_left_y + play_height)
        )


def clear_rows(grid, locked):
    # check each row and clear if full
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        if (0, 0, 0) not in grid[i]:
            inc += 1
            ind = i
            for j in range(len(grid[i])):
                try:
                    del locked[(j, i)]
                except KeyError:
                    pass
    if inc > 0:
        # shift all rows above down
        for key in sorted(locked.keys(), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked[new_key] = locked.pop(key)
    return inc


def draw_window(surface, grid):
    surface.fill((0, 0, 0))
    # play area border
    pygame.draw.rect(
        surface, (255, 0, 0),
        (top_left_x, top_left_y, play_width, play_height), 4
    )
    draw_grid(surface, grid)


def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5

    pygame.init()
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

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
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        # lock piece and spawn next
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            clear_rows(grid, locked_positions)

            if check_lost(locked_positions):
                draw_text_middle(win, "YOU LOST!", 60, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(2000)
                run = False

        draw_window(win, grid)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
