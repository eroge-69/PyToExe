import pygame
import time
import random
import sys

# Инициализация pygame
pygame.init()

# Настройки окна
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("С Днём Рождения, Линочка! ❤️")

# Цвета
WHITE = (255, 255, 255)
PINK = (255, 182, 193)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Текст поздравления
messages = [
    "Солнышко,",
    "С Днём Рождения!",
    "Ты - самое прекрасное,",
    "что случилось в моей жизни!",
    "Пусть каждый день будет",
    "наполнен счастьем,",
    "любовью и улыбками!",
    "Я тебя люблю! ❤️"
]

# Частицы для эффекта
particles = []
for _ in range(100):
    particles.append([
        [random.randint(0, width), random.randint(0, height)],
        [random.randint(-5, 5), random.randint(-5, 5)],
        random.randint(2, 5),
        random.choice(COLORS)
    ])

# Основной цикл
clock = pygame.time.Clock()
font = pygame.font.SysFont('comicsansms', 30)
birthday_font = pygame.font.SysFont('comicsansms', 50, bold=True)

running = True
while running:
    screen.fill(WHITE)
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Рисование частиц
    for particle in particles:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        
        # Если частица ушла за экран, возвращаем ее
        if particle[0][0] > width or particle[0][0] < 0:
            particle[1][0] *= -1
        if particle[0][1] > height or particle[0][1] < 0:
            particle[1][1] *= -1
            
        pygame.draw.circle(screen, particle[3], [int(particle[0][0]), int(particle[0][1])], particle[2])
    
    # Отображение текста
    title = birthday_font.render("С Днём Рождения, Лина!", True, RED)
    screen.blit(title, (width//2 - title.get_width()//2, 50))
    
    for i, message in enumerate(messages):
        text = font.render(message, True, GOLD if i % 2 == 0 else PINK)
        screen.blit(text, (width//2 - text.get_width()//2, 150 + i * 40))
    
    # Сердечко внизу
    heart = font.render("❤️", True, RED)
    screen.blit(heart, (width//2 - heart.get_width()//2, height - 100))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()