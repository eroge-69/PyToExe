import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os

DB_NAME = "workers_data.db"
CURRENCY = "MAD"

# DB Setup
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    hourly_rate REAL NOT NULL
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS work_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER NOT NULL,
    work_date TEXT NOT NULL,
    regular_hours REAL NOT NULL,
    supplement_hours REAL NOT NULL,
    FOREIGN KEY(worker_id) REFERENCES workers(id)
)
""")
conn.commit()

# Helper Functions
def fetch_workers():
    c.execute("SELECT id, first_name, last_name FROM workers")
    return c.fetchall()

def fetch_worker_hourly_rate(worker_id):
    c.execute("SELECT hourly_rate FROM workers WHERE id=?", (worker_id,))
    res = c.fetchone()
    return res[0] if res else 0

def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)

def group_by_15days(df):
    # Create a period label for each row based on the 15-day interval
    def period_label(date):
        day = date.day
        start_day = 1 if day <= 15 else 16
        end_day = 15 if day <= 15 else (date.replace(day=28) + timedelta(days=4)).day
        return f"{date.year}-{date.month:02d}-{start_day:02d} to {date.year}-{date.month:02d}-{end_day:02d}"
    df['Period'] = df['work_date'].apply(lambda d: period_label(pd.to_datetime(d)))
    return df.groupby(['worker_id', 'Period']).agg({
        'regular_hours': 'sum',
        'supplement_hours': 'sum',
        'salary': 'sum'
    }).reset_index()

# GUI App
class WorkerHoursApp:
    def __init__(self, root):
        self.root = root
        root.title("Worker Hours Manager")
        root.geometry("900x600")
        root.configure(bg="#f0f4f7")

        # Style
        style = ttk.Style()
        style.configure("Treeview", font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'))
        style.configure("TButton", font=('Segoe UI', 10))
        style.configure("TLabel", background="#f0f4f7", font=('Segoe UI', 10))

        # --- Worker Frame ---
        worker_frame = ttk.LabelFrame(root, text="Workers", padding=10)
        worker_frame.place(x=10, y=10, width=420, height=280)

        ttk.Label(worker_frame, text="First Name:").grid(row=0, column=0, sticky=tk.W)
        self.first_name_var = tk.StringVar()
        ttk.Entry(worker_frame, textvariable=self.first_name_var).grid(row=0, column=1)

        ttk.Label(worker_frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W)
        self.last_name_var = tk.StringVar()
        ttk.Entry(worker_frame, textvariable=self.last_name_var).grid(row=1, column=1)

        ttk.Label(worker_frame, text=f"Hourly Rate ({CURRENCY}):").grid(row=2, column=0, sticky=tk.W)
        self.hourly_rate_var = tk.StringVar()
        ttk.Entry(worker_frame, textvariable=self.hourly_rate_var).grid(row=2, column=1)

        ttk.Button(worker_frame, text="Add Worker", command=self.add_worker).grid(row=3, column=0, pady=10)
        ttk.Button(worker_frame, text="Delete Worker", command=self.delete_worker).grid(row=3, column=1, pady=10)

        self.worker_listbox = tk.Listbox(worker_frame, height=8)
        self.worker_listbox.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.worker_listbox.bind('<<ListboxSelect>>', self.load_worker_details)

        self.load_workers()

        # --- Work Log Frame ---
        log_frame = ttk.LabelFrame(root, text="Daily Work Log", padding=10)
        log_frame.place(x=450, y=10, width=430, height=280)

        ttk.Label(log_frame, text="Select Worker:").grid(row=0, column=0, sticky=tk.W)
        self.work_log_worker_var = tk.StringVar()
        self.work_log_worker_combo = ttk.Combobox(log_frame, textvariable=self.work_log_worker_var, state='readonly')
        self.work_log_worker_combo.grid(row=0, column=1)
        self.refresh_worker_combo()

        ttk.Label(log_frame, text="Work Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W)
        self.work_date_var = tk.StringVar()
        self.work_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(log_frame, textvariable=self.work_date_var).grid(row=1, column=1)

        ttk.Label(log_frame, text="Regular Hours:").grid(row=2, column=0, sticky=tk.W)
        self.reg_hours_var = tk.StringVar()
        ttk.Entry(log_frame, textvariable=self.reg_hours_var).grid(row=2, column=1)

        ttk.Label(log_frame, text="Supplement Hours:").grid(row=3, column=0, sticky=tk.W)
        self.sup_hours_var = tk.StringVar()
        ttk.Entry(log_frame, textvariable=self.sup_hours_var).grid(row=3, column=1)

        ttk.Button(log_frame, text="Add Work Log", command=self.add_work_log).grid(row=4, column=0, columnspan=2, pady=10)

        # --- Work Log Table Frame ---
        table_frame = ttk.LabelFrame(root, text="Work Log Records", padding=10)
        table_frame.place(x=10, y=300, width=870, height=280)

        columns = ("id", "worker", "date", "regular_hours", "supplement_hours", "salary")
        self.work_log_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.work_log_tree.heading(col, text=col.replace("_", " ").title())
            self.work_log_tree.column(col, width=130)
        self.work_log_tree.pack(fill="both", expand=True)

        # --- Export Controls ---
        export_frame = ttk.LabelFrame(root, text="Export to Excel", padding=10)
        export_frame.place(x=10, y=580, width=870, height=60)

        ttk.Label(export_frame, text="From Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        self.export_from_var = tk.StringVar()
        self.export_from_var.set((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(export_frame, textvariable=self.export_from_var, width=15).grid(row=0, column=1)

        ttk.Label(export_frame, text="To Date (YYYY-MM-DD):").grid(row=0, column=2, sticky=tk.W)
        self.export_to_var = tk.StringVar()
        self.export_to_var.set(datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(export_frame, textvariable=self.export_to_var, width=15).grid(row=0, column=3)

        ttk.Button(export_frame, text="Export Excel", command=self.export_excel).grid(row=0, column=4, padx=10)

        self.load_work_logs()

    def add_worker(self):
        fn = self.first_name_var.get().strip()
        ln = self.last_name_var.get().strip()
        rate = self.hourly_rate_var.get().strip()
        if not fn or not ln or not rate:
            messagebox.showerror("Error", "Please fill all worker fields")
            return
        try:
            rate = float(rate)
        except:
            messagebox.showerror("Error", "Hourly rate must be a number")
            return

        c.execute("INSERT INTO workers (first_name, last_name, hourly_rate) VALUES (?, ?, ?)", (fn, ln, rate))
        conn.commit()
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.hourly_rate_var.set("")
        self.load_workers()
        self.refresh_worker_combo()
        messagebox.showinfo("Success", "Worker added")

    def delete_worker(self):
        selected = self.worker_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select a worker to delete")
            return
        idx = selected[0]
        worker_id = self.worker_listbox.get(idx).split(":")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure to delete this worker? This will delete all related work logs.")
        if confirm:
            c.execute("DELETE FROM work_log WHERE worker_id=?", (worker_id,))
            c.execute("DELETE FROM workers WHERE id=?", (worker_id,))
            conn.commit()
            self.load_workers()
            self.refresh_worker_combo()
            self.load_work_logs()
            messagebox.showinfo("Success", "Worker and related logs deleted")

    def load_workers(self):
        self.worker_listbox.delete(0, tk.END)
        for w in fetch_workers():
            self.worker_listbox.insert(tk.END, f"{w[0]}: {w[1]} {w[2]}")

    def load_worker_details(self, event):
        selected = self.worker_listbox.curselection()
        if not selected:
            return
        idx = selected[0]
        worker_id = self.worker_listbox.get(idx).split(":")[0]
        c.execute("SELECT first_name, last_name, hourly_rate FROM workers WHERE id=?", (worker_id,))
        res = c.fetchone()
        if res:
            self.first_name_var.set(res[0])
            self.last_name_var.set(res[1])
            self.hourly_rate_var.set(str(res[2]))

    def refresh_worker_combo(self):
        workers = fetch_workers()
        worker_display = [f"{w[0]}: {w[1]} {w[2]}" for w in workers]
        self.work_log_worker_combo['values'] = worker_display
        if worker_display:
            self.work_log_worker_combo.current(0)

    def add_work_log(self):
        worker = self.work_log_worker_var.get()
        if not worker:
            messagebox.showerror("Error", "Select a worker")
            return
        worker_id = int(worker.split(":")[0])

        date_str = self.work_date_var.get().strip()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD")
            return

        reg_hours = self.reg_hours_var.get().strip()
        sup_hours = self.sup_hours_var.get().strip()
        try:
            reg_hours = float(reg_hours)
            sup_hours = float(sup_hours)
            if reg_hours < 0 or sup_hours < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Hours must be positive numbers")
            return

        c.execute(
            "INSERT INTO work_log (worker_id, work_date, regular_hours, supplement_hours) VALUES (?, ?, ?, ?)",
            (worker_id, date_str, reg_hours, sup_hours)
        )
        conn.commit()
        self.reg_hours_var.set("")
        self.sup_hours_var.set("")
        self.load_work_logs()
        messagebox.showinfo("Success", "Work log added")

    def load_work_logs(self):
        clear_tree(self.work_log_tree)
        c.execute("""
        SELECT wl.id, w.first_name || ' ' || w.last_name as worker_name, wl.work_date, wl.regular_hours, wl.supplement_hours,
            (wl.regular_hours + wl.supplement_hours) * w.hourly_rate as salary
        FROM work_log wl
        JOIN workers w ON wl.worker_id = w.id
        ORDER BY wl.work_date DESC
        """)
        rows = c.fetchall()
        for row in rows:
            self.work_log_tree.insert("", tk.END, values=(
                row[0], row[1], row[2], f"{row[3]:.2f}", f"{row[4]:.2f}", f"{row[5]:.2f} {CURRENCY}"
            ))

    def export_excel(self):
        from_date_str = self.export_from_var.get().strip()
        to_date_str = self.export_to_var.get().strip()
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")
            if from_date > to_date:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid date range")
            return

        c.execute("""
        SELECT wl.worker_id, w.first_name || ' ' || w.last_name as worker_name, wl.work_date, wl.regular_hours, wl.supplement_hours,
            (wl.regular_hours + wl.supplement_hours) * w.hourly_rate as salary
        FROM work_log wl
        JOIN workers w ON wl.worker_id = w.id
        WHERE wl.work_date BETWEEN ? AND ?
        ORDER BY wl.work_date ASC
        """, (from_date_str, to_date_str))
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Info", "No data in the selected date range")
            return

        df = pd.DataFrame(rows, columns=['worker_id', 'worker_name', 'work_date', 'regular_hours', 'supplement_hours', 'salary'])
        # Group by 15-day periods
        df['work_date'] = pd.to_datetime(df['work_date'])
        def get_period(d):
            if d.day <= 15:
                return f"{d.year}-{d.month:02d}-01 to {d.year}-{d.month:02d}-15"
            else:
                # last day of month calculation
                next_month = d.replace(day=28) + timedelta(days=4)
                last_day = (next_month - timedelta(days=next_month.day)).day
                return f"{d.year}-{d.month:02d}-16 to {d.year}-{d.month:02d}-{last_day:02d}"

        df['Period'] = df['work_date'].apply(get_period)
        summary = df.groupby(['worker_name', 'Period']).agg({
            'regular_hours': 'sum',
            'supplement_hours': 'sum',
            'salary': 'sum'
        }).reset_index()

        # Export all detailed and summary sheets
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel file"
        )
        if not save_path:
            return

        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Detailed Work Logs", index=False)
            summary.to_excel(writer, sheet_name="15-Day Summary", index=False)

        messagebox.showinfo("Exported", f"Data exported successfully to:\n{save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkerHoursApp(root)
    root.mainloop()
