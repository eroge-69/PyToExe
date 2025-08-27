import keyboard
import time
a = input('Привет тебя приветствует спам-бот\nВведите сюда то что вы хоите написать: ')
s = float(input('Введи сюда задержку: '))
print('Чтобы начать спам нажмите "TAB", чтобы завершить "TAB"')
keyboard.wait('tab')
while 1:
    if keyboard.is_pressed('tab'):
        break
    keyboard.write(a)
    if keyboard.is_pressed('tab'):
        break
    keyboard.press_and_release('enter')
    if keyboard.is_pressed('tab'):
        break
    time.sleep(s)