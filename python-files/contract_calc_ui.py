import tkinter as tk
from tkinter import ttk

def calculate(*args):
    try:
        risk_amt = float(risk_entry.get())
        entry_price = float(entry_entry.get())
        sl_price = float(sl_entry.get())

        per_contract_loss = abs(entry_price - sl_price)

        if per_contract_loss <= 0:
            result.config(text="SL設定有誤！")
            return

        contracts = risk_amt / per_contract_loss
        position_value = contracts * entry_price

        result.config(text=f"合約數量: {contracts:.2f}\n合約價值: {position_value:.2f}")

    except ValueError:
        result.config(text="等待有效輸入...")

app = tk.Tk()
app.title("簡易合約計算器")
app.geometry("300x220")
app.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use('clam')

# 輸入框設定
fields = [
    ("Risk (金額):", 'risk_entry'),
    ("Entry Price:", 'entry_entry'),
    ("SL Price:", 'sl_entry')
]

entries = {}
for idx, (label_text, var_name) in enumerate(fields, 1):
    ttk.Label(app, text=label_text, background="#f0f0f0").grid(row=idx, column=0, padx=10, pady=10, sticky="w")
    entry = ttk.Entry(app)
    entry.grid(row=idx, column=1, padx=10, pady=10)
    entry.bind("<KeyRelease>", calculate)
    entries[var_name] = entry

risk_entry = entries['risk_entry']
entry_entry = entries['entry_entry']
sl_entry = entries['sl_entry']

# 結果顯示
result = ttk.Label(app, text="等待有效輸入...", font=("Arial", 12), background="#f0f0f0")
result.grid(row=len(fields)+1, column=0, columnspan=2, pady=15)

app.mainloop()
