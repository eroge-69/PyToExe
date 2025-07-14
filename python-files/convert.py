import pandas as pd
from docx import Document
import os
import zipfile
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import re

class WordExcelFiller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Word Document Gap Filler")
        self.root.geometry("700x650")  # Increased height for new control
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.word_template_path = tk.StringVar()
        self.excel_data_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to process documents")
        self.group_by_var = tk.StringVar()
        self.generated_files = []
        self.zip_path = None
        
        # Set default output folder
        self.output_folder.set(os.path.join(os.path.expanduser("~"), "Desktop", "Generated_Documents"))
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 Word Document Gap Filler", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="15")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Word template selection
        ttk.Label(file_frame, text="Word Template:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        word_entry = ttk.Entry(file_frame, textvariable=self.word_template_path, width=60)
        word_entry.grid(row=0, column=1, pady=5, padx=(10, 5))
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_word_template).grid(row=0, column=2, pady=5)
        
        # Excel data selection
        ttk.Label(file_frame, text="Excel Data:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        excel_entry = ttk.Entry(file_frame, textvariable=self.excel_data_path, width=60)
        excel_entry.grid(row=1, column=1, pady=5, padx=(10, 5))
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_excel_data).grid(row=1, column=2, pady=5)
        
        # Group by selection
        ttk.Label(file_frame, text="Group By Column:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.group_by_dropdown = ttk.Combobox(file_frame, textvariable=self.group_by_var, state='readonly', width=57)
        self.group_by_dropdown.grid(row=2, column=1, pady=5, padx=(10, 5), sticky=tk.W)
        ttk.Label(file_frame, text="(Leave empty for individual docs)").grid(row=3, column=1, sticky=tk.W, padx=(10, 5))
        
        # Output folder selection
        ttk.Label(file_frame, text="Output Folder:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(file_frame, textvariable=self.output_folder, width=60)
        output_entry.grid(row=4, column=1, pady=5, padx=(10, 5))
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_output_folder).grid(row=4, column=2, pady=5)
        
        # Instructions section
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="15")
        instructions_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        instructions_text = """
🔹 Create a Word template with placeholders like {{name}}, {{date}}, {{company}}, etc.
🔹 Prepare an Excel file with columns matching your placeholder names
🔹 Select a column to group by (or leave empty for individual documents)
🔹 Generated documents will be automatically zipped for download
🔹 Supported formats: .docx for Word, .xlsx/.xls for Excel
        """
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, 
                                     justify=tk.LEFT, font=("Arial", 9))
        instructions_label.grid(row=0, column=0, sticky=tk.W)
        
        # Processing section
        process_frame = ttk.LabelFrame(main_frame, text="Processing", padding="15")
        process_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Process button
        self.process_btn = ttk.Button(process_frame, text="🚀 Process Documents", 
                                     command=self.start_processing)
        self.process_btn.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Progress section
        ttk.Label(process_frame, text="Progress:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.progress_bar = ttk.Progressbar(process_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=1, column=1, pady=5, padx=(10, 5), sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(process_frame, textvariable=self.status_var, 
                                     font=("Arial", 10), foreground="blue")
        self.status_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Download section
        download_frame = ttk.LabelFrame(main_frame, text="Download", padding="15")
        download_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Download button (initially disabled)
        self.download_btn = ttk.Button(download_frame, text="📥 Download ZIP File", 
                                      command=self.download_zip, state=tk.DISABLED)
        self.download_btn.grid(row=0, column=0, pady=10)
        
        # Results info
        self.results_label = ttk.Label(download_frame, text="", font=("Arial", 9))
        self.results_label.grid(row=1, column=0, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
        process_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def browse_word_template(self):
        filename = filedialog.askopenfilename(
            title="Select Word Template (.docx)",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if filename:
            self.word_template_path.set(filename)
    
    def browse_excel_data(self):
        filename = filedialog.askopenfilename(
            title="Select Excel Data File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if filename:
            self.excel_data_path.set(filename)
            try:
                df = pd.read_excel(filename)
                self.group_by_dropdown['values'] = list(df.columns)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read Excel columns: {str(e)}")
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def validate_inputs(self):
        if not self.word_template_path.get():
            messagebox.showerror("Error", "Please select a Word template file")
            return False
        
        if not self.excel_data_path.get():
            messagebox.showerror("Error", "Please select an Excel data file")
            return False
        
        if not os.path.exists(self.word_template_path.get()):
            messagebox.showerror("Error", "Word template file not found")
            return False
        
        if not os.path.exists(self.excel_data_path.get()):
            messagebox.showerror("Error", "Excel data file not found")
            return False
        
        return True
    
    def start_processing(self):
        if not self.validate_inputs():
            return
        
        # Disable process button during processing
        self.process_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Starting processing...")
        
        # Start processing in a separate thread
        threading.Thread(target=self.process_documents, daemon=True).start()
    
    def process_documents(self):
        try:
            # Create output directory
            output_dir = self.output_folder.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Read Excel data
            self.status_var.set("Reading Excel data...")
            self.progress_var.set(10)
            df = pd.read_excel(self.excel_data_path.get())
            
            if len(df) == 0:
                raise ValueError("Excel file is empty")
            
            # Get group by column
            group_by_column = self.group_by_var.get()
            
            # Load Word template
            self.status_var.set("Loading Word template...")
            self.progress_var.set(20)
            template_doc = Document(self.word_template_path.get())
            placeholders = self.find_placeholders(template_doc)
            
            self.generated_files = []
            
            if group_by_column and group_by_column in df.columns:
                # Process grouped documents
                self.status_var.set(f"Processing grouped by {group_by_column}...")
                grouped = df.groupby(group_by_column)
                total_groups = len(grouped)
                
                for idx, (group_name, group_df) in enumerate(grouped):
                    progress = 20 + (idx / total_groups) * 60
                    self.progress_var.set(progress)
                    self.status_var.set(f"Processing group {idx + 1} of {total_groups}: {group_name}")
                    
                    new_doc = Document(self.word_template_path.get())
                    
                    # Create combined data for all placeholders
                    data = {}
                    for col in df.columns:
                        if col == group_by_column:
                            data[col] = group_name
                        else:
                            values = group_df[col].dropna().astype(str).tolist()
                            data[col] = "\n".join(values)
                    
                    self.replace_placeholders(new_doc, data, placeholders)
                    
                    filename = f"Group_{group_name}.docx".replace("/", "_")
                    filepath = os.path.join(output_dir, filename)
                    new_doc.save(filepath)
                    self.generated_files.append(filepath)
            else:
                # Process individual documents
                self.status_var.set("Processing individual documents...")
                total_rows = len(df)
                
                for idx, row in df.iterrows():
                    progress = 20 + (idx / total_rows) * 60
                    self.progress_var.set(progress)
                    self.status_var.set(f"Processing document {idx + 1} of {total_rows}")
                    
                    new_doc = Document(self.word_template_path.get())
                    self.replace_placeholders(new_doc, row.to_dict(), placeholders)
                    
                    filename = f"Document_{idx + 1}.docx"
                    if 'name' in row and pd.notna(row['name']):
                        filename = f"{row['name']}.docx".replace("/", "_")
                    
                    filepath = os.path.join(output_dir, filename)
                    new_doc.save(filepath)
                    self.generated_files.append(filepath)
            
            # Create ZIP file
            self.status_var.set("Creating ZIP file...")
            self.progress_var.set(85)
            
            zip_filename = f"generated_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            self.zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(self.zip_path, 'w') as zipf:
                for file_path in self.generated_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            # Update UI
            self.progress_var.set(100)
            self.status_var.set(f"✅ Successfully processed {len(self.generated_files)} documents!")
            self.results_label.config(text=f"Generated {len(self.generated_files)} documents")
            
            # Enable download button
            self.download_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("❌ Processing failed")
        
        finally:
            # Re-enable process button
            self.process_btn.config(state=tk.NORMAL)
    
    def find_placeholders(self, doc):
        """Find all placeholders in the document"""
        placeholders = set()
        
        # Search in paragraphs
        for paragraph in doc.paragraphs:
            matches = re.findall(r'\{\{(\w+)\}\}', paragraph.text)
            placeholders.update(matches)
        
        # Search in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    matches = re.findall(r'\{\{(\w+)\}\}', cell.text)
                    placeholders.update(matches)
        
        return list(placeholders)
    
    def replace_placeholders(self, doc, data, placeholders):
        """Replace placeholders with actual data"""
        
        # Replace in paragraphs
        for paragraph in doc.paragraphs:
            for placeholder in placeholders:
                if placeholder in data:
                    placeholder_text = f"{{{{{placeholder}}}}}"
                    if placeholder_text in paragraph.text:
                        paragraph.text = paragraph.text.replace(
                            placeholder_text, 
                            str(data[placeholder])
                        )
        
        # Replace in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for placeholder in placeholders:
                        if placeholder in data:
                            placeholder_text = f"{{{{{placeholder}}}}}"
                            if placeholder_text in cell.text:
                                cell.text = cell.text.replace(
                                    placeholder_text,
                                    str(data[placeholder])
                                )
    
    def download_zip(self):
        if not self.zip_path or not os.path.exists(self.zip_path):
            messagebox.showerror("Error", "ZIP file not found")
            return
        
        # Let user choose where to save
        save_path = filedialog.asksaveasfilename(
            title="Save ZIP file",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialname=os.path.basename(self.zip_path)
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(self.zip_path, save_path)
                messagebox.showinfo("Success", f"ZIP file saved to: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save ZIP file: {str(e)}")
    
    def run(self):
        self.root.mainloop()

def main():
    app = WordExcelFiller()
    app.run()

if __name__ == "__main__":
    main()