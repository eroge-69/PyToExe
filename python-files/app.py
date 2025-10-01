import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import ctypes
from PIL import Image, ImageTk
import pygame  # Импортируем pygame вместо playsound

# Инициализируем pygame
pygame.mixer.init()

# Скрываем консоль для Windows
if sys.platform.startswith("win"):
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def check_input():
    user_input = entry.get().lower()
    
    if user_input == "1234567890abc":
        messagebox.showinfo("МОЩЬ", "Смотри фотки!")
        try:
            os.startfile(r"C:\Construct 2\effects\ешь говно\1e3d559e3b4ae8d56df3e1c49c8af405.jpg")
            os.startfile(r"C:\Construct 2\effects\ешь говно\eh24cdn1g6fuxfln5z1z-ohay-tv-13924.jpeg")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файлы не найдены!")
    else:
        for _ in range(5):
            messagebox.showerror("Ошибка", "Неверный пароль!")

def play_startup_sound():
    try:
        # Воспроизведение звука через pygame
        pygame.mixer.music.load('tutututu-meme-demotivator.mp3')  # Укажите путь к вашему звуковому файлу
        pygame.mixer.music.play()
    except FileNotFoundError:
        print("Звуковой файл не найден!")
    except Exception as e:
        print(f"Ошибка при воспроизведении звука: {e}")

# Создаем главное окно
root = tk.Tk()
root.title("Проверка пароля")
root.geometry("400x300")  # Устанавливаем размер окна
root.resizable(False, False)  # Запрещаем изменение размера

# Воспроизводим звук при запуске
play_startup_sound()  # Вызываем функцию воспроизведения звука

try:
    # Добавляем фоновое изображение
    bg_image = Image.open("nemeckaa-ovcarka-3d-illustracia.jpg")  # Убедитесь, что файл существует
    bg_image = bg_image.resize((400, 300), Image.Resampling.LANCZOS)  # Исправлено
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except FileNotFoundError:
    messagebox.showerror("Ошибка", "Фоновое изображение не найдено!")
    root.destroy()
    sys.exit(1)

# Стилизуем поле ввода
style = ttk.Style()
style.configure('My.TEntry',
                font=('Arial', 14),
                foreground='white',
                background='black',
                borderwidth=2,
                relief='ridge')

entry = ttk.Entry(root, style='My.TEntry', width=30)
entry.place(x=50, y=100)

# Стилизуем кнопку
button = ttk.Button(root, 
                   text="Ввести пароль", 
                   command=check_input,
                   style='TButton',
                   width=20)
button.place(x=125, y=150)

# Добавляем иконки и стили
try:
    root.iconbitmap('icon.ico')  # Добавьте свою иконку
except tk.TclError:
    print("Иконка не найдена, продолжаем без неё")

# Настраиваем шрифты и цвета
root.configure(bg='#282c34')  # Тёмный фон

# Запускаем главный цикл
root.mainloop()


