import tkinter as tk

def calculate():
    try:
        result = eval(entry.get())
        result_label.config(text=f"Результат: {result}")
    except:
        result_label.config(text="Ошибка, проверьте ввод")

root = tk.Tk()
root.title("Калькулятор")

entry = tk.Entry(root, width=30)
entry.pack(pady=10)

calc_button = tk.Button(root, text="Посчитать", command=calculate)
calc_button.pack(pady=5)

result_label = tk.Label(root, text="Результат: ")
result_label.pack(pady=10)

root.mainloop()