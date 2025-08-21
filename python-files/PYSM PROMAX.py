import tkinter as tk
import math

# ---------------- 功能函数 ----------------
history_list = []

def press(key):
    entry.insert(tk.END, key)

def clear():
    entry.delete(0, tk.END)
    explanation.delete("1.0", tk.END)

def calculate():
    expression = entry.get()
    if not expression.strip():
        return
    try:
        safe_dict = {"pi": math.pi, "sqrt": math.sqrt}
        result = eval(expression, {"_builtins_": None}, safe_dict)

        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))

        # 三语方程式
        equation_text = f"""
中文方程式: {expression} = {result}
English Equation: {expression} = {result}
Bahasa Melayu Persamaan: {expression} = {result}
"""
        explanation_text = explain_expression(expression, result)
        explanation.delete("1.0", tk.END)
        explanation.insert(tk.END, equation_text + explanation_text)

        # 保存历史
        history_list.append(expression)
        update_history()

    except Exception:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "错误")
        explanation.delete("1.0", tk.END)
        explanation.insert(tk.END, "输入错误，请检查公式")

def explain_expression(expression, result):
    if "+" in expression:
        cn, en, ms = "加法", "Addition", "Tambah"
    elif "-" in expression:
        cn, en, ms = "减法", "Subtraction", "Tolak"
    elif "*" in expression:
        cn, en, ms = "乘法", "Multiplication", "Darab"
    elif "/" in expression:
        cn, en, ms = "除法", "Division", "Bahagi"
    elif "sqrt" in expression:
        cn, en, ms = "平方根", "Square Root", "Punca Kuasa Dua"
    elif "pi" in expression:
        cn, en, ms = "使用了 π", "Using π", "Menggunakan π"
    else:
        cn, en, ms = "普通计算", "Normal calculation", "Pengiraan biasa"

    text = f"""
解释：
中文: {cn}: {expression} = {result}
English: {en}: {expression} = {result}
Bahasa Melayu: {ms}: {expression} = {result}

步骤：
中文: 按步骤计算得到结果
English: Follow the steps to get the result
Bahasa Melayu: Ikuti langkah-langkah untuk mendapatkan hasil
"""
    return text

def update_history():
    history_box.delete(0, tk.END)
    for item in history_list[-10:]:
        history_box.insert(tk.END, item)

def use_history(event):
    selection = history_box.curselection()
    if selection:
        expr = history_box.get(selection[0])
        entry.delete(0, tk.END)
        entry.insert(tk.END, expr)

# ---------------- UI ----------------
root = tk.Tk()
root.title("For Sim - 稳定版")
root.geometry("600x750")
root.configure(bg="#E6F2F8")

entry = tk.Entry(root, font=("Arial", 24), justify="right")
entry.pack(fill="both", ipadx=8, ipady=8, pady=10)

buttons = [
    "7", "8", "9", "+",
    "4", "5", "6", "-",
    "1", "2", "3", "*",
    "0", "C", "=", "/",
    "sqrt(", "pi"
]

frame = tk.Frame(root, bg="#E6F2F8")
frame.pack()

row, col = 0, 0
for btn in buttons:
    action = lambda x=btn: press(x)
    if btn == "C":
        action = clear
    elif btn == "=":
        action = calculate

    b = tk.Button(frame, text=btn, width=6, height=3,
                  font=("Arial", 18), command=action,
                  bg="#FFFFFF", fg="#333333", relief="raised")
    b.grid(row=row, column=col, padx=5, pady=5)
    col += 1
    if col > 3:
        col = 0
        row += 1

explanation = tk.Text(root, height=20, font=("Arial", 12), wrap="word", bg="#F9F9F9")
explanation.pack(fill="both", padx=10, pady=10)

history_label = tk.Label(root, text="历史记录（点击使用）", bg="#E6F2F8", font=("Arial", 12))
history_label.pack()
history_box = tk.Listbox(root, height=10, font=("Arial", 12))
history_box.pack(fill="both", padx=10, pady=5)
history_box.bind("<<ListboxSelect>>", use_history)

root.mainloop()