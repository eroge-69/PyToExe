import pygame
import sys
import os
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('game_coordinates.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация pygame
pygame.init()
pygame.mixer.init()

# Начальное разрешение
INITIAL_WIDTH, INITIAL_HEIGHT = 800, 600
current_width, current_height = INITIAL_WIDTH, INITIAL_HEIGHT
screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
pygame.display.set_caption("Майнкрафт Меню")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (198, 198, 198)
DARK_GRAY = (150, 150, 150)
GREEN = (58, 179, 58)
DARK_GREEN = (28, 98, 28)
SLIDER_COLOR = (100, 100, 100)
SLIDER_HANDLE_COLOR = (70, 70, 70)
DIALOG_BG = (50, 50, 70)  # Темно-синий фон диалога
DIALOG_TEXT = (240, 240, 240)

# Папка для сохранений
SAVES_FOLDER = "saves"
if not os.path.exists(SAVES_FOLDER):
    os.makedirs(SAVES_FOLDER)

# Загрузка фона и музыки
try:
    background = pygame.image.load("minecraft_background.jpg")
    background = pygame.transform.scale(background, (current_width, current_height))

    pygame.mixer.music.load("main.mp3")
    pygame.mixer.music.set_volume(0.5)
    music_playing = True
    pygame.mixer.music.play(-1)
except:
    print("Ошибка загрузки файлов! Используется стандартный фон.")
    background = pygame.Surface((current_width, current_height))
    background.fill((135, 206, 235))
    music_playing = False

# Шрифты
try:
    minecraft_font = pygame.font.Font("Minecraft.ttf", 40)
    small_minecraft_font = pygame.font.Font("Minecraft.ttf", 30)
    dialog_font = pygame.font.Font("Minecraft.ttf", 24)
except:
    print("Шрифт Minecraft.ttf не найден, используется стандартный")
    minecraft_font = pygame.font.Font(None, 40)
    small_minecraft_font = pygame.font.Font(None, 30)
    dialog_font = pygame.font.Font(None, 24)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = font or minecraft_font

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color

        pygame.draw.rect(surface, color, self.rect, border_radius=2)
        pygame.draw.line(surface, (213, 213, 213), (self.rect.left, self.rect.top),
                         (self.rect.right - 1, self.rect.top), 3)
        pygame.draw.line(surface, (213, 213, 213), (self.rect.left, self.rect.top),
                         (self.rect.left, self.rect.bottom - 1), 3)
        pygame.draw.line(surface, (85, 85, 85), (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right - 1, self.rect.bottom - 1), 3)
        pygame.draw.line(surface, (85, 85, 85), (self.rect.right - 1, self.rect.top),
                         (self.rect.right - 1, self.rect.bottom - 1), 3)

        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = self.rect.collidepoint(pos)
            if clicked:
                logger.info(f"Клик по кнопке '{self.text}' в координатах: {pos}")
            return clicked
        return False


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_rect = pygame.Rect(x, y - 5, 20, height + 10)
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, SLIDER_COLOR, self.rect, border_radius=5)
        pygame.draw.rect(surface, SLIDER_HANDLE_COLOR, self.handle_rect, border_radius=5)

    def update(self, pos):
        if self.dragging:
            self.handle_rect.centerx = max(self.rect.left, min(pos[0], self.rect.right))
            self.value = self.min_val + (self.max_val - self.min_val) * (
                    (self.handle_rect.centerx - self.rect.left) / self.rect.width)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                logger.info(f"Начало перетаскивания слайдера в координатах: {event.pos}")
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                logger.info(f"Конец перетаскивания слайдера. Текущее значение: {self.value}")
            self.dragging = False


class DialogBox:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dialog_width = 500
        self.dialog_height = 200
        self.dialog_rect = pygame.Rect(
            (screen_width - self.dialog_width) // 2,
            (screen_height - self.dialog_height) // 2,
            self.dialog_width,
            self.dialog_height
        )
        self.text = ""
        self.speaker = ""
        self.showing = False
        self.text_speed = 1
        self.current_text = ""
        self.char_index = 0
        self.text_complete = False

        # Кнопки
        button_width = 100
        button_height = 40
        self.yes_button = Button(
            self.dialog_rect.centerx - button_width - 10,
            self.dialog_rect.bottom - button_height - 20,
            button_width,
            button_height,
            "Да",
            GREEN,
            DARK_GREEN,
            dialog_font
        )
        self.no_button = Button(
            self.dialog_rect.centerx + 10,
            self.dialog_rect.bottom - button_height - 20,
            button_width,
            button_height,
            "Нет",
            GRAY,
            DARK_GRAY,
            dialog_font
        )
        self.show_choice = False

    def start_dialog(self, speaker, text):
        self.speaker = speaker
        self.text = text
        self.current_text = ""
        self.char_index = 0
        self.text_complete = False
        self.showing = True
        self.show_choice = False

    def update(self):
        if not self.text_complete and self.showing:
            self.char_index += self.text_speed
            if self.char_index >= len(self.text):
                self.char_index = len(self.text)
                self.text_complete = True
            self.current_text = self.text[:int(self.char_index)]

    def draw(self, surface):
        if not self.showing:
            return

        # Затемнение фона
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        surface.blit(s, (0, 0))

        # Рисуем диалоговое окно
        pygame.draw.rect(surface, DIALOG_BG, self.dialog_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.dialog_rect, 2, border_radius=10)

        # Текст говорящего
        speaker_text = dialog_font.render(f"{self.speaker}:", True, WHITE)
        surface.blit(speaker_text, (self.dialog_rect.x + 20, self.dialog_rect.y + 20))

        # Основной текст
        y_offset = self.dialog_rect.y + 60
        words = self.current_text.split(' ')
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()
            if dialog_font.size(test_line)[0] < self.dialog_width - 40:
                line = test_line
            else:
                text_surface = dialog_font.render(line, True, DIALOG_TEXT)
                surface.blit(text_surface, (self.dialog_rect.x + 20, y_offset))
                y_offset += 30
                line = word

        if line:
            text_surface = dialog_font.render(line, True, DIALOG_TEXT)
            surface.blit(text_surface, (self.dialog_rect.x + 20, y_offset))

        # Кнопки выбора (если текст полностью отображен)
        if self.text_complete and self.show_choice:
            self.yes_button.draw(surface)
            self.no_button.draw(surface)

    def handle_event(self, event):
        if not self.showing:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.text_complete:
                # Пропустить анимацию текста
                self.current_text = self.text
                self.text_complete = True
                self.show_choice = True
                return True
            elif self.show_choice:
                if self.yes_button.is_clicked(mouse_pos, event):
                    self.showing = False
                    return "yes"
                elif self.no_button.is_clicked(mouse_pos, event):
                    self.showing = False
                    return "no"

        return None


def handle_click_logging(pos, context=""):
    """Логирует координаты клика с дополнительным контекстом"""
    logger.info(f"Клик в координатах: {pos} {context}")


def show_settings():
    global current_width, current_height, screen, music_playing

    fullscreen = False

    width_slider = Slider(200, 200, 400, 10, 640, 1920, current_width)
    height_slider = Slider(200, 300, 400, 10, 480, 1080, current_height)

    apply_button = Button(current_width // 2 - 100, 400, 200, 50, "Применить", GRAY, DARK_GRAY)
    music_toggle = Button(current_width // 2 - 100, 500, 200, 50,
                          "Музыка: ВКЛ" if music_playing else "Музыка: ВЫКЛ",
                          GRAY, DARK_GRAY)
    fullscreen_toggle = Button(current_width // 2 - 100, 350, 200, 50,
                               "Полный экран: ВЫКЛ" if not fullscreen else "Полный экран: ВКЛ",
                               GRAY, DARK_GRAY)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click_logging(event.pos, "в настройках")

            width_slider.handle_event(event)
            height_slider.handle_event(event)

            if apply_button.is_clicked(mouse_pos, event):
                if not fullscreen:
                    new_width = int(width_slider.value)
                    new_height = int(height_slider.value)
                    if new_width != current_width or new_height != current_height:
                        current_width, current_height = new_width, new_height
                        screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                running = False

            if music_toggle.is_clicked(mouse_pos, event):
                music_playing = not music_playing
                if music_playing:
                    pygame.mixer.music.play(-1)
                    music_toggle.text = "Музыка: ВКЛ"
                else:
                    pygame.mixer.music.stop()
                    music_toggle.text = "Музыка: ВЫКЛ"

            if fullscreen_toggle.is_clicked(mouse_pos, event):
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    current_width, current_height = screen.get_size()
                    fullscreen_toggle.text = "Полный экран: ВКЛ"
                else:
                    screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                    fullscreen_toggle.text = "Полный экран: ВЫКЛ"

        width_slider.update(mouse_pos)
        height_slider.update(mouse_pos)

        screen.fill((240, 240, 240))

        title = minecraft_font.render("Настройки", True, BLACK)
        screen.blit(title, (current_width // 2 - title.get_width() // 2, 50))

        if not fullscreen:
            width_text = small_minecraft_font.render(f"Ширина: {int(width_slider.value)}", True, BLACK)
            height_text = small_minecraft_font.render(f"Высота: {int(height_slider.value)}", True, BLACK)
            screen.blit(width_text, (50, 190))
            screen.blit(height_text, (50, 290))

            width_slider.draw(screen)
            height_slider.draw(screen)
        else:
            message = small_minecraft_font.render("Полноэкранный режим активен", True, BLACK)
            screen.blit(message, (current_width // 2 - message.get_width() // 2, 200))

        apply_button.check_hover(mouse_pos)
        apply_button.draw(screen)
        music_toggle.check_hover(mouse_pos)
        music_toggle.draw(screen)
        fullscreen_toggle.check_hover(mouse_pos)
        fullscreen_toggle.draw(screen)

        pygame.display.flip()


def show_trader_interface():
    """Функция для отображения интерфейса торговца с диалоговым окном"""
    current_width, current_height = pygame.display.get_surface().get_size()

    try:
        trader_bg = pygame.image.load("trade.jpg")
        trader_bg = pygame.transform.scale(trader_bg, (current_width, current_height))
    except:
        trader_bg = pygame.Surface((current_width, current_height))
        trader_bg.fill((50, 50, 50))

    try:
        hover_bg = pygame.image.load("navodkatrader.jpg")
        hover_bg = pygame.transform.scale(hover_bg, (current_width, current_height))
    except:
        hover_bg = None

    back_button = Button(current_width - 210, current_height - 80, 200, 50, "Назад", GRAY, DARK_GRAY)

    # Определяем зону перехода
    x_coords = [15, 67, 601, 624]
    y_coords = [686, 14, 67, 668]
    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)
    transition_zone = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    # Создаем диалоговое окно
    dialog_box = DialogBox(current_width, current_height)

    # Состояния интерфейса
    is_hovering = False
    show_dialog = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_hover_state = transition_zone.collidepoint(mouse_pos) if not show_dialog else False

        if current_hover_state != is_hovering:
            is_hovering = current_hover_state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click_logging(event.pos, "в интерфейсе торговца")

                if transition_zone.collidepoint(event.pos) and not show_dialog:
                    show_dialog = True
                    dialog_box.start_dialog("Торговец", "Хотите ли вы нарубить дерева?")
                    dialog_box.show_choice = True

            if show_dialog:
                result = dialog_box.handle_event(event)
                if result == "yes":
                    print("Игрок выбрал Да")
                    show_dialog = False
                elif result == "no":
                    print("Игрок выбрал Нет")
                    show_dialog = False

            if back_button.is_clicked(mouse_pos, event) and not show_dialog:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if show_dialog:
                    show_dialog = False
                else:
                    running = False

        # Отрисовка фона
        if is_hovering and hover_bg and not show_dialog:
            screen.blit(hover_bg, (0, 0))
        else:
            screen.blit(trader_bg, (0, 0))

        # Отрисовка диалогового окна
        if show_dialog:
            dialog_box.update()
            dialog_box.draw(screen)

        # Отрисовка кнопки "Назад" (если не показываем диалог)
        if not show_dialog:
            back_button.check_hover(mouse_pos)
            back_button.draw(screen)

        # Изменение курсора
        if is_hovering and not show_dialog:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()


def show_map():
    global music_playing

    if music_playing:
        pygame.mixer.music.stop()
        music_playing = False

    try:
        map_image = pygame.image.load("map.png")
        map_image = pygame.transform.scale(map_image, (current_width, current_height))
    except:
        map_image = pygame.Surface((current_width, current_height))
        map_image.fill((100, 100, 100))

    trader_zone = pygame.Rect(1150, 550, 100, 100)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click_logging(event.pos, "на карте")
                if trader_zone.collidepoint(event.pos):
                    logger.info("Клик по зоне торговца")
                    show_trader_interface()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.blit(map_image, (0, 0))
        pygame.display.flip()

    if not music_playing:
        pygame.mixer.music.play(-1)
        music_playing = True


def main_menu():
    buttons = [
        Button(current_width // 2 - 150, 150, 300, 60, "Старт", GRAY, DARK_GRAY),
        Button(current_width // 2 - 150, 250, 300, 60, "Загрузить", GRAY, DARK_GRAY),
        Button(current_width // 2 - 150, 350, 300, 60, "Настройки", GRAY, DARK_GRAY),
        Button(current_width // 2 - 150, 450, 300, 60, "Выход", GRAY, DARK_GRAY)
    ]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click_logging(event.pos, "в главном меню")

            for i, button in enumerate(buttons):
                if button.is_clicked(mouse_pos, event):
                    if i == 0:
                        show_map()
                    elif i == 1:
                        print("Загрузка игры")
                    elif i == 2:
                        show_settings()
                        for j, btn in enumerate(buttons):
                            btn.rect.x = current_width // 2 - 150
                            btn.rect.y = 150 + j * 100
                    elif i == 3:
                        running = False

        scaled_bg = pygame.transform.scale(background, (current_width, current_height))
        screen.blit(scaled_bg, (0, 0))

        title = minecraft_font.render("Главное Меню", True, WHITE)
        screen.blit(title, (current_width // 2 - title.get_width() // 2, 50))

        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
    pygame.quit()
    sys.exit()