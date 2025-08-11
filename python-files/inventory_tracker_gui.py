import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from hashlib import sha256
import re

# Database Setup
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 quantity INTEGER,
                 price REAL,
                 category TEXT)''')
    conn.commit()
    conn.close()

# Main Application
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.current_user = None
        init_db()
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Inventory Tracker", font=("Helvetica", 24, "bold"), bg="#f0f0f0").pack(pady=20)
        
        tk.Label(self.root, text="Username", font=("Helvetica", 12), bg="#f0f0f0").pack()
        self.username_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.username_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password", font=("Helvetica", 12), bg="#f0f0f0").pack()
        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 12))
        self.password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=10)
        tk.Button(self.root, text="Create Account", command=self.show_create_account, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)

    def show_create_account(self):
        self.clear_window()
        tk.Label(self.root, text="Create Account", font=("Helvetica", 24, "bold"), bg="#f0f0f0").pack(pady=20)
        
        tk.Label(self.root, text="Username", font=("Helvetica", 12), bg="#f0f0f0").pack()
        self.new_username_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.new_username_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password", font=("Helvetica", 12), bg="#f0f0f0").pack()
        self.new_password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 12))
        self.new_password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Create", command=self.create_account, bg="#4CAF50", fg="white", font=("Helvetica", 12)).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.show_login_screen, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = sha256(self.password_entry.get().encode()).hexdigest()
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            self.current_user = username
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def create_account(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        if not re.match("^[a-zA-Z0-9_]+$", username):
            messagebox.showerror("Error", "Username can only contain letters, numbers, and underscores")
            return
        
        password_hash = sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()

    def show_main_screen(self):
        self.clear_window()
        tk.Label(self.root, text=f"Welcome, {self.current_user}", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.show_login_screen, bg="#F44336", fg="white", font=("Helvetica", 12)).pack(anchor="ne", padx=10)
        
        # Inventory Form
        form_frame = tk.Frame(self.root, bg="#f0f0f0")
        form_frame.pack(pady=10, fill="x", padx=10)
        
        tk.Label(form_frame, text="Name", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Quantity", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5)
        self.quantity_entry = tk.Entry(form_frame)
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Price", bg="#f0f0f0").grid(row=0, column=4, padx=5, pady=5)
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(form_frame, text="Category", bg="#f0f0f0").grid(row=0, column=6, padx=5, pady=5)
        self.category_entry = tk.Entry(form_frame)
        self.category_entry.grid(row=0, column=7, padx=5, pady=5)
        
        tk.Button(form_frame, text="Add Item", command=self.add_item, bg="#4CAF50", fg="white").grid(row=1, column=0, columnspan=8, pady=10)
        
        # Search
        tk.Label(form_frame, text="Search", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(form_frame)
        self.search_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        tk.Button(form_frame, text="Search", command=self.search_items, bg="#2196F3", fg="white").grid(row=2, column=4, padx=5, pady=5)
        
        # Inventory Table
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Quantity", "Price", "Category"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Category", text="Category")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Button(self.root, text="Edit Selected", command=self.edit_item, bg="#FFC107", fg="black").pack(side="left", padx=5)
        tk.Button(self.root, text="Delete Selected", command=self.delete_item, bg="#F44336", fg="white").pack(side="left", padx=5)
        
        self.load_inventory()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_item(self):
        name = self.name_entry.get()
        try:
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
            category = self.category_entry.get()
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers")
            return
        
        if not name or not category:
            messagebox.showerror("Error", "All fields are required")
            return
        
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("INSERT INTO inventory (name, quantity, price, category) VALUES (?, ?, ?, ?)", 
                  (name, quantity, price, category))
        conn.commit()
        conn.close()
        
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.load_inventory()

    def load_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
            if row[2] < 5:  # Low stock alert
                messagebox.showwarning("Low Stock", f"Item '{row[1]}' has low stock: {row[2]}")
        conn.close()

    def search_items(self):
        query = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", 
                  (f"%{query}%", f"%{query}%"))
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an item to edit")
            return
        item = self.tree.item(selected[0])["values"]
        self.clear_window()
        
        tk.Label(self.root, text="Edit Item", font=("Helvetica", 24, "bold"), bg="#f0f0f0").pack(pady=20)
        
        tk.Label(self.root, text="Name", bg="#f0f0f0").pack()
        self.edit_name_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.edit_name_entry.insert(0, item[1])
        self.edit_name_entry.pack(pady=5)
        
        tk.Label(self.root, text="Quantity", bg="#f0f0f0").pack()
        self.edit_quantity_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.edit_quantity_entry.insert(0, item[2])
        self.edit_quantity_entry.pack(pady=5)
        
        tk.Label(self.root, text="Price", bg="#f0f0f0").pack()
        self.edit_price_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.edit_price_entry.insert(0, item[3])
        self.edit_price_entry.pack(pady=5)
        
        tk.Label(self.root, text="Category", bg="#f0f0f0").pack()
        self.edit_category_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.edit_category_entry.insert(0, item[4])
        self.edit_category_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save", command=lambda: self.save_edit(item[0]), bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Cancel", command=self.show_main_screen, bg="#F44336", fg="white").pack(pady=5)

    def save_edit(self, item_id):
        try:
            name = self.edit_name_entry.get()
            quantity = int(self.edit_quantity_entry.get())
            price = float(self.edit_price_entry.get())
            category = self.edit_category_entry.get()
        except ValueError:
            messagebox.showerror("Error", "Quantity and Price must be numbers")
            return
        
        if not name or not category:
            messagebox.showerror("Error", "All fields are required")
            return
        
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("UPDATE inventory SET name = ?, quantity = ?, price = ?, category = ? WHERE id = ?", 
                  (name, quantity, price, category, item_id))
        conn.commit()
        conn.close()
        self.show_main_screen()

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an item to delete")
            return
        item_id = self.tree.item(selected[0])["values"][0]
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        self.load_inventory()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()