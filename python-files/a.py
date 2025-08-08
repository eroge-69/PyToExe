# calculator.py
# آلة حاسبة بواجهة رسومية (tkinter) — دعم + - * / % ** و التعامل مع النقطة
import tkinter as tk
import ast
import operator as op

# دوال لتقييم تعبير بشكل آمن باستخدام ast
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def safe_eval(expr: str):
    """
    يقبل تعبيرًا نصيًا ويعيد القيمة العددية أو يرمي استثناء عند وجود شيء غير مصرح.
    يدعم الأعداد العشرية والعمليات الأساسية.
    """
    def _eval(node):
        if isinstance(node, ast.Num):  # Python <3.8
            return node.n
        if hasattr(ast, "Constant") and isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("قيمة غير مدعومة")
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError("عامل غير مسموح")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError("عامل وحيد غير مسموح")
        raise ValueError("بناء جملة غير مدعوم")
    parsed = ast.parse(expr, mode='eval')
    return _eval(parsed.body)

# واجهة المستخدم
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("آلة حاسبة")
        self.geometry("320x420")
        self.resizable(False, False)
        self.configure(bg="#222")

        self.expr = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        entry = tk.Entry(self, textvariable=self.expr, font=("Arial", 24), bd=0,
                         bg="#eee", justify="right")
        entry.pack(fill="both", padx=10, pady=10, ipady=10)

        btns_frame = tk.Frame(self, bg="#222")
        btns_frame.pack(expand=True, fill="both")

        buttons = [
            ["C", "←", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="],
        ]

        for r, row in enumerate(buttons):
            row_frame = tk.Frame(btns_frame, bg="#222")
            row_frame.pack(expand=True, fill="both")
            for c, label in enumerate(row):
                btn = tk.Button(row_frame, text=label, font=("Arial", 18),
                                relief="flat", bd=0, padx=8, pady=15,
                                command=lambda l=label: self.on_button(l))
                btn.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    def on_button(self, label):
        if label == "C":
            self.expr.set("")
        elif label == "←":
            self.expr.set(self.expr.get()[:-1])
        elif label == "=":
            self.calculate()
        elif label == "+/-":
            self.toggle_sign()
        else:
            # اضغط زر يضيف للنص
            self.expr.set(self.expr.get() + label)

    def toggle_sign(self):
        s = self.expr.get()
        if not s:
            return
        try:
            # نجرب تقييم كامل ونبدل الإشارة
            val = safe_eval(s)
            if isinstance(val, (int, float)):
                # إزالة الكسور العدمية عند عدد صحيح
                if float(val).is_integer():
                    val = int(val)
                self.expr.set(str(-val))
        except Exception:
            # إذا لم ينجح، نجرب إقحام إشارة للمقدمة/الإزالة اليدوية
            if s.startswith("-"):
                self.expr.set(s[1:])
            else:
                self.expr.set("-" + s)

    def calculate(self):
        expr = self.expr.get().replace("×", "*").replace("÷", "/")
        try:
            result = safe_eval(expr)
            # عرض بصيغة مناسبة (int إذا كان عددًا صحيحًا)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expr.set(str(result))
        except Exception as e:
            self.expr.set("خطأ")
            # يمكنك إلغاء التعليق لعرض التفاصيل أثناء التطوير
            # print("Evaluation error:", e)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()