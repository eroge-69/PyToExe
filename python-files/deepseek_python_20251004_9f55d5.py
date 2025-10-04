import tkinter as tk
from tkinter import PhotoImage
import pygame
import threading
import numpy as np
import time

def play_train_horn():
    """Создает и воспроизводит громкий гудок паровоза"""
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        # Параметры для громкого гудка
        duration = 3.0  # 3 секунды
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Создаем многослойный гудок с разными частотами
        freq1 = 180  # Основная низкая частота
        freq2 = 220  # Вторая гармоника
        freq3 = 280  # Третья гармоника
        
        # Основные тоны
        tone1 = 0.7 * np.sin(2 * np.pi * freq1 * t)
        tone2 = 0.5 * np.sin(2 * np.pi * freq2 * t)
        tone3 = 0.3 * np.sin(2 * np.pi * freq3 * t)
        
        # Добавляем вибрацию и модуляцию
        vibrato = 0.2 * np.sin(2 * np.pi * 6 * t)  # Вибрация 6 Hz
        envelope = np.minimum(t / 0.5, 1.0) * np.minimum((duration - t) / 0.8, 1.0)  # Огибающая
        
        # Комбинируем все компоненты
        audio_signal = (tone1 + tone2 + tone3 + vibrato) * envelope
        
        # Увеличиваем громкость
        audio_signal = audio_signal * 0.8
        
        # Конвертируем в стерео
        stereo_signal = np.column_stack([audio_signal, audio_signal])
        audio_data = np.int16(stereo_signal * 32767)
        
        # Создаем и воспроизводим звук
        sound = pygame.sndarray.make_sound(audio_data)
        sound.set_volume(1.0)  # Максимальная громкость
        sound.play()
        
        # Ждем окончания звука
        time.sleep(duration)
        
    except Exception as e:
        print(f"Ошибка воспроизведения звука: {e}")
        # Резервный вариант через winsound
        try:
            import winsound
            for _ in range(2):
                winsound.Beep(200, 800)
                time.sleep(0.2)
        except:
            print("🚂 ТУ-ТУУУ! ГУДОК! 🚂")

def create_train_image():
    """Создает графическое изображение паровоза"""
    root = tk.Tk()
    root.title("Паровоз!")
    
    # Делаем окно поверх всех окон
    root.attributes('-topmost', True)
    root.overrideredirect(True)  # Убираем рамку окна
    
    # Создаем canvas для рисования паровоза
    canvas = tk.Canvas(root, width=600, height=400, bg='lightblue', highlightthickness=0)
    canvas.pack()
    
    # Рисуем небо
    canvas.create_rectangle(0, 0, 600, 250, fill='skyblue', outline='')
    
    # Рисуем землю
    canvas.create_rectangle(0, 250, 600, 400, fill='green', outline='')
    
    # Основной корпус паровоза
    canvas.create_rectangle(80, 180, 450, 230, fill='darkred', outline='black', width=3)
    
    # Котел
    canvas.create_oval(100, 140, 250, 230, fill='black', outline='gray', width=2)
    
    # Большая труба
    canvas.create_rectangle(160, 80, 190, 140, fill='black')
    canvas.create_rectangle(155, 70, 195, 80, fill='gray')
    
    # Кабина машиниста
    canvas.create_rectangle(350, 130, 440, 230, fill='brown', outline='black', width=2)
    canvas.create_rectangle(370, 150, 420, 190, fill='lightblue')  # Окно
    
    # Колеса с детализацией
    wheel_positions = [(150, 220), (250, 220), (350, 220), (400, 220)]
    for x, y in wheel_positions:
        canvas.create_oval(x-30, y-30, x+30, y+30, fill='black', outline='silver', width=3)
        canvas.create_oval(x-20, y-20, x+20, y+20, fill='', outline='gray', width=2)
        canvas.create_line(x-30, y, x+30, y, fill='darkgray', width=2)
        canvas.create_line(x, y-30, x, y+30, fill='darkgray', width=2)
    
    # Дым из трубы
    smoke_colors = ['#666666', '#888888', '#AAAAAA', '#CCCCCC']
    smoke_sizes = [40, 50, 60, 45]
    smoke_y_positions = [40, 20, 10, 30]
    
    for i in range(4):
        canvas.create_oval(150 + i*10, smoke_y_positions[i], 
                          150 + i*10 + smoke_sizes[i], smoke_y_positions[i] + smoke_sizes[i],
                          fill=smoke_colors[i], outline='')
    
    # Пар из-под колес
    for x in [120, 220, 320, 370]:
        canvas.create_oval(x-15, 260, x+15, 280, fill='white', outline='')
        canvas.create_oval(x-10, 270, x+10, 290, fill='white', outline='')
    
    # Надпись
    canvas.create_text(300, 50, text="🚂 ПАРОВОЗ! ТУ-ТУУУ! 🚂", 
                      font=('Arial', 18, 'bold'), 
                      fill='darkblue')
    
    # Информация
    canvas.create_text(300, 350, text="Закроется через 5 секунд", 
                      font=('Arial', 10), 
                      fill='darkgreen')
    
    # Центрируем окно на экране
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    root.geometry(f"+{x}+{y}")
    
    # Запускаем звук в отдельном потоке
    sound_thread = threading.Thread(target=play_train_horn)
    sound_thread.daemon = True
    sound_thread.start()
    
    # Закрываем окно через 5 секунд
    root.after(5000, root.destroy)
    
    root.mainloop()

if __name__ == "__main__":
    # Инициализируем pygame
    try:
        pygame.init()
    except:
        pass
    
    # Запускаем паровоз
    create_train_image()