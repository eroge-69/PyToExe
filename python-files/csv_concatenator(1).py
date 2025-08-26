import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
from pathlib import Path

class CSVConcatenator:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV File Concatenator")
        self.root.geometry("600x400")
        
        # Variables
        self.input_dir = tk.StringVar()
        self.output_file = tk.StringVar()
        self.cancel_flag = threading.Event()
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input directory selection
        ttk.Label(main_frame, text="Input Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_input_dir).grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_output_file).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.run_button = ttk.Button(button_frame, text="Run", command=self.start_concatenation)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_operation, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def select_input_dir(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)
            self.log_message(f"Input directory selected: {directory}")
            
    def select_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file.set(file_path)
            self.log_message(f"Output file selected: {file_path}")
            
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_concatenation(self):
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select an output file")
            return
            
        # Start the concatenation in a separate thread
        self.is_running = True
        self.cancel_flag.clear()
        self.run_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.concatenate_files)
        thread.daemon = True
        thread.start()
        
    def cancel_operation(self):
        self.cancel_flag.set()
        self.log_message("Cancellation requested...")
        
    def concatenate_files(self):
        try:
            # Get all CSV files in the directory
            input_path = Path(self.input_dir.get())
            csv_files = list(input_path.glob("*.csv"))
            
            if not csv_files:
                self.log_message("No CSV files found in the selected directory")
                self.reset_ui()
                return
                
            total_files = len(csv_files)
            self.status_var.set(f"Found {total_files} CSV files to concatenate")
            self.log_message(f"Found {total_files} CSV files to concatenate")
            
            # Initialize progress bar
            self.progress['maximum'] = total_files
            self.progress['value'] = 0
            
            # List to store dataframes
            dataframes = []
            
            for i, file_path in enumerate(csv_files):
                if self.cancel_flag.is_set():
                    self.log_message("Operation cancelled by user")
                    self.reset_ui()
                    return
                    
                try:
                    self.log_message(f"Processing: {file_path.name}")
                    df = pd.read_csv(file_path)
                    
                    # Add source file column (optional)
                    df['source_file'] = file_path.name
                    
                    dataframes.append(df)
                    
                    # Update progress
                    self.progress['value'] = i + 1
                    progress_percent = ((i + 1) / total_files) * 100
                    self.status_var.set(f"Processing file {i + 1} of {total_files} ({progress_percent:.1f}%)")
                    self.root.update_idletasks()
                    
                except Exception as e:
                    self.log_message(f"Error reading {file_path.name}: {str(e)}")
                    continue
                    
            if self.cancel_flag.is_set():
                self.log_message("Operation cancelled by user")
                self.reset_ui()
                return
                
            if not dataframes:
                self.log_message("No valid CSV files could be processed")
                self.reset_ui()
                return
                
            # Concatenate all dataframes
            self.log_message("Concatenating data...")
            self.status_var.set("Concatenating data...")
            
            combined_df = pd.concat(dataframes, ignore_index=True)
            
            # Save to output file
            self.log_message("Saving output file...")
            self.status_var.set("Saving output file...")
            
            combined_df.to_csv(self.output_file.get(), index=False)
            
            # Success
            total_rows = len(combined_df)
            self.log_message(f"Success! Concatenated {len(dataframes)} files with {total_rows} total rows")
            self.status_var.set(f"Complete! {len(dataframes)} files concatenated, {total_rows} total rows")
            
            messagebox.showinfo("Success", f"Successfully concatenated {len(dataframes)} CSV files!\nOutput saved to: {self.output_file.get()}")
            
        except Exception as e:
            error_msg = f"Error during concatenation: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
        finally:
            self.reset_ui()
            
    def reset_ui(self):
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        if not self.cancel_flag.is_set():
            self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = CSVConcatenator(root)
    root.mainloop()

if __name__ == "__main__":
    main()