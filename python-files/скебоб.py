import pygame
import sys
import os

# Путь к ресурсам (для совместимости)
BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "скебоб.png")
MUSIC_PATH = os.path.join(BASE_DIR, "громко.mp3")

# Инициализация
pygame.init()
pygame.mixer.init()

# Настройки окна
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Полноэкранный режим
pygame.display.set_caption("Полноэкранное приложение")

# Загрузка изображения
background = pygame.image.load(IMAGE_PATH)
background = pygame.transform.scale(background, screen.get_size())

# Воспроизведение музыки
pygame.mixer.music.load(MUSIC_PATH)
pygame.mixer.music.play(-1)  # -1 = бесконечный цикл

# Главный цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.blit(background, (0, 0))
    pygame.display.flip()

# Завершение
pygame.mixer.music.stop()
pygame.quit()
sys.exit()


