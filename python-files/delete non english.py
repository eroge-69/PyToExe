import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from pathlib import Path

class VTTCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("VTT File Cleaner")
        self.root.geometry("600x400")
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.files_to_delete = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Folder selection
        ttk.Label(main_frame, text="Select Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.selected_folder, width=50).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        
        # Scan button
        ttk.Button(main_frame, text="Scan for Non-English VTT Files", command=self.scan_files).grid(row=2, column=0, pady=10)
        
        # Results area
        ttk.Label(main_frame, text="Files to be deleted:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.file_listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Delete button
        ttk.Button(main_frame, text="Delete Selected Files", command=self.delete_files).grid(row=5, column=0, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=6, column=0, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
    
    def is_english_content(self, text):
        """Check if text contains primarily English content"""
        # Remove VTT formatting and timestamps
        clean_text = re.sub(r'WEBVTT.*?\n', '', text, flags=re.DOTALL)
        clean_text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', '', clean_text)
        clean_text = re.sub(r'<[^>]+>', '', clean_text)  # Remove HTML tags
        clean_text = re.sub(r'\n+', ' ', clean_text)  # Replace newlines with spaces
        clean_text = clean_text.strip()
        
        if not clean_text:
            return False
        
        # Check for English characteristics
        english_indicators = [
            # Common English words
            r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b',
            # English articles and pronouns
            r'\b(a|an|this|that|these|those|he|she|it|they|we|you|I)\b',
            # Common English patterns
            r'\b(is|are|was|were|have|has|had|will|would|can|could)\b'
        ]
        
        # Count English word matches
        english_matches = 0
        total_words = len(clean_text.split())
        
        for pattern in english_indicators:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            english_matches += len(matches)
        
        # If less than 10% English indicators, consider it non-English
        if total_words > 0:
            english_ratio = english_matches / total_words
            return english_ratio > 0.1
        
        return False
    
    def scan_files(self):
        if not self.selected_folder.get():
            messagebox.showerror("Error", "Please select a folder first")
            return
        
        folder_path = Path(self.selected_folder.get())
        if not folder_path.exists():
            messagebox.showerror("Error", "Selected folder does not exist")
            return
        
        self.files_to_delete = []
        self.file_listbox.delete(0, tk.END)
        
        try:
            # Find all .vtt files
            vtt_files = list(folder_path.rglob("*.vtt"))
            
            if not vtt_files:
                self.status_label.config(text="No VTT files found in the selected folder")
                return
            
            self.status_label.config(text=f"Scanning {len(vtt_files)} VTT files...")
            self.root.update()
            
            for vtt_file in vtt_files:
                try:
                    with open(vtt_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not self.is_english_content(content):
                        self.files_to_delete.append(vtt_file)
                        self.file_listbox.insert(tk.END, str(vtt_file))
                
                except Exception as e:
                    print(f"Error reading {vtt_file}: {e}")
                    continue
            
            self.status_label.config(text=f"Found {len(self.files_to_delete)} non-English VTT files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning files: {str(e)}")
    
    def delete_files(self):
        if not self.files_to_delete:
            messagebox.showwarning("Warning", "No files selected for deletion")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {len(self.files_to_delete)} files?\n\nThis action cannot be undone!"
        )
        
        if not result:
            return
        
        deleted_count = 0
        errors = []
        
        for file_path in self.files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        # Show results
        if errors:
            error_msg = f"Deleted {deleted_count} files successfully.\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors) - 5} more errors"
            messagebox.showwarning("Deletion Complete with Errors", error_msg)
        else:
            messagebox.showinfo("Success", f"Successfully deleted {deleted_count} non-English VTT files")
        
        # Clear the list
        self.files_to_delete = []
        self.file_listbox.delete(0, tk.END)
        self.status_label.config(text="Ready")

def main():
    root = tk.Tk()
    app = VTTCleaner(root)
    root.mainloop()

if __name__ == "__main__":
    main()