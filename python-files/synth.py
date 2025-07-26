import sys
print(sys.executable)
import pygame
import numpy as np

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("באס עמוק - אוקטבה מעל Subbass")

sample_rate = 44100
duration = 5.0
volume = 0.5

def deep_bass_wave(freq, t):
    sine = np.sin(2 * np.pi * freq * t)
    # מודולציית עוצמה איטית ל'נשימה' טבעית
    amp_mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.03 * t)
    wave = sine * amp_mod
    return wave

def generate_deep_bass_sound(freq):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = deep_bass_wave(freq, t)
    wave = (wave * volume * 32767).astype(np.int16)
    sound = pygame.mixer.Sound(buffer=wave.tobytes())
    return sound

semitone_ratio = 2 ** (1/12)
base_freq = 13.75  # אוקטבה מעל 6.875 הרץ
keys = ['a', 'w', 's', 'e', 'd', 'f', 't', 'g', 'y', 'h', 'u', 'j', 'k']
key_mapping = {}
for i, key_char in enumerate(keys):
    freq = base_freq * (semitone_ratio ** i)
    key = pygame.key.key_code(key_char)
    key_mapping[key] = generate_deep_bass_sound(freq)

playing_keys = {}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in key_mapping and event.key not in playing_keys:
                sound = key_mapping[event.key]
                sound.play(-1)
                playing_keys[event.key] = sound

        elif event.type == pygame.KEYUP:
            if event.key in playing_keys:
                playing_keys[event.key].stop()
                del playing_keys[event.key]

    pygame.time.delay(10)

pygame.quit()
