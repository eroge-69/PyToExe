import customtkinter as ctk
import json
from datetime import datetime, timedelta
import os
from tkinter import messagebox

class SabiQureshiPOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sabi Qureshi's POS - Enhanced")
        self.geometry("1400x800")
        ctk.set_appearance_mode("dark")  # Modern dark theme

        # Data file paths
        self.inventory_file = "inventory.json"
        self.sales_file = "sales.json"
        self.expenses_file = "expenses.json"
        self.withdrawals_file = "withdrawals.json"

        # Create necessary folders
        os.makedirs("receipts", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

        # Load data
        self.inventory = self.load_data(self.inventory_file)
        self.sales = self.load_data(self.sales_file)
        self.expenses = self.load_data(self.expenses_file)
        self.withdrawals = self.load_data(self.withdrawals_file)

        # Main frames
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel (Inventory)
        self.left_panel = ctk.CTkFrame(self.main_frame, width=350)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)

        # Right panel (POS and Financials)
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Initialize UI
        self.create_inventory_ui()
        self.create_pos_ui()
        self.create_financial_ui()  # New financial section
        self.update_inventory_list()
        self.update_product_dropdown()

    def load_data(self, filename):
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_data(self, filename, data):
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    # ==============================================================================
    # Inventory UI (Improved)
    # ==============================================================================
    def create_inventory_ui(self):
        # Title with better styling
        title_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(title_frame, 
                            text="Inventory Management", 
                            font=("Arial", 18, "bold"),
                            anchor="w")
        title.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(title_frame, 
                                   text="↻", 
                                   width=30,
                                   command=self.update_inventory_list)
        refresh_btn.pack(side="right", padx=5)

        # Inventory List with better styling
        self.inventory_list = ctk.CTkScrollableFrame(self.left_panel, 
                                                   label_text="Product Inventory",
                                                   label_font=("Arial", 14),
                                                   height=300)
        self.inventory_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Add/Update Product Form with better organization
        form_frame = ctk.CTkFrame(self.left_panel)
        form_frame.pack(fill="x", padx=5, pady=(10, 5))

        form_title = ctk.CTkLabel(form_frame, 
                                 text="Add/Update Product",
                                 font=("Arial", 14))
        form_title.pack(pady=(5, 10))

        # Form entries with labels
        ctk.CTkLabel(form_frame, text="Product Name:").pack(anchor="w", padx=5)
        self.product_name_entry = ctk.CTkEntry(form_frame, 
                                              placeholder_text="Enter product name")
        self.product_name_entry.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(form_frame, text="Purchase Price (PKR):").pack(anchor="w", padx=5)
        self.purchase_price_entry = ctk.CTkEntry(form_frame, 
                                                placeholder_text="Enter purchase price")
        self.purchase_price_entry.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(form_frame, text="Stock Quantity:").pack(anchor="w", padx=5)
        self.stock_entry = ctk.CTkEntry(form_frame, 
                                      placeholder_text="Enter stock quantity")
        self.stock_entry.pack(fill="x", padx=5, pady=(0, 10))

        # Form buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))

        add_button = ctk.CTkButton(btn_frame, 
                                  text="Add/Update", 
                                  command=self.add_update_product)
        add_button.pack(side="left", expand=True, padx=2)

        clear_button = ctk.CTkButton(btn_frame, 
                                    text="Clear", 
                                    command=self.clear_product_entries)
        clear_button.pack(side="right", expand=True, padx=2)

    def add_update_product(self):
        name = self.product_name_entry.get().strip()
        purchase_price_str = self.purchase_price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()

        # Improved validation with error messages
        if not name:
            messagebox.showerror("Error", "Product name is required")
            self.product_name_entry.configure(border_color="red")
            return
        if not purchase_price_str:
            messagebox.showerror("Error", "Purchase price is required")
            self.purchase_price_entry.configure(border_color="red")
            return
        if not stock_str:
            messagebox.showerror("Error", "Stock quantity is required")
            self.stock_entry.configure(border_color="red")
            return

        try:
            purchase_price = float(purchase_price_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value")
            self.purchase_price_entry.configure(border_color="red")
            self.stock_entry.configure(border_color="red")
            return
        
        # Reset border colors
        self.product_name_entry.configure(border_color="#979DA2")
        self.purchase_price_entry.configure(border_color="#979DA2")
        self.stock_entry.configure(border_color="#979DA2")

        # Update or add product
        product_exists = False
        for product in self.inventory:
            if product['name'].lower() == name.lower():
                product['purchase_price'] = purchase_price
                product['stock'] = stock
                product_exists = True
                break
        
        if not product_exists:
            self.inventory.append({
                "name": name, 
                "purchase_price": purchase_price, 
                "stock": stock
            })

        self.save_data(self.inventory_file, self.inventory)
        self.update_inventory_list()
        self.update_product_dropdown()
        self.clear_product_entries()
        messagebox.showinfo("Success", "Product saved successfully")

    def update_inventory_list(self):
        for widget in self.inventory_list.winfo_children():
            widget.destroy()

        if not self.inventory:
            empty_label = ctk.CTkLabel(self.inventory_list, text="No products in inventory")
            empty_label.pack(pady=10)
            return

        for product in self.inventory:
            item_frame = ctk.CTkFrame(self.inventory_list, height=40)
            item_frame.pack(fill="x", pady=2, padx=2)

            stock_color = "green" if product['stock'] > 5 else "orange" if product['stock'] > 0 else "red"
            
            product_info = f"{product['name']}"
            label = ctk.CTkLabel(item_frame, 
                                text=product_info,
                                anchor="w")
            label.pack(side="left", padx=5, fill="x", expand=True)

import customtkinter as ctk
import json
from datetime import datetime, timedelta
import os
from tkinter import messagebox

class SabiQureshiPOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sabi Qureshi's POS - Enhanced")
        self.geometry("1400x800")
        ctk.set_appearance_mode("dark")  # Modern dark theme

        # Data file paths
        self.inventory_file = "inventory.json"
        self.sales_file = "sales.json"
        self.expenses_file = "expenses.json"
        self.withdrawals_file = "withdrawals.json"

        # Create necessary folders
        os.makedirs("receipts", exist_ok=True)
        os.makedirs("reports", exist_ok=True)

        # Load data
        self.inventory = self.load_data(self.inventory_file)
        self.sales = self.load_data(self.sales_file)
        self.expenses = self.load_data(self.expenses_file)
        self.withdrawals = self.load_data(self.withdrawals_file)

        # Main frames
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel (Inventory)
        self.left_panel = ctk.CTkFrame(self.main_frame, width=350)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)

        # Right panel (POS and Financials)
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Initialize UI
        self.create_inventory_ui()
        self.create_pos_ui()
        self.create_financial_ui()  # New financial section
        self.update_inventory_list()
        self.update_product_dropdown()

    def load_data(self, filename):
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_data(self, filename, data):
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    # ==============================================================================
    # Inventory UI (Improved)
    # ==============================================================================
    def create_inventory_ui(self):
        # Title with better styling
        title_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(title_frame, 
                            text="Inventory Management", 
                            font=("Arial", 18, "bold"),
                            anchor="w")
        title.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(title_frame, 
                                   text="↻", 
                                   width=30,
                                   command=self.update_inventory_list)
        refresh_btn.pack(side="right", padx=5)

        # Inventory List with better styling
        self.inventory_list = ctk.CTkScrollableFrame(self.left_panel, 
                                                   label_text="Product Inventory",
                                                   label_font=("Arial", 14),
                                                   height=300)
        self.inventory_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Add/Update Product Form with better organization
        form_frame = ctk.CTkFrame(self.left_panel)
        form_frame.pack(fill="x", padx=5, pady=(10, 5))

        form_title = ctk.CTkLabel(form_frame, 
                                 text="Add/Update Product",
                                 font=("Arial", 14))
        form_title.pack(pady=(5, 10))

        # Form entries with labels
        ctk.CTkLabel(form_frame, text="Product Name:").pack(anchor="w", padx=5)
        self.product_name_entry = ctk.CTkEntry(form_frame, 
                                              placeholder_text="Enter product name")
        self.product_name_entry.pack(fill="x", padx=5, pady=(0, 5))
        # Bind the key release event for autocomplete
        self.product_name_entry.bind("<KeyRelease>", self.on_product_name_key_release)
        
        # Autocomplete suggestions listbox
        self.suggestion_listbox = ctk.CTkScrollableFrame(form_frame, height=0) # Initially hidden
        self.suggestion_listbox.pack(fill="x", padx=5)
        self.suggestion_listbox.pack_forget() # Hide it initially

        ctk.CTkLabel(form_frame, text="Purchase Price (PKR):").pack(anchor="w", padx=5)
        self.purchase_price_entry = ctk.CTkEntry(form_frame, 
                                                placeholder_text="Enter purchase price")
        self.purchase_price_entry.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(form_frame, text="Stock Quantity:").pack(anchor="w", padx=5)
        self.stock_entry = ctk.CTkEntry(form_frame, 
                                      placeholder_text="Enter stock quantity")
        self.stock_entry.pack(fill="x", padx=5, pady=(0, 10))

        # Form buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))

        add_button = ctk.CTkButton(btn_frame, 
                                  text="Add/Update", 
                                  command=self.add_update_product)
        add_button.pack(side="left", expand=True, padx=2)

        clear_button = ctk.CTkButton(btn_frame, 
                                    text="Clear", 
                                    command=self.clear_product_entries)
        clear_button.pack(side="right", expand=True, padx=2)

    def on_product_name_key_release(self, event):
        search_term = self.product_name_entry.get().strip().lower()
        
        # Clear previous suggestions
        for widget in self.suggestion_listbox.winfo_children():
            widget.destroy()
        
        if search_term:
            matching_products = [
                p for p in self.inventory 
                if search_term in p['name'].lower()
            ]
            
            if matching_products:
                self.suggestion_listbox.pack(fill="x", padx=5) # Show the listbox
                for product in matching_products:
                    suggestion_label = ctk.CTkLabel(self.suggestion_listbox, 
                                                    text=product['name'],
                                                    anchor="w",
                                                    cursor="hand2")
                    suggestion_label.pack(fill="x", pady=1)
                    suggestion_label.bind("<Button-1>", 
                                          lambda e, p=product: self.select_suggested_product(p))
            else:
                self.suggestion_listbox.pack_forget() # Hide if no matches
        else:
            self.suggestion_listbox.pack_forget() # Hide if entry is empty

    def select_suggested_product(self, product):
        self.product_name_entry.delete(0, 'end')
        self.product_name_entry.insert(0, product['name'])
        
        self.purchase_price_entry.delete(0, 'end')
        self.purchase_price_entry.insert(0, str(product['purchase_price']))
        
        self.stock_entry.delete(0, 'end')
        self.stock_entry.insert(0, str(product['stock']))
        
        self.suggestion_listbox.pack_forget() # Hide suggestions after selection


    def add_update_product(self):
        name = self.product_name_entry.get().strip()
        purchase_price_str = self.purchase_price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()

        # Improved validation with error messages
        if not name:
            messagebox.showerror("Error", "Product name is required")
            self.product_name_entry.configure(border_color="red")
            return
        if not purchase_price_str:
            messagebox.showerror("Error", "Purchase price is required")
            self.purchase_price_entry.configure(border_color="red")
            return
        if not stock_str:
            messagebox.showerror("Error", "Stock quantity is required")
            self.stock_entry.configure(border_color="red")
            return

        try:
            purchase_price = float(purchase_price_str)
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value")
            self.purchase_price_entry.configure(border_color="red")
            self.stock_entry.configure(border_color="red")
            return
        
        # Reset border colors
        self.product_name_entry.configure(border_color="#979DA2")
        self.purchase_price_entry.configure(border_color="#979DA2")
        self.stock_entry.configure(border_color="#979DA2")

        # Update or add product
        product_exists = False
        for product in self.inventory:
            if product['name'].lower() == name.lower():
                product['purchase_price'] = purchase_price
                product['stock'] = stock
                product_exists = True
                break
        
        if not product_exists:
            self.inventory.append({
                "name": name, 
                "purchase_price": purchase_price, 
                "stock": stock
            })

        self.save_data(self.inventory_file, self.inventory)
        self.update_inventory_list()
        self.update_product_dropdown()
        self.clear_product_entries()
        messagebox.showinfo("Success", "Product saved successfully")

    def update_inventory_list(self):
        for widget in self.inventory_list.winfo_children():
            widget.destroy()

        if not self.inventory:
            empty_label = ctk.CTkLabel(self.inventory_list, text="No products in inventory")
            empty_label.pack(pady=10)
            return

        for product in self.inventory:
            item_frame = ctk.CTkFrame(self.inventory_list, height=40)
            item_frame.pack(fill="x", pady=2, padx=2)

            stock_color = "green" if product['stock'] > 5 else "orange" if product['stock'] > 0 else "red"
            
            product_info = f"{product['name']}"
            label = ctk.CTkLabel(item_frame, 
                                text=product_info,
                                anchor="w")
            label.pack(side="left", padx=5, fill="x", expand=True)

            stock_label = ctk.CTkLabel(item_frame, 
                                     text=f"Stock: {product['stock']}",
                                     text_color=stock_color)
            stock_label.pack(side="left", padx=5)

            price_label = ctk.CTkLabel(item_frame, 
                                     text=f"{product['purchase_price']:.2f} PKR")
            price_label.pack(side="right", padx=5)

    def clear_product_entries(self):
        self.product_name_entry.delete(0, 'end')
        self.purchase_price_entry.delete(0, 'end')
        self.stock_entry.delete(0, 'end')
        self.suggestion_listbox.pack_forget() # Hide suggestions on clear
    
    # ==============================================================================
    # POS UI (Improved)
    # ==============================================================================
    def create_pos_ui(self):
        # POS Frame
        pos_frame = ctk.CTkFrame(self.right_panel)
        pos_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # POS Title with better styling
        pos_title = ctk.CTkLabel(pos_frame, 
                                text="Point of Sale", 
                                font=("Arial", 18, "bold"),
                                anchor="w")
        pos_title.pack(fill="x", pady=(5, 10), padx=10)
        
        # Product Selection with better organization
        product_selection_frame = ctk.CTkFrame(pos_frame)
        product_selection_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(product_selection_frame, 
                    text="Select Product:").pack(side="left", padx=5)

        self.product_dropdown = ctk.CTkOptionMenu(product_selection_frame, 
                                                values=["Loading products..."],
                                                dynamic_resizing=False)
        self.product_dropdown.pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkLabel(product_selection_frame, 
                    text="Sale Price:").pack(side="left", padx=5)

        self.sale_price_entry = ctk.CTkEntry(product_selection_frame, 
                                           width=100,
                                           placeholder_text="PKR")
        self.sale_price_entry.pack(side="left", padx=5)

        add_to_cart_button = ctk.CTkButton(product_selection_frame, 
                                         text="Add to Cart",
                                         width=100,
                                         command=self.add_to_cart)
        add_to_cart_button.pack(side="right", padx=5)

        # Cart with better styling
        self.cart_frame = ctk.CTkScrollableFrame(pos_frame, 
                                               label_text="Shopping Cart",
                                               label_font=("Arial", 14),
                                               height=200)
        self.cart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Checkout section improved
        checkout_frame = ctk.CTkFrame(pos_frame)
        checkout_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = ctk.CTkLabel(checkout_frame, 
                                      text="Total: 0.00 PKR", 
                                      font=("Arial", 16, "bold"))
        self.total_label.pack(side="left", expand=True)

        complete_sale_button = ctk.CTkButton(checkout_frame, 
                                           text="Complete Sale", 
                                           height=40,
                                           fg_color="green",
                                           hover_color="dark green",
                                           command=self.complete_sale)
        complete_sale_button.pack(side="right", padx=5)

        # Cart data
        self.cart = []

    def product_selected(self, selected_product_name):
        self.sale_price_entry.delete(0, 'end')
        product = next((p for p in self.inventory if p['name'] == selected_product_name), None)
        if product:
            # Auto-suggest sale price (20% markup)
            suggested_price = product['purchase_price'] * 1.6
            self.sale_price_entry.insert(0, f"{suggested_price:.2f}")

    def update_product_dropdown(self):
        self.product_names = [p['name'] for p in self.inventory if p['stock'] > 0]
        if self.product_names:
            self.product_dropdown.configure(values=self.product_names)
            self.product_dropdown.set(self.product_names[0])
            self.product_dropdown.bind("<Button-1>", lambda e: self.product_selected(self.product_dropdown.get()))
        else:
            self.product_dropdown.configure(values=["No products in stock"])
            self.product_dropdown.set("No products in stock")

    def add_to_cart(self):
        product_name = self.product_dropdown.get()
        sale_price_str = self.sale_price_entry.get().strip()

        if not product_name or product_name == "No products in stock":
            messagebox.showerror("Error", "Please select a valid product")
            return

        if not sale_price_str:
            messagebox.showerror("Error", "Please enter a sale price")
            self.sale_price_entry.configure(border_color="red")
            return

        try:
            sale_price = float(sale_price_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid sale price")
            self.sale_price_entry.configure(border_color="red")
            return

        product = next((p for p in self.inventory if p['name'] == product_name), None)

        if not product:
            messagebox.showerror("Error", "Selected product not found in inventory")
            return

        if product['stock'] <= 0:
            messagebox.showerror("Error", "Product out of stock")
            return

        cart_item = {
            "name": product['name'],
            "sale_price": sale_price,
            "purchase_price": product['purchase_price'],
            "timestamp": datetime.now().isoformat()
        }
        self.cart.append(cart_item)
        product['stock'] -= 1
        
        self.update_cart_display()
        self.update_inventory_list()
        self.update_product_dropdown()
        self.sale_price_entry.delete(0, 'end')
        self.sale_price_entry.configure(border_color="#979DA2")

    def update_cart_display(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
        
        if not self.cart:
            empty_label = ctk.CTkLabel(self.cart_frame, text="Cart is empty")
            empty_label.pack(pady=10)
            self.total_label.configure(text="Total: 0.00 PKR")
            return

        total = 0
        for idx, item in enumerate(self.cart):
            item_frame = ctk.CTkFrame(self.cart_frame, height=35)
            item_frame.pack(fill="x", pady=2, padx=2)

            # Item info
            item_label = ctk.CTkLabel(item_frame, 
                                    text=f"{item['name']} - {item['sale_price']:.2f} PKR",
                                    anchor="w")
            item_label.pack(side="left", padx=5, fill="x", expand=True)

            # Remove button
            remove_btn = ctk.CTkButton(item_frame, 
                                      text="×", 
                                      width=30,
                                      fg_color="transparent",
                                      hover_color="#FF000020",
                                      text_color="red",
                                      command=lambda i=idx: self.remove_from_cart(i))
            remove_btn.pack(side="right", padx=2)

            total += item['sale_price']

        self.total_label.configure(text=f"Total: {total:.2f} PKR")
        
    def remove_from_cart(self, index):
        if 0 <= index < len(self.cart):
            # Return stock to inventory
            product_name = self.cart[index]['name']
            product = next((p for p in self.inventory if p['name'] == product_name), None)
            if product:
                product['stock'] += 1
            
            # Remove from cart
            del self.cart[index]
            
            # Update displays
            self.update_cart_display()
            self.update_inventory_list()
            self.update_product_dropdown()

    def complete_sale(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty")
            return

        timestamp = datetime.now()
        sale_record = {
            "timestamp": timestamp.isoformat(),
            "items": self.cart.copy(),
            "total": sum(item['sale_price'] for item in self.cart)
        }
        self.sales.append(sale_record)
        
        # Save updated data
        self.save_data(self.sales_file, self.sales)
        self.save_data(self.inventory_file, self.inventory)
        
        # Generate receipt
        self.generate_receipt(sale_record, timestamp)
        
        # Clear cart and reset UI
        self.cart = []
        self.update_cart_display()
        self.update_product_dropdown()
        self.update_inventory_list()
        
        messagebox.showinfo("Success", "Sale completed successfully!\nReceipt has been generated.")

    def generate_receipt(self, sale, timestamp):
        receipt_filename = f"receipts/receipt_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        try:
            with open(receipt_filename, 'w') as f:
                f.write("="*40 + "\n")
                f.write(f"{'Sabi Qureshi\'s POS':^40}\n")
                f.write("="*40 + "\n")
                f.write(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Receipt #: {len(self.sales)}\n")
                f.write("-"*40 + "\n")
                f.write("{:<25} {:>10}\n".format("ITEM", "PRICE (PKR)"))
                f.write("-"*40 + "\n")
                for item in sale['items']:
                    f.write("{:<25} {:>10.2f}\n".format(item['name'], item['sale_price']))
                f.write("-"*40 + "\n")
                f.write("{:<25} {:>10.2f}\n".format("TOTAL", sale['total']))
                f.write("="*40 + "\n")
                f.write("\nThank you for your business!\n")
        except IOError:
            messagebox.showerror("Error", "Failed to generate receipt file")

    # ==============================================================================
    # Financial UI (New Features: Withdrawals and Expenses)
    # ==============================================================================
    def create_financial_ui(self):
        # Financial Tabview
        financial_tab = ctk.CTkTabview(self.right_panel)
        financial_tab.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Add tabs
        financial_tab.add("Reports")
        financial_tab.add("Expenses")
        financial_tab.add("Withdrawals")
        
        # Reports Tab
        self.create_reports_ui(financial_tab.tab("Reports"))
        
        # Expenses Tab
        self.create_expenses_ui(financial_tab.tab("Expenses"))
        
        # Withdrawals Tab
        self.create_withdrawals_ui(financial_tab.tab("Withdrawals"))

    def create_reports_ui(self, tab):
        # Reporting section with better organization
        report_label = ctk.CTkLabel(tab, 
                                   text="Generate Profit Reports",
                                   font=("Arial", 16, "bold"))
        report_label.pack(pady=(5, 10))
        
        # Report buttons grid
        report_buttons_frame = ctk.CTkFrame(tab, fg_color="transparent")
        report_buttons_frame.pack(fill="x", pady=5)
        
        daily_report_button = ctk.CTkButton(report_buttons_frame, 
                                          text="Daily", 
                                          command=lambda: self.generate_profit_report('daily'))
        daily_report_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        weekly_report_button = ctk.CTkButton(report_buttons_frame, 
                                           text="Weekly", 
                                           command=lambda: self.generate_profit_report('weekly'))
        weekly_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        monthly_report_button = ctk.CTkButton(report_buttons_frame, 
                                            text="Monthly", 
                                            command=lambda: self.generate_profit_report('monthly'))
        monthly_report_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        quarterly_report_button = ctk.CTkButton(report_buttons_frame, 
                                              text="Quarterly", 
                                              command=lambda: self.generate_profit_report('quarterly'))
        quarterly_report_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        yearly_report_button = ctk.CTkButton(report_buttons_frame, 
                                           text="Yearly", 
                                           command=lambda: self.generate_profit_report('yearly'))
        yearly_report_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Configure grid
        report_buttons_frame.grid_columnconfigure(0, weight=1)
        report_buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Financial Summary
        summary_frame = ctk.CTkFrame(tab)
        summary_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(summary_frame, 
                    text="Financial Summary", 
                    font=("Arial", 14)).pack(pady=5)
        
        # Summary buttons
        summary_btn_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(summary_btn_frame, 
                     text="Today's Summary", 
                     command=lambda: self.show_financial_summary('daily')).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(summary_btn_frame, 
                     text="This Month", 
                     command=lambda: self.show_financial_summary('monthly')).pack(side="left", expand=True, padx=2)

    def create_expenses_ui(self, tab):
        # Expenses management
        ctk.CTkLabel(tab, 
                    text="Record Expenses", 
                    font=("Arial", 16, "bold")).pack(pady=(5, 10))
        
        # Expense form
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(form_frame, text="Expense Description:").pack(anchor="w", padx=5)
        self.expense_desc_entry = ctk.CTkEntry(form_frame)
        self.expense_desc_entry.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(form_frame, text="Amount (PKR):").pack(anchor="w", padx=5)
        self.expense_amount_entry = ctk.CTkEntry(form_frame)
        self.expense_amount_entry.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(form_frame, text="Category:").pack(anchor="w", padx=5)
        self.expense_category_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Utilities, Supplies")
        self.expense_category_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(btn_frame, 
                     text="Add Expense", 
                     command=self.add_expense).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(btn_frame, 
                     text="Clear", 
                     command=self.clear_expense_entries).pack(side="right", expand=True, padx=2)
        
        # Expenses list
        self.expenses_list = ctk.CTkScrollableFrame(tab, height=200)
        self.expenses_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_expenses_list()

    def add_expense(self):
        description = self.expense_desc_entry.get().strip()
        amount_str = self.expense_amount_entry.get().strip()
        category = self.expense_category_entry.get().strip() or "Uncategorized"
        
        if not description:
            messagebox.showerror("Error", "Description is required")
            self.expense_desc_entry.configure(border_color="red")
            return
        
        if not amount_str:
            messagebox.showerror("Error", "Amount is required")
            self.expense_amount_entry.configure(border_color="red")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            self.expense_amount_entry.configure(border_color="red")
            return
        
        expense_record = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "amount": amount,
            "category": category
        }
        
        self.expenses.append(expense_record)
        self.save_data(self.expenses_file, self.expenses)
        self.update_expenses_list()
        self.clear_expense_entries()
        messagebox.showinfo("Success", "Expense recorded successfully")

    def clear_expense_entries(self):
        self.expense_desc_entry.delete(0, 'end')
        self.expense_amount_entry.delete(0, 'end')
        self.expense_category_entry.delete(0, 'end')
        self.expense_desc_entry.configure(border_color="#979DA2")
        self.expense_amount_entry.configure(border_color="#979DA2")

    def update_expenses_list(self):
        for widget in self.expenses_list.winfo_children():
            widget.destroy()
        
        if not self.expenses:
            empty_label = ctk.CTkLabel(self.expenses_list, text="No expenses recorded")
            empty_label.pack(pady=10)
            return
        
        for expense in self.expenses[-20:]:  # Show last 20 expenses
            timestamp = datetime.fromisoformat(expense['timestamp'])
            item_frame = ctk.CTkFrame(self.expenses_list, height=35)
            item_frame.pack(fill="x", pady=2, padx=2)
            
            # Expense info
            info_label = ctk.CTkLabel(item_frame, 
                                    text=f"{timestamp.strftime('%m/%d %H:%M')} - {expense['description']}",
                                    anchor="w")
            info_label.pack(side="left", padx=5, fill="x", expand=True)
            
            # Category and amount
            category_label = ctk.CTkLabel(item_frame, 
                                        text=f"{expense['category']}",
                                        text_color="gray")
            category_label.pack(side="left", padx=5)
            
            amount_label = ctk.CTkLabel(item_frame, 
                                      text=f"-{expense['amount']:.2f} PKR",
                                      text_color="red")
            amount_label.pack(side="right", padx=5)

    def create_withdrawals_ui(self, tab):
        # Withdrawals management
        ctk.CTkLabel(tab, 
                    text="Record Withdrawals", 
                    font=("Arial", 16, "bold")).pack(pady=(5, 10))
        
        # Withdrawal form
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(form_frame, text="Withdrawal Purpose:").pack(anchor="w", padx=5)
        self.withdrawal_purpose_entry = ctk.CTkEntry(form_frame)
        self.withdrawal_purpose_entry.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkLabel(form_frame, text="Amount (PKR):").pack(anchor="w", padx=5)
        self.withdrawal_amount_entry = ctk.CTkEntry(form_frame)
        self.withdrawal_amount_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(btn_frame, 
                     text="Record Withdrawal", 
                     command=self.add_withdrawal).pack(side="left", expand=True, padx=2)
        
        ctk.CTkButton(btn_frame, 
                     text="Clear", 
                     command=self.clear_withdrawal_entries).pack(side="right", expand=True, padx=2)
        
        # Withdrawals list
        self.withdrawals_list = ctk.CTkScrollableFrame(tab, height=200)
        self.withdrawals_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_withdrawals_list()

    def add_withdrawal(self):
        purpose = self.withdrawal_purpose_entry.get().strip()
        amount_str = self.withdrawal_amount_entry.get().strip()
        
        if not purpose:
            messagebox.showerror("Error", "Purpose is required")
            self.withdrawal_purpose_entry.configure(border_color="red")
            return
        
        if not amount_str:
            messagebox.showerror("Error", "Amount is required")
            self.withdrawal_amount_entry.configure(border_color="red")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            self.withdrawal_amount_entry.configure(border_color="red")
            return
        
        withdrawal_record = {
            "timestamp": datetime.now().isoformat(),
            "purpose": purpose,
            "amount": amount
        }
        
        self.withdrawals.append(withdrawal_record)
        self.save_data(self.withdrawals_file, self.withdrawals)
        self.update_withdrawals_list()
        self.clear_withdrawal_entries()
        messagebox.showinfo("Success", "Withdrawal recorded successfully")

    def clear_withdrawal_entries(self):
        self.withdrawal_purpose_entry.delete(0, 'end')
        self.withdrawal_amount_entry.delete(0, 'end')
        self.withdrawal_purpose_entry.configure(border_color="#979DA2")
        self.withdrawal_amount_entry.configure(border_color="#979DA2")

    def update_withdrawals_list(self):
        for widget in self.withdrawals_list.winfo_children():
            widget.destroy()
        
        if not self.withdrawals:
            empty_label = ctk.CTkLabel(self.withdrawals_list, text="No withdrawals recorded")
            empty_label.pack(pady=10)
            return
        
        for withdrawal in self.withdrawals[-20:]:  # Show last 20 withdrawals
            timestamp = datetime.fromisoformat(withdrawal['timestamp'])
            item_frame = ctk.CTkFrame(self.withdrawals_list, height=35)
            item_frame.pack(fill="x", pady=2, padx=2)
            
            # Withdrawal info
            info_label = ctk.CTkLabel(item_frame, 
                                    text=f"{timestamp.strftime('%m/%d %H:%M')} - {withdrawal['purpose']}",
                                    anchor="w")
            info_label.pack(side="left", padx=5, fill="x", expand=True)
            
            # Amount
            amount_label = ctk.CTkLabel(item_frame, 
                                      text=f"-{withdrawal['amount']:.2f} PKR",
                                      text_color="orange")
            amount_label.pack(side="right", padx=5)

    # ==============================================================================
    # Reporting (Enhanced)
    # ==============================================================================
    def generate_profit_report(self, period):
        today = datetime.now()
        start_date, end_date = self.get_date_range(period)
        
        # Calculate profit from sales
        sales_profit = 0
        sales_revenue = 0
        sales_cost = 0
        
        for sale in self.sales:
            sale_time = datetime.fromisoformat(sale['timestamp'])
            if start_date <= sale_time < end_date:
                sales_revenue += sale['total']
                for item in sale['items']:
                    sales_cost += item['purchase_price']
        
        sales_profit = sales_revenue - sales_cost
        
        # Calculate total expenses
        total_expenses = sum(
            exp['amount'] for exp in self.expenses
            if start_date <= datetime.fromisoformat(exp['timestamp']) < end_date
        )
        
        # Calculate total withdrawals
        total_withdrawals = sum(
            wd['amount'] for wd in self.withdrawals
            if start_date <= datetime.fromisoformat(wd['timestamp']) < end_date
        )
        
        # Net profit (after expenses and withdrawals)
        net_profit = sales_profit - total_expenses - total_withdrawals
        
        # Generate report filename
        report_filename = f"reports/{period}_financial_report_{today.strftime('%Y-%m-%d')}.txt"
        
        try:
            with open(report_filename, 'w') as f:
                f.write(f"{'Sabi Qureshi\'s POS':^40}\n")
                f.write(f"{period.capitalize()} Financial Report\n")
                f.write("="*40 + "\n")
                f.write(f"Report Generated: {today.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
                f.write("="*40 + "\n\n")
                
                # Sales section
                f.write("Sales Summary:\n")
                f.write("-"*40 + "\n")
                f.write(f"Total Revenue: {sales_revenue:.2f} PKR\n")
                f.write(f"Cost of Goods Sold: {sales_cost:.2f} PKR\n")
                f.write(f"Gross Profit: {sales_profit:.2f} PKR\n")
                f.write("-"*40 + "\n\n")
                
                # Expenses section
                f.write("Expenses Summary:\n")
                f.write("-"*40 + "\n")
                f.write(f"Total Expenses: {total_expenses:.2f} PKR\n")
                f.write("-"*40 + "\n\n")
                
                # Withdrawals section
                f.write("Withdrawals Summary:\n")
                f.write("-"*40 + "\n")
                f.write(f"Total Withdrawals: {total_withdrawals:.2f} PKR\n")
                f.write("-"*40 + "\n\n")
                
                # Final summary
                f.write("Final Summary:\n")
                f.write("-"*40 + "\n")
                f.write(f"Net Profit: {net_profit:.2f} PKR\n")
                f.write("="*40 + "\n")
        except IOError:
            messagebox.showerror("Error", "Failed to generate report file")
            return
        
        # Show success message
        report_popup = ctk.CTkToplevel(self)
        report_popup.title("Report Generated")
        report_popup.geometry("400x150")
        
        ctk.CTkLabel(report_popup, 
                    text=f"{period.capitalize()} Financial Report Generated",
                    font=("Arial", 14)).pack(pady=10)
        
        ctk.CTkLabel(report_popup,
             text=f"Saved to: {report_filename}", # Corrected line: use report_filename
             font=("Arial", 12)).pack(pady=5)

        
        ctk.CTkButton(report_popup, 
                     text="OK", 
                     command=report_popup.destroy).pack(pady=10)

    def show_financial_summary(self, period):
        today = datetime.now()
        start_date, end_date = self.get_date_range(period)
        
        # Calculate sales data
        total_sales = 0
        total_profit = 0
        sales_count = 0
        
        for sale in self.sales:
            sale_time = datetime.fromisoformat(sale['timestamp'])
            if start_date <= sale_time < end_date:
                total_sales += sale['total']
                sales_count += 1
                for item in sale['items']:
                    total_profit += (item['sale_price'] - item['purchase_price'])
        
        # Calculate expenses
        total_expenses = sum(
            exp['amount'] for exp in self.expenses
            if start_date <= datetime.fromisoformat(exp['timestamp']) < end_date
        )
        
        # Calculate withdrawals
        total_withdrawals = sum(
            wd['amount'] for wd in self.withdrawals
            if start_date <= datetime.fromisoformat(wd['timestamp']) < end_date
        )
        
        # Create summary popup
        summary_popup = ctk.CTkToplevel(self)
        summary_popup.title(f"{period.capitalize()} Financial Summary")
        summary_popup.geometry("500x300")
        
        # Summary content
        summary_frame = ctk.CTkFrame(summary_popup)
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(summary_frame, 
                    text=f"{period.capitalize()} Financial Summary",
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Summary data
        data_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Total Sales: {total_sales:.2f} PKR",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Number of Transactions: {sales_count}",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Gross Profit: {total_profit:.2f} PKR",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Total Expenses: {total_expenses:.2f} PKR",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(data_frame, 
                    text=f"Total Withdrawals: {total_withdrawals:.2f} PKR",
                    font=("Arial", 12)).pack(anchor="w", pady=2)
        
        net_income = total_profit - total_expenses - total_withdrawals
        net_color = "green" if net_income >= 0 else "red"
        
        ctk.CTkLabel(data_frame, 
                    text=f"Net Income: {net_income:.2f} PKR",
                    text_color=net_color,
                    font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        
        # Close button
        ctk.CTkButton(summary_frame, 
                     text="Close", 
                     command=summary_popup.destroy).pack(pady=10)

    def get_date_range(self, period):
        today = datetime.now()
        
        if period == 'daily':
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(weeks=1)
        elif period == 'monthly':
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if today.month == 12:
                end_date = today.replace(year=today.year+1, month=1, day=1)
            else:
                end_date = today.replace(month=today.month+1, day=1)
        elif period == 'quarterly':
            quarter = (today.month - 1) // 3
            start_date = today.replace(month=quarter*3+1, day=1, hour=0, minute=0, second=0, microsecond=0)
            if quarter == 3:
                end_date = today.replace(year=today.year+1, month=1, day=1)
            else:
                end_date = today.replace(month=start_date.month+3, day=1)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(year=today.year+1, month=1, day=1)
        else:
            start_date = today
            end_date = today + timedelta(days=1)
            
        return start_date, end_date

if __name__ == "__main__":
    app = SabiQureshiPOS()
    app.mainloop()