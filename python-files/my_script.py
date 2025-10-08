import tkinter as tk
import random

# Генерация случайного числа
secret_number = random.randint(1, 100)

def check_guess():
    guess = int(entry.get())
    if guess < secret_number:
        result_label.config(text="Слишком мало!")
    elif guess > secret_number:
        result_label.config(text="Слишком много!")
    else:
        result_label.config(text="Ты угадал! 🎉")

# Интерфейс
window = tk.Tk()
window.title("Угадай число")
window.geometry("300x200")

title_label = tk.Label(window, text="Угадай число от 1 до 100", font=("Arial", 14))
title_label.pack(pady=10)

entry = tk.Entry(window)
entry.pack()

check_button = tk.Button(window, text="Проверить", command=check_guess)
check_button.pack(pady=5)

result_label = tk.Label(window, text="", font=("Arial", 12))
result_label.pack(pady=10)

window.mainloop()