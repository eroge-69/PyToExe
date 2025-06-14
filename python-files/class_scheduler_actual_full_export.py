
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime

columns = ["SEMESTER", "COURSE", "YEAR", "SUBJECT DESCRIPTIONS", "ROOM",
           "DAY", "START TIME", "END TIME", "TYPE", "FACULTY", "WEC", "FEC"]
schedule_df = pd.DataFrame(columns=columns)
selected_item_id = None

def parse_time(t): 
    try: return datetime.strptime(t, "%H:%M")
    except: return None

def time_overlap(s1, e1, s2, e2): return s1 < e2 and s2 < e1

def check_conflicts(entry, exclude=None):
    global schedule_df
    day, room, faculty = entry['DAY'], entry['ROOM'], entry['FACULTY']
    start, end = parse_time(entry['START TIME']), parse_time(entry['END TIME'])
    if not start or not end: return "Invalid time format! Use HH:MM."
    same_day = schedule_df[schedule_df['DAY'] == day]
    if exclude is not None: same_day = same_day.drop(index=exclude)
    for i, row in same_day.iterrows():
        es, ee = parse_time(row['START TIME']), parse_time(row['END TIME'])
        if row['ROOM'] == room and time_overlap(start, end, es, ee):
            return f"Room conflict on {day} ({room})"
        if row['FACULTY'] == faculty and time_overlap(start, end, es, ee):
            return f"Faculty conflict on {day} ({faculty})"
    return None

def collect(): return {col: widgets[col].get() if col in widgets else entries[col].get() for col in columns}

def clear():
    for col in columns:
        if col in widgets: widgets[col].set('')
        else: entries[col].delete(0, tk.END)
    search_entry.delete(0, tk.END)
    disable_fields()
    update_table()

def enable_fields():
    for widget in widgets.values():
        widget_widget(widget).config(state='readonly')
    for entry in entries.values():
        entry.config(state='normal')

def disable_fields():
    for widget in widgets.values():
        widget_widget(widget).config(state='disabled')
    for entry in entries.values():
        entry.config(state='disabled')

def widget_widget(widget):
    for w in root.winfo_children():
        if isinstance(w, ttk.Combobox) and w.cget("textvariable") == str(widget):
            return w
    return None

def add_schedule():
    global schedule_df
    entry = collect()
    conflict = check_conflicts(entry)
    if conflict: messagebox.showerror("Conflict", conflict); return
    schedule_df.loc[len(schedule_df)] = entry
    schedule_df.reset_index(drop=True, inplace=True)
    update_table(); clear()

def update_table():
    global schedule_df
    schedule_df.reset_index(drop=True, inplace=True)
    table.delete(*table.get_children())
    for idx, row in schedule_df.iterrows():
        table.insert('', 'end', iid=str(idx), values=list(row))

def delete_schedule():
    global schedule_df
    sel = table.focus()
    if not sel: messagebox.showwarning("Warning", "No record selected."); return
    schedule_df.drop(index=int(sel), inplace=True)
    schedule_df.reset_index(drop=True, inplace=True)
    update_table(); clear()

def select_row(e):
    global selected_item_id
    sel = table.focus()
    if not sel: return
    selected_item_id = int(sel)
    row = schedule_df.loc[selected_item_id]
    for col in columns:
        if col in widgets: widgets[col].set(row[col])
        else: entries[col].delete(0, tk.END); entries[col].insert(0, row[col])
    disable_fields()

def edit_record():
    if selected_item_id is None:
        messagebox.showwarning("Warning", "Select a record first.")
        return
    enable_fields()

def save_changes():
    global schedule_df
    if selected_item_id is None:
        messagebox.showwarning("Warning", "No record selected."); return
    entry = collect()
    conflict = check_conflicts(entry, exclude=selected_item_id)
    if conflict: messagebox.showerror("Conflict", conflict); return
    for col in columns:
        schedule_df.at[selected_item_id, col] = entry[col]
    update_table(); clear()

def save_schedule():
    global schedule_df
    f = filedialog.asksaveasfilename(defaultextension=".csv")
    if f: schedule_df.to_csv(f, index=False); messagebox.showinfo("Success", "Schedule saved.")

def load_schedule():
    global schedule_df
    f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if f: schedule_df = pd.read_csv(f)
    schedule_df.reset_index(drop=True, inplace=True)
    update_table(); clear()

def print_schedule():
    global schedule_df
    rpt = "SCHEDULE REPORT\n\n" + schedule_df.to_string(index=False)
    f = filedialog.asksaveasfilename(defaultextension=".txt")
    if f: open(f, 'w').write(rpt); messagebox.showinfo("Success", "Report saved.")

def search_schedule():
    global schedule_df
    query = search_entry.get().strip().lower()
    filtered = schedule_df[
        schedule_df['COURSE'].str.lower().str.contains(query) |
        schedule_df['FACULTY'].str.lower().str.contains(query)
    ]
    table.delete(*table.get_children())
    for idx, row in filtered.iterrows():
        table.insert('', 'end', iid=str(idx), values=list(row))

def faculty_load_summary():
    global schedule_df
    if schedule_df.empty:
        messagebox.showinfo("No data", "No schedule loaded!")
        return
    try:
        schedule_df["WEC"] = pd.to_numeric(schedule_df["WEC"], errors='coerce').fillna(0)
        schedule_df["FEC"] = pd.to_numeric(schedule_df["FEC"], errors='coerce').fillna(0)
        schedule_df["TOTAL"] = schedule_df["WEC"] + schedule_df["FEC"]
        summary = schedule_df.groupby("FACULTY")["TOTAL"].sum().reset_index()
        report = "TOTAL EQUIVALENT CREDITS\n\n"
        for idx, row in summary.iterrows():
            report += f"{row['FACULTY']}: {row['TOTAL']} Units\n"
        messagebox.showinfo("FACULTY CREDITS", report)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Layout
root = tk.Tk()
root.title("BUP - Technology Department Class Scheduler")
root.geometry("1400x800")

semester_opts = ["1st", "2nd", "SUMMER"]
year_opts = ["1st", "2nd", "3rd", "4th"]
type_opts = ["Lecture", "Laboratory"]
day_opts = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

widgets, entries = {}, {}

for i in range(8): root.grid_rowconfigure(i, pad=4)

# Search Bar
tk.Label(root, text="Search Course/Faculty:").grid(row=0, column=0, sticky="e", padx=(20, 5), pady=3)
search_entry = tk.Entry(root, width=40)
search_entry.grid(row=0, column=1, padx=5, pady=3, sticky="w", columnspan=2)
tk.Button(root, text=" Search ", width=23, command=search_schedule).grid(row=0, column=2, padx=(10, 5), pady=3, sticky="w")

# Left Fields
left_labels = ["Semester", "Course", "Year", "Subject", "Room", "Day", "Start Time (HH:MM)", "End Time (HH:MM)"]
left_fields = ["SEMESTER", "COURSE", "YEAR", "SUBJECT DESCRIPTIONS", "ROOM", "DAY", "START TIME", "END TIME"]

for i, label in enumerate(left_labels):
    row_index = i+1
    tk.Label(root, text=label + ":").grid(row=row_index, column=0, sticky="e", padx=(20, 5), pady=3)
    field = left_fields[i]
    if field == "SEMESTER":
        var = tk.StringVar(); combo = ttk.Combobox(root, textvariable=var, values=semester_opts, width=25, state="disabled")
        combo.grid(row=row_index, column=1, padx=5, pady=3, sticky="w"); widgets[field] = var
    elif field == "YEAR":
        var = tk.StringVar(); combo = ttk.Combobox(root, textvariable=var, values=year_opts, width=25, state="disabled")
        combo.grid(row=row_index, column=1, padx=5, pady=3, sticky="w"); widgets[field] = var
    elif field == "DAY":
        var = tk.StringVar(); combo = ttk.Combobox(root, textvariable=var, values=day_opts, width=25, state="disabled")
        combo.grid(row=row_index, column=1, padx=5, pady=3, sticky="w"); widgets[field] = var
    else:
        ent = tk.Entry(root, width=28, state="disabled")
        ent.grid(row=row_index, column=1, padx=5, pady=3, sticky="w"); entries[field] = ent

# Right Fields
right_labels = ["Type", "Faculty", "WEC", "FEC"]
right_fields = ["TYPE", "FACULTY", "WEC", "FEC"]

for i, label in enumerate(right_labels):
    tk.Label(root, text=label + ":").grid(row=i+1, column=2, sticky="e", padx=(40, 5), pady=3)
    field = right_fields[i]
    if field == "TYPE":
        var = tk.StringVar(); combo = ttk.Combobox(root, textvariable=var, values=type_opts, width=25, state="disabled")
        combo.grid(row=i+1, column=3, padx=5, pady=3, sticky="w"); widgets[field] = var
    else:
        ent = tk.Entry(root, width=28, state="disabled")
        ent.grid(row=i+1, column=3, padx=5, pady=3, sticky="w"); entries[field] = ent

# Buttons
btns = [
    (" Add ", add_schedule), (" Edit ", edit_record), (" Update ", save_changes), (" Delete ", delete_schedule),
    (" Save ", save_schedule), (" Load ", load_schedule), (" Print Report ", print_schedule),
    (" Faculty Load ", faculty_load_summary), (" Clear ", clear)
]

for i, (txt, cmd) in enumerate(btns):
    tk.Button(root, text=txt, width=15, command=cmd).grid(row=i+1, column=4, padx=(40, 20), pady=8, sticky="w")

# Table
table = ttk.Treeview(root, columns=columns, show='headings', height=12)
for col in columns: table.heading(col, text=col); table.column(col, width=100)
table.grid(row=12, column=0, columnspan=5, padx=10, pady=20, sticky="nsew")
table.bind("<<TreeviewSelect>>", select_row)

root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, minsize=200)
root.grid_rowconfigure(12, weight=1)

disable_fields()
root.mainloop()
