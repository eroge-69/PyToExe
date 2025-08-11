import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class InventoryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adil Inventory Management Software")
        self.root.geometry("1000x700")

        # Initialize JSON storage
        self.data_file = "inventory.json"
        self.load_data()

        # GUI Components
        self.setup_gui()

    def load_data(self):
        """Load data from JSON file or initialize empty data."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                self.inventory = data.get("inventory", [])
                self.sales = data.get("sales", [])
        else:
            self.inventory = []
            self.sales = []

    def save_data(self):
        """Save data to JSON file."""
        data = {
            "inventory": self.inventory,
            "sales": self.sales
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4)

    def setup_gui(self):
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Inventory Tab
        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventory")

        # Sales Tab
        self.sales_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_tab, text="Sales")

        # Reports Tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")

        # Populate tabs
        self.setup_inventory_tab()
        self.setup_sales_tab()
        self.setup_reports_tab()

    def setup_inventory_tab(self):
        # Add Item Frame
        add_frame = ttk.LabelFrame(self.inventory_tab, text="Add/Update Item")
        add_frame.pack(pady=10, padx=10, fill=tk.X)

        # Labels and Entries
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(add_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(add_frame)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Quantity:").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(add_frame)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(add_frame)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        ttk.Button(add_frame, text="Add Item", command=self.add_item).grid(row=4, column=0, pady=10)
        ttk.Button(add_frame, text="Update Item", command=self.update_item).grid(row=4, column=1, pady=10)
        ttk.Button(add_frame, text="Delete Item", command=self.delete_item).grid(row=4, column=2, pady=10)

        # Inventory Treeview
        self.inventory_tree = ttk.Treeview(
            self.inventory_tab,
            columns=("Name", "Price", "Quantity", "Category"),
            show="headings"
        )
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load inventory data
        self.load_inventory()

    def setup_sales_tab(self):
        # Sales Frame
        sales_frame = ttk.LabelFrame(self.sales_tab, text="Record Sale")
        sales_frame.pack(pady=10, padx=10, fill=tk.X)

        # Labels and Entries
        ttk.Label(sales_frame, text="Item Name:").grid(row=0, column=0, padx=5, pady=5)
        self.sale_item_entry = ttk.Entry(sales_frame)
        self.sale_item_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(sales_frame, text="Quantity Sold:").grid(row=1, column=0, padx=5, pady=5)
        self.sale_quantity_entry = ttk.Entry(sales_frame)
        self.sale_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        ttk.Button(sales_frame, text="Record Sale", command=self.record_sale).grid(row=2, column=0, columnspan=2, pady=10)

        # Sales Treeview
        self.sales_tree = ttk.Treeview(
            self.sales_tab,
            columns=("Item", "Quantity", "Date"),
            show="headings"
        )
        self.sales_tree.heading("Item", text="Item")
        self.sales_tree.heading("Quantity", text="Quantity")
        self.sales_tree.heading("Date", text="Date")
        self.sales_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load sales data
        self.load_sales()

    def setup_reports_tab(self):
        # Reports Frame
        reports_frame = ttk.LabelFrame(self.reports_tab, text="Reports")
        reports_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Low Stock Report
        ttk.Label(reports_frame, text="Low Stock Items (Quantity < 10):").pack(pady=5)
        self.low_stock_tree = ttk.Treeview(
            reports_frame,
            columns=("Name", "Quantity"),
            show="headings"
        )
        self.low_stock_tree.heading("Name", text="Name")
        self.low_stock_tree.heading("Quantity", text="Quantity")
        self.low_stock_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Sales Summary
        ttk.Label(reports_frame, text="Sales Summary:").pack(pady=5)
        self.sales_summary_tree = ttk.Treeview(
            reports_frame,
            columns=("Item", "Total Sold"),
            show="headings"
        )
        self.sales_summary_tree.heading("Item", text="Item")
        self.sales_summary_tree.heading("Total Sold", text="Total Sold")
        self.sales_summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Load reports
        self.load_reports()

    def add_item(self):
        """Add a new item to the inventory."""
        name = self.name_entry.get()
        price = self.price_entry.get()
        quantity = self.quantity_entry.get()
        category = self.category_entry.get()

        if not name or not price or not quantity or not category:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            self.inventory.append({
                "name": name,
                "price": float(price),
                "quantity": int(quantity),
                "category": category
            })
            self.save_data()
            messagebox.showinfo("Success", "Item added successfully!")
            self.load_inventory()
        except ValueError:
            messagebox.showerror("Error", "Invalid price or quantity!")

    def update_item(self):
        """Update the quantity of an existing item."""
        selected_item = self.inventory_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected!")
            return

        item_name = self.inventory_tree.item(selected_item)["values"][0]
        new_quantity = self.quantity_entry.get()

        if not new_quantity:
            messagebox.showerror("Error", "Quantity is required!")
            return

        try:
            for item in self.inventory:
                if item["name"] == item_name:
                    item["quantity"] = int(new_quantity)
                    break
            self.save_data()
            messagebox.showinfo("Success", "Item updated successfully!")
            self.load_inventory()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")

    def delete_item(self):
        """Delete an item from the inventory."""
        selected_item = self.inventory_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected!")
            return

        item_name = self.inventory_tree.item(selected_item)["values"][0]
        for item in self.inventory:
            if item["name"] == item_name:
                self.inventory.remove(item)
                break
        self.save_data()
        messagebox.showinfo("Success", "Item deleted successfully!")
        self.load_inventory()

    def record_sale(self):
        """Record a sale and update inventory."""
        item_name = self.sale_item_entry.get()
        quantity_sold = self.sale_quantity_entry.get()

        if not item_name or not quantity_sold:
            messagebox.showerror("Error", "Item name and quantity are required!")
            return

        try:
            quantity_sold = int(quantity_sold)
            for item in self.inventory:
                if item["name"] == item_name:
                    if item["quantity"] < quantity_sold:
                        messagebox.showerror("Error", "Not enough stock!")
                        return
                    item["quantity"] -= quantity_sold
                    self.sales.append({
                        "item": item_name,
                        "quantity": quantity_sold,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    self.save_data()
                    messagebox.showinfo("Success", "Sale recorded successfully!")
                    self.load_inventory()
                    self.load_sales()
                    self.load_reports()
                    return
            messagebox.showerror("Error", "Item not found!")
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity!")

    def load_inventory(self):
        """Load inventory data into the Treeview."""
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        for item in self.inventory:
            self.inventory_tree.insert("", tk.END, values=(
                item["name"],
                item["price"],
                item["quantity"],
                item["category"]
            ))

    def load_sales(self):
        """Load sales data into the Treeview."""
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)

        for sale in self.sales:
            self.sales_tree.insert("", tk.END, values=(
                sale["item"],
                sale["quantity"],
                sale["date"]
            ))

    def load_reports(self):
        """Load reports data into the Treeviews."""
        # Low Stock Report
        for row in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(row)

        for item in self.inventory:
            if item["quantity"] < 10:
                self.low_stock_tree.insert("", tk.END, values=(
                    item["name"],
                    item["quantity"]
                ))

        # Sales Summary
        for row in self.sales_summary_tree.get_children():
            self.sales_summary_tree.delete(row)

        sales_summary = {}
        for sale in self.sales:
            if sale["item"] in sales_summary:
                sales_summary[sale["item"]] += sale["quantity"]
            else:
                sales_summary[sale["item"]] = sale["quantity"]

        for item, total in sales_summary.items():
            self.sales_summary_tree.insert("", tk.END, values=(item, total))

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagementApp(root)
    root.mainloop()