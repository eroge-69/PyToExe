import tkinter as tk
from tkinter import messagebox
import sqlite3

class TMSApp:
    def __init__(self, master):
        self.master = master
        master.title("Trucking Management System")
        master.geometry("800x600")

        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        tk.Label(self.login_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()

        tk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect("tms_app/tms.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", f"Welcome, {user[1]} ({user[3]})!")
            self.user_role = user[3]  # Store user role
            self.show_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_main_app(self):
        self.login_frame.destroy()
        self.main_app_frame = tk.Frame(self.master)
        self.main_app_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.main_app_frame, text=f"Logged in as: {self.user_role}").pack()
        tk.Button(self.main_app_frame, text="Logout", command=self.logout).pack()

        # Role-based access control
        if self.user_role == "Admin":
            self.create_admin_dashboard()
        elif self.user_role == "Dispatcher":
            self.create_dispatcher_dashboard()

    def create_admin_dashboard(self):
        admin_frame = tk.Frame(self.main_app_frame)
        admin_frame.pack()
        tk.Label(admin_frame, text="Admin Dashboard").pack()
        tk.Button(admin_frame, text="Manage Drivers", command=self.open_driver_manager).pack()
        tk.Button(admin_frame, text="Manage Trucks/Trailers", command=self.open_truck_trailer_manager).pack()
        tk.Button(admin_frame, text="Manage Customers/Brokers", command=self.open_customer_broker_manager).pack()
        tk.Button(admin_frame, text="Load Board", command=self.open_load_board).pack()
        tk.Button(admin_frame, text="Dispatching Module", command=self.open_dispatching_module).pack()
        tk.Button(admin_frame, text="Invoice & Billing", command=self.open_invoice_manager).pack()
        tk.Button(admin_frame, text="Document Management", command=self.open_document_manager).pack()
        tk.Button(admin_frame, text="Reports", command=self.open_reports_manager).pack()

    def create_dispatcher_dashboard(self):
        dispatcher_frame = tk.Frame(self.main_app_frame)
        dispatcher_frame.pack()
        tk.Label(dispatcher_frame, text="Dispatcher Dashboard").pack()

    def open_driver_manager(self):
        driver_window = tk.Toplevel(self.master)
        from driver_manager import DriverManager
        DriverManager(driver_window)

    def logout(self):
        self.main_app_frame.destroy()
        self.create_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = TMSApp(root)
    root.mainloop()




    def open_truck_trailer_manager(self):
        truck_trailer_window = tk.Toplevel(self.master)
        from truck_trailer_manager import TruckTrailerManager
        TruckTrailerManager(truck_trailer_window)

    def open_customer_broker_manager(self):
        customer_broker_window = tk.Toplevel(self.master)
        from customer_broker_manager import CustomerBrokerManager
        CustomerBrokerManager(customer_broker_window)



    def open_load_board(self):
        load_board_window = tk.Toplevel(self.master)
        from load_board import LoadBoard
        LoadBoard(load_board_window)



    def open_dispatching_module(self):
        dispatching_window = tk.Toplevel(self.master)
        from dispatching_module import DispatchingModule
        DispatchingModule(dispatching_window)



    def open_invoice_manager(self):
        invoice_window = tk.Toplevel(self.master)
        from invoice_manager import InvoiceManager
        InvoiceManager(invoice_window)



    def open_document_manager(self):
        document_window = tk.Toplevel(self.master)
        from document_manager import DocumentManager
        DocumentManager(document_window)



    def open_reports_manager(self):
        reports_window = tk.Toplevel(self.master)
        from reports_manager import ReportsManager
        ReportsManager(reports_window)

