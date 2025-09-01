import tkinter as tk
from tkinter import messagebox, ttk
import os

# File to store data
DATA_FILE = "store_inventory.txt"

# Function to load data from file
def load_data():
    inventory = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    name = parts[0]
                    purchase_price = float(parts[1])
                    sell_price = float(parts[2])
                    stock = int(parts[3])
                    profit = sell_price - purchase_price
                    inventory.append({
                        "name": name,
                        "purchase_price": purchase_price,
                        "sell_price": sell_price,
                        "profit": profit,
                        "stock": stock
                    })
    return inventory

# Function to save data to file
def save_data(inventory):
    with open(DATA_FILE, "w") as file:
        for item in inventory:
            file.write(f"{item['name']},{item['purchase_price']},{item['sell_price']},{item['stock']}\n")

# Main application class
class StoreApp:
    def init(self, root):
        self.root = root
        self.root.title("مدیریت فروشگاه لباس")
        self.inventory = load_data()

        # Create UI elements
def new_func():

new_func() self.create_widgets()

    def create_widgets(self):
        # Treeview for displaying inventory
        self.tree = ttk.Treeview(self.root, columns=("name", "purchase", "sell", "profit", "stock"), show="headings")
        self.tree.heading("name", text="نام محصول")
        self.tree.heading("purchase", text="قیمت خرید")
        self.tree.heading("sell", text="قیمت فروش")
        self.tree.heading("profit", text="سود")
        self.tree.heading("stock", text="موجودی")
        self.tree.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        add_btn = tk.Button(btn_frame, text="اضافه کردن محصول", command=self.add_product)
        add_btn.grid(row=0, column=0, padx=5)

        edit_btn = tk.Button(btn_frame, text="ویرایش محصول", command=self.edit_product)
        edit_btn.grid(row=0, column=1, padx=5)

        delete_btn = tk.Button(btn_frame, text="حذف محصول", command=self.delete_product)
        delete_btn.grid(row=0, column=2, padx=5)

        sell_btn = tk.Button(btn_frame, text="فروش محصول", command=self.sell_product)
        sell_btn.grid(row=0, column=3, padx=5)

        self.refresh_tree()

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for prod in self.inventory:
            self.tree.insert("", "end", values=(
                prod["name"],
                prod["purchase_price"],
                prod["sell_price"],
                prod["profit"],
                prod["stock"]
            ))

    def add_product(self):
        self.product_window("اضافه کردن محصول")

    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک محصول انتخاب کنید.")
            return
        item = self.tree.item(selected[0])
        values = item["values"]
        self.product_window("ویرایش محصول", values)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک محصول انتخاب کنید.")
            return
        if messagebox.askyesno("تأیید", "آیا مطمئن هستید که می‌خواهید این محصول را حذف کنید؟"):
            name = self.tree.item(selected[0])["values"][0]
            self.inventory = [p for p in self.inventory if p["name"] != name]
            save_data(self.inventory)
            self.refresh_tree()