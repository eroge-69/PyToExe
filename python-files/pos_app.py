import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

# Función para obtener la ruta del escritorio
def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

# Rutas base de datos
DATA_FOLDER = os.path.join(get_desktop_path(), "POS_Data")
USERS_FILE = os.path.join(DATA_FOLDER, "users.txt")
PRODUCTS_FILE = os.path.join(DATA_FOLDER, "products.txt")

# Crear carpeta y archivos iniciales si no existen
def init_data():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            f.write("admin:admin\n")  # Cuenta por defecto
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w') as f:
            pass  # Vacío inicialmente

# Clase para la ventana de Login
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Punto de Venta")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')

        # Labels y entradas
        tk.Label(root, text="Usuario:", font=("Arial", 12)).pack(pady=10)
        self.username_entry = tk.Entry(root, font=("Arial", 12))
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Contraseña:", font=("Arial", 12)).pack(pady=10)
        self.password_entry = tk.Entry(root, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        login_btn = tk.Button(root, text="Iniciar Sesión", font=("Arial", 12),
                              bg="#4CAF50", fg="white", command=self.login)
        login_btn.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        with open(USERS_FILE, 'r') as f:
            users = f.readlines()

        is_admin = False
        for line in users:
            stored_user, stored_pass = line.strip().split(':')
            if username == stored_user and password == stored_pass:
                if username == "admin":
                    is_admin = True
                self.root.destroy()
                MainWindow(is_admin)
                return

        messagebox.showerror("Error", "Credenciales inválidas.")

# Clase principal
class MainWindow:
    def __init__(self, is_admin):
        self.is_admin = is_admin
        self.root = tk.Tk()
        self.root.title("Punto de Venta - Leveraa")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Sidebar
        self.create_sidebar()

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Mostrar inventario al inicio
        self.show_inventory()
        self.root.mainloop()

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, width=200, bg="#2c3e50", relief="raised", bd=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        sidebar.pack_propagate(False)

        title = tk.Label(sidebar, text="Venta Menu", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=20)

        buttons = [
            ("Cobrar", self.show_checkout),
            ("Agregar Producto", self.show_add_product),
            ("Ver Inventario", self.show_inventory)
        ]

        if self.is_admin:
            buttons.append(("Gestión de Cuentas", self.show_accounts))

        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, font=("Arial", 11), bg="#3498db", fg="white",
                            command=command, relief="flat", pady=10, width=15)
            btn.pack(pady=5, padx=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_checkout(self):
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Sistema de Cobro", font=("Arial", 16, "bold"),
                 bg="#f0f0f0").pack(pady=20)

        search_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Buscar por Código o Nombre:", font=("Arial", 12)).pack()
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(pady=5)
        tk.Button(search_frame, text="Buscar", command=self.search_product,
                  bg="#4CAF50", fg="white").pack(pady=5)

        columns = ("Producto", "Precio", "Cantidad", "Subtotal")
        self.cart_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=150)
        self.cart_tree.pack(pady=20)

        total_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        total_frame.pack(pady=10)
        self.total_label = tk.Label(total_frame, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack()

        tk.Button(total_frame, text="Procesar Pago", command=self.process_checkout,
                  bg="#FF9800", fg="white").pack(pady=10)

        self.cart = []
        self.update_total()

    def search_product(self):
        query = self.search_entry.get().lower()
        with open(PRODUCTS_FILE, 'r') as f:
            products = f.readlines()

        found = False
        for line in products:
            parts = line.strip().split(':')
            if len(parts) == 4:
                code, name, price, stock = parts
                if query in code.lower() or query in name.lower():
                    qty = simpledialog.askinteger("Cantidad",
                                                  f"Producto: {name}\nPrecio: ${price}\nStock: {stock}\n\nIngresa cantidad:")
                    if qty and int(qty) <= int(stock):
                        subtotal = float(price) * qty
                        self.cart.append({"name": name, "price": float(price), "qty": qty, "subtotal": subtotal})
                        self.cart_tree.insert("", "end", values=(name, f"${price}", qty, f"${subtotal:.2f}"))
                        self.update_total()
                        found = True
                    else:
                        messagebox.showwarning("Advertencia", "Cantidad inválida o sin stock.")
                    break

        if not found:
            messagebox.showinfo("Info", "Producto no encontrado.")

    def update_total(self):
        total = sum(item["subtotal"] for item in self.cart)
        self.total_label.config(text=f"Total: ${total:.2f}")

    def process_checkout(self):
        if not self.cart:
            messagebox.showwarning("Advertencia", "Carrito vacío.")
            return

        total = sum(item["subtotal"] for item in self.cart)
        confirm = messagebox.askyesno("Confirmar", f"¿Procesar pago por ${total:.2f}?")
        if confirm:
            self.update_stock()
            messagebox.showinfo("Éxito", "Pago procesado correctamente.")
            self.cart.clear()
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
            self.update_total()

    def update_stock(self):
        with open(PRODUCTS_FILE, 'r') as f:
            products = f.readlines()

        new_products = []
        for line in products:
            parts = line.strip().split(':')
            if len(parts) == 4:
                code, name, price, stock = parts
                stock_int = int(stock)
                for item in self.cart:
                    if item["name"] == name:
                        stock_int -= item["qty"]
                new_products.append(f"{code}:{name}:{price}:{stock_int}\n")
            else:
                new_products.append(line)

        with open(PRODUCTS_FILE, 'w') as f:
            f.writelines(new_products)

    def show_add_product(self):
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Agregar Producto", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)

        fields = ["Código de Barras:", "Nombre:", "Precio:", "Stock Inicial:"]
        self.entries = {}
        for field in fields:
            tk.Label(self.main_frame, text=field, font=("Arial", 12)).pack()
            entry = tk.Entry(self.main_frame, font=("Arial", 12), width=30)
            entry.pack(pady=5)
            self.entries[field] = entry

        tk.Button(self.main_frame, text="Agregar", command=self.add_product,
                  bg="#4CAF50", fg="white").pack(pady=20)

    def add_product(self):
        code = self.entries["Código de Barras:"].get()
        name = self.entries["Nombre:"].get()
        price = self.entries["Precio:"].get()
        stock = self.entries["Stock Inicial:"].get()

        if all([code, name, price, stock]):
            with open(PRODUCTS_FILE, 'a') as f:
                f.write(f"{code}:{name}:{price}:{stock}\n")
            messagebox.showinfo("Éxito", "Producto agregado.")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Completa todos los campos.")

    def show_inventory(self):
        self.clear_main_frame()
        tk.Label(self.main_frame, text="Inventario", font=("Arial", 16, "bold"),
                 bg="#f0f0f0").pack(pady=20)

        columns = ("Código", "Nombre", "Precio", "Stock")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        with open(PRODUCTS_FILE, 'r') as f:
            products = f.readlines()

        for line in products:
            parts = line.strip().split(':')
            if len(parts) == 4:
                tree.insert("", "end", values=parts)

        tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def show_accounts(self):
        if not self.is_admin:
            messagebox.showerror("Error", "Acceso denegado. Solo para admin.")
            return

        self.clear_main_frame()
        tk.Label(self.main_frame, text="Gestión de Cuentas (Admin)", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)

        list_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        list_frame.pack(pady=10)
        tk.Label(list_frame, text="Usuarios Existentes:", font=("Arial", 12)).pack()
        self.users_listbox = tk.Listbox(list_frame, height=10, width=50)
        self.users_listbox.pack()
        self.load_users()

        add_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        add_frame.pack(pady=10)
        tk.Label(add_frame, text="Nuevo Usuario:", font=("Arial", 12)).pack()
        new_user_entry = tk.Entry(add_frame, font=("Arial", 12), width=20)
        new_user_entry.pack(side=tk.LEFT, padx=5)
        new_pass_entry = tk.Entry(add_frame, show="*", font=("Arial", 12), width=20)
        new_pass_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(add_frame, text="Agregar Usuario",
                  command=lambda: self.add_user(new_user_entry, new_pass_entry),
                  bg="#4CAF50", fg="white").pack(pady=5)

        tk.Button(self.main_frame, text="Eliminar Usuario Seleccionado",
                  command=self.delete_user, bg="#f44336", fg="white").pack(pady=10)

    def load_users(self):
        self.users_listbox.delete(0, tk.END)
        with open(USERS_FILE, 'r') as f:
            for line in f:
                user = line.strip().split(':')[0]
                self.users_listbox.insert(tk.END, user)

    def add_user(self, user_entry, pass_entry):
        username = user_entry.get()
        password = pass_entry.get()
        if username and password and username != "admin":
            with open(USERS_FILE, 'a') as f:
                f.write(f"{username}:{password}\n")
            messagebox.showinfo("Éxito", "Usuario agregado.")
            user_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            self.load_users()
        else:
            messagebox.showerror("Error", "Datos inválidos o intento de modificar admin.")

    def delete_user(self):
        selection = self.users_listbox.curselection()
        if selection:
            username = self.users_listbox.get(selection[0])
            if username == "admin":
                messagebox.showerror("Error", "No puedes eliminar al usuario admin.")
                return

            with open(USERS_FILE, 'r') as f:
                lines = f.readlines()
            with open(USERS_FILE, 'w') as f:
                for line in lines:
                    if not line.startswith(username + ":"):
                        f.write(line)

            messagebox.showinfo("Éxito", "Usuario eliminado.")
            self.load_users()
        else:
            messagebox.showwarning("Advertencia", "Selecciona un usuario para eliminar.")

# Inicializar datos y lanzar app
if __name__ == "__main__":
    init_data()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()