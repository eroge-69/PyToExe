import time
from random import randint
import pygame

# Инициализация pygame
pygame.mixer.init()

pygame.mixer.music.load("happy_birthday.mp3")

# Воспроизведение музыки
pygame.mixer.music.play()

for i in range(1, 85):
    print('')

space = ''
for i in range(1, 1000):
    count = randint(1, 100)
    while count > 0:
        space += ' '
        count -= 1
    if i % 10 == 0:
        print(space + '🎂С днём рожения тебя!')
    elif i % 9 == 0:
        print(space + "🎂")
    elif i % 5 == 0:
        print(space + "💛")
    elif i % 8 == 0:
        print(space + "🎉")
    elif i % 7 == 0:
        print(space + "🍫")
    elif i % 6 == 0:
        print(space + "С днём роженияяя тебяяя💖")
    else:
        print(space + "🔸")
    space = ''
    time.sleep(0.2)

# Остановка музыки после завершения программы
pygame.mixer.music.stop()
