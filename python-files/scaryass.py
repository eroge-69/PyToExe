import pygame
import multiprocessing
import threading
import time
import random
import os
from pygame import mixer

# === Конфигурация ===
IMAGES = [
    "horror_face.png",
    "screamer1.webp",
    "screamer2.jpeg"
]

SOUNDS = [
    "scary.mp3",
    "scary4.mp3",
    "scary3.mp3",
    "scary2.mp3"
]

NUM_WINDOWS = 1000
SECRET_KEYS = {pygame.K_a, pygame.K_s}


def launch_screamer(image_path):
    pygame.init()
    try:
        mixer.init()
    except:
        pass

    x = random.randint(0, 1400)
    y = random.randint(0, 700)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"

    screen_size = (random.randint(300, 600), random.randint(300, 600))
    screen = pygame.display.set_mode(screen_size, pygame.NOFRAME)
    pygame.display.set_caption(" ")

    try:
        img = pygame.image.load(image_path)
        img = pygame.transform.scale(img, screen_size)
    except:
        screen.fill((255, 0, 0))
        img = None

    pygame.mouse.set_visible(False)
    running = True
    pressed_keys = set()

    while running:
        if img:
            screen.blit(img, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)

            if SECRET_KEYS.issubset(pressed_keys):
                running = False

        pygame.time.delay(10)

    pygame.quit()


def play_random_sounds():
    mixer.init()
    while True:
        time.sleep(random.uniform(0.5, 3))  # случайная задержка между звуками
        sound_path = random.choice(SOUNDS)
        if os.path.exists(sound_path):
            sound = mixer.Sound(sound_path)
            sound.set_volume(random.uniform(0.6, 1.0))
            sound.play()
        else:
            print(f"[!] Звук {sound_path} не найден.")


def horror_chaos():
    sound_thread = threading.Thread(target=play_random_sounds, daemon=True)
    sound_thread.start()

    processes = []
    for _ in range(NUM_WINDOWS):
        img = random.choice(IMAGES)
        if os.path.exists(img):
            p = multiprocessing.Process(target=launch_screamer, args=(img,))
            p.start()
            processes.append(p)
            time.sleep(0.1)
        else:
            print(f"[!] Картинка {img} не найдена.")

    for p in processes:
        p.join()


if __name__ == "__main__":
    horror_chaos()
