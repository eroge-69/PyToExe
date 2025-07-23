import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime

DATA_DIR = "data"
PRODUCTS_FILE = "products.json"

DEFAULT_PRODUCTS = {
    "Леб": {"цена": 25, "количина": 0},
    "Геврек": {"цена": 20, "количина": 0},
    "Кифла": {"цена": 15, "количина": 0},
    "Пица": {"цена": 50, "количина": 0}
}

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Програма за Производи")
        self.products = self.load_products()

        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.listbox = tk.Listbox(self.frame, width=40)
        self.listbox.grid(row=0, column=0, columnspan=4)

        self.update_listbox()

        tk.Button(self.frame, text="Влез", command=self.add_stock).grid(row=1, column=0)
        tk.Button(self.frame, text="Излез", command=self.remove_stock).grid(row=1, column=1)
        tk.Button(self.frame, text="Измени Цена", command=self.change_price).grid(row=1, column=2)
        tk.Button(self.frame, text="Избриши", command=self.delete_product).grid(row=1, column=3)
        tk.Button(self.frame, text="Нов Производ", command=self.add_product).grid(row=2, column=0, columnspan=2)
        tk.Button(self.frame, text="Сними Денес", command=self.save_daily).grid(row=2, column=2, columnspan=2)

    def load_products(self):
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return DEFAULT_PRODUCTS.copy()

    def save_products(self):
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for name, data in self.products.items():
            self.listbox.insert(tk.END, f"{name} - Кол: {data['количина']} - Цена: {data['цена']} ден")

    def get_selected_product(self):
        selection = self.listbox.curselection()
        if selection:
            return list(self.products.keys())[selection[0]]
        messagebox.showwarning("Избор", "Избери производ од листата.")
        return None

    def add_stock(self):
        product = self.get_selected_product()
        if product:
            amount = simpledialog.askinteger("Внес", f"Колку {product} да додадеш?")
            if amount is not None:
                self.products[product]['количина'] += amount
                self.save_products()
                self.update_listbox()

    def remove_stock(self):
        product = self.get_selected_product()
        if product:
            amount = simpledialog.askinteger("Излез", f"Колку {product} да одземеш?")
            if amount is not None:
                self.products[product]['количина'] -= amount
                self.save_products()
                self.update_listbox()

    def change_price(self):
        product = self.get_selected_product()
        if product:
            price = simpledialog.askinteger("Цена", f"Нова цена за {product}?")
            if price is not None:
                self.products[product]['цена'] = price
                self.save_products()
                self.update_listbox()

    def delete_product(self):
        product = self.get_selected_product()
        if product:
            if messagebox.askyesno("Бришење", f"Сигурно сакаш да го избришеш {product}?"):
                del self.products[product]
                self.save_products()
                self.update_listbox()

    def add_product(self):
        name = simpledialog.askstring("Нов Производ", "Име на производот?")
        if name and name not in self.products:
            price = simpledialog.askinteger("Цена", f"Цена за {name}?")
            if price is not None:
                self.products[name] = {"цена": price, "количина": 0}
                self.save_products()
                self.update_listbox()

    def save_daily(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DATA_DIR, f"products_{date_str}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Снимано", f"Податоците се снимени за {date_str}.")

if __name__ == '__main__':
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
