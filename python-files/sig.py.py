import pygame
import random
import sys
import math
from pygame import mixer
from pygame.locals import *

# Инициализация Pygame
pygame.init()
mixer.init()

# Настройки окна
INITIAL_WIDTH, INITIAL_HEIGHT = 1560, 900
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Блок-пазл")

# Константы
GRID_Y_OFFSET = 150
UI_MARGIN = 20
BACKGROUND_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_SIZE = 10
MIN_CELL_SIZE = 30
DEFAULT_CELL_SIZE = 50
PINK = (255, 105, 180)  # Розовый цвет для кнопки Тетриса
TICTACTOE_GRID_SIZE = 12  #  поле для крестиков-ноликов
WIN_CONDITION = 5  # Сколько нужно в ряд для победы

# Звуки
try:
    place_sound = mixer.Sound("place.wav")
    clear_sound = mixer.Sound("clear.wav")
    has_sound = True
except:
    print("Звуки не загружены")
    has_sound = False

# Фигуры для разных уровней
SHAPES_BY_LEVEL = [
    [[(0, 0)], [(0, 0), (1, 0)], [(0, 0), (0, 1)]],
    [[(0, 0), (0, 1), (1, 0)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 0), (2, 0)]],
    [[(0, 0), (0, 1), (1, 1), (1, 0)], [(0, 0), (1, 0), (1, 1), (2, 1)], [(0, 1), (1, 1), (1, 0), (2, 0)]],
    [[(0, 0), (0, 1), (0, 2), (1, 0)], [(0, 0), (0, 1), (0, 2), (1, 2)], [(0, 0), (1, 0), (2, 0), (1, 1)]],
    [[(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 0), (0, 1), (0, 2), (0, 3)],
     [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)], [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]]
]

# Классические тетромино
TETROMINOES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Цвета фигур
COLORS = [
    (243, 134, 48), (66, 135, 245), (248, 231, 28), (123, 201, 123),
    (173, 105, 237), (237, 67, 55), (0, 200, 200), (255, 105, 180)
]

class Particle:
    def __init__(self, x, y, color, cell_size):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, max(3, cell_size // 10))
        self.speed = random.uniform(1, 5)
        self.angle = random.uniform(0, math.pi * 2)
        self.life = random.randint(20, 40)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.gravity = 0.1
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
    
    def draw(self, surface):
        alpha = min(255, self.life * 6)
        color = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))
    
    def is_dead(self):
        return self.life <= 0

class Block:
    def __init__(self, shape, color, x, y, cell_size):
        self.shape = shape
        self.color = color
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.held = False
        self.offset_x = 0
        self.offset_y = 0

    def update_cell_size(self, new_cell_size):
        scale_factor = new_cell_size / self.cell_size
        self.x = self.x * scale_factor
        self.y = self.y * scale_factor
        self.cell_size = new_cell_size

    def draw(self, surface):
        for dx, dy in self.shape:
            rect = pygame.Rect(
                self.x + dx * self.cell_size,
                self.y + dy * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, max(1, self.cell_size // 25))

    def rotate(self):
        new_shape = [(-dy, dx) for dx, dy in self.shape]
        max_x = max(dx for dx, dy in new_shape)
        max_y = max(dy for dx, dy in new_shape)
        
        if (0 <= self.x + max_x * self.cell_size < pygame.display.get_surface().get_width() and
            0 <= self.y + max_y * self.cell_size < pygame.display.get_surface().get_height()):
            self.shape = new_shape

class TetrisBlock:
    def __init__(self, shape, color, x, y, cell_size):
        self.shape = shape
        self.color = color
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.rotation = 0
    
    def get_rotated_shape(self):
        if not self.shape:
            return []
        
        rotated = []
        if self.rotation % 4 == 0:
            return self.shape
        elif self.rotation % 4 == 1:
            for i in range(len(self.shape[0])):
                rotated.append([row[i] for row in self.shape[::-1]])
        elif self.rotation % 4 == 2:
            rotated = [row[::-1] for row in self.shape[::-1]]
        elif self.rotation % 4 == 3:
            for i in range(len(self.shape[0])-1, -1, -1):
                rotated.append([row[i] for row in self.shape])
        return rotated
    
    def rotate(self):
        self.rotation += 1
    
    def draw(self, surface):
        shape = self.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        self.x + x * self.cell_size,
                        self.y + y * self.cell_size,
                        self.cell_size, self.cell_size
                    )
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, BLACK, rect, max(1, self.cell_size // 25))

class Grid:
    def __init__(self, cell_size):
        self.cells = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.particles = []
        self.cell_size = cell_size
    
    def update_cell_size(self, new_cell_size):
        self.cell_size = new_cell_size
    
    def get_grid_offset(self, screen_width):
        return (screen_width - GRID_SIZE * self.cell_size) // 2
    
    def draw(self, surface):
        screen_width = surface.get_width()
        grid_x_offset = self.get_grid_offset(screen_width)
        
        pygame.draw.rect(
            surface, (40, 40, 40),
            (grid_x_offset, GRID_Y_OFFSET, 
             GRID_SIZE * self.cell_size, GRID_SIZE * self.cell_size)
        )
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    grid_x_offset + x * self.cell_size,
                    GRID_Y_OFFSET + y * self.cell_size,
                    self.cell_size, self.cell_size
                )
                if self.cells[y][x]:
                    pygame.draw.rect(surface, self.cells[y][x], rect)
                pygame.draw.rect(surface, GRID_COLOR, rect, max(1, self.cell_size // 25))
        
        for particle in self.particles[:]:
            particle.draw(surface)
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
    
    def create_particles(self, x, y, color):
        for _ in range(20):
            self.particles.append(Particle(x, y, color, self.cell_size))
    
    def clear_line(self, y, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        for x in range(GRID_SIZE):
            if self.cells[y][x]:
                center_x = grid_x_offset + x * self.cell_size + self.cell_size // 2
                center_y = GRID_Y_OFFSET + y * self.cell_size + self.cell_size // 2
                self.create_particles(center_x, center_y, self.cells[y][x])
        self.cells[y] = [None] * GRID_SIZE
    
    def clear_column(self, x, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        for y in range(GRID_SIZE):
            if self.cells[y][x]:
                center_x = grid_x_offset + x * self.cell_size + self.cell_size // 2
                center_y = GRID_Y_OFFSET + y * self.cell_size + self.cell_size // 2
                self.create_particles(center_x, center_y, self.cells[y][x])
            self.cells[y][x] = None
    
    def can_place(self, block, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        for dx, dy in block.shape:
            grid_x = int((block.x - grid_x_offset + block.cell_size/2) / block.cell_size) + dx
            grid_y = int((block.y - GRID_Y_OFFSET + block.cell_size/2) / block.cell_size) + dy
            
            if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
                return False
            if self.cells[grid_y][grid_x]:
                return False
        return True
    
    def can_place_tetromino(self, tetromino, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        shape = tetromino.get_rotated_shape()
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = int((tetromino.x - grid_x_offset) / tetromino.cell_size) + x
                    grid_y = int((tetromino.y - GRID_Y_OFFSET) / tetromino.cell_size) + y
                    
                    if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
                        return False
                    if self.cells[grid_y][grid_x]:
                        return False
        return True
    
    def place_block(self, block, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        placed_positions = []
        
        for dx, dy in block.shape:
            grid_x = int((block.x - grid_x_offset + block.cell_size/2) / block.cell_size) + dx
            grid_y = int((block.y - GRID_Y_OFFSET + block.cell_size/2) / block.cell_size) + dy
            
            if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
                return False
            if self.cells[grid_y][grid_x]:
                return False
            placed_positions.append((grid_x, grid_y))
        
        for grid_x, grid_y in placed_positions:
            self.cells[grid_y][grid_x] = block.color
        
        lines_cleared = 0
        for y in range(GRID_SIZE):
            if all(self.cells[y]):
                self.clear_line(y, screen_width)
                lines_cleared += 1
        
        for x in range(GRID_SIZE):
            if all(self.cells[y][x] is not None for y in range(GRID_SIZE)):
                self.clear_column(x, screen_width)
                lines_cleared += 1
        
        return lines_cleared
    
    def place_tetromino(self, tetromino, screen_width):
        grid_x_offset = self.get_grid_offset(screen_width)
        shape = tetromino.get_rotated_shape()
        placed_positions = []
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = int((tetromino.x - grid_x_offset) / tetromino.cell_size) + x
                    grid_y = int((tetromino.y - GRID_Y_OFFSET) / tetromino.cell_size) + y
                    
                    if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
                        return False
                    if self.cells[grid_y][grid_x]:
                        return False
                    placed_positions.append((grid_x, grid_y))
        
        for grid_x, grid_y in placed_positions:
            self.cells[grid_y][grid_x] = tetromino.color
        
        lines_cleared = 0
        for y in range(GRID_SIZE):
            if all(self.cells[y]):
                self.clear_line(y, screen_width)
                lines_cleared += 1
        
        return lines_cleared

class TicTacToeGrid:
    def __init__(self, cell_size):
        self.cells = [[None for _ in range(TICTACTOE_GRID_SIZE)] for _ in range(TICTACTOE_GRID_SIZE)]
        self.cell_size = cell_size
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.x_color = (237, 67, 55)  # Красный для X
        self.o_color = (66, 135, 245)  # Синий для O
        self.last_move = None
    
    def update_cell_size(self, new_cell_size):
        self.cell_size = new_cell_size
    
    def get_grid_offset(self, screen_width):
        return (screen_width - TICTACTOE_GRID_SIZE * self.cell_size) // 2
    
    def draw(self, surface):
        screen_width = surface.get_width()
        grid_x_offset = self.get_grid_offset(screen_width)
        
        # Рисуем фон сетки
        pygame.draw.rect(
            surface, (40, 40, 40),
            (grid_x_offset, GRID_Y_OFFSET, 
             TICTACTOE_GRID_SIZE * self.cell_size, TICTACTOE_GRID_SIZE * self.cell_size)
        )
        
        # Рисуем клетки
        for y in range(TICTACTOE_GRID_SIZE):
            for x in range(TICTACTOE_GRID_SIZE):
                rect = pygame.Rect(
                    grid_x_offset + x * self.cell_size,
                    GRID_Y_OFFSET + y * self.cell_size,
                    self.cell_size, self.cell_size
                )
                pygame.draw.rect(surface, (50, 50, 50), rect)
                pygame.draw.rect(surface, (70, 70, 70), rect, max(1, self.cell_size // 25))
                
                # Рисуем X или O
                if self.cells[y][x] == 'X':
                    pygame.draw.line(
                        surface, self.x_color,
                        (rect.left + self.cell_size//4, rect.top + self.cell_size//4),
                        (rect.right - self.cell_size//4, rect.bottom - self.cell_size//4),
                        max(3, self.cell_size // 10)
                    )
                    pygame.draw.line(
                        surface, self.x_color,
                        (rect.right - self.cell_size//4, rect.top + self.cell_size//4),
                        (rect.left + self.cell_size//4, rect.bottom - self.cell_size//4),
                        max(3, self.cell_size // 10)
                    )
                elif self.cells[y][x] == 'O':
                    pygame.draw.circle(
                        surface, self.o_color,
                        (rect.centerx, rect.centery),
                        self.cell_size // 3,
                        max(3, self.cell_size // 10)
                    )
        
        # Подпись текущего игрока
        font = pygame.font.SysFont('Arial', 32)
        player_text = f"Ход: {'Игрок (X)' if self.current_player == 'X' else 'Бот (O)'}"
        player_surface = font.render(player_text, True, WHITE)
        surface.blit(player_surface, (grid_x_offset, GRID_Y_OFFSET - 40))
    
    def make_move(self, x, y, screen_width):
        if self.game_over:
            return False
        
        grid_x_offset = self.get_grid_offset(screen_width)
        grid_x = int((x - grid_x_offset) / self.cell_size)
        grid_y = int((y - GRID_Y_OFFSET) / self.cell_size)
        
        if 0 <= grid_x < TICTACTOE_GRID_SIZE and 0 <= grid_y < TICTACTOE_GRID_SIZE:
            if self.cells[grid_y][grid_x] is None:
                self.cells[grid_y][grid_x] = self.current_player
                self.last_move = (grid_x, grid_y)
                
                # Проверяем победу
                if self.check_win(grid_x, grid_y):
                    self.game_over = True
                    self.winner = self.current_player
                # Проверяем ничью
                elif all(all(row) for row in self.cells):
                    self.game_over = True
                    self.winner = None
                else:
                    self.current_player = 'O' if self.current_player == 'X' else 'X'
                    if self.current_player == 'O':
                        self.bot_move()
                
                return True
        return False
    
    def evaluate_position(self, x, y, player):
        """Оценивает выгодность позиции для указанного игрока"""
        directions = [
            (1, 0),   # горизонталь
            (0, 1),    # вертикаль
            (1, 1),    # диагональ \
            (1, -1)    # диагональ /
        ]
        
        score = 0
        
        for dx, dy in directions:
            # Проверяем линию в обоих направлениях
            line_length = 1  # текущая клетка уже занята
            
            # Проверяем в одном направлении
            nx, ny = x + dx, y + dy
            while 0 <= nx < TICTACTOE_GRID_SIZE and 0 <= ny < TICTACTOE_GRID_SIZE and self.cells[ny][nx] == player:
                line_length += 1
                nx += dx
                ny += dy
            
            # Проверяем в противоположном направлении
            nx, ny = x - dx, y - dy
            while 0 <= nx < TICTACTOE_GRID_SIZE and 0 <= ny < TICTACTOE_GRID_SIZE and self.cells[ny][nx] == player:
                line_length += 1
                nx -= dx
                ny -= dy
            
            # Оцениваем длину линии
            if line_length >= WIN_CONDITION:
                return 100  # выигрышная позиция
            score += line_length * line_length
        
        return score
    
    def bot_move(self):
        best_score = -1
        best_moves = []
        
        # Сначала проверяем возможность выиграть
        for y in range(TICTACTOE_GRID_SIZE):
            for x in range(TICTACTOE_GRID_SIZE):
                if self.cells[y][x] is None:
                    self.cells[y][x] = 'O'
                    if self.check_win(x, y):
                        self.game_over = True
                        self.winner = 'O'
                        return
                    self.cells[y][x] = None
        
        # Затем проверяем возможность блокировки игрока
        for y in range(TICTACTOE_GRID_SIZE):
            for x in range(TICTACTOE_GRID_SIZE):
                if self.cells[y][x] is None:
                    self.cells[y][x] = 'X'
                    if self.check_win(x, y):
                        self.cells[y][x] = 'O'
                        self.current_player = 'X'
                        return
                    self.cells[y][x] = None
        
        # Если нет срочных ходов, ищем лучшую позицию
        for y in range(TICTACTOE_GRID_SIZE):
            for x in range(TICTACTOE_GRID_SIZE):
                if self.cells[y][x] is None:
                    # Оцениваем позицию для бота
                    score = self.evaluate_position(x, y, 'O')
                    # Добавляем штраф за углы и края (чтобы бот стремился к центру)
                    center_dist = abs(x - TICTACTOE_GRID_SIZE//2) + abs(y - TICTACTOE_GRID_SIZE//2)
                    score -= center_dist * 0.5
                    
                    if score > best_score:
                        best_score = score
                        best_moves = [(x, y)]
                    elif score == best_score:
                        best_moves.append((x, y))
        
        if best_moves:
            # Если есть несколько лучших ходов, выбираем случайный
            x, y = random.choice(best_moves)
            self.cells[y][x] = 'O'
            self.last_move = (x, y)
            
            if self.check_win(x, y):
                self.game_over = True
                self.winner = 'O'
            elif all(all(row) for row in self.cells):
                self.game_over = True
                self.winner = None
            else:
                self.current_player = 'X'
    
    def check_win(self, x, y):
        directions = [
            [(1, 0), (-1, 0)],  # Горизонталь
            [(0, 1), (0, -1)],   # Вертикаль
            [(1, 1), (-1, -1)], # Диагональ \
            [(1, -1), (-1, 1)]   # Диагональ /
        ]
        
        for dir_pair in directions:
            count = 1  # Текущая клетка уже содержит символ
            
            for dx, dy in dir_pair:
                nx, ny = x + dx, y + dy
                while 0 <= nx < TICTACTOE_GRID_SIZE and 0 <= ny < TICTACTOE_GRID_SIZE and self.cells[ny][nx] == self.current_player:
                    count += 1
                    nx += dx
                    ny += dy
            
            if count >= WIN_CONDITION:
                return True
        
        return False
    
    def reset(self):
        self.cells = [[None for _ in range(TICTACTOE_GRID_SIZE)] for _ in range(TICTACTOE_GRID_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.last_move = None

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', 32)
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Background:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.stars = []
        self.type = "particles"  # particles, solid, gradient, stars, geometric, waves, nebula, circuit, matrix
        
        # Создаем частицы для фона
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(5, 15),
                'color': random.choice(COLORS),
                'speed': random.uniform(0.5, 1.5),
                'direction': random.uniform(0, math.pi * 2)
            })
        
        # Создаем звезды для звездного фона
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 3),
                'brightness': random.uniform(0.3, 1.0)
            })
        
        # Создаем геометрические фигуры для геометрического фона
        self.geometric_shapes = []
        for _ in range(7):
            shape_type = random.choice(['rect', 'circle', 'triangle'])
            if shape_type == 'rect':
                self.geometric_shapes.append({
                    'type': 'rect',
                    'x': random.randint(0, width),
                    'y': random.randint(0, height),
                    'w': random.randint(20, 100),
                    'h': random.randint(20, 100),
                    'color': random.choice(COLORS),
                    'alpha': random.randint(30, 100),
                    'angle': random.uniform(0, 360),
                    'speed': random.uniform(0.2, 1.0)
                })
            elif shape_type == 'circle':
                self.geometric_shapes.append({
                    'type': 'circle',
                    'x': random.randint(0, width),
                    'y': random.randint(0, height),
                    'r': random.randint(10, 50),
                    'color': random.choice(COLORS),
                    'alpha': random.randint(30, 100),
                    'speed': random.uniform(0.2, 1.0)
                })
            else:  # triangle
                self.geometric_shapes.append({
                    'type': 'triangle',
                    'points': [
                        (random.randint(0, width), random.randint(0, height)),
                        (random.randint(0, width), random.randint(0, height)),
                        (random.randint(0, width), random.randint(0, height))
                    ],
                    'color': random.choice(COLORS),
                    'alpha': random.randint(30, 100),
                    'speed': random.uniform(0.2, 1.0)
                })
        
        # Для волнового фона
        self.wave_points = []
        for x in range(0, width + 20, 20):
            self.wave_points.append((x, height // 2))
        self.wave_offset = 0
        
        # Для туманности
        self.nebula_colors = [
            (100, 50, 150), (50, 100, 200), (150, 50, 100),
            (50, 150, 100), (200, 100, 50), (100, 200, 50)
        ]
        self.nebula_centers = []
        for _ in range(5):
            self.nebula_centers.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'color': random.choice(self.nebula_colors),
                'radius': random.randint(100, 300),
                'alpha': random.randint(30, 80)
            })
        
        # Для схемы (circuit)
        self.circuit_lines = []
        for _ in range(15):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-100, 100)
            self.circuit_lines.append({
                'points': [(x1, y1), (x2, y2)],
                'color': (0, 200, 200),
                'width': random.randint(1, 3),
                'alpha': random.randint(50, 150),
                'speed': random.uniform(0.1, 0.5)
            })
        self.circuit_nodes = []
        for _ in range(20):
            self.circuit_nodes.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(2, 5),
                'color': (0, 200, 200),
                'alpha': random.randint(100, 200)
            })
        
        # Для матрицы (matrix)
        self.matrix_chars = []
        self.matrix_font = pygame.font.SysFont('courier', 16)
        for _ in range(50):
            self.matrix_chars.append({
                'x': random.randint(0, width),
                'y': random.randint(-100, 0),
                'speed': random.uniform(1, 3),
                'length': random.randint(5, 15),
                'chars': [chr(random.randint(33, 126)) for _ in range(15)],
                'color': (0, 255, 0)
            })
    
    def update(self):
        if self.type == "particles":
            for particle in self.particles:
                particle['x'] += math.cos(particle['direction']) * particle['speed']
                particle['y'] += math.sin(particle['direction']) * particle['speed']
                
                if particle['x'] < 0:
                    particle['x'] = self.width
                elif particle['x'] > self.width:
                    particle['x'] = 0
                if particle['y'] < 0:
                    particle['y'] = self.height
                elif particle['y'] > self.height:
                    particle['y'] = 0
        elif self.type == "geometric":
            for shape in self.geometric_shapes:
                if shape['type'] == 'rect':
                    shape['angle'] += shape['speed']
                elif shape['type'] == 'circle':
                    shape['x'] += shape['speed'] * 0.5
                    if shape['x'] > self.width + shape['r']:
                        shape['x'] = -shape['r']
                elif shape['type'] == 'triangle':
                    for i in range(3):
                        shape['points'][i] = (shape['points'][i][0] + shape['speed'] * 0.3, 
                                            shape['points'][i][1] + shape['speed'] * 0.3)
                        if shape['points'][i][0] > self.width + 50:
                            shape['points'][i] = (-50, random.randint(0, self.height))
        elif self.type == "waves":
            self.wave_offset += 0.5
            for i, (x, y) in enumerate(self.wave_points):
                self.wave_points[i] = (
                    x,
                    self.height // 2 + math.sin((x + self.wave_offset) * 0.02) * 50
                )
        elif self.type == "nebula":
            for center in self.nebula_centers:
                center['x'] += random.uniform(-0.5, 0.5)
                center['y'] += random.uniform(-0.5, 0.5)
                center['radius'] += random.uniform(-1, 1)
        elif self.type == "circuit":
            for line in self.circuit_lines:
                for i in range(2):
                    line['points'][i] = (
                        line['points'][i][0] + random.uniform(-line['speed'], line['speed']),
                        line['points'][i][1] + random.uniform(-line['speed'], line['speed'])
                    )
                line['alpha'] += random.uniform(-1, 1)
                line['alpha'] = max(50, min(150, line['alpha']))
        elif self.type == "matrix":
            for char in self.matrix_chars:
                char['y'] += char['speed']
                if char['y'] > self.height + char['length'] * 20:
                    char['y'] = random.randint(-100, -20)
                    char['x'] = random.randint(0, self.width)
    
    def draw(self, surface):
        if self.type == "particles":
            surface.fill(BACKGROUND_COLOR)
            for particle in self.particles:
                pygame.draw.circle(
                    surface, 
                    particle['color'], 
                    (int(particle['x']), int(particle['y'])), 
                    particle['size']
                )
        elif self.type == "solid":
            surface.fill(BACKGROUND_COLOR)
        elif self.type == "gradient":
            # Градиентный фон от темного к светлому
            for y in range(self.height):
                color_val = 30 + int(50 * (y / self.height))
                pygame.draw.line(surface, (color_val, color_val, color_val), (0, y), (self.width, y))
        elif self.type == "stars":
            surface.fill((10, 10, 30))
            for star in self.stars:
                brightness = int(255 * star['brightness'])
                pygame.draw.circle(
                    surface, 
                    (brightness, brightness, brightness), 
                    (int(star['x']), int(star['y'])), 
                    star['size']
                )
        elif self.type == "geometric":
            surface.fill((20, 20, 40))
            for shape in self.geometric_shapes:
                s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                if shape['type'] == 'rect':
                    pygame.draw.rect(
                        s, 
                        (*shape['color'], shape['alpha']), 
                        (shape['x'], shape['y'], shape['w'], shape['h'])
                    )
                    rotated = pygame.transform.rotate(s, shape['angle'])
                    surface.blit(rotated, (shape['x'] - rotated.get_width()//2, 
                                         shape['y'] - rotated.get_height()//2))
                elif shape['type'] == 'circle':
                    pygame.draw.circle(
                        s, 
                        (*shape['color'], shape['alpha']), 
                        (shape['x'], shape['y']), 
                        shape['r']
                    )
                    surface.blit(s, (0, 0))
                elif shape['type'] == 'triangle':
                    pygame.draw.polygon(
                        s, 
                        (*shape['color'], shape['alpha']), 
                        shape['points']
                    )
                    surface.blit(s, (0, 0))
        elif self.type == "waves":
            surface.fill((10, 20, 40))
            if len(self.wave_points) > 1:
                pygame.draw.lines(surface, (0, 150, 200), False, self.wave_points, 3)
                # Отражение волн
                reflected_points = [(x, self.height - y) for x, y in self.wave_points]
                pygame.draw.lines(surface, (0, 100, 150), False, reflected_points, 2)
        elif self.type == "nebula":
            surface.fill((5, 5, 15))
            for center in self.nebula_centers:
                s = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    s, 
                    (*center['color'], center['alpha']), 
                    (center['x'], center['y']), 
                    center['radius']
                )
                surface.blit(s, (0, 0))
        elif self.type == "circuit":
            surface.fill((5, 10, 15))
            for line in self.circuit_lines:
                s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(
                    s, 
                    (*line['color'], int(line['alpha'])), 
                    line['points'][0], line['points'][1], 
                    line['width']
                )
                surface.blit(s, (0, 0))
            for node in self.circuit_nodes:
                s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(
                    s, 
                    (*node['color'], node['alpha']), 
                    (node['x'], node['y']), 
                    node['size']
                )
                surface.blit(s, (0, 0))
        elif self.type == "matrix":
            surface.fill((0, 0, 0))
            for char in self.matrix_chars:
                for i in range(char['length']):
                    if char['y'] - i * 20 < 0:
                        continue
                    alpha = 255 - i * (255 // char['length'])
                    color = (0, min(255, 50 + i * 20), 0, alpha)
                    char_surface = self.matrix_font.render(char['chars'][i], True, color)
                    surface.blit(char_surface, (char['x'], char['y'] - i * 20))
    
    def resize(self, new_width, new_height):
        scale_x = new_width / self.width
        scale_y = new_height / self.height
        
        for particle in self.particles:
            particle['x'] *= scale_x
            particle['y'] *= scale_y
            particle['size'] *= min(scale_x, scale_y)
        
        for star in self.stars:
            star['x'] *= scale_x
            star['y'] *= scale_y
        
        for shape in self.geometric_shapes:
            if shape['type'] == 'rect':
                shape['x'] *= scale_x
                shape['y'] *= scale_y
                shape['w'] *= scale_x
                shape['h'] *= scale_y
            elif shape['type'] == 'circle':
                shape['x'] *= scale_x
                shape['y'] *= scale_y
                shape['r'] *= min(scale_x, scale_y)
            elif shape['type'] == 'triangle':
                new_points = []
                for point in shape['points']:
                    new_points.append((point[0] * scale_x, point[1] * scale_y))
                shape['points'] = new_points
        
        # Обновляем волновой фон
        self.wave_points = []
        for x in range(0, new_width + 20, 20):
            self.wave_points.append((x, new_height // 2))
        
        # Обновляем туманность
        for center in self.nebula_centers:
            center['x'] *= scale_x
            center['y'] *= scale_y
            center['radius'] *= max(scale_x, scale_y)
        
        # Обновляем схему
        for line in self.circuit_lines:
            new_points = []
            for point in line['points']:
                new_points.append((point[0] * scale_x, point[1] * scale_y))
            line['points'] = new_points
        
        for node in self.circuit_nodes:
            node['x'] *= scale_x
            node['y'] *= scale_y
        
        # Обновляем матрицу
        for char in self.matrix_chars:
            char['x'] *= scale_x
            char['y'] *= scale_y
        
        self.width = new_width
        self.height = new_height

class Console:
    def __init__(self, width, height, game=None):
        self.width = width
        self.height = height
        self.visible = False
        self.input_text = ""
        self.font = pygame.font.SysFont('courier', 24)
        self.history = []
        self.max_history = 10
        self.rect = pygame.Rect(50, height - 150, width - 100, 100)
        self.input_rect = pygame.Rect(60, height - 40, width - 120, 30)
        self.active_input = False
        self.game = game
    
    def toggle(self):
        self.visible = not self.visible
        self.active_input = self.visible
    
    def handle_event(self, event):
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.execute_command(self.input_text)
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode
        
        return True
    
    def execute_command(self, command):
        self.history.append(f"> {command}")
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Новые команды
        if command.lower() == "help":
            self.history.append("Доступные команды: help, clear, score, level, time")
        elif command.lower() == "clear":
            self.history = []
        elif command.lower() == "score":
            if self.game:
                self.history.append(f"Текущий счет: {self.game.score}")
            else:
                self.history.append("Ошибка: игра не доступна")
        elif command.lower() == "level":
            if self.game:
                self.history.append(f"Текущий уровень: {self.game.level}")
            else:
                self.history.append("Ошибка: игра не доступна")
        elif command.lower() == "time":
            if self.game and hasattr(self.game, 'speed_mode'):
                if self.game.speed_mode:
                    elapsed = (pygame.time.get_ticks() - self.game.level_start_time - self.game.paused_time) // 1000
                    time_left = max(0, self.game.time_limit - elapsed)
                    self.history.append(f"Осталось времени: {time_left} сек")
                else:
                    self.history.append("Режим без ограничения времени")
            else:
                self.history.append("Ошибка: игра не доступна")
        else:
            self.history.append("Неизвестная команда. Введите 'help' для списка команд")
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Рисуем фон консоли
        pygame.draw.rect(surface, (0, 0, 0, 200), self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        
        # Рисуем историю команд
        y_pos = self.rect.y + 10
        for line in self.history[-self.max_history:]:
            text_surface = self.font.render(line, True, (200, 200, 200))
            surface.blit(text_surface, (self.rect.x + 10, y_pos))
            y_pos += 25
        
        # Рисуем поле ввода
        pygame.draw.rect(surface, (30, 30, 30), self.input_rect)
        pygame.draw.rect(surface, (100, 100, 100), self.input_rect, 1)
        
        # Рисуем текст в поле ввода
        input_surface = self.font.render("> " + self.input_text, True, WHITE)
        surface.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # Рисуем курсор, если активно поле ввода
        if self.active_input and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.input_rect.x + 5 + self.font.size("> " + self.input_text)[0]
            pygame.draw.line(surface, WHITE, (cursor_x, self.input_rect.y + 5), 
                            (cursor_x, self.input_rect.y + 25), 2)

class Settings:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons = []
        self.scroll_offset = 0
        self.max_scroll = 0
        self.background = Background(screen_width, screen_height)
        self.update_ui()
    
    def update_ui(self):
        button_width = min(300, self.screen_width // 2.5)
        button_height = min(60, self.screen_height // 12)
        button_spacing = min(20, button_height // 2)
        
        # Создаем 9 кнопок для фонов + кнопка назад
        total_height = (9 * button_height) + (8 * button_spacing) + button_height + button_spacing
        start_y = (self.screen_height - min(total_height, self.screen_height - 100)) // 2
        
        self.buttons = [
            Button(
                self.screen_width//2 - button_width//2, 
                start_y, 
                button_width, button_height, 
                "Обои: Частицы", (66, 135, 245), (100, 170, 255)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + button_height + button_spacing, 
                button_width, button_height, 
                "Обои: Тёмные", (100, 100, 100), (150, 150, 150)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 2*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Градиент", (123, 201, 123), (150, 230, 150)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 3*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Звёзды", (248, 231, 28), (255, 240, 100)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 4*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Геометрия", (173, 105, 237), (200, 140, 255)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 5*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Волны", (0, 150, 200), (0, 200, 250)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 6*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Туманность", (100, 50, 150), (150, 100, 200)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 7*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Схема", (0, 200, 200), (0, 250, 250)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 8*(button_height + button_spacing), 
                button_width, button_height, 
                "Обои: Матрица", (0, 255, 0), (100, 255, 100)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 9*(button_height + button_spacing), 
                button_width, button_height, 
                "Назад", (237, 67, 55), (255, 100, 100)
            )
        ]
        
        # Устанавливаем максимальное смещение прокрутки
        last_button_bottom = self.buttons[-1].rect.bottom
        screen_bottom = self.screen_height - 50
        self.max_scroll = max(0, last_button_bottom - screen_bottom)
    
    def handle_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.background.resize(new_width, new_height)
        self.update_ui()
        self.scroll_offset = 0  # Сбрасываем прокрутку при изменении размера
    
    def handle_scroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 20  # Чувствительность прокрутки
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            self.handle_scroll(event)
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                pygame.time.delay(50)
                pygame.display.flip()
            
            for button in self.buttons:
                # Корректируем позицию мыши для проверки наведения с учетом прокрутки
                adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_offset)
                button.check_hover(adjusted_mouse_pos)
                if button.is_clicked(adjusted_mouse_pos, event):
                    if button.text == "Обои: Частицы":
                        self.background.type = "particles"
                    elif button.text == "Обои: Тёмные":
                        self.background.type = "solid"
                    elif button.text == "Обои: Градиент":
                        self.background.type = "gradient"
                    elif button.text == "Обои: Звёзды":
                        self.background.type = "stars"
                    elif button.text == "Обои: Геометрия":
                        self.background.type = "geometric"
                    elif button.text == "Обои: Волны":
                        self.background.type = "waves"
                    elif button.text == "Обои: Туманность":
                        self.background.type = "nebula"
                    elif button.text == "Обои: Схема":
                        self.background.type = "circuit"
                    elif button.text == "Обои: Матрица":
                        self.background.type = "matrix"
                    elif button.text == "Назад":
                        return "menu"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        
        return "settings"
    
    def draw(self, surface):
        self.background.draw(surface)
        
        # Создаем поверхность для кнопок с учетом прокрутки
        buttons_surface = pygame.Surface((self.screen_width, self.buttons[-1].rect.bottom + 50), pygame.SRCALPHA)
        
        title_font = pygame.font.SysFont('Arial', 64, bold=True)
        title_text = title_font.render("", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, 100))
        buttons_surface.blit(title_text, title_rect)
        
        for button in self.buttons:
            # Рисуем кнопки на поверхности с их оригинальными позициями
            button.draw(buttons_surface)
        
        # Рисуем только видимую часть поверхности кнопок
        visible_rect = pygame.Rect(0, self.scroll_offset, self.screen_width, self.screen_height)
        surface.blit(buttons_surface, (0, 0), visible_rect)
        
        # Рисуем полосу прокрутки, если нужно
        if self.max_scroll > 0:
            scrollbar_width = 10
            scrollbar_x = self.screen_width - scrollbar_width - 5
            scrollbar_height = self.screen_height * (self.screen_height / (self.buttons[-1].rect.bottom + 50))
            scrollbar_pos = (self.scroll_offset / self.max_scroll) * (self.screen_height - scrollbar_height)
            
            pygame.draw.rect(surface, (100, 100, 100), (scrollbar_x, scrollbar_pos, scrollbar_width, scrollbar_height))
            pygame.draw.rect(surface, (150, 150, 150), (scrollbar_x, scrollbar_pos, scrollbar_width, scrollbar_height), 2)

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 32)
        self.buttons = []
        self.background = Background(screen_width, screen_height)
        self.update_ui()
    
    def update_ui(self):
        button_width = min(300, self.screen_width // 2.5)
        button_height = min(60, self.screen_height // 12)
        button_spacing = min(20, button_height // 2)
        
        total_height = 6 * button_height + 5 * button_spacing
        start_y = (self.screen_height - total_height) // 1.5
        
        self.buttons = [
            Button(
                self.screen_width//2 - button_width//2, 
                start_y, 
                button_width, button_height, 
                "Обычный режим", (66, 135, 245), (100, 170, 255)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + button_height + button_spacing, 
                button_width, button_height, 
                "Скоростной режим", (237, 67, 55), (255, 100, 100)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 2*(button_height + button_spacing), 
                button_width, button_height, 
                "Классический Тетрис", PINK, (255, 150, 200)  # Розовая кнопка
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 3*(button_height + button_spacing), 
                button_width, button_height, 
                "Крестики-нолики", (123, 201, 123), (150, 230, 150)  # Зеленая кнопка
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 4*(button_height + button_spacing), 
                button_width, button_height, 
                "Настройки", (150, 150, 150), (200, 200, 200)
            ),
            Button(
                self.screen_width//2 - button_width//2, 
                start_y + 5*(button_height + button_spacing), 
                button_width, button_height, 
                "Выход", (100, 100, 100), (150, 150, 150)
            )
        ]
    
    def handle_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.background.resize(new_width, new_height)
        self.update_ui()
    
    def update(self):
        self.background.update()
    
    def draw(self, surface):
        self.background.draw(surface)
        
        title_text = self.title_font.render("Блок-пазл", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//4))
        surface.blit(title_text, title_rect)
        
        for button in self.buttons:
            button.draw(surface)
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                pygame.time.delay(50)
                pygame.display.flip()
            
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    if button.text == "Обычный режим":
                        return "play"
                    elif button.text == "Скоростной режим":
                        return "speed"
                    elif button.text == "Классический Тетрис":
                        return "tetris"
                    elif button.text == "Крестики-нолики":
                        return "tictactoe"
                    elif button.text == "Настройки":
                        return "settings"
                    elif button.text == "Выход":
                        return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
        
        return "menu"

class Game:
    def __init__(self, speed_mode=False, background_type="particles"):
        self.screen_width, self.screen_height = INITIAL_WIDTH, INITIAL_HEIGHT
        self.cell_size = self.calculate_cell_size()
        self.grid = Grid(self.cell_size)
        self.blocks = []
        self.selected_block = None
        self.score = 0
        self.level = 1
        self.font = pygame.font.SysFont('Arial', 32)
        self.speed_mode = speed_mode
        self.time_limit = 90  # 1 минута 30 секунд
        self.level_start_time = pygame.time.get_ticks()
        self.pause_start_time = 0
        self.paused_time = 0
        self.game_over = False
        self.paused = False
        self.back_to_menu_button = Button(
            self.screen_width - 150, 20, 130, 40, 
            "Меню", (100, 100, 100), (150, 150, 150)
        )
        self.background = Background(self.screen_width, self.screen_height)
        self.background.type = background_type
        self.console = Console(self.screen_width, self.screen_height, self)
        
        # Генерируем начальные блоки
        self.generate_blocks()
    
    def calculate_cell_size(self):
        max_possible = min(
            (self.screen_width - 2 * UI_MARGIN) // GRID_SIZE,
            (self.screen_height - GRID_Y_OFFSET - 150) // GRID_SIZE
        )
        return max(MIN_CELL_SIZE, min(DEFAULT_CELL_SIZE, max_possible))
    
    def handle_resize(self, new_width, new_height):
        self.screen_width, self.screen_height = new_width, new_height
        old_cell_size = self.cell_size
        self.cell_size = self.calculate_cell_size()
        
        self.grid.update_cell_size(self.cell_size)
        self.background.resize(new_width, new_height)
        self.console = Console(new_width, new_height, self)
        
        for i, block in enumerate(self.blocks):
            rel_x = (block.x - UI_MARGIN) / (220 * (old_cell_size / DEFAULT_CELL_SIZE))
            rel_y = (block.y - (self.screen_height - 120 * (old_cell_size / DEFAULT_CELL_SIZE))) / (120 * (old_cell_size / DEFAULT_CELL_SIZE))
            
            block.update_cell_size(self.cell_size)
            block.x = UI_MARGIN + rel_x * (220 * (self.cell_size / DEFAULT_CELL_SIZE))
            block.y = (self.screen_height - 120 * (self.cell_size / DEFAULT_CELL_SIZE)) + rel_y * (120 * (self.cell_size / DEFAULT_CELL_SIZE))
        
        self.back_to_menu_button.rect.x = self.screen_width - 150
        self.back_to_menu_button.rect.y = 20
        
        pygame.display.flip()
    
    def get_available_shapes(self):
        level_index = min(self.level - 1, len(SHAPES_BY_LEVEL) - 1)
        shapes = []
        for i in range(level_index + 1):
            shapes.extend(SHAPES_BY_LEVEL[i])
        return shapes
    
    def generate_blocks(self):
        available_shapes = self.get_available_shapes()
        available_colors = COLORS.copy()
        self.blocks = []
        
        for i in range(3):
            shape = random.choice(available_shapes)
            color = random.choice(available_colors)
            
            if color in available_colors:
                available_colors.remove(color)
            
            self.blocks.append(Block(
                shape,
                color,
                UI_MARGIN + i * 220 * (self.cell_size / DEFAULT_CELL_SIZE),
                self.screen_height - 120 * (self.cell_size / DEFAULT_CELL_SIZE),
                self.cell_size
            ))
            
            if not available_colors:
                available_colors = COLORS.copy()
    
    def draw_ui(self, surface):
        score_text = self.font.render(f"Очки: {self.score}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.level}", True, WHITE)
        
        surface.blit(score_text, (UI_MARGIN, UI_MARGIN))
        surface.blit(level_text, (UI_MARGIN, UI_MARGIN + 40))
        
        if self.speed_mode:
            if self.paused:
                elapsed = (self.pause_start_time - self.level_start_time - self.paused_time) // 1000
            else:
                elapsed = (pygame.time.get_ticks() - self.level_start_time - self.paused_time) // 1000
            time_left = max(0, self.time_limit - elapsed)
            time_text = self.font.render(f"Время: {time_left}", True, 
                (255, 0, 0) if time_left < 10 else WHITE)
            surface.blit(time_text, (UI_MARGIN, UI_MARGIN + 80))
        
        self.back_to_menu_button.draw(surface)
        
        if self.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("ТЫ ПРОИГРАЛ!", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            surface.blit(game_over_text, game_over_rect)
            
            menu_button = Button(
                self.screen_width//2 - 150, 
                self.screen_height//2 + 20, 
                300, 50, 
                "Главное меню", (100, 100, 100), (150, 150, 150)
            )
            menu_button.draw(surface)
            return menu_button
        
        if self.paused:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            pause_text = self.font.render("ПАУЗА", True, WHITE)
            pause_rect = pause_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            surface.blit(pause_text, pause_rect)
        
        return None
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        self.background.update()
        
        if self.speed_mode:
            elapsed = (pygame.time.get_ticks() - self.level_start_time - self.paused_time) // 1000
            if elapsed >= self.time_limit:
                self.game_over = True
                return
        
        new_level = self.score // 500 + 1
        if new_level > self.level:
            self.level = new_level
            self.level_start_time = pygame.time.get_ticks()
            self.paused_time = 0
            self.generate_blocks()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        menu_button = self.draw_ui(pygame.display.get_surface()) if self.game_over else None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                pygame.time.delay(50)
                pygame.display.flip()
            
            # Обработка консоли
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.console.toggle()
                    continue
            
            if self.console.visible:
                if self.console.handle_event(event):
                    continue
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if self.paused:
                        self.pause_start_time = pygame.time.get_ticks()
                    else:
                        self.paused_time += pygame.time.get_ticks() - self.pause_start_time
                elif event.key == pygame.K_r and self.selected_block and not self.paused and not self.game_over:
                    self.selected_block.rotate()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and menu_button and menu_button.is_clicked(mouse_pos, event):
                    return "menu"
                
                if self.back_to_menu_button.is_clicked(mouse_pos, event):
                    return "menu"
                
                if not self.paused and not self.game_over and not self.console.visible:
                    for block in self.blocks:
                        for dx, dy in block.shape:
                            rect = pygame.Rect(
                                block.x + dx * block.cell_size,
                                block.y + dy * block.cell_size,
                                block.cell_size, block.cell_size
                            )
                            if rect.collidepoint(event.pos):
                                self.selected_block = block
                                block.offset_x = event.pos[0] - block.x
                                block.offset_y = event.pos[1] - block.y
                                break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_block and not self.paused and not self.game_over and not self.console.visible:
                    if self.grid.can_place(self.selected_block, self.screen_width):
                        lines_cleared = self.grid.place_block(self.selected_block, self.screen_width)
                        if lines_cleared > 0:
                            self.score += lines_cleared * 100 * self.level
                            if has_sound: clear_sound.play()
                        else:
                            if has_sound: place_sound.play()
                        
                        self.blocks.remove(self.selected_block)
                        if len(self.blocks) <= 1:
                            self.generate_blocks()
                    else:
                        idx = self.blocks.index(self.selected_block)
                        self.selected_block.x = UI_MARGIN + idx * 220 * (self.cell_size / DEFAULT_CELL_SIZE)
                        self.selected_block.y = self.screen_height - 120 * (self.cell_size / DEFAULT_CELL_SIZE)
                    
                    self.selected_block = None
            
            elif event.type == pygame.MOUSEMOTION and self.selected_block and not self.paused and not self.game_over and not self.console.visible:
                self.selected_block.x = event.pos[0] - self.selected_block.offset_x
                self.selected_block.y = event.pos[1] - self.selected_block.offset_y
        
        if self.game_over:
            return "game_over"
        return "game"

class TetrisGame:
    def __init__(self, background_type="particles"):
        self.screen_width, self.screen_height = INITIAL_WIDTH, INITIAL_HEIGHT
        self.cell_size = self.calculate_cell_size()
        self.grid = Grid(self.cell_size)
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.font = pygame.font.SysFont('Arial', 32)
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 500  # начальная скорость падения (мс)
        self.last_fall = pygame.time.get_ticks()
        self.back_to_menu_button = Button(
            self.screen_width - 150, 20, 130, 40, 
            "Меню", (100, 100, 100), (150, 150, 150)
        )
        self.background = Background(self.screen_width, self.screen_height)
        self.background.type = background_type
        self.console = Console(self.screen_width, self.screen_height, self)
        
        # Генерируем первые фигуры
        self.new_piece()
        self.new_next_piece()
    
    def calculate_cell_size(self):
        max_possible = min(
            (self.screen_width - 2 * UI_MARGIN) // GRID_SIZE,
            (self.screen_height - GRID_Y_OFFSET - 150) // GRID_SIZE
        )
        return max(MIN_CELL_SIZE, min(DEFAULT_CELL_SIZE, max_possible))
    
    def handle_resize(self, new_width, new_height):
        self.screen_width, self.screen_height = new_width, new_height
        self.cell_size = self.calculate_cell_size()
        self.grid.update_cell_size(self.cell_size)
        self.background.resize(new_width, new_height)
        self.console = Console(new_width, new_height, self)
        
        # Обновляем позицию кнопки
        self.back_to_menu_button.rect.x = self.screen_width - 150
        self.back_to_menu_button.rect.y = 20
        
        pygame.display.flip()
    
    def new_piece(self):
        if self.next_piece:
            self.current_piece = self.next_piece
            self.current_piece.x = (self.screen_width // 2) - (len(self.current_piece.shape[0]) * self.cell_size // 2)
            self.current_piece.y = GRID_Y_OFFSET
            self.current_piece.cell_size = self.cell_size
        else:
            shape_idx = random.randint(0, len(TETROMINOES) - 1)
            shape = TETROMINOES[shape_idx]
            color = random.choice(COLORS)
            self.current_piece = TetrisBlock(
                shape, color,
                (self.screen_width // 2) - (len(shape[0]) * self.cell_size // 2),
                GRID_Y_OFFSET,
                self.cell_size
            )
        
        self.new_next_piece()
        
        # Проверяем, можно ли разместить новую фигуру
        if not self.grid.can_place_tetromino(self.current_piece, self.screen_width):
            self.game_over = True
    
    def new_next_piece(self):
        shape_idx = random.randint(0, len(TETROMINOES) - 1)
        shape = TETROMINOES[shape_idx]
        color = random.choice(COLORS)
        self.next_piece = TetrisBlock(
            shape, color,
            0, 0,  # Позиция будет установлена при отрисовке
            self.cell_size
        )
    
    def draw_ui(self, surface):
        score_text = self.font.render(f"Очки: {self.score}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Линии: {self.lines_cleared}", True, WHITE)
        
        surface.blit(score_text, (UI_MARGIN, UI_MARGIN))
        surface.blit(level_text, (UI_MARGIN, UI_MARGIN + 40))
        surface.blit(lines_text, (UI_MARGIN, UI_MARGIN + 80))
        
        # Рисуем следующую фигуру
        next_text = self.font.render("", True, WHITE)
        surface.blit(next_text, (self.screen_width - 200, UI_MARGIN))
        
        if self.next_piece:
            self.next_piece.x = self.screen_width - 150
            self.next_piece.y = UI_MARGIN + 50
            self.next_piece.cell_size = 30
            self.next_piece.draw(surface)
        
        self.back_to_menu_button.draw(surface)
        
        if self.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("ТЫ ПРОИГРАЛ!", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            surface.blit(game_over_text, game_over_rect)
            
            menu_button = Button(
                self.screen_width//2 - 150, 
                self.screen_height//2 + 20, 
                300, 50, 
                "Главное меню", (100, 100, 100), (150, 150, 150)
            )
            menu_button.draw(surface)
            return menu_button
        
        if self.paused:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            pause_text = self.font.render("ПАУЗА", True, WHITE)
            pause_rect = pause_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            surface.blit(pause_text, pause_rect)
        
        return None
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        self.background.update()
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fall > self.fall_speed:
            self.last_fall = current_time
            self.move_down()
    
    def move_down(self):
        if not self.current_piece:
            return
        
        self.current_piece.y += self.cell_size
        if not self.grid.can_place_tetromino(self.current_piece, self.screen_width):
            self.current_piece.y -= self.cell_size
            lines = self.grid.place_tetromino(self.current_piece, self.screen_width)
            if lines > 0:
                self.lines_cleared += lines
                self.score += lines * 100 * self.level
                if has_sound: clear_sound.play()
            else:
                if has_sound: place_sound.play()
            
            # Увеличиваем сложность каждые 10 линий
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)
            
            self.new_piece()
    
    def move_side(self, dx):
        if not self.current_piece or self.game_over or self.paused:
            return
        
        self.current_piece.x += dx * self.cell_size
        if not self.grid.can_place_tetromino(self.current_piece, self.screen_width):
            self.current_piece.x -= dx * self.cell_size
    
    def rotate(self):
        if not self.current_piece or self.game_over or self.paused:
            return
        
        self.current_piece.rotate()
        if not self.grid.can_place_tetromino(self.current_piece, self.screen_width):
            # Отменяем вращение, если оно приводит к столкновению
            self.current_piece.rotation -= 1
    
    def drop(self):
        if not self.current_piece or self.game_over or self.paused:
            return
        
        while self.grid.can_place_tetromino(self.current_piece, self.screen_width):
            self.current_piece.y += self.cell_size
        
        self.current_piece.y -= self.cell_size
        lines = self.grid.place_tetromino(self.current_piece, self.screen_width)
        if lines > 0:
            self.lines_cleared += lines
            self.score += lines * 100 * self.level
            if has_sound: clear_sound.play()
        else:
            if has_sound: place_sound.play()
        
        self.new_piece()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        menu_button = self.draw_ui(pygame.display.get_surface()) if self.game_over else None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                pygame.time.delay(50)
                pygame.display.flip()
            
            # Обработка консоли
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.console.toggle()
                    continue
            
            if self.console.visible:
                if self.console.handle_event(event):
                    continue
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_side(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.move_side(1)
                    elif event.key == pygame.K_DOWN:
                        self.move_down()
                    elif event.key == pygame.K_UP:
                        self.rotate()
                    elif event.key == pygame.K_SPACE:
                        self.drop()
                    elif event.key == pygame.K_r:  # Поворот на R
                        self.rotate()
                    elif event.key == pygame.K_a:  # Движение влево на A
                        self.move_side(-1)
                    elif event.key == pygame.K_d:  # Движение вправо на D
                        self.move_side(1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and menu_button and menu_button.is_clicked(mouse_pos, event):
                    return "menu"
                
                if self.back_to_menu_button.is_clicked(mouse_pos, event):
                    return "menu"
        
        if self.game_over:
            return "game_over"
        return "tetris"

class TicTacToeGame:
    def __init__(self, background_type="particles"):
        self.screen_width, self.screen_height = INITIAL_WIDTH, INITIAL_HEIGHT
        self.cell_size = self.calculate_cell_size()
        self.grid = TicTacToeGrid(self.cell_size)
        self.font = pygame.font.SysFont('Arial', 32)
        self.back_to_menu_button = Button(
            self.screen_width - 150, 20, 130, 40, 
            "Меню", (100, 100, 100), (150, 150, 150)
        )
        self.restart_button = Button(
            self.screen_width - 150, 70, 130, 40,
            "Заново", (100, 100, 100), (150, 150, 150)
        )
        self.background = Background(self.screen_width, self.screen_height)
        self.background.type = background_type
    
    def calculate_cell_size(self):
        max_possible = min(
            (self.screen_width - 2 * UI_MARGIN) // TICTACTOE_GRID_SIZE,
            (self.screen_height - GRID_Y_OFFSET - 150) // TICTACTOE_GRID_SIZE
        )
        return max(MIN_CELL_SIZE, min(DEFAULT_CELL_SIZE, max_possible))
    
    def handle_resize(self, new_width, new_height):
        self.screen_width, self.screen_height = new_width, new_height
        self.cell_size = self.calculate_cell_size()
        self.grid.update_cell_size(self.cell_size)
        self.background.resize(new_width, new_height)
        
        # Обновляем позиции кнопок
        self.back_to_menu_button.rect.x = self.screen_width - 150
        self.back_to_menu_button.rect.y = 20
        self.restart_button.rect.x = self.screen_width - 150
        self.restart_button.rect.y = 70
        
        pygame.display.flip()
    
    def draw_ui(self, surface):
        self.back_to_menu_button.draw(surface)
        self.restart_button.draw(surface)
        
        if self.grid.game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            if self.grid.winner:
                result_text = f"{'Игрок (X)' if self.grid.winner == 'X' else 'Бот (O)'} победил!"
                color = self.grid.x_color if self.grid.winner == 'X' else self.grid.o_color
            else:
                result_text = "Ничья!"
                color = WHITE
            
            result_surface = self.font.render(result_text, True, color)
            result_rect = result_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            surface.blit(result_surface, result_rect)
            
            restart_button = Button(
                self.screen_width//2 - 150, 
                self.screen_height//2 + 20, 
                300, 50, 
                "Играть снова", (100, 100, 100), (150, 150, 150)
            )
            restart_button.draw(surface)
            return restart_button
        
        return None
    
    def update(self):
        self.background.update()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        restart_button = self.draw_ui(pygame.display.get_surface()) if self.grid.game_over else None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                pygame.time.delay(50)
                pygame.display.flip()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.grid.game_over and restart_button and restart_button.is_clicked(mouse_pos, event):
                    self.grid.reset()
                    return "tictactoe"
                
                if self.back_to_menu_button.is_clicked(mouse_pos, event):
                    return "menu"
                
                if self.restart_button.is_clicked(mouse_pos, event):
                    self.grid.reset()
                    return "tictactoe"
                
                if not self.grid.game_over:
                    self.grid.make_move(mouse_pos[0], mouse_pos[1], self.screen_width)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_r:
                    self.grid.reset()
                    return "tictactoe"
        
        return "tictactoe"

def main():
    clock = pygame.time.Clock()
    current_screen = "menu"
    game = None
    tetris = None
    tictactoe = None
    main_menu = MainMenu(INITIAL_WIDTH, INITIAL_HEIGHT)
    settings = None
    background_type = "particles"
    
    running = True
    while running:
        if current_screen == "menu":
            action = main_menu.handle_events()
            if action == "play":
                game = Game(speed_mode=False, background_type=background_type)
                current_screen = "game"
            elif action == "speed":
                game = Game(speed_mode=True, background_type=background_type)
                current_screen = "game"
            elif action == "tetris":
                tetris = TetrisGame(background_type=background_type)
                current_screen = "tetris"
            elif action == "tictactoe":
                tictactoe = TicTacToeGame(background_type=background_type)
                current_screen = "tictactoe"
            elif action == "settings":
                settings = Settings(INITIAL_WIDTH, INITIAL_HEIGHT)
                settings.background.type = background_type
                current_screen = "settings"
            elif action == "quit":
                running = False
            main_menu.update()
            main_menu.draw(screen)
        
        elif current_screen == "settings":
            action = settings.handle_events()
            if action == "menu":
                current_screen = "menu"
                background_type = settings.background.type
                main_menu = MainMenu(settings.screen_width, settings.screen_height)
                main_menu.background.type = background_type
            elif action == "quit":
                running = False
            settings.background.update()
            settings.draw(screen)
        
        elif current_screen == "game":
            action = game.handle_events()
            
            if action == "menu":
                current_screen = "menu"
                main_menu = MainMenu(game.screen_width, game.screen_height)
                main_menu.background.type = background_type
            elif action == "game_over":
                current_screen = "game_over"
            elif action == "quit":
                running = False
            else:
                game.update()
                game.background.draw(screen)
                game.grid.draw(screen)
                for block in game.blocks:
                    block.draw(screen)
                game.draw_ui(screen)
                game.console.draw(screen)
        
        elif current_screen == "tetris":
            action = tetris.handle_events()
            
            if action == "menu":
                current_screen = "menu"
                main_menu = MainMenu(tetris.screen_width, tetris.screen_height)
                main_menu.background.type = background_type
            elif action == "game_over":
                current_screen = "tetris_over"
            elif action == "quit":
                running = False
            else:
                tetris.update()
                tetris.background.draw(screen)
                tetris.grid.draw(screen)
                if tetris.current_piece:
                    tetris.current_piece.draw(screen)
                tetris.draw_ui(screen)
                tetris.console.draw(screen)
        
        elif current_screen == "tictactoe":
            action = tictactoe.handle_events()
            
            if action == "menu":
                current_screen = "menu"
                main_menu = MainMenu(tictactoe.screen_width, tictactoe.screen_height)
                main_menu.background.type = background_type
            elif action == "quit":
                running = False
            else:
                tictactoe.update()
                tictactoe.background.draw(screen)
                tictactoe.grid.draw(screen)
                tictactoe.draw_ui(screen)
        
        elif current_screen == "game_over":
            game.background.draw(screen)
            game.grid.draw(screen)
            for block in game.blocks:
                block.draw(screen)
            menu_button = game.draw_ui(screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if menu_button and menu_button.is_clicked(mouse_pos, event):
                        current_screen = "menu"
                        main_menu = MainMenu(INITIAL_WIDTH, INITIAL_HEIGHT)
                        main_menu.background.type = background_type
        
        elif current_screen == "tetris_over":
            tetris.background.draw(screen)
            tetris.grid.draw(screen)
            if tetris.current_piece:
                tetris.current_piece.draw(screen)
            menu_button = tetris.draw_ui(screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if menu_button and menu_button.is_clicked(mouse_pos, event):
                        current_screen = "menu"
                        main_menu = MainMenu(INITIAL_WIDTH, INITIAL_HEIGHT)
                        main_menu.background.type = background_type
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()