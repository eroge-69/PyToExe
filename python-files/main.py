import pygame
import sounddevice as sd
import numpy as np
import sys
from pathlib import Path

pygame.init()
WINDOW_SIZE = (800, 600)
BACKGROUND_COLOR = (0, 255, 0)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("VoiceAvatar")

assets_dir = Path(__file__).parent / "assets"
try:
    icon = pygame.image.load(assets_dir / "icon.png")
    pygame.display.set_icon(icon)
except Exception as e:
    print(f"Не удалось загрузить иконку: {e}")

images = []
for i in range(4):
    try:
        img = pygame.image.load(assets_dir / f"{i}.png")
        images.append(pygame.transform.scale(img, WINDOW_SIZE))
    except Exception as e:
        print(f"Изображение не загружено: {e}")
        sys.exit(1)

current_image = 0
THERESOLDS = [0.01, 0.05, 0.1]

def audio_callback(indata, frames, time, status):
    global current_image
    if status:
        print(status, file=sys.stderr)

    rms = np.sqrt(np.mean(np.square(indata)))
    if rms < THERESOLDS[0]:
        current_image = 0
    elif rms < THERESOLDS[1]:
        current_image = 1
    elif rms < THERESOLDS[2]:
        current_image = 2
    else:
        current_image = 3

try:
    with sd.InputStream(samplerate=44100, blocksize=1024, channels=1, callback=audio_callback):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            window.fill(BACKGROUND_COLOR)
            window.blit(images[current_image], (0, 0))
            pygame.display.flip()

except Exception as e:
    print(f"Ошибка: {e}")
finally:
    pygame.quit()



