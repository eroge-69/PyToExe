import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()

# Получаем информацию о текущем экране
info = pygame.display.Info()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 768

# Создаем окно во весь экран
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Симулятор приборной панели")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 120, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
DARK_BLUE = (0, 80, 160)
METAL_COLOR = (180, 180, 200)
HANDLE_COLOR = (80, 80, 100)
BRIGHT_METAL = (200, 200, 220)
BEIGE = (245, 245, 220)
DARK_GREEN = (0, 100, 0)
LIGHT_GRAY = (200, 200, 200)

# Состояния элементов
current_screen = "menu"
contactor_mass = False
bcn_switch_position = 1
emzn_handle_position = 0
starter_button = False
gas_pedal_position = 0
pressure_value = 0.0
speed = 0
rpm = 0
engine_running = False
engine_stalling = False
stall_progress = 0.0
fuel_valve_position = 1
fuel_view_switch = 0
gear_position = 2
handbrake_on = False
shift_pressed = False
horn_pressed = False
pjd_motor_switch = 1  # 0-продув (низ), 1-выкл (центр), 2-работа (верх)
pjd_valve_switch = 0  # 0-продув (низ), 1-работа (верх)
pjd_glow_plug_switch = False  # Флажок свечи
pjd_glow_plug_active = False  # Контрольная лампа
pjd_glow_plug_timer = 0
pjd_glow_plug_duration = 0  # Таймер свечи (0-30 секунд)
pjd_operation_timer = 0
pjd_status = "ОТКЛЮЧЕН"
pjd_hum_detected = False
pjd_valve_timer = 0
pjd_start_timer = 0
pjd_start_phase = 0

# Система топливных баков
fuel_tanks = [random.randint(50, 350), random.randint(50, 350)]

# Коэффициенты масштабирования
scale_factor = min(SCREEN_WIDTH / 1200, SCREEN_HEIGHT / 800)

def scale_x(x):
    return int(x * SCREEN_WIDTH / 1200)

def scale_y(y):
    return int(y * SCREEN_HEIGHT / 800)

def scale_size(size):
    return int(size * scale_factor)

# Функция для рисования прямоугольной кнопки
def draw_button(x, y, width, height, text, is_pressed=False, color=GRAY, hover_color=LIGHT_BLUE, text_color=WHITE):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = x <= mouse_x <= x + width and y <= mouse_y <= y + height
    
    button_color = hover_color if is_hover else color
    if is_pressed:
        button_color = GREEN
    
    # Рисуем кнопку с более выраженными гранями
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), 0, scale_size(15))
    pygame.draw.rect(screen, button_color, (x + scale_size(2), y + scale_size(2), width - scale_size(4), height - scale_size(4)), 0, scale_size(15))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), scale_size(2), scale_size(15))
    
    font = pygame.font.SysFont('Arial', scale_size(24))
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height), is_hover

def draw_horn_button(x, y, radius, is_pressed):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    distance = math.sqrt((mouse_x - x)**2 + (mouse_y - y)**2)
    is_hover = distance <= radius
    
    button_color = LIGHT_BLUE if is_hover else RED
    if is_pressed:
        button_color = BRIGHT_METAL
    
    # Основа кнопки
    pygame.draw.circle(screen, DARK_GRAY, (x, y), radius + scale_size(2))
    pygame.draw.circle(screen, button_color, (x, y), radius)
    pygame.draw.circle(screen, WHITE, (x, y), radius, scale_size(2))
    
    # Иконка звукового сигнала (рожок)
    pygame.draw.circle(screen, BLACK, (x, y), scale_size(8))
    pygame.draw.arc(screen, BLACK, (x - scale_size(15), y - scale_size(15), 
                                  scale_size(30), scale_size(30)), 
                   math.radians(45), math.radians(135), scale_size(2))
    
    # Текст
    font = pygame.font.SysFont('Arial', scale_size(20))
    text_surface = font.render("Звуковой сигнал", True, YELLOW)
    text_rect = text_surface.get_rect(center=(x, y + scale_size(40)))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x - radius, y - radius, radius * 2, radius * 2), is_hover

# Функция для рисования круглой кнопки
def draw_round_button(x, y, radius, text, is_pressed=False, color=GRAY):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    distance = math.sqrt((mouse_x - x)**2 + (mouse_y - y)**2)
    is_hover = distance <= radius
    
    button_color = LIGHT_BLUE if is_hover else color
    if is_pressed:
        button_color = GREEN
    
    pygame.draw.circle(screen, DARK_GRAY, (x, y), radius + scale_size(2))
    pygame.draw.circle(screen, button_color, (x, y), radius)
    pygame.draw.circle(screen, WHITE, (x, y), radius, scale_size(2))
    
    font = pygame.font.SysFont('Arial', scale_size(16))
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x - radius, y - radius, radius * 2, radius * 2), is_hover

# Функция для рисования тумблера
def draw_toggle_switch(x, y, width, height, positions, current_position, text, vertical=False):
    # Основа тумблера
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), 0, scale_size(5))
    pygame.draw.rect(screen, BRIGHT_METAL, (x, y, width, height), scale_size(2), scale_size(5))
    
    if vertical:
        pos_height = height // positions
        for i in range(positions):
            pos_y = y + i * pos_height
            pygame.draw.rect(screen, GRAY, (x, pos_y, width, pos_height), scale_size(1))
        
        # Переключатель
        switch_y = y + current_position * pos_height + pos_height // 2
        pygame.draw.circle(screen, YELLOW, (x - scale_size(15), switch_y), scale_size(10))
        pygame.draw.rect(screen, YELLOW, (x - scale_size(15) - scale_size(5), switch_y - scale_size(5), scale_size(25), scale_size(10)))
    else:
        pos_width = width // positions
        for i in range(positions):
            pos_x = x + i * pos_width
            pygame.draw.rect(screen, GRAY, (pos_x, y, pos_width, height), scale_size(1))
        
        # Переключатель
        switch_x = x + current_position * pos_width + pos_width // 2
        pygame.draw.circle(screen, YELLOW, (switch_x, y - scale_size(15)), scale_size(10))
        pygame.draw.rect(screen, YELLOW, (switch_x - scale_size(5), y - scale_size(15), scale_size(10), scale_size(25)))
    
    # Текст
    font = pygame.font.SysFont('Arial', scale_size(16))
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width//2, y - scale_size(20)))
    screen.blit(text_surface, text_rect)
    
    # Возвращаем область для клика
    click_areas = []
    if vertical:
        for i in range(positions):
            click_areas.append(pygame.Rect(x - scale_size(30), y + i * pos_height, scale_size(60), pos_height))
    else:
        for i in range(positions):
            click_areas.append(pygame.Rect(x + i * pos_width, y, pos_width, height))
    
    return click_areas

# Функция для рисования педали газа
def draw_gas_pedal(x, y, width, height, position, text):
    # Основа педали
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), 0, scale_size(10))
    pygame.draw.rect(screen, BRIGHT_METAL, (x, y, width, height), scale_size(2), scale_size(10))
    
    # Положение педали (0-100%)
    pedal_height = scale_size(30)
    pedal_y = y + height - scale_size(10) - (position / 100) * (height - scale_size(20))
    
    # Сама педаль
    pedal_color = RED if position > 0 else GRAY
    pygame.draw.rect(screen, pedal_color, (x + scale_size(10), pedal_y - pedal_height//2, 
                                         width - scale_size(20), pedal_height), 0, scale_size(5))
    
    # Текст
    font = pygame.font.SysFont('Arial', scale_size(16))
    text_surface = font.render(f"{text}: {position}%", True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width//2, y - scale_size(20)))
    screen.blit(text_surface, text_rect)
    
    # Подсказка управления
    control_font = pygame.font.SysFont('Arial', scale_size(12))
    control_text = control_font.render("Регулировка - Колесико мыши", True, YELLOW)
    control_rect = control_text.get_rect(center=(x + width//2, y + height + scale_size(15)))
    screen.blit(control_text, control_rect)
    
    return pygame.Rect(x, y, width, height)

# Функция для рисования рукоятки ЭМЗН
def draw_emzn_handle(x, y, size, position, text):
    # Основание рукоятки
    base_width = scale_size(size)
    base_height = scale_size(size * 0.8)
    pygame.draw.rect(screen, BRIGHT_METAL, (x - base_width//2, y - base_height//2, base_width, base_height), 0, scale_size(5))
    pygame.draw.rect(screen, DARK_GRAY, (x - base_width//2, y - base_height//2, base_width, base_height), scale_size(2), scale_size(5))
    
    # Шарнир
    hinge_radius = scale_size(8)
    pygame.draw.circle(screen, BRIGHT_METAL, (x, y), hinge_radius)
    pygame.draw.circle(screen, DARK_GRAY, (x, y), hinge_radius, scale_size(2))
    
    # Рукоятка
    handle_length = scale_size(size * 1.5)
    handle_width = scale_size(size * 0.3)
    
    if position == 0:  # Выкл - рукоятка опущена вниз
        angle = math.radians(90)
        handle_color = GRAY
    else:  # Вкл - рукоятка повернута влево
        angle = math.radians(180)
        handle_color = GREEN
    
    # Рисуем рукоятку
    end_x = x + handle_length * math.cos(angle)
    end_y = y + handle_length * math.sin(angle)
    
    # Основная часть рукоятки
    pygame.draw.line(screen, handle_color, (x, y), (end_x, end_y), handle_width)
    
    # Ручка на конце
    grip_radius = scale_size(6)
    pygame.draw.circle(screen, HANDLE_COLOR, (int(end_x), int(end_y)), grip_radius)
    pygame.draw.circle(screen, DARK_GRAY, (int(end_x), int(end_y)), grip_radius, scale_size(1))
    
    # Текст состояния
    font = pygame.font.SysFont('Arial', scale_size(20))
    status_text = "ВКЛ" if position == 1 else "ВЫКЛ"
    status_color = GREEN if position == 1 else RED
    text_surface = font.render(f"{text}: {status_text}", True, status_color)
    text_rect = text_surface.get_rect(center=(x, y + scale_size(40)))
    screen.blit(text_surface, text_rect)
    
    # Подсказка управления
    control_font = pygame.font.SysFont('Arial', scale_size(16))
    control_text = control_font.render("7 - ВКЛ, 8 - ВЫКЛ", True, YELLOW)
    control_rect = control_text.get_rect(center=(x, y + scale_size(70)))
    screen.blit(control_text, control_rect)
    
    return text_rect

def draw_gearbox(x, y, radius, position):
    # Основа коробки (полукруг справа)
    pygame.draw.arc(screen, DARK_GRAY, (x - radius, y - radius, radius * 2, radius * 2), 
                   math.radians(-90), math.radians(90), scale_size(20))
    pygame.draw.arc(screen, BRIGHT_METAL, (x - radius, y - radius, radius * 2, radius * 2), 
                   math.radians(-90), math.radians(90), scale_size(2))
    
    # Позиции передач по полукругу (-90 до 90 градусов)
    gear_positions = {
        0: ("ЗХ", math.radians(-90)),    # Правая нижняя
        1: ("Н", math.radians(-60)),     # Правая середина-низ
        2: ("1", math.radians(-30)),     # Правая середина
        3: ("2", math.radians(0)),       # Центр
        4: ("3", math.radians(30)),      # Левая середина
        5: ("Н", math.radians(60))       # Левая середина-верх
    }
    
    # Рисуем позиции передач
    for gear, (text, angle) in gear_positions.items():
        pos_x = x + (radius - scale_size(30)) * math.cos(angle)
        pos_y = y + (radius - scale_size(30)) * math.sin(angle)
        
        color = GREEN if gear == position else GRAY
        pygame.draw.circle(screen, color, (int(pos_x), int(pos_y)), scale_size(12))
        pygame.draw.circle(screen, WHITE, (int(pos_x), int(pos_y)), scale_size(12), scale_size(1))
        
        font = pygame.font.SysFont('Arial', scale_size(14))
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(int(pos_x), int(pos_y)))
        screen.blit(text_surface, text_rect)
    
    # Рычаг переключения
    current_angle = gear_positions[position][1]
    lever_x = x + (radius - scale_size(15)) * math.cos(current_angle)
    lever_y = y + (radius - scale_size(15)) * math.sin(current_angle)
    
    pygame.draw.line(screen, YELLOW, (x, y), (lever_x, lever_y), scale_size(3))
    pygame.draw.circle(screen, YELLOW, (int(lever_x), int(lever_y)), scale_size(6))
    
    # Название
    title_font = pygame.font.SysFont('Arial', scale_size(16))
    title_text = title_font.render("КПП", True, WHITE)
    title_rect = title_text.get_rect(center=(x, y - radius - scale_size(20)))
    screen.blit(title_text, title_rect)
    
    # Возвращаем области для клика
    click_areas = {}
    for gear, (text, angle) in gear_positions.items():
        pos_x = x + (radius - scale_size(30)) * math.cos(angle)
        pos_y = y + (radius - scale_size(30)) * math.sin(angle)
        click_areas[gear] = pygame.Rect(pos_x - scale_size(15), pos_y - scale_size(15), 
                                      scale_size(30), scale_size(30))
    
    return click_areas
    
    # Рычаг переключения (вертикальный)
    current_x, current_y = gear_positions[position][1], gear_positions[position][2]
    pygame.draw.line(screen, YELLOW, (x + width//2, y + height//2), (current_x, current_y), scale_size(3))
    pygame.draw.circle(screen, YELLOW, (current_x, current_y), scale_size(6))
    
    # Название
    title_font = pygame.font.SysFont('Arial', scale_size(16))
    title_text = title_font.render("КПП", True, WHITE)
    title_rect = title_text.get_rect(center=(x + width//2, y - scale_size(20)))
    screen.blit(title_text, title_rect)
    
    # Возвращаем области для клика
    click_areas = {}
    for gear, (_, pos_x, pos_y) in gear_positions.items():
        click_areas[gear] = pygame.Rect(pos_x - scale_size(15), pos_y - scale_size(15), scale_size(30), scale_size(30))
    
    return click_areas

# Функция для рисования ручника
def draw_handbrake(x, y, width, height, is_on):
    # Основа ручника
    pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), 0, scale_size(5))
    pygame.draw.rect(screen, BRIGHT_METAL, (x, y, width, height), scale_size(2), scale_size(5))
    
    # Ручка
    handle_color = RED if is_on else GREEN
    handle_height = scale_size(30)
    handle_y = y + scale_size(10) if is_on else y + height - scale_size(10) - handle_height
    
    pygame.draw.rect(screen, handle_color, (x + scale_size(5), handle_y, width - scale_size(10), handle_height), 0, scale_size(3))
    
    # Текст
    font = pygame.font.SysFont('Arial', scale_size(16))
    status_text = "ВКЛ" if is_on else "ВЫКЛ"
    text_surface = font.render(f"РУЧНИК: {status_text}", True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width//2, y - scale_size(20)))
    screen.blit(text_surface, text_rect)
    
    # Подсказка управления
    control_font = pygame.font.SysFont('Arial', scale_size(12))
    control_text = control_font.render("H - переключить", True, YELLOW)
    control_rect = control_text.get_rect(center=(x + width//2, y + height + scale_size(15)))
    screen.blit(control_text, control_rect)
    
    return pygame.Rect(x, y, width, height)

# Функция для рисования спидометра или тахометра
def draw_gauge(x, y, radius, value, max_value, text, unit, is_tachometer=False):
    pygame.draw.circle(screen, DARK_GRAY, (x, y), radius)
    pygame.draw.circle(screen, BRIGHT_METAL, (x, y), radius, scale_size(3))
    
    start_angle = 135
    end_angle = 405
    
    for i in range(13):
        angle = math.radians(start_angle + i * 22.5)
        start_x = x + (radius - scale_size(20)) * math.cos(angle)
        start_y = y + (radius - scale_size(20)) * math.sin(angle)
        end_x = x + (radius - scale_size(5)) * math.cos(angle)
        end_y = y + (radius - scale_size(5)) * math.sin(angle)
        pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), scale_size(2))
        
        if i % 2 == 0:
            display_value = i * (max_value // 12)
            num_font = pygame.font.SysFont('Arial', scale_size(16))
            num_text = num_font.render(f"{display_value}", True, WHITE)
            num_x = x + (radius - scale_size(30)) * math.cos(angle) - num_text.get_width()//2
            num_y = y + (radius - scale_size(35)) * math.sin(angle) - num_text.get_height()//2
            screen.blit(num_text, (num_x, num_y))
    
    if is_tachometer and value > 6000:
        danger_angle = math.radians(start_angle + (value / max_value) * 270)
        danger_x = x + (radius - scale_size(10)) * math.cos(danger_angle)
        danger_y = y + (radius - scale_size(10)) * math.sin(danger_angle)
        pygame.draw.circle(screen, RED, (danger_x, danger_y), scale_size(8))
    
    angle = math.radians(start_angle + (value / max_value) * 270)
    end_x = x + (radius - scale_size(15)) * math.cos(angle)
    end_y = y + (radius - scale_size(15)) * math.sin(angle)
    pygame.draw.line(screen, RED, (x, y), (end_x, end_y), scale_size(4))
    pygame.draw.circle(screen, RED, (x, y), scale_size(6))
    
    font = pygame.font.SysFont('Arial', scale_size(24))
    value_text = font.render(f"{value:.0f} {unit}", True, GREEN if value < max_value * 0.8 else RED)
    value_rect = value_text.get_rect(center=(x, y + radius + scale_size(30)))
    screen.blit(value_text, value_rect)
    
    title_font = pygame.font.SysFont('Arial', scale_size(28))
    title_text = title_font.render(text, True, WHITE)
    title_rect = title_text.get_rect(center=(x, y - radius - scale_size(25)))
    screen.blit(title_text, title_rect)
    return title_rect


# Функция для рисования указателя уровня топлива
def draw_fuel_gauge(x, y, radius, value, max_value, text):
    pygame.draw.circle(screen, DARK_GRAY, (x, y), radius)
    pygame.draw.circle(screen, BRIGHT_METAL, (x, y), radius, scale_size(3))
    
    start_angle = 180
    end_angle = 360
    
    for i in range(11):
        angle = math.radians(start_angle + i * 18)
        start_x = x + (radius - scale_size(20)) * math.cos(angle)
        start_y = y + (radius - scale_size(20)) * math.sin(angle)
        end_x = x + (radius - scale_size(5)) * math.cos(angle)
        end_y = y + (radius - scale_size(5)) * math.sin(angle)
        pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), scale_size(2))
        
        if i % 2 == 0:
            display_value = i * (max_value // 10)
            num_font = pygame.font.SysFont('Arial', scale_size(18))
            num_text = num_font.render(f"{display_value}", True, WHITE)
            num_x = x + (radius - scale_size(35)) * math.cos(angle) - num_text.get_width()//2
            num_y = y + (radius - scale_size(35)) * math.sin(angle) - num_text.get_height()//2
            screen.blit(num_text, (num_x, num_y))
    
    angle = math.radians(start_angle + (value / max_value) * 180)
    end_x = x + (radius - scale_size(15)) * math.cos(angle)
    end_y = y + (radius - scale_size(15)) * math.sin(angle)
    pygame.draw.line(screen, BLUE, (x, y), (end_x, end_y), scale_size(4))
    pygame.draw.circle(screen, BLUE, (x, y), scale_size(6))
    
    font = pygame.font.SysFont('Arial', scale_size(24))
    value_text = font.render(f"{value:.0f} л", True, BLUE)
    value_rect = value_text.get_rect(center=(x, y + radius + scale_size(30)))
    screen.blit(value_text, value_rect)
    
    title_font = pygame.font.SysFont('Arial', scale_size(28))
    title_text = title_font.render(text, True, WHITE)
    title_rect = title_text.get_rect(center=(x, y - radius - scale_size(25)))
    screen.blit(title_text, title_rect)
    
    info_font = pygame.font.SysFont('Arial', scale_size(16))
    tank_text = info_font.render(f"Бак: {'Левый' if fuel_view_switch == 0 else 'Правый'}", True, YELLOW)
    tank_rect = tank_text.get_rect(center=(x, y + radius + scale_size(55)))
    screen.blit(tank_text, tank_rect)
    
    return title_rect

# Функция для рисования манометра
def draw_pressure_gauge(x, y, radius, value, max_value, text):
    pygame.draw.circle(screen, DARK_GRAY, (x, y), radius)
    pygame.draw.circle(screen, BRIGHT_METAL, (x, y), radius, scale_size(3))
    
    for i in range(6):
        angle = math.radians(30 + i * 30)
        start_x = x + (radius - scale_size(20)) * math.cos(angle)
        start_y = y + (radius - scale_size(20)) * math.sin(angle)
        end_x = x + (radius - scale_size(5)) * math.cos(angle)
        end_y = y + (radius - scale_size(5)) * math.sin(angle)
        pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), scale_size(2))
        
        num_font = pygame.font.SysFont('Arial', scale_size(18))
        num_text = num_font.render(f"{i * 0.5}", True, WHITE)
        num_x = x + (radius - scale_size(30)) * math.cos(angle) - num_text.get_width()//2
        num_y = y + (radius - scale_size(30)) * math.sin(angle) - num_text.get_height()//2
        screen.blit(num_text, (num_x, num_y))
    
    angle = math.radians(30 + (value / max_value) * 150)
    end_x = x + (radius - scale_size(15)) * math.cos(angle)
    end_y = y + (radius - scale_size(15)) * math.sin(angle)
    pygame.draw.line(screen, RED, (x, y), (end_x, end_y), scale_size(3))
    pygame.draw.circle(screen, RED, (x, y), scale_size(5))
    
    font = pygame.font.SysFont('Arial', scale_size(20))
    value_text = font.render(f"{value:.1f} кгс/см²", True, GREEN)
    value_rect = value_text.get_rect(center=(x, y + radius + scale_size(20)))
    screen.blit(value_text, value_rect)
    
    title_font = pygame.font.SysFont('Arial', scale_size(24))
    title_text = title_font.render(text, True, WHITE)
    title_rect = title_text.get_rect(center=(x, y - radius - scale_size(20)))
    screen.blit(title_text, title_rect)
    return title_rect

# Функция для рисования текста
def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont('Arial', scale_size(size))
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect

# Функция для отрисовки главного меню
def draw_main_menu():
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, DARK_GRAY, (scale_x(400), scale_y(250), scale_x(400), scale_y(350)), 0, scale_size(20))
    pygame.draw.rect(screen, GRAY, (scale_x(400), scale_y(250), scale_x(400), scale_y(350)), scale_size(3), scale_size(20))
    
    draw_text("СИМУЛЯТОР ПРИБОРНОЙ ПАНЕЛИ", 36, SCREEN_WIDTH//2, scale_y(150), LIGHT_BLUE)
    
    btn_width, btn_height = scale_x(300), scale_y(60)
    dashboard_btn, dashboard_hover = draw_button(
        SCREEN_WIDTH//2 - btn_width//2, scale_y(320), 
        btn_width, btn_height, 
        "СИМУЛЯТОР ПАНЕЛИ", False, BLUE
    )
    pjd_btn, pjd_hover = draw_button(
        SCREEN_WIDTH//2 - btn_width//2, scale_y(400), 
        btn_width, btn_height, 
        "СИМУЛЯТОР ПЖД", False, GREEN
    )
    exit_btn, exit_hover = draw_button(
        SCREEN_WIDTH//2 - btn_width//2, scale_y(480), 
        btn_width, btn_height, 
        "ВЫХОД", False, RED
    )
    
    draw_text("Выберите режим симуляции", 24, SCREEN_WIDTH//2, scale_y(580), YELLOW)
    
    return dashboard_btn, pjd_btn, exit_btn, dashboard_hover, pjd_hover, exit_hover

def draw_pjd_screen():
    global pjd_glow_plug_active, pjd_glow_plug_timer, pjd_operation_timer, pjd_status, pjd_hum_detected
    global pjd_motor_switch, pjd_valve_switch, pjd_glow_plug_switch, pjd_glow_plug_duration
    global pjd_valve_timer, pjd_start_timer, pjd_start_phase
    
    # Обновление таймеров
    if pjd_motor_switch == 2:  # Если электродвигатель в положении "работа"
        pjd_operation_timer += 1
        
        # Автоматическое отключение через 10 секунд
        if pjd_operation_timer > 600:  # 10 секунд
            pjd_motor_switch = 1
            pjd_operation_timer = 0
            pjd_status = "ПРОДУВ ЗАВЕРШЕН"
    
    if pjd_glow_plug_switch:
        pjd_glow_plug_timer += 1
        pjd_glow_plug_duration = min(1800, pjd_glow_plug_duration + 1)  # Максимум 30 секунд
        
        # Активация свечи через 1 секунду
        if pjd_glow_plug_timer > 60:  # 1 секунда
            pjd_glow_plug_active = True
            
        # Когда лампа становится ярко-красной (после 15 секунд), разрешаем следующий этап
        if pjd_glow_plug_duration > 900 and pjd_start_phase == 0:  # 15 секунд
            pjd_start_phase = 1
            pjd_status = "ВКЛЮЧИТЕ КЛАПАН"
    
    # Таймер для электромагнитного клапана (3 секунды после включения)
    if pjd_valve_switch == 1 and pjd_start_phase == 1:
        pjd_valve_timer += 1
        if pjd_valve_timer > 180:  # 3 секунды
            pjd_start_phase = 2
            pjd_status = "ВКЛЮЧИТЕ ДВИГАТЕЛЬ"
    
    # Таймер для запуска двигателя (после включения двигателя)
    if pjd_motor_switch == 2 and pjd_start_phase == 2:
        pjd_start_timer += 1
        if pjd_start_timer > 60:  # 1 секунда
            pjd_hum_detected = True
            pjd_status = "ГУЛ"
            pjd_start_phase = 3
    
    # Автоматическое возвращение флажка свечи
    if pjd_glow_plug_timer > 20 and not pjd_glow_plug_switch:  # Автоматическое выключение
        pjd_glow_plug_active = False
        pjd_glow_plug_timer = 0
        pjd_glow_plug_duration = 0
        pjd_start_phase = 0
    
    # Фон
    screen.fill(DARK_BLUE)
    pygame.draw.rect(screen, DARK_GRAY, (scale_x(100), scale_y(100), 
                                       SCREEN_WIDTH-scale_x(200), SCREEN_HEIGHT-scale_y(200)), 0, scale_size(20))
    pygame.draw.rect(screen, GRAY, (scale_x(100), scale_y(100), 
                                  SCREEN_WIDTH-scale_x(200), SCREEN_HEIGHT-scale_y(200)), scale_size(3), scale_size(20))
    
    # Заголовок
    draw_text("ПУЛЬТ УПРАВЛЕНИЯ ПОДОГРЕВАТЕЛЕМ", 36, SCREEN_WIDTH//2, scale_y(150), LIGHT_BLUE)
    
    # 1. Переключатель электродвигателя (вертикальный)
    motor_x, motor_y = scale_x(400), scale_y(300)
    motor_areas = draw_toggle_switch(motor_x, motor_y, scale_size(80), scale_size(120), 
                                    3, pjd_motor_switch, "ЭЛЕКТРОДВИГАТЕЛЬ", True)
    draw_text("0-Продув 1-Выкл 2-Пуск", 16, motor_x, motor_y + scale_size(80), YELLOW)
    
    # 2. Переключатель электромагнитного клапана (вертикальный)
    valve_x, valve_y = scale_x(600), scale_y(300)
    valve_areas = draw_toggle_switch(valve_x, valve_y, scale_size(80), scale_size(80), 
                                    2, pjd_valve_switch, "ЭЛЕКТРОМАГНИТНЫЙ КЛАПАН", True)
    draw_text("0-Продув 1-Работа", 16, valve_x, valve_y + scale_size(60), YELLOW)
    
    # 3. Флажок свечи зажигания
    glow_x, glow_y = scale_x(800), scale_y(300)
    glow_rect = pygame.Rect(glow_x - scale_size(40), glow_y - scale_size(20), scale_size(80), scale_size(40))
    
    # Рисуем флажок
    glow_color = ORANGE if pjd_glow_plug_switch else GRAY
    pygame.draw.rect(screen, DARK_GRAY, glow_rect, 0, scale_size(5))
    pygame.draw.rect(screen, glow_color, (glow_x - scale_size(35), glow_y - scale_size(15), 
                                        scale_size(70), scale_size(30)), 0, scale_size(3))
    
    # Ручка флажка
    handle_x = glow_x + scale_size(25) if pjd_glow_plug_switch else glow_x - scale_size(25)
    pygame.draw.circle(screen, YELLOW, (handle_x, glow_y), scale_size(8))
    
    draw_text("СВЕЧА ЗАЖИГАНИЯ", 16, glow_x, glow_y - scale_size(30), WHITE)
    draw_text("← повернуть", 14, glow_x, glow_y + scale_size(30), YELLOW)
    
    # 4. Контрольная лампа свечи накаливания с постепенным изменением цвета
    lamp_x, lamp_y = scale_x(800), scale_y(400)
    
    # Расчет цвета лампы (от серого до ярко-красного)
    progress = min(1.0, pjd_glow_plug_duration / 1800)  # 0-30 секунд
    lamp_red = int(255 * progress)
    lamp_color = (lamp_red, 0, 0) if pjd_glow_plug_active else GRAY
    
    pygame.draw.circle(screen, lamp_color, (lamp_x, lamp_y), scale_size(15))
    pygame.draw.circle(screen, WHITE, (lamp_x, lamp_y), scale_size(15), scale_size(2))
    draw_text("КОНТРОЛЬНАЯ ЛАМПА", 16, lamp_x, lamp_y + scale_size(30), WHITE)
    
    # Таймер свечи
    if pjd_glow_plug_active:
        seconds = pjd_glow_plug_duration // 60
        draw_text(f"{seconds}/30 сек", 14, lamp_x, lamp_y + scale_size(50), YELLOW)
    
    # 5. Таймеры этапов запуска
    if pjd_start_phase == 1:  # Ожидание включения клапана
        draw_text("ВКЛЮЧИТЕ КЛАПАН →", 20, SCREEN_WIDTH//2, scale_y(450), ORANGE)
    
    elif pjd_start_phase == 2:  # Таймер клапана
        valve_seconds = 3 - (pjd_valve_timer // 60)
        draw_text(f"ЖДЕМ {valve_seconds} сек...", 20, SCREEN_WIDTH//2, scale_y(450), YELLOW)
        draw_text("ПОДГОТОВКА К ПУСКУ", 18, SCREEN_WIDTH//2, scale_y(480), YELLOW)
    
    elif pjd_start_phase == 3:  # Запуск двигателя
        draw_text("ЗАПУСК ВЫПОЛНЕН", 20, SCREEN_WIDTH//2, scale_y(450), GREEN)
    
    # 6. Статус системы
    status_color = GREEN if "ГУЛ" in pjd_status else YELLOW
    draw_text(f"СТАТУС: {pjd_status}", 28, SCREEN_WIDTH//2, scale_y(500), status_color)
    
    # 7. Инструкция
    instructions = [
        "АЛГОРИТМ ЗАПУСКА:",
        "1. Включить свечу зажигания (ждать красную лампу)",
        "2. Электромагнитный клапан: Работа (ждем 3 сек)",
        "3. Электродвигатель: Пуск",
        "4. Дождаться появления 'ГУЛ'",
        "5. Отпустить флажок свечи",
        "",
        "ОТКЛЮЧЕНИЕ:",
        "1. Электромагнитный клапан: Продув",
        "2. Через 15-20 сек Электродвигатель: Продув"
    ]
    
    for i, text in enumerate(instructions):
        draw_text(text, 18, SCREEN_WIDTH//2, scale_y(550) + i * scale_size(25), LIGHT_BLUE)
    
    # 8. Кнопка назад
    back_btn, back_hover = draw_button(SCREEN_WIDTH//2 - scale_x(100), scale_y(650), 
                                      scale_x(200), scale_size(50), "НАЗАД", False, RED)
    
    return motor_areas, valve_areas, glow_rect, back_btn, back_hover

# Функция для отрисовки приборной панели
def draw_dashboard():
    global speed, rpm, pressure_value, engine_running, fuel_tanks
    global engine_stalling, stall_progress, gas_pedal_position
    
    # Обновление давления
    if engine_running:
        pressure_value = 2.5
    else:
        if emzn_handle_position == 1:
            pressure_value = min(2.5, pressure_value + 0.02)
        else:
            pressure_value = max(0.0, pressure_value - 0.05)
    
    # Проверка условий запуска двигателя
    if (emzn_handle_position == 1 and starter_button and 
        contactor_mass and bcn_switch_position != 1 and gas_pedal_position > 0 and 
        not engine_running and not engine_stalling):
        engine_running = True
        rpm = 700 + gas_pedal_position * 13
    
    # Проверка условий заглушения двигателя
    if engine_running and (gas_pedal_position <= 0 or rpm < 300) and not engine_stalling:
        engine_stalling = True
        stall_progress = 0.0
    
    # Плавное заглушение двигателя
    if engine_stalling:
        stall_progress += 0.01
        rpm = max(0, rpm - 50 * stall_progress)
        if rpm <= 0:
            engine_running = False
            engine_stalling = False
            gas_pedal_position = 0
    
    # Обновление скорости и оборотов
    if engine_running and not engine_stalling and not handbrake_on:
        base_rpm = 700 + gas_pedal_position * 13
        if gear_position == 1 or gear_position == 5:  # Обе нейтрали
            rpm = base_rpm
            speed = max(0, speed - 0.5)
        elif gear_position >= 2 and gear_position <= 4:  # Скорости 1-3
            target_rpm = base_rpm + 2000
            rpm = min(target_rpm, rpm + 20)
            gear_multiplier = [0, 0, 0.5, 0.8, 1.0, 0][gear_position]  # Добавлен 0 для 5-й позиции
            speed = min(60 * gear_multiplier, speed + 0.5 * gear_multiplier)
        elif gear_position == 0:  # Задний ход
            rpm = base_rpm
            speed = max(-20, speed - 0.3)
        
        # Расход топлива
        if bcn_switch_position == 0:  # Левый бак
            fuel_tanks[0] = max(0, fuel_tanks[0] - 0.1 * (gas_pedal_position / 100 + 0.1))
        elif bcn_switch_position == 2:  # Правый бак
            fuel_tanks[1] = max(0, fuel_tanks[1] - 0.1 * (gas_pedal_position / 100 + 0.1))
    else:
        speed = max(0, speed - 0.5)
        if not engine_stalling:
            rpm = max(0, rpm - 20)
    
    # Очистка экрана
    screen.fill(BLACK)
    
    # Рисуем фон приборной панели
    pygame.draw.rect(screen, DARK_GRAY, (scale_x(20), scale_y(20), SCREEN_WIDTH-scale_x(40), SCREEN_HEIGHT-scale_y(40)), 0, scale_size(15))
    pygame.draw.rect(screen, GRAY, (scale_x(20), scale_y(20), SCREEN_WIDTH-scale_x(40), SCREEN_HEIGHT-scale_y(40)), scale_size(3), scale_size(15))
    
    # Заголовок
    draw_text("ПРИБОРНАЯ ПАНЕЛЬ", 40, SCREEN_WIDTH//2, scale_y(50), LIGHT_BLUE)
    
    # 1. Спидометр
    draw_gauge(scale_x(200), scale_y(200), scale_size(60), abs(speed), 60, "СПИДОМЕТР", "км/ч")
    
    # 2. Тахометр
    draw_gauge(scale_x(400), scale_y(200), scale_size(60), rpm, 8000, "ТАХОМЕТР", "об/м", True)
    
    # 3. Тумблер массы
    mass_toggle = draw_toggle_switch(scale_x(650), scale_y(150), scale_size(80), scale_size(40), 2, 1 if contactor_mass else 0, "МАССА")
    draw_text("M - переключить", 16, scale_x(690), scale_y(210), YELLOW)
    
    # 4. Тумблер БЦН (3 положения)
    bcn_toggle = draw_toggle_switch(scale_x(750), scale_y(150), scale_size(120), scale_size(40), 3, bcn_switch_position, "БЦН")
    draw_text("B - переключить", 16, scale_x(810), scale_y(210), YELLOW)
    
    # 5. Педаль газа
    gas_pedal = draw_gas_pedal(scale_x(900), scale_y(150), scale_size(80), scale_size(120), gas_pedal_position, "ГАЗ")
    
    # 6. Топливораспределительный кран
    fuel_valve_toggle = draw_toggle_switch(scale_x(1050), scale_y(150), scale_size(120), scale_size(40), 3, fuel_valve_position, "ТОПЛИВНЫЙ КРАН")
    draw_text("V - переключить", 16, scale_x(1110), scale_y(210), YELLOW)
    
    # 7. Тумблер просмотра топлива
    fuel_view_toggle = draw_toggle_switch(scale_x(650), scale_y(250), scale_size(120), scale_size(40), 2, fuel_view_switch, "ПРОСМОТР ТОПЛИВА")
    draw_text("F - переключить", 16, scale_x(710), scale_y(310), YELLOW)
    
    # 8. Указатель уровня топлива
    current_fuel = fuel_tanks[fuel_view_switch]
    draw_fuel_gauge(scale_x(400), scale_y(400), scale_size(60), current_fuel, 350, "ТОПЛИВО")

    # 6. Рукоятка ЭМЗН
    draw_emzn_handle(scale_x(430), scale_y(640), 40, emzn_handle_position, "ЭМЗН")
    
    # 9. Манометр
    draw_pressure_gauge(scale_x(200), scale_y(400), scale_size(60), pressure_value, 2.5, "ДАВЛЕНИЕ")
    
    # 11. Круглая кнопка стартера
    starter_button_rect, starter_hover = draw_round_button(scale_x(800), scale_y(400), scale_size(30), "СТАРТ", starter_button, GREEN if starter_button else RED)
    draw_text("S - нажать", 16, scale_x(800), scale_y(470), YELLOW)

    # 12.коробка передач
    gearbox_areas = draw_gearbox(scale_x(1100), scale_y(550), scale_size(80), gear_position)
    draw_text("1-6 - переключение", 14, scale_x(1100), scale_y(670), YELLOW)
    draw_text("1- Задний Ход", 14, scale_x(1100), scale_y(350), YELLOW)
    draw_text("2- Нейтральная", 14, scale_x(1100), scale_y(365), YELLOW)
    draw_text("3- 1 передача", 14, scale_x(1100), scale_y(380), YELLOW)
    draw_text("4- 2 передача", 14, scale_x(1100), scale_y(395), YELLOW)
    draw_text("5- 3 передача", 14, scale_x(1100), scale_y(410), YELLOW)
    draw_text("6- Нейтральная", 14, scale_x(1100), scale_y(425), YELLOW)

    # Кнопка звукового сигнала
    horn_button, horn_hover = draw_horn_button(scale_x(1000), scale_y(700), scale_size(30), horn_pressed)
    
    # 14. Ручник
    handbrake_rect = draw_handbrake(scale_x(900), scale_y(500), scale_size(100), scale_size(60), handbrake_on)
    
    # Индикатор двигателя
    engine_x, engine_y = scale_x(650), scale_y(400)
    engine_color = GREEN if engine_running else RED
    pygame.draw.circle(screen, engine_color, (engine_x, engine_y), scale_size(15))
    pygame.draw.circle(screen, WHITE, (engine_x, engine_y), scale_size(15), scale_size(2))
    
    engine_font = pygame.font.SysFont('Arial', scale_size(16))
    engine_text = engine_font.render("ДВИГАТЕЛЬ", True, WHITE)
    engine_text_rect = engine_text.get_rect(center=(engine_x, engine_y + scale_size(30)))
    screen.blit(engine_text, engine_text_rect)
    
    engine_status_text = "ЗАПУЩЕН" if engine_running else "ЗАГЛУШЕН"
    if engine_stalling:
        engine_status_text = "ГЛОХНЕТ"
    engine_status = engine_font.render(engine_status_text, True, engine_color)
    engine_status_rect = engine_status.get_rect(center=(engine_x, engine_y + scale_size(55)))
    screen.blit(engine_status, engine_status_rect)
    
    
    # Кнопка назад
    back_button, back_hover = draw_round_button(SCREEN_WIDTH - scale_x(50), SCREEN_HEIGHT - scale_y(50), scale_size(30), "←", False, RED)
    
    return (mass_toggle, bcn_toggle, gas_pedal, fuel_valve_toggle, 
            fuel_view_toggle, starter_button_rect, gearbox_areas, 
            handbrake_rect, back_button, starter_hover, back_hover)
    
# Основной цикл
clock = pygame.time.Clock()
running = True

# Области для клика
mass_toggle_areas = []
bcn_toggle_areas = []
fuel_valve_toggle_areas = []
fuel_view_toggle_areas = []
gearbox_areas = {}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_pos = pygame.mouse.get_pos()
                
                if current_screen == "menu":
                    dashboard_btn, pjd_btn, exit_btn, dashboard_hover, pjd_hover, exit_hover = draw_main_menu()
                    if dashboard_hover:
                        current_screen = "dashboard"
                    elif pjd_hover:
                        current_screen = "pjd"
                    elif exit_hover:
                        running = False

                elif current_screen == "pjd":
                    motor_areas, valve_areas, glow_rect, back_btn, back_hover = draw_pjd_screen()


                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                    for i, area in enumerate(motor_areas):
                        if area.collidepoint(mouse_pos):
                            pjd_motor_switch = i
                            pjd_operation_timer = 0
                            if i == 2 and pjd_start_phase == 2:  # Пуск на правильном этапе
                                pjd_status = "ЗАПУСК ДВИГАТЕЛЯ"
                            break

                    for i, area in enumerate(valve_areas):
                        if area.collidepoint(mouse_pos):
                            pjd_valve_switch = i
                            if i == 1 and pjd_start_phase == 1:  # Работа на правильном этапе
                                pjd_valve_timer = 0
                                pjd_status = "КЛАПАН ВКЛЮЧЕН"
                            break

                    if glow_rect.collidepoint(mouse_pos):
                        pjd_glow_plug_switch = not pjd_glow_plug_switch
                        if not pjd_glow_plug_switch:
                            pjd_glow_plug_active = False
                            pjd_hum_detected = False
                            pjd_glow_plug_duration = 0
                            pjd_start_phase = 0

                    if back_hover:
                        current_screen = "menu"
                        pjd_motor_switch = 1
                        pjd_valve_switch = 0
                        pjd_glow_plug_switch = False
                        pjd_glow_plug_active = False
                        pjd_status = "ОТКЛЮЧЕН"
                        pjd_start_phase = 0
                
                elif current_screen == "dashboard":
                    (mass_toggle_areas, bcn_toggle_areas, gas_pedal_rect, fuel_valve_toggle_areas,
                     fuel_view_toggle_areas, starter_button_rect, gearbox_areas,
                     handbrake_rect, back_button_rect, starter_hover, back_hover) = draw_dashboard()
                    
                    
                    # Обработка кликов по тумблерам
                    for i, area in enumerate(mass_toggle_areas):
                        if area.collidepoint(mouse_pos):
                            contactor_mass = (i == 1)  # 0-выкл, 1-вкл
                            break
                    
                    for i, area in enumerate(bcn_toggle_areas):
                        if area.collidepoint(mouse_pos):
                            bcn_switch_position = i  # 0-левый, 1-выкл, 2-правый
                            break
                    
                    for i, area in enumerate(fuel_valve_toggle_areas):
                        if area.collidepoint(mouse_pos):
                            fuel_valve_position = i  # 0-левый, 1-выкл, 2-правый
                            break
                    
                    for i, area in enumerate(fuel_view_toggle_areas):
                        if area.collidepoint(mouse_pos):
                            fuel_view_switch = i  # 0-левый, 1-правый
                            break
                    
                    # Обработка кликов по коробке передач
                    for gear, area in gearbox_areas.items():
                        if area.collidepoint(mouse_pos):
                            gear_position = gear
                            break
                    
                    if starter_button_rect.collidepoint(mouse_pos):
                        starter_button = True
                    
                    if handbrake_rect.collidepoint(mouse_pos):
                        handbrake_on = not handbrake_on
                    
                    if back_button_rect.collidepoint(mouse_pos):
                        current_screen = "menu"
                
                elif current_screen == "pjd":
                    back_btn, back_hover = draw_pjd_screen()
                    if back_hover:
                        current_screen = "menu"
        
        elif event.type == pygame.KEYDOWN:
            if current_screen == "dashboard":
                # Тумблер массы
                if event.key == pygame.K_m:
                    contactor_mass = not contactor_mass
                    if not contactor_mass:
                        engine_running = False
                        engine_stalling = False
                        stall_progress = 0.0
                
                # Тумблер БЦН
                elif event.key == pygame.K_b:
                    bcn_switch_position = (bcn_switch_position + 1) % 3
                
                # Топливораспределительный кран
                elif event.key == pygame.K_v:
                    fuel_valve_position = (fuel_valve_position + 1) % 3
                
                # Тумблер просмотра топлива
                elif event.key == pygame.K_f:
                    fuel_view_switch = (fuel_view_switch + 1) % 2
                
                # Стартер
                elif event.key == pygame.K_s:
                    starter_button = True
                
                # Коробка передач (0-5)
                elif event.key == pygame.K_1:
                    gear_position = 0  # ЗХ
                elif event.key == pygame.K_2:
                    gear_position = 1  # Н (нижняя)
                elif event.key == pygame.K_3:
                    gear_position = 2  # 1
                elif event.key == pygame.K_4:
                    gear_position = 3  # 2
                elif event.key == pygame.K_5:
                    gear_position = 4  # 3
                elif event.key == pygame.K_6:
                    gear_position = 5  # Н (верхняя)

                     # Рукоятка ЭМЗН
                elif event.key == pygame.K_7:
                    emzn_handle_position = 1  # Включено
                elif event.key == pygame.K_8:
                    emzn_handle_position = 0  # Выключено
                
                # Ручник
                elif event.key == pygame.K_SPACE:
                    handbrake_on = not handbrake_on
                
                # Назад
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
            
            elif current_screen == "pjd":
                if event.key == pygame.K_ESCAPE:
                    current_screen = "menu"
        
        elif event.type == pygame.KEYUP:
            if current_screen == "dashboard":
                # Педаль газа отпущена
                if event.key == pygame.K_g:
                    if not shift_pressed:
                        gas_pedal_position = 0
                
                # SHIFT отпущен
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_pressed = False
                    gas_pedal_position = 0
                
                # Стартер отпущен
                elif event.key == pygame.K_s:
                    starter_button = False
        
        # Обработка колесика мыши для тонкой регулировки педали газа
        elif event.type == pygame.MOUSEWHEEL:
            if current_screen == "dashboard":
                gas_pedal_position = max(0, min(100, gas_pedal_position + event.y * 5))
    
    # Отрисовка текущего экрана
    if current_screen == "menu":
        draw_main_menu()
    elif current_screen == "dashboard":
        draw_dashboard()
    elif current_screen == "pjd":
        draw_pjd_screen()
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Выход
pygame.quit()
sys.exit()
