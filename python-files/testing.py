import tkinter as tk
from tkinter import messagebox
import math

def solve_equation():
    try:

        a = entry_a.get()
        b = entry_b.get()
        c = entry_c.get()
        round_digits = entry_round.get()
        

        if a == "" or b == "" or c == "" or round_digits == "":
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        a = float(a.replace(',', '.'))
        b = float(b.replace(',', '.'))
        c = float(c.replace(',', '.'))
        round_digits = int(round_digits)
        
        
        text_result.delete(1.0, tk.END)
        
        text_result.insert(tk.END, f"Уравнение: {a}x² + {b}x + {c} = 0\n")
        text_result.insert(tk.END, "-" * 40 + "\n")
        

        if a == 0:
            if b == 0:
                if c == 0:
                    result = "Бесконечное количество решений"
                else:
                    result = "Нет решений"
            else:
   
                x = -c / b
                x = round(x, round_digits)
                result = f"Линейное уравнение\nx = {x}"
        else:
    
            D = b*b - 4*a*c
            text_result.insert(tk.END, f"Дискриминант D = {D}\n")
            
            if D > 0:
                x1 = (-b + math.sqrt(D)) / (2*a)
                x2 = (-b - math.sqrt(D)) / (2*a)
                x1 = round(x1, round_digits)
                x2 = round(x2, round_digits)
                result = f"Два корня:\nx₁ = {x1}\nx₂ = {x2}"
            elif D == 0:
                x = -b / (2*a)
                x = round(x, round_digits)
                result = f"Один корень:\nx = {x}"
            else:
                result = "Действительных корней нет"
        
        text_result.insert(tk.END, f"\nРезультат:\n{result}")
        
    except ValueError:
        messagebox.showerror("Ошибка", "Введите правильные числа!")
    except ZeroDivisionError:
        messagebox.showerror("Ошибка", "Деление на ноль!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

def clear_all():
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_round.delete(0, tk.END)
    entry_round.insert(0, "2")
    text_result.delete(1.0, tk.END)


root = tk.Tk()
root.title("Решение квадратных уравнений")
root.geometry("400x500")


label_title = tk.Label(root, text="Решение квадратного уравнения", font=("Arial", 14))
label_title.pack(pady=10)


frame_coeff = tk.Frame(root)
frame_coeff.pack(pady=10)

tk.Label(frame_coeff, text="a =").grid(row=0, column=0, padx=5, pady=5)
entry_a = tk.Entry(frame_coeff, width=10)
entry_a.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_coeff, text="b =").grid(row=1, column=0, padx=5, pady=5)
entry_b = tk.Entry(frame_coeff, width=10)
entry_b.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_coeff, text="c =").grid(row=2, column=0, padx=5, pady=5)
entry_c = tk.Entry(frame_coeff, width=10)
entry_c.grid(row=2, column=1, padx=5, pady=5)


frame_round = tk.Frame(root)
frame_round.pack(pady=5)

tk.Label(frame_round, text="Знаков после запятой:").pack(side=tk.LEFT, padx=5)
entry_round = tk.Entry(frame_round, width=5)
entry_round.pack(side=tk.LEFT, padx=5)
entry_round.insert(0, "2")


frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_solve = tk.Button(frame_buttons, text="Решить", command=solve_equation, width=10)
btn_solve.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(frame_buttons, text="Очистить", command=clear_all, width=10)
btn_clear.pack(side=tk.LEFT, padx=5)


frame_result = tk.Frame(root)
frame_result.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

tk.Label(frame_result, text="Результат:").pack(anchor=tk.W)
text_result = tk.Text(frame_result, height=8, width=40)
text_result.pack(fill=tk.BOTH, expand=True)


root.mainloop()