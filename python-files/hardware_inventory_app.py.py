import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc
import datetime

# === SQL SERVER CONNECTION ===
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=localhost;"  # Change if needed
    "DATABASE=HardwareInventory;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# === LOGIN SCREEN ===
def login_screen():
    login = tk.Tk()
    login.title("Login")
    login.geometry("300x200")

    tk.Label(login, text="Username").pack(pady=5)
    username = tk.Entry(login)
    username.pack()

    tk.Label(login, text="Password").pack(pady=5)
    password = tk.Entry(login, show="*")
    password.pack()

    def check_login():
        user = username.get()
        pw = password.get()
        cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", (user, pw))
        if cursor.fetchone():
            login.destroy()
            main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(login, text="Login", command=check_login).pack(pady=10)
    login.mainloop()

# === MAIN APPLICATION ===
def main_app():
    root = tk.Tk()
    root.title("Hardware Inventory")
    root.geometry("950x550")

    # === Form Fields ===
    form = tk.Frame(root)
    form.pack(pady=10)

    tk.Label(form, text="Name").grid(row=0, column=0)
    tk.Label(form, text="Code").grid(row=0, column=1)
    tk.Label(form, text="Size").grid(row=0, column=2)
    tk.Label(form, text="Quantity").grid(row=0, column=3)
    tk.Label(form, text="Expiry Date (YYYY-MM-DD)").grid(row=0, column=4)

    name = tk.Entry(form)
    code = tk.Entry(form)
    size = tk.Entry(form)
    qty = tk.Entry(form)
    expiry = tk.Entry(form)

    name.grid(row=1, column=0)
    code.grid(row=1, column=1)
    size.grid(row=1, column=2)
    qty.grid(row=1, column=3)
    expiry.grid(row=1, column=4)

    def clear_fields():
        name.delete(0, tk.END)
        code.delete(0, tk.END)
        size.delete(0, tk.END)
        qty.delete(0, tk.END)
        expiry.delete(0, tk.END)

    def add_product():
        try:
            cursor.execute("""
                INSERT INTO Products (product_name, product_code, size, quantity, expiry_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name.get(), code.get(), size.get(), int(qty.get()), expiry.get()
            ))
            conn.commit()
            load_products()
            clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_product():
        selected = tree.focus()
        if selected:
            pid = tree.item(selected)["values"][0]
            cursor.execute("""
                UPDATE Products
                SET product_name=?, product_code=?, size=?, quantity=?, expiry_date=?
                WHERE product_id=?
            """, (
                name.get(), code.get(), size.get(), int(qty.get()), expiry.get(), pid
            ))
            conn.commit()
            load_products()
            clear_fields()

    def delete_product():
        selected = tree.focus()
        if selected:
            pid = tree.item(selected)["values"][0]
            cursor.execute("DELETE FROM Products WHERE product_id=?", (pid,))
            conn.commit()
            load_products()

    def on_select(event):
        selected = tree.focus()
        if selected:
            vals = tree.item(selected)["values"]
            name.delete(0, tk.END)
            code.delete(0, tk.END)
            size.delete(0, tk.END)
            qty.delete(0, tk.END)
            expiry.delete(0, tk.END)

            name.insert(0, vals[1])
            code.insert(0, vals[2])
            size.insert(0, vals[3])
            qty.insert(0, vals[4])
            expiry.insert(0, vals[5])

    def load_products():
        for i in tree.get_children():
            tree.delete(i)
        cursor.execute("SELECT * FROM Products")
        for row in cursor.fetchall():
            is_expired = datetime.datetime.strptime(str(row[5]), "%Y-%m-%d").date() < datetime.date.today()
            tag = "expired" if is_expired else ""
            tree.insert("", "end", values=row, tags=(tag,))

    # === Buttons ===
    tk.Button(root, text="Add Product", command=add_product).pack()
    tk.Button(root, text="Update Product", command=update_product).pack()
    tk.Button(root, text="Delete Product", command=delete_product).pack()

    # === Table ===
    columns = ("ID", "Name", "Code", "Size", "Quantity", "Expiry")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=tk.BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    tree.tag_configure("expired", background="red")

    load_products()
    root.mainloop()

# === START ===
login_screen()
