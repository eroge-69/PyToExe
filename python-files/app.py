# app.pyw
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import json
import os
import traceback

# ----------------- CONFIG -----------------
SPREADSHEET_ID = "1QPZb30gY3cQa-SleW2gd2mra4w9vHul2Lkb_8hLDdlk"
CREDENTIALS_FILE = "salesrecorderapp-dcb79bd9eb16.json"  # <- siguraduhin nandito ang tama mong JSON
CONFIG_FILE = "config.json"

DEFAULT_SERVICES = ["Print", "Xerox", "Scan", "Laminate", "ID Picture",
                    "Photo Print", "Typing Job", "Online Job"]

DEFAULT_PANINDA = {
    "Soft Drink": {},
    "Chichirya": {},
    "Sweets": {}
}

EMPLOYEES = ["Carlos", "Ryzza", "Stanner", "James"]

# ----------------- LOAD / SAVE CONFIG -----------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                services = data.get("services", DEFAULT_SERVICES)
                paninda = data.get("paninda", DEFAULT_PANINDA)
                # ensure structure: paninda[cat] -> {product: {"price":..., "stock":...}}
                for cat in DEFAULT_PANINDA:
                    if cat not in paninda:
                        paninda[cat] = {}
                return services, paninda
        except Exception:
            traceback.print_exc()
            return DEFAULT_SERVICES, DEFAULT_PANINDA
    else:
        return DEFAULT_SERVICES, DEFAULT_PANINDA

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"services": SERVICES, "paninda": PANINDA_CATEGORIES}, f, indent=4, ensure_ascii=False)

SERVICES, PANINDA_CATEGORIES = load_config()

# ----------------- GOOGLE SHEETS AUTH -----------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
except Exception as e:
    print("ERROR: Could not authenticate to Google Sheets. Check credentials file and spreadsheet ID.")
    print(e)
    raise SystemExit(1)

# Daily sheet (create if not exists)
today = datetime.now().strftime("%Y-%m-%d")
try:
    ws = spreadsheet.worksheet(today)
except gspread.exceptions.WorksheetNotFound:
    ws = spreadsheet.add_worksheet(title=today, rows="1200", cols="200")

# Inventory sheet (single table)
try:
    ws_inventory = spreadsheet.worksheet("Inventory")
except gspread.exceptions.WorksheetNotFound:
    ws_inventory = spreadsheet.add_worksheet(title="Inventory", rows="1000", cols="20")
    # Header: Category, Product, Price, Stock (master), Date, Time, Change, Stock After, Employee, Note
    ws_inventory.insert_row(["Category", "Product", "Price", "Stock", "Date", "Time", "Change", "Stock After", "Employee", "Note"], 1)

# ----------------- HEADERS for daily sheet -----------------
def build_headers():
    headers = []
    # Services: each service has Price column (we will write total for that service) and Time
    for s in SERVICES:
        headers.append(s)            # we'll store total amount for that service in its column
        headers.append(s + " Time")
    # For paninda we create per category: Name, Price, Time (we store totals in Price column)
    for cat in PANINDA_CATEGORIES.keys():
        headers.append(cat + " Name")
        headers.append(cat + " Price")
        headers.append(cat + " Time")
    # Extra columns
    headers.append("School Supplies Name")
    headers.append("School Supplies Price")
    headers.append("School Supplies Time")
    headers.append("Expenses Reason")
    headers.append("Expenses Cost")
    headers.append("Expenses Time")
    headers.append("Employee")

    # Insert or replace header row to match current buttons/config
    existing = ws.row_values(1)
    if not existing:
        ws.insert_row(headers, 1)
    else:
        # resize and replace row 1 to avoid leftover columns mismatch
        try:
            ws.resize(rows=1200, cols=len(headers) + 10)
        except Exception:
            pass
        try:
            ws.delete_rows(1)
        except Exception:
            pass
        ws.insert_row(headers, 1)

build_headers()

# ----------------- HELPERS -----------------
def get_next_row(col_idx):
    col_vals = ws.col_values(col_idx)
    return max(3, len(col_vals) + 1)

def append_inventory_record(category, product, change_qty, employee, note=""):
    """Record a change (positive for restock, negative for sale) in Inventory sheet and update stock cell in inventory file and config"""
    # Update master PANINDA_CATEGORIES data, then write record
    details = PANINDA_CATEGORIES.get(category, {}).get(product)
    stock_after = details["stock"] if details else 0
    now = datetime.now()
    row = [
        category,
        product,
        details["price"] if details else "",
        stock_after,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        change_qty,
        stock_after,
        employee,
        note
    ]
    try:
        ws_inventory.append_row(row)
    except Exception:
        # fallback: try to insert later
        traceback.print_exc()

def record_sale(employee, item_name, col_idx_price, col_idx_time,
                col_idx_name=None, fixed_price=None, col_idx_stock=None, qty=1, category=None):
    """Writes sale into daily sheet:
       - for services: item_name is service name, fixed_price (or prompt) is price for single unit; qty not used (always 1)
       - for paninda: item_name is product name, fixed_price is price per unit, qty used (can be >1). We write total = price*qty to the Price column.
       Also updates inventory (PANINDA_CATEGORIES) and inventory sheet when applicable.
    """
    try:
        # price for one item
        price_per = fixed_price
        if price_per is None:
            price_per = simpledialog.askfloat("Price", f"Enter price for {item_name}:")
        if price_per is None:
            return False

        row = get_next_row(col_idx_price)
        # if we have qty (paninda) write total amount (price_per * qty) into the Price column so totals add up
        total_amount = float(price_per) * int(qty)
        if col_idx_name:
            ws.update_cell(row, col_idx_name, item_name)
        ws.update_cell(row, col_idx_price, total_amount)
        ws.update_cell(row, col_idx_time, datetime.now().strftime("%H:%M:%S"))

        # Deduct stock if provided (paninda)
        if category and item_name and qty:
            # decrease in-memory stock
            try:
                PANINDA_CATEGORIES[category][item_name]["stock"] -= int(qty)
                if PANINDA_CATEGORIES[category][item_name]["stock"] < 0:
                    PANINDA_CATEGORIES[category][item_name]["stock"] = 0
            except Exception:
                pass
            # record inventory change (negative)
            append_inventory_record(category, item_name, -int(qty), employee, note="sale")
            save_config()  # persist new stock
            # Also update master stock display inside daily sheet row 2 for that category's "Stock" column if present
            # (we don't rely on exact column indices here; refresh_buttons will update UI)
        # write employee in the last column (Employee)
        emp_col = len(ws.row_values(1))
        ws.update_cell(row, emp_col, employee)
        return True
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error saving sale", str(e))
        return False

# ----------------- GUI -----------------
root = tk.Tk()
root.title("Sales Recorder")
root.geometry("1700x900")

# Employee select
top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=6)
tk.Label(top_frame, text="Employee:").pack(side="left")
emp_var = tk.StringVar(value=EMPLOYEES[0])
emp_cb = ttk.Combobox(top_frame, values=EMPLOYEES, textvariable=emp_var, state="readonly", width=20)
emp_cb.pack(side="left")

# ----------- Buttons -----------
def add_service():
    new_service = simpledialog.askstring("Add Service", "Enter new service name:")
    if not new_service:
        return
    price = simpledialog.askfloat("Service Price", f"Enter default price for {new_service} (optional, can be changed each time):")
    # Add to SERVICES but don't change existing daily header behavior (we keep SERVICE columns)
    if new_service not in SERVICES:
        SERVICES.append(new_service)
    # update headers and buttons
    save_config()
    build_headers()
    refresh_buttons()
    messagebox.showinfo("Added", f"Service '{new_service}' added. You can still enter a different price when recording.")

def add_product():
    form = tk.Toplevel(root)
    form.title("Add Product")
    form.resizable(False, False)

    tk.Label(form, text="Category:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
    cat_var = tk.StringVar(value=list(PANINDA_CATEGORIES.keys())[0])
    cat_cb = ttk.Combobox(form, values=list(PANINDA_CATEGORIES.keys()), textvariable=cat_var, state="readonly", width=30)
    cat_cb.grid(row=0, column=1, padx=6, pady=4)

    tk.Label(form, text="Product Name:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    name_var = tk.StringVar()
    tk.Entry(form, textvariable=name_var, width=32).grid(row=1, column=1, padx=6, pady=4)

    tk.Label(form, text="Price:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
    price_var = tk.DoubleVar(value=0.0)
    tk.Entry(form, textvariable=price_var, width=32).grid(row=2, column=1, padx=6, pady=4)

    tk.Label(form, text="Initial Stock:").grid(row=3, column=0, sticky="w", padx=6, pady=4)
    stock_var = tk.IntVar(value=0)
    tk.Entry(form, textvariable=stock_var, width=32).grid(row=3, column=1, padx=6, pady=4)

    def submit():
        cat = cat_var.get()
        name = name_var.get().strip()
        try:
            price = float(price_var.get())
        except Exception:
            messagebox.showerror("Error", "Invalid price")
            return
        try:
            stock = int(stock_var.get())
        except Exception:
            messagebox.showerror("Error", "Invalid stock")
            return
        if not cat or not name:
            messagebox.showerror("Error", "Category and product name required")
            return
        if name in PANINDA_CATEGORIES.get(cat, {}):
            if not messagebox.askyesno("Overwrite", f"{name} already exists in {cat}. Overwrite?"):
                return
        PANINDA_CATEGORIES[cat][name] = {"price": price, "stock": stock}
        save_config()
        # record initial inventory addition to Inventory sheet
        append_inventory_record(cat, name, stock, emp_var.get(), note="initial add")
        build_headers()
        refresh_buttons()
        form.destroy()
        messagebox.showinfo("Added", f"{name} added to {cat} (stock {stock}).")

    tk.Button(form, text="Save", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

def remove_product():
    # simple remove flow
    cat = simpledialog.askstring("Remove Product", f"Enter category {list(PANINDA_CATEGORIES.keys())}:")
    if not cat or cat not in PANINDA_CATEGORIES:
        messagebox.showerror("Error", "Invalid category")
        return
    prod = simpledialog.askstring("Remove Product", "Enter product name to remove:")
    if not prod:
        return
    if prod in PANINDA_CATEGORIES[cat]:
        if messagebox.askyesno("Confirm", f"Remove {prod} from {cat}?"):
            del PANINDA_CATEGORIES[cat][prod]
            save_config()
            refresh_buttons()
            messagebox.showinfo("Removed", f"{prod} removed from {cat}.")

def restock_product():
    form = tk.Toplevel(root)
    form.title("Restock Product")
    form.resizable(False, False)

    tk.Label(form, text="Category:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
    cat_var = tk.StringVar(value=list(PANINDA_CATEGORIES.keys())[0])
    cat_cb = ttk.Combobox(form, values=list(PANINDA_CATEGORIES.keys()), textvariable=cat_var, state="readonly", width=30)
    cat_cb.grid(row=0, column=1, padx=6, pady=4)

    tk.Label(form, text="Product:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    prod_var = tk.StringVar()
    prod_cb = ttk.Combobox(form, textvariable=prod_var, state="readonly", width=30)
    prod_cb.grid(row=1, column=1, padx=6, pady=4)

    def update_products(*args):
        c = cat_var.get()
        prod_cb["values"] = list(PANINDA_CATEGORIES.get(c, {}).keys())

    cat_var.trace("w", lambda *a: update_products())
    update_products()

    tk.Label(form, text="Qty to add:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
    qty_var = tk.IntVar(value=1)
    tk.Entry(form, textvariable=qty_var, width=32).grid(row=2, column=1, padx=6, pady=4)

    def submit_restock():
        c = cat_var.get()
        p = prod_var.get()
        try:
            qty = int(qty_var.get())
        except Exception:
            messagebox.showerror("Error", "Invalid quantity")
            return
        if not c or not p or qty <= 0:
            messagebox.showerror("Error", "Complete fields")
            return
        PANINDA_CATEGORIES[c][p]["stock"] = PANINDA_CATEGORIES[c][p].get("stock", 0) + qty
        save_config()
        append_inventory_record(c, p, qty, emp_var.get(), note="restock")
        refresh_buttons()
        form.destroy()
        messagebox.showinfo("Restocked", f"Added {qty} to {p} (category {c}).")

    tk.Button(form, text="Restock", command=submit_restock).grid(row=3, column=0, columnspan=2, pady=8)

def school_supplies():
    emp = emp_var.get()
    item = simpledialog.askstring("School Supplies", "Enter item name:")
    if not item:
        return
    price = simpledialog.askfloat("Price", f"Enter price for {item}:")
    if price is None:
        return
    headers = ws.row_values(1)
    try:
        idx_name = headers.index("School Supplies Name") + 1
        idx_price = headers.index("School Supplies Price") + 1
        idx_time = headers.index("School Supplies Time") + 1
    except ValueError:
        build_headers()
        headers = ws.row_values(1)
        idx_name = headers.index("School Supplies Name") + 1
        idx_price = headers.index("School Supplies Price") + 1
        idx_time = headers.index("School Supplies Time") + 1
    record_sale(emp, item, idx_price, idx_time, idx_name, fixed_price=price)
    messagebox.showinfo("Saved", f"{item} - ₱{price} recorded for {emp}")

def add_expenses():
    emp = emp_var.get()
    reason = simpledialog.askstring("Expenses", "Enter reason for expense:")
    if not reason:
        return
    cost = simpledialog.askfloat("Expenses", "Enter cost:")
    if cost is None:
        return
    headers = ws.row_values(1)
    try:
        idx_reason = headers.index("Expenses Reason") + 1
        idx_cost = headers.index("Expenses Cost") + 1
        idx_time = headers.index("Expenses Time") + 1
    except ValueError:
        build_headers()
        headers = ws.row_values(1)
        idx_reason = headers.index("Expenses Reason") + 1
        idx_cost = headers.index("Expenses Cost") + 1
        idx_time = headers.index("Expenses Time") + 1
    row = get_next_row(idx_cost)
    ws.update_cell(row, idx_reason, reason)
    ws.update_cell(row, idx_cost, cost)
    ws.update_cell(row, idx_time, datetime.now().strftime("%H:%M:%S"))
    ws.update_cell(row, len(headers), emp)
    messagebox.showinfo("Saved", f"Expense {reason} - ₱{cost} recorded.")

def view_total():
    # Read row 2 totals where formulas might exist — fallback to summing recent rows
    headers = ws.row_values(1)
    row2 = ws.row_values(2)
    try:
        # Some columns are service columns (exact names) and some are category Price columns (end with " Price")
        total_services = 0.0
        total_paninda = 0.0
        total_expenses = 0.0
        for i, h in enumerate(headers):
            # index in python lists is i, sheet is i+1
            val = 0.0
            try:
                if i < len(row2) and row2[i] != "":
                    val = float(row2[i])
            except:
                val = 0.0
            if h in SERVICES:
                total_services += val
            elif h.endswith(" Price") and "School Supplies" not in h:
                total_paninda += val
            elif h == "Expenses Cost":
                total_expenses += val
        net = total_services + total_paninda - total_expenses
        messagebox.showinfo("Totals", f"Services: ₱{total_services:.2f}\nPaninda: ₱{total_paninda:.2f}\nExpenses: ₱{total_expenses:.2f}\n\nNet: ₱{net:.2f}")
    except Exception:
        traceback.print_exc()
        messagebox.showwarning("Totals", "No totals available yet or parsing error.")

def view_inventory():
    # popup treeview showing current PANINDA_CATEGORIES with price & stock
    top = tk.Toplevel(root)
    top.title("Inventory")
    cols = ("Category", "Product", "Price", "Stock")
    tree = ttk.Treeview(top, columns=cols, show="headings", height=20)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=150)
    tree.pack(fill="both", expand=True)
    for cat, products in PANINDA_CATEGORIES.items():
        for prod, details in products.items():
            tree.insert("", tk.END, values=(cat, prod, details.get("price", 0), details.get("stock", 0)))

# Buttons on topbar
tk.Button(top_frame, text="Add Service", command=add_service).pack(side="left", padx=5)
tk.Button(top_frame, text="Add Product", command=add_product).pack(side="left", padx=5)
tk.Button(top_frame, text="Remove Product", command=remove_product).pack(side="left", padx=5)
tk.Button(top_frame, text="Restock", command=restock_product).pack(side="left", padx=5)
tk.Button(top_frame, text="School Supplies", command=school_supplies).pack(side="left", padx=5)
tk.Button(top_frame, text="Expenses", command=add_expenses, bg="red", fg="white").pack(side="left", padx=5)
tk.Button(top_frame, text="View Total", command=view_total, bg="green", fg="white").pack(side="left", padx=5)
tk.Button(top_frame, text="View Inventory", command=view_inventory, bg="orange", fg="black").pack(side="left", padx=5)

# Frames for services and paninda
svc_frame = tk.LabelFrame(root, text="Services", padx=6, pady=6)
svc_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
pan_frame = tk.LabelFrame(root, text="Paninda", padx=6, pady=6)
pan_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

pan_frames = {}
for cat in PANINDA_CATEGORIES:
    frame = tk.LabelFrame(pan_frame, text=cat, padx=6, pady=6)
    frame.pack(side="left", padx=8, fill="y")
    pan_frames[cat] = frame

# Button handlers
def button_click_service(name, col_idx_price, col_idx_time):
    emp = emp_var.get()
    # ask price each time for services
    ok = record_sale(emp, name, col_idx_price, col_idx_time, col_idx_name=None, fixed_price=None, qty=1)
    if ok:
        messagebox.showinfo("Saved", f"{name} recorded for {emp}")

def button_click_paninda(name, col_idx_name, col_idx_price, col_idx_time, col_idx_stock, price, stock, category):
    emp = emp_var.get()
    if stock <= 0:
        messagebox.showwarning("Out of Stock", f"{name} is out of stock!")
        return
    qty = simpledialog.askinteger("Quantity", f"How many {name} to sell?", minvalue=1, initialvalue=1)
    if qty is None:
        return
    if qty > stock:
        messagebox.showerror("Not enough stock", f"Only {stock} left.")
        return
    # write sale: write name, write total price (price * qty) into price column
    ok = record_sale(emp, name, col_idx_price, col_idx_time, col_idx_name=col_idx_name, fixed_price=price, col_idx_stock=col_idx_stock, qty=qty, category=category)
    if ok:
        # record inventory change (already done inside record_sale via append_inventory_record)
        messagebox.showinfo("Saved", f"{qty} x {name} recorded for {emp}")
        # update display buttons to reflect new stock
        refresh_buttons()

# Refresh buttons builds buttons and calculates the mapping of columns
def refresh_buttons():
    # clear frames
    for w in svc_frame.winfo_children():
        w.destroy()
    for frame in pan_frames.values():
        for w in frame.winfo_children():
            w.destroy()

    # Build service buttons: we must compute column indices consistent with build_headers()
    col_index = 1
    for s in SERVICES:
        btn = tk.Button(svc_frame, text=s, width=22, height=2,
                        command=lambda n=s, c1=col_index, c2=col_index+1: button_click_service(n, c1, c2))
        btn.pack(pady=4)
        col_index += 2

    # Build paninda columns: for each category allocate Name, Price, Time columns in the daily sheet layout
    for cat, items in PANINDA_CATEGORIES.items():
        col_idx_name = col_index
        col_idx_price = col_index + 1
        col_idx_time = col_index + 2
        col_idx_stock = col_index + 3  # not necessarily written to daily sheet row 2, but reserved for UI/mapping
        for item, details in items.items():
            price = details.get("price", 0)
            stock = details.get("stock", 0)
            btn_text = f"{item} — ₱{price} [Stock:{stock}]"
            btn = tk.Button(pan_frames[cat], text=btn_text, width=28, height=2,
                            command=lambda n=item, c1=col_idx_name, c2=col_idx_price, c3=col_idx_time, c4=col_idx_stock, p=price, s=stock, cat=cat:
                            button_click_paninda(n, c1, c2, c3, c4, p, s, cat))
            btn.pack(pady=3)
        col_index += 4

# initial build
refresh_buttons()

# ensure config saved on exit
def on_close():
    try:
        save_config()
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

