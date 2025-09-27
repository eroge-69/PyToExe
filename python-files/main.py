import tkinter as tk
import random

def move_no_button(event):
    """Телепортируем кнопку 'Нет' в случайное место окна"""
    new_x = random.randint(0, root.winfo_width() - no_button.winfo_width())
    new_y = random.randint(50, root.winfo_height() - no_button.winfo_height())
    no_button.place(x=new_x, y=new_y)

def yes_answer():
    """Меняем текст и убираем кнопки"""
    question_label.config(text="Я так и знал 😏")
    yes_button.place_forget()
    no_button.place_forget()

# --- GUI ---
root = tk.Tk()
root.title("Вопросик")
root.geometry("800x500")  # увеличенное окно
root.resizable(False, False)

question_label = tk.Label(root, text="Сосал?", font=("Arial", 20))
question_label.pack(pady=40)

# кнопки
yes_button = tk.Button(root, text="Да", font=("Arial", 14), bg="green", fg="white", command=yes_answer)
yes_button.place(x=300, y=200)

no_button = tk.Button(root, text="Нет", font=("Arial", 14), bg="red", fg="white")
no_button.place(x=400, y=200)

# обработчик наведения
no_button.bind("<Enter>", move_no_button)

root.mainloop()
