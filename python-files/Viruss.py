import tkinter as tk
from tkinter import messagebox
import webbrowser

def on_yes():
    root.destroy()

def on_no():
    webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    root.destroy()

root = tk.Tk()
root.title("Вопрос")
root.geometry("300x150")

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

label = tk.Label(root, text="Сосал?", font=("Arial", 16))
label.pack(pady=20)

frame = tk.Frame(root)
frame.pack()

yes_button = tk.Button(frame, text="Да", command=on_yes, width=10)
yes_button.pack(side=tk.LEFT, padx=10)

no_button = tk.Button(frame, text="Нет", command=on_no, width=10)
no_button.pack(side=tk.LEFT, padx=10)

root.mainloop()
