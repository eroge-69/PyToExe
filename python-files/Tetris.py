import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
FPS = 60
PANEL_WIDTH = 5  # Grid units for left panel (preview, score, controls)

# Resolution options (width, height)
RESOLUTIONS = [(450, 600), (600, 800), (300, 400)]
RESOLUTION_INDEX = 0  # Default to 450x600
WIDTH, HEIGHT = RESOLUTIONS[RESOLUTION_INDEX]
GRID_SIZE = (WIDTH - PANEL_WIDTH * (WIDTH // (GRID_WIDTH + PANEL_WIDTH))) // GRID_WIDTH

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY1 = (50, 50, 50)
GRAY2 = (100, 100, 100)
GRAY3 = (150, 150, 150)
GRAY4 = (200, 200, 200)
GRAY5 = (80, 80, 80)
GRAY6 = (120, 120, 120)
GRAY7 = (180, 180, 180)

# Colorful tetromino colors
COLORFUL_SHAPE_COLORS = [
    (0, 255, 255),  # Cyan (I)
    (255, 255, 0),  # Yellow (O)
    (255, 0, 255),  # Magenta (T)
    (255, 165, 0),  # Orange (L)
    (0, 0, 255),    # Blue (J)
    (0, 255, 0),    # Green (S)
    (255, 0, 0)     # Red (Z)
]

# Black-and-white tetromino colors
BW_SHAPE_COLORS = [GRAY1, GRAY2, GRAY3, GRAY4, GRAY5, GRAY6, GRAY7]

# Current color mode
COLOR_MODE = "colorful"  # Options: "colorful", "bw"
SHAPE_COLORS = COLORFUL_SHAPE_COLORS

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]

# Game state
board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = None
next_piece = None
current_pos = [0, 0]
score = 0
game_state = "menu"  # Possible states: "menu", "playing", "game_over", "settings"
menu_selection = 0  # 0: Start Game, 1: Settings
settings_selection = 0  # 0: Resolution, 1: Color Mode, 2: Back

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def update_resolution():
    global WIDTH, HEIGHT, GRID_SIZE, screen
    WIDTH, HEIGHT = RESOLUTIONS[RESOLUTION_INDEX]
    GRID_SIZE = (WIDTH - PANEL_WIDTH * (WIDTH // (GRID_WIDTH + PANEL_WIDTH))) // GRID_WIDTH
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

def create_piece():
    index = random.randint(0, len(SHAPES) - 1)
    return SHAPES[index], SHAPE_COLORS[index]

def valid_move(piece, pos, dx=0, dy=0):
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                new_x = pos[0] + x + dx
                new_y = pos[1] + y + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and board[new_y][new_x] != BLACK):
                    return False
    return True

def merge_piece():
    global board
    for y, row in enumerate(current_piece[0]):
        for x, cell in enumerate(row):
            if cell:
                board[current_pos[1] + y][current_pos[0] + x] = current_piece[1]

def clear_lines():
    global board, score
    lines_cleared = 0
    new_board = [row for row in board if any(cell == BLACK for cell in row)]
    lines_cleared = GRID_HEIGHT - len(new_board)
    score += lines_cleared * 100
    board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(lines_cleared)] + new_board

def rotate_piece():
    global current_piece, current_pos
    piece = current_piece[0]
    height = len(piece)
    width = len(piece[0])
    rotated = [[0 for _ in range(height)] for _ in range(width)]
    for y in range(height):
        for x in range(width):
            rotated[width - 1 - x][y] = piece[y][x]
    
    new_pos = current_pos.copy()
    if new_pos[0] + len(rotated[0]) > GRID_WIDTH:
        new_pos[0] = GRID_WIDTH - len(rotated[0])
    if new_pos[0] < 0:
        new_pos[0] = 0
    if valid_move(rotated, new_pos):
        current_piece = (rotated, current_piece[1])
        current_pos[0] = new_pos[0]

def reset_game():
    global board, current_piece, next_piece, current_pos, score, game_state
    board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_piece = create_piece()
    next_piece = create_piece()
    current_pos = [GRID_WIDTH // 2 - len(current_piece[0][0]) // 2, 0]
    score = 0
    if not valid_move(current_piece[0], current_pos):
        game_state = "game_over"

def setup():
    global game_state
    reset_game()
    game_state = "playing"

def draw_menu():
    screen.fill(BLACK)
    fontT = pygame.font.Font(None, int(HEIGHT / 6))
    font = pygame.font.Font(None, int(HEIGHT / 12))
    title_text = fontT.render("Tetris", True, WHITE)
    start_text = font.render("> Start Game" if menu_selection == 0 else "  Start Game", True, WHITE)
    settings_text = font.render("> Settings" if menu_selection == 1 else "  Settings", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    screen.blit(settings_text, (WIDTH // 2 - settings_text.get_width() // 2, HEIGHT * 2 // 3))
    pygame.display.flip()

def draw_settings():
    screen.fill(BLACK)
    font = pygame.font.Font(None, int(HEIGHT / 18))
    resolution_text = font.render(f"> Resolution: {RESOLUTIONS[RESOLUTION_INDEX][0]}x{RESOLUTIONS[RESOLUTION_INDEX][1]}" if settings_selection == 0 else f"  Resolution: {RESOLUTIONS[RESOLUTION_INDEX][0]}x{RESOLUTIONS[RESOLUTION_INDEX][1]}", True, WHITE)
    color_text = font.render(f"> Color Mode: {'Colorful' if COLOR_MODE == 'colorful' else 'Black & White'}" if settings_selection == 1 else f"  Color Mode: {'Colorful' if COLOR_MODE == 'colorful' else 'Black & White'}", True, WHITE)
    back_text = font.render("> Back" if settings_selection == 2 else "  Back", True, WHITE)
    screen.blit(resolution_text, (WIDTH // 2 - resolution_text.get_width() // 2, HEIGHT // 3))
    screen.blit(color_text, (WIDTH // 2 - color_text.get_width() // 2, HEIGHT // 2))
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT * 2 // 3))
    pygame.display.flip()

def draw_game_over():
    screen.fill(BLACK)
    fontT = pygame.font.Font(None, int(HEIGHT / 6))
    font = pygame.font.Font(None, int(HEIGHT / 12))
    game_over_text = fontT.render("Game Over!", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    menu_text = font.render("Press Enter for Menu", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT * 2 // 3))
    pygame.display.flip()

def draw_game():
    screen.fill(BLACK)
    # Draw separator line
    pygame.draw.line(screen, WHITE, (PANEL_WIDTH * GRID_SIZE - 5, 0), (PANEL_WIDTH * GRID_SIZE - 5, HEIGHT), int(GRID_SIZE / 5))

    # Draw game grid (shifted right to accommodate left panel)
    grid_offset_x = PANEL_WIDTH * GRID_SIZE
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell != BLACK:
                pygame.draw.rect(screen, cell, (grid_offset_x + x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
    for y, row in enumerate(current_piece[0]):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current_piece[1], (grid_offset_x + (current_pos[0] + x) * GRID_SIZE, (current_pos[1] + y) * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

    # Draw left panel (next piece, score, controls)
    fontT = pygame.font.Font(None, int(HEIGHT / 10))
    fontS = pygame.font.Font(None, int(HEIGHT / 20))
    font = pygame.font.Font(None, int(HEIGHT / 30))
    # Next piece preview
    next_text = fontT.render("Next:", True, WHITE)
    screen.blit(next_text, (10, 10))
    for y, row in enumerate(next_piece[0]):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_piece[1], (15 + x * GRID_SIZE, 60 + y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

    # Score
    score_text = fontS.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 150))

    # Controls
    controls = [
        "Left/Right: Move",
        "Up: Rotate",
        "Down: Go Down",
        "Space: Drop"
    ]
    for i, text in enumerate(controls):
        control_text = font.render(text, True, WHITE)
        screen.blit(control_text, (10, 200 + i * (HEIGHT / 20)))

    pygame.display.flip()

def update_loop():
    global current_pos, current_piece, next_piece, game_state, menu_selection, settings_selection, COLOR_MODE, SHAPE_COLORS, RESOLUTION_INDEX
    if game_state == "menu":
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_selection = (menu_selection - 1) % 2
                if event.key == pygame.K_DOWN:
                    menu_selection = (menu_selection + 1) % 2
                if event.key == pygame.K_RETURN:
                    if menu_selection == 0:
                        setup()
                    else:
                        game_state = "settings"
                        settings_selection = 0
        return False

    if game_state == "settings":
        draw_settings()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    settings_selection = (settings_selection - 1) % 3
                if event.key == pygame.K_DOWN:
                    settings_selection = (settings_selection + 1) % 3
                if event.key == pygame.K_RETURN:
                    if settings_selection == 0:
                        RESOLUTION_INDEX = (RESOLUTION_INDEX + 1) % len(RESOLUTIONS)
                        update_resolution()
                    elif settings_selection == 1:
                        COLOR_MODE = "bw" if COLOR_MODE == "colorful" else "colorful"
                        SHAPE_COLORS = BW_SHAPE_COLORS if COLOR_MODE == "bw" else COLORFUL_SHAPE_COLORS
                    elif settings_selection == 2:
                        game_state = "menu"
        return False

    if game_state == "game_over":
        draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "menu"
        return False

    # Game playing state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid_move(current_piece[0], current_pos, dx=-1):
                current_pos[0] -= 1
            if event.key == pygame.K_RIGHT and valid_move(current_piece[0], current_pos, dx=1):
                current_pos[0] += 1
            if event.key == pygame.K_DOWN and valid_move(current_piece[0], current_pos, dy=1):
                current_pos[1] += 1
            if event.key == pygame.K_UP:
                rotate_piece()
            if event.key == pygame.K_SPACE:
                while valid_move(current_piece[0], current_pos, dy=1):
                    current_pos[1] += 1
                merge_piece()
                clear_lines()
                current_piece = next_piece
                next_piece = create_piece()
                current_pos = [GRID_WIDTH // 2 - len(current_piece[0][0]) // 2, 0]
                if not valid_move(current_piece[0], current_pos):
                    game_state = "game_over"

    # Move piece down
    if pygame.time.get_ticks() % 60 == 0:
        if valid_move(current_piece[0], current_pos, dy=1):
            current_pos[1] += 1
        else:
            merge_piece()
            clear_lines()
            current_piece = next_piece
            next_piece = create_piece()
            current_pos = [GRID_WIDTH // 2 - len(current_piece[0][0]) // 2, 0]
            if not valid_move(current_piece[0], current_pos):
                game_state = "game_over"

    draw_game()
    return False

async def main():
    while True:
        if update_loop():
            break
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())