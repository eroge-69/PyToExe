
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF

def generate_invoice():
    customer = entry_name.get()
    product = entry_product.get()
    price = entry_price.get()

    if not customer or not product or not price:
        messagebox.showerror("Error", "Sab fields bharna zaroori hai")
        return

    try:
        price = float(price)
    except:
        messagebox.showerror("Error", "Price number mein hona chahiye")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Invoice", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(100, 10, txt=f"Customer: {customer}", ln=True)
    pdf.cell(100, 10, txt=f"Product: {product}", ln=True)
    pdf.cell(100, 10, txt=f"Price: Rs {price:.2f}", ln=True)

    filename = f"{customer}_invoice.pdf"
    pdf.output(filename)
    messagebox.showinfo("Success", f"Invoice saved as {filename}")

root = tk.Tk()
root.title("Simple Invoice Manager")

tk.Label(root, text="Customer Name:").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Product:").grid(row=1, column=0)
entry_product = tk.Entry(root)
entry_product.grid(row=1, column=1)

tk.Label(root, text="Price (Rs):").grid(row=2, column=0)
entry_price = tk.Entry(root)
entry_price.grid(row=2, column=1)

tk.Button(root, text="Generate Invoice", command=generate_invoice).grid(row=3, column=1)

root.mainloop()
