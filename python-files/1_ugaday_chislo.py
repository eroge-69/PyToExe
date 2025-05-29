
import random
import tkinter as tk

number = random.randint(1, 100)

def check_guess():
    guess = int(entry.get())
    if guess < number:
        root.config(bg="lightblue")
        result.config(text="Слишком маленькое число!")
    elif guess > number:
        root.config(bg="lightcoral")
        result.config(text="Слишком большое число!")
    else:
        root.config(bg="lightgreen")
        result.config(text="Правильно!")

root = tk.Tk()
root.title("Угадай число")
root.geometry("300x150")

tk.Label(root, text="Угадай число от 1 до 100").pack()
entry = tk.Entry(root)
entry.pack()

tk.Button(root, text="Проверить", command=check_guess).pack()
result = tk.Label(root, text="")
result.pack()

root.mainloop()
