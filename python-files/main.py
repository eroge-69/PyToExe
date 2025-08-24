import tkinter as tk

# Создаем главное окно
root = tk.Tk()
root.title("Time Farm")  # Название окна
root.geometry("300x100")  # Размер окна

# Добавляем текст
label = tk.Label(root, text="Запущено!", font=("Arial", 14))
label.pack(expand=True)

# Запускаем цикл обработки событий
root.mainloop()