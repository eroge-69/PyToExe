import pygame
import random

# Konfiguration
WIDTH, HEIGHT = 800, 800
CELL_SIZE = 10
FPS = 10

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Gittergröße
cols = WIDTH // CELL_SIZE
rows = HEIGHT // CELL_SIZE

# Initialisiere Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()

# Gitter initialisieren
def create_grid(randomize=True):
    return [[random.randint(0, 1) if randomize else 0 for _ in range(cols)] for _ in range(rows)]

grid = create_grid(randomize=False)

# Zähle lebende Nachbarn
def count_neighbors(grid, x, y):
    neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            ni = (x + i + rows) % rows
            nj = (y + j + cols) % cols
            neighbors += grid[ni][nj]
    return neighbors

# Aktualisiere Gitter nach den Regeln
def update_grid(grid):
    new_grid = create_grid(randomize=False)
    for i in range(rows):
        for j in range(cols):
            alive = grid[i][j]
            neighbors = count_neighbors(grid, i, j)

            if alive:
                if neighbors == 2 or neighbors == 3:
                    new_grid[i][j] = 1
            else:
                if neighbors == 3:
                    new_grid[i][j] = 1
    return new_grid

# Zeichne das Gitter
def draw_grid(grid):
    screen.fill(BLACK)
    for i in range(rows):
        for j in range(cols):
            if grid[i][j]:
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
    # Steuerungshinweise anzeigen
    font = pygame.font.SysFont(None, 24)
    info_text = "Leertaste: Pause/Start   R: Reset   Linksklick: Zelle lebt   Rechtsklick: Zelle tot"
    text_surface = font.render(info_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 12))
    screen.blit(text_surface, text_rect)
    # Pause-Anzeige oben mittig
    if paused:
        pause_font = pygame.font.SysFont(None, 60)
        pause_surface = pause_font.render("Pause", True, (255, 0, 0))
        pause_rect = pause_surface.get_rect(center=(WIDTH // 2, 30))
        screen.blit(pause_surface, pause_rect)
    pygame.display.flip()

# Hauptloop
running = True
paused = True  # Startet im pausierten Modus
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                grid = create_grid(randomize=False)  # Reset: leeres Spielfeld
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            j = x // CELL_SIZE
            i = y // CELL_SIZE
            if event.button == 1:  # Linksklick
                grid[i][j] = 1
            elif event.button == 3:  # Rechtsklick
                grid[i][j] = 0

    if not paused:
        grid = update_grid(grid)

    draw_grid(grid)

pygame.quit()
