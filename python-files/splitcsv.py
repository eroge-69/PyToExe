#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

def split_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return

    try:
        num_splits = int(num_splits_entry.get())
    except ValueError:
        result_label.config(text="Invalid number of splits")
        return

    try:
        df = pd.read_csv(filepath)
        total_rows = len(df)
        rows_per_split = total_rows // num_splits
        remainder = total_rows % num_splits

        for i in range(num_splits):
            start_row = i * rows_per_split
            end_row = start_row + rows_per_split + (1 if i < remainder else 0)
            split_df = df.iloc[start_row:end_row]
            split_filename = f"split_{i+1}.csv"
            split_df.to_csv(split_filename, index=False)

        result_label.config(text="CSV file split successfully!")
    except Exception as e:
        result_label.config(text=f"Error: {e}")

# GUI setup
root = tk.Tk()
root.title("CSV Splitter")

# File selection
select_button = tk.Button(root, text="Select CSV File", command=split_csv)
select_button.pack(pady=10)

# Number of splits input
num_splits_label = tk.Label(root, text="Number of splits:")
num_splits_label.pack()
num_splits_entry = tk.Entry(root)
num_splits_entry.pack()

# Result label
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

root.mainloop()

