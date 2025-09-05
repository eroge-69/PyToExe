import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fpdf import FPDF
import os

# Initialize main window
root = tk.Tk()
root.title("POS System - APEX ELECTRONICS")
root.geometry("1000x700")

# Global list to store products
products = []

# --- Functions ---
def add_product():
    item_code = entry_item_code.get().strip()
    item_name = entry_item_name.get().strip()
    try:
        qty = int(entry_qty.get())
        price = float(entry_price.get())
        discount = float(entry_discount.get() or 0.0)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for Qty, Price, and Discount.")
        return

    if not item_code or not item_name or qty <= 0 or price < 0:
        messagebox.showerror("Input Error", "Please fill all fields correctly.")
        return

    total = (price * qty) - (discount * qty)
    products.append({
        "no": len(products) + 1,
        "item_code": item_code,
        "item_name": item_name,
        "qty": qty,
        "price": price,
        "discount": discount,
        "total": total
    })

    # Add to table
    tree.insert("", "end", values=(
        len(products),
        item_code,
        item_name,
        qty,
        f"{price:.2f}",
        f"{discount:.2f}",
        f"{total:.2f}"
    ))

    # Clear inputs
    entry_item_code.delete(0, tk.END)
    entry_item_name.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_discount.delete(0, tk.END)
    entry_qty.insert(0, "1")
    entry_discount.insert(0, "0.00")

def print_invoice():
    if not products:
        messagebox.showwarning("No Products", "Please add at least one product.")
        return

    update_preview()
    os.startfile(f"Invoice_{invoice_no.get()}_{current_date.get().replace('-', '')}.pdf", "print")

def save_pdf():
    if not products:
        messagebox.showwarning("No Products", "Please add at least one product.")
        return

    update_preview()  # Refresh totals
    generate_pdf()

def update_preview():
    # Update header
    label_inv_no_val.config(text=invoice_no.get())
    label_date_val.config(text=current_date.get())
    label_customer_val.config(text=customer_name.get())

    # Clear previous items
    for item in preview_tree.get_children():
        preview_tree.delete(item)

    # Insert products
    total_amount = 0
    total_discount = 0
    for p in products:
        preview_tree.insert("", "end", values=(
            p["no"],
            p["item_code"],
            p["item_name"],
            p["qty"],
            f"{p['price']:.2f}",
            f"{p['discount']:.2f}",
            f"{p['total']:.2f}"
        ))
        total_amount += p["total"]
        total_discount += p["discount"] * p["qty"]

    # Update totals
    label_item_count_val.config(text=str(len(products)))
    label_total_amount_val.config(text=f"Rs {total_amount:.2f}")
    label_total_discount_val.config(text=f"Rs {total_discount:.2f}")
    label_net_amount_val.config(text=f"Rs {total_amount:.2f}")
    label_grand_total_val.config(text=f"Rs {total_amount:.2f}")

    # Set print time
    label_print_time_val.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Set font
    pdf.set_font("Courier", size=12)

    # Logo (if you have one in same folder)
    try:
        pdf.image("1234.jpg", x=10, y=8, w=30)
    except Exception:
        pass  # Ignore if image not found

    pdf.set_x(45)
    pdf.set_font("Courier", 'B', 16)
    pdf.cell(0, 10, "APEX HYDRAULIC HOSE & CABLE", ln=True)
    pdf.set_x(45)
    pdf.set_font("Courier", size=12)
    pdf.cell(0, 8, "Power steering, Oil Hose, Hand Brake, Speed Meter, Accalerator Cables", ln=True)
    pdf.set_x(45)
    pdf.cell(0, 8, "Ginigathena Road Meepitiya Nawalapitiya.", ln=True)
    pdf.set_x(45)
    pdf.cell(0, 8, "0775192882 / 0705192882 / 0725192882", ln=True)
    pdf.ln(5)

    # Title
    pdf.set_font("Courier", 'B', 16)
    pdf.cell(0, 10, "INVOICE", align='C', ln=True)
    pdf.ln(5)

    # Invoice details
    pdf.set_font("Courier", size=12)
    pdf.cell(60, 8, f"Invoice No : {invoice_no.get()}")
    pdf.cell(0, 8, f"Date : {current_date.get()}", ln=True)
    pdf.cell(60, 8, f"Customer : {customer_name.get()}")
    pdf.ln(10)

    # Table Header
    col_widths = [10, 30, 60, 15, 25, 15, 25]
    headers = ["No.", "Item Code", "Item Name", "Qty", "Price", "Dis", "Total"]
    pdf.set_font("Courier", 'B', 12)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, h, border=1, align='C')
    pdf.ln(10)

    # Table Rows
    pdf.set_font("Courier", size=12)
    total_amount = 0
    for p in products:
        pdf.cell(col_widths[0], 10, str(p["no"]), border=1, align='C')
        pdf.cell(col_widths[1], 10, p["item_code"], border=1)
        pdf.cell(col_widths[2], 10, p["item_name"], border=1)
        pdf.cell(col_widths[3], 10, str(p["qty"]), border=1, align='C')
        pdf.cell(col_widths[4], 10, f"{p['price']:.2f}", border=1, align='C')
        pdf.cell(col_widths[5], 10, f"{p['discount']:.2f}", border=1, align='C')
        pdf.cell(col_widths[6], 10, f"{p['total']:.2f}", border=1, align='R')
        pdf.ln(10)
        total_amount += p["total"]

    pdf.ln(10)

    # Totals
    pdf.set_font("Courier", 'B', 13)
    pdf.cell(0, 10, f"{'No of Items:':<20}{len(products):>5}", ln=True)
    pdf.cell(0, 10, f"{'Total Amount:':<20}{'Rs ' + f'{total_amount:.2f}':>15}", ln=True)
    pdf.cell(0, 10, f"{'Total Discount:':<20}{'Rs ' + f'{sum(p['discount']*p['qty'] for p in products):.2f}':>15}", ln=True)
    pdf.cell(0, 10, f"{'Net Amount:':<20}{'Rs ' + f'{total_amount:.2f}':>15}", ln=True)
    pdf.cell(0, 10, f"{'Grand Total:':<20}{'Rs ' + f'{total_amount:.2f}':>15}", ln=True)
    pdf.ln(15)

    # Print time
    pdf.set_font("Courier", size=10)
    pdf.cell(0, 8, f"Print time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Signatures
    pdf.cell(90, 10, "*Cashier By:", align='C')
    pdf.cell(90, 10, "*Manager By:", align='C', ln=True)
    pdf.ln(20)

    # Save PDF
    filename = f"Invoice_{invoice_no.get()}_{current_date.get().replace('-', '')}.pdf"
    pdf.output(filename)
    messagebox.showinfo("PDF Saved", f"Invoice saved as:\n{filename}")

# --- GUI Layout ---
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left Panel (POS Input)
left_frame = ttk.LabelFrame(main_frame, text="Invoice Info", width=400)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
left_frame.pack_propagate(False)

ttk.Label(left_frame, text="Customer:").pack(anchor=tk.W, pady=2)
customer_name = tk.StringVar(value="APEX WASANTHA (A)")
ttk.Entry(left_frame, textvariable=customer_name).pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Invoice No:").pack(anchor=tk.W, pady=2)
invoice_no = tk.StringVar(value="1755")
ttk.Entry(left_frame, textvariable=invoice_no).pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Date:").pack(anchor=tk.W, pady=2)
current_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
ttk.Entry(left_frame, textvariable=current_date).pack(fill=tk.X, pady=2)

ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)

ttk.Label(left_frame, text="Add Product", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))

ttk.Label(left_frame, text="Item Code:").pack(anchor=tk.W, pady=2)
entry_item_code = ttk.Entry(left_frame)
entry_item_code.pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Item Name:").pack(anchor=tk.W, pady=2)
entry_item_name = ttk.Entry(left_frame)
entry_item_name.pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Qty:").pack(anchor=tk.W, pady=2)
entry_qty = ttk.Entry(left_frame)
entry_qty.insert(0, "1")
entry_qty.pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Price:").pack(anchor=tk.W, pady=2)
entry_price = ttk.Entry(left_frame)
entry_price.pack(fill=tk.X, pady=2)

ttk.Label(left_frame, text="Discount:").pack(anchor=tk.W, pady=2)
entry_discount = ttk.Entry(left_frame)
entry_discount.insert(0, "0.00")
entry_discount.pack(fill=tk.X, pady=2)

ttk.Button(left_frame, text="Add Product", command=add_product).pack(pady=5, fill=tk.X)

ttk.Label(left_frame, text="Products", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))

# Product Table (POS)
columns = ("No.", "Item Code", "Item Name", "Qty", "Price", "Dis", "Total")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=50 if col == "No." else 80)
tree.pack(fill=tk.BOTH, expand=True, pady=5)

ttk.Button(left_frame, text="🖨️ Print Invoice", command=print_invoice).pack(pady=5, fill=tk.X)
ttk.Button(left_frame, text="📥 Save PDF", command=save_pdf).pack(pady=5, fill=tk.X)

# Right Panel (Invoice Preview)
right_frame = ttk.LabelFrame(main_frame, text="Invoice Preview")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Use Treeview and Labels to simulate invoice
preview_frame = tk.Frame(right_frame)
preview_frame.pack(padx=10, pady=10)

tk.Label(preview_frame, text="APEX HYDRAULIC HOSE & CABLE", font=("Courier", 16, "bold")).grid(row=0, column=0, columnspan=2)
tk.Label(preview_frame, text="Power steering, Oil Hose, Hand Brake, Speed Meter, Accalerator Cables").grid(row=1, column=0, columnspan=2)
tk.Label(preview_frame, text="Ginigathena Road Meepitiya Nawalapitiya.").grid(row=2, column=0, columnspan=2)
tk.Label(preview_frame, text="0775192882 / 0705192882 / 0725192882").grid(row=3, column=0, columnspan=2)

tk.Label(preview_frame, text="INVOICE", font=("Courier", 16, "bold"), pady=10).grid(row=4, column=0, columnspan=2)

# Invoice Details
tk.Label(preview_frame, text="Invoice No :").grid(row=5, column=0, sticky=tk.W)
label_inv_no_val = tk.Label(preview_frame, text="1755", font=("Courier", 10, "bold"))
label_inv_no_val.grid(row=5, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Customer :").grid(row=6, column=0, sticky=tk.W)
label_customer_val = tk.Label(preview_frame, text="APEX WASANTHA (A)")
label_customer_val.grid(row=6, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Date :").grid(row=7, column=0, sticky=tk.W)
label_date_val = tk.Label(preview_frame, text="2025-08-22")
label_date_val.grid(row=7, column=1, sticky=tk.W)

# Product Table Preview
preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=8)
for col in columns:
    preview_tree.heading(col, text=col)
    preview_tree.column(col, width=50 if col == "No." else 80)
preview_tree.grid(row=8, column=0, columnspan=2, pady=10)

# Totals
tk.Label(preview_frame, text="No of Items:").grid(row=9, column=0, sticky=tk.W)
label_item_count_val = tk.Label(preview_frame, text="0")
label_item_count_val.grid(row=9, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Print time:").grid(row=10, column=0, sticky=tk.W)
label_print_time_val = tk.Label(preview_frame, text="--/--/-- --:--:--")
label_print_time_val.grid(row=10, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Total Amount:", font=("bold")).grid(row=11, column=0, sticky=tk.W)
label_total_amount_val = tk.Label(preview_frame, text="Rs 0.00", font=("bold"))
label_total_amount_val.grid(row=11, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Total Discount:", font=("bold")).grid(row=12, column=0, sticky=tk.W)
label_total_discount_val = tk.Label(preview_frame, text="Rs 0.00", font=("bold"))
label_total_discount_val.grid(row=12, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Net Amount:", font=("bold")).grid(row=13, column=0, sticky=tk.W)
label_net_amount_val = tk.Label(preview_frame, text="Rs 0.00", font=("bold"))
label_net_amount_val.grid(row=13, column=1, sticky=tk.W)

tk.Label(preview_frame, text="Grand Total:", font=("bold")).grid(row=14, column=0, sticky=tk.W)
label_grand_total_val = tk.Label(preview_frame, text="Rs 0.00", font=("bold"))
label_grand_total_val.grid(row=14, column=1, sticky=tk.W)

# Signatures
tk.Label(preview_frame, text="*Cashier By:", font=("bold")).grid(row=15, column=0, pady=30)
tk.Label(preview_frame, text="*Manager By:", font=("bold")).grid(row=15, column=1, pady=30)

# Run the app
root.mainloop()