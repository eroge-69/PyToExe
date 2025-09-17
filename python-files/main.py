import pygame
import random
import sys
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (230, 230, 230)
RED = (255, 80, 80)
GREEN = (80, 200, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 220, 80)
PURPLE = (180, 80, 220)
CYAN = (80, 200, 200)
ORANGE = (255, 150, 50)

# Цвета для цифр
NUMBER_COLORS = {
    1: BLUE,
    2: GREEN,
    3: RED,
    4: PURPLE,
    5: (150, 0, 0),
    6: CYAN,
    7: BLACK,
    8: DARK_GRAY
}

# Уровни сложности
DIFFICULTY_LEVELS = {
    "Лёгкий": {"width": 9, "height": 9, "mines": 10},
    "Средний": {"width": 16, "height": 16, "mines": 40},
    "Сложный": {"width": 24, "height": 20, "mines": 99}
}


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        self.highlighted = False

    def reveal(self):
        self.is_revealed = True
        self.highlighted = False

    def toggle_flag(self):
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged


class Game:
    def __init__(self, difficulty="Средний", screen_width=DEFAULT_WIDTH, screen_height=DEFAULT_HEIGHT):
        self.difficulty = difficulty
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.set_difficulty(difficulty)
        self.reset()

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        config = DIFFICULTY_LEVELS[difficulty]
        self.grid_width = config["width"]
        self.grid_height = config["height"]
        self.mines_count = config["mines"]

        # Автоматический расчет размера ячейки на основе размера окна
        self.calculate_cell_size()

    def calculate_cell_size(self):
        # Рассчитываем максимальный размер ячейки, который помещается в окно
        max_cell_width = (self.screen_width - 40) // self.grid_width
        max_cell_height = (self.screen_height - 120) // self.grid_height
        self.cell_size = min(max_cell_width, max_cell_height, 50)  # Ограничиваем максимальный размер

        # Минимальный размер ячейки
        self.cell_size = max(self.cell_size, 15)

        # Пересчитываем размеры окна для идеального соответствия
        self.width = self.grid_width * self.cell_size + 40
        self.height = self.grid_height * self.cell_size + 120

        # Создаем окно
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

    def handle_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.calculate_cell_size()

    def reset(self):
        self.grid = [[Cell(x, y) for y in range(self.grid_width)] for x in range(self.grid_height)]
        self.game_over = False
        self.game_won = False
        self.mines_flagged = 0
        self.first_click = True
        self.start_time = 0
        self.elapsed_time = 0
        self.highlight_cell = None

        # Шрифты
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_medium = pygame.font.SysFont("Arial", max(14, self.cell_size // 2), bold=True)
        self.font_large = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_huge = pygame.font.SysFont("Arial", 48, bold=True)

    def place_mines(self, first_x, first_y):
        safe_cells = [(first_x, first_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < self.grid_height and 0 <= ny < self.grid_width:
                    safe_cells.append((nx, ny))

        mines_placed = 0
        while mines_placed < self.mines_count:
            x, y = random.randint(0, self.grid_height - 1), random.randint(0, self.grid_width - 1)
            if (x, y) not in safe_cells and not self.grid[x][y].is_mine:
                self.grid[x][y].is_mine = True
                mines_placed += 1

                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.grid_height and 0 <= ny < self.grid_width:
                            self.grid[nx][ny].neighbor_mines += 1

    def reveal_cell(self, x, y):
        if not (0 <= x < self.grid_height and 0 <= y < self.grid_width):
            return

        cell = self.grid[x][y]

        if cell.is_revealed or cell.is_flagged:
            return

        if self.first_click:
            self.first_click = False
            self.place_mines(x, y)
            self.start_time = pygame.time.get_ticks()

        cell.reveal()

        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return

        if cell.neighbor_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        self.reveal_cell(x + dx, y + dy)

        self.check_win()

    def reveal_all_mines(self):
        for row in self.grid:
            for cell in row:
                if cell.is_mine:
                    cell.is_revealed = True

    def toggle_flag(self, x, y):
        if not (0 <= x < self.grid_height and 0 <= y < self.grid_width):
            return

        cell = self.grid[x][y]

        if not cell.is_revealed:
            cell.toggle_flag()
            if cell.is_flagged:
                self.mines_flagged += 1
            else:
                self.mines_flagged -= 1

    def check_win(self):
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return
        self.game_won = True

    def draw_cell(self, cell, x, y):
        rect = pygame.Rect(
            y * self.cell_size + 20,
            x * self.cell_size + 80,
            self.cell_size - 2,
            self.cell_size - 2
        )

        # Рисуем фон ячейки
        if cell.is_revealed:
            color = LIGHT_GRAY
            if cell.highlighted:
                color = (240, 240, 200)
            pygame.draw.rect(self.screen, color, rect)

            if cell.is_mine:
                # Мина
                pygame.draw.circle(self.screen, BLACK, rect.center, self.cell_size // 3 - 2)
                pygame.draw.circle(self.screen, DARK_GRAY, rect.center, self.cell_size // 4)

            elif cell.neighbor_mines > 0:
                font_size = max(14, self.cell_size // 2)
                font = pygame.font.SysFont("Arial", font_size, bold=True)
                text = font.render(str(cell.neighbor_mines), True, NUMBER_COLORS[cell.neighbor_mines])
                self.screen.blit(text, (rect.centerx - text.get_width() // 2,
                                        rect.centery - text.get_height() // 2))
        else:
            # Неоткрытая ячейка с 3D эффектом
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.line(self.screen, WHITE, rect.topleft, (rect.right, rect.top), 2)
            pygame.draw.line(self.screen, WHITE, rect.topleft, (rect.left, rect.bottom), 2)
            pygame.draw.line(self.screen, DARK_GRAY, (rect.right, rect.top), rect.bottomright, 2)
            pygame.draw.line(self.screen, DARK_GRAY, (rect.left, rect.bottom), rect.bottomright, 2)

            if cell.is_flagged:
                # Флажок
                flag_color = RED
                pole_rect = pygame.Rect(rect.centerx - 2, rect.top + 5, 4, rect.height - 10)
                pygame.draw.rect(self.screen, BLACK, pole_rect)

                flag_points = [
                    (rect.centerx + 2, rect.top + 8),
                    (rect.centerx + 2, rect.top + self.cell_size // 2),
                    (rect.right - 5, rect.top + self.cell_size // 3)
                ]
                pygame.draw.polygon(self.screen, flag_color, flag_points)

    def draw(self):
        # Фон
        self.screen.fill((240, 240, 240))

        # Заголовок
        title_bg = pygame.Rect(0, 0, self.width, 70)
        pygame.draw.rect(self.screen, (60, 80, 120), title_bg)

        title = self.font_large.render("САПЁР", True, WHITE)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        # Информация о сложности
        diff_text = self.font_small.render(f"Уровень: {self.difficulty}", True, WHITE)
        self.screen.blit(diff_text, (20, 25))

        # Панель статуса
        status_bg = pygame.Rect(10, self.height - 60, self.width - 20, 50)
        pygame.draw.rect(self.screen, WHITE, status_bg, border_radius=8)
        pygame.draw.rect(self.screen, (180, 180, 180), status_bg, 2, border_radius=8)

        # Мины
        mines_text = self.font_medium.render(f"Мины: {self.mines_count - self.mines_flagged}", True, RED)
        self.screen.blit(mines_text, (30, self.height - 45))

        # Время
        if not self.game_over and not self.game_won and not self.first_click:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.font_medium.render(f"Время: {self.elapsed_time}s", True, BLUE)
        self.screen.blit(time_text, (self.width - 120, self.height - 45))

        # Кнопка перезапуска
        restart_rect = pygame.Rect(self.width // 2 - 50, self.height - 50, 100, 30)
        pygame.draw.rect(self.screen, GREEN if not (self.game_over or self.game_won) else ORANGE,
                         restart_rect, border_radius=15)
        pygame.draw.rect(self.screen, DARK_GRAY, restart_rect, 2, border_radius=15)

        restart_text = self.font_small.render("Перезапуск", True, WHITE)
        self.screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2,
                                        restart_rect.centery - restart_text.get_height() // 2))

        # Игровое поле
        field_bg = pygame.Rect(15, 75, self.grid_width * self.cell_size + 10,
                               self.grid_height * self.cell_size + 10)
        pygame.draw.rect(self.screen, (200, 200, 200), field_bg, border_radius=5)

        # Ячейки
        for x in range(self.grid_height):
            for y in range(self.grid_width):
                self.draw_cell(self.grid[x][y], x, y)

        # Сообщения о конце игры
        if self.game_over or self.game_won:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            if self.game_over:
                text = self.font_huge.render("ПОРАЖЕНИЕ!", True, RED)
            else:
                text = self.font_huge.render("ПОБЕДА!", True, GREEN)

            self.screen.blit(text, (self.width // 2 - text.get_width() // 2,
                                    self.height // 2 - text.get_height() // 2 - 30))

            subtext = self.font_medium.render("Нажмите R для новой игры", True, WHITE)
            self.screen.blit(subtext, (self.width // 2 - subtext.get_width() // 2,
                                       self.height // 2 + 20))

    def get_cell_at_pos(self, x, y):
        """Преобразует координаты мыши в координаты ячейки"""
        if x < 20 or y < 80:
            return None, None

        cell_x = (y - 80) // self.cell_size
        cell_y = (x - 20) // self.cell_size

        if (0 <= cell_x < self.grid_height and
                0 <= cell_y < self.grid_width):
            return cell_x, cell_y
        return None, None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Проверяем клик по кнопке перезапуска
            restart_rect = pygame.Rect(self.width // 2 - 50, self.height - 50, 100, 30)
            if restart_rect.collidepoint(x, y):
                self.reset()
                return

            # Проверяем клик по игровому полю
            cell_x, cell_y = self.get_cell_at_pos(x, y)
            if cell_x is not None and cell_y is not None:
                if event.button == 1:  # Левая кнопка
                    if not self.game_over and not self.game_won:
                        self.reveal_cell(cell_x, cell_y)

                elif event.button == 3:  # Правая кнопка
                    if not self.game_over and not self.game_won:
                        self.toggle_flag(cell_x, cell_y)

        elif event.type == pygame.MOUSEMOTION:
            # Подсветка ячейки при наведении
            x, y = pygame.mouse.get_pos()
            cell_x, cell_y = self.get_cell_at_pos(x, y)

            # Сбрасываем предыдущую подсветку
            if self.highlight_cell:
                old_x, old_y = self.highlight_cell
                if 0 <= old_x < self.grid_height and 0 <= old_y < self.grid_width:
                    self.grid[old_x][old_y].highlighted = False

            # Устанавливаем новую подсветку
            if cell_x is not None and cell_y is not None:
                self.grid[cell_x][cell_y].highlighted = True
                self.highlight_cell = (cell_x, cell_y)
            else:
                self.highlight_cell = None


class Menu:
    def __init__(self):
        self.screen_width = DEFAULT_WIDTH
        self.screen_height = DEFAULT_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Сапёр - Меню")

        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 24)
        self.font_button = pygame.font.SysFont("Arial", 20)

        self.create_buttons()

    def create_buttons(self):
        self.buttons = {}
        center_x = self.screen_width // 2
        button_width = min(250, self.screen_width - 100)
        button_height = 50

        # Кнопки сложности
        difficulties = list(DIFFICULTY_LEVELS.keys())
        for i, diff in enumerate(difficulties):
            self.buttons[diff] = pygame.Rect(
                center_x - button_width // 2,
                200 + i * 70,
                button_width,
                button_height
            )

        # Кнопка выхода
        self.buttons["exit"] = pygame.Rect(
            center_x - button_width // 2,
            200 + len(difficulties) * 70 + 20,
            button_width,
            button_height
        )

    def handle_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.create_buttons()

    def draw(self):
        # Фон с градиентом
        for y in range(self.screen_height):
            color = (50 + y // 10, 70 + y // 8, 100 + y // 6)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))

        # Заголовок
        title = self.font_title.render("САПЁР", True, WHITE)
        subtitle = self.font_subtitle.render("Выберите уровень сложности", True, WHITE)

        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 80))
        self.screen.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 140))

        # Кнопки
        for text, rect in self.buttons.items():
            # Красивая кнопка
            pygame.draw.rect(self.screen, (60, 80, 120), rect, border_radius=10)
            pygame.draw.rect(self.screen, (40, 60, 100), rect, 3, border_radius=10)

            # Тень
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, (30, 40, 60), shadow_rect, border_radius=10)

            # Текст
            btn_text = self.font_button.render(text, True, WHITE)
            self.screen.blit(btn_text, (rect.centerx - btn_text.get_width() // 2,
                                        rect.centery - btn_text.get_height() // 2))

        # Подсказка
        hint = self.font_subtitle.render("Или нажмите ESC для выхода", True, WHITE)
        self.screen.blit(hint, (self.screen_width // 2 - hint.get_width() // 2,
                                self.screen_height - 60))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            for difficulty, rect in self.buttons.items():
                if rect.collidepoint(x, y):
                    if difficulty == "exit":
                        return "exit"
                    return difficulty
        return None


def main():
    clock = pygame.time.Clock()

    # Показываем меню
    menu = Menu()
    difficulty = None

    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                menu.handle_resize(event.w, event.h)

            result = menu.handle_event(event)
            if result == "exit":
                pygame.quit()
                sys.exit()
            elif result:
                difficulty = result

        menu.draw()
        pygame.display.flip()
        clock.tick(FPS)

    # Запускаем игру
    game = Game(difficulty, menu.screen_width, menu.screen_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_m:
                    # Возврат в меню
                    return main()
            elif event.type == pygame.VIDEORESIZE:
                game.handle_resize(event.w, event.h)

            game.handle_event(event)

        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    from setuptools import setup

    setup(
        name='сапер',
        version='1.0',
        packages=[],
        scripts=['main.py'],
        install_requires=['pygame'],
        entry_points={
            'gui_scripts': [
                'сапер = main:main'
            ]
        },
    )