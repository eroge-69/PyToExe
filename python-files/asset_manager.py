import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import re
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas
import barcode
from barcode.writer import ImageWriter
import cv2
from pyzbar.pyzbar import decode
import numpy as np

APP_TITLE = "Company Asset Management"
DB_PATH = "assets.db"
BARCODES_DIR = "barcodes"

# Ensure folders exist
os.makedirs(BARCODES_DIR, exist_ok=True)

# ---------------------- Database ----------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    serial_number TEXT,
    location TEXT,
    assigned_to TEXT,
    status TEXT,
    asset_code TEXT UNIQUE
)
""")
conn.commit()

# ---------------------- Helpers ----------------------
def next_asset_index_for_category(category: str) -> int:
    """Return next sequential index based on existing asset_code entries per category."""
    cat = category.strip().lower()
    if cat == "pc":
        like = "BSBG-PC-%"
    elif cat == "laptop":
        like = "BSBG-LT-%"
    else:
        like = "BSBG-OT-%"
    cursor.execute("SELECT asset_code FROM assets WHERE asset_code LIKE ? ORDER BY id ASC", (like,))
    codes = [row[0] for row in cursor.fetchall()]
    max_idx = 0
    for c in codes:
        m = re.search(r"(\d+)$", c or "")
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1

def generate_asset_code(category: str) -> str:
    prefix = "BSBG"
    cat = (category or "").strip().lower()
    if cat == "pc":
        code_prefix = f"{prefix}-PC-"
    elif cat == "laptop":
        code_prefix = f"{prefix}-LT-"
    else:
        code_prefix = f"{prefix}-OT-"
    idx = next_asset_index_for_category(category)
    return f"{code_prefix}{idx:03d}"

def create_barcode(code: str) -> str:
    """Create Code128 barcode PNG for the given code and return path."""
    filename_no_ext = os.path.join(BARCODES_DIR, code)
    ean = barcode.get("code128", code, writer=ImageWriter())
    # python-barcode appends proper .png extension
    saved_path = ean.save(filename_no_ext)  # returns full path without needing .png here
    # Normalize to .png path
    if not saved_path.lower().endswith(".png"):
        saved_path = filename_no_ext + ".png"
    return saved_path

# ---------------------- CRUD Functions ----------------------
def add_asset():
    if not name_var.get().strip() or not category_var.get().strip():
        messagebox.showwarning("Input Error", "Name and Category are required!")
        return
    code = generate_asset_code(category_var.get())
    try:
        cursor.execute("""INSERT INTO assets
            (name, category, serial_number, location, assigned_to, status, asset_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name_var.get().strip(), category_var.get().strip(), serial_var.get().strip(),
             location_var.get().strip(), assigned_var.get().strip(), status_var.get().strip(), code))
        conn.commit()
        path = create_barcode(code)
        load_assets()
        clear_fields()
        messagebox.showinfo("Asset Added", f"Asset code: {code}\nBarcode saved: {path}")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Duplicate asset code! Try again.")

def load_assets(search_text: str = ""):
    for row in tree.get_children():
        tree.delete(row)
    if search_text:
        like = f"%{search_text}%"
        cursor.execute("""SELECT * FROM assets
                          WHERE name LIKE ? OR assigned_to LIKE ? OR asset_code LIKE ?
                          ORDER BY id DESC""", (like, like, like))
    else:
        cursor.execute("SELECT * FROM assets ORDER BY id DESC")
    for asset in cursor.fetchall():
        tree.insert("", "end", values=asset)

def delete_asset():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Delete Error", "Select an asset to delete!")
        return
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected asset?"):
        return
    asset_id = tree.item(selected[0])['values'][0]
    cursor.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    conn.commit()
    load_assets()

def edit_asset():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Edit Error", "Select an asset to edit!")
        return
    asset = tree.item(selected[0])['values']
    update_fields(asset)

def update_fields(asset):
    clear_fields()
    asset_id_var.set(asset[0])
    name_var.set(asset[1])
    category_var.set(asset[2])
    serial_var.set(asset[3])
    location_var.set(asset[4])
    assigned_var.set(asset[5])
    status_var.set(asset[6])
    asset_code_var.set(asset[7])

def update_asset():
    if not asset_id_var.get():
        messagebox.showwarning("Update Error", "No asset selected!")
        return
    cursor.execute("""UPDATE assets
                      SET name=?, category=?, serial_number=?, location=?, assigned_to=?, status=?
                      WHERE id=?""",
                   (name_var.get().strip(), category_var.get().strip(), serial_var.get().strip(),
                    location_var.get().strip(), assigned_var.get().strip(), status_var.get().strip(),
                    asset_id_var.get()))
    conn.commit()
    load_assets()
    clear_fields()

def search_assets():
    load_assets(search_var.get().strip())

def scan_asset():
    code = scan_var.get().strip()
    if not code:
        messagebox.showwarning("Scan Error", "Enter or scan an asset code!")
        return
    load_assets(code)

# ---------------------- Export ----------------------
def export_excel():
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel Files", "*.xlsx")],
                                            title="Save Excel Report")
    if not filepath:
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Assets"
    headers = ["ID", "Name", "Category", "Serial Number", "Location", "Assigned To", "Status", "Asset Code"]
    ws.append(headers)
    cursor.execute("SELECT * FROM assets ORDER BY id ASC")
    for row in cursor.fetchall():
        ws.append(row)
    wb.save(filepath)
    messagebox.showinfo("Export Successful", f"Data exported to {filepath}")

def export_pdf():
    filepath = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            filetypes=[("PDF Files", "*.pdf")],
                                            title="Save PDF Report")
    if not filepath:
        return
    c = pdfcanvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(180, height - 40, "Company Asset Report")
    c.setFont("Helvetica", 9)

    cursor.execute("SELECT * FROM assets ORDER BY id ASC")
    rows = cursor.fetchall()
    x, y = 30, height - 80
    headers = ["ID", "Name", "Category", "Serial No.", "Location", "Assigned To", "Status", "Asset Code"]
    c.drawString(x, y, " | ".join(headers))
    y -= 16
    for row in rows:
        line = " | ".join(str(item) for item in row)
        c.drawString(x, y, line[:1100])  # safety truncation
        y -= 14
        if y < 40:  # New page if needed
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 40
    c.save()
    messagebox.showinfo("Export Successful", f"Data exported to {filepath}")

# ---------------------- Camera Scan ----------------------
def camera_scan():
    cap = cv2.VideoCapture(0)  # default camera
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Could not access the camera.")
        return
    messagebox.showinfo("Camera Scan", "A camera window will open.\nPoint to a barcode. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect barcodes
        found_code = None
        for b in decode(frame):
            code = b.data.decode("utf-8")
            # Draw polygon
            pts = b.polygon
            pts = [(pt.x, pt.y) for pt in pts]
            if len(pts) >= 3:
                cv2.polylines(frame, [np.array(pts, np.int32)], True, (0, 255, 0), 2)
            cv2.putText(frame, code, (b.rect.left, max(0, b.rect.top - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            found_code = code

        cv2.imshow("Barcode Scanner", frame)
        if found_code:
            scan_var.set(found_code)
            load_assets(found_code)
            cap.release()
            cv2.destroyAllWindows()
            return

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------------- UI ----------------------
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1200x720")

asset_id_var = tk.StringVar()
name_var = tk.StringVar()
category_var = tk.StringVar()
serial_var = tk.StringVar()
location_var = tk.StringVar()
assigned_var = tk.StringVar()
status_var = tk.StringVar()
asset_code_var = tk.StringVar()
search_var = tk.StringVar()
scan_var = tk.StringVar()

# Top Title
title = tk.Label(root, text=APP_TITLE, font=("Segoe UI", 16, "bold"))
title.pack(pady=8)

# Input Frame
frame = tk.Frame(root)
frame.pack(pady=6)

fields = [
    ("Asset Name", name_var),
    ("Category (PC/Laptop)", category_var),
    ("Serial No.", serial_var),
    ("Location", location_var),
    ("Assigned To", assigned_var),
    ("Status", status_var)
]

for i, (label, var) in enumerate(fields):
    tk.Label(frame, text=label).grid(row=i, column=0, padx=8, pady=6, sticky="e")
    tk.Entry(frame, textvariable=var, width=28).grid(row=i, column=1, padx=8, pady=6)

btn_style = {"padx": 10, "pady": 4}
tk.Button(frame, text="Add Asset", command=add_asset, bg="#16a34a", fg="white").grid(row=0, column=2, **btn_style)
tk.Button(frame, text="Edit ⇣", command=edit_asset, bg="#fb923c", fg="white").grid(row=1, column=2, **btn_style)
tk.Button(frame, text="Update", command=update_asset, bg="#2563eb", fg="white").grid(row=2, column=2, **btn_style)
tk.Button(frame, text="Delete", command=delete_asset, bg="#dc2626", fg="white").grid(row=3, column=2, **btn_style)
tk.Button(frame, text="Export Excel", command=export_excel, bg="#7c3aed", fg="white").grid(row=4, column=2, **btn_style)
tk.Button(frame, text="Export PDF", command=export_pdf, bg="#78350f", fg="white").grid(row=5, column=2, **btn_style)

# Search Bar
search_frame = tk.Frame(root)
search_frame.pack(pady=6)
tk.Label(search_frame, text="Search:").pack(side="left")
tk.Entry(search_frame, textvariable=search_var, width=40).pack(side="left", padx=6)
tk.Button(search_frame, text="Search", command=search_assets).pack(side="left")

# Scan Bar
scan_frame = tk.Frame(root)
scan_frame.pack(pady=6)
tk.Label(scan_frame, text="Scan/Enter Asset Code:").pack(side="left")
tk.Entry(scan_frame, textvariable=scan_var, width=32).pack(side="left", padx=6)
tk.Button(scan_frame, text="Scan", command=scan_asset, bg="#0f172a", fg="white").pack(side="left", padx=4)
tk.Button(scan_frame, text="Scan with Camera", command=camera_scan, bg="#047857", fg="white").pack(side="left", padx=4)

# Asset Table
columns = ("ID", "Name", "Category", "Serial Number", "Location", "Assigned To", "Status", "Asset Code")
tree = ttk.Treeview(root, columns=columns, show="headings", height=17)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140)
tree.pack(fill="both", expand=True, padx=8, pady=8)

# Footer
footer = tk.Label(root, text="Tip: Use categories 'PC' or 'Laptop' for codes like BSBG-PC-001 / BSBG-LT-001", fg="#475569")
footer.pack(pady=4)

load_assets()
root.mainloop()
