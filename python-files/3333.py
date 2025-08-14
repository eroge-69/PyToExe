import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os
from datetime import datetime

# ---------------- DATABASE SETUP ---------------- #
DB_FILE = "techwiz.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    timing TEXT NOT NULL,
    seat_limit INTEGER NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    batch_id INTEGER NOT NULL,
    FOREIGN KEY(batch_id) REFERENCES batches(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    year INTEGER NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()

# ---------------- MAIN APP ---------------- #
root = tk.Tk()
root.title("Techwiz Academy - Fees & Batch Manager")
root.geometry("900x600")
root.configure(bg="white")

tab_control = ttk.Notebook(root)

# Tabs
batch_tab = ttk.Frame(tab_control)
student_tab = ttk.Frame(tab_control)
fees_tab = ttk.Frame(tab_control)
report_tab = ttk.Frame(tab_control)

tab_control.add(batch_tab, text="Batches")
tab_control.add(student_tab, text="Students")
tab_control.add(fees_tab, text="Fees")
tab_control.add(report_tab, text="Reports")
tab_control.pack(expand=1, fill="both")

# ---------------- FUNCTIONS ---------------- #
def refresh_batch_list():
    for row in batch_tree.get_children():
        batch_tree.delete(row)
    cur.execute("SELECT id, name, timing, seat_limit FROM batches")
    for r in cur.fetchall():
        batch_tree.insert("", tk.END, values=r)
    draw_batch_chart()

def add_batch():
    name = batch_name_var.get()
    timing = batch_time_var.get()
    seat_limit = batch_seat_var.get()
    if not name or not timing or not seat_limit.isdigit():
        messagebox.showerror("Error", "Please enter valid batch details.")
        return
    cur.execute("INSERT INTO batches (name, timing, seat_limit) VALUES (?, ?, ?)",
                (name, timing, int(seat_limit)))
    conn.commit()
    refresh_batch_list()
    batch_name_var.set("")
    batch_time_var.set("")
    batch_seat_var.set("")

def delete_batch():
    selected = batch_tree.selection()
    if not selected:
        return
    bid = batch_tree.item(selected[0])['values'][0]
    cur.execute("DELETE FROM batches WHERE id=?", (bid,))
    conn.commit()
    refresh_batch_list()

def draw_batch_chart():
    cur.execute("""
        SELECT name, seat_limit, 
        (SELECT COUNT(*) FROM students WHERE batch_id=b.id) as allocated
        FROM batches b
    """)
    data = cur.fetchall()
    names = [r[0] for r in data]
    allocated = [r[2] for r in data]
    vacant = [r[1] - r[2] for r in data]

    fig = Figure(figsize=(4,3), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(names, allocated, label="Allocated", color="skyblue")
    ax.bar(names, vacant, bottom=allocated, label="Vacant", color="lightgreen")
    ax.set_ylabel("Seats")
    ax.set_title("Batch Seats Allocation")
    ax.legend()

    for widget in batch_chart_frame.winfo_children():
        widget.destroy()

    chart_canvas = FigureCanvasTkAgg(fig, batch_chart_frame)
    chart_canvas.get_tk_widget().pack(fill="both", expand=True)
    chart_canvas.draw()

def refresh_student_list():
    for row in student_tree.get_children():
        student_tree.delete(row)
    cur.execute("""
        SELECT s.id, s.name, b.name, b.timing 
        FROM students s 
        JOIN batches b ON s.batch_id = b.id
    """)
    for r in cur.fetchall():
        student_tree.insert("", tk.END, values=r)

def add_student():
    name = student_name_var.get()
    batch = student_batch_var.get()
    if not name or not batch:
        messagebox.showerror("Error", "Please enter student name and batch.")
        return
    cur.execute("SELECT id FROM batches WHERE name=?", (batch,))
    batch_id = cur.fetchone()
    if not batch_id:
        messagebox.showerror("Error", "Batch not found.")
        return
    cur.execute("INSERT INTO students (name, batch_id) VALUES (?, ?)", (name, batch_id[0]))
    conn.commit()
    refresh_student_list()
    refresh_batch_list()
    student_name_var.set("")

def delete_student():
    selected = student_tree.selection()
    if not selected:
        return
    sid = student_tree.item(selected[0])['values'][0]
    cur.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    refresh_student_list()
    refresh_batch_list()

def refresh_fees_list():
    for row in fees_tree.get_children():
        fees_tree.delete(row)
    cur.execute("""
        SELECT f.id, s.name, f.month, f.year, f.amount
        FROM fees f
        JOIN students s ON f.student_id = s.id
    """)
    for r in cur.fetchall():
        fees_tree.insert("", tk.END, values=r)

def add_fee():
    student = fee_student_var.get()
    month = fee_month_var.get()
    year = fee_year_var.get()
    amount = fee_amount_var.get()
    if not student or not month or not year.isdigit() or not amount.replace('.','',1).isdigit():
        messagebox.showerror("Error", "Please enter valid fee details.")
        return
    cur.execute("SELECT id FROM students WHERE name=?", (student,))
    sid = cur.fetchone()
    if not sid:
        messagebox.showerror("Error", "Student not found.")
        return
    cur.execute("INSERT INTO fees (student_id, month, year, amount) VALUES (?, ?, ?, ?)",
                (sid[0], month, int(year), float(amount)))
    conn.commit()
    refresh_fees_list()

def delete_fee():
    selected = fees_tree.selection()
    if not selected:
        return
    fid = fees_tree.item(selected[0])['values'][0]
    cur.execute("DELETE FROM fees WHERE id=?", (fid,))
    conn.commit()
    refresh_fees_list()

def draw_income_chart():
    cur.execute("""
        SELECT year, month, SUM(amount)
        FROM fees
        GROUP BY year, month
        ORDER BY year, month
    """)
    data = cur.fetchall()
    months = [f"{m}-{y}" for y, m, _ in data]
    amounts = [a for _, _, a in data]

    fig = Figure(figsize=(4,3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(months, amounts, marker="o", color="red")
    ax.set_ylabel("Income")
    ax.set_title("Monthly Income")
    ax.tick_params(axis='x', rotation=45)

    for widget in report_chart_frame.winfo_children():
        widget.destroy()

    chart_canvas = FigureCanvasTkAgg(fig, report_chart_frame)
    chart_canvas.get_tk_widget().pack(fill="both", expand=True)
    chart_canvas.draw()

def export_csv():
    cur.execute("SELECT * FROM batches")
    batches = cur.fetchall()
    with open("batches.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Timing", "Seat Limit"])
        writer.writerows(batches)
    messagebox.showinfo("Export", "Batches exported to batches.csv")

# ---------------- UI: BATCH TAB ---------------- #
batch_name_var = tk.StringVar()
batch_time_var = tk.StringVar()
batch_seat_var = tk.StringVar()

tk.Label(batch_tab, text="Batch Name:").pack()
tk.Entry(batch_tab, textvariable=batch_name_var).pack()

tk.Label(batch_tab, text="Timing:").pack()
tk.Entry(batch_tab, textvariable=batch_time_var).pack()

tk.Label(batch_tab, text="Seat Limit:").pack()
tk.Entry(batch_tab, textvariable=batch_seat_var).pack()

tk.Button(batch_tab, text="Add Batch", command=add_batch, bg="lightblue").pack(pady=5)
tk.Button(batch_tab, text="Delete Batch", command=delete_batch, bg="lightcoral").pack(pady=5)
tk.Button(batch_tab, text="Export CSV", command=export_csv, bg="lightgreen").pack(pady=5)

batch_tree = ttk.Treeview(batch_tab, columns=("ID", "Name", "Timing", "Seats"), show="headings")
for col in ("ID", "Name", "Timing", "Seats"):
    batch_tree.heading(col, text=col)
batch_tree.pack(fill="both", expand=True)

batch_chart_frame = tk.Frame(batch_tab, bg="white")
batch_chart_frame.pack(fill="both", expand=True)

# ---------------- UI: STUDENT TAB ---------------- #
student_name_var = tk.StringVar()
student_batch_var = tk.StringVar()

tk.Label(student_tab, text="Student Name:").pack()
tk.Entry(student_tab, textvariable=student_name_var).pack()

tk.Label(student_tab, text="Batch:").pack()
tk.Entry(student_tab, textvariable=student_batch_var).pack()

tk.Button(student_tab, text="Add Student", command=add_student, bg="lightblue").pack(pady=5)
tk.Button(student_tab, text="Delete Student", command=delete_student, bg="lightcoral").pack(pady=5)

student_tree = ttk.Treeview(student_tab, columns=("ID", "Name", "Batch", "Timing"), show="headings")
for col in ("ID", "Name", "Batch", "Timing"):
    student_tree.heading(col, text=col)
student_tree.pack(fill="both", expand=True)

# ---------------- UI: FEES TAB ---------------- #
fee_student_var = tk.StringVar()
fee_month_var = tk.StringVar()
fee_year_var = tk.StringVar()
fee_amount_var = tk.StringVar()

tk.Label(fees_tab, text="Student:").pack()
tk.Entry(fees_tab, textvariable=fee_student_var).pack()

tk.Label(fees_tab, text="Month:").pack()
tk.Entry(fees_tab, textvariable=fee_month_var).pack()

tk.Label(fees_tab, text="Year:").pack()
tk.Entry(fees_tab, textvariable=fee_year_var).pack()

tk.Label(fees_tab, text="Amount:").pack()
tk.Entry(fees_tab, textvariable=fee_amount_var).pack()

tk.Button(fees_tab, text="Add Fee", command=add_fee, bg="lightblue").pack(pady=5)
tk.Button(fees_tab, text="Delete Fee", command=delete_fee, bg="lightcoral").pack(pady=5)

fees_tree = ttk.Treeview(fees_tab, columns=("ID", "Student", "Month", "Year", "Amount"), show="headings")
for col in ("ID", "Student", "Month", "Year", "Amount"):
    fees_tree.heading(col, text=col)
fees_tree.pack(fill="both", expand=True)

# ---------------- UI: REPORT TAB ---------------- #
report_chart_frame = tk.Frame(report_tab, bg="white")
report_chart_frame.pack(fill="both", expand=True)

tk.Button(report_tab, text="Show Income Chart", command=draw_income_chart, bg="lightblue").pack(pady=5)

# Initial load
refresh_batch_list()
refresh_student_list()
refresh_fees_list()

root.mainloop()
