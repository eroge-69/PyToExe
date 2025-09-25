import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Для музыки

# Загрузка музыки
try:
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play(-1)  # В цикле
except pygame.error as e:
    print(f"Ошибка загрузки музыки: {e}. Проверьте файл 'your_reality.mp3'.")

# Размеры экрана
width, height = 1100, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Любимой Милане!<333333")

# Часы для FPS
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)  # Для фона, если ошибка

# Список персонажей, фонов и сообщений (индекс 0 - Моника)
characters_files = ['m.png', 's.png', 'y.png', 'n.png']
backgrounds_files = ['class.png', 'room.png', 'rrr.png', 'kitchen.png']  # Подстройте расширения
messages = [
    "Поздравляю! Пусть каждый день будет как поэма.",
    "Ура! Поздравляю тебя от всего сердца!",
    "Прими мои искренние поздравления с этим событием.",
    "Эй, поздравляю! Не вздумай грустить, ладно?"
]

# Загрузка изображений
try:
    characters = [pygame.transform.scale(pygame.image.load(file), (500, 500)) for file in characters_files]  # Масштаб: ширина 200, высота 300
    backgrounds = [pygame.transform.scale(pygame.image.load(file), (width, height)) for file in backgrounds_files]
except pygame.error as e:
    print(f"Ошибка загрузки изображений: {e}. Проверьте файлы.")
    sys.exit()

# Позиции персонажей (центр)
char_rects = [img.get_rect(center=(width // 2, height // 2 + 50)) for img in characters]

# Предварительный рендер сообщений (шрифт 50)
font = pygame.font.Font(None, 50)
texts = [font.render(msg, True, WHITE) for msg in messages]
text_rects = [text.get_rect(center=(width // 2, height // 2 - 200)) for text in texts]

# Надпись снизу (маленький шрифт 20)
small_font = pygame.font.Font(None, 35)
bottom_text = small_font.render("Нажми пробел для продолжения..", True, WHITE)
bottom_rect = bottom_text.get_rect(center=(width // 2, height - 20))

# Текущий индекс (стартуем с Моники)
current_index = 0

# Основной цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_index = (current_index + 1) % 4  # Цикл по 4 персонажам

    # Отрисовка фона
    screen.blit(backgrounds[current_index], (0, 0))

    # Отрисовка персонажа
    screen.blit(characters[current_index], char_rects[current_index])

    # Отрисовка сообщения для текущего персонажа
    screen.blit(texts[current_index], text_rects[current_index])

    # Отрисовка надписи снизу
    screen.blit(bottom_text, bottom_rect)

    # Обновление экрана
    pygame.display.flip()

    # FPS
    clock.tick(60)

# Выход
pygame.quit()
sys.exit()