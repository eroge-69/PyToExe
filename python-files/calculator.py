import tkinter as tk
from tkinter import messagebox, ttk
import random

# نافذة رئيسية
root = tk.Tk()
root.title("Calculator")
root.geometry("350x450")
root.resizable(False, False)

# مربع الإدخال
entry = tk.Entry(root, width=18, font=("Arial", 24),
                 borderwidth=5, relief="ridge", justify="right")
entry.grid(row=0, column=0, columnspan=4, pady=10)

# متغير لتشغيل المقلب
prank_mode = False

# نافذة كبيرة بالشريط (رئيسية)
def main_fake_window():
    win = tk.Toplevel(root)
    win.title("System Process")
    win.geometry("400x200+{}+{}".format(root.winfo_screenwidth()//2 - 200,
                                        root.winfo_screenheight()//2 - 100))
    win.resizable(False, False)
    win.attributes("-topmost", True)  # 👈 دائماً فوق الكل

    tk.Label(win, text="Copying files...", font=("Arial", 16)).pack(pady=10)

    progress = ttk.Progressbar(win, length=300, mode='determinate')
    progress.pack(pady=10)

    percent = tk.Label(win, text="0%")
    percent.pack()

    def update_bar(i=0):
        if i <= 100:
            progress['value'] = i
            percent.config(text=f"{i}%")
            win.after(300, update_bar, i+5)  # يتحرك ببطء
        else:
            percent.config(text="Done ✅")

    update_bar()

# نوافذ صغيرة وهمية مع اهتزاز
def fake_window():
    win = tk.Toplevel(root)
    win.title("System")
    w, h = 250, 100
    x = random.randint(0, root.winfo_screenwidth() - w)
    y = random.randint(0, root.winfo_screenheight() - h)
    win.geometry(f"{w}x{h}+{x}+{y}")
    win.attributes("-topmost", True)  # 👈 دائماً فوق الكل
    tk.Label(win, text="Error: Unknown issue", font=("Arial", 12)).pack(expand=True)

    # ✨ حركة الاهتزاز
    def shake(count=0):
        if count < 10:
            dx = (-1) ** count * 10  # يتحرك يمين/يسار
            win.geometry(f"{w}x{h}+{x+dx}+{y}")
            win.after(50, shake, count+1)

    shake()

# إدخال
def press(value):
    global prank_mode
    entry.insert(tk.END, value)

    # تفعيل المقلب مباشرة عند كتابة 0000
    if entry.get() == "0000":
        prank_mode = True
        messagebox.showwarning("Warning", "Unknown error occurred!")
        entry.delete(0, tk.END)
        main_fake_window()

    # إلغاء المقلب مباشرة عند كتابة 1111
    elif entry.get() == "1111":
        prank_mode = False
        messagebox.showinfo("Info", "System restored to normal ✅")
        entry.delete(0, tk.END)

# مسح
def clear():
    if not prank_mode:  # ما يشتغل لو المقلب شغال
        entry.delete(0, tk.END)

# حساب
def calculate():
    global prank_mode
    expression = entry.get()

    # إذا المزحة مفعلة
    if prank_mode:
        for _ in range(3):
            fake_window()
        clear()
        return

    # عادي
    try:
        result = eval(expression)
        clear()
        entry.insert(tk.END, str(result))
    except:
        messagebox.showerror("Error", "Invalid expression!")
        clear()

# إغلاق
def on_close():
    if prank_mode:
        main_fake_window()
        for _ in range(15):
            fake_window()
    else:
        root.destroy()

# الأزرار
buttons = [
    ('7',1,0), ('8',1,1), ('9',1,2), ('/',1,3),
    ('4',2,0), ('5',2,1), ('6',2,2), ('*',2,3),
    ('1',3,0), ('2',3,1), ('3',3,2), ('-',3,3),
    ('0',4,0), ('.',4,1), ('=',4,2), ('+',4,3),
    ('C',5,0)
]

for (text, row, col) in buttons:
    if text == "=":
        b = tk.Button(root, text=text, width=5, height=2,
                      font=("Arial", 16), command=calculate)
    elif text == "C":
        b = tk.Button(root, text=text, width=22, height=2,
                      font=("Arial", 16), command=clear)
    else:
        b = tk.Button(root, text=text, width=5, height=2,
                      font=("Arial", 16), command=lambda t=text: press(t))
    b.grid(row=row, column=col, padx=5, pady=5, columnspan=1 if text != "C" else 4)

# زر X
root.protocol("WM_DELETE_WINDOW", on_close)

# تشغيل
root.mainloop()