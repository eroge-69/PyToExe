import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, json, datetime
from fpdf import FPDF
from openpyxl import Workbook, load_workbook

DATA_DIR = "data"
PRODUCT_FILE = os.path.join(DATA_DIR, "products.json")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.json")
INVOICE_EXCEL = os.path.join(DATA_DIR, "invoices.xlsx")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
LEDGER_FILE = os.path.join(DATA_DIR, "ledger.json")
PAYMENT_FILE = os.path.join(DATA_DIR, "payments.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("invoices", exist_ok=True)

def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else []

def save_json(path, data):
    json.dump(data, open(path, "w"), indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        return json.load(open(SETTINGS_FILE))
    return {
        "Company Name": "", "GSTIN": "", "Address": "", "Contact": "", "Logo": "",
        "Bank Name": "", "Branch Name": "", "Bank Ac No": "", "IFSC Code": ""
    }

def save_settings(settings):
    json.dump(settings, open(SETTINGS_FILE, "w"), indent=2)

def num2words(num):
    d = {0:'Zero',1:'One',2:'Two',3:'Three',4:'Four',5:'Five',6:'Six',7:'Seven',8:'Eight',9:'Nine',
         10:'Ten',11:'Eleven',12:'Twelve',13:'Thirteen',14:'Fourteen',15:'Fifteen',16:'Sixteen',17:'Seventeen',18:'Eighteen',19:'Nineteen',
         20:'Twenty',30:'Thirty',40:'Forty',50:'Fifty',60:'Sixty',70:'Seventy',80:'Eighty',90:'Ninety'}
    if num <= 20: return d.get(num, str(num))
    elif num < 100: return d[num-num%10] + " " + d.get(num%10,"")
    elif num < 1000: return d[num//100] + " Hundred " + num2words(num%100)
    elif num < 100000: return num2words(num//1000) + " Thousand " + num2words(num%1000)
    elif num < 10000000: return num2words(num//100000) + " Lakh " + num2words(num%100000)
    else: return str(num)

def today():
    return datetime.datetime.now().strftime("%d/%m/%Y")

def this_month():
    return datetime.datetime.now().strftime("%m/%Y")

def this_year():
    return datetime.datetime.now().strftime("%Y")

def filter_invoices(period="today"):
    rows = []
    if not os.path.exists(INVOICE_EXCEL): return rows
    wb = load_workbook(INVOICE_EXCEL)
    ws = wb.active
    for r in ws.iter_rows(min_row=2, values_only=True):
        dt = r[0]
        amt = float(r[8]) if r[8] else 0
        if period == "today" and dt == today(): rows.append(amt)
        elif period == "month" and dt[-7:] == this_month(): rows.append(amt)
        elif period == "year" and dt[-4:] == this_year(): rows.append(amt)
    return rows

root = tk.Tk()
root.title("Finno ERP Billing")
root.state("zoomed")
style = ttk.Style()
style.configure("Treeview", rowheight=28)
style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

sidebar = tk.Frame(root, width=220, bg="#2f3e46")
sidebar.pack(side="left", fill="y")
header = tk.Frame(root, height=80, bg="#354f52")
header.pack(side="top", fill="x")
home_frame = tk.Frame(root, bg="#f7f7f7")
product_frame = tk.Frame(root, bg="#e5e5e5")
customer_frame = tk.Frame(root, bg="#e5e5e5")
invoice_frame = tk.Frame(root, bg="#e5e5e5")
settings_frame = tk.Frame(root, bg="#f0f0f0")
ledger_frame = tk.Frame(root, bg="#e5e5e5")
payment_frame = tk.Frame(root, bg="#e5e5e5")
reports_frame = tk.Frame(root, bg="#f7f7f7")

def switch_frame(f):
    for frame in [home_frame, product_frame, customer_frame, invoice_frame, ledger_frame, payment_frame, reports_frame, settings_frame]:
        frame.pack_forget()
    f.pack(fill="both", expand=True)

tk.Label(sidebar, text="📊 Dashboard", bg="#2f3e46", fg="white", font=("Arial", 14), pady=20).pack()
for label, frame in [
    ("🏠 Home", home_frame),
    ("📦 Products", product_frame),
    ("👥 Customers", customer_frame),
    ("🧾 Invoice", invoice_frame),
    ("💼 Ledger", ledger_frame),
    ("💰 Payments", payment_frame),
    ("📈 Reports", reports_frame),
    ("⚙️ Settings", settings_frame)
]:
    tk.Button(sidebar, text=label, bg="#354f52", fg="white", font=("Arial", 12),
              command=lambda f=frame: switch_frame(f), relief="flat").pack(fill="x")
tk.Label(header, text="FINNO ERP Billing System", bg="#354f52", fg="white", font=("Arial", 32, "bold")).pack(pady=20)

def refresh_home():
    for w in home_frame.winfo_children(): w.destroy()
    tk.Label(home_frame, text="Welcome to Finno ERP", font=("Arial", 26, "bold"), bg="#f7f7f7").pack(pady=14)
    stats = tk.Frame(home_frame, bg="#f7f7f7"); stats.pack(pady=14)
    today_sales = sum(filter_invoices("today"))
    month_sales = sum(filter_invoices("month"))
    year_sales = sum(filter_invoices("year"))
    tk.Label(stats, text=f"Today's Sales: Rs. {today_sales:.2f}", font=("Arial", 18), bg="#f7f7f7").grid(row=0, column=0, padx=40)
    tk.Label(stats, text=f"Monthly Sales: Rs. {month_sales:.2f}", font=("Arial", 18), bg="#f7f7f7").grid(row=0, column=1, padx=40)
    tk.Label(stats, text=f"Yearly Sales: Rs. {year_sales:.2f}", font=("Arial", 18), bg="#f7f7f7").grid(row=0, column=2, padx=40)
    total_p = len(load_json(PRODUCT_FILE)); total_c = len(load_json(CUSTOMER_FILE))
    tk.Label(home_frame, text=f"Products: {total_p}   Customers: {total_c}", font=("Arial", 16), bg="#f7f7f7").pack(pady=10)
refresh_home()

def refresh_product_table(search_text=""):
    for row in prod_tree.get_children():
        prod_tree.delete(row)
    for p in load_json(PRODUCT_FILE):
        if search_text.lower() in p['name'].lower():
            prod_tree.insert('', 'end', values=(p['name'], p['price'], p['stock']))

def add_product():
    name = prod_name.get()
    price = prod_price.get()
    stock = prod_stock.get()
    if not name or not price or not stock:
        messagebox.showerror("Error", "Please fill all fields.")
        return
    data = load_json(PRODUCT_FILE)
    data.append({'name': name, 'price': float(price), 'stock': int(stock)})
    save_json(PRODUCT_FILE, data)
    refresh_product_table()
    prod_name.delete(0, 'end')
    prod_price.delete(0, 'end')
    prod_stock.delete(0, 'end')
    invoice_update_dropdowns()

def delete_selected_product():
    selected = prod_tree.selection()
    if not selected:
        return
    values = prod_tree.item(selected[0])['values']
    data = load_json(PRODUCT_FILE)
    data = [d for d in data if d['name'] != values[0]]
    save_json(PRODUCT_FILE, data)
    refresh_product_table()
    invoice_update_dropdowns()

def edit_selected_product():
    selected = prod_tree.selection()
    if not selected:
        return
    values = prod_tree.item(selected[0])['values']
    prod_name.delete(0, 'end')
    prod_price.delete(0, 'end')
    prod_stock.delete(0, 'end')
    prod_name.insert(0, values[0])
    prod_price.insert(0, values[1])
    prod_stock.insert(0, values[2])
    delete_selected_product()

tk.Label(product_frame, text="Manage Products", font=("Arial", 22, "bold"), bg="#e5e5e5").pack(pady=20)
form_frame = tk.Frame(product_frame, bg="#e5e5e5"); form_frame.pack()
tk.Label(form_frame, text="Product Name", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=0)
prod_name = tk.Entry(form_frame, font=("Arial", 12)); prod_name.grid(row=0, column=1)
tk.Label(form_frame, text="Price (Rs.)", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=2)
prod_price = tk.Entry(form_frame, font=("Arial", 12)); prod_price.grid(row=0, column=3)
tk.Label(form_frame, text="Stock", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=4)
prod_stock = tk.Entry(form_frame, font=("Arial", 12)); prod_stock.grid(row=0, column=5)
tk.Button(form_frame, text="➕ Add / Update", bg="#2f3e46", fg="white", font=("Arial", 12), command=add_product).grid(row=0, column=6, padx=10)
search_entry = tk.Entry(product_frame, font=("Arial", 12)); search_entry.pack(pady=5)
search_entry.insert(0, "Search product..."); search_entry.bind("<KeyRelease>", lambda e: refresh_product_table(search_entry.get()))
table_frame = tk.Frame(product_frame); table_frame.pack(pady=10)
cols = ("Name", "Price", "Stock")
prod_tree = ttk.Treeview(table_frame, columns=cols, show='headings')
for col in cols: prod_tree.heading(col, text=col); prod_tree.column(col, width=200)
prod_tree.pack(side="left", fill="y")
scroll = ttk.Scrollbar(table_frame, orient="vertical", command=prod_tree.yview)
prod_tree.configure(yscrollcommand=scroll.set); scroll.pack(side="right", fill="y")
btns = tk.Frame(product_frame, bg="#e5e5e5"); btns.pack(pady=10)
tk.Button(btns, text="✏️ Edit Selected", command=edit_selected_product, bg="#f4a261", font=("Arial", 12)).grid(row=0, column=0, padx=10)
tk.Button(btns, text="🗑️ Delete Selected", command=delete_selected_product, bg="#e76f51", fg="white", font=("Arial", 12)).grid(row=0, column=1, padx=10)
refresh_product_table()

def refresh_customer_table(search_text=""):
    for row in cust_tree.get_children():
        cust_tree.delete(row)
    for c in load_json(CUSTOMER_FILE):
        if search_text.lower() in c['name'].lower():
            cust_tree.insert('', 'end', values=(c['name'], c['address'], c['phone'], c.get('email', '')))

def add_customer():
    name = cust_name.get()
    address = cust_address.get()
    phone = cust_phone.get()
    email = cust_email.get()
    if not name or not phone or not address:
        messagebox.showerror("Error", "Fill Name, Address, and Phone")
        return
    data = load_json(CUSTOMER_FILE)
    data.append({'name': name, 'address': address, 'phone': phone, 'email': email})
    save_json(CUSTOMER_FILE, data)
    refresh_customer_table()
    cust_name.delete(0, 'end')
    cust_address.delete(0, 'end')
    cust_phone.delete(0, 'end')
    cust_email.delete(0, 'end')
    invoice_update_dropdowns()

def delete_selected_customer():
    selected = cust_tree.selection()
    if not selected:
        return
    values = cust_tree.item(selected[0])['values']
    data = load_json(CUSTOMER_FILE)
    data = [d for d in data if d['name'] != values[0]]
    save_json(CUSTOMER_FILE, data)
    refresh_customer_table()
    invoice_update_dropdowns()

def edit_selected_customer():
    selected = cust_tree.selection()
    if not selected:
        return
    values = cust_tree.item(selected[0])['values']
    cust_name.delete(0, 'end')
    cust_address.delete(0, 'end')
    cust_phone.delete(0, 'end')
    cust_email.delete(0, 'end')
    cust_name.insert(0, values[0])
    cust_address.insert(0, values[1])
    cust_phone.insert(0, values[2])
    cust_email.insert(0, values[3])
    delete_selected_customer()

tk.Label(customer_frame, text="Manage Customers", font=("Arial", 22, "bold"), bg="#e5e5e5").pack(pady=20)
cust_form = tk.Frame(customer_frame, bg="#e5e5e5"); cust_form.pack()
tk.Label(cust_form, text="Name", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=0)
cust_name = tk.Entry(cust_form, font=("Arial", 12)); cust_name.grid(row=0, column=1)
tk.Label(cust_form, text="Address", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=2)
cust_address = tk.Entry(cust_form, font=("Arial", 12), width=30); cust_address.grid(row=0, column=3)
tk.Label(cust_form, text="Phone", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=0)
cust_phone = tk.Entry(cust_form, font=("Arial", 12)); cust_phone.grid(row=1, column=1)
tk.Label(cust_form, text="Email (optional)", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=2)
cust_email = tk.Entry(cust_form, font=("Arial", 12)); cust_email.grid(row=1, column=3)
tk.Button(cust_form, text="➕ Add / Update", bg="#2f3e46", fg="white", font=("Arial", 12), command=add_customer).grid(row=0, column=5, rowspan=2, padx=10)
cust_search = tk.Entry(customer_frame, font=("Arial", 12)); cust_search.pack(pady=5)
cust_search.insert(0, "Search customer..."); cust_search.bind("<KeyRelease>", lambda e: refresh_customer_table(cust_search.get()))
cust_table_frame = tk.Frame(customer_frame); cust_table_frame.pack(pady=10)
cust_cols = ("Name", "Address", "Phone", "Email")
cust_tree = ttk.Treeview(cust_table_frame, columns=cust_cols, show='headings')
for col in cust_cols: cust_tree.heading(col, text=col); cust_tree.column(col, width=200)
cust_tree.pack(side="left", fill="y")
cust_scroll = ttk.Scrollbar(cust_table_frame, orient="vertical", command=cust_tree.yview)
cust_tree.configure(yscrollcommand=cust_scroll.set); cust_scroll.pack(side="right", fill="y")
cust_btns = tk.Frame(customer_frame, bg="#e5e5e5"); cust_btns.pack(pady=10)
tk.Button(cust_btns, text="✏️ Edit Selected", command=edit_selected_customer, bg="#f4a261", font=("Arial", 12)).grid(row=0, column=0, padx=10)
tk.Button(cust_btns, text="🗑️ Delete Selected", command=delete_selected_customer, bg="#e76f51", fg="white", font=("Arial", 12)).grid(row=0, column=1, padx=10)
refresh_customer_table()

invoice_items = []
def invoice_update_dropdowns():
    prodlist = [p['name'] for p in load_json(PRODUCT_FILE)]
    inv_product['values'] = prodlist
    custlist = [c['name'] for c in load_json(CUSTOMER_FILE)]
    inv_customer['values'] = custlist

def on_product_select(event=None):
    name = inv_product.get()
    for p in load_json(PRODUCT_FILE):
        if p['name'] == name:
            inv_price.delete(0, 'end')
            inv_price.insert(0, p['price'])
            inv_gst.delete(0, 'end')
            inv_gst.insert(0, p.get('gst', 12))
            return

def on_customer_select(event=None):
    name = inv_customer.get()
    for c in load_json(CUSTOMER_FILE):
        if c['name'] == name:
            inv_addr_var.set(c['address'])
            inv_phone_var.set(c['phone'])
            return

def refresh_invoice_table():
    for row in inv_tree.get_children():
        inv_tree.delete(row)
    total = 0
    for item in invoice_items:
        amount = item['qty'] * item['price']
        gst_amt = amount * item['gst'] / 100
        total_amt = amount + gst_amt
        total += total_amt
        inv_tree.insert('', 'end', values=(item['product'], item['qty'], item['price'], item['gst'], round(total_amt, 2)))
    inv_total_label.config(text=f"Total: Rs. {round(total, 2)}")

def add_invoice_item():
    name = inv_product.get()
    qty = inv_qty.get()
    price = inv_price.get()
    gst = inv_gst.get()
    if not name or not qty or not price:
        messagebox.showerror("Error", "Please fill Product, Qty, and Price.")
        return
    prod_data = load_json(PRODUCT_FILE)
    for p in prod_data:
        if p['name'] == name:
            if int(qty) > int(p['stock']):
                messagebox.showerror("Error", f"Not enough stock for {name}. Available: {p['stock']}")
                return
    invoice_items.append({'product': name, 'qty': int(qty), 'price': float(price), 'gst': float(gst or 0)})
    inv_product.set("")
    inv_qty.delete(0, 'end')
    inv_price.delete(0, 'end')
    inv_gst.delete(0, 'end')
    refresh_invoice_table()

def delete_invoice_item():
    selected = inv_tree.selection()
    if not selected:
        return
    idx = inv_tree.index(selected[0])
    invoice_items.pop(idx)
    refresh_invoice_table()

def edit_invoice_item():
    selected = inv_tree.selection()
    if not selected:
        return
    idx = inv_tree.index(selected[0])
    item = invoice_items.pop(idx)
    inv_product.set(item['product'])
    inv_qty.delete(0, 'end')
    inv_price.delete(0, 'end')
    inv_gst.delete(0, 'end')
    inv_qty.insert(0, str(item['qty']))
    inv_price.insert(0, str(item['price']))
    inv_gst.insert(0, str(item['gst']))
    refresh_invoice_table()

def save_invoice():
    customer = inv_customer.get()
    address = inv_addr_var.get()
    phone = inv_phone_var.get()
    date = today()
    discount_value = 0.0
    discount_percent = 0.0
    try:
        discount_value = float(inv_discount.get())
    except:
        discount_value = 0.0
    try:
        discount_percent = float(inv_discount_percent.get())
    except:
        discount_percent = 0.0
    inv_type = inv_type_var.get() or "Cash"
    if not customer or not invoice_items:
        messagebox.showerror("Error", "Customer and at least one product are required.")
        return
    prod_data = load_json(PRODUCT_FILE)
    for item in invoice_items:
        for p in prod_data:
            if p['name'] == item['product']:
                if int(item['qty']) > int(p['stock']):
                    messagebox.showerror("Error", f"Not enough stock for {p['name']}. Available: {p['stock']}")
                    return
                p['stock'] = int(p['stock']) - int(item['qty'])
    save_json(PRODUCT_FILE, prod_data)
    refresh_product_table()
    invoice_update_dropdowns()
    settings = load_settings()
    total_basic = sum(item['qty'] * item['price'] for item in invoice_items)
    total_gst = sum(item['qty'] * item['price'] * item['gst'] / 100 for item in invoice_items)
    total_amt = total_basic + total_gst
    discount_percent_amt = total_amt * (discount_percent/100)
    grand_discount = discount_value + discount_percent_amt
    total_after_discount = total_amt - grand_discount
    # Save invoice to Excel
    if not os.path.exists(INVOICE_EXCEL):
        wb = Workbook()
        ws = wb.active
        ws.append(["Date", "Customer", "Product", "Qty", "Price", "GST%", "Discount(Rs.)", "Discount(%)", "Total", "Type"])
    else:
        wb = load_workbook(INVOICE_EXCEL)
        ws = wb.active
    for item in invoice_items:
        amt = item['qty'] * item['price']
        gst_amt = amt * item['gst'] / 100
        total_inv = amt + gst_amt - (grand_discount / len(invoice_items) if len(invoice_items) else 0)
        ws.append([date, customer, item['product'], item['qty'], item['price'], item['gst'], discount_value, discount_percent, round(total_inv, 2), inv_type])
    wb.save(INVOICE_EXCEL)
    # Add to ledger (for credit)
    ledger = load_json(LEDGER_FILE)
    if inv_type == "Credit":
        ledger.append({
            "customer": customer, "date": date, "amount": total_after_discount, "status": "Due",
            "partially_paid": 0.0, "remaining": total_after_discount
        })
        save_json(LEDGER_FILE, ledger)
    # Add to payments (for cash)
    payments = load_json(PAYMENT_FILE)
    if inv_type == "Cash":
        payments.append({"customer": customer, "amount": total_after_discount, "mode": "Cash", "ref": "Invoice", "date": date})
        save_json(PAYMENT_FILE, payments)
    pdf = FPDF()
    pdf.add_page()
    if settings.get("Logo") and os.path.exists(settings["Logo"]):
        pdf.image(settings["Logo"], x=10, y=8, w=33)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, settings.get("Company Name", ""), ln=1, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, settings.get("Address", ""), ln=1, align="C")
    pdf.cell(0, 8, f"GSTIN: {settings.get('GSTIN','')}   Contact: {settings.get('Contact','')}", ln=1, align="C")
    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "GST Invoice", ln=1, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Customer: {customer}", ln=1)
    pdf.cell(0, 7, f"Address: {address}", ln=1)
    pdf.cell(0, 7, f"Phone: {phone}", ln=1)
    pdf.cell(0, 7, f"Date: {date}   Type: {inv_type}", ln=1)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(10, 8, "Sr", 1)
    pdf.cell(50, 8, "Product", 1)
    pdf.cell(18, 8, "Qty", 1)
    pdf.cell(25, 8, "Price", 1)
    pdf.cell(17, 8, "GST%", 1)
    pdf.cell(25, 8, "GST Amt", 1)
    pdf.cell(25, 8, "Amount", 1, ln=1)
    pdf.set_font("Arial", "", 10)
    for i, item in enumerate(invoice_items, 1):
        amt = item['qty'] * item['price']
        gst_amt = amt * item['gst'] / 100
        total_line = amt + gst_amt
        pdf.cell(10, 8, str(i), 1)
        pdf.cell(50, 8, item['product'], 1)
        pdf.cell(18, 8, str(item['qty']), 1)
        pdf.cell(25, 8, f"Rs. {item['price']:.2f}", 1)
        pdf.cell(17, 8, f"{item['gst']}%", 1)
        pdf.cell(25, 8, f"Rs. {gst_amt:.2f}", 1)
        pdf.cell(25, 8, f"Rs. {total_line:.2f}", 1, ln=1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(120, 8, "Sub Total", 1)
    pdf.cell(25, 8, f"Rs. {total_basic:.2f}", 1)
    pdf.cell(25, 8, "GST Total", 1)
    pdf.cell(25, 8, f"Rs. {total_gst:.2f}", 1, ln=1)
    pdf.cell(120, 8, "Discount (Rs.)", 1)
    pdf.cell(25, 8, f"Rs. {discount_value:.2f}", 1)
    pdf.cell(25, 8, "Discount (%)", 1)
    pdf.cell(25, 8, f"{discount_percent:.2f}%", 1, ln=1)
    pdf.cell(120, 8, "Grand Total", 1)
    pdf.cell(75, 8, f"Rs. {total_after_discount:.2f}", 1, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 8, f"Amount in words: {num2words(round(total_after_discount))} only", ln=1)
    pdf.cell(0, 6, f"Bank: {settings.get('Bank Name','')} Branch: {settings.get('Branch Name','')}", ln=1)
    pdf.cell(0, 6, f"A/C: {settings.get('Bank Ac No','')} IFSC: {settings.get('IFSC Code','')}", ln=1)
    pdf.ln(8)
    pdf.cell(0, 6, "Customer Sign", ln=0)
    pdf.cell(0, 6, "Authorised Signatory", ln=1, align="R")
    fname = f"invoices/invoice_{customer.replace(' ','_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    try:
        pdf.output(fname)
        messagebox.showinfo("Saved", f"Invoice saved as {fname}")
    except Exception as e:
        messagebox.showerror("Error", f"PDF not saved: {e}")
    invoice_items.clear()
    refresh_invoice_table()
    refresh_product_table()
    refresh_home()
    refresh_ledger()
    refresh_payments()
    refresh_reports()

def print_invoice():
    import platform
    filename = filedialog.askopenfilename(initialdir="invoices", filetypes=[("PDF Files", "*.pdf")])
    if not filename:
        return
    try:
        if platform.system() == "Windows":
            os.startfile(filename, "print")
        elif platform.system() == "Darwin":
            os.system(f"lp {filename}")
        else:
            os.system(f"lp {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Print failed: {e}")

tk.Label(invoice_frame, text="Invoice Generator", font=("Arial", 22, "bold"), bg="#e5e5e5").pack(pady=10)
inv_top = tk.Frame(invoice_frame, bg="#e5e5e5"); inv_top.pack()
tk.Label(inv_top, text="Customer", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=0)
inv_customer = ttk.Combobox(inv_top, font=("Arial", 12), width=30, postcommand=invoice_update_dropdowns)
inv_customer.grid(row=0, column=1)
inv_customer.bind("<<ComboboxSelected>>", on_customer_select)
inv_addr_var = tk.StringVar(); inv_phone_var = tk.StringVar()
tk.Label(inv_top, text="Address", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=2)
tk.Entry(inv_top, font=("Arial", 12), textvariable=inv_addr_var, width=30, state='readonly').grid(row=0, column=3)
tk.Label(inv_top, text="Phone", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=4)
tk.Entry(inv_top, font=("Arial", 12), textvariable=inv_phone_var, width=15, state='readonly').grid(row=0, column=5)
tk.Label(inv_top, text="Invoice Type", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=6)
inv_type_var = tk.StringVar(); inv_type = ttk.Combobox(inv_top, textvariable=inv_type_var, font=("Arial", 12), width=8)
inv_type['values'] = ["Cash", "Credit"]; inv_type.set("Cash"); inv_type.grid(row=0, column=7)
tk.Label(inv_top, text="Discount (Rs.)", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=8)
inv_discount = tk.Entry(inv_top, font=("Arial", 12), width=10); inv_discount.grid(row=0, column=9)
tk.Label(inv_top, text="Discount (%)", font=("Arial", 12), bg="#e5e5e5").grid(row=0, column=10)
inv_discount_percent = tk.Entry(inv_top, font=("Arial", 12), width=10); inv_discount_percent.grid(row=0, column=11)
tk.Label(inv_top, text="Product", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=0)
inv_product = ttk.Combobox(inv_top, font=("Arial", 12), width=30, postcommand=invoice_update_dropdowns)
inv_product.grid(row=1, column=1)
inv_product.bind("<<ComboboxSelected>>", on_product_select)
tk.Label(inv_top, text="Qty", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=2)
inv_qty = tk.Entry(inv_top, font=("Arial", 12), width=8); inv_qty.grid(row=1, column=3)
tk.Label(inv_top, text="Price", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=4)
inv_price = tk.Entry(inv_top, font=("Arial", 12), width=10); inv_price.grid(row=1, column=5)
tk.Label(inv_top, text="GST%", font=("Arial", 12), bg="#e5e5e5").grid(row=1, column=6)
inv_gst = tk.Entry(inv_top, font=("Arial", 12), width=8); inv_gst.grid(row=1, column=7)
tk.Button(inv_top, text="➕ Add Item", bg="#2f3e46", fg="white", font=("Arial", 12), command=add_invoice_item).grid(row=1, column=8, padx=10)

inv_table = tk.Frame(invoice_frame); inv_table.pack(pady=10)
inv_tree = ttk.Treeview(inv_table, columns=("Product", "Qty", "Price", "GST", "Total"), show='headings')
for col in ("Product", "Qty", "Price", "GST", "Total"): inv_tree.heading(col, text=col); inv_tree.column(col, width=120)
inv_tree.pack(side="left")
scroll = ttk.Scrollbar(inv_table, orient="vertical", command=inv_tree.yview)
inv_tree.configure(yscrollcommand=scroll.set); scroll.pack(side="right", fill="y")

btns = tk.Frame(invoice_frame, bg="#e5e5e5"); btns.pack(pady=10)
tk.Button(btns, text="✏️ Edit", command=edit_invoice_item, bg="#f4a261", font=("Arial", 12)).grid(row=0, column=0, padx=10)
tk.Button(btns, text="🗑️ Delete", command=delete_invoice_item, bg="#e76f51", fg="white", font=("Arial", 12)).grid(row=0, column=1, padx=10)
tk.Button(btns, text="💾 Save Invoice", command=save_invoice, bg="#2a9d8f", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=10)
tk.Button(btns, text="🖨️ Print", command=print_invoice, bg="#264653", fg="white", font=("Arial", 12)).grid(row=0, column=3, padx=10)
inv_total_label = tk.Label(invoice_frame, text="Total: Rs. 0.00", font=("Arial", 18, "bold"), bg="#e5e5e5"); inv_total_label.pack(pady=10)

def refresh_ledger():
    for w in ledger_frame.winfo_children():
        w.destroy()
    tk.Label(ledger_frame, text="Ledger (Credit Invoices)", font=("Arial", 22, "bold"), bg="#e5e5e5").pack(pady=10)
    ledger = load_json(LEDGER_FILE)
    led_tree = ttk.Treeview(ledger_frame, columns=("Customer", "Date", "Amount", "Status", "Partially Paid", "Remaining"), show="headings")
    for col in ("Customer", "Date", "Amount", "Status", "Partially Paid", "Remaining"): led_tree.heading(col, text=col); led_tree.column(col, width=120)
    for r in ledger: led_tree.insert('', 'end', values=(r['customer'], r['date'], r['amount'], r['status'], r.get('partially_paid',0.0), r.get('remaining',r['amount'])))
    led_tree.pack(pady=10)
    def edit_ledger():
        sel = led_tree.selection()
        if not sel:
            return
        vals = led_tree.item(sel[0])['values']
        idx = led_tree.index(sel[0])
        win = tk.Toplevel(root); win.title("Edit Ledger Entry")
        tk.Label(win, text="Customer", font=("Arial", 12)).grid(row=0, column=0); ecust = tk.Entry(win, font=("Arial", 12)); ecust.insert(0, vals[0]); ecust.grid(row=0, column=1)
        tk.Label(win, text="Amount", font=("Arial", 12)).grid(row=1, column=0); eamt = tk.Entry(win, font=("Arial", 12)); eamt.insert(0, vals[2]); eamt.grid(row=1, column=1)
        tk.Label(win, text="Status", font=("Arial", 12)).grid(row=2, column=0); estatus = ttk.Combobox(win, font=("Arial", 12), values=["Due","Paid"])
        estatus.set(vals[3]); estatus.grid(row=2, column=1)
        tk.Label(win, text="Partially Paid", font=("Arial", 12)).grid(row=3, column=0); epartial = tk.Entry(win, font=("Arial", 12)); epartial.insert(0, vals[4]); epartial.grid(row=3, column=1)
        def save_edit():
            ledger[idx]['customer'] = ecust.get()
            ledger[idx]['amount'] = float(eamt.get())
            ledger[idx]['status'] = estatus.get()
            ledger[idx]['partially_paid'] = float(epartial.get())
            ledger[idx]['remaining'] = float(ledger[idx]['amount']) - float(epartial.get())
            save_json(LEDGER_FILE, ledger); refresh_ledger(); win.destroy()
        tk.Button(win, text="Save", command=save_edit, bg="#4caf50", fg="white", font=("Arial", 12)).grid(row=4, column=0, columnspan=2, pady=8)
    def export_ledger_pdf():
        fname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if fname:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Ledger Report", ln=1, align="C")
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40,8,"Customer",1); pdf.cell(25,8,"Date",1); pdf.cell(25,8,"Amount",1); pdf.cell(25,8,"Status",1); pdf.cell(35,8,"Partially Paid",1); pdf.cell(30,8,"Remaining",1,ln=1)
            pdf.set_font("Arial", "", 10)
            for r in ledger: pdf.cell(40,8,str(r['customer']),1); pdf.cell(25,8,str(r['date']),1); pdf.cell(25,8,str(r['amount']),1); pdf.cell(25,8,str(r['status']),1); pdf.cell(35,8,str(r.get('partially_paid',0.0)),1); pdf.cell(30,8,str(r.get('remaining',r['amount'])),1,ln=1)
            pdf.output(fname); messagebox.showinfo("Exported", f"Ledger PDF saved as {fname}")
    tk.Button(ledger_frame, text="Edit Selected", command=edit_ledger, bg="#2a9d8f", fg="white", font=("Arial", 12)).pack(pady=8)
    tk.Button(ledger_frame, text="Export Ledger PDF", command=export_ledger_pdf, bg="#264653", fg="white", font=("Arial", 12)).pack(pady=8)
refresh_ledger()

def refresh_payments():
    for w in payment_frame.winfo_children():
        w.destroy()
    tk.Label(payment_frame, text="Payments", font=("Arial", 22, "bold"), bg="#e5e5e5").pack(pady=10)
    payment_list = load_json(PAYMENT_FILE)
    pay_tree = ttk.Treeview(payment_frame, columns=("Customer","Amount","Mode","Ref","Date"), show="headings")
    for col in ("Customer","Amount","Mode","Ref","Date"): pay_tree.heading(col, text=col); pay_tree.column(col, width=120)
    for r in payment_list: pay_tree.insert('', 'end', values=(r['customer'], r['amount'], r['mode'], r['ref'], r['date']))
    pay_tree.pack(pady=10)
    def add_partial_payment():
        win = tk.Toplevel(root); win.title("Partial Payment")
        tk.Label(win, text="Customer", font=("Arial", 12)).grid(row=0, column=0); ecust = ttk.Combobox(win, font=("Arial", 12)); ecust['values'] = [x['customer'] for x in load_json(LEDGER_FILE) if x['status'] == 'Due']; ecust.grid(row=0, column=1)
        tk.Label(win, text="Payment Amount", font=("Arial", 12)).grid(row=1, column=0); eamt = tk.Entry(win, font=("Arial", 12)); eamt.grid(row=1, column=1)
        tk.Label(win, text="Mode", font=("Arial", 12)).grid(row=2, column=0); emode = ttk.Combobox(win, font=("Arial", 12)); emode['values'] = ['Cash','UPI','Card','Bank']; emode.grid(row=2, column=1)
        tk.Label(win, text="Reference", font=("Arial", 12)).grid(row=3, column=0); eref = tk.Entry(win, font=("Arial", 12)); eref.grid(row=3, column=1)
        def save_partial():
            customer = ecust.get(); amt = float(eamt.get()); mode = emode.get(); ref = eref.get()
            payments = load_json(PAYMENT_FILE)
            payments.append({"customer": customer, "amount": amt, "mode": mode, "ref": ref, "date": today()})
            save_json(PAYMENT_FILE, payments)
            # update ledger
            ledger = load_json(LEDGER_FILE)
            for entry in ledger:
                if entry['customer'] == customer and entry['status'] == 'Due':
                    entry['partially_paid'] = entry.get('partially_paid',0.0) + amt
                    entry['remaining'] = float(entry['amount']) - float(entry['partially_paid'])
                    if entry['remaining'] <= 0:
                        entry['status'] = 'Paid'
            save_json(LEDGER_FILE, ledger)
            win.destroy()
            refresh_ledger()
            refresh_payments()
        tk.Button(win, text="Save Payment", command=save_partial, bg="#2a9d8f", fg="white", font=("Arial", 12)).grid(row=4, column=0, columnspan=2, pady=8)
    tk.Button(payment_frame, text="Add Partial Payment", command=add_partial_payment, bg="#2a9d8f", fg="white", font=("Arial", 12)).pack(pady=8)
    def export_payments_pdf():
        fname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if fname:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Payments List", ln=1, align="C")
            pdf.set_font("Arial", "B", 10)
            pdf.cell(50,8,"Customer",1); pdf.cell(30,8,"Amount",1); pdf.cell(30,8,"Mode",1); pdf.cell(50,8,"Ref",1); pdf.cell(30,8,"Date",1,ln=1)
            pdf.set_font("Arial", "", 10)
            for r in payment_list: pdf.cell(50,8,str(r['customer']),1); pdf.cell(30,8,str(r['amount']),1); pdf.cell(30,8,str(r['mode']),1); pdf.cell(50,8,str(r['ref']),1); pdf.cell(30,8,str(r['date']),1,ln=1)
            pdf.output(fname); messagebox.showinfo("Exported", f"Payments PDF saved as {fname}")
    tk.Button(payment_frame, text="Export Payments PDF", command=export_payments_pdf, bg="#264653", fg="white", font=("Arial", 12)).pack(pady=8)
refresh_payments()

def refresh_reports():
    for w in reports_frame.winfo_children(): w.destroy()
    tk.Label(reports_frame, text="Reports", font=("Arial", 22, "bold"), bg="#f7f7f7").pack(pady=10)
    rep_tabs = ttk.Notebook(reports_frame); rep_tabs.pack(fill="both", expand=True)
    sales_tab = tk.Frame(rep_tabs, bg="#f7f7f7"); rep_tabs.add(sales_tab, text="Sales Report")
    sales_tree = ttk.Treeview(sales_tab, columns=("Date","Customer","Product","Qty","Price","GST%","Discount(Rs.)","Discount(%)","Total","Type"), show="headings")
    for col in ("Date","Customer","Product","Qty","Price","GST%","Discount(Rs.)","Discount(%)","Total","Type"):
        sales_tree.heading(col, text=col); sales_tree.column(col, width=90)
    if os.path.exists(INVOICE_EXCEL):
        ws = load_workbook(INVOICE_EXCEL).active
        for r in ws.iter_rows(min_row=2, values_only=True): sales_tree.insert('', 'end', values=r)
    sales_tree.pack(fill="x", pady=8)
    def export_sales_pdf():
        fname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if fname:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Sales Report", ln=1, align="C")
            pdf.set_font("Arial", "B", 10)
            for col in ("Date","Customer","Product","Qty","Price","GST%","Discount(Rs.)","Discount(%)","Total","Type"):
                pdf.cell(25,8,col,1)
            pdf.ln(8)
            pdf.set_font("Arial", "", 10)
            if os.path.exists(INVOICE_EXCEL):
                ws = load_workbook(INVOICE_EXCEL).active
                for r in ws.iter_rows(min_row=2, values_only=True):
                    for v in r: pdf.cell(25,8,str(v),1)
                    pdf.ln(8)
            pdf.output(fname); messagebox.showinfo("Exported", f"Sales Report PDF saved as {fname}")
    tk.Button(sales_tab, text="Export Sales PDF", command=export_sales_pdf, bg="#264653", fg="white", font=("Arial", 12)).pack(pady=8)
    inv_tab = tk.Frame(rep_tabs, bg="#f7f7f7"); rep_tabs.add(inv_tab, text="Inventory")
    inv_tree = ttk.Treeview(inv_tab, columns=("Product","Stock"), show="headings")
    for col in ("Product","Stock"): inv_tree.heading(col, text=col); inv_tree.column(col, width=150)
    for p in load_json(PRODUCT_FILE): inv_tree.insert('', 'end', values=(p['name'], p['stock']))
    inv_tree.pack(fill="x", pady=8)
    def export_inv_pdf():
        fname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if fname:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Inventory Report", ln=1, align="C")
            pdf.set_font("Arial", "B", 10); pdf.cell(60,8,"Product",1); pdf.cell(60,8,"Stock",1,ln=1)
            pdf.set_font("Arial", "", 10)
            for p in load_json(PRODUCT_FILE): pdf.cell(60,8,p['name'],1); pdf.cell(60,8,str(p['stock']),1,ln=1)
            pdf.output(fname); messagebox.showinfo("Exported", f"Inventory PDF saved as {fname}")
    tk.Button(inv_tab, text="Export Inventory PDF", command=export_inv_pdf, bg="#264653", fg="white", font=("Arial", 12)).pack(pady=8)
    cust_tab = tk.Frame(rep_tabs, bg="#f7f7f7"); rep_tabs.add(cust_tab, text="Customer List")
    cust_tree = ttk.Treeview(cust_tab, columns=("Name","Address","Phone","Email"), show="headings")
    for col in ("Name","Address","Phone","Email"): cust_tree.heading(col, text=col); cust_tree.column(col, width=150)
    for c in load_json(CUSTOMER_FILE): cust_tree.insert('', 'end', values=(c['name'],c['address'],c['phone'],c.get('email','')))
    cust_tree.pack(fill="x", pady=8)
    def export_cust_pdf():
        fname = filedialog.asksaveasfilename(defaultextension=".pdf")
        if fname:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Customer List", ln=1, align="C")
            pdf.set_font("Arial", "B", 10); pdf.cell(60,8,"Name",1); pdf.cell(60,8,"Address",1); pdf.cell(60,8,"Phone",1,ln=1)
            pdf.set_font("Arial", "", 10)
            for c in load_json(CUSTOMER_FILE): pdf.cell(60,8,c['name'],1); pdf.cell(60,8,c['address'],1); pdf.cell(60,8,c['phone'],1,ln=1)
            pdf.output(fname); messagebox.showinfo("Exported", f"Customer PDF saved as {fname}")
    tk.Button(cust_tab, text="Export Customer PDF", command=export_cust_pdf, bg="#264653", fg="white", font=("Arial", 12)).pack(pady=8)
refresh_reports()

def refresh_settings():
    for w in settings_frame.winfo_children():
        w.destroy()
    tk.Label(settings_frame, text="Company Settings", font=("Arial", 22, "bold"), bg="#f0f0f0").pack(pady=20)
    f = tk.Frame(settings_frame, bg="#f0f0f0"); f.pack()
    fields = [
        ("Company Name", 0), ("GSTIN", 1), ("Address", 2), ("Contact", 3),
        ("Logo", 4), ("Bank Name", 5), ("Branch Name", 6), ("Bank Ac No", 7), ("IFSC Code", 8)
    ]
    entries = {}; settings = load_settings()
    for label, i in fields:
        tk.Label(f, text=label+":", font=("Arial", 12), bg="#f0f0f0").grid(row=i, column=0, padx=10, pady=7, sticky="e")
        ent = tk.Entry(f, font=("Arial", 12), width=38)
        ent.insert(0, settings.get(label,"")); ent.grid(row=i, column=1, padx=5, pady=7)
        entries[label] = ent
        if label == "Logo":
            def browse_logo(e=ent):
                fname = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
                if fname: e.delete(0, tk.END); e.insert(0, fname)
            tk.Button(f, text="Browse", command=browse_logo).grid(row=i, column=2, padx=4)
    tk.Button(f, text="Save Settings", bg="#4caf50", fg="#fff", font=("Arial", 12, "bold"),
              padx=20, pady=4, command=lambda: (
                  save_settings({k: e.get() for k, e in entries.items()}),
                  messagebox.showinfo("Saved", "Company info updated.")
              )).grid(row=9, column=0, columnspan=3, pady=14)
refresh_settings()

switch_frame(home_frame)
invoice_update_dropdowns()
refresh_home()
refresh_ledger()
refresh_payments()
refresh_reports()
refresh_settings()
root.mainloop()