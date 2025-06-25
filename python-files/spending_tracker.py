import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "spending_data.json"

class SpendingTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Eggsmart Spending Tracker")

        self.store_data = self.load_data()

        ttk.Label(root, text="Store Name:").grid(row=0, column=0)
        self.store_entry = ttk.Entry(root)
        self.store_entry.grid(row=0, column=1)

        ttk.Label(root, text="Item Name:").grid(row=1, column=0)
        self.item_entry = ttk.Entry(root)
        self.item_entry.grid(row=1, column=1)

        ttk.Label(root, text="Price:").grid(row=2, column=0)
        self.price_entry = ttk.Entry(root)
        self.price_entry.grid(row=2, column=1)

        ttk.Button(root, text="Add Entry", command=self.add_entry).grid(row=3, column=0, columnspan=2, pady=10)

        self.output = tk.Text(root, width=50, height=15)
        self.output.grid(row=4, column=0, columnspan=2)

        self.update_output()

    def add_entry(self):
        store = self.store_entry.get().strip()
        item = self.item_entry.get().strip()
        price_text = self.price_entry.get().strip()

        try:
            price = float(price_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for price.")
            return

        if store not in self.store_data:
            self.store_data[store] = []

        self.store_data[store].append((item, price))
        self.save_data()
        self.update_output()
        self.item_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def update_output(self):
        self.output.delete(1.0, tk.END)
        for store, entries in self.store_data.items():
            self.output.insert(tk.END, f"Store: {store}\n")
            total = 0
            for item, price in entries:
                self.output.insert(tk.END, f"  - {item}: ${price:.2f}\n")
                total += price
            self.output.insert(tk.END, f"  Total Spent: ${total:.2f}\n\n")

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.store_data, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

if __name__ == "__main__":
    root = tk.Tk()
    app = SpendingTracker(root)
    root.mainloop()
