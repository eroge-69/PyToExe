import tkinter as tk
from tkinter import messagebox
import os

# Настройки пароля
CORRECT_PASSWORD = "12345"
attempts_left = 3

def check_password():
    global attempts_left
    entered_password = password_entry.get()
    
    if not entered_password:
        messagebox.showerror("Ошибка", "Введите пароль!")
        return
    
    if entered_password == CORRECT_PASSWORD:
        root.destroy()  # Закрываем блокировку
    else:
        attempts_left -= 1
        if attempts_left > 0:
            messagebox.showerror("Ошибка", f"Неверный пароль! Осталось попыток: {attempts_left}")
            password_entry.delete(0, tk.END)
        else:
            # Действия при исчерпании попыток
            messagebox.showerror("Блокировка", "Попытки исчерпаны!")
            os.system("shutdown /s /t 10")  # Выключение через 10 секунд
            root.destroy()

# Создаем полноэкранное окно блокировки
root = tk.Tk()
root.attributes("-fullscreen", True)  # Полный экран
root.attributes("-topmost", True)    # Поверх всех окон
root.configure(bg='black')           # Черный фон

# Поле для ввода пароля
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.5, anchor='center')

tk.Label(frame, text="КОМПЬЮТЕР ЗАБЛОКИРОВАН", 
        font=('Arial', 24), fg='white', bg='black').pack(pady=20)

tk.Label(frame, text="Введите пароль для разблокировки:", 
        font=('Arial', 14), fg='white', bg='black').pack()

password_entry = tk.Entry(frame, show="*", font=('Arial', 14), width=20)
password_entry.pack(pady=10)

submit_btn = tk.Button(frame, text="Разблокировать", 
                     command=check_password, font=('Arial', 12))
submit_btn.pack(pady=10)
# Блокируем сочетания клавиш
root.bind("<Alt-F4>", lambda e: "break")
root.bind("<Control-Alt-Delete>", lambda e: "break")
root.bind("<Escape>", lambda e: "break")
# Блокировка ЛЕВОЙ и ПРАВОЙ клавиши Win
root.bind("<Super_L>", lambda e: "break")  # Левая Win (⊞)
root.bind("<Super_R>", lambda e: "break")  # Правая Win (⊞)


# Блокировка популярных комбинаций Win + ...

# Запускаем
password_entry.focus()
root.mainloop()