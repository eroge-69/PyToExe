import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

DATA_FILE = 'stock_data.json'

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Monitor")

        self.stock = self.load_data()

        self.canvas = tk.Canvas(root, bg="#f0f0f0")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Add", width=10, command=self.add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit", width=10, command=self.edit_item).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", width=10, command=self.delete_item).pack(side=tk.LEFT, padx=5)

        self.item_frames = {}
        self.selected_item = None

        self.refresh_grid()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.stock, f, indent=4)

    def get_color(self, quantity):
        if quantity <= 2:
            return "#ff4c4c"  # Red
        elif quantity <= 5:
            return "#ffa500"  # Orange
        else:
            return "#4caf50"  # Green

    def refresh_grid(self):
        for frame in self.canvas.winfo_children():
            frame.destroy()

        self.item_frames = {}
        row = 0
        col = 0
        for item, qty in self.stock.items():
            color = self.get_color(qty)
            frame = tk.Frame(self.canvas, width=150, height=100, bg=color, borderwidth=2, relief="raised")
            frame.grid_propagate(False)
            frame.grid(row=row, column=col, padx=10, pady=10)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)

            label = tk.Label(frame, text=f"{item}\nQty: {qty}", bg=color, fg="white", font=("Arial", 12), justify="center")
            label.pack(expand=True, fill=tk.BOTH)

            frame.bind("<Button-1>", lambda e, i=item: self.select_item(i))
            label.bind("<Button-1>", lambda e, i=item: self.select_item(i))

            self.item_frames[item] = frame

            col += 1
            if col >= 3:  # 3 items per row
                col = 0
                row += 1

    def select_item(self, item):
        self.selected_item = item
        for i, frame in self.item_frames.items():
            frame.config(highlightthickness=4 if i == item else 0, highlightbackground="blue")

    def add_item(self):
        item = simpledialog.askstring("Item Name", "Enter item name:")
        if item:
            qty = simpledialog.askinteger("Quantity", f"Enter quantity for '{item}':", minvalue=0)
            if qty is not None:
                self.stock[item] = qty
                self.save_data()
                self.refresh_grid()

    def edit_item(self):
        if not self.selected_item:
            messagebox.showwarning("No Selection", "Please select an item to edit.")
            return
        new_qty = simpledialog.askinteger("Edit Quantity", f"Enter new quantity for '{self.selected_item}':", minvalue=0)
        if new_qty is not None:
            self.stock[self.selected_item] = new_qty
            self.save_data()
            self.refresh_grid()

    def delete_item(self):
        if not self.selected_item:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete '{self.selected_item}' from stock?"):
            del self.stock[self.selected_item]
            self.selected_item = None
            self.save_data()
            self.refresh_grid()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x400")
    app = StockApp(root)
    root.mainloop()
