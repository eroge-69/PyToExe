import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# ===============================
# STEP 1: File selection
# ===============================
def upload_files():
    file_paths = filedialog.askopenfilenames(
        title="Select Excel files",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_paths:
        messagebox.showwarning("No File", "Please select at least one Excel file.")
        return

    all_dfs = []
    for path in file_paths:
        temp_df = pd.read_excel(path)
        temp_df["Source File"] = path.split("/")[-1]
        all_dfs.append(temp_df)

    global df
    df = pd.concat(all_dfs, ignore_index=True)

    country_list = sorted(df['Ctry of Destination'].dropna().unique().tolist())
    country_list.insert(0, "All Countries")
    country_dropdown['values'] = country_list
    messagebox.showinfo("Files Uploaded", f"Loaded {len(file_paths)} files and {len(df)} rows.")

# ===============================
# STEP 2: Query Parser
# ===============================
def parse_query(query):
    query = query.lower()
    qty_condition = None
    qty_match = re.search(r'(qty|quantity)\s*(>|<|=)\s*(\d+)', query)
    if qty_match:
        qty_condition = (qty_match.group(2), int(qty_match.group(3)))
        query = query.replace(qty_match.group(0), "")
    for word in ["show", "data", "for", "to", "more than", "less than", "equal to"]:
        query = query.replace(word, "")
    return query.strip(), qty_condition

# ===============================
# STEP 3: Search and Generate
# ===============================
def run_search():
    if 'df' not in globals():
        messagebox.showerror("Error", "Please upload files first.")
        return

    query = query_entry.get()
    country = country_dropdown.get()

    product_kw, qty_cond = parse_query(query)
    filtered_df = df.copy()

    if product_kw:
        keywords = [kw.strip() for kw in product_kw.split() if kw.strip()]
        for kw in keywords:
            filtered_df = filtered_df[filtered_df['Product'].str.contains(kw, case=False, na=False)]

    if qty_cond:
        op, qty_val = qty_cond
        if op == ">":
            filtered_df = filtered_df[filtered_df['QTY'] > qty_val]
        elif op == "<":
            filtered_df = filtered_df[filtered_df['QTY'] < qty_val]
        elif op == "=":
            filtered_df = filtered_df[filtered_df['QTY'] == qty_val]

    if country != "All Countries":
        filtered_df = filtered_df[filtered_df['Ctry of Destination'].astype(str).str.lower() == country.lower()]

    if filtered_df.empty:
        messagebox.showinfo("No Results", "No matching records found.")
    else:
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if save_path:
            filtered_df.to_excel(save_path, index=False)
            messagebox.showinfo("Success", f"Report saved:\n{save_path}")

# ===============================
# STEP 4: Tkinter UI
# ===============================
root = tk.Tk()
root.title("Excel Search Tool")
root.geometry("500x200")

upload_btn = tk.Button(root, text="📂 Upload Excel Files", command=upload_files)
upload_btn.pack(pady=10)

query_label = tk.Label(root, text="Search Query:")
query_label.pack()
query_entry = tk.Entry(root, width=50)
query_entry.pack()

country_label = tk.Label(root, text="Country Filter:")
country_label.pack()
country_dropdown = ttk.Combobox(root, values=["All Countries"])
country_dropdown.current(0)
country_dropdown.pack()

search_btn = tk.Button(root, text="▶️ Run Search", command=run_search, bg="green", fg="white")
search_btn.pack(pady=10)

root.mainloop()
