
import tkinter as tk
from tkinter import messagebox
from openpyxl import load_workbook
from datetime import datetime

excel_path = "monthly_buying.xlsx"

def save_invoice(invoice_date, invoice_no, distributor_name,
                 amount, credit_amount, final_amount, check_no, paid_date):
    try:
        wb = load_workbook(excel_path)
        ws = wb.active
        ws.append([
            invoice_date, invoice_no, distributor_name,
            amount, credit_amount, final_amount, check_no, paid_date
        ])
        wb.save(excel_path)
        return "Invoice saved successfully!"
    except Exception as e:
        return f"Error: {e}"

def create_invoice_app():
    window = tk.Tk()
    window.title("Invoice Entry")

    labels = [
        "Invoice Date (YYYY-MM-DD)", "Invoice No.", "Distributor Name",
        "Amount", "Credit Amount", "Final Amount After Credit",
        "Paid by Check No.", "Paid Date (YYYY-MM-DD)"
    ]
    entries = []

    for i, label_text in enumerate(labels):
        label = tk.Label(window, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(window, width=30)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    def submit():
        data = [entry.get() for entry in entries]
        result = save_invoice(*data)
        messagebox.showinfo("Result", result)
        if "successfully" in result:
            for entry in entries:
                entry.delete(0, tk.END)

    submit_button = tk.Button(window, text="Save Invoice", command=submit)
    submit_button.grid(row=len(labels), columnspan=2, pady=10)

    window.mainloop()

create_invoice_app()
