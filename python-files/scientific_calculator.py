import tkinter as tk
import math

# --- الدوال الرئيسية للحاسبة ---

def click_button(char):
    """
    تُضاف الأحرف (أرقام أو عمليات) إلى شاشة العرض.
    """
    current_text = entry.get()
    entry.delete(0, tk.END) # مسح المحتوى الحالي
    entry.insert(0, current_text + str(char)) # إضافة الحرف الجديد

def clear_screen():
    """
    مسح شاشة العرض بالكامل.
    """
    entry.delete(0, tk.END)

def calculate():
    """
    حساب التعبير الرياضي الموجود في شاشة العرض.
    """
    current_expression = entry.get()
    try:
        # استبدال بعض الرموز لتتوافق مع Python's eval()
        # على سبيل المثال، "^" للأس تصبح "**" في بايثون
        expression = current_expression.replace('^', '**')

        # السماح باستخدام دوال مكتبة math مباشرة
        # هذه خطوة حاسمة للحاسبة العلمية
        # يجب توخي الحذر عند استخدام eval() مع مدخلات المستخدم بشكل عام
        # ولكن في هذه الحاسبة البسيطة، هي مقبولة
        result = str(eval(expression, {"__builtins__": None}, math.__dict__)) # تقييم التعبير
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(0, "خطأ")
        print(f"حدث خطأ: {e}")

# --- إعداد واجهة المستخدم الرسومية (GUI) ---

root = tk.Tk()
root.title("الحاسبة العلمية - Python")
root.geometry("400x550") # تحديد حجم النافذة
root.resizable(False, False) # منع تغيير حجم النافذة

# شاشة العرض (Entry)
entry = tk.Entry(root, width=30, borderwidth=5, font=('Arial', 20), justify='right')
entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10) # span يمتد على 5 أعمدة

# --- إنشاء الأزرار ---

# الأزرار العادية (الأرقام والعمليات الأساسية)
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('C', 1, 4),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), ('(', 2, 4),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), (')', 3, 4),
    ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3), ('^', 4, 4),
]

# الأزرار العلمية
scientific_buttons = [
    ('sin', 5, 0), ('cos', 5, 1), ('tan', 5, 2), ('log', 5, 3), ('sqrt', 5, 4),
    ('exp', 6, 0), ('pi', 6, 1), ('e', 6, 2), ('abs', 6, 3), ('mod', 6, 4),
]

# إضافة الأزرار العادية
for (text, row, col) in buttons:
    if text == '=':
        btn = tk.Button(root, text=text, padx=20, pady=20, font=('Arial', 15), command=calculate, bg='#4CAF50', fg='white')
    elif text == 'C':
        btn = tk.Button(root, text=text, padx=20, pady=20, font=('Arial', 15), command=clear_screen, bg='#f44336', fg='white')
    else:
        btn = tk.Button(root, text=text, padx=20, pady=20, font=('Arial', 15), command=lambda char=text: click_button(char))
    btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5) # sticky للتمدد داخل الخلية

# إضافة الأزرار العلمية
for (text, row, col) in scientific_buttons:
    btn = tk.Button(root, text=text, padx=20, pady=20, font=('Arial', 15),
                    command=lambda char=text: click_button(char + '(') if char not in ['pi', 'e'] else click_button('math.' + char),
                    bg='#2196F3', fg='white')
    btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

# ضبط تمدد الأعمدة والصفوف لجعل الأزرار تتوسع بمرونة
for i in range(7): # لدينا 7 صفوف تقريبا (0 للشاشة و 6 للأزرار)
    root.grid_rowconfigure(i, weight=1)
for i in range(5): # 5 أعمدة
    root.grid_columnconfigure(i, weight=1)

# بدء حلقة Tkinter الرئيسية
root.mainloop()
