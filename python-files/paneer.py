import tkinter as tk
from tkinter import messagebox

class SalesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PaneerTopia Sales")
        self.root.geometry("800x1000")

        self.cart = []

        # Header
        header = tk.Label(root, text="PaneerTopia - Best Paneer Products", font=("Arial", 20, "bold"))
        header.pack(pady=10)

        # Frame for products
        products_frame = tk.Frame(root)
        products_frame.pack(pady=10, side="left", fill="both", expand=True)

        # Example products: name and base price per kg
        self.products = [
            {"name": "Paneer Butter Masala", "price_per_kg": 8.99},
            {"name": "Paneer Tikka", "price_per_kg": 7.50},
            {"name": "Paneer Wrap", "price_per_kg": 6.25},
            {"name": "Paneer Sandwich", "price_per_kg": 5.00},
            {"name": "Paneer Salad", "price_per_kg": 4.75},
            {"name": "Paneer Curry", "price_per_kg": 9.50},
            {"name": "Paneer Biryani", "price_per_kg": 10.00},
            {"name": "Paneer Pakora", "price_per_kg": 3.50},
        ]

        # Weights options
        self.weights = [1, 10, 100, 1000]

        # Create product widgets with weight buttons
        for idx, product in enumerate(self.products):
            frame = tk.Frame(products_frame, bd=1, relief="solid", padx=10, pady=10)
            frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky="nsew")

            name_label = tk.Label(frame, text=product["name"], font=("Arial", 14))
            name_label.pack()

            price_label = tk.Label(frame, text=f"Price per kg: ${product['price_per_kg']:.2f}", fg="green")
            price_label.pack(pady=(0, 5))

            # Buttons for different weights
            for w in self.weights:
                price = product["price_per_kg"] * w
                btn = tk.Button(frame, text=f"Add {w} kg - ${price:.2f}",
                                command=lambda p=product, w=w, price=price: self.add_to_cart(p["name"], w, price))
                btn.pack(pady=2)

        # Cart section on right
        cart_frame = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
        cart_frame.pack(side="right", fill="y", padx=10, pady=10)

        cart_label = tk.Label(cart_frame, text="Shopping Cart", font=("Arial", 16, "bold"))
        cart_label.pack()

        self.cart_listbox = tk.Listbox(cart_frame, width=40, height=25)
        self.cart_listbox.pack(pady=5)

        self.total_label = tk.Label(cart_frame, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=5)

        checkout_btn = tk.Button(cart_frame, text="Checkout", command=self.checkout)
        checkout_btn.pack(pady=10)

    def add_to_cart(self, product_name, weight, price):
        item = {"name": product_name, "weight": weight, "price": price}
        self.cart.append(item)
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0
        for item in self.cart:
            self.cart_listbox.insert(tk.END, f"{item['name']} - {item['weight']} kg - ${item['price']:.2f}")
            total += item['price']
        self.total_label.config(text=f"Total: ${total:.2f}")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty! Add some products.")
            return
        total = sum(item['price'] for item in self.cart)
        messagebox.showinfo("Checkout", f"Thank you for your purchase!\nTotal: ${total:.2f}")
        self.cart.clear()
        self.update_cart_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesApp(root)
    root.mainloop()
