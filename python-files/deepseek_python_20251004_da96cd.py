import tkinter as tk
from PIL import Image, ImageTk
import pygame
import threading
import time
import os

def play_train_sound():
    """Воспроизведение звука гудка паровоза"""
    try:
        pygame.mixer.init()
        # Создаем простой звук гудка программно
        import numpy as np
        
        # Параметры звука
        duration = 2.0  # секунды
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        # Создаем низкочастотный гудок
        t = np.linspace(0, duration, frames, False)
        frequency1 = 220  # Hz (низкий тон)
        frequency2 = 165  # Hz (еще ниже)
        
        # Создаем основной тон с вибрацией
        tone1 = 0.6 * np.sin(2 * np.pi * frequency1 * t)
        tone2 = 0.4 * np.sin(2 * np.pi * frequency2 * t)
        
        # Добавляем "дребезжание"
        vibrato = 0.1 * np.sin(2 * np.pi * 5 * t)  # вибрация 5 Hz
        
        # Собираем все вместе
        audio_data = tone1 + tone2 + vibrato
        
        # Нормализуем
        audio_data = np.int16(audio_data * 32767)
        
        # Воспроизводим
        sound = pygame.sndarray.make_sound(audio_data)
        sound.play()
        time.sleep(2)  # Ждем окончания звука
        
    except Exception as e:
        # Альтернативный простой звук через системный бипер
        try:
            import winsound
            winsound.Beep(220, 1000)  # Низкий тон 1 секунду
            winsound.Beep(165, 800)   # Еще ниже 0.8 секунд
        except:
            print("🚂 ТУ-ТУУУ!")  # Если звук не работает, выводим в консоль

def create_train_popup():
    # Инициализируем pygame для звука
    try:
        pygame.mixer.init()
    except:
        pass
    
    # Создаем главное окно
    root = tk.Tk()
    root.title("Паровоз!")
    
    # Убираем стандартные рамки окна
    root.overrideredirect(True)
    
    # Делаем окно поверх всех остальных
    root.attributes('-topmost', True)
    
    try:
        # Создаем красивую картинку паровоза
        from tkinter import Canvas
        canvas = Canvas(root, width=500, height=350, bg='lightblue')
        canvas.pack()
        
        # Рисуем детализированный паровоз
        # Основной корпус
        canvas.create_rectangle(50, 180, 400, 230, fill='darkred', outline='black', width=2)
        
        # Котел
        canvas.create_oval(80, 150, 200, 230, fill='black', outline='gray', width=2)
        
        # Труба
        canvas.create_rectangle(120, 100, 140, 150, fill='black')
        canvas.create_rectangle(115, 90, 145, 100, fill='gray')
        
        # Кабина
        canvas.create_rectangle(300, 130, 380, 230, fill='brown', outline='black', width=2)
        canvas.create_rectangle(320, 150, 360, 190, fill='lightblue')  # окно
        
        # Колеса
        canvas.create_oval(120, 220, 180, 280, fill='black', outline='silver', width=3)
        canvas.create_oval(120, 220, 180, 280, fill='', outline='gray', width=2)  # обод
        
        canvas.create_oval(220, 220, 280, 280, fill='black', outline='silver', width=3)
        canvas.create_oval(220, 220, 280, 280, fill='', outline='gray', width=2)  # обод
        
        canvas.create_oval(320, 220, 380, 280, fill='black', outline='silver', width=3)
        canvas.create_oval(320, 220, 380, 280, fill='', outline='gray', width=2)  # обод
        
        # Дым
        canvas.create_oval(100, 70, 130, 100, fill='gray', outline='')
        canvas.create_oval(80, 50, 120, 80, fill='darkgray', outline='')
        canvas.create_oval(60, 30, 100, 60, fill='lightgray', outline='')
        
        # Текст
        canvas.create_text(250, 50, text="🚂 ТУ-ТУУУ! 🚂", 
                          font=('Arial', 20, 'bold'), 
                          fill='darkblue')
        
        # Добавляем немного пара
        canvas.create_oval(60, 200, 90, 220, fill='white', outline='')
        canvas.create_oval(40, 190, 70, 210, fill='white', outline='')
        
    except Exception as e:
        # Простой вариант если не получилось нарисовать
        label = tk.Label(root, text="🚂 ПАРОВОЗ! 🚂\nТУ-ТУУУ!", 
                        font=('Arial', 24, 'bold'), 
                        fg='darkblue', bg='lightyellow',
                        padx=20, pady=20)
        label.pack()
    
    # Центрируем окно на экране
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Запускаем звук в отдельном потоке
    sound_thread = threading.Thread(target=play_train_sound)
    sound_thread.daemon = True
    sound_thread.start()
    
    # Закрываем окно через 5 секунд
    root.after(5000, root.destroy)
    
    root.mainloop()

if __name__ == "__main__":
    create_train_popup()