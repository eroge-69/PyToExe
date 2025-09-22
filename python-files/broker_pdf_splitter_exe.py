#!/usr/bin/env python3
"""
Broker Route PDF Splitter - Standalone Application
Creates individual PDF files for each broker based on Excel route assignments
100% Offline - No Internet Required - Cybersecurity Safe
"""

import os
import sys
import re
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF for better text extraction

class BrokerPDFSplitter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Broker Route PDF Splitter")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.excel_file = tk.StringVar()
        self.pdf_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.broker_routes = {}
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to start...")
        
        # Set default output directory
        self.output_dir.set(str(Path.home() / "Desktop" / "Broker_Route_PDFs"))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 Broker Route PDF Splitter", 
            font=('Arial', 20, 'bold'),
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            title_frame, 
            text="Split PDF routes by broker assignments - 100% Offline & Secure", 
            font=('Arial', 10),
            fg='#ecf0f1', 
            bg='#2c3e50'
        )
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Step 1: Excel File Selection
        self.create_step_frame(main_frame, "1", "📊 Select Excel File (Broker & Route Mapping)", 0)
        excel_frame = tk.Frame(main_frame, bg='#ffffff', relief='ridge', bd=2)
        excel_frame.pack(fill='x', pady=(0, 20), padx=10, ipady=10)
        
        tk.Label(
            excel_frame, 
            text="Choose Excel file with broker names and route assignments:",
            font=('Arial', 10),
            bg='#ffffff'
        ).pack(pady=(10, 5))
        
        excel_select_frame = tk.Frame(excel_frame, bg='#ffffff')
        excel_select_frame.pack(fill='x', padx=20)
        
        tk.Entry(
            excel_select_frame, 
            textvariable=self.excel_file, 
            font=('Arial', 9),
            state='readonly'
        ).pack(side='left', fill='x', expand=True)
        
        tk.Button(
            excel_select_frame, 
            text="Browse...", 
            command=self.select_excel_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 9, 'bold')
        ).pack(side='right', padx=(10, 0))
        
        # Broker preview area
        self.broker_preview = tk.Text(
            excel_frame, 
            height=6, 
            font=('Courier', 9),
            state='disabled',
            bg='#f8f9fa'
        )
        self.broker_preview.pack(fill='x', padx=20, pady=10)
        
        # Step 2: PDF File Selection
        self.create_step_frame(main_frame, "2", "📄 Select Master PDF (All Routes)", 1)
        pdf_frame = tk.Frame(main_frame, bg='#ffffff', relief='ridge', bd=2)
        pdf_frame.pack(fill='x', pady=(0, 20), padx=10, ipady=10)
        
        tk.Label(
            pdf_frame, 
            text="Choose the complete PDF file containing all route pages:",
            font=('Arial', 10),
            bg='#ffffff'
        ).pack(pady=(10, 5))
        
        pdf_select_frame = tk.Frame(pdf_frame, bg='#ffffff')
        pdf_select_frame.pack(fill='x', padx=20)
        
        tk.Entry(
            pdf_select_frame, 
            textvariable=self.pdf_file, 
            font=('Arial', 9),
            state='readonly'
        ).pack(side='left', fill='x', expand=True)
        
        tk.Button(
            pdf_select_frame, 
            text="Browse...", 
            command=self.select_pdf_file,
            bg='#3498db',
            fg='white',
            font=('Arial', 9, 'bold')
        ).pack(side='right', padx=(10, 0))
        
        # Step 3: Output Directory
        self.create_step_frame(main_frame, "3", "📁 Output Directory", 2)
        output_frame = tk.Frame(main_frame, bg='#ffffff', relief='ridge', bd=2)
        output_frame.pack(fill='x', pady=(0, 20), padx=10, ipady=10)
        
        tk.Label(
            output_frame, 
            text="Choose where to save the split PDF files:",
            font=('Arial', 10),
            bg='#ffffff'
        ).pack(pady=(10, 5))
        
        output_select_frame = tk.Frame(output_frame, bg='#ffffff')
        output_select_frame.pack(fill='x', padx=20)
        
        tk.Entry(
            output_select_frame, 
            textvariable=self.output_dir, 
            font=('Arial', 9)
        ).pack(side='left', fill='x', expand=True)
        
        tk.Button(
            output_select_frame, 
            text="Browse...", 
            command=self.select_output_dir,
            bg='#3498db',
            fg='white',
            font=('Arial', 9, 'bold')
        ).pack(side='right', padx=(10, 0))
        
        # Step 4: Processing
        self.create_step_frame(main_frame, "4", "⚡ Process & Split PDF", 3)
        process_frame = tk.Frame(main_frame, bg='#ffffff', relief='ridge', bd=2)
        process_frame.pack(fill='x', pady=(0, 20), padx=10, ipady=15)
        
        self.process_btn = tk.Button(
            process_frame, 
            text="🚀 Start Processing", 
            command=self.start_processing,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            state='disabled'
        )
        self.process_btn.pack(pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            process_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            process_frame, 
            textvariable=self.status_var,
            font=('Arial', 10),
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.status_label.pack()
        
        # Results area
        self.results_text = tk.Text(
            process_frame, 
            height=8, 
            font=('Courier', 9),
            state='disabled',
            bg='#f8f9fa'
        )
        self.results_text.pack(fill='x', padx=20, pady=10)
        
        # Check if files are selected
        self.excel_file.trace('w', self.check_ready_to_process)
        self.pdf_file.trace('w', self.check_ready_to_process)
        
    def create_step_frame(self, parent, step_num, title, row):
        """Create a step header frame"""
        step_frame = tk.Frame(parent, bg='#34495e', height=40)
        step_frame.pack(fill='x', pady=(10, 5), padx=10)
        step_frame.pack_propagate(False)
        
        # Step number circle
        step_circle = tk.Label(
            step_frame,
            text=step_num,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=3,
            height=1
        )
        step_circle.pack(side='left', padx=(10, 15), pady=8)
        
        # Step title
        step_title = tk.Label(
            step_frame,
            text=title,
            bg='#34495e',
            fg='white',
            font=('Arial', 14, 'bold')
        )
        step_title.pack(side='left', pady=10)
        
    def select_excel_file(self):
        """Select Excel file with broker routes"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if filename:
            self.excel_file.set(filename)
            self.load_excel_file(filename)
            
    def select_pdf_file(self):
        """Select master PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_file.set(filename)
            
    def select_output_dir(self):
        """Select output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
            
    def load_excel_file(self, filename):
        """Load and parse Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(filename, header=None)
            
            # Parse broker routes
            self.broker_routes = {}
            for idx, row in df.iterrows():
                if pd.notnull(row[0]):
                    broker = str(row[0]).strip()
                    routes = [str(item).strip() for item in row[1:] if pd.notnull(item)]
                    # Filter out non-numeric routes
                    routes = [route for route in routes if route.replace('.', '', 1).replace('-', '', 1).isdigit()]
                    if routes:
                        self.broker_routes[broker] = routes
            
            # Update preview
            self.update_broker_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file:\n{str(e)}")
            
    def update_broker_preview(self):
        """Update the broker preview text area"""
        self.broker_preview.config(state='normal')
        self.broker_preview.delete(1.0, tk.END)
        
        if self.broker_routes:
            self.broker_preview.insert(tk.END, f"Found {len(self.broker_routes)} brokers:\n\n")
            for broker, routes in self.broker_routes.items():
                route_preview = ', '.join(routes[:5])
                if len(routes) > 5:
                    route_preview += f"... ({len(routes)} total)"
                self.broker_preview.insert(tk.END, f"• {broker}: {route_preview}\n")
        else:
            self.broker_preview.insert(tk.END, "No broker routes loaded yet.")
            
        self.broker_preview.config(state='disabled')
        
    def check_ready_to_process(self, *args):
        """Check if ready to process and enable/disable button"""
        if self.excel_file.get() and self.pdf_file.get() and self.broker_routes:
            self.process_btn.config(state='normal')
        else:
            self.process_btn.config(state='disabled')
            
    def start_processing(self):
        """Start processing in a separate thread"""
        self.process_btn.config(state='disabled')
        self.status_var.set("Starting processing...")
        self.progress_var.set(0)
        
        # Clear results
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        # Start processing thread
        thread = threading.Thread(target=self.process_pdf)
        thread.daemon = True
        thread.start()
        
    def extract_route_from_text(self, text):
        """Extract route number from text using various patterns"""
        if not text:
            return None
            
        # Clean text
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Common patterns for route identification
        patterns = [
            r'Route\s*[:#]?\s*(\d+)',
            r'ROUTE\s*[:#]?\s*(\d+)',
            r'Rte\s*[:#]?\s*(\d+)',
            r'Route\s+(\d+)',
            r'(\d+)\s*-\s*Route',
            r'^(\d+)\s*-',  # Number at start followed by dash
            r'(\d{1,4})\s+[A-Za-z]',  # 1-4 digits followed by letters
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Return the first reasonable route number (1-9999)
                for match in matches:
                    route_num = match.strip()
                    if route_num.isdigit() and 1 <= int(route_num) <= 9999:
                        return route_num
        
        return None
        
    def find_broker_for_route(self, route_num):
        """Find which broker is assigned to a specific route"""
        for broker, routes in self.broker_routes.items():
            if route_num in routes:
                return broker
        return None
        
    def update_results(self, message):
        """Update results text area"""
        self.results_text.config(state='normal')
        self.results_text.insert(tk.END, message + '\n')
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')
        self.root.update()
        
    def process_pdf(self):
        """Main PDF processing function"""
        try:
            pdf_path = self.pdf_file.get()
            output_dir = Path(self.output_dir.get())
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create broker subdirectories
            broker_dirs = {}
            for broker in self.broker_routes.keys():
                # Clean broker name for folder
                clean_broker = re.sub(r'[<>:"/\\|?*]', '_', broker)
                broker_dir = output_dir / clean_broker
                broker_dir.mkdir(exist_ok=True)
                broker_dirs[broker] = broker_dir
            
            # Load PDF
            self.status_var.set("Loading PDF...")
            self.root.update()
            
            # Use PyMuPDF for better text extraction
            pdf_doc = fitz.open(pdf_path)
            pdf_reader = PdfReader(pdf_path)
            total_pages = len(pdf_reader.pages)
            
            self.update_results(f"📖 Loaded PDF: {total_pages} pages")
            
            # Process each page
            processed_pages = 0
            unassigned_pages = []
            broker_page_counts = {broker: 0 for broker in self.broker_routes.keys()}
            unassigned_writer = PdfWriter()
            
            for page_num in range(total_pages):
                try:
                    # Update progress
                    progress = ((page_num + 1) / total_pages) * 100
                    self.progress_var.set(progress)
                    self.status_var.set(f"Processing page {page_num + 1}/{total_pages}")
                    self.root.update()
                    
                    # Extract text using PyMuPDF (better than PyPDF2)
                    fitz_page = pdf_doc.load_page(page_num)
                    page_text = fitz_page.get_text()
                    
                    # Extract route number
                    route_num = self.extract_route_from_text(page_text)
                    
                    if route_num:
                        # Find assigned broker
                        assigned_broker = self.find_broker_for_route(route_num)
                        
                        if assigned_broker:
                            # Create PDF for this page
                            pdf_writer = PdfWriter()
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            # Save to broker's directory
                            output_filename = f"Route_{route_num}.pdf"
                            output_path = broker_dirs[assigned_broker] / output_filename
                            
                            with open(output_path, 'wb') as output_pdf:
                                pdf_writer.write(output_pdf)
                            
                            broker_page_counts[assigned_broker] += 1
                            processed_pages += 1
                            
                            if processed_pages % 10 == 0:
                                self.update_results(f"✓ Processed {processed_pages} pages...")
                        else:
                            # Add to unassigned
                            unassigned_pages.append((page_num + 1, f"Route {route_num} - No broker assigned"))
                            unassigned_writer.add_page(pdf_reader.pages[page_num])
                    else:
                        # No route number found
                        unassigned_pages.append((page_num + 1, "No route number found"))
                        unassigned_writer.add_page(pdf_reader.pages[page_num])
                        
                except Exception as e:
                    error_msg = f"Error on page {page_num + 1}: {str(e)}"
                    self.update_results(f"⚠️ {error_msg}")
                    unassigned_pages.append((page_num + 1, error_msg))
            
            # Close PyMuPDF document
            pdf_doc.close()
            
            # Save unassigned pages if any
            if len(unassigned_writer.pages) > 0:
                unassigned_path = output_dir / 'Unassigned_Routes.pdf'
                with open(unassigned_path, 'wb') as output_pdf:
                    unassigned_writer.write(output_pdf)
                self.update_results(f"📄 Unassigned pages saved: {unassigned_path.name}")
            
            # Create ZIP file
            self.status_var.set("Creating ZIP file...")
            self.root.update()
            
            zip_path = output_dir / 'Broker_Route_PDFs.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.pdf'):
                            file_path = Path(root) / file
                            arc_name = file_path.relative_to(output_dir)
                            zipf.write(file_path, arc_name)
            
            # Final results
            self.progress_var.set(100)
            self.status_var.set("✅ Processing Complete!")
            
            self.update_results("\n" + "="*50)
            self.update_results("🎉 PROCESSING COMPLETE!")
            self.update_results("="*50)
            self.update_results(f"📊 Total pages processed: {processed_pages}/{total_pages}")
            self.update_results(f"📁 Output directory: {output_dir}")
            self.update_results(f"📦 ZIP file created: {zip_path.name}")
            self.update_results(f"⚠️ Unassigned pages: {len(unassigned_pages)}")
            
            self.update_results("\n📈 Pages per broker:")
            for broker, count in broker_page_counts.items():
                if count > 0:
                    self.update_results(f"  • {broker}: {count} pages")
            
            if unassigned_pages:
                self.update_results(f"\n⚠️ First few unassigned pages:")
                for page_num, reason in unassigned_pages[:5]:
                    self.update_results(f"  • Page {page_num}: {reason}")
                if len(unassigned_pages) > 5:
                    self.update_results(f"  • ... and {len(unassigned_pages) - 5} more")
            
            # Show completion message
            messagebox.showinfo(
                "Processing Complete!", 
                f"✅ Successfully processed {processed_pages} pages!\n\n"
                f"📁 Files saved to: {output_dir}\n"
                f"📦 ZIP file: {zip_path.name}\n\n"
                f"Check the output directory for all files."
            )
            
        except Exception as e:
            error_msg = f"❌ Processing failed: {str(e)}"
            self.update_results(error_msg)
            self.status_var.set("❌ Processing Failed!")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
        
        finally:
            self.process_btn.config(state='normal')
            
    def run(self):
        """Run the application"""
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Start the main loop
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = BrokerPDFSplitter()
        app.run()
    except Exception as e:
        # Fallback error handling
        try:
            import tkinter.messagebox as mb
            mb.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        except:
            print(f"Fatal Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
