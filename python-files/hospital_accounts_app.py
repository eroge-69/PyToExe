"""
Hospital Accounts & Daily Tasks Management (single-file Tkinter + SQLite app)

Features:
- Patients: add/edit/delete/search patient records (Name, CNIC, Age, Ward, Room, Address, Mobile)
- Doctors: add/edit/delete/search doctor records (Name, Department, Mobile)
- Invoices: create/edit/delete/search invoices recording patient, treatment type, amount paid, pending, discharge date
- Dashboard: shows total payments collected today and total number of patients
- Reports: show total payment, total collected cash, and pending balances, exportable to PDF or Excel, with search and filter by date, patient, and doctor, plus charts
- Settings: change currency symbol, date/time format, hospital name, logo, address, contact
- Uses system date/time automatically
- Data persisted in local SQLite database `hospital.db`
- Single Python file. No external packages required (uses built-in tkinter, sqlite3, csv). For PDF export requires reportlab. For charts requires matplotlib.

Run: python hospital_accounts_app.py
Requires: Python 3.8+ (Tkinter included)
Optional: `pip install reportlab matplotlib`

Note: This is a polished starter application. You can extend fields, validations, and add security/backup as needed.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, csv
from datetime import datetime, date

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ---------------------- Database helpers ----------------------
DB_FILENAME = 'hospital.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row
    return conn

# (init_db, get_setting, set_setting unchanged)

# ---------------------- App ----------------------
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(get_setting('hospital_name') or 'Hospital App')
        self.geometry('1200x750')
        self.minsize(950,600)
        self.style = ttk.Style(self)
        self._apply_theme()

        # Layout
        self.header_frame=ttk.Frame(self,padding=8); self.header_frame.pack(fill='x')
        self._build_header()

        self.main_frame=ttk.Frame(self); self.main_frame.pack(fill='both',expand=True)
        self.sidebar=ttk.Frame(self.main_frame,width=220); self.sidebar.pack(side='left',fill='y')
        self.content=ttk.Frame(self.main_frame); self.content.pack(side='left',fill='both',expand=True)

        self._build_sidebar()
        self._show_dashboard()

    # (theme, header, sidebar, dashboard unchanged)

    # ---------------------- Reports ----------------------
    def _show_reports(self):
        self._clear_content(); page=ttk.Frame(self.content,padding=12,style='Card.TFrame'); page.pack(fill='both',expand=True)
        ttk.Label(page,text='Reports',style='Header.TLabel').pack(anchor='w')

        # Filters
        filter_frame=ttk.Frame(page); filter_frame.pack(fill='x',pady=6)
        ttk.Label(filter_frame,text="Start Date:").pack(side='left')
        self.start_date=ttk.Entry(filter_frame); self.start_date.pack(side='left',padx=5)
        ttk.Label(filter_frame,text="End Date:").pack(side='left')
        self.end_date=ttk.Entry(filter_frame); self.end_date.pack(side='left',padx=5)
        ttk.Label(filter_frame,text="Patient:").pack(side='left')
        self.patient_filter=ttk.Entry(filter_frame,width=15); self.patient_filter.pack(side='left',padx=5)
        ttk.Label(filter_frame,text="Doctor:").pack(side='left')
        self.doctor_filter=ttk.Entry(filter_frame,width=15); self.doctor_filter.pack(side='left',padx=5)
        ttk.Button(filter_frame,text="Apply Filter",command=self._apply_report_filters).pack(side='left',padx=5)

        self.report_summary=ttk.Frame(page); self.report_summary.pack(fill='x',pady=8)

        self.chart_frame=ttk.Frame(page); self.chart_frame.pack(fill='both',expand=True,pady=8)

        self._apply_report_filters()

        btns=ttk.Frame(page); btns.pack(pady=10)
        ttk.Button(btns,text='Export CSV',command=self._export_csv).pack(side='left',padx=5)
        ttk.Button(btns,text='Export PDF',command=self._export_pdf).pack(side='left',padx=5)

    def _apply_report_filters(self):
        for w in self.report_summary.winfo_children(): w.destroy()
        for w in self.chart_frame.winfo_children(): w.destroy()

        query="SELECT SUM(amount_total), SUM(amount_paid), SUM(amount_pending) FROM invoices WHERE 1=1"
        params=[]

        if self.start_date.get():
            query+=" AND date(created_at)>=?"; params.append(self.start_date.get())
        if self.end_date.get():
            query+=" AND date(created_at)<=?"; params.append(self.end_date.get())
        if self.patient_filter.get():
            query+=" AND patient_name LIKE ?"; params.append('%'+self.patient_filter.get()+'%')
        if self.doctor_filter.get():
            query+=" AND doctor_id IN (SELECT id FROM doctors WHERE name LIKE ?)"; params.append('%'+self.doctor_filter.get()+'%')

        conn=get_db_connection(); cur=conn.cursor(); cur.execute(query,params)
        totals=cur.fetchone(); conn.close()

        total_payment, collected, pending=[float(x or 0) for x in totals]
        ttk.Label(self.report_summary,text=f"Total Payment: {get_setting('currency')} {total_payment:.2f}").pack(anchor='w',pady=4)
        ttk.Label(self.report_summary,text=f"Total Collected: {get_setting('currency')} {collected:.2f}").pack(anchor='w',pady=4)
        ttk.Label(self.report_summary,text=f"Total Pending: {get_setting('currency')} {pending:.2f}").pack(anchor='w',pady=4)

        if HAS_MATPLOTLIB:
            fig, ax = plt.subplots(figsize=(4,3))
            values=[collected,pending]
            labels=['Collected','Pending']
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title("Payments Overview")
            chart=FigureCanvasTkAgg(fig,self.chart_frame)
            chart.get_tk_widget().pack(fill='both',expand=True)
            plt.close(fig)

    # (export_csv, export_pdf unchanged)

if __name__ == '__main__':
    init_db()
    app=HospitalApp()
    app.mainloop()
