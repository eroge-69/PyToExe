import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
import os

class DentalLabManagerAdvanced:
    def __init__(self, root):
        self.root = root
        self.root.title("Menaxher i Avancuar i Laboratorëve Dentarë")
        self.root.geometry("900x700")

        # Inicializo bazën e të dhënave
        self.conn = sqlite3.connect("dental_lab_advanced.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Çmimet e paracaktuara
        self.prices = {"Kurorë": 50, "Urë": 75, "Protezë": 100}

        # Ndërfaqja grafike
        self.create_gui()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS work_orders
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             date TEXT,
                             technician TEXT,
                             work_type TEXT,
                             teeth_count INTEGER,
                             price_per_unit REAL,
                             total REAL,
                             payment_status TEXT)''')
        self.conn.commit()

    def create_gui(self):
        # Frame për input
        input_frame = ttk.LabelFrame(self.root, text="Shto Punim të Ri")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Data
        ttk.Label(input_frame, text="Data (DD/MM/YYYY):").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Teknik
        ttk.Label(input_frame, text="Emri i Teknikut:").grid(row=1, column=0, padx=5, pady=5)
        self.technician_entry = ttk.Entry(input_frame)
        self.technician_entry.grid(row=1, column=1, padx=5, pady=5)

        # Lloji i punimit
        ttk.Label(input_frame, text="Lloji i Punimit:").grid(row=2, column=0, padx=5, pady=5)
        self.work_type_combo = ttk.Combobox(input_frame, values=list(self.prices.keys()))
        self.work_type_combo.grid(row=2, column=1, padx=5, pady=5)
        self.work_type_combo.set("Kurorë")

        # Sasia e dhëmbëve
        ttk.Label(input_frame, text="Sasia e Dhëmbëve:").grid(row=3, column=0, padx=5, pady=5)
        self.teeth_count_entry = ttk.Entry(input_frame)
        self.teeth_count_entry.grid(row=3, column=1, padx=5, pady=5)

        # Statusi i pagesës
        ttk.Label(input_frame, text="Statusi i Pagesës:").grid(row=4, column=0, padx=5, pady=5)
        self.payment_status_combo = ttk.Combobox(input_frame, values=["E Paguar", "Jo e Paguar"])
        self.payment_status_combo.grid(row=4, column=1, padx=5, pady=5)
        self.payment_status_combo.set("Jo e Paguar")

        # Buton për të shtuar punim
        ttk.Button(input_frame, text="Shto Punim", command=self.add_work_order).grid(row=5, column=0, columnspan=2, pady=10)

        # Tabela për të shfaqur punimet
        self.tree = ttk.Treeview(self.root, columns=("ID", "Data", "Teknik", "Lloji", "Dhëmbë", "Çmimi", "Totali", "Pagesa"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Teknik", text="Teknik")
        self.tree.heading("Lloji", text="Lloji i Punimit")
        self.tree.heading("Dhëmbë", text="Sasia e Dhëmbëve")
        self.tree.heading("Çmimi", text="Çmimi për Njësi (€)")
        self.tree.heading("Totali", text="Totali (€)")
        self.tree.heading("Pagesa", text="Statusi i Pagesës")
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Buton për të rifreskuar tabelën
        ttk.Button(self.root, text="Rifresko Tabelën", command=self.refresh_table).grid(row=2, column=0, pady=5)

        # Buton për të gjeneruar raport mujor
        ttk.Button(self.root, text="Gjenero Raport Mujor (Excel)", command=self.generate_monthly_report).grid(row=3, column=0, pady=5)

        # Rifresko tabelën fillestare
        self.refresh_table()

    def add_work_order(self):
        date = self.date_entry.get()
        technician = self.technician_entry.get()
        work_type = self.work_type_combo.get()
        teeth_count = self.teeth_count_entry.get()
        payment_status = self.payment_status_combo.get()

        try:
            teeth_count = int(teeth_count)
            price_per_unit = self.prices.get(work_type, 0)
            total = teeth_count * price_per_unit

            self.cursor.execute("INSERT INTO work_orders (date, technician, work_type, teeth_count, price_per_unit, total, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (date, technician, work_type, teeth_count, price_per_unit, total, payment_status))
            self.conn.commit()
            messagebox.showinfo("Sukses", "Punimi u shtua me sukses!")
            self.refresh_table()
            self.clear_entries()
        except ValueError:
            messagebox.showerror("Gabim", "Sasia e dhëmbëve duhet të jetë numër i plotë!")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute("SELECT * FROM work_orders")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.technician_entry.delete(0, tk.END)
        self.work_type_combo.set("Kurorë")
        self.teeth_count_entry.delete(0, tk.END)
        self.payment_status_combo.set("Jo e Paguar")

    def generate_monthly_report(self):
        month = datetime.now().strftime("%m/%Y")
        self.cursor.execute("SELECT date, technician, work_type, teeth_count, total, payment_status FROM work_orders WHERE strftime('%m/%Y', date) = ?", (month,))
        data = self.cursor.fetchall()

        df = pd.DataFrame(data, columns=["Data", "Teknik", "Lloji i Punimit", "Sasia e Dhëmbëve", "Totali (€)", "Statusi i Pagesës"])
        output_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "DentalApp", f"Raport_Mujor_{month.replace('/', '_')}.xlsx")
        df.to_excel(output_path, index=False)
        messagebox.showinfo("Sukses", f"Raporti mujor u gjenerua në: {output_path}")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DentalLabManagerAdvanced(root)
    root.mainloop()