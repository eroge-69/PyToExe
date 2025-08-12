import tkinter as tk
from tkinter import messagebox, ttk
import os

class PizzaOrderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("🍕 Custom Pizza Order")
        self.master.configure(bg="#f8efd4")
        self.order = {
            "size": None,
            "crust": None,
            "toppings": [],
            "sauces": [],
            "instructions": "",
            "name": ""
        }
        self.frames = {}
        self.create_frames()
        self.show_frame("Size")

    def create_frames(self):
        # Size Page
        frame_size = tk.Frame(self.master, bg="#f8efd4")
        tk.Label(frame_size, text="Choose Size", font=("Arial Rounded MT Bold", 22, "bold"), bg="#f8efd4", fg="#b83b5e").pack(pady=18)
        self.size_var = tk.StringVar(value="Medium")
        sizes = [("Small", "🟢"), ("Medium", "🟡"), ("Large", "🔴")]
        for s, icon in sizes:
            ttk.Radiobutton(frame_size, text=f"{icon} {s}", variable=self.size_var, value=s).pack(anchor="w", padx=40, pady=6)
        tk.Button(frame_size, text="Next →", font=("Arial Rounded MT Bold", 13), bg="#b83b5e", fg="white",
                  command=lambda: self.next_page("Crust")).pack(pady=18, ipadx=10, ipady=4)
        self.frames["Size"] = frame_size

        # Crust Page
        frame_crust = tk.Frame(self.master, bg="#f8efd4")
        tk.Label(frame_crust, text="Choose Crust", font=("Arial Rounded MT Bold", 22, "bold"), bg="#f8efd4", fg="#b83b5e").pack(pady=18)
        self.crust_var = tk.StringVar(value="Regular")
        crusts = ["Thin", "Regular", "Thick", "Cheese Burst"]
        for c in crusts:
            ttk.Radiobutton(frame_crust, text=c, variable=self.crust_var, value=c).pack(anchor="w", padx=40, pady=6)
        nav = tk.Frame(frame_crust, bg="#f8efd4")
        nav.pack(pady=18)
        tk.Button(nav, text="← Back", font=("Arial Rounded MT Bold", 12), command=lambda: self.show_frame("Size")).pack(side="left", padx=8)
        tk.Button(nav, text="Next →", font=("Arial Rounded MT Bold", 12), bg="#b83b5e", fg="white",
                  command=lambda: self.next_page("Toppings")).pack(side="left", padx=8)
        self.frames["Crust"] = frame_crust

        # Toppings Page
        frame_toppings = tk.Frame(self.master, bg="#f8efd4")
        tk.Label(frame_toppings, text="Choose Toppings", font=("Arial Rounded MT Bold", 22, "bold"), bg="#f8efd4", fg="#b83b5e").pack(pady=18)
        self.toppings_vars = {}
        toppings = [
            ("Pepperoni", "🍖"), ("Mushrooms", "🍄"), ("Onions", "🧅"), ("Sausage", "🌭"),
            ("Bacon", "🥓"), ("Parmesan", "🧀"), ("Olives", "🫒"),
            ("Capsicum", "🫑"), ("Pineapple", "🍍"), ("Spinach", "🥬")
        ]
        for t, icon in toppings:
            var = tk.BooleanVar()
            self.toppings_vars[t] = var
            ttk.Checkbutton(frame_toppings, text=f"{icon} {t}", variable=var).pack(anchor="w", padx=40, pady=2)
        nav = tk.Frame(frame_toppings, bg="#f8efd4")
        nav.pack(pady=18)
        tk.Button(nav, text="← Back", font=("Arial Rounded MT Bold", 12), command=lambda: self.show_frame("Crust")).pack(side="left", padx=8)
        tk.Button(nav, text="Next →", font=("Arial Rounded MT Bold", 12), bg="#b83b5e", fg="white",
                  command=lambda: self.next_page("Sauces")).pack(side="left", padx=8)
        self.frames["Toppings"] = frame_toppings

        # Sauces Page
        frame_sauces = tk.Frame(self.master, bg="#f8efd4")
        tk.Label(frame_sauces, text="Choose Sauce Swirls", font=("Arial Rounded MT Bold", 22, "bold"), bg="#f8efd4", fg="#b83b5e").pack(pady=18)
        self.sauce_vars = {}
        sauces = [
            ("Tomato Basil", "🍅"),
            ("Barbecue", "🍖"),
            ("Pesto", "🌿"),
            ("Garlic Aioli", "🧄"),
            ("Buffalo", "🌶️"),
            ("Ranch", "🥛")
        ]
        for s, icon in sauces:
            var = tk.BooleanVar()
            self.sauce_vars[s] = var
            ttk.Checkbutton(frame_sauces, text=f"{icon} {s}", variable=var).pack(anchor="w", padx=40, pady=2)
        nav = tk.Frame(frame_sauces, bg="#f8efd4")
        nav.pack(pady=18)
        tk.Button(nav, text="← Back", font=("Arial Rounded MT Bold", 12), command=lambda: self.show_frame("Toppings")).pack(side="left", padx=8)
        tk.Button(nav, text="Next →", font=("Arial Rounded MT Bold", 12), bg="#b83b5e", fg="white",
                  command=lambda: self.next_page("Details")).pack(side="left", padx=8)
        self.frames["Sauces"] = frame_sauces

        # Details Page
        frame_details = tk.Frame(self.master, bg="#f8efd4")
        tk.Label(frame_details, text="Special Instructions", font=("Arial Rounded MT Bold", 16), bg="#f8efd4", fg="#b83b5e").pack(pady=(18, 2))
        self.instructions = tk.Entry(frame_details, width=38, font=("Arial", 11))
        self.instructions.pack(padx=10, pady=6)
        tk.Label(frame_details, text="Order Name", font=("Arial Rounded MT Bold", 16), bg="#f8efd4", fg="#b83b5e").pack(pady=(18, 2))
        self.name_entry = tk.Entry(frame_details, width=38, font=("Arial", 11))
        self.name_entry.pack(padx=10, pady=6)
        nav = tk.Frame(frame_details, bg="#f8efd4")
        nav.pack(pady=18)
        tk.Button(nav, text="← Back", font=("Arial Rounded MT Bold", 12), command=lambda: self.show_frame("Sauces")).pack(side="left", padx=8)
        tk.Button(nav, text="Review Order →", font=("Arial Rounded MT Bold", 12), bg="#b83b5e", fg="white",
                  command=self.review_order).pack(side="left", padx=8)
        self.frames["Details"] = frame_details

        # Review/Submit Page
        frame_review = tk.Frame(self.master, bg="#f8efd4")
        self.review_label = tk.Label(frame_review, text="", font=("Arial", 13), bg="#f8efd4", fg="#222")
        self.review_label.pack(pady=18)
        nav = tk.Frame(frame_review, bg="#f8efd4")
        nav.pack(pady=18)
        tk.Button(nav, text="← Back", font=("Arial Rounded MT Bold", 12), command=lambda: self.show_frame("Details")).pack(side="left", padx=8)
        tk.Button(nav, text="Place Order", font=("Arial Rounded MT Bold", 13), bg="#b83b5e", fg="white",
                  command=self.place_order).pack(side="left", padx=8)
        self.frames["Review"] = frame_review

        # Footer
        tk.Label(self.master, text="© 2025 Pizza Palace", bg="#f8efd4", fg="#b83b5e", font=("Arial Rounded MT Bold", 10)).pack(side="bottom", pady=4)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        self.master.update_idletasks()
        self.master.minsize(self.master.winfo_reqwidth(), self.master.winfo_reqheight())
        self.master.geometry("")

    def next_page(self, next_name):
        # Save current page's data
        if next_name == "Crust":
            self.order["size"] = self.size_var.get()
        elif next_name == "Toppings":
            self.order["crust"] = self.crust_var.get()
        elif next_name == "Sauces":
            self.order["toppings"] = [t for t, v in self.toppings_vars.items() if v.get()]
        elif next_name == "Details":
            self.order["sauces"] = [s for s, v in self.sauce_vars.items() if v.get()]
        self.show_frame(next_name)

    def review_order(self):
        self.order["instructions"] = self.instructions.get()
        self.order["name"] = self.name_entry.get()
        summary = (
            f"Order Name: {self.order['name'] or 'N/A'}\n"
            f"Size: {self.order['size']}\n"
            f"Crust: {self.order['crust']}\n"
            f"Toppings: {', '.join(self.order['toppings']) if self.order['toppings'] else 'None'}\n"
            f"Sauce Swirls: {', '.join(self.order['sauces']) if self.order['sauces'] else 'None'}\n"
            f"Instructions: {self.order['instructions'] or 'None'}"
        )
        self.review_label.config(text=summary)
        self.show_frame("Review")

    def place_order(self):
        import datetime
        name = self.order["name"] or "pizza"
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()
        # Ensure the 'orders' subfolder exists
        orders_dir = "orders"
        os.makedirs(orders_dir, exist_ok=True)
        filename = os.path.join(orders_dir, f"{safe_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pza")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("Pizza Order\n")
                f.write("="*30 + "\n")
                f.write(f"Order Name: {self.order['name']}\n")
                f.write(f"Size: {self.order['size']}\n")
                f.write(f"Crust: {self.order['crust']}\n")
                f.write(f"Toppings: {', '.join(self.order['toppings']) if self.order['toppings'] else 'None'}\n")
                f.write(f"Sauce Swirls: {', '.join(self.order['sauces']) if self.order['sauces'] else 'None'}\n")
                f.write(f"Instructions: {self.order['instructions']}\n")
            messagebox.showinfo("Order Placed", f"Your pizza order has been saved as:\n{filename}\n\nThank you for ordering!")
            self.master.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save order: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaOrderApp(root)
    root.mainloop()