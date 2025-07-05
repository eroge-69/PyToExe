import pandas as pd
import os
import re
import zipfile
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from logging.handlers import QueueHandler
import queue
import threading
from tqdm import tqdm
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextHandler(logging.Handler):
    """Custom logging handler to send logs to a Tkinter Text widget"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.update()

def clean_sheet_name(name):
    """Sanitize sheet name by removing or replacing invalid characters."""
    name = str(name)[:31]
    name = re.sub(r'[\/\\*?:\[\]]', '_', name)
    return name if name.strip() else 'Sheet'

def split_and_group_excel(input_file, group_column, output_zip, selected_sheets, status_text, progress_var, total_groups):
    """Process Excel file and create zip archive of grouped data with case-insensitive grouping."""
    input_dir = os.path.dirname(input_file) or '.'
    output_dir = os.path.join(input_dir, "SEPERATED_DATA")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    created_files = []

    try:
        # Read Excel file
        logger.info(f"Reading Excel file: {input_file}")
        excel_data = pd.read_excel(input_file, sheet_name=None, header=0)
        
        # Calculate total groups for progress
        processed_groups = 0
        progress_per_group = 100.0 / total_groups if total_groups > 0 else 100.0

        for sheet_name, df in excel_data.items():
            if selected_sheets and sheet_name not in selected_sheets:
                logger.info(f"Skipping sheet: {sheet_name}")
                continue
            logger.info(f"Processing sheet: {sheet_name}")
            if isinstance(group_column, str):
                if group_column not in df.columns:
                    logger.warning(f"Column '{group_column}' not found in sheet '{sheet_name}', skipping")
                    continue
                group_col = group_column
            else:
                if group_column >= len(df.columns):
                    logger.warning(f"Column index {group_column} out of range in sheet '{sheet_name}', skipping")
                    continue
                group_col = df.columns[group_column]
            
            # Normalize group column to lowercase
            df['temp_group_col'] = df[group_col].astype(str).str.lower()
            df[group_col] = df[group_col].fillna("Blank")
            df['temp_group_col'] = df['temp_group_col'].fillna("blank")
            group_col_name = 'temp_group_col'
            
            # Group by normalized column
            for group_value, group in df.groupby(group_col_name):
                # Use original group value for sheet name (first occurrence)
                original_group_value = group[group_col].iloc[0]
                sheet_name_clean = clean_sheet_name(f"{sheet_name}_{original_group_value}")
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False, dir=output_dir) as temp_file:
                    temp_file_path = temp_file.name
                    # Drop temporary column before saving
                    group = group.drop(columns=['temp_group_col'])
                    group.to_excel(temp_file_path, index=False, sheet_name=sheet_name_clean)
                    created_files.append((temp_file_path, sheet_name_clean))
                    logger.info(f"Created temporary file: {temp_file_path}")
                
                # Update progress
                processed_groups += 1
                progress_var.set(processed_groups * progress_per_group)
                status_text.update()

        # Create zip file
        logger.info(f"Creating zip archive: {output_zip}")
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, sheet_name in created_files:
                safe_sheet_name = clean_sheet_name(sheet_name)
                arcname = os.path.join("SEPERATED_DATA", f"{safe_sheet_name}.xlsx")
                zipf.write(file_path, arcname)
        logger.info(f"Created zip archive: {output_zip}")
    
    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found")
        messagebox.showerror("Error", f"Input file '{input_file}' not found")
    except ValueError as ve:
        logger.error(f"Error reading Excel file: {str(ve)}")
        messagebox.showerror("Error", f"Error reading Excel file: {str(ve)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    finally:
        # Clean up temporary files
        for file_path, _ in created_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            logger.info(f"Cleaned up temporary folder: {output_dir}")
        
        # Ensure progress bar reaches 100%
        progress_var.set(100)
        status_text.update()
    
    logger.info(f"Successfully created {output_zip} containing all grouped Excel files.")
    messagebox.showinfo("Success", f"Successfully created {output_zip}")

class ExcelSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Data Splitter")
        self.root.geometry("800x600")

        # Create main canvas and scrollbar
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)   # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)   # Linux

        # Variables
        self.input_file = tk.StringVar()
        self.output_zip = tk.StringVar(value="Separated_Data_Archive.zip")
        self.group_column = tk.StringVar()
        self.columns = []
        self.sheets = []
        self.selected_sheets = []
        self.progress = tk.DoubleVar(value=0)

        # GUI Elements (inside scrollable_frame)
        tk.Label(self.scrollable_frame, text="Excel Data Splitter", font=("Arial", 14, "bold")).pack(pady=10)

        # Input File Selection
        tk.Label(self.scrollable_frame, text="Input Excel File:").pack(anchor="w", padx=10)
        tk.Entry(self.scrollable_frame, textvariable=self.input_file, width=50).pack(padx=10, pady=5)
        tk.Button(self.scrollable_frame, text="Browse", command=self.browse_input).pack(pady=5)

        # Sheet Selection
        tk.Label(self.scrollable_frame, text="Select Sheets to Process (leave empty for all):").pack(anchor="w", padx=10)
        self.sheet_listbox = tk.Listbox(self.scrollable_frame, selectmode=tk.MULTIPLE, height=4, width=50)
        self.sheet_listbox.pack(padx=10, pady=5)
        tk.Button(self.scrollable_frame, text="Load Sheets", command=self.load_sheets).pack(pady=5)

        # Group Column Selection
        tk.Label(self.scrollable_frame, text="Group By Column:").pack(anchor="w", padx=10)
        self.column_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.group_column, state="readonly")
        self.column_dropdown.pack(padx=10, pady=5)
        tk.Button(self.scrollable_frame, text="Load Columns", command=self.load_columns).pack(pady=5)

        # Output Zip File
        tk.Label(self.scrollable_frame, text="Output Zip File:").pack(anchor="w", padx=10)
        tk.Entry(self.scrollable_frame, textvariable=self.output_zip, width=50).pack(padx=10, pady=5)
        tk.Button(self.scrollable_frame, text="Browse Output Directory", command=self.browse_output).pack(pady=5)

        # Data Preview
        tk.Label(self.scrollable_frame, text="Data Preview:").pack(anchor="w", padx=10)
        self.preview_frame = tk.Frame(self.scrollable_frame)
        self.preview_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.preview_tree = ttk.Treeview(self.preview_frame, show="headings", height=5)
        self.preview_tree_scroll_x = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree_scroll_y = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(xscrollcommand=self.preview_tree_scroll_x.set, yscrollcommand=self.preview_tree_scroll_y.set)
        self.preview_tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.preview_tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Progress Bar
        tk.Label(self.scrollable_frame, text="Progress:").pack(anchor="w", padx=10)
        self.progress_bar = ttk.Progressbar(self.scrollable_frame, variable=self.progress, maximum=100, length=400)
        self.progress_bar.pack(padx=10, pady=5)

        # Status Text Area
        tk.Label(self.scrollable_frame, text="Status:").pack(anchor="w", padx=10)
        self.status_text = tk.Text(self.scrollable_frame, height=6, width=60, state="normal")
        self.status_text.pack(padx=10, pady=5)
        # Attach logging to status text
        text_handler = TextHandler(self.status_text)
        logger.addHandler(text_handler)

        # Buttons
        tk.Button(self.scrollable_frame, text="Save Log", command=self.save_log).pack(pady=5)
        tk.Button(self.scrollable_frame, text="Start Processing", command=self.start_processing).pack(pady=10)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for the canvas."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.input_file.set(file_path)
            self.load_sheets()
            self.load_columns()
            self.update_preview()

    def browse_output(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_zip.set(os.path.join(output_dir, "Separated_Data_Archive.zip"))

    def load_sheets(self):
        input_file = self.input_file.get()
        if not input_file:
            messagebox.showwarning("Warning", "Please select an input Excel file first")
            return
        try:
            excel_data = pd.read_excel(input_file, sheet_name=None, header=0)
            self.sheets = list(excel_data.keys())
            self.sheet_listbox.delete(0, tk.END)
            for sheet in self.sheets:
                self.sheet_listbox.insert(tk.END, sheet)
            self.update_preview()
        except Exception as e:
            logger.error(f"Error loading sheets: {str(e)}")
            messagebox.showerror("Error", f"Error loading sheets: {str(e)}")

    def load_columns(self):
        self.progress.set(0)  # Reset progress bar
        input_file = self.input_file.get()
        if not input_file:
            messagebox.showwarning("Warning", "Please select an input Excel file first")
            return
        try:
            df = pd.read_excel(input_file, sheet_name=0, header=0)
            self.columns = df.columns.tolist()
            self.column_dropdown['values'] = self.columns
            if self.columns:
                self.group_column.set(self.columns[0])
        except Exception as e:
            logger.error(f"Error loading columns: {str(e)}")
            messagebox.showerror("Error", f"Error loading columns: {str(e)}")

    def update_preview(self):
        """Update the preview table with data from selected sheets or first sheet."""
        input_file = self.input_file.get()
        if not input_file:
            return

        # Clear existing preview
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_tree['columns'] = []
        for col in self.preview_tree['columns']:
            self.preview_tree.heading(col, text="")
            self.preview_tree.column(col, width=0)

        try:
            # Get selected sheets
            selected_indices = self.sheet_listbox.curselection()
            selected_sheets = [self.sheets[i] for i in selected_indices] if selected_indices else [self.sheets[0]] if self.sheets else []

            if not selected_sheets:
                return

            # Read data from the first selected sheet (fixed 5 rows, header at row 0)
            df = pd.read_excel(input_file, sheet_name=selected_sheets[0], header=0, nrows=5)
            columns = df.columns.tolist()
            
            # Set up Treeview columns
            self.preview_tree['columns'] = columns
            for col in columns:
                self.preview_tree.heading(col, text=col)
                self.preview_tree.column(col, width=100, anchor="w")

            # Insert data
            for _, row in df.iterrows():
                self.preview_tree.insert("", tk.END, values=[str(val) for val in row])

            # Update canvas scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        except Exception as e:
            logger.error(f"Error loading preview: {str(e)}")
            messagebox.showerror("Error", f"Error loading preview: {str(e)}")

    def save_log(self):
        """Save status log to a file."""
        output_dir = os.path.dirname(self.output_zip.get()) or '.'
        log_file = os.path.join(output_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(log_file, 'w') as f:
                f.write(self.status_text.get(1.0, tk.END))
            logger.info(f"Saved log to: {log_file}")
            messagebox.showinfo("Success", f"Log saved to: {log_file}")
        except Exception as e:
            logger.error(f"Error saving log: {str(e)}")
            messagebox.showerror("Error", f"Error saving log: {str(e)}")

    def count_total_groups(self, input_file, group_column, selected_sheets):
        """Count total groups across selected sheets for progress bar with case-insensitive grouping."""
        total_groups = 0
        try:
            excel_data = pd.read_excel(input_file, sheet_name=None, header=0)
            for sheet_name, df in excel_data.items():
                if selected_sheets and sheet_name not in selected_sheets:
                    continue
                if isinstance(group_column, str):
                    if group_column not in df.columns:
                        continue
                    group_col = group_column
                else:
                    if group_column >= len(df.columns):
                        continue
                    group_col = df.columns[group_column]
                df['temp_group_col'] = df[group_col].astype(str).str.lower()
                df['temp_group_col'] = df['temp_group_col'].fillna("blank")
                total_groups += len(df.groupby('temp_group_col'))
        except Exception as e:
            logger.error(f"Error counting groups: {str(e)}")
        return total_groups

    def start_processing(self):
        if not self.input_file.get():
            messagebox.showwarning("Warning", "Please select an input Excel file")
            return
        if not self.group_column.get():
            messagebox.showwarning("Warning", "Please select a group column")
            return
        if not self.output_zip.get():
            messagebox.showwarning("Warning", "Please specify an output zip file")
            return

        # Get selected sheets
        selected_indices = self.sheet_listbox.curselection()
        self.selected_sheets = [self.sheets[i] for i in selected_indices] if selected_indices else []

        # Reset progress bar
        self.progress.set(0)
        self.status_text.delete(1.0, tk.END)

        # Count total groups for progress bar
        total_groups = self.count_total_groups(
            self.input_file.get(), self.group_column.get(), self.selected_sheets
        )

        # Run processing in a separate thread
        threading.Thread(target=split_and_group_excel, args=(
            self.input_file.get(),
            self.group_column.get(),
            self.output_zip.get(),
            self.selected_sheets,
            self.status_text,
            self.progress,
            total_groups
        ), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelSplitterApp(root)
    root.mainloop()
