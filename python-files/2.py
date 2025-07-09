import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import tempfile
import os

# ----------------- Database -----------------
conn = sqlite3.connect("pharmacy.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS medicine (
    drug_code TEXT PRIMARY KEY,
    drug_name TEXT,
    generic_name TEXT,
    hsn_code TEXT,
    packing TEXT,
    manufacturing_name TEXT,
    gst REAL,
    schedule_list TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS vendor (
    vendor_code TEXT PRIMARY KEY,
    vendor_name TEXT,
    vendor_address TEXT,
    vendor_gst TEXT,
    vendor_drug_no TEXT,
    credit_days INTEGER,
    phone_no TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS sales_bill (
    bill_no INTEGER,
    vendor_code TEXT,
    customer_name TEXT,
    customer_address TEXT,
    gst_no TEXT,
    drug_license_no TEXT,
    bill_date TEXT,
    due_date TEXT,
    medicine_name TEXT,
    qty INTEGER,
    purchase_rate REAL,
    gst REAL,
    mrp REAL,
    discount REAL,
    total REAL
)
''')

conn.commit()

# ----------------- Master -----------------
def open_master():
    m = tk.Toplevel(root)
    m.title("Master")
    for txt, cmd in [
        ("Add Medicine", add_medicine),
        ("Edit Medicine", edit_medicine),
        ("Delete Medicine", delete_medicine),
        ("Add Vendor", add_vendor),
        ("Edit Vendor", edit_vendor),
        ("Delete Vendor", delete_vendor)
    ]:
        tk.Button(m, text=txt, width=30, command=cmd).pack(pady=5)

def add_medicine():
    win = tk.Toplevel(root)
    win.title("Add Medicine")
    fields = ["Drug Code", "Drug Name", "Generic Name", "HSN Code", "Packing",
              "Manufacturing Name", "GST", "Schedule List"]
    entries = {}
    for f in fields:
        tk.Label(win, text=f).pack()
        e = tk.Entry(win)
        e.pack()
        entries[f] = e

    def save():
        vals = [entries[f].get() for f in fields]
        try:
            c.execute("INSERT INTO medicine VALUES (?,?,?,?,?,?,?,?)", vals)
            conn.commit()
            messagebox.showinfo("Success", "Medicine Saved")
            win.destroy()
        except:
            messagebox.showerror("Error", "Drug Code must be unique!")

    tk.Button(win, text="Save", command=save).pack(pady=10)

def edit_medicine():
    win = tk.Toplevel(root)
    win.title("Edit Medicine")
    tk.Label(win, text="Drug Code:").pack()
    code = tk.Entry(win)
    code.pack()

    def search():
        c.execute("SELECT * FROM medicine WHERE drug_code=?", (code.get(),))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error", "Not found")
            return

        fields = ["Drug Name", "Generic Name", "HSN Code", "Packing",
                  "Manufacturing Name", "GST", "Schedule List"]
        entries = {}
        for i, f in enumerate(fields, start=1):
            tk.Label(win, text=f).pack()
            e = tk.Entry(win)
            e.insert(0, row[i])
            e.pack()
            entries[f] = e

        def save():
            vals = [entries[f].get() for f in fields]
            c.execute('''
                UPDATE medicine SET drug_name=?, generic_name=?, hsn_code=?, packing=?,
                manufacturing_name=?, gst=?, schedule_list=? WHERE drug_code=?
            ''', (*vals, code.get()))
            conn.commit()
            messagebox.showinfo("Updated", "Medicine Updated")
            win.destroy()

        tk.Button(win, text="Save Changes", command=save).pack(pady=5)

    tk.Button(win, text="Search", command=search).pack(pady=5)

def delete_medicine():
    win = tk.Toplevel(root)
    win.title("Delete Medicine")
    tk.Label(win, text="Drug Code:").pack()
    code = tk.Entry(win)
    code.pack()

    def delete():
        c.execute("DELETE FROM medicine WHERE drug_code=?", (code.get(),))
        conn.commit()
        messagebox.showinfo("Deleted", "Medicine Deleted")
        win.destroy()

    tk.Button(win, text="Delete", command=delete).pack(pady=5)

def add_vendor():
    win = tk.Toplevel(root)
    win.title("Add Vendor")
    fields = ["Vendor Code", "Vendor Name", "Vendor Address",
              "Vendor GST No", "Vendor Drug No", "Credit Allowed Days", "Phone No"]
    entries = {}
    for f in fields:
        tk.Label(win, text=f).pack()
        e = tk.Entry(win)
        e.pack()
        entries[f] = e

    def save():
        vals = [entries[f].get() for f in fields]
        c.execute("INSERT INTO vendor VALUES (?,?,?,?,?,?,?)", vals)
        conn.commit()
        messagebox.showinfo("Success", "Vendor Saved")
        win.destroy()

    tk.Button(win, text="Save", command=save).pack(pady=10)

def edit_vendor():
    win = tk.Toplevel(root)
    win.title("Edit Vendor")
    tk.Label(win, text="Vendor Code:").pack()
    code = tk.Entry(win)
    code.pack()

    def search():
        c.execute("SELECT * FROM vendor WHERE vendor_code=?", (code.get(),))
        row = c.fetchone()
        if not row:
            messagebox.showerror("Error", "Not found")
            return

        fields = ["Vendor Name", "Vendor Address", "Vendor GST No",
                  "Vendor Drug No", "Credit Allowed Days", "Phone No"]
        entries = {}
        for i, f in enumerate(fields, start=1):
            tk.Label(win, text=f).pack()
            e = tk.Entry(win)
            e.insert(0, row[i])
            e.pack()
            entries[f] = e

        def save():
            vals = [entries[f].get() for f in fields]
            c.execute('''
                UPDATE vendor SET vendor_name=?, vendor_address=?, vendor_gst=?,
                vendor_drug_no=?, credit_days=?, phone_no=? WHERE vendor_code=?
            ''', (*vals, code.get()))
            conn.commit()
            messagebox.showinfo("Updated", "Vendor Updated")
            win.destroy()

        tk.Button(win, text="Save Changes", command=save).pack(pady=5)

    tk.Button(win, text="Search", command=search).pack(pady=5)

def delete_vendor():
    win = tk.Toplevel(root)
    win.title("Delete Vendor")
    tk.Label(win, text="Vendor Code:").pack()
    code = tk.Entry(win)
    code.pack()

    def delete():
        c.execute("DELETE FROM vendor WHERE vendor_code=?", (code.get(),))
        conn.commit()
        messagebox.showinfo("Deleted", "Vendor Deleted")
        win.destroy()

    tk.Button(win, text="Delete", command=delete).pack(pady=5)

# ----------------- Billing -----------------
def open_billing():   # <-- new one here
    b = tk.Toplevel(root)
    b.title("Billing")
    tk.Button(b, text="New Sales Bill", width=30, command=new_sales_bill).pack(pady=5)
    tk.Button(b, text="View Sales Bill", width=30, command=view_sales_bill).pack(pady=5)
    tk.Button(b, text="Return Sales Bill", width=30, command=return_sales_bill).pack(pady=5)
    tk.Button(b, text="New Inventory Entry", command=new_inventory_entry).pack(pady=5)

def new_sales_bill():
    win = tk.Toplevel(root)
    win.title("New Sales Bill")

    c.execute("SELECT vendor_code, vendor_name FROM vendor")
    vendors = c.fetchall()

    tk.Label(win, text="Customer:").pack()
    vendor_var = tk.StringVar()
    vendor_combo = ttk.Combobox(win, textvariable=vendor_var, values=[f"{v[0]} - {v[1]}" for v in vendors])
    vendor_combo.pack()

    address_var = tk.StringVar()
    gst_var = tk.StringVar()
    drug_var = tk.StringVar()
    due_date_var = tk.StringVar()

    tk.Label(win, text="Address:").pack()
    tk.Entry(win, textvariable=address_var).pack()

    tk.Label(win, text="GST No:").pack()
    tk.Entry(win, textvariable=gst_var).pack()

    tk.Label(win, text="Drug License No:").pack()
    tk.Entry(win, textvariable=drug_var).pack()

    tk.Label(win, text="Due Date:").pack()
    tk.Entry(win, textvariable=due_date_var).pack()

    def fill_vendor(event):
        if vendor_var.get():
            code = vendor_var.get().split(' - ')[0]
            c.execute("SELECT * FROM vendor WHERE vendor_code=?", (code,))
            row = c.fetchone()
            if row:
                address_var.set(row[2])
                gst_var.set(row[3])
                drug_var.set(row[4])
                due_date = datetime.date.today() + datetime.timedelta(days=row[5])
                due_date_var.set(str(due_date))

    vendor_combo.bind("<<ComboboxSelected>>", fill_vendor)

    tree = ttk.Treeview(win, columns=("Medicine", "Qty", "Rate", "GST", "MRP", "Discount", "Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=90)
    tree.pack()

    f = tk.Frame(win)
    f.pack()
    med = tk.Entry(f, width=15)
    qty = tk.Entry(f, width=5)
    rate = tk.Entry(f, width=8)
    gst = tk.Entry(f, width=5)
    mrp = tk.Entry(f, width=8)
    disc = tk.Entry(f, width=8)
    med.grid(row=0, column=0)
    qty.grid(row=0, column=1)
    rate.grid(row=0, column=2)
    gst.grid(row=0, column=3)
    mrp.grid(row=0, column=4)
    disc.grid(row=0, column=5)

    def add_item():
        try:
            q = int(qty.get())
            r = float(rate.get())
            d = float(disc.get())
            t = (q * r) - d
            tree.insert("", "end", values=(med.get(), q, r, gst.get(), mrp.get(), d, t))
            med.delete(0, 'end')
            qty.delete(0, 'end')
            rate.delete(0, 'end')
            gst.delete(0, 'end')
            mrp.delete(0, 'end')
            disc.delete(0, 'end')
        except:
            messagebox.showerror("Error", "Check item fields")

    tk.Button(f, text="Add Item", command=add_item).grid(row=0, column=6, padx=5)

    def save_bill():
        if not tree.get_children():
            messagebox.showerror("Error", "No items added")
            return
        code = vendor_var.get().split(' - ')[0]
        name = vendor_var.get().split(' - ')[1]
        today = datetime.date.today()
        for i in tree.get_children():
            vals = tree.item(i)['values']
            c.execute('''
                INSERT INTO sales_bill (
                    bill_no, vendor_code, customer_name, customer_address, gst_no, drug_license_no,
                    bill_date, due_date, medicine_name, qty, purchase_rate, gst, mrp, discount, total
                )
                VALUES (
                    (SELECT IFNULL(MAX(bill_no), 0) + 1 FROM sales_bill),
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            ''', (
                code, name, address_var.get(), gst_var.get(), drug_var.get(),
                today, due_date_var.get(), vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6]
            ))
        conn.commit()
        messagebox.showinfo("Done", "Bill Saved")
        win.destroy()

    tk.Button(win, text="Save Bill", command=save_bill).pack(pady=10)

def view_sales_bill():
    win = tk.Toplevel(root)
    win.title("View Sales Bills")
    tree = ttk.Treeview(win, columns=("Bill No","Customer","Medicine","Qty","Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("SELECT DISTINCT bill_no, customer_name FROM sales_bill")
    bills = c.fetchall()
    for b in bills:
        c.execute("SELECT medicine_name, qty, total FROM sales_bill WHERE bill_no=?", (b[0],))
        rows = c.fetchall()
        for r in rows:
            tree.insert("", "end", values=(b[0], b[1], r[0], r[1], r[2]))

    def show_preview(event):
        selected = tree.item(tree.selection())['values']
        if not selected: return
        bno = selected[0]
        c.execute("SELECT * FROM sales_bill WHERE bill_no=?", (bno,))
        rows = c.fetchall()
        text = f"--- Sales Bill No: {bno} ---\n\n"
        for row in rows:
            text += f"{row[8]} - Qty: {row[9]}, Total: {row[14]}\n"
        text += "\nThank you!"

        prev = tk.Toplevel(win)
        prev.title(f"Print Preview - Bill {bno}")
        txt = tk.Text(prev, width=50, height=20)
        txt.insert('1.0', text)
        txt.pack()

        def print_bill():
            filename = tempfile.mktemp(".txt")
            with open(filename, "w") as f:
                f.write(txt.get("1.0", 'end'))
            os.startfile(filename, "print")

        tk.Button(prev, text="Print", command=print_bill).pack()

    tree.bind("<Double-1>", show_preview)

def return_sales_bill():
    win = tk.Toplevel(root)
    win.title("Return Sales Bill")
    tk.Label(win, text="Enter Bill No to Return:").pack()
    bno = tk.Entry(win)
    bno.pack()

    def ret():
        c.execute("DELETE FROM sales_bill WHERE bill_no=?", (bno.get(),))
        conn.commit()
        messagebox.showinfo("Done", "Bill Returned")
        win.destroy()

    tk.Button(win, text="Return Bill", command=ret).pack(pady=10)

# ----------------- Sales Reports -----------------
def open_sales_reports():
    sr = tk.Toplevel(root)
    sr.title("Sales Reports")

    tk.Button(sr, text="Vendor-wise Sales Report", width=30, command=vendor_sales_report).pack(pady=5)
    tk.Button(sr, text="Daily Sales Report", width=30, command=daily_sales_report).pack(pady=5)
    tk.Button(sr, text="Credit Sales Report", width=30, command=credit_sales_report).pack(pady=5)

def vendor_sales_report():
    win = tk.Toplevel(root)
    win.title("Vendor-wise Sales Report")

    tree = ttk.Treeview(win, columns=("Vendor", "Total Sales"), show="headings")
    tree.heading("Vendor", text="Vendor")
    tree.heading("Total Sales", text="Total Sales")
    tree.pack(fill="both", expand=True)

    c.execute('''
        SELECT customer_name, SUM(total) FROM sales_bill
        GROUP BY customer_name
    ''')
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def export():
        with open("vendor_sales_report.csv", "w") as f:
            f.write("Vendor,Total Sales\n")
            for row in tree.get_children():
                vals = tree.item(row)["values"]
                f.write(f"{vals[0]},{vals[1]}\n")
        messagebox.showinfo("Exported", "Saved to vendor_sales_report.csv")

    tk.Button(win, text="Export CSV", command=export).pack(pady=10)

def daily_sales_report():
    win = tk.Toplevel(root)
    win.title("Daily Sales Report")

    tree = ttk.Treeview(win, columns=("Date", "Total Sales"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Total Sales", text="Total Sales")
    tree.pack(fill="both", expand=True)

    c.execute('''
        SELECT bill_date, SUM(total) FROM sales_bill
        GROUP BY bill_date
    ''')
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def export():
        with open("daily_sales_report.csv", "w") as f:
            f.write("Date,Total Sales\n")
            for row in tree.get_children():
                vals = tree.item(row)["values"]
                f.write(f"{vals[0]},{vals[1]}\n")
        messagebox.showinfo("Exported", "Saved to daily_sales_report.csv")

    tk.Button(win, text="Export CSV", command=export).pack(pady=10)

def credit_sales_report():
    win = tk.Toplevel(root)
    win.title("Credit Sales Report")

    tree = ttk.Treeview(win, columns=("Customer", "Due Date", "Amount"), show="headings")
    tree.heading("Customer", text="Customer")
    tree.heading("Due Date", text="Due Date")
    tree.heading("Amount", text="Amount")
    tree.pack(fill="both", expand=True)

    today = datetime.date.today()
    c.execute('''
        SELECT customer_name, due_date, SUM(total) FROM sales_bill
        WHERE due_date > ?
        GROUP BY customer_name, due_date
    ''', (today,))
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def export():
        with open("credit_sales_report.csv", "w") as f:
            f.write("Customer,Due Date,Amount\n")
            for row in tree.get_children():
                vals = tree.item(row)["values"]
                f.write(f"{vals[0]},{vals[1]},{vals[2]}\n")
        messagebox.showinfo("Exported", "Saved to credit_sales_report.csv")

    tk.Button(win, text="Export CSV", command=export).pack(pady=10)

import csv  # Put this at the top of your file if not already there!

def open_purchase_reports():
    win = tk.Toplevel(root)
    win.title("Purchase Reports")

    # Create button for each report type
    def vendor_wise():
        show_report("Vendor Wise Purchase", "SELECT customer_name, SUM(total) FROM purchase_entry GROUP BY customer_name")

    def daily_report():
        show_report("Daily Purchase", "SELECT bill_date, SUM(total) FROM purchase_entry GROUP BY bill_date")

    def mfg_wise():
        show_report("Manufacturing Wise Purchase", "SELECT medicine_name, SUM(total) FROM purchase_entry GROUP BY medicine_name")

    def credit_report():
        show_report("Credit Purchase", "SELECT customer_name, SUM(total) FROM purchase_entry WHERE due_date > bill_date GROUP BY customer_name")

    # Reusable viewer for each report
    def show_report(title, query):
        rpt = tk.Toplevel(win)
        rpt.title(title)

        tree = ttk.Treeview(rpt, columns=("Field", "Total"), show="headings")
        tree.heading("Field", text="Field")
        tree.heading("Total", text="Total")
        tree.pack(fill="both", expand=True)

        c.execute(query)
        rows = c.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)

        def export_csv():
            file = title.replace(" ", "_") + ".csv"
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Field", "Total"])
                writer.writerows(rows)
            messagebox.showinfo("Exported", f"Saved as {file}")

        tk.Button(rpt, text="Export CSV", command=export_csv).pack(pady=5)

    # The buttons to choose what report to view
    tk.Button(win, text="Vendor Wise", command=vendor_wise).pack(pady=5)
    tk.Button(win, text="Daily Report", command=daily_report).pack(pady=5)
    tk.Button(win, text="Manufacturing Wise", command=mfg_wise).pack(pady=5)
    tk.Button(win, text="Credit Purchase", command=credit_report).pack(pady=5)

def new_inventory_entry():
    win = tk.Toplevel(root)
    win.title("New Inventory Entry")

    tk.Label(win, text="Vendor Name").pack()
    cname = tk.Entry(win)
    cname.pack()

    tk.Label(win, text="Vendor Address").pack()
    cadd = tk.Entry(win)
    cadd.pack()

    tk.Label(win, text="GST No").pack()
    gst = tk.Entry(win)
    gst.pack()

    tk.Label(win, text="Drug License No").pack()
    dl = tk.Entry(win)
    dl.pack()

    tk.Label(win, text="GRN Date").pack()
    bdate = tk.Entry(win)
    bdate.insert(0, datetime.date.today())
    bdate.pack()

    tk.Label(win, text="Due Date").pack()
    ddate = tk.Entry(win)
    ddate.insert(0, datetime.date.today())
    ddate.pack()

    tree = ttk.Treeview(win, columns=("Medicine", "Qty", "Rate", "GST", "MRP", "Disc", "Total"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack()

    f = tk.Frame(win)
    f.pack()
    m = tk.Entry(f)
    q = tk.Entry(f)
    r = tk.Entry(f)
    g = tk.Entry(f)
    mrp = tk.Entry(f)
    d = tk.Entry(f)
    m.grid(row=0, column=0)
    q.grid(row=0, column=1)
    r.grid(row=0, column=2)
    g.grid(row=0, column=3)
    mrp.grid(row=0, column=4)
    d.grid(row=0, column=5)

    def add_item():
        total = int(q.get()) * float(r.get()) - float(d.get())
        tree.insert("", "end", values=(m.get(), q.get(), r.get(), g.get(), mrp.get(), d.get(), total))
        m.delete(0, 'end')
        q.delete(0, 'end')
        r.delete(0, 'end')
        g.delete(0, 'end')
        mrp.delete(0, 'end')
        d.delete(0, 'end')

    tk.Button(f, text="Add Item", command=add_item).grid(row=0, column=6)

def open_inventory_reports():
    inv_win = tk.Toplevel(root)
    inv_win.title("Inventory Reports")

    tk.Label(inv_win, text="Inventory Reports", font=("Arial", 16)).pack(pady=10)

    tk.Button(inv_win, text="Expiry Medicine Report", width=30, command=expiry_medicine_report).pack(pady=5)
    tk.Button(inv_win, text="Medicine Movement Report", width=30, command=medicine_movement_report).pack(pady=5)
    tk.Button(inv_win, text="Reorder Level Report", width=30, command=reorder_level_report).pack(pady=5)
    tk.Button(inv_win, text="Stock Report", width=30, command=stock_report).pack(pady=5)
    tk.Button(inv_win, text="Batch Wise Stock Report", width=30, command=batch_wise_stock_report).pack(pady=5)
    tk.Button(inv_win, text="Low Stock Alert", width=30, command=low_stock_alert).pack(pady=5)
    tk.Button(inv_win, text="GST Sales Report", width=30, command=gst_sales_report).pack(pady=5)
    tk.Button(inv_win, text="GST Purchase Report", width=30, command=gst_purchase_report).pack(pady=5)
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv

# === DB Connection ===
conn = sqlite3.connect("pharmacy.db")
c = conn.cursor()

# === HELPERS ===
def export_treeview_to_csv(tree, filename, headers):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in tree.get_children():
            writer.writerow(tree.item(row)["values"])
    messagebox.showinfo("Export", f"Saved as {filename}")

def print_treeview(tree, title, parent):
    preview = tk.Toplevel(parent)
    preview.title(f"Print Preview - {title}")

    text = tk.Text(preview)
    text.pack(fill="both", expand=True)

    for row in tree.get_children():
        values = tree.item(row)["values"]
        line = "\t".join(str(x) for x in values)
        text.insert("end", line + "\n")

    def do_print():
        messagebox.showinfo("Print", f"Sending {title} to printer...")

    tk.Button(preview, text="Print", command=do_print).pack(pady=5)

# === INDIVIDUAL REPORTS ===

def expiry_medicine_report():
    win = tk.Toplevel(root)
    win.title("Expiry Medicine Report")

    cols = ("Drug Code", "Drug Name", "Batch", "Expiry Date", "Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, expiry_date, stock_qty
        FROM stock
        WHERE expiry_date <= date('now', '+30 days')
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "expiry_medicine.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Expiry Medicine Report", win)).pack(side="left", padx=5)

def medicine_movement_report():
    win = tk.Toplevel(root)
    win.title("Medicine Movement Report")

    cols = ("Drug Code", "Drug Name", "Movement Type", "Date", "Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, movement_type, movement_date, qty
        FROM medicine_movement
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "medicine_movement.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Medicine Movement Report", win)).pack(side="left", padx=5)

def reorder_level_report():
    win = tk.Toplevel(root)
    win.title("Reorder Level Report")

    cols = ("Drug Code", "Drug Name", "Stock Qty", "Reorder Level")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, stock_qty, reorder_level
        FROM stock
        WHERE stock_qty <= reorder_level
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "reorder_level.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Reorder Level Report", win)).pack(side="left", padx=5)

def stock_report():
    win = tk.Toplevel(root)
    win.title("Stock Report")

    cols = ("Drug Code", "Drug Name", "Batch", "Stock Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, stock_qty
        FROM stock
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "stock_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Stock Report", win)).pack(side="left", padx=5)

def batch_wise_stock_report():
    win = tk.Toplevel(root)
    win.title("Batch Wise Stock Report")

    cols = ("Drug Code", "Drug Name", "Batch", "Mfg Date", "Expiry Date", "Stock Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, mfg_date, expiry_date, stock_qty
        FROM stock
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "batch_wise_stock.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Batch Wise Stock Report", win)).pack(side="left", padx=5)

def low_stock_alert():
    win = tk.Toplevel(root)
    win.title("Low Stock Alert")

    cols = ("Drug Code", "Drug Name", "Stock Qty", "Reorder Level")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, stock_qty, reorder_level
        FROM stock
        WHERE stock_qty < reorder_level
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "low_stock_alert.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Low Stock Alert", win)).pack(side="left", padx=5)

def gst_sales_report():
    win = tk.Toplevel(root)
    win.title("GST Sales Report")

    cols = ("Bill No", "Customer", "GST %", "GST Amount")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT bill_no, customer_name, gst_percent, gst_amount
        FROM sales
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "gst_sales_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "GST Sales Report", win)).pack(side="left", padx=5)

def gst_purchase_report():
    win = tk.Toplevel(root)
    win.title("GST Purchase Report")

    cols = ("GRN No", "Vendor", "GST %", "GST Amount")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT grn_no, vendor_name, gst_percent, gst_amount
        FROM purchase
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "gst_purchase_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "GST Purchase Report", win)).pack(side="left", padx=5)

def accounts_panel():
    win = tk.Toplevel(root)
    win.title("Accounts")

    tk.Label(win, text="Accounts - Credit Bills", font=("Arial", 16)).pack(pady=10)

    cols = ("Bill No", "Customer", "Bill Date", "Due Date", "Amount", "Paid")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    # Load unpaid bills
    c.execute("""
        SELECT bill_no, customer_name, bill_date, due_date, total_amount, paid_status
        FROM sales
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def mark_as_paid():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a bill.")
            return
        bill_no = tree.item(selected)["values"][0]
        c.execute("UPDATE sales SET paid_status='Paid' WHERE bill_no=?", (bill_no,))
        conn.commit()
        messagebox.showinfo("Updated", f"Bill {bill_no} marked as Paid.")
        accounts_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Mark Selected as Paid", command=mark_as_paid).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "accounts_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Accounts Report", win)).pack(side="left", padx=5)
def audit_panel():
    win = tk.Toplevel(root)
    win.title("Audit - Adjust Stock")

    cols = ("Drug Code", "Drug Name", "Batch", "Current Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, stock_qty
        FROM stock
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def adjust_stock():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an item.")
            return
        drug_code = tree.item(selected)["values"][0]
        new_qty = simpledialog.askinteger("Adjust Stock", "Enter new stock qty:")
        if new_qty is not None:
            c.execute("UPDATE stock SET stock_qty=? WHERE drug_code=?", (new_qty, drug_code))
            conn.commit()
            messagebox.showinfo("Updated", f"Stock updated for {drug_code}.")
            audit_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Adjust Selected Stock", command=adjust_stock).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "audit_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Audit Report", win)).pack(side="left", padx=5)




def accounts_panel():
    win = tk.Toplevel(root)
    win.title("Accounts")

    tk.Label(win, text="Accounts - Credit Bills", font=("Arial", 16)).pack(pady=10)

    cols = ("Bill No", "Customer", "Bill Date", "Due Date", "Amount", "Paid")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    # Load unpaid bills
    c.execute("""
        SELECT bill_no, customer_name, bill_date, due_date, total_amount, paid_status
        FROM sales
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def mark_as_paid():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a bill.")
            return
        bill_no = tree.item(selected)["values"][0]
        c.execute("UPDATE sales SET paid_status='Paid' WHERE bill_no=?", (bill_no,))
        conn.commit()
        messagebox.showinfo("Updated", f"Bill {bill_no} marked as Paid.")
        accounts_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Mark Selected as Paid", command=mark_as_paid).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "accounts_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Accounts Report", win)).pack(side="left", padx=5)
def audit_panel():
    win = tk.Toplevel(root)
    win.title("Audit - Adjust Stock")

    cols = ("Drug Code", "Drug Name", "Batch", "Current Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, stock_qty
        FROM stock
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def adjust_stock():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an item.")
            return
        drug_code = tree.item(selected)["values"][0]
        new_qty = simpledialog.askinteger("Adjust Stock", "Enter new stock qty:")
        if new_qty is not None:
            c.execute("UPDATE stock SET stock_qty=? WHERE drug_code=?", (new_qty, drug_code))
            conn.commit()
            messagebox.showinfo("Updated", f"Stock updated for {drug_code}.")
            audit_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Adjust Selected Stock", command=adjust_stock).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "audit_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Audit Report", win)).pack(side="left", padx=5)



def accounts_panel():
    win = tk.Toplevel(root)
    win.title("Accounts")

    tk.Label(win, text="Accounts - Credit Bills", font=("Arial", 16)).pack(pady=10)

    cols = ("Bill No", "Customer", "Bill Date", "Due Date", "Amount", "Paid")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    # Load unpaid bills
    c.execute("""
        SELECT bill_no, customer_name, bill_date, due_date, total_amount, paid_status
        FROM sales
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def mark_as_paid():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a bill.")
            return
        bill_no = tree.item(selected)["values"][0]
        c.execute("UPDATE sales SET paid_status='Paid' WHERE bill_no=?", (bill_no,))
        conn.commit()
        messagebox.showinfo("Updated", f"Bill {bill_no} marked as Paid.")
        accounts_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Mark Selected as Paid", command=mark_as_paid).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "accounts_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Accounts Report", win)).pack(side="left", padx=5)
def audit_panel():
    win = tk.Toplevel(root)
    win.title("Audit - Adjust Stock")

    cols = ("Drug Code", "Drug Name", "Batch", "Current Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    c.execute("""
        SELECT drug_code, drug_name, batch_no, stock_qty
        FROM stock
    """)
    for row in c.fetchall():
        tree.insert("", "end", values=row)

    def adjust_stock():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an item.")
            return
        drug_code = tree.item(selected)["values"][0]
        new_qty = simpledialog.askinteger("Adjust Stock", "Enter new stock qty:")
        if new_qty is not None:
            c.execute("UPDATE stock SET stock_qty=? WHERE drug_code=?", (new_qty, drug_code))
            conn.commit()
            messagebox.showinfo("Updated", f"Stock updated for {drug_code}.")
            audit_panel()  # Reload panel

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Adjust Selected Stock", command=adjust_stock).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Export to CSV",
              command=lambda: export_treeview_to_csv(tree, "audit_report.csv", cols)).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Print Preview",
              command=lambda: print_treeview(tree, "Audit Report", win)).pack(side="left", padx=5)



# ----------------- Root -----------------
root = tk.Tk()
root.title("Pharmacy Management")
tk.Button(root, text="Master", width=30, command=open_master).pack(pady=10)
tk.Button(root, text="Billing", width=30, command=open_billing).pack(pady=10)
tk.Button(root, text="Sales Reports", width=30, command=open_sales_reports).pack(pady=10)
tk.Button(root, text="Purchase Reports", width=30, command=open_purchase_reports).pack(pady=5)
tk.Button(root, text="Inventory Report", command=open_inventory_reports).pack(pady=5)
tk.Button(root, text="Accounts", command=accounts_panel).pack(pady=5)
tk.Button(root, text="Audit", command=audit_panel).pack(pady=5)



root.mainloop()
