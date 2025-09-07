#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
from collections import Counter

class PointsTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Points Tracker")
        self.root.geometry("600x400")

        # Button to load files
        self.load_btn = tk.Button(root, text="Load Excel Files", command=self.load_files)
        self.load_btn.pack(pady=10)

        # Treeview for table
        self.tree = ttk.Treeview(root, columns=("Name", "Points"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Points", text="Points")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_files(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Excel Files",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filepaths:
            return

        try:
            counter = Counter()
            for file in filepaths:
                df = pd.read_excel(file, engine="openpyxl")

                # Assuming first column = First Name, second column = Last Name
                for _, row in df.iterrows():
                    if pd.notna(row[0]) and pd.notna(row[1]):
                        full_name = f"{row[0]} {row[1]}"
                        counter[full_name] += 1

            # Clear previous results
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Insert new results sorted by points
            for name, points in counter.most_common():
                self.tree.insert("", tk.END, values=(name, points))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read files:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PointsTrackerApp(root)
    root.mainloop()


# In[ ]:




