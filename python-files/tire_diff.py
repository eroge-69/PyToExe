import tkinter as tk
from tkinter import scrolledtext

def compare_texts():
    text1 = input1.get("1.0", tk.END).strip().splitlines()
    text2 = input2.get("1.0", tk.END).strip().splitlines()

    # Находим строки из text1, которых нет в text2
    differences = [line for line in text1 if line not in text2]

    # Выводим в третье поле
    output.delete("1.0", tk.END)
    if differences:
        output.insert("1.0", "\n".join(differences))
    else:
        output.insert("1.0", "Нет различий.")

# Создаём главное окно
root = tk.Tk()
root.title("Сравнение размеров шин")
root.geometry("600x800")

# Первое поле ввода (с прокруткой)
tk.Label(root, text="Первое поле (оригинал):").pack(pady=5)
input1 = scrolledtext.ScrolledText(root, width=50, height=10)
input1.pack(pady=5)

# Второе поле ввода
tk.Label(root, text="Второе поле (сравнение):").pack(pady=5)
input2 = scrolledtext.ScrolledText(root, width=50, height=10)
input2.pack(pady=5)

# Кнопка сравнения
compare_button = tk.Button(root, text="Сравнить", command=compare_texts)
compare_button.pack(pady=10)

# Поле вывода
tk.Label(root, text="Различия (строки из первого, которых нет во втором):").pack(pady=5)
output = scrolledtext.ScrolledText(root, width=50, height=8)
output.pack(pady=5)

# Запуск
root.mainloop()
