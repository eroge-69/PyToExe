import tkinter as tk
import random

# Создаём главное окно
root = tk.Tk()
root.title("EMOJI BUTTON")
root.geometry("1280x720")  # Устанавливаем размер окна

# Список эмодзи
emojis = [":)", ":(", ":]", ":[", ":}", ":{", ":P", ":3", ":I"]

# Функция для изменения текста на кнопке
def change_button_text():
    new_text = random.choice(emojis)
    button.config(text=new_text)

# Функция для выхода из приложения
def exit_app():
    root.quit()

# Создаём кнопку для изменения текста
button = tk.Button(root, text="BUTTON", font=("Arial", 48), command=change_button_text)
button.pack(expand=True)  # Центрируем кнопку по вертикали и горизонтали

# Создаём кнопку для выхода
exit_button = tk.Button(root, text="EXIT", font=("Arial", 20), command=exit_app)
exit_button.pack(side=tk.BOTTOM, pady=20)  # Размещаем кнопку внизу

# Запускаем главный цикл приложения
root.mainloop()
