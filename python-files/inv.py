import tkinter as tk
from tkinter import ttk, messagebox

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hardware & Sanitaryware Invoice")
        self.root.configure(bg='#ffe5ec')

        header = tk.Frame(root, bg='#f9c6c9')
        header.pack(fill='x')
        tk.Label(header, text="INVOICE", font=("Arial", 26, "bold"), bg='#f9c6c9', fg='#a4133c').pack(side='left', padx=20)
        tk.Label(header, text="Your Business Name", font=("Brush Script MT", 20, "italic"), bg='#f9c6c9', fg="#f7a072").pack(side='right', padx=20)

        detail_frame = tk.Frame(root, bg='#ffe5ec')
        detail_frame.pack(pady=5, fill='x', padx=15)
        tk.Label(detail_frame, text="Invoice Num:", bg='#ffe5ec', fg='#590d22').grid(row=0, column=0, sticky="w")
        self.invoice_num_entry = tk.Entry(detail_frame, bg='#fff0f3', fg='#370617', borderwidth=2)
        self.invoice_num_entry.grid(row=0, column=1, sticky="w")
        tk.Label(detail_frame, text="Date:", bg='#ffe5ec', fg='#590d22').grid(row=0, column=3, sticky="w", padx=(30,0))
        self.date_entry = tk.Entry(detail_frame, bg='#fff0f3', fg='#370617', borderwidth=2)
        self.date_entry.grid(row=0, column=4, sticky="w")

        info_frame = tk.Frame(root, bg='#ffe5ec')
        info_frame.pack(fill='x', padx=15, pady=(2,10))
        lbstyle = {"bg":'#fcd5ce', "fg":'#370617', "font":("Arial",10,"bold")}
        bstyle = {"bg":'#fff6f0', "fg":'#590d22', "relief":'ridge'}
        tk.Label(info_frame, text="Bill To:", **lbstyle).grid(row=0, column=0, sticky="w")
        self.client_text = tk.Text(info_frame, height=3, width=30, **bstyle)
        self.client_text.grid(row=1, column=0, padx=10, pady=2)
        tk.Label(info_frame, text="Your Company Name:", **lbstyle).grid(row=0, column=2, sticky="w")
        self.company_text = tk.Text(info_frame, height=3, width=30, **bstyle)
        self.company_text.grid(row=1, column=2, padx=10, pady=2)

        style = ttk.Style()
        style.configure("Treeview.Heading", background="#c9184a", foreground="#fff0f3", font=("Arial", 10, "bold"))
        style.configure("Treeview", background="#fff8e1", fieldbackground="#fff8e1", font=("Arial", 10), rowheight=25)

        columns = ("item", "description", "qty", "unit_price", "amount")
        self.tree = ttk.Treeview(root, columns=columns, show='headings', selectmode='browse', style='Treeview')
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120)
        self.tree.pack(padx=15, pady=12, fill='x')

        addf = tk.Frame(root, bg='#ffe5ec')
        addf.pack(pady=5)
        entry_style = {"bg":'#fff8e1', "fg":'#03071e', "borderwidth":2, "relief":'groove'}
        tk.Label(addf, text="Item #:", bg='#ffe5ec').grid(row=0, column=0)
        self.item_entry = tk.Entry(addf, width=8, **entry_style)
        self.item_entry.grid(row=0, column=1)
        tk.Label(addf, text="Description:", bg='#ffe5ec').grid(row=0, column=2)
        self.desc_entry = tk.Entry(addf, width=24, **entry_style)
        self.desc_entry.grid(row=0, column=3)
        tk.Label(addf, text="Qty:", bg='#ffe5ec').grid(row=0, column=4)
        self.qty_entry = tk.Entry(addf, width=8, **entry_style)
        self.qty_entry.grid(row=0, column=5)
        tk.Label(addf, text="Unit Price:", bg='#ffe5ec').grid(row=0, column=6)
        self.unit_price_entry = tk.Entry(addf, width=10, **entry_style)
        self.unit_price_entry.grid(row=0, column=7)
        tk.Button(addf, text="Add Item", command=self.add_item, bg="#c9184a", fg="#fff0f3", font=("Arial", 10, "bold")).grid(row=0, column=8, padx=10)

        botf = tk.Frame(root, bg='#ffe5ec')
        botf.pack(pady=8, fill='x', padx=15)
        payf = tk.LabelFrame(botf, text="Payment Info", bg='#fcd5ce', fg='#590d22')
        payf.pack(side="left", fill='both', expand=True, padx=(0,8))
        self.payment_text = tk.Text(payf, height=6, width=36, bg='#fff0f3', fg='#370617')
        self.payment_text.pack(padx=10, pady=6)

        amountf = tk.LabelFrame(botf, text="Amount Info", bg='#caf0f8', fg='#590d22')
        amountf.pack(side="right", fill='both', expand=True)
        tk.Label(amountf, text="Subtotal:", bg='#caf0f8').grid(row=0, column=0, sticky="w")
        self.subtotal_var = tk.StringVar()
        tk.Entry(amountf, textvariable=self.subtotal_var, state='readonly', width=12, bg='#fff8e1').grid(row=0, column=1)
        tk.Label(amountf, text="Discount:", bg='#caf0f8').grid(row=1, column=0, sticky="w")
        self.discount_entry = tk.Entry(amountf, width=12, bg='#fff8e1')
        self.discount_entry.grid(row=1, column=1)
        tk.Label(amountf, text="Taxes (%):", bg='#caf0f8').grid(row=2, column=0, sticky="w")
        self.taxes_entry = tk.Entry(amountf, width=12, bg='#fff8e1')
        self.taxes_entry.grid(row=2, column=1)
        tk.Label(amountf, text="Total Amount:", bg='#caf0f8', font=("Arial",10,"bold")).grid(row=3, column=0, sticky="w")
        self.total_var = tk.StringVar()
        tk.Entry(amountf, textvariable=self.total_var, state='readonly', width=12, bg='#fff8e1', fg='#c9184a', font=("Arial",10,"bold")).grid(row=3, column=1)
        tk.Button(amountf, text="Calculate Total", command=self.calculate_total, bg="#a7c957", fg="#03071e", font=("Arial", 9, "bold")).grid(row=4, column=0, columnspan=2, pady=5)

        tk.Label(root, text="Notes and Terms:", bg='#ffe5ec', fg='#a4133c', font=('Arial',10,'bold')).pack(anchor='w', padx=20, pady=(4,0))
        self.notes_text = tk.Text(root, height=4, bg='#fff0f3', fg='#370617')
        self.notes_text.pack(fill='x', padx=15, pady=4)
        tk.Label(root, text="Thank You", font=("Brush Script MT", 15, "italic"), bg='#ffe5ec', fg="#a4133c").pack(pady=6)

    def add_item(self):
        try:
            item = self.item_entry.get()
            desc = self.desc_entry.get()
            qty = int(self.qty_entry.get())
            unit_price = float(self.unit_price_entry.get())
            amount = qty * unit_price
            self.tree.insert('', 'end', values=(item, desc, qty, f"{unit_price:.2f}", f"{amount:.2f}"))
            self.clear_entries()
            self.update_subtotal()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid quantity and unit price.")

    def clear_entries(self):
        self.item_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.unit_price_entry.delete(0, tk.END)

    def update_subtotal(self):
        total = 0
        for child in self.tree.get_children():
            amount = float(self.tree.item(child)['values'][4])
            total += amount
        self.subtotal_var.set(f"{total:.2f}")

    def calculate_total(self):
        try:
            subtotal = float(self.subtotal_var.get())
            discount = float(self.discount_entry.get()) if self.discount_entry.get() else 0
            taxes = float(self.taxes_entry.get()) if self.taxes_entry.get() else 0
            total = subtotal - discount + subtotal * taxes / 100
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid discount and taxes.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
