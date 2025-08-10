import tkinter as tk
from tkinter import messagebox

def disable_event():
    pass

root = tk.Tk()
root.title("Ошибка")
root.protocol("WM_DELETE_WINDOW", disable_event)

label = tk.Label(root, text="idi na fig", font=("Arial", 14))
label.pack(pady=20)

button_yes1 = tk.Button(root, text="Да", width=10, command=root.quit)
button_yes1.pack(side=tk.LEFT, padx=20, pady=10)

button_yes2 = tk.Button(root, text="Да", width=10, command=root.quit)
button_yes2.pack(side=tk.RIGHT, padx=20, pady=10)

root.mainloop()