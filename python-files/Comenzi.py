import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os

class OrderManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Order Management System")
        self.root.geometry("1000x700")
        
        # Initialize data
        self.filename = "orders.xlsx"
        self.orders = []
        self.couriers = ["Pallex", "KLG", "Sameday"]
        self.status_options = [
            "Comanda plasata", 
            "Spre livrare", 
            "In asteptare", 
            "Livrata"
        ]
        
        # Create Excel file if it doesn't exist
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=[
                "Order Number", 
                "Recipient Name", 
                "Courier", 
                "Products", 
                "Products Type", 
                "Products Notes", 
                "Date", 
                "Payment Type", 
                "Cash on Delivery Amount", 
                "Status", 
                "Waiting Reason"
            ])
            df.to_excel(self.filename, index=False)
        
        self.load_orders()
        
        # Create GUI
        self.create_widgets()
        
    def load_orders(self):
        try:
            df = pd.read_excel(self.filename)
            self.orders = df.to_dict('records')
        except:
            self.orders = []
    
    def save_orders(self):
        df = pd.DataFrame(self.orders)
        df.to_excel(self.filename, index=False)
    
    def create_widgets(self):
        # Search Frame
        search_frame = ttk.LabelFrame(self.root, text="Cautare Comenzi", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.search_orders)
        
        search_btn = ttk.Button(search_frame, text="Cauta", command=self.search_orders)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(search_frame, text="Reseteaza", command=self.reset_search)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Orders Treeview
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=(
            "Order Number", "Recipient Name", "Courier", "Date", "Status"
        ), show="headings")
        
        self.tree.heading("Order Number", text="Nr. Comanda")
        self.tree.heading("Recipient Name", text="Destinatar")
        self.tree.heading("Courier", text="Curier")
        self.tree.heading("Date", text="Data")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("Order Number", width=100)
        self.tree.column("Recipient Name", width=200)
        self.tree.column("Courier", width=100)
        self.tree.column("Date", width=100)
        self.tree.column("Status", width=150)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<ButtonRelease-1>", self.select_order)
        
        # Buttons Frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_btn = ttk.Button(btn_frame, text="Adauga Comanda", command=self.add_order_window)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(btn_frame, text="Editeaza Comanda", command=self.edit_order_window)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Sterge Comanda", command=self.delete_order)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Gata")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.refresh_treeview()
    
    def refresh_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for order in self.orders:
            self.tree.insert("", tk.END, values=(
                order["Order Number"],
                order["Recipient Name"],
                order["Courier"],
                order["Date"],
                order["Status"]
            ))
    
    def search_orders(self, event=None):
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.refresh_treeview()
            return
        
        filtered_orders = []
        for order in self.orders:
            if (search_term in str(order["Order Number"]).lower() or 
                search_term in order["Recipient Name"].lower()):
                filtered_orders.append(order)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for order in filtered_orders:
            self.tree.insert("", tk.END, values=(
                order["Order Number"],
                order["Recipient Name"],
                order["Courier"],
                order["Date"],
                order["Status"]
            ))
    
    def reset_search(self):
        self.search_var.set("")
        self.refresh_treeview()
    
    def select_order(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_order = self.tree.item(selected_item)["values"]
    
    def add_order_window(self):
        self.order_window = tk.Toplevel(self.root)
        self.order_window.title("Adauga Comanda Noua")
        self.order_window.geometry("600x700")
        
        self.create_order_form(self.order_window, mode="add")
    
    def edit_order_window(self):
        if not hasattr(self, 'selected_order'):
            messagebox.showwarning("Avertisment", "Selectati o comanda pentru a o edita!")
            return
        
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Avertisment", "Selectati o comanda pentru a o edita!")
            return
        
        self.order_window = tk.Toplevel(self.root)
        self.order_window.title("Editeaza Comanda")
        self.order_window.geometry("600x700")
        
        order_number = self.tree.item(selected_item)["values"][0]
        self.order_to_edit = next((order for order in self.orders if str(order["Order Number"]) == str(order_number)), None)
        
        if not self.order_to_edit:
            messagebox.showerror("Eroare", "Comanda selectata nu a putut fi gasita!")
            self.order_window.destroy()
            return
        
        self.create_order_form(self.order_window, mode="edit", order=self.order_to_edit)
    
    def create_order_form(self, window, mode, order=None):
        # Order Number
        ttk.Label(window, text="Numar Comanda (4 cifre):").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.order_num_var = tk.StringVar()
        if mode == "edit":
            self.order_num_var.set(order["Order Number"])
        order_num_entry = ttk.Entry(window, textvariable=self.order_num_var)
        order_num_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Recipient Name
        ttk.Label(window, text="Nume Destinatar/Firma:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.recipient_var = tk.StringVar()
        if mode == "edit":
            self.recipient_var.set(order["Recipient Name"])
        recipient_entry = ttk.Entry(window, textvariable=self.recipient_var)
        recipient_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Courier
        ttk.Label(window, text="Curier:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.courier_var = tk.StringVar()
        if mode == "edit":
            self.courier_var.set(order["Courier"])
        courier_combo = ttk.Combobox(window, textvariable=self.courier_var, values=self.couriers, state="readonly")
        courier_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Products
        ttk.Label(window, text="Produse:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.products_var = tk.StringVar()
        self.products_var.set("Toate produsele")
        if mode == "edit":
            self.products_var.set(order["Products Type"])
        
        products_frame = ttk.Frame(window)
        products_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Radiobutton(products_frame, text="Toate produsele", variable=self.products_var, value="Toate produsele").pack(side=tk.LEFT)
        ttk.Radiobutton(products_frame, text="Partial", variable=self.products_var, value="Partial").pack(side=tk.LEFT)
        
        # Products Notes
        ttk.Label(window, text="Note Produse (daca e Partial):").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.products_notes_var = tk.StringVar()
        if mode == "edit":
            self.products_notes_var.set(order["Products Notes"])
        products_notes_entry = tk.Text(window, height=4)
        if mode == "edit":
            products_notes_entry.insert("1.0", order["Products Notes"])
        products_notes_entry.pack(fill=tk.X, padx=10, pady=5)
        self.products_notes_entry = products_notes_entry
        
        # Date
        ttk.Label(window, text="Data:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.date_var = tk.StringVar()
        if mode == "edit":
            self.date_var.set(order["Date"])
        else:
            self.date_var.set(datetime.now().strftime("%d.%m.%Y"))
        date_entry = ttk.Entry(window, textvariable=self.date_var)
        date_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Payment
        ttk.Label(window, text="Plata:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.payment_var = tk.StringVar()
        self.payment_var.set("Achitat")
        if mode == "edit":
            self.payment_var.set(order["Payment Type"])
        
        payment_frame = ttk.Frame(window)
        payment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Radiobutton(payment_frame, text="Achitat", variable=self.payment_var, value="Achitat").pack(side=tk.LEFT)
        ttk.Radiobutton(payment_frame, text="Ramburs", variable=self.payment_var, value="Ramburs").pack(side=tk.LEFT)
        
        # Cash on Delivery Amount
        ttk.Label(window, text="Suma Ramburs:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.cod_var = tk.StringVar()
        if mode == "edit":
            self.cod_var.set(order["Cash on Delivery Amount"])
        cod_entry = ttk.Entry(window, textvariable=self.cod_var)
        cod_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Status
        ttk.Label(window, text="Status:").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.status_form_var = tk.StringVar()
        if mode == "edit":
            self.status_form_var.set(order["Status"])
        else:
            self.status_form_var.set("Comanda plasata")
        status_combo = ttk.Combobox(window, textvariable=self.status_form_var, values=self.status_options, state="readonly")
        status_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Waiting Reason
        ttk.Label(window, text="Motiv Asteptare (daca e cazul):").pack(pady=(10, 0), padx=10, anchor=tk.W)
        self.waiting_reason_var = tk.StringVar()
        if mode == "edit":
            self.waiting_reason_var.set(order["Waiting Reason"])
        waiting_reason_entry = ttk.Entry(window, textvariable=self.waiting_reason_var)
        waiting_reason_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if mode == "add":
            save_btn = ttk.Button(btn_frame, text="Salveaza", command=self.save_new_order)
            save_btn.pack(side=tk.RIGHT, padx=5)
        else:
            save_btn = ttk.Button(btn_frame, text="Actualizeaza", command=lambda: self.update_order(order))
            save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Anuleaza", command=window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def save_new_order(self):
        # Validate order number
        order_num = self.order_num_var.get().strip()
        if not order_num.isdigit() or len(order_num) != 4:
            messagebox.showerror("Eroare", "Numarul comenzii trebuie sa fie format din exact 4 cifre!")
            return
        
        # Check if order number already exists
        if any(str(order["Order Number"]) == order_num for order in self.orders):
            messagebox.showerror("Eroare", "Exista deja o comanda cu acest numar!")
            return
        
        # Validate recipient name
        recipient_name = self.recipient_var.get().strip()
        if not recipient_name:
            messagebox.showerror("Eroare", "Numele destinatarului este obligatoriu!")
            return
        
        # Create new order
        new_order = {
            "Order Number": order_num,
            "Recipient Name": recipient_name,
            "Courier": self.courier_var.get(),
            "Products": self.products_var.get(),
            "Products Type": self.products_var.get(),
            "Products Notes": self.products_notes_entry.get("1.0", tk.END).strip(),
            "Date": self.date_var.get(),
            "Payment Type": self.payment_var.get(),
            "Cash on Delivery Amount": self.cod_var.get() if self.payment_var.get() == "Ramburs" else "",
            "Status": self.status_form_var.get(),
            "Waiting Reason": self.waiting_reason_var.get() if self.status_form_var.get() == "In asteptare" else ""
        }
        
        self.orders.append(new_order)
        self.save_orders()
        self.refresh_treeview()
        self.order_window.destroy()
        messagebox.showinfo("Succes", "Comanda a fost adaugata cu succes!")
    
    def update_order(self, old_order):
        # Validate order number
        order_num = self.order_num_var.get().strip()
        if not order_num.isdigit() or len(order_num) != 4:
            messagebox.showerror("Eroare", "Numarul comenzii trebuie sa fie format din exact 4 cifre!")
            return
        
        # Check if order number is changed and already exists
        if str(old_order["Order Number"]) != order_num and any(str(order["Order Number"]) == order_num for order in self.orders):
            messagebox.showerror("Eroare", "Exista deja o comanda cu acest numar!")
            return
        
        # Validate recipient name
        recipient_name = self.recipient_var.get().strip()
        if not recipient_name:
            messagebox.showerror("Eroare", "Numele destinatarului este obligatoriu!")
            return
        
        # Update order
        updated_order = {
            "Order Number": order_num,
            "Recipient Name": recipient_name,
            "Courier": self.courier_var.get(),
            "Products": self.products_var.get(),
            "Products Type": self.products_var.get(),
            "Products Notes": self.products_notes_entry.get("1.0", tk.END).strip(),
            "Date": self.date_var.get(),
            "Payment Type": self.payment_var.get(),
            "Cash on Delivery Amount": self.cod_var.get() if self.payment_var.get() == "Ramburs" else "",
            "Status": self.status_form_var.get(),
            "Waiting Reason": self.waiting_reason_var.get() if self.status_form_var.get() == "In asteptare" else ""
        }
        
        # Find and update the order
        for i, order in enumerate(self.orders):
            if str(order["Order Number"]) == str(old_order["Order Number"]):
                self.orders[i] = updated_order
                break
        
        self.save_orders()
        self.refresh_treeview()
        self.order_window.destroy()
        messagebox.showinfo("Succes", "Comanda a fost actualizata cu succes!")
    
    def delete_order(self):
        if not hasattr(self, 'selected_order'):
            messagebox.showwarning("Avertisment", "Selectati o comanda pentru a o sterge!")
            return
        
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Avertisment", "Selectati o comanda pentru a o sterge!")
            return
        
        order_number = self.tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Confirmare", f"Sunteti sigur ca doriti sa stergeti comanda {order_number}?"):
            self.orders = [order for order in self.orders if str(order["Order Number"]) != str(order_number)]
            self.save_orders()
            self.refresh_treeview()
            messagebox.showinfo("Succes", "Comanda a fost stearsa cu succes!")
    
    def refresh_data(self):
        self.load_orders()
        self.refresh_treeview()
        self.status_var.set("Date reincarcate cu succes")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderManagementSystem(root)
    root.mainloop()