import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from tkinter.filedialog import asksaveasfilename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import json

# Persistent invoice number file
invoice_number_file = "invoice_number.json"

# Load or initialize invoice number
if os.path.exists(invoice_number_file):
    with open(invoice_number_file, "r") as f:
        invoice_data = json.load(f)
        invoice_number = invoice_data.get("last_invoice", 1000) + 1
else:
    invoice_number = 1001

def save_invoice_number():
    with open(invoice_number_file, "w") as f:
        json.dump({"last_invoice": invoice_number}, f)

# Salary Calculator Function
def calculate_salary():
    try:
        basic = float(entry_basic.get())
        hra = float(entry_hra.get())
        other = float(entry_other.get())
        tax = float(entry_tax.get())
        net_salary = basic + hra + other - tax
        label_salary_result.config(text=f"Net Salary: ₹{net_salary:.2f}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")

# GST Calculator Function
def calculate_gst():
    try:
        amount = float(entry_amount.get())
        gst_percent = float(entry_gst.get())
        gst = amount * gst_percent / 100
        total = amount + gst
        label_gst_result.config(text=f"GST: ₹{gst:.2f}, Total: ₹{total:.2f}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")

# EMI Calculator Function
def calculate_emi():
    try:
        principal = float(entry_principal.get())
        rate = float(entry_rate.get()) / 12 / 100
        tenure = int(entry_tenure.get()) * 12
        emi = principal * rate * (1 + rate)**tenure / ((1 + rate)**tenure - 1)
        label_emi_result.config(text=f"Monthly EMI: ₹{emi:.2f}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers.")

# Invoice Generator Function
def generate_invoice():
    global invoice_number
    client = entry_client.get()
    item = entry_item.get()
    price = entry_price.get()
    qty = entry_quantity.get()
    try:
        price = float(price)
        qty = int(qty)
        total = price * qty
        today = datetime.date.today()
        invoice_text = (
            f"Your Company\n"
            f"123 Business Street, Your City\n"
            f"Phone: +91-1234567890\n"
            f"\nInvoice #: INV{invoice_number}\nInvoice Date: {today}\nClient: {client}\n\n"
            f"Item: {item}\nQuantity: {qty}\nPrice per Item: ₹{price:.2f}\n"
            f"------------------------------\nTotal: ₹{total:.2f}\n\nThank you for your business!"
        )
        text_invoice.delete("1.0", tk.END)
        text_invoice.insert(tk.END, invoice_text)
        save_invoice_number()
        invoice_number += 1
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for price and quantity.")

# Save Invoice to Text and PDF File
def save_invoice():
    file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")])
    if file_path:
        invoice_content = text_invoice.get("1.0", tk.END)
        try:
            if file_path.endswith(".txt"):
                with open(file_path, 'w') as f:
                    f.write(invoice_content)
                messagebox.showinfo("Success", "Invoice saved as text successfully!")
            elif file_path.endswith(".pdf"):
                c = canvas.Canvas(file_path, pagesize=A4)
                lines = invoice_content.strip().split('\n')
                y = 800
                for line in lines:
                    c.drawString(50, y, line)
                    y -= 20
                c.save()
                messagebox.showinfo("Success", "Invoice saved as PDF successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

# Main Window
root = tk.Tk()
root.title("Multi Calculator App")
root.geometry("500x500")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Salary Tab
frame_salary = ttk.Frame(notebook)
notebook.add(frame_salary, text='Salary')

tk.Label(frame_salary, text="Basic Salary").pack()
entry_basic = tk.Entry(frame_salary)
entry_basic.pack()

tk.Label(frame_salary, text="HRA").pack()
entry_hra = tk.Entry(frame_salary)
entry_hra.pack()

tk.Label(frame_salary, text="Other Allowance").pack()
entry_other = tk.Entry(frame_salary)
entry_other.pack()

tk.Label(frame_salary, text="Tax Deduction").pack()
entry_tax = tk.Entry(frame_salary)
entry_tax.pack()

tk.Button(frame_salary, text="Calculate Salary", command=calculate_salary).pack(pady=10)
label_salary_result = tk.Label(frame_salary, text="Net Salary: ₹0.00")
label_salary_result.pack()

# GST Tab
frame_gst = ttk.Frame(notebook)
notebook.add(frame_gst, text='GST')

tk.Label(frame_gst, text="Amount").pack()
entry_amount = tk.Entry(frame_gst)
entry_amount.pack()

tk.Label(frame_gst, text="GST %").pack()
entry_gst = tk.Entry(frame_gst)
entry_gst.pack()

tk.Button(frame_gst, text="Calculate GST", command=calculate_gst).pack(pady=10)
label_gst_result = tk.Label(frame_gst, text="GST: ₹0.00, Total: ₹0.00")
label_gst_result.pack()

# EMI Tab
frame_emi = ttk.Frame(notebook)
notebook.add(frame_emi, text='EMI')

tk.Label(frame_emi, text="Loan Amount").pack()
entry_principal = tk.Entry(frame_emi)
entry_principal.pack()

tk.Label(frame_emi, text="Annual Interest Rate (%)").pack()
entry_rate = tk.Entry(frame_emi)
entry_rate.pack()

tk.Label(frame_emi, text="Tenure (Years)").pack()
entry_tenure = tk.Entry(frame_emi)
entry_tenure.pack()

tk.Button(frame_emi, text="Calculate EMI", command=calculate_emi).pack(pady=10)
label_emi_result = tk.Label(frame_emi, text="Monthly EMI: ₹0.00")
label_emi_result.pack()

# Invoice Tab
frame_invoice = ttk.Frame(notebook)
notebook.add(frame_invoice, text='Invoice')

tk.Label(frame_invoice, text="Client Name").pack()
entry_client = tk.Entry(frame_invoice)
entry_client.pack()

tk.Label(frame_invoice, text="Item").pack()
entry_item = tk.Entry(frame_invoice)
entry_item.pack()

tk.Label(frame_invoice, text="Price per Item").pack()
entry_price = tk.Entry(frame_invoice)
entry_price.pack()

tk.Label(frame_invoice, text="Quantity").pack()
entry_quantity = tk.Entry(frame_invoice)
entry_quantity.pack()

tk.Button(frame_invoice, text="Generate Invoice", command=generate_invoice).pack(pady=5)
text_invoice = tk.Text(frame_invoice, height=10, width=50)
text_invoice.pack()
tk.Button(frame_invoice, text="Save as File", command=save_invoice).pack(pady=5)

root.mainloop()
