import tkinter as tk
import random  
# Глобальные переменные для координат кнопки "Да"
yes_button_x = 150
yes_button_y = 150
n=0
def on_yes():
    global yes_button_x, yes_button_y,n
    
    # Измените координаты кнопки "Да"
    #yes_button_x = random.randint(20,380)  # Увеличьте координату x на 20
    #yes_button_y = random.randint(20,280)  # Увеличьте координату y на 20
    #yes_button.place(x=yes_button_x, y=yes_button_y)
    #n =n+1
    #print(n)
    #if n == 0:
    yes_button.config(text="ДА")

def on_no():
    yes_button.config(text="ДА")
    new_window = tk.Toplevel(root)
    new_window.title("Сообщение")
    label = tk.Label(new_window, text="Я так и знал")
    label.pack()

root = tk.Tk()
root.title("Вопрос")
root.geometry("400x300")

question = tk.Label(root, text="Ты гей?")
question.pack(pady=20)

yes_button = tk.Button(root, text="Нет", command=on_no)
yes_button.place(x=yes_button_x, y=yes_button_y)  # Исходное положение кнопки "Да"

no_button = tk.Button(root, text="ДА", command=on_no)
no_button.place(x=250, y=150)  # Исходное положение кнопки "Нет"

root.mainloop()
