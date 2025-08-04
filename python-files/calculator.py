import math
import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        amount = float(entry.get())
        result = amount * 1.05 * 1.0417
        rounded_result = math.ceil(result)
        messagebox.showinfo("結果", f"計算結果為：{rounded_result}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字")

# 建立 GUI 介面
root = tk.Tk()
root.title("金額計算工具")

tk.Label(root, text="請輸入金額：").pack(pady=10)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="計算", command=calculate).pack(pady=10)

root.mainloop()
