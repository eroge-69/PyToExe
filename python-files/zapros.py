import tkinter as tk
from tkinter import messagebox

def handle_request(answer):
    if answer == "yes":
        pass  # Ничего не делаем
    else:
        messagebox.showinfo("Информация", "Запрос не обработан")
        root.destroy()

root = tk.Tk()
root.title("Серьезный запрос")
root.geometry("250x120")
root.resizable(False, False)

label = tk.Label(root, text="Обработать запрос?", font=("Arial", 12))
label.pack(pady=15)

frame = tk.Frame(root)
frame.pack()

yes_button = tk.Button(frame, text="Да", width=10, command=lambda: handle_request("yes"))
yes_button.pack(side="left", padx=5)

no_button = tk.Button(frame, text="Нет", width=10, command=lambda: handle_request("no"))
no_button.pack(side="right", padx=5)

root.mainloop()