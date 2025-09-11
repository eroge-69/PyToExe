import tkinter as tk

# Создаём главное окно
root = tk.Tk()
root.title("Баннер")
root.geometry("400x200+500+300") # Размер и позиция окна
root.configure(bg="lightblue")

# Убираем рамку и системные кнопки
root.overrideredirect(True)

# Делаем окно всегда поверх других
root.attributes("-topmost", True)

# Добавляем текст или изображение
label = tk.Label(root, text="ВАЖНЫЙ БАННЕР", font=("Arial", 20), bg="lightblue")
label.pack(expand=True)

# Отключаем закрытие по клавишам (Alt+F4, Esc)
def disable_event():
    pass

root.protocol("WM_DELETE_WINDOW", disable_event)
root.bind("<Escape>", lambda e: None)

# Запускаем окно
root.mainloop()