import customtkinter as ctk
from tkinter import ttk, messagebox
import database

# --- Main Application Window ---
class RestaurantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Restaurant Billing System")
        self.geometry("1200x700")
        
        # Initialize database
        database.connect_db()

        # --- Current Bill Data ---
        self.current_bill = []
        self.bill_total = 0.0

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Left Frame (Menu and Controls) ---
        self.left_frame = ctk.CTkFrame(self, width=300)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.control_label = ctk.CTkLabel(self.left_frame, text="Menu & Controls", font=ctk.CTkFont(size=20, weight="bold"))
        self.control_label.pack(pady=20)

        # Tab view for Menu Management and POS
        self.tab_view = ctk.CTkTabview(self.left_frame)
        self.tab_view.pack(padx=10, pady=10, fill="both", expand=True)
        self.tab_view.add("POS")
        self.tab_view.add("Manage Menu")
        
        # --- POS Tab ---
        self.pos_frame = self.tab_view.tab("POS")
        self.menu_label = ctk.CTkLabel(self.pos_frame, text="Select Item:")
        self.menu_label.pack(pady=(10,0))
        
        self.menu_items_options = self.get_menu_item_names()
        self.menu_item_var = ctk.StringVar(value=self.menu_items_options[0] if self.menu_items_options else "No items")
        self.menu_dropdown = ctk.CTkOptionMenu(self.pos_frame, variable=self.menu_item_var, values=self.menu_items_options)
        self.menu_dropdown.pack(pady=5, padx=10, fill="x")

        self.qty_label = ctk.CTkLabel(self.pos_frame, text="Quantity:")
        self.qty_label.pack(pady=(10,0))
        self.qty_entry = ctk.CTkEntry(self.pos_frame, placeholder_text="1")
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=5, padx=10, fill="x")

        self.add_to_bill_button = ctk.CTkButton(self.pos_frame, text="Add to Bill", command=self.add_item_to_bill)
        self.add_to_bill_button.pack(pady=20, padx=10, fill="x")

        # --- Manage Menu Tab ---
        self.manage_frame = self.tab_view.tab("Manage Menu")
        
        self.item_name_entry = ctk.CTkEntry(self.manage_frame, placeholder_text="Item Name")
        self.item_name_entry.pack(pady=5, padx=10, fill="x")

        self.item_cat_entry = ctk.CTkEntry(self.manage_frame, placeholder_text="Category (e.g., Main Course)")
        self.item_cat_entry.pack(pady=5, padx=10, fill="x")

        self.item_price_entry = ctk.CTkEntry(self.manage_frame, placeholder_text="Price (e.g., 250.00)")
        self.item_price_entry.pack(pady=5, padx=10, fill="x")

        self.add_item_button = ctk.CTkButton(self.manage_frame, text="Add New Menu Item", command=self.add_new_menu_item)
        self.add_item_button.pack(pady=20, padx=10, fill="x")


        # --- Right Frame (Bill Display) ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.bill_label = ctk.CTkLabel(self.right_frame, text="Current Bill", font=ctk.CTkFont(size=20, weight="bold"))
        self.bill_label.pack(pady=20)

        # Bill table (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f6aa5')])
        
        self.bill_table = ttk.Treeview(self.right_frame, columns=("qty", "item", "price", "total"), show="headings")
        self.bill_table.heading("qty", text="Qty")
        self.bill_table.heading("item", text="Item")
        self.bill_table.heading("price", text="Price")
        self.bill_table.heading("total", text="Total")
        self.bill_table.column("qty", width=50, anchor="center")
        self.bill_table.column("item", width=300)
        self.bill_table.column("price", width=100, anchor="e")
        self.bill_table.column("total", width=100, anchor="e")
        self.bill_table.pack(padx=10, pady=10, fill="both", expand=True)

        # --- Totals & Finalize ---
        self.total_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.total_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_label = ctk.CTkLabel(self.total_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=16))
        self.total_label.pack(side="left")
        
        self.finalize_button = ctk.CTkButton(self.total_frame, text="Finalize Bill", command=self.finalize_bill)
        self.finalize_button.pack(side="right")
        
        self.clear_button = ctk.CTkButton(self.total_frame, text="Clear Bill", fg_color="firebrick", hover_color="darkred", command=self.clear_bill)
        self.clear_button.pack(side="right", padx=10)


    def get_menu_item_names(self):
        items = database.get_menu_items()
        return [f"{item[0]} (₹{item[2]:.2f})" for item in items] if items else ["Please add items"]

    def refresh_menu_dropdown(self):
        self.menu_items_options = self.get_menu_item_names()
        self.menu_dropdown.configure(values=self.menu_items_options)
        if self.menu_items_options:
            self.menu_dropdown.set(self.menu_items_options[0])

    def add_new_menu_item(self):
        name = self.item_name_entry.get()
        category = self.item_cat_entry.get()
        price_str = self.item_price_entry.get()

        if not all([name, category, price_str]):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Price must be a valid number.")
            return

        if database.add_menu_item(name, category, price):
            messagebox.showinfo("Success", f"'{name}' added to the menu.")
            self.item_name_entry.delete(0, 'end')
            self.item_cat_entry.delete(0, 'end')
            self.item_price_entry.delete(0, 'end')
            self.refresh_menu_dropdown()
        else:
            messagebox.showerror("Error", f"Item '{name}' already exists.")

    def add_item_to_bill(self):
        selected_item_str = self.menu_item_var.get()
        if selected_item_str == "Please add items" or not selected_item_str:
            messagebox.showerror("Error", "No menu item selected or available.")
            return
            
        item_name = selected_item_str.split(" (₹")[0]
        
        try:
            quantity = int(self.qty_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return
            
        price = database.get_item_price(item_name)
        if price is not None:
            self.current_bill.append({"name": item_name, "quantity": quantity, "price": price})
            self.update_bill_display()

    def update_bill_display(self):
        # Clear existing table
        for row in self.bill_table.get_children():
            self.bill_table.delete(row)
        
        self.bill_total = 0.0
        # Add new items
        for item in self.current_bill:
            subtotal = item["quantity"] * item["price"]
            self.bill_table.insert("", "end", values=(item["quantity"], item["name"], f"{item['price']:.2f}", f"{subtotal:.2f}"))
            self.bill_total += subtotal
        
        self.total_label.configure(text=f"Total: ₹{self.bill_total:.2f}")

    def clear_bill(self):
        self.current_bill = []
        self.bill_total = 0.0
        self.update_bill_display()
        
    def finalize_bill(self):
        if not self.current_bill:
            messagebox.showerror("Error", "The bill is empty.")
            return
            
        # Assuming a simple GST calculation
        gst_rate = 0.05  # 5% GST
        sub_total = self.bill_total
        gst_amount = sub_total * gst_rate
        grand_total = sub_total + gst_amount
        
        bill_summary = "--- Final Bill ---\n\n"
        order_items_for_db = []
        for item in self.current_bill:
            item_subtotal = item['price'] * item['quantity']
            bill_summary += f"{item['name']} (x{item['quantity']}) : ₹{item_subtotal:.2f}\n"
            order_items_for_db.append({
                'name': item['name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'subtotal': item_subtotal
            })

        bill_summary += "--------------------\n"
        bill_summary += f"Sub-Total: ₹{sub_total:.2f}\n"
        bill_summary += f"GST (5%): ₹{gst_amount:.2f}\n"
        bill_summary += f"Grand Total: ₹{grand_total:.2f}\n"

        # Ask for confirmation
        if messagebox.askokcancel("Confirm Bill", bill_summary):
            order_id = database.save_order(sub_total, gst_amount, grand_total, order_items_for_db)
            messagebox.showinfo("Success", f"Bill finalized and saved! Order ID: {order_id}")
            self.clear_bill()


if __name__ == "__main__":
    app = RestaurantApp()
    app.mainloop()