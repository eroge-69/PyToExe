import tkinter as tk

# Функция, которая вызывается при нажатии на кнопку
def on_button_click():
    label.config(text="Кнопка нажата!")

# Создаем главное окно
root = tk.Tk()
root.title("Пример приложения на tkinter")

# Создаем метку
label = tk.Label(root, text="Нажми на кнопку!")
label.pack(pady=20)

# Создаем кнопку
button = tk.Button(root, text="Нажми меня", command=on_button_click)
button.pack(pady=10)

# Запускаем главный цикл приложения
root.mainloop()
