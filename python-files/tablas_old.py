import pygame
import sys
import random
import time
import math
import ctypes
from typing import Dict, List, Tuple, Optional

# Bloquear teclas de Windows para evitar trampas
# La constante para la tecla Windows (VK_LWIN = 0x5B, VK_RWIN = 0x5C)
user32 = ctypes.WinDLL('user32', use_last_error=True)
# Bloquear la tecla Windows y Alt+F4
VK_LWIN = 0x5B  # Tecla Windows izquierda
VK_RWIN = 0x5C  # Tecla Windows derecha
VK_F4 = 0x73    # Tecla F4
VK_ALT = 0x12   # Tecla Alt

# Initialize Pygame
pygame.init()
pygame.font.init()

class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (46, 204, 113)
    RED = (231, 76, 60)
    BLUE = (52, 152, 219)
    PURPLE = (142, 68, 173)
    BACKGROUND = (236, 240, 241)
    BUTTON = (52, 73, 94)
    YELLOW = (241, 196, 15)
    ORANGE = (230, 126, 34)
    GRADIENT1 = (52, 152, 219)
    GRADIENT2 = (142, 68, 173)

class MultiplicationGame:
    def __init__(self):
        # Configuración de administrador para salida segura
        self.admin_password = "1245"  # Contraseña que solo el profesor conocerá
        self.admin_mode_active = False
        # Secuencia especial y su tiempo máximo de ejecución
        self.secret_keys = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_p]  # Shift izq + Shift der + p
        self.key_sequence = []  # Para registrar las teclas presionadas en secuencia
        self.keys_pressed = set()  # Para detectar teclas que siguen presionadas
        self.key_sequence_time = 0  # Tiempo cuando se detectó la primera tecla de la secuencia
        self.key_sequence_timeout = 1.5  # Tiempo máximo para completar la secuencia (en segundos)
        self.password_input = ""
        self.showing_password_dialog = False

        # Get the screen info for fullscreen
        screen_info = pygame.display.Info()
        self.width = screen_info.current_w
        self.height = screen_info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        
        # Adjusted font sizes for better fit - con escalado según tamaño de pantalla
        screen_scale = min(self.width, self.height) / 1080  # Factor de escala basado en la resolución
        self.font_large = pygame.font.SysFont('Arial', int(82 * screen_scale))
        self.font = pygame.font.SysFont('Arial', int(64 * screen_scale))
        self.font_small = pygame.font.SysFont('Arial', int(48 * screen_scale))
        # Create a special large font for questions
        self.question_font = pygame.font.SysFont('Arial', int(180 * screen_scale))  # Much larger font for questions
        
        # Adjusted UI element sizes
        self.button_width = int(self.width * 0.35)  # Wider buttons
        self.button_height = 80  # Taller buttons
        self.button_spacing = 100  # Space between buttons
        self.checkbox_size = 60

        self.time_limits = {
            'easy': 8,
            'medium': 5,
            'hard': 3
        }
        self.time_limit = self.time_limits['medium']  # Default to medium
        self.mistakes = []
        self.mistake_counters = {}  # Para llevar el seguimiento de los errores repetidos
        self.required_successes = 3  # Número de éxitos requeridos para considerar una pregunta dominada
        self.current_answer = ""
        self.clock = pygame.time.Clock()
        self.selected_tables = list(range(2, 10))  # Default all tables selected

        # Initialize stars for background animation
        self.stars = [(random.randint(0, self.width), random.randint(0, self.height), 
                       random.randint(2, 5)) for _ in range(20)]
        self.star_speed = 0.5

    def draw_beautiful_background(self):
        # Create gradient background
        for y in range(self.height):
            progress = y / self.height
            color = [int(a + (b - a) * progress) for a, b in 
                    zip(Colors.GRADIENT1, Colors.GRADIENT2)]
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
        
        # Update and draw moving stars
        current_time = time.time()
        for i, (x, y, size) in enumerate(self.stars):
            # Move stars slowly downward
            new_y = (y + self.star_speed) % self.height
            self.stars[i] = (x, new_y, size)
            # Draw star with pulsing effect
            brightness = abs(math.sin(current_time + i))
            star_color = tuple(int(c * brightness) for c in Colors.YELLOW)
            pygame.draw.circle(self.screen, star_color, (int(x), int(new_y)), size)

    def draw_title(self, text, y_pos):
        title_shadow = self.font_large.render(text, True, Colors.BLACK)
        title = self.font_large.render(text, True, Colors.WHITE)
        
        self.screen.blit(title_shadow, (self.width//2 - title.get_width()//2 + 3, y_pos + 3))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, y_pos))

    def draw_button(self, text, y_pos, color=Colors.BUTTON, width=None, height=None):
        if width is None:
            width = self.button_width
        if height is None:
            height = self.button_height
            
        # Draw button shadow
        shadow = pygame.Rect((self.width - width)//2 + 5, y_pos + 5, width, height)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow, border_radius=int(height * 0.3))
        
        # Draw main button with gradient effect
        button = pygame.Rect((self.width - width)//2, y_pos, width, height)
        pygame.draw.rect(self.screen, color, button, border_radius=int(height * 0.3))
        
        # Add highlight effect
        highlight = pygame.Rect((self.width - width)//2, y_pos, width, height//2)
        pygame.draw.rect(self.screen, (*[min(255, c + 30) for c in color], 128), 
                        highlight, border_radius=int(height * 0.3))
        
        # Render text with shadow
        text_shadow = self.font.render(text, True, (0, 0, 0, 128))
        text_surface = self.font.render(text, True, Colors.WHITE)
        
        # Center text with shadow effect
        self.screen.blit(text_shadow, (button.centerx - text_shadow.get_width()//2 + 2, 
                                     button.centery - text_shadow.get_height()//2 + 2))
        self.screen.blit(text_surface, (button.centerx - text_surface.get_width()//2, 
                                      button.centery - text_surface.get_height()//2))
        return button

    def draw_checkbox(self, x, y, text, checked):
        checkbox = pygame.Rect(x, y, self.checkbox_size, self.checkbox_size)
        pygame.draw.rect(self.screen, Colors.BLACK, checkbox, 3)  # Thicker border
        if checked:
            # Larger checkmark
            pygame.draw.line(self.screen, Colors.GREEN, 
                           (x + 10, y + self.checkbox_size//2),
                           (x + self.checkbox_size//3, y + self.checkbox_size - 15), 4)
            pygame.draw.line(self.screen, Colors.GREEN,
                           (x + self.checkbox_size//3, y + self.checkbox_size - 15),
                           (x + self.checkbox_size - 10, y + 15), 4)
        
        text_surface = self.font.render(text, True, Colors.BLACK)
        self.screen.blit(text_surface, (x + self.checkbox_size + 20, y + 5))
        return checkbox

    def draw_timer(self, time_left):
        bar_width = self.width - 100
        height = 40  # Was 30 - made timer bar taller
        pygame.draw.rect(self.screen, Colors.RED, (50, 20, bar_width, height))
        pygame.draw.rect(self.screen, Colors.GREEN, 
                        (50, 20, bar_width * (time_left/self.time_limit), height))

    def ask_question(self, num1, num2):
        start_time = time.time()
        self.current_answer = ""
        
        while True:
            time_left = max(0, self.time_limit - (time.time() - start_time))
            
            if time_left == 0:
                self.mistakes.append((num1, num2, num1 * num2))
                return False

            self.draw_beautiful_background()
            self.draw_timer(time_left)
            
            # Render question with much larger size - ajustado para evitar amontonamiento
            question = self.question_font.render(f"{num1}", True, Colors.BLACK)
            times = self.question_font.render("×", True, Colors.BLACK)
            num2_text = self.question_font.render(f"{num2}", True, Colors.BLACK)
            equals = self.question_font.render("=", True, Colors.BLACK)
            answer = self.question_font.render(self.current_answer if self.current_answer else "_", True, Colors.BLUE)
            
            # Calculate total width with proper spacing - ajustado para evitar amontonamiento
            spacing = max(60, int(self.width * 0.02))  # Spacing adaptive to screen width
            
            # Comprobar si el contenido cabe en la pantalla
            total_width = (question.get_width() + times.get_width() + num2_text.get_width() + 
                         equals.get_width() + answer.get_width() + spacing * 4)
            
            # Si el contenido es demasiado ancho, ajustar el espaciado
            if total_width > self.width * 0.95:
                spacing = max(30, int((self.width * 0.95 - question.get_width() - times.get_width() - 
                             num2_text.get_width() - equals.get_width() - answer.get_width()) / 4))
                total_width = (question.get_width() + times.get_width() + num2_text.get_width() + 
                             equals.get_width() + answer.get_width() + spacing * 4)
            
            # Center everything
            start_x = (self.width - total_width) // 2
            center_y = (self.height - question.get_height()) // 2
              # Draw each part with proper spacing
            self.screen.blit(question, (start_x, center_y))
            self.screen.blit(times, (start_x + question.get_width() + spacing, center_y))
            self.screen.blit(num2_text, (start_x + question.get_width() + times.get_width() + spacing * 2, center_y))
            self.screen.blit(equals, (start_x + question.get_width() + times.get_width() + 
                                    num2_text.get_width() + spacing * 3, center_y))
            self.screen.blit(answer, (start_x + question.get_width() + times.get_width() + 
                                    num2_text.get_width() + equals.get_width() + spacing * 4, center_y))
            
            pygame.display.flip()
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        try:
                            if int(self.current_answer) == num1 * num2:
                                return True
                            self.mistakes.append((num1, num2, num1 * num2))
                            return False
                        except ValueError:
                            self.mistakes.append((num1, num2, num1 * num2))
                            return False
                    elif event.key == pygame.K_BACKSPACE:
                        self.current_answer = self.current_answer[:-1]
                    elif event.unicode.isnumeric():
                        self.current_answer += event.unicode

    def show_results(self, from_practice=False):
        self.draw_beautiful_background()
        y_pos = self.height * 0.1

        if not self.mistakes:
            self.draw_title("¡¡¡FELICIDADES!!!", y_pos)
            text = self.font.render("¡Eres un genio de las matemáticas! 🌟", True, Colors.PURPLE)
            self.screen.blit(text, (self.width//2 - text.get_width()//2, y_pos + 80))
        else:
            self.draw_title("Repasa estos ejercicios", y_pos)
            y_pos += 60
            
            # Mostrar errores en una disposición más espaciada
            items_per_row = 3
            horizontal_spacing = self.width // (items_per_row + 1)
            vertical_spacing = 40
            
            for i, (num1, num2, result) in enumerate(self.mistakes):
                row = i // items_per_row
                col = i % items_per_row
                x = (col + 1) * horizontal_spacing - horizontal_spacing // 2
                y = y_pos + row * vertical_spacing
                
                text = self.font_small.render(f"{num1} × {num2} = {result}", True, Colors.BLACK)
                self.screen.blit(text, (x - text.get_width() // 2, y))

        practice_button = self.draw_button("Practicar Errores", self.height - 150, Colors.BLUE)
        
        # En modo práctica, no mostramos el botón de menú principal para evitar que salgan sin completar
        if from_practice:
            pygame.display.flip()
            return 0  # Forzar a que siempre practiquen los errores
        else:
            menu_button = self.draw_button("Menú Principal", self.height - 80, Colors.PURPLE)
            pygame.display.flip()
            return self.wait_for_button_click([practice_button, menu_button])

    def wait_for_button_click(self, buttons):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for i, button in enumerate(buttons):
                        if button.collidepoint(pos):
                            return i

    def select_tables(self):
        checkboxes = {}
        selected = self.selected_tables.copy()
        
        while True:
            self.draw_beautiful_background()
            self.draw_title("Selecciona las Tablas", self.height * 0.08)
            
            # Adjusted grid layout
            grid_width = self.width * 0.9
            grid_height = self.height * 0.6
            grid_start_x = (self.width - grid_width) // 2
            grid_start_y = self.height * 0.22
            
            # "Select All" checkbox with better positioning
            all_selected = len(selected) == 8
            all_checkbox_y = grid_start_y - 100
            checkboxes["all"] = self.draw_checkbox(
                self.width//2 - 200, all_checkbox_y, "Todas las Tablas", all_selected)
            
            # Improved grid spacing
            horizontal_spacing = grid_width // 4
            vertical_spacing = grid_height // 2
            
            for i, num in enumerate(range(2, 10)):
                row = i // 4
                col = i % 4
                x = grid_start_x + (col * horizontal_spacing)
                y = grid_start_y + (row * vertical_spacing)
                checkboxes[num] = self.draw_checkbox(x, y, f"Tabla del {num}", num in selected)
            
            # Better positioned start button
            button_y = self.height * 0.85
            start_button = self.draw_button("Comenzar", button_y, 
                                          Colors.GREEN if selected else Colors.BUTTON)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if start_button.collidepoint(pos) and selected:
                        self.selected_tables = selected
                        return
                    
                    for num, rect in checkboxes.items():
                        if rect.collidepoint(pos):
                            if num == "all":
                                if all_selected:
                                    selected = []
                                else:
                                    selected = list(range(2, 10))
                            else:
                                if num in selected:
                                    selected.remove(num)
                                else:
                                    selected.append(num)

    def select_difficulty(self):
        while True:
            self.draw_beautiful_background()
            self.draw_title("Selecciona la Dificultad", self.height * 0.1)
            
            # Draw difficulty buttons
            easy_button = self.draw_button("Fácil (8s)", self.height * 0.4, Colors.GREEN)
            medium_button = self.draw_button("Intermedio (5s)", self.height * 0.5, Colors.BLUE)
            hard_button = self.draw_button("Difícil (3s)", self.height * 0.6, Colors.RED)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if easy_button.collidepoint(pos):
                        self.time_limit = self.time_limits['easy']
                        return
                    elif medium_button.collidepoint(pos):
                        self.time_limit = self.time_limits['medium']
                        return
                    elif hard_button.collidepoint(pos):
                        self.time_limit = self.time_limits['hard']
                        return

    def show_countdown(self):
        # Create a larger countdown font
        countdown_font = pygame.font.SysFont('Arial', 300)  # Larger font for countdown
        countdown_font_small = pygame.font.SysFont('Arial', 150)  # Smaller version
        
        # Count from 4 to 1
        for i in range(4, 0, -1):
            self.draw_beautiful_background()
            self.draw_title("¡Prepárate!", self.height * 0.1)
            
            # Small countdown first
            small_text = countdown_font_small.render(str(i), True, Colors.BLACK)
            self.screen.blit(small_text, (self.width//2 - small_text.get_width()//2, 
                                       self.height//2 - small_text.get_height()//2))
            pygame.display.flip()
            pygame.time.delay(300)  # Show small version briefly
            
            # Then large countdown with animation
            for scale in range(80, 101, 5):  # Animation effect (80% to 100% size)
                size = int(300 * scale / 100)
                countdown_font_anim = pygame.font.SysFont('Arial', size)
                
                self.draw_beautiful_background()
                self.draw_title("¡Prepárate!", self.height * 0.1)
                
                count_text = countdown_font_anim.render(str(i), True, Colors.BLACK)
                self.screen.blit(count_text, (self.width//2 - count_text.get_width()//2, 
                                           self.height//2 - count_text.get_height()//2))
                
                pygame.display.flip()
                pygame.time.delay(50)
            
            # Hold the number briefly
            pygame.time.delay(400)
          # Show "¡Comienza!" message
        self.draw_beautiful_background()
        start_text = self.font_large.render("¡COMIENZA!", True, Colors.GREEN)
        self.screen.blit(start_text, (self.width//2 - start_text.get_width()//2, 
                                   self.height//2 - start_text.get_height()//2))
        pygame.display.flip()
        pygame.time.delay(700)
        
    def play_game(self):
        self.mistakes = []
        questions = [(n, m) for n in self.selected_tables 
                    for m in range(1, 11)]
        random.shuffle(questions)
        # Add countdown before starting
        self.show_countdown()
        for num1, num2 in questions:
            if self.ask_question(num1, num2):
                self.show_feedback(True)
            else:
                self.show_feedback(False)
            pygame.time.delay(500)

        # Si hay errores, forzar el modo práctica sin opción de volver al menú
        if self.mistakes:
            self.show_results(True)  # Usar from_practice=True para forzar solo botón de práctica
            self.practice_mode()
        else:
            # Solo mostrar la opción de volver al menú si no hay errores
            self.show_results(False)

    def practice_mode(self):
        if not self.mistakes:
            return
        
        # Inicializar el contador de errores si no existe
        if not self.mistake_counters:
            for num1, num2, result in self.mistakes:
                # Clave única para cada ejercicio
                exercise_key = f"{num1}x{num2}"
                self.mistake_counters[exercise_key] = {
                    "correct_count": 0,
                    "total_attempts": 0
                }
                
        # Mientras haya errores por practicar
        while True:
            self.draw_beautiful_background()
            self.draw_title("Domina estos ejercicios:", self.height * 0.1)
            
            # Calcular el espaciado en función del tamaño de la pantalla y el número de errores
            available_height = self.height * 0.6
            spacing = min(100, available_height / (len(self.mistakes) + 1))
            y_pos = self.height * 0.2
              # Dibujar cada ejercicio con su estado de dominio en una cuadrícula para evitar amontonamiento
            items_per_row = min(3, len(self.mistakes))
            if items_per_row > 0:  # Evitar división por cero
                horizontal_spacing = self.width // (items_per_row + 1)
                for i, (num1, num2, result) in enumerate(self.mistakes):
                    exercise_key = f"{num1}x{num2}"
                    # Asegurarse de que el exercise_key existe en mistake_counters
                    if exercise_key not in self.mistake_counters:
                        self.mistake_counters[exercise_key] = {
                            "correct_count": 0,
                            "total_attempts": 0
                        }
                    correct_count = self.mistake_counters[exercise_key]["correct_count"]
                    
                    # Crear texto con información del progreso
                    progress_text = f" ({correct_count}/{self.required_successes})"
                    
                    # El color del texto depende del progreso
                    if correct_count == 0:
                        text_color = Colors.RED
                    elif correct_count < self.required_successes:
                        text_color = Colors.YELLOW
                    else:
                        text_color = Colors.GREEN
                    
                    # Posición en cuadrícula
                    row = i // items_per_row
                    col = i % items_per_row
                    x_pos = (col + 1) * horizontal_spacing - horizontal_spacing // 2
                    y_current = y_pos + row * spacing
                    
                    # Preparar el texto
                    text = self.font.render(f"{num1} × {num2} = {result}{progress_text}", True, text_color)
                    shadow_text = self.font.render(f"{num1} × {num2} = {result}{progress_text}", True, Colors.BLACK)
                    
                    text_width = text.get_width()
                    text_x = x_pos - text_width // 2
                    
                    # Dibujar texto con sombra
                    self.screen.blit(shadow_text, (text_x + 2, y_current + 2))
                    self.screen.blit(text, (text_x, y_current))
                    
                    # Dibujar subrayado con efecto de degradado
                    line_y = y_current + text.get_height() + 5
                    line_width = text_width + 20  # Extender línea más allá del texto
                    line_x = text_x - 10
                    
                    for j in range(line_width):
                        progress = j / line_width
                        alpha = int(255 * (1 - abs(2 * progress - 1)))  # Desvanecer en los bordes
                        pygame.draw.line(self.screen, (*Colors.WHITE, alpha),
                                      (line_x + j, line_y),
                                      (line_x + j, line_y), 2)
            
            # Información de instrucciones
            info_text = self.font_small.render("Debes responder correctamente 3 veces cada ejercicio para dominarlo", True, Colors.WHITE)
            self.screen.blit(info_text, (self.width//2 - info_text.get_width()//2, self.height - 220))
            
            # Información adicional sobre el orden aleatorio
            info_text2 = self.font_small.render("Los ejercicios se repetirán 3 veces en orden aleatorio", True, Colors.YELLOW)
            self.screen.blit(info_text2, (self.width//2 - info_text2.get_width()//2, self.height - 180))
            
            continue_button = self.draw_button("Practicar", self.height - 120, Colors.GREEN)
            pygame.display.flip()
            self.clock.tick(30)
            
            # Esperar clic en el botón
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if continue_button.collidepoint(event.pos):
                            waiting = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            # Practicar los ejercicios que aún no están dominados
            pending_questions = []
            
            # Seleccionar solo los ejercicios que aún no se han dominado
            for num1, num2, _ in self.mistakes:
                exercise_key = f"{num1}x{num2}"
                if self.mistake_counters[exercise_key]["correct_count"] < self.required_successes:
                    # Agregar cada ejercicio 3 veces para asegurar que se repita
                    for _ in range(3):
                        pending_questions.append((num1, num2))
            
            # Mezclar los ejercicios para que aparezcan en orden aleatorio
            random.shuffle(pending_questions)
              # Si no hay más ejercicios pendientes, terminar
            if not pending_questions:
                self.draw_beautiful_background()
                text = self.font_large.render("¡Excelente! ¡Has dominado todos los ejercicios! 🎉", True, Colors.GREEN)
                self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2))
                pygame.display.flip()
                pygame.time.delay(2000)
                break
              # Practicar los ejercicios pendientes en orden aleatorio
            for num1, num2 in pending_questions:
                exercise_key = f"{num1}x{num2}"
                
                # Asegurarse de que el exercise_key existe en mistake_counters
                if exercise_key not in self.mistake_counters:
                    self.mistake_counters[exercise_key] = {
                        "correct_count": 0,
                        "total_attempts": 0
                    }
                
                # Mostrar información del progreso antes de la pregunta
                self.draw_beautiful_background()
                progress_info = self.font.render(
                    f"Ejercicio: {num1} × {num2} - Progreso: {self.mistake_counters[exercise_key]['correct_count']}/{self.required_successes}", 
                    True, Colors.WHITE
                )
                self.screen.blit(progress_info, (self.width//2 - progress_info.get_width()//2, self.height * 0.2))
                pygame.display.flip()
                pygame.time.delay(1000)  # Mostrar durante 1 segundo
                  # Hacer la pregunta
                if self.ask_question(num1, num2):
                    # Respuesta correcta, incrementar contador
                    # Asegurarse de que el exercise_key existe en mistake_counters
                    if exercise_key not in self.mistake_counters:
                        self.mistake_counters[exercise_key] = {
                            "correct_count": 0,
                            "total_attempts": 0
                        }
                    self.mistake_counters[exercise_key]["correct_count"] += 1
                    self.show_feedback(True)
                else:
                    # Respuesta incorrecta, reiniciar contador
                    # Asegurarse de que el exercise_key existe en mistake_counters
                    if exercise_key not in self.mistake_counters:
                        self.mistake_counters[exercise_key] = {
                            "correct_count": 0,
                            "total_attempts": 0
                        }
                    self.mistake_counters[exercise_key]["correct_count"] = 0
                    self.show_feedback(False)
                
                self.mistake_counters[exercise_key]["total_attempts"] += 1
                pygame.time.delay(500)
                
            # Actualizar la lista de ejercicios con problema
            self.mistakes = []
            # Usar un conjunto para evitar duplicados en la lista de ejercicios
            processed_exercises = set()
            
            # Recopilar los ejercicios únicos que aún no se han dominado
            for num1, num2 in pending_questions:
                exercise_key = f"{num1}x{num2}"
                # Evitar procesar el mismo ejercicio más de una vez
                if exercise_key not in processed_exercises and self.mistake_counters[exercise_key]["correct_count"] < self.required_successes:
                    self.mistakes.append((num1, num2, num1 * num2))
                    processed_exercises.add(exercise_key)
                    
            # Si no hay más errores, terminar
            if not self.mistakes:
                break

    def draw_password_dialog(self):
        # Fondo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Negro semi-transparente
        self.screen.blit(overlay, (0, 0))
        
        # Dibujar el cuadro de diálogo
        dialog_width = int(self.width * 0.5)
        dialog_height = int(self.height * 0.3)
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Fondo del diálogo
        pygame.draw.rect(self.screen, Colors.BACKGROUND, 
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        border_radius=15)
        
        # Borde del diálogo
        pygame.draw.rect(self.screen, Colors.BLUE, 
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        width=3, border_radius=15)
        
        # Título
        title_text = self.font.render("Modo Administrador", True, Colors.BLACK)
        self.screen.blit(title_text, 
                        (dialog_x + (dialog_width - title_text.get_width()) // 2,
                         dialog_y + 30))
        
        # Indicación
        instruction_text = self.font_small.render("Ingrese la contraseña:", True, Colors.BLACK)
        self.screen.blit(instruction_text, 
                        (dialog_x + (dialog_width - instruction_text.get_width()) // 2,
                         dialog_y + 90))
          # Campo de contraseña
        password_display = "*" * len(self.password_input)
        password_text = self.font.render(password_display, True, Colors.BLUE)
        pygame.draw.rect(self.screen, Colors.WHITE,
                        (dialog_x + 50, dialog_y + 140, dialog_width - 100, 60),
                        border_radius=10)
        pygame.draw.rect(self.screen, Colors.BLACK, 
                        (dialog_x + 50, dialog_y + 140, dialog_width - 100, 60),
                        width=2, border_radius=10)
        self.screen.blit(password_text, 
                        (dialog_x + (dialog_width - password_text.get_width()) // 2,
                         dialog_y + 150))
                         
    def show_feedback(self, correct):
        text = "¡Muy bien! 👍" if correct else "¡Incorrecto! 😢"
        color = Colors.GREEN if correct else Colors.RED
        
        feedback = self.font.render(text, True, color)
        self.screen.blit(feedback, (self.width//2 - feedback.get_width()//2, 300))
        pygame.display.flip()
        
    def check_admin_password(self):
        if self.password_input == self.admin_password:
            self.showing_password_dialog = False
            self.admin_mode_active = True
            return True
        else:
            self.password_input = ""  # Limpiar entrada errónea
            return False
    
    def process_special_keys(self, event):
        current_time = time.time()
        
        # Detectar la secuencia especial del administrador (Shift izq + Shift der + P)
        if event.type == pygame.KEYDOWN:
            # Registrar la tecla presionada
            self.keys_pressed.add(event.key)
            
            # Si es la primera tecla de la secuencia o parte de la secuencia y está en el orden correcto
            if event.key in self.secret_keys:
                # Si es la primera tecla o si la secuencia está vacía, registra el tiempo
                if not self.key_sequence:
                    self.key_sequence_time = current_time
                
                # Si no está en la secuencia actual y corresponde a la siguiente tecla esperada
                if (event.key not in self.key_sequence and 
                    len(self.key_sequence) < len(self.secret_keys) and 
                    event.key == self.secret_keys[len(self.key_sequence)]):
                    self.key_sequence.append(event.key)
                
                # Si completamos la secuencia correcta dentro del tiempo límite
                if (len(self.key_sequence) == len(self.secret_keys) and 
                    self.key_sequence == self.secret_keys and
                    current_time - self.key_sequence_time <= self.key_sequence_timeout):
                    self.showing_password_dialog = True
                    self.password_input = ""
                    # Reiniciar la secuencia
                    self.key_sequence = []
            
            # Si se presiona cualquier otra tecla, reiniciar la secuencia
            elif event.key not in self.secret_keys:
                self.key_sequence = []
        
        # Manejar la liberación de teclas
        if event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)
            
        # Verificar si se ha excedido el tiempo límite para la secuencia
        if self.key_sequence and current_time - self.key_sequence_time > self.key_sequence_timeout:
            self.key_sequence = []  # Reiniciar la secuencia si se excede el tiempo
                
        # Si el diálogo de contraseña está activo, procesar entradas
        if self.showing_password_dialog:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    return self.check_admin_password()
                elif event.key == pygame.K_BACKSPACE:
                    self.password_input = self.password_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.showing_password_dialog = False
                    self.password_input = ""
                elif event.unicode.isprintable():  # Aceptar cualquier caracter imprimible
                    self.password_input += event.unicode
            return True  # Consumir el evento si estamos en el diálogo de contraseña
        return False

    def run(self):
        while True:
            self.draw_beautiful_background()
            self.draw_title("Tablas de Multiplicar", self.height * 0.1)
            
            # Buttons with proper spacing
            y_start = self.height * 0.3
            select_button = self.draw_button("Modo Práctica", y_start, Colors.GREEN)
            competition_button = self.draw_button("Modo Competencia", 
                                              y_start + self.button_spacing, Colors.BLUE)
            difficulty_button = self.draw_button("Seleccionar Dificultad", 
                                              y_start + self.button_spacing * 2, Colors.PURPLE)
            quit_button = self.draw_button("Salir", 
                                         y_start + self.button_spacing * 3, Colors.RED)
            
            if self.showing_password_dialog:
                self.draw_password_dialog()
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                # Procesar secuencia especial y diálogo de contraseña
                if self.process_special_keys(event):
                    continue
                    
                if event.type == pygame.QUIT:
                    if self.admin_mode_active:
                        pygame.quit()
                        sys.exit()
                    # Si no está en modo admin, ignorar el evento de cierre
                
                if event.type == pygame.KEYDOWN:
                    # Solo permitir salir con ESC si está en modo admin
                    if event.key == pygame.K_ESCAPE and self.admin_mode_active:
                        pygame.quit()
                        sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.showing_password_dialog:
                    pos = pygame.mouse.get_pos()
                    if select_button.collidepoint(pos):
                        self.select_tables()
                        self.play_game()
                    elif competition_button.collidepoint(pos):
                        self.configure_competition()
                    elif difficulty_button.collidepoint(pos):
                        self.select_difficulty()
                    elif quit_button.collidepoint(pos):
                        if self.admin_mode_active:  # Solo permitir salir en modo admin
                            pygame.quit()
                            sys.exit()
                        else:  # Si no es admin, mostrar mensaje
                            warning_text = self.font.render("¡Solo el profesor puede salir del programa!", True, Colors.RED)
                            self.screen.blit(warning_text, (self.width//2 - warning_text.get_width()//2, self.height * 0.8))
                            pygame.display.flip()
                            pygame.time.delay(1500)  # Mostrar mensaje por 1.5 segundos

        pygame.quit()
        
    def configure_competition(self):
        # Inicializar variables de competencia
        self.player_count = 2  # Default number of players
        self.player_names = ["Jugador 1", "Jugador 2"]
        self.current_player = 0
        self.player_scores = [0] * self.player_count
        self.player_mistakes = [[] for _ in range(self.player_count)]
        self.player_finished = [False] * self.player_count
        self.competition_questions = []
        
        # Set up competition
        self.select_difficulty()  # Primero configuramos la dificultad
        
        # Configure number of players
        self.select_player_count()
        
        # Configure player names
        self.enter_player_names()
        
        # Select tables for competition
        self.select_tables()
        
        # Start the competition
        self.start_competition()
    
    def select_player_count(self):
        while True:
            self.draw_beautiful_background()
            self.draw_title("¿Cuántos jugadores?", self.height * 0.1)
            
            # Draw player count options
            two_button = self.draw_button("2 Jugadores", self.height * 0.35, Colors.GREEN)
            three_button = self.draw_button("3 Jugadores", self.height * 0.45, Colors.BLUE)
            four_button = self.draw_button("4 Jugadores", self.height * 0.55, Colors.YELLOW)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if two_button.collidepoint(pos):
                        self.player_count = 2
                        self.player_names = ["Jugador 1", "Jugador 2"]
                        self.player_scores = [0] * self.player_count
                        self.player_mistakes = [[] for _ in range(self.player_count)]
                        self.player_finished = [False] * self.player_count
                        return
                    elif three_button.collidepoint(pos):
                        self.player_count = 3
                        self.player_names = ["Jugador 1", "Jugador 2", "Jugador 3"]
                        self.player_scores = [0] * self.player_count
                        self.player_mistakes = [[] for _ in range(self.player_count)]
                        self.player_finished = [False] * self.player_count
                        return
                    elif four_button.collidepoint(pos):
                        self.player_count = 4
                        self.player_names = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
                        self.player_scores = [0] * self.player_count
                        self.player_mistakes = [[] for _ in range(self.player_count)]
                        self.player_finished = [False] * self.player_count
                        return
    
    def enter_player_names(self):
        for i in range(self.player_count):
            name = self.get_player_name(i)
            if name:  # Si se proporciona un nombre
                self.player_names[i] = name
    
    def get_player_name(self, player_index):
        name_input = ""
        
        while True:
            self.draw_beautiful_background()
            self.draw_title(f"Nombre del Jugador {player_index + 1}", self.height * 0.15)
            
            # Draw text input field
            input_width = 600
            input_height = 80
            input_x = (self.width - input_width) // 2
            input_y = self.height * 0.4
            
            pygame.draw.rect(self.screen, Colors.WHITE, 
                           (input_x, input_y, input_width, input_height), 
                           border_radius=15)
            pygame.draw.rect(self.screen, Colors.BLACK, 
                           (input_x, input_y, input_width, input_height), 
                           width=3, border_radius=15)
            
            if name_input:
                text_surface = self.font.render(name_input, True, Colors.BLUE)
            else:
                text_surface = self.font.render(f"Jugador {player_index + 1}", True, Colors.GRAY)
            
            self.screen.blit(text_surface, 
                           (input_x + 20, input_y + (input_height - text_surface.get_height()) // 2))
            
            # Draw continue button
            continue_button = self.draw_button("Continuar", self.height * 0.6, Colors.GREEN)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        return name_input if name_input else f"Jugador {player_index + 1}"
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    elif event.unicode.isprintable():
                        name_input += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button.collidepoint(event.pos):
                        return name_input if name_input else f"Jugador {player_index + 1}"
    
    def start_competition(self):
        # Generate questions for competition
        self.competition_questions = [(n, m) for n in self.selected_tables 
                                    for m in range(1, 6)]  # Half the questions compared to practice mode
        
        # Shuffle the questions
        random.shuffle(self.competition_questions)
        
        # Start the competition countdown
        self.show_competition_countdown()
        
        # Cycle through players until all have finished
        game_complete = False
        while not game_complete:
            # If current player has already finished, move to next
            if self.player_finished[self.current_player]:
                self.current_player = (self.current_player + 1) % self.player_count
                continue
                
            # Show player turn
            self.show_player_turn()
            
            # Let the player answer questions
            if not self.play_competition_round():
                # Player made a mistake, reset their progress
                self.player_mistakes[self.current_player] = []
                self.player_scores[self.current_player] = 0
                
                # Show feedback that the player needs to start over
                self.show_restart_feedback()
            else:
                # Player completed all questions!
                self.player_finished[self.current_player] = True
                
            # Check if all players have finished
            game_complete = all(self.player_finished)
            
            # Move to the next player
            self.current_player = (self.current_player + 1) % self.player_count
        
        # Show final results
        self.show_competition_results()
    
    def show_competition_countdown(self):
        # Create countdown text
        self.draw_beautiful_background()
        self.draw_title("¡Competencia de Multiplicación!", self.height * 0.1)
        
        # Explain the rules
        rules = [
            "Cada jugador resolverá las mismas preguntas en su turno.",
            "Si cometes un error, tendrás que empezar de nuevo.",
            "¡El primero en completar todas las preguntas gana!",
            "Todos los jugadores deben responder las mismas preguntas."
        ]
        
        for i, rule in enumerate(rules):
            rule_text = self.font_small.render(rule, True, Colors.WHITE)
            self.screen.blit(rule_text, (self.width//2 - rule_text.get_width()//2, 
                                      self.height * 0.25 + i * 50))
        
        # Show start button
        start_button = self.draw_button("¡Comenzar!", self.height * 0.6, Colors.GREEN)
        pygame.display.flip()
        
        # Wait for button click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        waiting = False
        
        # Show the actual countdown
        self.show_countdown()
    
    def show_player_turn(self):
        self.draw_beautiful_background()
        
        # Show player name
        player_text = self.font_large.render(f"Turno: {self.player_names[self.current_player]}", True, Colors.WHITE)
        self.screen.blit(player_text, (self.width//2 - player_text.get_width()//2, self.height * 0.3))
        
        # Show player score
        score_text = self.font.render(f"Preguntas respondidas: {self.player_scores[self.current_player]}/{len(self.competition_questions)}", 
                                    True, Colors.YELLOW)
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height * 0.4))
        
        pygame.display.flip()
        pygame.time.delay(2000)  # Show for 2 seconds
    
    def play_competition_round(self):
        # Start from where the player left off
        start_index = self.player_scores[self.current_player]
        
        for i in range(start_index, len(self.competition_questions)):
            num1, num2 = self.competition_questions[i]
            
            # Display player progress
            self.draw_beautiful_background()
            
            # Show player name and progress
            player_text = self.font.render(f"{self.player_names[self.current_player]}", True, Colors.WHITE)
            self.screen.blit(player_text, (self.width - player_text.get_width() - 20, 20))
            
            progress_text = self.font_small.render(f"Pregunta {i+1}/{len(self.competition_questions)}", True, Colors.WHITE)
            self.screen.blit(progress_text, (20, 20))
            
            pygame.display.flip()
            pygame.time.delay(500)  # Brief pause before question
            
            # Ask the question
            if self.ask_question(num1, num2):
                # Correct answer
                self.player_scores[self.current_player] += 1
                self.show_feedback(True)
            else:
                # Wrong answer - add to mistakes and return False (player needs to start over)
                self.player_mistakes[self.current_player].append((num1, num2, num1 * num2))
                self.show_feedback(False)
                return False
            
            pygame.time.delay(500)
        
        # Player completed all questions successfully
        return True
    
    def show_restart_feedback(self):
        self.draw_beautiful_background()
        
        # Show feedback messages
        wrong_text = self.font_large.render("¡Respuesta Incorrecta!", True, Colors.RED)
        restart_text = self.font.render("Debes volver a empezar", True, Colors.WHITE)
        
        self.screen.blit(wrong_text, (self.width//2 - wrong_text.get_width()//2, self.height * 0.3))
        self.screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.height * 0.4))
        
        pygame.display.flip()
        pygame.time.delay(2500)  # Show for 2.5 seconds
    
    def show_competition_results(self):
        self.draw_beautiful_background()
        self.draw_title("¡Competencia Finalizada!", self.height * 0.1)
        
        # Find the highest score
        max_score = max(self.player_scores)
        winners = [i for i, score in enumerate(self.player_scores) if score == max_score]
        
        # Display winner(s)
        if len(winners) == 1:
            winner_text = self.font_large.render(f"¡{self.player_names[winners[0]]} Gana!", True, Colors.GREEN)
            self.screen.blit(winner_text, (self.width//2 - winner_text.get_width()//2, self.height * 0.25))
        else:
            # Multiple winners (tie)
            winner_text = self.font_large.render("¡Empate!", True, Colors.YELLOW)
            self.screen.blit(winner_text, (self.width//2 - winner_text.get_width()//2, self.height * 0.25))
            
            tie_names = [self.player_names[i] for i in winners]
            tie_text = self.font.render(" y ".join(tie_names), True, Colors.WHITE)
            self.screen.blit(tie_text, (self.width//2 - tie_text.get_width()//2, self.height * 0.35))
        
        # Show all player results
        y_pos = self.height * 0.5
        for i, player_name in enumerate(self.player_names):
            color = Colors.GREEN if i in winners else Colors.WHITE
            result_text = self.font.render(f"{player_name}: {self.player_scores[i]}/{len(self.competition_questions)} preguntas", 
                                        True, color)
            self.screen.blit(result_text, (self.width//2 - result_text.get_width()//2, y_pos))
            y_pos += 60
        
        # Show continue button
        continue_button = self.draw_button("Menú Principal", self.height * 0.8, Colors.BLUE)
        
        pygame.display.flip()
        
        # Wait for button click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button.collidepoint(event.pos):
                        waiting = False

# Iniciar el juego
if __name__ == "__main__":
    game = MultiplicationGame()
    game.run()
