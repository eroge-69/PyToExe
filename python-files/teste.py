import pygame
import random
import sys

# Configurações
CELL_SIZE = 80
COLS, ROWS = 15, 11
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
PLAYER_SPEED = 3

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (30, 30, 30)
PLAYER_COLOR = (0, 200, 200)
GOAL_COLOR = (0, 255, 0)

COLOR_START = (0, 51, 102)
COLOR_GAMEOVER = (102, 0, 0)
COLOR_WIN = (0, 0, 0)

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labirinto")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 40)
small_font = pygame.font.SysFont("arial", 24)

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# Carregar sons
pygame.mixer.init()
music = pygame.mixer.music
music.load("jarabe_tapatio_fast.mp3")
music.set_volume(0.25)

sound_start = pygame.mixer.Sound("game_start_sound.wav")
sound_lose = pygame.mixer.Sound("game_over_sound.wav")
sound_win = pygame.mixer.Sound("game_win_sound.wav")
sound_win.set_volume(1.25)


class Maze:
    def __init__(self):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.generate_maze(0, 0)
        self.goal_positions = [
            (COLS - 2, ROWS - 2),
            (COLS - 1, ROWS - 2),
            (COLS - 2, ROWS - 1),
            (COLS - 1, ROWS - 1)
        ]
        for gx, gy in self.goal_positions:
            self.grid[gy][gx] = 0

    def generate_maze(self, cx, cy, visited=None):
        if visited is None:
            visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
        visited[cy][cx] = True
        self.grid[cy][cx] = 0

        dirs = DIRS[:]
        random.shuffle(dirs)

        for dx, dy in dirs:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < COLS and 0 <= ny < ROWS and not visited[ny][nx]:
                self.grid[cy + dy][cx + dx] = 0
                self.generate_maze(nx, ny, visited)

    def draw(self, surface):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = WALL_COLOR if self.grid[y][x] == 1 else WHITE
                pygame.draw.rect(surface, color, rect)

        for gx, gy in self.goal_positions:
            goal_rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GOAL_COLOR, goal_rect)

    def is_wall_at(self, px, py):
        grid_x = px // CELL_SIZE
        grid_y = py // CELL_SIZE
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            return self.grid[grid_y][grid_x] == 1
        return True

    def is_goal(self, rect):
        for gx, gy in self.goal_positions:
            goal_rect = pygame.Rect(gx * CELL_SIZE, gy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if rect.colliderect(goal_rect):
                return True
        return False


class Player:
    def __init__(self, maze):
        self.maze = maze
        self.size = CELL_SIZE // 2
        start_x = CELL_SIZE // 2 - self.size // 2
        start_y = CELL_SIZE // 2 - self.size // 2

        image_name = random.choice(["player1.png", "player2.png"])
        self.icon = pygame.image.load(image_name).convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (self.size, self.size))

        self.rect = self.icon.get_rect(topleft=(start_x, start_y))

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        corners = [
            (new_rect.left, new_rect.top),
            (new_rect.right - 1, new_rect.top),
            (new_rect.left, new_rect.bottom - 1),
            (new_rect.right - 1, new_rect.bottom - 1),
        ]
        for corner in corners:
            if self.maze.is_wall_at(*corner):
                return "lose"
        self.rect = new_rect
        if self.maze.is_goal(self.rect):
            return "win"
        return "ok"

    def draw(self, surface):
        surface.blit(self.icon, self.rect)


def draw_text_centered(surface, text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    surface.blit(text_surface, text_rect)


def show_screen(title, subtitle, bg_color, image_path=None):
    if image_path:
        try:
            background = pygame.image.load(image_path).convert()
            win.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        except:
            win.fill(bg_color)
    else:
        win.fill(bg_color)

    text_color = BLACK if title in ["Ganhaste!", "Game Over!"] else WHITE

    big_font = pygame.font.SysFont("arial", 80)
    medium_font = pygame.font.SysFont("arial", 40)

    draw_text_centered(win, title, big_font, text_color, y_offset=100)
    draw_text_centered(win, subtitle, medium_font, text_color, y_offset=200)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def main():
    game_state = "start"

    while True:
        if game_state == "start":
            sound_lose.stop()
            sound_win.stop()
            music.stop()
            sound_start.play()
            # Altere aqui o caminho para a imagem que deseja usar como fundo do ecrã inicial
            show_screen("Bem-vindo ao Labirinto!", "Prima ENTER para começar", COLOR_START, image_path="start_background.png")
            maze = Maze()
            player = Player(maze)
            music.play(-1)
            game_state = "playing"

        elif game_state == "playing":
            clock.tick(60)
            sound_start.stop()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_w]:
                dy = -PLAYER_SPEED
            elif keys[pygame.K_s]:
                dy = PLAYER_SPEED
            if keys[pygame.K_a]:
                dx = -PLAYER_SPEED
            elif keys[pygame.K_d]:
                dx = PLAYER_SPEED

            if dx != 0 or dy != 0:
                result = player.move(dx, dy)
                if result == "lose":
                    music.stop()
                    sound_lose.play()
                    game_state = "gameover"
                elif result == "win":
                    music.stop()
                    sound_win.play()
                    game_state = "win"

            win.fill(BLACK)
            maze.draw(win)
            player.draw(win)
            pygame.display.flip()

        elif game_state == "gameover":
            show_screen("Game Over!", "Prima ENTER para voltar ao menu", COLOR_GAMEOVER, image_path="lose_background.png")
            game_state = "start"

        elif game_state == "win":
            show_screen("Ganhaste!", "Prima ENTER para voltar ao menu", COLOR_WIN, image_path="win_background.png")
            game_state = "start"


if __name__ == "__main__":
    main()
