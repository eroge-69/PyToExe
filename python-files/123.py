import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Визуальная новелла")

# Цвета
BACKGROUND = (30, 30, 50)
TEXT_BOX = (40, 40, 70, 200)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT = (180, 70, 150)
NAME_COLORS = {
    "Данил": (100, 150, 220),
    "Ангелина": (220, 100, 150),
    "Никита": (150, 220, 100)
}

# Шрифты
font_large = pygame.font.SysFont("Arial", 32)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 22)

# Состояния игры
current_scene = 0
current_dialogue = 0
animation_phase = 0
animation_progress = 0
animation_speed = 0.1

# Сцены и диалоги
scenes = [
    {
        "name": "Встреча",
        "dialogues": [
            {"character": "Данил", "text": "Ангелина, я так долго ждал этой встречи..."},
            {"character": "Ангелина", "text": "Данил, я тоже... Ты не представляешь, как я по тебе скучала."},
            {"character": "Никита", "text": "*тихо наблюдает из угла комнаты*"},
            {"character": "Данил", "text": "Ты сегодня такая красивая... Моё сердце бешено бьётся!"},
            {"character": "Ангелина", "text": "Перестань... Я вся краснею..."},
        ]
    },
    {
        "name": "Страсть",
        "dialogues": [
            {"character": "Ангелина", "text": "Ох, Данил... Твои прикосновения сводят меня с ума!"},
            {"character": "Данил", "text": "Ты так прекрасна, когда возбуждена... Я не могу сдержаться!"},
            {"character": "Никита", "text": "*вздыхает и отворачивается*"},
            {"character": "Ангелина", "text": "Да, вот так... Не останавливайся!"},
            {"character": "Данил", "text": "Ты вся дрожишь... Это так возбуждает!"},
        ]
    },
    {
        "name": "Кульминация",
        "dialogues": [
            {"character": "Ангелина", "text": "Я больше не могу... Кончаю!"},
            {"character": "Данил", "text": "Со мной... Давай вместе!"},
            {"character": "Никита", "text": "*тихо плачет в уголке*"},
            {"character": "Ангелина", "text": "Это было невероятно..."},
            {"character": "Данил", "text": "Ты лучшая, Ангелина..."},
        ]
    }
]

# Функции для рисования
def draw_background():
    screen.fill(BACKGROUND)
    # Рисуем звёзды на фоне
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT - 200)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

def draw_characters():
    # Рисуем персонажей в зависимости от сцены
    if current_scene == 0:
        # Первая сцена - все персонажи отдельно
        draw_character("Данил", 250, 300, 1.0)
        draw_character("Ангелина", 500, 300, 1.0)
        draw_character("Никита", 750, 300, 0.8)
    elif current_scene == 1:
        # Вторая сцена - Данил и Ангелина ближе
        draw_character("Данил", 350, 300, 1.0)
        draw_character("Ангелина", 500, 300, 1.0)
        draw_character("Никита", 800, 350, 0.7)
        
        # Анимация палки во второй сцене
        if current_dialogue >= 2:  # Начинаем анимацию с третьего диалога
            draw_stick_animation(400, 300, 500, 300)
    else:
        # Третья сцена - Данил и Ангелина очень близко
        draw_character("Данил", 400, 300, 1.0)
        draw_character("Ангелина", 500, 300, 1.0)
        draw_character("Никита", 850, 400, 0.6)
        
        # Анимация палки в третьей сцене
        if current_dialogue >= 1:  # Начинаем анимацию со второго диалога
            draw_stick_animation(420, 300, 500, 300)

def draw_stick_animation(danil_x, danil_y, angelina_x, angelina_y):
    global animation_phase, animation_progress
    
    # Вычисляем позицию палки на основе фазы анимации
    progress = (math.sin(animation_phase) + 1) / 2  # От 0 до 1
    stick_length = 80
    
    # Начальная точка у Данила
    start_x = danil_x + 30
    start_y = danil_y
    
    # Конечная точка у Ангелины (движется вперед-назад)
    end_x = angelina_x - 30 - (1 - progress) * 40
    end_y = angelina_y
    
    # Рисуем палку
    pygame.draw.line(screen, (200, 150, 100), (start_x, start_y), (end_x, end_y), 8)
    pygame.draw.circle(screen, (200, 150, 100), (start_x, start_y), 5)
    
    # Обновляем анимацию
    animation_phase += animation_speed
    animation_progress = progress

def draw_character(name, x, y, scale):
    color = NAME_COLORS[name]
    size = int(80 * scale)
    
    # Рисуем тело
    pygame.draw.circle(screen, color, (x, y - size//3), size//2)
    pygame.draw.rect(screen, color, (x - size//2, y - size//3, size, size))
    
    # Рисуем глаза
    eye_y = y - size//3 - size//10
    pygame.draw.circle(screen, (255, 255, 255), (x - size//4, eye_y), size//8)
    pygame.draw.circle(screen, (255, 255, 255), (x + size//4, eye_y), size//8)
    pygame.draw.circle(screen, (0, 0, 0), (x - size//4, eye_y), size//16)
    pygame.draw.circle(screen, (0, 0, 0), (x + size//4, eye_y), size//16)
    
    # Рисуем рот
    if name == "Никита" and current_scene > 0:
        # Грустный рот для Никиты
        pygame.draw.arc(screen, (0, 0, 0), (x - size//4, y - size//5, size//2, size//2), math.pi, 2*math.pi, 2)
    elif name == "Ангелина" and current_scene > 0 and animation_progress > 0.7:
        # Открытый рот для Ангелины во время анимации
        pygame.draw.ellipse(screen, (0, 0, 0), (x - size//4, y, size//2, size//4))
    else:
        # Нормальный рот
        pygame.draw.arc(screen, (0, 0, 0), (x - size//4, y - size//10, size//2, size//3), 0, math.pi, 2)
    
    # Рисуем имя
    name_text = font_small.render(name, True, TEXT_COLOR)
    screen.blit(name_text, (x - name_text.get_width()//2, y + size//2))

def draw_text_box():
    # Рисуем полупрозрачный текстовый бокс
    s = pygame.Surface((WIDTH - 100, 130), pygame.SRCALPHA)
    s.fill(TEXT_BOX)
    screen.blit(s, (50, HEIGHT - 180))
    
    # Рисуем рамку
    pygame.draw.rect(screen, HIGHLIGHT, (50, HEIGHT - 180, WIDTH - 100, 130), 3)
    
    # Рисуем имя персонажа
    dialogue = scenes[current_scene]["dialogues"][current_dialogue]
    name_text = font_medium.render(dialogue["character"] + ":", True, NAME_COLORS[dialogue["character"]])
    screen.blit(name_text, (80, HEIGHT - 160))
    
    # Рисуем текст
    text = font_medium.render(dialogue["text"], True, TEXT_COLOR)
    screen.blit(text, (80, HEIGHT - 120))
    
    # Рисуем подсказку
    hint_text = font_small.render("Нажмите ПРОБЕЛ для продолжения...", True, (180, 180, 180))
    screen.blit(hint_text, (WIDTH - hint_text.get_width() - 80, HEIGHT - 60))

def draw_scene_name():
    name = scenes[current_scene]["name"]
    text = font_large.render(name, True, HIGHLIGHT)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 30))

def draw_hearts():
    # Рисуем сердечки вокруг Данила и Ангелины во время анимации
    if current_scene > 0 and animation_progress > 0.5:
        for i in range(3):
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-60, -20)
            size = random.randint(5, 15)
            x = 450 + offset_x
            y = 250 + offset_y
            
            pygame.draw.polygon(screen, (255, 100, 100), [
                (x, y - size),
                (x - size, y - size//2),
                (x - size//2, y + size//2),
                (x, y),
                (x + size//2, y + size//2),
                (x + size, y - size//2)
            ])

# Основной цикл игры
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Переход к следующему диалогу или сцене
                current_dialogue += 1
                if current_dialogue >= len(scenes[current_scene]["dialogues"]):
                    current_dialogue = 0
                    current_scene += 1
                    if current_scene >= len(scenes):
                        current_scene = 0  # Начать заново после завершения
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Отрисовка
    draw_background()
    draw_characters()
    draw_hearts()
    draw_text_box()
    draw_scene_name()
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()