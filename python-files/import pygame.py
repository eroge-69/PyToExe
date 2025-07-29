import pygame
import numpy as np
import sounddevice as sd
import random
import time

# --- Settings ---
WIDTH, HEIGHT = 1000, 600
FS = 44100  # Samplingrate
BUFFER_SIZE = 2048

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sound-to-Light Mehrere Effekte")

clock = pygame.time.Clock()
audio_data = np.zeros(BUFFER_SIZE)

def audio_callback(indata, frames, time, status):
    global audio_data
    if status:
        print(status)
    audio_data = indata[:, 0]

AUDIO_DEVICE = None

stream = sd.InputStream(
    device=AUDIO_DEVICE,
    channels=1,
    samplerate=FS,
    blocksize=BUFFER_SIZE,
    callback=audio_callback
)
stream.start()

# --- Effekt 1: Langsame sanfte Linien ---
class SlowLine:
    def __init__(self, orientation, color, length, thickness):
        self.orientation = orientation
        self.color = color
        self.length = length
        self.thickness = thickness
        self.pos = random.randint(0, HEIGHT if orientation == "horizontal" else WIDTH)
        self.direction = 1
        self.speed = 0.2  # sehr langsam

    def update(self, dt):
        self.pos += self.speed * self.direction * dt * 60
        max_pos = HEIGHT if self.orientation == "horizontal" else WIDTH
        if self.pos < 0 or self.pos > max_pos:
            self.direction *= -1
            self.pos = max(0, min(self.pos, max_pos))

    def draw(self, surface, alpha):
        color = (*self.color[:3], int(alpha))
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.orientation == "horizontal":
            start = (0, int(self.pos))
            end = (self.length, int(self.pos))
        else:
            start = (int(self.pos), 0)
            end = (int(self.pos), self.length)
        pygame.draw.line(surf, color, start, end, self.thickness)
        surface.blit(surf, (0, 0))

# --- Effekt 2: Drop Lines (wie vorher) ---
class DropLine:
    def __init__(self, orientation, color, base_speed, length, thickness):
        self.orientation = orientation
        self.color = color
        self.base_speed = base_speed
        self.speed = base_speed
        self.length = length
        self.thickness = thickness
        self.pos = random.randint(0, HEIGHT if orientation == "horizontal" else WIDTH)
        self.direction = 1
        self.speed_timer = 0

    def update(self, dt):
        if self.speed_timer > 0:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.speed = self.base_speed
        self.pos += self.speed * self.direction * dt * 60
        max_pos = HEIGHT if self.orientation == "horizontal" else WIDTH
        if self.pos < 0 or self.pos > max_pos:
            self.direction *= -1
            self.pos = max(0, min(self.pos, max_pos))

    def draw(self, surface, alpha):
        color = (*self.color[:3], int(alpha))
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if self.orientation == "horizontal":
            start = (0, int(self.pos))
            end = (self.length, int(self.pos))
        else:
            start = (int(self.pos), 0)
            end = (int(self.pos), self.length)
        pygame.draw.line(surf, color, start, end, self.thickness)
        surface.blit(surf, (0, 0))

    def speed_boost(self, duration, multiplier):
        self.speed = self.base_speed * multiplier * random.uniform(0.8, 1.3)
        self.speed_timer = duration

# --- Effekt 3: Strobe mit dicken Linien und Punkten ---
class StrobeEffect:
    def __init__(self, color):
        self.color = color
        self.alpha = 0
        self.brightness = 0
        self.active = False
        self.fade_speed = 8  # Wie schnell das Aufleuchten abnimmt
        # Linienpositionen (horizontal und vertikal)
        self.positions_h = [random.randint(0, HEIGHT) for _ in range(3)]
        self.positions_v = [random.randint(0, WIDTH) for _ in range(3)]

    def trigger(self):
        self.alpha = 255
        self.brightness = 255
        self.active = True

    def update(self, dt):
        if self.active:
            self.alpha -= self.fade_speed * dt * 60
            self.brightness -= self.fade_speed * dt * 60
            if self.alpha <= 0 or self.brightness <= 0:
                self.alpha = 0
                self.brightness = 0
                self.active = False

    def draw(self, surface):
        if not self.active:
            return
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # Dicke Linien horizontal
        for y in self.positions_h:
            color = (*self.color[:3], int(self.alpha))
            pygame.draw.line(surf, color, (0, y), (WIDTH, y), 8)

        # Dicke Linien vertikal
        for x in self.positions_v:
            color = (*self.color[:3], int(self.alpha))
            pygame.draw.line(surf, color, (x, 0), (x, HEIGHT), 8)

        # Punkte an Schnittpunkten
        for x in self.positions_v:
            for y in self.positions_h:
                pygame.draw.circle(surf, (*self.color[:3], int(self.brightness)), (x, y), 12)

        surface.blit(surf, (0, 0))

colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
]

# Erzeuge Linien für Effekte 1 und 2
slow_lines = []
drop_lines = []

for i in range(6):
    orientation = "horizontal" if i % 2 == 0 else "vertical"
    color = colors[i % len(colors)]
    slow_lines.append(SlowLine(orientation, color, WIDTH if orientation == "horizontal" else HEIGHT, 2))
    base_speed = 1 + i * 0.3
    drop_lines.append(DropLine(orientation, color, base_speed, WIDTH if orientation == "horizontal" else HEIGHT, 3))

# Strobe Effekt (ein Objekt)
strobe = StrobeEffect((255, 255, 255))

last_drop_time = 0
drop_cooldown = 0.5

def calculate_alpha():
    rms = np.sqrt(np.mean(audio_data**2))
    alpha = min(max(int(rms * 2000), 20), 150)
    return alpha, rms

running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    alpha, rms = calculate_alpha()

    # Drop trigger für Effekt 2 und 3
    if rms > 0.05 and (time.time() - last_drop_time) > drop_cooldown:
        last_drop_time = time.time()
        for line in drop_lines:
            line.speed_boost(duration=0.5, multiplier=4)
        strobe.trigger()

    # Haze Hintergrund
    screen.fill((0, 0, 0, 15))

    # Effekte zeichnen
    for line in slow_lines:
        line.update(dt)
        line.draw(screen, alpha // 3)  # langsame Linien sind weniger intensiv

    for line in drop_lines:
        line.update(dt)
        line.draw(screen, alpha)

    strobe.update(dt)
    strobe.draw(screen)

    pygame.display.flip()

stream.stop()
stream.close()
pygame.quit()
