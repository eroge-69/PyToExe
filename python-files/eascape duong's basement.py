import pygame
import sys
import random
import heapq


# --- Constants ---
WIDTH, HEIGHT = 960, 704
TILE_SIZE = 32
MAZE_ROWS = HEIGHT // TILE_SIZE
MAZE_COLS = WIDTH // TILE_SIZE
PLAYER_SIZE = TILE_SIZE
ENEMY_SIZE = TILE_SIZE
PLAYER_SPEED = 4
ENEMY_SPEED = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
WALL_COLOR = (40, 40, 40)

FLASHLIGHT_RADIUS = 80
NUM_KEYS = 20

# --- Load Images & Sounds ---
pygame.init()
pygame.mixer.init()
PLAYER_IMG = pygame.image.load("player.png")
ENEMY_IMG = pygame.image.load("enemy.png")
KEY_IMG = pygame.image.load("key.png")
WALL_IMG = pygame.image.load("wall.png")
BG_MUSIC = "bg_music.mp3"
JUMPSCARE_SOUND = pygame.mixer.Sound("jumpscare.wav")

# --- Maze Generation ---
def generate_maze():
    maze = [[1]*MAZE_COLS]
    for r in range(1, MAZE_ROWS-1):
        row = [1] + [0]*(MAZE_COLS-2) + [1]
        maze.append(row)
    maze.append([1]*MAZE_COLS)
    for _ in range(180):
        r = random.randint(2, MAZE_ROWS-3)
        c = random.randint(2, MAZE_COLS-3)
        maze[r][c] = 1
    return maze

maze = generate_maze()

def is_wall(x, y):
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
        return maze[row][col] == 1
    return True

def is_open_area(r, c, size=1):
    for dr in range(-size, size+1):
        for dc in range(-size, size+1):
            rr = r + dr
            cc = c + dc
            if rr < 1 or rr >= MAZE_ROWS-1 or cc < 1 or cc >= MAZE_COLS-1:
                return False
            if maze[rr][cc] == 1:
                return False
    return True

def find_open_position():
    attempts = 0
    while attempts < 1000:
        r = random.randint(2, MAZE_ROWS-3)
        c = random.randint(2, MAZE_COLS-3)
        if maze[r][c] == 0 and is_open_area(r, c, size=1):
            return r, c
        attempts += 1
    return 2, 2

# --- Classes ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        # Try move X
        new_rect = self.rect.move(dx, 0)
        if not is_wall(new_rect.x, new_rect.y) and not is_wall(new_rect.x + PLAYER_SIZE - 1, new_rect.y):
            self.rect.x = new_rect.x
        # Try move Y
        new_rect = self.rect.move(0, dy)
        if not is_wall(new_rect.x, new_rect.y) and not is_wall(new_rect.x, new_rect.y + PLAYER_SIZE - 1):
            self.rect.y = new_rect.y

    def draw(self, screen):
        screen.blit(PLAYER_IMG, self.rect)

class Key:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE // 2, TILE_SIZE // 2)
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            screen.blit(KEY_IMG, self.rect)

def astar(start, goal, maze):
    rows, cols = len(maze), len(maze[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        for dr, dc in directions:
            neighbor = (current[0]+dr, current[1]+dc)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] == 0:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
    return []

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.path = []

    def chase(self, target_rect):
        enemy_grid = (self.rect.y // TILE_SIZE, self.rect.x // TILE_SIZE)
        player_grid = (target_rect.y // TILE_SIZE, target_rect.x // TILE_SIZE)
        if not self.path or self.path[-1] != player_grid:
            self.path = astar(enemy_grid, player_grid, maze)
        if self.path:
            next_pos = self.path[0]
            next_x, next_y = next_pos[1]*TILE_SIZE, next_pos[0]*TILE_SIZE
            dx = dy = 0
            if self.rect.x < next_x:
                dx = ENEMY_SPEED
            elif self.rect.x > next_x:
                dx = -ENEMY_SPEED
            if self.rect.y < next_y:
                dy = ENEMY_SPEED
            elif self.rect.y > next_y:
                dy = -ENEMY_SPEED
            # Try move X
            new_rect = self.rect.move(dx, 0)
            if not is_wall(new_rect.x, new_rect.y) and not is_wall(new_rect.x + ENEMY_SIZE - 1, new_rect.y):
                self.rect.x = new_rect.x
            # Try move Y
            new_rect = self.rect.move(0, dy)
            if not is_wall(new_rect.x, new_rect.y) and not is_wall(new_rect.x, new_rect.y + ENEMY_SIZE - 1):
                self.rect.y = new_rect.y
            if self.rect.x == next_x and self.rect.y == next_y:
                self.path.pop(0)

    def draw(self, screen):
        screen.blit(ENEMY_IMG, self.rect)

# --- UI & Effects ---
def show_jumpscare(screen):
    pygame.mixer.music.stop()
    JUMPSCARE_SOUND.play()
    font = pygame.font.SysFont(None, 80)
    text = font.render("DUONG CAUGHT YOU", True, WHITE)
    screen.fill(RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(2000)
    JUMPSCARE_SOUND.stop()

def show_escape(screen):
    font = pygame.font.SysFont(None, 80)
    text = font.render("TRIS ESCAPED!", True, WHITE)
    screen.fill(GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(2000)

def draw_maze(screen):
    for r in range(MAZE_ROWS):
        for c in range(MAZE_COLS):
            if maze[r][c] == 1:
                screen.blit(WALL_IMG, (c*TILE_SIZE, r*TILE_SIZE))

def draw_flashlight(screen, player_rect):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    pygame.draw.circle(overlay, (0, 0, 0, 0), player_rect.center, FLASHLIGHT_RADIUS)
    screen.blit(overlay, (0, 0))

def menu(screen):
    font = pygame.font.SysFont(None, 80)
    small_font = pygame.font.SysFont(None, 40)
    while True:
        screen.fill(BLACK)
        title = font.render("Eascape Duong's basement", True, WHITE)
        start = small_font.render("Press [ENTER] to START", True, WHITE)
        quit_ = small_font.render("Press [ESC] to QUIT", True, WHITE)
        by_ = small_font.render("by Cao Bad Dat", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2))
        screen.blit(quit_, (WIDTH//2 - quit_.get_width()//2, HEIGHT//2 + 50))
        screen.blit(by_, (WIDTH//2 - quit_.get_width()//2, HEIGHT//2 + 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# --- Main Game ---
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Horror Maze Game")

    pygame.mixer.music.load(BG_MUSIC)
    pygame.mixer.music.play(-1)

    menu(screen)

    pr, pc = find_open_position()
    player = Player(pc*TILE_SIZE, pr*TILE_SIZE)

    while True:
        er, ec = find_open_position()
        if abs(er - pr) + abs(ec - pc) > max(MAZE_ROWS, MAZE_COLS) // 2:
            break
    enemy = Enemy(ec*TILE_SIZE, er*TILE_SIZE)

    keys_list = []
    placed = 0
    while placed < NUM_KEYS:
        r = random.randint(1, MAZE_ROWS-2)
        c = random.randint(1, MAZE_COLS-2)
        if maze[r][c] == 0:
            key_rect = pygame.Rect(c*TILE_SIZE+TILE_SIZE//4, r*TILE_SIZE+TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2)
            if not key_rect.colliderect(player.rect) and not key_rect.colliderect(enemy.rect):
                keys_list.append(Key(c*TILE_SIZE+TILE_SIZE//4, r*TILE_SIZE+TILE_SIZE//4))
                placed += 1

    clock = pygame.time.Clock()
    running = True
    died = False
    escaped = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not died and not escaped:
            keys = pygame.key.get_pressed()
            player.move(keys)
            enemy.chase(player.rect)

            for key in keys_list:
                if not key.collected and player.rect.colliderect(key.rect):
                    key.collected = True

            if all(key.collected for key in keys_list):
                show_escape(screen)
                escaped = True

            if player.rect.colliderect(enemy.rect):
                show_jumpscare(screen)
                died = True

            screen.fill(BLACK)
            draw_maze(screen)
            for key in keys_list:
                key.draw(screen)
            player.draw(screen)
            enemy.draw(screen)
            draw_flashlight(screen, player.rect)

            font = pygame.font.SysFont(None, 32)
            text = font.render(f"Keys: {sum(k.collected for k in keys_list)}/{NUM_KEYS}", True, WHITE)
            screen.blit(text, (10, 10))

            pygame.display.flip()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()