
import tkinter as tk
import math
from bidi.algorithm import get_display
import arabic_reshaper

# تابعی برای تبدیل متن فارسی به حالت قابل‌نمایش در Tkinter
def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# کلاس ماشین حساب
class Calculator:
    def __init__(self, root):
        self.root = root
        root.title(reshape_text("ماشین حساب پیشرفته"))

        # ورودی محاسبه
        self.entry = tk.Entry(root, width=30, font=('Vazir', 18), justify='right')
        self.entry.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

        # تعریف دکمه‌ها
        buttons = [
            '7', '8', '9', '/', 'sqrt', 'C',
            '4', '5', '6', '*', '**', 'log',
            '1', '2', '3', '-', '(', ')',
            '0', '.', '%', '+', '=', 'sin'
        ]

        row = 1
        col = 0
        for button in buttons:
            action = lambda x=button: self.on_click(x)
            b = tk.Button(root, text=reshape_text(button), width=6, height=2, font=('Vazir', 14), command=action)
            b.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 5:
                col = 0
                row += 1

    # واکنش به کلیک دکمه‌ها
    def on_click(self, char):
        if char == '=':
            try:
                # استفاده از eval با توابع امن ریاضی
                result = eval(self.entry.get(), {"__builtins__": None}, {
                    'sqrt': math.sqrt,
                    'log': math.log10,
                    'sin': lambda x: round(math.sin(math.radians(float(x))), 5)
                })
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(result))
            except Exception:
                # پیام خطا به زبان فارسی
                self.entry.delete(0, tk.END)
                self.entry.insert(0, reshape_text("خطا!"))
        elif char == 'C':
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, char)

# اجرای برنامه
if __name__ == '__main__':
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()
