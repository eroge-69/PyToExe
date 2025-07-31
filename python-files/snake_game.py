import pygame
import random
import json
import os
import time

pygame.init()

# Настройки экрана
SCREEN_WIDTH = 810
SCREEN_HEIGHT = 600
CELL_SIZE = 30
FPS = 7
FPS_INCREMENT = 0.04

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
UI_COLOR = (183, 219, 165)

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def create(self):
        start_x = (SCREEN_WIDTH // 2) // CELL_SIZE * CELL_SIZE
        start_y = (SCREEN_HEIGHT // 2) // CELL_SIZE * CELL_SIZE
        self.body = [(start_x, start_y)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0
        self.level = 1
        self.speed = FPS
        self.obstacles = []
        self.game_mode = "obstacles"

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_x = head_x + dir_x * CELL_SIZE
        new_y = head_y + dir_y * CELL_SIZE
        new_head = (new_x, new_y)

        if (new_x < 0 or new_x >= SCREEN_WIDTH or
                new_y < 0 or new_y >= SCREEN_HEIGHT):
            return False

        if new_head in self.body[1:] or new_head in self.obstacles:
            return False

        self.body.insert(0, new_head)
        if len(self.body) > self.length:
            self.body.pop()
        return True

    def grow(self, is_special=False):
        self.length += 1
        self.score += 20 * self.level if is_special else 10 * self.level

        if self.score >= self.level * 30:
            self.level += 1
            self.speed += FPS_INCREMENT
            self.add_obstacles()

    def add_obstacles(self):
        if self.game_mode == "classic":
            return

        for _ in range(self.level // 3):
            while True:
                x = random.randrange(0, SCREEN_WIDTH, CELL_SIZE)
                y = random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)
                obstacle = (x, y)

                head_x, head_y = self.body[0]
                if (abs(x - head_x) > 3 * CELL_SIZE or abs(y - head_y) > 3 * CELL_SIZE):
                    if obstacle not in self.body and obstacle not in self.obstacles:
                        self.obstacles.append(obstacle)
                        break

    def change_direction(self, new_dir):
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir


class Food:
    def create(self):
        self.position = (0, 0)
        self.special_position = (0, 0)
        self.special_active = False
        self.special_spawn_time = 0
        self.spawn([])

    def spawn(self, obstacles):
        if self.special_active:
            return

        if random.random() < 0.15:
            self.spawn_special(obstacles)
        else:
            self.spawn_regular(obstacles)

    def spawn_regular(self, obstacles):
        while True:
            x = random.randrange(0, SCREEN_WIDTH, CELL_SIZE)
            y = random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)
            self.position = (x, y)
            if self.position not in obstacles:
                self.is_special = False
                break

    def spawn_special(self, obstacles):
        while True:
            x = random.randrange(0, SCREEN_WIDTH, CELL_SIZE)
            y = random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)
            self.special_position = (x, y)
            if self.special_position not in obstacles:
                self.special_active = True
                self.special_spawn_time = time.time()
                self.position = (-CELL_SIZE, -CELL_SIZE)
                break

    def update(self):
        if self.special_active and time.time() - self.special_spawn_time > 10:
            self.special_active = False
            self.spawn([])


class Game:
    def setup(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Змейка")
        self.clock = pygame.time.Clock()

        # Инициализация шрифтов и изображений
        self.init_assets()

        self.snake = Snake()
        self.snake.create()
        self.food = Food()
        self.food.create()

        self.state = "welcome"
        self.current_user = None
        self.user_input = ""
        self.input_active = True
        self.highscores = []
        self.users = {}
        self.game_mode = "obstacles"
        self.show_help_screen = False

        self.load_data()

    def init_assets(self):
        """Инициализация всех ресурсов игры"""
        # Загрузка иконки
        self.load_icon()

        # Загрузка шрифтов
        try:
            self.font = pygame.font.Font('font.ttf', 25)
            self.big_font = pygame.font.Font('font.ttf', 50)
            self.small_font = pygame.font.Font('font.ttf', 20)
        except:
            self.font = pygame.font.SysFont('Arial', 25)
            self.big_font = pygame.font.SysFont('Arial', 50)
            self.small_font = pygame.font.SysFont('Arial', 20)

        # Загрузка фоновых изображений
        self.backgrounds = {
            'login': self.load_image('login_bg.png'),
            'help': self.load_image('help_bg.png'),
            'menu': self.load_image('menu_bg.png'),
            'highscores': self.load_image('highscores_bg.png'),
            'gameover': self.load_image('gameover_bg.png'),
            'game': self.load_image('game_bg.png')
        }

        # Загрузка изображений объектов
        self.images = {
            'snake_head': self.load_image('snake_head.png', True, CELL_SIZE),
            'snake_body': self.load_image('snake_body.png', True, CELL_SIZE),
            'snake_corner': self.load_image('snake_corner.png', True, CELL_SIZE),
            'snake_tail': self.load_image('snake_tail.png', True, CELL_SIZE),
            'regular_food': self.load_image('red_apple.png', True, CELL_SIZE),
            'special_food': self.load_image('golden_apple.png', True, CELL_SIZE),
            'obstacle': self.load_image('obstacle.png', True, CELL_SIZE)
        }

    def load_icon(self):
        """Загрузка иконки приложения"""
        try:
            icon = pygame.image.load('icon.ico')
            pygame.display.set_icon(icon)
        except:
            icon = pygame.Surface((32, 32))
            icon.fill(GREEN)
            pygame.display.set_icon(icon)

    def load_image(self, filename, alpha=False, size=None):
        """Универсальная функция загрузки изображений"""
        try:
            if alpha:
                img = pygame.image.load(filename).convert_alpha()
            else:
                img = pygame.image.load(filename).convert()
            if size:
                img = pygame.transform.scale(img, (size, size) if isinstance(size, int) else size)
            return img
        except:
            return None

    def load_data(self):
        """Загрузка данных игроков и рекордов"""
        try:
            if os.path.exists('users.json'):
                with open('users.json') as f:
                    self.users = json.load(f)
        except:
            self.users = {}

        try:
            if os.path.exists('highscores.json'):
                with open('highscores.json') as f:
                    self.highscores = json.load(f)
        except:
            self.highscores = []

    def save_data(self):
        with open('users.json', 'w') as f:
            json.dump(self.users, f)

        with open('highscores.json', 'w') as f:
            json.dump(self.highscores, f)

    def add_highscore(self):
        if self.snake.score > 0:
            self.highscores.append({
                'name': self.current_user,
                'score': self.snake.score,
                'level': self.snake.level,
            })

            if self.current_user in self.users:
                if self.snake.score > self.users[self.current_user].get('best_score', 0):
                    self.users[self.current_user]['best_score'] = self.snake.score
            else:
                self.users[self.current_user] = {'best_score': self.snake.score}

            self.save_data()

    def draw_snake(self):
        for i, segment in enumerate(self.snake.body):
            # Голова
            if i == 0:
                angle = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: 270}[self.snake.direction]
                img = self.images['snake_head']
            # Хвост
            elif i == len(self.snake.body) - 1:
                prev_seg = self.snake.body[i - 1]
                if prev_seg[0] < segment[0]:
                    angle = 0
                elif prev_seg[0] > segment[0]:
                    angle = 180
                elif prev_seg[1] < segment[1]:
                    angle = 270
                else:
                    angle = 90
                img = self.images['snake_tail']
            # Тело
            else:
                prev_seg = self.snake.body[i - 1]
                next_seg = self.snake.body[i + 1]

                if prev_seg[0] == next_seg[0]:  # Вертикальный
                    angle = 90
                    img = self.images['snake_body']
                elif prev_seg[1] == next_seg[1]:  # Горизонтальный
                    angle = 0
                    img = self.images['snake_body']
                else:  # Угловой
                    if (prev_seg[0] < segment[0] and next_seg[1] < segment[1]) or \
                            (next_seg[0] < segment[0] and prev_seg[1] < segment[1]):
                        angle = 270
                    elif (prev_seg[0] > segment[0] and next_seg[1] < segment[1]) or \
                            (next_seg[0] > segment[0] and prev_seg[1] < segment[1]):
                        angle = 180
                    elif (prev_seg[0] < segment[0] and next_seg[1] > segment[1]) or \
                            (next_seg[0] < segment[0] and prev_seg[1] > segment[1]):
                        angle = 0
                    else:
                        angle = 90
                    img = self.images['snake_corner'] or self.images['snake_body']

            if img:
                self.screen.blit(pygame.transform.rotate(img, angle), (segment[0], segment[1]))
            else:
                rect = pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GREEN, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_food(self):
        if self.images['regular_food']:
            self.screen.blit(self.images['regular_food'], self.food.position)
        else:
            rect = pygame.Rect(self.food.position[0], self.food.position[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, RED, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_special_food(self):
        if self.food.special_active and self.images['special_food']:
            self.screen.blit(self.images['special_food'], self.food.special_position)

    def draw_obstacles(self):
        for obs in self.snake.obstacles:
            if self.images['obstacle']:
                self.screen.blit(self.images['obstacle'], obs)
            else:
                rect = pygame.Rect(obs[0], obs[1], CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, BLUE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_text(self, text, font, color, x, y, centered=False):
        text_surf = font.render(text, True, color)
        if centered:
            text_rect = text_surf.get_rect(center=(x, y))
        else:
            text_rect = text_surf.get_rect(topleft=(x, y))
        self.screen.blit(text_surf, text_rect)
        return text_rect

    def show_help(self):
        self.screen.blit(self.backgrounds['help'], (0, 0))
        help_texts = [
            "Управление в игре:", "Стрелки - движение змейки", "P - пауза       ESC - выход в меню", "",
            "Цель игры:", "Избегайте препятствий", "Собирайте еду",
            "Бейте свои рекорды съедая яблоки", "Красное: 10 очков * уровень",
            "Золотое: 20 очков * уровень", "Выше уровень - быстрее змейка",
            "и больше препятствий", "", "Нажмите любую клавишу для выхода"
        ]

        for i, text in enumerate(help_texts):
            self.draw_text(text, self.font, UI_COLOR, SCREEN_WIDTH // 2, 150 + i * 30, True)

    def show_welcome_screen(self):
        self.screen.blit(self.backgrounds['login'], (0, 0))
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 315, 300, 40)
        pygame.draw.rect(self.screen, UI_COLOR if self.input_active else GRAY, input_rect, 2)
        self.draw_text(self.user_input, self.font, UI_COLOR, input_rect.x + 10, input_rect.y + 10)

        # Кнопка помощи
        help_btn = pygame.Rect(SCREEN_WIDTH - 50, 20, 30, 30)
        pygame.draw.circle(self.screen, UI_COLOR, (SCREEN_WIDTH - 35, 35), 15)
        self.draw_text("?", self.font, BLACK, SCREEN_WIDTH - 35, 35, True)

        mouse_pos = pygame.mouse.get_pos()
        if input_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.input_active = True
        elif pygame.mouse.get_pressed()[0]:
            self.input_active = False

        if help_btn.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.show_help_screen = True

    def show_menu(self):
        self.screen.blit(self.backgrounds['menu'], (0, 0))

        if self.current_user:
            best_score = self.users.get(self.current_user, {}).get('best_score', 0)
            info_text = f"Игрок: {self.current_user}  |  Счёт: {best_score}"
            rect_width = self.font.size(info_text)[0] + 40
            user_rect = pygame.Rect((SCREEN_WIDTH - rect_width) // 2, 170, rect_width, 40)
            pygame.draw.rect(self.screen, UI_COLOR, user_rect, 2)
            self.draw_text(info_text, self.font, UI_COLOR, user_rect.centerx, user_rect.centery, True)

        # Кнопка помощи
        help_btn = pygame.Rect(SCREEN_WIDTH - 50, 20, 30, 30)
        pygame.draw.circle(self.screen, UI_COLOR, (SCREEN_WIDTH - 35, 35), 15)
        self.draw_text("?", self.font, BLACK, SCREEN_WIDTH - 35, 35, True)

        # Элементы меню
        mode_label = self.draw_text("Режим игры:", self.font, UI_COLOR, SCREEN_WIDTH // 2, 250, True)
        classic_btn = self.draw_text("Классический", self.font, UI_COLOR, SCREEN_WIDTH // 2 - 130, 290, True)
        obstacles_btn = self.draw_text("С препятствиями", self.font, UI_COLOR, SCREEN_WIDTH // 2 + 110, 290, True)

        # Подчеркивание выбранного режима
        underline_x = SCREEN_WIDTH // 2 - 130 - 70 if self.game_mode == "classic" else SCREEN_WIDTH // 2 + 110 - 90
        pygame.draw.line(self.screen, UI_COLOR, (underline_x, 310), (underline_x + 140, 310), 2)

        # Основные кнопки меню
        buttons = [
            ("Играть", 350),
            ("Рекорды", 400),
            ("Сменить пользователя", 450),
            ("Выход", 500)
        ]

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if classic_btn.collidepoint(mouse_pos) and mouse_clicked:
            self.game_mode = "classic"
        if obstacles_btn.collidepoint(mouse_pos) and mouse_clicked:
            self.game_mode = "obstacles"

        for text, y_pos in buttons:
            btn = self.draw_text(text, self.font, UI_COLOR, SCREEN_WIDTH // 2, y_pos, True)
            if btn.collidepoint(mouse_pos) and mouse_clicked:
                if text == "Играть":
                    self.state = "game"
                    self.snake.create()
                    self.snake.game_mode = self.game_mode
                    if self.game_mode == "classic":
                        self.snake.obstacles = []
                    self.food.spawn(self.snake.body + self.snake.obstacles)
                elif text == "Рекорды":
                    self.state = "highscores"
                elif text == "Сменить пользователя":
                    self.state = "welcome"
                    self.user_input = ""
                    self.input_active = True
                elif text == "Выход":
                    return False

        if help_btn.collidepoint(mouse_pos) and mouse_clicked:
            self.show_help_screen = True

        return True

    def show_highscores(self):
        self.screen.blit(self.backgrounds['highscores'], (0, 0))

        seen_scores = set()
        unique_scores = [record for record in self.highscores
                         if not (record_key := (record['name'], record['score'])) in seen_scores
                         and not seen_scores.add(record_key)]
        sorted_scores = sorted(unique_scores, key=lambda x: x['score'], reverse=True)[:10]

        if not sorted_scores:
            self.draw_text("Нет рекордов!", self.font, UI_COLOR, SCREEN_WIDTH // 2, 200 + 30, True)
        else:
            for i, record in enumerate(sorted_scores):
                y_pos = 120 + i * 40 + 30
                self.draw_text(f"{i + 1}. {record['name']}: {record['score']} (ур. {record['level']})",
                               self.font, UI_COLOR, SCREEN_WIDTH // 2, y_pos, True)

        back_btn = self.draw_text("Назад", self.font, UI_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, True)

        if back_btn.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.state = "menu"

        return True

    def show_game_over(self):
        self.screen.blit(self.backgrounds['gameover'], (0, 0))
        self.draw_text(f"Счет: {self.snake.score}", self.font, UI_COLOR, SCREEN_WIDTH // 2, 290, True)
        self.draw_text(f"Уровень: {self.snake.level}", self.font, UI_COLOR, SCREEN_WIDTH // 2, 340, True)

        buttons = [("Заново", 400, SCREEN_WIDTH // 2 - 100),
                   ("В меню", 400, SCREEN_WIDTH // 2 + 100)]

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for text, y, x in buttons:
            btn = self.draw_text(text, self.font, UI_COLOR, x, y, True)
            if btn.collidepoint(mouse_pos) and mouse_clicked:
                if text == "Заново":
                    self.add_highscore()
                    self.state = "game"
                    self.snake.create()
                    self.snake.game_mode = self.game_mode
                    if self.game_mode == "classic":
                        self.snake.obstacles = []
                    self.food.spawn(self.snake.body + self.snake.obstacles)
                else:
                    self.add_highscore()
                    self.state = "menu"

        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == "game" and not self.show_help_screen:
                    key_actions = {
                        pygame.K_UP: UP,
                        pygame.K_DOWN: DOWN,
                        pygame.K_LEFT: LEFT,
                        pygame.K_RIGHT: RIGHT
                    }
                    if event.key in key_actions:
                        self.snake.change_direction(key_actions[event.key])
                    elif event.key == pygame.K_p:
                        self.state = "pause"
                    elif event.key == pygame.K_ESCAPE:
                        self.add_highscore()
                        self.state = "menu"

                elif self.state == "pause" and event.key == pygame.K_p:
                    self.state = "game"

                elif self.state == "welcome" and self.input_active:
                    if event.key == pygame.K_RETURN and self.user_input.strip():
                        self.current_user = self.user_input.strip()
                        if self.current_user not in self.users:
                            self.users[self.current_user] = {'best_score': 0}
                            self.save_data()
                        self.state = "menu"
                        self.user_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_input = self.user_input[:-1]
                    elif len(self.user_input) < 10:
                        self.user_input += event.unicode

                elif self.show_help_screen:
                    self.show_help_screen = False

        return True

    def run_game(self):
        self.setup()
        running = True

        while running:
            running = self.handle_events()

            if self.show_help_screen:
                self.show_help()
            elif self.state == "welcome":
                self.show_welcome_screen()
            elif self.state == "menu":
                if not self.show_menu():
                    running = False
            elif self.state == "game":
                head = self.snake.body[0]

                # Проверка съедения еды
                food_eaten = False
                if self.food.special_active and head == self.food.special_position:
                    self.snake.grow(True)
                    self.food.special_active = False
                    food_eaten = True
                elif not self.food.special_active and head == self.food.position:
                    self.snake.grow(False)
                    food_eaten = True

                if not self.snake.move():
                    self.state = "over"

                if food_eaten:
                    self.food.spawn(self.snake.body + self.snake.obstacles)

                # Отрисовка игры
                self.screen.blit(self.backgrounds['game'], (0, 0))
                if self.game_mode == "obstacles":
                    self.draw_obstacles()
                if self.food.special_active:
                    self.draw_special_food()
                self.draw_food()
                self.draw_snake()
                self.food.update()

                # Статистика
                stats = [
                    f"Счет: {self.snake.score}",
                    f"Уровень: {self.snake.level}",
                    f"Лучший: {self.users.get(self.current_user, {}).get('best_score', 0)}"
                ]
                for i, stat in enumerate(stats):
                    self.draw_text(stat, self.font, (24, 76, 47), 10, 10 + i * 30)

            elif self.state == "over":
                self.show_game_over()
            elif self.state == "highscores":
                self.show_highscores()
            elif self.state == "pause":
                self.draw_text("ПАУЗА", self.big_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, True)
                self.draw_text("Нажмите P для продолжения", self.font, WHITE,
                               SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, True)

            pygame.display.flip()
            self.clock.tick(self.snake.speed if self.state == "game" else FPS)

        pygame.quit()


game_instance = Game()
game_instance.run_game()