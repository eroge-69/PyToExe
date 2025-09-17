# calculator.py
import tkinter as tk
import ast
import operator as op

# --- безопасный вычислитель (только числа и арифм операции) ---
_ops = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}
_unary = {
    ast.UAdd: lambda x: +x,
    ast.USub: lambda x: -x,
}

def safe_eval(expr: str):
    """Вычисляет арифметическое выражение безопасно (без eval)."""
    expr = expr.strip()
    if not expr:
        raise ValueError("Пустое выражение")
    node = ast.parse(expr, mode="eval")
    return _eval(node.body)

def _eval(node):
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _ops:
            raise ValueError("Недопустимая операция")
        return _ops[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _unary:
            raise ValueError("Недопустимая унарная операция")
        return _unary[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Num):  # Python <3.8
        return node.n
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Недопустимое значение")
    raise ValueError(f"Недопустимый элемент: {type(node).__name__}")

# --- UI ---
BG = "#0f1115"
BTN_BG = "#1f2329"
ACCENT = "#ff9f1c"
EQUAL_BG = "#0a84ff"
TEXT = "#ffffff"

root = tk.Tk()
root.title("Калькулятор")
root.configure(bg=BG)
root.geometry("360x520")
root.resizable(False, False)

# Экран
entry = tk.Entry(root, font=("Segoe UI", 28), justify="right",
                 bg="#121418", fg=TEXT, bd=0, insertbackground=TEXT)
entry.pack(fill="both", padx=12, pady=(18, 8), ipady=18)
entry.focus_set()

def press(ch):
    entry.insert(tk.END, ch)

def clear():
    entry.delete(0, tk.END)

def backspace():
    s = entry.get()
    if s:
        entry.delete(len(s)-1, tk.END)

def calculate(event=None):
    expr = entry.get()
    try:
        result = safe_eval(expr)
        # Отображаем результат, но поддерживаем float -> int, если целое
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except ZeroDivisionError:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Ошибка: деление на 0")
    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Ошибка")

# Кнопки
btn_frame = tk.Frame(root, bg=BG)
btn_frame.pack(expand=True, fill="both", padx=12, pady=12)

buttons = [
    ["C", "(", ")", "←"],
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
]

for r, row in enumerate(buttons):
    btn_frame.rowconfigure(r, weight=1, uniform="row")
    for c, char in enumerate(row):
        btn_frame.columnconfigure(c, weight=1, uniform="col")
        if char == "C":
            cmd = clear
            bg = "#d63b3b"
        elif char == "←":
            cmd = backspace
            bg = BTN_BG
        elif char == "=":
            cmd = calculate
            bg = EQUAL_BG
        else:
            cmd = lambda ch=char: press(ch)
            bg = BTN_BG if char not in ("+", "-", "*", "/", "(", ")") else BTN_BG

        b = tk.Button(btn_frame, text=char, font=("Segoe UI", 18, "bold"),
                      command=cmd, bd=0, relief="flat",
                      bg=bg, fg=TEXT, activebackground="#2b2b2b")
        b.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

# Клавиатурные привязки
root.bind("<Return>", calculate)
root.bind("<KP_Enter>", calculate)
root.bind("<BackSpace>", lambda e: backspace())
root.bind("<Escape>", lambda e: clear())

# Доп: вставляем копирование/вставку с Ctrl+C / Ctrl+V на Windows/Linux
def paste_from_clipboard(event=None):
    try:
        txt = root.clipboard_get()
        entry.insert(tk.END, txt)
    except tk.TclError:
        pass

root.bind("<Control-v>", paste_from_clipboard)
root.bind("<Control-V>", paste_from_clipboard)

if __name__ == "__main__":
    root.mainloop()
