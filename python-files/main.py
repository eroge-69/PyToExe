# -*- coding: utf-8 -*-
#
# Hero Scheme Calculator Desktop Application
#
# This script creates a desktop application to process Excel and PDF files
# for scheme calculations based on user-defined rules.
#
# Requirements:
# - Python 3.x
# - Libraries: tkinter, pandas, openpyxl, PyPDF2
#
# To install the required libraries, run the following command in your terminal:
# pip install pandas openpyxl PyPDF2
#

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import os
import json
import re
from PyPDF2 import PdfReader

# --- Global Configuration and Persistence ---
CONFIG_FILE = "config.json"
STATE = {
    "source_folder": "",
    "b1_discount": 0.0,
    "b2_discount": 0.0,
    "mrp_discount": 0.0,
    "annexure_a_schemes": {}
}

def load_config():
    """Loads application state from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            STATE.update(data)

def save_config():
    """Saves application state to a JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(STATE, f)

# --- Main Application Class ---
class HeroSchemeCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hero Scheme Calculator")
        self.geometry("800x600")
        self.configure(bg="#f4f4f9")

        self.bill_files = []
        self.annexure_a_groups = []
        
        load_config()

        self.create_widgets()
        self.update_ui()
        
    def create_widgets(self):
        """Builds the main application window's widgets."""
        
        # --- Header Frame ---
        header_frame = tk.Frame(self, bg="#d4e0ff", pady=10)
        header_frame.pack(fill="x")
        
        logo_text = "🏍️"
        logo_label = tk.Label(header_frame, text=logo_text, font=("Arial", 36), bg="#d4e0ff")
        logo_label.pack(side="left", padx=20)
        
        header_label = tk.Label(header_frame, text="HERO SCHEME CALCULATOR", font=("Arial", 20, "bold"), bg="#d4e0ff", fg="#2a2e5d")
        header_label.pack(side="left", fill="x", expand=True)
        
        agency_label = tk.Label(header_frame, text="वर्मा ऑटो एजेंसीज, बाराबंकी मो.9936230777", font=("Arial", 12), bg="#d4e0ff", fg="#555")
        agency_label.pack(side="right", padx=20)
        
        # --- Main Content Frame ---
        content_frame = tk.Frame(self, bg="#f4f4f9", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # --- Input Section ---
        input_frame = tk.LabelFrame(content_frame, text="1. Select Files & Enter Discounts", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#2a2e5d", padx=15, pady=15)
        input_frame.pack(fill="x", pady=10)

        # Source Folder Selection
        tk.Label(input_frame, text="Source Files Folder:", font=("Arial", 12), bg="#f4f4f9").grid(row=0, column=0, sticky="w", pady=5)
        self.source_path_label = tk.Label(input_frame, text=STATE["source_folder"] or "No folder selected", font=("Arial", 10), bg="#e9ecef", relief="solid", bd=1, width=60)
        self.source_path_label.grid(row=0, column=1, padx=5, sticky="ew")
        tk.Button(input_frame, text="Select Folder", command=self.select_source_folder, bg="#ffc107", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="ew")

        # Bill Files Selection
        tk.Label(input_frame, text="Bill Files (XLS):", font=("Arial", 12), bg="#f4f4f9").grid(row=1, column=0, sticky="w", pady=5)
        self.bill_files_label = tk.Label(input_frame, text="No files selected", font=("Arial", 10), bg="#e9ecef", relief="solid", bd=1, width=60)
        self.bill_files_label.grid(row=1, column=1, padx=5, sticky="ew")
        tk.Button(input_frame, text="Select Bills", command=self.select_bill_files, bg="#28a745", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky="ew")

        # Discount Entries
        discount_frame = tk.Frame(input_frame, bg="#f4f4f9", pady=10)
        discount_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        
        tk.Label(discount_frame, text="MRP Discount (%):", font=("Arial", 12), bg="#f4f4f9").pack(side="left", padx=(0, 5))
        self.mrp_discount_entry = tk.Entry(discount_frame, width=5)
        self.mrp_discount_entry.insert(0, str(STATE["mrp_discount"]))
        self.mrp_discount_entry.pack(side="left")

        tk.Label(discount_frame, text="Annexure B1 Discount (%):", font=("Arial", 12), bg="#f4f4f9").pack(side="left", padx=(15, 5))
        self.b1_discount_entry = tk.Entry(discount_frame, width=5)
        self.b1_discount_entry.insert(0, str(STATE["b1_discount"]))
        self.b1_discount_entry.pack(side="left")

        tk.Label(discount_frame, text="Annexure B2 Discount (%):", font=("Arial", 12), bg="#f4f4f9").pack(side="left", padx=(15, 5))
        self.b2_discount_entry = tk.Entry(discount_frame, width=5)
        self.b2_discount_entry.insert(0, str(STATE["b2_discount"]))
        self.b2_discount_entry.pack(side="left")
        
        # --- Action Buttons ---
        action_frame = tk.Frame(content_frame, bg="#f4f4f9", pady=15)
        action_frame.pack(fill="x")
        
        tk.Button(action_frame, text="Set Annexure A Schemes", command=self.set_annexure_a_schemes, bg="#007bff", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        tk.Button(action_frame, text="Process Files & Download", command=self.process_files, bg="#dc3545", fg="white", font=("Arial", 12, "bold")).pack(side="right", padx=10)

        # --- Status Bar ---
        self.status_label = tk.Label(self, text="Ready", relief="sunken", bd=1, anchor="w", bg="#e9ecef")
        self.status_label.pack(side="bottom", fill="x")

    def update_ui(self):
        """Updates the UI with current state values."""
        self.source_path_label.config(text=STATE["source_folder"] or "No folder selected")
        self.mrp_discount_entry.delete(0, tk.END)
        self.mrp_discount_entry.insert(0, str(STATE["mrp_discount"]))
        self.b1_discount_entry.delete(0, tk.END)
        self.b1_discount_entry.insert(0, str(STATE["b1_discount"]))
        self.b2_discount_entry.delete(0, tk.END)
        self.b2_discount_entry.insert(0, str(STATE["b2_discount"]))
    
    def select_source_folder(self):
        """Opens a dialog to select the source folder containing scheme files."""
        folder = filedialog.askdirectory()
        if folder:
            STATE["source_folder"] = folder
            self.source_path_label.config(text=folder)
            save_config()
            self.read_annexure_a()
            self.read_hgp_sales_promotion()

    def select_bill_files(self):
        """Opens a dialog to select one or more bill files."""
        files = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xls *.xlsx")])
        if files:
            self.bill_files = list(files)
            self.bill_files_label.config(text=f"{len(self.bill_files)} file(s) selected")
            messagebox.showinfo("Files Selected", "Selected bill files are ready for processing.")

    def read_annexure_a(self):
        """
        Reads 'Annexure A' to get item groups. This is a crucial step for the
        user to set scheme amounts.
        """
        annexure_a_path = os.path.join(STATE["source_folder"], "Annexure A.pdf")
        if not os.path.exists(annexure_a_path):
            self.status_label.config(text="Error: 'Annexure A.pdf' not found in source folder.")
            return

        try:
            reader = PdfReader(annexure_a_path)
            self.annexure_a_groups = []
            for page in reader.pages:
                text = page.extract_text()
                # Use a simple regex to find potential item groups. This is a heuristic
                # and might need adjustment based on the actual PDF format.
                groups = re.findall(r'(\n[A-Z\s]+?)\s+\d+\s+Rs', text)
                for group in groups:
                    group_clean = group.strip().replace('\n', '')
                    if group_clean and group_clean not in self.annexure_a_groups:
                        self.annexure_a_groups.append(group_clean)
            self.status_label.config(text=f"Found {len(self.annexure_a_groups)} item groups in Annexure A.")
        except Exception as e:
            self.status_label.config(text=f"Error reading Annexure A: {e}")

    def read_hgp_sales_promotion(self):
        """
        Reads 'HGP & HGO Sales Promotion' to get a preview of schemes.
        Similar to Annexure A, this is a heuristic approach.
        """
        hgp_path = os.path.join(STATE["source_folder"], "HGP & HGO Sales Promotion*.pdf")
        hgp_path = hgp_path.replace("*", "") # Simple wildcard handling
        if not os.path.exists(hgp_path):
            self.status_label.config(text="Warning: 'HGP & HGO Sales Promotion*.pdf' not found.")
            return

        try:
            reader = PdfReader(hgp_path)
            # This is a placeholder. Real-world PDF table extraction is complex.
            # A library like `tabula-py` would be better for this task.
            self.status_label.config(text="Preview of HGP & HGO Sales Promotion* is not implemented due to complex table extraction from PDF.")
        except Exception as e:
            self.status_label.config(text=f"Error reading HGP & HGO Sales Promotion*: {e}")
            
    def set_annexure_a_schemes(self):
        """
        Opens a new window for the user to select item groups and enter scheme amounts.
        """
        if not self.annexure_a_groups:
            messagebox.showerror("Error", "Please select the source folder first and ensure 'Annexure A.pdf' is present.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Set Annexure A Schemes")
        dialog.geometry("500x400")
        
        tk.Label(dialog, text="Select Item Groups and Enter Scheme Amounts:", font=("Arial", 12, "bold")).pack(pady=10)
        
        listbox_frame = tk.Frame(dialog)
        listbox_frame.pack(fill="both", expand=True, padx=20)

        listbox = tk.Listbox(listbox_frame, selectmode="multiple")
        listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        
        scheme_entries = {}
        for group in self.annexure_a_groups:
            listbox.insert(tk.END, group)
        
        # Function to save the entered amounts
        def save_schemes():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "Please select at least one item group.")
                return

            new_schemes = {}
            for i in selected_indices:
                group_name = listbox.get(i)
                amount = simpledialog.askfloat("Scheme Amount", f"Enter scheme amount for '{group_name}':")
                if amount is not None:
                    new_schemes[group_name] = amount
            
            STATE["annexure_a_schemes"].update(new_schemes)
            save_config()
            messagebox.showinfo("Saved", "Annexure A schemes have been saved.")
            dialog.destroy()

        # Action buttons
        button_frame = tk.Frame(dialog, pady=10)
        button_frame.pack()
        tk.Button(button_frame, text="Save Schemes", command=save_schemes).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=10)

    def process_files(self):
        """
        Main function to process all files, perform calculations, and
        generate new Excel files.
        """
        if not STATE["source_folder"] or not self.bill_files:
            messagebox.showerror("Error", "Please select a source folder and at least one bill file.")
            return

        self.status_label.config(text="Processing... Please wait.")
        self.update_idletasks()
        
        try:
            # Get user-defined discounts
            STATE["mrp_discount"] = float(self.mrp_discount_entry.get())
            STATE["b1_discount"] = float(self.b1_discount_entry.get())
            STATE["b2_discount"] = float(self.b2_discount_entry.get())
            save_config()

            # Load scheme data from the source files
            try:
                annexure_a_data = pd.read_excel(os.path.join(STATE["source_folder"], "Annexure A.xls"), header=None)
                annexure_b1_data = pd.read_excel(os.path.join(STATE["source_folder"], "Annexure B1.xls"), header=None)
                annexure_b2_data = pd.read_excel(os.path.join(STATE["source_folder"], "Annexure B2.xls"), header=None)
            except FileNotFoundError as e:
                self.status_label.config(text=f"Error: Missing source file: {e}")
                return

            # Process each bill file
            for bill_file_path in self.bill_files:
                self.process_single_bill(bill_file_path, annexure_a_data, annexure_b1_data, annexure_b2_data)

            self.status_label.config(text=f"Successfully processed {len(self.bill_files)} file(s).")
            messagebox.showinfo("Success", "All bills have been processed and saved as new Excel files.")
            self.bill_files = [] # Clear the list for new processing
            self.bill_files_label.config(text="No files selected")

        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}")
            messagebox.showerror("Processing Error", f"An error occurred during processing:\n{e}")

    def process_single_bill(self, bill_file_path, a_data, b1_data, b2_data):
        """
        Processes a single bill file and generates the output.
        """
        bill_df = pd.read_excel(bill_file_path, header=None)
        
        # Assuming header is row 1 (index 0), data starts from row 2 (index 1)
        bill_df = bill_df.iloc[1:].copy()
        bill_df.columns = bill_df.iloc[0] # Use the second row as header
        bill_df = bill_df.iloc[1:].reset_index(drop=True)
        
        # Ensure required columns are present. Using column indices as per user request.
        bill_df.rename(columns={
            bill_df.columns[1]: "Part Number",
            bill_df.columns[2]: "QTY",
            bill_df.columns[4]: "MRP"
        }, inplace=True)
        
        # Convert numeric columns to appropriate data types
        bill_df["QTY"] = pd.to_numeric(bill_df["QTY"], errors='coerce').fillna(0)
        bill_df["MRP"] = pd.to_numeric(bill_df["MRP"], errors='coerce').fillna(0)

        # 1. Calculate MRP Discounted Value
        bill_df["MRP Discounted Value"] = (bill_df["MRP"] * bill_df["QTY"]) * (1 - STATE["mrp_discount"] / 100)
        bill_df["Discount Amount (MRP)"] = (bill_df["MRP"] * bill_df["QTY"]) - bill_df["MRP Discounted Value"]

        output_path = os.path.splitext(bill_file_path)[0] + "_processed.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # --- Sheet 1: Annexure A Schemes ---
            a_df = bill_df.copy()
            # Assuming 'Part Number' in A data is in column 2 (index 1)
            # and 'Item Group' is in column 4 (index 3)
            a_data.rename(columns={
                a_data.columns[1]: "Part Number",
                a_data.columns[3]: "Item Group"
            }, inplace=True)
            a_data["Part Number"] = a_data["Part Number"].astype(str)
            a_df["Part Number"] = a_df["Part Number"].astype(str)
            
            merged_a = a_df.merge(a_data[['Part Number', 'Item Group']], on='Part Number', how='left')
            merged_a["Scheme Amount (Group Wise)"] = merged_a["Item Group"].map(STATE["annexure_a_schemes"])
            merged_a["Scheme Value"] = merged_a["QTY"] * merged_a["Scheme Amount (Group Wise)"]
            merged_a["Scheme Value"].fillna(0, inplace=True)
            merged_a.to_excel(writer, sheet_name="Annexure A", index=False)
            
            # Add total row
            workbook = writer.book
            worksheet = writer.sheets["Annexure A"]
            total_scheme = merged_a["Scheme Value"].sum()
            worksheet.cell(row=len(merged_a) + 2, column=worksheet.max_column, value="Total Scheme:")
            worksheet.cell(row=len(merged_a) + 2, column=worksheet.max_column + 1, value=total_scheme)
            
            # --- Sheet 2: Annexure B1 Schemes ---
            b1_df = bill_df.copy()
            # Assuming 'Part Number' in B1 data is in column 2 (index 1)
            b1_data.rename(columns={
                b1_data.columns[1]: "Part Number"
            }, inplace=True)
            b1_data["Part Number"] = b1_data["Part Number"].astype(str)
            b1_df["Part Number"] = b1_df["Part Number"].astype(str)
            
            merged_b1 = b1_df.merge(b1_data, on='Part Number', how='left', indicator=True)
            merged_b1["Scheme Value"] = 0
            merged_b1.loc[merged_b1['_merge'] == 'both', "Scheme Value"] = merged_b1["MRP Discounted Value"] * (STATE["b1_discount"] / 100)
            merged_b1.drop('_merge', axis=1, inplace=True)
            merged_b1.to_excel(writer, sheet_name="Annexure B1", index=False)
            
            # Add total row
            worksheet = writer.sheets["Annexure B1"]
            total_scheme = merged_b1["Scheme Value"].sum()
            worksheet.cell(row=len(merged_b1) + 2, column=worksheet.max_column, value="Total Scheme:")
            worksheet.cell(row=len(merged_b1) + 2, column=worksheet.max_column + 1, value=total_scheme)
            
            # --- Sheet 3: Annexure B2 Schemes ---
            b2_df = bill_df.copy()
            # Assuming 'Part Number' in B2 data is in column 1 (index 0)
            b2_data.rename(columns={
                b2_data.columns[0]: "Part Number"
            }, inplace=True)
            b2_data["Part Number"] = b2_data["Part Number"].astype(str)
            b2_df["Part Number"] = b2_df["Part Number"].astype(str)

            merged_b2 = b2_df.merge(b2_data, on='Part Number', how='left', indicator=True)
            merged_b2["Scheme Value"] = 0
            merged_b2.loc[merged_b2['_merge'] == 'both', "Scheme Value"] = merged_b2["MRP Discounted Value"] * (STATE["b2_discount"] / 100)
            merged_b2.drop('_merge', axis=1, inplace=True)
            merged_b2.to_excel(writer, sheet_name="Annexure B2", index=False)

            # Add total row
            worksheet = writer.sheets["Annexure B2"]
            total_scheme = merged_b2["Scheme Value"].sum()
            worksheet.cell(row=len(merged_b2) + 2, column=worksheet.max_column, value="Total Scheme:")
            worksheet.cell(row=len(merged_b2) + 2, column=worksheet.max_column + 1, value=total_scheme)

        self.status_label.config(text=f"Processed '{os.path.basename(bill_file_path)}' and saved to '{os.path.basename(output_path)}'.")

if __name__ == "__main__":
    app = HeroSchemeCalculator()
    app.mainloop()
