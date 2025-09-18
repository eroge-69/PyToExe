import pygame
import random
import math
import time
import sys
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Константы
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
GLASS_COLOR = (200, 220, 240, 100)

# Цвета жидкостей
LIQUID_COLORS = [
    (255, 0, 0),  # Красный
    (0, 255, 0),  # Зеленый
    (0, 0, 255),  # Синий
    (255, 255, 0),  # Желтый
    (255, 0, 255),  # Фиолетовый
    (0, 255, 255),  # Голубой
    (255, 165, 0),  # Оранжевый
    (255, 192, 203),  # Розовый
    (128, 0, 128),  # Пурпурный
    (0, 128, 0),  # Темно-зеленый
    (165, 42, 42),  # Коричневый
    (255, 20, 147),  # Ярко-розовый
    (50, 205, 50),  # Лайм
    (255, 140, 0),  # Темно-оранжевый
    (138, 43, 226),  # Синефиолетовый
    (220, 20, 60),  # Кармин
    (255, 215, 0),  # Золотой
    (0, 206, 209),  # Темно-бирюзовый
    (199, 21, 133),  # Средне-красно-фиолетовый
    (32, 178, 170),  # Светло-морской зеленый
]

# Параметры бутылки
BOTTLE_WIDTH = 80
BOTTLE_HEIGHT = 200
BOTTLE_CAPACITY = 4  # Максимум 4 слоя жидкости
LIQUID_LAYER_HEIGHT = BOTTLE_HEIGHT // BOTTLE_CAPACITY

# Параметры игры
BOTTLES_PER_ROW = 5
BOTTLE_ROWS = 3
TOTAL_BOTTLES = 15
BOTTLE_SPACING = 140
START_X = (WINDOW_WIDTH - (BOTTLES_PER_ROW * BOTTLE_SPACING)) // 2
START_Y = (WINDOW_HEIGHT - (BOTTLE_ROWS * 300)) // 2


class LiquidLayer:
    def __init__(self, color, amount=1):
        self.color = color
        self.amount = amount  # Количество жидкости в слое (1-4)


class Bottle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.layers = []  # Список слоев жидкости (снизу вверх)
        self.selected = False
        self.pouring_to = None
        self.pour_animation = 0
        self.shake_animation = 0

    def add_layer(self, color, amount=1):
        """Добавляет слой жидкости"""
        # Если верхний слой того же цвета, объединяем
        if self.layers and self.layers[-1].color == color:
            available_space = BOTTLE_CAPACITY - self.layers[-1].amount
            if available_space > 0:
                add_amount = min(amount, available_space)
                self.layers[-1].amount += add_amount
                amount -= add_amount

        # Если еще есть жидкость для добавления, создаем новый слой
        if amount > 0 and len(self.layers) < BOTTLE_CAPACITY:
            self.layers.append(LiquidLayer(color, amount))

    def can_pour_to(self, other_bottle):
        """Проверяет, можно ли перелить в другую бутылку"""
        if not self.layers or self == other_bottle:
            return False

        # Проверяем, есть ли место в целевой бутылке
        other_total = sum(layer.amount for layer in other_bottle.layers)
        if other_total >= BOTTLE_CAPACITY:
            return False

        # Теперь можно переливать любые цвета!
        return True

    def get_top_color(self):
        """Возвращает цвет верхнего слоя"""
        return self.layers[-1].color if self.layers else None

    def get_top_amount(self):
        """Возвращает количество жидкости в верхнем слое"""
        return self.layers[-1].amount if self.layers else 0

    def pour_to(self, other_bottle):
        """Переливает жидкость в другую бутылку"""
        if not self.can_pour_to(other_bottle):
            return False

        top_layer = self.layers[-1]
        top_color = top_layer.color

        # Считаем сколько можно перелить
        other_total = sum(layer.amount for layer in other_bottle.layers)
        available_space = BOTTLE_CAPACITY - other_total

        # Считаем сколько жидкости того же цвета подряд сверху
        pourabe_amount = 0
        for layer in reversed(self.layers):
            if layer.color == top_color:
                pourabe_amount += layer.amount
            else:
                break

        # Переливаем максимально возможное количество
        pour_amount = min(pourabe_amount, available_space)
        if pour_amount <= 0:
            return False

        # Убираем жидкость из исходной бутылки
        remaining_to_remove = pour_amount
        while remaining_to_remove > 0 and self.layers:
            top = self.layers[-1]
            if top.color != top_color:
                break

            if top.amount <= remaining_to_remove:
                remaining_to_remove -= top.amount
                self.layers.pop()
            else:
                top.amount -= remaining_to_remove
                remaining_to_remove = 0

        # Добавляем в целевую бутылку
        other_bottle.add_layer(top_color, pour_amount)

        return True

    def is_complete(self):
        """Проверяет, состоит ли бутылка из жидкости одного цвета"""
        if not self.layers:
            return True

        color = self.layers[0].color
        total_amount = sum(layer.amount for layer in self.layers)

        # Проверяем, что все слои одного цвета и бутылка полная
        for layer in self.layers:
            if layer.color != color:
                return False

        return total_amount == BOTTLE_CAPACITY

    def is_empty(self):
        """Проверяет, пуста ли бутылка"""
        return len(self.layers) == 0

    def get_total_amount(self):
        """Возвращает общее количество жидкости"""
        return sum(layer.amount for layer in self.layers)

    def update(self, dt):
        """Обновляет анимации"""
        if self.pour_animation > 0:
            self.pour_animation -= dt * 3
        if self.shake_animation > 0:
            self.shake_animation -= dt * 10

    def draw(self, screen, font):
        """Рисует бутылку"""
        # Смещение для анимации тряски
        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_animation > 0:
            shake_offset_x = math.sin(time.time() * 20) * self.shake_animation * 5
            shake_offset_y = math.cos(time.time() * 25) * self.shake_animation * 2

        bottle_x = self.x + shake_offset_x
        bottle_y = self.y + shake_offset_y

        # Рисуем контур бутылки
        border_color = WHITE if self.selected else GRAY
        border_width = 3 if self.selected else 2

        # Горлышко бутылки
        neck_width = 20
        neck_height = 30
        neck_x = bottle_x + (BOTTLE_WIDTH - neck_width) // 2
        neck_y = bottle_y - neck_height

        pygame.draw.rect(screen, border_color,
                         (neck_x, neck_y, neck_width, neck_height), border_width)

        # Основная часть бутылки
        pygame.draw.rect(screen, border_color,
                         (bottle_x, bottle_y, BOTTLE_WIDTH, BOTTLE_HEIGHT), border_width)

        # Рисуем жидкость
        current_y = bottle_y + BOTTLE_HEIGHT
        for layer in self.layers:
            layer_height = LIQUID_LAYER_HEIGHT * layer.amount
            current_y -= layer_height

            # Создаем градиент для жидкости
            liquid_rect = pygame.Rect(bottle_x + 5, current_y, BOTTLE_WIDTH - 10, layer_height)

            # Основной цвет жидкости
            pygame.draw.rect(screen, layer.color, liquid_rect)

            # Блик на жидкости
            highlight_color = tuple(min(255, c + 50) for c in layer.color)
            highlight_rect = pygame.Rect(bottle_x + 8, current_y + 2, 15, layer_height - 4)
            pygame.draw.rect(screen, highlight_color, highlight_rect)

        # Рисуем стеклянный эффект
        glass_surface = pygame.Surface((BOTTLE_WIDTH - 4, BOTTLE_HEIGHT - 4), pygame.SRCALPHA)
        glass_surface.fill(GLASS_COLOR)
        screen.blit(glass_surface, (bottle_x + 2, bottle_y + 2))

        # Анимация переливания
        if self.pour_animation > 0:
            # Рисуем струю жидкости
            if self.pouring_to and self.get_top_color():
                start_x = bottle_x + BOTTLE_WIDTH // 2
                start_y = bottle_y
                end_x = self.pouring_to.x + BOTTLE_WIDTH // 2
                end_y = self.pouring_to.y

                # Создаем изогнутую траекторию
                control_x = (start_x + end_x) // 2
                control_y = min(start_y, end_y) - 50

                # Рисуем струю как серию кругов
                for t in range(0, 100, 5):
                    t_norm = t / 100
                    # Квадратичная кривая Безье
                    x = (1 - t_norm) ** 2 * start_x + 2 * (1 - t_norm) * t_norm * control_x + t_norm ** 2 * end_x
                    y = (1 - t_norm) ** 2 * start_y + 2 * (1 - t_norm) * t_norm * control_y + t_norm ** 2 * end_y

                    pygame.draw.circle(screen, self.get_top_color(), (int(x), int(y)), 3)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Liquid Sort Puzzle - Сортировка жидкостей")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 64)

        self.bottles = []
        self.selected_bottle = None
        self.level = 1
        self.moves = 0
        self.best_moves = float('inf')
        self.game_completed = False
        self.victory_timer = 0

        # Система коллекции персонажей
        self.character_collection = set()  # Открытые персонажи
        self.current_level_character = None  # Персонаж текущего уровня
        self.show_gallery = False  # Показ галереи
        self.new_character_unlocked = False  # Флаг нового персонажа

        # Система прокрутки галереи
        self.gallery_scroll_y = 0  # Позиция прокрутки
        self.gallery_max_scroll = 0  # Максимальная прокрутка
        self.gallery_scroll_speed = 30  # Скорость прокрутки
        self.scrollbar_dragging = False  # Флаг перетаскивания бегунка
        self.scrollbar_drag_offset = 0  # Смещение при перетаскивании

        # Конфигурация персонажей (имя, редкость, основной цвет)
        self.characters = {
            'venti': {'name': 'Venti', 'rarity': 0.20, 'color': (100, 255, 200)},  # Анемо
            'raiden': {'name': 'Raiden Shogun', 'rarity': 0.05, 'color': (150, 100, 255)},  # Электро
            'barbara': {'name': 'Barbara', 'rarity': 0.25, 'color': (100, 150, 255)},  # Гидро
            'diluc': {'name': 'Diluc', 'rarity': 0.08, 'color': (255, 100, 100)},  # Пиро
            'arlecchino': {'name': 'Arlecchino', 'rarity': 0.03, 'color': (200, 50, 50)},  # Пиро
            'mavuika': {'name': 'Mavuika', 'rarity': 0.02, 'color': (255, 150, 50)},  # Пиро
            'fischl': {'name': 'Fischl', 'rarity': 0.15, 'color': (200, 150, 255)},  # Электро
            'lisa': {'name': 'Lisa', 'rarity': 0.18, 'color': (180, 120, 255)},  # Электро
            'kaeya': {'name': 'Kaeya', 'rarity': 0.22, 'color': (150, 200, 255)},  # Крио
            'lumine': {'name': 'Lumine', 'rarity': 0.01, 'color': (255, 255, 150)},  # Легендарная
            'aether': {'name': 'Aether', 'rarity': 0.01, 'color': (255, 200, 100)},  # Легендарная
        }

        # Инициализация звуков
        self.init_sounds()

        # Загрузка изображения Yae Miko
        self.yae_miko_image = self.create_yae_miko_image()

        self.create_level()

    def create_level(self):
        """Создает новый уровень"""
        self.bottles = []
        self.selected_bottle = None
        self.moves = 0
        self.game_completed = False
        self.victory_timer = 0

        # Генерируем случайного персонажа для уровня
        self.current_level_character = self.generate_random_character()

        # Количество цветов зависит от уровня
        num_colors = min(4 + (self.level - 1) // 2, len(LIQUID_COLORS))
        colors = LIQUID_COLORS[:num_colors]

        # Используем все 15 бутылок
        num_bottles = TOTAL_BOTTLES

        # Создаем бутылки в 3 ряда по 5
        for i in range(num_bottles):
            row = i // BOTTLES_PER_ROW
            col = i % BOTTLES_PER_ROW

            x = START_X + col * BOTTLE_SPACING
            y = START_Y + row * 300

            self.bottles.append(Bottle(x, y))

        # Заполняем 12 из 15 бутылок жидкостью, оставляя 3 пустые для стратегии
        bottles_to_fill = TOTAL_BOTTLES - 3  # Оставляем 3 пустые бутылки

        # Создаем список всех порций жидкости
        liquid_portions = []
        for color in colors:
            liquid_portions.extend([color] * BOTTLE_CAPACITY)

        # Добавляем дополнительные цвета если нужно заполнить все бутылки
        while len(liquid_portions) < bottles_to_fill * BOTTLE_CAPACITY:
            # Используем дополнительные цвета из палитры
            extra_color_index = len(liquid_portions) // BOTTLE_CAPACITY
            if extra_color_index < len(LIQUID_COLORS):
                extra_color = LIQUID_COLORS[extra_color_index]
                liquid_portions.extend([extra_color] * BOTTLE_CAPACITY)
            else:
                # Если цветов не хватает, повторяем существующие
                liquid_portions.extend([random.choice(colors)] * BOTTLE_CAPACITY)

        # Обрезаем до нужного количества
        liquid_portions = liquid_portions[:bottles_to_fill * BOTTLE_CAPACITY]

        # Перемешиваем
        random.shuffle(liquid_portions)

        # Распределяем по первым бутылкам
        bottle_index = 0
        for portion in liquid_portions:
            if bottle_index >= bottles_to_fill:
                break
            if self.bottles[bottle_index].get_total_amount() >= BOTTLE_CAPACITY:
                bottle_index += 1
                if bottle_index >= bottles_to_fill:
                    break

            self.bottles[bottle_index].add_layer(portion, 1)

    def handle_click(self, pos):
        """Обрабатывает клик мыши"""
        # Находим бутылку под курсором
        clicked_bottle = None
        for bottle in self.bottles:
            bottle_rect = pygame.Rect(bottle.x, bottle.y - 30, BOTTLE_WIDTH, BOTTLE_HEIGHT + 30)
            if bottle_rect.collidepoint(pos):
                clicked_bottle = bottle
                break

        if not clicked_bottle:
            # Клик вне бутылок - снимаем выделение
            if self.selected_bottle:
                self.selected_bottle.selected = False
                self.selected_bottle = None
            return

        if self.selected_bottle is None:
            # Выбираем бутылку для переливания
            if not clicked_bottle.is_empty():
                clicked_bottle.selected = True
                self.selected_bottle = clicked_bottle
                self.play_sound('select')  # Звук выбора
                # Добавляем случайный пузырь
                import random
                bubble_sound = random.choice(['bubble1', 'bubble2', 'bubble3'])
                self.play_sound(bubble_sound)
        else:
            # Пытаемся перелить
            if clicked_bottle == self.selected_bottle:
                # Клик по той же бутылке - снимаем выделение
                self.selected_bottle.selected = False
                self.selected_bottle = None
                self.play_sound('deselect')  # Звук отмены
            else:
                # Переливаем жидкость
                if self.selected_bottle.can_pour_to(clicked_bottle):
                    # Запускаем анимацию
                    self.selected_bottle.pour_animation = 1.0
                    self.selected_bottle.pouring_to = clicked_bottle

                    # Выполняем переливание
                    success = self.selected_bottle.pour_to(clicked_bottle)
                    if success:
                        self.moves += 1
                        self.play_sound('pour')

                        # Проверяем победу
                        if self.check_victory():
                            self.game_completed = True
                            self.victory_timer = 3.0  # 3 секунды показа сообщения

                            # Добавляем персонажа в коллекцию
                            if self.current_level_character and self.current_level_character not in self.character_collection:
                                self.character_collection.add(self.current_level_character)
                                self.new_character_unlocked = True
                                print(
                                    f"🎉 Новый персонаж разблокирован: {self.characters[self.current_level_character]['name']}")

                            self.play_sound('complete')  # Мелодия победы
                            if self.moves < self.best_moves and self.moves < 999:  # Не считаем читы как рекорд
                                self.best_moves = self.moves
                else:
                    # Нельзя перелить - трясем бутылку
                    clicked_bottle.shake_animation = 1.0
                    self.play_sound('error')

                # Снимаем выделение
                self.selected_bottle.selected = False
                self.selected_bottle = None

    def check_victory(self):
        """Проверяет условие победы"""
        for bottle in self.bottles:
            if not bottle.is_empty() and not bottle.is_complete():
                return False
        return True

    def reset_level(self):
        """Перезапускает текущий уровень"""
        self.create_level()

    def next_level(self):
        """Переходит к следующему уровню"""
        self.level += 1
        self.new_character_unlocked = False  # Сбрасываем флаг
        self.create_level()

    def reset_level(self):
        """Перезапускает текущий уровень"""
        self.create_level()

    def draw_ui(self):
        """Рисует интерфейс пользователя"""
        # Градиентный фон
        for y in range(WINDOW_HEIGHT):
            color_factor = y / WINDOW_HEIGHT
            r = int(20 + 30 * color_factor)
            g = int(10 + 20 * color_factor)
            b = int(40 + 60 * color_factor)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        # Заголовок с тенью
        title_text = f"Liquid Sort Puzzle - Уровень {self.level}"

        # Тень
        shadow_surface = self.title_font.render(title_text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(WINDOW_WIDTH // 2 + 2, 52))
        self.screen.blit(shadow_surface, shadow_rect)

        # Основной текст
        title_surface = self.title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)

        # Левая панель с информацией
        info_panel_width = 280
        info_panel_height = 200
        info_x = 20
        info_y = 120

        # Полупрозрачная панель
        info_surface = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 150))
        pygame.draw.rect(info_surface, (100, 100, 100, 100), (0, 0, info_panel_width, info_panel_height), 2)
        self.screen.blit(info_surface, (info_x, info_y))

        # Информация о ходах
        moves_text = self.font.render(f"💫 Ходы: {self.moves}", True, WHITE)
        self.screen.blit(moves_text, (info_x + 20, info_y + 20))

        if self.best_moves != float('inf'):
            best_text = self.small_font.render(f"🏆 Лучший: {self.best_moves}", True, (255, 215, 0))
            self.screen.blit(best_text, (info_x + 20, info_y + 60))

        # Статистика бутылок
        filled_bottles = sum(1 for bottle in self.bottles if not bottle.is_empty())
        completed_bottles = sum(1 for bottle in self.bottles if bottle.is_complete())

        bottles_text = self.small_font.render(f"🍾 Заполнено: {filled_bottles}/{TOTAL_BOTTLES}", True, LIGHT_GRAY)
        self.screen.blit(bottles_text, (info_x + 20, info_y + 100))

        complete_text = self.small_font.render(f"✅ Готово: {completed_bottles}", True, GREEN)
        self.screen.blit(complete_text, (info_x + 20, info_y + 130))

        # Правая панель с управлением
        controls_panel_width = 400
        controls_panel_height = 300
        controls_x = WINDOW_WIDTH - controls_panel_width - 20
        controls_y = 120

        # Полупрозрачная панель
        controls_surface = pygame.Surface((controls_panel_width, controls_panel_height), pygame.SRCALPHA)
        controls_surface.fill((0, 0, 0, 150))
        pygame.draw.rect(controls_surface, (100, 100, 100, 100), (0, 0, controls_panel_width, controls_panel_height), 2)
        self.screen.blit(controls_surface, (controls_x, controls_y))

        # Инструкции
        instructions_title = self.font.render("🎮 Управление:", True, WHITE)
        self.screen.blit(instructions_title, (controls_x + 20, controls_y + 20))

        instructions = [
            "🕹️ Клик - выбрать бутылку",
            "🔄 Клик на другую - перелить",
            "🎯 Цель: сортировать по цветам",
            "♾️ R - перезапустить уровень",
            "➡️ N - следующий уровень",
            "🎭 G - галерея персонажей",
            ""
            "❌ ESC/F11 - выход",
            "",
            "🎆 Новое: Можно мешать цвета!"
        ]

        for i, instruction in enumerate(instructions):
            color = (255, 255, 100) if "Новое" in instruction else LIGHT_GRAY
            text = self.small_font.render(instruction, True, color)
            self.screen.blit(text, (controls_x + 20, controls_y + 60 + i * 30))

    def init_sounds(self):
        """Инициализирует звуковые эффекты"""
        self.sounds = {}

        # Простая система звуков без numpy
        try:
            # Используем встроенные возможности pygame.mixer
            # Создаем разнообразные звуки

            # Звук переливания (бульканье)
            self.sounds['pour'] = self.create_tone_sound(300, 0.3)

            # Звук ошибки (низкий тон)
            self.sounds['error'] = self.create_tone_sound(150, 0.2)

            # Звук победы (высокий тон)
            self.sounds['victory'] = self.create_tone_sound(523, 0.8)

            # Новые разнообразные звуки
            self.sounds['select'] = self.create_tone_sound(400, 0.1)  # Клик по бутылке
            self.sounds['deselect'] = self.create_tone_sound(200, 0.1)  # Отмена выбора
            self.sounds['complete'] = self.create_melody_sound([523, 659, 784], 0.6)  # Мелодия завершения
            self.sounds['bubble1'] = self.create_bubble_sound(250, 0.2)  # Пузырь 1
            self.sounds['bubble2'] = self.create_bubble_sound(350, 0.15)  # Пузырь 2
            self.sounds['bubble3'] = self.create_bubble_sound(450, 0.18)  # Пузырь 3

            print("✓ Звуковые эффекты инициализированы успешно")

        except Exception as e:
            print(f"⚠️  Не удалось создать звуки: {e}")
            print("🔇 Игра запустится без звуков")
            # Если не удается создать звуки, используем пустые
            self.sounds = {key: None for key in
                           ['pour', 'error', 'victory', 'select', 'deselect', 'complete', 'bubble1', 'bubble2',
                            'bubble3']}

    def create_yae_miko_image(self):
        """Создаёт стилизованное изображение Yae Miko"""
        try:
            # Размер изображения
            width, height = 200, 280
            surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Цвета для Yae Miko
            skin_color = (255, 220, 185)
            hair_color = (255, 140, 200)  # Розовые волосы
            outfit_color = (120, 60, 150)  # Фиолетовая одежда
            accent_color = (255, 200, 100)  # Золотистые акценты
            eye_color = (150, 100, 255)  # Фиолетовые глаза

            # Тело / основа
            body_rect = pygame.Rect(width // 2 - 30, height - 100, 60, 100)
            pygame.draw.ellipse(surface, outfit_color, body_rect)

            # Голова
            head_center = (width // 2, height // 3)
            head_radius = 35
            pygame.draw.circle(surface, skin_color, head_center, head_radius)

            # Волосы (длинные розовые)
            # Левая часть волос
            left_hair_points = [
                (head_center[0] - 45, head_center[1] - 30),
                (head_center[0] - 60, head_center[1]),
                (head_center[0] - 50, head_center[1] + 60),
                (head_center[0] - 20, head_center[1] + 40),
                (head_center[0] - 25, head_center[1] - 25)
            ]
            pygame.draw.polygon(surface, hair_color, left_hair_points)

            # Правая часть волос
            right_hair_points = [
                (head_center[0] + 45, head_center[1] - 30),
                (head_center[0] + 60, head_center[1]),
                (head_center[0] + 50, head_center[1] + 60),
                (head_center[0] + 20, head_center[1] + 40),
                (head_center[0] + 25, head_center[1] - 25)
            ]
            pygame.draw.polygon(surface, hair_color, right_hair_points)

            # Верхняя часть волос
            top_hair_rect = pygame.Rect(head_center[0] - 40, head_center[1] - 45, 80, 50)
            pygame.draw.ellipse(surface, hair_color, top_hair_rect)

            # Ушки лисицы (характерная черта Yae)
            # Левое ушко
            left_ear_points = [
                (head_center[0] - 30, head_center[1] - 40),
                (head_center[0] - 40, head_center[1] - 60),
                (head_center[0] - 15, head_center[1] - 55)
            ]
            pygame.draw.polygon(surface, hair_color, left_ear_points)
            pygame.draw.polygon(surface, (255, 200, 200), [(p[0] + 3, p[1] + 5) for p in left_ear_points])

            # Правое ушко
            right_ear_points = [
                (head_center[0] + 30, head_center[1] - 40),
                (head_center[0] + 40, head_center[1] - 60),
                (head_center[0] + 15, head_center[1] - 55)
            ]
            pygame.draw.polygon(surface, hair_color, right_ear_points)
            pygame.draw.polygon(surface, (255, 200, 200), [(p[0] - 3, p[1] + 5) for p in right_ear_points])

            # Глаза
            left_eye = (head_center[0] - 12, head_center[1] - 5)
            right_eye = (head_center[0] + 12, head_center[1] - 5)
            pygame.draw.circle(surface, WHITE, left_eye, 8)
            pygame.draw.circle(surface, WHITE, right_eye, 8)
            pygame.draw.circle(surface, eye_color, left_eye, 5)
            pygame.draw.circle(surface, eye_color, right_eye, 5)
            pygame.draw.circle(surface, BLACK, left_eye, 2)
            pygame.draw.circle(surface, BLACK, right_eye, 2)

            # Нос
            nose_pos = (head_center[0], head_center[1] + 5)
            pygame.draw.circle(surface, (240, 200, 170), nose_pos, 2)

            # Рот
            mouth_rect = pygame.Rect(head_center[0] - 8, head_center[1] + 12, 16, 6)
            pygame.draw.ellipse(surface, (220, 150, 150), mouth_rect)

            # Одежда - японский стиль
            # Кимоно
            kimono_rect = pygame.Rect(width // 2 - 40, height // 2 + 10, 80, 120)
            pygame.draw.rect(surface, outfit_color, kimono_rect)

            # Золотистые детали на одежде
            pygame.draw.rect(surface, accent_color, (width // 2 - 35, height // 2 + 15, 70, 8))
            pygame.draw.rect(surface, accent_color, (width // 2 - 30, height // 2 + 40, 60, 6))

            # Рукава
            left_sleeve = pygame.Rect(width // 2 - 60, height // 2 + 20, 25, 50)
            right_sleeve = pygame.Rect(width // 2 + 35, height // 2 + 20, 25, 50)
            pygame.draw.ellipse(surface, outfit_color, left_sleeve)
            pygame.draw.ellipse(surface, outfit_color, right_sleeve)

            # Кисти рук
            pygame.draw.circle(surface, skin_color, (width // 2 - 50, height // 2 + 45), 8)
            pygame.draw.circle(surface, skin_color, (width // 2 + 50, height // 2 + 45), 8)

            # Магические эффекты (молнии)
            # Маленькие молнии вокруг персонажа
            lightning_color = (255, 255, 100)
            for i in range(5):
                angle = i * 72  # 360/5 = 72 градусов
                x = head_center[0] + 60 * math.cos(math.radians(angle))
                y = head_center[1] + 60 * math.sin(math.radians(angle))
                end_x = x + 15 * math.cos(math.radians(angle + 30))
                end_y = y + 15 * math.sin(math.radians(angle + 30))
                pygame.draw.line(surface, lightning_color, (x, y), (end_x, end_y), 3)

            # Подпись
            font = pygame.font.Font(None, 20)
            text = font.render("Yae Miko", True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height - 15))

            # Тень для текста
            shadow_text = font.render("Yae Miko", True, (0, 0, 0))
            surface.blit(shadow_text, (text_rect.x + 1, text_rect.y + 1))
            surface.blit(text, text_rect)

            return surface

        except Exception as e:
            print(f"⚠️  Ошибка создания изображения Yae Miko: {e}")
            # Возвращаем простой плейсхолдер
            placeholder = pygame.Surface((200, 280), pygame.SRCALPHA)
            placeholder.fill((100, 50, 150))
            font = pygame.font.Font(None, 24)
            text = font.render("Yae Miko", True, WHITE)
            text_rect = text.get_rect(center=(100, 140))
            placeholder.blit(text, text_rect)
            return placeholder

    def generate_random_character(self):
        """Генерирует случайного персонажа на основе шансов"""
        import random
        rand = random.random()
        cumulative_chance = 0

        # Сортируем по редкости (от редких к обычным)
        sorted_chars = sorted(self.characters.items(), key=lambda x: x[1]['rarity'])

        for char_id, char_data in sorted_chars:
            cumulative_chance += char_data['rarity']
            if rand <= cumulative_chance:
                return char_id

        # Если ничего не выпало, возвращаем обычного персонажа
        return 'barbara'

    def create_character_image(self, character_id):
        """Создаёт детализированное изображение персонажа в стиле Genshin Impact"""
        if character_id not in self.characters:
            return self.create_yae_miko_image()  # Fallback

        char_data = self.characters[character_id]
        width, height = 180, 250
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Основные цвета
        main_color = char_data['color']
        skin_color = (255, 220, 185)

        if character_id == 'venti':
            self.draw_venti(surface, width, height, main_color, skin_color)
        elif character_id == 'raiden':
            self.draw_raiden(surface, width, height, main_color, skin_color)
        elif character_id == 'barbara':
            self.draw_barbara(surface, width, height, main_color, skin_color)
        elif character_id == 'diluc':
            self.draw_diluc(surface, width, height, main_color, skin_color)
        elif character_id == 'arlecchino':
            self.draw_arlecchino(surface, width, height, main_color, skin_color)
        elif character_id == 'mavuika':
            self.draw_mavuika(surface, width, height, main_color, skin_color)
        elif character_id == 'fischl':
            self.draw_fischl(surface, width, height, main_color, skin_color)
        elif character_id == 'lisa':
            self.draw_lisa(surface, width, height, main_color, skin_color)
        elif character_id == 'kaeya':
            self.draw_kaeya(surface, width, height, main_color, skin_color)
        elif character_id == 'lumine':
            self.draw_lumine(surface, width, height, main_color, skin_color)
        elif character_id == 'aether':
            self.draw_aether(surface, width, height, main_color, skin_color)
        else:
            self.draw_generic_character(surface, width, height, main_color, skin_color)

        return surface

    def draw_venti(self, surface, width, height, main_color, skin_color):
        """Рисует Venti - анемо бард с косичками"""
        head_center = (width // 2, height // 3)

        # Голова
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Волосы - тёмно-бирюзовые с косичками
        hair_color = (75, 150, 130)
        # Основная масса волос
        hair_rect = pygame.Rect(head_center[0] - 35, head_center[1] - 40, 70, 65)
        pygame.draw.ellipse(surface, hair_color, hair_rect)

        # Косички по бокам
        left_braid = [(head_center[0] - 45, head_center[1] - 10), (head_center[0] - 50, head_center[1] + 20),
                      (head_center[0] - 40, head_center[1] + 50), (head_center[0] - 35, head_center[1] + 80)]
        right_braid = [(head_center[0] + 45, head_center[1] - 10), (head_center[0] + 50, head_center[1] + 20),
                       (head_center[0] + 40, head_center[1] + 50), (head_center[0] + 35, head_center[1] + 80)]

        for i in range(len(left_braid) - 1):
            pygame.draw.line(surface, hair_color, left_braid[i], left_braid[i + 1], 8)
            pygame.draw.line(surface, hair_color, right_braid[i], right_braid[i + 1], 8)

        # Глаза - бирюзовые
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, (100, 255, 200), left_eye, 4)
        pygame.draw.circle(surface, (100, 255, 200), right_eye, 4)
        pygame.draw.circle(surface, BLACK, left_eye, 2)
        pygame.draw.circle(surface, BLACK, right_eye, 2)

        # Одежда - бардовский костюм
        # Корсет
        corset_rect = pygame.Rect(width // 2 - 25, height // 2 - 10, 50, 60)
        pygame.draw.rect(surface, (60, 120, 80), corset_rect)
        # Корсетная шнуровка
        for i in range(5):
            y_pos = height // 2 - 5 + i * 10
            pygame.draw.line(surface, WHITE, (width // 2 - 15, y_pos), (width // 2 + 15, y_pos), 2)

        # Плащ
        cape_points = [(width // 2 - 35, height // 2), (width // 2 - 40, height // 2 + 80),
                       (width // 2 + 40, height // 2 + 80), (width // 2 + 35, height // 2)]
        pygame.draw.polygon(surface, (40, 100, 60), cape_points)

        # Шляпа барда
        hat_points = [(head_center[0] - 25, head_center[1] - 35), (head_center[0], head_center[1] - 50),
                      (head_center[0] + 25, head_center[1] - 35)]
        pygame.draw.polygon(surface, (40, 80, 60), hat_points)

        # Перо на шляпе
        feather_points = [(head_center[0] + 15, head_center[1] - 45), (head_center[0] + 25, head_center[1] - 55),
                          (head_center[0] + 20, head_center[1] - 40)]
        pygame.draw.polygon(surface, (255, 255, 255), feather_points)

        # Ветровые эффекты
        for i in range(4):
            angle = i * 90
            x = head_center[0] + 45 * math.cos(math.radians(angle))
            y = head_center[1] + 45 * math.sin(math.radians(angle))
            pygame.draw.circle(surface, (150, 255, 200), (int(x), int(y)), 6)

        # Подпись
        font = pygame.font.Font(None, 28)
        text = font.render("Venti", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Venti", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_raiden(self, surface, width, height, main_color, skin_color):
        """Рисует Raiden Shogun - электро архонт с кимоно"""
        head_center = (width // 2, height // 3)

        # Голова
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Волосы - длинная фиолетовая коса
        hair_color = (100, 50, 150)
        # Основная масса волос
        hair_rect = pygame.Rect(head_center[0] - 35, head_center[1] - 40, 70, 50)
        pygame.draw.ellipse(surface, hair_color, hair_rect)

        # Длинная коса сзади
        braid_points = [(head_center[0], head_center[1] + 10), (head_center[0] - 5, head_center[1] + 40),
                        (head_center[0], head_center[1] + 70), (head_center[0] + 5, head_center[1] + 100)]
        for i in range(len(braid_points) - 1):
            pygame.draw.line(surface, hair_color, braid_points[i], braid_points[i + 1], 12)

        # Глаза - фиолетовые с особым бликом
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 7)
        pygame.draw.circle(surface, WHITE, right_eye, 7)
        pygame.draw.circle(surface, (150, 100, 255), left_eye, 5)
        pygame.draw.circle(surface, (150, 100, 255), right_eye, 5)
        pygame.draw.circle(surface, BLACK, left_eye, 2)
        pygame.draw.circle(surface, BLACK, right_eye, 2)

        # Кимоно с электро узорами
        kimono_rect = pygame.Rect(width // 2 - 30, height // 2 - 5, 60, 90)
        pygame.draw.rect(surface, (80, 40, 120), kimono_rect)

        # Оби (пояс)
        obi_rect = pygame.Rect(width // 2 - 35, height // 2 + 20, 70, 15)
        pygame.draw.rect(surface, (150, 100, 200), obi_rect)

        # Электро узоры
        for i in range(3):
            y_pos = height // 2 + i * 15
            pygame.draw.line(surface, (200, 150, 255), (width // 2 - 25, y_pos), (width // 2 + 25, y_pos), 2)

        # Электрические эффекты
        for i in range(6):
            angle = i * 60
            x = head_center[0] + 50 * math.cos(math.radians(angle))
            y = head_center[1] + 50 * math.sin(math.radians(angle))
            end_x = x + 15 * math.cos(math.radians(angle + 45))
            end_y = y + 15 * math.sin(math.radians(angle + 45))
            pygame.draw.line(surface, (200, 150, 255), (int(x), int(y)), (int(end_x), int(end_y)), 3)

        # Подпись
        font = pygame.font.Font(None, 28)
        text = font.render("Raiden Shogun", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Raiden Shogun", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_barbara(self, surface, width, height, main_color, skin_color):
        """Рисует Barbara - гидро целительница"""
        head_center = (width // 2, height // 3)
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Волосы - светло-блондинистые с кудрями
        hair_color = (255, 220, 150)
        hair_rect = pygame.Rect(head_center[0] - 35, head_center[1] - 40, 70, 65)
        pygame.draw.ellipse(surface, hair_color, hair_rect)

        # Кудри по бокам
        for i in range(3):
            left_curl = (head_center[0] - 40 + i * 5, head_center[1] - 15 + i * 10)
            right_curl = (head_center[0] + 40 - i * 5, head_center[1] - 15 + i * 10)
            pygame.draw.circle(surface, hair_color, left_curl, 8)
            pygame.draw.circle(surface, hair_color, right_curl, 8)

        # Глаза - голубые
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, (100, 150, 255), left_eye, 4)
        pygame.draw.circle(surface, (100, 150, 255), right_eye, 4)
        pygame.draw.circle(surface, BLACK, left_eye, 2)
        pygame.draw.circle(surface, BLACK, right_eye, 2)

        # Платье священника
        dress_rect = pygame.Rect(width // 2 - 30, height // 2 - 5, 60, 85)
        pygame.draw.rect(surface, (255, 255, 255), dress_rect)

        # Голубые акценты
        accent_rect = pygame.Rect(width // 2 - 25, height // 2 + 10, 50, 10)
        pygame.draw.rect(surface, (100, 150, 255), accent_rect)

        # Крест на груди
        cross_v = pygame.Rect(width // 2 - 2, height // 2 + 5, 4, 20)
        cross_h = pygame.Rect(width // 2 - 8, height // 2 + 11, 16, 4)
        pygame.draw.rect(surface, (200, 200, 100), cross_v)
        pygame.draw.rect(surface, (200, 200, 100), cross_h)

        # Водные эффекты
        for i in range(5):
            angle = i * 72
            x = head_center[0] + 45 * math.cos(math.radians(angle))
            y = head_center[1] + 45 * math.sin(math.radians(angle))
            pygame.draw.circle(surface, (150, 200, 255), (int(x), int(y)), 5)

        font = pygame.font.Font(None, 28)
        text = font.render("Barbara", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Barbara", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_diluc(self, surface, width, height, main_color, skin_color):
        """Рисует Diluc - пиро мститель"""
        head_center = (width // 2, height // 3)
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Волосы - красные волнистые
        hair_color = (200, 50, 50)
        hair_rect = pygame.Rect(head_center[0] - 40, head_center[1] - 40, 80, 70)
        pygame.draw.ellipse(surface, hair_color, hair_rect)

        # Длинные пряди сзади
        back_hair = pygame.Rect(head_center[0] - 15, head_center[1] + 15, 30, 80)
        pygame.draw.ellipse(surface, hair_color, back_hair)

        # Глаза - огненные
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, (255, 100, 100), left_eye, 4)
        pygame.draw.circle(surface, (255, 100, 100), right_eye, 4)
        pygame.draw.circle(surface, BLACK, left_eye, 2)
        pygame.draw.circle(surface, BLACK, right_eye, 2)

        # Тёмный костюм
        coat_rect = pygame.Rect(width // 2 - 30, height // 2 - 10, 60, 95)
        pygame.draw.rect(surface, (50, 30, 30), coat_rect)

        # Красные акценты
        for i in range(3):
            y_pos = height // 2 + i * 20
            pygame.draw.line(surface, (200, 50, 50), (width // 2 - 20, y_pos), (width // 2 + 20, y_pos), 3)

        # Огненные эффекты
        for i in range(6):
            angle = i * 60
            x = head_center[0] + 50 * math.cos(math.radians(angle))
            y = head_center[1] + 50 * math.sin(math.radians(angle))
            # Пламя
            flame_points = [(int(x), int(y)), (int(x - 5), int(y + 10)), (int(x + 5), int(y + 10))]
            pygame.draw.polygon(surface, (255, 150, 50), flame_points)

        font = pygame.font.Font(None, 28)
        text = font.render("Diluc", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Diluc", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_arlecchino(self, surface, width, height, main_color, skin_color):
        """Рисует Arlecchino - двойственный персонаж"""
        head_center = (width // 2, height // 3)
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Белые волосы с чёрными прядями (характерная черта Арлекино)
        hair_rect = pygame.Rect(head_center[0] - 35, head_center[1] - 40, 70, 60)
        pygame.draw.ellipse(surface, (255, 255, 255), hair_rect)

        # Чёрные пряди по бокам
        left_black = pygame.Rect(head_center[0] - 35, head_center[1] - 35, 15, 50)
        right_black = pygame.Rect(head_center[0] + 20, head_center[1] - 35, 15, 50)
        pygame.draw.ellipse(surface, BLACK, left_black)
        pygame.draw.ellipse(surface, BLACK, right_black)

        # Центральная чёрная прядь
        center_black = pygame.Rect(head_center[0] - 8, head_center[1] - 35, 16, 45)
        pygame.draw.ellipse(surface, BLACK, center_black)

        # Глаза - красные с крестообразными зрачками
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, (200, 50, 50), left_eye, 4)
        pygame.draw.circle(surface, (200, 50, 50), right_eye, 4)
        # Крестообразные зрачки
        pygame.draw.line(surface, BLACK, (left_eye[0] - 2, left_eye[1]), (left_eye[0] + 2, left_eye[1]), 2)
        pygame.draw.line(surface, BLACK, (left_eye[0], left_eye[1] - 2), (left_eye[0], left_eye[1] + 2), 2)
        pygame.draw.line(surface, BLACK, (right_eye[0] - 2, right_eye[1]), (right_eye[0] + 2, right_eye[1]), 2)
        pygame.draw.line(surface, BLACK, (right_eye[0], right_eye[1] - 2), (right_eye[0], right_eye[1] + 2), 2)

        # Элегантный чёрно-белый костюм
        coat_rect = pygame.Rect(width // 2 - 30, height // 2 - 5, 60, 90)
        pygame.draw.rect(surface, (30, 30, 30), coat_rect)

        # Белые акценты на одежде
        white_trim = pygame.Rect(width // 2 - 25, height // 2, 50, 8)
        pygame.draw.rect(surface, WHITE, white_trim)

        # Красные детали (как кровь)
        for i in range(3):
            y_pos = height // 2 + 15 + i * 20
            pygame.draw.circle(surface, (150, 30, 30), (width // 2 - 15 + i * 15, y_pos), 3)

        # Тёмные эффекты вокруг персонажа
        for i in range(4):
            angle = i * 90
            x = head_center[0] + 45 * math.cos(math.radians(angle))
            y = head_center[1] + 45 * math.sin(math.radians(angle))
            pygame.draw.circle(surface, (100, 30, 30), (int(x), int(y)), 5)

        # ... existing code ...
        font = pygame.font.Font(None, 28)
        text = font.render("Arlecchino", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Arlecchino", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_mavuika(self, surface, width, height, main_color, skin_color):
        """Рисует Mavuika - пиро архонт с огненными волосами"""
        head_center = (width // 2, height // 3)
        pygame.draw.circle(surface, skin_color, head_center, 30)

        # Огненно-оранжевые волосы с градиентом
        hair_rect = pygame.Rect(head_center[0] - 40, head_center[1] - 40, 80, 65)
        pygame.draw.ellipse(surface, (255, 150, 50), hair_rect)

        # Огненные пряди по бокам
        left_flame_hair = [(head_center[0] - 45, head_center[1] - 20),
                           (head_center[0] - 50, head_center[1] + 10),
                           (head_center[0] - 35, head_center[1] + 40)]
        right_flame_hair = [(head_center[0] + 45, head_center[1] - 20),
                            (head_center[0] + 50, head_center[1] + 10),
                            (head_center[0] + 35, head_center[1] + 40)]
        pygame.draw.polygon(surface, (255, 100, 30), left_flame_hair)
        pygame.draw.polygon(surface, (255, 100, 30), right_flame_hair)

        # Глаза - ярко-оранжевые
        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, (255, 150, 50), left_eye, 4)
        pygame.draw.circle(surface, (255, 150, 50), right_eye, 4)
        pygame.draw.circle(surface, BLACK, left_eye, 2)
        pygame.draw.circle(surface, BLACK, right_eye, 2)

        # Огненный боевой костюм
        armor_rect = pygame.Rect(width // 2 - 30, height // 2 - 10, 60, 95)
        pygame.draw.rect(surface, (150, 80, 40), armor_rect)

        # Огненные узоры на доспехах
        for i in range(4):
            y_pos = height // 2 + i * 15
            pygame.draw.line(surface, (255, 200, 100), (width // 2 - 20, y_pos), (width // 2 + 20, y_pos), 3)

        # Пламенные налокотники
        left_gauntlet = pygame.Rect(width // 2 - 55, height // 2 + 15, 20, 35)
        right_gauntlet = pygame.Rect(width // 2 + 35, height // 2 + 15, 20, 35)
        pygame.draw.rect(surface, (200, 100, 50), left_gauntlet)
        pygame.draw.rect(surface, (200, 100, 50), right_gauntlet)

        # Огненные эффекты в виде пламени
        for i in range(8):
            angle = i * 45
            x = head_center[0] + 50 * math.cos(math.radians(angle))
            y = head_center[1] + 50 * math.sin(math.radians(angle))
            # Пламя разных размеров
            flame_size = 3 + (i % 3) * 2
            flame_points = [(int(x), int(y)), (int(x - flame_size), int(y + flame_size * 2)),
                            (int(x + flame_size), int(y + flame_size * 2))]
            color = (255, 100 + i * 10, 0) if i % 2 == 0 else (255, 150, 50)
            pygame.draw.polygon(surface, color, flame_points)

        # ... existing code ...
        font = pygame.font.Font(None, 28)
        text = font.render("Mavuika", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Mavuika", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_fischl(self, surface, width, height, main_color, skin_color):
        self.draw_generic_character(surface, width, height, (200, 150, 255), skin_color)
        font = pygame.font.Font(None, 28)
        text = font.render("Fischl", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Fischl", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_lisa(self, surface, width, height, main_color, skin_color):
        self.draw_generic_character(surface, width, height, (150, 100, 200), skin_color)
        font = pygame.font.Font(None, 28)
        text = font.render("Lisa", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Lisa", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_kaeya(self, surface, width, height, main_color, skin_color):
        self.draw_generic_character(surface, width, height, (100, 150, 200), skin_color)
        font = pygame.font.Font(None, 28)
        text = font.render("Kaeya", True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height - 20))
        shadow_text = font.render("Kaeya", True, BLACK)
        surface.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text, text_rect)

    def draw_lumine(self, surface, width, height, main_color, skin_color):
        """Рисует Lumine - путешественницу с магическими силами"""
        # Светящиеся золотые волосы
        hair_base = (245, 220, 150)
        hair_magic = (255, 235, 120)

        # Основные волосы
        hair_rect = pygame.Rect(width * 0.12, height * 0.06, width * 0.76, height * 0.42)
        pygame.draw.ellipse(surface, hair_base, hair_rect)

        # Магические косы
        braid1 = pygame.Rect(width * 0.02, height * 0.22, width * 0.18, height * 0.58)
        braid2 = pygame.Rect(width * 0.8, height * 0.22, width * 0.18, height * 0.58)
        pygame.draw.ellipse(surface, (255, 245, 180), braid1)
        pygame.draw.ellipse(surface, (255, 245, 180), braid2)

        # Магический цветок
        flower_x, flower_y = int(width * 0.38), int(height * 0.12)
        for i in range(6):
            angle = i * 60
            petal_x = flower_x + 8 * math.cos(math.radians(angle))
            petal_y = flower_y + 8 * math.sin(math.radians(angle))
            pygame.draw.circle(surface, (255, 220, 160), (int(petal_x), int(petal_y)), 4)
        pygame.draw.circle(surface, (255, 200, 100), (flower_x, flower_y), 3)

        # Лицо
        face_rect = pygame.Rect(width * 0.25, height * 0.18, width * 0.5, height * 0.34)
        pygame.draw.ellipse(surface, skin_color, face_rect)

        # Светящиеся золотые глаза
        eye_base = (220, 180, 90)
        eye_glow = (255, 235, 130)

        left_eye = pygame.Rect(width * 0.31, height * 0.27, width * 0.11, width * 0.08)
        right_eye = pygame.Rect(width * 0.58, height * 0.27, width * 0.11, width * 0.08)
        pygame.draw.ellipse(surface, eye_base, left_eye)
        pygame.draw.ellipse(surface, eye_base, right_eye)

        pygame.draw.circle(surface, eye_glow, (int(width * 0.365), int(height * 0.3)), 3)
        pygame.draw.circle(surface, eye_glow, (int(width * 0.635), int(height * 0.3)), 3)

        # Путешественнический наряд
        outfit_white = (250, 250, 255)
        outfit_blue = (70, 130, 180)

        # Белая рубашка с магическими рунами
        shirt_rect = pygame.Rect(width * 0.26, height * 0.46, width * 0.48, height * 0.32)
        pygame.draw.rect(surface, outfit_white, shirt_rect)

        # Синий жилет
        vest_rect = pygame.Rect(width * 0.3, height * 0.5, width * 0.4, height * 0.27)
        pygame.draw.rect(surface, outfit_blue, vest_rect)

        # Магический меч
        sword_handle = pygame.Rect(width * 0.04, height * 0.28, width * 0.08, height * 0.15)
        pygame.draw.rect(surface, (140, 120, 80), sword_handle)
        sword_blade = pygame.Rect(width * 0.07, height * 0.12, width * 0.02, height * 0.18)
        pygame.draw.rect(surface, (220, 220, 240), sword_blade)
        pygame.draw.rect(surface, (180, 220, 255), (width * 0.075, height * 0.12, width * 0.01, height * 0.18))

        # Анемо эффекты
        wind_color = (150, 255, 200)
        star_color = (255, 255, 200)

        for i in range(6):
            star_x = width * (0.1 + i * 0.16)
            star_y = height * (0.05 + (i % 3) * 0.45)
            pygame.draw.line(surface, star_color, (star_x - 4, star_y), (star_x + 4, star_y), 1)
            pygame.draw.line(surface, star_color, (star_x, star_y - 4), (star_x, star_y + 4), 1)

    def draw_aether(self, surface, width, height, main_color, skin_color):
        """Рисует Aether - путешественника с анемо силой"""
        # Светло-золотистые волосы с косичкой
        hair_main = (220, 190, 130)
        hair_highlight = (240, 215, 155)

        # Основные волосы
        hair_rect = pygame.Rect(width * 0.18, height * 0.08, width * 0.64, height * 0.4)
        pygame.draw.ellipse(surface, hair_main, hair_rect)

        # Косичка сзади
        braid_rect = pygame.Rect(width * 0.42, height * 0.4, width * 0.16, height * 0.35)
        pygame.draw.ellipse(surface, hair_highlight, braid_rect)

        # Лицо
        face_rect = pygame.Rect(width * 0.28, height * 0.2, width * 0.44, height * 0.32)
        pygame.draw.ellipse(surface, skin_color, face_rect)

        # Золотые глаза
        eye_color = (180, 150, 70)
        left_eye = pygame.Rect(width * 0.34, height * 0.29, width * 0.08, width * 0.07)
        right_eye = pygame.Rect(width * 0.58, height * 0.29, width * 0.08, width * 0.07)
        pygame.draw.ellipse(surface, eye_color, left_eye)
        pygame.draw.ellipse(surface, eye_color, right_eye)

        # Мужская одежда путешественника
        outfit_dark = (60, 80, 100)
        outfit_light = (200, 180, 140)

        # Темная куртка
        jacket_rect = pygame.Rect(width * 0.25, height * 0.48, width * 0.5, height * 0.35)
        pygame.draw.rect(surface, outfit_dark, jacket_rect)

        # Светлые вставки
        trim_rect = pygame.Rect(width * 0.35, height * 0.52, width * 0.3, height * 0.25)
        pygame.draw.rect(surface, outfit_light, trim_rect)

        # Меч на спине
        sword_handle = pygame.Rect(width * 0.05, height * 0.35, width * 0.08, height * 0.15)
        pygame.draw.rect(surface, (120, 90, 60), sword_handle)

        # Анемо эффекты
        wind_color = (150, 220, 180)
        for i in range(5):
            wind_x = width * (0.1 + i * 0.2)
            wind_y = height * (0.15 + (i % 2) * 0.6)
            pygame.draw.circle(surface, wind_color, (int(wind_x), int(wind_y)), 2)

    def draw_generic_character(self, surface, width, height, main_color, skin_color):
        """Рисует обычного персонажа"""
        head_center = (width // 2, height // 3)
        pygame.draw.circle(surface, skin_color, head_center, 30)

        hair_rect = pygame.Rect(head_center[0] - 35, head_center[1] - 40, 70, 60)
        pygame.draw.ellipse(surface, main_color, hair_rect)

        left_eye = (head_center[0] - 8, head_center[1] - 5)
        right_eye = (head_center[0] + 8, head_center[1] - 5)
        pygame.draw.circle(surface, WHITE, left_eye, 6)
        pygame.draw.circle(surface, WHITE, right_eye, 6)
        pygame.draw.circle(surface, main_color, left_eye, 3)
        pygame.draw.circle(surface, main_color, right_eye, 3)

        body_rect = pygame.Rect(width // 2 - 25, height // 2, 50, 100)
        outfit_color = tuple(c // 2 for c in main_color)
        pygame.draw.rect(surface, outfit_color, body_rect)

        for i in range(3):
            effect_x = head_center[0] + 40 * math.cos(i * 2.1)
            effect_y = head_center[1] + 40 * math.sin(i * 2.1)
            pygame.draw.circle(surface, main_color, (int(effect_x), int(effect_y)), 4)

    def create_tone_sound(self, frequency, duration):
        """Создает простой тональный звук"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate)

            # Создаем массив звуковых данных
            sound_buffer = []

            for i in range(frames):
                t = i / sample_rate
                # Простая синусоида
                amplitude = 0.3 * (1 - t / duration)  # Затухание
                sample_value = amplitude * math.sin(frequency * 2 * math.pi * t)
                # Конвертируем в 16-битный формат
                sample_16bit = int(sample_value * 32767)
                sound_buffer.append(sample_16bit)
                sound_buffer.append(sample_16bit)  # Стерео

            # Преобразуем в bytes
            sound_bytes = b''
            for sample in sound_buffer:
                sound_bytes += sample.to_bytes(2, byteorder='little', signed=True)

            return pygame.mixer.Sound(buffer=sound_bytes)

        except Exception as e:
            print(f"⚠️  Ошибка создания звука {frequency}Hz: {e}")
            return None

    def create_bubble_sound(self, base_freq, duration):
        """Создает звук пузыря"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate)
            sound_buffer = []

            for i in range(frames):
                t = i / sample_rate
                # Пузырьковый эффект с вибрацией
                frequency = base_freq + 50 * math.sin(t * 15)  # Вибрация частоты
                amplitude = 0.2 * (1 - t / duration) * (1 + 0.3 * math.sin(t * 25))  # Модуляция амплитуды
                sample_value = amplitude * math.sin(frequency * 2 * math.pi * t)
                sample_16bit = int(sample_value * 32767)
                sound_buffer.append(sample_16bit)
                sound_buffer.append(sample_16bit)

            sound_bytes = b''
            for sample in sound_buffer:
                sound_bytes += sample.to_bytes(2, byteorder='little', signed=True)

            return pygame.mixer.Sound(buffer=sound_bytes)

        except Exception as e:
            print(f"⚠️  Ошибка создания пузыря {base_freq}Hz: {e}")
            return None

    def create_melody_sound(self, frequencies, duration):
        """Создает мелодию из нескольких нот"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate)
            sound_buffer = []

            note_duration = duration / len(frequencies)

            for i in range(frames):
                t = i / sample_rate
                note_index = min(int(t / note_duration), len(frequencies) - 1)
                frequency = frequencies[note_index]

                # Плавные переходы между нотами
                note_progress = (t % note_duration) / note_duration
                envelope = math.sin(note_progress * math.pi)  # Огибающая

                amplitude = 0.25 * envelope
                sample_value = amplitude * math.sin(frequency * 2 * math.pi * t)
                sample_16bit = int(sample_value * 32767)
                sound_buffer.append(sample_16bit)
                sound_buffer.append(sample_16bit)

            sound_bytes = b''
            for sample in sound_buffer:
                sound_bytes += sample.to_bytes(2, byteorder='little', signed=True)

            return pygame.mixer.Sound(buffer=sound_bytes)

        except Exception as e:
            print(f"⚠️  Ошибка создания мелодии: {e}")
            return None

    def handle_gallery_click(self, pos):
        """Обработка кликов в галерее"""
        gallery_width = WINDOW_WIDTH - 100
        gallery_height = WINDOW_HEIGHT - 100
        gallery_x = 50
        gallery_y = 50

        # Проверяем клик по бегунку
        scrollbar_x = gallery_x + gallery_width - 20
        scrollbar_width = 15

        if (scrollbar_x <= pos[0] <= scrollbar_x + scrollbar_width and
                gallery_y + 120 <= pos[1] <= gallery_y + gallery_height - 120):
            self.scrollbar_dragging = True
            self.scrollbar_drag_offset = pos[1] - self.get_scrollbar_handle_y()
            return

        # Клик вне галереи - закрываем
        if not (gallery_x <= pos[0] <= gallery_x + gallery_width and
                gallery_y <= pos[1] <= gallery_y + gallery_height):
            self.show_gallery = False
            self.play_sound('deselect')

    def handle_scrollbar_drag(self, pos):
        """Обработка перетаскивания бегунка"""
        gallery_height = WINDOW_HEIGHT - 100
        gallery_y = 50

        scrollbar_area_height = gallery_height - 240  # Вычитаем отступы
        handle_y = pos[1] - self.scrollbar_drag_offset

        # Ограничиваем позицию бегунка
        min_handle_y = gallery_y + 120
        max_handle_y = gallery_y + gallery_height - 120 - 30  # 30 - высота бегунка
        handle_y = max(min_handle_y, min(max_handle_y, handle_y))

        # Пересчитываем позицию прокрутки
        if max_handle_y > min_handle_y:
            scroll_ratio = (handle_y - min_handle_y) / (max_handle_y - min_handle_y)
            self.gallery_scroll_y = scroll_ratio * self.gallery_max_scroll

    def get_scrollbar_handle_y(self):
        """Вычисляет Y-позицию бегунка"""
        gallery_height = WINDOW_HEIGHT - 100
        gallery_y = 50

        min_handle_y = gallery_y + 120
        max_handle_y = gallery_y + gallery_height - 120 - 30

        if self.gallery_max_scroll <= 0:
            return min_handle_y

        scroll_ratio = self.gallery_scroll_y / self.gallery_max_scroll
        return min_handle_y + scroll_ratio * (max_handle_y - min_handle_y)

    def play_sound(self, sound_name):
        """Воспроизводит звук"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Warning: Could not play {sound_name} sound: {e}")
                pass  # Игнорируем ошибки звука
        """Воспроизводит звук"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Warning: Could not play {sound_name} sound: {e}")
                pass  # Игнорируем ошибки звука

    def run(self):
        """Главный игровой цикл"""
        running = True
        last_time = time.time()

        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        if self.show_gallery:
                            self.handle_gallery_click(event.pos)
                        else:
                            self.handle_click(event.pos)
                    elif event.button == 4 and self.show_gallery:  # Колесо вверх
                        self.gallery_scroll_y = max(0, self.gallery_scroll_y - self.gallery_scroll_speed)
                    elif event.button == 5 and self.show_gallery:  # Колесо вниз
                        self.gallery_scroll_y = min(self.gallery_max_scroll,
                                                    self.gallery_scroll_y + self.gallery_scroll_speed)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Отпускание левой кнопки
                        self.scrollbar_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.scrollbar_dragging:
                        self.handle_scrollbar_drag(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_level()
                        self.play_sound('pour')
                    elif event.key == pygame.K_n and self.game_completed:
                        self.next_level()
                        self.play_sound('pour')
                    elif event.key == pygame.K_g:  # Открыть галерею
                        self.show_gallery = not self.show_gallery
                        self.play_sound('select')
                    # Клавиша C зарезервирована для будущего использования
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_F11:
                        if self.show_gallery:
                            self.show_gallery = False
                            self.play_sound('deselect')
                        else:
                            running = False

            # Обновление таймера победы
            if self.game_completed and self.victory_timer > 0:
                self.victory_timer -= dt
                if self.victory_timer <= 0:
                    self.next_level()  # Автоматический переход к следующему уровню

            # Обновление
            for bottle in self.bottles:
                bottle.update(dt)

            # Рендеринг
            self.draw_ui()

            # Рисуем бутылки сначала
            for bottle in self.bottles:
                bottle.draw(self.screen, self.font)

            # Потом рисуем экран победы ПОВЕРХ всего
            self.draw_victory_screen()

            # Галерея персонажей (самая верхняя)
            if self.show_gallery:
                self.draw_character_gallery()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def draw_victory_screen(self):
        """Отдельный метод для рисования экрана победы (поверх всего)"""
        if not (self.game_completed and self.victory_timer > 0):
            return

        # Полупрозрачный фон (поверх всего!)
        victory_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        victory_surface.fill((0, 0, 0, 200))  # Увеличиваем непрозрачность
        self.screen.blit(victory_surface, (0, 0))

        # Главное окно победы
        panel_width = 600
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2

        # Фон панели
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 60, 240))  # Темно-синий фон
        pygame.draw.rect(panel_surface, (100, 200, 255), (0, 0, panel_width, panel_height), 4)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Анимированный текст победы
        pulse = 1.0 + 0.3 * math.sin(time.time() * 4)
        title_size = int(72 * pulse)
        victory_font = pygame.font.Font(None, title_size)

        victory_text = victory_font.render("🎉 ПОБЕДА! 🎉", True, (255, 215, 0))
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 80))

        # Тень для текста
        shadow_text = victory_font.render("🎉 ПОБЕДА! 🎉", True, BLACK)
        shadow_rect = victory_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(victory_text, victory_rect)

        # Информация об уровне
        level_text = self.font.render(f"Уровень {self.level} завершён!", True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 160))
        self.screen.blit(level_text, level_rect)

        # Статистика
        moves_text = self.small_font.render(f"💫 Потрачено ходов: {self.moves}", True, LIGHT_GRAY)
        moves_rect = moves_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 200))
        self.screen.blit(moves_text, moves_rect)

        if self.best_moves != float('inf') and self.moves < self.best_moves:
            record_text = self.small_font.render("🏆 НОВЫЙ РЕКОРД!", True, (255, 215, 0))
            record_rect = record_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 225))
            self.screen.blit(record_text, record_rect)

        # Управление
        continue_text = self.small_font.render("♾️ R - повторить    ➡️ N - следующий уровень", True, LIGHT_GRAY)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 290))
        self.screen.blit(continue_text, continue_rect)

        # Таймер автоперехода
        timer_color = (255, 255 - int(self.victory_timer * 85), 0)  # От жёлтого к красному
        timer_text = self.small_font.render(f"⏱️ Автопереход через: {int(self.victory_timer + 1)}", True, timer_color)
        timer_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 330))
        self.screen.blit(timer_text, timer_rect)

    def draw_character_gallery(self):
        """Отображает прокручиваемую галерею персонажей"""
        # Полупрозрачный фон
        gallery_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        gallery_surface.fill((0, 0, 0, 220))
        self.screen.blit(gallery_surface, (0, 0))

        # Главное окно галереи
        gallery_width = WINDOW_WIDTH - 100
        gallery_height = WINDOW_HEIGHT - 100
        gallery_x = 50
        gallery_y = 50

        # Фон галереи
        gallery_bg = pygame.Surface((gallery_width, gallery_height), pygame.SRCALPHA)
        gallery_bg.fill((30, 30, 60, 240))
        pygame.draw.rect(gallery_bg, (100, 200, 255), (0, 0, gallery_width, gallery_height), 4)
        self.screen.blit(gallery_bg, (gallery_x, gallery_y))

        # Заголовок (увеличенный)
        large_title_font = pygame.font.Font(None, 72)
        title_text = large_title_font.render("🎭 Галерея персонажей Genshin Impact", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, gallery_y + 40))
        self.screen.blit(title_text, title_rect)

        # Статистика
        collected = len(self.character_collection)
        total = len(self.characters)
        stats_font = pygame.font.Font(None, 40)
        stats_text = stats_font.render(f"Собрано: {collected}/{total} персонажей", True, LIGHT_GRAY)
        stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, gallery_y + 80))
        self.screen.blit(stats_text, stats_rect)

        # Параметры для отображения персонажей
        chars_per_row = 3
        char_size = 220
        card_spacing_x = 30
        card_spacing_y = 40

        # Вычисляем область для прокрутки
        content_start_y = gallery_y + 120
        content_area_height = gallery_height - 240

        # Вычисляем общую высоту контента
        total_chars = len(self.characters)
        rows_needed = (total_chars + chars_per_row - 1) // chars_per_row
        total_content_height = rows_needed * (char_size + card_spacing_y) - card_spacing_y

        # Обновляем максимальную прокрутку
        self.gallery_max_scroll = max(0, total_content_height - content_area_height)
        self.gallery_scroll_y = max(0, min(self.gallery_max_scroll, self.gallery_scroll_y))

        # Создаем область обрезки для прокручиваемого контента
        content_surface = pygame.Surface((gallery_width - 40, content_area_height), pygame.SRCALPHA)

        # Отображаем всех персонажей
        char_list = list(self.characters.keys())
        start_x = 80
        start_y = -self.gallery_scroll_y

        for i, char_id in enumerate(char_list):
            row = i // chars_per_row
            col = i % chars_per_row

            char_x = start_x + col * (char_size + card_spacing_x)
            char_y = start_y + row * (char_size + card_spacing_y)

            # Пропускаем невидимые карточки
            if char_y + char_size < 0 or char_y > content_area_height:
                continue

            # Фон карточки
            card_bg = pygame.Surface((char_size, char_size), pygame.SRCALPHA)

            if char_id in self.character_collection:
                # Открытый персонаж
                card_bg.fill((50, 50, 100, 200))
                pygame.draw.rect(card_bg, self.characters[char_id]['color'], (0, 0, char_size, char_size), 3)

                # Рисуем персонажа
                char_image = self.create_character_image(char_id)
                scaled_image = pygame.transform.scale(char_image, (char_size - 30, char_size - 40))
                card_bg.blit(scaled_image, (15, 15))

                # Новый персонаж - свечение
                if char_id == self.current_level_character and self.new_character_unlocked:
                    glow_surface = pygame.Surface((char_size + 20, char_size + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (255, 255, 0, 100), (0, 0, char_size + 20, char_size + 20), 10)
                    content_surface.blit(glow_surface, (char_x - 10, char_y - 10))

                    large_font = pygame.font.Font(None, 36)
                    new_text = large_font.render("NEW!", True, (255, 255, 0))
                    content_surface.blit(new_text, (char_x + char_size - 50, char_y + 8))
            else:
                # Закрытый персонаж
                card_bg.fill((30, 30, 30, 200))
                pygame.draw.rect(card_bg, (100, 100, 100), (0, 0, char_size, char_size), 3)

                question_font = pygame.font.Font(None, 120)
                question_text = question_font.render("?", True, (150, 150, 150))
                question_rect = question_text.get_rect(center=(char_size // 2, char_size // 2))
                card_bg.blit(question_text, question_rect)

                name_font = pygame.font.Font(None, 32)
                name_text = name_font.render("???", True, (100, 100, 100))
                name_rect = name_text.get_rect(center=(char_size // 2, char_size - 20))
                card_bg.blit(name_text, name_rect)

            content_surface.blit(card_bg, (char_x, char_y))

        # Отрисовываем прокручиваемый контент
        self.screen.blit(content_surface, (gallery_x + 20, content_start_y))

        # Рисуем бегунок прокрутки
        if self.gallery_max_scroll > 0:
            scrollbar_x = gallery_x + gallery_width - 20
            scrollbar_y = content_start_y
            scrollbar_width = 15
            scrollbar_height = content_area_height

            pygame.draw.rect(self.screen, (60, 60, 60), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            pygame.draw.rect(self.screen, (100, 100, 100),
                             (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), 2)

            handle_height = max(30, int(scrollbar_height * content_area_height / total_content_height))
            handle_y = self.get_scrollbar_handle_y()

            pygame.draw.rect(self.screen, (150, 150, 150),
                             (scrollbar_x + 2, handle_y, scrollbar_width - 4, handle_height))
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (scrollbar_x + 2, handle_y, scrollbar_width - 4, handle_height), 1)

        # Инструкции
        instructions = [
            "G - открыть/закрыть галерею | Колесо мыши: прокрутка",
            "ESC - закрыть галерею | Перетаскивание бегунка",
            "Проходите уровни, чтобы разблокировать персонажей!"
        ]

        instructions_font = pygame.font.Font(None, 32)
        for i, instruction in enumerate(instructions):
            text = instructions_font.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(text, (gallery_x + 30, gallery_y + gallery_height - 100 + i * 25))


if __name__ == "__main__":
    print("🧪 Запуск Liquid Sort Puzzle...")
    print("🎯 Цель: отсортируйте жидкости по цветам")
    print("🖱️ Управление: клики мышью")
    print("⌨️ R - перезапуск, N - следующий уровень")
    print("=" * 50)

    game = Game()
    game.run()