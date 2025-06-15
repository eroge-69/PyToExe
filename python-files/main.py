
import tkinter as tk
from tkinter import messagebox, simpledialog

class StationaryTrackingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Stationary Tracking System")
        self.items = {}

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.listbox = tk.Listbox(self.frame, width=40)
        self.listbox.pack()

        self.add_button = tk.Button(self.frame, text="Add Item", command=self.add_item)
        self.add_button.pack(fill='x')

        self.remove_button = tk.Button(self.frame, text="Remove Item", command=self.remove_item)
        self.remove_button.pack(fill='x')

        self.refresh_button = tk.Button(self.frame, text="Refresh List", command=self.refresh_list)
        self.refresh_button.pack(fill='x')

        self.refresh_list()

    def add_item(self):
        name = simpledialog.askstring("Add Item", "Enter item name:")
        if not name:
            return
        try:
            qty = int(simpledialog.askstring("Add Item", "Enter quantity:"))
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Invalid quantity.")
            return
        self.items[name] = self.items.get(name, 0) + qty
        self.refresh_list()

    def remove_item(self):
        name = simpledialog.askstring("Remove Item", "Enter item name:")
        if not name or name not in self.items:
            messagebox.showerror("Error", "Item not found.")
            return
        try:
            qty = int(simpledialog.askstring("Remove Item", "Enter quantity to remove:"))
        except (TypeError, ValueError):
            messagebox.showerror("Error", "Invalid quantity.")
            return
        if self.items[name] < qty:
            messagebox.showerror("Error", "Not enough items.")
            return
        self.items[name] -= qty
        if self.items[name] == 0:
            del self.items[name]
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        if not self.items:
            self.listbox.insert(tk.END, "No items in inventory.")
        else:
            for name, qty in self.items.items():
                self.listbox.insert(tk.END, f"{name}: {qty}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StationaryTrackingSystem(root)
    root.mainloop()


