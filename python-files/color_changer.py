import tkinter as tk
import random

def change_color():
    """Изменяет цвет области на случайный."""
    colors = ["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]
    new_color = random.choice(colors)
    color_area.config(bg=new_color) # Изменяем цвет фона области

# Создаем главное окно
root = tk.Tk()
root.title("Изменение цвета")
root.geometry("400x300") # Устанавливаем размер окна

# Создаем область, которая будет менять цвет
color_area = tk.Label(root, text="Нажми на кнопку!", bg="lightgray", font=("Arial", 16))
color_area.pack(pady=20, padx=20, fill=tk.BOTH, expand=True) # Размещаем область

# Создаем кнопку
color_button = tk.Button(root, text="Изменить цвет", command=change_color)
color_button.pack(pady=10) # Размещаем кнопку

# Запускаем основной цикл приложения
root.mainloop()