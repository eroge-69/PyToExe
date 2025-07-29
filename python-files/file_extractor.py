import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import csv
from pathlib import Path

class FileExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Data Extractor - MFCSL#BATCH Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_file = None
        self.extracted_data = ""
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure the application styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📄 File Data Extractor", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text="Extract last row data and create MFCSL#BATCH files", 
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_section = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_section.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_section.columnconfigure(1, weight=1)
        
        ttk.Label(file_section, text="Select File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_section, textvariable=self.file_path_var, state='readonly')
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_section, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        # File info display
        self.file_info_var = tk.StringVar()
        self.file_info_label = ttk.Label(file_section, textvariable=self.file_info_var, 
                                       font=('Arial', 9), foreground='blue')
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Batch number section
        batch_section = ttk.LabelFrame(main_frame, text="Batch Configuration", padding="10")
        batch_section.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        batch_section.columnconfigure(1, weight=1)
        
        ttk.Label(batch_section, text="Batch Number:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.batch_var = tk.StringVar()
        self.batch_entry = ttk.Entry(batch_section, textvariable=self.batch_var, width=20)
        self.batch_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.batch_entry.bind('<KeyRelease>', self.on_batch_change)
        
        ttk.Label(batch_section, text="(e.g., 001, ABC123)", font=('Arial', 9), 
                 foreground='gray').grid(row=0, column=2, sticky=tk.W)
        
        # Process section
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15))
        
        self.process_btn = ttk.Button(process_frame, text="🚀 Extract Last Row & Create File", 
                                    command=self.process_file, style='Custom.TButton', state='disabled')
        self.process_btn.pack()
        
        # Results section
        results_section = ttk.LabelFrame(main_frame, text="Extracted Data", padding="10")
        results_section.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        results_section.columnconfigure(0, weight=1)
        results_section.rowconfigure(1, weight=1)
        
        # Results text area with scrollbar
        text_frame = ttk.Frame(results_section)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, height=8, wrap=tk.WORD, state='disabled',
                                  font=('Courier New', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Save button
        self.save_btn = ttk.Button(results_section, text="💾 Save MFCSL#BATCH File", 
                                  command=self.save_file, state='disabled')
        self.save_btn.grid(row=2, column=0, pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a file and enter batch number to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, 
                              font=('Arial', 9))
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(5, weight=1)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def browse_file(self):
        """Open file dialog to select input file"""
        file_types = [
            ('Text files', '*.txt'),
            ('CSV files', '*.csv'),
            ('TSV files', '*.tsv'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=file_types
        )
        
        if filename:
            self.selected_file = filename
            self.file_path_var.set(filename)
            
            # Show file info
            file_size = os.path.getsize(filename) / 1024  # KB
            self.file_info_var.set(f"File: {os.path.basename(filename)} | Size: {file_size:.2f} KB")
            
            self.check_ready_state()
            self.status_var.set(f"File selected: {os.path.basename(filename)}")
    
    def on_batch_change(self, event=None):
        """Handle batch number input changes"""
        self.check_ready_state()
    
    def check_ready_state(self):
        """Enable/disable process button based on input state"""
        if self.selected_file and self.batch_var.get().strip():
            self.process_btn.config(state='normal')
        else:
            self.process_btn.config(state='disabled')
    
    def process_file(self):
        """Process the selected file and extract last row"""
        if not self.selected_file or not self.batch_var.get().strip():
            messagebox.showerror("Error", "Please select a file and enter a batch number.")
            return
        
        try:
            self.status_var.set("Processing file...")
            self.root.update()
            
            # Read file content
            with open(self.selected_file, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            
            # Remove empty lines
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                messagebox.showerror("Error", "The file appears to be empty or contains no valid data.")
                self.status_var.set("Error: Empty file")
                return
            
            # Get last row
            last_row = lines[-1]
            self.extracted_data = last_row
            
            # Display extracted data
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Last row data (Row {len(lines)}):\n\n{last_row}")
            self.result_text.config(state='disabled')
            
            # Enable save button
            self.save_btn.config(state='normal')
            
            self.status_var.set(f"Success: Extracted data from row {len(lines)}")
            messagebox.showinfo("Success", f"Successfully extracted data from row {len(lines)}!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing file: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def save_file(self):
        """Save extracted data to MFCSL#BATCH file"""
        if not self.extracted_data:
            messagebox.showerror("Error", "No data to save. Please process a file first.")
            return
        
        batch_num = self.batch_var.get().strip()
        if not batch_num:
            messagebox.showerror("Error", "Please enter a batch number.")
            return
        
        # Create filename
        filename = f"MFCSL#{batch_num}.txt"
        
        # Ask user where to save
        save_path = filedialog.asksaveasfilename(
            title="Save MFCSL#BATCH File",
            defaultextension=".txt",
            initialvalue=filename,
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(self.extracted_data)
                
                self.status_var.set(f"File saved: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File saved successfully as:\n{os.path.basename(save_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                self.status_var.set(f"Error saving file: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = FileExtractorApp(root)
    
    # Set window icon (optional - will use default if icon file not found)
    try:
        root.iconbitmap('icon.ico')  # Add your icon file if available
    except:
        pass  # Use default icon if custom icon not found
    
    root.mainloop()

if __name__ == "__main__":
    main()