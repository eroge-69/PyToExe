import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import shutil
import threading
from pathlib import Path
import time

class FileCopyUtility:
    def __init__(self, root):
        self.root = root
        self.root.title("File Copy Utility - Image Hub to Briefs")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configuration
        self.source_dir = "D:\\Image hub"
        
        # Get Desktop path - try multiple methods
        desktop_path = None
        try:
            # Method 1: Try Windows registry
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        except:
            try:
                # Method 2: Try environment variable
                desktop_path = os.environ.get('USERPROFILE')
                if desktop_path:
                    desktop_path = os.path.join(desktop_path, "Desktop")
            except:
                # Method 3: Standard fallback
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Ensure we have a valid Desktop path
        if not desktop_path or not os.path.exists(desktop_path):
            desktop_path = os.path.expanduser("~")  # Use home directory as fallback
        
        self.dest_dir = os.path.join(desktop_path, "Briefs")
        
        # Normalize the path to handle any issues
        self.dest_dir = os.path.normpath(self.dest_dir)
        
        self.setup_ui()
        
        # Validate paths at startup
        self.validate_paths()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Copy Utility", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Source and destination info
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Source:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=self.source_dir, foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Destination:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=self.dest_dir, foreground="blue").grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input File Names/Numbers (space-separated)", padding="5")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        input_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.input_text.configure(yscrollcommand=input_scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.copy_button = ttk.Button(button_frame, text="🚀 COPY FILES", 
                                     command=self.start_copy_operation, style="Accent.TButton")
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear", 
                                      command=self.clear_input)
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, state=tk.DISABLED)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.results_text.tag_configure("success", foreground="green", font=("Consolas", 9))
        self.results_text.tag_configure("error", foreground="red", font=("Consolas", 9))
        self.results_text.tag_configure("info", foreground="blue", font=("Consolas", 9))
        self.results_text.tag_configure("warning", foreground="orange", font=("Consolas", 9))
    
    def validate_paths(self):
        """Validate and display path information at startup"""
        self.log_message("🔍 Validating paths...", "info")
        
        # Check source directory
        if os.path.exists(self.source_dir):
            self.log_message(f"✅ Source directory found: {self.source_dir}", "success")
        else:
            self.log_message(f"⚠️ Source directory not found: {self.source_dir}", "warning")
        
        # Check if we can access the destination parent directory
        parent_dir = os.path.dirname(self.dest_dir)
        self.log_message(f"📁 Destination parent: {parent_dir}", "info")
        
        if os.path.exists(parent_dir):
            self.log_message(f"✅ Can access destination parent directory", "success")
        else:
            self.log_message(f"⚠️ Destination parent directory not accessible", "warning")
        
        self.log_message(f"📋 Will create destination at: {self.dest_dir}", "info")
        self.log_message("=" * 50, "info")
        
    def log_message(self, message, tag="info"):
        """Add a message to the results area with color coding"""
        self.results_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_input(self):
        """Clear the input text box and results"""
        self.input_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def find_matching_files(self, search_terms):
        """Find files that start with any of the given search terms (first 9 digits)"""
        matching_files = []
        
        if not os.path.exists(self.source_dir):
            self.log_message(f"❌ Source directory not found: {self.source_dir}", "error")
            return matching_files
        
        self.log_message(f"🔍 Searching for files in: {self.source_dir}", "info")
        
        # Extract first 9 digits from each search term
        search_patterns = []
        for term in search_terms:
            # Extract first 9 digits from the term
            digits = ''.join(filter(str.isdigit, term))[:9]
            if len(digits) >= 9:
                search_patterns.append(digits)
            else:
                self.log_message(f"⚠️ Skipping '{term}' - need at least 9 digits", "warning")
        
        if not search_patterns:
            self.log_message("❌ No valid search patterns found", "error")
            return matching_files
        
        self.log_message(f"📋 Search patterns: {', '.join(search_patterns)}", "info")
        
        # Walk through all files in source directory and subdirectories
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if filename starts with any of our search patterns
                for pattern in search_patterns:
                    if file.startswith(pattern):
                        matching_files.append(file_path)
                        rel_path = os.path.relpath(file_path, self.source_dir)
                        self.log_message(f"✓ Found: {rel_path}", "success")
                        break
        
        return matching_files
    
    def copy_files(self, file_list):
        """Copy the list of files to destination directory"""
        if not file_list:
            self.log_message("❌ No files to copy", "error")
            return
        
        # Create destination directory if it doesn't exist
        try:
            # Use absolute path and ensure parent directories exist
            abs_dest_dir = os.path.abspath(self.dest_dir)
            os.makedirs(abs_dest_dir, exist_ok=True)
            self.log_message(f"📁 Destination directory ready: {abs_dest_dir}", "success")
            
            # Test write access
            test_file = os.path.join(abs_dest_dir, "test_write_access.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                self.log_message(f"✅ Write access confirmed", "success")
            except Exception as e:
                self.log_message(f"❌ No write access to destination: {str(e)}", "error")
                return
                
        except Exception as e:
            self.log_message(f"❌ Failed to create destination directory: {str(e)}", "error")
            return
        
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for file_path in file_list:
            try:
                # Convert to absolute paths
                abs_source_path = os.path.abspath(file_path)
                
                # Verify source file exists
                if not os.path.exists(abs_source_path):
                    self.log_message(f"❌ Source file not found: {abs_source_path}", "error")
                    error_count += 1
                    continue
                
                filename = os.path.basename(abs_source_path)
                abs_dest_path = os.path.abspath(os.path.join(self.dest_dir, filename))
                
                # Debug: Log the full paths
                self.log_message(f"🔍 Copying from: {abs_source_path}", "info")
                self.log_message(f"🔍 Copying to: {abs_dest_path}", "info")
                
                # Skip if file already exists
                if os.path.exists(abs_dest_path):
                    self.log_message(f"⏭️ Skipped (exists): {filename}", "warning")
                    skipped_count += 1
                    continue
                
                # Verify we can read the source file
                if not os.access(abs_source_path, os.R_OK):
                    self.log_message(f"❌ Cannot read source file: {filename}", "error")
                    error_count += 1
                    continue
                
                # Copy the file
                shutil.copy2(abs_source_path, abs_dest_path)
                self.log_message(f"✅ Successfully copied: {filename}", "success")
                copied_count += 1
                
            except PermissionError as e:
                self.log_message(f"❌ Permission denied copying {os.path.basename(file_path)}: {str(e)}", "error")
                error_count += 1
            except FileNotFoundError as e:
                self.log_message(f"❌ File not found {os.path.basename(file_path)}: {str(e)}", "error")
                error_count += 1
            except Exception as e:
                self.log_message(f"❌ Error copying {os.path.basename(file_path)}: {str(e)}", "error")
                error_count += 1
        
        # Summary
        self.log_message("=" * 50, "info")
        self.log_message(f"📊 SUMMARY:", "info")
        self.log_message(f"✅ Files copied: {copied_count}", "success")
        self.log_message(f"⏭️ Files skipped: {skipped_count}", "warning")
        self.log_message(f"❌ Errors: {error_count}", "error")
        self.log_message("=" * 50, "info")
    
    def copy_operation_thread(self, search_terms):
        """Run the copy operation in a separate thread"""
        try:
            self.log_message("🚀 Starting file copy operation...", "info")
            
            # Find matching files
            matching_files = self.find_matching_files(search_terms)
            
            if matching_files:
                self.log_message(f"📋 Found {len(matching_files)} matching files", "info")
                # Copy the files
                self.copy_files(matching_files)
            else:
                self.log_message("❌ No matching files found", "error")
            
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {str(e)}", "error")
        
        finally:
            # Re-enable the copy button and stop progress bar
            self.root.after(0, self.operation_complete)
    
    def operation_complete(self):
        """Called when the copy operation is complete"""
        self.progress.stop()
        self.copy_button.config(state=tk.NORMAL, text="🚀 COPY FILES")
    
    def start_copy_operation(self):
        """Start the copy operation in a separate thread"""
        # Get input text and split by spaces
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            self.log_message("❌ Please enter file names or numbers", "error")
            return
        
        search_terms = input_text.split()
        
        if not search_terms:
            self.log_message("❌ No valid search terms found", "error")
            return
        
        # Disable button and start progress bar
        self.copy_button.config(state=tk.DISABLED, text="Processing...")
        self.progress.start()
        
        # Clear previous results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        # Start the operation in a separate thread
        thread = threading.Thread(target=self.copy_operation_thread, args=(search_terms,))
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = FileCopyUtility(root)
    root.mainloop()

if __name__ == "__main__":
    main()