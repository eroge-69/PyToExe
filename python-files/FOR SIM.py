import tkinter as tk
import math

def press(key):
    entry.insert(tk.END, key)

def clear():
    entry.delete(0, tk.END)
    explanation_label.config(text="")
    equation_label.config(text="")

def calculate():
    try:
        expression = entry.get()
        expr_display = expression

        # 替换特殊符号
        expression = expression.replace("√", "math.sqrt")
        expression = expression.replace("^", "")
        expression = expression.replace("π", str(math.pi))

        result = eval(expression)

        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))

        # 方程式展示
        equation_label.config(text=f"{expr_display} = {result}")

        # 三语解释
        explanation = explain_expression(expr_display, result)
        explanation_label.config(text=explanation)

    except Exception as e:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "错误")
        explanation_label.config(text=f"输入有问题：{e}")
        equation_label.config(text="")

def explain_expression(expression, result):
    zh, en, ms = "", "", ""
    if "+" in expression:
        zh = f"中文: 这是加法：{expression}，结果是 {result}。"
        en = f"English: This is addition: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah tambah: {expression}, hasilnya {result}."
    elif "-" in expression:
        zh = f"中文: 这是减法：{expression}，结果是 {result}。"
        en = f"English: This is subtraction: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah tolak: {expression}, hasilnya {result}."
    elif "*" in expression:
        zh = f"中文: 这是乘法：{expression}，结果是 {result}。"
        en = f"English: This is multiplication: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah darab: {expression}, hasilnya {result}."
    elif "/" in expression:
        zh = f"中文: 这是除法：{expression}，结果是 {result}。"
        en = f"English: This is division: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah bahagi: {expression}, hasilnya {result}."
    elif "√" in expression:
        zh = f"中文: 这是平方根运算：{expression}，结果是 {result}。"
        en = f"English: This is square root: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah punca kuasa dua: {expression}, hasilnya {result}."
    elif "^" in expression:
        zh = f"中文: 这是次方运算：{expression}，结果是 {result}。"
        en = f"English: This is power operation: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ini adalah kuasa: {expression}, hasilnya {result}."
    elif "π" in expression:
        zh = f"中文: 这里用了 π（圆周率）：{expression}，结果是 {result}。"
        en = f"English: This expression uses π (pi): {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Ungkapan ini menggunakan π (pi): {expression}, hasilnya {result}."
    else:
        zh = f"中文: 计算完成：{expression}，结果是 {result}。"
        en = f"English: Calculation done: {expression}, the result is {result}."
        ms = f"Bahasa Melayu: Pengiraan siap: {expression}, hasilnya {result}."

    return zh + "\n" + en + "\n" + ms

# ---------------- UI ----------------
root = tk.Tk()
root.title("For Sim X - 小博士版")
root.geometry("500x650")
root.configure(bg="lightyellow")  # 简单背景，保证能开

entry = tk.Entry(root, font=("Arial", 24), justify="right")
entry.pack(fill="both", ipadx=8, ipady=8, pady=10)

buttons = [
    "7", "8", "9", "+",
    "4", "5", "6", "-",
    "1", "2", "3", "*",
    "0", ".", "=", "/",
    "√", "^", "π", "C"
]

frame = tk.Frame(root, bg="#dddddd")
frame.pack()

row, col = 0, 0
for btn in buttons:
    action = lambda x=btn: press(x)
    if btn == "C":
        action = clear
    elif btn == "=":
        action = calculate

    b = tk.Button(frame, text=btn, width=6, height=3, font=("Arial", 18), command=action)
    b.grid(row=row, column=col, padx=5, pady=5)

    col += 1
    if col > 3:
        col = 0
        row += 1

# 方程式显示
equation_label = tk.Label(root, text="", font=("Arial", 16), fg="darkred", bg="white")
equation_label.pack(pady=10, fill="x")

# 解释框
explanation_label = tk.Label(root, text="", font=("Arial", 13), wraplength=480, justify="left", bg="white", fg="blue")
explanation_label.pack(pady=20, fill="both", expand=True)

root.mainloop()