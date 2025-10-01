import pygame
import sys
import random
import math
import os
import zipfile
import re
import shutil
from pygame import mixer

# Inicializar Pygame
pygame.init()
mixer.init()

# Configuración de pantalla - MÁS GRANDE 1360x768
WIDTH, HEIGHT = 1360, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OSU! Mania Clone")

# Colores
BLACK = (0, 0, 0)
DARK_BLUE = (20, 20, 40)
BLUE = (30, 30, 60)
WHITE = (255, 255, 255)
RED = (255, 80, 80)
ORANGE = (255, 150, 50)
YELLOW = (255, 255, 80)
GREEN = (80, 255, 80)
CYAN = (80, 255, 255)
PURPLE = (200, 80, 255)
PINK = (255, 100, 200)
LIGHT_BLUE = (100, 150, 255)
LIGHT_GRAY = (180, 180, 200)
DARK_GRAY = (60, 60, 80)
GLOW_BLUE = (80, 120, 255, 100)

# Configuración de juego
clock = pygame.time.Clock()
FPS = 120

# Fuentes (ligeramente más grandes para la nueva resolución)
title_font = pygame.font.SysFont("Arial", 56, bold=True)
menu_font = pygame.font.SysFont("Arial", 42, bold=True)
game_font = pygame.font.SysFont("Arial", 28)
combo_font = pygame.font.SysFont("Arial", 80, bold=True)
judgement_font = pygame.font.SysFont("Arial", 48, bold=True)
key_font = pygame.font.SysFont("Arial", 24, bold=True)

# Estados del juego
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
BEATMAP_SELECT = 4
SKIN_SELECT = 5

# Configuración de teclas para 4K
KEY_CONFIGS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]

# Nombres de teclas para mostrar
KEY_NAMES = {
    pygame.K_d: "D", 
    pygame.K_f: "F", 
    pygame.K_j: "J", 
    pygame.K_k: "K"
}

# Sistema de skins
class SkinManager:
    def __init__(self):
        self.current_skin = "default"
        self.skins_dir = "skins"
        self.available_skins = []
        self.load_available_skins()
        
    def load_available_skins(self):
        """Cargar lista de skins disponibles"""
        if not os.path.exists(self.skins_dir):
            os.makedirs(self.skins_dir)
            
        self.available_skins = ["default"]
        
        for item in os.listdir(self.skins_dir):
            item_path = os.path.join(self.skins_dir, item)
            if os.path.isdir(item_path):
                self.available_skins.append(item)
            elif item.endswith(".osk"):
                skin_name = item[:-4]
                self.extract_osk(item_path, skin_name)
                self.available_skins.append(skin_name)
                
    def extract_osk(self, osk_path, skin_name):
        """Extraer archivo .osk a una carpeta de skin"""
        try:
            skin_dir = os.path.join(self.skins_dir, skin_name)
            if os.path.exists(skin_dir):
                shutil.rmtree(skin_dir)
                
            with zipfile.ZipFile(osk_path, 'r') as zip_ref:
                zip_ref.extractall(skin_dir)
            os.remove(osk_path)
            
        except Exception as e:
            print(f"Error al extraer skin {osk_path}: {e}")
            
    def set_skin(self, skin_name):
        """Establecer skin actual"""
        if skin_name in self.available_skins:
            self.current_skin = skin_name
            return True
        return False

# Efectos de partículas (OPTIMIZADO)
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(-3, -1)
        self.life = random.randint(15, 25)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size *= 0.92
        return self.life > 0
        
    def draw(self, screen):
        alpha = min(255, self.life * 8)
        pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), int(self.size))

# Clase para las notas (OPTIMIZADO)
class Note:
    def __init__(self, column, time, note_type="normal", hold_duration=0):
        self.column = column
        self.hit_time = time
        self.note_type = note_type
        self.hold_duration = hold_duration
        self.held = False
        self.active = True
        self.hit = False
        self.missed = False
        self.hit_effect = 0
        self.hold_progress = 0
        self.hold_start = 0
        self.particles = []
        
    def update(self, current_time, scroll_speed):
        if not self.active:
            return False
            
        if self.note_type == "hold" and self.hit:
            if current_time < self.hold_start + self.hold_duration:
                self.hold_progress = (current_time - self.hold_start) / self.hold_duration
            else:
                self.active = False
                return True
                
        if current_time > self.hit_time + 150 and not self.hit and not (self.note_type == "hold" and self.held):
            self.missed = True
            self.active = False
            return False
            
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
                
        return True
        
    def draw(self, screen, current_time, columns, column_width, receptor_y, scroll_speed):
        if not self.active:
            return
            
        x = columns[self.column]
        note_height = 20
        
        time_to_hit = self.hit_time - current_time
        distance_to_receptor = (time_to_hit / 1000) * scroll_speed
        y = receptor_y - distance_to_receptor
        
        if y < -150 or y > HEIGHT + 150:
            return
            
        color = self.get_column_color(self.column)
        
        if self.note_type == "normal":
            pygame.draw.rect(screen, color, (x - column_width//2, y - note_height//2, column_width, note_height), border_radius=6)
            pygame.draw.rect(screen, WHITE, (x - column_width//2, y - note_height//2, column_width, note_height), 1, border_radius=6)
            
        elif self.note_type == "hold":
            hold_height = int((self.hold_duration / 1000) * scroll_speed)
            hold_y = int(y - hold_height)
            
            pygame.draw.rect(screen, color, (x - column_width//2, hold_y, column_width, hold_height), border_radius=4)
            pygame.draw.rect(screen, WHITE, (x - column_width//2, hold_y, column_width, hold_height), 1, border_radius=4)
            
            pygame.draw.rect(screen, color, (x - column_width//2, int(y - note_height//2), column_width, note_height), border_radius=6)
            pygame.draw.rect(screen, WHITE, (x - column_width//2, int(y - note_height//2), column_width, note_height), 1, border_radius=6)
            
            if self.held:
                progress_height = int(hold_height * self.hold_progress)
                pygame.draw.rect(screen, WHITE, (x - column_width//2, int(y - progress_height), column_width, progress_height), border_radius=4)
        
        if self.hit and self.hit_effect < 15:
            self.hit_effect += 1
            effect_size = self.hit_effect * 2
            effect_rect = (x - column_width//2 - effect_size, 
                          int(y - note_height//2 - effect_size), 
                          column_width + effect_size*2, 
                          note_height + effect_size*2)
            pygame.draw.rect(screen, WHITE, effect_rect, 2, border_radius=8)
            
            if self.hit_effect % 3 == 0:
                self.particles.append(Particle(x, y, color))
        
        for particle in self.particles:
            particle.draw(screen)
            
    def get_column_color(self, column):
        colors = [RED, ORANGE, YELLOW, GREEN]
        return colors[column % len(colors)]
        
    def check_hit(self, current_time, key_pressed, key_released=None):
        if not self.active or self.hit or self.missed:
            return False
            
        time_diff = abs(current_time - self.hit_time)
        
        if self.note_type == "normal":
            if time_diff <= 150:
                self.hit = True
                self.active = False
                return time_diff
                
        elif self.note_type == "hold":
            if not self.held and time_diff <= 150 and key_pressed:
                self.held = True
                self.hit = True
                self.hold_start = current_time
                return time_diff
                
            if self.held and key_released and current_time >= self.hold_start:
                self.active = False
                return 0
                
        return False

# Parser de archivos .osu
class OsuParser:
    def __init__(self):
        self.beatmaps = []
        self.load_beatmaps()
        
    def load_beatmaps(self):
        beatmaps_dir = "beatmaps"
        if not os.path.exists(beatmaps_dir):
            os.makedirs(beatmaps_dir)
            return
            
        self.beatmaps = []
        
        for file in os.listdir(beatmaps_dir):
            if file.endswith(".osu"):
                beatmap_path = os.path.join(beatmaps_dir, file)
                beatmap_info = self.parse_osu_file(beatmap_path)
                if beatmap_info:
                    self.beatmaps.append(beatmap_info)
            elif file.endswith(".osz"):
                self.extract_osz(os.path.join(beatmaps_dir, file))
                
        for file in os.listdir(beatmaps_dir):
            if file.endswith(".osu"):
                beatmap_path = os.path.join(beatmaps_dir, file)
                if not any(b['path'] == beatmap_path for b in self.beatmaps):
                    beatmap_info = self.parse_osu_file(beatmap_path)
                    if beatmap_info:
                        self.beatmaps.append(beatmap_info)
                        
    def extract_osz(self, osz_path):
        try:
            beatmaps_dir = "beatmaps"
            with zipfile.ZipFile(osz_path, 'r') as zip_ref:
                zip_ref.extractall(beatmaps_dir)
        except Exception as e:
            print(f"Error al extraer {osz_path}: {e}")
            
    def parse_osu_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            beatmap_info = {
                'path': file_path,
                'title': 'Desconocido',
                'artist': 'Desconocido',
                'creator': 'Desconocido',
                'difficulty': 'Desconocido',
                'hp': 5,
                'od': 5,
                'audio_file': None,
                'objects': []
            }
            
            title_match = re.search(r'Title:(.*)', content)
            artist_match = re.search(r'Artist:(.*)', content)
            creator_match = re.search(r'Creator:(.*)', content)
            version_match = re.search(r'Version:(.*)', content)
            hp_match = re.search(r'HPDrainRate:([0-9.]+)', content)
            od_match = re.search(r'OverallDifficulty:([0-9.]+)', content)
            audio_match = re.search(r'AudioFilename:\s*(.*)', content)
            
            if title_match:
                beatmap_info['title'] = title_match.group(1).strip()
            if artist_match:
                beatmap_info['artist'] = artist_match.group(1).strip()
            if creator_match:
                beatmap_info['creator'] = creator_match.group(1).strip()
            if version_match:
                beatmap_info['difficulty'] = version_match.group(1).strip()
            if hp_match:
                beatmap_info['hp'] = float(hp_match.group(1))
            if od_match:
                beatmap_info['od'] = float(od_match.group(1))
            if audio_match:
                audio_filename = audio_match.group(1).strip()
                beatmap_dir = os.path.dirname(file_path)
                beatmap_info['audio_file'] = os.path.join(beatmap_dir, audio_filename)
                
            hit_objects_section = False
            for line in content.split('\n'):
                line = line.strip()
                
                if line == '[HitObjects]':
                    hit_objects_section = True
                    continue
                elif line.startswith('[') and hit_objects_section:
                    break
                    
                if hit_objects_section and line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        x = int(parts[0])
                        time = int(parts[2])
                        obj_type = int(parts[3])
                        
                        column = (x * 4) // 512
                        if column > 3:
                            column = 3
                        elif column < 0:
                            column = 0
                            
                        note_type = "normal"
                        hold_duration = 0
                        
                        if obj_type & 2:
                            note_type = "hold"
                            if len(parts) > 7:
                                try:
                                    pixel_length = float(parts[7])
                                    slides = int(parts[6])
                                    hold_duration = int(pixel_length * slides / 5)
                                except:
                                    hold_duration = 500
                            else:
                                hold_duration = 500
                                
                        beatmap_info['objects'].append({
                            'column': column,
                            'time': time,
                            'type': note_type,
                            'hold_duration': hold_duration
                        })
                        
            beatmap_info['objects'].sort(key=lambda x: x['time'])
            return beatmap_info
            
        except Exception as e:
            print(f"Error al parsear {file_path}: {e}")
            return None
            
    def get_beatmap_list(self):
        return [f"{b['artist']} - {b['title']} [{b['difficulty']}]" for b in self.beatmaps]
    
    def get_random_audio_file(self):
        """Obtener un archivo de audio aleatorio de los beatmaps disponibles"""
        audio_files = []
        for beatmap in self.beatmaps:
            if beatmap.get('audio_file') and os.path.exists(beatmap['audio_file']):
                audio_files.append(beatmap['audio_file'])
        
        if audio_files:
            return random.choice(audio_files)
        return None

# Clase principal del juego
class OsuMania:
    def __init__(self):
        self.state = MENU
        self.keys = 4
        self.key_bindings = KEY_CONFIGS
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.accuracy = 100.0
        self.hits = {"PERFECT": 0, "GREAT": 0, "GOOD": 0, "BAD": 0, "MISS": 0}
        self.current_time = 0
        self.start_time = 0
        self.notes = []
        self.active_notes = []
        self.receptor_y = HEIGHT - 150
        self.scroll_speed = 300
        self.columns = []
        self.column_width = 0
        self.judgement_text = ""
        self.judgement_time = 0
        self.key_states = {key: False for key in self.key_bindings}
        self.key_effects = {key: 0 for key in self.key_bindings}
        self.menu_options = []
        self.combo_effect = 0
        self.approach_time = 2000
        self.song_length = 45000
        
        self.parser = OsuParser()
        self.selected_beatmap = None
        self.beatmap_options = []
        
        self.skin_manager = SkinManager()
        self.current_music = None
        self.menu_music = None
        
        self.logo = self.load_logo()
        self.background_particles = []
        
        for _ in range(20):  # Más partículas para pantalla más grande
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 2)
            speed = random.uniform(0.05, 0.2)
            self.background_particles.append([x, y, size, speed])
        
        # Reproducir música aleatoria en el menú
        self.play_random_menu_music()
        
    def play_random_menu_music(self):
        """Reproducir una canción aleatoria en el menú"""
        if self.menu_music:
            pygame.mixer.music.stop()
            
        audio_file = self.parser.get_random_audio_file()
        if audio_file:
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play(-1)  # -1 para loop infinito
                self.menu_music = audio_file
            except Exception as e:
                self.menu_music = None
        
    def load_logo(self):
        try:
            logo_path = os.path.join("resources", "logo.png")
            if os.path.exists(logo_path):
                logo = pygame.image.load(logo_path)
                original_width, original_height = logo.get_size()
                max_width = 400  # Un poco más grande para la nueva resolución
                max_height = 180
                
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                return pygame.transform.smoothscale(logo, (new_width, new_height))
        except:
            pass
        
        # Logo placeholder si no se encuentra
        logo = pygame.Surface((350, 140), pygame.SRCALPHA)
        pygame.draw.rect(logo, LIGHT_BLUE, (0, 0, 350, 140), border_radius=12)
        logo_text = title_font.render("OSU! CLONE", True, WHITE)
        text_rect = logo_text.get_rect(center=(175, 70))
        logo.blit(logo_text, text_rect)
        return logo
        
    def setup_columns(self):
        self.column_width = WIDTH // (self.keys + 2)
        self.columns = []
        for i in range(self.keys):
            x = (i + 1) * self.column_width + self.column_width // 2
            self.columns.append(x)
            
    def generate_beatmap(self):
        self.beatmap = []
        patterns = [
            [0, 1, 2, 3],
            [0, 3, 1, 2],
            [0, 0, 3, 3],
            [0, 1, 2, 3, 2, 1, 0],
            [random.randint(0, 3) for _ in range(8)]
        ]
        
        current_time = 3000
        pattern_index = 0
        
        while current_time < self.song_length:
            pattern = patterns[pattern_index % len(patterns)]
            
            for column in pattern:
                if random.random() < 0.8:
                    self.beatmap.append({"time": current_time, "column": column, "type": "normal", "hold_duration": 0})
                else:
                    hold_duration = random.randint(800, 1500)
                    self.beatmap.append({"time": current_time, "column": column, "type": "hold", "hold_duration": hold_duration})
                
                current_time += random.randint(200, 400)
            
            current_time += 800
            pattern_index += 1
            
    def load_selected_beatmap(self):
        if self.selected_beatmap is not None:
            beatmap_info = self.parser.beatmaps[self.selected_beatmap]
            self.beatmap = beatmap_info['objects']
            
            od = beatmap_info.get('od', 5)
            self.scroll_speed = 200 + (od * 20)
            
            if self.beatmap:
                self.song_length = self.beatmap[-1]['time'] + 5000
            else:
                self.song_length = 45000
                
            if beatmap_info.get('audio_file') and os.path.exists(beatmap_info['audio_file']):
                try:
                    if self.current_music:
                        pygame.mixer.music.stop()
                    pygame.mixer.music.load(beatmap_info['audio_file'])
                    pygame.mixer.music.play()
                    self.current_music = beatmap_info['audio_file']
                except:
                    self.current_music = None
            else:
                self.current_music = None
        else:
            self.generate_beatmap()
            self.current_music = None
                
    def start_game(self, beatmap_index=None):
        # Detener música del menú
        if self.menu_music:
            pygame.mixer.music.stop()
            self.menu_music = None
            
        self.setup_columns()
        
        if beatmap_index is not None:
            self.selected_beatmap = beatmap_index
            self.load_selected_beatmap()
        else:
            self.generate_beatmap()
            self.current_music = None
            
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.accuracy = 100.0
        self.hits = {"PERFECT": 0, "GREAT": 0, "GOOD": 0, "BAD": 0, "MISS": 0}
        self.notes = []
        self.active_notes = []
        self.judgement_text = ""
        self.judgement_time = 0
        self.key_states = {key: False for key in self.key_bindings}
        self.key_effects = {key: 0 for key in self.key_bindings}
        self.combo_effect = 0
        
        for obj in self.beatmap:
            self.notes.append(Note(obj["column"], obj["time"], obj["type"], obj["hold_duration"]))
        
        self.notes.sort(key=lambda x: x.hit_time)
        
        self.start_time = pygame.time.get_ticks()
        self.state = PLAYING
        
    def update(self):
        for particle in self.background_particles:
            particle[1] += particle[3]
            if particle[1] > HEIGHT:
                particle[1] = 0
                particle[0] = random.randint(0, WIDTH)
                
        if self.combo_effect > 0:
            self.combo_effect -= 1
        
        if self.state != PLAYING:
            return
            
        self.current_time = pygame.time.get_ticks() - self.start_time
        
        for key in self.key_effects:
            if self.key_effects[key] > 0:
                self.key_effects[key] -= 1
        
        i = 0
        while i < len(self.active_notes):
            note = self.active_notes[i]
            if not note.update(self.current_time, self.scroll_speed):
                if note.missed:
                    self.register_miss()
                self.active_notes.pop(i)
            else:
                i += 1
                
        i = 0
        while i < len(self.notes):
            note = self.notes[i]
            if note.hit_time - self.approach_time <= self.current_time:
                self.active_notes.append(note)
                self.notes.pop(i)
            else:
                i += 1
                
        if self.judgement_time > 0:
            self.judgement_time -= 1
        else:
            self.judgement_text = ""
                
        if not self.notes and not self.active_notes and self.current_time > self.song_length:
            if self.current_music:
                pygame.mixer.music.stop()
            self.state = GAME_OVER
            
    def draw(self, screen):
        screen.fill(BLACK)
        
        for x, y, size, _ in self.background_particles:
            pygame.draw.circle(screen, (100, 100, 150), (int(x), int(y)), size)
        
        if self.state == MENU:
            self.draw_menu(screen)
        elif self.state == PLAYING or self.state == PAUSED:
            self.draw_game(screen)
        elif self.state == GAME_OVER:
            self.draw_game_over(screen)
        elif self.state == BEATMAP_SELECT:
            self.draw_beatmap_select(screen)
        elif self.state == SKIN_SELECT:
            self.draw_skin_select(screen)
            
        pygame.display.flip()
        
    def draw_menu(self, screen):
        # Logo centrado
        logo_rect = self.logo.get_rect(center=(WIDTH//2, HEIGHT//3))
        screen.blit(self.logo, logo_rect)
        
        # Posiciones de los botones (más separados para pantalla más grande)
        play_center = (WIDTH//2 + 250, HEIGHT//2)
        options_center = (WIDTH//2 - 250, HEIGHT//2)
        
        # Detectar hover
        mouse_pos = pygame.mouse.get_pos()
        play_hover = math.dist(mouse_pos, play_center) < 70  # Botones más grandes
        options_hover = math.dist(mouse_pos, options_center) < 70
        
        # Dibujar líneas desde el logo a los botones
        pygame.draw.line(screen, LIGHT_BLUE, logo_rect.midright, (play_center[0] - 70, play_center[1]), 3)
        pygame.draw.line(screen, LIGHT_BLUE, logo_rect.midleft, (options_center[0] + 70, options_center[1]), 3)
        
        # Efecto de brillo para PLAY
        if play_hover:
            for i in range(3):
                glow_radius = 70 + i * 10
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*LIGHT_BLUE, 50 - i*15), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (play_center[0] - glow_radius, play_center[1] - glow_radius))
        
        # Efecto de brillo para OPTIONS
        if options_hover:
            for i in range(3):
                glow_radius = 70 + i * 10
                glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*LIGHT_BLUE, 50 - i*15), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (options_center[0] - glow_radius, options_center[1] - glow_radius))
        
        # Botón PLAY (derecha) - más grande
        play_color = LIGHT_BLUE if play_hover else BLUE
        pygame.draw.circle(screen, play_color, play_center, 70)
        pygame.draw.circle(screen, WHITE, play_center, 70, 3)
        
        play_text = menu_font.render("PLAY", True, WHITE)
        play_text_rect = play_text.get_rect(center=play_center)
        screen.blit(play_text, play_text_rect)
        
        # Botón OPTIONS (izquierda) - más grande
        options_color = LIGHT_BLUE if options_hover else BLUE
        pygame.draw.circle(screen, options_color, options_center, 70)
        pygame.draw.circle(screen, WHITE, options_center, 70, 3)
        
        options_text = menu_font.render("OPTIONS", True, WHITE)
        options_text_rect = options_text.get_rect(center=options_center)
        screen.blit(options_text, options_text_rect)
        
        # Almacenar rectángulos para el manejo de eventos
        self.menu_options = [
            (pygame.Rect(play_center[0]-70, play_center[1]-70, 140, 140), 
             lambda: setattr(self, 'state', BEATMAP_SELECT)),
            (pygame.Rect(options_center[0]-70, options_center[1]-70, 140, 140), 
             lambda: setattr(self, 'state', SKIN_SELECT))
        ]
            
    def draw_beatmap_select(self, screen):
        title = title_font.render("SELECT BEATMAP", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        self.beatmap_options = []
        beatmaps = self.parser.get_beatmap_list()
        
        if not beatmaps:
            no_maps = menu_font.render("No beatmaps available", True, LIGHT_GRAY)
            screen.blit(no_maps, (WIDTH//2 - no_maps.get_width()//2, 200))
            
            help_text = game_font.render("Place .osu or .osz files in the 'beatmaps' folder", True, YELLOW)
            screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, 250))
        else:
            start_index = max(0, min(self.selected_beatmap or 0, len(beatmaps) - 6))  # Mostrar más beatmaps
            
            for i in range(start_index, min(start_index + 6, len(beatmaps))):
                y_pos = 150 + (i - start_index) * 60
                beatmap_text = game_font.render(beatmaps[i], True, LIGHT_GRAY)
                text_rect = beatmap_text.get_rect(center=(WIDTH//2, y_pos))
                
                if i == self.selected_beatmap:
                    bg_rect = pygame.Rect(text_rect.x - 15, text_rect.y - 5, text_rect.width + 30, text_rect.height + 10)
                    pygame.draw.rect(screen, (50, 50, 100), bg_rect, border_radius=8)
                    pygame.draw.rect(screen, LIGHT_BLUE, bg_rect, 2, border_radius=8)
                
                screen.blit(beatmap_text, text_rect)
                self.beatmap_options.append((text_rect, i))
        
        back_rect = pygame.Rect(50, HEIGHT - 80, 200, 60)
        pygame.draw.rect(screen, DARK_GRAY, back_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_GRAY, back_rect, 2, border_radius=10)
        back_text = menu_font.render("BACK", True, WHITE)
        screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2, back_rect.centery - back_text.get_height()//2))
        self.back_button = back_rect
        
        if self.selected_beatmap is not None:
            play_rect = pygame.Rect(WIDTH - 250, HEIGHT - 80, 200, 60)
            pygame.draw.rect(screen, GREEN, play_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, play_rect, 2, border_radius=10)
            play_text = menu_font.render("PLAY", True, WHITE)
            screen.blit(play_text, (play_rect.centerx - play_text.get_width()//2, play_rect.centery - play_text.get_height()//2))
            self.play_button = play_rect

    def draw_skin_select(self, screen):
        title = title_font.render("SELECT SKIN", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        self.skin_options = []
        skins = self.skin_manager.available_skins
        
        if not skins:
            no_skins = menu_font.render("No skins available", True, LIGHT_GRAY)
            screen.blit(no_skins, (WIDTH//2 - no_skins.get_width()//2, 200))
            
            help_text = game_font.render("Place .osk files in the 'skins' folder", True, YELLOW)
            screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, 250))
        else:
            start_index = max(0, min(self.skin_manager.available_skins.index(self.skin_manager.current_skin), len(skins) - 6))
            
            for i in range(start_index, min(start_index + 6, len(skins))):
                y_pos = 150 + (i - start_index) * 60
                skin_text = game_font.render(skins[i], True, LIGHT_GRAY)
                text_rect = skin_text.get_rect(center=(WIDTH//2, y_pos))
                
                if skins[i] == self.skin_manager.current_skin:
                    bg_rect = pygame.Rect(text_rect.x - 15, text_rect.y - 5, text_rect.width + 30, text_rect.height + 10)
                    pygame.draw.rect(screen, (50, 50, 100), bg_rect, border_radius=8)
                    pygame.draw.rect(screen, LIGHT_BLUE, bg_rect, 2, border_radius=8)
                
                screen.blit(skin_text, text_rect)
                self.skin_options.append((text_rect, skins[i]))
        
        back_rect = pygame.Rect(50, HEIGHT - 80, 200, 60)
        pygame.draw.rect(screen, DARK_GRAY, back_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_GRAY, back_rect, 2, border_radius=10)
        back_text = menu_font.render("BACK", True, WHITE)
        screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2, back_rect.centery - back_text.get_height()//2))
        self.back_button = back_rect
            
    def draw_game(self, screen):
        for i, x in enumerate(self.columns):
            pygame.draw.line(screen, BLUE, (x, 0), (x, HEIGHT), 2)
            
            receptor_height = 20
            color = self.get_column_color(i)
            
            pygame.draw.rect(screen, color, (x - self.column_width//2, self.receptor_y - receptor_height//2, self.column_width, receptor_height), border_radius=6)
            pygame.draw.rect(screen, WHITE, (x - self.column_width//2, self.receptor_y - receptor_height//2, self.column_width, receptor_height), 1, border_radius=6)
            
            key = self.key_bindings[i]
            key_name = KEY_NAMES.get(key, str(key))
            
            key_bg_rect = pygame.Rect(x - 25, self.receptor_y + 25, 50, 35)
            pygame.draw.rect(screen, LIGHT_GRAY, key_bg_rect, border_radius=6)
            pygame.draw.rect(screen, WHITE, key_bg_rect, 1, border_radius=6)
            
            key_text = key_font.render(key_name, True, BLACK)
            screen.blit(key_text, (x - key_text.get_width()//2, self.receptor_y + 32))
        
        for note in self.active_notes:
            note.draw(screen, self.current_time, self.columns, self.column_width, self.receptor_y, self.scroll_speed)
            
        # HUD simplificado
        score_text = game_font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        accuracy_text = game_font.render(f"Accuracy: {self.accuracy:.2f}%", True, WHITE)
        screen.blit(accuracy_text, (20, 50))
        
        if self.combo > 0:
            combo_text = combo_font.render(f"{self.combo}x", True, YELLOW)
            screen.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, 100))
            
        if self.judgement_text:
            judgement = judgement_font.render(self.judgement_text, True, WHITE)
            screen.blit(judgement, (WIDTH//2 - judgement.get_width()//2, HEIGHT//2 - 50))
            
        if self.state == PAUSED:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            pause_bg = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
            pygame.draw.rect(screen, (30, 30, 60), pause_bg, border_radius=20)
            pygame.draw.rect(screen, LIGHT_BLUE, pause_bg, 3, border_radius=20)
            
            pause_text = title_font.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 150))
            
            # Opciones del menú de pausa
            self.pause_options = []
            options = [
                ("RESUME", lambda: setattr(self, 'state', PLAYING)),
                ("RESTART", lambda: self.start_game(self.selected_beatmap)),
                ("MAIN MENU", lambda: self.return_to_menu()),
            ]
            
            for i, (text, action) in enumerate(options):
                y_pos = HEIGHT//2 - 50 + i * 80
                option_rect = pygame.Rect(WIDTH//2 - 150, y_pos, 300, 60)
                
                # Detectar hover
                mouse_pos = pygame.mouse.get_pos()
                is_hover = option_rect.collidepoint(mouse_pos)
                bg_color = LIGHT_BLUE if is_hover else BLUE
                
                pygame.draw.rect(screen, bg_color, option_rect, border_radius=15)
                pygame.draw.rect(screen, WHITE, option_rect, 2, border_radius=15)
                
                option_text = menu_font.render(text, True, WHITE)
                text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, text_rect)
                
                self.pause_options.append((option_rect, action))
            
    def return_to_menu(self):
        """Volver al menú principal desde pausa o juego"""
        if self.current_music:
            pygame.mixer.music.stop()
            self.current_music = None
        
        self.state = MENU
        self.play_random_menu_music()
            
    def draw_game_over(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        main_panel = pygame.Rect(WIDTH//2 - 300, 100, 600, 500)
        pygame.draw.rect(screen, DARK_GRAY, main_panel, border_radius=20)
        pygame.draw.rect(screen, LIGHT_BLUE, main_panel, 3, border_radius=20)
        
        game_over_text = title_font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 130))
        
        grade = self.calculate_grade()
        grade_text = title_font.render(grade, True, YELLOW)
        screen.blit(grade_text, (WIDTH//2 - grade_text.get_width()//2, 190))
        
        stats = [
            f"Score: {self.score}",
            f"Max Combo: {self.max_combo}",
            f"Accuracy: {self.accuracy:.2f}%",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = menu_font.render(stat, True, WHITE)
            screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, 250 + i*40))
            
        self.menu_options = []
        options = [
            ("PLAY AGAIN", lambda: self.start_game(self.selected_beatmap)),
            ("MAIN MENU", lambda: self.return_to_menu()),
        ]
        
        for i, (text, action) in enumerate(options):
            y_pos = 380 + i * 70
            option_rect = pygame.Rect(WIDTH//2 - 150, y_pos, 300, 60)
            pygame.draw.rect(screen, LIGHT_BLUE, option_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, option_rect, 2, border_radius=15)
            
            option_text = menu_font.render(text, True, WHITE)
            text_rect = option_text.get_rect(center=option_rect.center)
            screen.blit(option_text, text_rect)
            self.menu_options.append((option_rect, action))
            
        # Reanudar música del menú al volver
        if not self.menu_music:
            self.play_random_menu_music()
        
    def get_column_color(self, column):
        colors = [RED, ORANGE, YELLOW, GREEN]
        return colors[column % len(colors)]
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == PLAYING:
                        self.state = PAUSED
                        if self.current_music:
                            pygame.mixer.music.pause()
                    elif self.state == PAUSED:
                        self.state = PLAYING
                        if self.current_music:
                            pygame.mixer.music.unpause()
                    elif self.state in [BEATMAP_SELECT, SKIN_SELECT, GAME_OVER]:
                        self.state = MENU
                        # Reanudar música del menú si volvemos al menú principal
                        if not self.menu_music:
                            self.play_random_menu_music()
                
                if self.state == PLAYING and event.key in self.key_bindings:
                    column = self.key_bindings.index(event.key)
                    self.key_states[event.key] = True
                    self.key_effects[event.key] = 10
                    
                    for note in self.active_notes[:]:
                        if note.column == column:
                            time_diff = note.check_hit(self.current_time, True)
                            if time_diff is not False:
                                self.register_hit(time_diff, note.note_type)
                                if note.note_type == "normal" or (note.note_type == "hold" and not note.held):
                                    self.active_notes.remove(note)
                                break
                
                if event.type == pygame.KEYUP and event.key in self.key_bindings:
                    self.key_states[event.key] = False
                    column = self.key_bindings.index(event.key)
                    
                    for note in self.active_notes[:]:
                        if note.column == column and note.note_type == "hold" and note.held:
                            time_diff = note.check_hit(self.current_time, False, True)
                            if time_diff is not False:
                                self.register_hit(0, "hold_end")
                                self.active_notes.remove(note)
                                break
                                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == MENU:
                    for rect, action in self.menu_options:
                        if rect.collidepoint(mouse_pos):
                            action()
                            break
                            
                elif self.state == GAME_OVER:
                    for rect, action in self.menu_options:
                        if rect.collidepoint(mouse_pos):
                            action()
                            break
                            
                elif self.state == PAUSED:
                    for rect, action in self.pause_options:
                        if rect.collidepoint(mouse_pos):
                            action()
                            if action.__name__ == '<lambda>' and 'PLAYING' in str(action):
                                if self.current_music:
                                    pygame.mixer.music.unpause()
                            break
                            
                elif self.state == BEATMAP_SELECT:
                    for rect, beatmap_index in self.beatmap_options:
                        if rect.collidepoint(mouse_pos):
                            self.selected_beatmap = beatmap_index
                            break
                    
                    if hasattr(self, 'back_button') and self.back_button.collidepoint(mouse_pos):
                        self.state = MENU
                        if not self.menu_music:
                            self.play_random_menu_music()
                        
                    if hasattr(self, 'play_button') and self.play_button.collidepoint(mouse_pos) and self.selected_beatmap is not None:
                        self.start_game(self.selected_beatmap)
                
                elif self.state == SKIN_SELECT:
                    for rect, skin_name in self.skin_options:
                        if rect.collidepoint(mouse_pos):
                            self.skin_manager.set_skin(skin_name)
                            break
                    
                    if hasattr(self, 'back_button') and self.back_button.collidepoint(mouse_pos):
                        self.state = MENU
                        if not self.menu_music:
                            self.play_random_menu_music()
                        
        return True
        
    def register_hit(self, time_diff, note_type):
        if time_diff <= 25:
            judgement = "PERFECT"
            points = 300
        elif time_diff <= 50:
            judgement = "GREAT"
            points = 200
        elif time_diff <= 100:
            judgement = "GOOD"
            points = 100
        else:
            judgement = "BAD"
            points = 50
            
        points += points * self.combo // 50
        
        self.score += points
        self.combo += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo
            
        self.hits[judgement] += 1
        
        self.judgement_text = judgement
        self.judgement_time = 30
        self.combo_effect = 10
        
        total_hits = sum(self.hits.values())
        if total_hits > 0:
            accuracy = (self.hits["PERFECT"] * 300 + self.hits["GREAT"] * 200 + 
                       self.hits["GOOD"] * 100 + self.hits["BAD"] * 50) / (total_hits * 300)
            self.accuracy = accuracy * 100
            
    def register_miss(self):
        self.hits["MISS"] += 1
        self.combo = 0
        self.judgement_text = "MISS"
        self.judgement_time = 30
        
        total_hits = sum(self.hits.values())
        if total_hits > 0:
            accuracy = (self.hits["PERFECT"] * 300 + self.hits["GREAT"] * 200 + 
                       self.hits["GOOD"] * 100 + self.hits["BAD"] * 50) / (total_hits * 300)
            self.accuracy = accuracy * 100
            
    def calculate_grade(self):
        total_notes = sum(self.hits.values())
        if total_notes == 0:
            return "F"
            
        perfect_ratio = self.hits["PERFECT"] / total_notes
        great_ratio = self.hits["GREAT"] / total_notes
        good_ratio = self.hits["GOOD"] / total_notes
        bad_ratio = self.hits["BAD"] / total_notes
        miss_ratio = self.hits["MISS"] / total_notes
        
        if miss_ratio == 0 and bad_ratio == 0 and good_ratio == 0 and great_ratio == 0:
            return "SS"
        elif miss_ratio == 0 and bad_ratio == 0 and good_ratio == 0:
            return "S"
        elif miss_ratio == 0 and bad_ratio == 0:
            return "A"
        elif miss_ratio < 0.05:
            return "B"
        elif miss_ratio < 0.1:
            return "C"
        else:
            return "D"

# Función principal
def main():
    game = OsuMania()
    
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw(screen)
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
