import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes

# Проверка админ-прав (обход UAC)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Пароль для разблокировки
CORRECT_PASSWORD = "1337"  # Замените на свой пароль

def check_password():
    entered_password = password_entry.get()
    if entered_password == CORRECT_PASSWORD:
        messagebox.showinfo("Успех", "Доступ разрешен!")
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        password_entry.delete(0, tk.END)

def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    messagebox.showwarning("Заблокировано", "Ваш компьютер заблокирован")

# Создаём окно
root = tk.Tk()
root.title("Система безопасности")
root.attributes("-fullscreen", True)
root.configure(bg="#121212")

# Стиль для виджетов
style = {
    "bg": "#1e1e1e",
    "fg": "#ffffff",
    "font": ("Arial", 14),
    "bd": 0,
    "highlightthickness": 0,
    "relief": tk.FLAT
}

# Фрейм для центрирования
center_frame = tk.Frame(root, bg="#121212")
center_frame.place(relx=0.5, rely=0.5, anchor="center")

# Заголовок
title_label = tk.Label(
    center_frame,
    text="СИСТЕМА БЕЗОПАСНОСТИ",
    bg="#121212",
    fg="#ff5555",
    font=("Arial", 24, "bold")
)
title_label.pack(pady=(0, 30))

# Поле ввода пароля
password_frame = tk.Frame(center_frame, bg="#1e1e1e")
password_frame.pack(pady=10)

password_entry = tk.Entry(
    password_frame,
    **style,
    width=25,
    show="*",
    insertbackground="white"
)
password_entry.pack(side=tk.LEFT, padx=(0, 5))

# Кнопка разблокировки
unlock_btn = tk.Button(
    password_frame,
    text="🔓",
    command=check_password,
    bg="#ff5555",
    fg="white",
    font=("Arial", 12),
    activebackground="#ff3333",
    bd=0
)
unlock_btn.pack(side=tk.LEFT)

# Кнопка блокировки
lock_btn = tk.Button(
    center_frame,
    text="ЗАБЛОКИРОВАТЬ СИСТЕМУ",
    command=lock,
    bg="#333333",
    fg="#ff5555",
    font=("Arial", 12, "bold"),
    activebackground="#444444",
    bd=0,
    padx=20,
    pady=10
)
lock_btn.pack(pady=(30, 0))

# Запускаем окно
root.mainloop()
# Закругленные углы (требуется Pillow)
from PIL import Image, ImageDraw, ImageTk

def create_rounded_rectangle(width, height, radius, color):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width, height), radius, fill=color)
    return ImageTk.PhotoImage(image)
# 1. В начале кода (после импортов) добавьте:
import pygame
from pygame import mixer

# 2. Инициализация аудио (добавьте перед созданием окна Tkinter)
pygame.init()
mixer.init()

# 3. Загрузка и воспроизведение музыки (добавьте после root = tk.Tk())
try:
    mixer.music.load("sound.mp3")  # Укажите путь к вашему MP3-файлу
    mixer.music.play(loops=-1)     # loops=-1 - бесконечный повтор
except:
    print("Не удалось загрузить музыку")