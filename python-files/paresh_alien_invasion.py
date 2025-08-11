import pygame
import sys
import heapq
from collections import deque

# ---------------- Settings ----------------
WIDTH, HEIGHT = 800, 600
ROWS, COLS = 20, 25
CELL_SIZE = WIDTH // COLS
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alien Invasion Defense - A* vs BFS")
clock = pygame.time.Clock()

# ---------------- Grid ----------------
grid = [["empty" for _ in range(COLS)] for _ in range(ROWS)]
start = (ROWS - 1, COLS // 2)  # Base position
goal = (0, COLS // 2)          # Alien spawn position

# ---------------- Helper Functions ----------------
def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (r, c) == start:
                pygame.draw.rect(screen, GREEN, rect)
            elif (r, c) == goal:
                pygame.draw.rect(screen, RED, rect)
            elif grid[r][c] == "wall":
                pygame.draw.rect(screen, BLACK, rect)
            elif grid[r][c] == "open":
                pygame.draw.rect(screen, BLUE, rect)
            elif grid[r][c] == "closed":
                pygame.draw.rect(screen, YELLOW, rect)
            elif grid[r][c] == "path":
                pygame.draw.rect(screen, PURPLE, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, GREY, rect, 1)

def neighbors(r, c):
    for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != "wall":
            yield nr, nc

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ---------------- BFS ----------------
def bfs():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] in ("open", "closed", "path"):
                grid[r][c] = "empty"
    queue = deque([start])
    came_from = {start: None}
    grid[start[0]][start[1]] = "closed"

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for nb in neighbors(*current):
            if nb not in came_from:
                came_from[nb] = current
                queue.append(nb)
                grid[nb[0]][nb[1]] = "open"
        draw_grid()
        pygame.display.flip()
        clock.tick(FPS)
        grid[current[0]][current[1]] = "closed"

    # Reconstruct path
    if goal in came_from:
        cur = goal
        while cur != start:
            if cur != goal:
                grid[cur[0]][cur[1]] = "path"
            cur = came_from[cur]

# ---------------- A* ----------------
def astar():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] in ("open", "closed", "path"):
                grid[r][c] = "empty"
    open_set = []
    heapq.heappush(open_set, (0 + manhattan(start, goal), 0, start))
    came_from = {start: None}
    g_score = {start: 0}

    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            break
        grid[current[0]][current[1]] = "closed"

        for nb in neighbors(*current):
            tentative_g = g_score[current] + 1
            if nb not in g_score or tentative_g < g_score[nb]:
                came_from[nb] = current
                g_score[nb] = tentative_g
                f_score = tentative_g + manhattan(nb, goal)
                heapq.heappush(open_set, (f_score, tentative_g, nb))
                if grid[nb[0]][nb[1]] != "closed":
                    grid[nb[0]][nb[1]] = "open"

        draw_grid()
        pygame.display.flip()
        clock.tick(FPS)

    # Reconstruct path
    if goal in came_from:
        cur = goal
        while cur != start:
            if cur != goal:
                grid[cur[0]][cur[1]] = "path"
            cur = came_from[cur]

# ---------------- Main Loop ----------------
algo = "astar"
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if pygame.mouse.get_pressed()[0]:  # Left-click: wall
            mx, my = pygame.mouse.get_pos()
            c, r = mx // CELL_SIZE, my // CELL_SIZE
            if (r, c) != start and (r, c) != goal:
                grid[r][c] = "wall"

        if pygame.mouse.get_pressed()[2]:  # Right-click: remove wall
            mx, my = pygame.mouse.get_pos()
            c, r = mx // CELL_SIZE, my // CELL_SIZE
            if grid[r][c] == "wall":
                grid[r][c] = "empty"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                algo = "astar"
                astar()
            elif event.key == pygame.K_b:
                algo = "bfs"
                bfs()
            elif event.key == pygame.K_r:
                for r in range(ROWS):
                    for c in range(COLS):
                        grid[r][c] = "empty"

    screen.fill(WHITE)
    draw_grid()
    pygame.display.flip()
    clock.tick(FPS)
