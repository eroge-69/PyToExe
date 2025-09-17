import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marhaba Jewellery - Invoice Generator (Nellimattom)")
        self.items = []

        # Customer info
        tk.Label(root, text="Customer Name").grid(row=0, column=0, padx=5, pady=5)
        self.customer_name = tk.Entry(root)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)

        # Item input
        tk.Label(root, text="Item").grid(row=1, column=0)
        self.item_name = tk.Entry(root)
        self.item_name.grid(row=1, column=1)

        tk.Label(root, text="Weight (g)").grid(row=1, column=2)
        self.weight = tk.Entry(root)
        self.weight.grid(row=1, column=3)

        tk.Label(root, text="Price/g").grid(row=1, column=4)
        self.price_per_g = tk.Entry(root)
        self.price_per_g.grid(row=1, column=5)

        ttk.Button(root, text="Add Item", command=self.add_item).grid(row=1, column=6, padx=5)

        # Invoice Table
        self.tree = ttk.Treeview(root, columns=("Item", "Weight", "Price/g", "Total"), show="headings")
        for col in ("Item", "Weight", "Price/g", "Total"):
            self.tree.heading(col, text=col)
        self.tree.grid(row=2, column=0, columnspan=7, pady=10)

        # VA/MC
        tk.Label(root, text="VA/MC %").grid(row=3, column=0)
        self.commission = tk.Entry(root)
        self.commission.insert(0, "5")  # default 5%
        self.commission.grid(row=3, column=1)

        # Tax
        tk.Label(root, text="Tax %").grid(row=3, column=2)
        self.tax = tk.Entry(root)
        self.tax.insert(0, "3")  # default GST 3%
        self.tax.grid(row=3, column=3)

        ttk.Button(root, text="Generate Invoice", command=self.generate_invoice).grid(row=3, column=4)

        self.total_label = tk.Label(root, text="Grand Total: ₹0")
        self.total_label.grid(row=3, column=5, columnspan=2)

    def add_item(self):
        try:
            item = self.item_name.get()
            weight = float(self.weight.get())
            price = float(self.price_per_g.get())
            total = weight * price
            self.items.append((item, weight, price, total))
            self.tree.insert("", "end", values=(item, weight, price, total))
            self.item_name.delete(0, tk.END)
            self.weight.delete(0, tk.END)
            self.price_per_g.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def generate_invoice(self):
        subtotal = sum(i[3] for i in self.items)

        try:
            commission_rate = float(self.commission.get())
        except ValueError:
            commission_rate = 0
        commission_amount = subtotal * commission_rate / 100
        subtotal_with_commission = subtotal + commission_amount

        try:
            tax_rate = float(self.tax.get())
        except ValueError:
            tax_rate = 0
        tax_amount = subtotal_with_commission * tax_rate / 100

        grand_total = subtotal_with_commission + tax_amount

        self.total_label.config(text=f"Grand Total: ₹{grand_total:.2f}")

        # Save invoice to file
        filename = f"invoice_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write("Marhaba Jewellery - Nellimattom\n")
            f.write(f"Customer: {self.customer_name.get()}\n\n")
            f.write("Items:\n")
            for i in self.items:
                f.write(f"{i[0]} - {i[1]}g x {i[2]}/g = ₹{i[3]:.2f}\n")
            f.write(f"\nSubtotal: ₹{subtotal:.2f}")
            f.write(f"\nVA/MC {commission_rate}%: ₹{commission_amount:.2f}")
            f.write(f"\nSubtotal + VA/MC: ₹{subtotal_with_commission:.2f}")
            f.write(f"\nTax {tax_rate}%: ₹{tax_amount:.2f}")
            f.write(f"\nGrand Total: ₹{grand_total:.2f}")
        messagebox.showinfo("Invoice Saved", f"Invoice saved as {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
