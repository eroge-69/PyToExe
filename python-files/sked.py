import os
import tkinter as tk
from tkinter import messagebox
import time
import pygame

# Инициализация pygame для звука
pygame.mixer.init()

def play_sound(filename):
    try:
        sound = pygame.mixer.Sound(filename)
        sound.play()
    except pygame.error as e:
        print(f"Ошибка при воспроизведении звука {filename}: {e}")
    return sound

def stop_sound(sound):
    if sound:
        sound.stop()

def show_messagebox(title, message):
    messagebox.showinfo(title, message)

def ko1fort_script():
    # Открытие папки sked (не требуется отдельная команда, если скрипт запускается из той же директории)

    # Открытие файла с exe (предполагается, что ko1fort.exe находится в папке sked)
    try:
        os.system("start sked\\ko1fort.exe")
    except Exception as e:
        print(f"Ошибка при запуске ko1fort.exe: {e}")

    show_messagebox("Привет", "Привэт")

    # Диалог "Хочешь помурчу в дискорде?" (да/нет)
    response = messagebox.askyesno("Дискорд", "Хочешь помурчу в дискорде?")
    if response:
        show_messagebox("Ответ", "Хорошо!")
    else:
        show_messagebox("Ответ", "Ну ладно.")

    show_messagebox("Передумал", "А нэ я передумал")

    show_messagebox("Сценарий", "чё там надо сказать? я сценарий забыл,сорян")

    show_messagebox("Подарок", "Сорян немного опоздал с подарком,но я имею право")

    show_messagebox("Шкед", "я шкед потому что")

    show_messagebox("Нахуй", "иди нахуй")

    # Диалог "Хочешь покажу фокус?" (да/нет)
    response = messagebox.askyesno("Фокус", "Хочешь покажу фокус?")
    if response:
        show_messagebox("Фокус", "Хорошо, сейчас покажу!")
    else:
        show_messagebox("Фокус", "Ну и зря.")

    show_messagebox("Мнение", "Ой ебал я мнение шкилы спрашивать,ща покажу")

    # Включается музыка am.mp3
    music_am = play_sound("sked\\am.mp3")
    time.sleep(2) # Даем время музыке немного поиграть

    show_messagebox("Сворачивание", "Всё сворачивается на рабочий стол")

    # Сворачивание окна (предполагается, что скрипт сам имеет окно, которое нужно свернуть)
    # В данном случае, без GUI-фреймворка, это сложно реализовать напрямую,
    # но можно имитировать. Здесь пропустим явное сворачивание окна скрипта.

    # Рабочий стол меняется на фото dm.png
    # Это также требует манипуляций с ОС, что сложно сделать напрямую из Python без сторонних библиотек
    # или прав администратора. Для имитации можно вывести сообщение.
    show_messagebox("Рабочий стол", "Рабочий стол меняется на фото dm.png (имитация)")

    # Дальше процессор explorer.exe и открывается
    show_messagebox("Explorer", "Дальше процессор explorer.exe и открывается")

    show_messagebox("Прогресс", "1")
    show_messagebox("Прогресс", "2%")
    show_messagebox("Прогресс", "10%")
    show_messagebox("Прогресс", "30%")

    # О до,это шкэд идёт спасать тебя (ii.mp3)
    show_messagebox("Спасение", "О до,это шкэд идёт спасать тебя")
    music_ii = play_sound("sked\\ii.mp3")
    time.sleep(2)
    stop_sound(music_ii)

    show_messagebox("Сканирование", "ща посмотрю чё за порнуха у тебя на пк есть и помогу начало")

    show_messagebox("Прогресс", "шкэд спасает тебя 0%")

    show_messagebox("Завтра", "давай завтра уже помогу?")

    show_messagebox("Не ной", "да ладно не ной ща")

    show_messagebox("Восстановление", "восстанавливаю процесс explorer exe")

    # О я нашёл (ko1.mp3)
    show_messagebox("Находка", "О я нашёл")
    music_ko1 = play_sound("sked\\ko1.mp3")
    time.sleep(2)
    stop_sound(music_ko1)

    show_messagebox("Итог", "лучше бы я не смотрел... конец")

    show_messagebox("Деньги", "Мне деньги нужны поэтому скинь мне 200 зимбабайских долларов иначе")
    show_messagebox("Угроза", "спалю твой имя")

    # Мышка начнёт телепортироваться в разные стороны 10 раз
    # Это требует низкоуровневых манипуляций с мышью, что сложно сделать напрямую.
    # Для имитации можно вывести сообщение.
    for i in range(10):
        show_messagebox("Движение мыши", f"Мышка телепортируется ({i+1}/10)")
        time.sleep(0.5)

    # Появляется опрос
    show_messagebox("Опрос", "Включить камеру?")

    # Включается камера (имитация)
    response = messagebox.askyesno("Камера", "Включить камеру?")
    if response:
        show_messagebox("День наоборот", "Ответи да - сегодня день наоборот")
        # Здесь можно было бы включить камеру, что требует сторонних библиотек (например, OpenCV)
        # и прав доступа.
        print("(Имитация включения камеры)")
    else:
        show_messagebox("День наоборот", "Ответит нет - сегодня день наоборот")
        # Здесь можно было бы включить камеру, что требует сторонних библиотек (например, OpenCV)
        # и прав доступа.
        print("(Имитация включения камеры)")

    # Вдруг включается музыка (win.mp3)
    music_win = play_sound("sked\\win.mp3")

    # Через 10с выключается компьютер
    try:
        time.sleep(10)
        show_messagebox("Выключение", "Выключение компьютера через 3 секунды...")
        time.sleep(3)
        # Команда для выключения компьютера (может потребовать прав администратора)
        # For Windows: os.system("shutdown /s /t 1")
        # For Linux: os.system("sudo shutdown -h now")
        # Для macOS: os.system("sudo shutdown -h now")
        print("Имитация команды выключения компьютера.")
    except Exception as e:
        print(f"Ошибка при выключении компьютера: {e}")
    finally:
        stop_sound(music_win) # Останавливаем музыку перед завершением

if __name__ == "__main__":
    # Создаем главное окно Tkinter, чтобы messagebox работали корректно
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    ko1fort_script()

    # Важно: Не закрывайте Pygame mixer, пока скрипт работает,
    # но если скрипт завершается, то можно его очистить.
    # pygame.mixer.quit()