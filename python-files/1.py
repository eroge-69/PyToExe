Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
import time
import threading

# Для Windows
import winsound

# Если вы не на Windows, раскомментируйте одну из следующих строк
# и закомментируйте 'import winsound'.
# Убедитесь, что вы установили выбранную библиотеку:
# pip install pygame
# import pygame

# pip install simpleaudio
# import simpleaudio


def play_sound_for_duration(duration_sec=3):
    """
    Воспроизводит звуковой сигнал в течение указанного количества секунд.
    """
    try:
        # Для Windows: генерирует системный звуковой сигнал
        winsound.Beep(440, duration_sec * 1000) # Частота 440 Гц, длительность в мс

        # Пример для pygame (если вы используете эту библиотеку):
        # pygame.mixer.init()
        # # Создаем простой синусоидальный звук (440 Гц)
        # frequency = 440
        # sample_rate = 44100
        # duration_ms = duration_sec * 1000
        # num_samples = int(sample_rate * duration_sec)
        #
        # # Генерируем массив байтов для звука
        # import numpy as np
        # arr = np.array([4095 * np.sin(2 * np.pi * frequency * x / sample_rate) for x in range(num_samples)]).astype(np.int16)
        # sound = pygame.sndarray.make_sound(arr)
        # sound.play()
        # time.sleep(duration_sec) # Ждем пока звук воспроизведется

        # Пример для simpleaudio (если вы используете эту библиотеку):
        # import numpy as np
        # frequency = 440
        # sample_rate = 44100
        # t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
        # # Генерируем синусоидальную волну
        # note = np.sin(frequency * t * 2 * np.pi)
        # # Преобразуем в 16-битный формат
        # audio = note * (2**15 - 1) / np.max(np.abs(note))
        # audio = audio.astype(np.int16)
        # play_obj = simpleaudio.play_buffer(audio, 1, 2, sample_rate)
        # play_obj.wait_done() # Ждем пока звук воспроизведется


    except Exception as e:
        print(f"Ошибка при воспроизведении звука: {e}")
        print("Возможно, библиотека winsound доступна только на Windows.")
...         print("Для других ОС рассмотрите использование pygame или simpleaudio.")
... 
... def on_button_click():
...     """
...     Функция, которая вызывается при нажатии кнопки.
...     Запускает воспроизведение звука в отдельном потоке.
...     """
...     print("Кнопка нажата! Воспроизводится звуковой сигнал...")
...     # Запускаем воспроизведение звука в отдельном потоке,
...     # чтобы не блокировать основной поток GUI
...     sound_thread = threading.Thread(target=play_sound_for_duration, args=(3,))
...     sound_thread.start()
... 
... # Создаем главное окно
... root = tk.Tk()
... root.title("Звуковой сигнал")
... 
... # Устанавливаем размер окна (ширина x высота)
... window_width = 400
... window_height = 200
... root.geometry(f"{window_width}x{window_height}")
... 
... # Вычисляем положение окна по центру экрана
... screen_width = root.winfo_screenwidth()
... screen_height = root.winfo_screenheight()
... x_cordinate = int((screen_width / 2) - (window_width / 2))
... y_cordinate = int((screen_height / 2) - (window_height / 2))
... root.geometry(f"+{x_cordinate}+{y_cordinate}")
... 
... # Создаем фрейм для центрирования кнопки
... frame = tk.Frame(root)
... frame.pack(expand=True)
... 
... # Создаем кнопку
... button = tk.Button(frame, text="Воспроизвести звук", command=on_button_click,
...                    font=("Arial", 14), width=20, height=2)
... button.pack()
... 
... # Запускаем главный цикл Tkinter
