import tkinter as tk

# Настройки окна
root = tk.Tk()
root.title("pizdec")
root.geometry("400x200")

# Установка иконки (замените на путь к вашему файлу .ico)
root.iconbitmap("C:/10.ico")

# Перевод окна в полноэкранный режим
root.attributes('-fullscreen', True)

# Текстовая метка
label = tk.Label(root, text="мясо🍖🍖🍖🍖🍖🍖🍖🍖🍖", font=("Arial", 24))
label.pack(expand=True)

# Цвета для мигания
colors = ["red", "white"]
current_color = 0

# Функция мигания
def blink():
    global current_color
    root.configure(bg=colors[current_color])
    label.configure(bg=colors[current_color])
    current_color = (current_color + 1) % 2
    root.after(100, blink)  # мигает каждые 500 мс

# Запуск мигания
blink()

# Запуск окна
root.mainloop()
