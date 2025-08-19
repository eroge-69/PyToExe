
import pygame, random, sys, time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chromatic Lock")

# Colors
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 165, 0),
    (128, 0, 128)
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]

# Piece class
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# Grid setup
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

# Check if valid move
def valid_space(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, val in enumerate(row):
            if val:
                x = piece.x + j
                y = piece.y + i
                if x < 0 or x >= WIDTH // BLOCK_SIZE or y >= HEIGHT // BLOCK_SIZE:
                    return False
                if y >= 0 and grid[y][x] != (0, 0, 0):
                    return False
    return True

# Clear full rows
def clear_rows(grid, locked):
    cleared = 0
    for y in range(len(grid) - 1, -1, -1):
        if (0, 0, 0) not in grid[y]:
            cleared += 1
            for x in range(len(grid[y])):
                try:
                    del locked[(x, y)]
                except:
                    continue
    if cleared > 0:
        # shift rows down
        for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
            x, y = key
            if y < min([r for r in range(len(grid)) if (0, 0, 0) not in grid[r]]):
                continue
            if y < HEIGHT // BLOCK_SIZE:
                locked[(x, y + cleared)] = locked.pop((x, y))
    return cleared

# Draw grid
def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
    for j in range(len(grid[0])):
        pygame.draw.line(surface, (128, 128, 128), (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))

# Draw window
def draw_window(surface, grid, score, level):
    surface.fill((0, 0, 0))
    draw_grid(surface, grid)
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render(f"Score: {score}", 1, (255, 255, 255))
    surface.blit(label, (10, 10))
    lvl_label = font.render(f"Level: {level}", 1, (255, 255, 255))
    surface.blit(lvl_label, (10, 40))
    pygame.display.update()

# Ghost swap mechanic
def ghost_swap(locked_positions):
    if len(locked_positions) > 1:
        a, b = random.sample(list(locked_positions.keys()), 2)
        locked_positions[a], locked_positions[b] = locked_positions[b], locked_positions[a]

# Main loop
def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = Piece(3, 0, random.choice(SHAPES))
    next_piece = Piece(3, 0, random.choice(SHAPES))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0
    level = 1
    ghost_timer = time.time()

    score_thresholds = {1: 500, 2: 1500, 3: 3000, 4: 5000}

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        for _ in range(3):
                            current_piece.rotate()

        # Ghost mechanic at level 2+
        if level >= 2 and time.time() - ghost_timer > 15:
            ghost_swap(locked_positions)
            ghost_timer = time.time()

        shape_pos = []
        for i, row in enumerate(current_piece.shape):
            for j, val in enumerate(row):
                if val:
                    shape_pos.append((current_piece.x + j, current_piece.y + i))

        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(3, 0, random.choice(SHAPES))
            change_piece = False
            score += clear_rows(grid, locked_positions) * 100

        # Level progression based on score
        if level in score_thresholds and score >= score_thresholds[level]:
            level += 1
            fall_speed = max(0.1, fall_speed - 0.05)

        draw_window(screen, grid, score, level)

        if any(y < 1 for (x, y) in locked_positions):
            run = False

main()
