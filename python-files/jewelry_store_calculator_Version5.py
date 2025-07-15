import tkinter as tk

def calculate_price():
    try:
        weight = float(weight_entry.get())
        rate = float(rate_entry.get())
        making = float(making_entry.get())
        other = float(other_entry.get())
        profit_percent = float(profit_entry.get())

        gold_price = weight * rate
        subtotal = gold_price + making + other
        profit = (profit_percent / 100) * subtotal
        total_before_tax = subtotal + profit
        vat = 0.05 * total_before_tax  # 5% VAT
        final_price = total_before_tax + vat

        result_text = (
            f"Gold Price: AED {gold_price:.2f}\n"
            f"Making Charges: AED {making:.2f}\n"
            f"Other Charges: AED {other:.2f}\n"
            f"Subtotal: AED {subtotal:.2f}\n"
            f"Profit (@{profit_percent}%): AED {profit:.2f}\n"
            f"Total Before Tax: AED {total_before_tax:.2f}\n"
            f"VAT (5%): AED {vat:.2f}\n"
            f"Final Price: AED {final_price:.2f}"
        )
        result_label.config(text=result_text)
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

root = tk.Tk()
root.title("Jewelry Store Gold Price Calculator - UAE")
root.geometry("650x700")  # Much bigger window

# Large font settings
large_font = ("Arial", 24)
entry_font = ("Arial", 24)

tk.Label(root, text="Gold Weight (grams):", font=large_font).pack(pady=10)
weight_entry = tk.Entry(root, font=entry_font, width=16)
weight_entry.pack(pady=10, ipady=10)

tk.Label(root, text="Gold Rate per gram (AED):", font=large_font).pack(pady=10)
rate_entry = tk.Entry(root, font=entry_font, width=16)
rate_entry.pack(pady=10, ipady=10)

tk.Label(root, text="Making Charges (AED):", font=large_font).pack(pady=10)
making_entry = tk.Entry(root, font=entry_font, width=16)
making_entry.pack(pady=10, ipady=10)

tk.Label(root, text="Other Charges (AED):", font=large_font).pack(pady=10)
other_entry = tk.Entry(root, font=entry_font, width=16)
other_entry.pack(pady=10, ipady=10)
other_entry.insert(0, "0")

tk.Label(root, text="Profit Margin (%):", font=large_font).pack(pady=10)
profit_entry = tk.Entry(root, font=entry_font, width=16)
profit_entry.pack(pady=10, ipady=10)

tk.Button(root, text="Calculate", command=calculate_price, font=large_font, width=14, height=2).pack(pady=20)

result_label = tk.Label(root, text="", justify="left", font=("Arial", 20), wraplength=600)
result_label.pack(pady=20)

root.mainloop()