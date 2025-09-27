import pygame
import random
import math
import time
import csv
import os
import pandas as pd

# Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тест на динамику мыши")
FPS = 60
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
TEAL = (0, 128, 128)
BROWN = (165, 42, 42)
COLORS = [RED, BLUE, GREEN, YELLOW, PURPLE, CYAN, ORANGE, PINK, TEAL, BROWN]

# Типы заданий
TASKS = ["shape_click", "path_follow", "color_click"]
TASK_TRANSLATE = {
    "shape_click": "клик по фигуре",
    "path_follow": "следование траектории",
    "color_click": "клик по цвету"
}
EVENT_TRANSLATE = {
    "move": "движение",
    "left_click_down": "нажатие левой кнопки",
    "left_click_up": "отпускание левой кнопки",
    "right_click_down": "нажатие правой кнопки",
    "right_click_up": "отпускание правой кнопки"
}
TASK_COUNT = {"shape_click": 19, "path_follow": 1, "color_click": 10}
current_task = 0
shape_click_count = 0
color_click_count = 0
task_number = 1
running = True

# Переменные для заданий
FIGURE_SIZE = 50
SHAPES = ["circle", "square", "triangle"]
current_shape = None
current_pos = (0, 0)
current_color = WHITE

# Для траектории
PATH_POINTS = [(100, 500), (200, 400), (300, 500), (400, 400), (500, 500), (600, 400), (700, 500)]
PATH_WIDTH = 30
path_progress = 0.0

# Цвета
COLOR_ZONES = []
TARGET_COLORS = COLORS.copy()
random.shuffle(TARGET_COLORS)
current_target_color_index = 0

# Данные для сбора
mouse_data = []
start_time = time.time()
player_name = ""
input_active = True
input_text = ""
data_path = r"C:\Users\Admin\Desktop\mouse_data"
session_number = 1

def color_name(color):
    """Цвет на русском"""
    color_map = {
        tuple(RED): "красный", tuple(BLUE): "синий", tuple(GREEN): "зелёный",
        tuple(YELLOW): "жёлтый", tuple(PURPLE): "пурпурный", tuple(CYAN): "голубой",
        tuple(ORANGE): "оранжевый", tuple(PINK): "розовый", tuple(TEAL): "бирюзовый",
        tuple(BROWN): "коричневый"
    }
    return color_map.get(tuple(color), "неизвестный")

def generate_new_shape():
    """Генерация новой фигуры"""
    global current_shape, current_pos, current_color
    current_shape = random.choice(SHAPES)
    current_pos = (
        random.randint(FIGURE_SIZE, WIDTH - FIGURE_SIZE),
        random.randint(FIGURE_SIZE, HEIGHT - FIGURE_SIZE)
    )
    current_color = random.choice(COLORS)

def draw_shape():
    """Отрисовка фигуры"""
    if current_shape == "circle":
        pygame.draw.circle(screen, current_color, current_pos, FIGURE_SIZE // 2)
    elif current_shape == "square":
        pygame.draw.rect(screen, current_color, 
                        (current_pos[0] - FIGURE_SIZE // 2, 
                         current_pos[1] - FIGURE_SIZE // 2, 
                         FIGURE_SIZE, FIGURE_SIZE))
    elif current_shape == "triangle":
        points = [
            (current_pos[0], current_pos[1] - FIGURE_SIZE // 2),
            (current_pos[0] - FIGURE_SIZE // 2, current_pos[1] + FIGURE_SIZE // 2),
            (current_pos[0] + FIGURE_SIZE // 2, current_pos[1] + FIGURE_SIZE // 2)
        ]
        pygame.draw.polygon(screen, current_color, points)
    font = pygame.font.SysFont("arial", 24)
    text = font.render(f"Задание {task_number}: Нажмите на фигуру", True, WHITE)
    screen.blit(text, (10, 50))

def is_click_on_shape(mouse_pos):
    """Клик внутри фигуры"""
    if not current_shape:
        return False
    x, y = mouse_pos
    cx, cy = current_pos
    if current_shape == "circle":
        distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        return distance <= FIGURE_SIZE // 2
    elif current_shape == "square":
        return (abs(x - cx) <= FIGURE_SIZE // 2 and 
                abs(y - cy) <= FIGURE_SIZE // 2)
    elif current_shape == "triangle":
        return (abs(x - cx) <= FIGURE_SIZE // 2 and 
                abs(y - cy) <= FIGURE_SIZE // 2)

def draw_path():
    """Отрисовывает траекторию"""
    for i in range(len(PATH_POINTS) - 1):
        pygame.draw.line(screen, WHITE, PATH_POINTS[i], PATH_POINTS[i + 1], PATH_WIDTH)
    font = pygame.font.SysFont("arial", 24)
    text = font.render(f"Прогресс: {path_progress * 100:.1f}%", True, WHITE)
    screen.blit(text, (10, 10))
    instruction = font.render(f"Задание {task_number}: Зажмите ЛКМ и проведите курсором по траектории", True, WHITE)
    screen.blit(instruction, (10, 50))

def check_path_follow(mouse_pos):
    """Проверка курсора на траектории"""
    global path_progress
    x, y = mouse_pos
    for i in range(len(PATH_POINTS) - 1):
        p1, p2 = PATH_POINTS[i], PATH_POINTS[i + 1]
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            continue
        t = max(0, min(1, ((x - p1[0]) * dx + (y - p1[1]) * dy) / (length**2)))
        proj_x = p1[0] + t * dx
        proj_y = p1[1] + t * dy
        distance = math.sqrt((x - proj_x)**2 + (y - proj_y)**2)
        if distance <= PATH_WIDTH // 2:
            path_progress = max(path_progress, (i + t) / (len(PATH_POINTS) - 1))
            if path_progress >= 0.95:
                path_progress = 1.0
                return True
    return False

def draw_color_zones():
    """Отрисовка цветов"""
    for zone in COLOR_ZONES:
        pygame.draw.rect(screen, zone["color"], zone["rect"])
    font = pygame.font.SysFont("arial", 24)
    target_color = TARGET_COLORS[current_target_color_index]
    instruction = font.render(f"Задание {task_number}: Нажмите на {color_name(target_color)} цвет", True, WHITE)
    screen.blit(instruction, (10, 50))

def generate_color_zones():
    """Генерация цветов"""
    global COLOR_ZONES, current_target_color_index
    COLOR_ZONES = []
    available_colors = COLORS.copy()
    target_color = TARGET_COLORS[current_target_color_index]
    if target_color not in available_colors:
        available_colors.append(target_color)
    random.shuffle(available_colors)
    selected_colors = available_colors[:8]
    if target_color not in selected_colors:
        selected_colors[random.randint(0, 7)] = target_color
    random.shuffle(selected_colors)
    for i in range(8):
        x = (i % 4) * 200
        y = (i // 4) * 300 + 100
        COLOR_ZONES.append({"color": selected_colors[i], "rect": (x, y, 200, 200)})

def check_color_click(mouse_pos):
    """Клик по цветной зоне"""
    global current_target_color_index, color_click_count
    target_color = TARGET_COLORS[current_target_color_index]
    for zone in COLOR_ZONES:
        x, y = mouse_pos
        if zone["rect"][0] <= x <= zone["rect"][0] + zone["rect"][2] and \
           zone["rect"][1] <= y <= zone["rect"][1] + zone["rect"][3]:
            if zone["color"] == target_color:
                current_target_color_index = (current_target_color_index + 1) % len(TARGET_COLORS)
                return True
    return False

def setup():
    """Счетчик задания"""
    global path_progress, color_click_count, current_target_color_index
    screen.fill(BLACK)
    path_progress = 0.0
    color_click_count = 0
    current_target_color_index = 0
    random.shuffle(TARGET_COLORS)
    if TASKS[current_task] == "shape_click":
        generate_new_shape()
        draw_shape()
    elif TASKS[current_task] == "path_follow":
        draw_path()
    elif TASKS[current_task] == "color_click":
        generate_color_zones()
        draw_color_zones()
    pygame.display.flip()

def display_completion():
    """Сообщение о завершении"""
    screen.fill(BLACK)
    font = pygame.font.SysFont("arial", 36)
    if session_number > 1:
        text = font.render(f"{session_number}-сессия завершена!", True, WHITE)
    else:
        text = font.render("Сессия завершена!", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

def get_next_session(filename):
    if not os.path.exists(filename):
        return 1
    try:
        df = pd.read_excel(filename)
        if 'Сессия' in df.columns:
            return df['Сессия'].max() + 1
        else:
            return 1
    except:
        return 1

def save_data():
    """Сохранение данных в Excel"""
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    filename = os.path.join(data_path, f"{player_name}_mouse_data.xlsx")
    df = pd.DataFrame(mouse_data, columns=['Сессия', 'Временная метка', 'X', 'Y', 'Событие', 'Тип задачи', 'Номер задачи'])
    
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_excel(filename, index=False)
    print(f"Данные сохранены в {filename}")

def draw_input_screen():
    screen.fill(BLACK)
    font = pygame.font.SysFont("arial", 36)
    prompt = font.render("Введите ваше ФИО:", True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 50))
    input_render = font.render(input_text, True, WHITE)
    screen.blit(input_render, (WIDTH // 2 - input_render.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

# Основной цикл
running = True
input_active = True
last_pos = (0, 0)
last_time = start_time

while running:
    current_time = time.time()
    mouse_pos = pygame.mouse.get_pos()
    task_type = TASKS[current_task] if current_task < len(TASKS) else "completed"

    # Логирование движения мыши каждый кадр, если изменилось
    if mouse_pos != last_pos:
        mouse_data.append([session_number, current_time - start_time, mouse_pos[0], mouse_pos[1], EVENT_TRANSLATE.get('move'), TASK_TRANSLATE.get(task_type), task_number])
        last_pos = mouse_pos
        last_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_name = input_text.strip()
                    if player_name:
                        filename = os.path.join(data_path, f"{player_name}_mouse_data.xlsx")
                        session_number = get_next_session(filename)
                        input_active = False
                        setup()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ down
                    mouse_data.append([session_number, current_time - start_time, mouse_pos[0], mouse_pos[1], EVENT_TRANSLATE.get('left_click_down'), TASK_TRANSLATE.get(task_type), task_number])
                elif event.button == 3:  # ПКМ down
                    mouse_data.append([session_number, current_time - start_time, mouse_pos[0], mouse_pos[1], EVENT_TRANSLATE.get('right_click_down'), TASK_TRANSLATE.get(task_type), task_number])
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # ЛКМ up
                    mouse_data.append([session_number, current_time - start_time, mouse_pos[0], mouse_pos[1], EVENT_TRANSLATE.get('left_click_up'), TASK_TRANSLATE.get(task_type), task_number])
                    if current_task < len(TASKS):
                        if TASKS[current_task] == "shape_click":
                            if is_click_on_shape(mouse_pos):
                                screen.fill(BLACK)
                                shape_click_count += 1
                                task_number += 1
                                if shape_click_count < TASK_COUNT["shape_click"]:
                                    generate_new_shape()
                                    draw_shape()
                                else:
                                    current_task += 1
                                    if current_task < len(TASKS):
                                        setup()
                                    else:
                                        display_completion()
                                        save_data()
                                        pygame.time.wait(3000)
                                        running = False
                                pygame.display.flip()
                        elif TASKS[current_task] == "color_click":
                            if check_color_click(mouse_pos):
                                color_click_count += 1
                                task_number += 1
                                screen.fill(BLACK)
                                if color_click_count < TASK_COUNT["color_click"]:
                                    generate_color_zones()
                                    draw_color_zones()
                                else:
                                    current_task += 1
                                    if current_task < len(TASKS):
                                        setup()
                                    else:
                                        display_completion()
                                        save_data()
                                        pygame.time.wait(3000)
                                        running = False
                                pygame.display.flip()
                elif event.button == 3:  # ПКМ up
                    mouse_data.append([session_number, current_time - start_time, mouse_pos[0], mouse_pos[1], EVENT_TRANSLATE.get('right_click_up'), TASK_TRANSLATE.get(task_type), task_number])

    if not input_active and current_task < len(TASKS) and TASKS[current_task] == "path_follow":
        if pygame.mouse.get_pressed()[0]:
            completed = check_path_follow(mouse_pos)
            if completed:
                screen.fill(BLACK)
                draw_path()
                pygame.display.flip()
                pygame.time.wait(500)
                task_number += 1
                current_task += 1
                if current_task < len(TASKS):
                    setup()
                else:
                    display_completion()
                    save_data()
                    pygame.time.wait(3000)
                    running = False
            else:
                screen.fill(BLACK)
                draw_path()
                pygame.display.flip()

    if input_active:
        draw_input_screen()

    clock.tick(FPS)

pygame.quit()