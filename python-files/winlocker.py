# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

# Правильный пароль
CORRECT_PASSWORD = "12345"

# Функция для проверки пароля
def check_password():
    entered_password = entry.get()
    if entered_password == CORRECT_PASSWORD:
        root.destroy()  # Закрыть окно при правильном пароле
    else:
        messagebox.showerror("Ошибка", "Пароль введен неправильно!")
        entry.delete(0, tk.END)  # Очистить поле ввода

# Функция для блокировки системных клавиш
def block_system_keys(event):
    # Блокируем Alt+F4, Win, Ctrl+Shift+Esc
    if event.keysym == "F4" and event.state & 0x20000:  # Alt+F4
        return "break"
    if event.keysym in ["Super_L", "Super_R"]:  # Клавиши Win
        return "break"
    if event.keysym == "Escape" and event.state & 0x0004 and event.state & 0x0001:  # Ctrl+Shift+Esc
        return "break"
    return None

# Создаем основное окно
root = tk.Tk()
root.attributes("-fullscreen", True)  # Полноэкранный режим
root.attributes("-topmost", True)     # Окно всегда сверху
root.configure(bg="black")            # Черный фон

# Заголовок
label = tk.Label(root, text="Экран заблокирован! Введите пароль:", fg="white", bg="black", font=("Arial", 20))
label.pack(pady=50)

# Поле ввода пароля
entry = tk.Entry(root, show="*", font=("Arial", 16), width=20)
entry.pack(pady=20)
entry.focus_set()  # Фокус на поле ввода

# Кнопка для проверки пароля
button = tk.Button(root, text="Разблокировать", command=check_password, font=("Arial", 14))
button.pack(pady=20)

# Привязка клавиши Enter к проверке пароля
root.bind("<Return>", lambda event: check_password())

# Блокировка системных клавиш
root.bind("<Key>", block_system_keys)

# Отключаем возможность закрытия окна через Alt+F4
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Запуск основного цикла
root.mainloop()