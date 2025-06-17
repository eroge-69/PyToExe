
import pandas as pd
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

def extract_po_data(excel_path):
    df = pd.read_excel(excel_path, sheet_name=0, header=2)
    df = df.rename(columns={df.columns[0]: 'Product Code', df.columns[1]: 'Quantity'})
    df = df[['Product Code', 'Quantity']].dropna()
    df['Product Code'] = df['Product Code'].astype(str).str.strip()
    df['Quantity'] = df['Quantity'].astype(int)
    return df

def extract_oa_data(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    lines = text.split('\n')
    data = []
    for i, line in enumerate(lines):
        if line.strip().startswith("170"):
            parts = line.strip().split(' ')
            if len(parts) >= 2:
                code = parts[0]
                qty_line = lines[i+1] if i+1 < len(lines) else ''
                qty = 1 if "*" + code + "*" in qty_line else 0
                data.append({'Product Code': code.strip(), 'Quantity': qty})
    return pd.DataFrame(data)

def compare_data(po_df, oa_df):
    comparison = []
    for _, row in po_df.iterrows():
        po_code = row['Product Code']
        po_qty = row['Quantity']
        oa_row = oa_df[oa_df['Product Code'] == po_code]
        if not oa_row.empty:
            oa_qty = int(oa_row.iloc[0]['Quantity'])
            status = "Match" if po_qty == oa_qty else "Quantity Mismatch"
        else:
            oa_qty = "-"
            status = "Missing in OA"
        comparison.append({
            'Product Code': po_code,
            'PO Quantity': po_qty,
            'OA Quantity': oa_qty,
            'Status': status
        })
    return pd.DataFrame(comparison)

def launch_gui():
    def load_files():
        po_file = filedialog.askopenfilename(title="Select Purchase Order Excel File", filetypes=[("Excel files", "*.xlsx")])
        oa_file = filedialog.askopenfilename(title="Select Order Acknowledgment PDF File", filetypes=[("PDF files", "*.pdf")])
        if not po_file or not oa_file:
            return
        try:
            po_data = extract_po_data(po_file)
            oa_data = extract_oa_data(oa_file)
            result_df = compare_data(po_data, oa_data)
            for row in result_df.itertuples(index=False):
                tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("2-Way Invoice Matching Tool")

    ttk.Button(root, text="Load PO and OA Files", command=load_files).pack(pady=10)

    cols = ("Product Code", "PO Quantity", "OA Quantity", "Status")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=10)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(padx=10, pady=10, fill='both', expand=True)

    root.mainloop()

launch_gui()
