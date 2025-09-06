import pygame
import sys
import random
import math
import os

# ----- Sabitler ve Başlangıç Ayarları -----
# Ekran boyutları
WIDTH, HEIGHT = 800, 600
# Ekran adı
TITLE = "Karanlık Orman: İki Kahraman"
# FPS
FPS = 60

# Renkler
COLORS = {
    "DARK_SKY": (25, 25, 40),       # Koyu lacivert
    "BLOOD_RED": (136, 8, 8),       # Kan kırmızısı
    "DARK_GROUND": (40, 30, 30),    # Koyu toprak
    "BLUE": (30, 144, 255),         # Mavi
    "GREEN": (50, 205, 50),         # Yeşil
    "YELLOW": (255, 215, 0),        # Sarı
    "PURPLE": (138, 43, 226),       # Mor
    "ORANGE": (255, 140, 0),        # Turuncu
    "DARK_RED": (139, 0, 0),        # Koyu Kırmızı
    "GOLD": (255, 215, 0),          # Altın
    "LIGHT_BLUE": (173, 216, 230),  # Açık Mavi
    "PINK": (255, 192, 203),        # Pembe
    "HOT_PINK": (255, 105, 180),    # Sıcak Pembe
    "MAGENTA": (255, 0, 255),       # Magenta
    "WHITE": (255, 255, 255),       # Beyaz
    "BLACK": (0, 0, 0),             # Siyah
    "DARK_PURPLE": (48, 25, 52),    # Koyu Mor
    "BONE": (227, 218, 201),        # Kemik rengi
    "DARK_BROWN": (60, 40, 30),     # Koyu Kahverengi
    "DARK_GREEN": (20, 50, 30)      # Koyu Yeşil
}

# Oyun ayarları
PLAYER_SPEED = 7
ENEMY_TYPES = {
    "chaser": {"speed": 2, "size": 50},
    "zigzag": {"speed": 3, "size": 45},
    "dropper": {"speed": 3, "size": 40},
}

HEAT_DECAY_RATE = 0.35
HEAT_GAIN_RATE = 4
MAX_HEAT = 100
WIN_SCORE = 75


# Oyun durumları
GAME_STATE_PLAYING = "playing"
GAME_STATE_GAME_OVER = "game_over"

# ----- Ses Efektleri -----
def load_sounds():
    sounds = {}
    try:
        # Kara fantezi temalı sesler oluştur
        # Korkutucu uğultu (düşman yakınlığı)
        sample_rate = 44100
        duration = 1.0  # saniye
        frames = int(duration * sample_rate)
        sound_data = bytearray()
        for i in range(frames):
            value = int(127 + 100 * math.sin(i/50) * math.sin(i/200))
            sound_data.append(value)
        sounds["enemy_near"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["enemy_near"].set_volume(0.3)
        
        # Karanlık çarpışma sesi
        sound_data = bytearray()
        for i in range(1000):
            value = int(127 + 120 * (math.sin(i/10) + 0.5 * math.sin(i/3)) * math.exp(-i/500))
            sound_data.append(value)
        sounds["collision"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["collision"].set_volume(0.4)
        
        # Korkunç game over sesi
        sound_data = bytearray()
        for i in range(3000):
            value = int(127 + 120 * math.sin(i/100) * math.exp(-i/1000))
            sound_data.append(value)
        sounds["game_over"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["game_over"].set_volume(0.5)
        
        # Zafer sesi (daha hafif)
        sound_data = bytearray()
        for i in range(2500):
            value = int(127 + 100 * math.sin(i/30) * math.exp(-i/2000))
            sound_data.append(value)
        sounds["victory"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["victory"].set_volume(0.4)
        
        # Isınma sesi
        sound_data = bytearray()
        for i in range(1500):
            value = int(127 + 80 * math.sin(i/20) * math.exp(-i/1000))
            sound_data.append(value)
        sounds["heat_up"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["heat_up"].set_volume(0.3)
        
        # Düşman sesleri
        sound_data = bytearray()
        for i in range(2000):
            value = int(127 + 110 * math.sin(i/40) * math.sin(i/150))
            sound_data.append(value)
        sounds["enemy_growl"] = pygame.mixer.Sound(buffer=bytes(sound_data))
        sounds["enemy_growl"].set_volume(0.3)
        
    except Exception as e:
        # Ses oluşturma hatası
        print(f"Ses oluşturma hatası: {e}, sessiz modda çalışılıyor")
        silent_sound = pygame.mixer.Sound(buffer=bytearray([127]*100))
        sounds = {
            "collision": silent_sound,
            "game_over": silent_sound,
            "victory": silent_sound,
            "heat_up": silent_sound,
            "enemy_near": silent_sound,
            "enemy_growl": silent_sound
        }
    
    return sounds

# ----- Sprite Oluşturma Fonksiyonları -----
def create_player_sprite(color, size=40):
    # Orta dünya temalı savaşçı sprite'ı oluştur
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Gövde (zırh)
    pygame.draw.rect(surface, color, (5, 10, size-10, size-15), border_radius=5)
    
    # Kafa
    pygame.draw.circle(surface, (210, 180, 140), (size//2, size//4), size//5)
    
    # Gözler
    pygame.draw.circle(surface, COLORS["BLACK"], (size//2 - 5, size//4 - 2), 3)
    pygame.draw.circle(surface, COLORS["BLACK"], (size//2 + 5, size//4 - 2), 3)
    
    # Miğfer/kask
    pygame.draw.arc(surface, color, (size//4, size//6, size//2, size//3), math.pi, 2*math.pi, 3)
    
    # Kılıç veya mızrak
    pygame.draw.line(surface, COLORS["BONE"], (size-5, size//2), (size+5, size//2 - 10), 2)
    
    return surface

def create_enemy_sprite(enemy_type, size):
    # Kara fantezi temalı düşman sprite'ı oluştur
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    if enemy_type == "chaser":
        # Korkunç kara savaşçı
        color = COLORS["DARK_RED"]
        # Gövde
        pygame.draw.rect(surface, color, (5, 10, size-10, size-10), border_radius=3)
        # Kafa
        pygame.draw.circle(surface, COLORS["DARK_BROWN"], (size//2, size//4), size//5)
        # Gözler (kırmızı)
        pygame.draw.circle(surface, COLORS["BLOOD_RED"], (size//2 - 5, size//4 - 2), 4)
        pygame.draw.circle(surface, COLORS["BLOOD_RED"], (size//2 + 5, size//4 - 2), 4)
        # Boynuzlar
        pygame.draw.line(surface, COLORS["DARK_BROWN"], (size//2 - 8, size//6), (size//2 - 15, size//10), 3)
        pygame.draw.line(surface, COLORS["DARK_BROWN"], (size//2 + 8, size//6), (size//2 + 15, size//10), 3)
        # Kanlı kılıç
        pygame.draw.line(surface, COLORS["BLOOD_RED"], (size-5, size//2), (size+8, size//2 - 5), 3)
        
    elif enemy_type == "zigzag":
        # Tuhaf hareketli yaratık
        color = COLORS["DARK_PURPLE"]
        # Vücut (dairesel)
        pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 5)
        # Gözler
        pygame.draw.circle(surface, COLORS["MAGENTA"], (size//2 - 8, size//2 - 5), 5)
        pygame.draw.circle(surface, COLORS["MAGENTA"], (size//2 + 8, size//2 - 5), 5)
        # Pupiller
        pygame.draw.circle(surface, COLORS["BLACK"], (size//2 - 8, size//2 - 5), 2)
        pygame.draw.circle(surface, COLORS["BLACK"], (size//2 + 8, size//2 - 5), 2)
        # Ağız
        pygame.draw.arc(surface, COLORS["BLACK"], (size//4, size//2, size//2, size//3), 0, math.pi, 2)
        # Dokunaçlar
        for i in range(4):
            angle = i * math.pi / 2 + pygame.time.get_ticks() / 500
            end_x = size//2 + int(math.cos(angle) * size//2)
            end_y = size//2 + int(math.sin(angle) * size//2)
            pygame.draw.line(surface, color, (size//2, size//2), (end_x, end_y), 2)
        
    elif enemy_type == "dropper":
        # Uçan yaratık
        color = COLORS["DARK_GREEN"]
        # Kanatlar
        wing_beat = math.sin(pygame.time.get_ticks() / 200) * 5
        pygame.draw.ellipse(surface, color, (5, 10 + wing_beat, size-10, size-20))
        # Gövde
        pygame.draw.ellipse(surface, COLORS["DARK_BROWN"], (size//4, size//4, size//2, size//2))
        # Gözler
        pygame.draw.circle(surface, COLORS["YELLOW"], (size//2, size//2 - 5), 4)
        # Gaga
        pygame.draw.polygon(surface, COLORS["BONE"], [(size//2, size//2 + 5), 
                                                     (size//2 + 5, size//2 + 10), 
                                                     (size//2 - 5, size//2 + 10)])
    
    return surface

# ----- Animasyon Sınıfları -----
class AnimatedText:
    def __init__(self, text, font, color, target_pos, delay=0, animation_type="fade_slide"):
        self.text = text
        self.font = font
        self.color = color
        self.target_pos = target_pos
        self.delay = delay
        self.animation_type = animation_type
        self.timer = 0
        self.alpha = 0
        self.current_pos = list(target_pos)
        self.scale = 0.1
        self.visible = False
        
        if animation_type == "slide_down":
            self.current_pos[1] = target_pos[1] - 100
        elif animation_type == "slide_up":
            self.current_pos[1] = target_pos[1] + 100
        elif animation_type == "slide_left":
            self.current_pos[0] = target_pos[0] - 200
        elif animation_type == "slide_right":
            self.current_pos[0] = target_pos[0] + 200
    
    def update(self):
        self.timer += 1
        
        if self.timer < self.delay:
            return
            
        self.visible = True
        progress = min(1.0, (self.timer - self.delay) / 60.0)
        eased_progress = 1 - (1 - progress) ** 3
        
        if self.animation_type == "fade_slide":
            self.alpha = int(255 * eased_progress)
            self.current_pos[1] = self.target_pos[1] + (1 - eased_progress) * 50
            
        elif self.animation_type == "scale_bounce":
            self.alpha = int(255 * min(1.0, progress * 2))
            if progress < 1.0:
                bounce = math.sin(progress * math.pi * 2) * 0.2 * (1 - progress)
                self.scale = eased_progress * 1.2 + bounce
            else:
                self.scale = 1.0
                
        elif self.animation_type in ["slide_down", "slide_up", "slide_left", "slide_right"]:
            self.alpha = int(255 * eased_progress)
            if self.animation_type == "slide_down":
                self.current_pos[1] = self.target_pos[1] - 100 * (1 - eased_progress)
            elif self.animation_type == "slide_up":
                self.current_pos[1] = self.target_pos[1] + 100 * (1 - eased_progress)
            elif self.animation_type == "slide_left":
                self.current_pos[0] = self.target_pos[0] - 200 * (1 - eased_progress)
            elif self.animation_type == "slide_right":
                self.current_pos[0] = self.target_pos[0] + 200 * (1 - eased_progress)
    
    def draw(self, screen):
        if not self.visible or self.alpha <= 0:
            return
            
        text_surface = self.font.render(self.text, True, self.color)
        
        if self.animation_type == "scale_bounce":
            original_size = text_surface.get_size()
            new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
            if new_size[0] > 0 and new_size[1] > 0:
                text_surface = pygame.transform.scale(text_surface, new_size)
        
        text_surface.set_alpha(self.alpha)
        rect = text_surface.get_rect()
        rect.center = self.current_pos
        screen.blit(text_surface, rect)

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, particle_type="normal"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.particle_type = particle_type
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-5, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.angle += self.spin
        
        if self.particle_type == "explosion":
            self.vy += 0.1
            self.vx *= 0.98
            self.vy *= 0.98
            alpha_ratio = self.lifetime / self.max_lifetime
            self.size = self.max_size * alpha_ratio
            
        elif self.particle_type == "celebration":
            self.vy += 0.05
            if self.lifetime < self.max_lifetime * 0.3:
                alpha_ratio = self.lifetime / (self.max_lifetime * 0.3)
                self.size = self.max_size * alpha_ratio
        
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.size > 0:
            if self.particle_type == "celebration":
                points = []
                for i in range(8):
                    angle = (self.angle + i * 45) * math.pi / 180
                    if i % 2 == 0:
                        radius = self.size
                    else:
                        radius = self.size * 0.4
                    px = self.x + math.cos(angle) * radius
                    py = self.y + math.sin(angle) * radius
                    points.append((px, py))
                if len(points) > 2:
                    pygame.draw.polygon(screen, self.color, points)
            else:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class GameOverScreen:
    
    def __init__(self, sounds):
        self.sounds = sounds
        self.reset()
    
    def reset(self):
        self.timer = 0
        self.animated_texts = []
        self.particles = []
        self.background_alpha = 0
        self.is_win = False
        self.score_particles = []
        self.floating_elements = []
        self.screen_shake = 0
        
    def start_animation(self, is_win, score):
        self.reset()
        self.is_win = is_win
        
        # Ses efekti çal
        if is_win:
            self.sounds["victory"].play()
        else:
            self.sounds["game_over"].play()
        
        title_font = pygame.font.SysFont("Arial", 64, bold=True)
        normal_font = pygame.font.SysFont("Arial", 28)
        small_font = pygame.font.SysFont("Arial", 22)
        
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        if is_win:
            background = pygame.image.load("gorsel.jpeg")
            background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
            self.background = background  # sadece referansı kaydet
            self.animated_texts = [
                AnimatedText("🏆 ZAFER! 🏆", title_font, COLORS["GOLD"], 
                           (center_x, center_y - 100), delay=0, animation_type="scale_bounce"),
                AnimatedText("Karanlığı yendiniz!", normal_font, COLORS["YELLOW"], 
                           (center_x, center_y - 40), delay=20, animation_type="slide_down"),
                AnimatedText(f"Final Skor: {score}", normal_font, COLORS["GREEN"], 
                           (center_x, center_y), delay=40, animation_type="fade_slide"),
                AnimatedText("İkiniz mükemmel bir takım oldunuz!", small_font, COLORS["LIGHT_BLUE"], 
                           (center_x, center_y + 40), delay=60, animation_type="slide_up"),
                AnimatedText("R - Tekrar Oyna", small_font, COLORS["HOT_PINK"], 
                           (center_x, center_y + 90), delay=80, animation_type="fade_slide")
            ]
            
            for _ in range(100):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                vx = random.uniform(-4, 4)
                vy = random.uniform(-6, -2)
                colors = [COLORS["GOLD"], COLORS["YELLOW"], COLORS["ORANGE"], COLORS["GREEN"], COLORS["HOT_PINK"]]
                color = random.choice(colors)
                size = random.uniform(3, 8)
                lifetime = random.randint(150, 250)
                self.particles.append(Particle(x, y, vx, vy, color, size, lifetime, "celebration"))
            
        else:
            self.screen_shake = 30
            
            self.animated_texts = [
                AnimatedText("💀 YENİLGİ 💀", title_font, COLORS["DARK_RED"], 
                           (center_x, center_y - 100), delay=0, animation_type="scale_bounce"),
                AnimatedText("Karanlık sizi yuttu!", normal_font, COLORS["BLOOD_RED"], 
                           (center_x, center_y - 40), delay=30, animation_type="slide_left"),
                AnimatedText(f"Son Skor: {score}", normal_font, COLORS["ORANGE"], 
                           (center_x, center_y), delay=50, animation_type="slide_right"),
                AnimatedText("Bir dahaki sefere daha güçlü olun!", small_font, COLORS["YELLOW"], 
                           (center_x, center_y + 40), delay=70, animation_type="fade_slide"),
                AnimatedText("R - Tekrar Dene", small_font, COLORS["BLUE"], 
                           (center_x, center_y + 90), delay=90, animation_type="fade_slide")
            ]
            
            for _ in range(60):
                x = random.randint(100, WIDTH - 100)
                y = random.randint(100, HEIGHT - 100)
                vx = random.uniform(-6, 6)
                vy = random.uniform(-6, 6)
                colors = [COLORS["BLOOD_RED"], COLORS["DARK_RED"], COLORS["ORANGE"], COLORS["DARK_PURPLE"]]
                color = random.choice(colors)
                size = random.uniform(2, 6)
                lifetime = random.randint(80, 150)
                self.particles.append(Particle(x, y, vx, vy, color, size, lifetime, "explosion"))
    
    def update(self):
        self.timer += 1
        
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - 1)
        
        if self.background_alpha < 200:
            self.background_alpha = min(200, self.background_alpha + 2)
        
        for text in self.animated_texts:
            text.update()
        
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen):
        shake_offset_x = 0
        shake_offset_y = 0
        if not self.is_win and self.screen_shake > 0:
            shake_intensity = min(5, self.screen_shake // 3)
            shake_offset_x = random.randint(-shake_intensity, shake_intensity)
            shake_offset_y = random.randint(-shake_intensity, shake_intensity)
        
        if self.background_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            if self.is_win:
                overlay.fill((40, 30, 60))
            else:
                overlay.fill((20, 10, 10))
            overlay.set_alpha(self.background_alpha)
            screen.blit(overlay, (shake_offset_x, shake_offset_y))
        
        for particle in self.particles:
            original_x = particle.x
            original_y = particle.y
            particle.x += shake_offset_x
            particle.y += shake_offset_y
            particle.draw(screen)
            particle.x = original_x
            particle.y = original_y
        
        for text in self.animated_texts:
            original_pos = text.current_pos
            text.current_pos = [original_pos[0] + shake_offset_x, original_pos[1] + shake_offset_y]
            text.draw(screen)
            text.current_pos = original_pos
        if self.is_win and hasattr(self, "background"):
            screen.blit(self.background, (0, 0))

# ----- Fonksiyonlar -----
def draw_centered_text(font, screen, text_list, y_offset_start, line_height):
    """Verilen metinleri ekranın ortasında dikey olarak sıralar ve çizer."""
    screen_width, screen_height = screen.get_size()
    for i, (text, color) in enumerate(text_list):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(centerx=screen_width // 2)
        text_rect.centery = screen_height // 2 + y_offset_start + i * line_height
        screen.blit(text_surface, text_rect)

def reset_game():
    """Tüm oyun değişkenlerini başlangıç durumuna döndürür."""
    global player1, player2, enemies, heat, score, game_state, snowflakes, game_over_screen, last_collision_time, particles
    
    player1.topleft = (100, 500)
    player2.topleft = (200, 500)
    
    heat = MAX_HEAT
    score = 0
    game_state = GAME_STATE_PLAYING
    last_collision_time = 0
    particles = []
    
    snowflakes = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(50)]
    
    enemies = [
        {"rect": pygame.Rect(600, 500, ENEMY_TYPES["chaser"]["size"], ENEMY_TYPES["chaser"]["size"]), 
         "type": "chaser", "speed": ENEMY_TYPES["chaser"]["speed"], "sprite": None},
        {"rect": pygame.Rect(0, 200, ENEMY_TYPES["zigzag"]["size"], ENEMY_TYPES["zigzag"]["size"]), 
         "type": "zigzag", "speed": ENEMY_TYPES["zigzag"]["speed"], "dir": 2, "sprite": None},
        {"rect": pygame.Rect(random.randint(0, WIDTH-ENEMY_TYPES["dropper"]["size"]), 0, 
                           ENEMY_TYPES["dropper"]["size"], ENEMY_TYPES["dropper"]["size"]), 
         "type": "dropper", "speed": ENEMY_TYPES["dropper"]["speed"], "sprite": None}
    ]
    
    # Düşman sprite'larını oluştur
    for enemy in enemies:
        enemy["sprite"] = create_enemy_sprite(enemy["type"], enemy["rect"].width)
    
    game_over_screen.reset()

def keep_players_in_bounds():
    """Oyuncuları ekran sınırları içinde tutar."""
    player1.left = max(0, player1.left)
    player1.right = min(WIDTH, player1.right)
    player1.top = max(0, player1.top)
    player1.bottom = min(HEIGHT, player1.bottom)
    
    player2.left = max(0, player2.left)
    player2.right = min(WIDTH, player2.right)
    player2.top = max(0, player2.top)
    player2.bottom = min(HEIGHT, player2.bottom)

def update_enemies():
    """Düşman pozisyonlarını türlerine göre günceller."""
    for enemy in enemies:
        rect = enemy["rect"]
        enemy_type = enemy["type"]
        speed = enemy["speed"]

        if enemy_type == "chaser":
            # Hangi oyuncuya daha yakınsa onu takip et
            dist1 = math.hypot(player1.centerx - rect.centerx, player1.centery - rect.centery)
            dist2 = math.hypot(player2.centerx - rect.centerx, player2.centery - rect.centery)
            
            target = player1 if dist1 < dist2 else player2
            
            dx = target.centerx - rect.centerx
            dy = target.centery - rect.centery
            
            if abs(dx) > speed:
                rect.x += speed if dx > 0 else -speed
            if abs(dy) > speed:
                rect.y += speed if dy > 0 else -speed

        elif enemy_type == "zigzag":
            rect.x += speed * enemy["dir"]
            time_factor = pygame.time.get_ticks() / 500.0
            rect.y = 200 + int(30 * pygame.math.Vector2(1, 0).rotate(time_factor * 180).y)
            
            if rect.right >= WIDTH or rect.left <= 0:
                enemy["dir"] *= -1
                rect.x = max(0, min(WIDTH - rect.width, rect.x))

        elif enemy_type == "dropper":
            rect.y += speed
            if rect.top > HEIGHT:
                rect.x = random.randint(0, WIDTH - rect.width)
                rect.y = -rect.height
                
        # Düşman sprite'ını güncelle
        enemy["sprite"] = create_enemy_sprite(enemy_type, rect.width)

def handle_player_movement(keys):
    """Tuş basışlarına göre oyuncu hareketini yönetir."""
    if keys[pygame.K_a]:
        player1.x -= PLAYER_SPEED
    if keys[pygame.K_d]:
        player1.x += PLAYER_SPEED
    if keys[pygame.K_w]:
        player1.y -= PLAYER_SPEED
    if keys[pygame.K_s]:
        player1.y += PLAYER_SPEED
    
    if keys[pygame.K_RIGHT]:
        player2.x += PLAYER_SPEED
    if keys[pygame.K_LEFT]:
        player2.x -= PLAYER_SPEED
    if keys[pygame.K_UP]:
        player2.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        player2.y += PLAYER_SPEED
    
    keep_players_in_bounds()

# ----- Pygame Başlangıcı -----
pygame.init()
pygame.mixer.init()  # Ses sistemi başlat
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# Sesleri yükle
sounds = load_sounds()

# Oyuncu sprite'larını oluştur
player1_sprite = create_player_sprite(COLORS["BLUE"])
player2_sprite = create_player_sprite(COLORS["GREEN"])

# Oyuncular
player1 = pygame.Rect(100, 500, 40, 40)
player2 = pygame.Rect(200, 500, 40, 40)

# Oyun değişkenleri
heat = MAX_HEAT
score = 0
game_state = GAME_STATE_PLAYING
last_collision_time = 0  # Son çarpışma zamanı
particles = []  # Parçacık listesi
last_enemy_sound_time = 0  # Son düşman sesi zamanı

# Düşmanlar ve kar taneleri
enemies = []
snowflakes = []
game_over_screen = GameOverScreen(sounds)
reset_game()

# ----- Ana Oyun Döngüsü -----
running = True
frame_count = 0

while running:
    frame_count += 1
    
    # Olay yönetimi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == GAME_STATE_GAME_OVER and event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_ESCAPE:
                running = False
    
    if game_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        handle_player_movement(keys)
        update_enemies()
        
        heat -= HEAT_DECAY_RATE
        
        # Oyuncular çarpıştığında ısı artışı
        if player1.colliderect(player2):
            current_time = pygame.time.get_ticks()
            if current_time - last_collision_time > 500:  # 0.5 saniyede bir
                heat = min(MAX_HEAT, heat + HEAT_GAIN_RATE * 5)
                last_collision_time = current_time
                sounds["heat_up"].play()
        
        if frame_count % 10 == 0:
            score += 1
        
        win = score >= WIN_SCORE
        game_over = heat <= 0
        
        # Düşmanlarla çarpışma kontrolü
        for enemy in enemies:
            if player1.colliderect(enemy["rect"]) or player2.colliderect(enemy["rect"]):
                game_over = True
                sounds["collision"].play()
                break
        
        # Düşman yakınlığı uyarısı
        enemy_near = False
        for enemy in enemies:
            for player in [player1, player2]:
                dist = math.hypot(player.centerx - enemy["rect"].centerx, 
                                 player.centery - enemy["rect"].centery)
                if dist < 100:  # 100 piksel yakınlık
                    enemy_near = True
                    break
            if enemy_near:
                break
        
        if enemy_near and frame_count % 30 == 0:  # Her 0.5 saniyede bir
            sounds["enemy_near"].play()
            
        # Düşman sesleri (homurtu)
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_sound_time > 2000:  # Her 2 saniyede bir
            sounds["enemy_growl"].play()
            last_enemy_sound_time = current_time
        
        if win or game_over:
            game_state = GAME_STATE_GAME_OVER
            game_over_screen.start_animation(win, score)
    
    # Her şeyi çiz
    screen.fill(COLORS["DARK_SKY"])
    pygame.draw.rect(screen, COLORS["DARK_GROUND"], (0, HEIGHT-50, WIDTH, 50))
    
    # Karanlık orman efekti - düşen yapraklar/ışıklar
    for flake in snowflakes:
        flake[1] += 2
        flake[0] += random.uniform(-0.5, 0.5)
        if flake[1] > HEIGHT:
            flake[0] = random.randint(0, WIDTH)
            flake[1] = 0
        color = random.choice([COLORS["DARK_RED"], COLORS["DARK_PURPLE"], COLORS["DARK_GREEN"]])
        pygame.draw.circle(screen, color, (int(flake[0]), int(flake[1])), 2)

    if game_state == GAME_STATE_PLAYING:
        # Oyuncu sprite'larını çiz
        screen.blit(player1_sprite, player1)
        screen.blit(player2_sprite, player2)
        
        # Oyuncular yakın olduğunda etkileşim efekti (kutsal ışık)
        if player1.colliderect(player2.inflate(20, 20)):
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
            radius = 30 + int(10 * pulse)
            pygame.draw.circle(screen, COLORS["YELLOW"], player1.center, radius, 3)
            pygame.draw.circle(screen, COLORS["YELLOW"], player2.center, radius, 3)
            
            # Parçacık efekti (kutsal enerji)
            if frame_count % 3 == 0:
                for _ in range(2):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1, 3)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    mid_x = (player1.centerx + player2.centerx) / 2
                    mid_y = (player1.centery + player2.centery) / 2
                    particles.append(Particle(mid_x, mid_y, vx, vy, COLORS["YELLOW"], 
                                             random.uniform(2, 5), random.randint(20, 40)))
        
        # Düşmanları çiz
        for enemy in enemies:
            screen.blit(enemy["sprite"], enemy["rect"])
            
            # Düşman etrafında karanlık aura
            if enemy["type"] == "chaser":
                pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
                radius = enemy["rect"].width//2 + int(10 * pulse)
                pygame.draw.circle(screen, COLORS["BLOOD_RED"], enemy["rect"].center, radius, 2)
        
        # Parçacıkları güncelle ve çiz
        particles = [p for p in particles if p.update()]
        for p in particles:
            p.draw(screen)
        
        # Skor göstergesi (kutsal işaretler)
        star_count = score // 100
        for i in range(star_count):
            star_x = 20 + i * 25
            star_y = 20
            pygame.draw.circle(screen, COLORS["GOLD"], (star_x, star_y), 8)
            pygame.draw.circle(screen, COLORS["YELLOW"], (star_x, star_y), 5)
        
        # Isı çubuğunu çiz (yaşam enerjisi)
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH - bar_width - 10
        bar_y = 10
        
        pygame.draw.rect(screen, COLORS["BLACK"], (bar_x-2, bar_y-2, bar_width+4, bar_height+4), border_radius=3)
        pygame.draw.rect(screen, COLORS["DARK_RED"], (bar_x, bar_y, bar_width, bar_height), border_radius=2)
        
        heat_color = COLORS["BLOOD_RED"] if heat < 30 else COLORS["ORANGE"] if heat < 60 else COLORS["YELLOW"]
        pygame.draw.rect(screen, heat_color, (bar_x, bar_y, int(bar_width * (heat/MAX_HEAT)), bar_height), border_radius=2)
        
        # Isı seviyesi metni
        heat_text = font.render(f"Yaşam Enerjisi: {int(heat)}%", True, heat_color)
        screen.blit(heat_text, (bar_x - 50, bar_y + 25))
        
        # Skor metni
        score_text = font.render(f"Hayatta Kalma Süresi: {score}/{WIN_SCORE}", True, COLORS["WHITE"])
        screen.blit(score_text, (10, 10))
        
    elif game_state == GAME_STATE_GAME_OVER:
        game_over_screen.update()
        game_over_screen.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)
    
# Temizleme
pygame.quit()
sys.exit()