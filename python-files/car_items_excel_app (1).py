
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring

# Load the cleaned Excel file
file_path = "Cleaned_PivotReady_Car_Items_List.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# Ensure consistent column names
df.columns = [str(col).strip() for col in df.columns]

# Identify the relevant columns
columns = df.columns.tolist()
if len(columns) < 4:
    raise ValueError("The Excel file must contain at least 4 columns.")

col_wqc = columns[0]
col_item = columns[1]
col_asset = columns[2]
col_have = columns[3]

# Create the main application window
root = tk.Tk()
root.title("Car Items Search and Update App")

# Search options frame
options_frame = ttk.LabelFrame(root, text="Search Options")
options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

# Entry fields and dropdowns
search_vars = {}
dropdown_values = {
    col_wqc: sorted(df[col_wqc].dropna().unique().tolist()),
    col_have: ["", "yes", "no"]
}

for i, col in enumerate(columns):
    ttk.Label(options_frame, text=col).grid(row=i, column=0, sticky="w")
    if col in dropdown_values:
        var = tk.StringVar()
        search_vars[col] = var
        dropdown = ttk.Combobox(options_frame, textvariable=var, values=dropdown_values[col])
        dropdown.grid(row=i, column=1, sticky="ew")
    else:
        var = tk.StringVar()
        search_vars[col] = var
        entry = ttk.Entry(options_frame, textvariable=var)
        entry.grid(row=i, column=1, sticky="ew")

# Match type and logic
match_type = tk.StringVar(value="partial")
case_sensitive = tk.BooleanVar(value=False)
logic_type = tk.StringVar(value="and")

ttk.Checkbutton(options_frame, text="Case Sensitive", variable=case_sensitive).grid(row=4, column=0, sticky="w")
ttk.Radiobutton(options_frame, text="Partial Match", variable=match_type, value="partial").grid(row=5, column=0, sticky="w")
ttk.Radiobutton(options_frame, text="Exact Match", variable=match_type, value="exact").grid(row=5, column=1, sticky="w")
ttk.Radiobutton(options_frame, text="AND Logic", variable=logic_type, value="and").grid(row=6, column=0, sticky="w")
ttk.Radiobutton(options_frame, text="OR Logic", variable=logic_type, value="or").grid(row=6, column=1, sticky="w")

# Results treeview
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=1, column=1, sticky="ns")

# Search function
def perform_search(*args):
    filtered = df.copy()
    conditions = []

    for col in columns:
        val = search_vars[col].get()
        if val:
            col_data = filtered[col].astype(str)
            if not case_sensitive.get():
                col_data = col_data.str.lower()
                val = val.lower()
            if match_type.get() == "exact":
                condition = col_data == val
            else:
                condition = col_data.str.contains(val, na=False)
            conditions.append(condition)

    if conditions:
        if logic_type.get() == "and":
            mask = conditions[0]
            for cond in conditions[1:]:
                mask &= cond
        else:
            mask = conditions[0]
            for cond in conditions[1:]:
                mask |= cond
        filtered = df[mask]

    update_treeview(filtered)

# Update treeview
def update_treeview(data):
    tree.delete(*tree.get_children())
    for _, row in data.iterrows():
        tree.insert("", "end", values=list(row))

# Update function
def update_item():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a row to update.")
        return
    new_value = askstring("Update", "Enter new value for 'Have this item - yes/No' (yes/no):")
    if new_value not in ["yes", "no"]:
        messagebox.showerror("Invalid input", "Only 'yes' or 'no' are allowed.")
        return
    row_values = tree.item(selected[0])["values"]
    match = (df[col_wqc] == row_values[0]) & (df[col_item] == row_values[1]) & (df[col_asset] == row_values[2])
    df.loc[match, col_have] = new_value
    df.to_excel(file_path, index=False, engine="openpyxl")
    perform_search()

# Buttons
ttk.Button(root, text="Search", command=perform_search).grid(row=2, column=0, pady=5)
ttk.Button(root, text="Update Selected Row", command=update_item).grid(row=3, column=0, pady=5)

# Live search
for var in search_vars.values():
    var.trace_add("write", perform_search)

# Run the app
root.mainloop()
