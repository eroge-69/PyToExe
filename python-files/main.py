import tkinter as tk
from tkinter import messagebox
import random

def on_yes():
    messagebox.showinfo("Хах", "Я так и думал!")
    root.destroy()

def on_no_hover(event):
    new_x = random.randint(0, root.winfo_width() - 100)
    new_y = random.randint(0, root.winfo_height() - 30)
    no_btn.place(x=new_x, y=new_y)

root = tk.Tk()
root.title("Вопрос важный")
root.geometry("400x200")
root.resizable(False, False)

label = tk.Label(root, text="Ты гей?", font=("Arial", 18))
label.pack(pady=20)

yes_btn = tk.Button(root, text="Да", font=("Arial", 12), command=on_yes)
yes_btn.place(x=100, y=100)

no_btn = tk.Button(root, text="Нет", font=("Arial", 12))
no_btn.place(x=200, y=100)
no_btn.bind("<Enter>", on_no_hover)

root.mainloop()
