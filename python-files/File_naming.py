import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
from pypdf import PdfReader, PdfWriter
import re
import os
from pathlib import Path
import threading
import logging
from typing import List, Tuple
import sys

class CertificateProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Certificate Processor - Split PDF into Individual Certificates")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="individual_certificates")
        self.student_names = []
        self.processing = False
        
        # Setup GUI
        self.setup_gui()
        self.setup_logging()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Certificate Processor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # PDF file selection
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_pdf).grid(row=0, column=2, pady=5)
        
        # CSV file selection
        ttk.Label(file_frame, text="CSV File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.csv_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_csv).grid(row=1, column=2, pady=5)
        
        # Output directory
        ttk.Label(file_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # CSV column selection frame
        self.column_frame = ttk.LabelFrame(main_frame, text="CSV Column Selection", padding="10")
        self.column_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        self.column_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.column_frame, text="Name Column:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(self.column_frame, textvariable=self.column_var, 
                                        state="readonly", width=30)
        self.column_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(self.column_frame, text="Load CSV", command=self.load_csv_columns).grid(row=0, column=2, pady=5)
        
        # File info section
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="10")
        info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=4, width=70, state='disabled')
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process Certificates", 
                                     command=self.start_processing, style="Accent.TButton")
        self.process_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to process certificates", 
                                     foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=3)
        
        # Log output section
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
    def setup_logging(self):
        """Setup logging to display in the GUI"""
        # Create custom handler for GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                self.text_widget.update()
        
        # Setup logger
        self.logger = logging.getLogger('CertificateProcessor')
        self.logger.setLevel(logging.INFO)
        
        # Add GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(gui_handler)
        
    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            
    def browse_csv(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_path.set(filename)
            
    def browse_output(self):
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
            
    def load_csv_columns(self):
        """Load and display available columns from CSV"""
        if not self.csv_path.get():
            messagebox.showerror("Error", "Please select a CSV file first")
            return
            
        try:
            df = pd.read_csv(self.csv_path.get())
            columns = list(df.columns)
            self.column_combo['values'] = columns
            
            # Auto-select common name columns
            common_names = ['name', 'student_name', 'full_name', 'Name', 'Student Name', 'Full Name']
            for name in common_names:
                if name in columns:
                    self.column_var.set(name)
                    break
            else:
                # If no common name found, select first column
                if columns:
                    self.column_var.set(columns[0])
                    
            self.update_file_info()
            messagebox.showinfo("Success", f"Loaded {len(columns)} columns from CSV")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading CSV: {str(e)}")
            
    def update_file_info(self):
        """Update file information display"""
        info_lines = []
        
        # PDF info
        if self.pdf_path.get():
            try:
                reader = PdfReader(self.pdf_path.get())
                pdf_pages = len(reader.pages)
                info_lines.append(f"PDF: {pdf_pages} pages")
            except Exception as e:
                info_lines.append(f"PDF: Error reading file - {str(e)}")
        
        # CSV info
        if self.csv_path.get() and self.column_var.get():
            try:
                df = pd.read_csv(self.csv_path.get())
                names = df[self.column_var.get()].astype(str).str.strip().tolist()
                names = [name for name in names if name and name.lower() != 'nan']
                info_lines.append(f"CSV: {len(names)} student names")
                
                # Show sample names
                if names:
                    sample = names[:3]
                    info_lines.append(f"Sample names: {', '.join(sample)}")
                    
            except Exception as e:
                info_lines.append(f"CSV: Error reading file - {str(e)}")
        
        # Update display
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, '\n'.join(info_lines))
        self.info_text.config(state='disabled')
        
    def sanitize_filename(self, filename: str) -> str:
        """Remove or replace characters that are not allowed in filenames"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        sanitized = sanitized.replace(' ', '_')
        
        if not sanitized:
            sanitized = "unnamed_certificate"
            
        return sanitized
    
    def validate_inputs(self) -> bool:
        """Validate all inputs before processing"""
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return False
            
        if not self.csv_path.get():
            messagebox.showerror("Error", "Please select a CSV file")
            return False
            
        if not self.column_var.get():
            messagebox.showerror("Error", "Please select a name column from CSV")
            return False
            
        if not Path(self.pdf_path.get()).exists():
            messagebox.showerror("Error", "PDF file does not exist")
            return False
            
        if not Path(self.csv_path.get()).exists():
            messagebox.showerror("Error", "CSV file does not exist")
            return False
            
        return True
        
    def start_processing(self):
        """Start the certificate processing in a separate thread"""
        if self.processing:
            return
            
        if not self.validate_inputs():
            return
            
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing in background thread
        self.processing = True
        self.process_btn.config(state='disabled', text='Processing...')
        self.progress.start()
        self.status_label.config(text="Processing certificates...", foreground="orange")
        
        thread = threading.Thread(target=self.process_certificates)
        thread.daemon = True
        thread.start()
        
    def process_certificates(self):
        """Main processing function"""
        try:
            # Load student names
            df = pd.read_csv(self.csv_path.get())
            names = df[self.column_var.get()].astype(str).str.strip().tolist()
            names = [name for name in names if name and name.lower() != 'nan']
            
            # Handle duplicates
            seen = {}
            processed_names = []
            for name in names:
                if name in seen:
                    seen[name] += 1
                    processed_names.append(f"{name}_{seen[name]}")
                else:
                    seen[name] = 0
                    processed_names.append(name)
            
            # Load PDF
            reader = PdfReader(self.pdf_path.get())
            pdf_pages = len(reader.pages)
            
            self.logger.info(f"PDF pages: {pdf_pages}, CSV entries: {len(processed_names)}")
            
            # Create output directory
            output_path = Path(self.output_dir.get())
            output_path.mkdir(exist_ok=True)
            
            # Process certificates
            certificates_to_process = min(pdf_pages, len(processed_names))
            success_count = 0
            failed_count = 0
            
            for i in range(certificates_to_process):
                try:
                    # Create new PDF for this page
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    
                    # Create filename
                    sanitized_name = self.sanitize_filename(processed_names[i])
                    output_filename = f"{sanitized_name}.pdf"
                    file_path = output_path / output_filename
                    
                    # Write PDF
                    with open(file_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    success_count += 1
                    
                    if (i + 1) % 10 == 0:
                        self.logger.info(f"Processed {i + 1}/{certificates_to_process} certificates")
                        
                except Exception as e:
                    self.logger.error(f"Error processing certificate {i + 1} for '{processed_names[i]}': {e}")
                    failed_count += 1
                    continue
            
            # Final results
            self.logger.info(f"Processing complete!")
            self.logger.info(f"Successfully created: {success_count} certificate files")
            self.logger.info(f"Failed: {failed_count} certificate files")
            self.logger.info(f"Output location: {output_path.absolute()}")
            
            # Update GUI
            self.root.after(0, self.processing_complete, success_count, failed_count)
            
        except Exception as e:
            self.logger.error(f"Error in processing: {e}")
            self.root.after(0, self.processing_error, str(e))
            
    def processing_complete(self, success_count, failed_count):
        """Called when processing is complete"""
        self.processing = False
        self.process_btn.config(state='normal', text='Process Certificates')
        self.progress.stop()
        self.status_label.config(text=f"Complete! {success_count} successful, {failed_count} failed", 
                                foreground="green")
        
        # Show completion message
        messagebox.showinfo("Processing Complete", 
                           f"Successfully processed {success_count} certificates!\n"
                           f"Failed: {failed_count}\n"
                           f"Output location: {self.output_dir.get()}")
        
    def processing_error(self, error_msg):
        """Called when processing encounters an error"""
        self.processing = False
        self.process_btn.config(state='normal', text='Process Certificates')
        self.progress.stop()
        self.status_label.config(text="Error occurred during processing", foreground="red")
        messagebox.showerror("Processing Error", f"An error occurred:\n{error_msg}")

def main():
    root = tk.Tk()
    app = CertificateProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()