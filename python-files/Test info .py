import pygame
import sys
import os
import time
import json
import random
import base64
import zlib
from datetime import datetime
import traceback

# Инициализация Pygame и микшера
pygame.init()
pygame.mixer.init()

# Константы
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (15, 30, 60)
ACCENT_COLOR = (0, 200, 255)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (30, 120, 180)
BUTTON_HOVER = (50, 170, 220)
FONT_LARGE = pygame.font.SysFont('Arial', 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont('Arial', 32)
FONT_SMALL = pygame.font.SysFont('Arial', 24)

# Создаем экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Интерактивный Тест по Информатике")
clock = pygame.time.Clock()

# Пути к ресурсам (для работы в EXE)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Звуковые эффекты
SOUNDS = {}
def load_sounds():
    sounds_dir = resource_path("sounds")
    for name in ['correct', 'wrong', 'hint', 'timeout', 'click', 'complete']:
        sound_path = os.path.join(sounds_dir, f"{name}.wav")
        if os.path.exists(sound_path):
            try:
                SOUNDS[name] = pygame.mixer.Sound(sound_path)
            except:
                SOUNDS[name] = None
        else:
            SOUNDS[name] = None

# Загрузка вопросов
def load_questions(grade):
    try:
        # Проверяем наличие файла вопросов
        questions_path = resource_path(f"questions_{grade}.dat")
        
        # Если файл не найден, создаем демо-вопросы
        if not os.path.exists(questions_path):
            return create_demo_questions(grade)
        
        # Загружаем и расшифровываем вопросы
        with open(questions_path, 'rb') as f:
            encrypted = f.read()
        
        # Простая дешифровка
        decoded = base64.b64decode(encrypted)
        decompressed = zlib.decompress(decoded)
        return json.loads(decompressed.decode('utf-8'))
    
    except Exception as e:
        print(f"Ошибка загрузки вопросов: {str(e)}")
        return create_demo_questions(grade)

def create_demo_questions(grade):
    # Вопросы для разных классов
    if grade == 5:
        return [
            {
                "category": "💻 Основы компьютера",
                "question": "1. Что такое монитор?",
                "options": [
                    "a) Устройство для вывода информации",
                    "b) Устройство для ввода информации",
                    "c) Устройство для обработки информации",
                    "d) Устройство для хранения информации"
                ],
                "answer": "a",
                "hint": "На нем мы видим изображение"
            },
            {
                "category": "💾 Информация",
                "question": "2. Как называется устройство для печати?",
                "options": [
                    "a) Сканер",
                    "b) Принтер",
                    "c) Клавиатура",
                    "d) Монитор"
                ],
                "answer": "b",
                "hint": "Оно печатает на бумаге"
            }
        ]
    elif grade == 6:
        return [
            {
                "category": "💻 Аппаратное обеспечение",
                "question": "1. Что такое процессор?",
                "options": [
                    "a) Устройство для хранения информации",
                    "b) Устройство для обработки информации",
                    "c) Устройство для вывода информации",
                    "d) Устройство для ввода информации"
                ],
                "answer": "b",
                "hint": "Часто называют 'мозгом' компьютера"
            },
            {
                "category": "💾 Информация и данные",
                "question": "2. Как называется минимальная единица информации?",
                "options": [
                    "a) Байт",
                    "b) Бит",
                    "c) Килобайт",
                    "d) Мегабайт"
                ],
                "answer": "b",
                "hint": "Может принимать значение 0 или 1"
            }
        ]
    # Добавьте вопросы для других классов по аналогии
    else:  # По умолчанию для 7 класса
        return [
            {
                "category": "💻 Аппаратное обеспечение",
                "question": "1. Что такое ОЗУ?",
                "options": [
                    "a) Постоянное запоминающее устройство",
                    "b) Оперативное запоминающее устройство",
                    "c) Устройство ввода",
                    "d) Устройство вывода"
                ],
                "answer": "b",
                "hint": "Временная память компьютера"
            },
            {
                "category": "💾 Информация и данные",
                "question": "2. Сколько бит в одном байте?",
                "options": [
                    "a) 4",
                    "b) 8",
                    "c) 16",
                    "d) 32"
                ],
                "answer": "b",
                "hint": "Байт может хранить один символ"
            }
        ]

# Создание звездного фона
def create_stars():
    stars = []
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.uniform(0.5, 2)
        speed = random.uniform(0.1, 0.5)
        stars.append([x, y, size, speed])
    return stars

# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 3, border_radius=12)
        
        text_surf = FONT_MEDIUM.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                if SOUNDS.get('click'):
                    SOUNDS['click'].play()
                self.callback()
                return True
        return False

# Основной класс приложения
class TestApp:
    def __init__(self):
        self.current_screen = "main_menu"
        self.score = 0
        self.current_question = 0
        self.hints_left = 3
        self.start_time = time.time()
        self.used_hints = []
        self.user_name = ""
        self.user_class = 7  # Класс по умолчанию
        self.buttons = []
        self.questions = []
        self.name_input = ""
        self.class_input = ""
        self.input_active = True
        self.star_rotation = 0
        self.stars = create_stars()
        self.confetti = []  # Для анимации конфетти
        self.grade_animation_time = 0
        
        self.create_main_menu_buttons()
        
    def create_main_menu_buttons(self):
        self.buttons = [
            Button(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 60, "Начать тест", self.start_test),
            Button(WIDTH//2 - 150, HEIGHT//2 + 30, 300, 60, "Инструкция", self.show_instructions),
            Button(WIDTH//2 - 150, HEIGHT//2 + 110, 300, 60, "Выход", self.quit_app)
        ]
    
    def create_answer_buttons(self):
        self.buttons = []
        options = self.questions[self.current_question]['options']
        for i, option in enumerate(options):
            self.buttons.append(Button(
                WIDTH//2 - 250, 
                300 + i * 80, 
                500, 
                60, 
                option, 
                lambda idx=i: self.check_answer(idx)
            ))
        
        # Кнопка подсказки
        self.buttons.append(Button(
            WIDTH - 200, 
            HEIGHT - 80, 
            180, 
            60, 
            f"Подсказка ({self.hints_left})", 
            self.use_hint
        ))
    
    def start_test(self):
        self.current_screen = "user_info"
        self.name_input = ""
        self.class_input = ""
        self.input_active = True
        self.buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 100, 200, 60, "Начать тест", self.begin_test)
        ]
    
    def begin_test(self):
        if self.name_input.strip() and self.class_input.strip():
            self.user_name = self.name_input.strip()
            try:
                self.user_class = int(self.class_input)
                if self.user_class < 5 or self.user_class > 11:
                    self.user_class = 7
            except:
                self.user_class = 7
                
            self.questions = load_questions(self.user_class)
            self.current_screen = "test"
            self.score = 0
            self.current_question = 0
            self.hints_left = 3
            self.used_hints = []
            self.start_time = time.time()
            self.create_answer_buttons()
    
    def show_instructions(self):
        self.current_screen = "instructions"
        self.buttons = [
            Button(WIDTH//2 - 100, HEIGHT - 100, 200, 60, "Назад", self.show_main_menu)
        ]
    
    def show_main_menu(self):
        self.current_screen = "main_menu"
        self.create_main_menu_buttons()
        self.confetti = []  # Сбрасываем конфетти
    
    def quit_app(self):
        pygame.quit()
        sys.exit()
    
    def use_hint(self):
        if self.hints_left > 0:
            self.hints_left -= 1
            self.used_hints.append(self.current_question)
            if SOUNDS.get('hint'):
                SOUNDS['hint'].play()
            
            # Показываем подсказку
            hint = self.questions[self.current_question]['hint']
            
            # Создаем всплывающее окно с подсказкой
            hint_surf = pygame.Surface((600, 150), pygame.SRCALPHA)
            hint_surf.fill((30, 30, 50, 230))
            pygame.draw.rect(hint_surf, ACCENT_COLOR, hint_surf.get_rect(), 3)
            
            hint_text = FONT_MEDIUM.render(f"💡 Подсказка: {hint}", True, (255, 255, 100))
            hint_rect = hint_text.get_rect(center=(300, 75))
            hint_surf.blit(hint_text, hint_rect)
            
            screen.blit(hint_surf, (WIDTH//2 - 300, HEIGHT//2 - 75))
            pygame.display.flip()
            pygame.time.delay(3000)  # Задержка 3 секунды
    
    def check_answer(self, answer_idx):
        correct_idx = ord(self.questions[self.current_question]['answer']) - ord('a')
        
        if answer_idx == correct_idx:
            self.score += 1
            if SOUNDS.get('correct'):
                SOUNDS['correct'].play()
        else:
            if SOUNDS.get('wrong'):
                SOUNDS['wrong'].play()
        
        # Анимация ответа
        self.animate_answer(answer_idx, answer_idx == correct_idx)
        
        # Переход к следующему вопросу
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.create_answer_buttons()
        else:
            self.complete_test()
    
    def animate_answer(self, answer_idx, is_correct):
        color = (0, 255, 100) if is_correct else (255, 80, 80)
        
        for i in range(30):
            # Анимация звездного фона
            self.draw_stars()
            
            # Рисуем вопрос
            self.draw_question()
            
            # Подсвечиваем ответ
            button = self.buttons[answer_idx]
            pygame.draw.rect(screen, color, button.rect, border_radius=12)
            pygame.draw.rect(screen, ACCENT_COLOR, button.rect, 3, border_radius=12)
            
            # Анимация изменения размера
            size_factor = 1 + i * 0.02
            text_surf = FONT_MEDIUM.render(button.text, True, TEXT_COLOR)
            scaled_surf = pygame.transform.smoothscale(text_surf, 
                                                     (int(text_surf.get_width() * size_factor),
                                                     (int(text_surf.get_height() * size_factor)))
            scaled_rect = scaled_surf.get_rect(center=button.rect.center)
            screen.blit(scaled_surf, scaled_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.time.delay(500)
    
    def complete_test(self):
        self.current_screen = "results"
        total_time = time.time() - self.start_time
        self.test_time = f"{int(total_time // 60)} мин {int(total_time % 60)} сек"
        
        # Сохраняем результаты
        self.save_results()
        
        if SOUNDS.get('complete'):
            SOUNDS['complete'].play()
        
        # Создаем конфетти для анимации
        self.confetti = []
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(-100, -10)
            size = random.randint(5, 15)
            speed = random.uniform(2, 6)
            color = (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255)
            )
            self.confetti.append([x, y, size, speed, color])
        
        self.grade_animation_time = time.time()
        self.buttons = [
            Button(WIDTH//2 - 150, HEIGHT - 100, 300, 60, "Главное меню", self.show_main_menu)
        ]
    
    def update_confetti(self):
        for i, c in enumerate(self.confetti):
            c[1] += c[3]  # Двигаем вниз
            c[0] += random.uniform(-1, 1)  # Случайное смещение по горизонтали
            
            # Если конфетти упало за экран, создаем новое
            if c[1] > HEIGHT + 50:
                c[0] = random.randint(0, WIDTH)
                c[1] = random.randint(-100, -10)
                c[3] = random.uniform(2, 6)
    
    def draw_confetti(self):
        for c in self.confetti:
            pygame.draw.circle(screen, c[4], (int(c[0]), int(c[1])), c[2])
    
    def save_results(self):
        result = {
            "name": self.user_name,
            "class": self.user_class,
            "score": self.score,
            "total": len(self.questions),
            "time": self.test_time,
            "hints_used": len(self.used_hints),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            results_dir = resource_path("results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Создаем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{timestamp}_{self.user_name[:10]}.json"
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения результатов: {str(e)}")
    
    def draw_stars(self):
        # Анимированный звездный фон
        screen.fill(BG_COLOR)
        
        # Рисуем звезды
        self.star_rotation += 0.002
        for star in self.stars:
            x, y, size, speed = star
            # Эффект параллакса
            y = (y + speed * 50 * time.time()) % HEIGHT
            
            # Мерцание
            brightness = 200 + 55 * abs(pygame.math.Vector2(x, y).rotate(self.star_rotation * 100).y) / HEIGHT
            color = (brightness, brightness, brightness)
            
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
    
    def draw_main_menu(self):
        # Заголовок
        title = FONT_LARGE.render("ТЕСТ ПО ИНФОРМАТИКЕ", True, ACCENT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = FONT_MEDIUM.render("для 5-11 классов", True, (200, 200, 255))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 160))
        
        # Рисуем кнопки
        for button in self.buttons:
            button.draw(screen)
    
    def draw_user_info(self):
        # Заголовок
        title = FONT_LARGE.render("РЕГИСТРАЦИЯ УЧАСТНИКА", True, ACCENT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Поле ввода ФИО
        name_label = FONT_MEDIUM.render("Фамилия Имя Отчество:", True, TEXT_COLOR)
        screen.blit(name_label, (WIDTH//2 - 200, 200))
        
        name_rect = pygame.Rect(WIDTH//2 - 200, 240, 400, 50)
        pygame.draw.rect(screen, (40, 60, 100), name_rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT_COLOR, name_rect, 2, border_radius=8)
        
        name_text = FONT_MEDIUM.render(self.name_input, True, TEXT_COLOR)
        screen.blit(name_text, (name_rect.x + 10, name_rect.y + 10))
        
        # Поле ввода класса
        class_label = FONT_MEDIUM.render("Класс (5-11):", True, TEXT_COLOR)
        screen.blit(class_label, (WIDTH//2 - 200, 320))
        
        class_rect = pygame.Rect(WIDTH//2 - 200, 360, 100, 50)
        pygame.draw.rect(screen, (40, 60, 100), class_rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT_COLOR, class_rect, 2, border_radius=8)
        
        class_text = FONT_MEDIUM.render(self.class_input, True, TEXT_COLOR)
        screen.blit(class_text, (class_rect.x + 10, class_rect.y + 10))
        
        # Курсор
        if int(time.time() * 2) % 2 == 0 and self.input_active:
            if self.input_active == "name":
                cursor_pos = name_text.get_rect().right + 15
                pygame.draw.line(screen, TEXT_COLOR, 
                                (name_rect.x + cursor_pos, name_rect.y + 10),
                                (name_rect.x + cursor_pos, name_rect.y + 40), 3)
            elif self.input_active == "class":
                cursor_pos = class_text.get_rect().right + 15
                pygame.draw.line(screen, TEXT_COLOR, 
                                (class_rect.x + cursor_pos, class_rect.y + 10),
                                (class_rect.x + cursor_pos, class_rect.y + 40), 3)
        
        # Рисуем кнопки
        for button in self.buttons:
            button.draw(screen)
    
    def draw_question(self):
        # Заголовок
        category = self.questions[self.current_question]['category']
        category_text = FONT_MEDIUM.render(category, True, ACCENT_COLOR)
        screen.blit(category_text, (WIDTH//2 - category_text.get_width()//2, 100))
        
        # Текст вопроса
        question = self.questions[self.current_question]['question']
        q_text = FONT_MEDIUM.render(question, True, TEXT_COLOR)
        screen.blit(q_text, (WIDTH//2 - q_text.get_width()//2, 180))
        
        # Прогресс
        progress = FONT_SMALL.render(
            f"Вопрос {self.current_question + 1}/{len(self.questions)} | "
            f"Баллы: {self.score} | Подсказок: {self.hints_left}", 
            True, TEXT_COLOR
        )
        screen.blit(progress, (20, 20))
        
        # Рисуем кнопки с вариантами ответов
        for button in self.buttons:
            button.draw(screen)
    
    def draw_results(self):
        # Анимация конфетти
        self.update_confetti()
        self.draw_confetti()
        
        # Полупрозрачный фон для результатов
        result_surf = pygame.Surface((700, 500), pygame.SRCALPHA)
        result_surf.fill((20, 30, 50, 200))
        pygame.draw.rect(result_surf, ACCENT_COLOR, result_surf.get_rect(), 3)
        screen.blit(result_surf, (WIDTH//2 - 350, HEIGHT//2 - 250))
        
        # Заголовок
        title = FONT_LARGE.render("РЕЗУЛЬТАТЫ ТЕСТА", True, ACCENT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 230))
        
        # Имя пользователя
        name_text = FONT_MEDIUM.render(f"Ученик: {self.user_name}", True, TEXT_COLOR)
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2 - 160))
        
        # Класс
        class_text = FONT_MEDIUM.render(f"Класс: {self.user_class}", True, TEXT_COLOR)
        screen.blit(class_text, (WIDTH//2 - class_text.get_width()//2, HEIGHT//2 - 110))
        
        # Результаты
        score_text = FONT_MEDIUM.render(
            f"Правильных ответов: {self.score} из {len(self.questions)}", 
            True, TEXT_COLOR
        )
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 60))
        
        time_text = FONT_MEDIUM.render(f"Затраченное время: {self.test_time}", True, TEXT_COLOR)
        screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2 - 10))
        
        hints_text = FONT_MEDIUM.render(
            f"Использовано подсказок: {len(self.used_hints)}", 
            True, TEXT_COLOR
        )
        screen.blit(hints_text, (WIDTH//2 - hints_text.get_width()//2, HEIGHT//2 + 40))
        
        # Оценка с анимацией
        elapsed = time.time() - self.grade_animation_time
        scale_factor = min(1.0, elapsed * 2)  # Анимация масштабирования
        
        grade = "5️⃣" if self.score >= len(self.questions) * 0.85 else "4️⃣" if self.score >= len(self.questions) * 0.65 else "3️⃣"
        grade_color = (0, 255, 150) if grade == "5️⃣" else (255, 215, 0) if grade == "4️⃣" else (255, 150, 50)
        
        grade_text = FONT_LARGE.render(f"ОЦЕНКА: {grade}", True, grade_color)
        grade_rect = grade_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
        
        # Анимация
        scaled_surf = pygame.transform.smoothscale(
            grade_text, 
            (int(grade_text.get_width() * scale_factor), 
            int(grade_text.get_height() * scale_factor))
        scaled_rect = scaled_surf.get_rect(center=grade_rect.center)
        screen.blit(scaled_surf, scaled_rect)
        
        # Рисуем кнопки
        for button in self.buttons:
            button.draw(screen)
    
    def draw_instructions(self):
        # Заголовок
        title = FONT_LARGE.render("ИНСТРУКЦИЯ", True, ACCENT_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Текст инструкции
        instructions = [
            "Добро пожаловать в тест по информатике!",
            "",
            "📝 Тест содержит вопросы по различным темам",
            "⏱️ На каждый вопрос отводится ограниченное время",
            "💡 У вас есть 3 подсказки, которые можно использовать",
            "   в сложных ситуациях",
            "",
            "🎯 Для выбора ответа нажимайте на кнопки с вариантами",
            "🏆 В конце теста вы получите оценку и сможете",
            "   увидеть свои результаты",
            "",
            "🚀 Удачи в прохождении теста!"
        ]
        
        for i, line in enumerate(instructions):
            text = FONT_SMALL.render(line, True, TEXT_COLOR)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 200 + i * 40))
        
        # Рисуем кнопки
        for button in self.buttons:
            button.draw(screen)
    
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Обработка ввода текста
                if self.current_screen == "user_info" and self.input_active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            # Переключение между полями
                            if self.input_active == "name":
                                self.input_active = "class"
                            else:
                                self.input_active = "name"
                                
                        elif event.key == pygame.K_RETURN:
                            self.begin_test()
                            
                        elif event.key == pygame.K_BACKSPACE:
                            if self.input_active == "name":
                                self.name_input = self.name_input[:-1]
                            elif self.input_active == "class":
                                self.class_input = self.class_input[:-1]
                                
                        else:
                            if self.input_active == "name" and len(self.name_input) < 30:
                                self.name_input += event.unicode
                            elif self.input_active == "class" and len(self.class_input) < 2:
                                if event.unicode.isdigit():
                                    self.class_input += event.unicode
                
                # Обработка кнопок
                for button in self.buttons:
                    button.check_hover(mouse_pos)
                    button.handle_event(event)
            
            # Отрисовка текущего экрана
            self.draw_stars()
            
            if self.current_screen == "main_menu":
                self.draw_main_menu()
            elif self.current_screen == "user_info":
                self.draw_user_info()
            elif self.current_screen == "test":
                self.draw_question()
            elif self.current_screen == "results":
                self.draw_results()
            elif self.current_screen == "instructions":
                self.draw_instructions()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Точка входа
def main():
    try:
        # Загружаем звуки
        load_sounds()
        
        # Запускаем приложение
        app = TestApp()
        app.run()
    except Exception as e:
        # Создаем файл с ошибкой
        error_log = os.path.join(os.path.expanduser("~"), "test_error.log")
        with open(error_log, 'w') as f:
            f.write(f"Ошибка: {str(e)}\n")
            f.write(traceback.format_exc())
        
        # Показываем сообщение об ошибке
        pygame.quit()
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Ошибка приложения", 
                            f"Произошла ошибка в приложении. Детали сохранены в:\n{error_log}\n\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()