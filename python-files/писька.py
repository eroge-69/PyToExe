import tkinter as tk
from tkinter import messagebox

def check_age():
    try:
        age = int(entry.get())
        
        if age < 0:
            messagebox.showwarning("Ошибка", "Иди нахуй, пиздабол! Отрицательный возраст? Серьёзно?")
        elif age < 18:
            messagebox.showwarning("Результат", "Иди нахуй, пиздюк!")
        elif 18 <= age <= 51:
            messagebox.showinfo("Результат", "Лан, проходи, заебал.")
        elif age == 52:
            messagebox.showinfo("Результат", "Йооооу 52, всем нашим, ещкереее!")
        elif 53 <= age <= 122:
            messagebox.showinfo("Результат", "Нихуя ты старый...")
        elif age > 122:
            messagebox.showwarning("Результат", "Иди нахуй, пиздабол! Такого возраста не бывает.")
        else:
            messagebox.showerror("Ошибка", "Ты че, ваще с Марса?")
    
    except ValueError:
        messagebox.showerror("Ошибка", "Ты че, буквы в возрасте пишешь? Цифры, долбоёб!")

window = tk.Tk()
window.title("Писюнетик Про Макс")
window.geometry("300x150")

label = tk.Label(window, text="Введи свой возраст:", font=("Arial", 12))
label.pack(pady=10)

entry = tk.Entry(window, font=("Arial", 12))
entry.pack(pady=5)

button = tk.Button(window, text="Проверить", command=check_age, font=("Arial", 12))
button.pack(pady=10)

window.mainloop()