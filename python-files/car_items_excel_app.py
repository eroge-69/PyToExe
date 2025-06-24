
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# Load the Excel file
excel_file = 'Cleaned_PivotReady_Car_Items_List.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')

# Ensure consistent column names
df.columns = [col.strip() for col in df.columns]

# Define the columns
columns = ['WQC', 'Item Required', 'Asset Number', 'Have this item - yes/No']

# Create the main application window
root = tk.Tk()
root.title("Car Items Search and Update App")
root.geometry("1000x600")

# Frame for search options
search_frame = ttk.LabelFrame(root, text="Search Options")
search_frame.pack(fill="x", padx=10, pady=5)

# Dictionary to hold search entries
search_entries = {}
dropdown_values = {}

# Dropdowns for WQC and Have item
for col in columns:
    lbl = ttk.Label(search_frame, text=col)
    lbl.pack(side="left", padx=5)
    if col in ['WQC', 'Have this item - yes/No']:
        values = sorted(df[col].dropna().unique().tolist())
        values.insert(0, "")  # Allow blank selection
        dropdown = ttk.Combobox(search_frame, values=values, width=20)
        dropdown.pack(side="left", padx=5)
        search_entries[col] = dropdown
        dropdown_values[col] = values
    else:
        entry = ttk.Entry(search_frame, width=20)
        entry.pack(side="left", padx=5)
        search_entries[col] = entry

# Match type and case sensitivity
match_type = tk.StringVar(value="partial")
case_sensitive = tk.BooleanVar(value=False)
logic_type = tk.StringVar(value="AND")

ttk.Checkbutton(search_frame, text="Case Sensitive", variable=case_sensitive).pack(side="left", padx=5)
ttk.Radiobutton(search_frame, text="Partial Match", variable=match_type, value="partial").pack(side="left")
ttk.Radiobutton(search_frame, text="Exact Match", variable=match_type, value="exact").pack(side="left")
ttk.Radiobutton(search_frame, text="AND", variable=logic_type, value="AND").pack(side="left")
ttk.Radiobutton(search_frame, text="OR", variable=logic_type, value="OR").pack(side="left")

# Treeview for displaying results
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(fill="both", expand=True, padx=10, pady=5)

# Scrollbar for treeview
scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Frame for update section
update_frame = ttk.LabelFrame(root, text="Update 'Have this item - yes/No'")
update_frame.pack(fill="x", padx=10, pady=5)

update_index = ttk.Entry(update_frame, width=10)
update_index.pack(side="left", padx=5)
update_value = ttk.Combobox(update_frame, values=["yes", "no"], width=10)
update_value.pack(side="left", padx=5)

def update_item():
    try:
        idx = int(update_index.get())
        val = update_value.get().strip().lower()
        if val not in ["yes", "no"]:
            raise ValueError("Value must be 'yes' or 'no'")
        df.at[idx, 'Have this item - yes/No'] = val
        messagebox.showinfo("Success", f"Row {idx} updated.")
        perform_search()
    except Exception as e:
        messagebox.showerror("Error", str(e))

ttk.Button(update_frame, text="Update", command=update_item).pack(side="left", padx=5)

# Function to perform search
def perform_search(*args):
    filtered = df.copy()
    conditions = []

    for col in columns:
        val = search_entries[col].get()
        if val:
            if not case_sensitive.get():
                val = val.lower()
                series = df[col].astype(str).str.lower()
            else:
                series = df[col].astype(str)

            if match_type.get() == "partial":
                condition = series.str.contains(val, na=False)
            else:
                condition = series == val

            conditions.append(condition)

    if conditions:
        if logic_type.get() == "AND":
            mask = conditions[0]
            for cond in conditions[1:]:
                mask &= cond
        else:
            mask = conditions[0]
            for cond in conditions[1:]:
                mask |= cond
        filtered = df[mask]

    # Clear and insert into treeview
    for row in tree.get_children():
        tree.delete(row)
    for idx, row in filtered.iterrows():
        tree.insert("", "end", values=[row[col] for col in columns], iid=idx)

# Bind search to entry changes for live search
for widget in search_entries.values():
    if isinstance(widget, ttk.Entry):
        widget.bind("<KeyRelease>", perform_search)
    elif isinstance(widget, ttk.Combobox):
        widget.bind("<<ComboboxSelected>>", perform_search)

# Initial population
perform_search()

# Run the app
root.mainloop()
