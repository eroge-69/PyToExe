
# invoice_app.py
import tkinter as tk
from tkinter import messagebox
from fpdf_invoice import generate_invoice_pdf

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Billing Software")
        self.items = []

        # Company and Customer Info
        tk.Label(root, text="Company Name:").grid(row=0, column=0, padx=5, pady=5)
        self.company_entry = tk.Entry(root, width=40)
        self.company_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Customer Name:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_entry = tk.Entry(root, width=40)
        self.customer_entry.grid(row=1, column=1, padx=5, pady=5)

        # Item Entry
        tk.Label(root, text="Item Name:").grid(row=3, column=0, padx=5, pady=5)
        self.item_entry = tk.Entry(root)
        self.item_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(root, text="Quantity:").grid(row=4, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(root)
        self.quantity_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(root, text="Price:").grid(row=5, column=0, padx=5, pady=5)
        self.price_entry = tk.Entry(root)
        self.price_entry.grid(row=5, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(root, text="Add Item", command=self.add_item).grid(row=6, column=1, pady=10)
        tk.Button(root, text="Generate Invoice PDF", command=self.generate_invoice).grid(row=7, column=1, pady=10)

        # Item Display
        self.items_display = tk.Text(root, width=60, height=10)
        self.items_display.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def add_item(self):
        name = self.item_entry.get()
        try:
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid quantity and price.")
            return

        if name:
            self.items.append({"name": name, "quantity": quantity, "price": price})
            self.items_display.insert(tk.END, f"{name} - Qty: {quantity}, Price: {price}\n")
            self.item_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Missing item", "Item name is required.")

    def generate_invoice(self):
        company = self.company_entry.get()
        customer = self.customer_entry.get()
        if not company or not customer or not self.items:
            messagebox.showerror("Missing Info", "Company, customer name and at least one item are required.")
            return

        try:
            generate_invoice_pdf(company, customer, self.items, output_path="Invoice_Output.pdf")
            messagebox.showinfo("Success", "Invoice PDF generated successfully as Invoice_Output.pdf")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
