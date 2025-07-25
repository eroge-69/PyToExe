# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 19:10:21 2025

@author: itssk
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import os
from datetime import datetime, date
from tkcalendar import DateEntry

# --- Database Configuration ---
DB_FILE = "Pasys.accdb"
DB_DRIVER = "{Microsoft Access Driver (*.mdb, *.accdb)}"
TABLE_NAME = "Transactions"

# Load accounts data into a dictionary {Code: Name}
def get_accounts_dict():
    accounts_dict = {}
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Code, Name FROM Accounts")
            for code, name in cursor.fetchall():
                # Store as "Code Name" in the dictionary for easy lookup later
                accounts_dict[code.strip()] = name.strip()
        except pyodbc.Error as ex:
            messagebox.showerror("Database Error", f"Error fetching accounts: {ex}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return accounts_dict

def connect_db():
    """Establish a connection to the MS Access database."""
    try:
        conn_str = (
            f"DRIVER={DB_DRIVER};"
            f"DBQ={os.path.abspath(DB_FILE)};"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database connection error: {sqlstate}")
        messagebox.showerror(
            "Database Error",
            f"Could not connect to the database.\nError: {sqlstate}\n\n"
            "Please ensure:\n"
            "1. Microsoft Access Database Engine is installed.\n"
            "2. The driver matches your Access file type.\n"
            "3. The database file exists."
        )
        return None

# --- Main Application ---
class TransactionApp:
    def __init__(self, master):
        self.master = master
        master.title("MS Access Transaction Manager")
        master.geometry("1000x750")
        self.accounts_dict = get_accounts_dict()
        # Create a list of "Code Name" for combobox values
        self.accounts_display_list = [f"{code} {name}" for code, name in self.accounts_dict.items()]
        # Sort the display list for better user experience
        self.accounts_display_list.sort()


        # --- Input Variables ---
        self.tno_entry_var = tk.StringVar()
        self.debit_combobox = None
        self.credit_combobox = None
        self.debit_var = tk.StringVar()
        self.credit_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.narration_var = tk.StringVar()
        self.finyear_var = tk.StringVar()

        self.selected_tno = None

        # --- Build GUI ---
        self.build_gui()

        # Load data initially
        self.load_data_and_set_tno()

    def build_gui(self):
        # Input Frame
        self.input_frame = ttk.LabelFrame(self.master, text="Transaction Details", padding=(20, 10))
        self.input_frame.pack(pady=10, padx=20, fill="x")

        # TNo (readonly)
        ttk.Label(self.input_frame, text="TNo:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.tno_entry = ttk.Entry(self.input_frame, textvariable=self.tno_entry_var, width=10, state="readonly")
        self.tno_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Dated
        ttk.Label(self.input_frame, text="Dated:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.dated_entry = DateEntry(self.input_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                     year=datetime.now().year, month=datetime.now().month, day=datetime.now().day, date_pattern='yyyy-mm-dd')
        self.dated_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Debit Combobox (Now displays "Code Name")
        ttk.Label(self.input_frame, text="Debit Account:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.debit_combobox = ttk.Combobox(self.input_frame, values=self.accounts_display_list, width=30) # Increased width
        self.debit_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.debit_combobox.set("")

        # Credit Combobox (Now displays "Code Name")
        ttk.Label(self.input_frame, text="Credit Account:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.credit_combobox = ttk.Combobox(self.input_frame, values=self.accounts_display_list, width=30) # Increased width
        self.credit_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.credit_combobox.set("")

        # Amount
        ttk.Label(self.input_frame, text="Amount:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.amount_entry = ttk.Entry(self.input_frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Narration
        ttk.Label(self.input_frame, text="Narration (120):").grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.narration_entry = ttk.Entry(self.input_frame, textvariable=self.narration_var, width=50)
        self.narration_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # FinYear
        ttk.Label(self.input_frame, text="FinYear (YYYY-YY):").grid(row=6, column=0, sticky="w", pady=5, padx=5)
        self.finyear_entry = ttk.Entry(self.input_frame, textvariable=self.finyear_var, width=10)
        self.finyear_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Add New Transaction", command=self.add_new_transaction).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update Selected", command=self.update_selected_transaction).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected_transaction).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side="left", padx=5)

        # Filter Frame
        self.filter_frame = ttk.LabelFrame(self.master, text="Filter Transactions by Date", padding=(20,10))
        self.filter_frame.pack(pady=10, padx=20, fill="x")
        ttk.Label(self.filter_frame, text="From Date:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.from_date = DateEntry(self.filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.from_date.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.filter_frame, text="To Date:").grid(row=0, column=2, sticky="w", pady=5, padx=5)
        self.to_date = DateEntry(self.filter_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.to_date.grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter).grid(row=0, column=4, padx=5)
        ttk.Button(self.filter_frame, text="Clear Filter", command=self.clear_filter).grid(row=0, column=5, padx=5)

        # Data Display Treeview
        self.display_frame = ttk.LabelFrame(self.master, text="All Transactions", padding=(10,5))
        self.display_frame.pack(pady=10, padx=20, fill="both", expand=True)
        columns = ("TNo", "Dated", "Debit", "Credit", "Amount", "Narration", "FinYear")
        self.tree = ttk.Treeview(self.display_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("TNo", width=60, stretch=False)
        self.tree.column("Dated", width=100)
        self.tree.column("Debit", width=160) # Increased width for "Code Name"
        self.tree.column("Credit", width=160) # Increased width for "Code Name"
        self.tree.column("Amount", width=100)
        self.tree.column("Narration", width=250)
        self.tree.column("FinYear", width=80)
        self.tree.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def get_display_account(self, code):
        """Return 'Code Name' if available, else just code."""
        name = self.accounts_dict.get(code.strip(), "")
        return f"{code.strip()} {name}" if name else code.strip()

    def get_code_from_display(self, display_str):
        """Extract the account code from a 'Code Name' string."""
        if display_str:
            parts = display_str.split(" ", 1) # Split only on the first space
            return parts[0].strip()
        return ""

    def load_data_and_set_tno(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = self.fetch_data()
        for row in data:
            row_list = list(row)
            # Format date
            if isinstance(row_list[1], (datetime, date)):
                row_list[1] = row_list[1].strftime("%Y-%m-%d")
            # Format Debit and Credit for display (already handled by get_display_account)
            row_list[2] = self.get_display_account(str(row_list[2])) # Ensure string for get_display_account
            row_list[3] = self.get_display_account(str(row_list[3])) # Ensure string for get_display_account
            self.tree.insert("", "end", values=tuple(str(i) for i in row_list))
        self.set_next_tno()

    def fetch_data(self, start_date=None, end_date=None):
        conn = connect_db()
        data = []
        if conn:
            cursor = conn.cursor()
            try:
                sql = f"SELECT TNo, Dated, Debit, Credit, Amount, Narration, FinYear FROM {TABLE_NAME}"
                params = []
                clauses = []
                if start_date:
                    clauses.append("Dated >= ?")
                    params.append(start_date)
                if end_date:
                    clauses.append("Dated <= ?")
                    params.append(end_date)
                if clauses:
                    sql += " WHERE " + " AND ".join(clauses)
                sql += " ORDER BY TNo DESC"
                cursor.execute(sql, tuple(params))
                data = cursor.fetchall()
            except pyodbc.Error as ex:
                messagebox.showerror("Database Error", f"Error fetching data: {ex}")
            finally:
                cursor.close()
                conn.close()
        return data

    def set_next_tno(self):
        next_tno = self.get_next_tno()
        self.tno_entry.config(state="normal")
        self.tno_entry_var.set(str(next_tno))
        self.tno_entry.config(state="readonly")

    def get_next_tno(self):
        conn = connect_db()
        max_tno = 0
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT MAX(TNo) FROM {TABLE_NAME}")
                res = cursor.fetchone()
                if res and res[0]:
                    max_tno = int(res[0])
            except pyodbc.Error:
                max_tno = 0
            finally:
                cursor.close()
                conn.close()
        return max_tno + 1

    def add_new_transaction(self):
        tno_str = self.tno_entry_var.get().strip()
        dated = self.dated_entry.get_date()
        # Get the full string "Code Name" from the combobox
        debit_display = self.debit_combobox.get().strip()
        credit_display = self.credit_combobox.get().strip()
        
        # Extract only the code for database storage
        debit_code = self.get_code_from_display(debit_display)
        credit_code = self.get_code_from_display(credit_display)
        
        amount_str = self.amount_var.get().strip()
        narration = self.narration_var.get().strip()
        finyear = self.finyear_var.get().strip()

        # Validation
        if not tno_str or not amount_str:
            messagebox.showwarning("Input Error", "TNo and Amount are required.")
            return
        try:
            tno = int(tno_str)
        except ValueError: # Catch specific error for clarity
            messagebox.showwarning("Input Error", "TNo must be an integer.")
            return
        try:
            amount = float(amount_str)
        except ValueError: # Catch specific error for clarity
            messagebox.showwarning("Input Error", "Amount must be a number.")
            return
            
        # Validate that the selected codes actually exist in accounts_dict
        if debit_code not in self.accounts_dict:
            messagebox.showwarning("Input Error", "Invalid Debit Account selected.")
            return
        if credit_code not in self.accounts_dict:
            messagebox.showwarning("Input Error", "Invalid Credit Account selected.")
            return

        if len(narration) > 120:
            messagebox.showwarning("Input Error", "Narration max 120 chars.")
            return
        if len(finyear) > 7:
            messagebox.showwarning("Input Error", "FinYear max 7 chars.")
            return

        # Save only the code
        if self.insert_data(tno, dated, debit_code, credit_code, amount, narration, finyear):
            self.clear_fields()
            self.load_data_and_set_tno()

    def insert_data(self, tno, dated, debit_code, credit_code, amount, narration, finyear):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE TNo = ?", (tno,))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", f"TNo {tno} already exists.")
                    return False
                cursor.execute(
                    f"INSERT INTO {TABLE_NAME} (TNo, Dated, Debit, Credit, Amount, Narration, FinYear) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (tno, dated, debit_code, credit_code, amount, narration, finyear)
                )
                conn.commit()
                messagebox.showinfo("Success", "Transaction saved.")
                return True
            except pyodbc.Error as ex:
                messagebox.showerror("DB Error", f"{ex}")
            finally:
                cursor.close()
                conn.close()
        return False

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            vals = self.tree.item(selected, 'values')
            # TNo, Dated, Debit, Credit, Amount, Narration, FinYear
            self.selected_tno = int(vals[0])
            # Set fields
            self.tno_entry.config(state="normal")
            self.tno_entry_var.set(str(vals[0]))
            self.tno_entry.config(state="readonly")
            # Date
            try:
                dt = datetime.strptime(vals[1], "%Y-%m-%d").date()
                self.dated_entry.set_date(dt)
            except ValueError: # Catch specific error for clarity
                self.dated_entry.set_date(datetime.now().date())
                
            # Set comboboxes with the full "Code Name" string from the Treeview
            self.debit_combobox.set(vals[2])
            self.credit_combobox.set(vals[3])

            self.amount_var.set(vals[4])
            self.narration_var.set(vals[5])
            self.finyear_var.set(vals[6])
        else:
            self.clear_fields()

    def update_selected_transaction(self):
        if not self.selected_tno:
            messagebox.showwarning("No selection", "Please select a transaction.")
            return
        tno = self.selected_tno
        dated = self.dated_entry.get_date()
        
        # Get the full string "Code Name" from the combobox
        debit_display = self.debit_combobox.get().strip()
        credit_display = self.credit_combobox.get().strip()
        
        # Extract only the code for database storage
        debit_code = self.get_code_from_display(debit_display)
        credit_code = self.get_code_from_display(credit_display)
        
        amount_str = self.amount_var.get().strip()
        narration = self.narration_var.get().strip()
        finyear = self.finyear_var.get().strip()

        # Validation
        try:
            amount = float(amount_str)
        except ValueError: # Catch specific error for clarity
            messagebox.showwarning("Input Error", "Amount must be a number.")
            return
            
        # Validate that the selected codes actually exist in accounts_dict
        if debit_code not in self.accounts_dict:
            messagebox.showwarning("Input Error", "Invalid Debit Account selected.")
            return
        if credit_code not in self.accounts_dict:
            messagebox.showwarning("Input Error", "Invalid Credit Account selected.")
            return

        if len(narration) > 120:
            messagebox.showwarning("Input Error", "Narration max 120 chars.")
            return
        if len(finyear) > 7:
            messagebox.showwarning("Input Error", "FinYear max 7 chars.")
            return
        if messagebox.askyesno("Confirm Update", f"Update TNo {tno}?"):
            if self.update_data(tno, dated, debit_code, credit_code, amount, narration, finyear):
                self.load_data_and_set_tno()
                self.clear_fields()

    def update_data(self, tno, dated, debit_code, credit_code, amount, narration, finyear):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    f"UPDATE {TABLE_NAME} SET Dated=?, Debit=?, Credit=?, Amount=?, Narration=?, FinYear=? WHERE TNo=?",
                    (dated, debit_code, credit_code, amount, narration, finyear, tno)
                )
                if cursor.rowcount == 0:
                    messagebox.showwarning("Update", "No record updated.")
                else:
                    messagebox.showinfo("Success", "Record updated.")
                conn.commit()
                return True
            except pyodbc.Error as ex:
                messagebox.showerror("DB Error", str(ex))
            finally:
                cursor.close()
                conn.close()
        return False

    def delete_selected_transaction(self):
        if not self.selected_tno:
            messagebox.showwarning("No selection", "Please select a transaction.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete TNo {self.selected_tno}?"):
            if self.delete_data(self.selected_tno):
                self.load_data_and_set_tno()
                self.clear_fields()

    def delete_data(self, tno):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE TNo=?", (tno,))
                if cursor.rowcount == 0:
                    messagebox.showwarning("Delete", "No record deleted.")
                else:
                    messagebox.showinfo("Success", "Record deleted.")
                conn.commit()
                return True
            except pyodbc.Error as ex:
                messagebox.showerror("DB Error", str(ex))
            finally:
                cursor.close()
                conn.close()
        return False

    def clear_fields(self):
        self.tno_entry.config(state="normal")
        self.tno_entry_var.set("")
        self.tno_entry.config(state="readonly")
        self.dated_entry.set_date(datetime.now().date())
        self.debit_combobox.set("")
        self.credit_combobox.set("")
        self.amount_var.set("")
        self.narration_var.set("")
        self.finyear_var.set("")
        self.selected_tno = None
        self.set_next_tno()

    def set_next_tno(self):
        next_tno = self.get_next_tno()
        self.tno_entry.config(state="normal")
        self.tno_entry_var.set(str(next_tno))
        self.tno_entry.config(state="readonly")

    def apply_filter(self):
        start_date = self.from_date.get_date()
        end_date = self.to_date.get_date()
        self.load_filtered_data(start_date, end_date)

    def load_filtered_data(self, start_date, end_date):
        for item in self.tree.get_children():
            self.tree.delete(item)
        data = self.fetch_data(start_date, end_date)
        for row in data:
            row_list = list(row)
            if isinstance(row_list[1], (datetime, date)):
                row_list[1] = row_list[1].strftime("%Y-%m-%d")
            row_list[2] = self.get_display_account(str(row_list[2]))
            row_list[3] = self.get_display_account(str(row_list[3]))
            self.tree.insert("", "end", values=tuple(str(i) for i in row_list))

    def clear_filter(self):
        self.from_date.set_date(datetime.now())
        self.to_date.set_date(datetime.now())
        self.load_data_and_set_tno()

# --- Run the application ---
if __name__ == "__main__":
    create_table_if_not_exists = lambda: None  # Placeholder if needed
    root = tk.Tk()
    app = TransactionApp(root)
    root.mainloop()