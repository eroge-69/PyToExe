
import pygame, sys, random, math, io, base64

# ---------------------- Dźwięk kropli w base64 ----------------------
rain_wav_b64 = """
UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=
"""  # Miniaturowy "klik" (syntetyczny krótki dźwięk)

rain_wav_bytes = base64.b64decode(rain_wav_b64)
rain_sound_file = io.BytesIO(rain_wav_bytes)

# ---------------------- Inicjalizacja ----------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Symulator deszczu")
clock = pygame.time.Clock()
FPS = 60

# Kolory
BLACK = (0,0,0)
BLUE = (0,150,255)
GRAY = (50,50,60)

# Wczytaj dźwięk
rain_sound = pygame.mixer.Sound(rain_sound_file)
rain_sound.set_volume(0.1)
rain_sound.play(loops=-1)

# ---------------------- Deszcz ----------------------
class Raindrop:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(4, 8)
        self.length = random.randint(8, 14)
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()
    def draw(self, surf):
        pygame.draw.line(surf, BLUE, (self.x,self.y), (self.x,self.y+self.length), 2)

raindrops = [Raindrop() for _ in range(120)]

# ---------------------- Główna pętla ----------------------
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
    screen.fill(GRAY)
    for drop in raindrops:
        drop.update()
        drop.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
