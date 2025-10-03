import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import shutil

class HTMLReplacerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML String Replacer Tool (v5 - Logo & URL Replacements)")
        self.root.geometry("650x550")
        
        # Variables
        self.logo_var = tk.StringVar()  # New logo word to replace "StatusVideo"
        self.url_var = tk.StringVar()   # New URL to replace "statusvideo.app"
        self.file_paths = [None, None, None]  # For up to 3 files
        self.output_dir = tk.StringVar(value=os.getcwd())  # Default to current dir
        self.overwrite_mode = tk.BooleanVar(value=True)  # Default to overwrite (same filename)
        self.backup_mode = tk.BooleanVar(value=False)    # Option to backup originals
        
        # UI Elements
        self.create_widgets()
    
    def create_widgets(self):
        # Logo Replacement
        tk.Label(self.root, text="Logo (Replaces 'StatusVideo'):").pack(pady=5)
        tk.Entry(self.root, textvariable=self.logo_var, width=50).pack(pady=5)
        
        # URL Replacement
        tk.Label(self.root, text="URL (Replaces 'statusvideo.app'):").pack(pady=5)
        tk.Entry(self.root, textvariable=self.url_var, width=50).pack(pady=5)
        
        # Output Directory
        tk.Label(self.root, text="Output Directory:").pack(pady=5)
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(pady=5)
        tk.Entry(dir_frame, textvariable=self.output_dir, width=40).pack(side=tk.LEFT)
        tk.Button(dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Mode Options
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10)
        tk.Checkbutton(mode_frame, text="Overwrite originals (save with same filename)", variable=self.overwrite_mode).pack(anchor=tk.W)
        tk.Checkbutton(mode_frame, text="Create backups of originals (e.g., original_backup.html)", variable=self.backup_mode).pack(anchor=tk.W)
        
        # File Selection Frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)
        
        tk.Label(file_frame, text="Select Up to 3 HTML Files (Multi-Select Enabled):").pack()
        
        # Single multi-select button
        select_btn = tk.Button(file_frame, text="Select Files", command=self.select_multiple_files, bg="lightblue")
        select_btn.pack(pady=5)
        
        self.file_labels = []  # To update labels dynamically
        for i in range(3):
            row = tk.Frame(file_frame)
            row.pack(pady=2, anchor=tk.W)
            label_text = tk.StringVar(value=f"File {i+1}: No file selected")
            label = tk.Label(row, textvariable=label_text, wraplength=500, fg="gray", justify=tk.LEFT)
            label.pack(side=tk.LEFT)
            self.file_labels.append(label_text)
        
        # Replace Button
        tk.Button(self.root, text="Replace Logo & URL & Save", command=self.replace_in_files, bg="lightgreen").pack(pady=20)
        
        # Output Text Area
        tk.Label(self.root, text="Output Log:").pack()
        self.output_text = scrolledtext.ScrolledText(self.root, width=70, height=10)
        self.output_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # Warning Label
        warning_frame = tk.Frame(self.root)
        warning_frame.pack(pady=5)
        if self.overwrite_mode.get():
            warning = tk.Label(warning_frame, text="Warning: Overwrite mode enabled - originals will be replaced unless backups are checked.", fg="red", wraplength=600)
        else:
            warning = tk.Label(warning_frame, text="Note: New files will be saved as 'original_replaced.html'.", fg="blue", wraplength=600)
        warning.pack()
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def select_multiple_files(self):
        files = filedialog.askopenfilenames(
            title="Select up to 3 HTML Files",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        selected_files = list(files)
        num_selected = len(selected_files)
        
        if num_selected > 3:
            messagebox.showwarning("Selection Limit", f"You selected {num_selected} files, but only the first 3 will be processed.")
            selected_files = selected_files[:3]
            num_selected = 3
        
        self.file_paths = [None] * 3
        for i in range(num_selected):
            self.file_paths[i] = selected_files[i]
            self.file_labels[i].set(f"File {i+1}: {os.path.basename(selected_files[i])}")
            self.log_message(f"Selected File {i+1}: {selected_files[i]}")
        
        for i in range(num_selected, 3):
            self.file_labels[i].set(f"File {i+1}: No file selected")
        
        if num_selected > 0:
            self.log_message(f"Selected {num_selected} file(s).")
    
    def log_message(self, msg):
        self.output_text.insert(tk.END, msg + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def replace_in_file(self, filename, logo_str, url_str):
        try:
            output_dir = self.output_dir.get()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Backup if enabled (backup the original input file to output dir)
            if self.backup_mode.get():
                backup_name = os.path.basename(filename) + "_backup"
                backup_path = os.path.join(output_dir, backup_name)
                shutil.copy2(filename, backup_path)
                self.log_message(f"✓ Backup created: {backup_name}")
            
            # Read original content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Perform both replacements
            new_content = content.replace("StatusVideo", logo_str)
            new_content = new_content.replace("statusvideo.app", url_str)
            
            # Determine new filepath
            if self.overwrite_mode.get():
                name = os.path.basename(filename)
                new_filename = name  # Same name
            else:
                name, ext = os.path.splitext(os.path.basename(filename))
                new_filename = f"{name}_replaced{ext}"
            
            new_filepath = os.path.join(output_dir, new_filename)
            
            # Write new content
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            action = "Overwritten" if (new_filepath == filename) else "Saved"
            self.log_message(f"✓ {action}: {new_filename} ('StatusVideo' → '{logo_str}', 'statusvideo.app' → '{url_str}')")
            return True
        except Exception as e:
            self.log_message(f"✗ Error processing {os.path.basename(filename)}: {e}")
            return False
    
    def replace_in_files(self):
        logo_str = self.logo_var.get().strip()
        url_str = self.url_var.get().strip()
        
        if not logo_str:
            messagebox.showerror("Error", "Please enter the new Logo word.")
            return
        if not url_str:
            messagebox.showerror("Error", "Please enter the new URL.")
            return
        
        valid_files = [fp for fp in self.file_paths if fp and os.path.exists(fp)]
        if not valid_files:
            messagebox.showerror("Error", "Please select at least one valid HTML file.")
            return
        
        output_dir = self.output_dir.get()
        
        # Warning if overwriting
        overwrite_text = ""
        if self.overwrite_mode.get():
            overwrite_text = "\n\nWARNING: This will overwrite the original files with the same names (backups optional)."
        
        if messagebox.askyesno("Confirm", f"Replace 'StatusVideo' with '{logo_str}' and 'statusvideo.app' with '{url_str}' in {len(valid_files)} files?{overwrite_text}\n\nFiles will be saved to '{output_dir}'."):
            self.log_message(f"\nStarting replacements in {len(valid_files)} files...")
            self.log_message(f"Output directory: {output_dir}")
            self.log_message(f"Mode: {'Overwrite (same filename)' if self.overwrite_mode.get() else 'New files (_replaced)'}")
            self.log_message(f"Backups: {'Enabled' if self.backup_mode.get() else 'Disabled'}")
            success_count = 0
            for file in valid_files:
                if self.replace_in_file(file, logo_str, url_str):
                    success_count += 1
            
            self.log_message(f"\nDone! {success_count}/{len(valid_files)} files processed successfully.")
            messagebox.showinfo("Complete", f"Replacements finished! Check the log for details.")
        else:
            self.log_message("Replacement cancelled by user.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HTMLReplacerGUI(root)
    root.mainloop()