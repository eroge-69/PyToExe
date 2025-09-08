import pyaudio
import numpy as np
import pygame
import os
import time
import tkinter as tk
from tkinter import filedialog
import sys
import json
import shutil

# Configurações de áudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 0.5
SWITCH_DELAY = 0.02

# Configurações do Pygame
WINDOW_SIZE = (400, 800)
FPS = 30
IMAGE_SCALE_FACTOR = 1.0

# Cores disponíveis
COLORS = {
    "branco": (255, 255, 255),
    "preto": (0, 0, 0),
    "verde": (0, 255, 0),
    "rosa": (255, 105, 180),
    "amarelo": (255, 255, 0),
    "azul": (0, 0, 255)
}
background_color = COLORS["rosa"]
CONFIG_BG_COLOR = (0, 0, 0)
FPS_ACTIVE_COLOR = (144, 238, 144)
FPS_INACTIVE_COLOR = (200, 200, 200)

# Diretório para salvar imagens do usuário
USER_IMAGES_DIR = "user_images"
CONFIG_FILE = "config.json"

# Cria diretório para imagens do usuário, se não existir
if not os.path.exists(USER_IMAGES_DIR):
    os.makedirs(USER_IMAGES_DIR)

# Verifica se os arquivos existem
def check_file_exists(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, filename)
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo '{file_path}' não encontrado")
        return False
    return True

# Função para selecionar imagem
def select_image(current):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[
        ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
        ("PNG files", "*.png"),
        ("JPG files", "*.jpg *.jpeg"),
        ("BMP files", "*.bmp"),
        ("GIF files", "*.gif"),
        ("TIFF files", "*.tiff"),
        ("WEBP files", "*.webp"),
        ("All files", "*.*")
    ])
    if file_path and os.path.exists(file_path):
        try:
            # Copia a imagem para o diretório user_images
            filename = os.path.basename(file_path)
            dest_path = os.path.join(USER_IMAGES_DIR, filename)
            shutil.copy(file_path, dest_path)
            return pygame.image.load(dest_path).convert_alpha()
        except (pygame.error, shutil.Error) as e:
            print(f"Erro ao carregar ou copiar a imagem: {e}")
            return current
    return current

# Função para salvar configurações
def save_config(boca_fechada_path, boca_aberta_path):
    config = {
        "THRESHOLD": THRESHOLD,
        "SWITCH_DELAY": SWITCH_DELAY,
        "FPS": FPS,
        "IMAGE_SCALE_FACTOR": IMAGE_SCALE_FACTOR,
        "background_color": background_color,
        "boca_fechada_path": boca_fechada_path,
        "boca_aberta_path": boca_aberta_path
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print("Configurações salvas com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

# Função para carregar configurações
def load_config():
    global THRESHOLD, SWITCH_DELAY, FPS, IMAGE_SCALE_FACTOR, background_color
    global boca_fechada_original, boca_aberta_original
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        THRESHOLD = config.get("THRESHOLD", THRESHOLD)
        SWITCH_DELAY = config.get("SWITCH_DELAY", SWITCH_DELAY)
        FPS = config.get("FPS", FPS)
        IMAGE_SCALE_FACTOR = config.get("IMAGE_SCALE_FACTOR", IMAGE_SCALE_FACTOR)
        background_color = tuple(config.get("background_color", background_color))
        boca_fechada_path = config.get("boca_fechada_path", "")
        boca_aberta_path = config.get("boca_aberta_path", "")
        if boca_fechada_path and os.path.exists(boca_fechada_path):
            boca_fechada_original = pygame.image.load(boca_fechada_path).convert_alpha()
        if boca_aberta_path and os.path.exists(boca_aberta_path):
            boca_aberta_original = pygame.image.load(boca_aberta_path).convert_alpha()
        print("Configurações carregadas com sucesso!")
    except FileNotFoundError:
        print("Arquivo de configuração não encontrado. Usando configurações padrão.")
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("AnimaVoz")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
font_small = pygame.font.SysFont(None, 20)

# Configurações da superfície rolável
CONFIG_HEIGHT = 500  # Altura total da área de configurações
config_surface = pygame.Surface((400, CONFIG_HEIGHT))
scroll_y = 0
SCROLL_SPEED = 20

# Carrega imagens iniciais
image_files = ["boca_fechada.png", "boca_aberta.png"]
for img in image_files:
    if not check_file_exists(img):
        pygame.quit()
        exit()

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
boca_fechada_original = pygame.image.load(os.path.join(base_path, "boca_fechada.png")).convert_alpha()
boca_aberta_original = pygame.image.load(os.path.join(base_path, "boca_aberta.png")).convert_alpha()

# Inicializa caminhos das imagens
boca_fechada_path = os.path.join(base_path, "boca_fechada.png")
boca_aberta_path = os.path.join(base_path, "boca_aberta.png")

# Tenta carregar configurações salvas ao iniciar
load_config()

# Inicializa Pyaudio
try:
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
except Exception as e:
    print(f"Erro ao inicializar o microfone: {e}")
    pygame.quit()
    exit()

# Variáveis para animação e interface
last_switch = 0
color_buttons = [
    {"color": COLORS["branco"], "rect": pygame.Rect(20, 25, 40, 40)},
    {"color": COLORS["preto"], "rect": pygame.Rect(70, 25, 40, 40)},
    {"color": COLORS["verde"], "rect": pygame.Rect(120, 25, 40, 40)},
    {"color": COLORS["rosa"], "rect": pygame.Rect(170, 25, 40, 40)},
    {"color": COLORS["amarelo"], "rect": pygame.Rect(220, 25, 40, 40)},
    {"color": COLORS["azul"], "rect": pygame.Rect(270, 25, 40, 40)},
]
fps_buttons = [
    {"fps": 24, "rect": pygame.Rect(20, 95, 40, 40)},
    {"fps": 30, "rect": pygame.Rect(70, 95, 40, 40)},
    {"fps": 60, "rect": pygame.Rect(120, 95, 40, 40)},
]
image_buttons = [
    {"action": "boca_fechada", "rect": pygame.Rect(20, 165, 120, 30)},
    {"action": "boca_aberta", "rect": pygame.Rect(150, 165, 120, 30)},
]
scale_buttons = [
    {"action": "increase", "rect": pygame.Rect(340, 235, 30, 30)},
    {"action": "decrease", "rect": pygame.Rect(300, 235, 30, 30)},
]
threshold_buttons = [
    {"action": "increase", "rect": pygame.Rect(340, 295, 30, 30)},
    {"action": "decrease", "rect": pygame.Rect(300, 295, 30, 30)},
]
delay_buttons = [
    {"action": "increase", "rect": pygame.Rect(340, 335, 30, 30)},
    {"action": "decrease", "rect": pygame.Rect(300, 335, 30, 30)},
]
config_buttons = [
    {"action": "save", "rect": pygame.Rect(20, 395, 120, 30)},
    {"action": "load", "rect": pygame.Rect(150, 395, 120, 30)},
]

# Loop principal
running = True
current_image = boca_fechada_original
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Ajusta a posição do clique com base no deslocamento da rolagem
            adjusted_pos = (event.pos[0], event.pos[1] + scroll_y - 400)
            for button in color_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    background_color = button["color"]
            for button in fps_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    FPS = button["fps"]
            for button in threshold_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    if button["action"] == "increase":
                        THRESHOLD = min(THRESHOLD + 0.01, 5.0)
                    elif button["action"] == "decrease":
                        THRESHOLD = max(THRESHOLD - 0.01, 0.0)
            for button in delay_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    if button["action"] == "increase":
                        SWITCH_DELAY = min(SWITCH_DELAY + 0.01, 0.5)
                    elif button["action"] == "decrease":
                        SWITCH_DELAY = max(SWITCH_DELAY - 0.01, 0.0)
            for button in image_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    if button["action"] == "boca_fechada":
                        new_image = select_image(boca_fechada_original)
                        if new_image != boca_fechada_original:
                            boca_fechada_original = new_image
                            boca_fechada_path = os.path.join(USER_IMAGES_DIR, os.path.basename(boca_fechada_path))
                    elif button["action"] == "boca_aberta":
                        new_image = select_image(boca_aberta_original)
                        if new_image != boca_aberta_original:
                            boca_aberta_original = new_image
                            boca_aberta_path = os.path.join(USER_IMAGES_DIR, os.path.basename(boca_aberta_path))
            for button in scale_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    if button["action"] == "increase":
                        IMAGE_SCALE_FACTOR = min(IMAGE_SCALE_FACTOR + 0.1, 2.0)
                    elif button["action"] == "decrease":
                        IMAGE_SCALE_FACTOR = max(IMAGE_SCALE_FACTOR - 0.1, 0.5)
            for button in config_buttons:
                if button["rect"].collidepoint(adjusted_pos):
                    if button["action"] == "save":
                        save_config(boca_fechada_path, boca_aberta_path)
                    elif button["action"] == "load":
                        load_config()
        elif event.type == pygame.MOUSEWHEEL:
            # Ajusta a rolagem com a roda do mouse
            scroll_y -= event.y * SCROLL_SPEED
            # Limita a rolagem para não ultrapassar os limites da superfície
            scroll_y = max(0, min(scroll_y, CONFIG_HEIGHT - 400))

    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
    except Exception as e:
        continue

    audio_array = np.frombuffer(data, dtype=np.int16)
    volume = np.abs(audio_array).mean() / 100

    current_time = time.time()
    if volume > THRESHOLD and current_time - last_switch > SWITCH_DELAY:
        current_image = boca_aberta_original
        last_switch = current_time
    elif volume <= THRESHOLD and current_time - last_switch > SWITCH_DELAY:
        current_image = boca_fechada_original
        last_switch = current_time
    
    # Renderiza a área de animação (fixa)
    screen.fill(background_color, (0, 0, 400, 400))
    scaled_width = int(current_image.get_width() * IMAGE_SCALE_FACTOR)
    scaled_height = int(current_image.get_height() * IMAGE_SCALE_FACTOR)
    scaled_image = pygame.transform.scale(current_image, (scaled_width, scaled_height))
    image_x = (400 - scaled_width) // 2
    image_y = (400 - scaled_height) // 2
    screen.blit(scaled_image, (image_x, image_y))
    
    # Renderiza a área de configurações na superfície virtual
    config_surface.fill(CONFIG_BG_COLOR)
    
    color_label = font_small.render("COR DE FUNDO", True, (255, 255, 255))
    config_surface.blit(color_label, (20, 0))
    for button in color_buttons:
        pygame.draw.rect(config_surface, button["color"], button["rect"])
        pygame.draw.rect(config_surface, (255, 255, 255), button["rect"], 2)
    
    fps_label = font_small.render("FPS DE TRANSIÇÃO DE IMAGENS", True, (255, 255, 255))
    config_surface.blit(fps_label, (20, 70))
    for button in fps_buttons:
        color = FPS_ACTIVE_COLOR if button["fps"] == FPS else FPS_INACTIVE_COLOR
        pygame.draw.rect(config_surface, color, button["rect"])
        label = font.render(str(button["fps"]), True, (0, 0, 0))
        config_surface.blit(label, (button["rect"].x + 10, button["rect"].y + 10))
    
    image_label = font_small.render("IMAGENS DO PERSONAGEM", True, (255, 255, 255))
    config_surface.blit(image_label, (20, 140))
    for button in image_buttons:
        pygame.draw.rect(config_surface, (200, 200, 200), button["rect"])
    config_surface.blit(font.render("Boca Fechada", True, (0, 0, 0)), (25, 170))
    config_surface.blit(font.render("Boca Aberta", True, (0, 0, 0)), (155, 170))
    
    scale_label = font_small.render("TAMANHO DA IMAGEM", True, (255, 255, 255))
    config_surface.blit(scale_label, (20, 210))
    for button in scale_buttons:
        pygame.draw.rect(config_surface, (200, 200, 200), button["rect"])
    config_surface.blit(font.render("+", True, (0, 0, 0)), (350, 240))
    config_surface.blit(font.render("−", True, (0, 0, 0)), (310, 240))
    scale_text = font.render(f"Tamanho: {IMAGE_SCALE_FACTOR:.1f}x", True, (255, 255, 255))
    config_surface.blit(scale_text, (150, 240))
    
    sens_label = font_small.render("SENSIBILIDADE E DELAY DE TRANSIÇÃO", True, (255, 255, 255))
    config_surface.blit(sens_label, (20, 270))
    for button in threshold_buttons:
        pygame.draw.rect(config_surface, (200, 200, 200), button["rect"])
    config_surface.blit(font.render("+", True, (0, 0, 0)), (350, 300))
    config_surface.blit(font.render("−", True, (0, 0, 0)), (310, 300))
    threshold_text = font.render(f"Threshold: {THRESHOLD:.2f}", True, (255, 255, 255))
    config_surface.blit(threshold_text, (20, 300))
    
    for button in delay_buttons:
        pygame.draw.rect(config_surface, (200, 200, 200), button["rect"])
    config_surface.blit(font.render("+", True, (0, 0, 0)), (350, 340))
    config_surface.blit(font.render("−", True, (0, 0, 0)), (310, 340))
    delay_text = font.render(f"Delay: {SWITCH_DELAY:.2f}", True, (255, 255, 255))
    config_surface.blit(delay_text, (20, 340))
    
    config_label = font_small.render("CONFIGURAÇÕES", True, (255, 255, 255))
    config_surface.blit(config_label, (20, 380))
    for button in config_buttons:
        pygame.draw.rect(config_surface, (200, 200, 200), button["rect"])
    config_surface.blit(font.render("Salvar", True, (0, 0, 0)), (25, 400))
    config_surface.blit(font.render("Carregar", True, (0, 0, 0)), (155, 400))
    
    # Desenha a superfície de configurações com deslocamento
    screen.blit(config_surface, (0, 400), (0, scroll_y, 400, 400))
    
    pygame.display.update()
    clock.tick(FPS)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()