import pygame
import sys
import re
import pygame.locals as pg_locals
import tkinter as tk
from tkinter import scrolledtext

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
GRID_SIZE = 20
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255, 128)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_GRAY = (200, 200, 200)
BUTTON_HOVER = (180, 180, 180)
GOLD = (255, 215, 0)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Редактор карт для платформера")
font = pygame.font.SysFont('Arial', 16)
large_font = pygame.font.SysFont('Arial', 24)

# Настройки редактора
PLATFORM = 0
SPIKE = 1
COIN = 2
DELETE = 3
LOAD = 4
current_mode = PLATFORM
dragging = False
current_rect = None
start_pos = None
hovered_object = None
text_input_active = False
input_text = ""
input_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50, 500, 100)
load_phase = 1  # 1 - загрузка платформ/шипов, 2 - загрузка монет

# Камера - теперь без ограничений по миру
camera_x, camera_y = 0, 0
camera_move_speed = 20

# Хранилище объектов
platforms = []
spikes = []
coins = []

# Кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                return self.action()
        return None

# Функции, которые используются в кнопках
def confirm_clear():
    if show_confirmation_dialog("Очистить всю карту?"):
        platforms.clear()
        spikes.clear()
        coins.clear()
        show_message("Карта очищена!")
    return None

def set_mode(mode):
    global current_mode, text_input_active, load_phase
    current_mode = mode
    if mode == LOAD:
        handle_load_mode()
        load_phase = 1  # Сброс фазы при каждом входе в режим загрузки
    else:
        text_input_active = False
    return None

def save_to_file():
    code = generate_code()
    try:
        with open("level.c", "w") as f:
            f.write(code)
        show_message("Карта сохранена в level.c")
    except:
        show_message("Ошибка сохранения файла")
    return None

def show_code_window(code):
    root = tk.Tk()
    root.title("Код уровня")
    root.geometry("800x600")
    
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 10))
    text_area.insert(tk.INSERT, code)
    text_area.pack(expand=True, fill="both")
    
    # Кнопка копирования
    copy_button = tk.Button(root, text="Копировать весь код", 
                          command=lambda: root.clipboard_clear() or root.clipboard_append(code))
    copy_button.pack(pady=5)
    
    # Кнопка закрытия
    close_button = tk.Button(root, text="Закрыть", command=root.destroy)
    close_button.pack(pady=5)
    
    root.mainloop()

def print_code_to_console():
    code = generate_code()
    show_code_window(code)
    show_message("Код открыт в отдельном окне")

# Создаем кнопки
buttons = [
    Button(10, 10, 120, 40, "Платформа (P)", LIGHT_GRAY, BUTTON_HOVER, lambda: set_mode(PLATFORM)),
    Button(140, 10, 120, 40, "Шип (S)", LIGHT_GRAY, BUTTON_HOVER, lambda: set_mode(SPIKE)),
    Button(270, 10, 120, 40, "Монета (C)", LIGHT_GRAY, BUTTON_HOVER, lambda: set_mode(COIN)),
    Button(400, 10, 120, 40, "Удалить (D)", LIGHT_GRAY, BUTTON_HOVER, lambda: set_mode(DELETE)),
    Button(530, 10, 120, 40, "Загрузить (L)", LIGHT_GRAY, BUTTON_HOVER, lambda: set_mode(LOAD)),
    Button(660, 10, 120, 40, "Очистить все", (255, 150, 150), (255, 120, 120), confirm_clear),
    Button(790, 10, 120, 40, "Сгенерировать", (150, 255, 150), (120, 255, 120), print_code_to_console),
    Button(920, 10, 70, 40, "Выход", (255, 150, 150), (255, 120, 120), lambda: sys.exit())
]

def world_to_screen(x, y):
    return x - camera_x, y - camera_y

def screen_to_world(x, y):
    return x + camera_x, y + camera_y

def draw_grid():
    start_x = (camera_x // GRID_SIZE) * GRID_SIZE
    start_y = (camera_y // GRID_SIZE) * GRID_SIZE
    
    for x in range(int(start_x), int(start_x) + SCREEN_WIDTH + GRID_SIZE, GRID_SIZE):
        screen_x = x - camera_x
        pygame.draw.line(screen, (220, 220, 220), (screen_x, 0), (screen_x, SCREEN_HEIGHT))
    
    for y in range(int(start_y), int(start_y) + SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
        screen_y = y - camera_y
        pygame.draw.line(screen, (220, 220, 220), (0, screen_y), (SCREEN_WIDTH, screen_y))

def draw_objects():
    global hovered_object
    hovered_object = None
    
    for i, platform in enumerate(platforms):
        screen_x, screen_y = world_to_screen(platform.x, platform.y)
        rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
        pygame.draw.rect(screen, GRAY, rect)
        
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, rect, 2)
            hovered_object = ('platform', i)
    
    for i, spike in enumerate(spikes):
        screen_x, screen_y = world_to_screen(spike.x, spike.y)
        rect = pygame.Rect(screen_x, screen_y, spike.width, spike.height)
        pygame.draw.rect(screen, RED, rect)
        
        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, YELLOW, rect, 2)
            hovered_object = ('spike', i)
    
    for i, coin in enumerate(coins):
        screen_x, screen_y = world_to_screen(coin['x'], coin['y'])
        pygame.draw.circle(screen, GOLD, (int(screen_x), int(screen_y)), coin['radius'])
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(screen_y)), coin['radius'] - 3)
        
        mouse_pos = pygame.mouse.get_pos()
        distance = ((mouse_pos[0] - screen_x) ** 2 + (mouse_pos[1] - screen_y) ** 2) ** 0.5
        if distance <= coin['radius']:
            pygame.draw.circle(screen, YELLOW, (int(screen_x), int(screen_y)), coin['radius'], 2)
            hovered_object = ('coin', i)

def draw_preview():
    if dragging and start_pos and current_mode not in [DELETE, LOAD]:
        mouse_pos = pygame.mouse.get_pos()
        world_x, world_y = screen_to_world(*start_pos)
        mouse_world_x, mouse_world_y = screen_to_world(*mouse_pos)
        
        if current_mode == COIN:
            screen_x, screen_y = world_to_screen(world_x, world_y)
            pygame.draw.circle(screen, GOLD, (int(screen_x), int(screen_y)), 15)
        else:
            x = min(world_x, mouse_world_x)
            y = min(world_y, mouse_world_y)
            width = abs(mouse_world_x - world_x)
            height = abs(mouse_world_y - world_y)
            
            screen_x, screen_y = world_to_screen(x, y)
            preview_rect = pygame.Rect(screen_x, screen_y, width, height)
            
            if current_mode == PLATFORM:
                pygame.draw.rect(screen, (200, 200, 200, 128), preview_rect)
            else:
                pygame.draw.rect(screen, (255, 100, 100, 128), preview_rect)

def generate_code():
    code = "Platform platforms[] = {\n"
    code += "    // Основные платформы\n"
    for platform in platforms:
        code += f"    {{ (Rectangle){{ {platform.x}, {platform.y}, {platform.width}, {platform.height} }}, GRAY, false }},\n"
    
    if spikes:
        code += "\n    // Шипы\n"
    for spike in spikes:
        code += f"    {{ (Rectangle){{ {spike.x}, {spike.y}, {spike.width}, {spike.height} }}, RED, true }},\n"
    
    code = code[:-2] + "\n};\n\n"
    
    # Генерация монет с динамическим размером массива
    coin_count = len(coins)
    code += f"Coin coins[{coin_count}] = {{ 0 }};\n"
    code += "// Размещаем монетки на платформах\n"
    for i, coin in enumerate(coins):
        code += f"coins[{i}] = (Coin){{ (Vector2){{ {coin['x']}, {coin['y']} }}, 15, true, 0 }};\n"
    
    return code

def show_message(message, duration=1500):
    msg_surface = pygame.Surface((400, 50))
    msg_surface.fill(DARK_GRAY)
    text = large_font.render(message, True, WHITE)
    msg_surface.blit(text, (10, 10))
    screen.blit(msg_surface, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 25))
    pygame.display.flip()
    pygame.time.delay(duration)

def show_confirmation_dialog(message):
    dialog_width, dialog_height = 400, 100
    dialog_x = SCREEN_WIDTH // 2 - dialog_width // 2
    dialog_y = SCREEN_HEIGHT // 2 - dialog_height // 2
    
    pygame.draw.rect(screen, DARK_GRAY, (dialog_x, dialog_y, dialog_width, dialog_height))
    pygame.draw.rect(screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
    
    text = large_font.render(message, True, WHITE)
    screen.blit(text, (dialog_x + 20, dialog_y + 20))
    
    yes_rect = pygame.Rect(dialog_x + 100, dialog_y + 60, 80, 30)
    no_rect = pygame.Rect(dialog_x + 220, dialog_y + 60, 80, 30)
    
    pygame.draw.rect(screen, GREEN, yes_rect)
    pygame.draw.rect(screen, RED, no_rect)
    
    yes_text = font.render("Да", True, BLACK)
    no_text = font.render("Нет", True, BLACK)
    
    screen.blit(yes_text, (yes_rect.x + 30, yes_rect.y + 8))
    screen.blit(no_text, (no_rect.x + 30, no_rect.y + 8))
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if yes_rect.collidepoint(mouse_pos):
                    return True
                elif no_rect.collidepoint(mouse_pos):
                    return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y or event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    return False

def handle_camera_movement():
    global camera_x, camera_y
    
    keys = pygame.key.get_pressed()
    if keys[pg_locals.K_LEFT] or keys[pg_locals.K_a]:
        camera_x -= camera_move_speed
    if keys[pg_locals.K_RIGHT] or keys[pg_locals.K_d]:
        camera_x += camera_move_speed
    if keys[pg_locals.K_UP] or keys[pg_locals.K_w]:
        camera_y -= camera_move_speed
    if keys[pg_locals.K_DOWN] or keys[pg_locals.K_s]:
        camera_y += camera_move_speed

def delete_object():
    global hovered_object
    
    if hovered_object:
        obj_type, index = hovered_object
        if obj_type == 'platform':
            platforms.pop(index)
            show_message("Платформа удалена")
        elif obj_type == 'spike':
            spikes.pop(index)
            show_message("Шип удален")
        elif obj_type == 'coin':
            coins.pop(index)
            show_message("Монета удалена")

def load_platforms_and_spikes(code):
    global platforms, spikes
    
    platforms.clear()
    spikes.clear()
    
    platform_pattern = r'\{\s*\(Rectangle\)\{\s*(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*)\s*\},\s*GRAY,\s*false\s*\}'
    spike_pattern = r'\{\s*\(Rectangle\)\{\s*(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*),\s*(\d+\.?\d*)\s*\},\s*RED,\s*true\s*\}'
    
    for match in re.finditer(platform_pattern, code):
        x, y, w, h = map(float, match.groups())
        platforms.append(pygame.Rect(int(x), int(y), int(w), int(h)))
    
    for match in re.finditer(spike_pattern, code):
        x, y, w, h = map(float, match.groups())
        spikes.append(pygame.Rect(int(x), int(y), int(w), int(h)))
    
    show_message(f"Загружено платформ: {len(platforms)}, шипов: {len(spikes)}. Нажмите Enter для загрузки монет")

def load_coins(code):
    global coins
    
    coins.clear()
    coin_pattern = r'coins\[\d+\]\s*=\s*\(Coin\)\{\s*\(Vector2\)\{\s*(\d+\.?\d*),\s*(\d+\.?\d*)\s*\},\s*15,\s*true,\s*0\s*\}'
    
    for match in re.finditer(coin_pattern, code):
        x, y = map(float, match.groups())
        coins.append({'x': int(x), 'y': int(y), 'radius': 15})
    
    show_message(f"Загружено монет: {len(coins)}")

def draw_text_input():
    pygame.draw.rect(screen, WHITE, input_rect)
    pygame.draw.rect(screen, BLACK, input_rect, 2)
    
    if load_phase == 1:
        prompt = "Вставьте C-код карты (платформы/шипы) и нажмите Enter:"
    else:
        prompt = "Вставьте C-код монет и нажмите Enter:"
    
    text_surface = font.render(prompt, True, BLACK)
    screen.blit(text_surface, (input_rect.x + 10, input_rect.y - 25))
    
    cleaned_text = input_text.replace('\x00', '').strip()
    
    text_lines = []
    current_line = ""
    for word in cleaned_text.split():
        test_line = current_line + word + " "
        if font.size(test_line)[0] < input_rect.width - 20:
            current_line = test_line
        else:
            text_lines.append(current_line)
            current_line = word + " "
    if current_line:
        text_lines.append(current_line)
    
    for i, line in enumerate(text_lines[:10]):
        if line.strip():
            try:
                line_surface = font.render(line, True, BLACK)
                screen.blit(line_surface, (input_rect.x + 10, input_rect.y + 10 + i * 20))
            except:
                pass

def handle_load_mode():
    global text_input_active, input_text, load_phase
    
    if not text_input_active:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            clipboard_text = root.clipboard_get()
            root.destroy()
            
            if "Platform platforms[]" in clipboard_text or "Coin coins[]" in clipboard_text:
                input_text = clipboard_text.replace('\x00', '').strip()
                load_phase = 1  # Начинаем с загрузки платформ и шипов
        except:
            pass
    
    text_input_active = True
    draw_text_input()
    
    global camera_x, camera_y
    camera_x, camera_y = 0, 0

# Главный цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        button_action = None
        for button in buttons:
            button.check_hover(mouse_pos)
            action = button.handle_event(event)
            if action is not None:
                button_action = action
        
        if button_action is not None:
            continue
        
        if event.type == pygame.KEYDOWN:
            if text_input_active:
                if event.key == pygame.K_RETURN:
                    if load_phase == 1:  # Первое нажатие - загружаем платформы и шипы
                        load_platforms_and_spikes(input_text)
                        load_phase = 2  # Переходим к фазе загрузки монет
                        input_text = ""  # Очищаем поле ввода для следующего этапа
                    elif load_phase == 2:  # Второе нажатие - загружаем монеты
                        load_coins(input_text)
                        text_input_active = False
                        current_mode = PLATFORM
                        load_phase = 1  # Сбрасываем для следующей загрузки
                elif event.key == pygame.K_ESCAPE:
                    text_input_active = False
                    current_mode = PLATFORM
                    load_phase = 1  # Сбрасываем фазу при отмене
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        root.withdraw()
                        clipboard_text = root.clipboard_get()
                        root.destroy()
                        input_text += clipboard_text.replace('\x00', '')
                    except:
                        pass
                else:
                    if len(input_text) < 2000:
                        input_text += event.unicode
            else:
                if event.key == pygame.K_p:
                    set_mode(PLATFORM)
                elif event.key == pygame.K_s:
                    set_mode(SPIKE)
                elif event.key == pygame.K_c:
                    set_mode(COIN)
                elif event.key == pygame.K_d:
                    set_mode(DELETE)
                elif event.key == pygame.K_l:
                    set_mode(LOAD)
                elif event.key == pygame.K_g:
                    print_code_to_console()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_mode == DELETE and not text_input_active:
                    delete_object()
                elif current_mode not in [LOAD, DELETE] and not text_input_active:
                    start_pos = event.pos
                    dragging = True
            elif event.button == 2:
                pygame.mouse.get_rel()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging and current_mode not in [DELETE, LOAD] and not text_input_active:
                end_pos = event.pos
                start_world_x, start_world_y = screen_to_world(*start_pos)
                
                if current_mode == COIN:
                    coins.append({
                        'x': start_world_x,
                        'y': start_world_y,
                        'radius': 15
                    })
                else:
                    end_world_x, end_world_y = screen_to_world(*end_pos)
                    
                    x = min(start_world_x, end_world_x)
                    y = min(start_world_y, end_world_y)
                    width = abs(end_world_x - start_world_x)
                    height = abs(end_world_y - start_world_y)
                    
                    if width >= 5 and height >= 5:
                        new_rect = pygame.Rect(x, y, width, height)
                        if current_mode == PLATFORM:
                            platforms.append(new_rect)
                        else:
                            spikes.append(new_rect)
                
                dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[1] and not text_input_active:
                rel_x, rel_y = event.rel
                camera_x -= rel_x
                camera_y -= rel_y
    
    if not text_input_active:
        handle_camera_movement()
    
    screen.fill(WHITE)
    
    if not text_input_active:
        draw_grid()
        draw_objects()
        draw_preview()
    else:
        draw_text_input()
    
    for button in buttons:
        button.draw(screen)
    
    mode_text = f"Текущий режим: {'Платформа' if current_mode == PLATFORM else 'Шип' if current_mode == SPIKE else 'Монета' if current_mode == COIN else 'Удаление' if current_mode == DELETE else 'Загрузка'}"
    mode_surface = font.render(mode_text, True, BLACK)
    screen.blit(mode_surface, (10, 60))
    
    camera_text = f"Камера: ({camera_x}, {camera_y})"
    camera_surface = font.render(camera_text, True, BLACK)
    screen.blit(camera_surface, (10, 80))
    
    if current_mode == DELETE and not text_input_active:
        hint_text = "Щелкните по объекту, чтобы удалить его"
        hint_surface = font.render(hint_text, True, RED)
        screen.blit(hint_surface, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 30))
    elif current_mode == LOAD and text_input_active:
        if load_phase == 1:
            hint_text = "Нажмите Enter для загрузки платформ/шипов или Esc для отмены"
        else:
            hint_text = "Нажмите Enter для загрузки монет или Esc для отмены"
        hint_surface = font.render(hint_text, True, PURPLE)
        screen.blit(hint_surface, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 30))
    elif current_mode == COIN and not text_input_active:
        hint_text = "Щелкните, чтобы разместить монету"
        hint_surface = font.render(hint_text, True, GOLD)
        screen.blit(hint_surface, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 30))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
