
import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading
import time

# Function to load data from Excel
def load_data():
    return pd.read_excel("FG RM Wgt Details 1.XLSX", engine='openpyxl')

# Function to refresh data periodically
def auto_refresh():
    while True:
        time.sleep(60)  # Refresh every 60 seconds
        update_treeview()

# Function to update the treeview with filtered data
def update_treeview():
    df = load_data()
    column = column_var.get()
    term = search_entry.get()
    if column and term:
        filtered_df = df[df[column].astype(str).str.contains(term, case=False, na=False)]
    else:
        filtered_df = df

    tree.delete(*tree.get_children())
    tree["columns"] = list(filtered_df.columns)
    tree["show"] = "headings"
    for col in filtered_df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    for _, row in filtered_df.iterrows():
        tree.insert("", "end", values=list(row))

# Function to handle manual search
def search():
    update_treeview()

# Create the main application window
root = tk.Tk()
root.title("FG RM Wgt Details Lookup")
root.geometry("1200x700")

# Load initial data
df = load_data()

# Dropdown to select column
column_label = tk.Label(root, text="Select Column:")
column_label.pack(pady=5)
column_var = tk.StringVar()
column_dropdown = ttk.Combobox(root, textvariable=column_var, values=list(df.columns))
column_dropdown.pack(pady=5)

# Entry to input search term
search_label = tk.Label(root, text="Enter Search Term:")
search_label.pack(pady=5)
search_entry = tk.Entry(root)
search_entry.pack(pady=5)

# Search button
search_button = tk.Button(root, text="Search", command=search)
search_button.pack(pady=10)

# Treeview to display results
tree = ttk.Treeview(root)
tree.pack(expand=True, fill='both')

# Start auto-refresh in a separate thread
refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
refresh_thread.start()

# Initial display
update_treeview()

# Run the application
root.mainloop()
