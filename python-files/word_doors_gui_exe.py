import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sys
import os
from pathlib import Path
import threading

# Handle imports for exe compatibility
try:
    import mammoth
except ImportError:
    mammoth = None

class WordToDoorsConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Word to DOORS CSV Converter")
        self.root.geometry("600x500")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Word to DOORS CSV Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Select Word Document:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Entry(input_frame, textvariable=self.input_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Browse", command=self.browse_input_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Output file selection
        ttk.Label(main_frame, text="Output CSV File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Entry(output_frame, textvariable=self.output_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Convert button
        convert_button = ttk.Button(main_frame, text="Convert to CSV", 
                                   command=self.start_conversion, style="Accent.TButton")
        convert_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log area
        ttk.Label(main_frame, text="Processing Log:").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Word Document",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            input_path = Path(filename)
            output_path = input_path.parent / f"{input_path.stem}_DOORS.csv"
            self.output_file.set(str(output_path))
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save CSV File As",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def log(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """Start conversion in a separate thread"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input Word document")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output CSV file")
            return
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start progress bar
        self.progress.start()
        
        # Run conversion in thread to prevent GUI freezing
        thread = threading.Thread(target=self.convert_document)
        thread.daemon = True
        thread.start()
    
    def convert_document(self):
        """Main conversion logic"""
        try:
            self.log("Starting Word to DOORS CSV conversion...")
            
            # Check if mammoth is available
            if mammoth is None:
                self.log("Error: mammoth library not available. Please install with: pip install mammoth")
                messagebox.showerror("Error", "Required library 'mammoth' not found")
                return
            
            # Extract table from Word
            self.log(f"Reading Word document: {self.input_file.get()}")
            df = self.extract_table_from_word(self.input_file.get())
            
            if df is None:
                self.log("Failed to extract table from Word document")
                messagebox.showerror("Error", "Failed to extract table from Word document")
                return
            
            self.log(f"Extracted table with {len(df)} rows and {len(df.columns)} columns")
            self.log(f"Columns found: {list(df.columns)}")
            
            # Clean column names
            df = self.clean_column_names(df)
            self.log("Column names cleaned")
            
            # Process requirement columns
            df = self.process_requirements_columns(df)
            self.log(f"After processing requirement columns: {len(df)} rows")
            
            # Add Absolute Number column
            df = self.add_absolute_number_column(df)
            self.log("Added Absolute Number column")
            
            # Save to CSV
            df.to_csv(self.output_file.get(), index=False, encoding='utf-8')
            self.log(f"Successfully saved to: {self.output_file.get()}")
            self.log(f"Final CSV has {len(df)} rows and {len(df.columns)} columns")
            
            # Show preview
            self.log("\nPreview of first 3 rows:")
            preview = df.head(3).to_string()
            self.log(preview)
            
            messagebox.showinfo("Success", f"Conversion completed!\n\nOutput saved to:\n{self.output_file.get()}")
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)
        
        finally:
            self.progress.stop()
    
    def extract_table_from_word(self, word_file_path):
        """Extract table data from Word document"""
        try:
            with open(word_file_path, 'rb') as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value
            
            tables = pd.read_html(html_content, header=0)
            
            if not tables:
                raise ValueError("No tables found in the document")
            
            # Get the main table (usually the largest one)
            main_table = max(tables, key=len)
            return main_table
            
        except Exception as e:
            self.log(f"Error reading Word document: {e}")
            return None
    
    def clean_column_names(self, df):
        """Clean and standardize column names"""
        df.columns = [str(col).strip() for col in df.columns]
        
        column_mapping = {
            'Step': '_Step',
            'Action': '_Action', 
            'Expected Result': '_Expected_Result',
            'Expected_Result': '_Expected_Result',
            'T3_COM_Req_Verified': 'T3_COM_Requirements_Verified',
            'T3_COM_Requirements_Verified': 'T3_COM_Requirements_Verified',
            'T3_NAV_Req_Verified': 'T3_NAV_Requirements_Verified',
            'T3_SURV_Req_Verified': 'T3_SURV_Requirements_Verified',
            'Pass/Fail': 'Pass_Fail',
            'Comments': 'Comments'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        return df
    
    def process_requirements_columns(self, df):
        """Process all requirement columns to remove commas and prepare for DOORS"""
        req_columns = ['T3_COM_Requirements_Verified', 'T3_NAV_Requirements_Verified', 'T3_SURV_Requirements_Verified']
        
        existing_req_columns = [col for col in req_columns if col in df.columns]
        
        if not existing_req_columns:
            self.log("No requirement columns found, returning original dataframe")
            return df
        
        self.log(f"Processing requirement columns: {existing_req_columns}")
        
        processed_rows = []
        
        for idx, row in df.iterrows():
            all_requirements = {}
            has_requirements = False
            
            for req_col in existing_req_columns:
                req_value = str(row.get(req_col, ''))
                
                if not (pd.isna(row.get(req_col)) or req_value.strip() == '' or req_value == 'nan'):
                    requirements = [req.strip() for req in req_value.split(',') if req.strip()]
                    all_requirements[req_col] = requirements
                    if requirements:
                        has_requirements = True
                else:
                    all_requirements[req_col] = ['']
            
            if not has_requirements:
                processed_rows.append(row.copy())
            else:
                max_reqs = max(len(reqs) for reqs in all_requirements.values())
                
                for i in range(max_reqs):
                    new_row = row.copy()
                    
                    for req_col in existing_req_columns:
                        reqs = all_requirements[req_col]
                        if i < len(reqs) and reqs[i]:
                            new_row[req_col] = reqs[i]
                        else:
                            new_row[req_col] = ''
                    
                    if i > 0:
                        if '_Action' in new_row:
                            new_row['_Action'] = ''
                        if '_Expected_Result' in new_row:
                            new_row['_Expected_Result'] = ''
                    
                    processed_rows.append(new_row)
        
        return pd.DataFrame(processed_rows)
    
    def add_absolute_number_column(self, df):
        """Add Absolute Number as the first column"""
        df.insert(0, 'Absolute_Number', range(1, len(df) + 1))
        return df

def main():
    root = tk.Tk()
    app = WordToDoorsConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
