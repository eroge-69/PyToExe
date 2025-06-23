import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import os
import time

class ExcelViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KT Hospital Records for Today")
        self.root.geometry("900x500")

        # ⚠️ Set your Excel file path here
        self.file_path = "hospital_tickets.xlsx"  # Replace with your actual file path
        self.last_modified = None

        self.sheets = []
        self.sheet_data = {}

        self.setup_ui()

        if os.path.exists(self.file_path):
            try:
                self.load_excel_file()
                self.last_modified = os.path.getmtime(self.file_path)
                self.btn_refresh.config(state="normal")
                self.auto_check_for_changes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Excel file:\n{str(e)}")
        else:
            messagebox.showwarning("File Not Found", f"Excel file not found:\n{self.file_path}")

    def setup_ui(self):
        # Top Frame for Refresh Button
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=5)

        self.btn_refresh = tk.Button(top_frame, text="Refresh Sheet", command=self.refresh_sheet, state="disabled")
        self.btn_refresh.pack(side="left", padx=5)

        # Treeview Frame with Scrollbars
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side="left", expand=True, fill="both")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        hsb.pack(fill="x")

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Bottom Toolbar for Sheet Selection
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=5)

        tk.Label(bottom_frame, text="Select Sheet:").pack(side="left", padx=5)

        self.sheet_var = tk.StringVar()
        self.sheet_dropdown = ttk.Combobox(bottom_frame, textvariable=self.sheet_var, state="readonly")
        self.sheet_dropdown.pack(side="left", padx=5)
        self.sheet_dropdown.bind("<<ComboboxSelected>>", self.load_selected_sheet)

    def load_excel_file(self):
        xls = pd.ExcelFile(self.file_path)
        self.sheets = xls.sheet_names
        self.sheet_data = {sheet: xls.parse(sheet) for sheet in self.sheets}

        self.sheet_dropdown["values"] = self.sheets
        if self.sheets:
            self.sheet_var.set(self.sheets[0])
            self.display_dataframe(self.sheet_data[self.sheets[0]])

    def refresh_sheet(self):
        try:
            selected_sheet = self.sheet_var.get()
            if selected_sheet and os.path.exists(self.file_path):
                df = pd.read_excel(self.file_path, sheet_name=selected_sheet)
                self.sheet_data[selected_sheet] = df
                self.display_dataframe(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh sheet:\n{str(e)}")

    def auto_check_for_changes(self):
        if os.path.exists(self.file_path):
            current_modified = os.path.getmtime(self.file_path)
            if self.last_modified is None or current_modified != self.last_modified:
                self.last_modified = current_modified
                self.refresh_sheet()
        self.root.after(5000, self.auto_check_for_changes)  # Check every 5 seconds

    def load_selected_sheet(self, event=None):
        sheet_name = self.sheet_var.get()
        if sheet_name in self.sheet_data:
            self.display_dataframe(self.sheet_data[sheet_name])

    def display_dataframe(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

# Run the app
root = tk.Tk()
app = ExcelViewerApp(root)
root.mainloop()
