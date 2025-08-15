import pygame
import random
import platform
import asyncio

# Pygame initialisieren
pygame.init()

# Spielfeldgröße und Konstanten
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
FPS = 60

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino-Formen
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

# Spielfeld
grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Bildschirm initialisieren
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

# Tetromino-Klasse
class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = COLORS[SHAPES.index(self.shape)]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.shape = list(zip(*reversed(self.shape)))

# Kollisionsprüfung
def check_collision(tetromino, grid, dx=0, dy=0):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetromino.x + x + dx
                new_y = tetromino.y + y + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x] != BLACK):
                    return True
    return False

# Zeilen löschen
def clear_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if all(cell != BLACK for cell in row)]
    for row in full_rows:
        grid.pop(row)
        grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
    return len(full_rows)

# Spielfeld zeichnen
def draw_grid(screen, grid, tetromino):
    screen.fill(BLACK)
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color != BLACK:
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, tetromino.color, ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, ((tetromino.x + x) * BLOCK_SIZE, (tetromino.y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# Spiel-Setup
def setup():
    global current_tetromino, game_over
    current_tetromino = Tetromino()
    game_over = False

# Spiel-Update
def update_loop():
    global current_tetromino, game_over
    if game_over:
        return

    # Ereignisse prüfen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and not check_collision(current_tetromino, grid, dx=-1):
                current_tetromino.move(-1, 0)
            if event.key == pygame.K_RIGHT and not check_collision(current_tetromino, grid, dx=1):
                current_tetromino.move(1, 0)
            if event.key == pygame.K_DOWN and not check_collision(current_tetromino, grid, dy=1):
                current_tetromino.move(0, 1)
            if event.key == pygame.K_UP:
                original_shape = current_tetromino.shape
                current_tetromino.rotate()
                if check_collision(current_tetromino, grid):
                    current_tetromino.shape = original_shape

    # Tetromino automatisch fallen lassen
    if not check_collision(current_tetromino, grid, dy=1):
        current_tetromino.move(0, 1)
    else:
        # Tetromino platzieren
        for y, row in enumerate(current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    if current_tetromino.y + y < 0:
                        game_over = True
                        return
                    grid[current_tetromino.y + y][current_tetromino.x + x] = current_tetromino.color
        clear_rows(grid)
        current_tetromino = Tetromino()
        if check_collision(current_tetromino, grid):
            game_over = True

    # Spielfeld zeichnen
    draw_grid(screen, grid, current_tetromino)
    pygame.display.flip()

# Hauptspielschleife
async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

# Pyodide-kompatible Ausführung
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())