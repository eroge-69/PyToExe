import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

bc_df = None
vendor_df = None
bc_file = None


# --- Helper: Pick header row with preview ---
def pick_header_row(file_path, file_type="csv", sheet_name=None):
    preview_window = tk.Toplevel()
    preview_window.title(f"Pick Header Row - {os.path.basename(file_path)}")
    preview_window.geometry("900x400")

    if file_type == "csv":
        df = pd.read_csv(file_path, header=None, nrows=20)
    else:  # Excel
        df = pd.read_excel(file_path, header=None, sheet_name=sheet_name, nrows=20)

    tree = ttk.Treeview(preview_window, show="headings")
    tree.pack(expand=True, fill="both")

    tree["columns"] = list(range(len(df.columns)))
    for i in range(len(df.columns)):
        tree.heading(i, text=f"Col {i}")
        tree.column(i, width=120)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    def select_row():
        row_index = tree.index(tree.selection()[0])
        preview_window.destroy()
        if file_type == "csv":
            return pd.read_csv(file_path, header=row_index)
        else:
            return pd.read_excel(file_path, header=row_index, sheet_name=sheet_name)

    select_btn = tk.Button(preview_window, text="Use Selected Row as Header",
                           command=lambda: setattr(preview_window, "result", select_row()))
    select_btn.pack(pady=10)

    preview_window.wait_window()
    return getattr(preview_window, "result", None)


# --- Load BigCommerce CSV ---
def load_bc_file():
    global bc_df, bc_file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df = pick_header_row(file_path, "csv")
        if df is not None:
            bc_df = df
            bc_file = file_path
            messagebox.showinfo("Loaded", f"Loaded BigCommerce CSV with {len(bc_df)} rows.")


# --- Load Vendor Excel ---
def load_vendor_file():
    global vendor_df
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if not file_path:
        return

    xl = pd.ExcelFile(file_path)
    sheet_name = None
    if len(xl.sheet_names) > 1:
        sheet_picker = tk.Toplevel()
        sheet_picker.title("Select Sheet")
        tk.Label(sheet_picker, text="Select a sheet:").pack(pady=10)
        sheet_var = tk.StringVar(value=xl.sheet_names[0])
        dropdown = ttk.Combobox(sheet_picker, textvariable=sheet_var, values=xl.sheet_names, state="readonly")
        dropdown.pack(pady=5)

        def confirm():
            nonlocal sheet_name
            sheet_name = sheet_var.get()
            sheet_picker.destroy()

        tk.Button(sheet_picker, text="OK", command=confirm).pack(pady=10)
        sheet_picker.wait_window()

    df = pick_header_row(file_path, "excel", sheet_name=sheet_name)
    if df is not None:
        vendor_df = df
        messagebox.showinfo("Loaded", f"Loaded Vendor Excel with {len(vendor_df)} rows.")


# --- Column Mapping ---
def map_columns(bc_df, vendor_df):
    mapping_window = tk.Toplevel()
    mapping_window.title("Map Columns")
    mapping_window.geometry("500x400")

    mappings = {}
    bc_columns = bc_df.columns.tolist()
    vendor_columns = ["NONE"] + vendor_df.columns.tolist()

    fields = [
        "SKU", "Name", "Description", "Price", "Retail Price",
        "Product UPC/EAN", "Product Weight", "Product Width",
        "Product Height", "Product Depth"
    ]

    combos = {}
    for field in fields:
        frame = tk.Frame(mapping_window)
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=f"{field} (BC → Vendor):", width=20, anchor="w").pack(side="left")

        bc_combo = ttk.Combobox(frame, values=bc_columns, state="readonly")
        bc_combo.pack(side="left", padx=5)
        if "sku" in field.lower():
            bc_combo.set(bc_columns[0])  # guess first col for SKU

        vendor_combo = ttk.Combobox(frame, values=vendor_columns, state="readonly")
        vendor_combo.pack(side="left", padx=5)
        vendor_combo.set("NONE")
        combos[field] = (bc_combo, vendor_combo)

    def confirm():
        for field, (bc_combo, vendor_combo) in combos.items():
            bc_val = bc_combo.get()
            vendor_val = vendor_combo.get()
            if bc_val:
                mappings[field] = (bc_val, vendor_val)
        mapping_window.destroy()

    tk.Button(mapping_window, text="Confirm", command=confirm).pack(pady=10)
    mapping_window.wait_window()
    return mappings


# --- Helper: Unique filename with numbering ---
def get_unique_filename(base_name, suffix, ext):
    filename = f"{base_name}_{suffix}{ext}"
    counter = 1
    while os.path.exists(filename):
        filename = f"{base_name}_{suffix}_{counter}{ext}"
        counter += 1
    return filename


# --- Process & Save ---
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
        skipped_bc = []
        matched_vendor_skus = set()

        for idx, row in bc_df.iterrows():
            sku = str(row[sku_bc]).strip().lower()
            match = vendor_df[vendor_df[sku_vendor].astype(str).str.strip().str.lower() == sku]
            if match.empty:
                skipped_bc.append(row)
                continue

            matched_vendor_skus.add(sku)
            for field, (bc_col, vendor_col) in mappings.items():
                if field == "SKU" or vendor_col == "NONE":
                    continue
                bc_df.at[idx, bc_col] = match.iloc[0][vendor_col]
                update_count += 1

        base_name, ext = os.path.splitext(os.path.basename(bc_file))

        updated_file = get_unique_filename(base_name, "Updated", ext)
        skipped_vendor_file = get_unique_filename(base_name, "SkippedInVendor", ext)
        skipped_bc_file = get_unique_filename(base_name, "SkippedInBC", ext)

        bc_df.to_csv(updated_file, index=False)

        if skipped_bc:
            skipped_bc_df = pd.DataFrame(skipped_bc)
            skipped_bc_df.to_csv(skipped_vendor_file, index=False)

        unmatched_vendor = vendor_df[~vendor_df[sku_vendor].astype(str).str.strip().str.lower().isin(
            bc_df[sku_bc].astype(str).str.strip().str.lower()
        )]
        if not unmatched_vendor.empty:
            unmatched_vendor.to_csv(skipped_bc_file, index=False)

        messagebox.showinfo(
            "Success",
            f"Updated {update_count} fields.\n\n"
            f"Saved files:\n"
            f"- {updated_file}\n"
            f"- {skipped_vendor_file if skipped_bc else 'None'}\n"
            f"- {skipped_bc_file if not unmatched_vendor.empty else 'None'}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")


# --- Main Window ---
root = tk.Tk()
root.title("BigCommerce Vendor Updater")
root.geometry("450x400")

tk.Label(root, text="BigCommerce Vendor Updater", font=("Arial", 14, "bold"), fg="red").pack(pady=20)

tk.Button(root, text="Load BigCommerce CSV", command=load_bc_file,
          width=30, height=2, bg="#2196F3", fg="red").pack(pady=10)

tk.Button(root, text="Load Vendor Excel", command=load_vendor_file,
          width=30, height=2, bg="#9C27B0", fg="red").pack(pady=10)

tk.Button(root, text="Map & Update", command=process_files,
          width=30, height=2, bg="#4CAF50", fg="red").pack(pady=20)

root.mainloop()

