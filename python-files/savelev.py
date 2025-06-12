import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def find_numbers():
    try:
        N = int(entry.get())
        if N < 1000:
            messagebox.showerror("Ошибка", "N должно быть ≥ 1000")
            return
        
        result = []
        for num in range(1, N + 1):
            digits = [int(d) for d in str(num)]
            if len(digits) < 3:
                continue
            
            first_last_sum = digits[0] + digits[-1]
            middle_digits = digits[1:-1]
            
            found = False
            for i in range(len(middle_digits)):
                for j in range(i + 1, len(middle_digits)):
                    if middle_digits[i] + middle_digits[j] == first_last_sum:
                        found = True
                        break
                if found:
                    break
            
            if found:
                result.append(str(num))
        
        result_text.delete(1.0, tk.END)
        if result:
            result_text.insert(tk.END, ", ".join(result))
        else:
            result_text.insert(tk.END, "Подходящие числа не найдены")
        
        status_label.config(text=f"Найдено {len(result)} чисел")
    
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное число")

def clear_fields():
    entry.delete(0, tk.END)
    result_text.delete(1.0, tk.END)
    status_label.config(text="")

# Создаем графический интерфейс
root = tk.Tk()
root.title("Поиск чисел по условию")
root.geometry("650x450")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Поле ввода
input_frame = ttk.Frame(frame)
input_frame.pack(fill=tk.X, pady=5)

ttk.Label(input_frame, text="Введите N (≥1000):").pack(side=tk.LEFT)
entry = ttk.Entry(input_frame)
entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
entry.insert(0, "1000")

# Кнопки
button_frame = ttk.Frame(frame)
button_frame.pack(fill=tk.X, pady=5)

search_btn = ttk.Button(button_frame, text="Найти числа", command=find_numbers)
search_btn.pack(side=tk.LEFT, padx=2)

clear_btn = ttk.Button(button_frame, text="Очистить", command=clear_fields)
clear_btn.pack(side=tk.LEFT, padx=2)

# Текстовое поле для вывода результатов
ttk.Label(frame, text="Результаты:").pack()
result_text = scrolledtext.ScrolledText(frame, height=15, wrap=tk.WORD)
result_text.pack(fill=tk.BOTH, expand=True)

# Статус
status_label = ttk.Label(frame, text="")
status_label.pack()

root.mainloop()