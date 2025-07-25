import tkinter as tk
from tkinter import messagebox

def format_yen(amount):
    return f"¥{amount:,.0f}"

def calculate():
    try:
        students = int(entry_students.get())
        price = int(entry_price.get())
        frequency = int(entry_frequency.get())

        weekly = students * price * frequency
        monthly = weekly * 4
        yearly = weekly * 52

        label_monthly_result.config(text=format_yen(monthly))
        label_yearly_result.config(text=format_yen(yearly))
    except ValueError:
        messagebox.showerror("エラー", "すべての入力欄に数字を入力してください。")

root = tk.Tk()
root.title("学校予算計算機")
root.geometry("400x350")
root.configure(bg="#f0f8ff")

title = tk.Label(root, text="学校の予算計算", font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#333")
title.pack(pady=10)

frame_inputs = tk.Frame(root, bg="#f0f8ff")
frame_inputs.pack(pady=5)

tk.Label(frame_inputs, text="生徒数：", font=("Helvetica", 12), bg="#f0f8ff").grid(row=0, column=0, sticky="e")
entry_students = tk.Entry(frame_inputs, width=10, font=("Helvetica", 12))
entry_students.grid(row=0, column=1, padx=10)

tk.Label(frame_inputs, text="1レッスンの料金（円）：", font=("Helvetica", 12), bg="#f0f8ff").grid(row=1, column=0, sticky="e")
entry_price = tk.Entry(frame_inputs, width=10, font=("Helvetica", 12))
entry_price.grid(row=1, column=1, padx=10)

tk.Label(frame_inputs, text="週あたりの回数：", font=("Helvetica", 12), bg="#f0f8ff").grid(row=2, column=0, sticky="e")
entry_frequency = tk.Entry(frame_inputs, width=10, font=("Helvetica", 12))
entry_frequency.grid(row=2, column=1, padx=10)

btn = tk.Button(root, text="計算する", font=("Helvetica", 14), bg="#87cefa", command=calculate)
btn.pack(pady=15)

frame_results = tk.Frame(root, bg="#f0f8ff")
frame_results.pack(pady=10)

tk.Label(frame_results, text="月間収入：", font=("Helvetica", 12, "bold"), bg="#f0f8ff").grid(row=0, column=0, sticky="e")
label_monthly_result = tk.Label(frame_results, text="¥0", font=("Helvetica", 12), bg="#f0f8ff")
label_monthly_result.grid(row=0, column=1)

tk.Label(frame_results, text="年間収入：", font=("Helvetica", 12, "bold"), bg="#f0f8ff").grid(row=1, column=0, sticky="e")
label_yearly_result = tk.Label(frame_results, text="¥0", font=("Helvetica", 12), bg="#f0f8ff")
label_yearly_result.grid(row=1, column=1)

root.mainloop()
