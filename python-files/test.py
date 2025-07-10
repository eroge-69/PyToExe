import sys
import pandas as pd
import pymongo
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import uuid
import os
from datetime import datetime
import pandas as pd

# Global variables for MongoDB connection
_client = None
_db = None
_collection = None

def initialize_mongodb():
    """Initialize MongoDB connection"""
    global _client, _db, _collection
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://marwanashref836:asblXkc8U5lPaHa2@cluster0.tujrktt.mongodb.net/HypeAndHookDB?retryWrites=true&w=majority")
        _client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        _db = _client["HypeAndHookDB"]
        _collection = _db["excel_data"]
        # Test connection
        _client.admin.command('ping')
        return True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        return False

def get_collection():
    """Get the MongoDB collection"""
    global _collection
    return _collection

def close_mongodb():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()

# Default structures for each Excel file
file_structures = {
    "Income Statement.xlsx": [
        "Revenue", "Sales", "Sales Returns", "Sales Discounts", "<Other Revenue>", "<Other Revenue>", "<Other Revenue>",
        "Net Sales", "Cost of Goods Sold", "Gross Profit", "Operating Expenses", "Salaries & Wages",
        "Depreciation Expenses", "Office Expenses", "Rent Expense", "Travel Expenses", "Maintenance Expenses",
        "Advertising Expenses", "<Other Expense>", "<Other Expense>", "<Other Expense>", "Total Operating Expenses",
        "Income From Operations", "Interest Income (Expense)", "Income Before Income Taxes", "Income Tax Expense",
        "Net Income"
    ],
    "HYPE & HOOK Outreach Testing Framework.xlsx": [
        "Channel", "Volume", "N. of Replies", "Reply Rate", "N. of Meetings", "Meeting Rate", "Waste Rate",
        "Time Spent (Hours)", "Cost Per Meeting ($)", "Insights"
    ],
    "Balance Sheet.xlsx": [
        "ASSETS", "CURRENT ASSETS", "Cash", "Equipment (Microphone)", "Accounts Receivable", "FIXED (LONG-TERM) ASSETS",
        "Long-Term Investments", "Property, Plant, and Equipment", "(Less Accumulated Depreciation)", "Intangible Assets",
        "Total Fixed Assets", "OTHER ASSETS", "Deferred Income Tax", "Other", "Total Other Assets", "Total Assets",
        "LIABILITIES AND OWNER'S EQUITY", "CURRENT LIABILITIES", "Accounts Payable for Ahmed",
        "Accounts Payable for Abdallah", "Accounts Payable for Amr", "Unearned Revenue", "Total Current Liabilities",
        "LONG-TERM LIABILITIES", "Long-Term Debt", "Deferred Income Tax", "Other", "Total Long-Term Liabilities",
        "OWNER'S EQUITY", "Owner's Investment", "Capital", "Total Owner's Equity", "Total Liabilities and Owner's Equity"
    ],
    "Cash Flow Statement (1).xlsx": [
        "Cash at Beginning of Year", "Operations", "Cash receipts from", "Customers", "Other Operations",
        "Cash paid for", "Inventory purchases", "General operating and administrative expenses", "Wage expenses",
        "Interest", "Income taxes", "Net Cash Flow from Operations", "Investing Activities", "Cash receipts from",
        "Sale of property and equipment", "Collection of principal on loans", "Sale of investment securities",
        "Cash paid for", "Purchase of property and equipment", "Making loans to other entities",
        "Purchase of investment securities", "Net Cash Flow from Investing Activities", "Financing Activities",
        "Cash receipts from", "Issuance of stock", "Borrowing", "Cash paid for", "Repurchase of stock (treasury stock)",
        "Repayment of loans", "Dividends", "Net Cash Flow from Financing Activities", "Net Increase in Cash",
        "Cash at End of Year"
    ],
    "_HYPE & HOOK CONTENT PLAN (1).xlsx": [
        "Date", "Platform", "Type", "Content Idea", "Hook", "CTA", "Views", "Likes", "Engagement %", "New Client?", "Status"
    ],
    "HYPE & HOOK Outreach Tracking.xlsx": [
        "NAME", "Offer Accepted", "instagram", "Website", "Date", "Tiktok", "FIRST FOLLOW UP", "FALSE",
        "SECOND FOLLOW UP", "FALSE", "THIRD FOLLOW UP", "FALSE", "Notes"
    ]
}

class MongoLoadDialog(tk.Toplevel):
    """Custom dialog for selecting MongoDB records"""
    def __init__(self, parent, file_name):
        super().__init__(parent)
        self.title(f"Load {file_name} from MongoDB")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.file_name = file_name
        self.selected_id = None

        label = tk.Label(self, text="Select a record to load:", font=("Arial", 10, "bold"))
        label.pack(pady=10)

        self.record_combo = ttk.Combobox(self, font=("Arial", 10), state="readonly")
        self.record_combo.pack(padx=10, pady=5, fill=tk.X)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=self.accept).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.reject).pack(side=tk.LEFT, padx=5)

        self.populate_records()

    def populate_records(self):
        try:
            collection = get_collection()
            if collection is None:
                self.record_combo['values'] = ["Database not connected"]
                self.record_combo.set("Database not connected")
                self.record_combo.configure(state="disabled")
                return

            documents = list(collection.find({"file_name": self.file_name}).sort("timestamp", -1))
            if not documents:
                self.record_combo['values'] = ["No records found"]
                self.record_combo.set("No records found")
                self.record_combo.configure(state="disabled")
            else:
                items = [f"ID: {doc['_id']} (Uploaded: {doc['timestamp']})" for doc in documents]
                self.record_combo['values'] = items
                self.record_combo.configure(state="readonly")
                self.record_combo.bind("<<ComboboxSelected>>", self.on_select)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch records: {str(e)}", parent=self)
            self.record_combo['values'] = ["Error loading records"]
            self.record_combo.set("Error loading records")
            self.record_combo.configure(state="disabled")

    def on_select(self, event):
        try:
            selected_text = self.record_combo.get()
            if selected_text and "ID: " in selected_text:
                self.selected_id = selected_text.split("ID: ")[1].split(" ")[0]
        except Exception:
            self.selected_id = None

    def accept(self):
        self.destroy()

    def reject(self):
        self.selected_id = None
        self.destroy()

class AddRowDialog(tk.Toplevel):
    """Custom scrollable dialog for entering new row data"""
    def __init__(self, parent, file_name, headers, row_data=None):
        super().__init__(parent)
        self.title(f"{'Edit Row in' if row_data else 'Add New Row to'} {file_name}")
        self.geometry("400x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.file_name = file_name
        self.headers = headers
        self.inputs = {}
        self.row_data = row_data

        # Create a canvas and scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Add input fields
        for i, header in enumerate(headers):
            label = tk.Label(scrollable_frame, text=f"{header}:", font=("Arial", 10, "bold"))
            label.grid(row=i, column=0, sticky="w", pady=2)
            entry = tk.Entry(scrollable_frame, font=("Arial", 10))
            if row_data and header in row_data:
                entry.insert(0, str(row_data[header]))
            if file_name == "HYPE & HOOK Outreach Testing Framework.xlsx":
                if header in ['Volume', 'N. of Replies', 'N. of Meetings', 'Time Spent (Hours)', 'Cost Per Meeting ($)']:
                    entry.insert(0, "Enter a number")
                    entry.bind("<FocusIn>", lambda e, entry=entry: entry.delete(0, tk.END) if entry.get() == "Enter a number" else None)
                elif header in ['Reply Rate', 'Meeting Rate', 'Waste Rate']:
                    entry.insert(0, "Enter percentage (e.g., 25.5)")
                    entry.bind("<FocusIn>", lambda e, entry=entry: entry.delete(0, tk.END) if entry.get() == "Enter percentage (e.g., 25.5)" else None)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.inputs[header] = entry

        scrollable_frame.columnconfigure(1, weight=1)

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=self.validate_and_accept).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def validate_and_accept(self):
        if self.file_name == "HYPE & HOOK Outreach Testing Framework.xlsx":
            for header, entry in self.inputs.items():
                value = entry.get()
                if header in ['Volume', 'N. of Replies', 'N. of Meetings', 'Time Spent (Hours)', 'Cost Per Meeting ($)']:
                    try:
                        float(value) if value else 0.0
                    except ValueError:
                        messagebox.showwarning("Invalid Input", f"{header} must be a number", parent=self)
                        return
                elif header in ['Reply Rate', 'Meeting Rate', 'Waste Rate']:
                    try:
                        float(value.replace('%', '')) if value else 0.0
                    except ValueError:
                        messagebox.showwarning("Invalid Input", f"{header} must be a valid percentage", parent=self)
                        return
        self.destroy()

    def get_data(self):
        return {header: entry.get() for header, entry in self.inputs.items()}

class ExcelMongoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HYPE & HOOK Data Manager")
        self.geometry("1200x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize MongoDB connection
        self.status_label = tk.Label(self, text="Ready", anchor="w", font=("Arial", 10))
        self.status_label.pack(side="bottom", fill="x", padx=5)
        if initialize_mongodb():
            self.status_label.config(text="Connected to MongoDB")
        else:
            self.status_label.config(text="MongoDB connection failed - some features may not work")

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.dataframes = {}
        self.file_paths = {}
        self.tables = {}
        self.create_tabs()

    def on_closing(self):
        close_mongodb()
        self.destroy()

    def create_tabs(self):
        for file_name in file_structures.keys():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=file_name)

            # Button frame
            btn_frame = tk.Frame(frame)
            btn_frame.pack(fill="x", padx=5, pady=5)

            buttons = [
                (f"Select {file_name}", lambda f=file_name: self.select_file(f)),
                ("Add Row", lambda f=file_name: self.add_row(f)),
                ("Edit Row", lambda f=file_name: self.edit_row(f)),
                ("Delete Row", lambda f=file_name: self.delete_row(f)),
                ("Remove Last Row", lambda f=file_name: self.remove_row(f)),
                ("Swap Rows", lambda f=file_name: self.swap_rows(f)),
                ("Save to Excel", lambda f=file_name: self.save_to_excel(f)),
                ("Upload to MongoDB", lambda f=file_name: self.upload_to_mongodb(f)),
                ("Load from MongoDB", lambda f=file_name: self.load_from_mongodb(f))
            ]

            for btn_text, btn_command in buttons:
                btn = tk.Button(btn_frame, text=btn_text, font=("Arial", 10), command=btn_command)
                btn.pack(side="left", padx=5)

            # Treeview (table)
            tree_frame = tk.Frame(frame)
            tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
            tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
            tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
            tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
            tree_scroll_y.config(command=tree.yview)
            tree_scroll_y.pack(side="right", fill="y")
            tree_scroll_x.config(command=tree.xview)
            tree_scroll_x.pack(side="bottom", fill="x")
            tree.pack(fill="both", expand=True)

            self.tables[file_name] = tree
            self.initialize_table(tree, file_name)
            self.dataframes[file_name] = None
            self.file_paths[file_name] = None

    def initialize_table(self, tree, file_name):
        headers = file_structures[file_name]
        tree["columns"] = headers
        tree["show"] = "headings"
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=100, stretch=True)
        tree.tag_configure("oddrow", background="#f0f0f0")
        tree.tag_configure("evenrow", background="#ffffff")

    def select_file(self, file_name):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")], title=f"Select {file_name}")
            if file_path:
                df = pd.read_excel(file_path, sheet_name=0, header=None)
                df = self.clean_dataframe(df, file_name)
                self.dataframes[file_name] = df
                self.file_paths[file_name] = file_path
                self.populate_table(self.tables[file_name], df)
                self.status_label.config(text=f"Loaded {file_name}")
                messagebox.showinfo("Success", f"Loaded {file_name}", parent=self)
            else:
                headers = file_structures[file_name]
                self.dataframes[file_name] = pd.DataFrame(columns=headers)
                self.file_paths[file_name] = file_name
                self.initialize_table(self.tables[file_name], file_name)
                self.status_label.config(text=f"Created new table for {file_name}")
                messagebox.showinfo("Info", f"Created new table for {file_name}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error loading {file_name}")
            messagebox.showerror("Error", f"Failed to load {file_name}: {str(e)}", parent=self)

    def clean_dataframe(self, df, file_name):
        try:
            if file_name == "HYPE & HOOK Outreach Testing Framework.xlsx":
                df = df.replace("#DIV/0!", pd.NA)
                numeric_cols = ['Volume', 'N. of Replies', 'Reply Rate', 'N. of Meetings', 'Meeting Rate', 'Waste Rate',
                               'Time Spent (Hours)', 'Cost Per Meeting ($)']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')

            if not df.empty and len(df) > 0:
                first_row = df.iloc[0]
                if not first_row.isna().all():
                    try:
                        pd.to_numeric(first_row, errors='raise')
                    except (ValueError, TypeError):
                        df.columns = first_row.astype(str)
                        df = df.drop(0).reset_index(drop=True)

            expected_headers = file_structures[file_name]
            if list(df.columns) != expected_headers:
                new_df = pd.DataFrame(columns=expected_headers)
                for col in expected_headers:
                    if col in df.columns:
                        new_df[col] = df[col]
                df = new_df

            return df.fillna('')
        except Exception:
            return pd.DataFrame(columns=file_structures[file_name])

    def populate_table(self, tree, df):
        try:
            for item in tree.get_children():
                tree.delete(item)
            tree["columns"] = list(df.columns)
            tree["show"] = "headings"
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, stretch=True)
            for idx, row in df.iterrows():
                tags = ("evenrow",) if idx % 2 == 0 else ("oddrow",)
                values = [str(val) if pd.notna(val) else '' for val in row]
                tree.insert("", "end", values=values, tags=tags)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to populate table: {str(e)}", parent=self)

    def add_row(self, file_name):
        try:
            headers = file_structures[file_name]
            dialog = AddRowDialog(self, file_name, headers)
            self.wait_window(dialog)
            data = dialog.get_data()
            if data:
                tree = self.tables[file_name]
                values = [data.get(header, "") for header in headers]
                tags = ("evenrow",) if len(tree.get_children()) % 2 == 0 else ("oddrow",)
                tree.insert("", "end", values=values, tags=tags)
                self.status_label.config(text="Added new row via dialog")
                messagebox.showinfo("Success", "Row added successfully", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add row: {str(e)}", parent=self)

    def edit_row(self, file_name):
        try:
            tree = self.tables[file_name]
            selected = tree.selection()
            if len(selected) != 1:
                self.status_label.config(text="Select exactly one row to edit")
                messagebox.showwarning("Warning", "Please select exactly one row to edit", parent=self)
                return

            headers = file_structures[file_name]
            row_data = dict(zip(headers, tree.item(selected[0])["values"]))
            dialog = AddRowDialog(self, file_name, headers, row_data)
            self.wait_window(dialog)
            data = dialog.get_data()
            if data:
                values = [data.get(header, "") for header in headers]
                tags = tree.item(selected[0])["tags"]
                tree.item(selected[0], values=values, tags=tags)
                self.status_label.config(text="Row edited successfully")
                messagebox.showinfo("Success", "Row edited successfully", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit row: {str(e)}", parent=self)

    def delete_row(self, file_name):
        try:
            tree = self.tables[file_name]
            selected = tree.selection()
            if not selected:
                self.status_label.config(text="No row selected for deletion")
                messagebox.showwarning("Warning", "Please select a row to delete", parent=self)
                return

            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected row?", parent=self):
                tree.delete(selected[0])
                self.status_label.config(text="Row deleted successfully")
                messagebox.showinfo("Success", "Row deleted successfully", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete row: {str(e)}", parent=self)

    def remove_row(self, file_name):
        try:
            tree = self.tables[file_name]
            children = tree.get_children()
            if children:
                tree.delete(children[-1])
                self.status_label.config(text="Removed last row")
            else:
                self.status_label.config(text="No rows to remove")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove row: {str(e)}", parent=self)

    def swap_rows(self, file_name):
        try:
            tree = self.tables[file_name]
            selected = tree.selection()
            if len(selected) != 2:
                self.status_label.config(text="Select exactly two rows to swap")
                messagebox.showwarning("Warning", "Please select exactly two rows to swap", parent=self)
                return

            item1, item2 = selected
            values1 = tree.item(item1)["values"]
            values2 = tree.item(item2)["values"]
            tags1 = tree.item(item1)["tags"]
            tags2 = tree.item(item2)["tags"]
            tree.item(item1, values=values2, tags=tags1)
            tree.item(item2, values=values1, tags=tags2)
            self.status_label.config(text=f"Swapped rows")
            messagebox.showinfo("Success", f"Swapped rows", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to swap rows: {str(e)}", parent=self)

    def save_to_excel(self, file_name):
        try:
            tree = self.tables[file_name]
            if not tree.get_children():
                self.status_label.config(text="Cannot save: Table is empty")
                messagebox.showerror("Error", "Table is empty", parent=self)
                return

            headers = file_structures[file_name]
            data = [[tree.item(item)["values"][col] for col in range(len(headers))] for item in tree.get_children()]
            df = pd.DataFrame(data, columns=headers)
            self.dataframes[file_name] = df

            file_path = self.file_paths[file_name]
            if not file_path or file_path == file_name:
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title=f"Save {file_name}")
                if file_path:
                    self.file_paths[file_name] = file_path

            if file_path and file_path != file_name:
                df.to_excel(file_path, index=False)
                self.status_label.config(text=f"Saved {file_name} to {file_path}")
                messagebox.showinfo("Success", f"Saved {file_name} to {file_path}", parent=self)
            else:
                self.status_label.config(text="Save cancelled: No file path specified")
                messagebox.showwarning("Error", "No file path specified", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error saving {file_name}")
            messagebox.showerror("Error", f"Failed to save {file_name}: {str(e)}", parent=self)

    def upload_to_mongodb(self, file_name):
        try:
            collection = get_collection()
            if collection is None:
                messagebox.showerror("Error", "MongoDB connection not available", parent=self)
                return

            tree = self.tables[file_name]
            if not tree.get_children():
                self.status_label.config(text="Cannot upload: Table is empty")
                messagebox.showerror("Error", "Table is empty", parent=self)
                return

            headers = file_structures[file_name]
            data = []
            for item in tree.get_children():
                row_data = {}
                for col, header in enumerate(headers):
                    value = tree.item(item)["values"][col]
                    if file_name == "HYPE & HOOK Outreach Testing Framework.xlsx":
                        if header in ['Volume', 'N. of Replies', 'N. of Meetings', 'Time Spent (Hours)', 'Cost Per Meeting ($)']:
                            try:
                                value = float(value) if value else 0.0
                            except ValueError:
                                value = 0.0
                        elif header in ['Reply Rate', 'Meeting Rate', 'Waste Rate']:
                            try:
                                value = float(value.replace('%', ''))/100 if value else 0.0
                            except ValueError:
                                value = 0.0
                    row_data[header] = value
                data.append(row_data)

            unique_id = str(uuid.uuid4())
            collection.insert_one({
                "_id": unique_id,
                "file_name": file_name,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            self.status_label.config(text=f"Uploaded {file_name} to MongoDB")
            messagebox.showinfo("Success", f"Uploaded {file_name} to MongoDB with ID: {unique_id}", parent=self)
        except Exception as e:
            self.status_label.config(text=f"Error uploading {file_name} to MongoDB")
            messagebox.showerror("Error", f"Failed to upload {file_name} to MongoDB: {str(e)}", parent=self)

    def load_from_mongodb(self, file_name):
        try:
            collection = get_collection()
            if collection is None:
                messagebox.showerror("Error", "MongoDB connection not available", parent=self)
                return

            dialog = MongoLoadDialog(self, file_name)
            self.wait_window(dialog)
            selected_id = dialog.selected_id
            if not selected_id:
                self.status_label.config(text="No record selected")
                messagebox.showwarning("Warning", "No record selected", parent=self)
                return

            document = collection.find_one({"_id": selected_id, "file_name": file_name})
            if not document:
                self.status_label.config(text=f"No data found for ID: {selected_id}")
                messagebox.showwarning("Warning", f"No data found for ID: {selected_id}", parent=self)
                return

            if 'data' not in document or not document['data']:
                self.status_label.config(text=f"Empty data for ID: {selected_id}")
                messagebox.showwarning("Warning", f"Empty data for ID: {selected_id}", parent=self)
                return

            df = pd.DataFrame(document['data'])
            df = self.clean_dataframe(df, file_name)
            self.dataframes[file_name] = df
            self.file_paths[file_name] = file_name
            self.populate_table(self.tables[file_name], df)
            self.status_label.config(text=f"Loaded data from MongoDB for {file_name}")
            messagebox.showinfo("Success", f"Loaded data from MongoDB for {file_name}", parent=self)
        except Exception as e:
            self.status_label.config(text="Error loading from MongoDB")
            messagebox.showerror("Error", f"Failed to load from MongoDB: {str(e)}", parent=self)

def main():
    app = ExcelMongoApp()
    app.mainloop()

if __name__ == '__main__':
    main()