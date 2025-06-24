import pygame
import math
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GRAY = (200, 200, 200)
LIGHT_BLUE = (100, 150, 255)
DARK_BLUE = (30, 60, 120)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Анимация человечка")
clock = pygame.time.Clock()

# Параметры человечка
HEAD_RADIUS = 20
BODY_LENGTH = 60
ARM_LENGTH = 40
LEG_LENGTH = 50
HAND_RADIUS = 8
FOOT_RADIUS = 10
FLAG_WIDTH = 30
FLAG_HEIGHT = 20

# Класс для кнопок
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, surface):
        color = LIGHT_BLUE if self.hovered else BLUE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_BLUE, self.rect, 2, border_radius=8)
        
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()
                return True
        return False

# Класс для анимации
class Animation:
    def __init__(self):
        self.anim_type = "walking"
        self.paused = False
        self.frame = 0
        self.speed = 0.1
        self.flag_angle = 0
        self.flag_dir = 1
        self.body_lean = 0
        
    def update(self):
        if not self.paused:
            self.frame += self.speed
            
            # Динамика для разных анимаций
            if self.anim_type == "running":
                self.speed = 0.2  # более высокая скорость для бега
            elif self.anim_type == "walking":
                self.speed = 0.1  # нормальная скорость для ходьбы
            else:
                self.speed = 0.1
                
            if self.anim_type == "signaling":
                self.flag_angle += 0.1 * self.flag_dir
                if abs(self.flag_angle) > 1.2:
                    self.flag_dir *= -1
                    
            # Наклон тела для бега
            if self.anim_type == "running":
                self.body_lean = math.sin(self.frame * 2) * 0.2
            else:
                self.body_lean = 0
    
    def draw_human(self, surface, x, y):
        # Корректировка положения для наклона тела
        lean_offset = self.body_lean * BODY_LENGTH
        
        # Голова
        head_y = y - HEAD_RADIUS - BODY_LENGTH // 2 + lean_offset
        pygame.draw.circle(surface, BLACK, (x, head_y), HEAD_RADIUS)
        
        # Тело с учетом наклона
        body_start_y = y - BODY_LENGTH // 2 + lean_offset
        body_end_y = y + BODY_LENGTH // 2 + lean_offset
        pygame.draw.line(surface, BLACK, (x, body_start_y), (x, body_end_y), 3)
        
        # Ноги
        if self.anim_type == "squatting":
            squat_offset = math.sin(self.frame) * 30
            left_foot_x = x - 30
            left_foot_y = body_end_y + 20 + squat_offset
            right_foot_x = x + 30
            right_foot_y = body_end_y + 20 + squat_offset
            
            pygame.draw.line(surface, BLACK, (x, body_end_y), 
                            (left_foot_x, left_foot_y), 3)
            pygame.draw.line(surface, BLACK, (x, body_end_y), 
                            (right_foot_x, right_foot_y), 3)
            
            # Ступни для приседаний
            pygame.draw.circle(surface, BLACK, (left_foot_x, left_foot_y), FOOT_RADIUS)
            pygame.draw.circle(surface, BLACK, (right_foot_x, right_foot_y), FOOT_RADIUS)
        else:
            # Разная амплитуда для ходьбы и бега
            if self.anim_type == "running":
                amplitude = 1.2  # большая амплитуда для бега
            else:
                amplitude = 0.8  # нормальная амплитуда для ходьбы
                
            angle = math.sin(self.frame) * amplitude
            left_foot_x = x - LEG_LENGTH * math.sin(angle)
            left_foot_y = body_end_y + LEG_LENGTH * math.cos(angle)
            right_foot_x = x + LEG_LENGTH * math.sin(angle * 0.7)
            right_foot_y = body_end_y + LEG_LENGTH * math.cos(angle * 0.7)
            
            pygame.draw.line(surface, BLACK, (x, body_end_y), 
                            (left_foot_x, left_foot_y), 3)
            pygame.draw.line(surface, BLACK, (x, body_end_y), 
                            (right_foot_x, right_foot_y), 3)
            
            # Ступни для ходьбы/бега/сигнализации
            pygame.draw.circle(surface, BLACK, (left_foot_x, left_foot_y), FOOT_RADIUS)
            pygame.draw.circle(surface, BLACK, (right_foot_x, right_foot_y), FOOT_RADIUS)
        
        # Руки
        if self.anim_type == "signaling":
            # Сигнализирующая рука с флажком
            signal_arm_x = x - ARM_LENGTH * math.sin(self.flag_angle) - 20
            signal_arm_y = y - ARM_LENGTH * math.cos(self.flag_angle) + lean_offset
            pygame.draw.line(surface, BLACK, (x, y + lean_offset), 
                            (signal_arm_x, signal_arm_y), 3)
            
            # Флажок
            pygame.draw.polygon(surface, RED, [
                (signal_arm_x, signal_arm_y),
                (signal_arm_x - FLAG_WIDTH, signal_arm_y - FLAG_HEIGHT // 2),
                (signal_arm_x - FLAG_WIDTH, signal_arm_y + FLAG_HEIGHT // 2)
            ])
            
            # Другая рука
            other_arm_x = x + 30
            other_arm_y = y - 20 + lean_offset
            pygame.draw.line(surface, BLACK, (x, y + lean_offset), 
                            (other_arm_x, other_arm_y), 3)
            
            # Кисть на обычной руке
            pygame.draw.circle(surface, BLACK, (other_arm_x, other_arm_y), HAND_RADIUS)
        else:
            # Разная амплитуда для рук при ходьбе/беге
            if self.anim_type == "running":
                arm_amplitude = 1.5  # больший размах рук для бега
                arm_phase = 0  # руки и ноги синхронны
            else:
                arm_amplitude = 0.8  # нормальный размах для ходьбы
                arm_phase = 1  # руки и ноги в противофазе
                
            arm_angle = math.sin(self.frame + arm_phase) * arm_amplitude
            left_hand_x = x - ARM_LENGTH * math.sin(arm_angle)
            left_hand_y = y - ARM_LENGTH * math.cos(arm_angle) + lean_offset
            right_hand_x = x + ARM_LENGTH * math.sin(arm_angle * 0.7)
            right_hand_y = y - ARM_LENGTH * math.cos(arm_angle * 0.7) + lean_offset
            
            pygame.draw.line(surface, BLACK, (x, y + lean_offset), 
                            (left_hand_x, left_hand_y), 3)
            pygame.draw.line(surface, BLACK, (x, y + lean_offset), 
                            (right_hand_x, right_hand_y), 3)
            
            # Кисти для не-сигнализации
            pygame.draw.circle(surface, BLACK, (left_hand_x, left_hand_y), HAND_RADIUS)
            pygame.draw.circle(surface, BLACK, (right_hand_x, right_hand_y), HAND_RADIUS)
    
    def set_animation(self, anim_type):
        self.anim_type = anim_type
        self.frame = 0
        self.flag_angle = 0
        self.flag_dir = 1
        self.body_lean = 0
        
    def toggle_pause(self):
        self.paused = not self.paused

# Функции для кнопок
def set_walking():
    animation.set_animation("walking")

def set_running():
    animation.set_animation("running")
    
def set_squatting():
    animation.set_animation("squatting")
    
def set_signaling():
    animation.set_animation("signaling")
    
def toggle_pause():
    animation.toggle_pause()
    
def show_about():
    global show_about_screen
    show_about_screen = True
    
def show_help():
    global about_tab
    about_tab = "help"
    
def show_developer():
    global about_tab
    about_tab = "developer"
    
def close_about():
    global show_about_screen
    show_about_screen = False

# Создание объектов
animation = Animation()
show_about_screen = False
about_tab = "help"

# Создание кнопок
buttons = [
    Button(20, 20, 150, 40, "Идущий человечек", set_walking),
    Button(20, 70, 150, 40, "Бегущий человечек", set_running),
    Button(20, 120, 150, 40, "Приседания", set_squatting),
    Button(20, 170, 150, 40, "Сигнализация флажком", set_signaling),
    Button(20, 220, 150, 40, "Пауза", toggle_pause),
    Button(20, 270, 150, 40, "О программе", show_about)
]

about_buttons = [
    Button(WIDTH//2 - 100, HEIGHT - 80, 120, 40, "Закрыть", close_about),
    Button(WIDTH//2 - 250, HEIGHT//2 - 100, 120, 40, "Справка", show_help),
    Button(WIDTH//2 + 130, HEIGHT//2 - 100, 150, 40, "О разработчике", show_developer)
]

# Главный цикл
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if show_about_screen:
            for button in about_buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)
        else:
            for button in buttons:
                button.check_hover(mouse_pos)
                button.handle_event(event)
    
    # Обновление анимации
    animation.update()
    
    # Отрисовка
    screen.fill(WHITE)
    
    # Рисуем анимацию
    animation.draw_human(screen, WIDTH // 2, HEIGHT // 2 + 50)
    
    # Рисуем кнопки
    for button in buttons:
        button.draw(screen)
    
    # Рисуем окно "О программе"
    if show_about_screen:
        # Полупрозрачный фон
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        # Окно
        about_rect = pygame.Rect(WIDTH//4, HEIGHT//6, WIDTH//2, 2*HEIGHT//3)
        pygame.draw.rect(screen, LIGHT_BLUE, about_rect, border_radius=12)
        pygame.draw.rect(screen, DARK_BLUE, about_rect, 3, border_radius=12)
        
        # Заголовок
        font = pygame.font.SysFont(None, 36)
        title = font.render("О программе", True, DARK_BLUE)
        screen.blit(title, (about_rect.centerx - title.get_width() // 2, about_rect.y + 20))
        
        # Содержимое вкладок
        font = pygame.font.SysFont(None, 24)
        if about_tab == "help":
            lines = [
                "Программа для анимации движений человека",
                "",
                "Функции:",
                "- Идущий человечек",
                "- Бегущий человечек (более быстрый с наклоном)",
                "- Приседающий человечек",
                "- Человечек с сигнализацией флажком",
                "",
                "Управление:",
                "Используйте кнопки для выбора анимации",
                "Кнопка 'Пауза' приостанавливает анимацию"
            ]
        else:
            lines = [
                "Курсовой проект по программированию",
                "",
                "Разработчик: [Ваше Имя]",
                "Группа: [Ваша Группа]",
                "Год: 2023",
                "",
                "Университет: [Ваш Университет]",
                "Факультет: [Ваш Факультет]"
            ]
        
        y_offset = about_rect.y + 80
        for line in lines:
            text = font.render(line, True, BLACK)
            screen.blit(text, (about_rect.x + 30, y_offset))
            y_offset += 30
        
        # Кнопки
        for button in about_buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()