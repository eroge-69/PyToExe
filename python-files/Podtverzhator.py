import tkinter as tk
from tkinter import messagebox
import time


def check_code():
    entered_code = entry.get().strip().lower()
    correct_code = "мамалучшая"  # Секретный код

    if entered_code == correct_code:
        # Создаем эффект "загрузки"
        label.config(text="Проверка сертификата...")
        entry.delete(0, tk.END)
        root.update()
        time.sleep(1.5)

        # Специальное сообщение для мамы
        messagebox.showinfo("Результат проверки",
                            "Ошибка. Вы уже являетесь лучшей мамой!\n\n"
                            "Система не может выдать сертификат,\n"
                            "так как это звание присвоено пожизненно ♥")

        # Меняем интерфейс после успешного ввода
        label.config(text="Статус: Вы - лучшая мама!", fg="#E75480")
        entry.pack_forget()
        button.pack_forget()

        # Добавляем сердечки
        hearts_label = tk.Label(root, text="♥" * 30, fg="#FF69B4", font=("Arial", 14))
        hearts_label.pack(pady=10)
    else:
        messagebox.showerror("Ошибка", "Неверный код сертификата!\n\nПопробуйте еще раз ♥")


# Создаем главное окно
root = tk.Tk()
root.title("Сертификат Лучшей Мамы")
root.geometry("500x300")
root.configure(bg="#FFF0F5")  # Нежно-розовый фон

# Настраиваем шрифты
title_font = ("Arial", 16, "bold")
label_font = ("Arial", 12)

# Элементы интерфейса
tk.Label(root,
         text="Система активации сертификата",
         font=title_font,
         bg="#FFF0F5",
         fg="#8B0000").pack(pady=(20, 10))

tk.Label(root,
         text="Введите код с сертификата:",
         font=label_font,
         bg="#FFF0F5").pack()

entry = tk.Entry(root, width=30, font=label_font, justify="center", show="♥")
entry.pack(pady=10)
entry.focus()  # Фокус на поле ввода

button = tk.Button(root,
                   text="Проверить сертификат",
                   command=check_code,
                   bg="#FFB6C1",
                   fg="white",
                   font=label_font,
                   padx=10,
                   pady=5)
button.pack(pady=5)

label = tk.Label(root,
                 text="Статус: Ожидание ввода кода...",
                 font=label_font,
                 bg="#FFF0F5")
label.pack(pady=20)

# Инструкция внизу
tk.Label(root,
         text="Подсказка: код состоит из двух слов, которые всегда в вашем сердце ♥",
         font=("Arial", 9),
         bg="#FFF0F5",
         fg="#696969").pack(side=tk.BOTTOM, pady=10)

root.mainloop()