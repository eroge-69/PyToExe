import pygame
import random
import sys
import time

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
GRID_SIZE = 8
CELL_SIZE = 60
MARGIN = 50
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BACKGROUND = (50, 50, 80)

# Цвета для квадратиков
COLORS = [
    (255, 0, 0),    # Красный
    (0, 255, 0),    # Зеленый
    (0, 0, 255),    # Синий
    (255, 255, 0),  # Желтый
    (255, 0, 255),  # Пурпурный
    (0, 255, 255),  # Голубой
]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Три в ряд")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.grid = []
        self.selected = None
        self.score = 0
        self.initialize_grid()
        
    def initialize_grid(self):
        """Инициализация игрового поля"""
        self.grid = []
        for row in range(GRID_SIZE):
            self.grid.append([])
            for col in range(GRID_SIZE):
                color = random.choice(COLORS)
                self.grid[row].append(color)
        
        # Убедимся, что нет начальных совпадений
        while self.find_matches():
            self.remove_matches()
            self.fill_empty_cells()
    
    def draw(self):
        """Отрисовка игрового поля и интерфейса"""
        self.screen.fill(BACKGROUND)
        
        # Отрисовка сетки
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = MARGIN + col * CELL_SIZE
                y = MARGIN + row * CELL_SIZE
                
                # Рамка для выделенного элемента
                if self.selected == (row, col):
                    pygame.draw.rect(self.screen, WHITE, 
                                   (x-2, y-2, CELL_SIZE+4, CELL_SIZE+4), 3)
                
                # Квадратик
                pygame.draw.rect(self.screen, self.grid[row][col],
                               (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, GRAY,
                               (x, y, CELL_SIZE, CELL_SIZE), 2)
        
        # Отрисовка счета
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 10))
        
        # Инструкция
        instruction = self.small_font.render("Выберите два соседних квадратика для обмена", True, WHITE)
        self.screen.blit(instruction, (20, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def get_cell_at_pos(self, pos):
        """Получение координат ячейки по позиции мыши"""
        x, y = pos
        if (MARGIN <= x <= MARGIN + GRID_SIZE * CELL_SIZE and
            MARGIN <= y <= MARGIN + GRID_SIZE * CELL_SIZE):
            col = (x - MARGIN) // CELL_SIZE
            row = (y - MARGIN) // CELL_SIZE
            return row, col
        return None
    
    def are_adjacent(self, pos1, pos2):
        """Проверка, являются ли две ячейки соседними"""
        row1, col1 = pos1
        row2, col2 = pos2
        
        # Проверка по вертикали или горизонтали
        return (abs(row1 - row2) == 1 and col1 == col2) or \
               (abs(col1 - col2) == 1 and row1 == row2)
    
    def swap_cells(self, pos1, pos2):
        """Обмен двух ячеек"""
        row1, col1 = pos1
        row2, col2 = pos2
        
        self.grid[row1][col1], self.grid[row2][col2] = \
        self.grid[row2][col2], self.grid[row1][col1]
    
    def find_matches(self):
        """Поиск совпадений (три и более в ряд)"""
        matches = []
        
        # Проверка по горизонтали
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] == self.grid[row][col + 1] == 
                    self.grid[row][col + 2]):
                    # Найдено совпадение, ищем все подряд идущие
                    color = self.grid[row][col]
                    end_col = col + 2
                    while end_col + 1 < GRID_SIZE and self.grid[row][end_col + 1] == color:
                        end_col += 1
                    
                    for c in range(col, end_col + 1):
                        matches.append((row, c))
        
        # Проверка по вертикали
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2):
                if (self.grid[row][col] == self.grid[row + 1][col] == 
                    self.grid[row + 2][col]):
                    # Найдено совпадение, ищем все подряд идущие
                    color = self.grid[row][col]
                    end_row = row + 2
                    while end_row + 1 < GRID_SIZE and self.grid[end_row + 1][col] == color:
                        end_row += 1
                    
                    for r in range(row, end_row + 1):
                        matches.append((r, col))
        
        return list(set(matches))  # Убираем дубликаты
    
    def remove_matches(self):
        """Удаление совпадающих элементов и подсчет очков"""
        matches = self.find_matches()
        if matches:
            # Подсчет очков: больше очков за большее количество в ряд
            match_groups = self.group_matches(matches)
            for group in match_groups:
                self.score += len(group) * 10
            
            # Удаление совпадающих элементов
            for row, col in matches:
                self.grid[row][col] = None
            
            return True
        return False
    
    def group_matches(self, matches):
        """Группировка совпадений по строкам и столбцам"""
        groups = []
        visited = set()
        
        for match in matches:
            if match not in visited:
                # Находим все связанные совпадения
                group = self.find_connected_matches(match, matches)
                groups.append(group)
                visited.update(group)
        
        return groups
    
    def find_connected_matches(self, start, matches):
        """Поиск всех связанных совпадений от начальной точки"""
        stack = [start]
        group = set()
        
        while stack:
            current = stack.pop()
            if current in group:
                continue
            
            group.add(current)
            row, col = current
            
            # Проверяем соседей
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (row + dr, col + dc)
                if neighbor in matches and neighbor not in group:
                    stack.append(neighbor)
        
        return list(group)
    
    def fill_empty_cells(self):
        """Заполнение пустых ячеек новыми элементами"""
        for col in range(GRID_SIZE):
            # Собираем все непустые элементы в столбце снизу вверх
            non_empty = []
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is not None:
                    non_empty.append(self.grid[row][col])
            
            # Заполняем столбец сверху пустыми ячейками, затем непустыми
            for row in range(GRID_SIZE):
                if row < GRID_SIZE - len(non_empty):
                    self.grid[row][col] = random.choice(COLORS)
                else:
                    self.grid[row][col] = non_empty[GRID_SIZE - row - 1]
    
    def has_valid_moves(self):
        """Проверка наличия возможных ходов"""
        # Временный обмен соседних элементов и проверка на совпадения
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Проверка обмена с правым соседом
                if col < GRID_SIZE - 1:
                    self.swap_cells((row, col), (row, col + 1))
                    if self.find_matches():
                        self.swap_cells((row, col), (row, col + 1))  # Возвращаем обратно
                        return True
                    self.swap_cells((row, col), (row, col + 1))
                
                # Проверка обмена с нижним соседом
                if row < GRID_SIZE - 1:
                    self.swap_cells((row, col), (row + 1, col))
                    if self.find_matches():
                        self.swap_cells((row, col), (row + 1, col))  # Возвращаем обратно
                        return True
                    self.swap_cells((row, col), (row + 1, col))
        
        return False
    
    def run(self):
        """Основной игровой цикл"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    cell_pos = self.get_cell_at_pos(event.pos)
                    
                    if cell_pos:
                        if self.selected is None:
                            # Первое выделение
                            self.selected = cell_pos
                        else:
                            # Второе выделение - попытка обмена
                            if self.are_adjacent(self.selected, cell_pos):
                                # Сохраняем состояние для возможного отката
                                temp_grid = [row[:] for row in self.grid]
                                
                                # Пробуем обмен
                                self.swap_cells(self.selected, cell_pos)
                                
                                # Проверяем, привело ли это к совпадению
                                if self.find_matches():
                                    # Удаляем совпадения и обновляем поле
                                    while self.remove_matches():
                                        self.draw()
                                        pygame.display.flip()
                                        time.sleep(0.3)  # Небольшая пауза для визуализации
                                        self.fill_empty_cells()
                                        self.draw()
                                        pygame.display.flip()
                                        time.sleep(0.3)
                                    
                                    # Проверяем остались ли возможные ходы
                                    if not self.has_valid_moves():
                                        game_over_text = self.font.render("Игра окончена! Нет возможных ходов.", True, WHITE)
                                        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))
                                        pygame.display.flip()
                                        time.sleep(3)
                                        self.initialize_grid()
                                        self.score = 0
                                else:
                                    # Если совпадений нет - возвращаем обратно
                                    self.grid = temp_grid
                            
                            self.selected = None
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()