import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import json
import datetime
import os
import hashlib # For simple password hashing (for demonstration)
# from PIL import Image, ImageTk # Uncomment these two lines if you want to support JPG/JPEG images
                                # and run 'pip install Pillow' in your terminal

# --- File Paths for Data Persistence ---
STOCK_FILE = "stock_data.json"
SALES_FILE = "sales_history.json"
USERS_FILE = "users.json"
EXPENSES_FILE = "expenses_data.json"

# --- Pre-defined Admin User ---
DEFAULT_ADMIN_USER = {
    "username": "Admin",
    "password_hash": hashlib.sha256("123".encode()).hexdigest(), # Hashed password for '123'
    "role": "Admin"
}

# --- Main Application Class ---
class SimplePOSApp:
    def __init__(self, master):
        self.master = master
        master.withdraw() # Hide the main window initially
        master.title("Simple POS System")
        master.geometry("1100x750")
        master.resizable(True, True)
        master.configure(bg="#f8f9fa")

        self.logged_in_user = None
        self.user_role = None

        self.current_order = []
        self.stock = {}
        self.sales_history = []
        self.users = {}
        self.expenses = []

        self._load_data()
        self._ensure_admin_exists() # Ensure admin user is present on first run

        self._setup_styles() # Centralized style setup
        self._create_login_window() # Show login window first

    def _load_data(self):
        """Loads all application data from JSON files."""
        def load_json(filepath, default_value):
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    messagebox.showerror("Data Error", f"Could not load {filepath}. File might be corrupted. Starting fresh for this data type.")
                    return default_value
            return default_value

        self.stock = load_json(STOCK_FILE, {})
        self.sales_history = load_json(SALES_FILE, [])
        self.users = load_json(USERS_FILE, {})
        self.expenses = load_json(EXPENSES_FILE, [])

    def _save_data(self):
        """Saves all application data to JSON files."""
        def save_json(filepath, data):
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save data to {filepath}: {e}")

        save_json(STOCK_FILE, self.stock)
        save_json(SALES_FILE, self.sales_history)
        save_json(USERS_FILE, self.users)
        save_json(EXPENSES_FILE, self.expenses)

    def _ensure_admin_exists(self):
        """Ensures the default 'Admin' user exists."""
        if DEFAULT_ADMIN_USER["username"] not in self.users:
            self.users[DEFAULT_ADMIN_USER["username"]] = {
                "password_hash": DEFAULT_ADMIN_USER["password_hash"],
                "role": DEFAULT_ADMIN_USER["role"]
            }
            self._save_data() # Save immediately after adding admin

    def _setup_styles(self):
        """Configures the ttk styles for a modern look."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TFrame', background='#f8f9fa')
        self.style.configure('TLabel', background='#f8f9fa', font=('Inter', 12), foreground='#343a40')
        self.style.configure('TEntry', font=('Inter', 12), padding=8, fieldbackground='white', foreground='#343a40', borderwidth=1, relief="solid", bordercolor="#ced4da")
        self.style.configure('TButton', font=('Inter', 12, 'bold'), padding=10, relief="flat", borderwidth=0)
        self.style.map('TButton', background=[('active', '#e9ecef')])

        self.style.configure('TLabelframe', background='#ffffff', relief="flat", borderwidth=1, bordercolor="#dee2e6")
        self.style.configure('TLabelframe.Label', font=('Inter', 15, 'bold'), foreground='#343a40', background='#ffffff', padding=[10, 5])

        self.style.configure('Primary.TButton', background='#007bff', foreground='white')
        self.style.map('Primary.TButton', background=[('active', '#0056b3')])

        self.style.configure('Danger.TButton', background='#dc3545', foreground='white')
        self.style.map('Danger.TButton', background=[('active', '#c82333')])

        self.style.configure('Success.TButton', background='#28a745', foreground='white')
        self.style.map('Success.TButton', background=[('active', '#218838')])

        self.style.configure('Info.TButton', background='#17a2b8', foreground='white')
        self.style.map('Info.TButton', background=[('active', '#138496')])

        self.style.configure('Treeview.Heading', font=('Inter', 12, 'bold'), background='#6c757d', foreground='white', padding=[5, 10])
        self.style.configure('Treeview', font=('Inter', 12), rowheight=30, background='white', fieldbackground='white', foreground='#343a40', borderwidth=1, relief="solid", bordercolor="#dee2e6")
        self.style.map('Treeview', background=[('selected', '#a8d8ff')])

        self.style.configure('TNotebook', background='#f8f9fa', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#e9ecef', foreground='#495057', padding=[15, 8], font=('Inter', 13, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#ffffff')], foreground=[('selected', '#007bff')])

        # Login window specific styles
        self.style.configure('Login.TFrame', background='#e0e0e0')
        self.style.configure('Login.TLabel', background='#e0e0e0', font=('Inter', 14, 'bold'), foreground='#343a40')
        self.style.configure('Login.TEntry', font=('Inter', 14), padding=10, fieldbackground='white', foreground='#343a40', borderwidth=1, relief="solid", bordercolor="#adb5bd")
        self.style.configure('Login.TButton', font=('Inter', 14, 'bold'), padding=12, relief="flat", background='#007bff', foreground='white')
        self.style.map('Login.TButton', background=[('active', '#0056b3')])


    def _create_login_window(self):
        """Creates and displays the login window."""
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Login")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg="#e0e0e0")
        self.login_window.transient(self.master) # Make it appear on top of main window (even if main is hidden)
        self.login_window.grab_set() # Make it modal

        # Center the login window
        self.login_window.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.login_window.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.login_window.winfo_height() // 2)
        self.login_window.geometry(f"+{x}+{y}")

        login_frame = ttk.Frame(self.login_window, padding="25", style='Login.TFrame')
        login_frame.pack(expand=True)

        ttk.Label(login_frame, text="Username:", style='Login.TLabel').pack(pady=10)
        self.username_entry = ttk.Entry(login_frame, style='Login.TEntry')
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set()

        ttk.Label(login_frame, text="Password:", style='Login.TLabel').pack(pady=10)
        self.password_entry = ttk.Entry(login_frame, show="*", style='Login.TEntry')
        self.password_entry.pack(pady=5)

        ttk.Button(login_frame, text="Login", command=self._authenticate_user, style='Login.TButton').pack(pady=20)

        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self._authenticate_user())

        # Protocol for closing login window
        self.login_window.protocol("WM_DELETE_WINDOW", self.master.destroy) # Close entire app if login window closed

    def _authenticate_user(self):
        """Authenticates user credentials."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Login Error", "Please enter both username and password.", parent=self.login_window)
            return

        if username not in self.users:
            messagebox.showerror("Login Error", "Invalid username.", parent=self.login_window)
            return

        stored_password_hash = self.users[username]["password_hash"]
        entered_password_hash = hashlib.sha256(password.encode()).hexdigest()

        if entered_password_hash == stored_password_hash:
            self.logged_in_user = username
            self.user_role = self.users[username]["role"]
            self.login_window.destroy()
            self.master.deiconify() # Show the main window
            self._create_main_app_layout()
            self._update_status_bar() # Initial status bar update
            self._update_time() # Start live time update
        else:
            messagebox.showerror("Login Error", "Invalid password.", parent=self.login_window)

    def _create_main_app_layout(self):
        """Creates the main application layout after successful login."""
        # --- Notebook (Tabbed Interface) ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(pady=15, padx=15, fill="both", expand=True)

        # --- POS (Sales) Tab ---
        self.pos_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.pos_frame, text="  POS (Sales)  ")
        self._create_pos_tab(self.pos_frame)

        # --- Stock Management Tab ---
        self.stock_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.stock_frame, text="  Stock Management  ")
        self._create_stock_tab(self.stock_frame)

        # --- Expenses Tab ---
        self.expenses_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.expenses_frame, text="  Expenses  ")
        self._create_expenses_tab(self.expenses_frame)

        # --- Sales Reports Tab ---
        self.reports_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.reports_frame, text="  Sales Reports  ")
        self._create_reports_tab(self.reports_frame)

        # --- Daily Summary Report Tab ---
        self.daily_summary_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.daily_summary_frame, text="  Daily Summary  ")
        self._create_daily_summary_tab(self.daily_summary_frame)

        # --- User Management Tab (Admin Only) ---
        self.user_management_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.user_management_frame, text="  User Management  ")
        self._create_user_management_tab(self.user_management_frame)

        # Bind tab change event to refresh data and check permissions
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Status Bar
        self.status_bar = ttk.Frame(self.master, relief=tk.SUNKEN, borderwidth=1, padding="5 10")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.time_label = ttk.Label(self.status_bar, text="", font=('Inter', 10), background='#f0f0f0')
        self.time_label.pack(side=tk.LEFT, padx=10)

        self.user_label = ttk.Label(self.status_bar, text="", font=('Inter', 10, 'bold'), background='#f0f0f0', foreground='#007bff')
        self.user_label.pack(side=tk.RIGHT, padx=10)

        self._apply_permissions() # Apply initial permissions after tabs are created

    def _update_time(self):
        """Updates the live time in the status bar."""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Current Time: {current_time}")
        self.master.after(1000, self._update_time) # Update every 1 second

    def _update_status_bar(self):
        """Updates the logged-in user display in the status bar."""
        self.user_label.config(text=f"Logged in as: {self.logged_in_user} ({self.user_role})")

    def _apply_permissions(self):
        """Applies permissions based on the logged-in user's role."""
        # Define tab indices for easy reference
        tab_names = [self.notebook.tab(i, "text").strip() for i in range(self.notebook.index("end"))]
        tab_map = {name: i for i, name in enumerate(tab_names)}

        # Default all tabs to disabled
        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")

        if self.user_role == "Admin":
            for i in range(self.notebook.index("end")):
                self.notebook.tab(i, state="normal")
            self.notebook.select(tab_map.get("POS (Sales)", 0)) # Default to POS
        elif self.user_role == "Sales":
            self.notebook.tab(tab_map["POS (Sales)"], state="normal")
            self.notebook.tab(tab_map["Sales Reports"], state="normal")
            self.notebook.select(tab_map["POS (Sales)"])
        elif self.user_role == "StockManager":
            self.notebook.tab(tab_map["POS (Sales)"], state="normal")
            self.notebook.tab(tab_map["Stock Management"], state="normal")
            self.notebook.tab(tab_map["Sales Reports"], state="normal")
            self.notebook.select(tab_map["Stock Management"])
        elif self.user_role == "Viewer":
            self.notebook.tab(tab_map["Sales Reports"], state="normal")
            self.notebook.tab(tab_map["Daily Summary"], state="normal")
            self.notebook.select(tab_map["Sales Reports"])
        else:
            messagebox.showwarning("Permission Denied", "Your role does not have access to any sections. Please contact administrator.")
            self.master.destroy() # Close app if no access

    def _on_tab_change(self, event):
        """Refreshes data display and re-applies permissions when a tab is changed."""
        selected_tab_name = self.notebook.tab(self.notebook.select(), "text").strip()

        # Re-check permissions on tab change, though _apply_permissions handles most
        # This is more for dynamic scenarios or if direct access is attempted
        allowed_to_switch = False
        if self.user_role == "Admin":
            allowed_to_switch = True
        elif self.user_role == "Sales" and selected_tab_name in ["POS (Sales)", "Sales Reports"]:
            allowed_to_switch = True
        elif self.user_role == "StockManager" and selected_tab_name in ["POS (Sales)", "Stock Management", "Sales Reports"]:
            allowed_to_switch = True
        elif self.user_role == "Viewer" and selected_tab_name in ["Sales Reports", "Daily Summary"]:
            allowed_to_switch = True

        if not allowed_to_switch:
            messagebox.showwarning("Permission Denied", f"Your role ({self.user_role}) does not have permission to access '{selected_tab_name}'.")
            # Revert to a permitted tab if possible, or just stay put
            if self.user_role == "Sales":
                self.notebook.select(self.notebook.tab("POS (Sales)", "text"))
            elif self.user_role == "StockManager":
                self.notebook.select(self.notebook.tab("Stock Management", "text"))
            elif self.user_role == "Viewer":
                self.notebook.select(self.notebook.tab("Sales Reports", "text"))
            else: # Admin or no specific role, try POS
                self.notebook.select(self.notebook.tab("POS (Sales)", "text"))
            return

        # Refresh data for the selected tab
        if "Stock Management" in selected_tab_name:
            self.update_stock_display()
        elif "Sales Reports" in selected_tab_name:
            self.update_reports_display()
        elif "POS (Sales)" in selected_tab_name:
            self.update_pos_item_suggestions()
        elif "Expenses" in selected_tab_name:
            self.update_expenses_display()
        elif "Daily Summary" in selected_tab_name:
            self.update_daily_summary_report()
        elif "User Management" in selected_tab_name:
            self.update_user_display()

    # --- POS (Sales) Tab Methods ---
    def _create_pos_tab(self, parent_frame):
        """Configures the POS (Sales) tab layout and widgets."""
        entry_section = ttk.LabelFrame(parent_frame, text="Add Item to Order", padding="20")
        entry_section.pack(pady=15, padx=15, fill="x")

        ttk.Label(entry_section, text="Item Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.pos_item_name_entry = ttk.Entry(entry_section, width=40)
        self.pos_item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.pos_item_name_entry.focus_set()
        self.pos_item_name_entry.bind("<KeyRelease>", self.update_pos_item_suggestions)

        ttk.Label(entry_section, text="Price:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.pos_price_entry = ttk.Entry(entry_section, width=20, state='readonly')
        self.pos_price_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_section, text="Quantity:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.pos_quantity_entry = ttk.Entry(entry_section, width=15)
        self.pos_quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.pos_quantity_entry.insert(0, "1")

        ttk.Label(entry_section, text="Serial (if applicable):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.pos_serial_entry = ttk.Entry(entry_section, width=30)
        self.pos_serial_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        entry_section.grid_columnconfigure(1, weight=1)

        self.pos_suggestions_listbox = tk.Listbox(entry_section, height=5, selectmode=tk.SINGLE, font=('Inter', 12),
                                                 borderwidth=1, relief="solid", highlightbackground="#dee2e6", highlightcolor="#dee2e6")
        self.pos_suggestions_listbox.grid(row=0, column=2, rowspan=4, padx=10, pady=5, sticky="nsew")
        self.pos_suggestions_listbox.bind("<<ListboxSelect>>", self.select_pos_suggestion)
        entry_section.grid_columnconfigure(2, weight=1)

        button_frame = ttk.Frame(parent_frame, padding="15")
        button_frame.pack(pady=10, padx=15, fill="x")

        ttk.Button(button_frame, text="Add Item to Order", command=self.add_item_to_order, style='Primary.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Remove Selected Item", command=self.remove_selected_order_item, style='Danger.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Clear Order", command=self.clear_current_order, style='Danger.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Complete Sale", command=self.complete_sale, style='Success.TButton').pack(side="right", padx=8, expand=True, fill="x")

        order_display_section = ttk.LabelFrame(parent_frame, text="Current Order", padding="15")
        order_display_section.pack(pady=15, padx=15, fill="both", expand=True)

        self.pos_order_tree = ttk.Treeview(order_display_section, columns=("Item", "Price", "Quantity", "Serial", "Subtotal"), show="headings")
        self.pos_order_tree.heading("Item", text="Item Name", anchor="w")
        self.pos_order_tree.heading("Price", text="Price", anchor="e")
        self.pos_order_tree.heading("Quantity", text="Quantity", anchor="e")
        self.pos_order_tree.heading("Serial", text="Serial No.", anchor="w")
        self.pos_order_tree.heading("Subtotal", text="Subtotal", anchor="e")

        self.pos_order_tree.column("Item", width=200, minwidth=150, stretch=tk.YES)
        self.pos_order_tree.column("Price", width=80, minwidth=60, stretch=tk.NO, anchor="e")
        self.pos_order_tree.column("Quantity", width=80, minwidth=60, stretch=tk.NO, anchor="e")
        self.pos_order_tree.column("Serial", width=120, minwidth=80, stretch=tk.NO, anchor="w")
        self.pos_order_tree.column("Subtotal", width=100, minwidth=80, stretch=tk.NO, anchor="e")

        self.pos_order_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(order_display_section, orient="vertical", command=self.pos_order_tree.yview)
        self.pos_order_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        total_frame = ttk.Frame(parent_frame, padding="15")
        total_frame.pack(pady=15, padx=15, fill="x")

        ttk.Label(total_frame, text="Total:", font=('Inter', 18, 'bold')).pack(side="left", padx=10)
        self.pos_total_label = ttk.Label(total_frame, text="0.00", font=('Inter', 18, 'bold'), foreground="#007bff")
        self.pos_total_label.pack(side="right", padx=10)

        self.update_pos_total()

    def update_pos_item_suggestions(self, event=None):
        search_term = self.pos_item_name_entry.get().strip().lower()
        self.pos_suggestions_listbox.delete(0, tk.END)
        for item_name in self.stock:
            if search_term in item_name.lower():
                self.pos_suggestions_listbox.insert(tk.END, item_name)

    def select_pos_suggestion(self, event):
        selected_indices = self.pos_suggestions_listbox.curselection()
        if selected_indices:
            selected_item_name = self.pos_suggestions_listbox.get(selected_indices[0])
            if selected_item_name in self.stock:
                item_data = self.stock[selected_item_name]
                self.pos_item_name_entry.delete(0, tk.END)
                self.pos_item_name_entry.insert(0, selected_item_name)
                
                self.pos_price_entry.config(state='normal')
                self.pos_price_entry.delete(0, tk.END)
                self.pos_price_entry.insert(0, f"{item_data['price']:.2f}")
                self.pos_price_entry.config(state='readonly')

                self.pos_quantity_entry.delete(0, tk.END)
                self.pos_quantity_entry.insert(0, "1")
                self.pos_serial_entry.delete(0, tk.END)
            self.pos_suggestions_listbox.delete(0, tk.END)

    def add_item_to_order(self):
        item_name = self.pos_item_name_entry.get().strip()
        price_str = self.pos_price_entry.get().strip()
        quantity_str = self.pos_quantity_entry.get().strip()
        serial = self.pos_serial_entry.get().strip()

        if not item_name:
            messagebox.showwarning("Input Error", "Please enter an item name.")
            return

        if item_name not in self.stock:
            messagebox.showwarning("Stock Error", f"'{item_name}' not found in stock. Please add it via Stock Management.")
            return

        stock_item = self.stock[item_name]

        try:
            price = float(price_str)
            if price < 0:
                messagebox.showwarning("Input Error", "Price cannot be negative.")
                return
            if price != stock_item['price']:
                response = messagebox.askyesno("Price Mismatch", f"The entered price ({price:.2f}) differs from stock price ({stock_item['price']:.2f}). Use entered price?")
                if not response:
                    self.pos_price_entry.config(state='normal')
                    self.pos_price_entry.delete(0, tk.END)
                    self.pos_price_entry.insert(0, f"{stock_item['price']:.2f}")
                    self.pos_price_entry.config(state='readonly')
                    return

        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for price.")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showwarning("Input Error", "Quantity must be a positive integer.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid integer for quantity.")
            return

        if stock_item['quantity'] < quantity:
            messagebox.showwarning("Stock Alert", f"Not enough '{item_name}' in stock. Available: {stock_item['quantity']}")
            return

        if serial:
            if serial not in stock_item['serials']:
                messagebox.showwarning("Serial Error", f"Serial '{serial}' not found for '{item_name}' in stock.")
                return
            for order_item in self.current_order:
                if order_item['serial'] == serial and order_item['name'] == item_name:
                    messagebox.showwarning("Duplicate Serial", f"Serial '{serial}' for '{item_name}' is already in the current order.")
                    return
            if quantity > 1:
                messagebox.showwarning("Serial Error", "For items with serial numbers, quantity must be 1.")
                return
        elif stock_item['serials'] and quantity == 1:
             messagebox.showwarning("Serial Required", f"'{item_name}' requires a serial number for single quantity sale. Please enter one or increase quantity.")
             return
        elif stock_item['serials'] and quantity > 1:
            serial = "N/A"

        subtotal = price * quantity
        self.current_order.append({
            "name": item_name,
            "price": price,
            "quantity": quantity,
            "serial": serial if serial else "N/A",
            "subtotal": subtotal
        })
        self.update_pos_order_display()
        self.update_pos_total()

        self.pos_item_name_entry.delete(0, tk.END)
        self.pos_price_entry.config(state='normal')
        self.pos_price_entry.delete(0, tk.END)
        self.pos_price_entry.config(state='readonly')
        self.pos_quantity_entry.delete(0, tk.END)
        self.pos_quantity_entry.insert(0, "1")
        self.pos_serial_entry.delete(0, tk.END)
        self.pos_item_name_entry.focus_set()
        self.pos_suggestions_listbox.delete(0, tk.END)

    def remove_selected_order_item(self):
        selected_item_id = self.pos_order_tree.focus()
        if not selected_item_id:
            messagebox.showwarning("Selection Error", "Please select an item to remove from the order.")
            return

        item_index = self.pos_order_tree.index(selected_item_id)

        if messagebox.askyesno("Remove Item", "Are you sure you want to remove this item from the order?"):
            if 0 <= item_index < len(self.current_order):
                del self.current_order[item_index]
                self.update_pos_order_display()
                self.update_pos_total()
            else:
                messagebox.showerror("Error", "Could not find the selected item in the order list.")

    def update_pos_order_display(self):
        for item in self.pos_order_tree.get_children():
            self.pos_order_tree.delete(item)

        for item in self.current_order:
            self.pos_order_tree.insert("", "end", values=(
                item["name"],
                f"{item['price']:.2f}",
                item["quantity"],
                item["serial"],
                f"{item['subtotal']:.2f}"
            ))

    def update_pos_total(self):
        total = sum(item["subtotal"] for item in self.current_order)
        self.pos_total_label.config(text=f"{total:.2f}")

    def clear_current_order(self):
        if messagebox.askyesno("Clear Order", "Are you sure you want to clear the entire order?"):
            self.current_order = []
            self.update_pos_order_display()
            self.update_pos_total()
            messagebox.showinfo("Order Cleared", "The current order has been cleared.")

    def complete_sale(self):
        if not self.current_order:
            messagebox.showwarning("No Items", "The current order is empty. Add items before completing a sale.")
            return

        if messagebox.askyesno("Complete Sale", "Confirm to complete this sale?"):
            for order_item in self.current_order:
                item_name = order_item['name']
                quantity_sold = order_item['quantity']
                serial_sold = order_item['serial']

                if item_name in self.stock:
                    self.stock[item_name]['quantity'] -= quantity_sold
                    if serial_sold != "N/A" and serial_sold in self.stock[item_name]['serials']:
                        self.stock[item_name]['serials'].remove(serial_sold)

            invoice_id = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            total_amount = sum(item["subtotal"] for item in self.current_order)
            
            items_for_history = [item.copy() for item in self.current_order]

            self.sales_history.append({
                "invoice_id": invoice_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "items": items_for_history,
                "total_amount": total_amount,
                "sold_by": self.logged_in_user
            })

            self.current_order = []
            self.update_pos_order_display()
            self.update_pos_total()

            self._save_data()

            messagebox.showinfo("Sale Complete", f"Sale completed! Invoice ID: {invoice_id}\nTotal: {total_amount:.2f}")

            self.update_stock_display()
            self.update_reports_display()
            self.update_daily_summary_report()


    # --- Stock Management Tab Methods ---
    def _create_stock_tab(self, parent_frame):
        entry_panel = ttk.LabelFrame(parent_frame, text="Add/Update Stock Item", padding="20")
        entry_panel.pack(side="left", fill="y", padx=15, pady=15)

        ttk.Label(entry_panel, text="Item Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.stock_item_name_entry = ttk.Entry(entry_panel, width=30)
        self.stock_item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.stock_item_name_entry.bind("<KeyRelease>", self.populate_stock_fields)

        ttk.Label(entry_panel, text="Price:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.stock_price_entry = ttk.Entry(entry_panel, width=20)
        self.stock_price_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_panel, text="Quantity:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.stock_quantity_entry = ttk.Entry(entry_panel, width=15)
        self.stock_quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_panel, text="Serial No. (add/remove):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.stock_serial_entry = ttk.Entry(entry_panel, width=30)
        self.stock_serial_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_panel, text="Image Path:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.stock_image_path_entry = ttk.Entry(entry_panel, width=30)
        self.stock_image_path_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        ttk.Button(entry_panel, text="Browse Image", command=self.browse_image, style='Info.TButton').grid(row=5, column=0, columnspan=2, pady=10, sticky="ew", padx=10)

        self.stock_item_image_label = ttk.Label(entry_panel, text="No Image", background="#e9ecef", anchor="center", relief="solid", borderwidth=1, bordercolor="#dee2e6")
        self.stock_item_image_label.grid(row=6, column=0, columnspan=2, pady=15, sticky="nsew", ipadx=50, ipady=50, padx=10)
        self.current_stock_image = None
        entry_panel.grid_rowconfigure(6, weight=1)

        stock_button_frame = ttk.Frame(entry_panel)
        stock_button_frame.grid(row=7, column=0, columnspan=2, pady=15, sticky="ew", padx=10)
        ttk.Button(stock_button_frame, text="Add/Update Item", command=self.add_update_stock_item, style='Primary.TButton').pack(fill="x", expand=True, pady=5)
        ttk.Button(stock_button_frame, text="Add Serial", command=self.add_serial_to_stock, style='Info.TButton').pack(fill="x", expand=True, pady=5)
        ttk.Button(stock_button_frame, text="Remove Serial", command=self.remove_serial_from_stock, style='Danger.TButton').pack(fill="x", expand=True, pady=5)
        ttk.Button(stock_button_frame, text="Delete Item", command=self.delete_stock_item, style='Danger.TButton').pack(fill="x", expand=True, pady=5)
        ttk.Button(stock_button_frame, text="Clear Fields", command=self.clear_stock_fields, style='TButton').pack(fill="x", expand=True, pady=5)

        entry_panel.grid_columnconfigure(1, weight=1)

        stock_display_panel = ttk.LabelFrame(parent_frame, text="Current Stock Inventory", padding="15")
        stock_display_panel.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.stock_tree = ttk.Treeview(stock_display_panel, columns=("Item", "Price", "Quantity", "Serials"), show="headings")
        self.stock_tree.heading("Item", text="Item Name", anchor="w")
        self.stock_tree.heading("Price", text="Price", anchor="e")
        self.stock_tree.heading("Quantity", text="Quantity", anchor="e")
        self.stock_tree.heading("Serials", text="Serials (Count)", anchor="w")
        self.stock_tree.pack(side="left", fill="both", expand=True)

        self.stock_tree.column("Item", width=200, minwidth=150, stretch=tk.YES)
        self.stock_tree.column("Price", width=80, minwidth=60, stretch=tk.NO, anchor="e")
        self.stock_tree.column("Quantity", width=80, minwidth=60, stretch=tk.NO, anchor="e")
        self.stock_tree.column("Serials", width=150, minwidth=100, stretch=tk.YES, anchor="w")

        stock_scrollbar = ttk.Scrollbar(stock_display_panel, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=stock_scrollbar.set)
        stock_scrollbar.pack(side="right", fill="y")

        self.stock_tree.bind("<<TreeviewSelect>>", self.on_stock_item_select)

        self.update_stock_display()

    def populate_stock_fields(self, event=None):
        item_name = self.stock_item_name_entry.get().strip()
        if item_name in self.stock:
            item_data = self.stock[item_name]
            self.stock_price_entry.delete(0, tk.END)
            self.stock_price_entry.insert(0, f"{item_data['price']:.2f}")
            self.stock_quantity_entry.delete(0, tk.END)
            self.stock_quantity_entry.insert(0, str(item_data['quantity']))
            self.stock_image_path_entry.delete(0, tk.END)
            self.stock_image_path_entry.insert(0, item_data.get('image_path', ''))
            self.display_stock_image(item_data.get('image_path', ''))
        else:
            self.stock_price_entry.delete(0, tk.END)
            self.stock_quantity_entry.delete(0, tk.END)
            self.stock_image_path_entry.delete(0, tk.END)
            self.stock_item_image_label.config(image='')
            self.stock_item_image_label.config(text="No Image")
            self.current_stock_image = None

    def on_stock_item_select(self, event):
        selected_item_id = self.stock_tree.focus()
        if selected_item_id:
            values = self.stock_tree.item(selected_item_id, 'values')
            if values:
                item_name = values[0]
                self.stock_item_name_entry.delete(0, tk.END)
                self.stock_item_name_entry.insert(0, item_name)
                self.populate_stock_fields()

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", "*.png *.gif *.bmp *.ico *.jpg *.jpeg")] # Added JPG/JPEG
        )
        if file_path:
            self.stock_image_path_entry.delete(0, tk.END)
            self.stock_image_path_entry.insert(0, file_path)
            self.display_stock_image(file_path)

    def display_stock_image(self, image_path):
        self.stock_item_image_label.config(image='')
        self.stock_item_image_label.config(text="No Image")
        self.current_stock_image = None

        if image_path and os.path.exists(image_path):
            try:
                # Use Pillow for robust image loading (uncomment import at top)
                # from PIL import Image, ImageTk
                # pil_img = Image.open(image_path)
                # max_dim = 150
                # pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS) # Resize proportionally
                # self.current_stock_image = ImageTk.PhotoImage(pil_img)

                # Fallback to Tkinter's PhotoImage if Pillow is not used
                img = tk.PhotoImage(file=image_path)
                # Simple scaling for PhotoImage (might not be proportional)
                original_width = img.width()
                original_height = img.height()
                max_dim = 150
                if original_width > max_dim or original_height > max_dim:
                    if original_width > original_height:
                        ratio = max_dim / original_width
                    else:
                        ratio = max_dim / original_height
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    # Note: PhotoImage does not have a direct resize method.
                    # This will just use the original image if it's too large,
                    # or scale if it's smaller. For proper resizing, use Pillow.
                    # For demonstration, we'll just assign the image.
                    pass # Keep original image for PhotoImage, let label clip/scale if it can
                self.current_stock_image = img # Store reference to prevent garbage collection

                self.stock_item_image_label.config(image=self.current_stock_image, text="")
            except Exception as e:
                self.stock_item_image_label.config(text="Error loading image")
                messagebox.showerror("Image Error", f"Could not load image: {e}\n(For JPG/JPEG support, install Pillow: pip install Pillow)")
        else:
            self.stock_item_image_label.config(text="No Image")

    def add_update_stock_item(self):
        item_name = self.stock_item_name_entry.get().strip()
        price_str = self.stock_price_entry.get().strip()
        quantity_str = self.stock_quantity_entry.get().strip()
        image_path = self.stock_image_path_entry.get().strip()

        if not item_name:
            messagebox.showwarning("Input Error", "Please enter an item name.")
            return

        try:
            price = float(price_str)
            if price < 0:
                messagebox.showwarning("Input Error", "Price cannot be negative.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for price.")
            return

        try:
            quantity = int(quantity_str)
            if quantity < 0:
                messagebox.showwarning("Input Error", "Quantity cannot be negative.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid integer for quantity.")
            return

        if item_name in self.stock:
            self.stock[item_name]['price'] = price
            self.stock[item_name]['quantity'] = quantity
            self.stock[item_name]['image_path'] = image_path
            messagebox.showinfo("Stock Update", f"'{item_name}' updated successfully.")
        else:
            self.stock[item_name] = {
                "price": price,
                "quantity": quantity,
                "serials": [],
                "image_path": image_path
            }
            messagebox.showinfo("Stock Add", f"'{item_name}' added to stock.")

        self._save_data()
        self.update_stock_display()
        self.clear_stock_fields()

    def add_serial_to_stock(self):
        item_name = self.stock_item_name_entry.get().strip()
        serial = self.stock_serial_entry.get().strip()

        if not item_name or item_name not in self.stock:
            messagebox.showwarning("Input Error", "Please select or enter an existing item name.")
            return
        if not serial:
            messagebox.showwarning("Input Error", "Please enter a serial number to add.")
            return

        if serial in self.stock[item_name]['serials']:
            messagebox.showwarning("Duplicate Serial", f"Serial '{serial}' already exists for '{item_name}'.")
            return

        self.stock[item_name]['serials'].append(serial)
        self.stock[item_name]['quantity'] += 1
        self._save_data()
        self.update_stock_display()
        messagebox.showinfo("Serial Added", f"Serial '{serial}' added to '{item_name}'. Quantity updated.")
        self.stock_serial_entry.delete(0, tk.END)

    def remove_serial_from_stock(self):
        item_name = self.stock_item_name_entry.get().strip()
        serial = self.stock_serial_entry.get().strip()

        if not item_name or item_name not in self.stock:
            messagebox.showwarning("Input Error", "Please select or enter an existing item name.")
            return
        if not serial:
            messagebox.showwarning("Input Error", "Please enter a serial number to remove.")
            return

        if serial not in self.stock[item_name]['serials']:
            messagebox.showwarning("Serial Not Found", f"Serial '{serial}' not found for '{item_name}'.")
            return

        if messagebox.askyesno("Remove Serial", f"Are you sure you want to remove serial '{serial}' from '{item_name}'?"):
            self.stock[item_name]['serials'].remove(serial)
            self.stock[item_name]['quantity'] -= 1
            self._save_data()
            self.update_stock_display()
            messagebox.showinfo("Serial Removed", f"Serial '{serial}' removed from '{item_name}'. Quantity updated.")
            self.stock_serial_entry.delete(0, tk.END)

    def delete_stock_item(self):
        item_name = self.stock_item_name_entry.get().strip()
        if not item_name or item_name not in self.stock:
            messagebox.showwarning("Input Error", "Please select or enter an existing item name to delete.")
            return

        if messagebox.askyesno("Delete Item", f"Are you sure you want to delete '{item_name}' from stock? This action cannot be undone."):
            del self.stock[item_name]
            self._save_data()
            self.update_stock_display()
            self.clear_stock_fields()
            messagebox.showinfo("Item Deleted", f"'{item_name}' has been deleted from stock.")

    def clear_stock_fields(self):
        self.stock_item_name_entry.delete(0, tk.END)
        self.stock_price_entry.delete(0, tk.END)
        self.stock_quantity_entry.delete(0, tk.END)
        self.stock_serial_entry.delete(0, tk.END)
        self.stock_image_path_entry.delete(0, tk.END)
        self.stock_item_image_label.config(image='')
        self.stock_item_image_label.config(text="No Image")
        self.current_stock_image = None
        self.stock_item_name_entry.focus_set()

    def update_stock_display(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        for item_name, data in self.stock.items():
            serials_info = f"{len(data['serials'])} available"
            if data['serials']:
                serials_info = f"{len(data['serials'])} ({', '.join(data['serials'][:2])}...)" if len(data['serials']) > 2 else f"{', '.join(data['serials'])}"

            self.stock_tree.insert("", "end", values=(
                item_name,
                f"{data['price']:.2f}",
                data['quantity'],
                serials_info
            ))
        self._save_data()


    # --- Expenses Tab Methods ---
    def _create_expenses_tab(self, parent_frame):
        entry_section = ttk.LabelFrame(parent_frame, text="Add New Expense", padding="20")
        entry_section.pack(pady=15, padx=15, fill="x")

        ttk.Label(entry_section, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.expense_date_entry = ttk.Entry(entry_section, width=20)
        self.expense_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.expense_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d')) # Default to today

        ttk.Label(entry_section, text="Category:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.expense_category_entry = ttk.Entry(entry_section, width=30)
        self.expense_category_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_section, text="Amount:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.expense_amount_entry = ttk.Entry(entry_section, width=15)
        self.expense_amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_section, text="Description:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.expense_description_entry = ttk.Entry(entry_section, width=40)
        self.expense_description_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        entry_section.grid_columnconfigure(1, weight=1)

        button_frame = ttk.Frame(parent_frame, padding="15")
        button_frame.pack(pady=10, padx=15, fill="x")
        ttk.Button(button_frame, text="Add Expense", command=self.add_expense, style='Primary.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Remove Selected Expense", command=self.remove_expense, style='Danger.TButton').pack(side="right", padx=8, expand=True, fill="x")

        display_section = ttk.LabelFrame(parent_frame, text="Recent Expenses", padding="15")
        display_section.pack(pady=15, padx=15, fill="both", expand=True)

        self.expenses_tree = ttk.Treeview(display_section, columns=("ID", "Date", "Category", "Amount", "Description", "User"), show="headings")
        self.expenses_tree.heading("ID", text="ID", anchor="w")
        self.expenses_tree.heading("Date", text="Date", anchor="w")
        self.expenses_tree.heading("Category", text="Category", anchor="w")
        self.expenses_tree.heading("Amount", text="Amount", anchor="e")
        self.expenses_tree.heading("Description", text="Description", anchor="w")
        self.expenses_tree.heading("User", text="Recorded By", anchor="w")

        self.expenses_tree.column("ID", width=50, minwidth=30, stretch=tk.NO)
        self.expenses_tree.column("Date", width=120, minwidth=100, stretch=tk.NO)
        self.expenses_tree.column("Category", width=150, minwidth=100, stretch=tk.YES)
        self.expenses_tree.column("Amount", width=100, minwidth=80, stretch=tk.NO, anchor="e")
        self.expenses_tree.column("Description", width=250, minwidth=150, stretch=tk.YES)
        self.expenses_tree.column("User", width=100, minwidth=80, stretch=tk.NO)

        self.expenses_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(display_section, orient="vertical", command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.update_expenses_display()

    def add_expense(self):
        expense_date = self.expense_date_entry.get().strip()
        category = self.expense_category_entry.get().strip()
        amount_str = self.expense_amount_entry.get().strip()
        description = self.expense_description_entry.get().strip()

        if not expense_date or not category or not amount_str:
            messagebox.showwarning("Input Error", "Date, Category, and Amount are required.")
            return

        try:
            datetime.datetime.strptime(expense_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Input Error", "Date format must be YYYY-MM-DD.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Input Error", "Amount must be a positive number.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid number for amount.")
            return
        
        expense_id = len(self.expenses) + 1 # Simple ID generation
        self.expenses.append({
            "id": expense_id,
            "date": expense_date,
            "category": category,
            "amount": amount,
            "description": description,
            "user": self.logged_in_user
        })
        self._save_data()
        self.update_expenses_display()
        messagebox.showinfo("Success", "Expense added successfully.")
        self.expense_category_entry.delete(0, tk.END)
        self.expense_amount_entry.delete(0, tk.END)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_date_entry.delete(0, tk.END)
        self.expense_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))

    def remove_expense(self):
        selected_item_id = self.expenses_tree.focus()
        if not selected_item_id:
            messagebox.showwarning("Selection Error", "Please select an expense to remove.")
            return
        
        # Get the ID from the treeview item
        expense_id_to_remove = self.expenses_tree.item(selected_item_id, 'values')[0]

        if messagebox.askyesno("Remove Expense", "Are you sure you want to remove this expense?"):
            # Find and remove the expense by its ID
            self.expenses = [exp for exp in self.expenses if exp['id'] != expense_id_to_remove]
            self._save_data()
            self.update_expenses_display()
            messagebox.showinfo("Success", "Expense removed successfully.")

    def update_expenses_display(self):
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        for expense in sorted(self.expenses, key=lambda x: x['date'], reverse=True):
            self.expenses_tree.insert("", "end", values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}",
                expense['description'],
                expense['user']
            ))
        self._save_data()


    # --- Sales Reports Tab Methods ---
    def _create_reports_tab(self, parent_frame):
        reports_section = ttk.LabelFrame(parent_frame, text="Sales History", padding="15")
        reports_section.pack(pady=15, padx=15, fill="both", expand=True)

        self.reports_tree = ttk.Treeview(reports_section, columns=("InvoiceID", "Timestamp", "ItemsCount", "TotalAmount", "SoldBy"), show="headings")
        self.reports_tree.heading("InvoiceID", text="Invoice ID", anchor="w")
        self.reports_tree.heading("Timestamp", text="Date/Time", anchor="w")
        self.reports_tree.heading("ItemsCount", text="Items", anchor="e")
        self.reports_tree.heading("TotalAmount", text="Total", anchor="e")
        self.reports_tree.heading("SoldBy", text="Sold By", anchor="w")

        self.reports_tree.column("InvoiceID", width=150, minwidth=120, stretch=tk.YES)
        self.reports_tree.column("Timestamp", width=180, minwidth=150, stretch=tk.YES)
        self.reports_tree.column("ItemsCount", width=80, minwidth=60, stretch=tk.NO, anchor="e")
        self.reports_tree.column("TotalAmount", width=100, minwidth=80, stretch=tk.NO, anchor="e")
        self.reports_tree.column("SoldBy", width=100, minwidth=80, stretch=tk.NO, anchor="w")

        self.reports_tree.pack(side="left", fill="both", expand=True)

        reports_scrollbar = ttk.Scrollbar(reports_section, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=reports_scrollbar.set)
        reports_scrollbar.pack(side="right", fill="y")

        self.reports_tree.bind("<<TreeviewSelect>>", self.on_report_invoice_select)

        details_frame = ttk.LabelFrame(parent_frame, text="Invoice Details", padding="15")
        details_frame.pack(pady=15, padx=15, fill="x")

        self.invoice_details_label = ttk.Label(details_frame, text="Select an invoice to view details.", justify=tk.LEFT, wraplength=700, font=('Inter', 12))
        self.invoice_details_label.pack(fill="x", expand=True, padx=10, pady=10)

        self.update_reports_display()

    def update_reports_display(self):
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)

        sorted_history = sorted(self.sales_history, key=lambda x: x['timestamp'], reverse=True)

        for invoice in sorted_history:
            self.reports_tree.insert("", "end", values=(
                invoice['invoice_id'],
                datetime.datetime.fromisoformat(invoice['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                len(invoice['items']),
                f"{invoice['total_amount']:.2f}",
                invoice.get('sold_by', 'N/A') # Get sold_by, default to N/A if not present
            ), iid=invoice['invoice_id'])

    def on_report_invoice_select(self, event):
        selected_invoice_id = self.reports_tree.focus()
        if selected_invoice_id:
            invoice_data = next((inv for inv in self.sales_history if inv['invoice_id'] == selected_invoice_id), None)
            if invoice_data:
                details_text = f"Invoice ID: {invoice_data['invoice_id']}\n"
                details_text += f"Date/Time: {datetime.datetime.fromisoformat(invoice_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
                details_text += f"Total Amount: {invoice_data['total_amount']:.2f}\n"
                details_text += f"Sold By: {invoice_data.get('sold_by', 'N/A')}\n\n"
                details_text += "Items:\n"
                for item in invoice_data['items']:
                    details_text += f"  - {item['name']} (Qty: {item['quantity']}, Price: {item['price']:.2f}, Serial: {item['serial']}) - Subtotal: {item['subtotal']:.2f}\n"
                self.invoice_details_label.config(text=details_text)
            else:
                self.invoice_details_label.config(text="Invoice details not found.")
        else:
            self.invoice_details_label.config(text="Select an invoice to view details.")


    # --- Daily Summary Report Tab Methods ---
    def _create_daily_summary_tab(self, parent_frame):
        control_frame = ttk.LabelFrame(parent_frame, text="Select Date", padding="15")
        control_frame.pack(pady=15, padx=15, fill="x")

        ttk.Label(control_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.summary_date_entry = ttk.Entry(control_frame, width=20)
        self.summary_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.summary_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        ttk.Button(control_frame, text="Generate Report", command=self.update_daily_summary_report, style='Primary.TButton').grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1)

        summary_section = ttk.LabelFrame(parent_frame, text="Daily Summary", padding="20")
        summary_section.pack(pady=15, padx=15, fill="both", expand=True)

        self.summary_sales_label = ttk.Label(summary_section, text="Total Sales: 0.00", font=('Inter', 14, 'bold'), foreground='#28a745')
        self.summary_sales_label.pack(pady=5, anchor="w")

        self.summary_expenses_label = ttk.Label(summary_section, text="Total Expenses: 0.00", font=('Inter', 14, 'bold'), foreground='#dc3545')
        self.summary_expenses_label.pack(pady=5, anchor="w")

        self.summary_net_label = ttk.Label(summary_section, text="Net Profit/Loss: 0.00", font=('Inter', 16, 'bold'), foreground='#007bff')
        self.summary_net_label.pack(pady=10, anchor="w")

        self.summary_details_label = ttk.Label(summary_section, text="Details:", justify=tk.LEFT, wraplength=800, font=('Inter', 12))
        self.summary_details_label.pack(pady=10, fill="both", expand=True, anchor="w")

        self.update_daily_summary_report()

    def update_daily_summary_report(self):
        selected_date_str = self.summary_date_entry.get().strip()
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid date in YYYY-MM-DD format.")
            return

        total_sales = 0.0
        sales_details = []
        for invoice in self.sales_history:
            invoice_date = datetime.datetime.fromisoformat(invoice['timestamp']).date()
            if invoice_date == selected_date:
                total_sales += invoice['total_amount']
                sales_details.append(f"  - Invoice {invoice['invoice_id']} ({invoice.get('sold_by', 'N/A')}): {invoice['total_amount']:.2f}")

        total_expenses = 0.0
        expenses_details = []
        for expense in self.expenses:
            expense_date = datetime.datetime.strptime(expense['date'], '%Y-%m-%d').date()
            if expense_date == selected_date:
                total_expenses += expense['amount']
                expenses_details.append(f"  - {expense['category']} ({expense['user']}): {expense['amount']:.2f} - {expense['description']}")

        net_profit_loss = total_sales - total_expenses

        self.summary_sales_label.config(text=f"Total Sales: {total_sales:.2f}")
        self.summary_expenses_label.config(text=f"Total Expenses: {total_expenses:.2f}")
        self.summary_net_label.config(text=f"Net Profit/Loss: {net_profit_loss:.2f}")

        details_text = "Sales Details:\n" + ("\n".join(sales_details) if sales_details else "  No sales for this date.")
        details_text += "\n\nExpenses Details:\n" + ("\n".join(expenses_details) if expenses_details else "  No expenses for this date.")
        self.summary_details_label.config(text=details_text)


    # --- User Management Tab Methods ---
    def _create_user_management_tab(self, parent_frame):
        # Only Admin can access this tab, enforced by _apply_permissions
        # We still create the widgets, but they will be disabled/hidden for non-admins

        entry_section = ttk.LabelFrame(parent_frame, text="Create/Manage User", padding="20")
        entry_section.pack(pady=15, padx=15, fill="x")

        ttk.Label(entry_section, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.user_username_entry = ttk.Entry(entry_section, width=30)
        self.user_username_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.user_username_entry.bind("<KeyRelease>", self.populate_user_fields)

        ttk.Label(entry_section, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.user_password_entry = ttk.Entry(entry_section, width=30, show="*")
        self.user_password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(entry_section, text="Role:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.user_role_combobox = ttk.Combobox(entry_section, values=["Admin", "Sales", "StockManager", "Viewer"], state="readonly")
        self.user_role_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.user_role_combobox.set("Sales") # Default role

        entry_section.grid_columnconfigure(1, weight=1)

        button_frame = ttk.Frame(parent_frame, padding="15")
        button_frame.pack(pady=10, padx=15, fill="x")
        ttk.Button(button_frame, text="Create User", command=self.create_user, style='Primary.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Update User Role", command=self.update_user_role, style='Info.TButton').pack(side="left", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Delete User", command=self.delete_user, style='Danger.TButton').pack(side="right", padx=8, expand=True, fill="x")
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_user_fields, style='TButton').pack(side="right", padx=8, expand=True, fill="x")


        display_section = ttk.LabelFrame(parent_frame, text="Existing Users", padding="15")
        display_section.pack(pady=15, padx=15, fill="both", expand=True)

        self.users_tree = ttk.Treeview(display_section, columns=("Username", "Role"), show="headings")
        self.users_tree.heading("Username", text="Username", anchor="w")
        self.users_tree.heading("Role", text="Role", anchor="w")

        self.users_tree.column("Username", width=200, minwidth=150, stretch=tk.YES)
        self.users_tree.column("Role", width=150, minwidth=100, stretch=tk.YES)

        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(display_section, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)

        self.update_user_display()

    def populate_user_fields(self, event=None):
        username = self.user_username_entry.get().strip()
        if username in self.users:
            user_data = self.users[username]
            self.user_role_combobox.set(user_data['role'])
            # Do not populate password for security reasons
        else:
            self.user_role_combobox.set("Sales") # Reset to default if not found

    def on_user_select(self, event):
        selected_item_id = self.users_tree.focus()
        if selected_item_id:
            values = self.users_tree.item(selected_item_id, 'values')
            if values:
                username = values[0]
                self.user_username_entry.delete(0, tk.END)
                self.user_username_entry.insert(0, username)
                self.populate_user_fields() # This will set the role combobox

    def create_user(self):
        username = self.user_username_entry.get().strip()
        password = self.user_password_entry.get().strip()
        role = self.user_role_combobox.get()

        if not username or not password or not role:
            messagebox.showwarning("Input Error", "All fields are required to create a user.")
            return

        if username in self.users:
            messagebox.showwarning("User Exists", f"User '{username}' already exists. Use 'Update User Role' if you want to change their role.")
            return
        
        if username == self.logged_in_user:
            messagebox.showwarning("Error", "You cannot create a new user with your own username.")
            return

        self.users[username] = {
            "password_hash": hashlib.sha256(password.encode()).hexdigest(),
            "role": role
        }
        self._save_data()
        self.update_user_display()
        self.clear_user_fields()
        messagebox.showinfo("Success", f"User '{username}' created with role '{role}'.")

    def update_user_role(self):
        username = self.user_username_entry.get().strip()
        new_role = self.user_role_combobox.get()

        if not username or not new_role:
            messagebox.showwarning("Input Error", "Username and Role are required to update.")
            return

        if username not in self.users:
            messagebox.showwarning("User Not Found", f"User '{username}' does not exist.")
            return
        
        if username == self.logged_in_user and new_role != self.user_role:
            messagebox.showwarning("Permission Denied", "You cannot change your own role directly. Please ask another Admin.")
            return
        
        if username == DEFAULT_ADMIN_USER["username"] and new_role != DEFAULT_ADMIN_USER["role"]:
            messagebox.showwarning("Permission Denied", "The default 'Admin' user's role cannot be changed.")
            return

        self.users[username]['role'] = new_role
        self._save_data()
        self.update_user_display()
        self.clear_user_fields()
        messagebox.showinfo("Success", f"Role for user '{username}' updated to '{new_role}'.")

    def delete_user(self):
        username = self.user_username_entry.get().strip()

        if not username:
            messagebox.showwarning("Input Error", "Please select or enter a username to delete.")
            return

        if username not in self.users:
            messagebox.showwarning("User Not Found", f"User '{username}' does not exist.")
            return
        
        if username == self.logged_in_user:
            messagebox.showwarning("Permission Denied", "You cannot delete your own account while logged in.")
            return
        
        if username == DEFAULT_ADMIN_USER["username"]:
            messagebox.showwarning("Permission Denied", "The default 'Admin' user cannot be deleted.")
            return

        if messagebox.askyesno("Delete User", f"Are you sure you want to delete user '{username}'? This action cannot be undone."):
            del self.users[username]
            self._save_data()
            self.update_user_display()
            self.clear_user_fields()
            messagebox.showinfo("Success", f"User '{username}' deleted.")

    def clear_user_fields(self):
        self.user_username_entry.delete(0, tk.END)
        self.user_password_entry.delete(0, tk.END)
        self.user_role_combobox.set("Sales")
        self.user_username_entry.focus_set()

    def update_user_display(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        for username, data in self.users.items():
            self.users_tree.insert("", "end", values=(username, data['role']))
        self._save_data()


# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SimplePOSApp(root)
    root.mainloop()

    # Save data when the application closes (redundant if _save_data is called after every change, but good fallback)
    app._save_data()