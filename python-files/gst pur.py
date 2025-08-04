import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from fpdf import FPDF
import datetime

# Initialize database
conn = sqlite3.connect("purchase_register.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY,
        invoice_no TEXT,
        date TEXT,
        vendor TEXT,
        gst REAL,
        total REAL,
        payment_type TEXT
    )
''')
conn.commit()

# PDF Export function
def export_to_pdf():
    cursor.execute("SELECT * FROM purchases")
    rows = cursor.fetchall()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Purchase Ledger Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated: {datetime.datetime.now()}", ln=True)

    headers = ["ID", "Invoice", "Date", "Vendor", "GST", "Total", "Type"]
    for h in headers:
        pdf.cell(27, 10, h, border=1)
    pdf.ln()

    for row in rows:
        for item in row:
            pdf.cell(27, 10, str(item), border=1)
        pdf.ln()

    pdf.output("purchase_ledger.pdf")
    messagebox.showinfo("Export", "Ledger exported as 'purchase_ledger.pdf'")

# Add purchase
def add_purchase():
    invoice = invoice_entry.get()
    date = date_entry.get()
    vendor = vendor_entry.get()
    gst = float(gst_entry.get())
    total = float(total_entry.get())
    p_type = payment_type.get()

    cursor.execute("INSERT INTO purchases (invoice_no, date, vendor, gst, total, payment_type) VALUES (?, ?, ?, ?, ?, ?)",
                   (invoice, date, vendor, gst, total, p_type))
    conn.commit()
    messagebox.showinfo("Saved", "Purchase entry saved!")
    load_data()

# Load data to table
def load_data():
    for i in ledger.get_children():
        ledger.delete(i)
    cursor.execute("SELECT * FROM purchases")
    for row in cursor.fetchall():
        ledger.insert("", "end", values=row)

# GUI
root = tk.Tk()
root.title("GST Purchase Register")

tk.Label(root, text="Invoice No").grid(row=0, column=0)
invoice_entry = tk.Entry(root)
invoice_entry.grid(row=0, column=1)

tk.Label(root, text="Date (YYYY-MM-DD)").grid(row=1, column=0)
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=1)

tk.Label(root, text="Vendor").grid(row=2, column=0)
vendor_entry = tk.Entry(root)
vendor_entry.grid(row=2, column=1)

tk.Label(root, text="GST (%)").grid(row=3, column=0)
gst_entry = tk.Entry(root)
gst_entry.grid(row=3, column=1)

tk.Label(root, text="Total").grid(row=4, column=0)
total_entry = tk.Entry(root)
total_entry.grid(row=4, column=1)

tk.Label(root, text="Payment").grid(row=5, column=0)
payment_type = ttk.Combobox(root, values=["Credit", "Debit"])
payment_type.grid(row=5, column=1)

tk.Button(root, text="Add Purchase", command=add_purchase).grid(row=6, column=0, pady=10)
tk.Button(root, text="Export PDF", command=export_to_pdf).grid(row=6, column=1)

# Ledger display
ledger = ttk.Treeview(root, columns=("ID", "Invoice", "Date", "Vendor", "GST", "Total", "Payment"), show='headings')
for col in ledger["columns"]:
    ledger.heading(col, text=col)
ledger.grid(row=7, column=0, columnspan=2)

load_data()
root.mainloop()
