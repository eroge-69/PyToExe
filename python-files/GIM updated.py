import sqlite3
import hashlib
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import cv2
from pyzbar.pyzbar import decode
import openfoodfacts

OFF_API = openfoodfacts.API(user_agent="GroceryApp/1.0 (youremail@example.com)")
DB_NAME = "grocery_inventory_gui.db"

def create_tables():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            item_name TEXT NOT NULL,
            category TEXT,
            quantity TEXT,
            expiration_date TEXT,
            barcode TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS storage_options (
            name TEXT PRIMARY KEY
        )
        """)
        c.execute("SELECT COUNT(*) FROM storage_options")
        if c.fetchone()[0] == 0:
            for option in ['pantry', 'fridge', 'freezer']:
                c.execute("INSERT OR IGNORE INTO storage_options (name) VALUES (?)", (option,))
        conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, hash_password(password), "user"))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login_user(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?",
                  (username, hash_password(password)))
        result = c.fetchone()
        return result[0] if result else None

def add_item(user_id, name, category, quantity, expiration_date):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO inventory (user_id, item_name, category, quantity, expiration_date) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, category, quantity, expiration_date))
        conn.commit()

def get_inventory(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, item_name, category, quantity, expiration_date FROM inventory WHERE user_id=?", (user_id,))
        return c.fetchall()

def update_item(item_id, name, category, quantity, expiration_date):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
        UPDATE inventory SET item_name=?, category=?, quantity=?, expiration_date=?
        WHERE id=?
        """, (name, category, quantity, expiration_date, item_id))
        conn.commit()

def delete_item(user_id, item_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM inventory WHERE user_id = ? AND id = ?", (user_id, item_id))
        conn.commit()

def get_storage_options():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM storage_options")
        return [row[0] for row in c.fetchall()]

def add_storage_option(name):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO storage_options (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def delete_storage_option(name):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM storage_options WHERE name = ?", (name,))
        conn.commit()

#camera functions
def scan_barcode_and_fill():
    cap = cv2.VideoCapture(0)
    found_code = None
    cv2.namedWindow("Scan Barcode (press 'q' to cancel)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        for barcode in decode(frame):
            found_code = barcode.data.decode("utf-8")
            cv2.putText(frame, found_code, (barcode.rect.left, barcode.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            cv2.rectangle(frame, (barcode.rect.left, barcode.rect.top),
                          (barcode.rect.left + barcode.rect.width, barcode.rect.top + barcode.rect.height),
                          (0,255,0), 2)
        cv2.imshow("Scan Barcode (press 'q' to cancel)", frame)
        if found_code or cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if found_code:
        fill_fields_from_barcode(found_code)

def fill_fields_from_barcode(barcode):
    result = OFF_API.product.get(barcode, fields=["product_name"])
    product = result.get("product")
    if not product or not product.get("product_name"):
        messagebox.showerror("Not Found", f"No product info for barcode: {barcode}")
        return

    name = product["product_name"]
    grocery_name_entry.delete(0, tk.END)
    grocery_name_entry.insert(0, name)

    # Default quantity
    grocery_amount_entry.delete(0, tk.END)
    grocery_amount_entry.insert(0, "1")
    grocery_unit_var.set("lb")

    # Set expiration default to 7 days ahead
    exp = datetime.date.today() + datetime.timedelta(days=7)
    grocery_year_var.set(str(exp.year))
    grocery_month_var.set(f"{exp.month:02d}")
    grocery_day_var.set(f"{exp.day:02d}")

    messagebox.showinfo("Scanned", f"Found: {name}")

def build_gui():
    create_tables()
    app = tk.Tk()
    app.title("Grocery Inventory App")
    app.geometry("600x600")
    app.resizable(False, False)

    bg_color = "#D9EAD3"
    fg_color = "#4A635E"
    button_color = "#B4C9B5"
    button_hover = "#A1B299"
    entry_bg = "#F0F4EF"
    font_name = "Helvetica"
    font_size = 11

    style = ttk.Style()
    style.theme_use('default')
    style.configure("TLabel", background=bg_color, foreground=fg_color, font=(font_name, font_size))
    style.configure("TButton", background=button_color, foreground=fg_color, font=(font_name, font_size, "bold"))
    style.map("TButton", background=[('active', button_hover)])
    style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color, font=(font_name, font_size))
    style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg_color, font=(font_name, font_size))

    app.configure(bg=bg_color)

    current_user_id = [None]

    def show_frame(frame):
        frame.tkraise()

    container = tk.Frame(app, bg=bg_color)
    container.pack(fill="both", expand=True)

    login_frame = tk.Frame(container, bg=bg_color)
    home_frame = tk.Frame(container, bg=bg_color)
    groceries_frame = tk.Frame(container, bg=bg_color)
    storage_frame = tk.Frame(container, bg=bg_color)
    inventory_frame = tk.Frame(container, bg=bg_color)

    for frame in (login_frame, home_frame, groceries_frame, storage_frame, inventory_frame):
        frame.grid(row=0, column=0, sticky="nsew")

    #Login/Register Page
    ttk.Label(login_frame, text="Username").pack(pady=(80,5))
    username_entry = ttk.Entry(login_frame)
    username_entry.pack(ipady=6, ipadx=50, padx=100)
    ttk.Label(login_frame, text="Password").pack(pady=5)
    password_entry = ttk.Entry(login_frame, show="*")
    password_entry.pack(ipady=6, ipadx=50, padx=100)
    ttk.Button(login_frame, text="Login", command=lambda: login()).pack(pady=15)
    ttk.Button(login_frame, text="Register", command=lambda: register()).pack()

    #Home Page
    ttk.Label(home_frame, text="Home", font=(font_name, 18, "bold")).pack(pady=20)
    ttk.Button(home_frame, text="Manage Groceries", command=lambda: show_frame(groceries_frame)).pack(pady=10)
    ttk.Button(home_frame, text="Manage Storage", command=lambda: show_frame(storage_frame)).pack(pady=10)
    ttk.Button(home_frame, text="View Inventory", command=lambda: (refresh_inventory_tree(), show_frame(inventory_frame))).pack(pady=10)
    ttk.Button(home_frame, text="Logout", command=lambda: show_frame(login_frame)).pack(pady=30)

    #Groceries Page
    ttk.Label(groceries_frame, text="Add Grocery Item", font=(font_name, 16, "bold")).pack(pady=15)

    ttk.Label(groceries_frame, text="Item Name:").pack(pady=(10,2), anchor="center")
    grocery_name_entry = ttk.Entry(groceries_frame, font=(font_name, font_size))
    grocery_name_entry.pack(ipady=8, padx=30, fill="x")

    ttk.Label(groceries_frame, text="Quantity:").pack(pady=(10,2), anchor="center")
    grocery_qty_entry = ttk.Entry(groceries_frame, font=(font_name, font_size))
    grocery_qty_entry.pack(ipady=8, padx=30, fill="x")

    ttk.Label(groceries_frame, text="Amount:").pack(pady=(10,2), anchor="center")
    amount_frame = tk.Frame(groceries_frame, bg=bg_color)
    amount_frame.pack(ipady=8, padx=30, fill="x")

    grocery_amount_entry = ttk.Entry(amount_frame, font=(font_name, font_size))
    grocery_amount_entry.pack(side="left", fill="x", expand=True)

    grocery_unit_var = tk.StringVar()
    grocery_unit_menu = ttk.Combobox(amount_frame, textvariable=grocery_unit_var,
                                     values=["oz", "fl oz", "lb"], width=7,
                                     font=(font_name, font_size), state="readonly")
    grocery_unit_menu.pack(side="left", padx=(10, 0))
    grocery_unit_menu.current(0)

    ttk.Label(groceries_frame, text="Storage:").pack(pady=(10,2), anchor="center")
    grocery_storage_var = tk.StringVar()
    grocery_storage_menu = tk.OptionMenu(groceries_frame, grocery_storage_var, "")
    grocery_storage_menu.config(font=(font_name, font_size), bg=bg_color, fg=fg_color, highlightthickness=0)
    grocery_storage_menu.pack(ipady=8, padx=30, fill="x")

    ttk.Label(groceries_frame, text="Expiration Date:").pack(pady=(10,2), anchor="center")
    grocery_month_var = tk.StringVar(value="01")
    grocery_day_var = tk.StringVar(value="01")
    grocery_year_var = tk.StringVar(value=str(datetime.datetime.now().year))
    date_frame = tk.Frame(groceries_frame, bg=bg_color)
    tk.OptionMenu(date_frame, grocery_month_var, *["%02d" % m for m in range(1, 13)]).pack(side="left")
    tk.OptionMenu(date_frame, grocery_day_var, *["%02d" % d for d in range(1, 32)]).pack(side="left")
    tk.OptionMenu(date_frame, grocery_year_var, *[str(y) for y in range(2024, 2031)]).pack(side="left")
    date_frame.pack(pady=2)

    ttk.Button(groceries_frame, text="Submit", command=lambda: submit_grocery()).pack(pady=20, ipadx=10, ipady=6)
    ttk.Button(groceries_frame, text="Scan Barcode", command=scan_barcode_and_fill).pack(ipadx=10, ipady=6)
    ttk.Button(groceries_frame, text="Back", command=lambda: show_frame(home_frame)).pack(ipadx=10, ipady=6)

    #Storage Page
    ttk.Label(storage_frame, text="Manage Storage", font=(font_name, 16, "bold")).pack(pady=15)
    storage_entry = ttk.Entry(storage_frame, font=(font_name, font_size))
    storage_entry.pack(ipady=8, padx=30, fill="x")
    ttk.Button(storage_frame, text="Add", command=lambda: handle_add_storage()).pack(pady=15, ipadx=10, ipady=6)
    storage_list_frame = tk.Frame(storage_frame, bg=bg_color)
    storage_list_frame.pack(pady=10, padx=30, fill="both", expand=True)
    ttk.Button(storage_frame, text="Back", command=lambda: show_frame(home_frame)).pack(ipadx=10, ipady=6, pady=15)

    #Inventory Page
    ttk.Label(inventory_frame, text="Inventory", font=(font_name, 16, "bold")).pack(pady=15, anchor="center")
    inventory_search_entry = ttk.Entry(inventory_frame, font=(font_name, font_size))
    inventory_search_entry.pack(ipady=6, padx=30, fill="x")
    ttk.Button(inventory_frame, text="Search", command=lambda: search_inventory()).pack(pady=5, ipadx=10, ipady=6)

    columns = ("ID", "Name", "Category", "Quantity", "Expiration")
    inventory_tree = ttk.Treeview(inventory_frame, columns=columns, show="headings", height=15)
    for col in columns:
        inventory_tree.heading(col, text=col)
        inventory_tree.column(col, width=100, anchor="center")
    inventory_tree.tag_configure('red', background='#FFC1C1')
    inventory_tree.tag_configure('orange', background='#FFE6B3')
    inventory_tree.pack(padx=30, pady=10, fill="both", expand=True)

    action_buttons_frame = tk.Frame(inventory_frame, bg=bg_color)
    action_buttons_frame.pack(pady=5)
    ttk.Button(action_buttons_frame, text="Edit Selected", command=lambda: edit_selected_item()).pack(side="left", padx=10)
    ttk.Button(action_buttons_frame, text="Delete Selected", command=lambda: delete_selected_item()).pack(side="left", padx=10)
    ttk.Button(inventory_frame, text="Back", command=lambda: show_frame(home_frame)).pack(pady=15, ipadx=10, ipady=6)

    # --- GUI logic functions ---
    def login():
        user_id = login_user(username_entry.get(), password_entry.get())
        if user_id:
            current_user_id[0] = user_id
            refresh_storage_options()
            show_frame(home_frame)
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            if register_user(username, password):
                messagebox.showinfo("Success", "User registered successfully")
            else:
                messagebox.showerror("Error", "Username already exists")
        else:
            messagebox.showerror("Error", "Please enter username and password")

    def refresh_storage_options():
        options = get_storage_options()
        grocery_storage_var.set(options[0] if options else "")
        menu = grocery_storage_menu["menu"]
        menu.delete(0, "end")
        for option in options:
            menu.add_command(label=option, command=lambda value=option: grocery_storage_var.set(value))

        for widget in storage_list_frame.winfo_children():
            widget.destroy()
        for option in options:
            f = tk.Frame(storage_list_frame, bg=bg_color)
            f.pack(fill="x", pady=2)
            lbl = ttk.Label(f, text=option)
            lbl.pack(side="left", padx=5)
            btn = ttk.Button(f, text="Delete", command=lambda val=option: handle_delete_storage(val))
            btn.pack(side="right", padx=5)

    def handle_add_storage():
        name = storage_entry.get().strip()
        if name:
            if add_storage_option(name):
                messagebox.showinfo("Success", "Storage option added")
                storage_entry.delete(0, tk.END)
                refresh_storage_options()
            else:
                messagebox.showerror("Error", "Storage option already exists")
        else:
            messagebox.showerror("Error", "Please enter a storage name")

    def handle_delete_storage(name):
        if messagebox.askyesno("Confirm", f"Delete storage option '{name}'?"):
            delete_storage_option(name)
            refresh_storage_options()

    def submit_grocery():
        name = grocery_name_entry.get()
        qty = grocery_qty_entry.get()
        amount = grocery_amount_entry.get()
        unit = grocery_unit_var.get()
        storage = grocery_storage_var.get()
        month = grocery_month_var.get()
        day = grocery_day_var.get()
        year = grocery_year_var.get()
        exp_date = f"{year}-{month}-{day}"

        if not name:
            messagebox.showerror("Error", "Item name is required")
            return

        if not qty:
            messagebox.showerror("Error", "Quantity is required")
            return

        quantity = f"{qty} {amount} {unit}".strip()
        add_item(current_user_id[0], name, storage, quantity, exp_date)
        messagebox.showinfo("Success", "Item added to inventory")
        grocery_name_entry.delete(0, tk.END)
        grocery_qty_entry.delete(0, tk.END)
        grocery_amount_entry.delete(0, tk.END)

    def refresh_inventory_tree():
        for row in inventory_tree.get_children():
            inventory_tree.delete(row)
        today = datetime.datetime.now().date()
        for item in get_inventory(current_user_id[0]):
            try:
                exp = datetime.datetime.strptime(item[4], "%Y-%m-%d").date()
                days_left = (exp - today).days
            except:
                days_left = None
            tag = ''
            if days_left is not None:
                if days_left <= 3:
                    tag = 'red'
                elif days_left <= 7:
                    tag = 'orange'
            inventory_tree.insert("", "end", values=item, tags=(tag,))

    def search_inventory():
        term = inventory_search_entry.get().lower()
        for row in inventory_tree.get_children():
            inventory_tree.delete(row)
        today = datetime.datetime.now().date()
        for item in get_inventory(current_user_id[0]):
            if term in item[1].lower():
                try:
                    exp = datetime.datetime.strptime(item[4], "%Y-%m-%d").date()
                    days_left = (exp - today).days
                except:
                    days_left = None
                tag = ''
                if days_left is not None:
                    if days_left <= 3:
                        tag = 'red'
                    elif days_left <= 7:
                        tag = 'orange'
                inventory_tree.insert("", "end", values=item, tags=(tag,))

    def get_selected_item_id():
        selected = inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return None
        return inventory_tree.item(selected[0])["values"][0]

    def delete_selected_item():
        item_id = get_selected_item_id()
        if item_id and messagebox.askyesno("Confirm", "Delete selected item?"):
            delete_item(current_user_id[0], item_id)
            refresh_inventory_tree()
            messagebox.showinfo("Deleted", "Item deleted successfully")

    def edit_selected_item():
        item_id = get_selected_item_id()
        if not item_id:
            return
        item = next((i for i in get_inventory(current_user_id[0]) if i[0] == item_id), None)
        if not item:
            return

        edit_window = tk.Toplevel()
        edit_window.title("Edit Item")
        edit_window.geometry("400x400")
        edit_window.configure(bg=bg_color)

        tk.Label(edit_window, text="Name:", bg=bg_color).pack(pady=5)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, item[1])
        name_entry.pack()

        tk.Label(edit_window, text="Category:", bg=bg_color).pack(pady=5)
        category_var = tk.StringVar(value=item[2])
        category_menu = ttk.Combobox(edit_window, textvariable=category_var,
                                     values=get_storage_options(), state="readonly")
        category_menu.pack()

        tk.Label(edit_window, text="Quantity:", bg=bg_color).pack(pady=5)
        quantity_entry = ttk.Entry(edit_window)
        quantity_entry.insert(0, item[3])
        quantity_entry.pack()

        tk.Label(edit_window, text="Expiration Date (YYYY-MM-DD):", bg=bg_color).pack(pady=5)
        exp_entry = ttk.Entry(edit_window)
        exp_entry.insert(0, item[4])
        exp_entry.pack()

        def submit_edit():
            update_item(item_id, name_entry.get(), category_var.get(), quantity_entry.get(), exp_entry.get())
            refresh_inventory_tree()
            edit_window.destroy()
            messagebox.showinfo("Updated", "Item updated successfully")

        ttk.Button(edit_window, text="Save Changes", command=submit_edit).pack(pady=15)

    show_frame(login_frame)
    app.mainloop()

if __name__ == "__main__":
    build_gui()
