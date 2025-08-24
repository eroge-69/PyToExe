#!/usr/bin/env python3
"""
court_tracker.py
Trial Court Listing Tracker - single-file Windows-friendly Tkinter app.

Dependencies:
    pip install tkcalendar reportlab

Run:
    python court_tracker.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
import sqlite3
from datetime import datetime, timedelta, date
import csv
import os
import webbrowser

# PDF library
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------- CONFIG ----------
DB_PATH = "cases.db"
DATE_FMT = "%Y-%m-%d"

# ---------- DB SETUP ----------
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_name TEXT NOT NULL,
                case_number TEXT NOT NULL,
                court_name TEXT NOT NULL,
                next_date TEXT NOT NULL
            )''')
conn.commit()

# ---------- HELPERS ----------
def parse_date(s: str) -> date:
    return datetime.strptime(s, DATE_FMT).date()

def today() -> date:
    return date.today()

def next7() -> date:
    return today() + timedelta(days=7)

def fetch_cases(filters=None, order_by=("next_date", "ASC")):
    where, params = [], []
    if filters:
        if filters.get("case_number"):
            where.append("LOWER(case_number) LIKE ?"); params.append("%"+filters["case_number"].lower()+"%")
        if filters.get("court_name"):
            where.append("LOWER(court_name) LIKE ?"); params.append("%"+filters["court_name"].lower()+"%")
        if filters.get("from_date"):
            where.append("next_date >= ?"); params.append(filters["from_date"])
        if filters.get("to_date"):
            where.append("next_date <= ?"); params.append(filters["to_date"])
    sql = "SELECT id, case_name, case_number, court_name, next_date FROM cases"
    if where:
        sql += " WHERE " + " AND ".join(where)
    col, dirn = order_by
    sql += f" ORDER BY {col} {dirn}"
    c.execute(sql, params)
    return c.fetchall()

def insert_case(case_name, case_number, court_name, next_date_str):
    parse_date(next_date_str)  # validate
    c.execute("INSERT INTO cases (case_name, case_number, court_name, next_date) VALUES (?, ?, ?, ?)",
              (case_name, case_number, court_name, next_date_str))
    conn.commit()

def update_case_date(case_id: int, new_date_str: str):
    parse_date(new_date_str)
    c.execute("UPDATE cases SET next_date=? WHERE id=?", (new_date_str, case_id))
    conn.commit()

def delete_case(case_id: int):
    c.execute("DELETE FROM cases WHERE id=?", (case_id,))
    conn.commit()

# ---------- UI ----------
root = tk.Tk()
root.title("Trial Court Listing Tracker")
# set window icon if icon.ico exists (safe fallback)
if os.path.exists("icon.ico"):
    try:
        root.iconbitmap("icon.ico")
    except Exception:
        pass

root.geometry("1150x720")

notebook = ttk.Notebook(root)
tab_cases = ttk.Frame(notebook)
tab_calendar = ttk.Frame(notebook)
notebook.add(tab_cases, text="Cases")
notebook.add(tab_calendar, text="Calendar")
notebook.pack(fill="both", expand=True)

# ---------- CASES TAB ----------
# Add form
frm_add = tk.LabelFrame(tab_cases, text="Add New Case")
frm_add.pack(fill="x", padx=10, pady=8)

tk.Label(frm_add, text="Case Name").grid(row=0, column=0, padx=6, pady=6, sticky="e")
ent_name = tk.Entry(frm_add, width=34); ent_name.grid(row=0, column=1, padx=6, pady=6)

tk.Label(frm_add, text="Case Number").grid(row=0, column=2, padx=6, pady=6, sticky="e")
ent_number = tk.Entry(frm_add, width=20); ent_number.grid(row=0, column=3, padx=6, pady=6)

tk.Label(frm_add, text="Court").grid(row=0, column=4, padx=6, pady=6, sticky="e")
ent_court = tk.Entry(frm_add, width=20); ent_court.grid(row=0, column=5, padx=6, pady=6)

tk.Label(frm_add, text="Next Date (YYYY-MM-DD)").grid(row=0, column=6, padx=6, pady=6, sticky="e")
ent_date = tk.Entry(frm_add, width=14); ent_date.grid(row=0, column=7, padx=6, pady=6)

def on_add():
    name = ent_name.get().strip()
    number = ent_number.get().strip()
    court = ent_court.get().strip()
    nxt = ent_date.get().strip()
    if not all([name, number, court, nxt]):
        messagebox.showerror("Missing", "Please fill all fields."); return
    try:
        insert_case(name, number, court, nxt)
    except Exception as e:
        messagebox.showerror("Error", str(e)); return
    ent_name.delete(0, tk.END); ent_number.delete(0, tk.END)
    ent_court.delete(0, tk.END); ent_date.delete(0, tk.END)
    refresh_table()
    refresh_calendar()

tk.Button(frm_add, text="Add Case", command=on_add).grid(row=0, column=8, padx=6, pady=6)

# Filters
frm_filter = tk.LabelFrame(tab_cases, text="Search & Filter")
frm_filter.pack(fill="x", padx=10, pady=8)

tk.Label(frm_filter, text="Case Number").grid(row=0, column=0, padx=6, pady=6, sticky="e")
flt_number = tk.Entry(frm_filter, width=20); flt_number.grid(row=0, column=1, padx=6, pady=6)

tk.Label(frm_filter, text="Court").grid(row=0, column=2, padx=6, pady=6, sticky="e")
flt_court = tk.Entry(frm_filter, width=20); flt_court.grid(row=0, column=3, padx=6, pady=6)

tk.Label(frm_filter, text="From (YYYY-MM-DD)").grid(row=0, column=4, padx=6, pady=6, sticky="e")
flt_from = tk.Entry(frm_filter, width=14); flt_from.grid(row=0, column=5, padx=6, pady=6)

tk.Label(frm_filter, text="To (YYYY-MM-DD)").grid(row=0, column=6, padx=6, pady=6, sticky="e")
flt_to = tk.Entry(frm_filter, width=14); flt_to.grid(row=0, column=7, padx=6, pady=6)

def gather_filters_or_none():
    f = {}
    if flt_number.get().strip(): f["case_number"] = flt_number.get().strip()
    if flt_court.get().strip():  f["court_name"]  = flt_court.get().strip()
    if flt_from.get().strip():
        try: parse_date(flt_from.get().strip()); f["from_date"] = flt_from.get().strip()
        except Exception as e: messagebox.showerror("Error", f"From date: {e}"); return None
    if flt_to.get().strip():
        try: parse_date(flt_to.get().strip()); f["to_date"] = flt_to.get().strip()
        except Exception as e: messagebox.showerror("Error", f"To date: {e}"); return None
    return f

def apply_filters():
    f = gather_filters_or_none()
    if f is None: return
    refresh_table(f)

def clear_filters():
    flt_number.delete(0, tk.END); flt_court.delete(0, tk.END)
    flt_from.delete(0, tk.END); flt_to.delete(0, tk.END)
    refresh_table()

tk.Button(frm_filter, text="Filter", command=apply_filters).grid(row=0, column=8, padx=6, pady=6)
tk.Button(frm_filter, text="Clear", command=clear_filters).grid(row=0, column=9, padx=6, pady=6)

# Table
frm_table = tk.Frame(tab_cases); frm_table.pack(fill="both", expand=True, padx=10, pady=6)

columns = ("id", "case_name", "case_number", "court_name", "next_date")
headers = {"id":"ID","case_name":"Case Name","case_number":"Case Number","court_name":"Court","next_date":"Next Date"}

tree = ttk.Treeview(frm_table, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=headers[col], command=lambda c=col: sort_by_column(c))
    tree.column(col, anchor="w", width=160)
tree.column("id", width=60, anchor="center")
tree.pack(side="left", fill="both", expand=True)

scroll_y = ttk.Scrollbar(frm_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")

# Row highlighting tags
tree.tag_configure('upcoming', background='#FFF7CC')  # light yellow
tree.tag_configure('overdue',  background='#FFD6D6')  # light red

# Actions
frm_actions = tk.Frame(tab_cases); frm_actions.pack(fill="x", padx=10, pady=8)
tk.Label(frm_actions, text="New Date (YYYY-MM-DD):").pack(side="left", padx=6)
ent_update = tk.Entry(frm_actions, width=14); ent_update.pack(side="left", padx=6)

def on_update():
    sel = tree.selection()
    if not sel: messagebox.showerror("Select", "Please select a case."); return
    newd = ent_update.get().strip()
    try: parse_date(newd)
    except Exception as e: messagebox.showerror("Error", str(e)); return
    case_id = tree.item(sel[0])["values"][0]
    update_case_date(case_id, newd)
    ent_update.delete(0, tk.END)
    refresh_table()
    refresh_calendar()

def on_delete():
    sel = tree.selection()
    if not sel: messagebox.showerror("Select", "Please select a case to delete."); return
    case_id = tree.item(sel[0])["values"][0]
    if messagebox.askyesno("Confirm Delete", f"Delete case ID {case_id}?"):
        delete_case(case_id)
        refresh_table()
        refresh_calendar()

def on_export_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv",
                                        filetypes=[("CSV", "*.csv")],
                                        title="Export to CSV")
    if not path: return
    rows = fetch_cases(gather_filters_or_none() or {}, (sort_state["column"], sort_state["direction"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow([headers[c] for c in columns])
        for r in rows: w.writerow(r)
    messagebox.showinfo("Export", f"Exported {len(rows)} rows to:\n{path}")

def build_pdf(rows, filepath):
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph("Trial Court Listing Tracker", styles['Title'])
    elements.append(title)
    elements.append(Paragraph(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    data = [["ID", "Case Name", "Case Number", "Court", "Next Date"]]
    for r in rows:
        # r is tuple (id, name, number, court, next_date)
        data.append([str(r[0]), r[1], r[2], r[3], r[4]])
    table = Table(data, colWidths=[40, 200, 100, 140, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4B4B4B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(table)
    doc.build(elements)

def on_export_pdf(choice="all"):
    path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                        filetypes=[("PDF", "*.pdf")],
                                        title="Export to PDF")
    if not path: return
    all_rows = fetch_cases(gather_filters_or_none() or {}, (sort_state["column"], sort_state["direction"]))
    tdy = today()
    if choice == "all":
        rows = all_rows
    elif choice == "upcoming":
        rows = [r for r in all_rows if tdy <= parse_date(r[4]) <= next7()]
    elif choice == "overdue":
        rows = [r for r in all_rows if parse_date(r[4]) < tdy]
    else:
        rows = all_rows
    try:
        build_pdf(rows, path)
        messagebox.showinfo("Export", f"PDF exported to:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF: {e}")

tk.Button(frm_actions, text="Update Date", command=on_update).pack(side="left", padx=6)
tk.Button(frm_actions, text="Delete Case", command=on_delete).pack(side="left", padx=6)
tk.Button(frm_actions, text="Export CSV", command=on_export_csv).pack(side="left", padx=6)
tk.Button(frm_actions, text="Export All to PDF", command=lambda: on_export_pdf("all")).pack(side="left", padx=6)
tk.Button(frm_actions, text="Export Upcoming (7d) to PDF", command=lambda: on_export_pdf("upcoming")).pack(side="left", padx=6)
tk.Button(frm_actions, text="Export Overdue to PDF", command=lambda: on_export_pdf("overdue")).pack(side="left", padx=6)

# Sorting state
sort_state = {"column": "next_date", "direction": "ASC"}

def refresh_table(filters=None):
    for iid in tree.get_children(): tree.delete(iid)
    rows = fetch_cases(filters or gather_filters_or_none() or {}, (sort_state["column"], sort_state["direction"]))
    tdy, nxt = today(), next7()
    for r in rows:
        rid, name, num, court, nd = r
        tag = ()
        try:
            d = parse_date(nd)
            if d < tdy: tag = ('overdue',)
            elif tdy <= d <= nxt: tag = ('upcoming',)
        except Exception:
            pass
        tree.insert("", "end", values=r, tags=tag)

def sort_by_column(colname):
    if sort_state["column"] == colname:
        sort_state["direction"] = "DESC" if sort_state["direction"] == "ASC" else "ASC"
    else:
        sort_state["column"] = colname
        sort_state["direction"] = "ASC"
    refresh_table()

# ---------- CALENDAR TAB ----------
top_bar = tk.Frame(tab_calendar); top_bar.pack(fill="x", padx=10, pady=8)
lbl_info = tk.Label(top_bar, text="Click a date to show cases scheduled on that day.")
lbl_info.pack(side="left")

cal_frame = tk.Frame(tab_calendar); cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
calendar = Calendar(cal_frame, selectmode="day", date_pattern=DATE_FMT)
calendar.pack(side="left", fill="both", expand=True)

right_panel = tk.Frame(cal_frame); right_panel.pack(side="left", fill="both", expand=True, padx=10)
tk.Label(right_panel, text="Cases on selected date:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

cal_tree = ttk.Treeview(right_panel, columns=("id","case_name","case_number","court_name","next_date"), show="headings")
for col in ("id","case_name","case_number","court_name","next_date"):
    cal_tree.heading(col, text=headers[col])
    cal_tree.column(col, width=150 if col!="case_name" else 240, anchor="w")
cal_tree.column("id", width=60, anchor="center")
cal_tree.pack(fill="both", expand=True)

def calendar_date_changed(_event=None):
    sel = calendar.get_date()  # string YYYY-MM-DD
    for iid in cal_tree.get_children(): cal_tree.delete(iid)
    rows = fetch_cases({"from_date": sel, "to_date": sel})
    for r in rows: cal_tree.insert("", "end", values=r)

calendar.bind("<<CalendarSelected>>", calendar_date_changed)

def refresh_calendar():
    # clear existing events
    for ev in calendar.get_calevents():
        calendar.calevent_remove(ev)
    tdy, nxt = today(), next7()
    rows = fetch_cases()
    for rid, name, num, court, nd in rows:
        try:
            d = parse_date(nd)
        except Exception:
            continue
        tag = "future"
        if d < tdy: tag = "overdue"
        elif tdy <= d <= nxt: tag = "upcoming"
        title = f"{name} ({num})"
        calendar.calevent_create(d, title, tag)
    # set tag colors
    calendar.tag_config("overdue", background="#FFB3B3", foreground="black")
    calendar.tag_config("upcoming", background="#FFEAA7", foreground="black")
    calendar.tag_config("future", background="#C8F7C5", foreground="black")
    # update right panel for currently selected date
    calendar_date_changed()

# ---------- INITIAL FILL ----------
def initial_fill():
    refresh_table()
    refresh_calendar()

initial_fill()

# ---------- MAINLOOP ----------
root.mainloop()
