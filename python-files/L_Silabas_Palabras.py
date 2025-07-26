import pygame
import math
import pyphen
import PyPDF2
from tkinter import Tk, filedialog, simpledialog
import pyttsx3
import random
from PIL import Image
import re
import json
import os

# Inicializar pygame
pygame.init()

# Configuración de idioma para separación de sílabas
dic = pyphen.Pyphen(lang='es_ES')

# Inicializar el motor de síntesis de voz
engine = pyttsx3.init()
engine.setProperty('rate', 120)  # Velocidad del habla
engine.setProperty('volume', 2)  # Volumen

# Función para sanitizar nombres de archivo
def sanitize_filename(filename):
    """Eliminar caracteres no válidos para nombres de archivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.replace(' ', '_').strip()

# Función para destacar sílabas mientras se lee en voz alta
def highlight_syllables_while_reading(surface, sentence, x_start, y_start):
    """Resaltar cada sílaba mientras se lee en voz alta, respetando líneas múltiples."""
    words_with_syllables = process_sentence(sentence)
    max_width = screen_width - 100
    lines = wrap_sentence_to_lines(words_with_syllables, max_width, font)
    line_height = font_size + 60

    for line_index, line_syllables in enumerate(lines):
        line_width = calculate_sentence_width(line_syllables, font)
        x_start = (screen_width - line_width) // 2
        x = x_start
        for word_syllables in line_syllables:
            for syllable in word_syllables:
                surface.blit(background, (0, 0)) if 'background' in globals() else surface.fill((200, 200, 200))
                for li, ls in enumerate(lines):
                    lx = (screen_width - calculate_sentence_width(ls, font)) // 2
                    ly = y_start + li * line_height + y_offset
                    for ws in ls:
                        for s in ws:
                            color = RED if (re.match(r'^[¡¿.,;!?]+$', s) or re.search(r'[áéíóúÁÉÍÓÚ]', s)) else BLUE
                            if s == syllable and li == line_index:
                                pygame.draw.rect(surface, (255, 255, 0, 100), (lx, ly, font.size(s)[0], font_size), 0)
                                color = (255, 255, 0)
                            cache_key = (s, zoom_level, tuple(color))
                            if cache_key not in text_cache:
                                text_cache[cache_key] = font.render(s, True, color)
                            shadow_surface = font.render(s, True, BLACK)
                            surface.blit(shadow_surface, (lx + 2, ly + 2))
                            surface.blit(text_cache[cache_key], (lx, ly))
                            lx += font.size(s)[0]
                        lx += font.size(" ")[0]
                    draw_curves(surface, ls, (screen_width - calculate_sentence_width(ls, font)) // 2, ly, curve_amplitude, curve_type, 1)
                draw_buttons(surface)
                pygame.display.flip()
                engine.say(syllable)
                engine.runAndWait()
                x += font.size(syllable)[0]
            x += font.size(" ")[0]

# Cargar separaciones personalizadas desde un archivo TXT o PDF
def load_custom_syllables(file_path):
    custom_syllables = {}
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if ":" in line:
                        try:
                            word, syllables = line.split(":")
                            custom_syllables[word.strip()] = syllables.strip().split("-")
                        except ValueError:
                            print(f"Error en línea: {line}")
        elif file_path.endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    for line in text.split("\n"):
                        if ":" in line:
                            try:
                                word, syllables = line.split(":")
                                custom_syllables[word.strip()] = syllables.strip().split("-")
                            except ValueError:
                                print(f"Error en línea: {line}")
        else:
            print("Formato de archivo no compatible.")
    except Exception as e:
        print(f"Error al cargar archivo: {e}")
    return custom_syllables

# Función para cargar separaciones personalizadas mediante cuadro de diálogo
def import_custom_syllables():
    Tk().withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo con separaciones personalizadas",
        filetypes=[("Archivos TXT", "*.txt"), ("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        new_syllables = load_custom_syllables(file_path)
        if new_syllables:
            custom_syllables.update(new_syllables)

# Función para añadir separaciones manualmente
def add_to_custom_syllables(word, syllables):
    custom_syllables[word] = syllables.split("-")
    print(f"Añadido: {word} -> {syllables}")

# Función para editar separaciones en tiempo real
def edit_custom_syllables():
    Tk().withdraw()
    word = simpledialog.askstring("Editar palabra", "Introduce la palabra que deseas modificar:")
    if word:
        if word in custom_syllables:
            current_syllables = "-".join(custom_syllables[word])
            new_syllables = simpledialog.askstring(
                "Editar separaciones",
                f"Separaciones actuales: {current_syllables}\nIntroduce las nuevas separaciones (usa '-'):"
            )
            if new_syllables:
                custom_syllables[word] = new_syllables.split("-")
                print(f"Actualizado: {word} -> {new_syllables}")
            else:
                print("Edición cancelada.")
        else:
            print(f"La palabra '{word}' no está en las separaciones personalizadas.")

# Colores predefinidos
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
DEFAULT_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
]
COLORS = DEFAULT_COLORS[:]

# Paletas de colores
COLOR_PALETTES = [
    [(239, 71, 111), (255, 209, 102), (6, 214, 160), (17, 138, 178), (7, 59, 76)],
    [(244, 67, 54), (33, 150, 243), (76, 175, 80), (255, 235, 59), (156, 39, 176)],
    [(66, 133, 244), (52, 168, 83), (251, 188, 5), (234, 67, 53), (153, 102, 255)]
]

# Fuente y configuración gráfica
font_size = 80
zoom_level = 1.0
font = pygame.font.Font(None, int(font_size * zoom_level))
button_font = pygame.font.Font(None, 50)

# Configuración de la pantalla
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Oraciones con curvas avanzadas")

# Cargar fondo
try:
    background = pygame.image.load("fondo.jpg")
    background = pygame.transform.scale(background, (screen_width, screen_height))
except pygame.error:
    print("Fondo no encontrado, usando color sólido.")

# Cargar configuraciones
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        curve_type = config.get("curve_type", "senoidal")
        curve_amplitude = config.get("curve_amplitude", 20)
        COLORS = config.get("colors", DEFAULT_COLORS)
except FileNotFoundError:
    curve_type = "senoidal"
    curve_amplitude = 20

# Función para guardar configuraciones
def save_config():
    config = {
        "curve_type": curve_type,
        "curve_amplitude": curve_amplitude,
        "colors": COLORS
    }
    with open("config.json", "w") as f:
        json.dump(config, f)

# Función para separar sílabas con corrección personalizada
def split_syllables(word):
    punctuation_start = ''
    punctuation_end = ''
    cleaned_word = word
    match_start = re.match(r'^[¡¿.,;!?]+', word)
    if match_start:
        punctuation_start = match_start.group(0)
        cleaned_word = word[len(punctuation_start):]
    match_end = re.search(r'[.,;!?]+$', cleaned_word)
    if match_end:
        punctuation_end = match_end.group(0)
        cleaned_word = cleaned_word[:-len(punctuation_end)]
    if cleaned_word in custom_syllables:
        syllables = custom_syllables[cleaned_word]
    else:
        raw_syllables = dic.inserted(cleaned_word).split('-') if cleaned_word else []
        syllables = []
        for i, syllable in enumerate(raw_syllables):
            if i > 0 and len(syllable) == 1:
                syllables[-1] += syllable
            else:
                syllables.append(syllable)
    result = []
    if punctuation_start:
        result.append(punctuation_start)
    result.extend(syllables)
    if punctuation_end:
        result.append(punctuation_end)
    return result

# Función para procesar una oración completa
def process_sentence(sentence):
    words = sentence.split(" ")
    processed_words = []
    for word in words:
        if word:
            syllables = split_syllables(word)
            processed_words.append(syllables)
    return processed_words

# Función para dividir las sílabas en líneas según el ancho máximo
def wrap_sentence_to_lines(sentences_with_syllables, max_width, font):
    lines = []
    current_line = []
    current_width = 0
    space_width = font.size(" ")[0]
    for word_syllables in sentences_with_syllables:
        word_width = sum(font.size(syllable)[0] for syllable in word_syllables) + space_width
        if current_width + word_width > max_width and current_line:
            lines.append(current_line)
            current_line = [word_syllables]
            current_width = word_width
        else:
            current_line.append(word_syllables)
            current_width += word_width
    if current_line:
        lines.append(current_line)
    return lines

# Función para dibujar curvas bajo las palabras y sílabas
def draw_curves(surface, words_with_syllables, start_x, start_y, curve_amplitude=20, curve_type="senoidal", scale_factor=1):
    x = start_x
    last_color_index = -1
    for word_syllables in words_with_syllables:
        word_start_x = x
        word_end_x = x
        for syllable in word_syllables:
            syllable_width = font.size(syllable)[0] * scale_factor
            end_x = x + syllable_width
            base_y = start_y + font_size * scale_factor + 10 * scale_factor
            curve_width = 3 * scale_factor
            if not re.match(r'^[¡¿.,;!?]+$', syllable) and end_x > x:
                points = []
                for curve_x in range(int(x), int(end_x) + 1):
                    if curve_type == "senoidal":
                        curve_y = base_y - curve_amplitude * scale_factor * math.sin(math.pi * (curve_x - x) / (end_x - x))
                    elif curve_type == "recta":
                        curve_y = base_y
                    elif curve_type == "bezier":
                        t = (curve_x - x) / (end_x - x) if end_x > x else 0
                        curve_y = base_y - curve_amplitude * scale_factor * (1 - t) * t
                    points.append((curve_x, curve_y))
                color_index = (last_color_index + 1) % len(COLORS)
                while color_index != last_color_index and COLORS[color_index] == COLORS[last_color_index]:
                    color_index = (color_index + 1) % len(COLORS)
                color = COLORS[color_index]
                last_color_index = color_index
                pygame.draw.lines(surface, color, False, points, int(curve_width))
            x = end_x
        word_end_x = x
        base_y = start_y + font_size * scale_factor + 40 * scale_factor
        points = []
        for curve_x in range(int(word_start_x), int(word_end_x) + 1):
            if word_end_x > word_start_x:
                curve_y = base_y - 15 * scale_factor * math.sin(math.pi * (curve_x - word_start_x) / (word_end_x - word_start_x))
                points.append((curve_x, curve_y))
        if points:
            pygame.draw.lines(surface, WHITE, False, points, int(2 * scale_factor))
        x += font.size(" ")[0] * scale_factor

# Función para calcular el ancho total de la oración procesada
def calculate_sentence_width(words_with_syllables, font):
    total_width = 0
    for word_syllables in words_with_syllables:
        for syllable in word_syllables:
            total_width += font.size(syllable)[0]
        total_width += font.size(" ")[0]
    return total_width - font.size(" ")[0]

# Función para dibujar curvas representando intensidad fonética
def draw_phonetic_intensity_curve(surface, words_with_syllables, start_x, start_y, amplitude=20):
    x = start_x
    for word_syllables in words_with_syllables:
        for syllable in word_syllables:
            syllable_width = font.size(syllable)[0]
            end_x = x + syllable_width
            if not re.match(r'^[¡¿.,;!?]+$', syllable) and end_x > x:
                for curve_x in range(x, end_x + 1):
                    intensity = random.uniform(0.5, 1.5)
                    curve_y = start_y - amplitude * intensity * math.sin(math.pi * (curve_x - x) / (end_x - x))
                    pygame.draw.line(surface, (255, 0, 0), (curve_x, start_y), (curve_x, curve_y), 1)
            x = end_x + font.size(" ")[0]

# Función para exportar una oración como imagen con crop, alta resolución y fondo transparente
def export_processed_sentence_as_image(sentence, filename, format='PNG'):
    if not sentence.strip():
        print(f"Advertencia: La entrada '{sentence}' está vacía, omitiendo exportación.")
        return
    scale_factor = 2
    words_with_syllables = process_sentence(sentence)
    if not words_with_syllables:
        print(f"Advertencia: No se generaron sílabas para '{sentence}', omitiendo exportación.")
        return
    max_width = screen_width * scale_factor - 100
    export_font = pygame.font.Font(None, int(font_size * zoom_level * scale_factor))
    lines = wrap_sentence_to_lines(words_with_syllables, max_width, export_font)
    if not lines:
        print(f"Advertencia: No se generaron líneas para '{sentence}', omitiendo exportación.")
        return
    line_height = int((font_size + 60) * scale_factor)

    min_x, max_x = float('inf'), 0
    min_y, max_y = float('inf'), 0
    y_start = 100 * scale_factor
    for line_index, line_syllables in enumerate(lines):
        line_width = calculate_sentence_width(line_syllables, export_font)
        x_start = (screen_width * scale_factor - line_width) // 2
        x = x_start
        for word_syllables in line_syllables:
            for syllable in word_syllables:
                syllable_width = export_font.size(syllable)[0]
                min_x = min(min_x, x)
                max_x = max(max_x, x + syllable_width + 2 * scale_factor)
                min_y = min(min_y, y_start + line_index * line_height)
                max_y = max(max_y, y_start + line_index * line_height + font_size * scale_factor + 2 * scale_factor)
                x += syllable_width
            x += export_font.size(" ")[0]
        curve_base_y = y_start + line_index * line_height + font_size * scale_factor + 10 * scale_factor
        word_curve_base_y = y_start + line_index * line_height + font_size * scale_factor + 40 * scale_factor
        max_y = max(max_y, curve_base_y + curve_amplitude * scale_factor, word_curve_base_y + 15 * scale_factor)

    margin = 20 * scale_factor
    min_x = max(0, min_x - margin)
    max_x += margin
    min_y = max(0, min_y - margin)
    max_y += margin

    surface_width = int(max_x - min_x)
    surface_height = int(max_y - min_y)
    if surface_width <= 0 or surface_height <= 0:
        print(f"Error: Dimensiones inválidas para '{sentence}' (ancho: {surface_width}, alto: {surface_height}), omitiendo exportación.")
        return

    surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)

    for line_index, line_syllables in enumerate(lines):
        line_width = calculate_sentence_width(line_syllables, export_font)
        x_start = (screen_width * scale_factor - line_width) // 2
        x = x_start - min_x
        for word_syllables in line_syllables:
            for syllable in word_syllables:
                cache_key = (syllable, zoom_level * scale_factor, RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE)
                if cache_key not in text_cache:
                    color = RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE
                    text_cache[cache_key] = export_font.render(syllable, True, color)
                shadow_surface = export_font.render(syllable, True, BLACK)
                surface.blit(shadow_surface, (x + 2 * scale_factor, y_start + line_index * line_height - min_y + 2 * scale_factor))
                surface.blit(text_cache[cache_key], (x, y_start + line_index * line_height - min_y))
                x += export_font.size(syllable)[0]
            x += export_font.size(" ")[0]
        draw_curves(surface, line_syllables, x_start - min_x, y_start + line_index * line_height - min_y, curve_amplitude, curve_type, scale_factor)

    try:
        pygame.image.save(surface, filename)
        img = Image.open(filename)
        img.save(filename, optimize=True, compress_level=9)
    except Exception as e:
        print(f"Error al guardar imagen '{filename}': {e}")

# Nueva función para exportar una palabra como imagen
def export_word_as_image(word, filename, scale_factor=2):
    if not word.strip():
        print(f"Advertencia: La palabra '{word}' está vacía, omitiendo exportación.")
        return False
    word_syllables = split_syllables(word)
    if not word_syllables:
        print(f"Advertencia: No se generaron sílabas para '{word}', omitiendo exportación.")
        return False

    export_font = pygame.font.Font(None, int(font_size * zoom_level * scale_factor))
    word_width = sum(export_font.size(syllable)[0] for syllable in word_syllables)
    image_width = (word_width + 100 * scale_factor)
    image_height = (font_size * 3 + curve_amplitude + 50) * scale_factor

    if image_width <= 0 or image_height <= 0:
        print(f"Error: Dimensiones inválidas para '{word}' (ancho: {image_width}, alto: {image_height}), omitiendo exportación.")
        return False

    try:
        surface = pygame.Surface((image_width, image_height), pygame.SRCALPHA)
    except Exception as e:
        print(f"Error al crear superficie para '{word}': {e}")
        return False

    x_start = 50 * scale_factor
    y_start = font_size * scale_factor // 2
    x = x_start
    last_color_index = -1
    for syllable in word_syllables:
        cache_key = (syllable, zoom_level * scale_factor, RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE)
        if cache_key not in text_cache:
            color = RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE
            try:
                text_cache[cache_key] = export_font.render(syllable, True, color)
            except Exception as e:
                print(f"Error al renderizar texto para sílaba '{syllable}' en palabra '{word}': {e}")
                return False
        shadow_surface = export_font.render(syllable, True, BLACK)
        surface.blit(shadow_surface, (x + 2 * scale_factor, y_start + 2 * scale_factor))
        surface.blit(text_cache[cache_key], (x, y_start))

        syllable_width = export_font.size(syllable)[0]
        if not re.match(r'^[¡¿.,;!?]+$', syllable):
            points = []
            base_y = y_start + font_size * scale_factor + 10 * scale_factor
            for curve_x in range(int(x), int(x + syllable_width) + 1):
                if curve_type == "senoidal":
                    curve_y = base_y - curve_amplitude * scale_factor * math.sin(math.pi * (curve_x - x) / syllable_width if syllable_width > 0 else 0)
                elif curve_type == "recta":
                    curve_y = base_y
                elif curve_type == "bezier":
                    t = (curve_x - x) / syllable_width if syllable_width > 0 else 0
                    curve_y = base_y - curve_amplitude * scale_factor * (1 - t) * t
                points.append((curve_x, curve_y))
            color_index = (last_color_index + 1) % len(COLORS)
            while color_index != last_color_index and COLORS[color_index] == COLORS[last_color_index]:
                color_index = (color_index + 1) % len(COLORS)
            color = COLORS[color_index]
            last_color_index = color_index
            pygame.draw.lines(surface, color, False, points, int(3 * scale_factor))
        x += syllable_width

    if word_width > 0:
        base_y = y_start + font_size * scale_factor + 40 * scale_factor
        points = []
        for curve_x in range(int(x_start), int(x_start + word_width) + 1):
            curve_y = base_y - 15 * scale_factor * math.sin(math.pi * (curve_x - x_start) / word_width)
            points.append((curve_x, curve_y))
        pygame.draw.lines(surface, WHITE, False, points, int(2 * scale_factor))

    try:
        pygame.image.save(surface, filename)
        img = Image.open(filename)
        img.save(filename, optimize=True, compress_level=9)
        print(f"Palabra exportada: {filename}")
        return True
    except Exception as e:
        print(f"Error al guardar imagen '{filename}' para palabra '{word}': {e}")
        return False

# Nueva función para exportar todas las palabras en lote
def export_all_words(input_file_path):
    if not input_file_path:
        print("No se ha cargado un archivo de entrada.")
        return
    try:
        words = read_sentences_from_txt(input_file_path) if input_file_path.endswith('.txt') else read_sentences_from_pdf(input_file_path)
    except Exception as e:
        print(f"Error al leer archivo de entrada '{input_file_path}': {e}")
        return
    if not words:
        print("No se encontraron palabras para exportar.")
        return
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_dir = os.path.join(os.path.dirname(input_file_path) or ".", "exported_words")
    os.makedirs(output_dir, exist_ok=True)
    successful = 0
    failed = 0
    for i, word in enumerate(words):
        if word.strip():
            try:
                sanitized_word = sanitize_filename(word)
                filename = os.path.join(output_dir, f"{sanitized_word}.png")
                print(f"Exportando {i+1}/{len(words)}: '{word}' -> {filename}")
                if export_word_as_image(word, filename):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Error al exportar '{word}' (índice {i+1}): {e}")
                failed += 1
                continue
        else:
            print(f"Advertencia: Palabra vacía en índice {i+1}, omitiendo.")
            failed += 1
    print(f"Exportación de palabras completada. Éxitos: {successful}, Fallos: {failed}")

# Función para exportar oraciones en lote
def export_batch(sentences, input_file_path, is_words=False):
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_dir = os.path.join(os.path.dirname(input_file_path) or ".", "exported_sentences")
    os.makedirs(output_dir, exist_ok=True)
    for i, item in enumerate(sentences):
        try:
            if is_words:
                filename = os.path.join(output_dir, f"{sanitize_filename(item)}.png")
            else:
                filename = os.path.join(output_dir, f"{base_name}_{i+1}.png")
            print(f"Exportando {i+1}/{len(sentences)}: '{item}' -> {filename}")
            export_processed_sentence_as_image(item, filename)
        except Exception as e:
            print(f"Error al exportar '{item}' (índice {i+1}): {e}")
            continue

# Función para dibujar botones
def draw_buttons(surface):
    button_color = (100, 100, 100)
    custom_button_color = (150, 150, 150)
    edit_button_color = (200, 100, 100)
    curve_button_color = (100, 150, 200)
    export_sentence_color = (100, 200, 100)
    export_batch_color = (200, 200, 100)
    export_words_color = (150, 100, 200)
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    if button_rect.collidepoint(mouse_pos):
        button_color = (150, 150, 150) if not mouse_clicked else (200, 200, 200)
    if custom_button_rect.collidepoint(mouse_pos):
        custom_button_color = (200, 200, 200) if not mouse_clicked else (255, 255, 255)
    if edit_button_rect.collidepoint(mouse_pos):
        edit_button_color = (255, 150, 150) if not mouse_clicked else (255, 200, 200)
    if curve_button_rect.collidepoint(mouse_pos):
        curve_button_color = (150, 200, 255) if not mouse_clicked else (200, 255, 255)
    if export_sentence_rect.collidepoint(mouse_pos):
        export_sentence_color = (150, 255, 150) if not mouse_clicked else (200, 255, 200)
    if export_batch_rect.collidepoint(mouse_pos):
        export_batch_color = (255, 255, 150) if not mouse_clicked else (255, 255, 200)
    if export_words_rect.collidepoint(mouse_pos):
        export_words_color = (200, 150, 255) if not mouse_clicked else (255, 200, 255)

    pygame.draw.rect(surface, button_color, button_rect)
    pygame.draw.rect(surface, custom_button_color, custom_button_rect)
    pygame.draw.rect(surface, edit_button_color, edit_button_rect)
    pygame.draw.rect(surface, curve_button_color, curve_button_rect)
    pygame.draw.rect(surface, export_sentence_color, export_sentence_rect)
    pygame.draw.rect(surface, export_batch_color, export_batch_rect)
    pygame.draw.rect(surface, export_words_color, export_words_rect)

    button_info = [
        ("Importar", button_text, button_rect),
        ("Cargar Custom", custom_button_text, custom_button_rect),
        ("Editar", edit_button_text, edit_button_rect),
        (f"Curva: {curve_type}", curve_button_text, curve_button_rect),
        ("Exportar Oración", export_sentence_text, export_sentence_rect),
        ("Exportar en Lote", export_batch_text, export_batch_rect),
        ("Exportar Palabras", export_words_text, export_words_rect)
    ]

    for text_str, text_surface, rect in button_info:
        text_rect = text_surface.get_rect(center=rect.center)
        shadow_surface = button_font.render(text_str, True, BLACK)
        surface.blit(shadow_surface, text_rect.move(2, 2))
        surface.blit(text_surface, text_rect)

# Variables para navegación
current_sentence_index = 0
fade_alpha = 255
sentences = []
curve_amplitude = 20
curve_type = "senoidal"
y_offset = 0
text_cache = {}
custom_syllables = {}
input_file_path = ""
is_words = False

# Definir botones en disposición horizontal centrada
button_height = 50
button_spacing = 40
button_y = screen_height - 60
button_padding = 20
button_text = button_font.render("Importar", True, WHITE)
button_width = button_text.get_width() + button_padding
custom_button_text = button_font.render("Cargar Custom", True, WHITE)
custom_button_width = custom_button_text.get_width() + button_padding
edit_button_text = button_font.render("Editar", True, WHITE)
edit_button_width = edit_button_text.get_width() + button_padding
curve_button_text = button_font.render(f"Curva: {curve_type}", True, WHITE)
curve_button_width = curve_button_text.get_width() + button_padding
export_sentence_text = button_font.render("Exportar Oración", True, WHITE)
export_sentence_width = export_sentence_text.get_width() + button_padding
export_batch_text = button_font.render("Exportar en Lote", True, WHITE)
export_batch_width = export_batch_text.get_width() + button_padding
export_words_text = button_font.render("Exportar Palabras", True, WHITE)
export_words_width = export_words_text.get_width() + button_padding
total_buttons_width = (button_width + custom_button_width + edit_button_width + curve_button_width + export_sentence_width + export_batch_width + export_words_width + 6 * button_spacing)
button_start_x = (screen_width - total_buttons_width) // 2
button_rect = pygame.Rect(button_start_x, button_y, button_width, button_height)
custom_button_rect = pygame.Rect(button_start_x + button_width + button_spacing, button_y, custom_button_width, button_height)
edit_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing, button_y, edit_button_width, button_height)
curve_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing, button_y, curve_button_width, button_height)
export_sentence_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing, button_y, export_sentence_width, button_height)
export_batch_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing, button_y, export_batch_width, button_height)
export_words_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing + export_batch_width + button_spacing, button_y, export_words_width, button_height)

# Función para abrir el cuadro de diálogo e importar oraciones
def import_sentences():
    global input_file_path, is_words
    Tk().withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=[("Archivos TXT", "*.txt"), ("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        try:
            if file_path.endswith('.txt'):
                sentences = read_sentences_from_txt(file_path)
            elif file_path.endswith('.pdf'):
                sentences = read_sentences_from_pdf(file_path)
            else:
                print("Formato de archivo no compatible.")
                return []
            input_file_path = file_path
            is_words = all(len(word.split()) == 1 for word in sentences)
            return sentences
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return []
    return []

# Función para leer oraciones desde un archivo TXT
def read_sentences_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

# Función para leer oraciones desde un archivo PDF
def read_sentences_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        sentences = []
        for page in reader.pages:
            text = page.extract_text()
            sentences.extend(text.split("\n"))
        return [sentence.strip() for sentence in sentences if sentence.strip()]

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_config()
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_config()
                running = False
            elif event.key == pygame.K_RIGHT and sentences:
                current_sentence_index = (current_sentence_index + 1) % len(sentences)
                fade_alpha = 255
            elif event.key == pygame.K_LEFT and sentences:
                current_sentence_index = (current_sentence_index - 1) % len(sentences)
                fade_alpha = 255
            elif event.key == pygame.K_UP and y_offset < 0:
                y_offset += 20
            elif event.key == pygame.K_DOWN:
                y_offset -= 20
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                zoom_level = min(zoom_level + 0.1, 2.0)
                font = pygame.font.Font(None, int(font_size * zoom_level))
            elif event.key == pygame.K_MINUS:
                zoom_level = max(zoom_level - 0.1, 0.5)
                font = pygame.font.Font(None, int(font_size * zoom_level))
            elif event.key == pygame.K_b:
                Tk().withdraw()
                file_path = filedialog.askopenfilename(
                    title="Selecciona una imagen de fondo",
                    filetypes=[("Archivos de imagen", "*.jpg;*.png"), ("Todos los archivos", "*.*")]
                )
                if file_path:
                    background = pygame.image.load(file_path)
                    background = pygame.transform.scale(background, (screen_width, screen_height))
            elif event.key == pygame.K_c:
                COLORS = random.choice(COLOR_PALETTES)
            elif event.key == pygame.K_v and sentences:
                highlight_syllables_while_reading(screen, sentences[current_sentence_index], (screen_width - calculate_sentence_width(process_sentence(sentences[current_sentence_index]), font)) // 2, screen_height // 3)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                sentences = import_sentences()
            elif custom_button_rect.collidepoint(event.pos):
                import_custom_syllables()
            elif edit_button_rect.collidepoint(event.pos):
                edit_custom_syllables()
            elif curve_button_rect.collidepoint(event.pos):
                if curve_type == "senoidal":
                    curve_type = "recta"
                elif curve_type == "recta":
                    curve_type = "bezier"
                else:
                    curve_type = "senoidal"
                curve_button_text = button_font.render(f"Curva: {curve_type}", True, WHITE)
                curve_button_width = curve_button_text.get_width() + button_padding
                total_buttons_width = (button_width + custom_button_width + edit_button_width + curve_button_width + export_sentence_width + export_batch_width + export_words_width + 6 * button_spacing)
                button_start_x = (screen_width - total_buttons_width) // 2
                button_rect = pygame.Rect(button_start_x, button_y, button_width, button_height)
                custom_button_rect = pygame.Rect(button_start_x + button_width + button_spacing, button_y, custom_button_width, button_height)
                edit_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing, button_y, edit_button_width, button_height)
                curve_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing, button_y, curve_button_width, button_height)
                export_sentence_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing, button_y, export_sentence_width, button_height)
                export_batch_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing, button_y, export_batch_width, button_height)
                export_words_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing + export_batch_width + button_spacing, button_y, export_words_width, button_height)
            elif export_sentence_rect.collidepoint(event.pos) and sentences:
                Tk().withdraw()
                filename = filedialog.asksaveasfilename(
                    title="Exportar imagen",
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png")]
                )
                if filename:
                    export_processed_sentence_as_image(sentences[current_sentence_index], filename)
            elif export_batch_rect.collidepoint(event.pos) and sentences and input_file_path:
                export_batch(sentences, input_file_path, is_words)
            elif export_words_rect.collidepoint(event.pos) and input_file_path:
                export_all_words(input_file_path)
        if event.type == pygame.MOUSEWHEEL:
            y_offset += event.y * 20
        if event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.size
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            if 'background' in globals():
                background = pygame.transform.scale(background, (screen_width, screen_height))
            button_y = screen_height - 60
            total_buttons_width = (button_width + custom_button_width + edit_button_width + curve_button_width + export_sentence_width + export_batch_width + export_words_width + 6 * button_spacing)
            button_start_x = (screen_width - total_buttons_width) // 2
            button_rect = pygame.Rect(button_start_x, button_y, button_width, button_height)
            custom_button_rect = pygame.Rect(button_start_x + button_width + button_spacing, button_y, custom_button_width, button_height)
            edit_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing, button_y, edit_button_width, button_height)
            curve_button_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing, button_y, curve_button_width, button_height)
            export_sentence_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing, button_y, export_sentence_width, button_height)
            export_batch_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing, button_y, export_batch_width, button_height)
            export_words_rect = pygame.Rect(button_start_x + button_width + button_spacing + custom_button_width + button_spacing + edit_button_width + button_spacing + curve_button_width + button_spacing + export_sentence_width + button_spacing + export_batch_width + button_spacing, button_y, export_words_width, button_height)

    # Dibujar fondo
    if 'background' in globals():
        screen.blit(background, (0, 0))
    else:
        screen.fill((200, 150, 100))

    # Transición de desvanecimiento
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.set_alpha(fade_alpha)
    fade_surface.fill(BLACK)

    # Dibujar botones
    draw_buttons(screen)

    # Mostrar oración procesada si hay
    if sentences:
        sentence = sentences[current_sentence_index]
        sentences_with_syllables = process_sentence(sentence)
        max_width = screen_width - 100
        lines = wrap_sentence_to_lines(sentences_with_syllables, max_width, font)
        y_start = screen_height // 4 + y_offset
        line_height = font_size + 60
        for line_index, line_syllables in enumerate(lines):
            line_width = calculate_sentence_width(line_syllables, font)
            x_start = (screen_width - line_width) // 2
            x = x_start
            for word_syllables in line_syllables:
                for syllable in word_syllables:
                    cache_key = (syllable, zoom_level, RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE)
                    if cache_key not in text_cache:
                        color = RED if (re.match(r'^[¡¿.,;!?]+$', syllable) or re.search(r'[áéíóúÁÉÍÓÚ]', syllable)) else BLUE
                        text_cache[cache_key] = font.render(syllable, True, color)
                    shadow_surface = font.render(syllable, True, BLACK)
                    screen.blit(shadow_surface, (x + 2, y_start + line_index * line_height + 2))
                    screen.blit(text_cache[cache_key], (x, y_start + line_index * line_height))
                    x += font.size(syllable)[0]
                x += font.size(" ")[0]
            draw_curves(screen, line_syllables, x_start, y_start + line_index * line_height, curve_amplitude, curve_type, 1)

    # Indicador de progreso
    progress_text = f"Oración {current_sentence_index + 1} de {len(sentences)}"
    progress_surface = button_font.render(progress_text, True, WHITE)
    progress_rect = progress_surface.get_rect(center=(screen_width // 2, 50))
    shadow_surface = button_font.render(progress_text, True, BLACK)
    screen.blit(shadow_surface, progress_rect.move(2, 2))
    screen.blit(progress_surface, progress_rect)

    # Dibujar transición
    if fade_alpha > 0:
        screen.blit(fade_surface, (0, 0))
        fade_alpha -= 5

    # Actualizar pantalla
    pygame.display.flip()

# Salir
pygame.quit()