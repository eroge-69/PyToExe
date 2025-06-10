import sys
import subprocess
import os

# --- Library Check and Installation Block ---
# This block ensures all necessary libraries are installed before the main application runs.

def install_package(package_name):

    print(f"Attempting to install '{package_name}'...")
    try:
        # Use sys.executable to ensure pip runs with the same Python interpreter
        # that's running the script.
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"'{package_name}' installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install '{package_name}'.")
        print(f"Please try installing it manually: pip install {package_name}")
        print(f"Error details: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while installing '{package_name}': {e}")
        return False

required_third_party_packages = [
    "tkcalendar",
    "pyinstaller",
    "platformdirs"
]

print("--- Checking for required Python libraries ---")
all_libraries_present = True

try:
    import tkinter
    print("'tkinter' is available.")
except ImportError:
    print("'tkinter' not found. On some systems (e.g., Linux), this requires a system-level package like 'python3-tk'.")
    print("Attempting to install via pip (this might not always resolve system-level issues)...")
    if not install_package("tk"):
        all_libraries_present = False

for package in required_third_party_packages:
    try:
        # Attempt to import the module
        __import__(package)
        print(f"'{package}' is already installed.")
    except ImportError:
        #print(f"'{package}' is not installed.")
        if not install_package(package):
            all_libraries_present = False

if not all_libraries_present:
    print("\nSome required libraries could not be installed automatically.")
    print("Please install them manually to proceed. Exiting...")
    sys.exit(1) # Exit if critical libraries are missing

print("--- All required libraries are present. Proceeding with application start. ---")


# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog , filedialog
import sqlite3
from datetime import datetime, timedelta
from tkcalendar import Calendar
import threading
import time
import csv
import os


class SubscriptionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Subscription Manager")
        self.root.geometry("1024x768")

        # Initialize database
        self.init_db()

        # Create GUI
        self.create_widgets()

        # Load customers
        self.load_customers()

        # Start reminder thread
        self.reminder_active = True
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_db(self):
        self.conn = sqlite3.connect('subscriptions.db')
        self.cursor = self.conn.cursor()

        # Create tables if they don't exist
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS customers
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL,
                                email
                                TEXT,
                                phone
                                TEXT,
                                subscription_type
                                TEXT,
                                start_date
                                TEXT,
                                end_date
                                TEXT,
                                amount
                                REAL,
                                notes
                                TEXT,
                                last_reminder_sent
                                TEXT
                            )
                            ''')
        self.conn.commit()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame (customer list)
        left_frame = ttk.Frame(main_frame, padding="5", relief="ridge")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        # Add to create_widgets method (after search_frame)
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)

        # Customer list treeview
        self.tree = ttk.Treeview(left_frame, columns=('ID', 'Name', 'Email', 'Phone', 'Subscription', 'End Date'),
                                 show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Add to create_widgets method (in import_export_frame)
        self.import_btn = ttk.Button(filter_frame, text="Import CSV", command=self.import_csv)
        self.import_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        ttk.Button(filter_frame, text="Show All", command=self.load_customers).pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Show Expired", command=self.show_expired_subscriptions).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(filter_frame, text="Show Active", command=self.show_active_subscriptions).pack(side=tk.LEFT)

        # Add to create_widgets method (in button_frame)
        self.export_btn = ttk.Button(filter_frame, text="Export Data", command=self.export_data)
        self.export_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)


        # Configure columns
        self.tree.heading('ID', text='ID', anchor=tk.W)
        self.tree.heading('Name', text='Name', anchor=tk.W)
        self.tree.heading('Email', text='Email', anchor=tk.W)
        self.tree.heading('Phone', text='Phone', anchor=tk.W)
        self.tree.heading('Subscription', text='Subscription', anchor=tk.W)
        self.tree.heading('End Date', text='End Date', anchor=tk.W)

        self.tree.column('ID', width=50, stretch=tk.NO)
        self.tree.column('Name', width=150)
        self.tree.column('Email', width=150)
        self.tree.column('Phone', width=100)
        self.tree.column('Subscription', width=100)
        self.tree.column('End Date', width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_customer_select)

        # Right frame (customer details)
        right_frame = ttk.Frame(main_frame, padding="5", relief="ridge")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Customer details form
        detail_frame = ttk.LabelFrame(right_frame, text="Customer Details", padding="10")
        detail_frame.pack(fill=tk.X, pady=5)

        ttk.Label(detail_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(detail_frame, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(detail_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(detail_frame, textvariable=self.email_var)
        self.email_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(detail_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(detail_frame, textvariable=self.phone_var)
        self.phone_entry.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(detail_frame, text="Subscription Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sub_type_var = tk.StringVar()
        self.sub_type_entry = ttk.Combobox(detail_frame, textvariable=self.sub_type_var,
                                           values=["Monthly", "Quarterly", "Yearly", "Custom"])
        self.sub_type_entry.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=5)

        # Start Date
        ttk.Label(detail_frame, text="Start Date (dd-mm-YYYY):").grid(row=4, column=0, sticky=tk.W, pady=2)
        start_date_frame = ttk.Frame(detail_frame)
        start_date_frame.grid(row=4, column=1, sticky=tk.EW, pady=2, padx=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(start_date_frame, textvariable=self.start_date_var, width=10)
        self.start_date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(start_date_frame, text="📅", width=2, command=lambda: self.open_calendar(self.start_date_var)).pack(
            side=tk.LEFT)

        # End Date
        ttk.Label(detail_frame, text="End Date (dd-mm-YYYY):").grid(row=5, column=0, sticky=tk.W, pady=2)
        end_date_frame = ttk.Frame(detail_frame)
        end_date_frame.grid(row=5, column=1, sticky=tk.EW, pady=2, padx=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(end_date_frame, textvariable=self.end_date_var, width=10)
        self.end_date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(end_date_frame, text="📅", width=2, command=lambda: self.open_calendar(self.end_date_var)).pack(
            side=tk.LEFT)

        ttk.Label(detail_frame, text="Amount:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(detail_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=6, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(detail_frame, text="Notes:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(detail_frame, textvariable=self.notes_var)
        self.notes_entry.grid(row=7, column=1, sticky=tk.EW, pady=2, padx=5)

        # Button frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.add_btn = ttk.Button(button_frame, text="Add", command=self.add_customer)
        self.add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.update_btn = ttk.Button(button_frame, text="Update", command=self.update_customer, state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.delete_btn = ttk.Button(button_frame, text="Delete", command=self.delete_customer, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.renew_btn = ttk.Button(button_frame, text="Renew", command=self.renew_subscription, state=tk.DISABLED)
        self.renew_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Reminders frame
        reminders_frame = ttk.LabelFrame(right_frame, text="Upcoming Renewals", padding="10")
        reminders_frame.pack(fill=tk.BOTH, expand=True)

        self.reminders_text = tk.Text(reminders_frame, height=10, wrap=tk.WORD)
        self.reminders_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_reminders_btn = ttk.Button(reminders_frame, text="Refresh Reminders",
                                                command=self.display_upcoming_renewals)
        self.refresh_reminders_btn.pack(fill=tk.X, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

        # Display upcoming renewals
        self.display_upcoming_renewals()

    def load_customers(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch customers from database
        self.cursor.execute("SELECT id, name, email, phone, subscription_type, end_date FROM customers ORDER BY name")
        customers = self.cursor.fetchall()

        # Insert into treeview with date formatting
        for customer in customers:
            id_, name, email, phone, sub_type, end_date = customer
            end_date_display = self.format_date_for_display(end_date)
            self.tree.insert('', tk.END, values=(id_, name, email, phone, sub_type, end_date_display))

    def format_date_for_display(self, date_str):
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.strftime("%d-%m-%Y")
            except Exception:
                return date_str
        return ""

    def format_date_for_db(self, date_str):
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%d-%m-%Y")
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return date_str
        return None

    def on_search(self, event=None):
        query = self.search_var.get()
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not query.strip():
            self.load_customers()
            return

        sql = '''
              SELECT id, name, email, phone, subscription_type, end_date
              FROM customers
              WHERE name LIKE ? \
                 OR email LIKE ? \
                 OR phone LIKE ?
              ORDER BY name \
              '''
        like_query = f'%{query}%'
        self.cursor.execute(sql, (like_query, like_query, like_query))
        customers = self.cursor.fetchall()

        for customer in customers:
            id_, name, email, phone, sub_type, end_date = customer
            end_date_display = self.format_date_for_display(end_date)
            self.tree.insert('', tk.END, values=(id_, name, email, phone, sub_type, end_date_display))

    def on_customer_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.clear_form()
            return

        item = self.tree.item(selected[0])
        cust_id = item['values'][0]

        self.cursor.execute("SELECT * FROM customers WHERE id=?", (cust_id,))
        customer = self.cursor.fetchone()
        if customer:
            # Unpack all fields
            (id_, name, email, phone, sub_type, start_date, end_date, amount, notes, last_reminder_sent) = customer

            self.selected_customer_id = id_
            self.name_var.set(name)
            self.email_var.set(email or "")
            self.phone_var.set(phone or "")
            self.sub_type_var.set(sub_type or "")
            self.start_date_var.set(self.format_date_for_display(start_date))
            self.end_date_var.set(self.format_date_for_display(end_date))
            self.amount_var.set(str(amount) if amount else "")
            self.notes_var.set(notes or "")

            # Enable buttons
            self.update_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.renew_btn.config(state=tk.NORMAL)
            self.add_btn.config(state=tk.DISABLED)
        else:
            self.clear_form()

    def clear_form(self):
        self.selected_customer_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.sub_type_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.amount_var.set("")
        self.notes_var.set("")

        self.update_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.renew_btn.config(state=tk.DISABLED)
        self.add_btn.config(state=tk.NORMAL)

    def validate_form(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Name is required")
            return False


        # Validate end date in dd-mm-yyyy
        end_date = self.end_date_var.get().strip()
        if not end_date:
            messagebox.showerror("Error", "End date is required")
            return False
        try:
            datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Error", "End date must be in DD-MM-YYYY format")
            return False

        # Validate start date if entered
        start_date = self.start_date_var.get().strip()
        if start_date:
            try:
                datetime.strptime(start_date, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Error", "Start date must be in DD-MM-YYYY format")
                return False

        # Validate amount if entered
        amount = self.amount_var.get().strip()
        if amount:
            try:
                float(amount)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
                return False

        return True

    # Calender setup
    def open_calendar(self, date_var):
        def set_date():
            date_var.set(cal.selection_get().strftime("%d-%m-%Y"))
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Select Date")
        top.grab_set()

        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(padx=10, pady=10)

        # Set current date if available
        try:
            if date_var.get():
                cal.selection_set(datetime.strptime(date_var.get(), "%d-%m-%Y"))
        except ValueError:
            pass

        ttk.Button(top, text="OK", command=set_date).pack(pady=5)

    def add_customer(self):
        if not self.validate_form():
            return

        try:
            self.cursor.execute('''
                                INSERT INTO customers
                                (name, email, phone, subscription_type, start_date, end_date, amount, notes,
                                 last_reminder_sent)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    self.name_var.get().strip(),
                                    self.email_var.get().strip(),
                                    self.phone_var.get().strip(),
                                    self.sub_type_var.get().strip(),
                                    self.format_date_for_db(self.start_date_var.get().strip()),
                                    self.format_date_for_db(self.end_date_var.get().strip()),
                                    float(self.amount_var.get().strip() or 0.0),
                                    self.notes_var.get().strip(),
                                    None
                                ))
            self.conn.commit()
            self.status_var.set("Customer added successfully.")
            self.clear_form()
            self.load_customers()
            self.display_upcoming_renewals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer:\n{e}")

    def update_customer(self):
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected")
            return
        if not self.validate_form():
            return

        try:
            self.cursor.execute('''
                                UPDATE customers
                                SET name              = ?,
                                    email             = ?,
                                    phone             = ?,
                                    subscription_type = ?,
                                    start_date        = ?,
                                    end_date          = ?,
                                    amount            = ?,
                                    notes             = ?
                                WHERE id = ?
                                ''', (
                                    self.name_var.get().strip(),
                                    self.email_var.get().strip(),
                                    self.phone_var.get().strip(),
                                    self.sub_type_var.get().strip(),
                                    self.format_date_for_db(self.start_date_var.get().strip()),
                                    self.format_date_for_db(self.end_date_var.get().strip()),
                                    float(self.amount_var.get().strip() or 0.0),
                                    self.notes_var.get().strip(),
                                    self.selected_customer_id
                                ))
            self.conn.commit()
            self.status_var.set("Customer updated successfully.")
            self.load_customers()
            self.display_upcoming_renewals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update customer:\n{e}")

    def delete_customer(self):
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected")
            return

        answer = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?")
        if not answer:
            return

        try:
            self.cursor.execute("DELETE FROM customers WHERE id=?", (self.selected_customer_id,))
            self.conn.commit()
            self.status_var.set("Customer deleted.")
            self.clear_form()
            self.load_customers()
            self.display_upcoming_renewals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer:\n{e}")

    def renew_subscription(self):
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected")
            return

        # Fetch current end date and subscription type
        self.cursor.execute("SELECT end_date, subscription_type FROM customers WHERE id=?",
                            (self.selected_customer_id,))
        result = self.cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Selected customer not found")
            return

        current_end_date, sub_type = result
        if not current_end_date:
            messagebox.showerror("Error", "Current end date not set")
            return

        # Parse current end date
        try:
            current_end_dt = datetime.strptime(current_end_date, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Current end date is invalid")
            return

        # Ask user for renewal months
        renewal_months = simpledialog.askinteger("Renew Subscription", "Enter number of months to extend subscription:",
                                                 minvalue=1, maxvalue=120)
        if renewal_months is None:
            return  # Cancelled

        # Calculate new end date
        # Adding months carefully (approximate with month increments)
        new_end_dt = self.add_months(current_end_dt, renewal_months)
        new_end_date_str = new_end_dt.strftime("%Y-%m-%d")

        try:
            self.cursor.execute("UPDATE customers SET end_date=?, last_reminder_sent=NULL WHERE id=?",
                                (new_end_date_str, self.selected_customer_id))
            self.conn.commit()
            self.status_var.set(f"Subscription renewed until {new_end_dt.strftime('%d-%m-%Y')}")
            self.load_customers()
            self.display_upcoming_renewals()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to renew subscription:\n{e}")

    def add_months(self, sourcedate, months):
        # Add months to a date, accounting for month overflow
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, self.last_day_of_month(year, month))
        return datetime(year, month, day)

    def last_day_of_month(self, year, month):
        # Returns the last day of the given month/year
        if month == 12:
            return 31
        next_month = datetime(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).day
        return last_day

    def display_upcoming_renewals(self):
        self.reminders_text.delete(1.0, tk.END)
        today = datetime.today()
        soon = today + timedelta(days=30)  # Next 30 days

        self.cursor.execute("SELECT name, email, phone, end_date FROM customers WHERE end_date IS NOT NULL")
        customers = self.cursor.fetchall()

        reminders = ""
        for name, email, phone, end_date in customers:
            if not end_date:
                continue
            try:
                dt = datetime.strptime(end_date, "%Y-%m-%d")
            except Exception:
                continue
            if today <= dt <= soon:
                end_date_display = dt.strftime("%d-%m-%Y")
                reminders += f"Name: {name}\nEmail: {email}\nPhone: {phone}\nRenewal Due: {end_date_display}\n\n"

        if reminders:
            self.reminders_text.insert(tk.END, reminders)
        else:
            self.reminders_text.insert(tk.END, "No renewals due in next 30 days.")

    def check_reminders(self):
        # Runs in a separate thread; checks reminders every 60 seconds
        while self.reminder_active:
            self.display_upcoming_renewals()
            time.sleep(60)

    def on_close(self):
        # Ask user if they want to save before exiting
        response = messagebox.askyesnocancel(
            "Save Before Exiting?",
            "Would you like to save your data before exiting?\n\n"
            "This will export active, expired, and expiring subscriptions to CSV files.",
            icon=messagebox.QUESTION
        )

        if response is None:  # User clicked Cancel
            return

        if response:  # User clicked Yes
            self.save_on_exit()

        # Proceed with closing
        self.reminder_active = False
        self.conn.close()
        self.root.destroy()

    def on_close(self):
        # Ask user if they want to save before exiting
        response = messagebox.askyesnocancel(
            "Save Before Exiting?",
            "Would you like to save your data before exiting?\n\n"
            "This will export active, expired, and expiring subscriptions to CSV files.",
            icon=messagebox.QUESTION
        )

        if response is None:  # User clicked Cancel
            return

        if response:  # User clicked Yes
            self.save_on_exit()

        # Proceed with closing
        self.reminder_active = False
        self.conn.close()
        self.root.destroy()

    def save_on_exit(self):
        """Automatically save data when exiting the application"""


        try:
            # Create default save directory
            save_dir = os.path.join(os.path.expanduser("~"), "SubscriptionManager_Exports")
            os.makedirs(save_dir, exist_ok=True)

            # Create timestamped folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(save_dir, f"Export_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)

            today = datetime.today().strftime("%Y-%m-%d")
            three_days_later = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")

            # Export Active Subscriptions
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date > ?
                                ORDER BY end_date
                                """, (three_days_later,))
            active_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(export_dir, "active_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               active_rows)

            # Export Expired Subscriptions
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date < ?
                                ORDER BY end_date DESC
                                """, (today,))
            expired_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(export_dir, "expired_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               expired_rows)

            # Export Expiring Soon Subscriptions (within 3 days)
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date >= ?
                                  AND end_date <= ?
                                ORDER BY end_date
                                """, (today, three_days_later))
            expiring_soon_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(export_dir, "expiring_soon_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               expiring_soon_rows)

            # Show confirmation message
            messagebox.showinfo(
                "Export Complete",
                f"Data exported successfully to:\n{export_dir}\n\n"
                f"- active_subscriptions.csv\n"
                f"- expired_subscriptions.csv\n"
                f"- expiring_soon_subscriptions.csv"
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}")

    def export_to_csv(self, file_path, headers, rows):
        """Helper method to write data to CSV file"""


        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                # Format dates for display
                formatted_row = list(row)
                # Format start date (index 5)
                if formatted_row[5]:
                    formatted_row[5] = self.format_date_for_display(formatted_row[5])
                # Format end date (index 6)
                if formatted_row[6]:
                    formatted_row[6] = self.format_date_for_display(formatted_row[6])
                writer.writerow(formatted_row)


    # Add new methods to the class
    def show_expired_subscriptions(self):
        today = datetime.today().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT id, name, email, phone, subscription_type, end_date FROM customers WHERE end_date < ?", (today,))
        self.populate_treeview_with_query()

    def show_active_subscriptions(self):
        today = datetime.today().strftime("%Y-%m-%d")
        self.cursor.execute(
            "SELECT id, name, email, phone, subscription_type, end_date FROM customers WHERE end_date >= ?", (today,))
        self.populate_treeview_with_query()


    # Data Export to csv
    def export_data(self):



        # Ask for folder to save files
        folder_path = filedialog.askdirectory(title="Select Folder to Save Export Files")
        if not folder_path:
            return

        today = datetime.today().strftime("%Y-%m-%d")
        three_days_later = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")

        try:
            # Export Active Subscriptions
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date > ?
                                ORDER BY end_date
                                """, (today,))
            active_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(folder_path, "active_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               active_rows)

            # Export Expired Subscriptions
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date < ?
                                ORDER BY end_date DESC
                                """, (today,))
            expired_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(folder_path, "expired_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               expired_rows)

            # Export Expiring Soon Subscriptions (within 3 days)
            self.cursor.execute("""
                                SELECT id,
                                       name,
                                       email,
                                       phone,
                                       subscription_type,
                                       start_date,
                                       end_date,
                                       amount,
                                       notes
                                FROM customers
                                WHERE end_date >= ?
                                  AND end_date <= ?
                                ORDER BY end_date
                                """, (today, three_days_later))
            expiring_soon_rows = self.cursor.fetchall()
            self.export_to_csv(os.path.join(folder_path, "expiring_soon_subscriptions.csv"),
                               ["ID", "Name", "Email", "Phone", "Subscription Type",
                                "Start Date", "End Date", "Amount", "Notes"],
                               expiring_soon_rows)

            self.status_var.set(f"Data exported successfully to {folder_path}")
            messagebox.showinfo("Export Complete",
                                f"3 files exported to:\n{folder_path}\n\n"
                                f"- active_subscriptions.csv\n"
                                f"- expired_subscriptions.csv\n"
                                f"- expiring_soon_subscriptions.csv")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{e}")





    # Import csv
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File to Import",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Skip header row

                # Validate header format
                expected_headers = ["ID", "Name", "Email", "Phone", "Subscription Type",
                                    "Start Date", "End Date", "Amount", "Notes"]
                if headers != expected_headers:
                    messagebox.showerror("Import Error",
                                         "Invalid CSV format. Please use the same format as exported files.")
                    return

                # Process each row
                success_count = 0
                error_rows = []
                for i, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    if len(row) < len(expected_headers):
                        error_rows.append(f"Row {i}: Insufficient columns")
                        continue

                    # Parse row data
                    try:
                        # Convert dates from display format to database format
                        start_date = self.format_date_for_db(row[5]) if row[5] else None
                        end_date = self.format_date_for_db(row[6])

                        # Validate required fields
                        if not row[1] or not end_date:
                            error_rows.append(f"Row {i}: Missing required fields (Name or End Date)")
                            continue

                        # Insert into database
                        self.cursor.execute('''
                                            INSERT INTO customers
                                            (name, email, phone, subscription_type, start_date, end_date, amount, notes)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                            ''', (
                                                row[1].strip(),  # Name
                                                row[2].strip(),  # Email
                                                row[3].strip(),  # Phone
                                                row[4].strip(),  # Subscription Type
                                                start_date,  # Start Date
                                                end_date,  # End Date
                                                float(row[7]) if row[7] else 0.0,  # Amount
                                                row[8].strip()  # Notes
                                            ))
                        success_count += 1
                    except Exception as e:
                        error_rows.append(f"Row {i}: {str(e)}")

                self.conn.commit()

                # Show import summary
                message = f"Imported {success_count} customer(s) successfully."
                if error_rows:
                    error_count = len(error_rows)
                    message += f"\n\n{error_count} error(s) occurred:"
                    if error_count > 5:
                        message += "\n" + "\n".join(error_rows[:5])
                        message += f"\n... and {error_count - 5} more errors."
                    else:
                        message += "\n" + "\n".join(error_rows)

                messagebox.showinfo("Import Complete", message)
                self.status_var.set(f"Imported {success_count} customer(s) from CSV")
                self.load_customers()
                self.display_upcoming_renewals()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data:\n{e}")
    # Helper method for CSV export
    def export_to_csv(self, file_path, headers, rows):


        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                # Format dates for display
                formatted_row = list(row)
                # Format start date (index 5)
                if formatted_row[5]:
                    formatted_row[5] = self.format_date_for_display(formatted_row[5])
                # Format end date (index 6)
                if formatted_row[6]:
                    formatted_row[6] = self.format_date_for_display(formatted_row[6])
                writer.writerow(formatted_row)


    def populate_treeview_with_query(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        customers = self.cursor.fetchall()
        for customer in customers:
            id_, name, email, phone, sub_type, end_date = customer
            end_date_display = self.format_date_for_display(end_date)
            self.tree.insert('', tk.END, values=(id_, name, email, phone, sub_type, end_date_display))


if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriptionManager(root)
    root.mainloop()


