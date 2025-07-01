'''

            Online Python Compiler.
    Code, Compile and Run python program online.
Write your code and press "Run" button to execute it.

'''
import subprocess
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Проверка и установка библиотеки pygame
try:
    import pygame
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
    import pygame

# Инициализация pygame для воспроизведения звука
pygame.mixer.init()
tick_sound = pygame.mixer.Sound("C:/Users/User/Desktop/tick.wav")  # Укажите путь к вашему звуковому файлу

def start_timer():
    try:
        global seconds
        seconds = int(entry.get())
        timer_label.config(text=f"Осталось времени: {seconds} секунд")
        
        # Получаем длительность звуковой записи
        sound_duration = tick_sound.get_length()  # Время в секундах
        tick_count = int(seconds // sound_duration)  # Количество раз, сколько звук должен повториться

        # Воспроизводим звук столько раз, сколько он поместится в отведенное время
        for _ in range(tick_count):
            tick_sound.play()  # Воспроизводим звук тиканья
            time.sleep(sound_duration)  # Ждем, пока звук не закончится

        threading.Thread(target=countdown).start()  # Запускаем отсчет в отдельном потоке
    
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите число.")

def countdown():
    global seconds
    while seconds > 0:
        timer_label.config(text=f"Осталось времени: {seconds} секунд")
        root.update()  # Обновляем интерфейс
        tick_sound.play()  # Воспроизводим звук тиканья
        time.sleep(1)  # Ждем 1 секунду
        seconds -= 1
        
    # После завершения отсчета останавливаем звук и показываем сообщение
    tick_sound.stop()  # Останавливаем звук
    timer_label.config(text="Время истекло!")
    messagebox.showinfo("Время истекло!", "Таймер завершён!")  # Сообщаем пользователю

# Создаем основное окно
root = tk.Tk()
root.title("Таймер")

# Создаем метку и поле для ввода времени
label = tk.Label(root, text="Введите время в секундах:")
label.pack()

entry = tk.Entry(root)
entry.pack()

# Создаем метку для отображения обратного отсчета
timer_label = tk.Label(root, text="", font=("Helvetica", 16))
timer_label.pack()

# Создаем кнопку для запуска таймера
start_button = tk.Button(root, text="Запустить таймер", command=start_timer)
start_button.pack()

# Запускаем главный цикл приложения
root.mainloop()
