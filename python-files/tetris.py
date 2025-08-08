import pygame
import random

# Инициализация pygame
pygame.init()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - голубой
    (0, 0, 255),    # J - синий
    (255, 165, 0),  # L - оранжевый
    (255, 255, 0),  # O - желтый
    (0, 255, 0),    # S - зеленый
    (128, 0, 128),  # T - фиолетовый
    (255, 0, 0)     # Z - красный
]

# Настройки игры
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE

# Фигуры тетриса
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Тетрис")

clock = pygame.time.Clock()

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5  # секунды
        self.fall_time = 0
    
    def new_piece(self):
        # Выбираем случайную фигуру
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        
        # Начальная позиция (по центру сверху)
        x = GRID_WIDTH // 2 - len(shape[0]) // 2
        y = 0
        
        return {"shape": shape, "color": color, "x": x, "y": y}
    
    def valid_move(self, piece, x_offset=0, y_offset=0):
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece["x"] + x + x_offset
                    new_y = piece["y"] + y + y_offset
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True
    
    def rotate_piece(self):
        # Получаем текущую фигуру
        piece = self.current_piece
        shape = piece["shape"]
        
        # Поворачиваем фигуру (транспонируем и инвертируем строки)
        rotated = [[shape[y][x] for y in range(len(shape)-1, -1, -1)] 
                  for x in range(len(shape[0]))]
        
        old_shape = piece["shape"]
        piece["shape"] = rotated
        
        # Если после поворота фигура в недопустимом положении, отменяем поворот
        if not self.valid_move(piece):
            piece["shape"] = old_shape
    
    def lock_piece(self):
        piece = self.current_piece
        for y, row in enumerate(piece["shape"]):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[piece["y"] + y][piece["x"] + x] = piece["color"]
        
        # Проверяем заполненные линии
        self.clear_lines()
        
        # Создаем новую фигуру
        self.current_piece = self.new_piece()
        
        # Если новая фигура сразу сталкивается - игра окончена
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                # Удаляем линию и добавляем новую пустую сверху
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]
        
        # Обновляем счет
        if lines_cleared:
            self.score += (lines_cleared ** 2) * 100
            self.level = self.score // 2000 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def update(self, delta_time):
        if self.game_over:
            return
        
        self.fall_time += delta_time
        
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.valid_move(self.current_piece, 0, 1):
                self.current_piece["y"] += 1
            else:
                self.lock_piece()
    
    def draw(self):
        # Очищаем экран
        screen.fill(BLACK)
        
        # Рисуем игровую область
        pygame.draw.rect(screen, WHITE, (GAME_AREA_LEFT, 0, BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT), 1)
        
        # Рисуем сетку
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(screen, GRAY, 
                                 (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                  BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Рисуем стаканные фигуры
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(screen, self.grid[y][x], 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                     BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                    (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, 
                                     BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Рисуем текущую фигуру
        if not self.game_over:
            piece = self.current_piece
            for y, row in enumerate(piece["shape"]):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(screen, piece["color"], 
                                        (GAME_AREA_LEFT + (piece["x"] + x) * BLOCK_SIZE, 
                                         (piece["y"] + y) * BLOCK_SIZE, 
                                         BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, WHITE, 
                                        (GAME_AREA_LEFT + (piece["x"] + x) * BLOCK_SIZE, 
                                         (piece["y"] + y) * BLOCK_SIZE, 
                                         BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Рисуем информацию о счете и уровне
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Счет: {self.score}", True, WHITE)
        level_text = font.render(f"Уровень: {self.level}", True, WHITE)
        screen.blit(score_text, (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 10, 30))
        screen.blit(level_text, (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 10, 70))
        
        # Если игра окончена, выводим сообщение
        if self.game_over:
            game_over_font = pygame.font.SysFont(None, 48)
            game_over_text = game_over_font.render("Игра Окончена!", True, (255, 0, 0))
            screen.blit(game_over_text, 
                       (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                        SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))

# Создаем экземпляр игры
game = Tetris()

# Основной игровой цикл
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # В секундах
    last_time = current_time
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if not game.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and game.valid_move(game.current_piece, -1, 0):
                    game.current_piece["x"] -= 1
                elif event.key == pygame.K_RIGHT and game.valid_move(game.current_piece, 1, 0):
                    game.current_piece["x"] += 1
                elif event.key == pygame.K_DOWN and game.valid_move(game.current_piece, 0, 1):
                    game.current_piece["y"] += 1
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:  # Мгновенное падение
                    while game.valid_move(game.current_piece, 0, 1):
                        game.current_piece["y"] += 1
                    game.lock_piece()
    
    # Обновление игры
    game.update(delta_time)
    
    # Отрисовка
    game.draw()
    pygame.display.flip()
    
    # Ограничение FPS
    clock.tick(60)

pygame.quit()