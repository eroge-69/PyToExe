import tkinter as tk

# 計算各類別加總（空白視為 0）
def calculate_sums():
    try:
        totals = {}
        totals["來客數"] = sum(float(entry.get()) if entry.get() else 0 for entry in visitor_entries)
        totals["現金"] = sum(float(entry.get()) if entry.get() else 0 for entry in cash_entries)
        totals["信用卡"] = sum(float(entry.get()) if entry.get() else 0 for entry in card_entries)
        totals["電子票證"] = sum(float(entry.get()) if entry.get() else 0 for entry in eticket_entries)
        totals["木盒底"] = sum(float(entry.get()) if entry.get() else 0 for entry in box_entries)
        totals["圓底"] = sum(float(entry.get()) if entry.get() else 0 for entry in round_entries)

        result_text = ""
        for key in ["來客數","現金","信用卡","電子票證","木盒底","圓底"]:
            result_text += f"{key}總和: {totals[key]}\n"
        result_label.config(text=result_text)
    except ValueError:
        result_label.config(text="請輸入有效數字！")

# 清空所有輸入框
def clear_entries():
    for entry in visitor_entries + cash_entries + card_entries + eticket_entries + box_entries + round_entries:
        entry.delete(0, tk.END)
    result_label.config(text="")

# 主視窗
root = tk.Tk()
root.title("六類別加總程式")
root.geometry("650x400")
root.configure(bg="#f0f4f8")  # 背景色

# 左欄
left_frame = tk.Frame(root, bg="#f0f4f8")
left_frame.pack(side=tk.LEFT, padx=15, pady=10)

# 右欄
right_frame = tk.Frame(root, bg="#f0f4f8")
right_frame.pack(side=tk.LEFT, padx=15, pady=10)

# 左欄類別
tk.Label(left_frame, text="來客數（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
visitor_entries = [tk.Entry(left_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in visitor_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

tk.Label(left_frame, text="現金（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
cash_entries = [tk.Entry(left_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in cash_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

tk.Label(left_frame, text="信用卡（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
card_entries = [tk.Entry(left_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in card_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

# 右欄類別
tk.Label(right_frame, text="電子票證（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
eticket_entries = [tk.Entry(right_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in eticket_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

tk.Label(right_frame, text="木盒底（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
box_entries = [tk.Entry(right_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in box_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

tk.Label(right_frame, text="圓底（4 個數字）", font=("Arial", 12), bg="#f0f4f8").pack(anchor="w")
round_entries = [tk.Entry(right_frame, width=6, font=("Arial", 12)) for _ in range(4)]
for e in round_entries:
    e.pack(side=tk.LEFT, padx=3, pady=3)

# 按鈕
button_frame = tk.Frame(root, bg="#f0f4f8")
button_frame.pack(pady=15)
tk.Button(button_frame, text="計算總和", font=("Arial", 12), bg="#4caf50", fg="white", width=12, height=2, command=calculate_sums).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="清空數字", font=("Arial", 12), bg="#f44336", fg="white", width=12, height=2, command=clear_entries).pack(side=tk.LEFT, padx=10)

# 結果顯示
result_label = tk.Label(root, text="", font=("Arial", 12), justify=tk.LEFT, bg="#f0f4f8")
result_label.pack(pady=10)

root.mainloop()