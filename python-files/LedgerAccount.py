# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 14:43:39 2025

@author: itssk
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import pyodbc
from openpyxl import Workbook
from datetime import datetime

class TransactionsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transactions")
        self.geometry("1000x600")
        self.db_path = "G://JAVA Projects/Database/pasys.accdb"
        self.conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_path}"
        self.selected_row_index = 0
        self.data = []

        self.create_widgets()
        self.load_database()

    def create_widgets(self):
        # Title Label
        lbl_title = tk.Label(self, text="Transactions", font=("Lucida Bright", 18, "bold"), fg="#8000FF")
        lbl_title.pack(pady=5)

        # Control Frame
        control_frame = tk.Frame(self)
        control_frame.pack(pady=5, fill='x')

        tk.Label(control_frame, text="Account of", font=("Tahoma", 12, "bold")).grid(row=0, column=0, padx=5)
        self.cmb_account = ttk.Combobox(control_frame)
        self.cmb_account.grid(row=0, column=1, padx=5)

        self.btn_show = tk.Button(control_frame, text="Show Records", command=self.show_records)
        self.btn_show.grid(row=0, column=2, padx=5)

        # Style for Treeview with borders to simulate grid lines
        style = ttk.Style()
        style.configure("Treeview",
                        borderwidth=1,
                        relief="solid",
                        rowheight=20)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Treeview.Heading", relief="raised")

        # Treeview for table with specific column widths
        columns = ("Date", "Particulars", "VNo", "Debit", "Credit", "Balance", "Type", "Narration")
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style="Treeview")
        # Define column widths
        column_widths = [40, 160, 15, 40, 40, 40, 15, 180]
      
        alignments = ['center', 'w', 'center', 'e', 'e', 'e', 'center', 'w']  # Alignment per column

        for col, width, anchor in zip(columns, column_widths, alignments):
          self.tree.heading(col, text=col)
          self.tree.column(col, width=width, anchor=anchor)
          self.tree.pack(fill='both', expand=True, pady=5)

# Navigation Buttons
        nav_frame = tk.Frame(self)
        nav_frame.pack(pady=5)
        self.btn_prev = tk.Button(nav_frame, text="Previous", command=self.prev_record, state='disabled')
        self.btn_prev.pack(side='left', padx=5)
        self.btn_next = tk.Button(nav_frame, text="Next", command=self.next_record, state='disabled')
        self.btn_next.pack(side='left', padx=5)

        # Export Button
        self.btn_export = tk.Button(self, text="Export to Excel", command=self.export_excel)
        self.btn_export.pack(pady=5)

    def load_database(self):
        # Load account names into combobox
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Code, Name FROM Accounts")
                accounts = cursor.fetchall()
                account_names = [f"{row.Code} {row.Name}" for row in accounts]
                self.cmb_account['values'] = account_names
                if account_names:
                    self.cmb_account.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {e}")

    def show_records(self):
        account_str = self.cmb_account.get()
        if not account_str:
            return
        account_code = account_str[:4]

        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                sql = """
                SELECT Dated,  Name, Tno, DrAmt, CrAmt, Narration, Query1.Code
                FROM (
                    SELECT Dated, Credit AS Code, Tno, Amount AS DrAmt, 0 AS CrAmt, Narration
                    FROM Transactions
                    WHERE Debit=?
                    UNION ALL
                    SELECT Dated, Debit AS Code, Tno, 0 AS DrAmt, Amount AS CrAmt, Narration
                    FROM Transactions
                    WHERE Credit=?
                ) AS Query1
                LEFT JOIN Accounts ON Query1.Code = Accounts.Code
                ORDER BY Dated
                """
                cursor.execute(sql, (account_code, account_code))
                self.data = cursor.fetchall()
                self.populate_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def populate_table(self):
        self.tree.delete(*self.tree.get_children())
        total_debit = 0.0
        total_credit = 0.0
        balance = 0.0
        for row in self.data:
            date_value = row.Dated
            if isinstance(date_value, datetime):
                date_str = date_value.strftime("%d-%m-%Y")
            else:
                date_str = str(date_value)
           
            particulars = "To " + row.Name if row.DrAmt > 0 else "By " + row.Name
            vno = row.Tno
            debit = row.DrAmt or 0.0
            credit = row.CrAmt or 0.0
            balance += debit - credit

            t_type = "Dr" if balance >= 0 else "Cr"
            s_debit = f"{debit:,.2f}" if debit else ""
            s_credit = f"{credit:,.2f}" if credit else ""
            s_balance = f"{abs(balance):,.2f}" if balance != 0 else ""

            self.tree.insert('', 'end', values=(date_str, particulars, vno, s_debit, s_credit, s_balance, t_type, row.Narration))
            if balance >= 0:
                total_debit += debit
            else:
                total_credit += abs(credit)

        # Insert totals row
        self.tree.insert('', 'end', values=("", "Total", "", f"{total_debit:,.2f}", f"{total_credit:,.2f}", "", "", ""))

        if self.data:
            self.selected_row_index = 0
            self.select_row(self.selected_row_index)
            self.btn_prev.config(state='normal')
            self.btn_next.config(state='normal')

    def select_row(self, index):
        self.tree.selection_remove(self.tree.selection())
        item_id = self.tree.get_children()[index]
        self.tree.selection_set(item_id)
        self.tree.see(item_id)

    def next_record(self):
        if self.data and self.selected_row_index < len(self.data) - 1:
            self.selected_row_index += 1
            self.select_row(self.selected_row_index)

    def prev_record(self):
        if self.data and self.selected_row_index > 0:
            self.selected_row_index -= 1
            self.select_row(self.selected_row_index)

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"

        # Write headers
        headers = ("Date", "Particulars", "VNo", "Debit", "Credit", "Balance", "Type", "Narration")
        ws.append(headers)

        # Write data rows
        for row_id in self.tree.get_children():
            values = self.tree.item(row_id)['values']
            ws.append(values)

        try:
            wb.save(file_path)
            messagebox.showinfo("Success", "Exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    app = TransactionsApp()
    app.mainloop()