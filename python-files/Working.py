import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

bc_df = None
vendor_df = None
vendor_sheet = None
bc_file = None  # Keep track of original BigCommerce file


# --- Pick Header Row Window using Treeview ---
def pick_header_row(file_path, file_type="csv", sheet_name=None):
    preview_window = tk.Toplevel()
    preview_window.title(f"Pick Header Row - {os.path.basename(file_path)}")
    preview_window.geometry("900x500")

    tk.Label(preview_window, text=f"Preview: {os.path.basename(file_path)}",
             font=("Arial", 12, "bold"), fg="red").pack(pady=5)

    # Load first 20 rows
    if file_type == "csv":
        raw_df = pd.read_csv(file_path, header=None, nrows=20, dtype=str).fillna('')
    else:
        raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20, dtype=str).fillna('')

    raw_df = raw_df.astype(str)

    # Frame for Treeview
    frame = tk.Frame(preview_window)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = [str(i) for i in range(len(raw_df.columns))]
    tree = ttk.Treeview(frame, columns=columns, show="headings")

    # Style for Treeview
    style = ttk.Style()
    style.configure("Treeview", foreground="black", font=("Courier", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="red")
    tree.tag_configure("header", background="yellow", foreground="blue")

    tree.pack(side="left", fill="both", expand=True)

    # Scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    hsb.pack(side="bottom", fill="x")
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Set headings
    for i, col in enumerate(columns):
        tree.heading(col, text=f"Col {i}", anchor="w")
        tree.column(col, width=100, anchor="w")

    # Insert rows
    for idx, row in raw_df.iterrows():
        tree.insert("", "end", values=list(row))

    # Row selector
    row_var = tk.IntVar(value=0)
    row_frame = tk.Frame(preview_window)
    row_frame.pack(pady=10)
    tk.Label(row_frame, text="Select which row contains headers:", fg="red").pack(side="left", padx=5)
    row_spin = tk.Spinbox(row_frame, from_=0, to=len(raw_df)-1, textvariable=row_var, width=5, fg="red")
    row_spin.pack(side="left")

    def highlight_row(*args):
        for i in tree.get_children():
            tree.item(i, tags=())
        selected = min(max(0, row_var.get()), len(raw_df)-1)
        selected = str(selected)
        if selected in tree.get_children():
            tree.item(selected, tags=("header",))

    row_var.trace_add("write", highlight_row)
    highlight_row()

    chosen_df = {}

    def confirm():
        header_row = row_var.get()
        if file_type == "csv":
            df = pd.read_csv(file_path, header=header_row, dtype=str)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, dtype=str)
        chosen_df["df"] = df
        preview_window.destroy()

    tk.Button(preview_window, text="Confirm", command=confirm,
              bg="#4CAF50", fg="white", width=15).pack(pady=10)

    preview_window.grab_set()
    preview_window.wait_window()
    return chosen_df.get("df", None)


# --- Sheet Picker for Excel ---
def pick_sheet(file_path):
    sheets = pd.ExcelFile(file_path).sheet_names

    sheet_window = tk.Toplevel()
    sheet_window.title("Select Sheet")
    sheet_window.geometry("300x150")

    tk.Label(sheet_window, text="Select a sheet:", font=("Arial", 12, "bold")).pack(pady=10)
    sheet_var = tk.StringVar(value=sheets[0])
    sheet_dropdown = ttk.Combobox(sheet_window, textvariable=sheet_var, state="readonly", values=sheets)
    sheet_dropdown.pack(pady=5)

    chosen = {}

    def confirm():
        chosen["sheet"] = sheet_var.get()
        sheet_window.destroy()

    tk.Button(sheet_window, text="Confirm", command=confirm, bg="#4CAF50", fg="white").pack(pady=10)
    sheet_window.grab_set()
    sheet_window.wait_window()
    return chosen.get("sheet", sheets[0])


# --- Column Mapping Window ---
def map_columns(bc_df, vendor_df):
    mapping_window = tk.Toplevel()
    mapping_window.title("Column Mapping")
    mapping_window.geometry("750x500")

    tk.Label(mapping_window, text="Match BigCommerce columns with Vendor columns",
             font=("Arial", 12, "bold"), fg="red").pack(pady=10)

    frame_map = tk.Frame(mapping_window)
    frame_map.pack(pady=10)

    fields = [
        ("SKU", "Product Code/SKU"),
        ("Price", "Price"),
        ("Cost", "Cost Price"),
        ("Retail Price", "Retail Price"),
        ("Product UPC/EAN", "UPC/EAN"),
        ("Product Weight", "Weight"),
        ("Product Width", "Width"),
        ("Product Height", "Height"),
        ("Product Depth", "Depth")
    ]

    bc_vars = {}
    vendor_vars = {}

    bc_cols = list(bc_df.columns)
    vendor_cols = ["NONE"] + list(vendor_df.columns)  # Add NONE option

    for i, (label, default_bc) in enumerate(fields):
        tk.Label(frame_map, text=f"{label}:", font=("Arial", 11), fg="red").grid(row=i, column=0, padx=10, pady=5, sticky="e")

        bc_var = tk.StringVar(value=default_bc if default_bc in bc_cols else bc_cols[0])
        bc_dropdown = ttk.Combobox(frame_map, textvariable=bc_var, state="readonly",
                                   values=bc_cols, width=28)
        bc_dropdown.grid(row=i, column=1, padx=10, pady=5)
        bc_vars[label] = bc_var

        vendor_var = tk.StringVar(value="NONE")  # default NONE
        vendor_dropdown = ttk.Combobox(frame_map, textvariable=vendor_var, state="readonly",
                                       values=vendor_cols, width=28)
        vendor_dropdown.grid(row=i, column=2, padx=10, pady=5)
        vendor_vars[label] = vendor_var

    mappings = {}

    def save_mapping():
        for key in bc_vars.keys():
            mappings[key] = (bc_vars[key].get(), vendor_vars[key].get())
        mapping_window.destroy()

    tk.Button(mapping_window, text="Save Mapping", command=save_mapping,
              width=20, bg="#4CAF50", fg="white").pack(pady=20)

    mapping_window.grab_set()
    mapping_window.wait_window()
    return mappings if mappings else None


# --- File Loaders ---
def load_bc_file():
    global bc_df, bc_file
    bc_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not bc_file:
        return
    bc_df = pick_header_row(bc_file, "csv")
    if bc_df is not None:
        messagebox.showinfo("Loaded", f"Loaded BigCommerce file with {len(bc_df)} rows.")


def load_vendor_file():
    global vendor_df, vendor_sheet
    vendor_file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("Excel 97-2003", "*.xls")])
    if not vendor_file:
        return
    # Pick sheet
    vendor_sheet = pick_sheet(vendor_file)
    vendor_df = pick_header_row(vendor_file, "excel", sheet_name=vendor_sheet)
    if vendor_df is not None:
        messagebox.showinfo("Loaded", f"Loaded Vendor file '{vendor_sheet}' with {len(vendor_df)} rows.")


# --- Get Unique Filename based on original CSV ---
def get_unique_filename(original_file, suffix="_Updated", ext=None):
    base_name = os.path.splitext(os.path.basename(original_file))[0]
    ext = ext if ext else os.path.splitext(original_file)[1]

    i = 0
    while True:
        if i == 0:
            filename = f"{base_name}{suffix}{ext}"
        else:
            filename = f"{base_name}{suffix}_{i}{ext}"
        full_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(full_path):
            return full_path
        i += 1


# --- Process Data ---
def process_files():
    global bc_df, vendor_df, bc_file
    if bc_df is None or vendor_df is None:
        messagebox.showerror("Error", "Please load both BigCommerce and Vendor files first.")
        return

    mappings = map_columns(bc_df, vendor_df)
    if not mappings:
        return

    try:
        sku_bc, sku_vendor = mappings["SKU"]

        update_count = 0
        skipped_bc = []  # SKUs not found in vendor

        for idx, row in bc_df.iterrows():
            sku = str(row[sku_bc]).strip().lower()
            match = vendor_df[vendor_df[sku_vendor].astype(str).fillna('').str.strip().str.lower() == sku]
            if match.empty:
                skipped_bc.append(row.to_dict())
                continue

            for field, (bc_col, vendor_col) in mappings.items():
                if field == "SKU" or vendor_col == "NONE":
                    continue
                bc_df.at[idx, bc_col] = match.iloc[0][vendor_col]
                update_count += 1

        # Save updated BigCommerce CSV
        out_file = get_unique_filename(bc_file)
        bc_df.to_csv(out_file, index=False)

        # Save SKUs not found in vendor
        skipped_file = None
        if skipped_bc:
            skipped_bc_df = pd.DataFrame(skipped_bc)
            skipped_file = get_unique_filename(bc_file, suffix="_Skipped_in_Vendor")
            skipped_bc_df.to_csv(skipped_file, index=False)

        # Save Vendor items not in BigCommerce
        unmatched_vendor = vendor_df[~vendor_df[sku_vendor].astype(str).fillna('').str.strip().str.lower()
                                     .isin(bc_df[sku_bc].astype(str).fillna('').str.strip().str.lower())]
        unmatched_file = None
        if not unmatched_vendor.empty:
            unmatched_file = get_unique_filename(bc_file, suffix="_Skipped_in_BC")
            unmatched_vendor.to_csv(unmatched_file, index=False)

        messagebox.showinfo(
            "Success",
            f"Updated {update_count} fields.\n"
            f"Saved updated CSV: {out_file}\n"
            f"{len(skipped_bc)} BigCommerce items not found in Vendor saved as: {skipped_file if skipped_file else 'None'}\n"
            f"{len(unmatched_vendor)} Vendor items not found in BigCommerce saved as: {unmatched_file if unmatched_file else 'None'}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")


# --- Main Window ---
root = tk.Tk()
root.title("BigCommerce Vendor Updater")
root.geometry("450x400")

tk.Label(root, text="BigCommerce Vendor Updater", font=("Arial", 14, "bold"), fg="red").pack(pady=20)

tk.Button(root, text="Load BigCommerce CSV", command=load_bc_file,
          width=30, height=2, bg="#2196F3", fg="white").pack(pady=10)

tk.Button(root, text="Load Vendor Excel", command=load_vendor_file,
          width=30, height=2, bg="#9C27B0", fg="white").pack(pady=10)

tk.Button(root, text="Map & Update", command=process_files,
          width=30, height=2, bg="#4CAF50", fg="white").pack(pady=20)

root.mainloop()
