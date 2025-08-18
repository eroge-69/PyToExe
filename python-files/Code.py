import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

class LogFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Filter Tool with Statistics")
        self.root.geometry("600x400")
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.search_terms = tk.StringVar(value="CheckRxScResult() NR Unit, Band: 78, Result: FAIL")
        self.status_text = tk.StringVar(value="Ready")
        self.stats_text = tk.StringVar(value="Statistics: ")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Input Folder
        tk.Label(self.root, text="Test log folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.input_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output Folder
        tk.Label(self.root, text="Result folder:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Search Terms
        tk.Label(self.root, text="Search terms (comma separated):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.root, textvariable=self.search_terms, width=50).grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")
        
        # Status
        tk.Label(self.root, textvariable=self.status_text).grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Statistics
        tk.Label(self.root, textvariable=self.stats_text).grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Filter Files", command=self.filter_files).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear Stats", command=self.clear_stats).pack(side="left", padx=5)
        tk.Button(button_frame, text="Export Stats", command=self.export_stats).pack(side="left", padx=5)
        
    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            
    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
            
    def filter_files(self):
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        terms = [term.strip() for term in self.search_terms.get().split(",")]
        
        if not input_folder or not output_folder or not terms:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            # Prepare statistics
            total_files = 0
            processed_files = 0
            total_lines = 0
            matched_lines = 0
            
            # Get all log files
            log_files = [f for f in os.listdir(input_folder) if f.endswith('.log') or f.endswith('.txt')]
            total_files = len(log_files)
            self.progress["maximum"] = total_files
            
            # Process each file
            for filename in log_files:
                self.status_text.set(f"Processing {filename}...")
                self.root.update()
                
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile, \
                     open(output_path, 'w', encoding='utf-8') as outfile:
                    
                    file_lines = 0
                    file_matches = 0
                    
                    for line in infile:
                        file_lines += 1
                        # Check if all terms are in line AND "FAIL" is exactly in uppercase
                        if all(term in line for term in terms) and " FAIL " in line:
                            outfile.write(line)
                            file_matches += 1
                    
                    total_lines += file_lines
                    matched_lines += file_matches
                
                processed_files += 1
                self.progress["value"] = processed_files
                self.stats_text.set(
                    f"Statistics: Processed {processed_files}/{total_files} files. "
                    f"Total lines: {total_lines}. Matched lines: {matched_lines}"
                )
                self.root.update()
                
            self.status_text.set(f"Done! Processed {processed_files} files.")
            messagebox.showinfo("Success", "Filtering completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_text.set("Error occurred during processing")
            
    def clear_stats(self):
        self.stats_text.set("Statistics: ")
        self.progress["value"] = 0
        self.status_text.set("Ready")
        
    def export_stats(self):
        if not self.stats_text.get() or self.stats_text.get() == "Statistics: ":
            messagebox.showwarning("Warning", "No statistics to export")
            return
            
        try:
            output_folder = self.output_folder.get()
            if not output_folder:
                output_folder = os.getcwd()
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stats_file = os.path.join(output_folder, f"log_filter_stats_{timestamp}.txt")
            
            with open(stats_file, 'w') as f:
                f.write(self.stats_text.get())
                
            messagebox.showinfo("Success", f"Statistics exported to {stats_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export statistics: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogFilterApp(root)
    root.mainloop()