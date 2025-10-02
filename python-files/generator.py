import tkinter as tk
from random import randrange


root = tk.Tk()
root.title("Generowanie hasła")
root.geometry("200x100")

def generate():
    passwd = randrange(1000, 9999)
    label.config(text=passwd)

label = tk.Label(root, text="", font=("Arial", 14))
label.pack(pady=10)

button = tk.Button(root, text="Wygenerować hasło", command=generate)
button.pack(pady=10)

root.mainloop()
