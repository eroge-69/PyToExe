import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import re

# --------------------- DATA STORE -----------------------
class DataStore:
    def __init__(self):
        self.customers = []
        self.vendors = []
        self.products = []
        self.invoices = []
        self.paid_invoices = []
        self.purchases = []
        self.next_customer_id = 1
        self.next_vendor_id = 1
        self.next_product_id = 1
        self.next_invoice_id = 1
        self.next_purchase_id = 1

    def add_customer(self, name, phone, email, address):
        if not name.strip():
            raise ValueError("Customer name cannot be empty.")
        for c in self.customers:
            if c["name"].strip().lower() == name.strip().lower():
                raise ValueError("Customer name already exists.")
        if phone and not re.match(r'^\+?[\d\s\-]+$', phone):
            raise ValueError("Invalid phone number format.")
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid email format.")
        self.customers.append({
            "id": self.next_customer_id,
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip()
        })
        self.next_customer_id += 1

    def add_vendor(self, name, phone, email, address):
        self.vendors.append({
            "id": self.next_vendor_id,
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip()
        })
        self.next_vendor_id += 1

    def add_product(self, name, selling_price, cost_price, stock):
        self.products.append({
            "id": self.next_product_id,
            "name": name.strip(),
            "price": selling_price,  # selling price
            "cost_price": cost_price,  # cost price
            "stock": stock
        })
        self.next_product_id += 1

    def add_invoice(self, customer_id, items, total, paid_amount, date, discount=0):
        paid_status = paid_amount >= total
        invoice = {
            "id": self.next_invoice_id,
            "customer_id": customer_id,
            "items": items,
            "total": total,
            "paid_status": paid_status,
            "date": date,
            "paid_amount": paid_amount,
            "payments": [],
            "discount": discount
        }
        if paid_amount > 0:
            invoice["payments"].append({"date": date, "amount": paid_amount})
        if paid_status:
            self.paid_invoices.append(invoice)
        else:
            self.invoices.append(invoice)
        self.next_invoice_id += 1

    def add_payment(self, invoice_id, amount):
        for i, inv in enumerate(self.invoices):
            if inv["id"] == invoice_id:
                new_paid = inv["paid_amount"] + amount
                if new_paid > inv["total"]:
                    raise ValueError("Payment exceeds total invoice amount.")
                paid_status = new_paid >= inv["total"]
                inv["paid_amount"] = new_paid
                inv["paid_status"] = paid_status
                inv["payments"].append({"date": datetime.datetime.now().strftime("%Y-%m-%d"), "amount": amount})
                if paid_status:
                    self.paid_invoices.append(self.invoices.pop(i))
                return
        for inv in self.paid_invoices:
            if inv["id"] == invoice_id:
                raise ValueError("Invoice already fully paid.")

    def get_customer(self, customer_id):
        for c in self.customers:
            if c["id"] == customer_id:
                return c
        return None

    def get_product(self, product_id):
        for p in self.products:
            if p["id"] == product_id:
                return p
        return None

    def update_product_stock(self, product_id, qty):
        for p in self.products:
            if p["id"] == product_id:
                p["stock"] -= qty
                if p["stock"] < 0:
                    p["stock"] = 0

    def increase_product_stock(self, product_id, qty):
        for p in self.products:
            if p["id"] == product_id:
                p["stock"] += qty

    def get_debit_invoices(self):
        return [inv for inv in self.invoices if not inv["paid_status"]]

    def get_invoice_by_id(self, invoice_id):
        for inv in self.invoices + self.paid_invoices:
            if inv["id"] == invoice_id:
                return inv
        return None

    def get_customer_previous_due(self, customer_id, current_items=None, current_total=None):
        due = 0
        for inv in self.invoices:
            if inv["customer_id"] == customer_id:
                if current_items and current_total:
                    if inv["items"] == current_items and inv["total"] == current_total:
                        continue
                due += inv["total"] - inv["paid_amount"]
        return due

    # --- Purchases ---
    def add_purchase(self, vendor_id, items, total, paid_amount, date, credit=False):
        purchase = {
            "id": self.next_purchase_id,
            "vendor_id": vendor_id,
            "items": items,
            "total": total,
            "paid_amount": paid_amount,
            "date": date,
            "credit": credit,
            "payments": []
        }
        if paid_amount > 0:
            purchase["payments"].append({"date": date, "amount": paid_amount})
        self.purchases.append(purchase)
        self.next_purchase_id += 1

    def add_purchase_payment(self, purchase_id, amount):
        for purchase in self.purchases:
            if purchase["id"] == purchase_id:
                new_paid = purchase["paid_amount"] + amount
                if new_paid > purchase["total"]:
                    raise ValueError("Payment exceeds total purchase amount.")
                purchase["paid_amount"] = new_paid
                purchase["payments"].append({"date": datetime.datetime.now().strftime("%Y-%m-%d"), "amount": amount})
                return
        raise ValueError("Purchase not found.")

    def get_purchase_by_id(self, purchase_id):
        for purchase in self.purchases:
            if purchase["id"] == purchase_id:
                return purchase
        return None

    def get_credit_purchases(self):
        return [p for p in self.purchases if p["total"] > p["paid_amount"]]

    # --- Profit and Cash Calculations ---
    def calculate_total_profit(self):
        profit = 0
        for inv in self.invoices + self.paid_invoices:
            for item in inv["items"]:
                pid, qty, selling_price = item
                product = self.get_product(pid)
                cost_price = product.get("cost_price", 0) if product else 0
                profit += (selling_price - cost_price) * qty
        return profit

    def calculate_cash_in_hand(self):
        received = sum(inv["paid_amount"] for inv in self.invoices + self.paid_invoices)
        paid = sum(p["paid_amount"] for p in self.purchases)
        return received - paid

# -------------- CUSTOMER & VENDOR FRAMES ---------------

class CustomerFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        form = tk.Frame(self)
        form.pack()

        self.name = tk.Entry(form)
        self.phone = tk.Entry(form)
        self.email = tk.Entry(form)
        self.address = tk.Entry(form)

        labels = ["Name", "Phone", "Email", "Address"]
        for i, (label, entry) in enumerate(zip(labels, [self.name, self.phone, self.email, self.address])):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry.grid(row=i, column=1)

        tk.Button(self, text="Add Customer", command=self.add_customer).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Phone", "Email", "Address"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.refresh()

    def add_customer(self):
        try:
            self.db.add_customer(self.name.get(), self.phone.get(), self.email.get(), self.address.get())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        for entry in [self.name, self.phone, self.email, self.address]:
            entry.delete(0, tk.END)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in self.db.customers:
            self.tree.insert("", "end", values=(c["id"], c["name"], c["phone"], c["email"], c["address"]))

class VendorFrame(CustomerFrame):
    def add_customer(self):
        try:
            self.db.add_vendor(self.name.get(), self.phone.get(), self.email.get(), self.address.get())
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        for entry in [self.name, self.phone, self.email, self.address]:
            entry.delete(0, tk.END)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for v in self.db.vendors:
            self.tree.insert("", "end", values=(v["id"], v["name"], v["phone"], v["email"], v["address"]))

# -------------- INVENTORY FRAME ---------------

class EditProductWindow(tk.Toplevel):
    def __init__(self, parent, db, product, refresh_callback):
        super().__init__(parent)
        self.db = db
        self.product = product
        self.refresh_callback = refresh_callback
        self.title(f"Edit Product #{product['id']}")
        self.geometry("300x250")

        tk.Label(self, text="Name").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.insert(0, product["name"])
        self.name_entry.pack()

        tk.Label(self, text="Selling Price").pack()
        self.price_entry = tk.Entry(self)
        self.price_entry.insert(0, str(product["price"]))
        self.price_entry.pack()

        tk.Label(self, text="Cost Price").pack()
        self.cost_price_entry = tk.Entry(self)
        self.cost_price_entry.insert(0, str(product["cost_price"]))
        self.cost_price_entry.pack()

        tk.Label(self, text="Stock").pack()
        self.stock_entry = tk.Entry(self)
        self.stock_entry.insert(0, str(product["stock"]))
        self.stock_entry.pack()

        tk.Button(self, text="Save", command=self.save).pack(pady=10)

    def save(self):
        try:
            name = self.name_entry.get().strip()
            price = float(self.price_entry.get())
            cost_price = float(self.cost_price_entry.get())
            stock = int(self.stock_entry.get())
            if not name:
                raise ValueError("Name cannot be empty.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.product["name"] = name
        self.product["price"] = price
        self.product["cost_price"] = cost_price
        self.product["stock"] = stock
        self.refresh_callback()
        self.destroy()

class InventoryFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        form = tk.Frame(self)
        form.pack()
        self.name = tk.Entry(form)
        self.price = tk.Entry(form)
        self.cost_price = tk.Entry(form)
        self.stock = tk.Entry(form)
        for i, (label, entry) in enumerate(zip(["Name", "Selling Price", "Cost Price", "Stock"], [self.name, self.price, self.cost_price, self.stock])):
            tk.Label(form, text=label).grid(row=i, column=0)
            entry.grid(row=i, column=1)

        tk.Button(self, text="Add Product", command=self.add_product).pack(pady=5)
        tk.Button(self, text="Edit Product", command=self.edit_product).pack(pady=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Selling Price", "Cost Price", "Stock"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.refresh()

        # Add profit and cash section
        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(pady=10)
        self.profit_label = tk.Label(self.stats_frame, text="Total Profit: $0.00")
        self.profit_label.pack()
        self.cash_label = tk.Label(self.stats_frame, text="Total Amount in Hand: $0.00")
        self.cash_label.pack()
        self.update_stats()

    def add_product(self):
        try:
            price = float(self.price.get())
            cost_price = float(self.cost_price.get())
            stock = int(self.stock.get())
        except:
            messagebox.showerror("Invalid", "Prices/Stock should be numbers")
            return
        self.db.add_product(self.name.get(), price, cost_price, stock)
        self.name.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.cost_price.delete(0, tk.END)
        self.stock.delete(0, tk.END)
        self.refresh()
        self.update_stats()

    def edit_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a product to edit.")
            return
        pid = int(self.tree.item(selected)["values"][0])
        product = self.db.get_product(pid)
        if product:
            EditProductWindow(self, self.db, product, self.refresh_and_update)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in self.db.products:
            self.tree.insert("", "end", values=(p["id"], p["name"], p["price"], p["cost_price"], p["stock"]))

    def refresh_and_update(self):
        self.refresh()
        self.update_stats()

    def update_stats(self):
        profit = self.db.calculate_total_profit()
        cash = self.db.calculate_cash_in_hand()
        self.profit_label.config(text=f"Total Profit: ${profit:.2f}")
        self.cash_label.config(text=f"Total Amount in Hand: ${cash:.2f}")

# -------------- PURCHASE FRAME ---------------

class PurchaseFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.items = []

        form = tk.Frame(self)
        form.pack()

        self.vendor_var = tk.StringVar()
        self.vendor_menu = ttk.Combobox(form, textvariable=self.vendor_var, state="readonly")
        tk.Label(form, text="Vendor").grid(row=0, column=0)
        self.vendor_menu.grid(row=0, column=1)

        self.product_var = tk.StringVar()
        self.product_menu = ttk.Combobox(form, textvariable=self.product_var, state="readonly")
        tk.Label(form, text="Product").grid(row=1, column=0)
        self.product_menu.grid(row=1, column=1)

        tk.Label(form, text="Quantity").grid(row=2, column=0)
        self.qty_entry = tk.Entry(form)
        self.qty_entry.grid(row=2, column=1)

        tk.Label(form, text="Purchase Price").grid(row=3, column=0)
        self.price_entry = tk.Entry(form)
        self.price_entry.grid(row=3, column=1)

        tk.Button(form, text="Add Item", command=self.add_item).grid(row=4, column=1, pady=5)

        self.items_tree = ttk.Treeview(self, columns=("Product", "Qty", "Price", "Total"), show="headings")
        for col in self.items_tree["columns"]:
            self.items_tree.heading(col, text=col)
        self.items_tree.pack(fill="x", pady=5)

        tk.Button(self, text="Save Purchase", command=self.save_purchase).pack(pady=5)

        # Add profit and cash section
        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(pady=10)
        self.profit_label = tk.Label(self.stats_frame, text="Total Profit: $0.00")
        self.profit_label.pack()
        self.cash_label = tk.Label(self.stats_frame, text="Total Amount in Hand: $0.00")
        self.cash_label.pack()
        self.update_stats()

        self.refresh_vendors()
        self.refresh_products()

    def refresh_vendors(self):
        self.vendor_menu["values"] = [f"{v['id']}: {v['name']}" for v in self.db.vendors]

    def refresh_products(self):
        self.product_menu["values"] = [f"{p['id']}: {p['name']} (${p['price']}) [{p['stock']} in stock]" for p in self.db.products]

    def add_item(self):
        if not self.product_var.get():
            return
        try:
            pid = int(self.product_var.get().split(":")[0])
            qty = int(self.qty_entry.get())
            price = float(self.price_entry.get())
            if qty <= 0 or price < 0:
                messagebox.showerror("Invalid Input", "Quantity and price must be positive.")
                return
        except:
            messagebox.showerror("Invalid Input", "Please enter valid numbers.")
            return
        product = self.db.get_product(pid)
        if product is None:
            messagebox.showerror("Error", "Product not found.")
            return
        total = price * qty
        self.items.append((product["name"], qty, price, total, pid))
        self.items_tree.insert("", "end", values=(product["name"], qty, price, total))
        self.qty_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def save_purchase(self):
        if not self.vendor_var.get():
            messagebox.showerror("Error", "Please select a vendor.")
            return
        if not self.items:
            messagebox.showerror("Error", "Add at least one item.")
            return

        vendor_id = int(self.vendor_var.get().split(":")[0])
        total = sum(item[3] for item in self.items)

        # Ask for amount paid (for credit purchase support)
        paid_amount = 0
        def get_paid():
            nonlocal paid_amount
            paid_str = paid_entry.get()
            try:
                paid_amount = float(paid_str)
                if paid_amount < 0 or paid_amount > total:
                    raise ValueError
            except:
                messagebox.showerror("Invalid Input", "Enter a valid paid amount.")
                return
            win.destroy()

        win = tk.Toplevel(self)
        win.title("Amount Paid")
        tk.Label(win, text=f"Total: ${total:.2f}\nEnter Amount Paid:").pack(padx=10, pady=10)
        paid_entry = tk.Entry(win)
        paid_entry.insert(0, "0")
        paid_entry.pack(padx=10, pady=5)
        tk.Button(win, text="OK", command=get_paid).pack(pady=10)
        win.grab_set()
        self.wait_window(win)

        # Save purchase
        items_for_db = [(item[4], item[1], item[2]) for item in self.items]
        credit = paid_amount < total
        self.db.add_purchase(vendor_id, items_for_db, total, paid_amount, datetime.datetime.now().strftime("%Y-%m-%d"), credit=credit)

        for item in self.items:
            pid = item[4]
            qty = item[1]
            price = item[2]
            self.db.increase_product_stock(pid, qty)
            product = self.db.get_product(pid)
            if product:
                product["cost_price"] = price  # Update cost price to latest purchase price

        self.items = []
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        self.refresh_products()
        self.update_stats()
        messagebox.showinfo("Saved", "Purchase recorded and inventory updated.")

    def update_stats(self):
        profit = self.db.calculate_total_profit()
        cash = self.db.calculate_cash_in_hand()
        self.profit_label.config(text=f"Total Profit: ${profit:.2f}")
        self.cash_label.config(text=f"Total Amount in Hand: ${cash:.2f}")

# -------------- PURCHASE INVOICE FRAME ---------------

class PurchaseInvoiceFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        tk.Label(self, text="Purchase Invoices", font=("Arial", 14, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Vendor", "Total", "Paid", "Due", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="View Details", command=self.view_details).pack(pady=5)

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for purchase in self.db.purchases:
            vendor = next((v for v in self.db.vendors if v["id"] == purchase["vendor_id"]), {"name": "Unknown"})
            due = purchase["total"] - purchase["paid_amount"]
            self.tree.insert("", "end", values=(purchase["id"], vendor["name"], purchase["total"], purchase["paid_amount"], f"{due:.2f}", purchase["date"]))

    def view_details(self):
        selected = self.tree.focus()
        if not selected:
            return
        purchase_id = int(self.tree.item(selected)["values"][0])
        purchase = self.db.get_purchase_by_id(purchase_id)
        if purchase:
            win = tk.Toplevel(self)
            win.title(f"Purchase #{purchase['id']}")
            vendor = next((v for v in self.db.vendors if v["id"] == purchase["vendor_id"]), {"name": "Unknown"})
            tk.Label(win, text=f"Vendor: {vendor['name']}").pack()
            tk.Label(win, text=f"Date: {purchase['date']}").pack()
            tk.Label(win, text=f"Total: ${purchase['total']:.2f}").pack()
            tk.Label(win, text=f"Paid: ${purchase['paid_amount']:.2f}").pack()
            tk.Label(win, text=f"Due: ${purchase['total'] - purchase['paid_amount']:.2f}").pack()
            tk.Label(win, text="Items:").pack()
            for item in purchase["items"]:
                pid, qty, price = item
                product = self.db.get_product(pid)
                pname = product["name"] if product else "Unknown"
                tk.Label(win, text=f"{pname} x{qty} @ ${price:.2f}").pack()

# -------------- CREDIT PURCHASE FRAME ---------------

class CreditPurchaseFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        tk.Label(self, text="Credit Purchases (Unpaid)", font=("Arial", 14, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Vendor", "Total", "Paid", "Due", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="Add Payment", command=self.add_payment).pack(pady=5)

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for purchase in self.db.get_credit_purchases():
            vendor = next((v for v in self.db.vendors if v["id"] == purchase["vendor_id"]), {"name": "Unknown"})
            due = purchase["total"] - purchase["paid_amount"]
            self.tree.insert("", "end", values=(purchase["id"], vendor["name"], purchase["total"], purchase["paid_amount"], f"{due:.2f}", purchase["date"]))

    def add_payment(self):
        selected = self.tree.focus()
        if not selected:
            return
        purchase_id = int(self.tree.item(selected)["values"][0])
        purchase = self.db.get_purchase_by_id(purchase_id)
        if not purchase:
            return

        win = tk.Toplevel(self)
        win.title("Add Payment")
        tk.Label(win, text=f"Due: ${purchase['total'] - purchase['paid_amount']:.2f}").pack()
        entry = tk.Entry(win)
        entry.pack()
        def save_payment():
            try:
                amt = float(entry.get())
                if amt <= 0 or amt > (purchase['total'] - purchase['paid_amount']):
                    raise ValueError
            except:
                messagebox.showerror("Invalid", "Enter a valid payment amount.")
                return
            self.db.add_purchase_payment(purchase_id, amt)
            win.destroy()
            self.refresh()
        tk.Button(win, text="Save", command=save_payment).pack()

# -------------- INVOICE FRAME WITH TABS ---------------

class SingleInvoiceTab(tk.Frame):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent)
        self.db = db
        self.refresh_callback = refresh_callback
        self.items = []

        form = tk.Frame(self)
        form.pack()

        self.customer_var = tk.StringVar()
        self.customer_menu = ttk.Combobox(form, textvariable=self.customer_var, state="readonly")
        tk.Label(form, text="Customer").grid(row=0, column=0)
        self.customer_menu.grid(row=0, column=1)

        self.product_var = tk.StringVar()
        self.product_menu = ttk.Combobox(form, textvariable=self.product_var, state="readonly")
        tk.Label(form, text="Product").grid(row=1, column=0)
        self.product_menu.grid(row=1, column=1)

        tk.Label(form, text="Quantity").grid(row=2, column=0)
        self.qty_entry = tk.Entry(form)
        self.qty_entry.grid(row=2, column=1)

        tk.Label(form, text="Amount Paid").grid(row=3, column=0)
        self.amount_paid_entry = tk.Entry(form)
        self.amount_paid_entry.insert(0, "0")
        self.amount_paid_entry.grid(row=3, column=1)

        tk.Label(form, text="Discount").grid(row=4, column=0)
        self.discount_entry = tk.Entry(form)
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=4, column=1)

        tk.Button(form, text="Apply Discount", command=self.apply_discount).grid(row=5, column=1, pady=5)
        tk.Button(form, text="Add Item", command=self.add_item).grid(row=6, column=1, pady=5)

        self.items_tree = ttk.Treeview(self, columns=("Product", "Qty", "Price", "Total"), show="headings")
        for col in self.items_tree["columns"]:
            self.items_tree.heading(col, text=col)
        self.items_tree.pack(fill="x", pady=5)

        self.total_label = tk.Label(self, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack()

        tk.Button(self, text="Save Invoice", command=self.save_invoice).pack(pady=5)
        tk.Button(self, text="Print Invoice", command=self.print_invoice).pack()

        self.refresh_customers()
        self.refresh_products()

    def refresh_customers(self):
        self.customer_menu["values"] = [f"{c['id']}: {c['name']}" for c in self.db.customers]

    def refresh_products(self):
        self.product_menu["values"] = [f"{p['id']}: {p['name']} (${p['price']}) [{p['stock']} in stock]" for p in self.db.products]

    def add_item(self):
        if not self.product_var.get():
            return
        try:
            pid = int(self.product_var.get().split(":")[0])
            qty = int(self.qty_entry.get())
            if qty <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be positive.")
                return
        except:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")
            return
        product = self.db.get_product(pid)
        if product is None:
            messagebox.showerror("Error", "Product not found.")
            return
        if qty > product["stock"]:
            messagebox.showerror("Stock Error", f"Only {product['stock']} items in stock.")
            return
        total = product["price"] * qty
        self.items.append((product["name"], qty, product["price"], total, pid))
        self.items_tree.insert("", "end", values=(product["name"], qty, product["price"], total))
        self.qty_entry.delete(0, tk.END)
        self.update_total()

    def apply_discount(self):
        try:
            discount = float(self.discount_entry.get())
            if discount < 0:
                raise ValueError
        except:
            messagebox.showerror("Invalid Input", "Discount must be a non-negative number.")
            return
        self.update_total()

    def update_total(self):
        total = sum(item[3] for item in self.items)
        try:
            discount = float(self.discount_entry.get())
        except:
            discount = 0
        total -= discount
        if total < 0:
            total = 0
        self.total_label.config(text=f"Total: ${total:.2f}")

    def save_invoice(self):
        if not self.customer_var.get():
            messagebox.showerror("Error", "Please select a customer.")
            return
        if not self.items:
            messagebox.showerror("Error", "Add at least one item.")
            return
        cid = int(self.customer_var.get().split(":")[0])
        try:
            discount = float(self.discount_entry.get())
        except:
            discount = 0
        total = sum(i[3] for i in self.items) - discount
        if total < 0:
            total = 0
        try:
            paid = float(self.amount_paid_entry.get())
            if paid < 0:
                raise ValueError
        except:
            messagebox.showerror("Invalid Input", "Amount paid must be a non-negative number.")
            return
        if paid > total:
            messagebox.showerror("Invalid Input", "Amount paid cannot exceed total.")
            return

        paid_status = paid >= total
        items_for_db = [(i[4], i[1], i[2]) for i in self.items]

        self.db.add_invoice(cid, items_for_db, total, paid, datetime.datetime.now().strftime("%Y-%m-%d"), discount=discount)

        for item in self.items:
            self.db.update_product_stock(item[4], item[1])

        self.items = []
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        self.total_label.config(text="Total: $0.00")
        self.amount_paid_entry.delete(0, tk.END)
        self.amount_paid_entry.insert(0, "0")
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")
        self.refresh_products()
        self.refresh_callback()
        messagebox.showinfo("Saved", f"Invoice Added\nPaid: ${paid:.2f}, Due: ${total - paid:.2f}")

    def print_invoice(self):
        try:
            discount = float(self.discount_entry.get())
        except:
            discount = 0
        total = sum(i[3] for i in self.items) - discount
        if total < 0:
            total = 0
        try:
            paid = float(self.amount_paid_entry.get())
        except:
            paid = 0
        due = total - paid

        if not self.customer_var.get():
            messagebox.showerror("Error", "Please select a customer.")
            return
        cid = int(self.customer_var.get().split(":")[0])

        items_for_db = [(i[4], i[1], i[2]) for i in self.items]
        previous_due = self.db.get_customer_previous_due(cid, current_items=items_for_db, current_total=total)

        output = "UNITED TRADERS\n" + "=" * 50 + "\n"
        output += "Itemized Invoice:\n\n"
        for i in self.items:
            output += f"{i[0]} x{i[1]} @ ${i[2]:.2f} = ${i[3]:.2f}\n"
        output += "\n" + "="*50 + "\n"
        output += f"DISCOUNT: ${discount:.2f}\n"
        output += f"TOTAL: ${total:.2f}\nPAID: ${paid:.2f}\nDUE: ${due:.2f}\n"
        output += f"PREVIOUS DUE: ${previous_due:.2f}\n"
        output += f"TOTAL DUE (Including This Bill): ${previous_due + due:.2f}"

        win = tk.Toplevel(self)
        win.title("Invoice Print Preview")
        win.geometry("500x400")
        txt = tk.Text(win, font=("Courier", 10), wrap="word")
        txt.insert("1.0", output)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

class InvoiceFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.tab_count = 0

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        tk.Button(self, text="Add New Bill Tab", command=self.add_tab).pack(pady=5)

        # Add initial tab
        self.add_tab()

    def add_tab(self):
        self.tab_count += 1
        tab = SingleInvoiceTab(self.notebook, self.db, self.refresh_all)
        self.notebook.add(tab, text=f"Bill {self.tab_count}")

    def refresh_all(self):
        # Refresh products in all tabs
        for child in self.notebook.winfo_children():
            if isinstance(child, SingleInvoiceTab):
                child.refresh_products()

# ------------------ EDIT INVOICE WINDOW ------------------

class EditInvoiceWindow(tk.Toplevel):
    def __init__(self, parent, db, invoice):
        super().__init__(parent)
        self.db = db
        self.invoice = invoice
        self.title(f"Edit Invoice #{invoice['id']}")
        self.geometry("500x400")

        tk.Label(self, text="UNITED TRADERS", font=("Arial", 16, "bold")).pack(pady=10)

        customer = self.db.get_customer(invoice["customer_id"])
        tk.Label(self, text=f"Customer: {customer['name']}").pack()
        tk.Label(self, text=f"Date: {invoice['date']}").pack()
        tk.Label(self, text=f"Total Amount: ${invoice['total']:.2f}").pack()
        tk.Label(self, text=f"Current Paid: ${invoice['paid_amount']:.2f}").pack()

        tk.Label(self, text="Add Payment Amount:").pack(pady=(10, 0))
        self.amount_paid_entry = tk.Entry(self)
        self.amount_paid_entry.insert(0, "0")
        self.amount_paid_entry.pack()

        tk.Button(self, text="Add Payment", command=self.save_update).pack(pady=10)

        self.items_tree = ttk.Treeview(self, columns=("Product", "Qty", "Price", "Total"), show="headings", height=5)
        for col in self.items_tree["columns"]:
            self.items_tree.heading(col, text=col)
        self.items_tree.pack()

        self.populate_items()

        tk.Label(self, text="Payment History:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.payments_tree = ttk.Treeview(self, columns=("Date", "Amount"), show="headings", height=5)
        self.payments_tree.heading("Date", text="Date")
        self.payments_tree.heading("Amount", text="Amount")
        self.payments_tree.pack()
        self.populate_payments()

    def populate_items(self):
        self.items_tree.delete(*self.items_tree.get_children())
        for item in self.invoice["items"]:
            pid, qty, price = item
            product = self.db.get_product(pid)
            total = qty * price
            self.items_tree.insert("", "end", values=(product["name"], qty, price, total))

    def populate_payments(self):
        self.payments_tree.delete(*self.payments_tree.get_children())
        for p in self.invoice.get("payments", []):
            self.payments_tree.insert("", "end", values=(p["date"], f"${p['amount']:.2f}"))

    def save_update(self):
        try:
            add_amount = float(self.amount_paid_entry.get())
            if add_amount <= 0:
                messagebox.showerror("Invalid Input", "Payment amount must be positive.")
                return
        except:
            messagebox.showerror("Error", "Invalid input.")
            return

        remaining_due = self.invoice["total"] - self.invoice["paid_amount"]
        if add_amount > remaining_due:
            messagebox.showerror("Error", f"Payment exceeds due amount (${remaining_due:.2f}).")
            return

        try:
            self.db.add_payment(self.invoice["id"], add_amount)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Saved", f"Payment of ${add_amount:.2f} added to Invoice #{self.invoice['id']}.")
        self.destroy()

# ------------------ DEBIT INVOICE FRAME ------------------

class DebitInvoiceFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        tk.Label(self, text="Debit (Unpaid) Invoices", font=("Arial", 14, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Customer", "Total", "Paid", "Due", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="Edit Invoice", command=self.edit_invoice).pack(pady=5)
        tk.Button(self, text="Print Invoice", command=self.print_invoice).pack(pady=5)

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for inv in self.db.get_debit_invoices():
            cust = self.db.get_customer(inv["customer_id"])
            due = inv["total"] - inv["paid_amount"]
            self.tree.insert("", "end", values=(inv["id"], cust["name"], inv["total"], inv["paid_amount"], f"{due:.2f}", inv["date"]))

    def edit_invoice(self):
        selected = self.tree.focus()
        if not selected:
            return
        inv_id = int(self.tree.item(selected)["values"][0])
        invoice = self.db.get_invoice_by_id(inv_id)
        if invoice:
            EditInvoiceWindow(self, self.db, invoice)
            self.after(100, self.refresh)

    def print_invoice(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select an invoice to print.")
            return
        inv_id = int(self.tree.item(selected)["values"][0])
        invoice = self.db.get_invoice_by_id(inv_id)
        if not invoice:
            messagebox.showerror("Error", "Invoice not found.")
            return

        customer = self.db.get_customer(invoice["customer_id"])
        output = "UNITED TRADERS\n" + "=" * 50 + "\n"
        output += f"Customer: {customer['name']}\nDate: {invoice['date']}\n\n"
        output += "Items:\n"
        for item in invoice["items"]:
            pid, qty, price = item
            product = self.db.get_product(pid)
            total = qty * price
            output += f"{product['name']} x{qty} @ ${price:.2f} = ${total:.2f}\n"
        output += "\n" + "="*50 + "\n"
        output += f"DISCOUNT: ${invoice.get('discount', 0):.2f}\n"
        output += f"TOTAL: ${invoice['total']:.2f}\nPAID: ${invoice['paid_amount']:.2f}\nDUE: ${invoice['total'] - invoice['paid_amount']:.2f}\n"

        win = tk.Toplevel(self)
        win.title("Invoice Print Preview")
        win.geometry("500x400")
        txt = tk.Text(win, font=("Courier", 10), wrap="word")
        txt.insert("1.0", output)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

# ------------------ PAID INVOICE FRAME ------------------

class PaidInvoiceFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        tk.Label(self, text="Paid Invoices", font=("Arial", 14, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Customer", "Total", "Paid", "Date"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self, text="Edit Invoice", command=self.edit_invoice).pack(pady=5)

        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for inv in self.db.paid_invoices:
            cust = self.db.get_customer(inv["customer_id"])
            self.tree.insert("", "end", values=(inv["id"], cust["name"], inv["total"], inv["paid_amount"], inv["date"]))

    def edit_invoice(self):
        selected = self.tree.focus()
        if not selected:
            return
        inv_id = int(self.tree.item(selected)["values"][0])
        invoice = self.db.get_invoice_by_id(inv_id)
        if invoice:
            EditInvoiceWindow(self, self.db, invoice)

# -------------- DASHBOARD FRAME ---------------

class DashboardFrame(tk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db

        tk.Label(self, text="Welcome to United Traders Accounting System", font=("Arial", 18)).pack(pady=20)

        self.stats_frame = tk.Frame(self)
        self.stats_frame.pack(pady=10)
        self.profit_label = tk.Label(self.stats_frame, text="Total Profit: $0.00", font=("Arial", 14, "bold"))
        self.profit_label.pack()
        self.cash_label = tk.Label(self.stats_frame, text="Total Amount in Hand: $0.00", font=("Arial", 14, "bold"))
        self.cash_label.pack()
        self.update_stats()

    def update_stats(self):
        profit = self.db.calculate_total_profit()
        cash = self.db.calculate_cash_in_hand()
        self.profit_label.config(text=f"Total Profit: ${profit:.2f}")
        self.cash_label.config(text=f"Total Amount in Hand: ${cash:.2f}")

# ------------------ MAIN APPLICATION ------------------

class AccountingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Accounting App")
        self.geometry("1200x700")
        self.db = DataStore()

        self.sidebar = tk.Frame(self, bg='gray20', width=200)
        self.sidebar.pack(side='left', fill='y')

        self.container = tk.Frame(self)
        self.container.pack(side='right', fill='both', expand=True)

        self.create_sidebar()
        self.switch_frame(DashboardFrame)

    def create_sidebar(self):
        pages = [
            ("Dashboard", DashboardFrame),
            ("Customers", CustomerFrame),
            ("Vendors", VendorFrame),
            ("Inventory", InventoryFrame),
            ("Purchases", PurchaseFrame),
            ("Purchase Invoices", PurchaseInvoiceFrame),
            ("Credit Purchases", CreditPurchaseFrame),
            ("Invoices", InvoiceFrame),
            ("Debits", DebitInvoiceFrame),
            ("Paid Invoices", PaidInvoiceFrame),
        ]
        for name, frame in pages:
            tk.Button(self.sidebar, text=name, fg="white", bg="gray20",
                      font=("Arial", 12), command=lambda f=frame: self.switch_frame(f)).pack(fill='x', padx=10, pady=2)

    def switch_frame(self, frame_class):
        for widget in self.container.winfo_children():
            widget.destroy()

        frame = frame_class(self.container, self.db)
        frame.pack(fill="both", expand=True)

# ------------------ LOGIN WINDOW ------------------

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x200")
        tk.Label(self, text="Username").pack(pady=(20, 5))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        tk.Label(self, text="Password").pack(pady=(10, 5))
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "admin" and password == "admin":
            self.destroy()
            app = AccountingApp()
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")

# ------------------ RUN THE APPLICATION ------------------

if __name__ == "__main__":
    LoginWindow().mainloop()