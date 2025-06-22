import tkinter as tk
from tkinter import messagebox

def check_password():
    if entry.get() == "12345":
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")

root = tk.Tk()
root.title("WinLocker")
root.attributes('-fullscreen', True)
root.configure(bg='black')

label = tk.Label(root, text="Доступ закрыт.", fg="red", bg="black", font=("Arial", 24))
label.pack(pady=50)

entry = tk.Entry(root, show="*", font=("Arial", 18))
entry.pack(pady=20)

button = tk.Button(root, text="Ввести пароль", command=check_password, font=("Arial", 18))
button.pack(pady=20)

root.mainloop()