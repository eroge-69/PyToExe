import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        unit_cost = float(entry_unit_cost.get())
        qty = int(entry_qty.get())
        total_unit_cost = unit_cost * qty

        sscl_percent = float(entry_sscl.get()) if var_sscl.get() else 0
        vat_percent = float(entry_vat.get()) if var_vat.get() else 0

        sscl_amount = unit_cost * (sscl_percent / 100) if sscl_percent else 0
        vat_amount = (unit_cost + sscl_amount) * (vat_percent / 100) if vat_percent else 0

        total_with_tax = (unit_cost + sscl_amount + vat_amount) * qty

        result_text = f"""
Total Unit Cost (without tax): {total_unit_cost:.2f}
SSCL per Unit: {sscl_amount:.2f}
VAT per Unit: {vat_amount:.2f}
Total Cost with Taxes: {total_with_tax:.2f}
"""
        txt_result.config(state='normal')
        txt_result.delete("1.0", tk.END)
        txt_result.insert(tk.END, result_text)
        txt_result.config(state='disabled')

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

# GUI setup
root = tk.Tk()
root.title("Cost Calculator")

tk.Label(root, text="Unit Cost:").grid(row=0, column=0)
entry_unit_cost = tk.Entry(root)
entry_unit_cost.grid(row=0, column=1)

tk.Label(root, text="Quantity:").grid(row=1, column=0)
entry_qty = tk.Entry(root)
entry_qty.grid(row=1, column=1)

var_sscl = tk.BooleanVar()
chk_sscl = tk.Checkbutton(root, text="Apply SSCL", variable=var_sscl)
chk_sscl.grid(row=2, column=0)
entry_sscl = tk.Entry(root)
entry_sscl.grid(row=2, column=1)
entry_sscl.insert(0, "2.5")  # default percentage

var_vat = tk.BooleanVar()
chk_vat = tk.Checkbutton(root, text="Apply VAT", variable=var_vat)
chk_vat.grid(row=3, column=0)
entry_vat = tk.Entry(root)
entry_vat.grid(row=3, column=1)
entry_vat.insert(0, "18")  # default percentage

btn_calculate = tk.Button(root, text="Calculate", command=calculate)
btn_calculate.grid(row=4, column=0, columnspan=2, pady=10)

txt_result = tk.Text(root, height=6, width=40, state='disabled')
txt_result.grid(row=5, column=0, columnspan=2)

root.mainloop()
