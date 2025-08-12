import pygame
import random
import sys
import math

# Инициализация Pygame
pygame.init()

# --- Константы ---
# Цвета (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (160, 160, 160)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Размеры экрана и ячеек
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INFO_HEIGHT = 50 # Высота области для отображения информации

# Уровни сложности: (строки, столбцы, мины)
LEVELS = {
    "Легкий": (9, 9, 10),
    "Средний": (16, 16, 40),
    "Сложный": (20, 25, 99) # Широкий экран
}

# --- Классы ---

class Cell:
    """Класс, представляющий одну ячейку поля."""
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
        self.animation_progress = 0 # Для анимации открытия
        self.reveal_time = 0 # Время начала анимации открытия

    def draw(self, screen, cell_size, x_offset, y_offset, current_time):
        """Отрисовка ячейки."""
        rect = pygame.Rect(x_offset + self.col * cell_size,
                           y_offset + self.row * cell_size,
                           cell_size, cell_size)

        # Цвет ячейки
        if self.is_revealed:
            # Анимация открытия
            if self.animation_progress < 1.0:
                elapsed = current_time - self.reveal_time
                self.animation_progress = min(1.0, elapsed / 200.0) # 200ms анимация
            
            # Интерполяция цвета от серого к светло-серому
            color_factor = self.animation_progress
            color_r = int(GRAY[0] + (LIGHT_BLUE[0] - GRAY[0]) * color_factor)
            color_g = int(GRAY[1] + (LIGHT_BLUE[1] - GRAY[1]) * color_factor)
            color_b = int(GRAY[2] + (LIGHT_BLUE[2] - GRAY[2]) * color_factor)
            color = (color_r, color_g, color_b)
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, DARK_GRAY, rect, 1) # Тонкая рамка
            
            # Отображение числа мин вокруг
            if not self.is_mine and self.adjacent_mines > 0:
                font = pygame.font.SysFont(None, cell_size - 6)
                # Выбор цвета числа в зависимости от количества
                number_colors = {
                    1: BLUE, 2: GREEN, 3: RED, 4: PURPLE,
                    5: ORANGE, 6: CYAN, 7: BLACK, 8: GRAY
                }
                text_color = number_colors.get(self.adjacent_mines, BLACK)
                text = font.render(str(self.adjacent_mines), True, text_color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                
        else:
            # Неоткрытая ячейка
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2) # Выделенная рамка
            if self.is_flagged:
                # Рисуем флажок
                flag_pole_top = (rect.centerx, rect.top + 5)
                flag_pole_bottom = (rect.centerx, rect.bottom - 5)
                flag_top = (rect.centerx, rect.top + 5)
                flag_mid = (rect.centerx + cell_size // 3, rect.top + cell_size // 4)
                flag_bottom = (rect.centerx, rect.top + cell_size // 2)
                pygame.draw.line(screen, BLACK, flag_pole_top, flag_pole_bottom, 2)
                pygame.draw.polygon(screen, RED, [flag_top, flag_mid, flag_bottom])

        # Отображение мины (если игра проиграна)
        if self.is_mine and (game.game_over or self.is_revealed):
            # Рисуем мину (круг с крестиком)
            mine_center = rect.center
            radius = cell_size // 3
            pygame.draw.circle(screen, BLACK, mine_center, radius)
            # Крестик
            pygame.draw.line(screen, RED, 
                             (mine_center[0] - radius//2, mine_center[1] - radius//2),
                             (mine_center[0] + radius//2, mine_center[1] + radius//2), 3)
            pygame.draw.line(screen, RED, 
                             (mine_center[0] - radius//2, mine_center[1] + radius//2),
                             (mine_center[0] + radius//2, mine_center[1] - radius//2), 3)

class Game:
    """Класс, управляющий логикой игры."""
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = []
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.flags_placed = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.initialize_board()

    def initialize_board(self):
        """Создание пустого игрового поля."""
        self.board = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.flags_placed = 0
        self.start_time = 0
        self.elapsed_time = 0

    def place_mines(self, first_row, first_col):
        """Размещение мин на поле, избегая первой открытой ячейки."""
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            # Убедимся, что мина не ставится на первую ячейку и не дублируется
            if not self.board[row][col].is_mine and not (row == first_row and col == first_col):
                self.board[row][col].is_mine = True
                mines_placed += 1
                # Увеличиваем счетчик соседних мин для соседей
                for r in range(max(0, row - 1), min(self.rows, row + 2)):
                    for c in range(max(0, col - 1), min(self.cols, col + 2)):
                        if not self.board[r][c].is_mine:
                            self.board[r][c].adjacent_mines += 1

    def reveal(self, row, col):
        """Открытие ячейки и, при необходимости, рекурсивное открытие соседей."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        cell = self.board[row][col]
        
        if cell.is_revealed or cell.is_flagged:
            return

        # Запуск таймера при первом клике
        if self.first_click:
            self.start_time = pygame.time.get_ticks()
            self.place_mines(row, col)
            self.first_click = False

        cell.is_revealed = True
        cell.reveal_time = pygame.time.get_ticks() # Запуск анимации
        cell.animation_progress = 0

        if cell.is_mine:
            self.game_over = True
            # Открываем все мины
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c].is_mine:
                        self.board[r][c].is_revealed = True
        elif cell.adjacent_mines == 0:
            # Рекурсивно открываем соседние пустые ячейки
            for r in range(max(0, row - 1), min(self.rows, row + 2)):
                for c in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not self.board[r][c].is_revealed:
                        self.reveal(r, c)
        
        self.check_win()

    def toggle_flag(self, row, col):
        """Установка или снятие флажка."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        cell = self.board[row][col]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged
            self.flags_placed += 1 if cell.is_flagged else -1

    def check_win(self):
        """Проверка условия победы."""
        for row in self.board:
            for cell in row:
                # Если все не-мины открыты, игрок победил
                if not cell.is_mine and not cell.is_revealed:
                    return
        self.game_won = True
        self.game_over = True

    def draw(self, screen, cell_size, x_offset, y_offset, current_time):
        """Отрисовка всего игрового поля."""
        for row in self.board:
            for cell in row:
                cell.draw(screen, cell_size, x_offset, y_offset, current_time)

# --- Основная логика ---
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Сапер")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)

    # Выбор уровня
    level_names = list(LEVELS.keys())
    current_level_idx = 0
    rows, cols, mines = LEVELS[level_names[current_level_idx]]
    
    # Рассчитываем размер ячейки и смещения для центрирования
    max_board_width = SCREEN_WIDTH
    max_board_height = SCREEN_HEIGHT - INFO_HEIGHT
    cell_size = min(max_board_width // cols, max_board_height // rows)
    # Корректируем размер, если он слишком большой
    cell_size = min(cell_size, 40) 
    
    board_width = cols * cell_size
    board_height = rows * cell_size
    x_offset = (SCREEN_WIDTH - board_width) // 2
    y_offset = INFO_HEIGHT + (max_board_height - board_height) // 2

    game = Game(rows, cols, mines)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        if game.start_time > 0 and not game.game_over:
            game.elapsed_time = (current_time - game.start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Перезапуск игры
                    game.initialize_board()
                elif event.key == pygame.K_n: # Следующий уровень
                    current_level_idx = (current_level_idx + 1) % len(level_names)
                    rows, cols, mines = LEVELS[level_names[current_level_idx]]
                    # Пересчитываем размеры
                    cell_size = min(max_board_width // cols, max_board_height // rows)
                    cell_size = min(cell_size, 40)
                    board_width = cols * cell_size
                    board_height = rows * cell_size
                    x_offset = (SCREEN_WIDTH - board_width) // 2
                    y_offset = INFO_HEIGHT + (max_board_height - board_height) // 2
                    game = Game(rows, cols, mines)
                elif event.key == pygame.K_l: # Предыдущий уровень
                    current_level_idx = (current_level_idx - 1) % len(level_names)
                    rows, cols, mines = LEVELS[level_names[current_level_idx]]
                    cell_size = min(max_board_width // cols, max_board_height // rows)
                    cell_size = min(cell_size, 40)
                    board_width = cols * cell_size
                    board_height = rows * cell_size
                    x_offset = (SCREEN_WIDTH - board_width) // 2
                    y_offset = INFO_HEIGHT + (max_board_height - board_height) // 2
                    game = Game(rows, cols, mines)

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                mouse_x, mouse_y = event.pos
                # Проверяем, кликнули ли мы на поле
                if (x_offset <= mouse_x < x_offset + board_width and
                    y_offset <= mouse_y < y_offset + board_height):
                    col = (mouse_x - x_offset) // cell_size
                    row = (mouse_y - y_offset) // cell_size
                    
                    if event.button == 1: # Левая кнопка мыши
                        game.reveal(row, col)
                    elif event.button == 3: # Правая кнопка мыши
                        game.toggle_flag(row, col)

        # --- Отрисовка ---
        screen.fill(WHITE)
        
        # Отрисовка информационной панели
        info_rect = pygame.Rect(0, 0, SCREEN_WIDTH, INFO_HEIGHT)
        pygame.draw.rect(screen, DARK_GRAY, info_rect)
        pygame.draw.line(screen, BLACK, (0, INFO_HEIGHT), (SCREEN_WIDTH, INFO_HEIGHT), 2)
        
        # Отображение мин и времени
        mines_text = font.render(f"Мины: {mines - game.flags_placed}", True, RED)
        time_text = font.render(f"Время: {game.elapsed_time}s", True, BLUE)
        level_text = small_font.render(f"Уровень: {level_names[current_level_idx]}", True, BLACK)
        restart_text = small_font.render("R - Перезапуск, N - След., L - Пред.", True, BLACK)
        
        screen.blit(mines_text, (10, 10))
        screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 5))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, INFO_HEIGHT - 20))

        # Отрисовка игрового поля
        game.draw(screen, cell_size, x_offset, y_offset, current_time)

        # Отображение сообщения о конце игры
        if game.game_over:
            if game.game_won:
                end_text = font.render("Вы выиграли! Нажмите 'R' для перезапуска.", True, GREEN)
            else:
                end_text = font.render("Вы проиграли! Нажмите 'R' для перезапуска.", True, RED)
            
            # Центрируем текст
            text_rect = end_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            # Рисуем полупрозрачный фон для текста
            background_rect = text_rect.inflate(20, 10)
            s = pygame.Surface((background_rect.width, background_rect.height), pygame.SRCALPHA)
            s.fill((255, 255, 255, 200)) # Белый с 200 прозрачностью
            screen.blit(s, background_rect.topleft)
            screen.blit(end_text, text_rect.topleft)

        pygame.display.flip()
        clock.tick(60) # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()