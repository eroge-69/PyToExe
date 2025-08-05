# Sagar Lace Store Billing App
# billing_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import datetime
import os

# Load product data from Excel
PRODUCT_FILE = 'billing_data.xlsx'
if not os.path.exists(PRODUCT_FILE):
    messagebox.showerror("File Missing", f"Required file '{PRODUCT_FILE}' not found.")
    exit()

product_df = pd.read_excel(PRODUCT_FILE)
product_dict = {
    row['Product Name']: {'Rate': row['Rate'], 'GST': row['GST']} for _, row in product_df.iterrows()
}

# Save bill to Excel
def save_invoice(invoice_data):
    filename = f"Invoice_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df = pd.DataFrame(invoice_data)
    df.to_excel(filename, index=False)
    messagebox.showinfo("Saved", f"Invoice saved as {filename}")

# Calculate total with GST
def calculate_total(quantity, rate, gst):
    amount = quantity * rate
    gst_amount = amount * (gst / 100)
    return round(amount + gst_amount, 2)

# GUI Application
class BillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sagar Lace Store Billing App")
        self.root.geometry("700x500")

        # Customer Info
        tk.Label(root, text="Customer Name").grid(row=0, column=0)
        self.customer_name = tk.Entry(root)
        self.customer_name.grid(row=0, column=1)

        tk.Label(root, text="Mobile No.").grid(row=0, column=2)
        self.mobile = tk.Entry(root)
        self.mobile.grid(row=0, column=3)

        # Product Selection
        tk.Label(root, text="Select Product").grid(row=1, column=0)
        self.product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(root, textvariable=self.product_var, values=list(product_dict.keys()))
        self.product_dropdown.grid(row=1, column=1)
        self.product_dropdown.bind("<<ComboboxSelected>>", self.on_product_select)

        tk.Label(root, text="Rate").grid(row=1, column=2)
        self.rate_var = tk.StringVar()
        tk.Entry(root, textvariable=self.rate_var, state='readonly').grid(row=1, column=3)

        tk.Label(root, text="GST (%)").grid(row=2, column=0)
        self.gst_var = tk.StringVar()
        tk.Entry(root, textvariable=self.gst_var, state='readonly').grid(row=2, column=1)

        tk.Label(root, text="Quantity").grid(row=2, column=2)
        self.qty_var = tk.IntVar(value=1)
        tk.Entry(root, textvariable=self.qty_var).grid(row=2, column=3)

        # Add to Bill
        tk.Button(root, text="Add Item", command=self.add_item).grid(row=3, column=1)

        # Treeview for Bill
        columns = ('Product', 'Rate', 'GST', 'Qty', 'Total')
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.grid(row=4, column=0, columnspan=4, pady=10)

        # Save Button
        tk.Button(root, text="Generate Invoice", command=self.save_bill).grid(row=5, column=1, pady=10)

        self.invoice_items = []

    def on_product_select(self, event):
        product = self.product_var.get()
        if product in product_dict:
            self.rate_var.set(product_dict[product]['Rate'])
            self.gst_var.set(product_dict[product]['GST'])

    def add_item(self):
        product = self.product_var.get()
        if product not in product_dict:
            messagebox.showwarning("Select Product", "Please select a valid product.")
            return

        qty = self.qty_var.get()
        rate = float(self.rate_var.get())
        gst = float(self.gst_var.get())
        total = calculate_total(qty, rate, gst)

        self.invoice_items.append({
            'Product': product,
            'Rate': rate,
            'GST': gst,
            'Qty': qty,
            'Total': total
        })

        self.tree.insert('', 'end', values=(product, rate, gst, qty, total))

    def save_bill(self):
        if not self.invoice_items:
            messagebox.showwarning("Empty", "No items in invoice.")
            return

        save_invoice(self.invoice_items)


if __name__ == '__main__':
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()
