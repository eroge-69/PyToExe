#!/usr/bin/env python3
"""
Duplicate File Finder
A lightweight Windows application to scan folders, compute SHA-256 hashes,
identify duplicates, and manage duplicate files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
import threading
from pathlib import Path
from collections import defaultdict
import time


class DuplicateFileFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Data storage
        self.file_hashes = {}  # hash -> [file_paths]
        self.duplicates = {}   # hash -> [file_paths] (only duplicates)
        self.scanning = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="ewns")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Folder selection
        ttk.Label(main_frame, text="Select folder to scan:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, state="readonly")
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1)
        ttk.Button(folder_frame, text="Scan", command=self.start_scan).grid(row=0, column=2, padx=(5, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to scan")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Duplicates display
        ttk.Label(main_frame, text="Duplicate Files:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=5, column=0, columnspan=2, sticky="ewns", pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=("Size", "Path"), show="tree headings")
        self.tree.heading("#0", text="File Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Path", text="Full Path")
        
        # Configure column widths
        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("Size", width=100, minwidth=80)
        self.tree.column("Path", width=500, minwidth=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="ewns")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(title="Select folder to scan for duplicates")
        if folder:
            self.folder_var.set(folder)
            
    def start_scan(self):
        """Start scanning in a separate thread"""
        folder = self.folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid folder to scan.")
            return
            
        if self.scanning:
            messagebox.showwarning("Warning", "Scan already in progress.")
            return
            
        # Clear previous results
        self.clear_results()
        
        # Start scanning in background thread
        self.scanning = True
        scan_thread = threading.Thread(target=self.scan_folder, args=(folder,))
        scan_thread.daemon = True
        scan_thread.start()
        
    def scan_folder(self, folder_path):
        """Scan folder for files and compute hashes"""
        try:
            self.update_status("Discovering files...")
            self.update_progress(0)
            
            # First pass: collect all files
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        all_files.append(file_path)
            
            if not all_files:
                self.update_status("No files found in the selected folder.")
                self.scanning = False
                return
                
            total_files = len(all_files)
            self.update_status(f"Computing hashes for {total_files} files...")
            
            # Second pass: compute hashes
            file_hashes = defaultdict(list)
            processed = 0
            
            for file_path in all_files:
                try:
                    # Compute SHA-256 hash
                    file_hash = self.compute_file_hash(file_path)
                    if file_hash:
                        file_hashes[file_hash].append(file_path)
                    
                    processed += 1
                    progress = (processed / total_files) * 100
                    self.update_progress(progress)
                    
                    # Update status periodically
                    if processed % 10 == 0 or processed == total_files:
                        self.update_status(f"Processed {processed}/{total_files} files...")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
            
            # Find duplicates (hashes with more than one file)
            duplicates = {hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1}
            
            self.file_hashes = dict(file_hashes)
            self.duplicates = duplicates
            
            # Update UI with results
            self.root.after(0, self.display_duplicates)
            
        except Exception as e:
            self.update_status(f"Error during scan: {e}")
        finally:
            self.scanning = False
            
    def compute_file_hash(self, file_path):
        """Compute SHA-256 hash of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return None
            
    def display_duplicates(self):
        """Display duplicate files in the treeview"""
        self.tree.delete(*self.tree.get_children())
        
        if not self.duplicates:
            self.update_status("No duplicate files found.")
            self.update_progress(0)
            return
            
        total_duplicates = sum(len(paths) for paths in self.duplicates.values())
        duplicate_groups = len(self.duplicates)
        
        for i, (file_hash, file_paths) in enumerate(self.duplicates.items()):
            # Create parent node for each duplicate group
            group_size = self.format_size(os.path.getsize(file_paths[0]))
            parent = self.tree.insert("", "end", text=f"Duplicate Group {i+1} ({len(file_paths)} files)", 
                                    values=(group_size, f"Hash: {file_hash[:16]}..."), open=True)
            
            # Add each duplicate file as a child
            for file_path in file_paths:
                try:
                    file_name = os.path.basename(file_path)
                    file_size = self.format_size(os.path.getsize(file_path))
                    
                    # Insert file with checkbox capability
                    item = self.tree.insert(parent, "end", text=f"☐ {file_name}", 
                                          values=(file_size, file_path), tags=("file",))
                    
                except Exception as e:
                    print(f"Error getting file info for {file_path}: {e}")
                    
        self.update_status(f"Found {total_duplicates} duplicate files in {duplicate_groups} groups.")
        self.update_progress(100)
        
        # Bind click event to toggle checkboxes
        self.tree.bind("<Button-1>", self.on_tree_click)
        
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def on_tree_click(self, event):
        """Handle tree item clicks to toggle checkboxes"""
        item = self.tree.identify("item", event.x, event.y)
        if item and "file" in self.tree.item(item, "tags"):
            # Toggle checkbox
            current_text = self.tree.item(item, "text")
            if current_text.startswith("☐"):
                new_text = current_text.replace("☐", "☑")
            else:
                new_text = current_text.replace("☑", "☐")
            self.tree.item(item, text=new_text)
            
    def select_all(self):
        """Select all duplicate files"""
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                if "file" in self.tree.item(child, "tags"):
                    current_text = self.tree.item(child, "text")
                    new_text = current_text.replace("☐", "☑")
                    self.tree.item(child, text=new_text)
                    
    def deselect_all(self):
        """Deselect all duplicate files"""
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                if "file" in self.tree.item(child, "tags"):
                    current_text = self.tree.item(child, "text")
                    new_text = current_text.replace("☑", "☐")
                    self.tree.item(child, text=new_text)
                    
    def delete_selected(self):
        """Delete selected duplicate files"""
        selected_files = []
        
        # Collect selected files
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                if "file" in self.tree.item(child, "tags"):
                    text = self.tree.item(child, "text")
                    if text.startswith("☑"):
                        file_path = self.tree.item(child, "values")[1]
                        selected_files.append((child, file_path))
        
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected for deletion.")
            return
            
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to permanently delete {len(selected_files)} selected files?\n\n"
            "This action cannot be undone!"
        )
        
        if not response:
            return
            
        # Delete files
        deleted_count = 0
        errors = []
        
        for item, file_path in selected_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.tree.delete(item)
                    deleted_count += 1
                else:
                    errors.append(f"File not found: {file_path}")
            except Exception as e:
                errors.append(f"Error deleting {file_path}: {e}")
                
        # Show results
        message = f"Successfully deleted {deleted_count} files."
        if errors:
            message += f"\n\nErrors encountered:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... and {len(errors) - 5} more errors."
                
        messagebox.showinfo("Deletion Complete", message)
        
        # Clean up empty groups
        self.cleanup_empty_groups()
        
    def cleanup_empty_groups(self):
        """Remove empty duplicate groups from the tree"""
        for item in list(self.tree.get_children()):
            if not self.tree.get_children(item):
                self.tree.delete(item)
                
    def clear_results(self):
        """Clear all results and reset the interface"""
        self.tree.delete(*self.tree.get_children())
        self.file_hashes.clear()
        self.duplicates.clear()
        self.update_progress(0)
        self.update_status("Ready to scan")
        
    def update_status(self, message):
        """Update status label (thread-safe)"""
        self.root.after(0, lambda: self.status_var.set(message))
        
    def update_progress(self, value):
        """Update progress bar (thread-safe)"""
        self.root.after(0, lambda: self.progress_var.set(value))


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = DuplicateFileFinder(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()