import tkinter as tk
from tkinter import ttk, messagebox
import math


# -------------------- Helpers --------------------
def safe_float(s: str) -> float:
    s = s.strip()
    if s == "":
        raise ValueError("Поле пустое — введите число")
    try:
        return float(s)
    except Exception:
        raise ValueError("Ожидается число (например: 12.34)")


def parse_int_as_int(s: str) -> int:
    s = s.strip()
    if s == "":
        raise ValueError("Поле пустое — введите целое число")
    try:
        v = float(s)
    except Exception:
        raise ValueError("Ожидается целое число (например: 5)")
    if not v.is_integer():
        raise ValueError("Ожидается целое число без дробной части")
    return int(v)


# -------------------- Main window --------------------
root = tk.Tk()
root.title("Калькулятор")
root.geometry("520x420")
root.resizable(False, False)

style = ttk.Style()
# Необязательно: выбрать тему, если хотите
# style.theme_use('clam')

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=8, pady=8)

frame_basic = ttk.Frame(notebook, padding=12)
frame_trig = ttk.Frame(notebook, padding=12)
frame_math = ttk.Frame(notebook, padding=12)
frame_system = ttk.Frame(notebook, padding=12)

notebook.add(frame_basic, text="Обычный")
notebook.add(frame_trig, text="Тригонометрия")
notebook.add(frame_math, text="Математика")
notebook.add(frame_system, text="Системы счисления")


# -------------------- Обычный калькулятор --------------------
lbl = ttk.Label(frame_basic, text="Обычный калькулятор", font=(None, 12, "bold"))
lbl.grid(row=0, column=0, columnspan=3, pady=(0, 8))

ttk.Label(frame_basic, text="Первое число:").grid(row=1, column=0, sticky="w")
entry_num1 = ttk.Entry(frame_basic, width=20)
entry_num1.grid(row=1, column=1, sticky="w")

ttk.Label(frame_basic, text="Операция:").grid(row=2, column=0, sticky="w")
combo_op = ttk.Combobox(frame_basic, values=["+", "-", "*", "/", "%"], state="readonly", width=6)
combo_op.grid(row=2, column=1, sticky="w")
combo_op.current(0)

ttk.Label(frame_basic, text="Второе число:").grid(row=3, column=0, sticky="w")
entry_num2 = ttk.Entry(frame_basic, width=20)
entry_num2.grid(row=3, column=1, sticky="w")

label_basic_result_var = tk.StringVar(value="Результат:")
label_basic_result = ttk.Label(frame_basic, textvariable=label_basic_result_var, font=(None, 10))
label_basic_result.grid(row=5, column=0, columnspan=3, pady=(8, 0))


def calculate_basic():
    try:
        a = safe_float(entry_num1.get())
        b = safe_float(entry_num2.get())
        op = combo_op.get()

        if op == "+":
            res = a + b
        elif op == "-":
            res = a - b
        elif op == "*":
            res = a * b
        elif op == "/":
            if math.isclose(b, 0.0, abs_tol=1e-12):
                raise ZeroDivisionError("Деление на ноль")
            res = a / b
        elif op == "%":
            # Интерпретируем как "a процентов от b" => (a * b) / 100
            # Если вы хотите другое поведение, напишите — изменю.
            res = (a * b) / 100.0
        else:
            raise ValueError("Неизвестная операция")

        label_basic_result_var.set(f"Результат: {res}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

btn_calc_basic = ttk.Button(frame_basic, text="Вычислить", command=calculate_basic)
btn_calc_basic.grid(row=4, column=0, columnspan=2, pady=6)


# -------------------- Тригонометрия --------------------
ttk.Label(frame_trig, text="Тригонометрические функции", font=(None, 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 8))

ttk.Label(frame_trig, text="Угол (градусы):").grid(row=1, column=0, sticky="w")
entry_angle = ttk.Entry(frame_trig, width=20)
entry_angle.grid(row=1, column=1, sticky="w")

label_trig_result_var = tk.StringVar(value="Результат:")
label_trig_result = ttk.Label(frame_trig, textvariable=label_trig_result_var, font=(None, 10), justify="left")
label_trig_result.grid(row=3, column=0, columnspan=2, pady=(8, 0))


def calculate_trig():
    try:
        angle = safe_float(entry_angle.get())
        r = math.radians(angle)
        s = math.sin(r)
        c = math.cos(r)

        # tan = sin/cos  (не определён, если cos ≈ 0)
        tan = None if math.isclose(c, 0.0, abs_tol=1e-12) else s / c
        # cot = cos/sin (не определён, если sin ≈ 0)
        cot = None if math.isclose(s, 0.0, abs_tol=1e-12) else c / s

        lines = [f"sin = {s:.6f}", f"cos = {c:.6f}"]
        lines.append("tan = не определён" if tan is None else f"tan = {tan:.6f}")
        lines.append("cot = не определён" if cot is None else f"cot = {cot:.6f}")

        label_trig_result_var.set("\n".join(lines))
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

btn_calc_trig = ttk.Button(frame_trig, text="Вычислить", command=calculate_trig)
btn_calc_trig.grid(row=2, column=0, columnspan=2, pady=6)


# -------------------- Математические операции --------------------
ttk.Label(frame_math, text="Математические операции", font=(None, 12, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 8))

ttk.Label(frame_math, text="Операция:").grid(row=1, column=0, sticky="w")
combo_math = ttk.Combobox(frame_math, values=["Степень", "Квадратный корень", "Факториал"], state="readonly")
combo_math.grid(row=1, column=1, sticky="w")
combo_math.current(0)

ttk.Label(frame_math, text="Число:").grid(row=2, column=0, sticky="w")
entry_math1 = ttk.Entry(frame_math, width=20)
entry_math1.grid(row=2, column=1, sticky="w")

lbl_math2 = ttk.Label(frame_math, text="Показатель:")
lbl_math2.grid(row=3, column=0, sticky="w")
entry_math2 = ttk.Entry(frame_math, width=20)
entry_math2.grid(row=3, column=1, sticky="w")

label_math_result_var = tk.StringVar(value="Результат:")
label_math_result = ttk.Label(frame_math, textvariable=label_math_result_var, font=(None, 10))
label_math_result.grid(row=5, column=0, columnspan=3, pady=(8, 0))


def on_math_select(event=None):
    choice = combo_math.get()
    if choice == "Степень":
        entry_math2.config(state="normal")
        lbl_math2.config(text="Показатель:")
    else:
        # для корня и факториала второй ввод не нужен
        entry_math2.delete(0, tk.END)
        entry_math2.config(state="disabled")
        lbl_math2.config(text="")


combo_math.bind("<<ComboboxSelected>>", on_math_select)
# приводим интерфейс в соответствие с текущим выбором
on_math_select()


def calculate_math():
    try:
        choice = combo_math.get()
        if choice == "Степень":
            a = safe_float(entry_math1.get())
            b = safe_float(entry_math2.get())
            res = math.pow(a, b)
        elif choice == "Квадратный корень":
            a = safe_float(entry_math1.get())
            if a < 0:
                raise ValueError("Квадратный корень из отрицательного числа не допустим")
            res = math.sqrt(a)
        elif choice == "Факториал":
            n = parse_int_as_int(entry_math1.get())
            if n < 0:
                raise ValueError("Факториал определён только для неотрицательных целых чисел")
            # math.factorial возвращает int
            res = math.factorial(n)
        else:
            raise ValueError("Неизвестная операция")

        label_math_result_var.set(f"Результат: {res}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

btn_calc_math = ttk.Button(frame_math, text="Вычислить", command=calculate_math)
btn_calc_math.grid(row=4, column=0, columnspan=2, pady=6)


# -------------------- Системы счисления --------------------
ttk.Label(frame_system, text="Перевод числа в другие системы", font=(None, 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 8))

ttk.Label(frame_system, text="Целое число:").grid(row=1, column=0, sticky="w")
entry_number = ttk.Entry(frame_system, width=24)
entry_number.grid(row=1, column=1, sticky="w")

label_system_result_var = tk.StringVar(value="Результат:")
label_system_result = ttk.Label(frame_system, textvariable=label_system_result_var, font=(None, 10), justify="left")
label_system_result.grid(row=3, column=0, columnspan=2, pady=(8, 0))


def calculate_systems():
    try:
        n = parse_int_as_int(entry_number.get())
        if n >= 0:
            b = bin(n)[2:]
            o = oct(n)[2:]
            h = hex(n)[2:].upper()
        else:
            b = "-" + bin(-n)[2:]
            o = "-" + oct(-n)[2:]
            h = "-" + hex(-n)[2:].upper()

        label_system_result_var.set(f"Двоичная: {b}\nВосьмеричная: {o}\nШестнадцатеричная: {h}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

btn_calc_system = ttk.Button(frame_system, text="Перевести", command=calculate_systems)
btn_calc_system.grid(row=2, column=0, columnspan=2, pady=6)


# -------------------- Bindings: Enter key --------------------
# Нажатие Enter будет вызывать соответствующую кнопку в активной вкладке

def on_enter(event=None):
    current = notebook.index(notebook.select())
    if current == 0:
        calculate_basic()
    elif current == 1:
        calculate_trig()
    elif current == 2:
        calculate_math()
    elif current == 3:
        calculate_systems()

root.bind("<Return>", on_enter)


# -------------------- Запуск --------------------
if __name__ == "__main__":
    root.mainloop()
