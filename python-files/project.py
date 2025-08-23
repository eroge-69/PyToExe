import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ----------------------------
# Globals
# ----------------------------
item_vars = {}
dataframe = None
excel_path = None

# ----------------------------
# Helpers
# ----------------------------
def load_data(path=None):
    if not path:
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if path:
        df = pd.read_excel(path)
        save_last_path(path)
        return df, path
    return None, None

def save_last_path(path):
    with open("last_excel_path.json", "w") as f:
        json.dump({"path": path}, f)

def load_last_path():
    if os.path.exists("last_excel_path.json"):
        with open("last_excel_path.json", "r") as f:
            data = json.load(f)
            return data.get("path", "")
    return ""

def format_indian_number(n):
    try:
        n = float(n)
    except Exception:
        return ''
    s = f"{n:.2f}"
    int_part, dec_part = s.split('.')
    if len(int_part) <= 3:
        return f"{int_part}.{dec_part}"
    last3 = int_part[-3:]
    rest = int_part[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return f"{','.join(groups)},{last3}.{dec_part}"

# ----------------------------
# Core logic
# ----------------------------
def generate_report_table(df, party, start_date, end_date, items):
    headers = ["Sr. No.", "Date", "Vehicle No.", "Challan No.", "Ton", "Rate", "Amount"]
    required = headers + ["Party Name", "Item Name"]
    missing = [h for h in required if h not in df.columns]
    if missing:
        return None, f"Missing columns in Excel: {missing}"

    work = df.copy()
    work["Date"] = pd.to_datetime(work["Date"], format="%d/%m/%Y", errors="coerce")

    filtered = work[work["Party Name"] == party]
    filtered = filtered[(filtered["Date"] >= start_date) & (filtered["Date"] <= end_date)]

    if items:
        filtered = filtered[filtered["Item Name"].isin(items)]

    if filtered.empty:
        return [["No data for selection", '', '', '', '', '', '']], None

    table_rows = []
    grand_ton = 0.0
    grand_amt = 0.0

    for item_name in sorted(filtered["Item Name"].dropna().unique()):
        item_df = filtered[filtered["Item Name"] == item_name].sort_values("Date").copy()
        if item_df.empty:
            continue

        table_rows.append([item_name, '', '', '', '', '', ''])

        item_df.loc[:, "Sr. No."] = range(1, len(item_df) + 1)

        item_ton = float(item_df["Ton"].fillna(0).sum())
        item_amount = float(item_df["Amount"].fillna(0).sum())
        grand_ton += item_ton
        grand_amt += item_amount

        for _, r in item_df.iterrows():
            table_rows.append([
                str(int(r["Sr. No."])) if pd.notnull(r["Sr. No."]) else '',
                r["Date"].strftime("%d/%m/%Y") if pd.notnull(r["Date"]) else '',
                str(r.get("Vehicle No.", '') if pd.notnull(r.get("Vehicle No.", '')) else ''),
                str(r.get("Challan No.", '') if pd.notnull(r.get("Challan No.", '')) else ''),
                f"{float(r.get('Ton', 0) or 0):06.3f}" if pd.notnull(r.get("Ton")) else '',
                format_indian_number(r.get("Rate", '')) if pd.notnull(r.get("Rate")) else '',
                format_indian_number(r.get("Amount", '')) if pd.notnull(r.get("Amount")) else ''
            ])

        table_rows.append(['', '', '', '', f"{item_ton:06.3f}", '', format_indian_number(item_amount)])

    table_rows.append(['Total', '', '', '', f"{grand_ton:06.3f}", '', format_indian_number(grand_amt)])

    return table_rows, None

# ----------------------------
# UI callbacks
# ----------------------------
def on_generate():
    global dataframe
    if dataframe is None:
        messagebox.showerror("Error", "Please load an Excel file first.")
        return

    party = party_var.get().strip()
    selected_items = [name for name, v in item_vars.items() if v.get()]

    try:
        start_d = datetime.strptime(start_date_var.get(), "%d/%m/%Y")
        end_d = datetime.strptime(end_date_var.get(), "%d/%m/%Y")
    except Exception:
        messagebox.showerror("Error", "Please enter valid dates in dd/mm/yyyy format.")
        return

    rows, err = generate_report_table(dataframe, party, start_d, end_d, selected_items)

    tree.delete(*tree.get_children())
    if err:
        tree.insert('', 'end', values=(err, '', '', '', '', '', ''))
        return

    for idx, row in enumerate(rows):
        is_item_header = bool(row[0]) and all(str(c) == '' for c in row[1:])
        tag = 'itemrow' if is_item_header else ('evenrow' if idx % 2 == 0 else 'oddrow')
        tree.insert('', 'end', values=row, tags=(tag,))

def show_item_filter_popup():
    global item_filter_popup
    if 'item_filter_popup' in globals() and item_filter_popup is not None and tk.Toplevel.winfo_exists(item_filter_popup):
        item_filter_popup.lift()
        return

    item_filter_popup = tk.Toplevel(root)
    item_filter_popup.title("Filter Items")
    item_filter_popup.geometry("320x420")
    item_filter_popup.transient(root)
    item_filter_popup.grab_set()

    search_var = tk.StringVar()

    def update_list(*_):
        s = search_var.get().lower()
        for cb, name in checkboxes:
            (cb.pack if s in name.lower() else cb.pack_forget) (anchor='w', padx=6)

    ttk.Label(item_filter_popup, text="Search").pack(anchor='w', padx=6, pady=(8, 0))
    se = ttk.Entry(item_filter_popup, textvariable=search_var)
    se.pack(fill='x', padx=6, pady=(0, 8))
    search_var.trace_add('write', update_list)

    select_all_var = tk.BooleanVar(value=all(v.get() for v in item_vars.values()))

    def on_select_all():
        val = select_all_var.get()
        for v in item_vars.values():
            v.set(val)

    tk.Checkbutton(item_filter_popup, text="Select All", variable=select_all_var, command=on_select_all).pack(anchor='w', padx=6)

    canvas = tk.Canvas(item_filter_popup, borderwidth=0, highlightthickness=0)
    inner = ttk.Frame(canvas)
    vsb = ttk.Scrollbar(item_filter_popup, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    canvas.create_window((0, 0), window=inner, anchor='nw')

    def on_frame_configure(_):
        canvas.configure(scrollregion=canvas.bbox('all'))

    inner.bind('<Configure>', on_frame_configure)

    checkboxes = []
    for item_name, var in item_vars.items():
        cb = tk.Checkbutton(inner, text=item_name, variable=var)
        cb.pack(anchor='w', padx=6)
        checkboxes.append((cb, item_name))

    ttk.Button(item_filter_popup, text="Done", command=item_filter_popup.destroy).pack(pady=10)

def on_load(path=None):
    global dataframe, item_vars, excel_path
    dataframe, excel_path = load_data(path)
    if dataframe is not None:
        parties = sorted(dataframe['Party Name'].dropna().unique())
        party_dropdown['values'] = parties
        if parties:
            party_var.set(parties[0])

        refresh_items_for_party()

        item_filter_btn['state'] = 'normal'
        status_var.set(f"Loaded: {os.path.basename(excel_path)}")
        messagebox.showinfo("Success", "Data loaded successfully.")

def on_refresh():
    if excel_path:
        on_load(excel_path)
    else:
        messagebox.showerror("Error", "No previous Excel file path found.")

def refresh_items_for_party(*_):
    global item_vars
    if dataframe is None:
        return
    party = party_var.get().strip()
    if not party:
        return
    items = sorted(dataframe.loc[dataframe["Party Name"] == party, "Item Name"].dropna().unique())
    item_vars.clear()
    for item in items:
        item_vars[item] = tk.BooleanVar(value=True)

# ----------------------------
# PDF
# ----------------------------
def build_pdf_rows_from_tree():
    rows = []
    for iid in tree.get_children():
        vals = list(tree.item(iid)['values'])
        while len(vals) < 7:
            vals.append('')
        rows.append(vals[:7])
    return rows

def export_report_to_pdf():
    on_generate()
    table_rows = build_pdf_rows_from_tree()

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elements = []

    heading = Paragraph("<para align='center'><font size=16><b>Statement</b></font></para>", styles['Title'])
    elements.append(heading)
    elements.append(Spacer(1, 8))

    # Full width for info tables
    table_width = sum([55, 70, 110, 80, 70, 75, 95])

    drange = f"{start_date_var.get()} to {end_date_var.get()}"
    dr_table = Table([[f"{drange}"]], colWidths=[table_width])
    dr_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E3F2FD'))
    ]))
    elements.append(dr_table)

    pname = party_var.get()
    edate = end_date_var.get()
    info_tbl = Table([["Party Name: " + pname, "Date: " + edate]], colWidths=[0.7*table_width, 0.3*table_width])
    info_tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E3F2FD'))
    ]))
    elements.append(info_tbl)
    elements.append(Spacer(1, 10))

    headers = ["Sr. No.", "Date", "Vehicle No.", "Challan No.", "Ton", "Rate", "Amount"]
    data = [headers] + table_rows
    col_widths = [55, 70, 110, 80, 70, 75, 95]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)

    header_bg = colors.HexColor('#1E88E5')
    header_fg = colors.whitesmoke

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), header_fg),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ])

    last_row_index = len(data) - 1
    for i in range(1, len(data)):
        row = data[i]
        is_item_header = bool(row[0]) and all(str(x) == '' for x in row[1:])
        is_item_total = (row[0] == '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] != '' and row[6] != '' and i != last_row_index)

        if is_item_header:
            style.add('SPAN', (0, i), (-1, i))
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF59D'))
            style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
            style.add('ALIGN', (0, i), (-1, i), 'CENTER')
        elif is_item_total:
            style.add('SPAN', (0, i), (3, i))
            style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E1F5FE'))
            style.add('ALIGN', (0, i), (3, i), 'CENTER')
        elif i == last_row_index:
            data[i][0] = 'Total'
            data[i][1] = ''
            data[i][2] = ''
            data[i][3] = ''
            style.add('SPAN', (0, i), (3, i))
            style.add('BACKGROUND', (0, i), (-1, i), header_bg)
            style.add('TEXTCOLOR', (0, i), (-1, i), header_fg)
            style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
            style.add('ALIGN', (0, i), (-1, i), 'CENTER')

    tbl.setStyle(style)
    elements.append(tbl)
    doc.build(elements)

# ----------------------------
# UI
# ----------------------------
root = tk.Tk()
root.title("Trip Report Generator")
root.geometry("1100x720")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6, background="#4CAF50", foreground="white")
style.map("TButton", background=[("active", "#43A047")])
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("Treeview", font=("Segoe UI", 11), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#1E88E5", foreground="white")
style.configure("TCombobox", font=("Segoe UI", 12))
style.configure("DateEntry", font=("Segoe UI", 12))

root.configure(bg="#E3F2FD")

ttk.Label(root, text="Trip Report Generator", font=("Segoe UI", 22, "bold"), background="#E3F2FD", foreground="#0D47A1").pack(pady=(10, 6))

top_btn_frame = ttk.Frame(root, padding=8)
top_btn_frame.pack(fill="x", padx=10)

ttk.Button(top_btn_frame, text="Load Excel Data", command=on_load).pack(side="left", padx=4)
ttk.Button(top_btn_frame, text="Refresh", command=lambda: on_load(excel_path) if excel_path else on_refresh()).pack(side="left", padx=4)

ttk.Label(top_btn_frame, text="Party:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=6)
party_var = tk.StringVar()
party_dropdown = ttk.Combobox(top_btn_frame, textvariable=party_var, state="readonly", width=25, font=("Segoe UI", 12))
party_dropdown.pack(side="left", padx=6)
party_dropdown.bind("<<ComboboxSelected>>", refresh_items_for_party)

item_filter_btn = ttk.Button(top_btn_frame, text="Filter Items", command=show_item_filter_popup, state="disabled")
item_filter_btn.pack(side="left", padx=6)

ttk.Label(top_btn_frame, text="Start Date:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=6)
start_date_var = tk.StringVar()
start_date_entry = DateEntry(top_btn_frame, textvariable=start_date_var, date_pattern="dd/mm/yyyy", width=15, font=("Segoe UI", 12))
start_date_entry.pack(side="left", padx=6)

ttk.Label(top_btn_frame, text="End Date:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=6)
end_date_var = tk.StringVar()
end_date_entry = DateEntry(top_btn_frame, textvariable=end_date_var, date_pattern="dd/mm/yyyy", width=15, font=("Segoe UI", 12))
end_date_entry.pack(side="left", padx=6)

action_frame = ttk.Frame(root, padding=8)
action_frame.pack(fill="x", padx=10, pady=(0, 6))
ttk.Button(action_frame, text="Generate Report", command=on_generate).pack(side="left", padx=6)
ttk.Button(action_frame, text="Export PDF", command=export_report_to_pdf).pack(side="left", padx=6)

output_frame = ttk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Sr. No.", "Date", "Vehicle No.", "Challan No.", "Ton", "Rate", "Amount")
tree = ttk.Treeview(output_frame, columns=columns, show="headings")
tree.pack(fill="both", expand=True, side="left")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")

tree.tag_configure('itemrow', background="#FFF9C4", font=("Segoe UI", 11, "bold"))
tree.tag_configure('evenrow', background="white")
tree.tag_configure('oddrow', background="#F1F8E9")

tree_scroll_y = ttk.Scrollbar(output_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=tree_scroll_y.set)
tree_scroll_y.pack(side="right", fill="y")

status_var = tk.StringVar(value="No file loaded")
status_bar = ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w", padding=4)
status_bar.pack(fill="x", side="bottom")

last = load_last_path()
if last:
    on_load(last)

root.mainloop()
