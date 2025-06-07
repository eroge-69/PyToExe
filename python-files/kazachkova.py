import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        x = float(entry_x.get())
        y = float(entry_y.get())
        z = float(entry_z.get())
        
        if x == y or y == z or x == z:
            messagebox.showerror("Ошибка", "Числа должны быть попарно различными!")
            return
        
        numbers = [x, y, z]
        sum_xyz = x + y + z
        
        if sum_xyz < 1:
            max_num = max(numbers)
            index = numbers.index(max_num)
            other_nums = [num for num in numbers if num != max_num]
            numbers[index] = sum(other_nums) / 2
        else:
            min_xy = min(x, y)
            if min_xy == x:
                numbers[0] = (y + z) / 2
            else:
                numbers[1] = (x + z) / 2
        
        result_label.config(text=f"Результат: X = {numbers[0]:.3f}, Y = {numbers[1]:.3f}, Z = {numbers[2]:.3f}")
        
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите действительные числа!")

def clear_fields():
    entry_x.delete(0, tk.END)
    entry_y.delete(0, tk.END)
    entry_z.delete(0, tk.END)
    result_label.config(text="Результат: ")

# Создание графического интерфейса
root = tk.Tk()
root.title("Решение задачи с тремя числами")
root.geometry("400x300")

# Элементы интерфейса
label_x = tk.Label(root, text="Введите число X:")
label_x.pack(pady=5)
entry_x = tk.Entry(root)
entry_x.pack(pady=5)

label_y = tk.Label(root, text="Введите число Y:")
label_y.pack(pady=5)
entry_y = tk.Entry(root)
entry_y.pack(pady=5)

label_z = tk.Label(root, text="Введите число Z:")
label_z.pack(pady=5)
entry_z = tk.Entry(root)
entry_z.pack(pady=5)

# Фрейм для кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

calculate_button = tk.Button(button_frame, text="Вычислить", command=calculate)
calculate_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(button_frame, text="Очистить", command=clear_fields)
clear_button.pack(side=tk.LEFT, padx=5)

result_label = tk.Label(root, text="Результат: ")
result_label.pack(pady=10)

root.mainloop()