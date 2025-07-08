# csv_cleaner_gui.py

import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re # Import regex for advanced parsing
import csv # Import csv module for manual CSV writing
from tkcalendar import DateEntry # Import DateEntry for date picker

class CSVCleanerApp:
    """
    A simple GUI application for cleaning and structuring CSV/Text files.
    It allows users to select a text file with statement-like data,
    parses it into a structured format, removes missing values and duplicates,
    and saves the cleaned data to a new CSV file.
    It also includes advanced cleaning options like setting rates and deleting rows by date range.
    """
    def __init__(self, master):
        """
        Initializes the Tkinter application window and widgets.
        """
        self.master = master
        master.title("CSV Cleaner GUI")
        master.geometry("800x750") # Larger window to accommodate new controls and spacing
        # Removed master.resizable(False, False) to allow native minimize/maximize and resizing

        # Apply a modern theme if available (ttk themes)
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Configure styles for widgets with a new color palette
        self.style.configure('TFrame', background='#e0f2f7') # Light blue-gray background
        # Centering text in labels where data/status is displayed
        self.style.configure('TLabel', background='#e0f2f7', font=('Inter', 12), foreground='#333333', anchor='center')
        
        # Define a custom style for LabelFrame and explicitly set its layout
        self.style.configure('Custom.TLabelFrame', background='#ffffff', foreground='#004d40', font=('Inter', 14, 'bold'))
        # Explicitly define the layout for the custom LabelFrame style
        self.style.layout('Custom.TLabelFrame',
                          [('TLabelframe.border', {'sticky': 'nswe'}),
                           ('TLabelframe.padding', {'sticky': 'nswe', 'children':
                                                    [('TLabelframe.label', {'sticky': 'nw'}),
                                                     ('TLabelframe.contents', {'sticky': 'nswe'})]})])

        self.style.configure('TButton', font=('Inter', 12, 'bold'), padding=10, borderwidth=0, relief='flat')
        self.style.map('TButton',
                       background=[('active', '#004d40'), ('!disabled', '#00796b')], # Dark teal on active, teal otherwise
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        # Centering text in Entry widgets
        self.style.configure('TEntry', font=('Inter', 10), padding=5, fieldbackground='#f8f8f8', bordercolor='#b2dfdb', justify='center')
        self.style.configure('TCheckbutton', background='#e0f2f7', foreground='#333333')
        self.style.configure('TSeparator', background='#b2dfdb') # Light teal separator

        # Create a Canvas to hold the scrollable content
        self.canvas = tk.Canvas(master, background='#e0f2f7', highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)


        # Main frame for content, placed inside the canvas
        # This frame will contain all other widgets and will be scrollable
        self.main_frame = ttk.Frame(self.canvas, padding="20 20 20 20", style='TFrame')
        # Store the item ID returned by create_window
        self.main_frame_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Bind the <Configure> event of the main_frame to update the canvas scrollregion
        # This ensures the scrollbar adapts as content (like advanced_frame) is packed/unpacked
        self.main_frame.bind("<Configure>", self._on_frame_configure)


        # Title Label
        self.title_label = ttk.Label(self.main_frame, text="CSV Data Cleaner & Structurer", font=('Inter', 28, 'bold'), foreground='#004d40', background='#e0f2f7')
        self.title_label.pack(pady=15)

        # File path display label (centered)
        self.file_path_label = ttk.Label(self.main_frame, text="No file selected.", wraplength=700, background='#e0f2f7', foreground='#333333')
        self.file_path_label.pack(pady=10)

        # Select File Button
        self.select_button = ttk.Button(self.main_frame, text="Select Text/CSV File", command=self.select_file)
        self.select_button.pack(pady=10)

        # Clean Data Button (initial processing)
        self.clean_basic_button = ttk.Button(self.main_frame, text="Clean Data (Basic)", command=self._parse_and_initial_clean, state=tk.DISABLED)
        self.clean_basic_button.pack(pady=10)

        # View Parsed Data Button (for debugging)
        self.view_parsed_data_button = ttk.Button(self.main_frame, text="View Parsed Data (for Debug)", command=self._view_parsed_data, state=tk.DISABLED)
        self.view_parsed_data_button.pack(pady=5)


        # Clean Data (Advanced) Button - New
        self.clean_advance_button = ttk.Button(self.main_frame, text="Clean Data (Advanced)", command=self._show_advanced_options, state=tk.DISABLED)
        self.clean_advance_button.pack(pady=10)

        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=15, padx=10)

        # Advanced Cleaning Options Frame (initially hidden)
        self.advanced_frame = ttk.LabelFrame(self.main_frame, text="Advanced Cleaning Options", padding="15 15 15 15", style='Custom.TLabelFrame')
        self.advanced_frame_visible = False # Track visibility

        # Row 1: Set Entire Rate
        ttk.Label(self.advanced_frame, text="Set Entire Rate:", background='#ffffff', foreground='#333333').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        # Centering text in this Entry widget
        self.entire_rate_entry = ttk.Entry(self.advanced_frame, width=20, style='TEntry', justify='center')
        self.entire_rate_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        self.apply_entire_rate_button = ttk.Button(self.advanced_frame, text="Apply", command=self.apply_entire_rate, state=tk.DISABLED)
        self.apply_entire_rate_button.grid(row=0, column=2, sticky='e', pady=5, padx=5)

        # Container for dynamically added rate range sections
        self.rate_range_sections_frame = ttk.Frame(self.advanced_frame, style='TFrame', padding=(0, 10, 0, 0))
        self.rate_range_sections_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        self.rate_range_sections_frame.grid_columnconfigure(1, weight=1) # Make entry column expandable

        self.rate_range_entries = [] # List to hold references to each set of rate range widgets

        # Add initial rate range section
        self._add_rate_range_section(can_delete=False) # Initial section cannot be deleted

        # Button to add another rate range section
        self.add_rate_range_button = ttk.Button(self.advanced_frame, text="Add Another Rate Range", command=lambda: self._add_rate_range_section(can_delete=True), state=tk.DISABLED)
        self.add_rate_range_button.grid(row=2, column=0, columnspan=3, pady=10) # Position below the dynamic sections

        # Row for Delete Rows in Date Range
        ttk.Label(self.advanced_frame, text="Delete Rows in Date Range:", background='#ffffff', foreground='#333333').grid(row=3, column=0, sticky='w', pady=10, padx=5, columnspan=3)
        ttk.Label(self.advanced_frame, text="Start Date (DD-MM-YYYY):", background='#ffffff', foreground='#333333').grid(row=4, column=0, sticky='w', pady=2, padx=5)
        # Centering text in DateEntry widgets
        self.delete_start_date_entry = DateEntry(self.advanced_frame, width=17, background='#f8f8f8', foreground='#333333', borderwidth=2, date_pattern='dd-mm-yyyy', justify='center')
        self.delete_start_date_entry.grid(row=4, column=1, sticky='ew', pady=2, padx=5)
        ttk.Label(self.advanced_frame, text="End Date (DD-MM-YYYY):", background='#ffffff', foreground='#333333').grid(row=5, column=0, sticky='w', pady=2, padx=5)
        # Centering text in DateEntry widgets
        self.delete_end_date_entry = DateEntry(self.advanced_frame, width=17, background='#f8f8f8', foreground='#333333', borderwidth=2, date_pattern='dd-mm-yyyy', justify='center')
        self.delete_end_date_entry.grid(row=5, column=1, sticky='ew', pady=2, padx=5)
        self.delete_range_button = ttk.Button(self.advanced_frame, text="Delete", command=self.delete_rows_in_range, state=tk.DISABLED)
        self.delete_range_button.grid(row=5, column=2, sticky='e', pady=5, padx=5)

        # Configure columns to expand in advanced_frame
        self.advanced_frame.grid_columnconfigure(1, weight=1)

        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=15, padx=10)

        # Save Cleaned CSV Button
        self.save_button = ttk.Button(self.main_frame, text="Save Cleaned CSV", command=self.save_cleaned_csv, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        # Status Label for user feedback (centered)
        self.status_label = ttk.Label(self.main_frame, text="", font=('Inter', 10, 'italic'), foreground='#6b7280', background='#e0f2f7')
        self.status_label.pack(pady=10)

        self.input_file_path = None # To store the path of the selected file
        self.df_cleaned = None # DataFrame to hold the cleaned data
        self.df_raw_parsed = None # DataFrame to hold the raw parsed data for debugging

    def _on_frame_configure(self, event):
        """Update the scrollregion of the canvas when the main_frame size changes."""
        # Ensure all pending geometry updates for the main_frame are processed
        self.main_frame.update_idletasks() 
        # Update the canvas scrollregion to encompass the entire main_frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Also ensure the canvas window (main_frame) width matches the canvas width
        self.canvas.itemconfig(self.main_frame_id, width=self.canvas.winfo_width())


    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling for the canvas."""
        # For Windows/Linux, event.delta is typically 120 or -120 per scroll
        # For macOS, event.delta is a more granular value
        if event.num == 5 or event.delta == -120: # Scroll down
            self.canvas.yview_scroll(1, "unit")
        elif event.num == 4 or event.delta == 120: # Scroll up
            self.canvas.yview_scroll(-1, "unit")

    def _update_advanced_buttons_state(self, state):
        """Helper to enable/disable advanced cleaning option buttons."""
        self.apply_entire_rate_button.config(state=state)
        self.add_rate_range_button.config(state=state)
        self.delete_range_button.config(state=state)
        # Update state for all dynamically added rate range apply buttons
        for section in self.rate_range_entries:
            section['apply_button'].config(state=state)

    def _show_advanced_options(self):
        """Shows the advanced cleaning options frame and enables its buttons."""
        if not self.advanced_frame_visible:
            self.advanced_frame.pack(fill='x', pady=10)
            self.advanced_frame_visible = True
            self._update_advanced_buttons_state(tk.NORMAL)
            self.status_label.config(text="Advanced cleaning options are now visible.")
            # After packing, force an update to ensure scrollregion is calculated correctly
            self.master.update_idletasks()
            self._on_frame_configure(None) # Manually trigger scrollregion update
        else:
            self.status_label.config(text="Advanced cleaning options are already visible.")

    def select_file(self):
        """
        Opens a file dialog to let the user select a text or CSV file.
        Updates the file path label and enables the initial clean button.
        """
        file_path = filedialog.askopenfilename(
            title="Select a Text or CSV file",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file_path = file_path
            self.file_path_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.clean_basic_button.config(state=tk.NORMAL)
            self.clean_advance_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.view_parsed_data_button.config(state=tk.DISABLED) # Disable until basic clean
            self._update_advanced_buttons_state(tk.DISABLED) # Disable advanced options
            if self.advanced_frame_visible: # Hide advanced frame if it was visible
                self.advanced_frame.pack_forget()
                self.advanced_frame_visible = False
            self.status_label.config(text="File selected. Click 'Clean Data (Basic)' to process.")
            # After changing visibility, force an update to ensure scrollregion is calculated correctly
            self.master.update_idletasks()
            self._on_frame_configure(None) # Manually trigger scrollregion update
        else:
            self.input_file_path = None
            self.file_path_label.config(text="No file selected.")
            self.clean_basic_button.config(state=tk.DISABLED)
            self.clean_advance_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.view_parsed_data_button.config(state=tk.DISABLED)
            self._update_advanced_buttons_state(tk.DISABLED)
            if self.advanced_frame_visible:
                self.advanced_frame.pack_forget()
                self.advanced_frame_visible = False
            self.status_label.config(text="Please select a file.")
            self.master.update_idletasks()
            self._on_frame_configure(None) # Manually trigger scrollregion update

    def _clean_number_string(self, num_str):
        """
        Cleans a number string by removing thousands separators and standardizing decimal.
        Handles cases like "1,234.56", "1.234,56", "1 234,56", or "123,45".
        """
        if not isinstance(num_str, str):
            return num_str # Return as is if not a string (e.g., already None)

        # Remove spaces
        cleaned_str = num_str.replace(' ', '')

        # Check for both comma and dot to infer decimal separator
        if '.' in cleaned_str and ',' in cleaned_str:
            # If both, assume dot is decimal, comma is thousands (e.g., 1,234.56)
            cleaned_str = cleaned_str.replace(',', '')
        elif ',' in cleaned_str and '.' not in cleaned_str:
            # If only comma, assume it's decimal (e.g., 123,45)
            cleaned_str = cleaned_str.replace(',', '.')

        return cleaned_str

    def _parse_statement_line(self, line):
        """
        Parses a single line from the input statement-like text based on the provided example.
        Returns a dictionary with parsed data or None if the line is not a valid data line.
        """
        line = line.strip()

        # Skip empty lines, lines of dashes, or header lines (e.g., "Date Inv. No. Receipts Issues Balance")
        if not line or line.startswith('-') or ("Date" in line and "Inv." in line and "Receipts" in line):
            return None

        parsed_data = {
            'Date': None,
            'Inv. No.': None,
            'Purchase': None, # Renamed from 'Receipts'
            'Sell': None,     # Renamed from 'Issues'
            'Stock': None     # Renamed from 'Balance'
        }

        # Try to parse "Balance B/f" line first (these lines typically don't have a date)
        balance_bf_match = re.match(r'^\s*Balance B/f\s*([\d.,\s]+)\s*$', line) # Allow more chars for balance
        if balance_bf_match:
            try:
                parsed_data['Inv. No.'] = 'Balance B/f'
                cleaned_balance_str = self._clean_number_string(balance_bf_match.group(1))
                parsed_data['Stock'] = float(cleaned_balance_str)
                return parsed_data
            except ValueError:
                pass

        # For other lines, split by any whitespace and try to identify components
        parts = line.split()

        if not parts:
            return None

        # Check if the first part is a date (DD-MM-YYYY or DD/MM/YYYY format)
        date_match = re.match(r'^\d{2}[-/]\d{2}[-/]\d{4}$', parts[0])
        if date_match:
            parsed_data['Date'] = parts[0]
            parts = parts[1:]

        # Identify numerical parts from the end of the line
        numerical_values_extracted = []
        # Relax regex to allow commas and spaces within numbers for initial extraction
        while parts and re.match(r'^[\d.,\s]+$', parts[-1]):
            numerical_values_extracted.insert(0, parts.pop())
            if len(numerical_values_extracted) == 3:
                break

        # Assign numerical values based on the number of values found
        if len(numerical_values_extracted) == 3:
            try:
                parsed_data['Purchase'] = float(self._clean_number_string(numerical_values_extracted[0]))
                parsed_data['Sell'] = float(self._clean_number_string(numerical_values_extracted[1]))
                parsed_data['Stock'] = float(self._clean_number_string(numerical_values_extracted[2]))
            except ValueError:
                return None
        elif len(numerical_values_extracted) == 2:
            try:
                parsed_data['Sell'] = float(self._clean_number_string(numerical_values_extracted[0]))
                parsed_data['Stock'] = float(self._clean_number_string(numerical_values_extracted[1]))
            except ValueError:
                return None
        elif len(numerical_values_extracted) == 1:
            try:
                parsed_data['Stock'] = float(self._clean_number_string(numerical_values_extracted[0]))
            except ValueError:
                return None
        else:
            return None

        # The remaining parts (if any) form the 'Inv. No.' (transaction type)
        if parts:
            parsed_data['Inv. No.'] = ' '.join(parts).strip()

        if parsed_data['Stock'] is not None or (parsed_data['Date'] is not None and parsed_data['Inv. No.'] is not None):
            return parsed_data
        return None

    def _parse_and_initial_clean(self):
        """
        Reads the selected file, parses it as a statement, performs initial cleaning
        (type conversions, dropna, drop_duplicates), and stores the result in self.df_cleaned.
        Enables advanced cleaning and save buttons.
        """
        if not self.input_file_path:
            messagebox.showerror("Error", "No file selected. Please select a file first.")
            return

        self.status_label.config(text="Parsing and performing initial clean... Please wait.")
        self.master.update_idletasks() # Update GUI to show message immediately

        parsed_rows = []
        try:
            with open(self.input_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    data = self._parse_statement_line(line)
                    if data:
                        parsed_rows.append(data)

            if not parsed_rows:
                messagebox.showwarning("No Data", "No valid data rows could be parsed from the selected file. Please check the file format.")
                self.status_label.config(text="No valid data parsed.")
                return # Exit early if no data

            df = pd.DataFrame(parsed_rows)

            expected_cols = ['Date', 'Inv. No.', 'Purchase', 'Sell', 'Stock'] # Updated column names
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            df = df[expected_cols]

            # Store the initially parsed (raw) DataFrame for debugging purposes
            self.df_raw_parsed = df.copy()
            self.view_parsed_data_button.config(state=tk.NORMAL) # Enable view button

            initial_rows = len(df)

            # Robust date parsing: try multiple formats with dayfirst=True
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)

            numerical_cols_to_convert = ['Purchase', 'Sell', 'Stock'] # Updated column names
            for col in numerical_cols_to_convert:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df['Purchase'] = df['Purchase'].fillna(0) # Updated column name
            df['Sell'] = df['Sell'].fillna(0)         # Updated column name

            df_cleaned_critical = df.dropna(subset=['Inv. No.', 'Stock']) # Updated column name
            rows_removed_critical_nan = initial_rows - len(df_cleaned_critical)

            self.df_cleaned = df_cleaned_critical.drop_duplicates()
            rows_removed_duplicates = len(df_cleaned_critical) - len(self.df_cleaned)

            # Initialize 'Rate' and 'Total Balance' columns
            self.df_cleaned['Rate'] = None
            self.df_cleaned['Total Balance'] = None

            self.status_label.config(text=f"Initial cleaning complete. Removed {rows_removed_critical_nan} rows with critical missing data and {rows_removed_duplicates} duplicate rows. Ready for advanced cleaning or saving.")
            self.clean_advance_button.config(state=tk.NORMAL) # Enable advanced button
            self.save_button.config(state=tk.NORMAL) # Enable save button

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during initial cleaning: {e}")
            self.status_label.config(text=f"Error: {e}")
        finally:
            self.clean_basic_button.config(state=tk.NORMAL) # Ensure clean basic button is re-enabled
            self.master.update_idletasks()
            self._on_frame_configure(None) # Manually trigger scrollregion update

    def _view_parsed_data(self):
        """Displays the first few rows of the raw parsed DataFrame for debugging."""
        if self.df_raw_parsed is None:
            messagebox.showwarning("No Data", "No data has been parsed yet. Please select a file and click 'Clean Data (Basic)'.")
            return

        # Convert Date column to desired string format for display
        display_df = self.df_raw_parsed.copy()
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].dt.strftime('%d-%m-%Y').fillna('')

        # Format numerical columns for display
        for col in ['Purchase', 'Sell', 'Stock', 'Rate', 'Total Balance']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}" if pd.notna(x) else '')

        messagebox.showinfo("Parsed Data (First 20 Rows)", display_df.head(20).to_string())


    def _add_rate_range_section(self, can_delete=True):
        """Adds a new set of date range and rate input fields."""
        # Use a dynamic row based on the number of existing sections
        # The main 'Delete Rows in Date Range' section starts at row 3 in advanced_frame
        # Each rate range section will be added before it in the rate_range_sections_frame
        current_row_in_subframe = len(self.rate_range_entries) * 4 # Each section takes 4 rows (label, start, end, rate/apply)

        # Frame for this specific rate range section
        section_frame = ttk.Frame(self.rate_range_sections_frame, style='TFrame', padding=(0, 5))
        section_frame.grid(row=current_row_in_subframe, column=0, columnspan=3, sticky='ew')
        section_frame.grid_columnconfigure(1, weight=1) # Make entry column expandable

        ttk.Label(section_frame, text=f"Rate Range {len(self.rate_range_entries) + 1}:", background='#ffffff', foreground='#333333').grid(row=0, column=0, sticky='w', pady=2, padx=5, columnspan=2)

        if can_delete:
            delete_btn = ttk.Button(section_frame, text="X", command=lambda f=section_frame, i=len(self.rate_range_entries): self._delete_rate_range_section(f, i), width=3)
            delete_btn.grid(row=0, column=2, sticky='e', padx=5, pady=2)

        ttk.Label(section_frame, text="Start Date (DD-MM-YYYY):", background='#ffffff', foreground='#333333').grid(row=1, column=0, sticky='w', pady=2, padx=5)
        # Centering text in DateEntry widgets
        start_date_entry = DateEntry(section_frame, width=17, background='#f8f8f8', foreground='#333333', borderwidth=2, date_pattern='dd-mm-yyyy', justify='center')
        start_date_entry.grid(row=1, column=1, sticky='ew', pady=2, padx=5)

        ttk.Label(section_frame, text="End Date (DD-MM-YYYY):", background='#ffffff', foreground='#333333').grid(row=2, column=0, sticky='w', pady=2, padx=5)
        # Centering text in DateEntry widgets
        end_date_entry = DateEntry(section_frame, width=17, background='#f8f8f8', foreground='#333333', borderwidth=2, date_pattern='dd-mm-yyyy', justify='center')
        end_date_entry.grid(row=2, column=1, sticky='ew', pady=2, padx=5)

        ttk.Label(section_frame, text="Rate:", background='#ffffff', foreground='#333333').grid(row=3, column=0, sticky='w', pady=2, padx=5)
        # Centering text in this Entry widget
        rate_entry = ttk.Entry(section_frame, width=20, style='TEntry', justify='center')
        rate_entry.grid(row=3, column=1, sticky='ew', pady=2, padx=5)

        # Store references and create a unique command for each apply button
        idx = len(self.rate_range_entries)
        apply_button = ttk.Button(section_frame, text="Apply", command=lambda i=idx: self.apply_rate_for_specific_range(i), state=tk.DISABLED)
        apply_button.grid(row=3, column=2, sticky='e', pady=5, padx=5)

        self.rate_range_entries.append({
            'frame': section_frame,
            'start_date_entry': start_date_entry,
            'end_date_entry': end_date_entry,
            'rate_entry': rate_entry,
            'apply_button': apply_button
        })

        # If advanced options are visible, enable the new apply button
        if self.advanced_frame_visible:
            apply_button.config(state=tk.NORMAL)

        # Force update of scroll region after adding new widgets
        self.master.update_idletasks()
        self._on_frame_configure(None)

    def _delete_rate_range_section(self, frame_to_delete, index_to_delete):
        """Deletes a dynamically added rate range section."""
        frame_to_delete.destroy() # Destroy the Tkinter frame and its widgets

        # Remove the section from our tracking list
        # Rebuild the list to avoid issues with pop/del and subsequent indices
        self.rate_range_entries = [
            section for i, section in enumerate(self.rate_range_entries)
            if i != index_to_delete
        ]

        # Re-index the commands for remaining apply buttons (important if deleting from middle)
        for i, section in enumerate(self.rate_range_entries):
            section['apply_button'].config(command=lambda current_idx=i: self.apply_rate_for_specific_range(current_idx))

        # Force update of scroll region after removing widgets
        self.master.update_idletasks()
        self._on_frame_configure(None)
        self.status_label.config(text=f"Rate Range section {index_to_delete + 1} deleted.")


    def apply_entire_rate(self):
        """Applies a user-defined rate to all rows in the 'Rate' column."""
        if self.df_cleaned is None:
            messagebox.showwarning("No Data", "Please clean data first using 'Clean Data (Basic)' button.")
            return

        rate_str = self.entire_rate_entry.get()
        try:
            rate = float(rate_str)
            # Ensure 'Rate' column exists (already initialized in _parse_and_initial_clean)
            self.df_cleaned['Rate'] = rate
            # Calculate 'Total Balance'
            self.df_cleaned['Total Balance'] = self.df_cleaned['Sell'] * self.df_cleaned['Rate']
            self.status_label.config(text=f"Applied rate {rate:.3f} to all rows and updated 'Total Balance'.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the entire rate.")
            self.status_label.config(text="Error: Invalid rate input.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred applying entire rate: {e}")
            self.status_label.config(text=f"Error: {e}")

    def apply_rate_for_specific_range(self, index):
        """Applies a user-defined rate to rows within a specific date range section."""
        if self.df_cleaned is None:
            messagebox.showwarning("No Data", "Please clean data first using 'Clean Data (Basic)' button.")
            return

        section = self.rate_range_entries[index]
        start_date_str = section['start_date_entry'].get()
        end_date_str = section['end_date_entry'].get()
        rate_str = section['rate_entry'].get()

        try:
            start_date = pd.to_datetime(start_date_str, format='%d-%m-%Y')
            end_date = pd.to_datetime(end_date_str, format='%d-%m-%Y')
            rate = float(rate_str)

            # Ensure 'Rate' column exists (already initialized in _parse_and_initial_clean)
            # Apply rate to rows within the date range
            date_mask = (self.df_cleaned['Date'] >= start_date) & (self.df_cleaned['Date'] <= end_date)
            rows_affected = self.df_cleaned.loc[date_mask].shape[0]
            self.df_cleaned.loc[date_mask, 'Rate'] = rate
            
            # Calculate 'Total Balance' for the affected rows
            self.df_cleaned.loc[date_mask, 'Total Balance'] = self.df_cleaned.loc[date_mask, 'Sell'] * self.df_cleaned.loc[date_mask, 'Rate']

            self.status_label.config(text=f"Applied rate {rate:.3f} to {rows_affected} rows between {start_date_str} and {end_date_str}. 'Total Balance' updated.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please ensure dates are DD-MM-YYYY and rate is a valid number.")
            self.status_label.config(text="Error: Invalid date/rate input.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred applying rate for range: {e}")
            self.status_label.config(text=f"Error: {e}")

    def delete_rows_in_range(self):
        """Deletes rows within a specified date range."""
        if self.df_cleaned is None:
            messagebox.showwarning("No Data", "Please clean data first using 'Clean Data (Basic)' button.")
            return

        start_date_str = self.delete_start_date_entry.get()
        end_date_str = self.delete_end_date_entry.get()

        try:
            start_date = pd.to_datetime(start_date_str, format='%d-%m-%Y')
            end_date = pd.to_datetime(end_date_str, format='%d-%m-%Y')

            initial_rows_before_delete = len(self.df_cleaned)
            # Create a mask for rows NOT in the date range to keep them
            self.df_cleaned = self.df_cleaned[
                (self.df_cleaned['Date'] < start_date) | 
                (self.df_cleaned['Date'] > end_date) |
                (self.df_cleaned['Date'].isna()) # Keep rows without dates (like Balance B/f)
            ].copy()

            rows_deleted = initial_rows_before_delete - len(self.df_cleaned)
            self.status_label.config(text=f"Deleted {rows_deleted} rows between {start_date_str} and {end_date_str}.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please ensure dates are in DD-MM-YYYY format.")
            self.status_label.config(text="Error: Invalid date input.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred deleting rows: {e}")
            self.status_label.config(text=f"Error: {e}")

    def save_cleaned_csv(self):
        """
        Prompts the user to save the current self.df_cleaned to a CSV file,
        including month change separators and a total row.
        """
        if self.df_cleaned is None or self.df_cleaned.empty:
            messagebox.showwarning("No Data", "No data to save. Please clean a file first.")
            return

        self.status_label.config(text="Saving structured CSV... Please wait.")
        self.master.update_idletasks()

        # Sort by Date again before saving to ensure correct month grouping after advanced operations
        # Rows with NaT (e.g., 'Balance B/f') will be placed at the beginning
        df_to_save = self.df_cleaned.sort_values(by='Date', na_position='first').copy()

        output_file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"structured_{os.path.basename(self.input_file_path).split('.')[0]}.csv" if self.input_file_path else "structured_data.csv"
        )

        if output_file_path:
            try:
                # Manually write to CSV to insert separators and totals
                with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)

                    # Define final columns for output
                    final_output_cols = ['Date', 'Inv. No.', 'Purchase', 'Sell', 'Stock'] # Updated names
                    if 'Rate' in df_to_save.columns:
                        final_output_cols.append('Rate')
                    if 'Total Balance' in df_to_save.columns:
                        final_output_cols.append('Total Balance')
                    writer.writerow(final_output_cols)

                    # Removed month change separator logic as per user request
                    # current_month = None
                    for index, row in df_to_save.iterrows():
                        # # Handle month change separator (removed)
                        # if pd.notna(row['Date']):
                        #     row_month = row['Date'].month
                        #     if current_month is not None and row_month != current_month:
                        #         writer.writerow([])
                        #         writer.writerow([])
                        #     current_month = row_month

                        # Format Date for output as DD-MM-YYYY
                        display_date = row['Date'].strftime('%d-%m-%Y') if pd.notna(row['Date']) else ''

                        # Prepare row data, formatting numerical values to 3 decimal places
                        row_data = [
                            display_date,
                            row['Inv. No.'] if pd.notna(row['Inv. No.']) else '',
                            f"{row['Purchase']:.3f}" if pd.notna(row['Purchase']) else '', # Updated name
                            f"{row['Sell']:.3f}" if pd.notna(row['Sell']) else '',         # Updated name
                            f"{row['Stock']:.3f}" if pd.notna(row['Stock']) else ''        # Updated name
                        ]
                        if 'Rate' in df_to_save.columns:
                            row_data.append(f"{row['Rate']:.3f}" if pd.notna(row['Rate']) else '')
                        if 'Total Balance' in df_to_save.columns:
                            row_data.append(f"{row['Total Balance']:.3f}" if pd.notna(row['Total Balance']) else '')
                        writer.writerow(row_data)

                    # Calculate totals
                    total_purchase = df_to_save['Purchase'].sum() # Updated name
                    total_sell = df_to_save['Sell'].sum()         # Updated name
                    # The final stock is the last stock value in the cleaned data
                    final_stock = df_to_save['Stock'].iloc[-1] if not df_to_save.empty else 0.0 # Updated name
                    total_total_balance = df_to_save['Total Balance'].sum() if 'Total Balance' in df_to_save.columns else 0.0


                    # Write total row
                    writer.writerow([]) # Optional empty row before totals for better separation
                    total_row_data = [
                        '', # Date column empty for total row
                        'TOTAL', # Inv. No. column for total label
                        f"{total_purchase:.3f}",
                        f"{total_sell:.3f}",
                        f"{final_stock:.3f}"
                    ]
                    if 'Rate' in df_to_save.columns:
                        total_row_data.append('') # Empty for Rate column in total row
                    if 'Total Balance' in df_to_save.columns:
                        total_row_data.append(f"{total_total_balance:.3f}") # Add total for Total Balance
                    writer.writerow(total_row_data)

                messagebox.showinfo(
                    "Success",
                    f"Structured CSV saved successfully to:\n{os.path.basename(output_file_path)}"
                )
                self.status_label.config(text=f"Structured CSV saved to {os.path.basename(output_file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during saving the CSV: {e}")
                self.status_label.config(text=f"Error during save: {e}")
        else:
            self.status_label.config(text="Save operation cancelled.")

        # No need to re-enable process_button here, as it's not a direct action button anymore.
        # Buttons are managed by their respective actions.

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVCleanerApp(root)
    root.mainloop()
