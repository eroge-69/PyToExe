import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkFont
import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl

# --- Configuration & Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_EXCEL_FILE_NAME = "Bill New Format.xlsx"
DEFAULT_EXCEL_PATH = os.path.join(SCRIPT_DIR, DEFAULT_EXCEL_FILE_NAME)
REPORTS_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "reports_gui_output_v7")

os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)

# Dummy data for Excel file creation if it doesn't exist
# Crucially structured with empty rows and 'Total' rows for auto-detection
DUMMY_DATA_FOR_SHEET1 = [
    # Table 1: Main Sales Data
    ['Sr.No', 'Party Name', 'Bill / Voucher', 'Amount', 'Site'],
    [1, 'Siddharth Industries', 'Bill', 464800, 'Solus Pearl'],
    [2, 'Bharat Fabrication', 'Bill', 200000, 'Amleshwari'],
    [3, 'JTC', 'Bill', 353402, 'Brijtara'],
    [4, 'Universal Tiles', 'Bill', 40000, 'Villa'],
    [5, 'G.R. Industries', 'Bill', 240000, 'Brijtara'],
    [6, 'B.S. Marketing', 'Bill', 401860, 'Brijtara'],
    [7, 'HR Construction', 'Bill', 6300, 'Solus Pearl'],
    [8, 'Jai Maa Durga Baadi', 'Bill', 1200, 'City Office'],
    [9, 'Tiwari Timber', 'Bill', 13300, 'Brijtara'],
    [10, 'Tiwari Timber', 'Bill', 12300, 'Brijtara'],
    ['Total', '', '', 1733162, ''], # Total row for Table 1
    
    # Empty row for separation
    ['', '', '', '', ''], 
    
    # Table 2: Quarterly Sales Summary
    ['Quarter', 'Product Line', 'QTR_Amount', 'Customers'],
    ['Q1 2024', 'Electronics', 1500000, 120],
    ['Q1 2024', 'Home Goods', 800000, 75],
    ['Q1 2024', 'Apparel', 350000, 50],
    ['Total Q1 Sales', '', 2650000, ''], # Total row for Table 2

    # Empty row for separation
    ['', '', '', '', ''],

    # Table 3: Regional Performance
    ['Region', 'Sales_Value', 'Growth_Rate'],
    ['North', 500000, '10%'],
    ['South', 300000, '8%'],
    ['East', 700000, '12%'],
    ['West', 450000, '9%'],
    ['Overall Total', 1950000, ''], # Total row for Table 3
]

DUMMY_DATA_FOR_SHEET2 = [
    ['Employee ID', 'Name', 'Department', 'Salary'],
    [101, 'Alice Johnson', 'HR', 70000],
    [102, 'Bob Williams', 'IT', 90000],
    [103, 'Charlie Brown', 'Marketing', 65000],
    ['Grand Total Salary', '', '', 225000] # Total row for Table in Sheet 2
]


def create_dummy_excel(file_path):
    """Creates a dummy Excel file with sample data structured with logical tables (headers + total rows + empty rows)."""
    try:
        wb = openpyxl.Workbook()
        
        # Sheet 1: Multiple logical tables
        ws1 = wb.active
        ws1.title = 'Sales_Reports'
        for row_data in DUMMY_DATA_FOR_SHEET1:
            ws1.append(row_data)

        # Sheet 2: Another logical table
        ws2 = wb.create_sheet('Employee_Data')
        for row_data in DUMMY_DATA_FOR_SHEET2:
            ws2.append(row_data)

        wb.save(file_path)
        messagebox.showinfo("Dummy File Created", f"Dummy Excel file created with 'Sales_Reports' and 'Employee_Data' sheets, structured for auto-detection of logical tables at:\n{file_path}")
    except ImportError:
        messagebox.showwarning("Missing openpyxl", "To create dummy Excel with structured data, 'openpyxl' is required. Please install it: `pip install openpyxl`.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create dummy Excel file: {e}")

def get_excel_sheet_names(file_path):
    """Returns a list of sheet names from an Excel file."""
    try:
        if not os.path.exists(file_path):
            create_dummy_excel(file_path)
            if not os.path.exists(file_path):
                return []

        excel_file = pd.ExcelFile(file_path)
        return excel_file.sheet_names
    except Exception as e:
        messagebox.showerror("Error Reading Sheets", f"Could not read sheet names from {file_path}:\n{e}")
        return []

def is_header_row(row_series):
    """
    Determines if a row looks like a header:
    - Contains at least one non-empty string.
    - No numbers in the first few cells (heuristic for data not starting immediately).
    """
    non_empty_strings = [str(x).strip() for x in row_series if pd.notna(x) and str(x).strip() != '']
    if not non_empty_strings:
        return False

    num_text_cells = sum(1 for x in row_series.iloc[:5] if isinstance(x, str) and not str(x).replace('.', '', 1).isdigit())
    if len(non_empty_strings) > 0 and num_text_cells >= 1:
        return True
    return False

def is_total_row(row_series, header_row=None):
    """
    Determines if a row looks like a total row:
    - Contains keywords like 'total', 'grand total', 'summary' (case-insensitive).
    - Contains at least one numeric value.
    """
    row_str = " ".join(str(x).lower() for x in row_series.dropna())
    
    if not any(keyword in row_str for keyword in ['total', 'grand total', 'summary', 'sum']):
        return False

    has_numeric_value = False
    for val in row_series:
        try:
            if pd.notna(pd.to_numeric(str(val).replace('₹', '').replace(',', ''), errors='coerce')):
                has_numeric_value = True
                break
        except Exception:
            pass
    
    return has_numeric_value

def auto_detect_tables_in_sheet(df_full_sheet_raw):
    """
    Analyzes a full DataFrame (representing an Excel sheet, loaded with header=None)
    to find logical tables based on:
    - Starting with a header-like row.
    - Ending with an empty row OR a 'total' row.
    - 'Total' rows are excluded from the extracted table data.
    Returns a dictionary of {table_name: DataFrame_of_table_data_only}.
    """
    tables = {}
    current_table_rows = []
    current_header = None
    table_counter = 0

    # Using .map for DataFrame element-wise application, more robust for newer pandas versions
    df_temp = df_full_sheet_raw.map(lambda x: str(x).strip() if pd.notna(x) else '')
    
    in_table_block = False

    for r_idx, row_series in df_temp.iterrows():
        is_empty = all(val == '' for val in row_series)

        if is_empty:
            if in_table_block and current_header is not None and current_table_rows:
                table_counter += 1
                table_name = f"Table {table_counter}"
                
                data_rows_for_df = current_table_rows
                if data_rows_for_df and is_total_row(df_full_sheet_raw.iloc[r_idx - 1], current_header):
                    data_rows_for_df = current_table_rows[:-1]

                if data_rows_for_df:
                    df_table = pd.DataFrame(data_rows_for_df, columns=current_header)
                    df_table.dropna(axis=1, how='all', inplace=True)
                    df_table.columns = [str(col) for col in df_table.columns]
                    tables[table_name] = df_table
                
            current_table_rows = []
            current_header = None
            in_table_block = False
            continue

        if not in_table_block and is_header_row(row_series):
            current_header = [str(col).strip() for col in df_full_sheet_raw.iloc[r_idx].tolist()]
            seen_cols = {}
            unique_header = []
            for col in current_header:
                original_col = col
                counter = 1
                while col in seen_cols:
                    col = f"{original_col}_{counter}"
                    counter += 1
                seen_cols[col] = True
                unique_header.append(col)
            current_header = unique_header

            in_table_block = True
            current_table_rows = []
            continue

        if in_table_block:
            current_table_rows.append(df_full_sheet_raw.iloc[r_idx].tolist())

    if in_table_block and current_header is not None and current_table_rows:
        table_counter += 1
        table_name = f"Table {table_counter}"
        
        data_rows_for_df = current_table_rows
        if data_rows_for_df and is_total_row(df_full_sheet_raw.iloc[r_idx], current_header):
             data_rows_for_df = current_table_rows[:-1]

        if data_rows_for_df:
            df_table = pd.DataFrame(data_rows_for_df, columns=current_header)
            df_table.dropna(axis=1, how='all', inplace=True)
            df_table.columns = [str(col) for col in df_table.columns]
            tables[table_name] = df_table

    return tables


def load_and_clean_excel_data_auto_detect(file_path, sheet_name, selected_table_name=None, detected_tables_dict=None):
    """
    Loads data from the specified Excel file and sheet, then uses auto-detected tables.
    Returns the DataFrame for the selected table, or the full sheet if no tables found/selected.
    """
    try:
        if not os.path.exists(file_path):
            messagebox.showwarning("File Not Found", f"Excel file not found at: {file_path}")
            return None

        df = None
        
        if selected_table_name and selected_table_name != "Entire Sheet" and detected_tables_dict and selected_table_name in detected_tables_dict:
            df = detected_tables_dict[selected_table_name].copy()
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
            if not df.empty:
                first_row_is_header = True
                for i in range(min(5, df.shape[1])):
                    cell_val = df.iloc[0, i]
                    if pd.notna(cell_val) and not isinstance(cell_val, str):
                        first_row_is_header = False
                        break
                
                if first_row_is_header and df.iloc[0].nunique() > 1:
                    df.columns = [str(col).strip() for col in df.iloc[0]]
                    df = df[1:].reset_index(drop=True)
                else:
                    df.columns = [f'Col{i+1}' for i in range(df.shape[1])]


        if df is None or df.empty:
            messagebox.showwarning("No Data", f"The selected data (Sheet: '{sheet_name}', Table: '{selected_table_name if selected_table_name else 'Entire Sheet'}') is empty or contains no data after cleaning.")
            return None

        for col in df.columns:
            if any(key in str(col).lower() for key in ['amount', 'value', 'sales_amount', 'unit cost', 'salary', 'net amount', 'qtr_amount']):
                df[col] = df[col].astype(str).str.replace(r'[₹$,€,¥,£,\s,]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)

        return df
    except Exception as e:
        messagebox.showerror("Error Loading Data", f"Error loading or processing data from '{sheet_name}' (Table: {selected_table_name if selected_table_name else 'N/A'}) in {file_path}:\n{e}")
        return None

def generate_party_wise_report(df):
    """Generates a Party-Wise report DataFrame, now including Site column."""
    required_cols = ['Party Name', 'Site']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        messagebox.showwarning("Missing Columns", f"Cannot generate Party-Wise report: Missing columns: {', '.join(missing_cols)} for this data.")
        return pd.DataFrame()

    amount_col = None
    for col in ['Amount', 'Sales_Value', 'QTR_Amount', 'Salary']:
        if col in df.columns:
            amount_col = col
            break

    if not amount_col:
        messagebox.showwarning("Missing Columns", "Cannot generate Party-Wise report: Suitable 'Amount' column (e.g., 'Amount', 'Sales_Value', 'QTR_Amount', 'Salary') missing for this data.")
        return pd.DataFrame()

    # Group by both 'Party Name' and 'Site'
    agg_dict_party = {'Total_Amount': (amount_col, 'sum')}
    
    party_wise_df = df.groupby(['Party Name', 'Site']).agg(**agg_dict_party).reset_index().sort_values(by=['Party Name', 'Total_Amount'], ascending=[True, False])
    party_wise_df.insert(0, 'Sr.No', range(1, 1 + len(party_wise_df)))
    return party_wise_df

def generate_site_wise_report(df):
    """Generates a Site-Wise report DataFrame with robust column handling."""
    if 'Site' not in df.columns:
        messagebox.showwarning("Missing Columns", "Cannot generate Site-Wise report: 'Site' column missing for this data.")
        return pd.DataFrame()

    amount_col = None
    for col in ['Amount', 'Sales_Value', 'QTR_Amount', 'Salary']:
        if col in df.columns:
            amount_col = col
            break

    if not amount_col:
        messagebox.showwarning("Missing Columns", "Cannot generate Site-Wise report: Suitable 'Amount' column (e.g., 'Amount', 'Sales_Value', 'QTR_Amount', 'Salary') missing for this data.")
        return pd.DataFrame()

    agg_dict_site = {'Total_Amount': (amount_col, 'sum')}
    
    site_wise_df = df.groupby('Site').agg(**agg_dict_site).reset_index().sort_values(by='Total_Amount', ascending=False)
    site_wise_df.insert(0, 'Sr.No', range(1, 1 + len(site_wise_df)))
    return site_wise_df

# --- GUI Application Class ---
class ExcelReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Sales Report Generator (GUI)")
        self.root.geometry("1000x700")

        self.df_raw = None
        self.current_report_df = None
        self.excel_sheet_names = []
        self.detected_tables_on_current_sheet = {}
        self.current_excel_path = DEFAULT_EXCEL_PATH

        self._setup_ui()
        self.load_initial_data()

    def _setup_ui(self):
        # --- File Selection and Load Frame ---
        file_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=5)
        file_frame.pack(side="top", fill="x", padx=10, pady=5)

        tk.Label(file_frame, text="Excel File:").pack(side="left", padx=(0, 5))
        self.file_path_entry = tk.Entry(file_frame, width=60)
        self.file_path_entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.file_path_entry.insert(0, self.current_excel_path)

        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="left", padx=(0, 5))
        tk.Button(file_frame, text="Load File", command=self.load_file).pack(side="left")

        # --- Sheet and Table Selection Frame ---
        sheet_table_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=5)
        sheet_table_frame.pack(side="top", fill="x", padx=10, pady=5)

        tk.Label(sheet_table_frame, text="Select Sheet:").pack(side="left", padx=(0, 5))
        self.sheet_name_combobox = ttk.Combobox(sheet_table_frame, width=30, state="readonly")
        self.sheet_name_combobox.pack(side="left", padx=(0, 10))
        self.sheet_name_combobox.bind("<<ComboboxSelected>>", self.on_sheet_selected)

        # Multi-select Listbox for Tables
        table_listbox_label = tk.Label(sheet_table_frame, text="Select Tables (Ctrl+Click):")
        table_listbox_label.pack(side="left", padx=(0, 5))

        self.table_listbox_frame = tk.Frame(sheet_table_frame)
        self.table_listbox_frame.pack(side="left", padx=(0, 10))
        
        self.table_listbox = tk.Listbox(self.table_listbox_frame, selectmode=tk.MULTIPLE, height=5, width=30)
        self.table_listbox.pack(side="left", fill="y", expand=True)
        # Bind the Listbox selection event
        self.table_listbox.bind("<<ListboxSelect>>", self.on_table_listbox_select)
        
        self.table_listbox_scrollbar = tk.Scrollbar(self.table_listbox_frame, orient="vertical", command=self.table_listbox.yview)
        self.table_listbox_scrollbar.pack(side="right", fill="y")
        self.table_listbox.config(yscrollcommand=self.table_listbox_scrollbar.set)

        tk.Button(sheet_table_frame, text="Load/Combine Selected", command=self.combine_selected_tables).pack(side="left")


        # --- Report Generation and Export Frame ---
        report_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=5)
        report_frame.pack(side="top", fill="x", padx=10, pady=5)

        tk.Label(report_frame, text="Generate Report:").pack(side="left", padx=(0, 5))
        tk.Button(report_frame, text="Party-Wise Report", command=self.generate_party_report).pack(side="left", padx=(0, 5))
        tk.Button(report_frame, text="Site-Wise Report", command=self.generate_site_report).pack(side="left", padx=(0, 0))
        tk.Button(report_frame, text="Export PDF", command=self.export_report_to_pdf).pack(side="right", padx=(5, 0))

        # --- Data Display Treeview ---
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(pady=10, padx=10, expand=True, fill="both")

        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbars
        ysb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        xsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        ysb.pack(side="right", fill="y")
        xsb.pack(side="bottom", fill="x")
        
        # Configure Treeview style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=tkFont.Font(family="Helvetica", size=10, weight="bold"))
        style.configure("Treeview", font=tkFont.Font(family="Helvetica", size=10))


    def load_initial_data(self):
        """Loads sheet names and initializes the first sheet/table."""
        self.excel_sheet_names = get_excel_sheet_names(self.current_excel_path)
        if self.excel_sheet_names:
            self.sheet_name_combobox['values'] = self.excel_sheet_names
            self.sheet_name_combobox.set(self.excel_sheet_names[0]) # Select first sheet by default
            # Instead of calling load_selected_data directly, trigger the listbox select event
            # This will ensure _load_single_selected_item is called correctly.
            self.on_sheet_selected(event=None) 
        else:
            messagebox.showwarning("No Sheets Found", "No sheets found in the Excel file or unable to create dummy file.")
            self.sheet_name_combobox['values'] = []
            self.sheet_name_combobox.set('')
            self.table_listbox.delete(0, tk.END)
            self.clear_treeview()


    def browse_file(self):
        """Opens a file dialog to select an Excel file."""
        file_selected = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_selected:
            self.current_excel_path = file_selected
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, self.current_excel_path)
            self.load_file()

    def load_file(self):
        """Loads the selected Excel file and populates sheet names."""
        self.excel_sheet_names = get_excel_sheet_names(self.current_excel_path)
        if self.excel_sheet_names:
            self.sheet_name_combobox['values'] = self.excel_sheet_names
            self.sheet_name_combobox.set(self.excel_sheet_names[0])  # Select the first sheet by default
            self.on_sheet_selected(event=None) # Trigger table detection for the new sheet
        else:
            messagebox.showerror("Error", "Could not load Excel file or no sheets found.")
            self.clear_treeview()
            self.table_listbox.delete(0, tk.END)


    def on_sheet_selected(self, event):
        """Event handler for sheet selection. Populates table listbox."""
        selected_sheet = self.sheet_name_combobox.get()
        self.table_listbox.delete(0, tk.END) # Clear previous table list
        self.clear_treeview() # Clear displayed data

        if selected_sheet:
            try:
                df_full_sheet_raw = pd.read_excel(self.current_excel_path, sheet_name=selected_sheet, header=None)
                self.detected_tables_on_current_sheet = auto_detect_tables_in_sheet(df_full_sheet_raw)

                table_names = ["Entire Sheet"] + list(self.detected_tables_on_current_sheet.keys())
                for name in table_names:
                    self.table_listbox.insert(tk.END, name)
                
                # Select the first item by default and trigger the listbox select event
                if table_names:
                    self.table_listbox.selection_set(0)
                    # Manually trigger the event handler to load the initial single table
                    self.on_table_listbox_select(event=None) 
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read sheet '{selected_sheet}': {e}")
                self.clear_treeview()
                self.detected_tables_on_current_sheet = {}

    def on_table_listbox_select(self, event):
        """Event handler for table listbox selection."""
        selected_indices = self.table_listbox.curselection()
        if len(selected_indices) == 1:
            # If only one table is selected, load and display that specific table
            self._load_single_selected_item()
        elif len(selected_indices) > 1:
            # If multiple tables are selected, do not automatically combine.
            # Clear the current view and inform the user to click the "Load/Combine" button.
            self.clear_treeview()
            self.current_report_df = None
            self.df_raw = None
            # Optionally, display a message
            # messagebox.showinfo("Multiple Tables Selected", "Click 'Load/Combine Selected' to view combined data.")
        else:
            # No selection or selection cleared
            self.clear_treeview()
            self.current_report_df = None
            self.df_raw = None


    def combine_selected_tables(self):
        """Combines data from selected tables in the listbox and displays it."""
        selected_indices = self.table_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select one or more tables from the list to combine.")
            self.clear_treeview()
            self.current_report_df = None
            self.df_raw = None
            return

        selected_table_names = [self.table_listbox.get(i) for i in selected_indices]
        
        combined_dfs = []
        current_sheet = self.sheet_name_combobox.get()

        for table_name in selected_table_names:
            if table_name == "Entire Sheet":
                # When "Entire Sheet" is part of multi-selection, load it entirely and break.
                # It doesn't make sense to combine "Entire Sheet" with sub-tables from it.
                df_single = load_and_clean_excel_data_auto_detect(self.current_excel_path, current_sheet, selected_table_name="Entire Sheet")
                if df_single is not None and not df_single.empty:
                    combined_dfs = [df_single] # Overwrite any previous tables if Entire Sheet is selected
                    break 
            elif table_name in self.detected_tables_on_current_sheet:
                df_table = self.detected_tables_on_current_sheet[table_name].copy()
                # Apply numeric cleaning to individual tables as well, just in case
                for col in df_table.columns:
                    if any(key in str(col).lower() for key in ['amount', 'value', 'sales_amount', 'unit cost', 'salary', 'net amount', 'qtr_amount']):
                        df_table[col] = df_table[col].astype(str).str.replace(r'[₹$,€,¥,£,\s,]', '', regex=True)
                        df_table[col] = pd.to_numeric(df_table[col], errors='coerce') # Corrected from df[col] to df_table[col]
                        df_table[col] = df_table[col].fillna(0)
                combined_dfs.append(df_table)
            else:
                messagebox.showwarning("Table Not Found", f"Table '{table_name}' not found in detected tables.")

        if not combined_dfs:
            messagebox.showwarning("No Data", "No data loaded for the selected tables.")
            self.clear_treeview()
            self.current_report_df = None
            self.df_raw = None
            return

        # Concatenate all selected DataFrames
        # sort=False prevents automatic sorting of columns, keeping original order where possible
        # ignore_index=True resets the index of the combined DataFrame
        self.df_raw = pd.concat(combined_dfs, ignore_index=True, sort=False)
        self.df_raw = self.df_raw.dropna(axis=0, how='all').dropna(axis=1, how='all') # Clean empty rows/cols after concat

        if not self.df_raw.empty:
            self.display_dataframe_in_treeview(self.df_raw)
            self.current_report_df = self.df_raw.copy()
            messagebox.showinfo("Data Loaded", f"Successfully loaded and combined data from {len(selected_table_names)} tables.")
        else:
            messagebox.showwarning("No Data", "Combined data is empty after processing.")
            self.clear_treeview()
            self.current_report_df = None
            self.df_raw = None


    def _load_single_selected_item(self):
        """
        Loads data from the currently selected sheet and a *single* selected
        table into the Treeview. This is typically for initial display or
        when only one table is chosen in the listbox.
        """
        selected_sheet = self.sheet_name_combobox.get()
        selected_indices = self.table_listbox.curselection()

        if not selected_sheet or not selected_indices:
            self.clear_treeview()
            return
        
        # Always take the first selected item when loading a single item
        first_selected_table_name = self.table_listbox.get(selected_indices[0])

        self.df_raw = load_and_clean_excel_data_auto_detect(
            self.current_excel_path, 
            selected_sheet, 
            selected_table_name=first_selected_table_name, 
            detected_tables_dict=self.detected_tables_on_current_sheet
        )

        if self.df_raw is not None and not self.df_raw.empty:
            self.display_dataframe_in_treeview(self.df_raw)
            self.current_report_df = self.df_raw.copy()
            messagebox.showinfo("Data Loaded", f"Successfully loaded '{first_selected_table_name}'.")
        else:
            self.clear_treeview()
            self.current_report_df = None
            messagebox.showwarning("No Data", f"No data found for '{first_selected_table_name}'.")


    def display_dataframe_in_treeview(self, df):
        """Clears existing data and displays the given DataFrame in the Treeview."""
        self.clear_treeview()

        if df.empty:
            return

        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")

        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def clear_treeview(self):
        """Clears all data from the Treeview widget."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree["columns"] = ()


    def generate_party_report(self):
        """Generates and displays the Party-Wise report."""
        if self.df_raw is None or self.df_raw.empty:
            messagebox.showwarning("No Data", "Please load an Excel file and select data first.")
            return

        party_report_df = generate_party_wise_report(self.df_raw)
        if not party_report_df.empty:
            self.display_dataframe_in_treeview(party_report_df)
            self.current_report_df = party_report_df
        else:
            messagebox.showinfo("Report Generation", "No Party-Wise data to display or required columns missing.")
            self.clear_treeview()
            self.current_report_df = None


    def generate_site_report(self):
        """Generates and displays the Site-Wise report."""
        if self.df_raw is None or self.df_raw.empty:
            messagebox.showwarning("No Data", "Please load an Excel file and select data first.")
            return

        site_report_df = generate_site_wise_report(self.df_raw)
        if not site_report_df.empty:
            self.display_dataframe_in_treeview(site_report_df)
            self.current_report_df = site_report_df
        else:
            messagebox.showinfo("Report Generation", "No Site-Wise data to display or required columns missing.")
            self.clear_treeview()
            self.current_report_df = None

    def format_indian_currency(self, amount):
        """Formats a number as Indian Rupee currency (e.g., ₹ 1,23,456). Removes .00 if no decimal part."""
        if pd.isna(amount):
            return ""
        
        amount_float = float(amount)
        
        # Separate integer and decimal parts
        integer_part = int(amount_float)
        decimal_part = int(round((amount_float - integer_part) * 100))

        s = str(integer_part)
        formatted_s = ''
        
        # Handle cases where amount is less than 1000 first
        if len(s) <= 3:
            formatted_s = s
        else:
            # Format the last three digits
            formatted_s = s[-3:]
            s = s[:-3]

            # Format the remaining digits in groups of two
            while s:
                formatted_s = s[-2:] + ',' + formatted_s
                s = s[:-2]
            
        if decimal_part > 0:
            return f"₹ {formatted_s}.{decimal_part:02d}"
        else:
            return f" {formatted_s}"


    def convert_amount_to_words(self, amount):
        """Converts a numeric amount to words (Indian Rupees style)."""
        try:
            num = int(amount)
            if num == 0:
                return "Zero Rupees Only"

            words_map = {
                0: '', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
                11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
                15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen',
                19: 'Nineteen'
            }
            tens_map = {
                2: 'Twenty', 3: 'Thirty', 4: 'Forty', 5: 'Fifty', 6: 'Sixty',
                7: 'Seventy', 8: 'Eighty', 9: 'Ninety'
            }

            def _num_to_words_below_100(n):
                if n < 20:
                    return words_map[n]
                else:
                    return tens_map[n // 10] + (" " + words_map[n % 10] if (n % 10 != 0) else "")

            parts = []

            crore = num // 10000000
            num %= 10000000
            if crore > 0:
                parts.append(_num_to_words_below_100(crore) + " Crore")

            lakh = num // 100000
            num %= 100000
            if lakh > 0:
                parts.append(_num_to_words_below_100(lakh) + " Lakh")

            thousand = num // 1000
            num %= 1000
            if thousand > 0:
                parts.append(_num_to_words_below_100(thousand) + " Thousand")

            hundred = num // 100
            num %= 100
            if hundred > 0:
                parts.append(words_map[hundred] + " Hundred")
            
            if num > 0:
                parts.append(_num_to_words_below_100(num))
            
            return " ".join(parts).strip() + " Rupees Only"
        except Exception as e:
            return f"Error converting amount to words: {e}"

    def export_report_to_pdf(self):
        """Exports the currently displayed report data to a PDF file."""
        if self.current_report_df is None or self.current_report_df.empty:
            messagebox.showwarning("No Data to Export", "No report data to export. Please generate a report first.")
            return

        if not self.current_report_df.columns.tolist():
            messagebox.showwarning("Empty Report", "The current report is empty or has no columns. Cannot export to PDF.")
            return

        try:
            if not os.path.exists(REPORTS_OUTPUT_DIR):
                os.makedirs(REPORTS_OUTPUT_DIR)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_type = "Combined_Data_Report" # Default for combined data
            
            # Refine report_type based on columns if a specific report was generated
            if "Party Name" in self.current_report_df.columns and "Site" in self.current_report_df.columns and "Total_Amount" in self.current_report_df.columns:
                report_type = "Party_Wise_Site_Wise_Report" # More specific name
            elif "Party Name" in self.current_report_df.columns and "Total_Amount" in self.current_report_df.columns:
                report_type = "Party_Wise_Report"
            elif "Site" in self.current_report_df.columns and "Total_Amount" in self.current_report_df.columns:
                report_type = "Site_Wise_Report"
            elif self.table_listbox.curselection() and len(self.table_listbox.curselection()) == 1:
                # If only one table is selected, use its name for the report type
                report_type = self.table_listbox.get(self.table_listbox.curselection()[0]).replace(" ", "_")
            else:
                 # Fallback for generic combined data if no specific report generated
                selected_names = [self.table_listbox.get(i) for i in self.table_listbox.curselection()]
                if len(selected_names) > 1:
                    report_type = "Combined_" + "_".join(n.replace(" ", "") for n in selected_names[:2]) # Combine first two selected names
                else:
                    report_type = "Raw_Data"


            file_path = os.path.join(REPORTS_OUTPUT_DIR, f"Report_{report_type}_{timestamp}.pdf")

            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Add a title
            title_text = f"Report: {report_type.replace('_', ' ')}"
            elements.append(Paragraph(f"<b><u>{title_text}</u></b>", styles['h1']))
            elements.append(Spacer(1, 12))

            # Convert DataFrame to a list of lists for ReportLab Table, including header
            data = [self.current_report_df.columns.tolist()] + self.current_report_df.values.tolist()
            
            # Find the amount column index for formatting
            amount_col_idx = -1
            header_row = data[0]
            for idx, col_name in enumerate(header_row):
                if any(key in str(col_name).lower() for key in ['amount', 'value', 'sales_value', 'qtr_amount', 'salary', 'total_amount']):
                    amount_col_idx = idx
                    break

            # Apply formatting to data (e.g., currency)
            formatted_data = []
            for row_idx, row_data in enumerate(data):
                new_row = []
                for col_idx, cell_value in enumerate(row_data):
                    # Apply currency formatting only to the identified amount column in data rows
                    if row_idx > 0 and col_idx == amount_col_idx and isinstance(cell_value, (int, float)):
                        new_row.append(self.format_indian_currency(cell_value))
                    elif pd.isna(cell_value):
                        new_row.append("") # Replace NaN with empty string for PDF
                    else:
                        new_row.append(str(cell_value))
                formatted_data.append(new_row)

            # Calculate column widths based on content
            max_widths = [0] * len(header_row)
            # Add some padding to max_width to prevent text from touching
            PADDING_FACTOR = 1.2 
            for row in formatted_data:
                for i, cell in enumerate(row):
                    max_widths[i] = max(max_widths[i], len(str(cell)) * PADDING_FACTOR)

            # Convert character width to points (approximate)
            CHAR_WIDTH_FACTOR = 6.5 # Approx for Helvetica 10pt
            col_widths = [max_width * CHAR_WIDTH_FACTOR for max_width in max_widths]

            total_calculated_width = sum(col_widths)
            available_width = letter[0] - 2 * doc.leftMargin
            
            if total_calculated_width > available_width:
                scale_factor = available_width / total_calculated_width
                col_widths = [w * scale_factor for w in col_widths]
            
            # Ensure no column width is too small
            min_col_width = 30 # Minimum width for a column to be readable
            col_widths = [max(w, min_col_width) for w in col_widths]


            table = Table(formatted_data, colWidths=col_widths)

            # Table style
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(table_style)

            # Add table to elements
            elements.append(table)

            # Add total sum and amount in words if an amount column was found and it's a numeric report
            if amount_col_idx != -1:
                try:
                    total_sum = self.current_report_df.iloc[:, amount_col_idx].sum()
                    
                    elements.append(Spacer(1, 12))
                    
                    total_sum_formatted = self.format_indian_currency(total_sum)
                    elements.append(Paragraph(f"<b>Grand Total:</b> {total_sum_formatted}", styles['Normal']))
                    
                    elements.append(Spacer(1, 6))
                    total_sum_words = self.convert_amount_to_words(total_sum)
                    elements.append(Paragraph(f"<b>Total Amount in Words:</b> {total_sum_words}", styles['Normal']))
                    elements.append(Spacer(1, 24))
                except Exception as e:
                    messagebox.showwarning("PDF Export Warning", f"Could not add total or total in words to PDF: {e}")
            
            doc.build(elements)
            messagebox.showinfo("Export Success", f"Report successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF: {e}\n"
                                               "Please ensure 'reportlab' and 'openpyxl' are installed.")


# --- Main Application Execution ---
if __name__ == "__main__":
    try:
        import reportlab
    except ImportError:
        messagebox.showwarning("Missing Library", "The 'reportlab' library is not installed. PDF export will not work.\n"
                                                  "Please install it using: pip install reportlab")
    try:
        import openpyxl
    except ImportError:
        messagebox.showwarning("Missing Library", "The 'openpyxl' library is not installed. Advanced Excel features and dummy file creation might be limited.\n"
                                                  "Please install it using: pip install openpyxl")

    root = tk.Tk()
    app = ExcelReportApp(root)
    root.mainloop()