import tkinter as tk
from tkinter import messagebox
import random

def show_broken_screen():
    """Создаем простое изображение разбитого экрана без PIL"""
    try:
        # Создаем новое окно
        window = tk.Toplevel(root)
        window.title("Разбитый экран")
        window.geometry("800x600")
        window.configure(bg='black')
        window.attributes('-fullscreen', True)  # Полноэкранный режим
        
        # Создаем canvas для рисования трещин
        canvas = tk.Canvas(window, bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        
        # Рисуем трещины
        for _ in range(15):
            x1 = random.randint(0, 800)
            y1 = random.randint(0, 600)
            x2 = random.randint(0, 800)
            y2 = random.randint(0, 600)
            canvas.create_line(x1, y1, x2, y2, fill='white', width=3)
        
        # Добавляем текст
        canvas.create_text(
            400, 300,
            text="ЭКРАН РАЗБИТ!",
            font=("Arial", 48, "bold"),
            fill="red",
            justify='center'
        )
        
        # Кнопка выхода
        exit_btn = tk.Button(
            window,
            text="Выйти",
            command=window.destroy,
            bg='red',
            fg='white',
            font=("Arial", 14)
        )
        exit_btn.place(x=700, y=550)
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать эффект: {e}")

# Основное окно
root = tk.Tk()
root.title("Симулятор разбитого экрана")
root.geometry("300x150")

tk.Button(
    root,
    text="Разбить экран!",
    command=show_broken_screen,
    bg='red',
    fg='white',
    font=("Arial", 16, "bold")
).pack(expand=True, padx=50, pady=50)

root.mainloop()