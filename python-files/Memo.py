import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CashMemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cash Memo Generator")

        # Top Frame: Seller, Buyer, Invoice number, Date
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill='x')

        tk.Label(top_frame, text="Seller:").grid(row=0, column=0, sticky='w')
        self.seller_entry = tk.Entry(top_frame, width=30)
        self.seller_entry.grid(row=0, column=1, padx=5)

        tk.Label(top_frame, text="Buyer:").grid(row=0, column=2, sticky='w')
        self.buyer_entry = tk.Entry(top_frame, width=30)
        self.buyer_entry.grid(row=0, column=3, padx=5)

        tk.Label(top_frame, text="Invoice No:").grid(row=1, column=0, sticky='w')
        self.invoice_entry = tk.Entry(top_frame, width=30)
        self.invoice_entry.grid(row=1, column=1, padx=5)

        tk.Label(top_frame, text="Date (DD-MM-YYYY):").grid(row=1, column=2, sticky='w')
        self.date_entry = tk.Entry(top_frame, width=30)
        self.date_entry.grid(row=1, column=3, padx=5)
        self.date_entry.insert(0, datetime.now().strftime('%d-%m-%Y'))

        # Middle Frame: Table for products
        middle_frame = tk.Frame(root)
        middle_frame.pack(fill='both', expand=True, pady=10)

        columns = ('S.No', 'Qty', 'Box', 'Product Details', 'MRP', 'Discount', 'Amount')
        self.tree = ttk.Treeview(middle_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(middle_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Entry fields to add new product
        entry_frame = tk.Frame(root, pady=5)
        entry_frame.pack(fill='x')

        self.qty_var = tk.StringVar()
        self.box_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.mrp_var = tk.StringVar()
        self.discount_var = tk.StringVar()

        tk.Label(entry_frame, text="Qty:").grid(row=0, column=0)
        tk.Entry(entry_frame, textvariable=self.qty_var, width=6).grid(row=0, column=1)

        tk.Label(entry_frame, text="Box:").grid(row=0, column=2)
        tk.Entry(entry_frame, textvariable=self.box_var, width=6).grid(row=0, column=3)

        tk.Label(entry_frame, text="Product Details:").grid(row=0, column=4)
        tk.Entry(entry_frame, textvariable=self.product_var, width=30).grid(row=0, column=5)

        tk.Label(entry_frame, text="MRP:").grid(row=0, column=6)
        tk.Entry(entry_frame, textvariable=self.mrp_var, width=8).grid(row=0, column=7)

        tk.Label(entry_frame, text="Discount (%):").grid(row=0, column=8)
        tk.Entry(entry_frame, textvariable=self.discount_var, width=8).grid(row=0, column=9)

        tk.Button(entry_frame, text="Add Item", command=self.add_item).grid(row=0, column=10, padx=10)

        # Bottom Frame: Amount summary
        bottom_frame = tk.Frame(root, pady=10)
        bottom_frame.pack(fill='x')

        tk.Label(bottom_frame, text="Total Amount:").pack(side='left', padx=10)
        self.total_amount_var = tk.StringVar(value="0.00")
        tk.Label(bottom_frame, textvariable=self.total_amount_var, font=('Arial', 12, 'bold')).pack(side='left')

        tk.Button(bottom_frame, text="Clear All", command=self.clear_all).pack(side='right', padx=10)
        tk.Button(bottom_frame, text="Save Memo", command=self.save_memo).pack(side='right')

    def add_item(self):
        try:
            qty = int(self.qty_var.get())
            box = self.box_var.get()
            product = self.product_var.get()
            mrp = float(self.mrp_var.get())
            discount = float(self.discount_var.get())

            if not product:
                messagebox.showerror("Input Error", "Product details cannot be empty.")
                return

            amount = qty * mrp * (1 - discount / 100)
            sno = len(self.tree.get_children()) + 1
            self.tree.insert('', 'end', values=(sno, qty, box, product, f"{mrp:.2f}", f"{discount:.2f}", f"{amount:.2f}"))

            self.update_total_amount()

            # Clear entry fields
            self.qty_var.set('')
            self.box_var.set('')
            self.product_var.set('')
            self.mrp_var.set('')
            self.discount_var.set('')

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for Qty, MRP, and Discount.")

    def update_total_amount(self):
        total = 0.0
        for child in self.tree.get_children():
            amount = float(self.tree.item(child)['values'][6])
            total += amount
        self.total_amount_var.set(f"{total:.2f}")

    def clear_all(self):
        self.seller_entry.delete(0, tk.END)
        self.buyer_entry.delete(0, tk.END)
        self.invoice_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%d-%m-%Y'))

        for child in self.tree.get_children():
            self.tree.delete(child)

        self.total_amount_var.set("0.00")

    def save_memo(self):
        seller = self.seller_entry.get()
        buyer = self.buyer_entry.get()
        invoice = self.invoice_entry.get()
        date = self.date_entry.get()

        if not seller or not buyer or not invoice or not date:
            messagebox.showerror("Missing Info", "Please fill in Seller, Buyer, Invoice number, and Date.")
            return

        try:
            datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            messagebox.showerror("Date Error", "Please enter date in DD-MM-YYYY format.")
            return

        items = []
        for child in self.tree.get_children():
            items.append(self.tree.item(child)['values'])

        if not items:
            messagebox.showerror("No Items", "Add at least one product to save memo.")
            return

        filename = f"CashMemo_{invoice}.txt"
        with open(filename, 'w') as f:
            f.write(f"Seller: {seller}\n")
            f.write(f"Buyer: {buyer}\n")
            f.write(f"Invoice No: {invoice}\n")
            f.write(f"Date: {date}\n")
            f.write("\n")
            f.write(f"{'S.No':<5}{'Qty':<5}{'Box':<10}{'Product Details':<30}{'MRP':<10}{'Discount':<10}{'Amount':<10}\n")
            f.write("-"*85 + "\n")
            for item in items:
                f.write(f"{item[0]:<5}{item[1]:<5}{item[2]:<10}{item[3]:<30}{item[4]:<10}{item[5]:<10}{item[6]:<10}\n")
            f.write("-"*85 + "\n")
            f.write(f"Total Amount: {self.total_amount_var.get()}\n")

        messagebox.showinfo("Saved", f"Cash memo saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CashMemoApp(root)
    root.geometry("950x450")
    root.mainloop()
