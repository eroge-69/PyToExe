import os
from collections import defaultdict
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk

def list_folders_files(root_folder):
    summary_stats = defaultdict(lambda: defaultdict(int))
    
    for root, dirs, files in os.walk(root_folder):
        if files:
            for file in files:
                file_path = os.path.join(root, file)
                file_format = os.path.splitext(file_path)[1]
                summary_stats[root][file_format] += 1
    
    return summary_stats

def display_summary_stats(summary_stats, selected_formats=None):
    data = []
    for folder, formats in summary_stats.items():
        for file_format, count in formats.items():
            if selected_formats is None or file_format in selected_formats:
                data.append([folder, file_format, count])
    
    df = pd.DataFrame(data, columns=["Folder", "File Format", "Count"])
    return df

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)
        summary_stats = list_folders_files(folder_selected)
        df = display_summary_stats(summary_stats)
        update_treeview(df)
        update_filter_options(df)

def update_treeview(df):
    for i in tree.get_children():
        tree.delete(i)
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def update_filter_options(df):
    formats = df["File Format"].unique()
    filter_var.set(formats.tolist())

def apply_filter():
    selected_formats = [filter_listbox.get(i) for i in filter_listbox.curselection()]
    summary_stats = list_folders_files(folder_path.get())
    df = display_summary_stats(summary_stats, selected_formats)
    update_treeview(df)

# Create the main window
root = tk.Tk()
root.title("Folder and File Lister with Summary Stats")
root.geometry("900x600")

# Create a frame for the folder selection
frame = tk.Frame(root)
frame.pack(pady=10)

# Folder path entry
folder_path_label = tk.Label(frame, text="Folder Path:")
folder_path_label.pack(side=tk.LEFT, padx=5)

folder_path = tk.StringVar()
entry = tk.Entry(frame, textvariable=folder_path, width=50)
entry.pack(side=tk.LEFT, padx=5)

# Browse button
browse_button = tk.Button(frame, text="Browse", command=browse_folder)
browse_button.pack(side=tk.LEFT)

# Treeview for displaying summary stats
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

tree_scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(tree_frame, columns=("Folder", "File Format", "Count"), show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree.heading("Folder", text="Folder")
tree.heading("File Format", text="File Format")
tree.heading("Count", text="Count")
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

# Filter options
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)

filter_label = tk.Label(filter_frame, text="Filter by File Format:")
filter_label.pack(side=tk.LEFT)

filter_var = tk.Variable(value=[])
filter_listbox = tk.Listbox(filter_frame, listvariable=filter_var, selectmode=tk.MULTIPLE, height=6)
filter_listbox.pack(side=tk.LEFT, padx=5)

apply_filter_button = tk.Button(filter_frame, text="Apply Filter", command=apply_filter)
apply_filter_button.pack(side=tk.LEFT)

# Run the application
root.mainloop()
