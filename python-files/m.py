import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import pygame
import threading


class Screamer:
    def __init__(self):
        # Инициализация pygame для звука
        pygame.mixer.init()

        self.root = tk.Tk()
        self.root.title("Игра")
        self.root.geometry("400x300")

        self.setup_ui()

    def setup_ui(self):
        # Создаем безобидный интерфейс
        label = tk.Label(self.root, text="Добро пожаловать!",
                         font=("Arial", 20))
        label.pack(pady=20)

        button = tk.Button(self.root, text="Получить сюрприз!",
                           command=self.activate_screamer,
                           font=("Arial", 16), bg="green", fg="white")
        button.pack(pady=10)

        # Таймер для автоматического запуска
        self.root.after(10000, self.auto_activate)  # Через 10 секунд

    def auto_activate(self):
        # Случайный автоматический запуск
        if random.random() < 0.3:  # 30% вероятность
            self.activate_screamer()

    def play_scary_sound(self):
        """Воспроизведение страшного звука"""
        try:
            # Попробуйте использовать любой WAV файл
            sound_files = [
                "scary_sound.wav",
                "scream.wav",
                "C://Users//ilya_slepets//Desktop//scary_sound.wav"
            ]

            for sound_file in sound_files:
                if os.path.exists(sound_file):
                    pygame.mixer.Sound(sound_file).play()
                    return

            # Если файлы не найдены, создаем простой страшный звук программно
            self.generate_scary_sound()

        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
            # Резервный вариант - системные звуки
            try:
                import winsound
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            except:
                for i in range(3):
                    print("\a")  # Системный бип

    def generate_scary_sound(self):
        """Генерация простого страшного звука"""
        try:
            import numpy as np
            import simpleaudio as sa

            # Генерируем страшный звук (резкий шум)
            frequency = 440  # Hz
            fs = 44100  # sampling rate
            seconds = 2  # duration

            t = np.linspace(0, seconds, int(fs * seconds), False)

            # Создаем сложный звук с разными частотами
            note1 = np.sin(frequency * t * 2 * np.pi)
            note2 = np.sin(frequency * 1.5 * t * 2 * np.pi) * 0.3
            note3 = np.random.normal(0, 0.1, len(t))  # белый шум

            audio = note1 + note2 + note3
            audio *= 32767 / np.max(np.abs(audio))
            audio = audio.astype(np.int16)

            # Воспроизводим
            play_obj = sa.play_buffer(audio, 1, 2, fs)
            play_obj.wait_done()

        except ImportError:
            # Если библиотеки нет, используем winsound
            try:
                import winsound
                for freq in [800, 400, 1000, 300]:
                    winsound.Beep(freq, 200)
            except:
                for i in range(5):
                    print("\a")

    def activate_screamer(self):
        # Создаем окно скримера
        scream_window = tk.Toplevel()
        scream_window.attributes('-fullscreen', True)
        scream_window.attributes('-topmost', True)

        # Загружаем страшное изображение
        try:
            image = Image.open("C://Users//ilya_slepets//Desktop//scary.jpg")
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(scream_window, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            # Если изображения нет, используем текст
            scream_window.configure(bg='black')
            scary_text = tk.Label(scream_window, text="ААААА!!!",
                                  font=("Arial", 100), fg="red", bg="black")
            scary_text.pack(expand=True)

        # Воспроизводим звук в отдельном потоке
        sound_thread = threading.Thread(target=self.play_scary_sound)
        sound_thread.daemon = True
        sound_thread.start()

        # Закрываем через 2 секунды
        scream_window.after(2000, scream_window.destroy)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = Screamer()
    app.run()