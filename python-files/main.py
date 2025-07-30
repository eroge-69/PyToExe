import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Печаталка")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GOLD = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)

# Шрифты
font_large = pygame.font.SysFont('Arial', 48)
font_medium = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

# Состояния игры
MENU = 0
DIFFICULTY_SELECT = 1
GAME = 2
ABOUT = 3
GAME_OVER = 4
game_state = MENU

# Настройки игры
difficulty = "easy"
target_text = ""
input_text = ""
score = 0
high_score = 0
time_left = 0
game_start_time = 0


# Создаем фоны
def create_background(width, height):
    background = pygame.Surface((width, height))
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            color = LIGHT_BLUE if (i // 20 + j // 20) % 2 == 0 else WHITE
            pygame.draw.rect(background, color, (i, j, 20, 20))
    return background


menu_background = create_background(WIDTH, HEIGHT)
game_background = create_background(WIDTH, HEIGHT)

# Декоративные элементы
pygame.draw.circle(menu_background, GOLD, (100, 100), 50, 5)
pygame.draw.circle(menu_background, GOLD, (700, 500), 60, 5)
pygame.draw.line(menu_background, BLUE, (0, 0), (WIDTH, HEIGHT), 3)

# Кнопки меню
play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
about_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)

# Кнопки выбора сложности
easy_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50)
medium_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)
hard_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50)

# Кнопка возврата
back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)


def generate_target_text(length):
    letters = "абвгдеёжзиклмнопрстуфхцчиёклмныъэьюя"
    return ''.join(random.choice(letters) for _ in range(length))


def start_game(diff):
    global target_text, input_text, score, time_left, difficulty, game_start_time, game_state
    difficulty = diff
    input_text = ""
    score = 0

    if difficulty == "easy":
        target_text = generate_target_text(5)
        time_left = 15
    elif difficulty == "medium":
        target_text = generate_target_text(8)
        time_left = 12
    elif difficulty == "hard":
        target_text = generate_target_text(12)
        time_left = 10

    game_start_time = time.time()
    game_state = GAME


def draw_text_with_outline(text, font, text_color, outline_color, x, y, outline_size=2):
    # Рендерим контур
    for dx in [-outline_size, 0, outline_size]:
        for dy in [-outline_size, 0, outline_size]:
            if dx != 0 or dy != 0:
                text_surface = font.render(text, True, outline_color)
                screen.blit(text_surface, (x + dx - text_surface.get_width() // 2, y + dy))

    # Рендерим основной текст
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x - text_surface.get_width() // 2, y))


def draw_button(rect, text, active_color, inactive_color):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0] == 1

    color = active_color if rect.collidepoint(mouse_pos) else inactive_color
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

    text_surf = font_medium.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    if click and rect.collidepoint(mouse_pos):
        pygame.time.delay(100)
        return True
    return False


def draw_text_box(text, font, text_color, box_color, x, y, padding=20):
    text_surface = font.render(text, True, text_color)
    box_width = text_surface.get_width() + padding * 2
    box_height = text_surface.get_height() + padding * 2
    box_rect = pygame.Rect(x - box_width // 2, y - box_height // 2, box_width, box_height)

    pygame.draw.rect(screen, box_color, box_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, box_rect, 3, border_radius=10)
    screen.blit(text_surface, (x - text_surface.get_width() // 2, y - text_surface.get_height() // 2))

    return box_rect


def main_menu():
    global game_state

    screen.blit(menu_background, (0, 0))

    draw_text_with_outline("Печаталка", font_large, BLUE, WHITE, WIDTH // 2, 100)
    draw_text_with_outline(f"Рекорд: {high_score}", font_small, BLACK, WHITE, WIDTH // 2, 170)

    if draw_button(play_button, "Играть", GREEN, GRAY):
        game_state = DIFFICULTY_SELECT

    if draw_button(about_button, "Об игре", BLUE, GRAY):
        game_state = ABOUT

    if draw_button(exit_button, "Выход", RED, GRAY):
        pygame.quit()
        sys.exit()


def difficulty_select():
    global game_state

    screen.blit(menu_background, (0, 0))

    draw_text_with_outline("Выберите сложность", font_large, BLUE, WHITE, WIDTH // 2, 100)

    if draw_button(easy_button, "Легкий", GREEN, GRAY):
        start_game("easy")

    if draw_button(medium_button, "Средний", BLUE, GRAY):
        start_game("medium")

    if draw_button(hard_button, "Сложный", RED, GRAY):
        start_game("hard")

    if draw_button(back_button, "Назад", DARK_GRAY, GRAY):
        game_state = MENU


def about_screen():
    global game_state

    screen.blit(menu_background, (0, 0))

    draw_text_with_outline("Об игре", font_large, BLUE, WHITE, WIDTH // 2, 80)

    lines = [
        "Правила: вводить буквы из рамки",
        "чтобы получать очки",
        "",
        "Сложности",
        "- Легкий: 5 букв, 15 секунд",
        "- Средний: 8 букв, 12 секунд",
        "- Сложный: 12 букв, 10 секунд",
        "",
        "Чем быстрее вы вводите текст,",
        "тем больше очков получаете!",
        "за каждое введёное рандомное слово вы получаете +1 секунду к временни"
    ]

    for i, line in enumerate(lines):
        text = font_small.render(line, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 180 + i * 30))

    if draw_button(back_button, "Назад", DARK_GRAY, GRAY):
        game_state = MENU


def game_screen():
    global input_text, score, time_left, game_state, game_start_time, target_text, high_score

    screen.blit(game_background, (0, 0))

    current_time = time.time()
    time_left = max(0, time_left - (current_time - game_start_time))
    game_start_time = current_time

    if time_left <= 0:
        if score > high_score:
            high_score = score
        game_state = GAME_OVER
        return

    draw_text_with_outline(f"Время: {time_left:.1f}", font_small, BLACK, WHITE, 100, 30)
    draw_text_with_outline(f"Счет: {score}", font_small, BLACK, WHITE, WIDTH - 100, 30)
    draw_text_with_outline(f"Рекорд: {high_score}", font_small, BLACK, WHITE, WIDTH // 2, 30)

    if not target_text:
        if difficulty == "easy":
            target_text = generate_target_text(5)
        elif difficulty == "medium":
            target_text = generate_target_text(8)
        else:
            target_text = generate_target_text(12)

    draw_text_box(target_text, font_large, BLUE, WHITE, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text_box(input_text, font_large, GREEN, WHITE, WIDTH // 2, HEIGHT // 2 + 80)

    if input_text == target_text:
        score += len(target_text) * max(1, int(time_left))
        if difficulty == "easy":
            target_text = generate_target_text(5)
            time_left += 3
        elif difficulty == "medium":
            target_text = generate_target_text(8)
            time_left += 2
        elif difficulty == "hard":
            target_text = generate_target_text(12)
            time_left += 1
        input_text = ""


def game_over_screen():
    global game_state

    screen.blit(menu_background, (0, 0))

    draw_text_with_outline("Игра окончена!", font_large, RED, WHITE, WIDTH // 2, 100)
    draw_text_with_outline(f"Ваш счет: {score}", font_medium, BLACK, WHITE, WIDTH // 2, 200)
    draw_text_with_outline(f"Рекорд: {high_score}", font_medium, GOLD, WHITE, WIDTH // 2, 250)

    if draw_button(back_button, "В главное меню", DARK_GRAY, GRAY):
        game_state = MENU


# Основной игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GAME and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = MENU
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                if len(event.unicode) > 0 and event.unicode.isalpha():
                    input_text += event.unicode.lower()

    if game_state == MENU:
        main_menu()
    elif game_state == DIFFICULTY_SELECT:
        difficulty_select()
    elif game_state == ABOUT:
        about_screen()
    elif game_state == GAME:
        game_screen()
    elif game_state == GAME_OVER:
        game_over_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()